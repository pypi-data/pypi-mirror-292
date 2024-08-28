import json
import logging
import os

import pytest
import requests
from localstack import config
from localstack.pro.core import config as ext_config
from localstack.testing.config import TEST_AWS_ACCESS_KEY_ID
from localstack.testing.pytest import markers
from localstack.utils.aws import arns
from localstack.utils.aws.request_context import mock_aws_request_headers
from localstack.utils.container_utils.container_client import Util as DockerUtil
from localstack.utils.docker_utils import get_host_path_for_path_in_docker
from localstack.utils.files import load_file
from localstack.utils.strings import short_uid, to_str
from localstack.utils.sync import retry

try:
    # Make code compatible with Python <3.7 (we could also use 'typing_extensions' lib
    #  in the future, but this seems like a reasonably simple fix for the tests here.)
    from typing import Dict, List, Literal

    JobQueueState = Literal["ENABLED", "DISABLED"]
    JobType = Literal["container", "multinode"]
except Exception:
    JobQueueState = str
    JobType = str

LOG = logging.getLogger(__name__)


@pytest.fixture
def create_job(aws_client):
    created_job_arns = []

    def _create_job(
        job_def_name, type: JobType = "container", container_props=None, image_name=None, command=""
    ):
        if container_props is None:
            command = ["sleep", "30"] if command == "" else command
            container_props = {
                "image": image_name or "busybox",
                "memory": 512,
                "vcpus": 1,
                "command": command,
                "resourceRequirements": [
                    {"value": "1", "type": "VCPU"},
                    {"value": "512", "type": "MEMORY"},
                ],
                **({"command": command} if command else {}),
            }
        job_definition = aws_client.batch.register_job_definition(
            jobDefinitionName=job_def_name,
            type=type,
            containerProperties=container_props,
        )
        created_job_arns.append(job_definition["jobDefinitionArn"])
        return job_definition

    yield _create_job

    for job_arn in created_job_arns:
        aws_client.batch.deregister_job_definition(jobDefinition=job_arn)


@pytest.fixture
def create_job_queue(aws_client):
    created_job_queue_arns = []

    def _create_job_queue(
        job_queue_name,
        state: JobQueueState = "ENABLED",
        priority=1,
        compute_env_order=None,
    ):
        job_queue_definition = aws_client.batch.create_job_queue(
            jobQueueName=job_queue_name,
            state=state,
            priority=priority,
            computeEnvironmentOrder=compute_env_order,
        )
        created_job_queue_arns.append(job_queue_definition["jobQueueArn"])
        return job_queue_definition

    yield _create_job_queue

    for job_queue_arn in created_job_queue_arns:
        try:
            aws_client.batch.delete_job_queue(jobQueue=job_queue_arn)
        except Exception as e:
            LOG.info("Unable to clean up job queue %s: %s", job_queue_arn, e)


@pytest.fixture
def create_compute_env(aws_client):
    roles = []
    compute_envs = []

    def _create_env(**kwargs):
        role_name = f"r-{short_uid()}"
        result = aws_client.iam.create_role(RoleName=role_name, AssumeRolePolicyDocument="{}")
        role_arn = result["Role"]["Arn"]

        env_name = f"env-{short_uid()}"
        kwargs.setdefault("type", "UNMANAGED")
        result = aws_client.batch.create_compute_environment(
            computeEnvironmentName=env_name, serviceRole=role_arn, **kwargs
        )
        compute_envs.append(result["computeEnvironmentArn"])
        return result

    yield _create_env

    # clean up
    for env_arn in compute_envs:
        try:
            aws_client.batch.delete_compute_environment(computeEnvironment=env_arn)
        except Exception as e:
            LOG.info("Unable to clean up Batch compute environment %s: %s", env_arn, e)
    for role_name in roles:
        try:
            aws_client.iam.delete_role(RoleName=role_name)
        except Exception as e:
            LOG.info("Unable to clean up IAM role %s: %s", role_name, e)


class TestBatch:
    # test tries to connect to LOCALSTACK_HOSTNAME, which is not accessible from outside no-internet network
    # since it being replaced with the IP of the docker container in the network
    @markers.skip_offline
    @pytest.mark.skip_store_check(
        reason="cannot pickle `socket` object for moto.batch.models.BatchBackend"
    )
    @markers.aws.unknown
    def test_create_submit_job(
        self, create_job, create_job_queue, aws_client, account_id, region_name
    ):
        events = aws_client.events
        s3 = aws_client.s3
        sqs = aws_client.sqs

        # create test job and job queue
        job_name = "job-%s" % short_uid()
        image_name = "amazon/aws-cli"
        environment = {"AWS_EC2_METADATA_DISABLED": "true"}
        job_name, job_queue_name = self._create_job_and_queue(
            aws_client.batch,
            iam_client=aws_client.iam,
            create_job=create_job,
            create_job_queue=create_job_queue,
            image_name=image_name,
            account_id=account_id,
            environment=environment,
        )

        # subscribe to events
        rule_name = "batch-rule-%s" % short_uid()
        queue_name = "batch-queue-%s" % short_uid()
        target_id = "batch-target-{}".format(short_uid())
        queue_url = sqs.create_queue(QueueName=queue_name)["QueueUrl"]
        queue_arn = arns.sqs_queue_arn(queue_name, account_id, region_name)
        events.put_rule(Name=rule_name, EventPattern='{"source":["aws.batch"]}')
        events.put_targets(Rule=rule_name, Targets=[{"Id": target_id, "Arn": queue_arn}])

        # start job execution
        bucket_name = "b-%s" % short_uid()
        cmd_array = [
            "s3",
            "--endpoint-url",
            "http://$LOCALSTACK_HOSTNAME:4566",
            "--region",
            "us-east-1",
            "mb",
            "s3://%s" % bucket_name,
        ]
        result = aws_client.batch.submit_job(
            jobName=job_name,
            jobQueue=job_queue_name,
            jobDefinition=job_name,
            containerOverrides={"command": cmd_array},
        )
        assert "jobId" in result
        job_id = result["jobId"]

        # get job logs
        def check_logs():
            log_group = "/aws/batch/job"
            stream_name = f"{job_name}/default/{job_id}"
            rs = aws_client.logs.filter_log_events(
                logGroupName=log_group, logStreamNames=[stream_name]
            )
            events = rs["events"]
            log_output = "\n".join([log["message"] for log in events]).strip()
            assert log_output
            if f"make_bucket: {bucket_name}" not in log_output:
                print("Unexpected log output: %s" % log_output)

        # assert job status and logs
        self._assert_job_logs(
            job_name, job_id, aws_client.logs, aws_client.batch, [f"make_bucket: {bucket_name}"]
        )

        # get job status events
        def check_job_events():
            resp = sqs.receive_message(QueueUrl=queue_url)
            for msg in resp.get("Messages", []):
                messages.append(msg)
                sqs.delete_message(QueueUrl=queue_url, ReceiptHandle=msg["ReceiptHandle"])
            msgs = [json.loads(msg["Body"])["detail"] for msg in messages]
            statuses = [msg["status"] for msg in msgs]
            assert statuses == [
                "SUBMITTED",
                "PENDING",
                "RUNNABLE",
                "STARTING",
                "RUNNING",
                "SUCCEEDED",
            ]
            commands = [msg.get("container", {}).get("command") for msg in msgs]
            for command in commands:
                assert "--endpoint-url" in command
            images = [msg.get("container", {}).get("image") for msg in msgs]
            assert set(images) == {image_name}
            environments = [msg.get("container", {}).get("environment") for msg in msgs]
            for environment in environments:
                assert {"name": "AWS_EC2_METADATA_DISABLED", "value": "true"} in environment

        messages = []
        retry(check_job_events, sleep=3, retries=15)

        # assert that S3 bucket has been created by the job
        result = s3.head_bucket(Bucket=bucket_name)
        assert result["ResponseMetadata"]["HTTPStatusCode"] == 200

        # clean up
        sqs.delete_queue(QueueUrl=queue_url)
        events.remove_targets(Rule=rule_name, Ids=[target_id])
        events.delete_rule(Name=rule_name)

    @markers.aws.only_localstack
    @pytest.mark.skip_store_check(
        reason="cannot pickle `socket` object for moto.batch.models.BatchBackend"
    )
    def test_create_job_default_command(self, create_job, create_job_queue, aws_client, account_id):
        job_name, job_queue_name = self._create_job_and_queue(
            aws_client.batch,
            iam_client=aws_client.iam,
            create_job=create_job,
            create_job_queue=create_job_queue,
            image_name="hello-world",
            account_id=account_id,
        )

        result = aws_client.batch.submit_job(
            jobName=job_name,
            jobQueue=job_queue_name,
            jobDefinition=job_name,
        )
        assert "jobId" in result
        job_id = result["jobId"]

        # assert job status and logs
        self._assert_job_logs(
            job_name, job_id, aws_client.logs, aws_client.batch, ["Hello from Docker!"]
        )

    def _create_job_and_queue(
        self,
        batch_client,
        iam_client,
        create_job,
        create_job_queue,
        image_name: str,
        account_id: str,
        environment: Dict = None,
    ):
        # create test action
        job_name = f"job-{short_uid()}"
        environment = environment or {}
        env_list = [{"name": key, "value": value} for key, value in environment.items()]
        result = create_job(
            job_def_name=job_name,
            type="container",
            container_props={
                "image": image_name,
                "memory": 500,
                "vcpus": 1,
                "environment": env_list,
            },
        )
        assert account_id in result.get("jobDefinitionArn")
        assert f"job-definition/{job_name}" in result.get("jobDefinitionArn")

        # create role
        role_name = f"r-{short_uid()}"
        result = iam_client.create_role(RoleName=role_name, AssumeRolePolicyDocument="{}")
        role_arn = result["Role"]["Arn"]

        # create compute environment
        env_name = f"env-{short_uid()}"
        result = batch_client.create_compute_environment(
            computeEnvironmentName=env_name, type="UNMANAGED", serviceRole=role_arn
        )
        assert account_id in result.get("computeEnvironmentArn")
        env_arn = result["computeEnvironmentArn"]

        # create job queue
        job_queue_name = f"q-{short_uid()}"
        result = create_job_queue(
            job_queue_name=job_queue_name,
            state="ENABLED",
            priority=1,
            compute_env_order=[{"order": 0, "computeEnvironment": env_arn}],
        )
        assert account_id in result.get("jobQueueArn")
        assert f"job-queue/{job_queue_name}" in result.get("jobQueueArn")

        return job_name, job_queue_name

    def _assert_job_logs(
        self, job_name, job_id, logs_client, batch_client, expected_logs: List[str]
    ):
        # get job logs
        def check_logs():
            log_group = "/aws/batch/job"
            stream_name = f"{job_name}/default/{job_id}"
            rs = logs_client.filter_log_events(logGroupName=log_group, logStreamNames=[stream_name])
            events = rs["events"]
            log_output = "\n".join([log["message"] for log in events]).strip()
            assert log_output
            for expected in expected_logs:
                assert expected in log_output

        # check final job status
        def check_job_status():
            result = batch_client.describe_jobs(jobs=[job_id])
            result = result["jobs"][0]
            if result["status"] in ["FAILED", "SUCCEEDED"]:
                check_logs()
            assert result["status"] == "SUCCEEDED"

        retry(check_job_status, sleep=3, retries=15)

    @markers.aws.only_localstack
    @pytest.mark.skip_store_check(
        reason="cannot pickle `socket` object for moto.batch.models.BatchBackend"
    )
    def test_create_with_additional_config(
        self, create_job, create_job_queue, create_compute_env, monkeypatch, aws_client, account_id
    ):
        # note: directory must be mountable from the host, cannot use "tmpdir" fixture from pytest here...
        local_tmpdir = DockerUtil.mountable_tmp_file()
        host_tmpdir = get_host_path_for_path_in_docker(local_tmpdir)
        monkeypatch.setattr(
            ext_config,
            "BATCH_DOCKER_FLAGS",
            (
                "-e ADDITIONAL_VAR=some_var --add-host sometest.localstack.cloud:127.0.0.1 "
                f"-v {host_tmpdir}:/tmp/mypath"
            ),
        )

        job_name = f"job-{short_uid()}"
        result = create_job(
            job_def_name=job_name,
            type="container",
            container_props={
                "image": "alpine",
                "memory": 500,
                "vcpus": 1,
                "environment": [
                    {"name": "AWS_EC2_METADATA_DISABLED", "value": "true"},
                    {"name": "TEST_ENV_VAR", "value": "test"},
                ],
            },
        )
        assert account_id in result.get("jobDefinitionArn")
        assert f"job-definition/{job_name}" in result.get("jobDefinitionArn")

        # create compute environment
        result = create_compute_env()
        assert account_id in result.get("computeEnvironmentArn")
        env_arn = result["computeEnvironmentArn"]

        # create job queue
        job_queue_name = "q-%s" % short_uid()
        result = create_job_queue(
            job_queue_name=job_queue_name,
            state="ENABLED",
            priority=1,
            compute_env_order=[{"order": 0, "computeEnvironment": env_arn}],
        )
        assert account_id in result.get("jobQueueArn")
        assert f"job-queue/{job_queue_name}" in result.get("jobQueueArn")

        # start job execution
        cmd_array = [
            "sh",
            "-c",
            "env; getent hosts sometest.localstack.cloud; echo 'foobar' > /tmp/mypath/foo.bar",
        ]
        result = aws_client.batch.submit_job(
            jobName=job_name,
            jobQueue=job_queue_name,
            jobDefinition=job_name,
            containerOverrides={"command": cmd_array},
        )
        assert "jobId" in result
        job_id = result["jobId"]

        # get job logs
        def check_logs():
            log_group = "/aws/batch/job"
            stream_name = f"{job_name}/default/{job_id}"
            rs = aws_client.logs.filter_log_events(
                logGroupName=log_group, logStreamNames=[stream_name]
            )
            events = rs["events"]
            log_output = "\n".join([log["message"] for log in events]).strip()
            assert log_output
            assert "AWS_EC2_METADATA_DISABLED=true" in log_output
            assert "TEST_ENV_VAR=test" in log_output
            assert "ADDITIONAL_VAR=some_var" in log_output
            assert "127.0.0.1" in log_output
            assert "sometest.localstack.cloud" in log_output

        def check_file_creation():
            foo_path = os.path.join(local_tmpdir, "foo.bar")
            assert os.path.isfile(foo_path), f"File {foo_path} was not created in mounted dir"
            assert load_file(foo_path).strip() == "foobar"

        # check final job status
        def check_job_status():
            result = aws_client.batch.describe_jobs(jobs=[job_id])
            result = result["jobs"][0]
            if result["status"] in ["FAILED", "SUCCEEDED"]:
                check_logs()
                check_file_creation()
            assert result["status"] == "SUCCEEDED"

        retry(check_job_status, sleep=3, retries=15)

    @markers.aws.unknown
    def test_describe_all_active_job_definitions(self, create_job, aws_client):
        result = aws_client.batch.describe_job_definitions(status="ACTIVE")
        assert result["jobDefinitions"] == []
        job_name = f"test_job_{short_uid()}"
        job_definition = create_job(job_name)
        result = aws_client.batch.describe_job_definitions(status="ACTIVE")
        result_job_definitions = result["jobDefinitions"]
        assert result_job_definitions
        for prop in ["jobDefinitionName", "jobDefinitionArn", "revision"]:
            assert any(
                [job_definition[prop] == result_job[prop] for result_job in result_job_definitions]
            )

    @markers.aws.unknown
    def test_describe_filtered_job_definitions(self, create_job, aws_client):
        result = aws_client.batch.describe_job_definitions(jobDefinitions=["non-existent-job"])
        assert result["jobDefinitions"] == []
        job_name = f"test_job_{short_uid()}"
        job_definition = create_job(job_name)
        result = aws_client.batch.describe_job_definitions(
            jobDefinitions=[job_definition["jobDefinitionArn"]]
        )
        result_job_definitions = result["jobDefinitions"]
        assert result_job_definitions
        for prop in ["jobDefinitionName", "jobDefinitionArn", "revision"]:
            assert any(
                [job_definition[prop] == result_job[prop] for result_job in result_job_definitions]
            )

    @markers.aws.only_localstack
    def test_environment_with_empty_params(self, iam_role, region_name):
        """Craft a request manually to create a compute environment with missing
        computeResources.maxvCpus (seems to be possible from Java AWS SDK, but not with latest boto3)
        """

        url = f"{config.internal_service_url()}/v1/createcomputeenvironment"
        request = {
            "computeEnvironmentName": "env1",
            "type": "UNMANAGED",
            "serviceRole": iam_role,
            "computeResources": {"type": "FARGATE"},
        }
        headers = mock_aws_request_headers(
            "batch",
            aws_access_key_id=TEST_AWS_ACCESS_KEY_ID,
            region_name=region_name,
        )
        result = requests.post(url, json=request, headers=headers)
        assert not result.ok
        assert "Missing required parameter" in to_str(result.content)
        assert "maxvCpus" in to_str(result.content)
