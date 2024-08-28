import json
import logging

import pytest
import requests
from localstack import config
from localstack.utils.aws import arns
from localstack.utils.strings import short_uid

LOG = logging.getLogger(__name__)


def test_get_object(persistence_validations, snapshot, aws_client):
    bucket_1 = f"bucket-{short_uid()}"
    aws_client.s3.create_bucket(Bucket=bucket_1)
    aws_client.s3.put_object(Bucket=bucket_1, Key="some-key-1", Body=b"test 123")
    aws_client.s3.put_object(Bucket=bucket_1, Key="some-key-2", Body=b"test 234")

    bucket_2 = f"bucket-{short_uid()}"
    aws_client.s3.create_bucket(Bucket=bucket_2)
    aws_client.s3.put_object(Bucket=bucket_2, Key="some-key-1", Body=b"test 456")

    def validate():
        snapshot.match("b1-f1", aws_client.s3.get_object(Bucket=bucket_1, Key="some-key-1"))
        snapshot.match("b1-f2", aws_client.s3.get_object(Bucket=bucket_1, Key="some-key-2"))

        snapshot.match("b2-f1", aws_client.s3.get_object(Bucket=bucket_2, Key="some-key-1"))

    persistence_validations.register(validate)


def test_s3_notifications(persistence_validations, snapshot, aws_client):
    snapshot.add_transformer(
        [
            snapshot.transform.key_value("ReceiptHandle"),
            snapshot.transform.key_value("x-amz-request-id"),
            snapshot.transform.key_value("MD5OfBody"),  # Body contains a timestamp
        ]
    )
    bucket = f"bucket-{short_uid()}"
    aws_client.s3.create_bucket(Bucket=bucket)
    response = aws_client.sqs.create_queue(QueueName=f"q-{short_uid()}")
    queue_url = response["QueueUrl"]
    queue_attrs = aws_client.sqs.get_queue_attributes(
        QueueUrl=queue_url, AttributeNames=["QueueArn"]
    )
    queue_arn = queue_attrs["Attributes"]["QueueArn"]
    bucket_arn = arns.s3_bucket_arn(bucket)

    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": "*",
                "Action": "sqs:SendMessage",
                "Resource": queue_arn,
                "Condition": {"ArnEquals": {"aws:SourceArn": bucket_arn}},
            }
        ],
    }
    aws_client.sqs.set_queue_attributes(
        QueueUrl=queue_url, Attributes={"Policy": json.dumps(policy)}
    )
    aws_client.s3.put_bucket_notification_configuration(
        Bucket=bucket,
        NotificationConfiguration={
            "QueueConfigurations": [{"QueueArn": queue_arn, "Events": ["s3:ObjectCreated:Put"]}]
        },
    )
    # remove TestEvent
    response = aws_client.sqs.receive_message(QueueUrl=queue_url, WaitTimeSeconds=1)
    messages = response.get("Messages", [])
    if not messages:
        LOG.info("no messages received from %s after 1 second", queue_url)

    for m in messages:
        body = m["Body"]
        # see https://www.mikulskibartosz.name/what-is-s3-test-event/
        if "s3:TestEvent" in body:
            aws_client.sqs.delete_message(QueueUrl=queue_url, ReceiptHandle=m["ReceiptHandle"])

    def validate():
        snapshot.match(
            "get-bucket-notif", aws_client.s3.get_bucket_notification_configuration(Bucket=bucket)
        )
        snapshot.match(
            "put-obj", aws_client.s3.put_object(Bucket=bucket, Key="my_key", Body="something")
        )
        _response = aws_client.sqs.receive_message(QueueUrl=queue_url, WaitTimeSeconds=5)

        snapshot.match("get-notifications", _response)
        for _m in _response.get("Messages", []):
            # delete the message so that it's not in queue when restarting
            aws_client.sqs.delete_message(QueueUrl=queue_url, ReceiptHandle=_m["ReceiptHandle"])

    persistence_validations.register(validate)


def test_list_multipart_and_parts(persistence_validations, snapshot, aws_client):
    bucket = f"bucket-{short_uid()}"
    aws_client.s3.create_bucket(Bucket=bucket)
    key = "multipart-test"
    create_multipart = aws_client.s3.create_multipart_upload(Bucket=bucket, Key=key)
    upload_id = create_multipart["UploadId"]
    aws_client.s3.upload_part(
        Bucket=bucket, Key=key, UploadId=upload_id, PartNumber=1, Body=b"part1"
    )
    aws_client.s3.upload_part(
        Bucket=bucket, Key=key, UploadId=upload_id, PartNumber=2, Body=b"part2"
    )

    def validate():
        snapshot.match("list-multiparts", aws_client.s3.list_multipart_uploads(Bucket=bucket))
        snapshot.match(
            "list-multipart-parts",
            aws_client.s3.list_parts(Bucket=bucket, Key=key, UploadId=upload_id),
        )

    persistence_validations.register(validate)


@pytest.mark.skip(
    reason="CORS handler seems to not properly restore, maybe missing an additional step"
)
def test_s3_cors(persistence_validations, snapshot, aws_client):
    snapshot.add_transformers_list(
        [
            snapshot.transform.key_value("server"),
            snapshot.transform.key_value("x-amz-id-2"),
            snapshot.transform.key_value("x-amz-request-id"),
            snapshot.transform.key_value("date", reference_replacement=False),
        ]
    )
    bucket = f"bucket-{short_uid()}"
    aws_client.s3.create_bucket(Bucket=bucket)
    key = "cors-test"
    aws_client.s3.put_object(Bucket=bucket, Key=key, Body=b"cors-ok")
    aws_client.s3.put_bucket_cors(
        Bucket=bucket,
        CORSConfiguration={
            "CORSRules": [
                {
                    "AllowedOrigins": ["http://localhost:4200"],
                    "AllowedMethods": ["GET", "PUT"],
                    "MaxAgeSeconds": 3000,
                    "AllowedHeaders": ["*"],
                }
            ]
        },
    )

    def validate():
        object_url = f"{config.internal_service_url()}/{bucket}/{key}"
        snapshot.match("get-bucket-cors", aws_client.s3.get_bucket_cors(Bucket=bucket))
        # assert that the CORS headers are correctly applied
        options_req = requests.options(
            object_url,
            headers={"Origin": "http://localhost:4200", "Access-Control-Request-Method": "GET"},
        )
        assert options_req.status_code == 200
        snapshot.match("options-object-cors-headers", dict(options_req.headers))

        get_req = requests.get(object_url, headers={"Origin": "http://localhost:4200"})
        assert get_req.status_code == 200
        snapshot.match("get-object-cors-headers", dict(get_req.headers))

    persistence_validations.register(validate)
