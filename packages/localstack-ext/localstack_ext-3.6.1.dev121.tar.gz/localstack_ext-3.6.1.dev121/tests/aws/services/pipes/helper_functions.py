import json

from botocore.client import BaseClient
from localstack.utils.sync import retry


def get_expected_messages_from_sqs(
    sqs_client: BaseClient,
    queue_url: str,
    expected_message_count: int = 1,
    source_service: str = "unknown",
) -> list[dict]:
    def get_message(queue_url):
        resp = sqs_client.receive_message(
            QueueUrl=queue_url, WaitTimeSeconds=5, MessageAttributeNames=["All"]
        )  # TODO check if this returns all messages if more than 10
        messages = resp.get("Messages", [])
        for message in messages:
            receipt_handle = message["ReceiptHandle"]
            sqs_client.delete_message(QueueUrl=queue_url, ReceiptHandle=receipt_handle)
        assert len(messages) == expected_message_count
        return messages

    messages = retry(get_message, retries=5, queue_url=queue_url)

    actual_event = json.loads(messages[0]["Body"])
    if source_service == "events":
        assert_valid_event(actual_event)
    return messages


def assert_valid_event(event: dict):
    expected_fields = (
        "version",
        "id",
        "detail-type",
        "source",
        "account",
        "time",
        "region",
        "resources",
        "detail",
    )
    for field in expected_fields:
        assert field in event


def assert_machine_created(state_machine_name: str, sfn_client: BaseClient) -> None:
    def check():
        state_machines = sfn_client.list_state_machines()["stateMachines"]
        assert any(state_machine["name"] == state_machine_name for state_machine in state_machines)

    retry(check, sleep=1, retries=4)
