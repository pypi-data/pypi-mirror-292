import os
from pathlib import Path

import pytest
import requests
from localstack.pro.core.services.mwaa.provider import (
    AIRFLOW_ADMIN_PASS,
    AIRFLOW_ADMIN_USER,
    AIRFLOW_VERSIONS,
    CONTAINER_NAME_PATTERN,
)
from localstack.testing.pytest import markers
from localstack.utils.aws import arns
from localstack.utils.bootstrap import in_ci
from localstack.utils.docker_utils import DOCKER_CLIENT
from localstack.utils.strings import short_uid, to_bytes, to_str
from localstack.utils.sync import retry

TEST_DAG_CODE_TEMPLATE = """
from airflow.decorators import dag, task
from airflow.utils.dates import days_ago
@dag(schedule_interval=None, start_date=days_ago(2), catchup=False)
def sample_dag{dag_id}():
    @task
    def task_1():
        print('task 1')
    @task
    def task_2(value):
        print('task 2')
    return task_2(task_1())
dag = sample_dag{dag_id}()
"""

BASEDIR = os.path.abspath(os.path.dirname(__file__))

S3_DAGS_PATH = "/dags"


@markers.aws.unknown
def test_list_environments(aws_client):
    # simple smoke test to assert that the provider is available, without creating an actual environment
    result = aws_client.mwaa.list_environments()
    assert isinstance(result.get("Environments"), list)


# TODO@viren: conditionally run these tests like we do with Big Data
# https://github.com/localstack/localstack-ext/blob/master/.github/workflows/bigdata-tests.yml
@pytest.mark.skipif(in_ci(), reason="Long-running MWAA tests currently disabled in CI")
class TestMWAA:
    # Some tests are not parametrised for older Airflow versions because
    # they rely on Airflow REST APIs which are only available on later versions.

    @pytest.mark.parametrize("airflow_version", AIRFLOW_VERSIONS)
    @markers.aws.unknown
    def test_dag_dependencies(
        self, mwaa_env_factory, s3_bucket, airflow_version, aws_client, account_id, region_name
    ):
        # create S3 bucket
        s3_bucket_arn = arns.s3_bucket_arn(s3_bucket)
        s3_requirements_path = "requirements.txt"

        # create Airflow environment
        env_name = f"env-{short_uid()}"
        mwaa_env_factory(env_name, S3_DAGS_PATH, s3_bucket_arn, airflow_version)

        req = "antigravity==0.1"

        # Put requirements file in S3 bucket
        aws_client.s3.put_object(Bucket=s3_bucket, Key=s3_requirements_path, Body=to_bytes(req))

        # Ensure the dependency is installed in the container
        def _assert_req():
            container_name = CONTAINER_NAME_PATTERN.format(
                account_id=account_id, region_name=region_name, env_name=env_name
            )
            result = DOCKER_CLIENT.exec_in_container(container_name, ["sh", "-c", "pip freeze"])
            stdout = to_str(result[0])
            assert req in stdout

        retry(_assert_req, retries=20, sleep=3)

    @pytest.mark.parametrize(
        "airflow_version", ("2.0.2", "2.2.2", "2.4.3", "2.5.1", "2.6.3", "2.7.2", "2.8.1")
    )
    @markers.aws.unknown
    def test_dags(self, mwaa_env_factory, s3_bucket, airflow_version, aws_client):
        # create S3 bucket
        s3_bucket_arn = arns.s3_bucket_arn(s3_bucket)

        # create Airflow environment
        env_name = f"env-{short_uid()}"
        webserver_url = mwaa_env_factory(env_name, S3_DAGS_PATH, s3_bucket_arn, airflow_version)

        # put dag in bucket root directory
        aws_client.s3.put_object(
            Bucket=s3_bucket,
            Key=f"{S3_DAGS_PATH.lstrip('/')}/dag1.py",
            Body=to_bytes(TEST_DAG_CODE_TEMPLATE.format(dag_id="1")),
        )

        # put the dag in a nested directory inside the bucket
        aws_client.s3.put_object(
            Bucket=s3_bucket,
            Key=f"{S3_DAGS_PATH.lstrip('/')}/nested/dag2.py",
            Body=to_bytes(TEST_DAG_CODE_TEMPLATE.format(dag_id="2")),
        )

        # assert that DAG has been created from S3 files
        def _assert_dag_created():
            response = requests.get(
                webserver_url + "/api/v1/dags", auth=(AIRFLOW_ADMIN_USER, AIRFLOW_ADMIN_PASS)
            )
            dags = response.json()["dags"]
            dags = [dag for dag in dags if dag["dag_id"].startswith("sample_dag")]
            assert len(dags) == 2
            assert dags[0]["dag_id"] == "sample_dag1"
            assert dags[1]["dag_id"] == "sample_dag2"

        retry(_assert_dag_created, retries=20, sleep=3)

    @pytest.mark.parametrize(
        "airflow_version", ("2.2.2", "2.4.3", "2.5.1", "2.6.3", "2.7.2", "2.8.1")
    )
    @pytest.mark.parametrize(
        "plugin_type,expected_plugin_name",
        [("plugin_v2_flat", "virtual_python_plugin"), ("plugin_v2_nested", "my_airflow_plugin")],
    )
    @markers.aws.unknown
    def test_custom_plugins(
        self,
        mwaa_env_factory,
        s3_bucket,
        airflow_version,
        plugin_type,
        expected_plugin_name,
        aws_client,
    ):
        # Airflow plugins can be a single python file (flat), or a python module with several files (nested)
        # Both must be zipped and named `plugins.zip`

        # create S3 bucket
        s3_bucket_arn = arns.s3_bucket_arn(s3_bucket)
        s3_plugins_path = "plugins.zip"

        # create Airflow environment
        env_name = f"env-{short_uid()}"
        webserver_url = mwaa_env_factory(env_name, S3_DAGS_PATH, s3_bucket_arn, airflow_version)

        # Upload plugin to S3
        with open(Path(BASEDIR) / plugin_type / s3_plugins_path, "rb") as f:
            aws_client.s3.put_object(Bucket=s3_bucket, Key=s3_plugins_path, Body=f.read())

        # Ensure plugins are loaded
        def _assert_plugin_created():
            response = requests.get(
                webserver_url + "/api/v1/plugins", auth=(AIRFLOW_ADMIN_USER, AIRFLOW_ADMIN_PASS)
            )
            plugins = response.json()["plugins"]
            plugin_names = [plugin["name"] for plugin in plugins]
            assert expected_plugin_name in plugin_names

        retry(_assert_plugin_created, retries=20, sleep=3)

    @pytest.mark.parametrize("airflow_version", ("2.4.3", "2.5.1", "2.6.3", "2.7.2", "2.8.1"))
    @markers.aws.only_localstack
    def test_mwaa_environment_runner(
        self,
        mwaa_env_factory,
        s3_bucket,
        airflow_version,
        account_id,
        region_name,
    ):
        # This test checks that the LocalStack MWAA runner resembles the AWS runner as much as possible.
        # There is no documented way to SSH into an MWAA runner which prevents AWS validation.

        s3_bucket_arn = arns.s3_bucket_arn(s3_bucket)

        env_name = f"env-{short_uid()}"
        mwaa_env_factory(env_name, S3_DAGS_PATH, s3_bucket_arn, airflow_version)

        container_name = CONTAINER_NAME_PATTERN.format(
            account_id=account_id, region_name=region_name, env_name=env_name
        )
        result = DOCKER_CLIENT.exec_in_container(container_name, ["java", "--version"])
        stdout = to_str(result[0])
        assert "openjdk 17" in stdout
        assert "Corretto" in stdout
