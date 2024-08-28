import aws_cdk as cdk
import pytest
from aws_cdk import aws_batch, aws_ec2, aws_ecs
from localstack.testing.aws.util import ServiceLevelClientFactory, is_aws_cloud
from localstack.testing.pytest import markers
from localstack.utils.strings import short_uid
from localstack.utils.sync import wait_until


@markers.acceptance_test
class TestBatch:
    stack_name: str = "BatchStack"

    @pytest.fixture(scope="class", autouse=True)
    def infrastructure(self, infrastructure_setup):
        infra = infrastructure_setup(namespace="BatchAcceptance")
        stack = cdk.Stack(infra.cdk_app, self.stack_name)

        vpc = aws_ec2.Vpc(stack, "Vpc")
        compute_environment = aws_batch.FargateComputeEnvironment(
            stack, "ComputeEnvironment", spot=True, vpc=vpc
        )
        queue = aws_batch.JobQueue(stack, "JobQueue")
        job_container_definition = aws_batch.EcsFargateContainerDefinition(
            stack,
            "ContainerDefinition",
            image=aws_ecs.ContainerImage.from_registry("ubuntu"),
            memory=cdk.Size.mebibytes(1024),
            cpu=0.5,
            command=["bash", "-c", "sleep 3 && echo Done"],
            # TODO: roles
        )
        job_definition = aws_batch.EcsJobDefinition(
            stack,
            "JobDefinition",
            container=job_container_definition,
            timeout=cdk.Duration.hours(4),
        )
        queue.add_compute_environment(compute_environment, 0)

        cdk.CfnOutput(stack, "QueueArn", value=queue.job_queue_arn)
        cdk.CfnOutput(stack, "JobDefinitionArn", value=job_definition.job_definition_arn)
        cdk.CfnOutput(
            stack, "ComputeEnvironmentArn", value=compute_environment.compute_environment_arn
        )

        with infra.provisioner() as prov:
            yield prov

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(
        paths=[
            # TODO
            "$..computeResources",
            # TODO
            "$..containerOrchestrationType",
            # TODO: the AWS arn:aws:iam:<account-id>:role/aws-service-role/batch.amazonaws.com/AWSServiceRoleForBatch
            #  does not exist by default
            "$..serviceRole",
            # difference in wording of a status message
            "$..statusReason",
            # TODO
            "$..tags",
            # Why does AWS include a `uuid` field?
            "$..uuid",
            # lack of parity between moto and AWS
            "$..ecsClusterArn",
        ]
    )
    def test_deployed_compute_environment(
        self, infrastructure, aws_client: ServiceLevelClientFactory, snapshot
    ):
        outputs = infrastructure.get_stack_outputs(stack_name=self.stack_name)
        compute_environment_arn = outputs["ComputeEnvironmentArn"]

        # describe
        compute_environment = aws_client.batch.describe_compute_environments(
            computeEnvironments=[compute_environment_arn],
        )["computeEnvironments"][0]

        snapshot.add_transformer(
            snapshot.transform.regex(
                compute_environment["computeEnvironmentName"], "<compute-environment-name>"
            )
        )

        # perform the matches
        snapshot.match("compute-environment", compute_environment)

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(
        paths=[
            # lack of parity
            "$..jobStateTimeLimitActions",
            "$..statusReason",
        ]
    )
    def test_deployed_job_queue(
        self, infrastructure, aws_client: ServiceLevelClientFactory, snapshot
    ):
        outputs = infrastructure.get_stack_outputs(stack_name=self.stack_name)
        compute_environment_arn = outputs["ComputeEnvironmentArn"]
        snapshot.add_transformer(
            snapshot.transform.regex(compute_environment_arn, "<compute-environment-arn>")
        )
        queue_arn = outputs["QueueArn"]
        snapshot.add_transformer(snapshot.transform.regex(queue_arn, "<queue-arn>"))

        # describe
        queue = aws_client.batch.describe_job_queues(jobQueues=[queue_arn])["jobQueues"][0]
        snapshot.add_transformer(
            snapshot.transform.regex(queue["jobQueueName"], "<job-queue-name>")
        )

        # perform the matches
        snapshot.match("job-queue", queue)

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(
        paths=[
            # lack of parity
            "$..containerOrchestrationType",
            "$..containerProperties.fargatePlatformConfiguration.platformVersion",
            "$..containerProperties.runtimePlatform.cpuArchitecture",
            "$..containerProperties.runtimePlatform.operatingSystemFamily",
            "$..propagateTags",
            # extra fields
            "$..retryStrategy",
        ]
    )
    def test_deployed_job_definition(
        self, infrastructure, aws_client: ServiceLevelClientFactory, snapshot
    ):
        outputs = infrastructure.get_stack_outputs(stack_name=self.stack_name)

        job_definition_arn = outputs["JobDefinitionArn"]
        snapshot.add_transformer(
            snapshot.transform.regex(job_definition_arn, "<job-definition-arn>")
        )

        job_definition = aws_client.batch.describe_job_definitions(
            jobDefinitions=[job_definition_arn],
        )["jobDefinitions"][0]
        snapshot.add_transformer(
            snapshot.transform.regex(job_definition["jobDefinitionName"], "<job-definition-name>")
        )
        snapshot.add_transformer(snapshot.transform.key_value("executionRoleArn"))

        # perform the matches
        snapshot.match("job-definition", job_definition)

    @markers.aws.validated
    @pytest.mark.skip_store_check(
        reason="cannot pickle `socket` object for moto.batch.models.BatchBackend"
    )
    def test_submit_job(self, infrastructure, aws_client: ServiceLevelClientFactory):
        outputs = infrastructure.get_stack_outputs(stack_name=self.stack_name)
        queue_arn = outputs["QueueArn"]
        job_definition_arn = outputs["JobDefinitionArn"]

        job_name = f"job-{short_uid()}"
        response = aws_client.batch.submit_job(
            jobName=job_name,
            jobQueue=queue_arn,
            jobDefinition=job_definition_arn,
        )

        job_id = response["jobId"]

        def job_finished() -> bool:
            describe_jobs_response = aws_client.batch.describe_jobs(jobs=[job_id])["jobs"][0]
            return describe_jobs_response["status"] in {"SUCCEEDED", "FAILED"}

        # wait for the job to complete
        wait = 1.0
        max_retries = 10
        if is_aws_cloud():
            # up to 10 minutes, batch can be slow
            wait = 10.0
            max_retries = 60
        wait_until(job_finished, strategy="static", wait=wait, max_retries=max_retries)

        job = aws_client.batch.describe_jobs(jobs=[job_id])["jobs"][0]
        assert job["status"] == "SUCCEEDED"
