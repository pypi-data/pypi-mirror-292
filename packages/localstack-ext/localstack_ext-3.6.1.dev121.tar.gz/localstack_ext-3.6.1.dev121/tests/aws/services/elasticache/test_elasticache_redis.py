"""These tests aim to test the the actual redis infrastructure integration. Are the redis clusters created
correctly, can they be accessed, etc.? This is harder to operatioanlize on AWS and still needs to be
tested."""

import logging

import aws_cdk as cdk
import aws_cdk.aws_ec2 as ec2
import aws_cdk.aws_elasticache as elasticache
import pytest
import redis
from localstack.testing.pytest import markers
from localstack.utils.common import external_service_ports
from localstack.utils.strings import short_uid
from localstack.utils.sync import retry

LOG = logging.getLogger(__name__)


class RedisVpcStack(cdk.Stack):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # VPC
        self.vpc = ec2.Vpc(
            self,
            "VPC",
            nat_gateways=1,
            cidr="10.0.0.0/16",
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="public", subnet_type=ec2.SubnetType.PUBLIC, cidr_mask=24
                ),
                ec2.SubnetConfiguration(
                    name="private", subnet_type=ec2.SubnetType.PRIVATE_WITH_NAT, cidr_mask=24
                ),
            ],
        )
        self.redis_sec_group = ec2.SecurityGroup(
            self,
            "redis-sec-group",
            security_group_name="redis-sec-group",
            vpc=self.vpc,
            allow_all_outbound=True,
        )
        redis_subnet_ids = [ps.subnet_id for ps in self.vpc.public_subnets]
        self.redis_subnet_group = elasticache.CfnSubnetGroup(
            self,
            id="redis_subnet_group",
            subnet_ids=redis_subnet_ids,  # todo: add list of subnet ids here
            description="subnet group for redis",
        )


class TestCacheCluster:
    stack_name = "TestElasticacheClusterStack"

    @pytest.fixture(scope="class", autouse=True)
    def infrastructure(self, aws_client, infrastructure_setup):
        infra = infrastructure_setup("elasticache-cluster-test")

        app = cdk.App()
        stack = RedisVpcStack(app, self.stack_name)

        # cluster
        cluster_name = f"redis-cluster-{short_uid()}"
        redis_cluster = elasticache.CfnCacheCluster(
            stack,
            id="RedisCluster",
            cluster_name=cluster_name,
            engine="redis",
            cache_node_type="cache.t2.micro",
            num_cache_nodes=1,
            cache_subnet_group_name=stack.redis_subnet_group.ref,
            vpc_security_group_ids=[stack.redis_sec_group.security_group_id],
        )

        cdk.CfnOutput(
            stack,
            id="CacheClusterId",
            value=redis_cluster.cluster_name,
        )
        cdk.CfnOutput(
            stack,
            id="CacheClusterAddress",
            value=redis_cluster.attr_redis_endpoint_address,
        )
        cdk.CfnOutput(
            stack,
            id="CacheClusterPort",
            value=redis_cluster.attr_redis_endpoint_port,
        )

        infra.add_cdk_stack(stack)

        with infra.provisioner() as prov:
            yield prov

    @markers.aws.only_localstack
    @pytest.mark.skip(reason="fails with old elasticache provider")
    def test_redis_endpoint(self, infrastructure, aws_client):
        outputs = infrastructure.get_stack_outputs(self.stack_name)
        assert outputs["CacheClusterAddress"] == "localhost.localstack.cloud"
        assert int(outputs["CacheClusterPort"]) in external_service_ports.as_range()

    @markers.aws.needs_fixing
    # TODO: need a way to test cluster configurations in AWS
    def test_redis_connection(self, infrastructure, aws_client):
        outputs = infrastructure.get_stack_outputs(self.stack_name)

        host = outputs["CacheClusterAddress"]
        port = int(outputs["CacheClusterPort"])
        with redis.Redis(host, port, decode_responses=True) as rds:
            assert rds.ping(), "redis cluster not available"
            rds.set("localstack", "is cool")
            assert rds.get("localstack") == "is cool"

            with pytest.raises(redis.ResponseError) as e:
                assert rds.cluster("nodes")

            e.match("This instance has cluster support disabled")


class TestReplicationGroupNonCluster:
    # TODO: need a way to test cluster configurations in AWS. currently this was only tested manually through
    #  an EC2 tunnel

    stack_name = "TestReplicationGroupNonClusterStack"
    num_cache_clusters = 3

    @pytest.fixture(scope="class", autouse=True)
    def infrastructure(self, aws_client, infrastructure_setup):
        infra = infrastructure_setup("elasticache-replication-group-non-cluster-test")

        app = cdk.App()
        stack = RedisVpcStack(app, self.stack_name)

        replication_group_id = f"redis-replication-group-{short_uid()}"
        replication_group = elasticache.CfnReplicationGroup(
            stack,
            id="ReplicationGroup",
            replication_group_id=replication_group_id,
            replication_group_description="testing replication group",
            engine="redis",
            cache_node_type="cache.t2.micro",
            num_cache_clusters=self.num_cache_clusters,
            cache_subnet_group_name=stack.redis_subnet_group.ref,
            security_group_ids=[stack.redis_sec_group.security_group_id],
        )

        cdk.CfnOutput(
            stack,
            id="ReplicationGroupId",
            value=replication_group.replication_group_id,
        )

        cdk.CfnOutput(
            stack,
            id="PrimaryEndpointAddress",
            value=replication_group.attr_primary_end_point_address,
        )
        cdk.CfnOutput(
            stack,
            id="PrimaryEndpointPort",
            value=replication_group.attr_primary_end_point_port,
        )
        cdk.CfnOutput(
            stack,
            id="ReadEndpointPorts",
            value=replication_group.attr_read_end_point_ports,
        )
        cdk.CfnOutput(
            stack,
            id="ReadEndpointAddresses",
            value=replication_group.attr_read_end_point_addresses,
        )

        infra.add_cdk_stack(stack)

        with infra.provisioner() as prov:
            yield prov

    def parse_endpoints_from_output(self, outputs) -> list[tuple[str, int]]:
        raw_addresses = outputs["ReadEndpointAddresses"][1:-1]
        raw_ports = outputs["ReadEndpointPorts"][1:-1]

        addresses = [a for a in raw_addresses.split(", ")] if raw_addresses else []
        ports = [int(p) for p in raw_ports.split(", ")] if raw_ports else []

        return list(zip(addresses, ports))

    @markers.aws.needs_fixing
    @pytest.mark.skip(
        reason="fails with old elasticache provider because of 'CLUSTERDOWN Hash slot not served'"
    )
    def test_redis_primary_endpoint(self, infrastructure, aws_client):
        outputs = infrastructure.get_stack_outputs(self.stack_name)
        host, port = outputs["PrimaryEndpointAddress"], int(outputs["PrimaryEndpointPort"])

        with redis.Redis(host, port, decode_responses=True) as rds:
            assert rds.ping(), f"{host}:{port} was not pingable"
            rds.set("foo", "bar")

    @markers.aws.needs_fixing
    @pytest.mark.skip(
        reason="fails with old elasticache provider because the cluster isn't created correctly"
    )
    def test_redis_topology(self, infrastructure, aws_client):
        outputs = infrastructure.get_stack_outputs(self.stack_name)

        endpoints = self.parse_endpoints_from_output(outputs)
        primary = outputs["PrimaryEndpointAddress"], int(outputs["PrimaryEndpointPort"])

        assert len(endpoints) == self.num_cache_clusters
        # make sure the three endpoints are distinct
        assert (
            len(set(endpoints)) == self.num_cache_clusters
        ), f"expected distinct endpoints in {endpoints}"

        # check that all nodes are up
        for host, port in endpoints:
            with redis.Redis(host, port) as rds:
                assert rds.ping(), f"{host}:{port} was not pingable"

        # check that all others are replicas
        for endpoint in endpoints:
            if endpoint == primary:
                continue
            else:
                with redis.Redis(endpoint[0], endpoint[1], decode_responses=True) as rds:
                    assert rds.role()[0] == "slave"

        def _check_is_master():
            # check the primary role
            with redis.Redis(primary[0], primary[1], decode_responses=True) as rds:
                role, offset, replicas = rds.role()
                assert role == "master"
                assert len(replicas) == len(endpoints) - 1

        # initial replication registration may take a while one localstack
        retry(_check_is_master, retries=30, sleep=1)


@pytest.mark.skip(reason="fails with old elasticache provider")
class TestReplicationGroupCluster:
    stack_name = "TestReplicationGroupClusterStack"
    num_node_groups = 2
    replicas_per_node_group = 3

    @pytest.fixture(scope="class", autouse=True)
    def infrastructure(self, aws_client, infrastructure_setup):
        infra = infrastructure_setup("elasticache-replication-group-cluster-test")

        app = cdk.App()
        stack = RedisVpcStack(app, self.stack_name)

        replication_group_id = f"redis-replication-group-{short_uid()}"
        replication_group = elasticache.CfnReplicationGroup(
            stack,
            id="ReplicationGroup",
            replication_group_id=replication_group_id,
            replication_group_description="testing replication group",
            engine="redis",
            cache_node_type="cache.t2.micro",
            num_node_groups=self.num_node_groups,
            replicas_per_node_group=self.replicas_per_node_group,
            cache_subnet_group_name=stack.redis_subnet_group.ref,
            security_group_ids=[stack.redis_sec_group.security_group_id],
        )

        cdk.CfnOutput(
            stack,
            id="ReplicationGroupId",
            value=replication_group.replication_group_id,
        )
        cdk.CfnOutput(
            stack,
            id="ConfigurationEndpointPort",
            value=replication_group.attr_configuration_end_point_port,
        )
        cdk.CfnOutput(
            stack,
            id="ConfigurationEndpointAddress",
            value=replication_group.attr_configuration_end_point_address,
        )

        infra.add_cdk_stack(stack)

        with infra.provisioner() as prov:
            yield prov

    @markers.aws.needs_fixing
    def test_redis_configuration_endpoint(self, infrastructure, aws_client):
        outputs = infrastructure.get_stack_outputs(self.stack_name)
        host = outputs["ConfigurationEndpointAddress"]
        port = int(outputs["ConfigurationEndpointPort"])

        with redis.Redis(host, port, decode_responses=True) as rds:
            assert rds.ping(), f"{host}:{port} was not pingable"

    @markers.aws.needs_fixing
    def test_redis_topology(self, infrastructure, aws_client):
        outputs = infrastructure.get_stack_outputs(self.stack_name)
        host = outputs["ConfigurationEndpointAddress"]
        port = int(outputs["ConfigurationEndpointPort"])

        def _wait_for_topology():
            with redis.Redis(host, port, decode_responses=True) as rds:
                nodes = rds.cluster("nodes")

            masters = []
            replicas = []

            for host_port, node_info in nodes.items():
                if "master" in node_info["flags"]:
                    masters.append(node_info)
                else:
                    replicas.append(node_info)

            assert len(masters) == self.num_node_groups, f"invalid cluster topology {nodes}"
            assert (
                len(replicas) == self.num_node_groups * self.replicas_per_node_group
            ), f"invalid cluster topology {nodes}"

            return nodes

        nodes = retry(_wait_for_topology, retries=15)

        # check that all assigned ports are in the service port range.
        for node_ip_port in nodes.keys():
            assert int(node_ip_port.split(":")[-1]) in external_service_ports.as_range()

    @markers.aws.needs_fixing
    def test_redis_cluster_mode(self, infrastructure, aws_client):
        outputs = infrastructure.get_stack_outputs(self.stack_name)
        host = outputs["ConfigurationEndpointAddress"]
        port = int(outputs["ConfigurationEndpointPort"])

        def _wait_for_topology():
            with redis.RedisCluster(host, port) as rds:
                slots = rds.cluster_slots()
                assert len(slots) == self.num_node_groups, f"invalid cluster slots {slots}"

        retry(_wait_for_topology, retries=10)

        # TODO: check that slots work correctly
        with redis.RedisCluster(host, port, decode_responses=True) as rds:
            rds.set("foo", "bar")

        with redis.RedisCluster(host, port, decode_responses=True) as rds:
            assert rds.get("foo") == "bar"
