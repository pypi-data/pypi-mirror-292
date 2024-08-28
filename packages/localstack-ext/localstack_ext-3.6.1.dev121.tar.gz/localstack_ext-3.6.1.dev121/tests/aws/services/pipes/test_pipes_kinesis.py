import base64
import json
import os

import aws_cdk as cdk
import pytest
from aws_cdk import aws_iam as iam
from aws_cdk import aws_kinesis as kinesis
from aws_cdk import aws_lambda as lambda_
from aws_cdk import aws_pipes as pipes
from aws_cdk import aws_sqs as sqs
from localstack.aws.api.pipes import PipeState
from localstack.testing.aws.util import is_aws_cloud
from localstack.testing.pytest import markers
from localstack.utils.files import load_file
from localstack.utils.sync import poll_condition

from tests.aws.services.pipes.test_pipes import get_shard_iterator

STACK_NAME = "PipesKinesisStack"

THIS_FOLDER = os.path.dirname(os.path.realpath(__file__))
TEST_LAMBDA_PYTHON_ENRICHMENT = os.path.join(THIS_FOLDER, "functions/enrichment_trigger_fail.py")


@markers.acceptance_test
class TestPipesKinesis:
    """
    Tests an EventBridge pipe using a source Kinesis stream with SQS DLQ => Lambda enrichment => target Kinesis stream
    * test_kinesis_dlq_behavior: event batches that contain a failed event should be sent to the SQS DLQ

    Similar to the following pattern from Serverless Land:
    https://serverlessland.com/patterns/content-filter-pattern-kinesis-cdk
    """

    @pytest.fixture(scope="class", autouse=True)
    def infrastructure(self, aws_client, infrastructure_setup):
        infra = infrastructure_setup(namespace="PipesKinesis")

        stack = cdk.Stack(infra.cdk_app, STACK_NAME)

        # Resources
        source_stream = kinesis.Stream(stack, "SourceStream", shard_count=3)
        dlq = sqs.Queue(stack, "DLQ")
        enrichment_function = lambda_.Function(
            stack,
            "Function",
            runtime=lambda_.Runtime.PYTHON_3_12,
            handler="index.handler",
            code=lambda_.InlineCode(code=load_file(TEST_LAMBDA_PYTHON_ENRICHMENT)),
        )

        target_stream = kinesis.Stream(stack, "TargetStream", shard_count=1)

        # IAM
        pipe_role = iam.Role(
            stack, "PipeRole", assumed_by=iam.ServicePrincipal("pipes.amazonaws.com")
        )
        source_stream.grant_read(pipe_role)
        dlq.grant_send_messages(pipe_role)
        enrichment_function.grant_invoke(pipe_role)
        target_stream.grant_write(pipe_role)

        # Pipe
        pipe = pipes.CfnPipe(
            stack,
            "Pipe",
            role_arn=pipe_role.role_arn,
            source=source_stream.stream_arn,
            source_parameters=pipes.CfnPipe.PipeSourceParametersProperty(
                kinesis_stream_parameters=pipes.CfnPipe.PipeSourceKinesisStreamParametersProperty(
                    starting_position="TRIM_HORIZON",
                    dead_letter_config=pipes.CfnPipe.DeadLetterConfigProperty(arn=dlq.queue_arn),
                    maximum_retry_attempts=1,
                    batch_size=2,
                ),
            ),
            enrichment=enrichment_function.function_arn,
            target=target_stream.stream_arn,
            target_parameters=pipes.CfnPipe.PipeTargetParametersProperty(
                kinesis_stream_parameters=pipes.CfnPipe.PipeTargetKinesisStreamParametersProperty(
                    partition_key="target-partition-key-0"
                )
            ),
        )

        # Outputs
        cdk.CfnOutput(stack, "PipeName", value=pipe.ref)
        cdk.CfnOutput(stack, "SourceStreamName", value=source_stream.stream_name)
        cdk.CfnOutput(stack, "DlqUrl", value=dlq.queue_url)
        cdk.CfnOutput(stack, "DlqName", value=dlq.queue_name)
        cdk.CfnOutput(stack, "EnrichmentFunctionName", value=enrichment_function.function_name)
        cdk.CfnOutput(stack, "TargetStreamName", value=target_stream.stream_name)
        cdk.CfnOutput(stack, "RoleName", value=pipe_role.role_name)

        with infra.provisioner() as prov:
            yield prov

    @markers.snapshot.skip_snapshot_verify(
        paths=[
            # TODO: test and implement state reason lifecycle
            "$..StateReason",
        ]
    )
    @markers.aws.validated
    def test_kinesis_dlq_behavior(self, aws_client, infrastructure, snapshot):
        # Assign outputs
        outputs = infrastructure.get_stack_outputs(stack_name=STACK_NAME)
        pipe_name = outputs["PipeName"]
        source_stream_name = outputs["SourceStreamName"]
        dlq_url = outputs["DlqUrl"]
        dlq_name = outputs["DlqName"]
        enrichment_function_name = outputs["EnrichmentFunctionName"]
        target_stream_name = outputs["TargetStreamName"]
        role_name = outputs["RoleName"]

        # Define transformers
        snapshot.add_transformer(snapshot.transform.regex(pipe_name, "<pipe-name>"))
        snapshot.add_transformer(snapshot.transform.regex(role_name, "<role-name>"))
        snapshot.add_transformer(
            snapshot.transform.regex(source_stream_name, "<source-stream-name>")
        )
        snapshot.add_transformer(snapshot.transform.regex(dlq_name, "<dlq-name>"))
        snapshot.add_transformer(
            snapshot.transform.key_value("approximateArrivalTimestamp", reference_replacement=False)
        )
        snapshot.add_transformer(snapshot.transform.key_value("sequenceNumber"))
        snapshot.add_transformer(snapshot.transform.key_value("startSequenceNumber"))
        snapshot.add_transformer(snapshot.transform.key_value("endSequenceNumber"))
        snapshot.add_transformer(
            snapshot.transform.regex(enrichment_function_name, "<enrichment-function-name>")
        )
        snapshot.add_transformer(
            snapshot.transform.regex(target_stream_name, "<target-stream-name>")
        )

        # Wait until the pipe is ready
        def _is_pipe_running():
            result = aws_client.pipes.describe_pipe(Name=pipe_name)
            return result["CurrentState"] == PipeState.RUNNING

        timeout = 60 if is_aws_cloud() else 20
        poll_condition(_is_pipe_running, timeout=timeout, interval=2)

        describe_pipe_response = aws_client.pipes.describe_pipe(Name=pipe_name)
        snapshot.match("describe_pipe_response", describe_pipe_response)

        # Initialize target iterator before triggering pipe
        target_iterator = get_shard_iterator(target_stream_name, aws_client.kinesis)

        # Trigger pipe
        # Sending 16 records at once with batch size 2 should trigger 8 batches with 2 Kinesis records each.
        # The "fail" parameter triggers a failure for every 4th event. This causes half of the batches to fail because
        # an event marked as "fail" causes its entire batch to fail (i.e., containing an additional non-fail event).
        # Retries will continuously fail because they are tied to the event and each batch with a failing event
        # should end up in the DLQ. `num_records` should be a multiple of 4.
        num_records = 16
        sent_data = []
        for i in range(num_records):
            should_fail = (i + 1) % 4 == 0
            data = {"counter": i + 1, "fail": should_fail}
            sent_data.append(data)

        partition_key = "source-partition-key-0"
        records = [{"Data": json.dumps(data), "PartitionKey": partition_key} for data in sent_data]
        put_records_response = aws_client.kinesis.put_records(
            Records=records, StreamName=source_stream_name
        )
        sent_records = put_records_response["Records"]

        # Validate that the successful events are available in the target Kinesis stream
        target_stream_records = []

        def _has_target_received_records():
            nonlocal target_iterator
            response = aws_client.kinesis.get_records(ShardIterator=target_iterator)
            response_records = response.get("Records")
            target_stream_records.extend(response_records)
            target_iterator = response["NextShardIterator"]
            return len(target_stream_records) == num_records / 2

        # On AWS, it can take several minutes until all messages appear at the target
        timeout = 300 if is_aws_cloud() else 40
        poll_condition(_has_target_received_records, timeout=timeout, interval=2)

        # Parse the "Data" field within the Kinesis record
        received_data = []
        data_1_record = None
        for record in target_stream_records:
            inner_record = json.loads(record["Data"])
            data_string = base64.b64decode(inner_record["data"]).decode("utf-8")
            data = json.loads(data_string)
            received_data.append(data)
            if data["counter"] == 1:
                data_1_record = inner_record
        # Skip every 4th record including its previous record in the same batch
        success_data = [
            data
            for data in sent_data
            if not (data["counter"] % 4 == 0 or (data["counter"] + 1) % 4 == 0)
        ]
        assert received_data == success_data
        snapshot.match("pipe_target_stream_record_data", data_1_record)

        # Validate that the failed events are available in the SQS DLQ
        dlq_events = []

        def _has_dlq_received_messages():
            receive_message_response = aws_client.sqs.receive_message(
                QueueUrl=dlq_url, MessageAttributeNames=["All"]
            )
            if "Messages" in receive_message_response:
                for message in receive_message_response["Messages"]:
                    dlq_event = json.loads(message["Body"])
                    dlq_events.append(dlq_event)
            # Each DLQ event has a batchSize indicating how many events are part of the failed batch
            dlq_batch_sizes = [event["KinesisBatchInfo"]["batchSize"] for event in dlq_events]
            return sum(dlq_batch_sizes) == num_records / 2

        # On AWS, it can take several minutes until all messages appear at the target
        timeout = 300 if is_aws_cloud() else 40
        poll_condition(_has_dlq_received_messages, timeout=timeout, interval=2)

        sorted_dlq_events = sorted(dlq_events, key=lambda x: x["timestamp"])
        first_dlq_event = sorted_dlq_events[0]
        last_dlq_event = sorted_dlq_events[-1]

        # Validate that the first and last failing event have the correct sequence number.
        # The 4th records at [3] is the first to fail, but it includes the 3rd record at [2] in the same batch
        first_failed_event = sent_records[2]
        last_failed_event = sent_records[-1]
        assert (
            first_dlq_event["KinesisBatchInfo"]["startSequenceNumber"]
            == first_failed_event["SequenceNumber"]
        )
        assert (
            last_dlq_event["KinesisBatchInfo"]["endSequenceNumber"]
            == last_failed_event["SequenceNumber"]
        )
        snapshot.match("pipe_dlq_first_event", first_dlq_event)
