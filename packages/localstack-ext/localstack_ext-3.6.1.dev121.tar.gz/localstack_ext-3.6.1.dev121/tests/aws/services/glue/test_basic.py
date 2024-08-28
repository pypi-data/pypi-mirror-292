import io
import json
import logging

import pytest
from localstack import config
from localstack.pro.core.aws.api.glue import (
    MetadataKeyValuePair,
    RegistryId,
    SchemaId,
    SchemaVersionNumber,
    SerDeInfo,
    StorageDescriptor,
    TableInput,
)
from localstack.pro.core.services.athena import query_utils
from localstack.pro.core.services.athena.query_utils import canonicalize_db_name
from localstack.pro.core.services.glue.models import DEFAULT_REGISTRY_NAME
from localstack.pro.core.utils.aws.aws_utils import run_athena_queries, run_athena_query
from localstack.testing.pytest import markers
from localstack.utils.aws import resources
from localstack.utils.strings import short_uid, to_bytes
from localstack.utils.sync import retry

from tests.aws.services.glue.conftest import (
    skip_bigdata_in_ci,
    wait_for_db_available_in_hive,
    wait_for_table_available_in_hive,
)

LOG = logging.getLogger(__name__)

TEST_TEMPLATE = """
AWSTemplateFormatVersion: '2010-09-09'
Resources:
  MyRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: "2012-10-17"
        Statement: []

  MyJob:
    Type: AWS::Glue::Job
    Properties:
      Command:
        Name: glueetl
        ScriptLocation: "s3://aws-glue-scripts//prod-job1"
      DefaultArguments:
        "--job-bookmark-option": "job-bookmark-enable"
      ExecutionProperty:
        MaxConcurrentRuns: 2
      MaxRetries: 0
      Name: cf-job1
      Role: !GetAtt MyRole.Arn

  MyDatabase:
    Type: AWS::Glue::Database
    Properties:
      CatalogId: !Ref AWS::AccountId
      DatabaseInput:
        Name: "dbCrawler"
        Description: "TestDatabaseDescription"
        LocationUri: "TestLocationUri"
        Parameters:
          key1 : "value1"
          key2 : "value2"

  MyClassifier:
    Type: AWS::Glue::Classifier
    Properties:
      GrokClassifier:
        Name: "CrawlerClassifier"
        Classification: "wikiData"
        GrokPattern: "%{NOTSPACE:language} %{NOTSPACE:page_title} %{NUMBER:hits:long} %{NUMBER:retrieved_size:long}"

  MyS3Bucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: crawlertesttarget
      AccessControl: BucketOwnerFullControl

  MyCrawler:
    Type: AWS::Glue::Crawler
    Properties:
      Name: testcrawler1
      Role: !GetAtt MyRole.Arn
      DatabaseName: !Ref MyDatabase
      Classifiers:
        - !Ref MyClassifier
      Targets:
        S3Targets:
          - Path: !Ref MyS3Bucket
      SchemaChangePolicy:
        UpdateBehavior: UPDATE_IN_DATABASE
        DeleteBehavior: LOG
      Schedule:
        ScheduleExpression: "cron(0/10 * ? * MON-FRI *)"

  MyJobTrigger:
    Type: AWS::Glue::Trigger
    Properties:
      Name: MyJobTrigger
      Type: CONDITIONAL
      Description: "Description for a conditional job trigger"
      Actions:
        - JobName: !Ref MyJob
          Arguments:
            "--job-bookmark-option": "job-bookmark-enable"
      Predicate:
        Conditions:
          - LogicalOperator: EQUALS
            JobName: !Ref MyJob
            State: SUCCEEDED

  MyTable:
    Type: AWS::Glue::Table
    Properties:
      CatalogId: !Ref AWS::AccountId
      DatabaseName: !Ref MyDatabase
      TableInput:
        Name: table1
        Description: Test table
        Owner: owner1

  MyWorkflow:
    Type: AWS::Glue::Workflow
    Properties:
      Name: wf1
      Description: Test workflow
      DefaultRunProperties:
        prop1: value1
"""


@skip_bigdata_in_ci
class TestGlueBasic:
    @markers.aws.unknown
    def test_create_table_with_empty_serde_properties(self, monkeypatch, aws_client):
        """
        This tests checks if a table in Hive is successfully created even if the SerdeProperties are an empty dict.
        """
        import pyarrow
        from pyarrow import parquet

        # resource names
        database_name = f"db-{short_uid()}"
        table_name = f"table-{short_uid()}"
        canonical_db_name = canonicalize_db_name(database_name)
        canonical_table_name = canonicalize_db_name(table_name)

        # create bucket
        bucket_name = f"b-{short_uid()}"
        resources.create_s3_bucket(bucket_name, s3_client=aws_client.s3)
        # create test file in S3
        s3_path = f"s3://{bucket_name}/{table_name}/"
        outstream = io.BytesIO()
        col_names = ["col1", "col2", "col3", "col4", "0col5&%_$", "timestamp"]
        arrays = [
            ["v1.1'", "v2.1"],
            ['v1.2"', "v2.2"],
            [r"v1.3\'", "v2.3"],
            [123, 45.6],
            ["", ""],
            [1646172627000000, 1652780743000000],
        ]
        table = pyarrow.Table.from_arrays(arrays, names=col_names)
        parquet.write_table(table, outstream)
        content = outstream.getvalue()
        aws_client.s3.upload_fileobj(
            io.BytesIO(to_bytes(content)),
            bucket_name,
            f"{table_name}/file.parquet",
        )

        # create the database in Glue
        aws_client.glue.create_database(DatabaseInput={"Name": database_name})
        wait_for_db_available_in_hive(database_name)

        # create the table in Glue
        # note: using BIGINT data type for local host mode, to avoid https://issues.apache.org/jira/browse/HIVE-15079:
        #   "java.lang.ClassCastException: class org.apache.hadoop.io.LongWritable cannot be
        #       cast to class org.apache.hadoop.hive.serde2.io.TimestampWritable"
        timestamp_type = "timestamp" if config.is_in_docker else "bigint"
        aws_client.glue.create_table(
            DatabaseName=database_name,
            TableInput=TableInput(
                Name=table_name,
                StorageDescriptor=StorageDescriptor(
                    Columns=[
                        {"Name": "col1", "Type": "string"},
                        {"Name": "col2", "Type": "string"},
                        {"Name": "col3", "Type": "string"},
                        {"Name": "col4", "Type": "double"},
                        {"Name": "0col5&%_$", "Type": "string"},
                        {"Name": "timestamp", "Type": timestamp_type},
                    ],
                    Location=s3_path,
                    InputFormat="org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat",
                    OutputFormat="org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat",
                    SerdeInfo=SerDeInfo(
                        SerializationLibrary="org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe",
                        # Test with empty parameters dict
                        Parameters={},
                    ),
                ),
                TableType="EXTERNAL_TABLE",
                Parameters={
                    "CreatedByJob": "springserve_cleanse_conform_s3_to_s3_ci",
                    "useGlueParquetWriter": "true",
                    "CreatedByJobRun": "springserve_cleanse_conform_s3_to_s3_ci",
                    "classification": "parquet",
                },
            ),
        )

        # wait until crawler has finished
        def _check(*_):
            # assert that data is available in Athena
            result = query_utils.execute_query(f"SHOW TABLES FROM {canonical_db_name}")
            assert len(result["rows"]) == 1
            assert result["rows"][0] == (canonical_table_name,)
            cols_str = ", ".join([f'"{col}"' for col in col_names])
            result = query_utils.execute_query(
                f"SELECT {cols_str} FROM {canonical_db_name}.{canonical_table_name}"
            )
            assert len(result["rows"]) == 2

        # Pulling the bigdata image or installing the bigdata components can take quite some time
        retry(_check, retries=300, sleep=2)

    @markers.aws.unknown
    def test_import_data_catalog(self, aws_client):
        # TODO this test seems to be failing in the old version as well

        bucket_name = f"b-{short_uid()}"
        resources.create_s3_bucket(bucket_name, s3_client=aws_client.s3)
        db_name = f"db{short_uid()}"

        run_athena_query(f"CREATE DATABASE {db_name}")
        queries = [
            f"CREATE EXTERNAL TABLE {db_name}.table1 (a1 Date, a2 STRING, a3 INT) LOCATION 's3://{bucket_name}/t1'",
            f"CREATE EXTERNAL TABLE {db_name}.table2 (a1 Date, a2 STRING, a3 INT) LOCATION 's3://{bucket_name}/t2'",
        ]
        results = run_athena_queries(queries)
        assert len(queries) == len(results)

        # import data catalog
        def _check_import():
            status = aws_client.glue.get_catalog_import_status()["ImportStatus"]
            assert status["ImportCompleted"] is True

        aws_client.glue.import_catalog_to_glue()

        # Pulling the bigdata image can take quite some time
        retry(_check_import, retries=300, sleep=2)

        # check databases/tables in Glue
        databases = aws_client.glue.get_databases().get("DatabaseList", [])
        assert len(databases) > 0
        database = aws_client.glue.get_database(Name=db_name)["Database"]
        assert database.get("Name") == db_name
        table = aws_client.glue.get_table(DatabaseName=db_name, Name="table1")["Table"]
        assert table.get("Name") == "table1"
        assert table.get("DatabaseName") == db_name
        assert "CreateTime" in table


class TestGlueCrud:
    @markers.aws.unknown
    def test_create_job_with_cloudformation(self, aws_client):
        # get jobs
        result = aws_client.glue.list_jobs()
        jobs_before = len(result["JobNames"])

        # create stack
        stack_name = "stack-%s" % short_uid()
        result = aws_client.cloudformation.create_stack(
            StackName=stack_name, TemplateBody=TEST_TEMPLATE
        )
        assert "StackId" in result
        aws_client.cloudformation.get_waiter("stack_create_complete").wait(StackName=stack_name)

        # assert job has been created
        result = aws_client.glue.list_jobs()
        jobs_after = len(result["JobNames"])
        # TODO: fix assertion, to make tests parallelizable!
        assert jobs_after == jobs_before + 1

    @markers.aws.unknown
    def test_job_crud(self, glue_create_job, aws_client):
        # Create a unique tag value
        tag_value = short_uid()

        # Create the first job
        job_name = glue_create_job(
            Role="r1",
            Command={"Name": "pythonshell", "ScriptLocation": "s3://test-bucket-name/job.py"},
            Tags={"Unique-Tag": tag_value},
        )
        job = aws_client.glue.get_job(JobName=job_name)
        assert job is not None
        assert "Job" in job
        assert job["Job"].get("Name") == job_name
        assert job["Job"].get("Role") == "r1"

        # Update the first job
        aws_client.glue.update_job(JobName=job_name, JobUpdate={"Role": "r2"})
        job = aws_client.glue.get_job(JobName=job_name)
        assert job is not None
        assert "Job" in job
        assert job["Job"].get("Name") == job_name
        assert job["Job"].get("Role") == "r2"

        # Create a second job
        job_name_2 = glue_create_job(
            Role="r1",
            Command={"Name": "pythonshell", "ScriptLocation": "s3://test-bucket-name/job.py"},
            Tags={"Unique-Tag": tag_value},
        )

        # Create a third job (without tags)
        glue_create_job(
            Role="r1",
            Command={"Name": "pythonshell", "ScriptLocation": "s3://test-bucket-name/job.py"},
        )

        # Test list jobs (with paging)
        list_jobs_1 = aws_client.glue.list_jobs(MaxResults=1, Tags={"Unique-Tag": tag_value})
        assert len(list_jobs_1["JobNames"]) == 1
        assert list_jobs_1["JobNames"][0] == job_name
        assert "NextToken" in list_jobs_1
        list_jobs_2 = aws_client.glue.list_jobs(
            MaxResults=1, NextToken=list_jobs_1["NextToken"], Tags={"Unique-Tag": tag_value}
        )
        assert len(list_jobs_2["JobNames"]) == 1
        assert list_jobs_2["JobNames"][0] == job_name_2

        # Test get_jobs
        get_jobs = aws_client.glue.get_jobs(MaxResults=1, NextToken=job_name)
        assert len(get_jobs["Jobs"]) == 1
        assert job_name in get_jobs["Jobs"][0]["Name"]

        aws_client.glue.delete_job(JobName=job_name)
        aws_client.glue.delete_job(JobName=job_name_2)

    @markers.aws.unknown
    @skip_bigdata_in_ci
    def test_job_runs_crud(self, glue_create_job, aws_client):
        job_name = glue_create_job(
            Role="r1",
            Command={
                "Name": "pythonshell",
                "ScriptLocation": "s3://non-existing-bucketname/job.py",
            },
        )
        job_runs = aws_client.glue.get_job_runs(JobName=job_name)
        assert len(job_runs["JobRuns"]) == 0
        job_run_id_1 = aws_client.glue.start_job_run(JobName=job_name)["JobRunId"]
        get_job_run = aws_client.glue.get_job_run(JobName=job_name, RunId=job_run_id_1)
        assert get_job_run["JobRun"]["Id"] == job_run_id_1
        aws_client.glue.start_job_run(JobName=job_name)
        get_job_runs = aws_client.glue.get_job_runs(JobName=job_name)
        assert len(get_job_runs["JobRuns"]) == 2

    @markers.aws.unknown
    def test_crawler_crud(self, glue_create_crawler, aws_client):
        crawler_count = len(aws_client.glue.get_crawlers()["Crawlers"])

        # Create
        crawler_name_1 = glue_create_crawler(
            Role="r1", Targets={"S3Targets": [{"Path": "s3://crawler1"}]}, Tags={"Spam": "Eggs"}
        )
        crawler_name_2 = glue_create_crawler(
            Role="r2", Targets={"S3Targets": [{"Path": "s3://crawler2"}]}
        )

        # Read
        crawler_1 = aws_client.glue.get_crawler(Name=crawler_name_1)
        assert crawler_1 is not None
        assert "Crawler" in crawler_1
        assert crawler_1["Crawler"].get("Role") == "r1"

        # Update
        aws_client.glue.update_crawler(Name=crawler_name_1, Role="r3")
        crawler_1 = aws_client.glue.get_crawler(Name=crawler_name_1)
        assert crawler_1 is not None
        assert "Crawler" in crawler_1
        assert crawler_1["Crawler"].get("Role") == "r3"

        # Get Crawlers
        get_crawlers_1 = aws_client.glue.get_crawlers(MaxResults=1)
        assert len(get_crawlers_1["Crawlers"]) == 1
        assert "NextToken" in get_crawlers_1
        get_crawlers_2 = aws_client.glue.get_crawlers()
        assert len(get_crawlers_2["Crawlers"]) == crawler_count + 2
        crawler_names = [crawler["Name"] for crawler in get_crawlers_2["Crawlers"]]
        assert crawler_name_1 in crawler_names
        assert crawler_name_2 in crawler_names

        # List
        list_crawlers_1 = aws_client.glue.list_crawlers(MaxResults=1)
        assert len(list_crawlers_1["CrawlerNames"]) == 1
        assert "NextToken" in list_crawlers_1
        list_crawlers_2 = aws_client.glue.list_crawlers()
        assert len(list_crawlers_2["CrawlerNames"]) == crawler_count + 2
        assert crawler_name_1 in list_crawlers_2["CrawlerNames"]
        assert crawler_name_2 in list_crawlers_2["CrawlerNames"]
        # List crawler by tag
        list_crawlers_3 = aws_client.glue.list_crawlers(Tags={"Spam": "Eggs"})
        assert len(list_crawlers_3["CrawlerNames"]) == 1
        assert crawler_name_1 in list_crawlers_3["CrawlerNames"]

        # Delete
        aws_client.glue.delete_crawler(Name=crawler_name_1)
        aws_client.glue.delete_crawler(Name=crawler_name_2)
        crawler_count_restored = len(aws_client.glue.get_crawlers()["Crawlers"])
        assert crawler_count_restored == crawler_count

    @markers.aws.unknown
    def test_registry_crud(self, glue_create_registry, aws_client):
        # Create
        reg_name_1 = glue_create_registry()
        reg_name_2 = glue_create_registry()

        # Update
        aws_client.glue.update_registry(
            RegistryId=RegistryId(RegistryName=reg_name_1), Description="Test"
        )

        # Read
        registry = aws_client.glue.get_registry(RegistryId=RegistryId(RegistryName=reg_name_1))
        assert registry is not None
        assert registry.get("RegistryName") == reg_name_1
        assert registry.get("Description") == "Test"

        # List
        result = aws_client.glue.list_registries()
        assert result is not None
        assert result.get("Registries") is not None
        found_registries = list(
            filter(
                lambda reg: reg["RegistryName"] in [reg_name_1, reg_name_2],
                result["Registries"],
            )
        )
        assert len(found_registries) == 2

        # Delete
        aws_client.glue.delete_registry(RegistryId=RegistryId(RegistryName=reg_name_1))
        aws_client.glue.delete_registry(RegistryId=RegistryId(RegistryName=reg_name_2))

    @markers.aws.unknown
    def test_schema_crud(self, glue_create_registry, glue_create_schema, aws_client):
        registry_name = glue_create_registry()
        # Create
        schema_name_1 = glue_create_schema(
            DataFormat="JSON", RegistryId=RegistryId(RegistryName=registry_name)
        )
        schema_name_2 = glue_create_schema(
            DataFormat="JSON", RegistryId=RegistryId(RegistryName=registry_name)
        )

        # Read
        schema = aws_client.glue.get_schema(
            SchemaId=SchemaId(SchemaName=schema_name_1, RegistryName=registry_name)
        )
        assert schema is not None
        assert schema.get("SchemaName") == schema_name_1
        schema_version_1 = aws_client.glue.get_schema_version(
            SchemaId=SchemaId(SchemaName=schema_name_1, RegistryName=registry_name)
        )
        schema_version_2 = aws_client.glue.get_schema_version(
            SchemaId=SchemaId(SchemaName=schema_name_1, RegistryName=registry_name),
            SchemaVersionId=schema_version_1.get("SchemaVersionId"),
        )
        schema_version_3 = aws_client.glue.get_schema_version(
            SchemaVersionId=schema_version_1.get("SchemaVersionId")
        )
        schema_version_1.pop("ResponseMetadata", None)
        schema_version_2.pop("ResponseMetadata", None)
        schema_version_3.pop("ResponseMetadata", None)
        assert schema_version_1 == schema_version_2 == schema_version_3

        # List
        schemas = aws_client.glue.list_schemas(RegistryId=RegistryId(RegistryName=registry_name))
        assert schemas is not None
        assert "Schemas" in schemas
        assert len(schemas["Schemas"]) == 2

        # Delete
        aws_client.glue.delete_schema(
            SchemaId=SchemaId(SchemaName=schema_name_1, RegistryName=registry_name)
        )
        aws_client.glue.delete_schema(
            SchemaId=SchemaId(SchemaName=schema_name_2, RegistryName=registry_name)
        )

    @markers.aws.unknown
    def test_schema_create_without_registry_returns_not_found(self, aws_client):
        with pytest.raises(aws_client.glue.exceptions.EntityNotFoundException):
            aws_client.glue.create_schema(
                SchemaName="test-name",
                DataFormat="JSON",
                RegistryId=RegistryId(RegistryName="non-existing-registry"),
            )

    @markers.aws.unknown
    def test_schema_version_metadata_crud(self, glue_create_schema, aws_client):
        person = '{"type":"record","namespace":"Test","name":"Person","fields":[{"name":"Name","type":"string"}]}'

        # Create
        schema_name = glue_create_schema(
            DataFormat="AVRO", Compatibility="NONE", SchemaDefinition=person
        )
        aws_client.glue.put_schema_version_metadata(
            SchemaId=SchemaId(SchemaName=schema_name, RegistryName=DEFAULT_REGISTRY_NAME),
            SchemaVersionNumber=SchemaVersionNumber(VersionNumber=1),
            MetadataKeyValue=MetadataKeyValuePair(
                MetadataKey="test-key", MetadataValue="test-value"
            ),
        )
        aws_client.glue.put_schema_version_metadata(
            SchemaId=SchemaId(SchemaName=schema_name, RegistryName=DEFAULT_REGISTRY_NAME),
            SchemaVersionNumber=SchemaVersionNumber(VersionNumber=1),
            MetadataKeyValue=MetadataKeyValuePair(
                MetadataKey="test-key", MetadataValue="test-value-2"
            ),
        )
        aws_client.glue.put_schema_version_metadata(
            SchemaId=SchemaId(SchemaName=schema_name, RegistryName=DEFAULT_REGISTRY_NAME),
            SchemaVersionNumber=SchemaVersionNumber(VersionNumber=1),
            MetadataKeyValue=MetadataKeyValuePair(
                MetadataKey="test-key-2", MetadataValue="test-value"
            ),
        )

        # Read without filtering
        query_result = aws_client.glue.query_schema_version_metadata(
            SchemaId=SchemaId(SchemaName=schema_name, RegistryName=DEFAULT_REGISTRY_NAME),
            SchemaVersionNumber=SchemaVersionNumber(VersionNumber=1),
        )
        assert query_result["MetadataInfoMap"]["test-key"]["MetadataValue"] == "test-value-2"
        other_metadata_list = query_result["MetadataInfoMap"]["test-key"]["OtherMetadataValueList"]
        assert len(other_metadata_list) == 1
        assert other_metadata_list[0]["MetadataValue"] == "test-value"

        # Read with matching filter on Metadata returns only one entry
        query_result = aws_client.glue.query_schema_version_metadata(
            SchemaId=SchemaId(SchemaName=schema_name, RegistryName=DEFAULT_REGISTRY_NAME),
            SchemaVersionNumber=SchemaVersionNumber(VersionNumber=1),
            MetadataList=[
                MetadataKeyValuePair(MetadataKey="test-key", MetadataValue="test-value-2")
            ],
        )
        assert query_result["MetadataInfoMap"]["test-key"]["MetadataValue"] == "test-value-2"
        other_metadata_list = query_result["MetadataInfoMap"]["test-key"]["OtherMetadataValueList"]
        assert len(other_metadata_list) == 0

        # Read with non-matching filter returns no entries
        query_result = aws_client.glue.query_schema_version_metadata(
            SchemaId=SchemaId(SchemaName=schema_name, RegistryName=DEFAULT_REGISTRY_NAME),
            SchemaVersionNumber=SchemaVersionNumber(VersionNumber=1),
            MetadataList=[
                MetadataKeyValuePair(MetadataKey="test-key", MetadataValue="Non-Existing-Value")
            ],
        )
        assert len(query_result["MetadataInfoMap"]) == 0

        # Delete
        aws_client.glue.remove_schema_version_metadata(
            SchemaId=SchemaId(SchemaName=schema_name, RegistryName=DEFAULT_REGISTRY_NAME),
            SchemaVersionNumber=SchemaVersionNumber(VersionNumber=1),
            MetadataKeyValue=MetadataKeyValuePair(
                MetadataKey="test-key", MetadataValue="test-value-2"
            ),
        )
        query_result = aws_client.glue.query_schema_version_metadata(
            SchemaId=SchemaId(SchemaName=schema_name, RegistryName=DEFAULT_REGISTRY_NAME),
            SchemaVersionNumber=SchemaVersionNumber(VersionNumber=1),
        )
        assert query_result["MetadataInfoMap"]["test-key"]["MetadataValue"] == "test-value"
        other_metadata_list = query_result["MetadataInfoMap"]["test-key"]["OtherMetadataValueList"]
        assert len(other_metadata_list) == 0

        # Delete the new main metadata element
        aws_client.glue.remove_schema_version_metadata(
            SchemaId=SchemaId(SchemaName=schema_name, RegistryName=DEFAULT_REGISTRY_NAME),
            SchemaVersionNumber=SchemaVersionNumber(VersionNumber=1),
            MetadataKeyValue=MetadataKeyValuePair(
                MetadataKey="test-key-2", MetadataValue="test-value"
            ),
        )
        query_result = aws_client.glue.query_schema_version_metadata(
            SchemaId=SchemaId(SchemaName=schema_name, RegistryName=DEFAULT_REGISTRY_NAME),
            SchemaVersionNumber=SchemaVersionNumber(VersionNumber=1),
            MetadataList=[
                MetadataKeyValuePair(MetadataKey="test-key-2", MetadataValue="test-value")
            ],
        )
        assert len(query_result["MetadataInfoMap"]) == 0

    @markers.aws.unknown
    def test_sec_config_crud(self, glue_create_sec_config, aws_client):
        sec_config_count = len(
            aws_client.glue.get_security_configurations()["SecurityConfigurations"]
        )

        # Create 1
        sec_config_name = glue_create_sec_config(
            EncryptionConfiguration={"S3Encryption": [{"S3EncryptionMode": "DISABLED"}]}
        )
        sec_config = aws_client.glue.get_security_configuration(Name=sec_config_name)
        assert sec_config is not None
        assert "SecurityConfiguration" in sec_config
        assert sec_config["SecurityConfiguration"].get("Name") == sec_config_name

        # Create 2
        sec_config_name_2 = glue_create_sec_config(
            EncryptionConfiguration={"S3Encryption": [{"S3EncryptionMode": "DISABLED"}]}
        )

        # List
        list_sec_configs_1 = aws_client.glue.get_security_configurations(MaxResults=1)
        assert len(list_sec_configs_1["SecurityConfigurations"]) == 1
        assert "NextToken" in list_sec_configs_1
        list_sec_configs_2 = aws_client.glue.get_security_configurations()
        assert len(list_sec_configs_2["SecurityConfigurations"]) == sec_config_count + 2
        sec_config_names = [
            sec_config["Name"] for sec_config in list_sec_configs_2["SecurityConfigurations"]
        ]
        assert sec_config_name in sec_config_names
        assert sec_config_name_2 in sec_config_names

        # Delete
        aws_client.glue.delete_security_configuration(Name=sec_config_name)
        aws_client.glue.delete_security_configuration(Name=sec_config_name_2)

    @markers.aws.unknown
    def test_resource_policy_crud(self, aws_client):
        try:
            policy_in_json = """{
              "Version": "2012-10-17",
              "Statement": [
                {
                  "Principal": {
                    "AWS": [
                      "arn:aws:iam::account-id:user/Alice"
                    ]
                  },
                  "Effect": "Allow",
                  "Action": [
                    "glue:*"
                  ],
                  "Resource": [
                    "arn:aws:glue:us-west-2:account-id1:*"
                  ]
                }
              ]
            }"""

            # Put
            aws_client.glue.put_resource_policy(PolicyInJson=policy_in_json)

            # Update
            policy_in_json_new = """{
              "Version": "2012-10-17",
              "Statement": [
                {
                  "Principal": {
                    "AWS": [
                      "arn:aws:iam::account-id:user/Bob"
                    ]
                  },
                  "Effect": "Allow",
                  "Action": [
                    "glue:*"
                  ],
                  "Resource": [
                    "arn:aws:glue:us-west-2:account-id2:*"
                  ]
                }
              ]
            }"""
            aws_client.glue.put_resource_policy(PolicyInJson=policy_in_json_new)

            # Get
            policy_in_json_get = aws_client.glue.get_resource_policy(
                ResourceArn="arn:aws:glue:us-west-2:account-id2:*"
            )["PolicyInJson"]
            assert json.loads(policy_in_json_new) == json.loads(policy_in_json_get)
        finally:
            aws_client.glue.delete_resource_policy(
                ResourceArn="arn:aws:glue:us-west-2:account-id2:*"
            )

    @markers.aws.unknown
    def test_classifier_crud(self, glue_create_csv_classifier, aws_client):
        classifier_count = len(aws_client.glue.get_classifiers()["Classifiers"])

        # Create 1
        classifier_name = glue_create_csv_classifier()["Name"]
        classifier = aws_client.glue.get_classifier(Name=classifier_name)
        assert classifier is not None
        assert "Classifier" in classifier
        assert classifier["Classifier"]["CsvClassifier"].get("Name") == classifier_name

        # Create 2
        classifier_name_2 = glue_create_csv_classifier()["Name"]

        # List
        list_classifiers_1 = aws_client.glue.get_classifiers(MaxResults=1)
        assert len(list_classifiers_1["Classifiers"]) == 1
        assert "NextToken" in list_classifiers_1
        list_classifiers_2 = aws_client.glue.get_classifiers()
        assert len(list_classifiers_2["Classifiers"]) == classifier_count + 2
        classifier_names = [
            classifier.get("CsvClassifier", {}).get("Name")
            for classifier in list_classifiers_2["Classifiers"]
        ]
        assert classifier_name in classifier_names
        assert classifier_name_2 in classifier_names

        # Delete
        aws_client.glue.delete_classifier(Name=classifier_name)
        aws_client.glue.delete_classifier(Name=classifier_name_2)

    @markers.aws.unknown
    def test_connection_crud(self, glue_create_connection, aws_client):
        connection_count = len(aws_client.glue.get_connections()["ConnectionList"])

        # Create 1
        connection_name = glue_create_connection(
            ConnectionInput={
                "ConnectionType": "SFTP",
                "ConnectionProperties": {"HOST": "localhost"},
            }
        )["Name"]
        connection = aws_client.glue.get_connection(Name=connection_name)
        assert connection is not None
        assert "Connection" in connection
        assert connection["Connection"].get("Name") == connection_name

        # Create 2
        connection_name_2 = glue_create_connection(
            ConnectionInput={
                "ConnectionType": "SFTP",
                "ConnectionProperties": {"HOST": "localhost"},
            }
        )["Name"]

        # Update 1
        aws_client.glue.update_connection(
            Name=connection_name,
            ConnectionInput={
                "Name": connection_name,
                "ConnectionType": "SFTP",
                "ConnectionProperties": {"HOST": "not-localhost-anymore"},
            },
        )
        connection = aws_client.glue.get_connection(Name=connection_name)
        assert connection is not None and "Connection" in connection
        assert connection["Connection"].get("ConnectionProperties") == {
            "HOST": "not-localhost-anymore"
        }

        # List
        list_connections_1 = aws_client.glue.get_connections(MaxResults=1)
        assert len(list_connections_1["ConnectionList"]) == 1
        assert "NextToken" in list_connections_1
        list_connections_2 = aws_client.glue.get_connections()
        assert len(list_connections_2["ConnectionList"]) == connection_count + 2
        connection_names = [
            connection["Name"] for connection in list_connections_2["ConnectionList"]
        ]
        assert connection_name in connection_names
        assert connection_name_2 in connection_names

        # Delete
        aws_client.glue.delete_connection(ConnectionName=connection_name)
        aws_client.glue.delete_connection(ConnectionName=connection_name_2)

    @markers.aws.unknown
    def test_trigger_crud(self, glue_create_trigger, aws_client):
        # Create
        trigger_name_1 = glue_create_trigger(
            Type="ON_DEMAND", Actions=[{"JobName": "test-job-name"}]
        )
        trigger_name_2 = glue_create_trigger(
            Type="ON_DEMAND", Actions=[{"JobName": "test-job-name_2"}]
        )
        trigger = aws_client.glue.get_trigger(Name=trigger_name_1)
        assert trigger is not None
        assert "Trigger" in trigger
        assert trigger["Trigger"].get("Name") == trigger_name_1

        # Update
        aws_client.glue.update_trigger(
            Name=trigger_name_1, TriggerUpdate={"Actions": [{"JobName": "test-job-name_1"}]}
        )

        # Read
        updated_trigger = aws_client.glue.get_trigger(Name=trigger_name_1)["Trigger"]
        assert updated_trigger["Name"] == trigger_name_1
        assert updated_trigger["Actions"] == [{"JobName": "test-job-name_1"}]

        # Get Triggers
        get_triggers = aws_client.glue.get_triggers(MaxResults=1)
        assert len(get_triggers["Triggers"]) == 1
        assert "NextToken" in get_triggers

        get_triggers = aws_client.glue.get_triggers()
        trigger_names = [trigger["Name"] for trigger in get_triggers["Triggers"]]
        assert trigger_name_1 in trigger_names
        assert trigger_name_2 in trigger_names

    @skip_bigdata_in_ci
    @markers.aws.unknown
    def test_database_crud(self, glue_create_database, aws_client):
        database_count = len(aws_client.glue.get_databases()["DatabaseList"])

        # Create 1
        database_name_1 = glue_create_database(DatabaseInput={"Description": "test-desc"})["Name"]
        database = aws_client.glue.get_database(Name=database_name_1)
        assert database is not None
        assert "Database" in database
        assert database["Database"].get("Description") == "test-desc"

        # Create 2
        database_name_2 = glue_create_database()["Name"]

        # Update
        aws_client.glue.update_database(
            Name=database_name_1,
            DatabaseInput={"Name": database_name_1, "Description": "test-description-updated"},
        )
        database = aws_client.glue.get_database(Name=database_name_1)
        assert database is not None
        assert "Database" in database
        assert database["Database"].get("Description") == "test-description-updated"

        # List (Paging)
        list_databases = aws_client.glue.get_databases(MaxResults=1)
        assert len(list_databases["DatabaseList"]) == 1
        assert "NextToken" in list_databases
        list_databases_2 = aws_client.glue.get_databases(
            MaxResults=1, NextToken=list_databases["NextToken"]
        )
        assert len(list_databases_2["DatabaseList"]) == 1

        # List
        list_databases = aws_client.glue.get_databases()
        assert len(list_databases["DatabaseList"]) == database_count + 2

        # Delete
        aws_client.glue.delete_database(Name=database_name_1)
        aws_client.glue.delete_database(Name=database_name_2)

    @skip_bigdata_in_ci
    @markers.aws.unknown
    def test_table_crud(self, glue_create_database, glue_create_table, aws_client):
        database_name = glue_create_database()["Name"]

        # Create
        table_name_1 = glue_create_table(
            DatabaseName=database_name, TableInput={"Description": "test-desc"}
        )["Name"]

        # Create 2
        table_name_2 = glue_create_table(DatabaseName=database_name)["Name"]

        # Read
        table = aws_client.glue.get_table(DatabaseName=database_name, Name=table_name_1)
        assert table is not None
        assert "Table" in table
        assert table["Table"].get("Description") == "test-desc"

        # Update
        aws_client.glue.update_table(
            DatabaseName=database_name, TableInput={"Name": table_name_1, "Description": "updated"}
        )
        table = aws_client.glue.get_table(DatabaseName=database_name, Name=table_name_1)
        assert table is not None
        assert "Table" in table
        assert table["Table"].get("Description") == "updated"

        # List (Paging)
        list_tables = aws_client.glue.get_tables(DatabaseName=database_name, MaxResults=1)
        assert len(list_tables["TableList"]) == 1
        assert "NextToken" in list_tables
        list_tables_2 = aws_client.glue.get_tables(
            DatabaseName=database_name, MaxResults=1, NextToken=list_tables["NextToken"]
        )
        assert len(list_tables_2["TableList"]) == 1

        # List
        list_tables = aws_client.glue.get_tables(DatabaseName=database_name)
        assert len(list_tables["TableList"]) == 2

        # Delete
        aws_client.glue.delete_table(DatabaseName=database_name, Name=table_name_1)
        aws_client.glue.delete_table(DatabaseName=database_name, Name=table_name_2)
        with pytest.raises(Exception) as e:
            aws_client.glue.delete_table(DatabaseName=database_name, Name=table_name_2)
        e.match("EntityNotFoundException")

    @skip_bigdata_in_ci
    @pytest.mark.parametrize("location_prefix", ["s3://", "s3a://", ""])
    @pytest.mark.parametrize("location_suffix", ["/", ""])
    @markers.aws.validated
    def test_create_table_with_s3_location(
        self,
        location_prefix,
        location_suffix,
        glue_create_database,
        glue_create_table,
        s3_bucket,
        aws_client,
    ):
        database_name = glue_create_database()["Name"]

        location = f"{location_prefix}{s3_bucket}{location_suffix}"
        table = glue_create_table(
            DatabaseName=database_name,
            TableInput={
                "StorageDescriptor": {
                    "Columns": [{"Name": "col1", "Type": "string"}],
                    "Location": location,
                    "InputFormat": "org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat",
                    "OutputFormat": "org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat",
                    "SerdeInfo": {
                        "SerializationLibrary": "org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe",
                    },
                },
                "TableType": "EXTERNAL_TABLE",
            },
        )
        table_name = table["Name"]

        # wait for table to become available
        if location_prefix and location_suffix:
            wait_for_table_available_in_hive(database_name, table_name)

        # Ensure defaults are assumed for certain attributes if not explicitly provided in CreateTable
        table = aws_client.glue.get_table(DatabaseName=database_name, Name=table_name)["Table"]
        assert table["Retention"] == 0
        assert not table["StorageDescriptor"]["Compressed"]
        assert table["StorageDescriptor"]["NumberOfBuckets"] == 0
        assert not table["StorageDescriptor"]["StoredAsSubDirectories"]

        # TODO: we should think about adding query rewriting, to allow querying tables with non-canonical names
        table_name = canonicalize_db_name(table_name)
        result = run_athena_queries(
            f'SELECT * FROM "{table_name}"',
            QueryExecutionContext={"Database": database_name, "Catalog": "AwsDataCatalog"},
            WorkGroup="primary",
            athena_client=aws_client.athena,
            s3_client=aws_client.s3,
        )

        if (location.startswith("s3://") or location.startswith("s3a://")) and location.endswith(
            "/"
        ):
            assert result[0]
            assert result[0]["ResultSet"]["Rows"][0]["Data"] == [{"VarCharValue": "col1"}]
        else:
            # all other locations are invalid and should yield an error / empty result
            assert result == [None]

    @markers.aws.unknown
    def test_workflow_crud(self, glue_create_workflow, aws_client):
        workflow_count = len(aws_client.glue.list_workflows()["Workflows"])

        # Create 1
        workflow_name = glue_create_workflow()
        workflow = aws_client.glue.get_workflow(Name=workflow_name)
        assert workflow is not None
        assert "Workflow" in workflow
        assert workflow["Workflow"].get("Name") == workflow_name

        # Create 2
        workflow_name_2 = glue_create_workflow()

        # List
        list_workflows_1 = aws_client.glue.list_workflows(MaxResults=1)
        assert len(list_workflows_1["Workflows"]) == 1
        assert "NextToken" in list_workflows_1
        list_workflows_2 = aws_client.glue.list_workflows()
        assert len(list_workflows_2["Workflows"]) == workflow_count + 2
        assert workflow_name in list_workflows_2["Workflows"]
        assert workflow_name_2 in list_workflows_2["Workflows"]

        # Delete
        aws_client.glue.delete_workflow(Name=workflow_name)
        aws_client.glue.delete_workflow(Name=workflow_name_2)

    @skip_bigdata_in_ci
    @markers.aws.unknown
    def test_partitions_crud(self, glue_create_database, glue_create_table, aws_client):
        database_name = glue_create_database()["Name"]
        table_name = glue_create_table(DatabaseName=database_name)["Name"]

        partition_values = ["value1", "value2"]
        try:
            # Create
            aws_client.glue.create_partition(
                DatabaseName=database_name,
                TableName=table_name,
                PartitionInput={"Values": partition_values},
            )

            # Update
            aws_client.glue.update_partition(
                DatabaseName=database_name,
                TableName=table_name,
                PartitionValueList=["value1", "value2"],
                PartitionInput={"Parameters": {"Key": "Value"}},
            )

            # Get
            partition = aws_client.glue.get_partition(
                DatabaseName=database_name, TableName=table_name, PartitionValues=partition_values
            )
            assert partition is not None
            assert "Partition" in partition
            assert partition["Partition"].get("Parameters") == {"Key": "Value"}

            # List
            partitions = aws_client.glue.get_partitions(
                DatabaseName=database_name, TableName=table_name
            )["Partitions"]
            assert len(partitions) == 1
            assert partitions[0]["Values"] == partition_values
        finally:
            aws_client.glue.delete_partition(
                DatabaseName=database_name,
                TableName=table_name,
                PartitionValues=["value1", "value2"],
            )

    @skip_bigdata_in_ci
    @markers.aws.unknown
    def test_partition_indexes_crud(self, glue_create_database, glue_create_table, aws_client):
        database_name = glue_create_database()["Name"]
        table_name = glue_create_table(DatabaseName=database_name)["Name"]

        keys = ["key1", "key2"]
        index_name = "IndexName1"
        try:
            # Create
            aws_client.glue.create_partition_index(
                DatabaseName=database_name,
                TableName=table_name,
                PartitionIndex={"Keys": keys, "IndexName": index_name},
            )

            # List
            partition_indexes = aws_client.glue.get_partition_indexes(
                DatabaseName=database_name, TableName=table_name
            )["PartitionIndexDescriptorList"]
            assert len(partition_indexes) == 1
            assert partition_indexes[0].get("Keys") == [{"Name": "key1"}, {"Name": "key2"}]
            assert partition_indexes[0].get("IndexName") == index_name
        finally:
            aws_client.glue.delete_partition_index(
                DatabaseName=database_name, TableName=table_name, IndexName=index_name
            )
