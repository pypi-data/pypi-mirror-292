from localstack.testing.aws.util import is_aws_cloud
from localstack.testing.pytest import markers
from localstack.testing.snapshots.transformer_utility import TransformerUtility
from localstack.utils.strings import short_uid
from localstack.utils.sync import poll_condition


def memorydb_api():
    """
    :return: array with Transformers for MemoryDB.
    """
    return [
        TransformerUtility.key_value("Name"),
        TransformerUtility.key_value("ACLName"),
    ]


class TestMemoryDB:
    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(
        paths=[
            # Endpoints are different on AWS and LocalStack
            "$..ClusterEndpoint",
            # TODO EngineVersion defaults are different between regions
            "$..EnginePatchVersion",
            "$..EngineVersion",
            # TODO unclear how those are evaluated
            "$..MaintenanceWindow",
            "$..SnapshotWindow",
            "$..SnapshotRetentionLimit",
            # TODO not yet implemented
            "$..TLSEnabled",
            "$..DataTiering",
            "$..SubnetGroupName",
            "$..AvailabilityMode",
            # List indices do not work:
            "$..Cluster.SecurityGroups",
            "$..Clusters..SecurityGroups",
            "$..Cluster.Shards",
        ]
    )
    def test_cluster_default_crud(self, aws_client, snapshot, cleanups):
        snapshot.add_transformers_list(memorydb_api())
        cluster_name = f"cluster-{short_uid()}"
        acl_name = f"acl-{short_uid()}"
        cleanups.append(lambda: aws_client.memorydb.delete_acl(ACLName=acl_name))

        aws_client.memorydb.create_acl(ACLName=acl_name)
        creation = aws_client.memorydb.create_cluster(
            ClusterName=cluster_name,
            ACLName=acl_name,
            NodeType="db.t4g.small",
            NumReplicasPerShard=0,
            NumShards=1,
        )
        snapshot.match("cluster-creation", creation)

        def _cluster_available():
            description = aws_client.memorydb.describe_clusters(ClusterName=cluster_name)
            return description["Clusters"][0]["Status"] == "available"

        # Wait for cluster to become available, 30 minutes on AWS, 60 seconds on LocalStack
        if is_aws_cloud():
            poll_condition(_cluster_available, timeout=1800, interval=10)
        else:
            poll_condition(_cluster_available, timeout=60, interval=1)

        description = aws_client.memorydb.describe_clusters(ClusterName=cluster_name)
        snapshot.match("cluster-description", description)

        deletion = aws_client.memorydb.delete_cluster(ClusterName=cluster_name)
        snapshot.match("cluster-deletion", deletion)
