import pytest
from localstack.utils.strings import short_uid
from localstack.utils.sync import retry


@pytest.mark.skip(reason="This test has been a bit flaky recently")
def test_log_and_get_record(persistence_validations, snapshot, aws_client):
    bucket_name = f"cloudtrail-bucket-{short_uid()}"
    aws_client.s3.create_bucket(Bucket=bucket_name)

    trail_name = f"test-trail-{short_uid()}"
    aws_client.cloudtrail.create_trail(
        Name=trail_name,
        S3BucketName=bucket_name,
    )
    aws_client.cloudtrail.start_logging(Name=trail_name)
    queue_name = f"test-queue-{short_uid()}"
    aws_client.sqs.create_queue(QueueName=queue_name)

    def validate():
        snapshot.match("get_log_record", aws_client.cloudtrail.get_trail(Name=trail_name))

        def _get_event():
            _events = aws_client.cloudtrail.lookup_events(
                LookupAttributes=[{"AttributeKey": "EventName", "AttributeValue": "CreateQueue"}]
            )["Events"]
            assert len(_events) >= 1
            return _events

        events = retry(_get_event, retries=5, sleep=2)
        snapshot.match("lookup_event", events)

    persistence_validations.register(validate)
