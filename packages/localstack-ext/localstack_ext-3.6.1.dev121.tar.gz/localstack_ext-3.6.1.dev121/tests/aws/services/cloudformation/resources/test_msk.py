from localstack.testing.pytest import markers
from localstack.utils.strings import short_uid
from localstack.utils.sync import retry, wait_until

from tests.aws.services.cloudformation.utils import load_template


@markers.aws.unknown
def test_create_cluster(cleanup_stacks, is_stack_created, aws_client):
    stack_name = f"stack-{short_uid()}"
    cluster_name = f"c-{short_uid()}"
    template_rendered = load_template("msk_kafka_cluster.yaml", cluster_name=cluster_name)

    response = aws_client.cloudformation.create_stack(
        StackName=stack_name, TemplateBody=template_rendered
    )
    stack_id = response["StackId"]

    def _is_cluster_active():
        clusters = aws_client.kafka.list_clusters()["ClusterInfoList"]
        matching = [c for c in clusters if c["ClusterName"] == cluster_name]
        return matching[0]["State"] == "ACTIVE"

    try:
        wait_until(is_stack_created(stack_id))

        # assert that cluster has been created
        assert wait_until(_is_cluster_active)

    finally:
        cleanup_stacks([stack_id])

        # assert that cluster no longer exists
        def _assert_deleted():
            assert not [
                c
                for c in aws_client.kafka.list_clusters()["ClusterInfoList"]
                if c["ClusterName"] == cluster_name
            ]

        retry(_assert_deleted, sleep=1, retries=5)
