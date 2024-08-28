import contextlib
import gzip

import pytest
from localstack.testing.pytest import markers
from localstack.utils import testutil
from localstack.utils.strings import short_uid, to_bytes, to_str
from localstack.utils.sync import retry

from tests.aws.fixtures import should_skip_bigdata_tests

# sample PySpark script - based on https://github.com/apache/spark/blob/master/examples/src/main/python/pi.py
PYSPARK_PI_EXAMPLE = """
import sys
from random import random
from operator import add
from pyspark.sql import SparkSession

def f(_: int) -> float:
    x = random() * 2 - 1
    y = random() * 2 - 1
    return 1 if x ** 2 + y ** 2 <= 1 else 0

spark = SparkSession.builder.appName("PythonPi").getOrCreate()
partitions = int(sys.argv[1]) if len(sys.argv) > 1 else 2
n = 100000 * partitions

count = spark.sparkContext.parallelize(range(1, n + 1), partitions).map(f).reduce(add)
print("Pi is roughly %f" % (4.0 * count / n))
spark.stop()
"""


def _wait_for_job_finished(aws_client, application_id, job_run_id):
    def _job_run_finished():
        result = aws_client.emr_serverless.get_job_run(
            applicationId=application_id, jobRunId=job_run_id
        )["jobRun"]
        assert result["state"] in ["SUCCESS", "FAILED"]
        return result

    result = retry(_job_run_finished, retries=60, sleep=4)
    assert result["state"] == "SUCCESS"
    return result


@pytest.fixture
def create_application(aws_client):
    app_ids = []
    client = aws_client.emr_serverless

    def _create(**kwargs):
        kwargs.setdefault("name", f"app-{short_uid()}")
        application = client.create_application(**kwargs)
        app_id = application["applicationId"]
        app_ids.append(app_id)
        return application

    yield _create

    for app_id in app_ids:

        def _check_app_stopped():
            state = client.get_application(applicationId=app_id)["application"]["state"]
            assert state == "STOPPED"

        with contextlib.suppress(Exception):
            client.stop_application(applicationId=app_id)
            retry(_check_app_stopped, retries=15, sleep=2)
            client.delete_application(applicationId=app_id)


@pytest.fixture
def role_with_policy(create_role_with_policy_for_principal):
    _, role_arn = create_role_with_policy_for_principal(
        principal={"Service": "emr-serverless.amazonaws.com"},
        resource="*",
        effect="Allow",
        actions=["glue:*", "s3:*"],
    )
    return role_arn


@pytest.fixture
def get_job_logs(aws_client, aws_client_factory):
    def _get_logs(s3_bucket):
        def _get_log_file_content():
            objects = testutil.map_all_s3_objects(
                buckets=s3_bucket, to_json=False, s3_client=aws_client.s3
            )
            stdout_logs = next(
                v for k, v in objects.items() if k.endswith("SPARK_DRIVER/stdout.gz")
            )
            stdout_logs_str = to_str(gzip.decompress(stdout_logs))
            return stdout_logs_str

        return retry(_get_log_file_content, retries=20, sleep=1)

    return _get_logs


@pytest.mark.skipif(
    should_skip_bigdata_tests(), reason="Test requires bigdata container - skipping in CI"
)
class TestEmrServerless:
    @markers.snapshot.skip_snapshot_verify(
        paths=[
            "$..totalExecutionDurationSeconds",
            "$..jobRun.stateDetails",
            # TODO those have now been added to get_job_run response
            "$..attempt",
            "$..attemptCreatedAt",
            "$..attemptUpdatedAt",
            "$..executionTimeoutMinutes",
            "$..mode",
            "$..retryPolicy",
            # TODO need to set default for these values when creating an application
            "$..application.architecture",
            "$..application.autoStartConfiguration",
            "$..application.autoStopConfiguration",
            "$..application.monitoringConfiguration",
            "$..application.tags",
        ]
    )
    @markers.aws.validated
    def test_create_application_run_job(
        self, role_with_policy, create_application, get_job_logs, aws_client, s3_bucket, snapshot
    ):
        snapshot.add_transformer(snapshot.transform.key_value("arn"))
        snapshot.add_transformer(snapshot.transform.key_value("name"))
        snapshot.add_transformer(snapshot.transform.key_value("createdBy"))
        snapshot.add_transformer(snapshot.transform.regex(s3_bucket, "<s3-bucket>"))
        snapshot.add_transformer(snapshot.transform.regex(role_with_policy, "<role-arn>"))

        # create application
        emr_client = aws_client.emr_serverless
        application = create_application(releaseLabel="emr-6.6.0", type="Spark")
        application_id = application["applicationId"]
        snapshot.add_transformer(snapshot.transform.regex(application_id, "<application-id>"))
        snapshot.match("create-app-details", application)

        application = aws_client.emr_serverless.get_application(applicationId=application_id)
        snapshot.match("get-app-details", application)

        # upload sample script to S3
        aws_client.s3.put_object(Bucket=s3_bucket, Key="pi.py", Body=to_bytes(PYSPARK_PI_EXAMPLE))

        # start job run
        job_driver = {"sparkSubmit": {"entryPoint": f"s3://{s3_bucket}/pi.py"}}
        configs = {
            "monitoringConfiguration": {
                "s3MonitoringConfiguration": {"logUri": f"s3://{s3_bucket}/logs/"}
            }
        }
        result = emr_client.start_job_run(
            applicationId=application_id,
            executionRoleArn=role_with_policy,
            jobDriver=job_driver,
            configurationOverrides=configs,
        )
        job_run_id = result["jobRunId"]
        snapshot.add_transformer(snapshot.transform.regex(job_run_id, "<job-run-id>"))

        # assert that "JobRun is waiting for the application to start"
        result = aws_client.emr_serverless.get_job_run(
            applicationId=application_id, jobRunId=job_run_id
        )
        snapshot.match("job-run-before-start", result)

        # start application, wait until the job is finished
        emr_client.start_application(applicationId=application_id)
        result = _wait_for_job_finished(aws_client, application_id, job_run_id)
        snapshot.match("job-finished-result", result)

        # get log files
        logs = get_job_logs(s3_bucket)
        assert "Pi is roughly 3.1" in logs
