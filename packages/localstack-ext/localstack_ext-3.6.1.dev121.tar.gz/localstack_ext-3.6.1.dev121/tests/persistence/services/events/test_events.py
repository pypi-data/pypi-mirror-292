import json

from localstack.utils.strings import short_uid
from localstack.utils.sync import retry


def test_events_sqs_event(aws_client, persistence_validations, snapshot):
    queue_name = f"queue-{short_uid()}"
    queue_url = aws_client.sqs.create_queue(QueueName=queue_name)["QueueUrl"]

    queue_arn = aws_client.sqs.get_queue_attributes(
        QueueUrl=queue_url, AttributeNames=["QueueArn"]
    )["Attributes"]["QueueArn"]
    policy = {
        "Version": "2012-10-17",
        "Id": f"sqs-eventbridge-{short_uid()}",
        "Statement": [
            {
                "Sid": f"SendMessage-{short_uid()}",
                "Effect": "Allow",
                "Principal": {"Service": "events.amazonaws.com"},
                "Action": "sqs:SendMessage",
                "Resource": queue_arn,
            }
        ],
    }
    aws_client.sqs.set_queue_attributes(
        QueueUrl=queue_url, Attributes={"Policy": json.dumps(policy)}
    )

    rule_name = f"test-rule-{short_uid()}"
    target_id = f"test-target-{short_uid()}"
    bus_name = f"test-bus-{short_uid()}"

    aws_client.events.create_event_bus(Name=bus_name)
    pattern = {
        "source": ["core.update-account-command"],
        "detail-type": ["core.update-account-command"],
    }
    aws_client.events.put_rule(
        Name=rule_name,
        EventBusName=bus_name,
        EventPattern=json.dumps(pattern),
    )
    aws_client.events.put_targets(
        Rule=rule_name,
        EventBusName=bus_name,
        Targets=[{"Id": target_id, "Arn": queue_arn}],
    )

    def validate():
        entry = [
            {
                "Source": pattern["source"][0],
                "DetailType": pattern["detail-type"][0],
                "Detail": json.dumps({"message": "long time"}),
                "Time": "2022-01-01 00:00:00Z",
            },
        ]
        describe_rule = aws_client.events.describe_rule(Name=rule_name, EventBusName=bus_name)
        snapshot.match("describe-rule", describe_rule)

        entry[0]["EventBusName"] = bus_name
        response = aws_client.events.put_events(Entries=entry)
        assert not response.get("FailedEntryCount")

        def _get_message(_queue_url: str):
            resp = aws_client.sqs.receive_message(
                QueueUrl=_queue_url, WaitTimeSeconds=5, MaxNumberOfMessages=1
            )
            messages = resp.get("Messages")
            if messages:
                for message in messages:
                    receipt_handle = message["ReceiptHandle"]
                    aws_client.sqs.delete_message(QueueUrl=_queue_url, ReceiptHandle=receipt_handle)
            assert len(messages) == 1
            return messages

        message = retry(_get_message, retries=5, _queue_url=queue_url)[0]
        snapshot.match("message-event", message["Body"])

    persistence_validations.register(validate)
