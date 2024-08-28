import json

from localstack.aws.api.pipes import PipeState
from localstack.testing.aws.util import is_aws_cloud
from localstack.testing.pytest import markers
from localstack.utils.strings import short_uid
from localstack.utils.sync import poll_condition

from tests.aws.services.pipes.helper_functions import (
    assert_machine_created,
    get_expected_messages_from_sqs,
)


class TestPipesTargets:
    @markers.aws.validated
    def test_target_events(
        self,
        aws_client,
        sqs_create_queue,
        cleanups,
        sqs_get_queue_arn,
        create_role,
        account_id,
        create_policy,
        snapshot,
    ):
        event_pattern = {
            "source": ["custom-source-name"],
            "detail-type": ["Event bridge pipes to event bus"],
            # for wildcard use "account": [account_id],
        }

        # Setup sqs queue to monitor event bridge
        final_queue_name = f"test-queue-final-{short_uid()}"
        final_queue_url = sqs_create_queue(QueueName=final_queue_name)
        final_queue_arn = sqs_get_queue_arn(final_queue_url)
        event_sqs_policy_document = {
            "Version": "2012-10-17",
            "Id": f"sqs-eventbridge-{short_uid()}",
            "Statement": [
                {
                    "Sid": f"SendMessage-{short_uid()}",
                    "Effect": "Allow",
                    "Principal": {"Service": "events.amazonaws.com"},
                    "Action": "sqs:SendMessage",
                    "Resource": final_queue_arn,
                }
            ],
        }
        aws_client.sqs.set_queue_attributes(
            QueueUrl=final_queue_url, Attributes={"Policy": json.dumps(event_sqs_policy_document)}
        )

        # Setup event bridge
        event_bus_name = f"test-bus-{short_uid()}"
        event_bus_arn = aws_client.events.create_event_bus(Name=event_bus_name)["EventBusArn"]
        cleanups.append(lambda: aws_client.events.delete_event_bus(Name=event_bus_name))

        rule_name = f"test-rule-{short_uid()}"
        aws_client.events.put_rule(
            Name=rule_name,
            EventPattern=json.dumps(event_pattern),
            EventBusName=event_bus_name,
        )
        cleanups.append(
            lambda: aws_client.events.delete_rule(Name=rule_name, EventBusName=event_bus_name)
        )

        target_id = f"test-target-{short_uid()}"
        response = aws_client.events.put_targets(
            Rule=rule_name,
            EventBusName=event_bus_name,
            Targets=[
                {
                    "Id": target_id,
                    "Arn": final_queue_arn,
                    # no RoleArn required sqs needs access policy
                }
            ],
        )
        cleanups.append(
            lambda: aws_client.events.remove_targets(
                Rule=rule_name, EventBusName=event_bus_name, Ids=[target_id]
            )
        )
        assert response["FailedEntryCount"] == 0

        # Setup sqs queue pipe source
        source_queue_name = f"test-queue-source-{short_uid()}"
        source_queue_url = sqs_create_queue(QueueName=source_queue_name)
        source_queue_arn = sqs_get_queue_arn(source_queue_url)

        # Setup pipe
        # Create IAM role
        pipes_role_name = f"test-role-pipes-{short_uid()}"
        pipes_policy_document = {
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
            RoleName=pipes_role_name,
            AssumeRolePolicyDocument=json.dumps(pipes_policy_document),
            iam_client=aws_client.iam,
        )
        pipes_role_arn = result["Role"]["Arn"]

        # Attach source policy
        source_policy_name = f"test-policy-sqs-source-{short_uid()}"
        source_queue_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": ["sqs:ReceiveMessage", "sqs:DeleteMessage", "sqs:GetQueueAttributes"],
                    "Resource": [source_queue_arn],
                }
            ],
        }
        source_policy_arn = create_policy(
            PolicyName=source_policy_name, PolicyDocument=json.dumps(source_queue_policy)
        )["Policy"]["Arn"]
        aws_client.iam.attach_role_policy(RoleName=pipes_role_name, PolicyArn=source_policy_arn)

        # Attach target policy
        target_policy_name = f"test-policy-events-target-{short_uid()}"
        target_event_bus_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": ["events:PutEvents"],
                    "Resource": [event_bus_arn],
                }
            ],
        }
        target_policy_arn = create_policy(
            PolicyName=target_policy_name, PolicyDocument=json.dumps(target_event_bus_policy)
        )["Policy"]["Arn"]
        aws_client.iam.attach_role_policy(RoleName=pipes_role_name, PolicyArn=target_policy_arn)

        # Create pipe
        pipe_name = f"test-pipe-{short_uid()}"
        snapshot.add_transformers_list(
            [
                snapshot.transform.regex(source_queue_name, "<source-queue-name>"),
                snapshot.transform.regex(pipe_name, "<pipe-name>"),
                snapshot.transform.regex(pipes_role_name, "<role-name>"),
                snapshot.transform.key_value(
                    "approximateArrivalTimestamp", reference_replacement=False
                ),
                snapshot.transform.key_value("SentTimestamp", reference_replacement=False),
                snapshot.transform.key_value(
                    "ApproximateFirstReceiveTimestamp", reference_replacement=False
                ),
                snapshot.transform.key_value("SenderId", reference_replacement=False),
                snapshot.transform.key_value("ReceiptHandle", reference_replacement=False),
                snapshot.transform.key_value("receiptHandle", reference_replacement=False),
                snapshot.transform.key_value("md5OfBody", reference_replacement=False),
                snapshot.transform.key_value("MD5OfBody", reference_replacement=False),
            ]
        )
        create_pipe_response = aws_client.pipes.create_pipe(
            Name=pipe_name,
            RoleArn=pipes_role_arn,
            Source=source_queue_arn,
            Target=event_bus_arn,
            TargetParameters={
                "EventBridgeEventBusParameters": {
                    "DetailType": event_pattern["detail-type"][0],
                    "Source": event_pattern["source"][0],
                    # TODO test Resources, EndpointId and Time
                }
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

        # Trigger pipe
        message_count = 1
        messages_body = {"message": "Hello, World!"}
        for _ in range(message_count):
            aws_client.sqs.send_message(
                QueueUrl=source_queue_url, MessageBody=json.dumps(messages_body)
            )

        # Get messages from sqs
        messages = get_expected_messages_from_sqs(
            aws_client.sqs,
            final_queue_url,
            expected_message_count=message_count,
            source_service="events",
        )
        snapshot.match("sqs-messages-from-events-from-pipes", messages)

    @markers.aws.validated
    # TODO parametrize wit different {"InvocationType": "FIRE_AND_FORGET" | "REQUEST_RESPONSE"}
    def test_target_stepfunctions(
        self,
        sqs_create_queue,
        sqs_get_queue_arn,
        account_id,
        cleanups,
        state_machine_get_arn,
        create_role,
        create_policy,
        create_iam_role_with_policy,
        snapshot,
        aws_client,
    ):
        # Setup sqs queue to monitor step function
        final_queue_name = f"test-queue-final-{short_uid()}"
        final_queue_url = sqs_create_queue(QueueName=final_queue_name)
        final_queue_arn = sqs_get_queue_arn(final_queue_url)

        # Setup stepfunction as target
        # Create IAM role
        stepfunctions_role_name = f"test-role-stepfunctions-{short_uid()}"
        stepfunctions_role_policy_document = {
            "Version": "2012-10-17",
            "Id": f"stepfunctions-role-{short_uid()}",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"Service": "states.amazonaws.com"},
                    "Action": "sts:AssumeRole",
                }
            ],
        }
        stepfunctions_policy_document = {
            "Version": "2012-10-17",
            "Id": f"stepfunctions-policy-{short_uid()}",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": ["sqs:SendMessage", "sqs:GetQueueAttributes"],
                    "Resource": [final_queue_arn],
                },
                {
                    "Effect": "Allow",
                    "Action": [
                        "logs:CreateLogGroup",
                        "logs:CreateLogStream",
                        "logs:PutLogEvents",
                        "logs:DescribeLogStreams",
                        "logs:GetLogEvents",
                    ],
                    "Resource": ["*"],  # TODO access for logging not working
                },
            ],
        }
        stepfunctions_role_arn = create_iam_role_with_policy(
            RoleName=stepfunctions_role_name,
            RoleDefinition=stepfunctions_role_policy_document,
            PolicyDefinition=stepfunctions_policy_document,
        )

        # Define state machine
        state_machine_sqs_target_definition = {
            "Comment": "Send message to SQS",
            "StartAt": "step1",
            "States": {
                "step1": {
                    "Type": "Task",
                    "Resource": "arn:aws:states:::sqs:sendMessage",
                    "Parameters": {
                        "QueueUrl": final_queue_url,
                        "MessageBody.$": "$",  # pass the complete input as message body
                        # "MessageBody.$": "States.StringToJson($)" convert input to json
                        # "MessageAttributes": {
                        #     "my_attribute": {"DataType": "String", "StringValue": "attribute1"},
                        # }, # TODO MessageAttributes not yet supported by stepfunctions
                    },
                    "End": True,
                },
            },
        }

        # Create state machine
        state_machine_name = f"test-state-machine-{short_uid()}"
        aws_client.stepfunctions.create_state_machine(
            name=state_machine_name,
            definition=json.dumps(state_machine_sqs_target_definition),
            roleArn=stepfunctions_role_arn,
        )
        cleanups.append(
            lambda: aws_client.stepfunctions.delete_state_machine(stateMachineArn=state_machine_arn)
        )
        assert_machine_created(state_machine_name, aws_client.stepfunctions)
        state_machine_arn = state_machine_get_arn(state_machine_name)

        # Setup sqs queue pipe source
        source_queue_name = f"test-queue-source-{short_uid()}"
        source_queue_url = sqs_create_queue(QueueName=source_queue_name)
        source_queue_arn = sqs_get_queue_arn(source_queue_url)

        # Setup pipe
        # Create IAM role
        pipes_role_name = f"test-role-pipes-{short_uid()}"
        pipes_policy_document = {
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
            RoleName=pipes_role_name,
            AssumeRolePolicyDocument=json.dumps(pipes_policy_document),
            iam_client=aws_client.iam,
        )
        pipes_role_arn = result["Role"]["Arn"]

        # Attach source policy
        source_policy_name = f"test-policy-sqs-source-{short_uid()}"
        source_queue_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": ["sqs:ReceiveMessage", "sqs:DeleteMessage", "sqs:GetQueueAttributes"],
                    "Resource": [source_queue_arn],
                }
            ],
        }
        source_policy_arn = create_policy(
            PolicyName=source_policy_name, PolicyDocument=json.dumps(source_queue_policy)
        )["Policy"]["Arn"]
        aws_client.iam.attach_role_policy(RoleName=pipes_role_name, PolicyArn=source_policy_arn)

        # Attach target policy
        target_policy_name = f"test-policy-stepfunction-target-{short_uid()}"
        target_stepfunctions_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": ["states:StartExecution", "states:StartSyncExecution"],
                    "Resource": [state_machine_arn],
                }
            ],
        }
        target_policy_arn = create_policy(
            PolicyName=target_policy_name, PolicyDocument=json.dumps(target_stepfunctions_policy)
        )["Policy"]["Arn"]
        aws_client.iam.attach_role_policy(RoleName=pipes_role_name, PolicyArn=target_policy_arn)

        # Create pipe
        pipe_name = f"test-pipe-{short_uid()}"
        snapshot.add_transformers_list(
            [
                snapshot.transform.regex(source_queue_name, "<source-queue-name>"),
                snapshot.transform.regex(pipe_name, "<pipe-name>"),
                snapshot.transform.regex(pipes_role_name, "<role-name>"),
                snapshot.transform.key_value("SentTimestamp", reference_replacement=False),
                snapshot.transform.key_value(
                    "ApproximateFirstReceiveTimestamp", reference_replacement=False
                ),
                snapshot.transform.key_value("SenderId", reference_replacement=False),
                snapshot.transform.key_value("ReceiptHandle", reference_replacement=False),
                snapshot.transform.key_value("receiptHandle", reference_replacement=False),
                snapshot.transform.key_value("md5OfBody", reference_replacement=False),
                snapshot.transform.key_value("MD5OfBody", reference_replacement=False),
                snapshot.transform.key_value("MD5OfMessageAttributes", reference_replacement=False),
            ]
        )
        create_pipe_response = aws_client.pipes.create_pipe(
            Name=pipe_name,
            RoleArn=pipes_role_arn,
            Source=source_queue_arn,
            Target=state_machine_arn,
            TargetParameters={
                "StepFunctionStateMachineParameters": {"InvocationType": "FIRE_AND_FORGET"}
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

        # Trigger pipe
        message_count = 1
        messages_body = {"message": "Hello, World!"}
        for _ in range(message_count):
            aws_client.sqs.send_message(
                QueueUrl=source_queue_url, MessageBody=json.dumps(messages_body)
            )

        # Get messages from sqs
        messages = get_expected_messages_from_sqs(
            aws_client.sqs, final_queue_url, expected_message_count=message_count
        )
        for message in messages:
            message["Body"] = json.loads(message["Body"])
        snapshot.match("sqs-messages-from-events-from-pipes", messages)
