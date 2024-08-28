import requests
from botocore.exceptions import ClientError
from localstack import config


def test_stackinfo_resource(aws_client):
    # make one api call to make sure to have something in the stackinfo
    aws_client.sqs.list_queues()

    response = requests.get(config.internal_service_url() + "/_localstack/stackinfo")
    first_call = response.json()
    assert not first_call["api_key"]
    assert first_call["duration_in_seconds"] >= 1
    assert first_call["number_of_services"] >= 1
    assert first_call["number_of_api_calls_success"] >= 1
    assert first_call["number_of_api_calls_error"] >= 0
    assert first_call["top_user_agent"]

    # make some API calls
    aws_client.sqs.list_queues()
    try:
        aws_client.sqs.delete_queue(
            QueueUrl=config.internal_service_url() + "/000000000000/does-not-exist"
        )
    except ClientError:
        pass

    response = requests.get(config.internal_service_url() + "/_localstack/stackinfo")
    second_call = response.json()

    assert second_call["number_of_api_calls_success"] > first_call["number_of_api_calls_success"]
    assert second_call["number_of_api_calls_error"] > first_call["number_of_api_calls_error"]
