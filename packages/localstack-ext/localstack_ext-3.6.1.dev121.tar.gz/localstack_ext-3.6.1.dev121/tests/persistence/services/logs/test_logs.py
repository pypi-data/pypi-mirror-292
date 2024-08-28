import base64
import gzip
import json

from localstack.aws.api.lambda_ import Runtime
from localstack.constants import AWS_REGION_US_EAST_1
from localstack.utils import testutil
from localstack.utils.strings import short_uid
from localstack.utils.sync import retry
from localstack.utils.time import now_utc

TEST_LAMBDA_CODE = """
def handler(event, context):
    import json
    print(json.dumps(event))
    return event
"""


def test_describe_log_stream(persistence_validations, snapshot, aws_client):
    log_group_name = f"test-grp-{short_uid()}"
    log_stream_name = f"test-stream-{short_uid()}"
    aws_client.logs.create_log_group(logGroupName=log_group_name)
    aws_client.logs.create_log_stream(logGroupName=log_group_name, logStreamName=log_stream_name)
    events = [
        {"timestamp": now_utc(millis=True), "message": '{"foo":"bar"}'},
        {"timestamp": now_utc(millis=True), "message": '{"foo":"baz"}'},
    ]
    aws_client.logs.put_log_events(
        logGroupName=log_group_name, logStreamName=log_stream_name, logEvents=events
    )

    def validate():
        snapshot.match(
            "describe_log_stream", aws_client.logs.describe_log_streams(logGroupName=log_group_name)
        )
        snapshot.match(
            "get_log_events",
            aws_client.logs.get_log_events(
                logStreamName=log_stream_name, logGroupName=log_group_name
            ),
        )

    persistence_validations.register(validate)


def test_put_subscription_filter_lambda(snapshot, persistence_validations, aws_client):
    test_lambda_name = f"test-lambda-function-{short_uid()}"
    test_lambda_arn = testutil.create_lambda_function(
        handler_file=TEST_LAMBDA_CODE,
        func_name=test_lambda_name,
        runtime=Runtime.python3_12,
        client=aws_client.lambda_,
    )["CreateFunctionResponse"]["FunctionArn"]
    lambda_log_group = f"/aws/lambda/{test_lambda_name}"

    logs_log_group = f"test-log-group-{short_uid()}"
    aws_client.logs.create_log_group(logGroupName=logs_log_group)

    logs_log_stream = f"test-log-stream-{short_uid()}"
    aws_client.logs.create_log_stream(logGroupName=logs_log_group, logStreamName=logs_log_stream)

    # get account-id to set the correct policy
    account_id = aws_client.sts.get_caller_identity()["Account"]
    aws_client.lambda_.add_permission(
        FunctionName=test_lambda_name,
        StatementId=test_lambda_name,
        Principal=f"logs.{AWS_REGION_US_EAST_1}.amazonaws.com",
        Action="lambda:InvokeFunction",
        SourceArn=f"arn:aws:logs:{AWS_REGION_US_EAST_1}:{account_id}:log-group:{logs_log_group}:*",
        SourceAccount=account_id,
    )

    aws_client.logs.put_subscription_filter(
        logGroupName=logs_log_group,
        filterName="test",
        filterPattern="",
        destinationArn=test_lambda_arn,
    )

    def validate():
        snapshot.match(
            "describe_subscription_filter",
            aws_client.logs.describe_subscription_filters(logGroupName=logs_log_group),
        )
        my_message = {"timestamp": now_utc(millis=True), "message": f"test message {short_uid()}"}
        aws_client.logs.put_log_events(
            logGroupName=logs_log_group,
            logStreamName=logs_log_stream,
            logEvents=[my_message],
        )

        def check_invocation(expected_msg: dict):
            events = aws_client.logs.filter_log_events(logGroupName=lambda_log_group)["events"]
            filtered_events = []
            for e in events:
                if "awslogs" in e["message"]:
                    data = json.loads(e["message"])["awslogs"]["data"].encode("utf-8")
                    decoded_data = gzip.decompress(base64.b64decode(data)).decode("utf-8")
                    for log_event in json.loads(decoded_data)["logEvents"]:
                        log_event.pop("id")  # we are not interested in verifying the id
                        filtered_events.append(log_event)
            assert expected_msg in filtered_events

        retry(check_invocation, retries=20, sleep=1, sleep_before=1, expected_msg=my_message)

    persistence_validations.register(validate)
