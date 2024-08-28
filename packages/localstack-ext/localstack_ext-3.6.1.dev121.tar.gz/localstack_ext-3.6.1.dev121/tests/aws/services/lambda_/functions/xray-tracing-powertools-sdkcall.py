import os

from aws_lambda_powertools import Logger, Tracer

logger = Logger(service="APP")
tracer = Tracer(service="xray-testing")


@tracer.capture_method
def say_hello(name):
    tracer.put_annotation("CustomAnnotation", "CONFIRMED")
    tracer.put_metadata("metakey", "metavalue")
    return {"message": f"hello {name}!"}


@logger.inject_lambda_context(log_event=True)
@tracer.capture_lambda_handler
def handler(event, context):
    import boto3

    if "AWS_ENDPOINT_URL" in os.environ:
        lambda_client = boto3.client(
            "lambda",
            endpoint_url=os.environ.get("AWS_ENDPOINT_URL"),
        )
    else:
        lambda_client = boto3.client("lambda")

    # TODO: avoid snapshotting list_functions, which could lead to a flaky test upon improper cleanup.
    #  Select a more deterministic operation instead or skip the snapshot wherever possible.
    #  See review comment: https://github.com/localstack/localstack-ext/pull/2891/files#r1579588097
    fns = lambda_client.list_functions()["Functions"]
    response = {
        "message": say_hello("user"),
        "functions": fns,
        "envs": {
            "_X_AMZN_TRACE_ID": os.environ.get("_X_AMZN_TRACE_ID"),
            "_AWS_XRAY_DAEMON_PORT": os.environ.get("_AWS_XRAY_DAEMON_PORT"),
            "_AWS_XRAY_DAEMON_ADDRESS": os.environ.get("_AWS_XRAY_DAEMON_ADDRESS"),
            "AWS_XRAY_CONTEXT_MISSING": os.environ.get("AWS_XRAY_CONTEXT_MISSING"),
            "AWS_XRAY_DAEMON_ADDRESS": os.environ.get("AWS_XRAY_DAEMON_ADDRESS"),
        },
    }
    return response
