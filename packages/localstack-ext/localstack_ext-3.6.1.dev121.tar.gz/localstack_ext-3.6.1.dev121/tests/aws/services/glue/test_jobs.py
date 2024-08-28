import io
import logging
import os
import tarfile
import textwrap
from fnmatch import fnmatch
from pathlib import Path

import pg8000
import psycopg2
import pytest
from localstack.pro.core.services.glue.crawler_utils import TableParserParquet
from localstack.pro.core.services.glue.job_executor import GLUE_LOG_GROUP_NAME
from localstack.pro.core.services.glue.packages import GLUE_SPARK_MAPPING
from localstack.pro.core.utils.aws.aws_utils import run_athena_queries
from localstack.testing.aws.util import is_aws_cloud
from localstack.testing.config import TEST_AWS_REGION_NAME
from localstack.testing.pytest import markers
from localstack.utils.aws import resources
from localstack.utils.files import load_file, mkdir, new_tmp_dir, new_tmp_file, rm_rf, save_file
from localstack.utils.http import download
from localstack.utils.strings import short_uid, to_bytes
from localstack.utils.sync import retry
from localstack.utils.testutil import create_zip_file, map_all_s3_objects

from tests.aws.services.glue.conftest import skip_bigdata_in_ci

LOG = logging.getLogger(__name__)

# TODO: create full integration test with a script like the one below!
TEST_SCALA_JOB = """
import com.amazonaws.services.glue.util.JsonOptions
import com.amazonaws.services.glue.{DynamicFrame, GlueContext}
import org.apache.spark.SparkContext

object JoinAndRelationalize1 {
  def main(sysArgs: Array[String]): Unit = {
    val sc: SparkContext = new SparkContext()
    val glueContext: GlueContext = new GlueContext(sc)

    // catalog: database and table names
    val dbName = "legislators"
    val tblPersons = "persons_json"
    val tblMembership = "memberships_json"
    val tblOrganization = "organizations_json"

    // output s3 and temp directories
    val outputHistoryDir = "s3://glue-sample-target/output-dir/legislator_history"
    val outputLgSingleDir = "s3://glue-sample-target/output-dir/legislator_single"
    val outputLgPartitionedDir = "s3://glue-sample-target/output-dir/legislator_part"
    val redshiftTmpDir = "s3://glue-sample-target/temp-dir/"

    // Create dynamic frames from the source tables
    val persons: DynamicFrame = glueContext.getCatalogSource(
        database = dbName, tableName = tblPersons).getDynamicFrame()
    val memberships: DynamicFrame = glueContext.getCatalogSource(
        database = dbName, tableName = tblMembership).getDynamicFrame()
    var orgs: DynamicFrame = glueContext.getCatalogSource(
        database = dbName, tableName = tblOrganization).getDynamicFrame()

    // Keep the fields we need and rename some.
    orgs = orgs.dropFields(Seq("other_names", "identifiers")).
        renameField("id", "org_id").renameField("name", "org_name")

    // Join the frames to create history
    val personMemberships = persons.join(
        keys1 = Seq("id"), keys2 = Seq("person_id"), frame2 = memberships)

    val lHistory = orgs.join(keys1 = Seq("org_id"),
        keys2 = Seq("organization_id"), frame2 = personMemberships)
      .dropFields(Seq("person_id", "org_id"))

    // ---- Write out the history ----

    // Write out the dynamic frame into parquet in "legislator_history" directory
    println("Writing to /legislator_history ...")
    lHistory.printSchema()

    glueContext.getSinkWithFormat(connectionType = "s3",
        options = JsonOptions(Map("path" -> outputHistoryDir)),
        format = "parquet", transformationContext = "").writeDynamicFrame(lHistory)

    // Write out a single file to directory "legislator_single"
    val sHistory: DynamicFrame = lHistory.repartition(1)

    println("Writing to /legislator_single ...")
    glueContext.getSinkWithFormat(connectionType = "s3",
        options = JsonOptions(Map("path" -> outputLgSingleDir)),
        format = "parquet", transformationContext = "").writeDynamicFrame(lHistory)

    // Convert to data frame, write to directory "legislator_part"...
    println("Writing to /legislator_part, partitioned by Senate and House ...")

    glueContext.getSinkWithFormat(connectionType = "s3",
      options = JsonOptions(Map("path" -> outputLgSingleDir, "partitionKeys" -> List("org_name"))),
      format = "parquet", transformationContext = "").writeDynamicFrame(lHistory)

    // ---- Write out to relational databases ----
    println("Converting to flat tables ...")
    val frames: Seq[DynamicFrame] = lHistory.relationalize(rootTableName = "hist_root",
      stagingPath = redshiftTmpDir, JsonOptions.empty)

    frames.foreach { frame =>
      val options = JsonOptions(Map("dbtable" -> frame.getName(), "database" -> "dev"))
      glueContext.getJDBCSink(catalogConnection = "test-redshift-3",
        options = options, redshiftTmpDir = redshiftTmpDir).writeDynamicFrame(frame)
    }
  }
}
"""

# Based on: https://github.com/aws-samples/aws-glue-samples/blob/master/examples/join_and_relationalize.py
TEST_PYSPARK_JOB = """
import os
import sys
from awsglue.transforms import Join
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job

glueContext = GlueContext(SparkContext.getOrCreate())

# catalog: database and table names
db_name = "legislators"
tbl_persons = "persons_json"
tbl_membership = "memberships_json"
tbl_organization = "organizations_json"

# output s3 and temp directories
output_history_dir = "s3://glue-sample-target/output-dir/legislator_history"
output_lg_single_dir = "s3://glue-sample-target/output-dir/legislator_single"
output_lg_partitioned_dir = "s3://glue-sample-target/output-dir/legislator_part"
redshift_temp_dir = "s3://glue-sample-target/temp-dir/"

# Create dynamic frames from the source tables
persons = glueContext.create_dynamic_frame.from_catalog(database=db_name, table_name=tbl_persons)
memberships = glueContext.create_dynamic_frame.from_catalog(database=db_name, table_name=tbl_membership)
orgs = glueContext.create_dynamic_frame.from_catalog(database=db_name, table_name=tbl_organization)

# Keep the fields we need and rename some.
orgs = (orgs.drop_fields(['other_names', 'identifiers'])
    .rename_field('id', 'org_id').rename_field('name', 'org_name'))

# Join the frames to create history
l_history = Join.apply(orgs,
    Join.apply(persons, memberships, 'id', 'person_id'), 'org_id', 'organization_id'
).drop_fields(['person_id', 'org_id'])

# ---- Write out the history ----

# Write out the dynamic frame into parquet in "legislator_history" directory
print("Writing to /legislator_history ...")
glueContext.write_dynamic_frame.from_options(
    frame = l_history, connection_type = "s3",
    connection_options = {"path": output_history_dir}, format = "parquet")

# Write out a single file to directory "legislator_single"
s_history = l_history.toDF().repartition(1)
print("Writing to /legislator_single ...")
s_history.write.parquet(output_lg_single_dir)

# Convert to data frame, write to directory "legislator_part", partitioned by Senate / House.
print("Writing to /legislator_part, partitioned by Senate and House ...")
l_history.toDF().write.parquet(output_lg_partitioned_dir, partitionBy=['org_name'])

# ---- Write out to relational databases ----

# Convert the data to flat tables
print("Converting to flat tables ...")
dfc = l_history.relationalize("hist_root", redshift_temp_dir)

# Cycle through and write to Redshift.
for df_name in dfc.keys():
    m_df = dfc.select(df_name)
    print("Writing to Redshift table: ", df_name, " ...")
    glueContext.write_dynamic_frame.from_jdbc_conf(
        frame = m_df, catalog_connection = "redshift3",
        connection_options = {"dbtable": df_name, "database": "testdb"},
        redshift_tmp_dir = redshift_temp_dir)
"""

TEST_USER_VARS_JOB = """
import sys
import requests
from awsglue.utils import getResolvedOptions

# getting argument
args = getResolvedOptions(sys.argv, ["JOB_NAME", "bucket_name"])
bucket_name = args["bucket_name"]

headers = {"Authorization": "AWS4-HMAC-SHA256 Credential=test/123/us-east-1/s3/aws4_request"}
requests.put(f"http://{bucket_name}.s3.localhost.localstack.cloud:4566", headers=headers)
"""

TEST_SPARK_VERSIONS_JOB = """
import os, sys, requests
from awsglue.utils import getResolvedOptions
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.context import SparkContext

sc = SparkContext.getOrCreate()
glue_context = GlueContext(sc)
spark = glue_context.spark_session
job = Job(glue_context)
job.init('in_out_job')

args = getResolvedOptions(sys.argv, ["bucket_prefix"])
bucket_name = f"{args['bucket_prefix']}-{sc.version}"

headers = {"Authorization": "AWS4-HMAC-SHA256 Credential=test/123/us-east-1/s3/aws4_request"}
requests.put(f"http://s3.localhost.localstack.cloud:4566/{bucket_name}", headers=headers)
"""

TEST_SPARK_READ_WRITE_JOB = """
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.context import SparkContext

sc = SparkContext.getOrCreate()
glue_context = GlueContext(sc)
spark = glue_context.spark_session
job = Job(glue_context)
job.init("jobjob")

inputFrame = glue_context.create_dynamic_frame_from_options(connection_type = "s3",
                               connection_options = {"paths" : ["s3://in-bucket/test.csv"]}, format = "csv")
glue_context.write_dynamic_frame.from_options(frame = inputFrame,
            connection_type = "s3", connection_options = {"path": "s3://out-bucket/out.parquet"}, format = "parquet")

inputFrame.printSchema()

# Convert DynamicFrame to DataFrame
df = inputFrame.toDF()
# Show the DataFrame
df.show(2)
job.commit()
"""

TEST_SPARK_LOGGING_JOB = """
import logging
from pyspark.context import SparkContext
from awsglue.context import GlueContext

LOG = logging.getLogger("test")
LOG.info("info message")
LOG.warning("warning message")

glueContext = GlueContext(SparkContext())
logger = glueContext.get_logger()
logger.info("spark logger info message")
logger.warn("spark logger warn message")
logger.error("spark logger error message")

print("print message")
print("print message 2")

raise Exception("error message")
"""

TEST_DELTALAKE_READ_WRITE_JOB = """
from awsglue.context import GlueContext
from pyspark.context import SparkContext
sc = SparkContext()
glueContext = GlueContext(sc)
df = glueContext.create_data_frame.from_catalog(
    database="{db_name}",
    table_name="{table_name}"
)
df.printSchema()
df.show(2)
additional_options = {
    "path": "s3://{s3_output_bucket}"
}
df.write \
    .format("delta") \
    .options(**additional_options) \
    .mode("append") \
    .partitionBy("{partition_key_field}") \
    .saveAsTable("{db_name}.{table_name}")
"""

TEST_PYSPARK_JOB_MODULE_IMPORT = """
import boto3
from awsglue.context import GlueContext
from pyspark.context import SparkContext

import <import_module>

# additional placeholder

sc = SparkContext.getOrCreate()
glue_context = GlueContext(sc)

s3_client = <s3_client>
s3_client.create_bucket(Bucket=<bucket_name>)
"""


def get_filtered_log_events(aws_client, job_id: str, filter_pattern: str = None) -> list[dict]:
    """Return the filtered CloudWatch Logs job log events for the given Glue job run ID"""

    def _check_logs():
        params = {
            "logGroupName": GLUE_LOG_GROUP_NAME,
            "logStreamNamePrefix": job_id,
        }
        if filter_pattern:
            params["filterPattern"] = filter_pattern

        log_events = aws_client.logs.filter_log_events(**params)["events"]
        assert log_events
        return log_events

    return retry(_check_logs, retries=30, sleep=2)


def get_tar_bytes(dir_path: str) -> bytes:
    tar_bytes = io.BytesIO()
    with tarfile.open(fileobj=tar_bytes, mode="w:gz") as tar:
        tar.add(dir_path, arcname=os.path.basename(dir_path))
    return tar_bytes.getvalue()


def get_s3_client_for_pyspark():
    if is_aws_cloud():
        return f"boto3.client('s3', region_name='{TEST_AWS_REGION_NAME}')"
    return f"boto3.client('s3', region_name='{TEST_AWS_REGION_NAME}', endpoint_url='http://localhost:4566')"


@skip_bigdata_in_ci
class TestGlueJobs:
    @markers.aws.unknown
    def test_create_pyspark_job(self, aws_client):
        job_name = f"j-{short_uid()}"
        bucket_name = f"glue-{short_uid()}"
        resources.create_s3_bucket(bucket_name, s3_client=aws_client.s3)
        aws_client.s3.upload_fileobj(io.BytesIO(to_bytes(TEST_PYSPARK_JOB)), bucket_name, "job.py")

        s3_url = f"s3://{bucket_name}/job.py"
        result = aws_client.glue.create_job(
            Name=job_name, Role="r1", Command={"Name": "pythonshell", "ScriptLocation": s3_url}
        )
        assert result["ResponseMetadata"]["HTTPStatusCode"] == 200

        result = aws_client.glue.start_job_run(JobName=job_name)
        assert result["ResponseMetadata"]["HTTPStatusCode"] == 200
        job_id = result.get("JobRunId")

        def check_job_status():
            result = aws_client.glue.get_job_run(JobName=job_name, RunId=job_id).get("JobRun", {})
            assert result["JobRunState"] == "SUCCEEDED"

        # TODO: add integration with and assert presence of logs (with environment variables) here

        # TODO: Set up Glue DBs etc - currently test still fails with "Unable to find Glue database named '...'"
        with pytest.raises(Exception):
            retry(check_job_status, sleep=3, retries=10)

    @markers.aws.unknown
    def test_create_pyspark_job_with_args(self, create_run_pyspark_job, aws_client):
        bucket_arg = f"args-{short_uid()}"
        job_args = {"--bucket_name": bucket_arg}
        create_run_pyspark_job(TEST_USER_VARS_JOB, command_name="glueetl", job_args=job_args)

        def _check_bucket():
            bucket_names = [b["Name"] for b in aws_client.s3.list_buckets()["Buckets"]]
            assert bucket_arg in bucket_names

        # Pulling the bigdata image can take quite some time
        retry(_check_bucket, retries=300, sleep=2)

    @markers.aws.validated
    def test_create_pyspark_job_with_class_parameter(
        self, create_run_job, s3_create_bucket, aws_client
    ):
        bucket_name = s3_create_bucket()
        script = textwrap.dedent(
            """
            from awsglue.context import GlueContext
            from pyspark.context import SparkContext

            sc = SparkContext.getOrCreate()
            glue_context = GlueContext(sc)
            logger = glue_context.get_logger()
            logger.info("Hello world")
            """
        )
        aws_client.s3.upload_fileobj(io.BytesIO(to_bytes(script)), bucket_name, "script.py")

        job_details = {
            "Command": {
                "Name": "glueetl",
                "PythonVersion": "3",
                "ScriptLocation": f"s3://{bucket_name}/script.py",
            },
            "DefaultArguments": {
                "--class": "GlueApp",
                "--enable-continuous-cloudwatch-log": "true",
            },
        }

        result = create_run_job(job_details=job_details)
        job_id = result["JobRun"]["Id"]

        # receive job logs, and run assertions
        log_events = get_filtered_log_events(
            aws_client, job_id=job_id, filter_pattern="Hello world"
        )
        messages = [e["message"] for e in log_events]
        assert any("Hello world" in log for log in messages)

    @pytest.mark.parametrize("glue_version", ["0.9", "1.0", "2.0", "3.0", "4.0"])
    @markers.aws.unknown
    def test_create_glue_versions(self, create_run_pyspark_job, glue_version, aws_client):
        bucket_prefix = f"bucket-{short_uid()}"
        job_args = {"--bucket_prefix": bucket_prefix}
        create_run_pyspark_job(
            TEST_SPARK_VERSIONS_JOB,
            command_name="glueetl",
            job_args=job_args,
            GlueVersion=glue_version,
        )

        spark_version = GLUE_SPARK_MAPPING.get(glue_version)
        bucket_name = f"{bucket_prefix}-{spark_version}"

        def _check_bucket():
            bucket_names = [b["Name"] for b in aws_client.s3.list_buckets()["Buckets"]]
            assert bucket_name in bucket_names

        # Pulling the bigdata image can take quite some time
        retry(_check_bucket, retries=300, sleep=2)

        aws_client.s3.delete_bucket(Bucket=bucket_name)

    @pytest.mark.parametrize("glue_version", ["0.9", "1.0", "2.0", "3.0", "4.0"])
    @markers.aws.unknown
    def test_job_read_write(self, create_run_pyspark_job, glue_version, aws_client):
        in_bucket = "in-bucket"
        out_bucket = "out-bucket"
        resources.create_s3_bucket(in_bucket, s3_client=aws_client.s3)
        resources.create_s3_bucket(out_bucket, s3_client=aws_client.s3)

        csv_content = textwrap.dedent(
            """
            a,b,c,d
            1,2,3,4
            foo,bar,baz,bee
        """
        ).strip()
        aws_client.s3.upload_fileobj(
            io.BytesIO(to_bytes(csv_content)),
            in_bucket,
            "test.csv",
        )

        create_run_pyspark_job(TEST_SPARK_READ_WRITE_JOB, GlueVersion=glue_version)

        objects = aws_client.s3.list_objects_v2(Bucket=out_bucket)["Contents"]
        data = None
        for s3_object in objects:
            if s3_object["Key"].endswith(".parquet"):
                data = aws_client.s3.get_object(Bucket=out_bucket, Key=s3_object["Key"])[
                    "Body"
                ].read()
        assert data is not None

        table = TableParserParquet().parse(content=data)

        assert len(table.rows) == 3
        assert table.rows[2]["col3"] == "bee"

    @markers.aws.validated
    @pytest.mark.parametrize(
        "dependency_type",
        [
            "extra_file_s3_zip",
            "extra_file_s3_file",
            "extra_file_s3_multi_files",
            "extra_module_pypi",
            "extra_module_s3_wheel",
            "extra_module_s3_tar",
        ],
    )
    def test_pyspark_jobs_with_extra_params(
        self, create_run_pyspark_job, s3_create_bucket, aws_client, dependency_type
    ):
        glue_version = "4.0"
        result_bucket = f"bucket-{short_uid()}"
        import_module = f"mymodule_{short_uid()}"
        module_bucket = f"bucket-{short_uid()}"
        pypi_url = "https://files.pythonhosted.org/packages"
        job_args = {}

        script = (
            textwrap.dedent(TEST_PYSPARK_JOB_MODULE_IMPORT)
            .replace("<s3_client>", get_s3_client_for_pyspark())
            .replace("<bucket_name>", f"'{result_bucket}'")
        )

        # create a module
        match dependency_type:
            case "extra_file_s3_zip":
                module_s3_key = f"{import_module}/{import_module}-0.1.zip"

                tmp_dir = new_tmp_dir()
                mkdir(os.path.join(tmp_dir, import_module))
                save_file(os.path.join(tmp_dir, import_module, "__init__.py"), "foo = 'bar'")
                module_bytes = create_zip_file(tmp_dir, get_content=True)
                rm_rf(tmp_dir)

                s3_create_bucket(Bucket=module_bucket)
                aws_client.s3.put_object(Bucket=module_bucket, Key=module_s3_key, Body=module_bytes)

                script = script.replace("<import_module>", import_module)

                job_args["--extra-py-files"] = f"s3://{module_bucket}/{module_s3_key}"
            case "extra_file_s3_file":
                module_s3_key = f"{import_module}/{import_module}.py"
                module_bytes = to_bytes("foo = 'bar'")

                s3_create_bucket(Bucket=module_bucket)
                aws_client.s3.put_object(Bucket=module_bucket, Key=module_s3_key, Body=module_bytes)

                script = script.replace("<import_module>", import_module)

                job_args["--extra-py-files"] = f"s3://{module_bucket}/{module_s3_key}"
            case "extra_file_s3_multi_files":
                module_s3_key_1 = f"{import_module}/{import_module}_1.py"
                module_s3_key_2 = f"{import_module}/{import_module}_2.py"

                module_1_bytes = to_bytes("foo = 'bar'")
                module_2_bytes = to_bytes("bar = 'baz'")

                s3_create_bucket(Bucket=module_bucket)
                aws_client.s3.put_object(
                    Bucket=module_bucket, Key=module_s3_key_1, Body=module_1_bytes
                )
                aws_client.s3.put_object(
                    Bucket=module_bucket, Key=module_s3_key_2, Body=module_2_bytes
                )

                script = script.replace("<import_module>", f"{import_module}_1")
                script = script.replace("# additional placeholder ", f" import {import_module}_2")

                job_args["--extra-py-files"] = (
                    f"s3://{module_bucket}/{module_s3_key_1},s3://{module_bucket}/{module_s3_key_2}"
                )
            case "extra_module_pypi":
                import_module = "jwt"
                additional_module = "pyjwt==2.4.0"

                script = script.replace("<import_module>", import_module)

                job_args["--additional-python-modules"] = additional_module
            case "extra_module_s3_wheel":
                import_module = "black"
                url = f"{pypi_url}/c6/63/a852b07abc942dc069b5457af40feca82667cf5ed9faec7d4688a4d9c7da/black-22.8.0-py3-none-any.whl"
                module_s3_key = "black/black-22.8.0-py3-none-any.whl"

                tmp_file = new_tmp_file()
                download(url, tmp_file)
                s3_create_bucket(Bucket=module_bucket)
                aws_client.s3.put_object(
                    Bucket=module_bucket, Key=module_s3_key, Body=load_file(tmp_file, mode="rb")
                )

                script = script.replace("<import_module>", import_module)

                job_args["--additional-python-modules"] = f"s3://{module_bucket}/{module_s3_key}"
            case "extra_module_s3_tar":
                import_module = f"mymodule_{short_uid()}"
                module_s3_key = f"{import_module}/{import_module}-0.1.tar.gz"

                tmp_dir = new_tmp_dir()
                mkdir(os.path.join(tmp_dir, import_module))
                save_file(os.path.join(tmp_dir, import_module, "__init__.py"), "foo = 'bar'")
                save_file(
                    os.path.join(tmp_dir, "setup.py"),
                    "from setuptools import setup; "
                    f'setup(name="{import_module}", version="0.1", packages=["{import_module}"])',
                )

                module_bytes = get_tar_bytes(tmp_dir)
                rm_rf(tmp_dir)

                s3_create_bucket(Bucket=module_bucket)
                aws_client.s3.put_object(Bucket=module_bucket, Key=module_s3_key, Body=module_bytes)

                script = script.replace("<import_module>", import_module)

                job_args["--additional-python-modules"] = f"s3://{module_bucket}/{module_s3_key}"

        create_run_pyspark_job(
            script,
            job_args=job_args,
            command_name="glueetl",
            GlueVersion=glue_version,
        )

        def _check_bucket():
            bucket_names = [b["Name"] for b in aws_client.s3.list_buckets()["Buckets"]]
            assert result_bucket in bucket_names

        retry(_check_bucket, retries=300, sleep=2)

        # clean up
        aws_client.s3.delete_bucket(Bucket=result_bucket)

    @markers.aws.unknown
    def test_store_job_logs(self, create_run_pyspark_job, aws_client):
        result = create_run_pyspark_job(
            TEST_SPARK_LOGGING_JOB, command_name="glueetl", expected_status="FAILED"
        )
        job_id = result["JobRun"]["Id"]

        # receive job logs, and run assertions
        log_events = get_filtered_log_events(aws_client, job_id=job_id)
        messages = [event["message"] for event in log_events]
        assert "warning message" in messages
        assert "print message" in messages
        assert "print message 2" in messages
        assert "Exception: error message" in messages
        assert any("spark logger info message" in msg for msg in messages)
        assert any("spark logger warn message" in msg for msg in messages)
        assert any("spark logger error message" in msg for msg in messages)

    @markers.aws.validated
    @pytest.mark.parametrize("glue_version", ["4.0"])
    @pytest.mark.skip(reason="work in progress, first aws validated snapshot test in construction")
    def test_deltalake_read_write(
        self,
        glue_version,
        s3_create_bucket,
        glue_create_database,
        glue_create_table,
        create_run_pyspark_job,
        aws_client,
        snapshot,
    ):
        # upload the deltalake table data to S3
        in_bucket_name = s3_create_bucket()
        path = Path(os.path.join(os.path.dirname(__file__), "./athena/deltalake/"))
        for file_path in path.rglob("*"):
            if file_path.is_dir():
                continue
            relative_path = os.path.relpath(file_path, path)
            path_in_bucket = os.path.join("test", relative_path)
            aws_client.s3.upload_file(str(file_path), Bucket=in_bucket_name, Key=path_in_bucket)

        # Create the Glue table
        location = f"s3://{in_bucket_name}/test/"
        # TODO continue here, the glue_create_database does not work on AWS, it does not complete
        database_name = glue_create_database()["Name"]
        table = glue_create_table(
            DatabaseName=database_name,
            TableInput={
                "StorageDescriptor": {
                    "Columns": [
                        {"Name": "letter", "Type": "string"},
                        {"Name": "number", "Type": "bigint"},
                    ],
                    "Location": location,
                    "InputFormat": "org.apache.hadoop.mapred.SequenceFileInputFormat",
                    "OutputFormat": "org.apache.hadoop.hive.ql.io.HiveSequenceFileOutputFormat",
                    "Compressed": False,
                    "NumberOfBuckets": -1,
                    "SerdeInfo": {
                        "SerializationLibrary": "org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe",
                        "Parameters": {"serialization.format": "1", "path": location},
                    },
                    "SortColumns": [],
                    "StoredAsSubDirectories": False,
                },
                "PartitionKeys": [],
                "TableType": "EXTERNAL_TABLE",
                "Parameters": {
                    "EXTERNAL": "TRUE",
                    "spark.sql.sources.schema.part.0": '{"type":"struct","fields":[{"name":"letter","type":"string","nullable":true,"metadata":{}},{"name":"number","type":"long","nullable":true,"metadata":{}}]}',
                    "spark.sql.partitionProvider": "catalog",
                    "spark.sql.sources.schema.numParts": "1",
                    "spark.sql.sources.provider": "delta",
                    "delta.lastCommitTimestamp": "1668400585501",
                    "delta.lastUpdateVersion": "2",
                    "table_type": "delta",
                },
            },
        )
        snapshot.match("create-table", table)
        table_name = table["Name"]

        # create a bucket for the results
        out_bucket_name = s3_create_bucket()
        job_code = TEST_DELTALAKE_READ_WRITE_JOB.format(
            {
                "partition_key_field": "letter",
                "db_name": database_name,
                "table_name": table_name,
                "s3_output_bucket": out_bucket_name,
            }
        )

        job_result = create_run_pyspark_job(job_code, GlueVersion=glue_version)
        snapshot.match("job-result", job_result)

        objects = aws_client.s3.list_objects_v2(Bucket=out_bucket_name)["Contents"]
        data = None
        # TODO enhance tests here
        for s3_object in objects:
            if s3_object["Key"].endswith(".parquet"):
                data = aws_client.s3.get_object(Bucket=out_bucket_name, Key=s3_object["Key"])[
                    "Body"
                ].read()
        assert data is not None

    @markers.aws.unknown
    # Note: Delta Lake SQL queries require `delta-core` version `0.7.0`+ (using Scala v2.12), hence
    #   older Glue versions 0.9/1.0/2.0 (using Scala v2.11) are not supported.
    #   See also: https://docs.aws.amazon.com/glue/latest/dg/aws-glue-programming-etl-format-delta-lake.html
    @pytest.mark.parametrize("glue_version", ["3.0", "4.0"])
    def test_pyspark_job_sql_with_delta_lake_table(
        self, glue_version, s3_create_bucket, create_run_pyspark_job, aws_client
    ):
        # create bucket and data folder
        bucket_name = s3_create_bucket()
        db_name = f"db_{short_uid()}"
        aws_client.s3.put_object(Bucket=bucket_name, Key="data/")

        job_script = (
            textwrap.dedent(
                """
        from pyspark import SparkContext, SparkConf
        from awsglue.context import GlueContext

        conf = SparkConf()
        conf.set("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
        conf.set("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
        sc = SparkContext.getOrCreate(conf=conf)
        glue_context = GlueContext(sc)
        spark = glue_context.spark_session

        # create database and table
        spark.sql("CREATE DATABASE <db_name>")
        spark.sql("CREATE TABLE <db_name>.table1 (name string, key long) USING delta PARTITIONED BY (key) LOCATION 's3://<bucket>/data/'")

        # create dataframe and write to table in S3
        df = spark.createDataFrame([("test1", 123)], ["name", "key"])
        additional_options = {"path": "s3://<bucket>/data/"}
        df.write \
            .format("delta") \
            .options(**additional_options) \
            .mode("append") \
            .partitionBy("key") \
            .saveAsTable("<db_name>.table1")

        # insert data via 'INSERT' query
        spark.sql("INSERT INTO <db_name>.table1 (name, key) VALUES ('test2', 456)")

        # get and print results, to run assertions further below
        result = spark.sql("SELECT * FROM <db_name>.table1")
        print("SQL result:", result.toJSON().collect())
        """
            )
            .replace("<bucket>", bucket_name)
            .replace("<db_name>", db_name)
        )
        # create job and start job run
        result = create_run_pyspark_job(
            job_script, command_name="glueetl", GlueVersion=glue_version
        )
        job_id = result["JobRun"]["Id"]

        # receive job logs, and run assertions
        log_events = get_filtered_log_events(aws_client, job_id=job_id)
        messages = [e["message"] for e in log_events]
        matching = [msg for msg in messages if "SQL result:" in msg]
        assert matching
        assert '{"name":"test1","key":123}' in matching[0]
        assert '{"name":"test2","key":456}' in matching[0]

        # assert that data exists in the bucket
        result = map_all_s3_objects(aws_client.s3, to_json=False, buckets=bucket_name)
        assert [key for key in result if "data/_delta_log/00000000000000000000.json" in key]
        assert [key for key in result if fnmatch(key, "*/data*/part-*.snappy.parquet")]

    @markers.aws.unknown
    @pytest.mark.parametrize("glue_version", ["4.0"])
    def test_create_dynamic_frame_from_catalog(
        self,
        glue_version,
        s3_create_bucket,
        glue_create_database,
        glue_create_table,
        create_run_pyspark_job,
        aws_client,
    ):
        # create bucket and data folder
        bucket_name = s3_create_bucket()
        db_name = f"db_{short_uid()}"
        table_name = f"t_{short_uid()}"
        aws_client.s3.put_object(Bucket=bucket_name, Key="data/")

        def _run_query(query: str):
            return run_athena_queries(
                query, timeout=150, athena_client=aws_client.athena, s3_client=aws_client.s3
            )

        _run_query(f"CREATE DATABASE {db_name}")

        storage_location = f"s3://{bucket_name}/prefix/"
        query = f"""
            CREATE TABLE {db_name}.{table_name} (c1 integer, c2 string, c3 double)
            ROW FORMAT SERDE 'org.apache.hive.hcatalog.data.JsonSerDe'
            STORED AS INPUTFORMAT 'org.apache.hadoop.mapred.TextInputFormat'
                OUTPUTFORMAT 'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat'
            LOCATION '{storage_location}'
            TBLPROPERTIES ('classification'='json', 'compressionType'='none', 'typeOfData'='file')
        """
        _run_query(query)

        def _check_catalog_populated():
            database = aws_client.glue.get_database(Name=db_name)["Database"]
            assert database
            table = aws_client.glue.get_table(DatabaseName=db_name, Name=table_name)["Table"]
            assert table

        # wait some time for the changes to get populated to Glue catalog
        retry(_check_catalog_populated, sleep=2, retries=20)

        # insert some data
        _run_query(f"INSERT INTO {db_name}.{table_name}(c1, c2, c3) VALUES (1, '2022-01-01', 2)")

        # run PySpark script that queries entries from the table via glue_context.create_dynamic_frame.from_catalog
        job_script = (
            textwrap.dedent(
                f"""
        from pyspark import SparkContext, SparkConf
        from awsglue.context import GlueContext

        conf = SparkConf()
        sc = SparkContext.getOrCreate(conf=conf)
        glue_context = GlueContext(sc)
        spark = glue_context.spark_session

        df = glue_context.create_dynamic_frame.from_catalog(database="{db_name}", table_name="{table_name}",
            additional_options={{"useSparkDataSource": True}}
        )
        print('!result', df.toDF().toJSON().collect())
        """
            )
            .replace("<bucket>", bucket_name)
            .replace("<db_name>", db_name)
        )
        # create job and start job run
        result = create_run_pyspark_job(
            job_script, command_name="glueetl", GlueVersion=glue_version
        )
        job_id = result["JobRun"]["Id"]

        # receive job logs, and run assertions
        log_events = get_filtered_log_events(aws_client, job_id=job_id)
        messages = [e["message"] for e in log_events]
        assert '!result [\'{"c1":1,"c2":"2022-01-01","c3":2.0}\']' in messages

    @markers.aws.unknown
    def test_run_scala_job(self, s3_create_bucket, s3_bucket, aws_client, create_run_spark_job):
        # define simple Glue Spark Scala job
        random_token = short_uid()
        scala_job = """
        import com.amazonaws.services.glue._
        import org.apache.spark._
        import org.apache.spark.sql._
        object TestJobScala {
          def main(sysArgs: Array[String]) {
            println("<token>")
            val spark: SparkContext = new SparkContext()
            val glueContext: GlueContext = new GlueContext(spark)
            val sparkSession: SparkSession = glueContext.getSparkSession
            println("DONE!")
          }
        }
        """.replace("<token>", random_token)

        # create job and start job run
        result = create_run_spark_job(
            to_bytes(scala_job),
            DefaultArguments={
                "--job-language": "scala",
                "--class": "TestJobScala",
                # TODO not yet supported
                # '--extra-jars': 's3://test/test.jar',
                # '--spark-event-logs-path': 's3://spark-jobs/spark-event-logs',
                # '--TempDir': 's3://spark-jobs/fx-localstack-wordcount-glue-job/temp-logs',
                # '--enable-continuous-cloudwatch-log': 'true', '--enable-continuous-log-filter': 'true',
                # '--successTopicArn': 'arn:aws:sns:us-east-1:000000000000:fx-localstack-success',
                # '--errorTopicArn': 'arn:aws:sns:us-east-1:000000000000:fx-localstack-error',
                # '--input_path': 's3://fx-localstack-wordcount-bucket/input/csv',
                # '--output_path': 's3://fx-localstack-wordcount-bucket/output'
            },
        )
        job_id = result["JobRun"]["Id"]

        # receive job logs, and run assertions
        log_events = get_filtered_log_events(aws_client, job_id=job_id)
        messages = [e["message"] for e in log_events]
        assert random_token in messages
        assert "DONE!" in messages

    @markers.aws.unknown
    @pytest.mark.parametrize("glue_version", ["0.9", "1.0", "2.0", "3.0", "4.0"])
    def test_pyspark_job_read_csv_from_s3(
        self, create_run_pyspark_job, s3_create_bucket, glue_version, aws_client
    ):
        # create file in S3
        bucket_name = s3_create_bucket()
        aws_client.s3.put_object(Bucket=bucket_name, Key="data.csv", Body=b"foo,bar,123")

        job_script = textwrap.dedent(
            """
        from pyspark.sql import SparkSession
        spark_session = SparkSession.builder.getOrCreate()
        spark_session.read.csv("s3a://<bucket_name>/data.csv").show()
        """
        ).replace("<bucket_name>", bucket_name)

        # create job and start job run
        result = create_run_pyspark_job(
            job_script,
            command_name="glueetl",
            GlueVersion=glue_version,
        )
        job_id = result["JobRun"]["Id"]

        # receive job logs, and run assertions
        log_events = get_filtered_log_events(aws_client, job_id=job_id)
        messages = [e["message"] for e in log_events]
        assert "|_c0|_c1|_c2|" in messages
        assert "|foo|bar|123|" in messages

    @markers.aws.unknown
    @pytest.mark.parametrize("glue_version", ["0.9", "1.0", "2.0", "3.0", "4.0"])
    def test_pyspark_job_read_data_from_postgres(
        self, create_run_pyspark_job, glue_version, aws_client, cleanups
    ):
        db_name = "test"
        master_user = "localstack"
        master_password = "password"
        table_name = "test"
        aws_client.rds.create_db_instance(
            DBInstanceIdentifier="test-instance",
            Engine="postgres",
            DBInstanceClass="db.t3.small",
            AllocatedStorage=5,
            MasterUsername=master_user,
            MasterUserPassword=master_password,
            DBName=db_name,
        )
        aws_client.rds.get_waiter("db_instance_available").wait(
            DBInstanceIdentifier="test-instance"
        )
        cleanups.append(
            lambda: aws_client.rds.delete_db_instance(DBInstanceIdentifier="test-instance")
        )

        response = aws_client.rds.describe_db_instances(DBInstanceIdentifier="test-instance")
        endpoint = response["DBInstances"][0]["Endpoint"]["Address"]
        port = response["DBInstances"][0]["Endpoint"]["Port"]

        conn = psycopg2.connect(
            dbname=db_name,
            user=master_user,
            password=master_password,
            host=endpoint,
            port=port,
        )
        cur = conn.cursor()
        cur.execute(f"DROP TABLE IF EXISTS {table_name};")
        cur.execute(
            f"CREATE TABLE {table_name} (id serial PRIMARY KEY, num integer, data varchar);"
        )
        cur.execute(f"INSERT INTO {table_name} (num, data) VALUES (100, 'abc')")
        conn.commit()
        cur.close()
        conn.close()

        print(f"Endpoint: {endpoint}, Port: {port}")
        job_script = (
            textwrap.dedent(
                """
        from pyspark.sql import SparkSession
        spark = SparkSession.builder.getOrCreate()
        connection_properties = {
            "user": "<user>",
            "password": "<password>",
            "driver": "org.postgresql.Driver"
        }
        df = spark.read.jdbc(
            url=f"jdbc:postgresql://<endpoint>:<port>/<database>",
            table="<table>",
            properties=connection_properties
        )
        df.show()
        """
            )
            .replace("<endpoint>", endpoint)
            .replace("<port>", str(port))
            .replace("<user>", master_user)
            .replace("<password>", master_password)
            .replace("<database>", db_name)
            .replace("<table>", table_name)
        )

        # create job and start job run
        result = create_run_pyspark_job(
            job_script,
            command_name="glueetl",
            GlueVersion=glue_version,
        )
        job_id = result["JobRun"]["Id"]

        log_events = get_filtered_log_events(aws_client, job_id=job_id)
        messages = [e["message"] for e in log_events]
        assert "|  1|100| abc|" in messages

    @markers.aws.unknown
    @pytest.mark.parametrize("glue_version", ["0.9", "1.0", "2.0", "3.0", "4.0"])
    def test_pyspark_job_read_data_from_redshift(
        self, create_run_pyspark_job, glue_version, aws_client, cleanups, redshift_create_cluster
    ):
        user = "localstack"
        password = "password"
        database = "test"
        cluster_id = short_uid()
        table_name = "test"

        result = redshift_create_cluster(
            DBName=database,
            NodeType="nt1",
            ClusterIdentifier=cluster_id,
            MasterUsername=user,
            MasterUserPassword=password,
        )
        aws_client.redshift.get_waiter("cluster_available").wait(ClusterIdentifier=cluster_id)

        cluster = result["Cluster"]
        port = cluster["Endpoint"]["Port"]
        address = cluster["Endpoint"]["Address"]

        with pg8000.connect(port=port, user=user, password=password, database=database) as conn:
            conn.autocommit = True
            with conn.cursor() as cursor:
                cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
                cursor.execute(f"CREATE TABLE {table_name}(id int)")
                cursor.execute(f"SELECT * FROM {table_name}")
                cursor.execute(f"INSERT INTO {table_name} VALUES (1)")
                cursor.execute(f"INSERT INTO {table_name} VALUES (2)")
                cursor.execute(f"INSERT INTO {table_name} VALUES (3)")

        driver = (
            "com.amazon.redshift.jdbc42.Driver"
            if glue_version == "4.0"
            else "com.amazon.redshift.jdbc41.Driver"
        )

        job_script = (
            textwrap.dedent(
                """
        from pyspark.sql import SparkSession
        spark = SparkSession.builder.getOrCreate()
        df = ((spark.read.format("jdbc").option("url", "jdbc:redshift://<address>:<port>/<database>;ssl=false")
         .option("dbtable", "<table>")
         .option("user", "<user>"))
        .option("password", "<password>")
        .option("driver", "<driver>")
        .load())
        df.show()
        """
            )
            .replace("<address>", address)
            .replace("<port>", str(port))
            .replace("<database>", database)
            .replace("<driver>", driver)
            .replace("<table>", table_name)
            .replace("<user>", user)
            .replace("<password>", password)
        )

        # create job and start job run
        result = create_run_pyspark_job(
            job_script,
            command_name="glueetl",
            GlueVersion=glue_version,
        )
        job_id = result["JobRun"]["Id"]

        log_events = get_filtered_log_events(aws_client, job_id=job_id)
        messages = [e["message"] for e in log_events]
        assert "|  1|" in messages
        assert "|  2|" in messages
        assert "|  3|" in messages

    @markers.aws.unknown
    def test_scala_spark_job_logger(
        self, s3_create_bucket, s3_bucket, aws_client, create_run_spark_job
    ):
        glue_version = "4.0"

        # define simple Glue Spark Scala job with LogManager
        scala_job = """
        import org.apache.spark.sql.SparkSession
        import org.apache.log4j.{Level, LogManager}
        object TestJobScala {
          def main(sysArgs: Array[String]) {
            // Configure the root logger level
            LogManager.getRootLogger.setLevel(Level.INFO)

            // Log some messages
            val logger = LogManager.getLogger(getClass)
            logger.info("DONE!")
            // FIXME: above line does not produce log output yet
            println("DONE!")
          }
        }"""

        # create job and start job run
        result = create_run_spark_job(
            to_bytes(scala_job),
            DefaultArguments={
                "--job-language": "scala",
                "--class": "TestJobScala",
            },
            GlueVersion=glue_version,
        )
        job_id = result["JobRun"]["Id"]

        # receive job logs, and run assertions
        log_events = get_filtered_log_events(aws_client, job_id=job_id)
        messages = [e["message"] for e in log_events]
        assert "DONE!" in messages
