import json
import os

import boto3
from aws_lambda_powertools import Tracer

tracer = Tracer(service="ActivePassiveTest")

if "AWS_ENDPOINT_URL" in os.environ:
    sns_client = boto3.client("sns", endpoint_url=os.environ["AWS_ENDPOINT_URL"])
else:
    sns_client = boto3.client("sns")


@tracer.capture_lambda_handler
def handler(event, context):
    sns_client.publish(
        TopicArn=os.environ.get("SNS_TOPIC_ARN"), Subject="Test subj", Message=json.dumps(event)
    )

    print(event)
    response = {
        "message": "hello world from active tracing lambda!",
        "envs": {
            "_X_AMZN_TRACE_ID": os.environ.get("_X_AMZN_TRACE_ID"),
            "_AWS_XRAY_DAEMON_PORT": os.environ.get("_AWS_XRAY_DAEMON_PORT"),
            "_AWS_XRAY_DAEMON_ADDRESS": os.environ.get("_AWS_XRAY_DAEMON_ADDRESS"),
            "AWS_XRAY_CONTEXT_MISSING": os.environ.get("AWS_XRAY_CONTEXT_MISSING"),
            "AWS_XRAY_DAEMON_ADDRESS": os.environ.get("AWS_XRAY_DAEMON_ADDRESS"),
        },
    }
    print(json.dumps(response))
    return response
