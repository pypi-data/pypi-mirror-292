import json
import os


def handler(event, context):
    print("hello world from tracing lambda!")
    print(event)
    response = {
        "message": "hello world from tracing lambda!",
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
