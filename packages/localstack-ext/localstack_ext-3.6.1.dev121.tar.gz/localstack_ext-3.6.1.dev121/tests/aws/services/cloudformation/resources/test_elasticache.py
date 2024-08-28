import os

import aws_cdk as cdk
import pytest
from localstack.testing.aws.util import is_aws_cloud
from localstack.testing.pytest import markers
from localstack.utils.strings import short_uid


@markers.aws.validated
@pytest.mark.parametrize("engine", ["redis"])  # TODO add memcache when is supported
@markers.snapshot.skip_snapshot_verify(
    paths=[
        "$..PhysicalResourceId",
        "$..CacheClusters",
    ]
)
def test_cache_cluster(engine, deploy_cfn_template, snapshot, aws_client):
    snapshot.add_transformer(snapshot.transform.key_value("CacheRef", "cache-ref"))
    snapshot.add_transformer(snapshot.transform.cloudformation_api())

    cluster_name = f"cluster-{short_uid()}"
    template_path = os.path.join(
        os.path.dirname(__file__), "../../../templates/elasticache_cache_cluster.yml"
    )
    stack = deploy_cfn_template(
        stack_name=f"stack-{engine}-{short_uid()}",
        template_path=template_path,
        parameters={"Engine": engine, "ClusterName": cluster_name},
        max_wait=2000 if is_aws_cloud() else None,
    )
    snapshot.match("stack_outputs", stack.outputs)

    description = aws_client.cloudformation.describe_stack_resources(StackName=stack.stack_name)
    resource = [
        res for res in description["StackResources"] if res["LogicalResourceId"] == "myCacheCluster"
    ][0]
    snapshot.match("stack_resource_description", resource)

    cluster = aws_client.elasticache.describe_cache_clusters(CacheClusterId=cluster_name)
    snapshot.match("cluster", cluster)


@markers.aws.validated
def test_cluster_with_replication(deploy_cfn_template, aws_client, snapshot):
    groups_before = aws_client.elasticache.describe_cache_parameter_groups().get(
        "CacheParameterGroups", []
    )

    # create stack
    stack_name = f"stack-{short_uid()}"
    group_id = f"g-{short_uid()}"
    cluster_id = f"c-{short_uid()}"
    deployment = deploy_cfn_template(
        template_path=os.path.join(
            os.path.dirname(__file__), "../../../templates/elasticache-cluster.yaml"
        ),
        stack_name=stack_name,
        parameters={"ClusterNameParam": cluster_id, "ReplicationGroupIdParam": group_id},
        max_wait=3500 if is_aws_cloud() else None,
    )

    snapshot.add_transformer(
        snapshot.transform.key_value("ClusterAddress", "cluster-address", False)
    )
    snapshot.add_transformer(snapshot.transform.key_value("ClusterPort", "cluster-port", False))
    snapshot.add_transformer(
        snapshot.transform.key_value("ReplicationGroupAddress", "replication-address", False)
    )
    snapshot.add_transformer(
        snapshot.transform.key_value("ReplicationGroupPort", "replication-port", False)
    )
    snapshot.match("elasticache-cluster", deployment.outputs)

    def _clusters():
        clusters = aws_client.elasticache.describe_cache_clusters()["CacheClusters"]
        clusters = [
            c
            for c in clusters
            if c["CacheClusterId"] == cluster_id or c["CacheClusterId"].startswith(f"{group_id}-")
        ]
        return clusters

    # assert cache clusters have been created
    assert len(_clusters()) == 4

    # assert cluster parameter group has been created
    groups = aws_client.elasticache.describe_cache_parameter_groups().get(
        "CacheParameterGroups", []
    )
    assert len(groups_before) + 1 == len(groups)

    deployment.destroy()

    # delete stack, assert clusters have been deleted
    assert len(_clusters()) == 0


class TestElasticacheResources:
    @pytest.fixture(scope="class", autouse=True)
    def infrastructure(self, infrastructure_setup):
        infra = infrastructure_setup("CfnResourcesElastiCache", force_synth=False)

        stack = cdk.Stack(infra.cdk_app, "CfnResourcesElastiCacheStack")
        vpc = cdk.aws_ec2.CfnVPC(
            stack,
            "vpc",
            cidr_block="10.0.0.0/16",
            enable_dns_support=True,
            enable_dns_hostnames=True,
        )
        subnet = cdk.aws_ec2.CfnSubnet(
            stack,
            "Subnet",
            vpc_id=vpc.ref,
            availability_zone=cdk.Fn.select(0, stack.availability_zones),
            cidr_block="10.0.0.0/24",
            map_public_ip_on_launch=False,
        )
        sec_group = cdk.aws_ec2.CfnSecurityGroup(
            stack,
            "Ec2SecurityGroup",
            vpc_id=vpc.ref,
            group_description="security group description",
            security_group_ingress=[
                cdk.aws_ec2.CfnSecurityGroup.IngressProperty(
                    ip_protocol="tcp", from_port=11211, to_port=11211
                )
            ],
        )

        subnet_group = cdk.aws_elasticache.CfnSubnetGroup(
            stack,
            "SubnetGroup",
            subnet_ids=[subnet.ref],
            tags=[cdk.CfnTag(key="k1", value="v1")],
            description="subnet description",
        )
        security_group = cdk.aws_elasticache.CfnSecurityGroup(
            stack,
            "SecurityGroup",
            description="test group",
            tags=[cdk.CfnTag(key="k1", value="v1")],
        )
        cache_cluster = cdk.aws_elasticache.CfnCacheCluster(
            stack,
            "CacheCluster",
            auto_minor_version_upgrade=True,
            engine="redis",
            cache_node_type="cache.t2.micro",
            num_cache_nodes=1,
            cache_subnet_group_name=subnet_group.ref,
            vpc_security_group_ids=[sec_group.attr_group_id],
        )
        # replication_group = cdk.aws_elasticache.CfnReplicationGroup(
        #     stack,
        #     "ReplicationGroup",
        #     replication_group_description="desc",
        #     engine="redis",
        #     cache_node_type="cache.t2.micro",
        #     num_cache_clusters=3,
        #     cache_subnet_group_name=subnet_group.ref,
        #     tags=[cdk.CfnTag(key="k1", value="v1")]
        # )

        parameter_group = cdk.aws_elasticache.CfnParameterGroup(
            stack,
            "ParameterGroup",
            cache_parameter_group_family="memcached1.4",
            description="test desc 1",
            properties={"cas_disabled": "1"},
            tags=[cdk.CfnTag(key="k1", value="v1")],
        )

        cdk.CfnOutput(stack, "CacheClusterRef", value=cache_cluster.ref)
        # only for non-redis
        # cdk.CfnOutput(stack, "CacheClusterAttConfigurationEndpointAddress", value=cache_cluster.attr_configuration_endpoint_address)
        # cdk.CfnOutput(stack, "CacheClusterAttConfigurationEndpointPort", value=cache_cluster.attr_configuration_endpoint_port)
        cdk.CfnOutput(
            stack,
            "CacheClusterAttRedisEndpointAddress",
            value=cache_cluster.attr_redis_endpoint_address,
        )
        cdk.CfnOutput(
            stack, "CacheClusterAttRedisEndpointPort", value=cache_cluster.attr_redis_endpoint_port
        )

        # TODO: can be extended at some point with all below, for now kept it simple since the replication group takes a long time to deploy
        # cdk.CfnOutput(stack, "ReplicationGroupRef", value=replication_group.ref)
        # cdk.CfnOutput(stack, "ReplicationGroupAttReadEndpointPorts", value=replication_group.attr_read_end_point_ports)
        # cdk.CfnOutput(stack, "ReplicationGroupAttReadEndpointAddresses", value=replication_group.attr_read_end_point_addresses)
        # cdk.CfnOutput(stack, "ReplicationGroupAttReadEndpointAddressesList", value=cdk.Fn.join("|", replication_group.attr_read_end_point_addresses_list))
        # cdk.CfnOutput(stack, "ReplicationGroupAttReaderEndpointPort", value=replication_group.attr_reader_end_point_port)
        # cdk.CfnOutput(stack, "ReplicationGroupAttReaderEndpointAddress", value=replication_group.attr_reader_end_point_address)
        # cdk.CfnOutput(stack, "ReplicationGroupAttConfigurationEndpointPort", value=replication_group.attr_configuration_end_point_port)
        # cdk.CfnOutput(stack, "ReplicationGroupAttConfigurationEndpointAddress", value=replication_group.attr_configuration_end_point_address)
        # cdk.CfnOutput(stack, "ReplicationGroupAttPrimaryEndpointPort", value=replication_group.attr_primary_end_point_port)
        # cdk.CfnOutput(stack, "ReplicationGroupAttPrimaryEndpointAddress", value=replication_group.attr_primary_end_point_address)

        cdk.CfnOutput(stack, "SecurityGroupRef", value=security_group.ref)
        cdk.CfnOutput(stack, "ParameterGroupRef", value=parameter_group.ref)
        cdk.CfnOutput(stack, "SubnetGroupRef", value=subnet_group.ref)

        with infra.provisioner(skip_teardown=False) as prov:
            yield prov

    @markers.aws.validated
    def test_resource_deployment(self, infrastructure, aws_client, snapshot):
        outputs = infrastructure.get_stack_outputs("CfnResourcesElastiCacheStack")
        snapshot.match("outputs", outputs)
        snapshot.add_transformer(snapshot.transform.key_value("CacheClusterRef"))
        snapshot.add_transformer(
            snapshot.transform.key_value("CacheClusterAttRedisEndpointAddress"), priority=-1
        )
        snapshot.add_transformer(snapshot.transform.key_value("CacheClusterAttRedisEndpointPort"))
        snapshot.add_transformer(snapshot.transform.key_value("SecurityGroupRef"))
        snapshot.add_transformer(snapshot.transform.key_value("ParameterGroupRef"))
        snapshot.add_transformer(snapshot.transform.key_value("SubnetGroupRef"))

        # TODO: extend at some point, for now we mostly care about it being up and outputs resolving
        cache_cluster_id = outputs["CacheClusterRef"]
        aws_client.elasticache.describe_cache_clusters(CacheClusterId=cache_cluster_id)
