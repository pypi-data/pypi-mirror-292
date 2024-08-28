from localstack.testing.snapshots.transformer_utility import TransformerUtility
from localstack.utils.strings import short_uid


def test_queue_attributes_and_tags(persistence_validations, snapshot, aws_client):
    response = aws_client.sqs.create_queue(
        QueueName=f"q-{short_uid()}",
        tags={"foo": "bar", "baz": "ed"},
    )
    queue_url = response["QueueUrl"]

    def validate():
        attributes = aws_client.sqs.get_queue_attributes(
            QueueUrl=queue_url,
            AttributeNames=["All"],
        )["Attributes"]
        snapshot.match("queue_attributes", attributes)

        assert aws_client.sqs.list_queue_tags(
            QueueUrl=queue_url,
        )["Tags"] == {"foo": "bar", "baz": "ed"}

    persistence_validations.register(validate)


def test_messages_persisted_correctly(persistence_validations, snapshot, aws_client):
    snapshot.add_transformer(TransformerUtility.key_value("ReceiptHandle"))

    response = aws_client.sqs.create_queue(QueueName=f"q-{short_uid()}")
    queue_url = response["QueueUrl"]

    aws_client.sqs.send_message(QueueUrl=queue_url, MessageBody="Hello")

    def validate():
        messages = aws_client.sqs.receive_message(QueueUrl=queue_url, VisibilityTimeout=0)[
            "Messages"
        ]
        snapshot.match("messages", messages)

    persistence_validations.register(validate)


def test_sqs_query_and_sqs_json_client(persistence_validations, snapshot, aws_client):
    response = aws_client.sqs_query.create_queue(
        QueueName=f"q-{short_uid()}",
    )
    queue_url = response["QueueUrl"]

    def validate():
        queue_response = aws_client.sqs.get_queue_attributes(QueueUrl=queue_url)
        snapshot.match("get-queue", queue_response)

    persistence_validations.register(validate)
