import json
import time
from enum import Enum
from typing import Callable

import pytest
import requests
from botocore.exceptions import ClientError
from localstack import config
from localstack.aws.api.lambda_ import Runtime
from localstack.constants import APPLICATION_JSON
from localstack.services.apigateway.helpers import host_based_url, path_based_url
from localstack.services.ses.provider import EMAILS_ENDPOINT
from localstack.services.sns.provider import SnsProvider
from localstack.testing.aws.lambda_utils import (
    _await_dynamodb_table_active,
    _await_event_source_mapping_enabled,
)
from localstack.testing.aws.util import is_aws_cloud
from localstack.testing.pytest import markers
from localstack.utils.aws import arns
from localstack.utils.aws.arns import s3_bucket_arn
from localstack.utils.strings import short_uid
from localstack.utils.sync import retry
from localstack.utils.testutil import create_lambda_archive

TEST_LAMBDA_ECHO = """
import json
def handler(event, context):
    print(json.dumps(event))
    return event
"""

TEST_LAMBDA_APIGATEWAY = """
import json

def handler(event, context):
    # Just print the event that was passed to the Lambda
    print(json.dumps(event))
    return {
        "statusCode": 200,
        "body": json.dumps(event),
        "isBase64Encoded": False,
    }
"""

TEST_LAMBDA_APIGATEWAY_AUTHORIZER = """

def handler(event, context):
    statement = {"Action": "execute-api:Invoke", "Effect": "Allow", "Resource": f"{event['methodArn']}*"}
    return {
        "principalId": 'principal123',
        "policyDocument": {"Version": "2012-10-17", "Statement": [statement]},
        "context": {"test": "value"}
    }

"""


LAMBDA_MINIMUM_PERMISSION = """{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "*"
        }
    ]
}
"""

LAMBDA_TRUST_POLICY = """{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
"""


# TODO unify with community
class UrlType(Enum):
    HOST_BASED = 0
    PATH_BASED = 1


class TestInterServiceCommunicationEnforcement:
    @markers.aws.validated
    def test_sns_lambda_subscription(
        self, create_lambda_function, sns_create_topic, create_role, create_policy, aws_client
    ):
        function_name = f"test-function-{short_uid()}"
        role_name = f"test-role-{short_uid()}"
        policy_name = f"test-policy-{short_uid()}"
        role_arn = create_role(RoleName=role_name, AssumeRolePolicyDocument=LAMBDA_TRUST_POLICY)[
            "Role"
        ]["Arn"]
        policy_arn = create_policy(
            PolicyName=policy_name, PolicyDocument=LAMBDA_MINIMUM_PERMISSION
        )["Policy"]["Arn"]
        aws_client.iam.attach_role_policy(RoleName=role_name, PolicyArn=policy_arn)

        function_arn = create_lambda_function(
            handler_file=TEST_LAMBDA_ECHO,
            func_name=function_name,
            runtime=Runtime.python3_12,
            role=role_arn,
        )["CreateFunctionResponse"]["FunctionArn"]
        topic_arn = sns_create_topic()["TopicArn"]
        aws_client.sns.subscribe(TopicArn=topic_arn, Protocol="lambda", Endpoint=function_arn)
        aws_client.sns.publish(Message="Message1", TopicArn=topic_arn)

        # some time for digesting the message
        time.sleep(1)

        aws_client.lambda_.add_permission(
            FunctionName=function_name,
            StatementId="s1",
            Action="lambda:InvokeFunction",
            Principal="sns.amazonaws.com",
            SourceArn=topic_arn,
        )

        aws_client.sns.publish(Message="Message2", TopicArn=topic_arn)

        def assert_events():
            log_events = aws_client.logs.filter_log_events(
                logGroupName=f"/aws/lambda/{function_name}",
            )["events"]
            assert len([e["message"] for e in log_events if e["message"].startswith("REPORT")]) == 1
            assert not any("Message1" in e["message"] for e in log_events)

        retry(assert_events, retries=20, sleep=2)

    @markers.aws.validated
    def test_sns_sqs_subscription(
        self, sns_create_topic, sqs_create_queue, sqs_get_queue_arn, aws_client
    ):
        queue_url = sqs_create_queue()
        queue_arn = sqs_get_queue_arn(queue_url)
        topic_arn = sns_create_topic()["TopicArn"]
        aws_client.sns.subscribe(TopicArn=topic_arn, Protocol="sqs", Endpoint=queue_arn)

        aws_client.sns.publish(Message="Message1", TopicArn=topic_arn)

        # some time for digesting the message
        time.sleep(1)

        policy = {
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"Service": "sns.amazonaws.com"},
                    "Action": "sqs:SendMessage",
                    "Resource": queue_arn,
                    "Condition": {"ArnEquals": {"aws:SourceArn": topic_arn}},
                }
            ]
        }

        aws_client.sqs.set_queue_attributes(
            QueueUrl=queue_url, Attributes={"Policy": json.dumps(policy)}
        )

        aws_client.sns.publish(Message="Message2", TopicArn=topic_arn)

        def _receive_messages():
            messages = aws_client.sqs.receive_message(QueueUrl=queue_url)["Messages"]
            assert len(messages) == 1
            return messages

        messages = retry(_receive_messages, sleep=2, retries=10)
        message = messages[0]
        message_body = message["Body"]
        assert "Message1" not in message_body
        assert "Message2" in message_body

    @markers.aws.validated
    def test_lambda_sqs_destination(
        self,
        create_lambda_function,
        create_role,
        create_policy,
        sqs_create_queue,
        sqs_get_queue_arn,
        aws_client,
    ):
        function_name = f"test-function-{short_uid()}"
        role_name = f"test-role-{short_uid()}"
        policy_name = f"test-policy-{short_uid()}"
        policy_name_sqs = f"test-sqs-policy-{short_uid()}"

        queue_url = sqs_create_queue()
        queue_arn = sqs_get_queue_arn(queue_url)

        role_arn = create_role(RoleName=role_name, AssumeRolePolicyDocument=LAMBDA_TRUST_POLICY)[
            "Role"
        ]["Arn"]
        policy_arn = create_policy(
            PolicyName=policy_name, PolicyDocument=LAMBDA_MINIMUM_PERMISSION
        )["Policy"]["Arn"]
        aws_client.iam.attach_role_policy(RoleName=role_name, PolicyArn=policy_arn)

        create_lambda_function(
            func_name=function_name,
            handler_file=TEST_LAMBDA_ECHO,
            runtime=Runtime.python3_12,
            role=role_arn,
        )

        lambda_sqs_permission = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": ["sqs:SendMessage"],
                    "Resource": queue_arn,
                }
            ],
        }

        policy_arn_sqs = create_policy(
            PolicyName=policy_name_sqs, PolicyDocument=json.dumps(lambda_sqs_permission)
        )["Policy"]["Arn"]
        aws_client.iam.attach_role_policy(RoleName=role_name, PolicyArn=policy_arn_sqs)

        def _put_invoke_config():
            aws_client.lambda_.put_function_event_invoke_config(
                FunctionName=function_name,
                DestinationConfig={
                    "OnSuccess": {"Destination": queue_arn},
                    "OnFailure": {"Destination": queue_arn},
                },
            )

        retry(_put_invoke_config, sleep=4, retries=30)

        aws_client.lambda_.invoke(
            FunctionName=function_name,
            Payload=json.dumps({"payload": "Message1"}),
            InvocationType="Event",
        )

        def _receive_messages():
            messages = aws_client.sqs.receive_message(QueueUrl=queue_url)["Messages"]
            assert len(messages) == 1
            message_body = messages[0]["Body"]
            assert "Message1" in message_body
            aws_client.sqs.delete_message(
                QueueUrl=queue_url, ReceiptHandle=messages[0]["ReceiptHandle"]
            )

        retry(_receive_messages, sleep=3, retries=120)
        aws_client.iam.detach_role_policy(RoleName=role_name, PolicyArn=policy_arn_sqs)

        # give time for permission changes
        time.sleep(30 if is_aws_cloud() else 5)

        aws_client.lambda_.invoke(
            FunctionName=function_name,
            Payload=json.dumps({"payload": "Message2"}),
            InvocationType="Event",
        )

        def assert_events():
            log_events = aws_client.logs.filter_log_events(
                logGroupName=f"/aws/lambda/{function_name}",
            )["events"]
            assert len([e["message"] for e in log_events if e["message"].startswith("REPORT")]) == 2

        retry(assert_events, retries=20, sleep=2)

        # give some time to potentially send the destination message
        time.sleep(150 if is_aws_cloud() else 5)

        messages = aws_client.sqs.receive_message(QueueUrl=queue_url).get("Messages")
        assert messages is None or messages == []

    @markers.aws.only_localstack
    def test_sns_ses_subscription(self, aws_client, sns_create_topic, sqs_create_queue, account_id):
        email = f"recipient-{short_uid()}@localhost"
        aws_client.ses.verify_email_identity(EmailAddress=email)

        topic_arn = sns_create_topic()["TopicArn"]

        subscription = aws_client.sns.subscribe(
            TopicArn=topic_arn,
            Protocol="email",
            Endpoint=email,
            ReturnSubscriptionArn=True,
        )

        store = SnsProvider.get_store(account_id, aws_client.sns.meta.region_name)
        topic_tokens = store.subscription_tokens.get(topic_arn, {})
        for token, sub_arn in topic_tokens.items():
            if sub_arn == subscription["SubscriptionArn"]:
                aws_client.sns.confirm_subscription(TopicArn=topic_arn, Token=token)
                break

        aws_client.sns.publish(Message="Message1", TopicArn=topic_arn)

        emails_url = config.internal_service_url() + EMAILS_ENDPOINT + "?email=admin@localstack.com"

        def _receive_messages():
            messages = requests.get(emails_url).json()["messages"]
            assert len(messages) > 0
            found = False
            for message in messages:
                if email in message["Destination"]["ToAddresses"]:
                    found = True
                    break
            assert found

        retry(_receive_messages, sleep=2, retries=10)

    @pytest.mark.parametrize("path", ["/", "/testpath/"])
    @markers.aws.validated
    def test_lambda_iam(
        self, aws_client, create_role, create_policy, create_lambda_function, snapshot, path
    ):
        function_name = f"test-function-{short_uid()}"
        role_name = f"test-role-{short_uid()}"
        policy_name = f"test-policy-{short_uid()}"

        trust_policy_lambda_deny = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Deny",
                    "Principal": {"Service": "lambda.amazonaws.com"},
                    "Action": "sts:AssumeRole",
                }
            ],
        }
        role_arn = create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(trust_policy_lambda_deny),
            Path=path,
        )["Role"]["Arn"]
        policy_arn = create_policy(
            PolicyName=policy_name, PolicyDocument=LAMBDA_MINIMUM_PERMISSION
        )["Policy"]["Arn"]
        aws_client.iam.attach_role_policy(RoleName=role_name, PolicyArn=policy_arn)

        with pytest.raises(ClientError) as e:
            aws_client.lambda_.create_function(
                FunctionName=function_name,
                Code={"ZipFile": create_lambda_archive(TEST_LAMBDA_ECHO, get_content=True)},
                Runtime=Runtime.python3_12,
                Handler="handler.handler",
                Role=role_arn,
            )
        snapshot.match("create-function-assume-denied", e.value.response)

        aws_client.iam.update_assume_role_policy(
            RoleName=role_name, PolicyDocument=LAMBDA_TRUST_POLICY
        )

        create_lambda_function(
            func_name=function_name,
            handler_file=TEST_LAMBDA_ECHO,
            runtime=Runtime.python3_12,
            role=role_arn,
        )

        invoke_result = aws_client.lambda_.invoke(
            FunctionName=function_name, Payload=json.dumps({"key": "value"})
        )

        snapshot.match("invoke-result", invoke_result)

    @markers.aws.validated
    def test_sns_firehose(
        self,
        sns_create_topic,
        firehose_create_delivery_stream,
        s3_create_bucket,
        sns_subscription,
        create_role,
        aws_client,
        account_id,
        partition,
    ):
        stream_name = f"test-stream-{short_uid()}"
        bucket_name = f"test-bucket-{short_uid()}"
        topic_name = f"test_topic_{short_uid()}"

        assume_role = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"Service": "sns.amazonaws.com"},
                    "Action": "sts:AssumeRole",
                }
            ],
        }
        subscription_role_name = f"test-role-{short_uid()}"
        subscription_role = create_role(
            RoleName=subscription_role_name, AssumeRolePolicyDocument=json.dumps(assume_role)
        )

        data_role_name = f"test-role-{short_uid()}"
        assume_role["Statement"][0]["Principal"]["Service"] = "firehose.amazonaws.com"
        data_role = create_role(
            RoleName=data_role_name, AssumeRolePolicyDocument=json.dumps(assume_role)
        )

        aws_client.iam.put_role_policy(
            RoleName=data_role_name,
            PolicyName="firehose-s3",
            PolicyDocument=json.dumps(
                {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Action": [
                                "s3:PutObject",
                            ],
                            "Resource": f"arn:{partition}:s3:::{bucket_name}/*",
                        }
                    ],
                }
            ),
        )

        if is_aws_cloud():
            time.sleep(15)

        s3_create_bucket(Bucket=bucket_name)

        stream = firehose_create_delivery_stream(
            DeliveryStreamName=stream_name,
            DeliveryStreamType="DirectPut",
            S3DestinationConfiguration={
                "RoleARN": data_role["Role"]["Arn"],
                "BucketARN": f"arn:{partition}:s3:::{bucket_name}",
                "BufferingHints": {"SizeInMBs": 1, "IntervalInSeconds": 60},
            },
        )

        topic = sns_create_topic(Name=topic_name)
        sns_subscription(
            TopicArn=topic["TopicArn"],
            Protocol="firehose",
            Endpoint=stream["DeliveryStreamARN"],
            Attributes={"SubscriptionRoleArn": subscription_role["Role"]["Arn"]},
        )

        aws_client.sns.publish(TopicArn=topic["TopicArn"], Message="Message")

        def validate_content():
            assert "Contents" in aws_client.s3.list_objects(Bucket=bucket_name)

        retries = 5
        sleep = 1
        sleep_before = 0
        if is_aws_cloud():
            retries = 30
            sleep = 20
            sleep_before = 10

        with pytest.raises(AssertionError):
            retry(validate_content, retries=retries, sleep_before=sleep_before, sleep=sleep)

        region_name = aws_client.sns.meta.region_name
        aws_client.iam.put_role_policy(
            RoleName=subscription_role_name,
            PolicyName="sns-firehose",
            PolicyDocument=json.dumps(
                {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Action": ["firehose:PutRecord", "firehose:PutRecordBatch"],
                            "Resource": f"arn:{partition}:firehose:{region_name}:{account_id}:deliverystream/{stream_name}",
                        }
                    ],
                }
            ),
        )

        if is_aws_cloud():
            time.sleep(15)
        aws_client.sns.publish(TopicArn=topic["TopicArn"], Message="Message")
        retry(validate_content, retries=retries, sleep_before=sleep_before, sleep=sleep)

    @markers.aws.validated
    def test_events_sqs(self, aws_client, sqs_create_queue, cleanups):
        queue_url = sqs_create_queue()
        bus_name = f"test-bus-{short_uid()}"
        rule_name = f"test-rule-{short_uid()}"

        aws_client.events.create_event_bus(Name=bus_name)
        cleanups.append(lambda: aws_client.events.delete_event_bus(Name=bus_name))

        aws_client.events.put_rule(
            Name=rule_name,
            EventPattern=json.dumps({"detail": {"EventType": ["0", "1"]}}),
            EventBusName=bus_name,
            State="ENABLED",
        )
        cleanups.append(
            lambda: aws_client.events.delete_rule(Name=rule_name, Force=True, EventBusName=bus_name)
        )

        queue_arn = aws_client.sqs.get_queue_attributes(
            QueueUrl=queue_url, AttributeNames=["QueueArn"]
        )["Attributes"]["QueueArn"]

        aws_client.events.put_targets(
            Rule=rule_name,
            EventBusName=bus_name,
            Targets=[
                {
                    "Id": "1",
                    "Arn": queue_arn,
                    "InputPath": "$.detail.EventType",
                }
            ],
        )
        cleanups.append(
            lambda: aws_client.events.remove_targets(
                Rule=rule_name, Force=True, Ids=["1"], EventBusName=bus_name
            )
        )

        aws_client.events.put_events(
            Entries=[
                {
                    "Source": "core.update-account-command",
                    "DetailType": "core.update-account-command",
                    "Detail": json.dumps({"EventType": "1"}),
                    "EventBusName": bus_name,
                }
            ]
        )

        def _receive_messages():
            response = aws_client.sqs.receive_message(QueueUrl=queue_url)
            assert "Messages" in response

            messages = response["Messages"]
            assert len(messages) == 1

            message_body = messages[0]["Body"]
            assert '"1"' in message_body

        with pytest.raises(AssertionError):
            retry(_receive_messages, sleep=2, retries=10)

        policy = {
            "Version": "2012-10-17",
            "Id": f"sqs-eventbridge-{short_uid()}",
            "Statement": [
                {
                    "Sid": f"sqs-eventbridge-{short_uid()}",
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": "sqs:*",
                    "Resource": queue_arn,
                }
            ],
        }

        aws_client.sqs.set_queue_attributes(
            QueueUrl=queue_url, Attributes={"Policy": json.dumps(policy)}
        )

        if is_aws_cloud():
            time.sleep(15)

        aws_client.events.put_events(
            Entries=[
                {
                    "Source": "core.update-account-command",
                    "DetailType": "core.update-account-command",
                    "Detail": json.dumps({"EventType": "1"}),
                    "EventBusName": bus_name,
                }
            ]
        )

        retry(_receive_messages, sleep=2, retries=10, sleep_before=10)

    @markers.aws.validated
    def test_events_lambda(
        self,
        aws_client,
        create_lambda_function,
        cleanups,
        create_policy,
        create_role,
    ):
        logs_role_name = f"test-role-{short_uid()}"
        logs_role_arn = create_role(
            RoleName=logs_role_name, AssumeRolePolicyDocument=LAMBDA_TRUST_POLICY
        )["Role"]["Arn"]
        logs_policy_name = f"test-policy-{short_uid()}"
        logs_policy_arn = create_policy(
            PolicyName=logs_policy_name, PolicyDocument=LAMBDA_MINIMUM_PERMISSION
        )["Policy"]["Arn"]
        aws_client.iam.attach_role_policy(RoleName=logs_role_name, PolicyArn=logs_policy_arn)

        function_name = f"test-function-{short_uid()}"
        function = create_lambda_function(
            func_name=function_name,
            handler_file=TEST_LAMBDA_ECHO,
            runtime=Runtime.python3_12,
            role=logs_role_arn,
        )

        bus_name = f"test-bus-{short_uid()}"
        aws_client.events.create_event_bus(Name=bus_name)
        cleanups.append(lambda: aws_client.events.delete_event_bus(Name=bus_name))

        rule_name = f"test-rule-{short_uid()}"
        response = aws_client.events.put_rule(
            Name=rule_name,
            State="ENABLED",
            EventBusName=bus_name,
            EventPattern=json.dumps({"detail": {"EventType": ["0", "1"]}}),
        )
        cleanups.append(
            lambda: aws_client.events.delete_rule(Name=rule_name, EventBusName=bus_name)
        )

        aws_client.events.put_targets(
            Rule=rule_name,
            EventBusName=bus_name,
            Targets=[
                {
                    "Id": "1",
                    "Arn": function["CreateFunctionResponse"]["FunctionArn"],
                    "InputPath": "$.detail.EventType",
                }
            ],
        )
        cleanups.append(
            lambda: aws_client.events.remove_targets(
                Rule=rule_name, Ids=["1"], EventBusName=bus_name
            )
        )

        def _assert_events():
            aws_client.logs.filter_log_events(
                logGroupName=f"/aws/lambda/{function_name}",
            )["events"]

        aws_client.events.put_events(
            Entries=[
                {
                    "Source": "test",
                    "DetailType": "0",
                    "Detail": json.dumps({"EventType": "0"}),
                    "EventBusName": bus_name,
                }
            ]
        )

        with pytest.raises(ClientError):
            retry(_assert_events, retries=20, sleep=2)

        aws_client.lambda_.add_permission(
            FunctionName=function_name,
            StatementId="1",
            Action="lambda:InvokeFunction",
            Principal="events.amazonaws.com",
            SourceArn=response["RuleArn"],
        )

        aws_client.events.put_events(
            Entries=[
                {
                    "Source": "test",
                    "DetailType": "0",
                    "Detail": json.dumps({"EventType": "0"}),
                    "EventBusName": bus_name,
                }
            ]
        )

        retry(_assert_events, retries=20, sleep=2)

    @markers.aws.validated
    def test_events_sns(self, aws_client, sns_create_topic, sqs_create_queue, cleanups):
        bus_name = f"test-bus-{short_uid()}"
        topic_arn = sns_create_topic()["TopicArn"]
        queue_url = sqs_create_queue(QueueName=f"test-{short_uid()}")
        queue_arn = aws_client.sqs.get_queue_attributes(
            QueueUrl=queue_url, AttributeNames=["QueueArn"]
        )["Attributes"]["QueueArn"]
        # get topic arn
        topic_arn = aws_client.sns.get_topic_attributes(TopicArn=topic_arn)["Attributes"][
            "TopicArn"
        ]

        aws_client.sns.subscribe(
            TopicArn=topic_arn,
            Protocol="sqs",
            Endpoint=queue_arn,
            ReturnSubscriptionArn=True,
        )

        policy = {
            "Version": "2012-10-17",
            "Id": f"sqs-eventbridge-{short_uid()}",
            "Statement": [
                {
                    "Sid": f"sqs-eventbridge-{short_uid()}",
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": "sqs:*",
                    "Resource": queue_arn,
                }
            ],
        }

        aws_client.sqs.set_queue_attributes(
            QueueUrl=queue_url, Attributes={"Policy": json.dumps(policy)}
        )
        if is_aws_cloud():
            time.sleep(10)

        aws_client.events.create_event_bus(Name=bus_name)
        cleanups.append(lambda: aws_client.events.delete_event_bus(Name=bus_name))

        rule_name = f"test-rule-{short_uid()}"
        aws_client.events.put_rule(
            Name=rule_name,
            EventPattern=json.dumps({"detail": {"EventType": ["0", "1"]}}),
            EventBusName=bus_name,
            State="ENABLED",
        )
        cleanups.append(
            lambda: aws_client.events.delete_rule(Name=rule_name, Force=True, EventBusName=bus_name)
        )
        aws_client.events.put_targets(
            Rule=rule_name,
            EventBusName=bus_name,
            Targets=[
                {
                    "Id": "1",
                    "Arn": topic_arn,
                    "InputPath": "$.detail.EventType",
                }
            ],
        )
        cleanups.append(
            lambda: aws_client.events.remove_targets(
                Rule=rule_name, Force=True, Ids=["1"], EventBusName=bus_name
            )
        )

        def _receive_messages():
            aws_client.events.put_events(
                Entries=[
                    {
                        "Source": "core.update-account-command",
                        "DetailType": "core.update-account-command",
                        "Detail": json.dumps({"EventType": "1"}),
                        "EventBusName": bus_name,
                    }
                ]
            )

            messages = aws_client.sqs.receive_message(QueueUrl=queue_url, WaitTimeSeconds=2).get(
                "Messages", []
            )
            assert len(messages) > 0

        with pytest.raises(AssertionError):
            retry(_receive_messages, sleep=2, retries=10)

        rule_arn = aws_client.events.describe_rule(Name=rule_name, EventBusName=bus_name)["Arn"]
        aws_client.sns.set_topic_attributes(
            TopicArn=topic_arn,
            AttributeName="Policy",
            AttributeValue=json.dumps(
                {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Sid": "AllowSNS",
                            "Effect": "Allow",
                            "Principal": {"Service": "events.amazonaws.com"},
                            "Action": "sns:Publish",
                            "Resource": topic_arn,
                            "Condition": {
                                "ArnEquals": {"aws:SourceArn": rule_arn},
                            },
                        }
                    ],
                }
            ),
        )

        retry(_receive_messages, sleep=2, retries=10, sleep_before=(10 if is_aws_cloud() else 0))

    @markers.aws.validated
    def test_events_firehose(
        self,
        aws_client,
        s3_create_bucket,
        firehose_create_delivery_stream,
        cleanups,
        create_role,
        partition,
    ):
        """
        Validates the enforcement of IAM policies on a EventsBridge-Firehose integration using an S3 to check that the event is being sent to Firehose.
        """
        stream_name = f"test-stream-{short_uid()}"
        bucket_name = f"test-bucket-{short_uid()}"

        assume_role = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"Service": "firehose.amazonaws.com"},
                    "Action": "sts:AssumeRole",
                }
            ],
        }

        data_role_name = f"test-role-{short_uid()}"
        data_role = create_role(
            RoleName=data_role_name, AssumeRolePolicyDocument=json.dumps(assume_role)
        )

        aws_client.iam.put_role_policy(
            RoleName=data_role_name,
            PolicyName="firehose-s3",
            PolicyDocument=json.dumps(
                {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Action": [
                                "s3:PutObject",
                            ],
                            "Resource": f"arn:{partition}:s3:::{bucket_name}/*",
                        }
                    ],
                }
            ),
        )

        if is_aws_cloud():
            time.sleep(15)

        s3_create_bucket(Bucket=bucket_name)

        stream = firehose_create_delivery_stream(
            DeliveryStreamName=stream_name,
            DeliveryStreamType="DirectPut",
            S3DestinationConfiguration={
                "RoleARN": data_role["Role"]["Arn"],
                "BucketARN": f"arn:{partition}:s3:::{bucket_name}",
                "BufferingHints": {"SizeInMBs": 1, "IntervalInSeconds": 60},
            },
        )

        def _validate_content():
            assert "Contents" in aws_client.s3.list_objects(Bucket=bucket_name)

        bus_name = f"test-bus-{short_uid()}"
        aws_client.events.create_event_bus(Name=bus_name)
        cleanups.append(lambda: aws_client.events.delete_event_bus(Name=bus_name))

        rule_name = f"test-rule-{short_uid()}"
        aws_client.events.put_rule(
            Name=rule_name,
            State="ENABLED",
            EventBusName=bus_name,
            EventPattern=json.dumps({"detail": {"EventType": ["0", "1"]}}),
        )
        cleanups.append(
            lambda: aws_client.events.delete_rule(Name=rule_name, EventBusName=bus_name)
        )

        assume_role["Statement"][0]["Principal"]["Service"] = "events.amazonaws.com"
        events_role_name = f"test-role-{short_uid()}"
        events_role = create_role(
            RoleName=events_role_name, AssumeRolePolicyDocument=json.dumps(assume_role)
        )

        if is_aws_cloud():
            time.sleep(15)

        aws_client.events.put_targets(
            Rule=rule_name,
            EventBusName=bus_name,
            Targets=[
                {
                    "Id": "1",
                    "Arn": stream["DeliveryStreamARN"],
                    "RoleArn": events_role["Role"]["Arn"],
                }
            ],
        )
        cleanups.append(
            lambda: aws_client.events.remove_targets(
                Rule=rule_name, Ids=["1"], EventBusName=bus_name
            )
        )

        aws_client.events.put_events(
            Entries=[
                {
                    "Source": "test",
                    "DetailType": "0",
                    "Detail": json.dumps({"EventType": "0"}),
                    "EventBusName": bus_name,
                }
            ]
        )

        retries = 5
        sleep = 1
        if is_aws_cloud():
            retries = 30
            sleep = 20

        with pytest.raises(AssertionError):
            retry(_validate_content, retries=retries, sleep=sleep)

        aws_client.iam.put_role_policy(
            RoleName=events_role_name,
            PolicyName="events-firehose",
            PolicyDocument=json.dumps(
                {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Action": [
                                "firehose:PutRecord",
                            ],
                            "Resource": stream["DeliveryStreamARN"],
                        }
                    ],
                }
            ),
        )

        if is_aws_cloud():
            time.sleep(15)

        aws_client.events.put_events(
            Entries=[
                {
                    "Source": "test",
                    "DetailType": "0",
                    "Detail": json.dumps({"EventType": "0"}),
                    "EventBusName": bus_name,
                }
            ]
        )

        retry(_validate_content, retries=retries, sleep=sleep)

    @markers.aws.validated
    def test_events_kinesis(
        self, aws_client, cleanups, kinesis_create_stream, wait_for_stream_ready, create_role
    ):
        stream_name = kinesis_create_stream(ShardCount=1)
        stream = aws_client.kinesis.describe_stream(StreamName=stream_name)

        bus_name = f"test-bus-{short_uid()}"
        aws_client.events.create_event_bus(Name=bus_name)
        cleanups.append(lambda: aws_client.events.delete_event_bus(Name=bus_name))

        rule_name = f"test-rule-{short_uid()}"
        aws_client.events.put_rule(
            Name=rule_name,
            State="ENABLED",
            EventBusName=bus_name,
            EventPattern=json.dumps({"detail": {"EventType": ["0", "1"]}}),
        )
        cleanups.append(
            lambda: aws_client.events.delete_rule(Name=rule_name, EventBusName=bus_name)
        )
        events_role_name = f"test-role-{short_uid()}"
        events_role = create_role(
            RoleName=events_role_name,
            AssumeRolePolicyDocument=json.dumps(
                {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Principal": {"Service": "events.amazonaws.com"},
                            "Action": "sts:AssumeRole",
                        }
                    ],
                }
            ),
        )

        if is_aws_cloud():
            time.sleep(15)

        wait_for_stream_ready(stream_name)

        aws_client.events.put_targets(
            Rule=rule_name,
            EventBusName=bus_name,
            Targets=[
                {
                    "Id": "1",
                    "Arn": stream["StreamDescription"]["StreamARN"],
                    "RoleArn": events_role["Role"]["Arn"],
                }
            ],
        )
        cleanups.append(
            lambda: aws_client.events.remove_targets(
                Rule=rule_name, Ids=["1"], EventBusName=bus_name
            )
        )

        aws_client.events.put_events(
            Entries=[
                {
                    "Source": "test",
                    "DetailType": "0",
                    "Detail": json.dumps({"EventType": "0"}),
                    "EventBusName": bus_name,
                }
            ]
        )

        stream_description = aws_client.kinesis.describe_stream(StreamName=stream_name)
        shard_id = stream_description["StreamDescription"]["Shards"][0]["ShardId"]
        latest_shard_iterator = aws_client.kinesis.get_shard_iterator(
            StreamName=stream_name, ShardId=shard_id, ShardIteratorType="LATEST"
        )["ShardIterator"]

        def _assert_events():
            nonlocal latest_shard_iterator
            aws_client.events.put_events(
                Entries=[
                    {
                        "Source": "test",
                        "DetailType": "0",
                        "Detail": json.dumps({"EventType": "0"}),
                        "EventBusName": bus_name,
                    }
                ]
            )

            # get records using the latest shard iterator
            get_records_result = aws_client.kinesis.get_records(
                ShardIterator=latest_shard_iterator, Limit=100
            )
            latest_shard_iterator = get_records_result["NextShardIterator"]
            records = get_records_result["Records"]
            assert len(records) > 0

        retries = 30 if is_aws_cloud() else 10

        with pytest.raises(AssertionError):
            retry(_assert_events, retries=retries, sleep=2)

        aws_client.iam.put_role_policy(
            RoleName=events_role_name,
            PolicyName="test-policy",
            PolicyDocument=json.dumps(
                {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Action": [
                                "kinesis:PutRecord",
                            ],
                            "Resource": stream["StreamDescription"]["StreamARN"],
                        }
                    ],
                }
            ),
        )

        retry(_assert_events, retries=retries, sleep=2, sleep_before=(15 if is_aws_cloud() else 0))

    @markers.aws.validated
    def test_events_logs(self, aws_client, cleanups):
        log_group_name = f"test-log-group-{short_uid()}"
        bus_name = f"test-bus-{short_uid()}"
        rule_name = f"test-rule-{short_uid()}"

        aws_client.logs.create_log_group(logGroupName=log_group_name)
        cleanups.append(lambda: aws_client.logs.delete_log_group(logGroupName=log_group_name))

        aws_client.events.create_event_bus(Name=bus_name)
        cleanups.append(lambda: aws_client.events.delete_event_bus(Name=bus_name))

        aws_client.events.put_rule(
            Name=rule_name,
            EventPattern=json.dumps({"detail": {"EventType": ["0", "1"]}}),
            State="ENABLED",
            EventBusName=bus_name,
        )
        cleanups.append(
            lambda: aws_client.events.delete_rule(Name=rule_name, Force=True, EventBusName=bus_name)
        )

        log_group_arn = aws_client.logs.describe_log_groups(logGroupNamePrefix=log_group_name)[
            "logGroups"
        ][0]["arn"]
        aws_client.events.put_targets(
            Rule=rule_name,
            EventBusName=bus_name,
            Targets=[
                {
                    "Id": "1",
                    "Arn": log_group_arn,
                }
            ],
        )

        cleanups.append(
            lambda: aws_client.events.remove_targets(
                Rule=rule_name, Force=True, Ids=["1"], EventBusName=bus_name
            )
        )

        def _receive_messages():
            aws_client.events.put_events(
                Entries=[
                    {
                        "Source": "core.update-account-command",
                        "DetailType": "core.update-account-command",
                        "Detail": json.dumps({"EventType": "1"}),
                        "EventBusName": bus_name,
                    }
                ]
            )
            response = aws_client.logs.describe_log_streams(logGroupName=log_group_name)
            assert len(response["logStreams"]) > 0

        with pytest.raises(AssertionError):
            retry(_receive_messages, sleep=2, retries=10)

        policy_name = f"test-policy-{short_uid()}"
        aws_client.logs.put_resource_policy(
            policyName=policy_name,
            policyDocument=json.dumps(
                {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Sid": "AllowPutEvents",
                            "Effect": "Allow",
                            "Principal": {"Service": "events.amazonaws.com"},
                            "Action": ["logs:PutLogEvents", "logs:CreateLogStream"],
                            "Resource": log_group_arn,
                        }
                    ],
                }
            ),
        )

        retry(_receive_messages, sleep=2, retries=10, sleep_before=10)

    @markers.aws.validated
    def test_events_events(self, aws_client, sqs_create_queue, cleanups, create_role):
        queue_url = sqs_create_queue()
        bus_name = f"test-bus-{short_uid()}"
        rule_name = f"test-rule-{short_uid()}"

        aws_client.events.create_event_bus(Name=bus_name)
        cleanups.append(lambda: aws_client.events.delete_event_bus(Name=bus_name))

        aws_client.events.put_rule(
            Name=rule_name,
            EventPattern=json.dumps({"detail": {"EventType": ["0", "1"]}}),
            EventBusName=bus_name,
            State="ENABLED",
        )
        cleanups.append(
            lambda: aws_client.events.delete_rule(Name=rule_name, Force=True, EventBusName=bus_name)
        )

        queue_arn = aws_client.sqs.get_queue_attributes(
            QueueUrl=queue_url, AttributeNames=["QueueArn"]
        )["Attributes"]["QueueArn"]

        aws_client.events.put_targets(
            Rule=rule_name,
            EventBusName=bus_name,
            Targets=[
                {
                    "Id": "1",
                    "Arn": queue_arn,
                    "InputPath": "$.detail.EventType",
                }
            ],
        )
        cleanups.append(
            lambda: aws_client.events.remove_targets(
                Rule=rule_name, Force=True, Ids=["1"], EventBusName=bus_name
            )
        )

        policy = {
            "Version": "2012-10-17",
            "Id": f"sqs-eventbridge-{short_uid()}",
            "Statement": [
                {
                    "Sid": f"sqs-eventbridge-{short_uid()}",
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": "sqs:*",
                    "Resource": queue_arn,
                }
            ],
        }

        aws_client.sqs.set_queue_attributes(
            QueueUrl=queue_url, Attributes={"Policy": json.dumps(policy)}
        )

        second_bus_name = f"test-bus-{short_uid()}"
        second_rule_name = f"test-rule-{short_uid()}"

        aws_client.events.create_event_bus(Name=second_bus_name)
        cleanups.append(lambda: aws_client.events.delete_event_bus(Name=second_bus_name))

        aws_client.events.put_rule(
            Name=second_rule_name,
            EventPattern=json.dumps({"detail": {"EventType": ["0", "1"]}}),
            EventBusName=second_bus_name,
            State="ENABLED",
        )
        cleanups.append(
            lambda: aws_client.events.delete_rule(
                Name=rule_name, Force=True, EventBusName=second_bus_name
            )
        )

        bus_arn = aws_client.events.describe_event_bus(Name=bus_name)["Arn"]

        events_role_name = f"test-role-{short_uid()}"
        events_role = create_role(
            RoleName=events_role_name,
            AssumeRolePolicyDocument=json.dumps(
                {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Principal": {"Service": "events.amazonaws.com"},
                            "Action": "sts:AssumeRole",
                        }
                    ],
                }
            ),
        )

        if is_aws_cloud():
            time.sleep(15)

        aws_client.events.put_targets(
            Rule=second_rule_name,
            EventBusName=second_bus_name,
            Targets=[
                {
                    "Id": "1",
                    "Arn": bus_arn,
                    "RoleArn": events_role["Role"]["Arn"],
                }
            ],
        )

        def _receive_messages():
            aws_client.events.put_events(
                Entries=[
                    {
                        "Source": "test",
                        "DetailType": "0",
                        "Detail": json.dumps({"EventType": "1"}),
                        "EventBusName": second_bus_name,
                    }
                ],
            )

            response = aws_client.sqs.receive_message(QueueUrl=queue_url)
            assert "Messages" in response

            messages = response["Messages"]
            assert len(messages) == 1

            message_body = messages[0]["Body"]
            assert '"1"' in message_body

        with pytest.raises(AssertionError):
            retry(_receive_messages, sleep=2, retries=10)

        bus_arn = aws_client.events.describe_event_bus(Name=bus_name)["Arn"]
        aws_client.iam.put_role_policy(
            RoleName=events_role_name,
            PolicyName="events-events",
            PolicyDocument=json.dumps(
                {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Action": [
                                "events:PutEvents",
                            ],
                            "Resource": bus_arn,
                        }
                    ],
                }
            ),
        )

        retry(_receive_messages, sleep=2, retries=10, sleep_before=(20 if is_aws_cloud() else 0))


@markers.snapshot.skip_snapshot_verify(
    paths=[
        "$..Error.ArgumentName",
        "$..Error.ArgumentName1",
        "$..Error.ArgumentValue",
        "$..Error.ArgumentValue1",
    ]
)
class TestS3BucketNotifications:
    @pytest.fixture(autouse=True)
    def add_transformers(self, snapshot):
        snapshot.add_transformer(snapshot.transform.key_value("Bucket"))
        snapshot.add_transformer(snapshot.transform.key_value("MD5OfBody"))
        snapshot.add_transformer(snapshot.transform.key_value("RequestId"))
        snapshot.add_transformer(snapshot.transform.key_value("HostId"))
        snapshot.add_transformer(snapshot.transform.key_value("eTag"))
        snapshot.add_transformer(snapshot.transform.key_value("Signature"))
        snapshot.add_transformer(snapshot.transform.key_value("SigningCertURL"))
        snapshot.add_transformer(snapshot.transform.key_value("UnsubscribeURL"))
        snapshot.add_transformer(snapshot.transform.key_value("CodeSha256"))
        snapshot.add_transformer(snapshot.transform.s3_api())
        snapshot.add_transformer(snapshot.transform.sqs_api())
        snapshot.add_transformer(snapshot.transform.lambda_api())

    @markers.aws.validated
    def test_s3_bucket_notification_sqs(
        self, aws_client, s3_bucket, sqs_queue, sqs_get_queue_arn, snapshot, region_name
    ):
        """Test enforcement of s3 bucket notifications"""
        queue_arn = sqs_get_queue_arn(sqs_queue)
        bucket_arn = s3_bucket_arn(s3_bucket, region=region_name)

        with pytest.raises(ClientError) as e:
            aws_client.s3.put_bucket_notification_configuration(
                Bucket=s3_bucket,
                NotificationConfiguration={
                    "QueueConfigurations": [
                        {
                            "Events": [
                                "s3:ObjectCreated:*",
                            ],
                            "QueueArn": queue_arn,
                        },
                    ],
                },
            )
        snapshot.match("invalid-permission", e.value.response)

        policy = {
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"Service": "s3.amazonaws.com"},
                    "Action": "sqs:SendMessage",
                    "Resource": queue_arn,
                    "Condition": {"ArnEquals": {"aws:SourceArn": bucket_arn}},
                }
            ]
        }

        aws_client.sqs.set_queue_attributes(
            QueueUrl=sqs_queue, Attributes={"Policy": json.dumps(policy)}
        )

        aws_client.s3.put_bucket_notification_configuration(
            Bucket=s3_bucket,
            NotificationConfiguration={
                "QueueConfigurations": [
                    {
                        "Events": [
                            "s3:ObjectCreated:*",
                        ],
                        "QueueArn": queue_arn,
                    },
                ],
            },
        )

        def check_for_messages():
            messages = aws_client.sqs.receive_message(QueueUrl=sqs_queue)
            assert len(messages["Messages"]) == 1
            return messages["Messages"]

        initial_messages = retry(check_for_messages, retries=10, sleep=1)

        snapshot.match("initial-messages", initial_messages)
        aws_client.sqs.delete_message(
            QueueUrl=sqs_queue, ReceiptHandle=initial_messages[0]["ReceiptHandle"]
        )

        aws_client.s3.put_object(Bucket=s3_bucket, Key="some-key", Body=b"content")

        notification_messages = retry(check_for_messages, retries=10, sleep=1)
        snapshot.match("notification-messages", notification_messages)
        aws_client.sqs.delete_message(
            QueueUrl=sqs_queue, ReceiptHandle=notification_messages[0]["ReceiptHandle"]
        )

    @markers.snapshot.skip_snapshot_verify(paths=["$..Signature"])
    @markers.aws.validated
    def test_s3_bucket_notification_sns(
        self, aws_client, s3_bucket, sns_topic, sqs_queue, sqs_get_queue_arn, snapshot, region_name
    ):
        """Test enforcement of s3 bucket notifications"""
        queue_arn = sqs_get_queue_arn(sqs_queue)
        bucket_arn = s3_bucket_arn(s3_bucket, region=region_name)
        topic_arn = sns_topic["Attributes"]["TopicArn"]

        # connect topic to sqs queue
        policy = {
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"Service": "sns.amazonaws.com"},
                    "Action": "sqs:SendMessage",
                    "Resource": queue_arn,
                    "Condition": {"ArnEquals": {"aws:SourceArn": topic_arn}},
                }
            ]
        }

        aws_client.sqs.set_queue_attributes(
            QueueUrl=sqs_queue, Attributes={"Policy": json.dumps(policy)}
        )
        aws_client.sns.subscribe(TopicArn=topic_arn, Protocol="sqs", Endpoint=queue_arn)

        with pytest.raises(ClientError) as e:
            aws_client.s3.put_bucket_notification_configuration(
                Bucket=s3_bucket,
                NotificationConfiguration={
                    "TopicConfigurations": [
                        {
                            "Events": [
                                "s3:ObjectCreated:*",
                            ],
                            "TopicArn": topic_arn,
                        },
                    ],
                },
            )
        snapshot.match("invalid-permission", e.value.response)

        policy = {
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"Service": "s3.amazonaws.com"},
                    "Action": "sns:Publish",
                    "Resource": topic_arn,
                    "Condition": {"ArnEquals": {"aws:SourceArn": bucket_arn}},
                }
            ]
        }

        aws_client.sns.set_topic_attributes(
            TopicArn=topic_arn, AttributeName="Policy", AttributeValue=json.dumps(policy)
        )

        aws_client.s3.put_bucket_notification_configuration(
            Bucket=s3_bucket,
            NotificationConfiguration={
                "TopicConfigurations": [
                    {
                        "Events": [
                            "s3:ObjectCreated:*",
                        ],
                        "TopicArn": topic_arn,
                    },
                ],
            },
        )

        def check_for_messages():
            messages = aws_client.sqs.receive_message(QueueUrl=sqs_queue)
            assert len(messages["Messages"]) == 1
            return messages["Messages"]

        initial_messages = retry(check_for_messages, retries=10, sleep=1)
        messages = [json.loads(message.get("Body")) for message in initial_messages]
        snapshot.match("initial-messages", messages)
        aws_client.sqs.delete_message(
            QueueUrl=sqs_queue, ReceiptHandle=initial_messages[0]["ReceiptHandle"]
        )

        aws_client.s3.put_object(Bucket=s3_bucket, Key="some-key", Body=b"content")

        notification_messages = retry(check_for_messages, retries=10, sleep=1)
        messages = [json.loads(message.get("Body")) for message in notification_messages]
        snapshot.match("notification-messages", messages)
        aws_client.sqs.delete_message(
            QueueUrl=sqs_queue, ReceiptHandle=notification_messages[0]["ReceiptHandle"]
        )

    @markers.aws.validated
    def test_s3_bucket_notification_lambda(
        self, aws_client, s3_bucket, create_lambda_function, snapshot, region_name
    ):
        """Test enforcement of s3 bucket notifications"""
        function_name = f"test-function-{short_uid()}"
        create_function_result = create_lambda_function(
            handler_file=TEST_LAMBDA_ECHO,
            func_name=function_name,
            runtime=Runtime.python3_12,
        )["CreateFunctionResponse"]
        snapshot.match("create-function-result", create_function_result)
        function_arn = create_function_result["FunctionArn"]
        bucket_arn = s3_bucket_arn(s3_bucket, region=region_name)

        notification_config = {
            "LambdaFunctionConfigurations": [
                {
                    "Events": [
                        "s3:ObjectCreated:*",
                    ],
                    "LambdaFunctionArn": function_arn,
                }
            ]
        }

        with pytest.raises(ClientError) as e:
            aws_client.s3.put_bucket_notification_configuration(
                Bucket=s3_bucket,
                NotificationConfiguration=notification_config,
            )
        snapshot.match("invalid-permission", e.value.response)

        aws_client.lambda_.add_permission(
            FunctionName=function_name,
            StatementId="s1",
            Action="lambda:InvokeFunction",
            Principal="s3.amazonaws.com",
            SourceArn=bucket_arn,
        )

        aws_client.s3.put_bucket_notification_configuration(
            Bucket=s3_bucket, NotificationConfiguration=notification_config
        )

        def check_logs():
            logs = aws_client.logs.filter_log_events(logGroupName=f"/aws/lambda/{function_name}")
            assert len(logs["events"]) > 1
            return logs["events"]

        with pytest.raises(ClientError):
            retry(check_logs, retries=5, sleep=4 if is_aws_cloud() else 1)

        aws_client.s3.put_object(Bucket=s3_bucket, Key="some-key", Body=b"content")

        logs = retry(check_logs, retries=5, sleep=4 if is_aws_cloud() else 1)
        message = next(event["message"] for event in logs if event["message"].startswith("{"))
        snapshot.match("notification-messages", json.loads(message))


class TestLambdaEventSourceMappings:
    @markers.aws.validated
    def test_dynamodb_event_source_mapping(
        self,
        create_lambda_function,
        dynamodb_create_table,
        cleanups,
        wait_for_dynamodb_stream_ready,
        create_role,
        create_policy,
        aws_client,
    ):
        function_name = f"lambda_func-{short_uid()}"
        table_name = f"test-table-{short_uid()}"
        partition_key = "my_partition_key"
        db_item = {partition_key: {"S": "hello world"}, "binary_key": {"B": b"foobar"}}

        role_name = f"test-lambda-role-{short_uid()}"
        log_policy_name = f"test-policy-{short_uid()}"
        dynamodb_policy_name = f"test-policy-{short_uid()}"
        role_arn = create_role(RoleName=role_name, AssumeRolePolicyDocument=LAMBDA_TRUST_POLICY)[
            "Role"
        ]["Arn"]

        dynamodb_create_table(table_name=table_name, partition_key=partition_key)

        _await_dynamodb_table_active(aws_client.dynamodb, table_name)
        stream_arn = aws_client.dynamodb.update_table(
            TableName=table_name,
            StreamSpecification={"StreamEnabled": True, "StreamViewType": "NEW_IMAGE"},
        )["TableDescription"]["LatestStreamArn"]
        assert wait_for_dynamodb_stream_ready(stream_arn)

        dynamodb_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "dynamodb:DescribeStream",
                        "dynamodb:GetRecords",
                        "dynamodb:GetShardIterator",
                    ],
                    "Resource": stream_arn,
                },
                {
                    "Effect": "Allow",
                    "Action": [
                        "dynamodb:ListStreams",
                    ],
                    "Resource": "*",
                },
            ],
        }
        log_policy_arn = create_policy(
            PolicyName=log_policy_name, PolicyDocument=LAMBDA_MINIMUM_PERMISSION
        )["Policy"]["Arn"]
        aws_client.iam.attach_role_policy(RoleName=role_name, PolicyArn=log_policy_arn)
        dynamodb_policy_arn = create_policy(
            PolicyName=dynamodb_policy_name, PolicyDocument=json.dumps(dynamodb_policy)
        )["Policy"]["Arn"]
        aws_client.iam.attach_role_policy(RoleName=role_name, PolicyArn=dynamodb_policy_arn)

        create_lambda_function(
            handler_file=TEST_LAMBDA_ECHO,
            func_name=function_name,
            runtime=Runtime.python3_12,
            role=role_arn,
        )
        # needed to wait for permissions to be ready for event source mapping
        time.sleep(30 if is_aws_cloud() else 5)
        create_event_source_mapping_response = aws_client.lambda_.create_event_source_mapping(
            FunctionName=function_name,
            BatchSize=1,
            StartingPosition="TRIM_HORIZON",
            EventSourceArn=stream_arn,
            MaximumBatchingWindowInSeconds=1,
            MaximumRetryAttempts=1,
        )
        event_source_uuid = create_event_source_mapping_response["UUID"]
        cleanups.append(
            lambda: aws_client.lambda_.delete_event_source_mapping(UUID=event_source_uuid)
        )

        _await_event_source_mapping_enabled(aws_client.lambda_, event_source_uuid)
        time.sleep(30 if is_aws_cloud() else 5)

        aws_client.dynamodb.put_item(TableName=table_name, Item=db_item)

        def _assert_events(expected_events: int):
            log_events = aws_client.logs.filter_log_events(
                logGroupName=f"/aws/lambda/{function_name}",
            )["events"]
            assert (
                len([e["message"] for e in log_events if e["message"].startswith("REPORT")])
                == expected_events
            )

        retry(_assert_events, expected_events=1, retries=30, sleep=2)

        aws_client.iam.detach_role_policy(RoleName=role_name, PolicyArn=dynamodb_policy_arn)
        # give time for permission changes
        time.sleep(30 if is_aws_cloud() else 5)
        aws_client.dynamodb.put_item(TableName=table_name, Item=db_item)

        with pytest.raises(Exception):
            retry(_assert_events, expected_events=2, retries=20, sleep=1)

    @markers.aws.validated
    def test_kinesis_event_source_mapping(
        self,
        create_lambda_function,
        kinesis_create_stream,
        wait_for_stream_ready,
        cleanups,
        create_role,
        create_policy,
        aws_client,
    ):
        function_name = f"lambda_func-{short_uid()}"
        stream_name = f"test-stream-{short_uid()}"

        role_name = f"test-lambda-role-{short_uid()}"
        log_policy_name = f"test-policy-{short_uid()}"
        kinesis_policy_name = f"test-policy-{short_uid()}"
        role_arn = create_role(RoleName=role_name, AssumeRolePolicyDocument=LAMBDA_TRUST_POLICY)[
            "Role"
        ]["Arn"]

        kinesis_create_stream(StreamName=stream_name, ShardCount=1)

        stream_arn = aws_client.kinesis.describe_stream(StreamName=stream_name)[
            "StreamDescription"
        ]["StreamARN"]

        assert wait_for_stream_ready(stream_name)

        kinesis_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "kinesis:DescribeStream",
                        "kinesis:GetRecords",
                        "kinesis:GetShardIterator",
                    ],
                    "Resource": "*",
                    # TODO support rendering for stream ARNs from shard iterator
                    # "Resource": stream_arn,
                },
                {
                    "Effect": "Allow",
                    "Action": [
                        "kinesis:ListStreams",
                    ],
                    "Resource": "*",
                },
            ],
        }
        log_policy_arn = create_policy(
            PolicyName=log_policy_name, PolicyDocument=LAMBDA_MINIMUM_PERMISSION
        )["Policy"]["Arn"]
        aws_client.iam.attach_role_policy(RoleName=role_name, PolicyArn=log_policy_arn)
        kinesis_policy_arn = create_policy(
            PolicyName=kinesis_policy_name, PolicyDocument=json.dumps(kinesis_policy)
        )["Policy"]["Arn"]
        aws_client.iam.attach_role_policy(RoleName=role_name, PolicyArn=kinesis_policy_arn)

        create_lambda_function(
            handler_file=TEST_LAMBDA_ECHO,
            func_name=function_name,
            runtime=Runtime.python3_12,
            role=role_arn,
        )
        # needed to wait for permissions to be ready for event source mapping
        time.sleep(30 if is_aws_cloud() else 5)
        create_event_source_mapping_response = aws_client.lambda_.create_event_source_mapping(
            FunctionName=function_name,
            BatchSize=1,
            StartingPosition="TRIM_HORIZON",
            EventSourceArn=stream_arn,
            MaximumBatchingWindowInSeconds=1,
            MaximumRetryAttempts=1,
        )
        event_source_uuid = create_event_source_mapping_response["UUID"]
        cleanups.append(
            lambda: aws_client.lambda_.delete_event_source_mapping(UUID=event_source_uuid)
        )

        _await_event_source_mapping_enabled(aws_client.lambda_, event_source_uuid)
        time.sleep(30 if is_aws_cloud() else 5)

        aws_client.kinesis.put_record(
            Data=json.dumps({"test": "data"}), StreamARN=stream_arn, PartitionKey="1"
        )

        def _assert_events(expected_events: int):
            log_events = aws_client.logs.filter_log_events(
                logGroupName=f"/aws/lambda/{function_name}",
            )["events"]
            assert (
                len([e["message"] for e in log_events if e["message"].startswith("REPORT")])
                == expected_events
            )

        retry(_assert_events, expected_events=1, retries=30, sleep=2)

        aws_client.iam.detach_role_policy(RoleName=role_name, PolicyArn=kinesis_policy_arn)
        # give time for permission changes
        time.sleep(300 if is_aws_cloud() else 5)
        aws_client.kinesis.put_record(
            Data=json.dumps({"test": "data2"}), StreamARN=stream_arn, PartitionKey="1"
        )

        with pytest.raises(Exception):
            retry(_assert_events, expected_events=2, retries=20, sleep=1)

    @markers.aws.validated
    def test_sqs_event_source_mapping(
        self,
        aws_client,
        create_lambda_function,
        sqs_create_queue,
        sqs_get_queue_arn,
        create_role,
        create_policy,
        cleanups,
    ):
        function_name = f"lambda_func-{short_uid()}"
        queue_name = f"queue-{short_uid()}-1"

        queue_url = sqs_create_queue(QueueName=queue_name)
        queue_arn = sqs_get_queue_arn(queue_url)

        role_name = f"test-role-{short_uid()}"
        log_policy_name = f"test-policy-{short_uid()}"
        sqs_policy_name = f"test-policy-{short_uid()}"
        role_arn = create_role(RoleName=role_name, AssumeRolePolicyDocument=LAMBDA_TRUST_POLICY)[
            "Role"
        ]["Arn"]
        sqs_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "sqs:ReceiveMessage",
                        "sqs:DeleteMessage",
                        "sqs:GetQueueAttributes",
                    ],
                    "Resource": queue_arn,
                }
            ],
        }
        log_policy_arn = create_policy(
            PolicyName=log_policy_name, PolicyDocument=LAMBDA_MINIMUM_PERMISSION
        )["Policy"]["Arn"]
        aws_client.iam.attach_role_policy(RoleName=role_name, PolicyArn=log_policy_arn)
        sqs_policy_arn = create_policy(
            PolicyName=sqs_policy_name, PolicyDocument=json.dumps(sqs_policy)
        )["Policy"]["Arn"]
        aws_client.iam.attach_role_policy(RoleName=role_name, PolicyArn=sqs_policy_arn)

        create_lambda_function(
            func_name=function_name,
            handler_file=TEST_LAMBDA_ECHO,
            runtime=Runtime.python3_12,
            role=role_arn,
        )
        create_event_source_mapping_response = aws_client.lambda_.create_event_source_mapping(
            EventSourceArn=queue_arn,
            FunctionName=function_name,
            MaximumBatchingWindowInSeconds=1,
        )
        mapping_uuid = create_event_source_mapping_response["UUID"]
        cleanups.append(lambda: aws_client.lambda_.delete_event_source_mapping(UUID=mapping_uuid))
        _await_event_source_mapping_enabled(aws_client.lambda_, mapping_uuid)

        aws_client.sqs.send_message(QueueUrl=queue_url, MessageBody=json.dumps({"foo": "bar"}))

        def _assert_events(expected_events: int):
            log_events = aws_client.logs.filter_log_events(
                logGroupName=f"/aws/lambda/{function_name}",
            )["events"]
            assert (
                len([e["message"] for e in log_events if e["message"].startswith("REPORT")])
                == expected_events
            )

        retry(_assert_events, expected_events=1, retries=20, sleep=2)

        rs = aws_client.sqs.receive_message(QueueUrl=queue_url)
        assert rs.get("Messages", []) == []

        aws_client.iam.detach_role_policy(RoleName=role_name, PolicyArn=sqs_policy_arn)
        # give time for permission changes
        time.sleep(30 if is_aws_cloud() else 5)
        aws_client.sqs.send_message(QueueUrl=queue_url, MessageBody=json.dumps({"foo": "bar"}))

        with pytest.raises(Exception):
            retry(_assert_events, expected_events=2, retries=20, sleep=1)


class TestApiGatewayIntegrations:
    @pytest.fixture
    def apigateway_invoke_url(self, aws_client):
        def _api_invoke_url(
            api_id: str, stage: str = "", path: str = "/", url_type: UrlType = UrlType.HOST_BASED
        ):
            path = f"/{path}" if not path.startswith("/") else path
            if is_aws_cloud():
                stage = f"/{stage}" if stage else ""
                return f"https://{api_id}.execute-api.{aws_client.apigateway.meta.region_name}.amazonaws.com{stage}{path}"
            if url_type == UrlType.HOST_BASED:
                return host_based_url(api_id, stage_name=stage, path=path)
            return path_based_url(api_id, stage_name=stage, path=path)

        return _api_invoke_url

    @pytest.fixture
    def run_role_access_test(
        self,
        aws_client,
        apigateway_invoke_url,
        create_rest_apigw,
        create_role,
        create_policy,
        snapshot,
    ):
        def _run_test(
            policy_document: dict | None,
            setup_integration: Callable[[str, str, str], None],
            disable_permissions: Callable[[], None] = None,
            expected_error_status: int = 500,
        ):
            """
            Runs a positive and a negative permission test against a rest API.
            It will perform the following steps:
                1. Create and set up the IAM role, if a policy document is supplied
                2. Create and set up the rest API
                3. Use callback to set up integrations
                4. Call APIGW and expect a 200 return value
                5. Disable the policy for the role if supplied, or call disable_permissions()
                6. Checks if the api now returns a 500 status code, and snapshots the response

            :param policy_document: Can be None, if disable_permissions is supplied
            :param setup_integration: Used to set up the apigateway integration for method ANY
                Will be called `setup_integration(api_id, resource_id, role_arn)
                role_arn will be None if policy document is None
            :param disable_permissions: Callback to disable permissions before negative test
            :param expected_error_status: Expected status code in the permission error case
            :return:
            """
            stage_name = "test"
            if policy_document:
                role_name = f"integration-role-{short_uid()}"
                policy_name = f"integration-policy-{short_uid()}"
                # create invocation role
                assume_role_policy_document = {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Principal": {"Service": "apigateway.amazonaws.com"},
                            "Action": "sts:AssumeRole",
                        }
                    ],
                }
                role_arn = create_role(
                    RoleName=role_name,
                    AssumeRolePolicyDocument=json.dumps(assume_role_policy_document),
                )["Role"]["Arn"]
                policy_arn = create_policy(
                    PolicyName=policy_name, PolicyDocument=json.dumps(policy_document)
                )["Policy"]["Arn"]
                aws_client.iam.attach_role_policy(RoleName=role_name, PolicyArn=policy_arn)
                snapshot.add_transformer(snapshot.transform.regex(role_name, "<role_name>"))
            else:
                role_arn = None
            # create rest api
            api_id, _, root = create_rest_apigw(
                name=f"test-api-{short_uid()}",
                description="Integration test API",
            )
            resource_id = aws_client.apigateway.create_resource(
                restApiId=api_id, parentId=root, pathPart="{proxy+}"
            )["id"]
            aws_client.apigateway.put_method(
                restApiId=api_id,
                resourceId=resource_id,
                httpMethod="ANY",
                authorizationType="NONE",
            )

            # Setup integration
            setup_integration(api_id, resource_id, role_arn)
            aws_client.apigateway.create_deployment(restApiId=api_id, stageName=stage_name)

            # invoke rest api
            invocation_url = apigateway_invoke_url(
                api_id=api_id,
                stage=stage_name,
                path="/test-path",
            )

            def invoke_api(url, expected_response_code: int):
                apigw_response = requests.get(
                    url,
                    headers={"User-Agent": "python-requests/testing"},
                    verify=False,
                )
                assert expected_response_code == apigw_response.status_code
                return apigw_response

            # retry is necessary against AWS, probably IAM permission delay
            retry(invoke_api, sleep=2, retries=10, url=invocation_url, expected_response_code=200)

            if policy_document:
                aws_client.iam.detach_role_policy(RoleName=role_name, PolicyArn=policy_arn)
            else:
                disable_permissions()

            # retry is necessary against AWS, probably IAM permission delay
            response = retry(
                invoke_api,
                sleep=2,
                retries=10,
                url=invocation_url,
                expected_response_code=expected_error_status,
            )
            snapshot.match("insufficient-permissions-response-status-code", response.status_code)
            snapshot.match("insufficient-permissions-response-body", response.text)

        return _run_test

    @markers.aws.validated
    @pytest.mark.parametrize("integration_type", ["AWS", "AWS_PROXY"])
    def test_lambda_integration(
        self,
        aws_client,
        create_lambda_function,
        run_role_access_test,
        integration_type,
        snapshot,
        partition,
    ):
        function_name = f"test-function-{short_uid()}"

        # create lambda
        create_function_response = create_lambda_function(
            func_name=function_name,
            handler_file=TEST_LAMBDA_APIGATEWAY,
            runtime=Runtime.python3_12,
        )
        function_arn = create_function_response["CreateFunctionResponse"]["FunctionArn"]
        policy_document = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "AllowInvoke",
                    "Effect": "Allow",
                    "Action": ["lambda:InvokeFunction"],
                    "Resource": function_arn,
                }
            ],
        }

        def setup_integration(api_id: str, resource_id: str, role_arn: str):
            aws_client.apigateway.put_integration(
                restApiId=api_id,
                resourceId=resource_id,
                httpMethod="ANY",
                type=integration_type,
                integrationHttpMethod="POST",
                uri=f"arn:{partition}:apigateway:{aws_client.apigateway.meta.region_name}:lambda:path/2015-03-31/functions/{function_arn}/invocations",
                credentials=role_arn,
            )

        run_role_access_test(policy_document, setup_integration)

    @markers.aws.validated
    @pytest.mark.parametrize("integration_type", ["AWS", "AWS_PROXY"])
    def test_lambda_integration_resource_based_policy(
        self,
        aws_client,
        create_lambda_function,
        run_role_access_test,
        account_id,
        integration_type,
        snapshot,
        partition,
    ):
        function_name = f"test-function-{short_uid()}"
        statement_id = f"Statement{short_uid()}"

        # create lambda
        create_function_response = create_lambda_function(
            func_name=function_name,
            handler_file=TEST_LAMBDA_APIGATEWAY,
            runtime=Runtime.python3_12,
        )
        function_arn = create_function_response["CreateFunctionResponse"]["FunctionArn"]

        def setup_integration(api_id: str, resource_id: str, role_arn: str):
            aws_client.lambda_.add_permission(
                FunctionName=function_name,
                Action="lambda:InvokeFunction",
                StatementId=statement_id,
                Principal="apigateway.amazonaws.com",
                SourceArn=f"arn:{partition}:execute-api:{aws_client.apigateway.meta.region_name}:{account_id}:{api_id}/*/*/*",
            )
            aws_client.apigateway.put_integration(
                restApiId=api_id,
                resourceId=resource_id,
                httpMethod="ANY",
                type=integration_type,
                integrationHttpMethod="POST",
                uri=f"arn:{partition}:apigateway:{aws_client.apigateway.meta.region_name}:lambda:path/2015-03-31/functions/{function_arn}/invocations",
            )
            if integration_type == "AWS":
                aws_client.apigateway.put_method_response(
                    restApiId=api_id, resourceId=resource_id, statusCode="200", httpMethod="ANY"
                )
                aws_client.apigateway.put_integration_response(
                    restApiId=api_id, resourceId=resource_id, statusCode="200", httpMethod="ANY"
                )

        def disable_permissions():
            aws_client.lambda_.remove_permission(
                FunctionName=function_name, StatementId=statement_id
            )

        run_role_access_test(
            policy_document=None,
            setup_integration=setup_integration,
            disable_permissions=disable_permissions,
        )

    @markers.aws.validated
    # message is identical, but casing is not. AWS snapshot is capitalized, we return all lowercase
    @markers.snapshot.skip_snapshot_verify(paths=["$..Message", "$..message"])
    def test_kinesis_integration(
        self,
        aws_client,
        run_role_access_test,
        kinesis_create_stream,
        wait_for_stream_ready,
        snapshot,
        partition,
    ):
        stream_name = f"kinesis-stream-{short_uid()}"
        snapshot.add_transformer(snapshot.transform.regex(stream_name, "<stream_name>"))
        kinesis_create_stream(StreamName=stream_name, ShardCount=1)
        wait_for_stream_ready(stream_name=stream_name)
        stream_arn = aws_client.kinesis.describe_stream(StreamName=stream_name)[
            "StreamDescription"
        ]["StreamARN"]
        policy_document = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "AllowPutRecord",
                    "Effect": "Allow",
                    "Action": ["kinesis:PutRecord"],
                    "Resource": stream_arn,
                }
            ],
        }

        # create REST API with Kinesis integration
        region_name = aws_client.apigateway.meta.region_name
        integration_uri = f"arn:{partition}:apigateway:{region_name}:kinesis:action/PutRecord"
        request_templates = {
            "application/json": json.dumps(
                {
                    "StreamName": stream_name,
                    "Data": "$util.base64Encode($input.body)",
                    "PartitionKey": "test",
                }
            )
        }

        def setup_integration(api_id: str, resource_id: str, role_arn: str):
            aws_client.apigateway.put_integration(
                restApiId=api_id,
                resourceId=resource_id,
                httpMethod="ANY",
                type="AWS",
                integrationHttpMethod="POST",
                requestTemplates=request_templates,
                uri=integration_uri,
                credentials=role_arn,
            )

            aws_client.apigateway.put_method_response(
                restApiId=api_id, resourceId=resource_id, statusCode="200", httpMethod="ANY"
            )
            aws_client.apigateway.put_integration_response(
                restApiId=api_id, resourceId=resource_id, statusCode="200", httpMethod="ANY"
            )
            # forward 4xx errors to 400, so the assertions of the test fixtures hold
            aws_client.apigateway.put_method_response(
                restApiId=api_id, resourceId=resource_id, statusCode="400", httpMethod="ANY"
            )
            aws_client.apigateway.put_integration_response(
                restApiId=api_id,
                resourceId=resource_id,
                statusCode="400",
                httpMethod="ANY",
                selectionPattern=r"4\d{2}",
            )

        run_role_access_test(policy_document, setup_integration, expected_error_status=400)

    @markers.aws.validated
    def test_dynamodb_integration(
        self, aws_client, run_role_access_test, dynamodb_create_table, snapshot, partition
    ):
        # create table
        table = dynamodb_create_table()["TableDescription"]
        table_name = table["TableName"]
        snapshot.add_transformer(snapshot.transform.regex(table_name, "<table_name>"))
        table_arn = table["TableArn"]

        policy_document = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "AllowPutItem",
                    "Effect": "Allow",
                    "Action": ["dynamodb:PutItem"],
                    "Resource": table_arn,
                }
            ],
        }

        template = json.dumps(
            {
                "TableName": table_name,
                "Item": {"id": {"S": "id1"}},
            }
        )
        request_templates = {APPLICATION_JSON: template}

        # deploy REST API with integration
        region_name = aws_client.apigateway.meta.region_name
        integration_uri = f"arn:{partition}:apigateway:{region_name}:dynamodb:action/PutItem"

        def setup_integration(api_id: str, resource_id: str, role_arn: str):
            aws_client.apigateway.put_integration(
                restApiId=api_id,
                resourceId=resource_id,
                httpMethod="ANY",
                type="AWS",
                integrationHttpMethod="POST",
                requestTemplates=request_templates,
                uri=integration_uri,
                credentials=role_arn,
            )

            aws_client.apigateway.put_method_response(
                restApiId=api_id, resourceId=resource_id, statusCode="200", httpMethod="ANY"
            )
            aws_client.apigateway.put_integration_response(
                restApiId=api_id, resourceId=resource_id, statusCode="200", httpMethod="ANY"
            )
            # forward 4xx errors to 400, so the assertions of the test fixtures hold
            aws_client.apigateway.put_method_response(
                restApiId=api_id, resourceId=resource_id, statusCode="400", httpMethod="ANY"
            )
            aws_client.apigateway.put_integration_response(
                restApiId=api_id,
                resourceId=resource_id,
                statusCode="400",
                httpMethod="ANY",
                selectionPattern=r"4\d{2}",
            )

        run_role_access_test(policy_document, setup_integration, expected_error_status=400)

    @markers.snapshot.skip_snapshot_verify  # skipped due to error translation from xml to json not implemented
    @markers.aws.validated
    def test_sqs_integration(
        self,
        aws_client,
        run_role_access_test,
        sqs_create_queue,
        sqs_get_queue_arn,
        account_id,
        snapshot,
        partition,
    ):
        # create queue
        queue_name = f"test-queue-{short_uid()}"
        queue_url = sqs_create_queue(QueueName=queue_name)
        queue_arn = sqs_get_queue_arn(queue_url)
        snapshot.add_transformer(snapshot.transform.regex(queue_name, "<queue_name>"))

        policy_document = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "AllowSendMessage",
                    "Effect": "Allow",
                    "Action": ["sqs:SendMessage"],
                    "Resource": queue_arn,
                }
            ],
        }
        request_parameters = {
            "integration.request.header.Content-Type": "'application/x-www-form-urlencoded'"
        }
        request_templates = {
            APPLICATION_JSON: "Action=SendMessage&MessageBody=$util.urlEncode($input.body)"
        }

        # deploy REST API with integration
        region_name = aws_client.apigateway.meta.region_name
        integration_uri = (
            f"arn:{partition}:apigateway:{region_name}:sqs:path/{account_id}/{queue_name}"
        )

        def setup_integration(api_id: str, resource_id: str, role_arn: str):
            aws_client.apigateway.put_integration(
                restApiId=api_id,
                resourceId=resource_id,
                httpMethod="ANY",
                type="AWS",
                integrationHttpMethod="POST",
                requestParameters=request_parameters,
                requestTemplates=request_templates,
                uri=integration_uri,
                credentials=role_arn,
            )

            aws_client.apigateway.put_method_response(
                restApiId=api_id, resourceId=resource_id, statusCode="200", httpMethod="ANY"
            )
            aws_client.apigateway.put_integration_response(
                restApiId=api_id, resourceId=resource_id, statusCode="200", httpMethod="ANY"
            )
            # forward 4xx errors to 400, so the assertions of the test fixtures hold
            aws_client.apigateway.put_method_response(
                restApiId=api_id, resourceId=resource_id, statusCode="400", httpMethod="ANY"
            )
            aws_client.apigateway.put_integration_response(
                restApiId=api_id,
                resourceId=resource_id,
                statusCode="400",
                httpMethod="ANY",
                selectionPattern=r"4\d{2}",
            )

        run_role_access_test(policy_document, setup_integration, expected_error_status=400)

    # TODO SNS integration seems to be pretty broken
    @pytest.mark.skip
    @markers.aws.validated
    def test_sns_integration(
        self, aws_client, run_role_access_test, sns_create_topic, snapshot, partition
    ):
        # create queue
        topic_name = f"test-topic-{short_uid()}"
        topic_arn = sns_create_topic(Name=topic_name)["TopicArn"]
        snapshot.add_transformer(snapshot.transform.regex(topic_name, "<topic_name>"))

        policy_document = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "AllowPublish",
                    "Effect": "Allow",
                    "Action": ["sns:Publish"],
                    "Resource": topic_arn,
                }
            ],
        }
        request_parameters = {
            "integration.request.querystring.TopicArn": f"'{topic_arn}'",
            "integration.request.querystring.Message": "'test-message'",
        }

        # deploy REST API with integration
        region_name = aws_client.apigateway.meta.region_name
        integration_uri = f"arn:{partition}:apigateway:{region_name}:sns:action/Publish"

        def setup_integration(api_id: str, resource_id: str, role_arn: str):
            aws_client.apigateway.put_integration(
                restApiId=api_id,
                resourceId=resource_id,
                httpMethod="ANY",
                type="AWS",
                integrationHttpMethod="POST",
                requestParameters=request_parameters,
                uri=integration_uri,
                credentials=role_arn,
            )

            aws_client.apigateway.put_method_response(
                restApiId=api_id, resourceId=resource_id, statusCode="200", httpMethod="ANY"
            )
            aws_client.apigateway.put_integration_response(
                restApiId=api_id, resourceId=resource_id, statusCode="200", httpMethod="ANY"
            )
            # forward 4xx errors to 400, so the assertions of the test fixtures hold
            aws_client.apigateway.put_method_response(
                restApiId=api_id, resourceId=resource_id, statusCode="400", httpMethod="ANY"
            )
            aws_client.apigateway.put_integration_response(
                restApiId=api_id,
                resourceId=resource_id,
                statusCode="400",
                httpMethod="ANY",
                selectionPattern=r"4\d{2}",
            )

        run_role_access_test(policy_document, setup_integration, expected_error_status=400)


class TestApiGatewayLambdaAuthorizers:
    @pytest.fixture
    def apigateway_invoke_url(self, aws_client):
        def _api_invoke_url(
            api_id: str, stage: str = "", path: str = "/", url_type: UrlType = UrlType.HOST_BASED
        ):
            path = f"/{path}" if not path.startswith("/") else path
            if is_aws_cloud():
                stage = f"/{stage}" if stage else ""
                return f"https://{api_id}.execute-api.{aws_client.apigateway.meta.region_name}.amazonaws.com{stage}{path}"
            if url_type == UrlType.HOST_BASED:
                return host_based_url(api_id, stage_name=stage, path=path)
            return path_based_url(api_id, stage_name=stage, path=path)

        return _api_invoke_url

    @pytest.fixture
    def setup_mock_resource_to_rest_api(self, aws_client):
        def _setup_resource(api_id: str, resource_id: str, authorizer_id: str):
            aws_client.apigateway.put_method(
                restApiId=api_id,
                resourceId=resource_id,
                httpMethod="GET",
                authorizationType="CUSTOM",
                authorizerId=authorizer_id,
            )

            aws_client.apigateway.put_method_response(
                restApiId=api_id,
                resourceId=resource_id,
                httpMethod="GET",
                statusCode="200",
            )

            aws_client.apigateway.put_integration(
                restApiId=api_id,
                resourceId=resource_id,
                httpMethod="GET",
                type="MOCK",
                requestTemplates={"application/json": '{"statusCode": 200}'},
            )

            aws_client.apigateway.put_integration_response(
                restApiId=api_id,
                resourceId=resource_id,
                httpMethod="GET",
                statusCode="200",
                selectionPattern="",
                responseTemplates={
                    "application/json": json.dumps({"statusCode": 200, "message": "GET request"})
                },
            )

        return _setup_resource

    @markers.aws.validated
    @pytest.mark.parametrize("authorizer_type", ["TOKEN", "REQUEST"])
    def test_apigateway_authorizer_with_credentials(
        self,
        aws_client,
        create_rest_apigw,
        create_lambda_function,
        region_name,
        create_role,
        create_policy,
        setup_mock_resource_to_rest_api,
        apigateway_invoke_url,
        snapshot,
        authorizer_type,
    ):
        api_id, _, root_resource_id = create_rest_apigw(name=f"api-{short_uid()}")
        response = aws_client.apigateway.create_resource(
            restApiId=api_id, parentId=root_resource_id, pathPart="auth"
        )
        resource_id = response["id"]

        lambda_auth_name = f"lambda_auth-{short_uid()}"

        auth_function_response = create_lambda_function(
            handler_file=TEST_LAMBDA_APIGATEWAY_AUTHORIZER,
            func_name=lambda_auth_name,
            runtime=Runtime.python3_12,
        )
        authorizer_arn = auth_function_response["CreateFunctionResponse"]["FunctionArn"]
        policy_document = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "AllowInvoke",
                    "Effect": "Allow",
                    "Action": ["lambda:InvokeFunction"],
                    "Resource": authorizer_arn,
                }
            ],
        }

        role_name = f"integration-role-{short_uid()}"
        policy_name = f"integration-policy-{short_uid()}"
        # create invocation role
        assume_role_policy_document = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"Service": "apigateway.amazonaws.com"},
                    "Action": "sts:AssumeRole",
                }
            ],
        }
        role_arn = create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(assume_role_policy_document),
        )["Role"]["Arn"]
        policy_arn = create_policy(
            PolicyName=policy_name, PolicyDocument=json.dumps(policy_document)
        )["Policy"]["Arn"]
        aws_client.iam.attach_role_policy(RoleName=role_name, PolicyArn=policy_arn)

        auth_invocation_arn = arns.apigateway_invocations_arn(authorizer_arn, region_name)

        authorizer = aws_client.apigateway.create_authorizer(
            restApiId=api_id,
            name="api_key_authorizer",
            type=authorizer_type,
            authorizerUri=auth_invocation_arn,
            authorizerCredentials=role_arn,
            authorizerResultTtlInSeconds=0,
            identitySource="method.request.header.apiKey",
        )

        setup_mock_resource_to_rest_api(
            api_id=api_id, resource_id=resource_id, authorizer_id=authorizer["id"]
        )

        stage_name = "dev"
        aws_client.apigateway.create_deployment(restApiId=api_id, stageName=stage_name)

        endpoint = apigateway_invoke_url(api_id=api_id, stage=stage_name, path="/auth")

        def invoke_api(expected_status_code: int):
            result = requests.get(endpoint, verify=False, headers={"apiKey": "whatever"})
            assert result.status_code == expected_status_code
            return result

        # retry is necessary against AWS, probably IAM permission delay
        retry(invoke_api, sleep=2, retries=10, expected_status_code=200)

        aws_client.iam.detach_role_policy(RoleName=role_name, PolicyArn=policy_arn)

        # retry is necessary against AWS, probably IAM permission delay
        response = retry(
            invoke_api,
            sleep=2,
            retries=10,
            expected_status_code=500,
        )
        snapshot.match("insufficient-permissions-response-status-code", response.status_code)
        snapshot.match("insufficient-permissions-response-body", response.text)

    @markers.aws.validated
    @pytest.mark.parametrize("authorizer_type", ["TOKEN", "REQUEST"])
    def test_apigateway_authorizer_resource_based(
        self,
        aws_client,
        create_rest_apigw,
        create_lambda_function,
        region_name,
        account_id,
        setup_mock_resource_to_rest_api,
        apigateway_invoke_url,
        authorizer_type,
        snapshot,
        partition,
    ):
        statement_id = f"Statement{short_uid()}"
        api_id, _, root_resource_id = create_rest_apigw(name=f"api-{short_uid()}")
        response = aws_client.apigateway.create_resource(
            restApiId=api_id, parentId=root_resource_id, pathPart="auth"
        )
        resource_id = response["id"]

        lambda_auth_name = f"lambda_auth-{short_uid()}"

        auth_function_response = create_lambda_function(
            handler_file=TEST_LAMBDA_APIGATEWAY_AUTHORIZER,
            func_name=lambda_auth_name,
            runtime=Runtime.python3_12,
        )
        authorizer_arn = auth_function_response["CreateFunctionResponse"]["FunctionArn"]
        auth_invocation_arn = arns.apigateway_invocations_arn(authorizer_arn, region_name)

        authorizer = aws_client.apigateway.create_authorizer(
            restApiId=api_id,
            name="api_key_authorizer",
            type=authorizer_type,
            authorizerUri=auth_invocation_arn,
            authorizerResultTtlInSeconds=0,
            identitySource="method.request.header.apiKey",
        )

        source_arn = f'arn:{partition}:execute-api:{region_name}:{account_id}:{api_id}/authorizers/{authorizer["id"]}'
        aws_client.lambda_.add_permission(
            FunctionName=lambda_auth_name,
            Action="lambda:InvokeFunction",
            StatementId=statement_id,
            Principal="apigateway.amazonaws.com",
            SourceArn=source_arn,
        )

        setup_mock_resource_to_rest_api(
            api_id=api_id, resource_id=resource_id, authorizer_id=authorizer["id"]
        )

        stage_name = "dev"
        aws_client.apigateway.create_deployment(restApiId=api_id, stageName=stage_name)

        endpoint = apigateway_invoke_url(api_id=api_id, stage=stage_name, path="/auth")

        def invoke_api(expected_status_code: int):
            result = requests.get(endpoint, verify=False, headers={"apiKey": "whatever"})
            assert result.status_code == expected_status_code
            return result

        # retry is necessary against AWS, probably IAM permission delay
        retry(invoke_api, sleep=2, retries=10, expected_status_code=200)

        aws_client.lambda_.remove_permission(
            FunctionName=lambda_auth_name, StatementId=statement_id
        )

        # retry is necessary against AWS, probably IAM permission delay
        response = retry(
            invoke_api,
            sleep=2,
            retries=10,
            expected_status_code=500,
        )
        snapshot.match("insufficient-permissions-response-status-code", response.status_code)
        snapshot.match("insufficient-permissions-response-body", response.text)
