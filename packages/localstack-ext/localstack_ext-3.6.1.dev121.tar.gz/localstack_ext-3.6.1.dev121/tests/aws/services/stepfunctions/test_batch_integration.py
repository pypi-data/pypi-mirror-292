import json
from typing import Final

import aws_cdk as cdk
import pytest
from aws_cdk import aws_batch, aws_ec2, aws_ecs, aws_stepfunctions, aws_stepfunctions_tasks
from localstack.testing.pytest import markers
from localstack.testing.pytest.stepfunctions.utils import launch_and_record_execution
from localstack.utils.strings import short_uid
from localstack_snapshot.snapshots.transformer import RegexTransformer

_SYNC_SKIP_SNAPSHOT_VERIFY: Final[list[str]] = [
    # LocalStack DescribeJobs output differs with AWS's.
    "$..Container",
    "$..Attempts",
    # Missing DescribeJobs description fields.
    "$..EksAttempts",
    "$..Parameters",
    "$..PlatformCapabilities",
    "$..PropagateTags",
    "$..StatusReason",
    "$..Tags",
    "$..Timeout",
    # AWS StepFunctions decides to normalise the arguments keys for only environment according to SFN
    # Pascal case before scheduling. However, no other arguments are normalised at this stage.
    # This is something unique to this service and only affects the details of the taskScheduled
    # event, which should be of minimum discomfort to end users. The dif
    "$..events..taskScheduledEventDetails.parameters.ContainerOverrides.Environment..Name",
    "$..events..taskScheduledEventDetails.parameters.ContainerOverrides.Environment..Value",
    "$..events..taskScheduledEventDetails.parameters.ContainerOverrides.Environment..name",
    "$..events..taskScheduledEventDetails.parameters.ContainerOverrides.Environment..value",
]


@markers.snapshot.skip_snapshot_verify(
    paths=[
        "$..tracingConfiguration",
        "$..SdkHttpMetadata",
        "$..SdkResponseMetadata",
    ]
)
class TestBatchIntegration:
    @pytest.fixture(scope="class", autouse=False)
    def infrastructure_batch_request_response(self, infrastructure_setup):
        infra = infrastructure_setup(namespace="StepFunctionsBatchSubmitJobRequestResponse")
        stack = cdk.Stack(infra.cdk_app, "infrastructure-batch-request-response")

        job_definition = aws_batch.EcsJobDefinition(
            stack,
            "JobDefinition",
            container=aws_batch.EcsFargateContainerDefinition(
                stack,
                "ContainerDefinition",
                image=aws_ecs.ContainerImage.from_registry("amazonlinux"),
                memory=cdk.Size.mebibytes(1024),
                cpu=0.5,
                command=["bash", "-c", "echo Done"],
            ),
            timeout=cdk.Duration.minutes(5),
        )
        compute_environment = aws_batch.FargateComputeEnvironment(
            stack, "ComputeEnvironment", spot=True, vpc=aws_ec2.Vpc(stack, "Vpc")
        )
        queue = aws_batch.JobQueue(stack, "JobQueue")
        queue.add_compute_environment(compute_environment, 0)

        batch_task = aws_stepfunctions_tasks.BatchSubmitJob(
            stack,
            "BatchTask",
            job_name=f"job-{short_uid()}",
            job_queue_arn=queue.job_queue_arn,
            job_definition_arn=job_definition.job_definition_arn,
            integration_pattern=aws_stepfunctions.IntegrationPattern.REQUEST_RESPONSE,
        )
        definition_body = aws_stepfunctions.DefinitionBody.from_chainable(batch_task)
        statemachine = aws_stepfunctions.StateMachine(
            stack, "statemachine", definition_body=definition_body
        )

        cdk.CfnOutput(stack, "StateMachineArn", value=statemachine.state_machine_arn)

        with infra.provisioner() as prov:
            yield prov

    @pytest.fixture(scope="class", autouse=False)
    def infrastructure_batch_sync(self, infrastructure_setup):
        infra = infrastructure_setup(namespace="StepFunctionsBatchSubmitJobSync")
        stack = cdk.Stack(infra.cdk_app, "infrastructure-batch-sync")

        job_definition = aws_batch.EcsJobDefinition(
            stack,
            "JobDefinition",
            container=aws_batch.EcsFargateContainerDefinition(
                stack,
                "ContainerDefinition",
                image=aws_ecs.ContainerImage.from_registry("amazonlinux"),
                memory=cdk.Size.mebibytes(1024),
                cpu=0.5,
                command=["bash", "-c", "echo Done"],
            ),
            timeout=cdk.Duration.minutes(5),
        )
        compute_environment = aws_batch.FargateComputeEnvironment(
            stack, "ComputeEnvironment", spot=True, vpc=aws_ec2.Vpc(stack, "Vpc")
        )
        queue = aws_batch.JobQueue(stack, "JobQueue")
        queue.add_compute_environment(compute_environment, 0)

        batch_task = aws_stepfunctions_tasks.BatchSubmitJob(
            stack,
            "BatchTask",
            job_name=f"job-{short_uid()}",
            job_queue_arn=queue.job_queue_arn,
            job_definition_arn=job_definition.job_definition_arn,
            integration_pattern=aws_stepfunctions.IntegrationPattern.RUN_JOB,
        )
        definition_body = aws_stepfunctions.DefinitionBody.from_chainable(batch_task)
        statemachine = aws_stepfunctions.StateMachine(
            stack, "statemachine", definition_body=definition_body
        )

        cdk.CfnOutput(stack, "StateMachineArn", value=statemachine.state_machine_arn)

        with infra.provisioner() as prov:
            yield prov

    @pytest.fixture(scope="class", autouse=False)
    def infrastructure_batch_invalid(self, infrastructure_setup):
        infra = infrastructure_setup(namespace="StepFunctionsBatchSubmitJobInvalidNamePattern")
        stack = cdk.Stack(infra.cdk_app, "infrastructure-batch-invalid")

        job_definition = aws_batch.EcsJobDefinition(
            stack,
            "JobDefinition",
            container=aws_batch.EcsFargateContainerDefinition(
                stack,
                "ContainerDefinition",
                image=aws_ecs.ContainerImage.from_registry("amazonlinux"),
                memory=cdk.Size.mebibytes(1024),
                cpu=0.5,
                command=["bash", "-c", "echo Done"],
            ),
            timeout=cdk.Duration.minutes(5),
        )
        compute_environment = aws_batch.FargateComputeEnvironment(
            stack, "ComputeEnvironment", spot=True, vpc=aws_ec2.Vpc(stack, "Vpc")
        )
        queue = aws_batch.JobQueue(stack, "JobQueue")
        queue.add_compute_environment(compute_environment, 0)

        batch_task = aws_stepfunctions_tasks.BatchSubmitJob(
            stack,
            "BatchTask",
            job_name=f"job%?-{short_uid()}",
            job_queue_arn=queue.job_queue_arn,
            job_definition_arn=job_definition.job_definition_arn,
            integration_pattern=aws_stepfunctions.IntegrationPattern.RUN_JOB,
        )
        definition_body = aws_stepfunctions.DefinitionBody.from_chainable(batch_task)
        statemachine = aws_stepfunctions.StateMachine(
            stack, "statemachine", definition_body=definition_body
        )

        cdk.CfnOutput(stack, "StateMachineArn", value=statemachine.state_machine_arn)

        with infra.provisioner() as prov:
            yield prov

    @pytest.fixture(scope="class", autouse=False)
    def infrastructure_batch_failure(self, infrastructure_setup):
        infra = infrastructure_setup(namespace="StepFunctionsBatchSubmitJobFailure")
        stack = cdk.Stack(infra.cdk_app, "infrastructure-batch-failure")

        job_definition = aws_batch.EcsJobDefinition(
            stack,
            "JobDefinition",
            container=aws_batch.EcsFargateContainerDefinition(
                stack,
                "ContainerDefinition",
                image=aws_ecs.ContainerImage.from_registry("amazonlinux"),
                memory=cdk.Size.mebibytes(1024),
                cpu=0.5,
                command=["bash", "-c", "exit 1"],
            ),
            timeout=cdk.Duration.minutes(5),
        )
        compute_environment = aws_batch.FargateComputeEnvironment(
            stack, "ComputeEnvironment", spot=True, vpc=aws_ec2.Vpc(stack, "Vpc")
        )
        queue = aws_batch.JobQueue(stack, "JobQueue")
        queue.add_compute_environment(compute_environment, 0)

        batch_task = aws_stepfunctions_tasks.BatchSubmitJob(
            stack,
            "BatchTask",
            job_name=f"job-{short_uid()}",
            job_queue_arn=queue.job_queue_arn,
            job_definition_arn=job_definition.job_definition_arn,
            integration_pattern=aws_stepfunctions.IntegrationPattern.RUN_JOB,
        )
        definition_body = aws_stepfunctions.DefinitionBody.from_chainable(batch_task)
        statemachine = aws_stepfunctions.StateMachine(
            stack, "statemachine", definition_body=definition_body
        )

        cdk.CfnOutput(stack, "StateMachineArn", value=statemachine.state_machine_arn)

        with infra.provisioner() as prov:
            yield prov

    @markers.aws.validated
    @pytest.mark.skip_store_check(
        reason="cannot pickle `socket` object for moto.batch.models.BatchBackend"
    )
    def test_batch_request_response(
        self,
        infrastructure_batch_request_response,
        aws_client,
        create_iam_role_for_sfn,
        create_state_machine,
        sfn_batch_snapshot,
    ):
        outputs = infrastructure_batch_request_response.get_stack_outputs(
            stack_name="infrastructure-batch-request-response"
        )
        state_machine_arn = outputs["StateMachineArn"]
        execution_input = json.dumps({})
        launch_and_record_execution(
            aws_client.stepfunctions,
            sfn_batch_snapshot,
            state_machine_arn,
            execution_input,
        )

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(paths=_SYNC_SKIP_SNAPSHOT_VERIFY)
    @pytest.mark.skip_store_check(
        reason="cannot pickle `socket` object for moto.batch.models.BatchBackend"
    )
    def test_batch_sync(
        self,
        infrastructure_batch_sync,
        aws_client,
        create_iam_role_for_sfn,
        create_state_machine,
        sfn_batch_snapshot,
    ):
        outputs = infrastructure_batch_sync.get_stack_outputs(
            stack_name="infrastructure-batch-sync"
        )
        state_machine_arn = outputs["StateMachineArn"]
        execution_input = json.dumps({})
        launch_and_record_execution(
            aws_client.stepfunctions,
            sfn_batch_snapshot,
            state_machine_arn,
            execution_input,
        )

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(paths=_SYNC_SKIP_SNAPSHOT_VERIFY)
    @pytest.mark.skip_store_check(
        reason="cannot pickle `socket` object for moto.batch.models.BatchBackend"
    )
    def test_batch_invalid(
        self,
        infrastructure_batch_invalid,
        aws_client,
        create_iam_role_for_sfn,
        create_state_machine,
        sfn_batch_snapshot,
    ):
        sfn_batch_snapshot.add_transformer(
            RegexTransformer("RequestId: [a-zA-Z0-9-]+", "RequestId: <request_id>")
        )
        sfn_batch_snapshot.add_transformer(
            RegexTransformer("Request ID: [a-zA-Z0-9-]+", "Request ID: <request_id>")
        )
        outputs = infrastructure_batch_invalid.get_stack_outputs(
            stack_name="infrastructure-batch-invalid"
        )
        state_machine_arn = outputs["StateMachineArn"]
        execution_input = json.dumps({})
        launch_and_record_execution(
            aws_client.stepfunctions,
            sfn_batch_snapshot,
            state_machine_arn,
            execution_input,
        )

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(paths=_SYNC_SKIP_SNAPSHOT_VERIFY)
    @pytest.mark.skip_store_check(
        reason="cannot pickle `socket` object for moto.batch.models.BatchBackend"
    )
    def test_batch_failure(
        self,
        infrastructure_batch_failure,
        aws_client,
        create_iam_role_for_sfn,
        create_state_machine,
        sfn_batch_snapshot,
    ):
        outputs = infrastructure_batch_failure.get_stack_outputs(
            stack_name="infrastructure-batch-failure"
        )
        state_machine_arn = outputs["StateMachineArn"]
        execution_input = json.dumps({})
        launch_and_record_execution(
            aws_client.stepfunctions,
            sfn_batch_snapshot,
            state_machine_arn,
            execution_input,
        )
