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
    response = {
        "message": say_hello("user"),
        "envs": {
            "_X_AMZN_TRACE_ID": os.environ.get("_X_AMZN_TRACE_ID"),
            "_AWS_XRAY_DAEMON_PORT": os.environ.get("_AWS_XRAY_DAEMON_PORT"),
            "_AWS_XRAY_DAEMON_ADDRESS": os.environ.get("_AWS_XRAY_DAEMON_ADDRESS"),
            "AWS_XRAY_CONTEXT_MISSING": os.environ.get("AWS_XRAY_CONTEXT_MISSING"),
            "AWS_XRAY_DAEMON_ADDRESS": os.environ.get("AWS_XRAY_DAEMON_ADDRESS"),
        },
    }
    return response
