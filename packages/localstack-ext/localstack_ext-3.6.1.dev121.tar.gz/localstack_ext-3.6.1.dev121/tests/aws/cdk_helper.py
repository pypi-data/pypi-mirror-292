from typing import TYPE_CHECKING

from localstack.testing.aws.util import is_aws_cloud
from localstack.utils.run import LOG
from localstack.utils.sync import retry

if TYPE_CHECKING:
    from mypy_boto3_rds import RDSClient


def delete_db_instances_from_cluster(rds_client: "RDSClient", cluster_id: str):
    """
    Utility to cleanup instances from a cluster. Helper to cleanup neptune clusters.
    With the latest alpha-cdk the neptune cleanup is not working properly, and instances
    need to be deleted manually, otherwise the cdk-stack cannot be deleted.

    :param rds_client: rds client
    :param cluster_id: cluster-id
    :return: None
    """
    if not cluster_id:
        LOG.warn("Cannot cleanup cluster, no cluster_id set")
        return

    filters = [{"Name": "db-cluster-id", "Values": [cluster_id]}]
    instances = rds_client.describe_db_instances(Filters=filters)["DBInstances"]
    for db_id in instances:
        rds_client.delete_db_instance(DBInstanceIdentifier=db_id["DBInstanceIdentifier"])

    # wait until all databases are gone
    def _deletion_complete():
        found_instances = rds_client.describe_db_instances(Filters=filters)["DBInstances"]
        assert not found_instances

    retry(
        _deletion_complete,
        sleep=30 if is_aws_cloud() else 1,
        retries=100 if is_aws_cloud() else 30,
    )
