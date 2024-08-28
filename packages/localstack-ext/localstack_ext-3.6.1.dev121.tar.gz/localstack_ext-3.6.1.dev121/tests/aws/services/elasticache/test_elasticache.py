import pytest
from botocore.exceptions import ClientError
from localstack.testing.aws.util import is_aws_cloud
from localstack.testing.pytest import markers
from localstack.testing.snapshots.transformer_utility import TransformerUtility
from localstack.utils.strings import short_uid


def elasticache_api():
    """
    :return: array with Transformers for Elasticache.
    """
    return [
        TransformerUtility.key_value("CacheClusterId"),
        TransformerUtility.key_value("ReplicationGroupId"),
    ]


def get_waiter_config():
    """Return a waiter config that can be used to spin up replication groups and cache clusters. 30 min on
    AWS, 60 seconds on LocalStack."""
    if is_aws_cloud():
        return {"Delay": 10, "MaxAttempts": 180}
    else:
        return {"Delay": 1, "MaxAttempts": 60}


class TestElastiCache:
    @markers.aws.validated
    def test_cluster_no_engine(self, aws_client, snapshot):
        with pytest.raises(ClientError) as e:
            aws_client.elasticache.create_cache_cluster(CacheClusterId=f"cluster-{short_uid()}")
        snapshot.match("cluster-null-engine", e.value.response)

    @markers.aws.validated
    def test_cluster_no_cache_type(self, aws_client, snapshot):
        with pytest.raises(ClientError) as e:
            aws_client.elasticache.create_cache_cluster(
                CacheClusterId=f"cluster-{short_uid()}", Engine="redis"
            )
        snapshot.match("cluster-null-cache-node-type", e.value.response)

    @markers.aws.validated
    def test_cluster_redis_num_nodes_greater_than_one(self, aws_client, snapshot):
        with pytest.raises(ClientError) as e:
            aws_client.elasticache.create_cache_cluster(
                CacheClusterId=f"cluster-{short_uid()}",
                Engine="redis",
                CacheNodeType="cache.t3.small",
                NumCacheNodes=3,
            )
        snapshot.match("cluster-redis-too-large", e.value.response)

    @markers.aws.validated
    def test_replication_group_no_engine(self, aws_client, snapshot):
        with pytest.raises(ClientError) as e:
            aws_client.elasticache.create_replication_group(
                ReplicationGroupId=f"replication-group-{short_uid()}",
                ReplicationGroupDescription="Description",
            )
        snapshot.match("replication-null-engine", e.value.response)

    @markers.aws.validated
    def test_replication_group_primary_cluster_non_existing(self, aws_client, snapshot):
        with pytest.raises(ClientError) as e:
            aws_client.elasticache.create_replication_group(
                ReplicationGroupId=f"replication-group-{short_uid()}",
                ReplicationGroupDescription="Description",
                PrimaryClusterId="cluster-does-not-exist",
                NumCacheClusters=1,
            )

        snapshot.match("replication-no-primary-cluster", e.value.response)

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(
        paths=[
            # snapshot windows and AZ cannot be guaranteed
            "$..SnapshotWindow",
            "$..PreferredAvailabilityZone",
            "$..CustomerAvailabilityZone",
            # engine is different depending on what the default is in localstack
            "$..CacheParameterGroup.CacheParameterGroupName",
            "$..EngineVersion",
            # endpoints are naturally different in AWS and localstack
            "$..CacheCluster.ConfigurationEndpoint",
            "$..CacheClusters..ConfigurationEndpoint",
            "$..Endpoint.Address",
            "$..Endpoint.Port",
        ]
    )
    def test_cache_cluster_default_crud(self, aws_client, snapshot, cleanups):
        snapshot.add_transformers_list(elasticache_api())
        cleanups.append(
            lambda: aws_client.elasticache.delete_cache_cluster(CacheClusterId=cache_cluster_id)
        )

        cache_cluster_id = f"test-cache-cluster-{short_uid()}"
        response = aws_client.elasticache.create_cache_cluster(
            CacheClusterId=cache_cluster_id,
            Engine="redis",
            CacheNodeType="cache.t2.micro",
            PreferredMaintenanceWindow="thu:05:30-thu:06:30",
            SnapshotWindow="04:00-05:00",
            NumCacheNodes=1,
        )
        snapshot.match("create-cache-cluster", response)

        aws_client.elasticache.get_waiter("cache_cluster_available").wait(
            CacheClusterId=cache_cluster_id,
            WaiterConfig=get_waiter_config(),
        )

        response = aws_client.elasticache.describe_cache_clusters(CacheClusterId=cache_cluster_id)
        snapshot.match("describe-cache-clusters", response)

        response = aws_client.elasticache.describe_cache_clusters(
            CacheClusterId=cache_cluster_id, ShowCacheNodeInfo=True
        )
        snapshot.match("describe-cache-clusters-with-info", response)

        response = aws_client.elasticache.delete_cache_cluster(CacheClusterId=cache_cluster_id)
        snapshot.match("delete-cache-cluster", response)

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(
        paths=[
            # snapshot windows and AZ cannot be guaranteed
            "$..SnapshotWindow",
            "$..PreferredAvailabilityZone",
            "$..PreferredMaintenanceWindow",
            # engine is different depending on what the default is in localstack
            "$..CacheParameterGroup.CacheParameterGroupName",
            "$..EngineVersion",
            # endpoints are naturally different in AWS and localstack
            "$..PrimaryEndpoint.Address",
            "$..PrimaryEndpoint.Port",
            "$..ReaderEndpoint.Address",
            "$..ReaderEndpoint.Port",
            "$..ReadEndpoint.Address",
            "$..ReadEndpoint.Port",
        ]
    )
    def test_basic_crud_replication_group_non_cluster(self, aws_client, snapshot, cleanups):
        snapshot.add_transformers_list(elasticache_api())
        cleanups.append(
            lambda: aws_client.elasticache.delete_replication_group(
                ReplicationGroupId=replication_group_id
            )
        )

        replication_group_id = f"test-replication-group-{short_uid()}"
        response = aws_client.elasticache.create_replication_group(
            ReplicationGroupId=replication_group_id,
            ReplicationGroupDescription="my test replication group",
            Engine="redis",
            CacheNodeType="cache.t2.micro",
            PreferredMaintenanceWindow="thu:05:30-thu:06:30",
            SnapshotWindow="03:00-04:00",
            NumCacheClusters=3,
        )
        snapshot.match("create-replication-group", response)

        aws_client.elasticache.get_waiter("replication_group_available").wait(
            ReplicationGroupId=replication_group_id,
            WaiterConfig=get_waiter_config(),
        )

        response = aws_client.elasticache.describe_replication_groups(
            ReplicationGroupId=replication_group_id
        )
        snapshot.match("describe-replication-group", response)

        response = aws_client.elasticache.describe_cache_clusters()
        clusters = [
            cluster
            for cluster in response["CacheClusters"]
            if cluster.get("ReplicationGroupId") == replication_group_id
        ]
        clusters.sort(key=lambda c: c["CacheClusterId"])
        snapshot.match("clusters", clusters)

        response = aws_client.elasticache.delete_replication_group(
            ReplicationGroupId=replication_group_id
        )
        snapshot.match("delete-replication-group", response)

    @markers.aws.validated
    @pytest.mark.parametrize(
        "param",
        [
            # TODO: there may be more
            ("CacheNodeType", "cache.m5.large"),
            ("Engine", "redis"),
            ("EngineVersion", "redis3.2"),
        ],
        ids=["CacheNodeType", "Engine", "EngineVersion"],
    )
    def test_replication_group_primary_cluster_invalid_parameter_combination(
        self, aws_client, param
    ):
        """You cannot use certain parameters when PrimaryClusterId is set because the attributes are derived from the
        primary cluster."""
        params = {
            "ReplicationGroupId": f"replication-group-{short_uid()}",
            "ReplicationGroupDescription": "Description",
            "PrimaryClusterId": "cluster-does-not-exist",
            param[0]: param[1],
        }

        with pytest.raises(ClientError) as e:
            aws_client.elasticache.create_replication_group(**params)

        assert e.value.response["Error"] == {
            "Code": "InvalidParameterCombination",
            "Message": "Cannot use the given parameters when using an existing primary cache cluster ID.",
            "Type": "Sender",
        }

    @markers.aws.validated
    def test_replication_group_no_cache_type(self, aws_client, snapshot):
        with pytest.raises(ClientError) as e:
            aws_client.elasticache.create_replication_group(
                ReplicationGroupId=f"replication-group-{short_uid()}",
                ReplicationGroupDescription="Description",
                Engine="redis",
            )
        snapshot.match("replication-group-null-cache-node-type", e.value.response)
