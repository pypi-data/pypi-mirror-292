import base64
import json
import os

import boto3

s3 = boto3.client("s3", endpoint_url=os.environ.get("AWS_ENDPOINT_URL"))
BUCKET_NAME = os.environ["S3_BUCKET_NAME"]


def get_data(event: dict) -> str:
    """Returns the content as string for different event sources (SQS, streaming)."""
    if sqs_body := event.get("body"):
        return sqs_body
    elif streaming_data := event.get("data"):
        return base64.b64decode(streaming_data).decode("utf-8")
    else:
        ValueError("Could not get data string from event.")


def get_item_identifier(data_json: dict) -> str:
    if message_id := data_json.get("messageId"):
        return message_id
    elif event_id := data_json.get("eventId"):
        return event_id
    else:
        raise ValueError("Could not detect item identifier in event data.")


def handler(events, context):
    # Store events in S3 bucket
    s3_key = context.aws_request_id
    s3.put_object(Body=json.dumps(events), Bucket=BUCKET_NAME, Key=s3_key)

    # Partial batch failure:
    # https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-pipes-batching-concurrency.html
    batch_item_failures = []
    for event in events:
        data = get_data(event)
        data_json = json.loads(data)
        if data_json.get("fail", False):
            item_identifier = get_item_identifier(event)
            if item_identifier is None:
                raise Exception("Failed to detect item identifier for partial batch failure.")
            batch_item = {"itemIdentifier": item_identifier}
            batch_item_failures.append(batch_item)

    return {"batchItemFailures": batch_item_failures}
