import logging

import pytest
import redis
from localstack.pro.core.aws.api.elasticache import CacheCluster, ReplicationGroup
from localstack.utils.strings import short_uid
from localstack.utils.sync import retry

LOG = logging.getLogger(__name__)


def connect_to_redis(
    redis_resource: CacheCluster | ReplicationGroup, cluster: bool = False
) -> redis.Redis | redis.RedisCluster:
    """Takes an Elasticache resource and creates a redis connection to the main endpoint."""
    if "ConfigurationEndpoint" in redis_resource:
        # replication groups in cluster mode (and legacy provider CacheCluster/non-cluster ReplicationGroup)
        endpoint = redis_resource["ConfigurationEndpoint"]
    elif "NodeGroups" in redis_resource:
        # replication group in non-cluster mode
        endpoint = redis_resource["NodeGroups"][0]["PrimaryEndpoint"]
    elif "CacheClusterId" in redis_resource:
        # normal cache cluster (needs ShowCacheNodeInfo=True)
        endpoint = redis_resource["CacheNodes"][0]["Endpoint"]
    else:
        raise KeyError

    if cluster:
        return redis.RedisCluster(host=endpoint["Address"], port=int(endpoint["Port"]))
    else:
        return redis.Redis(host=endpoint["Address"], port=int(endpoint["Port"]))


@pytest.mark.skip(reason="flaky")
@pytest.mark.skip_snapshot_verify(
    paths=[
        "$..CacheClusters..CacheNodes..Endpoint.Port",
        "$..CacheClusters..ConfigurationEndpoint.Port",
    ]
)
def test_elasticache_describe_cache_cluster(persistence_validations, snapshot, aws_client):
    cluster_id = f"cluster-{short_uid()}"
    aws_client.elasticache.create_cache_cluster(
        CacheClusterId=cluster_id,
        Engine="redis",
        CacheNodeType="cache.t3.small",
    )

    # wait for cluster
    aws_client.elasticache.get_waiter("cache_cluster_available").wait(CacheClusterId=cluster_id)
    cluster = aws_client.elasticache.describe_cache_clusters(
        CacheClusterId=cluster_id, ShowCacheNodeInfo=True
    )["CacheClusters"][0]

    with connect_to_redis(cluster) as r:
        r.set("foo", "bar")
        r.close()

    def validate():
        # wait for cluster to be ready
        aws_client.elasticache.get_waiter("cache_cluster_available").wait(CacheClusterId=cluster_id)

        # wait for cache cluster
        describe_cache_cluster = aws_client.elasticache.describe_cache_clusters(
            CacheClusterId=cluster_id, ShowCacheNodeInfo=True
        )
        snapshot.match("describe_cache_cluster", describe_cache_cluster)

        def _try_connect():
            with connect_to_redis(describe_cache_cluster["CacheClusters"][0]) as r:
                assert r.ping()
                assert r.get("foo") == b"bar"

        # the redis server may not immediately spin up
        retry(_try_connect, retries=10)

    persistence_validations.register(validate)


@pytest.mark.skip(reason="flaky")
@pytest.mark.skip_snapshot_verify(paths=["$..ReplicationGroups..NodeGroups..PrimaryEndpoint.Port"])
def test_elasticache_describe_replication_group(persistence_validations, snapshot, aws_client):
    group_id = f"group-id-{short_uid()}"
    aws_client.elasticache.create_replication_group(
        ReplicationGroupId=group_id,
        ReplicationGroupDescription="test",
        NumNodeGroups=2,
        ReplicasPerNodeGroup=2,
        Engine="redis",
        CacheNodeType="cache.t3.small",
    )

    aws_client.elasticache.get_waiter("replication_group_available").wait(
        ReplicationGroupId=group_id
    )

    replication_group = aws_client.elasticache.describe_replication_groups(
        ReplicationGroupId=group_id
    )["ReplicationGroups"][0]

    with connect_to_redis(replication_group, cluster=True) as r:
        r.set("foo", "bar")

    def validate():
        aws_client.elasticache.get_waiter("replication_group_available").wait(
            ReplicationGroupId=group_id
        )

        describe_replication_group = aws_client.elasticache.describe_replication_groups(
            ReplicationGroupId=group_id
        )
        snapshot.match("describe_replication_group", describe_replication_group)

        def _try_connect():
            with connect_to_redis(
                describe_replication_group["ReplicationGroups"][0], cluster=True
            ) as r:
                assert r.ping()
                assert r.get("foo") == b"bar"

        # the redis server may not immediately spin up
        retry(_try_connect, retries=10)

        # make sure we can also still set something
        with connect_to_redis(
            describe_replication_group["ReplicationGroups"][0], cluster=True
        ) as r:
            assert r.set("bar", "baz")
        with connect_to_redis(
            describe_replication_group["ReplicationGroups"][0], cluster=True
        ) as r:
            assert r.get("bar") == b"baz"

    persistence_validations.register(validate)
