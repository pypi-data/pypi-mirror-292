import json
import logging
from typing import Literal

import pytest
from localstack.utils.sync import retry

StreamType = Literal["DirectPut", "KinesisStreamAsSource", "MSKAsSource"]

LOG = logging.getLogger(__name__)


@pytest.fixture
def redshift_create_cluster(aws_client):
    redshift = aws_client.redshift
    cluster_ids = []

    def _redshift_create_cluster(
        cluster_id: str,
        master_username: str,
        master_password: str,
        db_name: str,
        node_type: str = "t1",
    ):
        response = aws_client.redshift.create_cluster(
            ClusterIdentifier=cluster_id,
            NodeType=node_type,
            MasterUsername=master_username,
            MasterUserPassword=master_password,
            DBName=db_name,
        )
        cluster_ids.append(cluster_id)

        wait_for_cluster_ready(aws_client, cluster_id)

        return response

    yield _redshift_create_cluster

    for cluster_id in cluster_ids:
        try:
            redshift.delete_cluster(ClusterIdentifier=cluster_id, SkipFinalClusterSnapshot=True)
        except Exception as e:
            LOG.info("Failed to delete redshift cluster %s with execption %s", cluster_id, e)


def wait_for_cluster_ready(aws_client, cluster_id: str, sleep: int = 5, retries: int = 3):
    def is_cluster_ready():
        response = aws_client.redshift.describe_clusters(ClusterIdentifier=cluster_id)
        cluster = response["Clusters"][0]
        return cluster["ClusterStatus"] == "available"

    retry(is_cluster_ready, sleep=sleep, retries=retries)


def read_s3_data(aws_client, bucket_name: str) -> dict[str, str]:
    response = aws_client.s3.list_objects(Bucket=bucket_name)
    if response.get("Contents") is None:
        raise Exception("No data in bucket yet")

    keys = [obj.get("Key") for obj in response.get("Contents")]

    bucket_data = dict()
    for key in keys:
        response = aws_client.s3.get_object(Bucket=bucket_name, Key=key)
        data = response["Body"].read().decode("utf-8")
        bucket_data[key] = data
    return bucket_data


def get_all_expected_messages_from_s3(
    aws_client,
    bucket_name: str,
    sleep: int = 5,
    retries: int = 3,
    expected_message_count: int | None = None,
) -> list[str]:
    def get_all_messages():
        bucket_data = read_s3_data(aws_client, bucket_name)
        messages = []
        for input_string in bucket_data.values():
            json_array_string = "[" + input_string.replace("}{", "},{") + "]"
            message = json.loads(json_array_string)
            LOG.debug(f"Received messages: {message}")
            messages.extend(message)
        if expected_message_count is not None and len(messages) != expected_message_count:
            raise Exception(f"Failed to receive all sent messages: {messages}")
        else:
            return messages

    all_messages = retry(get_all_messages, sleep=sleep, retries=retries)
    return all_messages
