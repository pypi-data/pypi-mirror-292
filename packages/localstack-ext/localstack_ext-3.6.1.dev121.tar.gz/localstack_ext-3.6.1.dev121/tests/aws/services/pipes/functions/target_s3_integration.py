import base64
import json
import os

import boto3

s3 = boto3.client("s3", endpoint_url=os.environ.get("AWS_ENDPOINT_URL"))
BUCKET_NAME = os.environ["S3_BUCKET_NAME"]


def handler(events, context):
    # Store events in S3 bucket
    s3_key = context.aws_request_id
    s3.put_object(Body=json.dumps(events), Bucket=BUCKET_NAME, Key=s3_key)

    # Trigger intentional failure
    for event in events:
        data = base64.b64decode(event["data"]).decode("utf-8")
        data_json = json.loads(data)
        if data_json.get("fail", False):
            raise Exception("Fail intentionally")
