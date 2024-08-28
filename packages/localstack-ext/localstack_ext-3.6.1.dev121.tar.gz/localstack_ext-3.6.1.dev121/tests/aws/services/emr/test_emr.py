import json
import os
import subprocess
import textwrap
from typing import List, Tuple

import pytest
from localstack import config
from localstack.pro.core.constants import S3_ASSETS_BUCKET_URL
from localstack.pro.core.utils.bigdata.bigdata_utils import get_main_endpoint_from_bigdata_container
from localstack.testing.pytest import markers
from localstack.utils import testutil
from localstack.utils.aws import resources
from localstack.utils.files import load_file, mkdir, save_file
from localstack.utils.http import download
from localstack.utils.run import is_command_available, run
from localstack.utils.strings import short_uid, to_bytes
from localstack.utils.sync import retry

from tests.aws.fixtures import should_skip_bigdata_tests

# test JAR file used for a Hadoop EMR job that copies a file between S3 buckets
THIS_DIR = os.path.dirname(__file__)
TEST_JAR_NAME = "localstack-emr-test-0.1.0{profile}-shaded.jar"
TEST_JAR_FILE = os.path.join(THIS_DIR, "", "target", TEST_JAR_NAME)
TEST_JAR_URL_BASE = S3_ASSETS_BUCKET_URL

TEST_FILE_CONTENT = {"foo": "bar"}
TEST_FILE_KEY = "test.json"


@pytest.fixture(scope="class", autouse=True)
def setup_class():
    if should_skip_bigdata_tests():
        return
    if is_command_available("mvn"):
        emr_dir = os.path.join(THIS_DIR, "")
        run([os.path.join(emr_dir, "build.sh")], cwd=emr_dir, outfile=subprocess.PIPE)
    else:
        for profile_suffix in ("", "-scala11", "-scala12"):
            jar_file = TEST_JAR_FILE.format(profile=profile_suffix)
            jar_name = TEST_JAR_NAME.format(profile=profile_suffix)
            mkdir(os.path.dirname(jar_file))
            test_jar_url = f"{TEST_JAR_URL_BASE}/{jar_name}"
            download(test_jar_url, jar_file)


@pytest.fixture()
def create_cluster(aws_client):
    def _create(steps: List = None) -> Tuple[str, str]:
        client = aws_client.emr
        instances = {
            "MasterInstanceType": "i1",
            "SlaveInstanceType": "i2",
            "InstanceCount": 1,
            "InstanceGroups": [
                {
                    "Name": "g1",
                    "Market": "ON_DEMAND",
                    "InstanceRole": "r1",
                    "InstanceType": "type-1",
                    "InstanceCount": 1,
                }
            ],
        }
        actions = []
        applications = [{"Name": "Spark"}]
        configs = []
        steps = steps or []
        cluster_name = f"c-{short_uid()}"
        response = client.run_job_flow(
            Name=cluster_name,
            Instances=instances,
            Steps=steps,
            BootstrapActions=actions,
            Applications=applications,
            Configurations=configs,
        )
        assert response["ResponseMetadata"]["HTTPStatusCode"] == 200
        return response["JobFlowId"], cluster_name

    yield _create


def _get_target_endpoint_from_emr_script() -> str:
    return f"http://{get_main_endpoint_from_bigdata_container()}:{config.GATEWAY_LISTEN[0].port}"


class TestEmrCrud:
    @markers.aws.unknown
    def test_instance_fleets(self, create_cluster, aws_client):
        cluster_id, _ = create_cluster()

        fleet_id = aws_client.emr.add_instance_fleet(
            ClusterId=cluster_id, InstanceFleet={"Name": "fleet1", "InstanceFleetType": "MASTER"}
        )["InstanceFleetId"]

        result = aws_client.emr.list_instance_fleets(ClusterId=cluster_id)
        assert result["InstanceFleets"]
        assert result["InstanceFleets"][0]["Name"] == "fleet1"

        aws_client.emr.modify_instance_fleet(
            ClusterId=cluster_id,
            InstanceFleet={
                "InstanceFleetId": fleet_id,
                "TargetOnDemandCapacity": 3,
                "TargetSpotCapacity": 4,
            },
        )
        result = aws_client.emr.list_instance_fleets(ClusterId=cluster_id)
        assert result["InstanceFleets"]
        assert result["InstanceFleets"][0]["TargetOnDemandCapacity"] == 3
        assert result["InstanceFleets"][0]["TargetSpotCapacity"] == 4

        with pytest.raises(Exception):
            aws_client.emr.modify_instance_fleet(
                ClusterId=cluster_id,
                InstanceFleet={
                    "InstanceFleetId": "invalid-id",
                    "TargetOnDemandCapacity": 2,
                    "TargetSpotCapacity": 1,
                },
            )

    @markers.aws.unknown
    def test_auto_termination_policies(self, create_cluster, aws_client):
        cluster_id, _ = create_cluster()

        # put policy
        aws_client.emr.put_auto_termination_policy(
            ClusterId=cluster_id, AutoTerminationPolicy={"IdleTimeout": 123}
        )
        response = aws_client.emr.get_auto_termination_policy(ClusterId=cluster_id)
        assert response["AutoTerminationPolicy"] == {"IdleTimeout": 123}

        # remove policy
        aws_client.emr.remove_auto_termination_policy(ClusterId=cluster_id)
        response = aws_client.emr.get_auto_termination_policy(ClusterId=cluster_id)
        assert not response.get("AutoTerminationPolicy")


@pytest.mark.skipif(
    should_skip_bigdata_tests(), reason="Test requires bigdata container - skipping in CI"
)
class TestEmrJobs:
    @markers.aws.unknown
    def test_create_cluster(self, create_cluster, aws_client):
        # get cluster steps
        steps, target_bucket = self._create_cluster_steps(aws_client.s3)

        # create cluster
        cluster_id, cluster_name = create_cluster(steps)

        # assert cluster has been created
        clusters = aws_client.emr.list_clusters()["Clusters"]
        assert [cl for cl in clusters if cl["Name"] == cluster_name]

        # assert Hadoop job has been run and S3 file has been copied
        self._assert_file_copied(aws_client.s3, target_bucket)

    @markers.aws.unknown
    def test_add_cluster_step(self, create_cluster, aws_client):
        # create cluster
        cluster_id, cluster_name = create_cluster()

        # add steps
        steps, target_bucket = self._create_cluster_steps(aws_client.s3)
        aws_client.emr.add_job_flow_steps(JobFlowId=cluster_id, Steps=steps)

        # assert Hadoop job has been run and S3 file has been copied
        self._assert_file_copied(aws_client.s3, target_bucket)

        # assert that the step is in state "COMPLETED"
        self._assert_job_completed(aws_client.emr, cluster_id)

    @pytest.mark.parametrize("script_lang", ["python", "scala11", "scala12"])
    @markers.aws.unknown
    def test_run_spark_submit_job(
        self, script_lang, s3_create_bucket, create_cluster, s3_bucket, aws_client
    ):
        # create cluster
        cluster_id, cluster_name = create_cluster()
        s3_result_bucket = s3_create_bucket()

        job_args = []
        if script_lang == "python":
            # create job script
            job_s3_key = "foo/test.py"
            endpoint_url = _get_target_endpoint_from_emr_script()
            script = textwrap.dedent(
                f"""
            import boto3
            client = boto3.client("s3", endpoint_url="{endpoint_url}")
            client.put_object(Bucket="{s3_result_bucket}", Key="job_done", Body=b"")
            """
            )
            aws_client.s3.put_object(Bucket=s3_bucket, Key=job_s3_key, Body=to_bytes(script))
        else:
            job_s3_key = "test-job.jar"
            jar_file = TEST_JAR_FILE.format(profile=f"-{script_lang}")
            aws_client.s3.put_object(
                Bucket=s3_bucket, Key=job_s3_key, Body=load_file(jar_file, mode="rb")
            )
            job_args = ["--class", "TestJobScala"]

        # define job step
        steps = [
            {
                "Name": "Spark application",
                "ActionOnFailure": "CONTINUE",
                "HadoopJarStep": {
                    "Jar": "command-runner.jar",
                    "Args": [
                        "spark-submit",
                        "--deploy-mode",
                        "client",
                        *job_args,
                        f"s3://{s3_bucket}/{job_s3_key}",
                        s3_result_bucket,
                    ],
                },
            }
        ]
        aws_client.emr.add_job_flow_steps(JobFlowId=cluster_id, Steps=steps)

        # assert that the step is in state "COMPLETED"
        self._assert_job_completed(aws_client.emr, cluster_id)

        # assert Hadoop job has been run and S3 result bucket has been created
        result = aws_client.s3.head_object(Bucket=s3_result_bucket, Key="job_done")
        assert result.get("ETag")

    def _assert_file_copied(self, s3_client, target_bucket: str):
        def check_copied():
            objects = testutil.map_all_s3_objects(buckets=[target_bucket], s3_client=s3_client)
            assert list(objects.values()) == [TEST_FILE_CONTENT]
            assert list(objects.keys())[0].endswith(f"/{TEST_FILE_KEY}")

        retry(check_copied, retries=240, sleep=1)

    def _assert_job_completed(self, emr_client, cluster_id):
        def _completed():
            result = emr_client.list_steps(ClusterId=cluster_id)["Steps"]
            for step in result:
                assert step["Status"]["State"] == "COMPLETED"

        retry(_completed, retries=10, sleep=1)

    def _create_cluster_steps(self, s3_client):
        # create bucket and copy jar file
        bucket_name1 = f"bucket-{short_uid()}"
        bucket_name2 = f"bucket-{short_uid()}"
        jar_key = "test.jar"
        resources.create_s3_bucket(bucket_name1)
        resources.create_s3_bucket(bucket_name2)
        # copy JAR file and test file to S3
        s3_client.put_object(
            Bucket=bucket_name1, Key=TEST_FILE_KEY, Body=json.dumps(TEST_FILE_CONTENT)
        )
        jar_file = TEST_JAR_FILE.format(profile="-scala11")
        if should_skip_bigdata_tests() and not os.path.exists(jar_file):
            # make sure to store a dummy file to avoid processing issues downstream
            save_file(jar_file, b"")
        s3_client.put_object(Bucket=bucket_name2, Key=jar_key, Body=load_file(jar_file, mode="rb"))

        steps = [
            {
                "Name": "file-copy-step",
                "ActionOnFailure": "CONTINUE",
                "HadoopJarStep": {
                    "Jar": f"s3://{bucket_name2}/{jar_key}",
                    "Args": [TEST_FILE_KEY, bucket_name1, bucket_name2],
                },
            }
        ]
        return [steps, bucket_name2]
