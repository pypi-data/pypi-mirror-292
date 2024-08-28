import json
import logging
import os.path
from typing import Callable, Dict, Optional, Union

import pytest
from localstack.pro.core.aws.api.glue import RegistryId, SchemaId
from localstack.pro.core.services.athena import query_utils
from localstack.pro.core.services.athena.query_utils import canonicalize_db_name
from localstack.pro.core.services.glue.models import DEFAULT_REGISTRY_NAME
from localstack.testing.aws.util import is_aws_cloud
from localstack.utils.files import load_file
from localstack.utils.strings import short_uid, to_bytes
from localstack.utils.sync import retry

from tests.aws.fixtures import should_skip_bigdata_tests, skip_in_ci

LOG = logging.getLogger(__name__)


def skip_bigdata_in_ci(fn):
    """Decorator used to skip tests when (1) running in CI, and (2) mono container mode is not enabled"""
    if not should_skip_bigdata_tests():
        return fn

    decorator = skip_in_ci(reason="Glue Database/Table creation needs the BigData image")
    return decorator(fn)


def generic_crud_fixture(
    entity_name: str,
    create_function: Callable,
    create_arg: Union[str, Callable],
    delete_function: Callable,
    delete_arg: Union[str, Callable],
    post_create_function: Optional[Callable] = None,
):
    entities = []

    def factory(**kwargs):
        unique_identifier = f"test-{entity_name}-{short_uid()}"
        if isinstance(create_arg, str) and create_arg not in kwargs:
            kwargs[create_arg] = unique_identifier
            created_arg = kwargs[create_arg]
        else:
            create_arg_key, create_arg_value = create_arg(unique_identifier)
            if create_arg_key in kwargs and isinstance(kwargs[create_arg_key], dict):
                kwargs[create_arg_key] = {**kwargs[create_arg_key], **create_arg_value}
            else:
                kwargs[create_arg_key] = create_arg_value
            created_arg = kwargs[create_arg_key]
        entities.append(kwargs)
        result = create_function(**kwargs)
        if post_create_function:
            post_create_function(kwargs, result)
        return created_arg

    yield factory

    # cleanup
    for create_kwargs in entities:
        try:
            kwargs = {}
            if isinstance(delete_arg, str):
                if isinstance(create_arg, str):
                    kwargs[delete_arg] = create_kwargs[create_arg]
                else:
                    create_arg_key, _ = create_arg("")
                    kwargs[delete_arg] = create_kwargs[create_arg_key]
            else:
                kwargs = delete_arg(create_kwargs)

            delete_function(**kwargs)
        except Exception as e:
            if e.__class__.__name__ != "EntityNotFoundException":
                LOG.error("error cleaning up %s %s: %s", entity_name, create_kwargs, e)


@pytest.fixture
def glue_create_job(aws_client):
    yield from generic_crud_fixture(
        "job", aws_client.glue.create_job, "Name", aws_client.glue.delete_job, "JobName"
    )


@pytest.fixture
def glue_create_workflow(aws_client):
    yield from generic_crud_fixture(
        "workflow", aws_client.glue.create_workflow, "Name", aws_client.glue.delete_workflow, "Name"
    )


@pytest.fixture
def glue_create_trigger(aws_client):
    yield from generic_crud_fixture(
        "trigger", aws_client.glue.create_trigger, "Name", aws_client.glue.delete_trigger, "Name"
    )


@pytest.fixture
def glue_create_sec_config(aws_client):
    yield from generic_crud_fixture(
        "security-config",
        aws_client.glue.create_security_configuration,
        "Name",
        aws_client.glue.delete_security_configuration,
        "Name",
    )


@pytest.fixture
def glue_create_crawler(aws_client):
    yield from generic_crud_fixture(
        "crawler", aws_client.glue.create_crawler, "Name", aws_client.glue.delete_crawler, "Name"
    )


@pytest.fixture
def glue_create_registry(aws_client):
    yield from generic_crud_fixture(
        "registry",
        aws_client.glue.create_registry,
        "RegistryName",
        aws_client.glue.delete_registry,
        lambda create_kwargs: {
            "RegistryId": RegistryId(RegistryName=create_kwargs["RegistryName"]),
        },
    )


@pytest.fixture
def glue_create_schema(aws_client):
    yield from generic_crud_fixture(
        "schema",
        aws_client.glue.create_schema,
        "SchemaName",
        aws_client.glue.delete_schema,
        lambda create_kwargs: {
            "SchemaId": SchemaId(
                SchemaName=create_kwargs["SchemaName"],
                RegistryName=create_kwargs.get("RegistryId", {}).get("RegistryName")
                or DEFAULT_REGISTRY_NAME,
            ),
        },
    )


@pytest.fixture
def glue_create_connection(aws_client):
    yield from generic_crud_fixture(
        "connection",
        aws_client.glue.create_connection,
        lambda connection_name: ("ConnectionInput", {"Name": connection_name}),
        aws_client.glue.delete_connection,
        lambda create_kwargs: {"ConnectionName": create_kwargs["ConnectionInput"]["Name"]},
    )


@pytest.fixture
def glue_create_csv_classifier(aws_client):
    yield from generic_crud_fixture(
        "classifier",
        aws_client.glue.create_classifier,
        lambda classifier_name: ("CsvClassifier", {"Name": classifier_name}),
        aws_client.glue.delete_classifier,
        lambda create_kwargs: {"Name": create_kwargs["CsvClassifier"]["Name"]},
    )


@pytest.fixture
def glue_create_database(aws_client):
    def wait_for_db(kwargs, *_):
        if not is_aws_cloud():
            wait_for_db_available_in_hive(kwargs["DatabaseInput"]["Name"])

    yield from generic_crud_fixture(
        "database",
        aws_client.glue.create_database,
        lambda database_name: ("DatabaseInput", {"Name": database_name}),
        aws_client.glue.delete_database,
        lambda create_kwargs: {"Name": create_kwargs["DatabaseInput"]["Name"]},
        post_create_function=wait_for_db,
    )


@pytest.fixture
def glue_create_table(aws_client):
    if should_skip_bigdata_tests():
        raise Exception(
            "Creating Glue tables via Hive / bigdata container currently not supported in CI"
        )
    yield from generic_crud_fixture(
        "table",
        aws_client.glue.create_table,
        lambda table_name: ("TableInput", {"Name": table_name}),
        aws_client.glue.delete_table,
        lambda create_kwargs: {
            "Name": create_kwargs["TableInput"]["Name"],
            "DatabaseName": create_kwargs["DatabaseName"],
        },
    )


@pytest.fixture
def create_run_spark_job(create_run_job, aws_client, s3_create_bucket):
    """Create and run a Spark Scala job"""

    def _create_and_run(
        job_script: str | bytes,
        job_args: Dict[str, str] = None,
        command_name: str = "glueetl",
        expected_status: str = "SUCCEEDED",
        **kwargs,
    ):
        bucket_name = s3_create_bucket()
        if isinstance(job_script, bytes):
            job_bytes = job_script
            job_s3_key = "job.scala"
        else:
            job_s3_key = os.path.basename(job_script)
            job_bytes = load_file(os.path.basename(job_script), mode="rb")

        aws_client.s3.put_object(Bucket=bucket_name, Key=job_s3_key, Body=job_bytes)
        s3_url = f"s3://{bucket_name}/{job_s3_key}"
        job_details = {"Command": {"Name": command_name, "ScriptLocation": s3_url}, **kwargs}

        return create_run_job(job_details, job_args=job_args, expected_status=expected_status)

    return _create_and_run


@pytest.fixture
def create_run_pyspark_job(create_run_job, aws_client, s3_create_bucket):
    """Create and run a PySpark Python job"""

    def _run_job(
        job_script: str,
        job_args: Dict[str, str] = None,
        command_name: str = "pythonshell",
        expected_status: str = "SUCCEEDED",
        **kwargs,
    ):
        bucket_name = s3_create_bucket()
        aws_client.s3.put_object(Bucket=bucket_name, Key="job.py", Body=to_bytes(job_script))
        s3_url = f"s3://{bucket_name}/job.py"
        job_details = {"Command": {"Name": command_name, "ScriptLocation": s3_url}, **kwargs}

        return create_run_job(job_details, job_args=job_args, expected_status=expected_status)

    return _run_job


@pytest.fixture
def create_run_job(aws_client, create_role, create_policy, wait_and_assume_role):
    job_names = []

    def _run_job(
        job_details: dict,
        job_args: Dict[str, str] = None,
        expected_status: str = "SUCCEEDED",
    ):
        # create job definition
        job_name = f"j-{short_uid()}"

        assume_role_policy_document = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"AWS": "*"},
                    "Action": "sts:AssumeRole",
                }
            ],
        }
        policy_document = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": ["s3:*", "cloudwatch:*", "logs:*"],
                    "Resource": "*",
                },
            ],
        }

        role = create_role(AssumeRolePolicyDocument=json.dumps(assume_role_policy_document))
        role_name = role["Role"]["RoleName"]
        role_arn = role["Role"]["Arn"]

        policy = create_policy(PolicyDocument=json.dumps(policy_document))
        policy_arn = policy["Policy"]["Arn"]

        aws_client.iam.attach_role_policy(
            RoleName=role_name,
            PolicyArn=policy_arn,
        )
        # make sure the role is available
        wait_and_assume_role(role_arn)

        aws_client.glue.create_job(
            Name=job_name,
            Role=role_arn,
            **job_details,
        )
        job_names.append(job_name)

        result = aws_client.glue.start_job_run(JobName=job_name, Arguments=job_args or {})
        run_id = result["JobRunId"]

        def _check_finished():
            result = aws_client.glue.get_job_run(JobName=job_name, RunId=run_id)
            assert result["JobRun"]["JobRunState"] in ["SUCCEEDED", "FAILED"]
            return result

        # Pulling the bigdata image can take quite some time
        result = retry(_check_finished, retries=300, sleep=2)
        assert result["JobRun"]["JobRunState"] == expected_status
        return result

    yield _run_job

    for job_name in job_names:
        aws_client.glue.delete_job(JobName=job_name)


def wait_for_db_available_in_hive(db_name: str):
    """Wait for the given DB to become available in Hive/Trino"""

    def _check_db_exists():
        result = query_utils.execute_query(f"SHOW TABLES FROM {canonical_db_name}")
        assert result.get("columns")

    canonical_db_name = canonicalize_db_name(db_name)
    retry(_check_db_exists, sleep=4, retries=20)


def wait_for_table_available_in_hive(db_name: str, table_name: str):
    """Wait for the given table to become available in Hive/Trino"""

    def _check_table_exists():
        result = query_utils.execute_query(f"DESCRIBE {canonical_db_name}.{table_name}")
        assert result.get("columns")

    canonical_db_name = canonicalize_db_name(db_name)
    table_name = canonicalize_db_name(table_name)
    retry(_check_table_exists, sleep=1, retries=20)
