import base64
import json
import os
import time

import pytest
from localstack.aws.api.lambda_ import Runtime
from localstack.aws.api.pipes import (
    CloudwatchLogsLogDestination,
    DynamoDBStreamStartPosition,
    IncludeExecutionDataOption,
    KinesisStreamStartPosition,
    LogLevel,
    PipeLogConfiguration,
    PipeState,
)
from localstack.pro.core.services.pipes.senders.sqs_sender import SqsSender
from localstack.testing.aws.util import is_aws_cloud
from localstack.testing.pytest import markers
from localstack.utils.strings import md5, short_uid
from localstack.utils.sync import poll_condition, retry

THIS_FOLDER = os.path.dirname(os.path.realpath(__file__))
TEST_LAMBDA_PYTHON_ENRICHMENT_ADD = os.path.join(THIS_FOLDER, "functions/enrichment_add_field.py")
TEST_LAMBDA_PYTHON_ENRICHMENT_FAIL = os.path.join(
    THIS_FOLDER, "functions/enrichment_trigger_fail.py"
)
TEST_LAMBDA_PYTHON_S3_INTEGRATION = os.path.join(THIS_FOLDER, "functions/target_s3_integration.py")
TEST_LAMBDA_PYTHON_S3_INTEGRATION_PARTIAL_FAIL = os.path.join(
    THIS_FOLDER, "functions/target_s3_integration_partial_fail.py"
)
TEST_LAMBDA_PYTHON_UNHANDLED_ERROR = os.path.join(THIS_FOLDER, "functions/unhandled_error.py")


@pytest.fixture(autouse=True)
def fixture_snapshot(snapshot):
    snapshot.add_transformer(
        snapshot.transform.key_value(
            "ApproximateFirstReceiveTimestamp", reference_replacement=False
        )
    )
    snapshot.add_transformer(
        snapshot.transform.key_value("SentTimestamp", reference_replacement=False)
    )


# TODO: consolidate with tests.aws.services.kinesis.test_kinesis.get_shard_iterator
def get_shard_iterator(stream_name, kinesis_client):
    response = kinesis_client.describe_stream(StreamName=stream_name)
    sequence_number = (
        response.get("StreamDescription")
        .get("Shards")[0]
        .get("SequenceNumberRange")
        .get("StartingSequenceNumber")
    )
    shard_id = response.get("StreamDescription").get("Shards")[0].get("ShardId")
    response = kinesis_client.get_shard_iterator(
        StreamName=stream_name,
        ShardId=shard_id,
        ShardIteratorType="AT_SEQUENCE_NUMBER",
        StartingSequenceNumber=sequence_number,
    )
    return response.get("ShardIterator")


# TODO: test sending a larger batch than the maximum (it should not send according to docs)
# TODO: test Kinesis DQL with event age expired
class TestPipes:
    @markers.aws.validated
    def test_pipe(
        self,
        aws_client,
        create_role,
        create_policy,
        account_id,
        region_name,
        sqs_create_queue,
        sqs_get_queue_arn,
        snapshot,
        cleanups,
    ):
        """Test a simple pipe from a source SQS queue to a target SQS queue."""
        # Create source resource
        source_queue_name = f"test-queue-source-{short_uid()}"
        source_queue_url = sqs_create_queue(QueueName=source_queue_name)
        source_queue_arn = sqs_get_queue_arn(source_queue_url)
        # Create target resource
        target_queue_name = f"test-queue-target-{short_uid()}"
        target_queue_url = sqs_create_queue(QueueName=target_queue_name)
        target_queue_arn = sqs_get_queue_arn(target_queue_url)

        # Create pipes IAM role
        pipe_name = f"test-pipe-{short_uid()}"
        role_name = f"test-role-pipes-{short_uid()}"
        assume_policy_doc = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"Service": "pipes.amazonaws.com"},
                    "Action": "sts:AssumeRole",
                    "Condition": {
                        "StringEquals": {
                            "aws:SourceAccount": account_id,
                            # The AWS console automatically creates an additional restriction
                            "aws:SourceArn": f"arn:aws:pipes:{region_name}:{account_id}:pipe/{pipe_name}",
                        }
                    },
                }
            ],
        }
        result = create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(assume_policy_doc),
            iam_client=aws_client.iam,
        )
        role_arn = result["Role"]["Arn"]

        # Attach source policy
        source_policy_name = f"test-policy-sqs-source-{short_uid()}"
        source_queue_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    # TODO: ensure that sqs:GetQueueAttributes is used for IAM features
                    "Action": ["sqs:ReceiveMessage", "sqs:DeleteMessage", "sqs:GetQueueAttributes"],
                    "Resource": [source_queue_arn],
                }
            ],
        }
        source_policy_arn = create_policy(
            PolicyName=source_policy_name, PolicyDocument=json.dumps(source_queue_policy)
        )["Policy"]["Arn"]
        aws_client.iam.attach_role_policy(RoleName=role_name, PolicyArn=source_policy_arn)

        # Attach target policy
        target_policy_name = f"test-policy-sqs-target-{short_uid()}"
        target_queue_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {"Effect": "Allow", "Action": ["sqs:SendMessage"], "Resource": [target_queue_arn]}
            ],
        }
        target_policy_arn = create_policy(
            PolicyName=target_policy_name, PolicyDocument=json.dumps(target_queue_policy)
        )["Policy"]["Arn"]
        aws_client.iam.attach_role_policy(RoleName=role_name, PolicyArn=target_policy_arn)

        # Create pipe
        snapshot.add_transformer(snapshot.transform.regex(pipe_name, "<pipe-name>"))
        snapshot.add_transformer(snapshot.transform.regex(role_name, "<role-name>"))
        # Alternatively use SQS service transformer: snapshot.add_transformer(snapshot.transform.sqs_api())
        snapshot.add_transformer(snapshot.transform.regex(source_queue_name, "<source-queue-name>"))
        snapshot.add_transformer(
            snapshot.transform.key_value("SenderId", reference_replacement=False)
        )
        snapshot.add_transformer(snapshot.transform.key_value("receiptHandle"))
        snapshot.add_transformer(snapshot.transform.key_value("ReceiptHandle"))
        snapshot.add_transformer(snapshot.transform.key_value("MD5OfBody"))
        snapshot.add_transformer(snapshot.transform.regex(target_queue_name, "<target-queue-name>"))
        # TODO: create fixture handling cleanup
        create_pipe_response = aws_client.pipes.create_pipe(
            Name=pipe_name,
            RoleArn=role_arn,
            Source=source_queue_arn,
            Target=target_queue_arn,
        )
        snapshot.match("create_pipe_response", create_pipe_response)
        cleanups.append(lambda: aws_client.pipes.delete_pipe(Name=pipe_name))

        # Wait until the pipe is ready
        def _is_pipe_running():
            result = aws_client.pipes.describe_pipe(Name=pipe_name)
            return result["CurrentState"] == PipeState.RUNNING

        timeout = 60 if is_aws_cloud() else 20
        assert poll_condition(_is_pipe_running, timeout=timeout, interval=2)

        describe_pipe_response = aws_client.pipes.describe_pipe(Name=pipe_name)
        snapshot.match("describe_pipe_response", describe_pipe_response)

        # Trigger pipe
        message_body = "message-1"
        # TODO: maybe snapshot response for matching details with received message
        aws_client.sqs.send_message(QueueUrl=source_queue_url, MessageBody=message_body)

        # Assert that the message has been received on the target queue
        def receive_message():
            rs = aws_client.sqs.receive_message(
                QueueUrl=target_queue_url, MessageAttributeNames=["All"]
            )
            assert len(rs["Messages"]) > 0
            return rs["Messages"][0]

        message = retry(receive_message, retries=15, sleep=2)
        snapshot.match("pipe_target_message", message)
        # Parse the nested SQS message in the Body
        received_message = json.loads(message["Body"])
        assert received_message["body"] == message_body

        # Check that the message is deleted from the source queue
        source_queue_response = aws_client.sqs.receive_message(
            QueueUrl=source_queue_url, MessageAttributeNames=["All"]
        )
        assert "Messages" not in source_queue_response

        # Delete pipe
        delete_pipe_response = aws_client.pipes.delete_pipe(Name=pipe_name)
        snapshot.match("delete_pipe_response", delete_pipe_response)

        describe_pipe_response_postdelete = aws_client.pipes.describe_pipe(Name=pipe_name)
        snapshot.match("describe_pipe_response_postdelete", describe_pipe_response_postdelete)

        # TODO: poll describe_pipe until gone?!

    @markers.aws.validated
    def test_pipe_filter_enrichment(
        self,
        aws_client,
        create_role,
        create_policy,
        account_id,
        sqs_create_queue,
        sqs_get_queue_arn,
        create_lambda_function,
        snapshot,
        cleanups,
    ):
        """Test a simple pipe from a source SQS queue to a target SQS queue with filter and enrichment."""
        # Create source resource
        source_queue_name = f"test-queue-source-{short_uid()}"
        source_queue_url = sqs_create_queue(QueueName=source_queue_name)
        source_queue_arn = sqs_get_queue_arn(source_queue_url)
        # Create target resource
        target_queue_name = f"test-queue-target-{short_uid()}"
        target_queue_url = sqs_create_queue(QueueName=target_queue_name)
        target_queue_arn = sqs_get_queue_arn(target_queue_url)

        # Create enrichment Lambda
        function_name = f"test-enrichment-{short_uid()}"
        create_function_response = create_lambda_function(
            handler_file=TEST_LAMBDA_PYTHON_ENRICHMENT_ADD,
            func_name=function_name,
            runtime=Runtime.python3_12,
        )
        enrichment_lambda_arn = create_function_response["CreateFunctionResponse"]["FunctionArn"]
        enrichment_lambda_name = create_function_response["CreateFunctionResponse"]["FunctionName"]

        # Create pipes IAM role
        role_name = f"test-role-pipes-{short_uid()}"
        assume_policy_doc = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"Service": "pipes.amazonaws.com"},
                    "Action": "sts:AssumeRole",
                    "Condition": {
                        "StringEquals": {
                            "aws:SourceAccount": account_id,
                        }
                    },
                }
            ],
        }
        result = create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(assume_policy_doc),
            iam_client=aws_client.iam,
        )
        role_arn = result["Role"]["Arn"]

        # Attach source policy
        source_policy_name = f"test-policy-sqs-source-{short_uid()}"
        source_queue_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    # TODO: ensure that sqs:GetQueueAttributes is used for IAM features
                    "Action": ["sqs:ReceiveMessage", "sqs:DeleteMessage", "sqs:GetQueueAttributes"],
                    "Resource": [source_queue_arn],
                }
            ],
        }
        source_policy_arn = create_policy(
            PolicyName=source_policy_name, PolicyDocument=json.dumps(source_queue_policy)
        )["Policy"]["Arn"]
        aws_client.iam.attach_role_policy(RoleName=role_name, PolicyArn=source_policy_arn)

        enrichment_policy_name = f"test-policy-sqs-enrichment-{short_uid()}"
        enrichment_lambda_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": ["lambda:InvokeFunction"],
                    "Resource": [enrichment_lambda_arn],
                }
            ],
        }
        enrichment_policy_arn = create_policy(
            PolicyName=enrichment_policy_name, PolicyDocument=json.dumps(enrichment_lambda_policy)
        )["Policy"]["Arn"]
        aws_client.iam.attach_role_policy(RoleName=role_name, PolicyArn=enrichment_policy_arn)

        # Attach target policy
        target_policy_name = f"test-policy-sqs-target-{short_uid()}"
        target_queue_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {"Effect": "Allow", "Action": ["sqs:SendMessage"], "Resource": [target_queue_arn]}
            ],
        }
        target_policy_arn = create_policy(
            PolicyName=target_policy_name, PolicyDocument=json.dumps(target_queue_policy)
        )["Policy"]["Arn"]
        aws_client.iam.attach_role_policy(RoleName=role_name, PolicyArn=target_policy_arn)

        # Create pipe
        pipe_name = f"test-pipe-{short_uid()}"
        snapshot.add_transformer(snapshot.transform.regex(pipe_name, "<pipe-name>"))
        snapshot.add_transformer(snapshot.transform.regex(role_name, "<role-name>"))
        # Alternatively use SQS service transformer: snapshot.add_transformer(snapshot.transform.sqs_api())
        snapshot.add_transformer(snapshot.transform.regex(source_queue_name, "<source-queue-name>"))
        snapshot.add_transformer(
            snapshot.transform.key_value("SenderId", reference_replacement=False)
        )
        snapshot.add_transformer(snapshot.transform.key_value("receiptHandle"))
        snapshot.add_transformer(snapshot.transform.key_value("ReceiptHandle"))
        snapshot.add_transformer(snapshot.transform.key_value("MD5OfBody"))
        snapshot.add_transformer(snapshot.transform.regex(target_queue_name, "<target-queue-name>"))
        snapshot.add_transformer(
            snapshot.transform.regex(enrichment_lambda_name, "<enrichment-lambda-name>")
        )

        keep_filter = ["message-1", "message-3"]
        filter_1 = {"body": [keep_filter[0]]}
        filter_2 = {"body": [keep_filter[1]]}
        source_parameters = {
            # TODO: test filter on metadata that should discard all events because pipe-specific fields are added later
            "FilterCriteria": {
                "Filters": [{"Pattern": json.dumps(filter_1)}, {"Pattern": json.dumps(filter_2)}]
            }
        }
        # TODO: create fixture handling cleanup
        create_pipe_response = aws_client.pipes.create_pipe(
            Name=pipe_name,
            RoleArn=role_arn,
            Source=source_queue_arn,
            SourceParameters=source_parameters,
            Target=target_queue_arn,
            Enrichment=enrichment_lambda_arn,
        )
        snapshot.match("create_pipe_response", create_pipe_response)
        cleanups.append(lambda: aws_client.pipes.delete_pipe(Name=pipe_name))

        # Wait until the pipe is ready
        def _is_pipe_running():
            result = aws_client.pipes.describe_pipe(Name=pipe_name)
            assert result["CurrentState"] != PipeState.CREATE_FAILED
            return result["CurrentState"] == PipeState.RUNNING

        timeout = 60 if is_aws_cloud() else 20
        assert poll_condition(_is_pipe_running, timeout=timeout, interval=2)

        describe_pipe_response = aws_client.pipes.describe_pipe(Name=pipe_name)
        snapshot.match("describe_pipe_response", describe_pipe_response)

        # Trigger pipe
        num_messages = 3
        message_bodies = [f"message-{i + 1}" for i in range(num_messages)]
        sqs_sender = SqsSender(
            target_arn=source_queue_arn, target_parameters={}, target_client=aws_client.sqs
        )
        sqs_sender.send_events(message_bodies)

        # Assert that the message has been received on the target queue
        # Store a mapping of received messages: message_id => message
        messages = {}

        def receive_messages():
            response = aws_client.sqs.receive_message(
                QueueUrl=target_queue_url, MessageAttributeNames=["All"]
            )
            if "Messages" in response:
                for msg in response["Messages"]:
                    messages[msg["MessageId"]] = msg
            assert len(messages) == len(keep_filter)

        retries = 90 if is_aws_cloud() else 20
        retry(receive_messages, retries=retries, sleep=2)
        # Parse the nested SQS message in the Body
        received_message_bodies = []
        for message in messages.values():
            received_message = json.loads(message["Body"])
            assert received_message["enrichment"] == "Hello from Lambda"
            received_message_bodies.append(received_message["body"])
        # Only fifo source queues guarantee the order
        assert set(received_message_bodies) == set(keep_filter)

        # TODO: validate that this happens at the right time for larger number of messages (100+)
        # Check that all messages are deleted from the source queue
        source_queue_response = aws_client.sqs.receive_message(
            QueueUrl=source_queue_url, MessageAttributeNames=["All"]
        )
        assert "Messages" not in source_queue_response

    @markers.aws.validated
    def test_pipe_filter_on_error(
        self,
        aws_client,
        create_role,
        create_policy,
        account_id,
        sqs_create_queue,
        sqs_get_queue_arn,
        create_lambda_function,
        snapshot,
        cleanups,
    ):
        """Test a simple pipe from a source SQS queue with filter to a failing Lambda target.
        The filtered messages should be deleted."""
        # Create DLQ
        dlq_name = f"test-queue-dlq-{short_uid()}"
        dlq_url = sqs_create_queue(QueueName=dlq_name)
        dlq_arn = sqs_get_queue_arn(dlq_url)

        # Create source resource
        source_queue_name = f"test-queue-source-{short_uid()}"
        visibility_timeout_seconds = 10
        source_queue_url = sqs_create_queue(
            QueueName=source_queue_name,
            Attributes={
                "RedrivePolicy": json.dumps(
                    {
                        "deadLetterTargetArn": dlq_arn,
                        "maxReceiveCount": 1,
                    }
                ),
                # Reduce visibility timeout to speed up testing (default 30s)
                "VisibilityTimeout": str(visibility_timeout_seconds),
            },
        )
        source_queue_arn = sqs_get_queue_arn(source_queue_url)
        # Create target Lambda
        function_name = f"test-target-{short_uid()}"
        create_function_response = create_lambda_function(
            handler_file=TEST_LAMBDA_PYTHON_UNHANDLED_ERROR,
            func_name=function_name,
            runtime=Runtime.python3_12,
        )
        target_function_arn = create_function_response["CreateFunctionResponse"]["FunctionArn"]
        target_function_name = create_function_response["CreateFunctionResponse"]["FunctionName"]

        # Create pipes IAM role
        role_name = f"test-role-pipes-{short_uid()}"
        assume_policy_doc = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"Service": "pipes.amazonaws.com"},
                    "Action": "sts:AssumeRole",
                    "Condition": {
                        "StringEquals": {
                            "aws:SourceAccount": account_id,
                        }
                    },
                }
            ],
        }
        result = create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(assume_policy_doc),
            iam_client=aws_client.iam,
        )
        role_arn = result["Role"]["Arn"]

        # Attach source policy
        source_policy_name = f"test-policy-sqs-source-{short_uid()}"
        source_queue_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        # Source queue
                        "sqs:ReceiveMessage",
                        "sqs:DeleteMessage",
                        "sqs:GetQueueAttributes",
                        # DLQ
                        "sqs:SendMessage",
                    ],
                    "Resource": [source_queue_arn, dlq_arn],
                }
            ],
        }
        source_policy_arn = create_policy(
            PolicyName=source_policy_name, PolicyDocument=json.dumps(source_queue_policy)
        )["Policy"]["Arn"]
        aws_client.iam.attach_role_policy(RoleName=role_name, PolicyArn=source_policy_arn)

        # Attach target policy
        target_policy_name = f"test-policy-lambda-target-{short_uid()}"
        target_function_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": ["lambda:InvokeFunction"],
                    "Resource": [target_function_arn],
                }
            ],
        }
        target_policy_arn = create_policy(
            PolicyName=target_policy_name, PolicyDocument=json.dumps(target_function_policy)
        )["Policy"]["Arn"]
        aws_client.iam.attach_role_policy(RoleName=role_name, PolicyArn=target_policy_arn)

        # Create pipe
        pipe_name = f"test-pipe-{short_uid()}"
        snapshot.add_transformer(snapshot.transform.regex(pipe_name, "<pipe-name>"))
        snapshot.add_transformer(snapshot.transform.regex(role_name, "<role-name>"))
        # Alternatively use SQS service transformer: snapshot.add_transformer(snapshot.transform.sqs_api())
        snapshot.add_transformer(snapshot.transform.regex(source_queue_name, "<source-queue-name>"))
        snapshot.add_transformer(
            snapshot.transform.key_value("SenderId", reference_replacement=False)
        )
        snapshot.add_transformer(snapshot.transform.key_value("receiptHandle"))
        snapshot.add_transformer(snapshot.transform.key_value("ReceiptHandle"))
        snapshot.add_transformer(snapshot.transform.key_value("MD5OfBody"))
        snapshot.add_transformer(
            snapshot.transform.regex(target_function_name, "<target-function-name>")
        )

        keep_filter = ["message-3"]
        filter_1 = {"body": keep_filter}
        source_parameters = {"FilterCriteria": {"Filters": [{"Pattern": json.dumps(filter_1)}]}}
        # TODO: create fixture handling cleanup
        create_pipe_response = aws_client.pipes.create_pipe(
            Name=pipe_name,
            RoleArn=role_arn,
            Source=source_queue_arn,
            SourceParameters=source_parameters,
            Target=target_function_arn,
        )
        snapshot.match("create_pipe_response", create_pipe_response)
        cleanups.append(lambda: aws_client.pipes.delete_pipe(Name=pipe_name))

        # Wait until the pipe is ready
        def _is_pipe_running():
            result = aws_client.pipes.describe_pipe(Name=pipe_name)
            assert result["CurrentState"] != PipeState.CREATE_FAILED
            return result["CurrentState"] == PipeState.RUNNING

        timeout = 60 if is_aws_cloud() else 20
        assert poll_condition(_is_pipe_running, timeout=timeout, interval=2)

        describe_pipe_response = aws_client.pipes.describe_pipe(Name=pipe_name)
        snapshot.match("describe_pipe_response", describe_pipe_response)

        # Trigger pipe
        num_messages = 3
        message_bodies = [f"message-{i + 1}" for i in range(num_messages)]
        sqs_sender = SqsSender(
            target_arn=source_queue_arn, target_parameters={}, target_client=aws_client.sqs
        )
        sqs_sender.send_events(message_bodies)

        # Assert that the failed message has been received on the DLQ
        # Store a mapping of received messages: message_id => message
        messages = {}

        def receive_messages():
            response = aws_client.sqs.receive_message(
                QueueUrl=dlq_url,
                MessageAttributeNames=["All"],
                WaitTimeSeconds=10,
            )
            if "Messages" in response:
                entries = []
                for index, msg in enumerate(response["Messages"]):
                    messages[msg["MessageId"]] = msg
                    entries.append({"Id": str(index), "ReceiptHandle": msg["ReceiptHandle"]})
                aws_client.sqs.delete_message_batch(QueueUrl=dlq_url, Entries=entries)
            assert len(messages) == len(keep_filter)

        retries = 9 if is_aws_cloud() else 3
        retry(receive_messages, retries=retries, sleep=1)
        received_msg_bodies = [dlq_msg["Body"] for dlq_msg in messages.values()]
        # The order is not guaranteed (unless using a FIFO queue)
        assert set(received_msg_bodies) == set(keep_filter)

        # Check that all messages are deleted from the source queue
        source_queue_response_1 = aws_client.sqs.receive_message(
            QueueUrl=source_queue_url, MessageAttributeNames=["All"]
        )
        assert "Messages" not in source_queue_response_1

        # TODO: improve this test case by stopping the pipe and then checking once stopping has been implemented
        # stop_pipe_response = aws_client.pipes.stop_pipe(Name=pipe_name)
        # Wait until pipe stopped

        # Check that the filtered out messages do not re-appear in the source queue after the visibility timeout
        time.sleep(visibility_timeout_seconds + 2)
        source_queue_response_2 = aws_client.sqs.receive_message(
            QueueUrl=source_queue_url, MessageAttributeNames=["All"]
        )
        assert "Messages" not in source_queue_response_2

    @markers.snapshot.skip_snapshot_verify(
        paths=[
            # TODO: log awsRequest and awsResponse if `IncludeExecutionData` is enabled
            "$..message.awsRequest",
            "$..message.awsResponse",
            # TODO: test and implement state reason lifecycle
            "$..StateReason",
        ]
    )
    @markers.aws.validated
    def test_pipe_logging(
        self,
        aws_client,
        create_role,
        create_policy,
        account_id,
        sqs_create_queue,
        sqs_get_queue_arn,
        kinesis_create_stream,
        wait_for_stream_ready,
        create_lambda_function,
        snapshot,
        cleanups,
    ):
        """Test logging for a pipe from a source Kinesis stream + DLQ to a target SQS queue with enrichment.
        Logging requires a completely predictable test case using a single fully-featured pipe execution.
        Filtering is part of the poller and is not logged.
        """
        # Create source resource
        source_stream_name = f"test-stream-source-{short_uid()}"
        kinesis_create_stream(StreamName=source_stream_name, ShardCount=1)
        wait_for_stream_ready(source_stream_name)
        source_stream = aws_client.kinesis.describe_stream(StreamName=source_stream_name)
        source_stream_arn = source_stream["StreamDescription"]["StreamARN"]

        # Create DLQ
        dlq_name = f"test-queue-dlq-{short_uid()}"
        dlq_url = sqs_create_queue(QueueName=dlq_name)
        dlq_arn = sqs_get_queue_arn(dlq_url)

        # Create target resource
        target_queue_name = f"test-queue-target-{short_uid()}"
        target_queue_url = sqs_create_queue(QueueName=target_queue_name)
        target_queue_arn = sqs_get_queue_arn(target_queue_url)

        # Create enrichment Lambda
        function_name = f"test-enrichment-{short_uid()}"
        create_function_response = create_lambda_function(
            handler_file=TEST_LAMBDA_PYTHON_ENRICHMENT_FAIL,
            func_name=function_name,
            runtime=Runtime.python3_12,
        )
        enrichment_lambda_arn = create_function_response["CreateFunctionResponse"]["FunctionArn"]
        enrichment_lambda_name = create_function_response["CreateFunctionResponse"]["FunctionName"]

        # Logging
        log_group_name = f"test-log-group-{short_uid()}"
        aws_client.logs.create_log_group(logGroupName=log_group_name)

        def _log_group_created() -> str:
            describe_log_groups_response = aws_client.logs.describe_log_groups(
                logGroupNamePattern=log_group_name
            )
            log_groups = describe_log_groups_response.get("logGroups", [])
            assert len(log_groups) > 0
            return log_groups[0]["arn"]

        # create_log_group does not happen instantly on AWS, even subsequent `describe_log_groups` yield no log groups
        log_group_arn = retry(_log_group_created, retries=10, sleep=0.5)
        cleanups.append(lambda: aws_client.logs.delete_log_group(logGroupName=log_group_name))

        # Create pipes IAM role
        role_name = f"test-role-pipes-{short_uid()}"
        assume_policy_doc = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"Service": "pipes.amazonaws.com"},
                    "Action": "sts:AssumeRole",
                    "Condition": {
                        "StringEquals": {
                            "aws:SourceAccount": account_id,
                        }
                    },
                }
            ],
        }
        result = create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(assume_policy_doc),
            iam_client=aws_client.iam,
        )
        role_arn = result["Role"]["Arn"]

        # Attach source policy
        source_policy_name = f"test-policy-stream-source-{short_uid()}"
        source_stream_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "kinesis:DescribeStream",
                        "kinesis:DescribeStreamSummary",
                        "kinesis:GetRecords",
                        "kinesis:GetShardIterator",
                        "kinesis:ListStreams",
                        "kinesis:ListShards",
                        # "kinesis:SubscribeToShard",
                        "sqs:SendMessage",
                    ],
                    "Resource": [source_stream_arn, dlq_arn],
                },
            ],
        }
        source_policy_arn = create_policy(
            PolicyName=source_policy_name, PolicyDocument=json.dumps(source_stream_policy)
        )["Policy"]["Arn"]
        aws_client.iam.attach_role_policy(RoleName=role_name, PolicyArn=source_policy_arn)

        enrichment_policy_name = f"test-policy-sqs-enrichment-{short_uid()}"
        enrichment_lambda_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": ["lambda:InvokeFunction"],
                    "Resource": [enrichment_lambda_arn],
                }
            ],
        }
        enrichment_policy_arn = create_policy(
            PolicyName=enrichment_policy_name, PolicyDocument=json.dumps(enrichment_lambda_policy)
        )["Policy"]["Arn"]
        aws_client.iam.attach_role_policy(RoleName=role_name, PolicyArn=enrichment_policy_arn)

        # Attach target policy
        target_policy_name = f"test-policy-sqs-target-{short_uid()}"
        target_queue_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {"Effect": "Allow", "Action": ["sqs:SendMessage"], "Resource": [target_queue_arn]}
            ],
        }
        target_policy_arn = create_policy(
            PolicyName=target_policy_name, PolicyDocument=json.dumps(target_queue_policy)
        )["Policy"]["Arn"]
        aws_client.iam.attach_role_policy(RoleName=role_name, PolicyArn=target_policy_arn)

        # Attach logging policy
        logging_policy_name = f"test-policy-logs-logging-{short_uid()}"
        logging_logs_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "logs:CreateLogGroup",
                        "logs:CreateLogStream",
                        "logs:PutLogEvents",
                    ],
                    "Resource": [log_group_arn],
                }
            ],
        }
        logging_policy_arn = create_policy(
            PolicyName=logging_policy_name, PolicyDocument=json.dumps(logging_logs_policy)
        )["Policy"]["Arn"]
        aws_client.iam.attach_role_policy(RoleName=role_name, PolicyArn=logging_policy_arn)

        # Create pipe
        pipe_name = f"test-pipe-{short_uid()}"
        snapshot.add_transformer(snapshot.transform.regex(pipe_name, "<pipe-name>"))
        snapshot.add_transformer(snapshot.transform.regex(role_name, "<role-name>"))
        # Alternatively use SQS service transformer: snapshot.add_transformer(snapshot.transform.sqs_api())
        snapshot.add_transformer(
            snapshot.transform.regex(source_stream_name, "<source-stream-name>")
        )
        snapshot.add_transformer(snapshot.transform.regex(dlq_name, "<dlq-name>"))
        snapshot.add_transformer(
            snapshot.transform.key_value("SenderId", reference_replacement=False)
        )
        snapshot.add_transformer(snapshot.transform.key_value("receiptHandle"))
        snapshot.add_transformer(snapshot.transform.key_value("ReceiptHandle"))
        snapshot.add_transformer(snapshot.transform.key_value("MD5OfBody"))
        snapshot.add_transformer(snapshot.transform.regex(target_queue_name, "<target-queue-name>"))
        snapshot.add_transformer(
            snapshot.transform.regex(enrichment_lambda_name, "<enrichment-lambda-name>")
        )
        # Logging
        snapshot.add_transformer(snapshot.transform.regex(log_group_name, "<log-group-name>"))
        snapshot.add_transformer(
            snapshot.transform.key_value("eventId", reference_replacement=False)
        )
        snapshot.add_transformer(
            snapshot.transform.key_value("awsRequest", reference_replacement=False)
        )
        snapshot.add_transformer(
            snapshot.transform.key_value("awsResponse", reference_replacement=False)
        )
        snapshot.add_transformer(
            snapshot.transform.key_value("timestamp", reference_replacement=False)
        )
        snapshot.add_transformer(
            snapshot.transform.key_value("ingestionTime", reference_replacement=False)
        )
        # TODO: more validation (e.g., extract message body) for such nested fields
        snapshot.add_transformer(
            snapshot.transform.key_value("payload", reference_replacement=False)
        )

        source_parameters = {
            "KinesisStreamParameters": {
                "BatchSize": 1,
                # LATEST could lead to timing issues where a message produced shortly after creating the stream is missed
                "StartingPosition": KinesisStreamStartPosition.TRIM_HORIZON,
                "DeadLetterConfig": {
                    "Arn": dlq_arn,
                },
                "MaximumRetryAttempts": 1,
            },
        }
        # TODO: create fixture handling cleanup
        create_pipe_response = aws_client.pipes.create_pipe(
            Name=pipe_name,
            RoleArn=role_arn,
            Source=source_stream_arn,
            SourceParameters=source_parameters,
            Target=target_queue_arn,
            Enrichment=enrichment_lambda_arn,
            LogConfiguration=PipeLogConfiguration(
                CloudwatchLogsLogDestination=CloudwatchLogsLogDestination(
                    LogGroupArn=log_group_arn,
                ),
                Level=LogLevel.TRACE,
                IncludeExecutionData=[IncludeExecutionDataOption.ALL],
            ),
        )
        snapshot.match("create_pipe_response", create_pipe_response)
        cleanups.append(lambda: aws_client.pipes.delete_pipe(Name=pipe_name))

        # Wait until the pipe is ready
        def _is_pipe_running():
            result = aws_client.pipes.describe_pipe(Name=pipe_name)
            assert result["CurrentState"] != PipeState.CREATE_FAILED
            return result["CurrentState"] == PipeState.RUNNING

        timeout = 60 if is_aws_cloud() else 20
        assert poll_condition(_is_pipe_running, timeout=timeout, interval=2)

        describe_pipe_response = aws_client.pipes.describe_pipe(Name=pipe_name)
        snapshot.match("describe_pipe_response", describe_pipe_response)

        # Trigger pipe
        data_1 = {"message": "message-1", "fail": False}
        aws_client.kinesis.put_record(
            StreamName=source_stream_name,
            Data=json.dumps(data_1),
            PartitionKey="source-partition-key-0",
        )

        # Validate log messages
        num_log_events = 15

        def _log_events_complete():
            log_events = aws_client.logs.filter_log_events(
                logGroupName=log_group_name,
            )["events"]
            # This assertion only works with a fully predictable scenario!
            return len(log_events) >= num_log_events

        timeout = 240 if is_aws_cloud() else 60
        poll_condition(_log_events_complete, timeout=timeout, interval=3)

        log_events = aws_client.logs.filter_log_events(
            logGroupName=log_group_name,
        )["events"]
        snapshot.match("pipe-logs-cloudwatch", log_events)
        assert len(log_events) == num_log_events

        # TODO: add negative assert that log_events don't grow more !!!

        # Delete log stream to test that it gets re-created automatically
        aws_client.logs.delete_log_stream(logGroupName=log_group_name, logStreamName=pipe_name)

        def _log_stream_deleted():
            describe_log_streams_response = aws_client.logs.describe_log_streams(
                logGroupName=log_group_name, logStreamNamePrefix=pipe_name
            )
            log_streams = describe_log_streams_response.get("logStreams")
            return len(log_streams) == 0

        # delete_log_stream does not happen instantly on AWS
        assert poll_condition(_log_stream_deleted, timeout=5, interval=0.5)

        # Trigger pipe
        data_2 = {"message": "message-2", "fail": True}
        aws_client.kinesis.put_record(
            StreamName=source_stream_name,
            Data=json.dumps(data_2),
            PartitionKey="source-partition-key-0",
        )

        # Validate fail log messages
        num_log_events = 18

        def _log_events_complete():
            log_events = aws_client.logs.filter_log_events(
                logGroupName=log_group_name,
            )["events"]
            # This assertion only works with a fully predictable scenario!
            return len(log_events) >= num_log_events

        timeout = 240 if is_aws_cloud() else 60
        poll_condition(_log_events_complete, timeout=timeout, interval=3)

        log_events = aws_client.logs.filter_log_events(
            logGroupName=log_group_name,
        )["events"]
        snapshot.match("pipe-logs-cloudwatch-fail", log_events)
        assert len(log_events) == num_log_events

    @markers.snapshot.skip_snapshot_verify(
        paths=[
            # TODO: test and implement state reason lifecycle
            "$..StateReason",
        ]
    )
    @markers.aws.validated
    def test_kinesis_pipe(
        self,
        aws_client,
        create_role,
        create_policy,
        account_id,
        sqs_create_queue,
        kinesis_create_stream,
        wait_for_stream_ready,
        snapshot,
        cleanups,
    ):
        """Test a pipe from a Kinesis stream as source to a target Kinesis stream."""
        # Create source resource
        source_stream_name = f"test-stream-source-{short_uid()}"
        kinesis_create_stream(StreamName=source_stream_name)
        wait_for_stream_ready(source_stream_name)
        source_stream = aws_client.kinesis.describe_stream(StreamName=source_stream_name)
        source_stream_arn = source_stream["StreamDescription"]["StreamARN"]
        # Create target resource
        target_stream_name = f"test-stream-target-{short_uid()}"
        kinesis_create_stream(StreamName=target_stream_name, ShardCount=1)
        wait_for_stream_ready(target_stream_name)
        target_stream = aws_client.kinesis.describe_stream(StreamName=target_stream_name)
        target_stream_arn = target_stream["StreamDescription"]["StreamARN"]

        # Create pipes IAM role
        role_name = f"test-role-pipes-{short_uid()}"
        assume_policy_doc = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"Service": "pipes.amazonaws.com"},
                    "Action": "sts:AssumeRole",
                    "Condition": {
                        "StringEquals": {
                            "aws:SourceAccount": account_id,
                        }
                    },
                }
            ],
        }
        result = create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(assume_policy_doc),
            iam_client=aws_client.iam,
        )
        role_arn = result["Role"]["Arn"]

        # Attach source policy
        source_policy_name = f"test-policy-stream-source-{short_uid()}"
        source_queue_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    # TODO: ensure these operations are used for proper IAM support
                    # Source: https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-pipes-permissions.html#pipes-perms-ak
                    "Action": [
                        "kinesis:DescribeStream",
                        "kinesis:DescribeStreamSummary",
                        "kinesis:GetRecords",
                        "kinesis:GetShardIterator",
                        "kinesis:ListStreams",
                        "kinesis:ListShards",
                        # TODO: Not created via AWS Console, needed?
                        # "kinesis:SubscribeToShard",
                    ],
                    "Resource": [source_stream_arn],
                }
            ],
        }
        source_policy_arn = create_policy(
            PolicyName=source_policy_name, PolicyDocument=json.dumps(source_queue_policy)
        )["Policy"]["Arn"]
        aws_client.iam.attach_role_policy(RoleName=role_name, PolicyArn=source_policy_arn)

        # Attach target policy
        target_policy_name = f"test-policy-stream-target-{short_uid()}"
        target_stream_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": ["kinesis:PutRecord", "kinesis:PutRecords"],
                    "Resource": [target_stream_arn],
                }
            ],
        }
        target_policy_arn = create_policy(
            PolicyName=target_policy_name, PolicyDocument=json.dumps(target_stream_policy)
        )["Policy"]["Arn"]
        aws_client.iam.attach_role_policy(RoleName=role_name, PolicyArn=target_policy_arn)

        # Create pipe
        pipe_name = f"test-pipe-{short_uid()}"
        snapshot.add_transformer(snapshot.transform.regex(pipe_name, "<pipe-name>"))
        snapshot.add_transformer(snapshot.transform.regex(role_name, "<role-name>"))
        snapshot.add_transformer(
            snapshot.transform.regex(source_stream_name, "<source-stream-name>")
        )
        snapshot.add_transformer(
            snapshot.transform.key_value("approximateArrivalTimestamp", reference_replacement=False)
        )
        snapshot.add_transformer(
            snapshot.transform.key_value("sequenceNumber", reference_replacement=True)
        )
        snapshot.add_transformer(
            snapshot.transform.regex(target_stream_name, "<target-stream-name>")
        )
        # TODO: create fixture handling cleanup
        create_pipe_response = aws_client.pipes.create_pipe(
            Name=pipe_name,
            RoleArn=role_arn,
            Source=source_stream_arn,
            SourceParameters={
                "KinesisStreamParameters": {
                    # LATEST could lead to timing issues where a message produced shortly after creating the stream is missed
                    "StartingPosition": KinesisStreamStartPosition.TRIM_HORIZON
                }
            },
            Target=target_stream_arn,
            TargetParameters={
                "KinesisStreamParameters": {"PartitionKey": "target-partition-key-0"}
            },
        )
        snapshot.match("create_pipe_response", create_pipe_response)
        cleanups.append(lambda: aws_client.pipes.delete_pipe(Name=pipe_name))

        # Wait until the pipe is ready
        def _is_pipe_running():
            result = aws_client.pipes.describe_pipe(Name=pipe_name)
            return result["CurrentState"] == PipeState.RUNNING

        timeout = 60 if is_aws_cloud() else 20
        assert poll_condition(_is_pipe_running, timeout=timeout, interval=2)

        describe_pipe_response = aws_client.pipes.describe_pipe(Name=pipe_name)
        snapshot.match("describe_pipe_response", describe_pipe_response)

        # Initialize target iterator before triggering pipe
        target_iterator = get_shard_iterator(target_stream_name, aws_client.kinesis)

        # Trigger pipe
        num_records = 150
        sent_data = []
        for i in range(num_records):
            data = f"data-{i + 1}"
            aws_client.kinesis.put_record(
                StreamName=source_stream_name,
                Data=data,
                PartitionKey="source-partition-key-0",
            )
            sent_data.append(data)

        # Assert that all records have been received in the target stream
        received_records = []

        def has_received_all_records():
            nonlocal target_iterator
            response = aws_client.kinesis.get_records(ShardIterator=target_iterator)
            response_records = response.get("Records")
            received_records.extend(response_records)
            target_iterator = response["NextShardIterator"]
            return len(received_records) == num_records

        # On AWS, it can take several minutes until all messages appear at the target
        timeout = 300 if is_aws_cloud() else 40
        assert poll_condition(has_received_all_records, timeout=timeout, interval=2)

        # Parse the inner Kinesis event
        received_data = []
        data_1_record = None
        for record in received_records:
            inner_record = json.loads(record["Data"])
            data = base64.b64decode(inner_record["data"]).decode("utf-8")
            received_data.append(data)
            if data == "data-1":
                data_1_record = inner_record
        assert received_data == sent_data
        snapshot.match("pipe_target_stream_record_data", data_1_record)

    @markers.snapshot.skip_snapshot_verify(
        paths=[
            # TODO: test and implement state reason lifecycle
            "$..StateReason",
            # TODO: implement waiting time in Kinesis poller before flushing the events (harder with single thread)
            "$..KinesisBatchInfo..batchSize",
            # TODO: fix account transformer collision with 12-digit shardId
            "$..KinesisBatchInfo..shardId",
            # TODO: fix account transformer collision with 12-digit shardId
            "pipe_target_function_event_1..eventID",
        ]
    )
    @markers.aws.validated
    def test_kinesis_dlq_pipe(
        self,
        aws_client,
        create_role,
        create_policy,
        account_id,
        sqs_create_queue,
        sqs_get_queue_arn,
        kinesis_create_stream,
        wait_for_stream_ready,
        create_lambda_function,
        s3_bucket,
        snapshot,
        cleanups,
    ):
        """Test a pipe from a Kinesis stream as source to a target Lambda with DLQ handling."""
        # Create source resource
        source_stream_name = f"test-stream-source-{short_uid()}"
        kinesis_create_stream(StreamName=source_stream_name, ShardCount=1)
        wait_for_stream_ready(source_stream_name)
        source_stream = aws_client.kinesis.describe_stream(StreamName=source_stream_name)
        source_stream_arn = source_stream["StreamDescription"]["StreamARN"]
        # Create DLQ
        dlq_name = f"test-queue-dlq-{short_uid()}"
        dlq_url = sqs_create_queue(QueueName=dlq_name)
        dlq_arn = sqs_get_queue_arn(dlq_name)

        # Create target resource
        target_function_name = f"test-function-target-{short_uid()}"
        create_function_response = create_lambda_function(
            func_name=target_function_name,
            handler_file=TEST_LAMBDA_PYTHON_S3_INTEGRATION,
            runtime=Runtime.python3_12,
            Environment={"Variables": {"S3_BUCKET_NAME": s3_bucket}},
        )
        target_function_arn = create_function_response["CreateFunctionResponse"]["FunctionArn"]

        # Create pipes IAM role
        role_name = f"test-role-pipes-{short_uid()}"
        assume_policy_doc = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"Service": "pipes.amazonaws.com"},
                    "Action": "sts:AssumeRole",
                    "Condition": {
                        "StringEquals": {
                            "aws:SourceAccount": account_id,
                        }
                    },
                }
            ],
        }
        result = create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(assume_policy_doc),
            iam_client=aws_client.iam,
        )
        role_arn = result["Role"]["Arn"]

        # Attach source policy
        source_policy_name = f"test-policy-stream-source-{short_uid()}"
        source_stream_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    # TODO: ensure these operations are used for proper IAM support
                    # Source: https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-pipes-permissions.html#pipes-perms-ak
                    "Action": [
                        "kinesis:DescribeStream",
                        "kinesis:DescribeStreamSummary",
                        "kinesis:GetRecords",
                        "kinesis:GetShardIterator",
                        "kinesis:ListStreams",
                        "kinesis:ListShards",
                        # TODO: Not created via AWS Console, but mentioned in the docs. Is it needed (under which conditions)?
                        # "kinesis:SubscribeToShard",
                        "sqs:SendMessage",
                    ],
                    "Resource": [source_stream_arn, dlq_arn],
                },
            ],
        }
        source_policy_arn = create_policy(
            PolicyName=source_policy_name, PolicyDocument=json.dumps(source_stream_policy)
        )["Policy"]["Arn"]
        aws_client.iam.attach_role_policy(RoleName=role_name, PolicyArn=source_policy_arn)

        # Attach target policy
        target_policy_name = f"test-policy-function-target-{short_uid()}"
        target_queue_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": ["lambda:InvokeFunction"],
                    "Resource": [target_function_arn],
                }
            ],
        }
        target_policy_arn = create_policy(
            PolicyName=target_policy_name, PolicyDocument=json.dumps(target_queue_policy)
        )["Policy"]["Arn"]
        aws_client.iam.attach_role_policy(RoleName=role_name, PolicyArn=target_policy_arn)

        # Create pipe
        pipe_name = f"test-pipe-{short_uid()}"
        snapshot.add_transformer(snapshot.transform.regex(pipe_name, "<pipe-name>"))
        snapshot.add_transformer(snapshot.transform.regex(role_name, "<role-name>"))
        snapshot.add_transformer(
            snapshot.transform.regex(source_stream_name, "<source-stream-name>")
        )
        snapshot.add_transformer(
            snapshot.transform.key_value("approximateArrivalTimestamp", reference_replacement=False)
        )
        snapshot.add_transformer(
            snapshot.transform.key_value("sequenceNumber", reference_replacement=True)
        )
        snapshot.add_transformer(snapshot.transform.regex(dlq_name, "<dlq-name>"))
        snapshot.add_transformer(snapshot.transform.key_value("startSequenceNumber"))
        snapshot.add_transformer(snapshot.transform.key_value("endSequenceNumber"))
        snapshot.add_transformer(
            snapshot.transform.regex(target_function_name, "<target-function-name>")
        )
        # TODO: create fixture handling cleanup
        maximum_retry_attempts = 1
        create_pipe_response = aws_client.pipes.create_pipe(
            Name=pipe_name,
            RoleArn=role_arn,
            Source=source_stream_arn,
            SourceParameters={
                "KinesisStreamParameters": {
                    # LATEST could lead to timing issues where a message produced shortly after creating the stream is missed
                    "StartingPosition": KinesisStreamStartPosition.TRIM_HORIZON,
                    "DeadLetterConfig": {
                        "Arn": dlq_arn,
                    },
                    "MaximumRetryAttempts": 1,
                },
            },
            Target=target_function_arn,
        )
        snapshot.match("create_pipe_response", create_pipe_response)
        cleanups.append(lambda: aws_client.pipes.delete_pipe(Name=pipe_name))

        # Wait until the pipe is ready
        def _is_pipe_running():
            result = aws_client.pipes.describe_pipe(Name=pipe_name)
            return result["CurrentState"] == PipeState.RUNNING

        timeout = 60 if is_aws_cloud() else 20
        assert poll_condition(_is_pipe_running, timeout=timeout, interval=2)

        describe_pipe_response = aws_client.pipes.describe_pipe(Name=pipe_name)
        snapshot.match("describe_pipe_response", describe_pipe_response)

        # Trigger pipe
        num_records = 3
        sent_data = []
        for i in range(num_records):
            # TODO: test timeout-based DLQ behavior
            data = {"counter": i + 1, "fail": True}
            sent_data.append(data)

        partition_key = "source-partition-key-0"
        records = [{"Data": json.dumps(data), "PartitionKey": partition_key} for data in sent_data]
        put_records_response = aws_client.kinesis.put_records(
            Records=records, StreamName=source_stream_name
        )
        sent_records = put_records_response["Records"]

        # Assert that the DLQ contains an event for failed batch with exhausted retries
        # Store a mapping of received messages: message_id => message
        received_dlq_events = []

        def receive_dlq_messages():
            response = aws_client.sqs.receive_message(
                QueueUrl=dlq_url, MessageAttributeNames=["All"]
            )
            if "Messages" in response:
                for message in response["Messages"]:
                    received_event = json.loads(message["Body"])
                    received_dlq_events.append(received_event)
                    # Delete DQL message to prevent receiving duplicates
                    aws_client.sqs.delete_message(
                        QueueUrl=dlq_url, ReceiptHandle=message["ReceiptHandle"]
                    )
            # Each DLQ event has a batchSize indicating how many events are part of the failed batch
            received_dlq_batch_sizes = [
                event["KinesisBatchInfo"]["batchSize"] for event in received_dlq_events
            ]
            assert sum(received_dlq_batch_sizes) == num_records

        # Waiting for DLQ messages to appear can take several minutes at AWS
        retries = 90 if is_aws_cloud() else 20
        retry(receive_dlq_messages, retries=retries, sleep=2)
        # Parse the nested SQS message in the Body
        sorted_dlq_events = sorted(received_dlq_events, key=lambda x: x["timestamp"])
        first_dlq_event = sorted_dlq_events[0]
        last_dlq_event = sorted_dlq_events[-1]
        # Validate that the first and last event have the correct sequence number. The batch size might vary!

        assert (
            first_dlq_event["KinesisBatchInfo"]["startSequenceNumber"]
            == sent_records[0]["SequenceNumber"]
        )
        assert (
            last_dlq_event["KinesisBatchInfo"]["endSequenceNumber"]
            == sent_records[-1]["SequenceNumber"]
        )
        snapshot.match("pipe_dlq_first_event", first_dlq_event)

        # Validate that the events get retried and sent multiple times to the target Lambda
        s3_items = get_s3_items(aws_client, s3_bucket)
        received_events = parse_events(s3_items)
        assert len(received_events) == (maximum_retry_attempts + 1) * num_records

    @markers.snapshot.skip_snapshot_verify(
        paths=[
            # TODO: test and implement state reason lifecycle
            "$..StateReason",
            # TODO: some fields different in length
            "$..Message.dynamodb.SizeBytes",
        ]
    )
    @markers.aws.validated
    def test_dynamodb_pipe(
        self,
        aws_client,
        create_role,
        create_policy,
        account_id,
        dynamodb_create_table,
        wait_for_dynamodb_stream_ready,
        sns_create_topic,
        sns_create_sqs_subscription,
        sqs_create_queue,
        sqs_get_queue_arn,
        snapshot,
        cleanups,
    ):
        """Test a pipe from a DynamoDB stream as source to a target SNS, which publishes to a validation SQS queue."""
        # Create source resource
        source_table_name = f"source-table-name-{short_uid()}"
        source_table_response = dynamodb_create_table(
            table_name=source_table_name,
            partition_key="id",
            stream_view_type="NEW_AND_OLD_IMAGES",
            wait_for_active=True,
        )
        source_table_stream_arn = source_table_response["TableDescription"]["LatestStreamArn"]

        # Create target resource
        target_topic_name = f"target-topic-name-{short_uid()}"
        # FIFO SNS topics are not supported:
        # https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-pipes-event-target.html
        create_topic_response = sns_create_topic(Name=target_topic_name)
        target_topic_arn = create_topic_response["TopicArn"]
        # Create validation resource because SNS needs a subscription destination
        validation_queue_name = f"validation-queue-name-{short_uid()}"
        validation_queue_url = sqs_create_queue(QueueName=validation_queue_name)
        validation_queue_arn = sqs_get_queue_arn(validation_queue_name)
        sns_create_sqs_subscription(topic_arn=target_topic_arn, queue_url=validation_queue_url)

        # Create pipes IAM role
        role_name = f"test-role-pipes-{short_uid()}"
        assume_policy_doc = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"Service": "pipes.amazonaws.com"},
                    "Action": "sts:AssumeRole",
                    "Condition": {
                        "StringEquals": {
                            "aws:SourceAccount": account_id,
                        }
                    },
                }
            ],
        }
        result = create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(assume_policy_doc),
            iam_client=aws_client.iam,
        )
        role_arn = result["Role"]["Arn"]

        # Attach source policy
        source_policy_name = f"test-policy-source-{short_uid()}"
        source_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    # TODO: ensure these operations are used for proper IAM support
                    # Source: https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-pipes-permissions.html#pipes-perms-ddb
                    "Action": [
                        "dynamodb:DescribeStream",
                        "dynamodb:GetRecords",
                        "dynamodb:GetShardIterator",
                        "dynamodb:ListStreams",
                    ],
                    "Resource": [source_table_stream_arn],
                }
            ],
        }
        source_policy_arn = create_policy(
            PolicyName=source_policy_name, PolicyDocument=json.dumps(source_policy)
        )["Policy"]["Arn"]
        aws_client.iam.attach_role_policy(RoleName=role_name, PolicyArn=source_policy_arn)

        # Attach target policy
        target_policy_name = f"test-policy-target-{short_uid()}"
        target_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": ["sns:Publish"],
                    "Resource": [target_topic_arn],
                }
            ],
        }
        target_policy_arn = create_policy(
            PolicyName=target_policy_name, PolicyDocument=json.dumps(target_policy)
        )["Policy"]["Arn"]
        aws_client.iam.attach_role_policy(RoleName=role_name, PolicyArn=target_policy_arn)

        # Create pipe
        pipe_name = f"test-pipe-{short_uid()}"
        snapshot.add_transformer(snapshot.transform.regex(pipe_name, "<pipe-name>"))
        snapshot.add_transformer(snapshot.transform.regex(role_name, "<role-name>"))
        snapshot.add_transformer(snapshot.transform.regex(source_table_name, "<source-table-name>"))
        source_stream_date = source_table_stream_arn.split("/")[-1]
        snapshot.add_transformer(
            snapshot.transform.regex(source_stream_date, "<source-stream-date>")
        )
        snapshot.add_transformer(
            snapshot.transform.key_value("approximateArrivalTimestamp", reference_replacement=False)
        )
        snapshot.add_transformer(
            snapshot.transform.key_value("sequenceNumber", reference_replacement=True)
        )
        snapshot.add_transformer(snapshot.transform.regex(target_topic_name, "<target-topic-name>"))
        snapshot.add_transformer(
            snapshot.transform.key_value("eventID", reference_replacement=False)
        )
        snapshot.add_transformer(
            snapshot.transform.key_value("ApproximateCreationDateTime", reference_replacement=False)
        )
        snapshot.add_transformer(
            snapshot.transform.key_value("SequenceNumber", reference_replacement=False)
        )
        snapshot.add_transformer(
            snapshot.transform.key_value("Signature", reference_replacement=False)
        )
        snapshot.add_transformer(
            snapshot.transform.key_value("SigningCertURL", reference_replacement=False)
        )
        snapshot.add_transformer(
            snapshot.transform.key_value("UnsubscribeURL", reference_replacement=False)
        )

        # wait until stream is ready before subscribing - reduces flakes
        wait_for_dynamodb_stream_ready(source_table_stream_arn)
        # TODO: create fixture handling cleanup
        create_pipe_response = aws_client.pipes.create_pipe(
            Name=pipe_name,
            RoleArn=role_arn,
            Source=source_table_stream_arn,
            SourceParameters={
                "DynamoDBStreamParameters": {
                    # LATEST could lead to timing issues where a message produced shortly after creating the stream is missed
                    # https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-pipes-dynamodb.html#pipes-ddb-stream-start-position
                    "StartingPosition": DynamoDBStreamStartPosition.TRIM_HORIZON
                }
            },
            Target=target_topic_arn,
        )
        snapshot.match("create_pipe_response", create_pipe_response)
        cleanups.append(lambda: aws_client.pipes.delete_pipe(Name=pipe_name))

        # Wait until the pipe is ready
        def _is_pipe_running():
            result = aws_client.pipes.describe_pipe(Name=pipe_name)
            return result["CurrentState"] == PipeState.RUNNING

        timeout = 60 if is_aws_cloud() else 20
        assert poll_condition(_is_pipe_running, timeout=timeout, interval=2)

        describe_pipe_response = aws_client.pipes.describe_pipe(Name=pipe_name)
        snapshot.match("describe_pipe_response", describe_pipe_response)

        # Trigger pipe
        item = {"id": {"S": "id-1"}, "counter": {"N": "1"}}
        aws_client.dynamodb.put_item(TableName=source_table_name, Item=item)

        # Assert that all records have been received in the validation SQS queue
        received_messages = []

        def _receive_messages():
            response = aws_client.sqs.receive_message(
                QueueUrl=validation_queue_url, MessageAttributeNames=["All"]
            )
            if "Messages" in response:
                for message in response["Messages"]:
                    received_event = json.loads(message["Body"])
                    received_messages.append(received_event)
                    # Delete message to prevent receiving duplicates
                    aws_client.sqs.delete_message(
                        QueueUrl=validation_queue_url, ReceiptHandle=message["ReceiptHandle"]
                    )
            return len(received_messages) >= 1

        # Wait until all messages are processed: DynamoDB stream => Pipe => SNS => SQS
        # This can take several minutes on AWS. TRIM_HORIZON ensures that all records from DynamoDB should be picked up.
        # The eventual consistency of DynamoDB can add extra delay, which we need to account for when polling here.
        timeout = 500 if is_aws_cloud() else 50
        poll_condition(_receive_messages, timeout=timeout, interval=5)
        # TODO: the eventID has a different length than at AWS (potential DynamoDB local issue?)
        #   e2dee65cf5e69ca9c2f2b85db5a8558f (AWS) vs. 5ac4c2fe (LocalStack)
        # TODO: the SequenceNumber has a different length than at AWS (potential DynamoDB local issue?)
        #  100000000038170464554 (AWS) vs. 49649331286124245432926725054171839041294375507307003906 (LocalStack)
        snapshot.match("received_messages", received_messages)
        assert len(received_messages) == 1

    @markers.snapshot.skip_snapshot_verify(
        paths=[
            # TODO: log awsRequest and awsResponse if `IncludeExecutionData` is enabled
            "$..message.awsRequest",
            "$..message.awsResponse",
        ]
    )
    @markers.aws.validated
    def test_sqs_fifo_dlq_partial_batch_failures(
        self,
        sqs_create_queue,
        sqs_get_queue_arn,
        create_lambda_function,
        s3_bucket,
        create_role,
        create_policy,
        account_id,
        aws_client,
        snapshot,
        cleanups,
    ):
        """Tests a pipe SQS FIFO queue (+ DLQ) => Lambda with partial batch failures.
        Using a FIFO queue makes this test case deterministic because ordering must be ensured.
        Therefore, a failed item blocks the queue of a given MessageGroupId, wherein ordering is guaranteed.
        """
        # Create DLQ
        dlq_name = f"test-queue-dlq-{short_uid()}.fifo"
        dlq_url = sqs_create_queue(QueueName=dlq_name, Attributes={"FifoQueue": "true"})
        dlq_arn = sqs_get_queue_arn(dlq_name)

        # Source SQS queue
        max_receive_count = 2
        source_queue_name = f"test-queue-source-{short_uid()}.fifo"
        source_queue_url = sqs_create_queue(
            QueueName=source_queue_name,
            Attributes={
                "FifoQueue": "true",
                "RedrivePolicy": json.dumps(
                    {
                        "deadLetterTargetArn": dlq_arn,
                        "maxReceiveCount": max_receive_count,
                    }
                ),
                # Reduce visibility timeout to speed up testing (default 30s)
                "VisibilityTimeout": "10",
            },
        )
        source_queue_arn = sqs_get_queue_arn(source_queue_name)

        # Target Lambda function
        target_function_name = f"test-function-target-{short_uid()}"
        create_function_response = create_lambda_function(
            func_name=target_function_name,
            handler_file=TEST_LAMBDA_PYTHON_S3_INTEGRATION_PARTIAL_FAIL,
            runtime=Runtime.python3_12,
            Environment={"Variables": {"S3_BUCKET_NAME": s3_bucket}},
        )
        target_function_arn = create_function_response["CreateFunctionResponse"]["FunctionArn"]

        # Logging
        log_group_name = f"test-log-group-{short_uid()}"
        aws_client.logs.create_log_group(logGroupName=log_group_name)

        def _log_group_created() -> str:
            describe_log_groups_response = aws_client.logs.describe_log_groups(
                logGroupNamePattern=log_group_name
            )
            log_groups = describe_log_groups_response.get("logGroups", [])
            assert len(log_groups) > 0
            return log_groups[0]["arn"]

        # create_log_group does not happen instantly on AWS, even subsequent `describe_log_groups` yield no log groups
        log_group_arn = retry(_log_group_created, retries=10, sleep=0.5)
        cleanups.append(lambda: aws_client.logs.delete_log_group(logGroupName=log_group_name))

        # Create pipes IAM role
        role_name = f"test-role-pipes-{short_uid()}"
        assume_policy_doc = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"Service": "pipes.amazonaws.com"},
                    "Action": "sts:AssumeRole",
                    "Condition": {
                        "StringEquals": {
                            "aws:SourceAccount": account_id,
                        }
                    },
                }
            ],
        }
        result = create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(assume_policy_doc),
            iam_client=aws_client.iam,
        )
        role_arn = result["Role"]["Arn"]

        # Attach source policy
        source_policy_name = f"test-policy-sqs-source-{short_uid()}"
        source_queue_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        # Poller
                        "sqs:ReceiveMessage",
                        "sqs:DeleteMessage",
                        "sqs:GetQueueAttributes",
                        # DLQ
                        "sqs:SendMessage",
                    ],
                    "Resource": [source_queue_arn, dlq_arn],
                }
            ],
        }
        source_policy_arn = create_policy(
            PolicyName=source_policy_name, PolicyDocument=json.dumps(source_queue_policy)
        )["Policy"]["Arn"]
        aws_client.iam.attach_role_policy(RoleName=role_name, PolicyArn=source_policy_arn)

        # Attach target policy
        target_policy_name = f"test-policy-function-target-{short_uid()}"
        target_queue_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": ["lambda:InvokeFunction"],
                    "Resource": [target_function_arn],
                }
            ],
        }
        target_policy_arn = create_policy(
            PolicyName=target_policy_name, PolicyDocument=json.dumps(target_queue_policy)
        )["Policy"]["Arn"]
        aws_client.iam.attach_role_policy(RoleName=role_name, PolicyArn=target_policy_arn)

        # Attach logging policy
        logging_policy_name = f"test-policy-logs-logging-{short_uid()}"
        logging_logs_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "logs:CreateLogGroup",
                        "logs:CreateLogStream",
                        "logs:PutLogEvents",
                    ],
                    "Resource": [log_group_arn],
                }
            ],
        }
        logging_policy_arn = create_policy(
            PolicyName=logging_policy_name, PolicyDocument=json.dumps(logging_logs_policy)
        )["Policy"]["Arn"]
        aws_client.iam.attach_role_policy(RoleName=role_name, PolicyArn=logging_policy_arn)

        # Create pipe
        pipe_name = f"test-pipe-{short_uid()}"
        snapshot.add_transformer(snapshot.transform.regex(pipe_name, "<pipe-name>"))
        snapshot.add_transformer(snapshot.transform.regex(role_name, "<role-name>"))
        snapshot.add_transformer(snapshot.transform.regex(source_queue_name, "<source-queue-name>"))
        snapshot.add_transformer(snapshot.transform.regex(dlq_name, "<dlq-name>"))
        snapshot.add_transformer(
            snapshot.transform.regex(target_function_name, "<target-function-name>")
        )
        snapshot.add_transformer(snapshot.transform.sqs_api())

        # Logging transformers
        snapshot.add_transformer(snapshot.transform.regex(log_group_name, "<log-group-name>"))
        snapshot.add_transformer(
            snapshot.transform.key_value("eventId", reference_replacement=False)
        )
        snapshot.add_transformer(
            snapshot.transform.key_value("awsRequest", reference_replacement=False)
        )
        snapshot.add_transformer(
            snapshot.transform.key_value("awsResponse", reference_replacement=False)
        )
        snapshot.add_transformer(
            snapshot.transform.key_value("timestamp", reference_replacement=False)
        )
        snapshot.add_transformer(
            snapshot.transform.key_value("ingestionTime", reference_replacement=False)
        )
        # TODO: more validation (e.g., extract message body) for such nested fields
        snapshot.add_transformer(
            snapshot.transform.key_value("payload", reference_replacement=False)
        )

        # TODO: create fixture handling cleanup
        create_pipe_response = aws_client.pipes.create_pipe(
            Name=pipe_name,
            RoleArn=role_arn,
            Source=source_queue_arn,
            SourceParameters={
                "SqsQueueParameters": {
                    "BatchSize": 2,
                },
            },
            Target=target_function_arn,
            LogConfiguration=PipeLogConfiguration(
                CloudwatchLogsLogDestination=CloudwatchLogsLogDestination(
                    LogGroupArn=log_group_arn,
                ),
                Level=LogLevel.TRACE,
                IncludeExecutionData=[IncludeExecutionDataOption.ALL],
            ),
        )
        snapshot.match("create_pipe_response", create_pipe_response)
        cleanups.append(lambda: aws_client.pipes.delete_pipe(Name=pipe_name))

        # Wait until the pipe is ready
        def _is_pipe_running():
            result = aws_client.pipes.describe_pipe(Name=pipe_name)
            return result["CurrentState"] == PipeState.RUNNING

        timeout = 40 if is_aws_cloud() else 10
        assert poll_condition(_is_pipe_running, timeout=timeout, interval=2)

        messages = [
            # Batch 1: success
            {"counter": 1, "fail": False},
            {"counter": 2, "fail": False},
            # Batch 2: partial fail
            {"counter": 3, "fail": False},
            {"counter": 4, "fail": True},
            # Batch 3: complete fail
            {"counter": 5, "fail": True},
            {"counter": 6, "fail": True},
        ]
        failed_messages = [message for message in messages if message["fail"]]

        # Trigger pipe
        entries = [
            {
                "Id": str(message["counter"]),
                "MessageBody": json.dumps(message),
                # Required for FIFO queues
                "MessageGroupId": "test-group",
                # Required for FIFO queues if content-based deduplication is not enabled
                "MessageDeduplicationId": str(message["counter"]),
            }
            for message in messages
        ]
        send_message_batch_response = aws_client.sqs.send_message_batch(
            QueueUrl=source_queue_url, Entries=entries
        )

        # Validate that all messages are sent to the target Lambda and failed events get retried
        def _validate_target_invokes():
            s3_items = get_s3_items(aws_client, s3_bucket)
            received_events = parse_events(s3_items)
            # TODO: figure out why max_receive_count=1 causes no retries and max_receive_count=2 causes 2 retries!?
            # TODO: test retry behavior if the target Lambda fails with an exception, which leads to a Lambda retry
            return len(received_events) == len(messages) + len(failed_messages)

        # Multiple retry attempts required and the visibility timeout delays each retry
        timeout = 180 if is_aws_cloud() else 60
        assert poll_condition(_validate_target_invokes, timeout=timeout, interval=4)

        # Validate that all failed messages end up in the DLQ
        # Assert that the DLQ contains an event for failed batch with exhausted retries
        # Store a mapping of received messages: message_id => message
        received_dlq_events = []

        def receive_dlq_messages():
            response = aws_client.sqs.receive_message(
                QueueUrl=dlq_url, MessageAttributeNames=["All"]
            )
            if "Messages" in response:
                for message in response["Messages"]:
                    received_event = json.loads(message["Body"])
                    received_dlq_events.append(received_event)
                    # Delete DQL message to prevent receiving duplicates
                    aws_client.sqs.delete_message(
                        QueueUrl=dlq_url, ReceiptHandle=message["ReceiptHandle"]
                    )
            # With DLQs for SQS, the received DLQ events contain the original event.
            # This behavior differs from DLQs of streaming services such as Kinesis,
            # where the DLQ events only contain metadata.
            return len(received_dlq_events) == len(failed_messages)

        # Waiting for DLQ messages to appear can take several minutes at AWS
        timeout = 240 if is_aws_cloud() else 20
        assert poll_condition(receive_dlq_messages, timeout=timeout, interval=3)

        # Parse the nested SQS message in the Body
        sorted_dlq_events = sorted(received_dlq_events, key=lambda x: x["counter"])
        # Validate that the first and last DLQ event
        first_dlq_event = sorted_dlq_events[0]
        last_dlq_event = sorted_dlq_events[-1]
        sent_message_batch_results = send_message_batch_response["Successful"]
        # Position [3] is the first failed event in `messages` and position [-1] the last one
        assert md5(json.dumps(first_dlq_event)) == sent_message_batch_results[3]["MD5OfMessageBody"]
        assert md5(json.dumps(last_dlq_event)) == sent_message_batch_results[-1]["MD5OfMessageBody"]
        snapshot.match("pipe_dlq_first_event", first_dlq_event)

        # Validate that all messages are deleted in the source queue
        source_queue_response = aws_client.sqs.receive_message(
            QueueUrl=source_queue_url, MessageAttributeNames=["All"]
        )
        assert "Messages" not in source_queue_response

        # Validate partial fail log messages
        num_log_events = 45

        def _log_events_complete():
            log_events = aws_client.logs.filter_log_events(
                logGroupName=log_group_name,
            )["events"]
            # This assertion only works with a fully predictable scenario!
            return len(log_events) >= num_log_events

        timeout = 240 if is_aws_cloud() else 60
        poll_condition(_log_events_complete, timeout=timeout, interval=5)

        log_events = aws_client.logs.filter_log_events(
            logGroupName=log_group_name,
        )["events"]
        snapshot.match("pipe-logs-cloudwatch-fail-partial", log_events)
        assert len(log_events) == num_log_events

    @markers.snapshot.skip_snapshot_verify(
        paths=[
            # TODO: log awsRequest and awsResponse if `IncludeExecutionData` is enabled
            "$..message.awsRequest",
            "$..message.awsResponse",
        ]
    )
    @markers.aws.validated
    def test_sqs_fifo_dlq_partial_batch_failures_delete(
        self,
        sqs_create_queue,
        sqs_get_queue_arn,
        create_lambda_function,
        s3_bucket,
        create_role,
        create_policy,
        account_id,
        aws_client,
        snapshot,
        cleanups,
    ):
        """Tests a pipe SQS FIFO queue (+ DLQ) => Lambda with partial batch failures where the failure happens first.
        Using a FIFO queue makes this test case deterministic because ordering must be ensured.
        Therefore, a failed item blocks the queue of a given MessageGroupId, wherein ordering is guaranteed.
        However, succeeding items within the same batch are deleted out of order if the target doesn't list them as failure.
        """
        # Create DLQ
        dlq_name = f"test-queue-dlq-{short_uid()}.fifo"
        dlq_url = sqs_create_queue(QueueName=dlq_name, Attributes={"FifoQueue": "true"})
        dlq_arn = sqs_get_queue_arn(dlq_name)

        # Source SQS queue
        max_receive_count = 2
        source_queue_name = f"test-queue-source-{short_uid()}.fifo"
        source_queue_url = sqs_create_queue(
            QueueName=source_queue_name,
            Attributes={
                "FifoQueue": "true",
                "RedrivePolicy": json.dumps(
                    {
                        "deadLetterTargetArn": dlq_arn,
                        "maxReceiveCount": max_receive_count,
                    }
                ),
                # Reduce visibility timeout to speed up testing (default 30s)
                "VisibilityTimeout": "10",
            },
        )
        source_queue_arn = sqs_get_queue_arn(source_queue_name)

        # Target Lambda function
        target_function_name = f"test-function-target-{short_uid()}"
        create_function_response = create_lambda_function(
            func_name=target_function_name,
            handler_file=TEST_LAMBDA_PYTHON_S3_INTEGRATION_PARTIAL_FAIL,
            runtime=Runtime.python3_12,
            Environment={"Variables": {"S3_BUCKET_NAME": s3_bucket}},
        )
        target_function_arn = create_function_response["CreateFunctionResponse"]["FunctionArn"]

        # Logging
        log_group_name = f"test-log-group-{short_uid()}"
        aws_client.logs.create_log_group(logGroupName=log_group_name)

        def _log_group_created() -> str:
            describe_log_groups_response = aws_client.logs.describe_log_groups(
                logGroupNamePattern=log_group_name
            )
            log_groups = describe_log_groups_response.get("logGroups", [])
            assert len(log_groups) > 0
            return log_groups[0]["arn"]

        # create_log_group does not happen instantly on AWS, even subsequent `describe_log_groups` yield no log groups
        log_group_arn = retry(_log_group_created, retries=10, sleep=0.5)
        cleanups.append(lambda: aws_client.logs.delete_log_group(logGroupName=log_group_name))

        # Create pipes IAM role
        role_name = f"test-role-pipes-{short_uid()}"
        assume_policy_doc = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"Service": "pipes.amazonaws.com"},
                    "Action": "sts:AssumeRole",
                    "Condition": {
                        "StringEquals": {
                            "aws:SourceAccount": account_id,
                        }
                    },
                }
            ],
        }
        result = create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(assume_policy_doc),
            iam_client=aws_client.iam,
        )
        role_arn = result["Role"]["Arn"]

        # Attach source policy
        source_policy_name = f"test-policy-sqs-source-{short_uid()}"
        source_queue_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        # Poller
                        "sqs:ReceiveMessage",
                        "sqs:DeleteMessage",
                        "sqs:GetQueueAttributes",
                        # DLQ
                        "sqs:SendMessage",
                    ],
                    "Resource": [source_queue_arn, dlq_arn],
                }
            ],
        }
        source_policy_arn = create_policy(
            PolicyName=source_policy_name, PolicyDocument=json.dumps(source_queue_policy)
        )["Policy"]["Arn"]
        aws_client.iam.attach_role_policy(RoleName=role_name, PolicyArn=source_policy_arn)

        # Attach target policy
        target_policy_name = f"test-policy-function-target-{short_uid()}"
        target_queue_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": ["lambda:InvokeFunction"],
                    "Resource": [target_function_arn],
                }
            ],
        }
        target_policy_arn = create_policy(
            PolicyName=target_policy_name, PolicyDocument=json.dumps(target_queue_policy)
        )["Policy"]["Arn"]
        aws_client.iam.attach_role_policy(RoleName=role_name, PolicyArn=target_policy_arn)

        # Attach logging policy
        logging_policy_name = f"test-policy-logs-logging-{short_uid()}"
        logging_logs_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "logs:CreateLogGroup",
                        "logs:CreateLogStream",
                        "logs:PutLogEvents",
                    ],
                    "Resource": [log_group_arn],
                }
            ],
        }
        logging_policy_arn = create_policy(
            PolicyName=logging_policy_name, PolicyDocument=json.dumps(logging_logs_policy)
        )["Policy"]["Arn"]
        aws_client.iam.attach_role_policy(RoleName=role_name, PolicyArn=logging_policy_arn)

        # Create pipe
        pipe_name = f"test-pipe-{short_uid()}"
        snapshot.add_transformer(snapshot.transform.regex(pipe_name, "<pipe-name>"))
        snapshot.add_transformer(snapshot.transform.regex(role_name, "<role-name>"))
        snapshot.add_transformer(snapshot.transform.regex(source_queue_name, "<source-queue-name>"))
        snapshot.add_transformer(snapshot.transform.regex(dlq_name, "<dlq-name>"))
        snapshot.add_transformer(
            snapshot.transform.regex(target_function_name, "<target-function-name>")
        )
        snapshot.add_transformer(snapshot.transform.sqs_api())

        # Logging transformers
        snapshot.add_transformer(snapshot.transform.regex(log_group_name, "<log-group-name>"))
        snapshot.add_transformer(
            snapshot.transform.key_value("eventId", reference_replacement=False)
        )
        snapshot.add_transformer(
            snapshot.transform.key_value("awsRequest", reference_replacement=False)
        )
        snapshot.add_transformer(
            snapshot.transform.key_value("awsResponse", reference_replacement=False)
        )
        snapshot.add_transformer(
            snapshot.transform.key_value("timestamp", reference_replacement=False)
        )
        snapshot.add_transformer(
            snapshot.transform.key_value("ingestionTime", reference_replacement=False)
        )
        # TODO: more validation (e.g., extract message body) for such nested fields
        snapshot.add_transformer(
            snapshot.transform.key_value("payload", reference_replacement=False)
        )

        # TODO: create fixture handling cleanup
        create_pipe_response = aws_client.pipes.create_pipe(
            Name=pipe_name,
            RoleArn=role_arn,
            Source=source_queue_arn,
            SourceParameters={
                "SqsQueueParameters": {
                    "BatchSize": 2,
                },
            },
            Target=target_function_arn,
            LogConfiguration=PipeLogConfiguration(
                CloudwatchLogsLogDestination=CloudwatchLogsLogDestination(
                    LogGroupArn=log_group_arn,
                ),
                Level=LogLevel.TRACE,
                IncludeExecutionData=[IncludeExecutionDataOption.ALL],
            ),
        )
        snapshot.match("create_pipe_response", create_pipe_response)
        cleanups.append(lambda: aws_client.pipes.delete_pipe(Name=pipe_name))

        # Wait until the pipe is ready
        def _is_pipe_running():
            result = aws_client.pipes.describe_pipe(Name=pipe_name)
            return result["CurrentState"] == PipeState.RUNNING

        timeout = 40 if is_aws_cloud() else 10
        assert poll_condition(_is_pipe_running, timeout=timeout, interval=2)

        messages = [
            # Batch 1: partial fail with blocking failure
            {"counter": 1, "fail": True},
            {"counter": 2, "fail": False},
            # TODO: potentially test success following a failure,
            #  which need to block until the failure got retried to ensure strict ordering
            # Batch 2: success
            # {"counter": 5, "fail": False},
            # {"counter": 6, "fail": False},
        ]
        failed_messages = [message for message in messages if message["fail"]]

        # Trigger pipe
        entries = [
            {
                "Id": str(message["counter"]),
                "MessageBody": json.dumps(message),
                # Required for FIFO queues
                "MessageGroupId": "test-group",
                # Required for FIFO queues if content-based deduplication is not enabled
                "MessageDeduplicationId": str(message["counter"]),
            }
            for message in messages
        ]
        send_message_batch_response = aws_client.sqs.send_message_batch(
            QueueUrl=source_queue_url, Entries=entries
        )

        # Validate that all messages are sent to the target Lambda and failed events get retried
        def _validate_target_invokes():
            s3_items = get_s3_items(aws_client, s3_bucket)
            received_events = parse_events(s3_items)
            return len(received_events) == len(messages) + len(failed_messages)

        # Multiple retry attempts required and the visibility timeout delays each retry
        timeout = 180 if is_aws_cloud() else 40
        assert poll_condition(_validate_target_invokes, timeout=timeout, interval=4)
        s3_items = get_s3_items(aws_client, s3_bucket)
        target_invokes_events = {}
        for request_id, target_invoke in s3_items.items():
            events = [event["body"] for event in target_invoke]
            target_invokes_events[request_id] = events

        snapshot.match("target-invokes-events", target_invokes_events)
        # Lower-case receiptHandle needs extra transformer
        snapshot.add_transformer(
            snapshot.transform.key_value("receiptHandle", reference_replacement=False)
        )

        # Validate that all failed messages end up in the DLQ
        # Assert that the DLQ contains an event for failed batch with exhausted retries
        # Store a mapping of received messages: message_id => message
        received_dlq_events = []

        def receive_dlq_messages():
            response = aws_client.sqs.receive_message(
                QueueUrl=dlq_url, MessageAttributeNames=["All"]
            )
            if "Messages" in response:
                for message in response["Messages"]:
                    received_event = json.loads(message["Body"])
                    received_dlq_events.append(received_event)
                    # Delete DQL message to prevent receiving duplicates
                    aws_client.sqs.delete_message(
                        QueueUrl=dlq_url, ReceiptHandle=message["ReceiptHandle"]
                    )
            # With DLQs for SQS, the received DLQ events contain the original event.
            # This behavior differs from DLQs of streaming services such as Kinesis,
            # where the DLQ events only contain metadata.
            return len(received_dlq_events) == len(failed_messages)

        # Waiting for DLQ messages to appear can take several minutes at AWS
        timeout = 240 if is_aws_cloud() else 40
        assert poll_condition(receive_dlq_messages, timeout=timeout, interval=3)

        # TODO: could simplify if only one failure remains in this test case
        # Parse the nested SQS message in the Body
        sorted_dlq_events = sorted(received_dlq_events, key=lambda x: x["counter"])
        # Validate the first and last DLQ event
        first_dlq_event = sorted_dlq_events[0]
        last_dlq_event = sorted_dlq_events[-1]
        sent_message_batch_results = send_message_batch_response["Successful"]
        # Position [0] is the first and last failed event in `messages`
        assert md5(json.dumps(first_dlq_event)) == sent_message_batch_results[0]["MD5OfMessageBody"]
        assert md5(json.dumps(last_dlq_event)) == sent_message_batch_results[0]["MD5OfMessageBody"]
        snapshot.match("pipe_dlq_first_event", first_dlq_event)

        # Validate that all messages are deleted in the source queue
        source_queue_response = aws_client.sqs.receive_message(
            QueueUrl=source_queue_url, MessageAttributeNames=["All"]
        )
        assert "Messages" not in source_queue_response

        # Validate partial fail log messages
        num_log_events = 18

        def _log_events_complete():
            log_events = aws_client.logs.filter_log_events(
                logGroupName=log_group_name,
            )["events"]
            # This assertion only works with a fully predictable scenario!
            return len(log_events) >= num_log_events

        timeout = 240 if is_aws_cloud() else 60
        poll_condition(_log_events_complete, timeout=timeout, interval=5)

        log_events = aws_client.logs.filter_log_events(
            logGroupName=log_group_name,
        )["events"]
        snapshot.match("pipe-logs-cloudwatch-fail-partial", log_events)
        assert len(log_events) == num_log_events

    @markers.aws.validated
    def test_pipe_tags(
        self,
        aws_client,
        create_role,
        create_policy,
        account_id,
        region_name,
        sqs_create_queue,
        sqs_get_queue_arn,
        snapshot,
        cleanups,
    ):
        # Create a SQS source resource
        source_queue_name = f"test-queue-source-{short_uid()}"
        source_queue_url = sqs_create_queue(QueueName=source_queue_name)
        source_queue_arn = sqs_get_queue_arn(source_queue_url)

        # Create SQS target resource
        target_queue_name = f"test-queue-target-{short_uid()}"
        target_queue_url = sqs_create_queue(QueueName=target_queue_name)
        target_queue_arn = sqs_get_queue_arn(target_queue_url)

        # Create pipes IAM role
        pipe_name = f"test-pipe-{short_uid()}"
        role_name = f"test-role-pipes-{short_uid()}"
        assume_policy_doc = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"Service": "pipes.amazonaws.com"},
                    "Action": "sts:AssumeRole",
                    "Condition": {
                        "StringEquals": {
                            "aws:SourceAccount": account_id,
                            "aws:SourceArn": f"arn:aws:pipes:{region_name}:{account_id}:pipe/{pipe_name}",
                        }
                    },
                }
            ],
        }
        result = create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(assume_policy_doc),
            iam_client=aws_client.iam,
        )
        role_arn = result["Role"]["Arn"]

        # Attach source policy
        source_policy_name = f"test-policy-sqs-source-{short_uid()}"
        source_queue_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    # TODO: ensure that sqs:GetQueueAttributes is used for IAM features
                    "Action": ["sqs:ReceiveMessage", "sqs:DeleteMessage", "sqs:GetQueueAttributes"],
                    "Resource": [source_queue_arn],
                }
            ],
        }
        source_policy_arn = create_policy(
            PolicyName=source_policy_name, PolicyDocument=json.dumps(source_queue_policy)
        )["Policy"]["Arn"]
        aws_client.iam.attach_role_policy(RoleName=role_name, PolicyArn=source_policy_arn)

        # Attach target policy
        target_policy_name = f"test-policy-sqs-target-{short_uid()}"
        target_queue_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {"Effect": "Allow", "Action": ["sqs:SendMessage"], "Resource": [target_queue_arn]}
            ],
        }
        target_policy_arn = create_policy(
            PolicyName=target_policy_name, PolicyDocument=json.dumps(target_queue_policy)
        )["Policy"]["Arn"]
        aws_client.iam.attach_role_policy(RoleName=role_name, PolicyArn=target_policy_arn)

        # TODO: create fixture handling cleanup
        pipe_arn = aws_client.pipes.create_pipe(
            Name=pipe_name,
            RoleArn=role_arn,
            Source=source_queue_arn,
            Target=target_queue_arn,
        )["Arn"]
        cleanups.append(lambda: aws_client.pipes.delete_pipe(Name=pipe_name))

        # Wait until the pipe is ready
        def _is_pipe_running():
            result = aws_client.pipes.describe_pipe(Name=pipe_name)
            return result["CurrentState"] == PipeState.RUNNING

        timeout = 60 if is_aws_cloud() else 20
        # This check is added in order to avoid any race condition with the pipe cleanup
        assert poll_condition(_is_pipe_running, timeout=timeout, interval=2)

        tags = {"tagName1": "tagValue1", "tagName2": "tagValue2"}

        # tag the pipe resource
        resp = aws_client.pipes.tag_resource(resourceArn=pipe_arn, tags=tags)
        # TODO: AWS returns HTTPStatusCode 204 while localstack returns 200 for the response.
        assert str(resp["ResponseMetadata"]["HTTPStatusCode"]).startswith("20")

        # list tags for the pipe resource
        list_tags_response = aws_client.pipes.list_tags_for_resource(resourceArn=pipe_arn)
        snapshot.match("list_tags_response", list_tags_response)

        # untag the pipe resource
        resp = aws_client.pipes.untag_resource(resourceArn=pipe_arn, tagKeys=["tagName1"])
        # TODO: AWS returns HTTPStatusCode 204 while localstack returns 200 for the response.
        assert str(resp["ResponseMetadata"]["HTTPStatusCode"]).startswith("20")

        # list tags for the pipe resource after untagging one tag "tagName1"
        list_tags_response = aws_client.pipes.list_tags_for_resource(resourceArn=pipe_arn)
        snapshot.match("list_tags_response_after_untag", list_tags_response)


def get_s3_items(aws_client, s3_bucket) -> dict[str, dict]:
    """Returns a mapping of S3 keys to their parsed JSON content for a given bucket."""
    s3_items = {}
    paginator = aws_client.s3.get_paginator("list_objects_v2")
    page_iterator = paginator.paginate(Bucket=s3_bucket)
    for page in page_iterator:
        for obj in page.get("Contents", []):
            key = obj["Key"]
            get_object_response = aws_client.s3.get_object(Bucket=s3_bucket, Key=key)
            body = json.loads(get_object_response["Body"].read())
            s3_items[key] = body
    return s3_items


def parse_events(s3_items: dict[str, dict]) -> [dict]:
    parsed_events = []
    """Returns a list of events parsed from a dictionary that maps each Lambda invoke (i.e., request-id) to the
    Lambda event (i.e., list of received events)"""
    for _, events in s3_items.items():
        parsed_events.extend(events)
    return parsed_events
