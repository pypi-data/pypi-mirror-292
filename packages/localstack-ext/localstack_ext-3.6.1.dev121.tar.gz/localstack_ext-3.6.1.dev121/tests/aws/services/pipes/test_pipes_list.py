import aws_cdk as cdk
import pytest
from aws_cdk import aws_iam as iam
from aws_cdk import aws_pipes as pipes
from aws_cdk import aws_sqs as sqs
from localstack.testing.pytest import markers
from localstack.utils.strings import short_uid
from localstack_snapshot.snapshots.transformer import SortingTransformer

STACK_NAME = f"PipeListingStack{short_uid()}"


class TestPipesList:
    @pytest.fixture(scope="class", autouse=True)
    def infrastructure(self, aws_client, infrastructure_setup):
        infra = infrastructure_setup(namespace="PipesListing")
        stack = cdk.Stack(infra.cdk_app, stack_name=STACK_NAME)

        """
        In order to properly test filtering by source and target
        we will need 3 pipes and 2 source and 2 target queues
        Queue 1, 2 have same source
        Queue 2, 3 have same target
        """

        # Resources
        source_stream = sqs.Queue(stack, id=short_uid(), queue_name=f"source_queue_{short_uid()}")
        target_stream = sqs.Queue(stack, id=short_uid(), queue_name=f"target_queue_{short_uid()}")

        other_source_stream = sqs.Queue(
            stack, id=short_uid(), queue_name=f"other_source_queue_{short_uid()}"
        )
        other_target_stream = sqs.Queue(
            stack, id=short_uid(), queue_name=f"other_target_queue_{short_uid()}"
        )

        # IAM
        pipe_role = iam.Role(
            stack, "PipeRole", assumed_by=iam.ServicePrincipal("pipes.amazonaws.com")
        )

        source_stream.grant_consume_messages(pipe_role)
        other_source_stream.grant_consume_messages(pipe_role)

        target_stream.grant_send_messages(pipe_role)
        other_target_stream.grant_send_messages(pipe_role)

        # Pipe
        first_pipe = pipes.CfnPipe(
            stack,
            id=short_uid(),
            name=f"pipe-1-{short_uid()}",
            role_arn=pipe_role.role_arn,
            source=source_stream.queue_arn,
            target=target_stream.queue_arn,
        )

        second_pipe = pipes.CfnPipe(
            stack,
            id=short_uid(),
            name=f"pipe-2-{short_uid()}",
            role_arn=pipe_role.role_arn,
            source=source_stream.queue_arn,
            target=other_target_stream.queue_arn,
        )

        third_pipe = pipes.CfnPipe(
            stack,
            id=short_uid(),
            name=f"pipe-3-{short_uid()}",
            role_arn=pipe_role.role_arn,
            source=other_source_stream.queue_arn,
            target=other_target_stream.queue_arn,
        )

        # Outputs
        cdk.CfnOutput(stack, "FirstPipeName", value=first_pipe.ref)
        cdk.CfnOutput(stack, "SecondPipeName", value=second_pipe.ref)
        cdk.CfnOutput(stack, "ThirdPipeName", value=third_pipe.ref)

        cdk.CfnOutput(stack, "FirstSourceQueueName", value=source_stream.queue_name)
        cdk.CfnOutput(stack, "FirstSourceQueueARN", value=source_stream.queue_arn)

        cdk.CfnOutput(stack, "SecondSourceQueueName", value=other_source_stream.queue_name)
        cdk.CfnOutput(stack, "SecondSourceQueueARN", value=other_source_stream.queue_arn)

        cdk.CfnOutput(stack, "FirstTargetQueueName", value=target_stream.queue_name)
        cdk.CfnOutput(stack, "FirstTargetQueueARN", value=target_stream.queue_arn)

        cdk.CfnOutput(stack, "SecondTargetQueueName", value=other_target_stream.queue_name)
        cdk.CfnOutput(stack, "SecondTargetQueueARN", value=other_target_stream.queue_arn)

        with infra.provisioner() as prov:
            yield prov

    def _add_pipe_list_transformers(self, outputs, snapshot):
        # pipes
        first_pipe_name = outputs["FirstPipeName"]
        snapshot.add_transformer(snapshot.transform.regex(first_pipe_name, "<pipe-name:1>"))

        second_pipe_name = outputs["SecondPipeName"]
        snapshot.add_transformer(snapshot.transform.regex(second_pipe_name, "<pipe-name:2>"))

        third_pipe_name = outputs["ThirdPipeName"]
        snapshot.add_transformer(snapshot.transform.regex(third_pipe_name, "<pipe-name:3>"))

        # sources
        first_source_queue = outputs["FirstSourceQueueName"]
        snapshot.add_transformer(
            snapshot.transform.regex(first_source_queue, "<source-queue-name:1>")
        )

        second_source_queue = outputs["SecondSourceQueueName"]
        snapshot.add_transformer(
            snapshot.transform.regex(second_source_queue, "<source-queue-name:2>")
        )

        # targets
        first_target_queue = outputs["FirstTargetQueueName"]
        snapshot.add_transformer(
            snapshot.transform.regex(first_target_queue, "<target-queue-name:1>")
        )

        second_target_queue = outputs["SecondTargetQueueName"]
        snapshot.add_transformer(
            snapshot.transform.regex(second_target_queue, "<target-queue-name:2>")
        )

        snapshot.add_transformer(SortingTransformer("Pipes", lambda x: x["Name"]))

    @markers.aws.validated
    def test_list_pipes_empty(self, aws_client, snapshot):
        prefix = short_uid()
        response = aws_client.pipes.list_pipes(NamePrefix=prefix)
        snapshot.match("no_pipes", response)

    @markers.aws.validated
    def test_list_pipe_name_prefix(self, aws_client, infrastructure, snapshot):
        outputs = infrastructure.get_stack_outputs(stack_name=STACK_NAME)
        self._add_pipe_list_transformers(outputs, snapshot)

        pipe_name = outputs["FirstPipeName"]

        response = aws_client.pipes.list_pipes(NamePrefix=pipe_name)
        snapshot.match("full_name_pipe_response", response)

        prefix = pipe_name[:-3]
        response = aws_client.pipes.list_pipes(NamePrefix=prefix)
        snapshot.match("prefix_pipe_response", response)

    @markers.aws.validated
    def test_list_pipe_target_prefix(self, aws_client, infrastructure, snapshot):
        outputs = infrastructure.get_stack_outputs(stack_name=STACK_NAME)
        self._add_pipe_list_transformers(outputs, snapshot)
        target_arn = outputs["SecondTargetQueueARN"]

        response = aws_client.pipes.list_pipes(TargetPrefix=target_arn)
        snapshot.match("full_target_arn_response", response)

        prefix = target_arn[:-3]
        response = aws_client.pipes.list_pipes(TargetPrefix=prefix)
        snapshot.match("prefix_target_response", response)

    @markers.aws.validated
    def test_list_pipe_source_prefix(self, aws_client, infrastructure, snapshot):
        outputs = infrastructure.get_stack_outputs(stack_name=STACK_NAME)
        self._add_pipe_list_transformers(outputs, snapshot)

        source_arn = outputs["FirstSourceQueueARN"]

        response = aws_client.pipes.list_pipes(SourcePrefix=source_arn)
        snapshot.match("full_source_name_response", response)

        prefix = source_arn[:-3]
        response = aws_client.pipes.list_pipes(SourcePrefix=prefix)
        snapshot.match("prefix_source_response", response)
