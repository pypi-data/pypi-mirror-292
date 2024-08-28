import aws_cdk as cdk
import pytest
from localstack.testing.pytest import markers


class TestCfnRedshiftSubnet:
    STACK_NAME = "CfnRedshiftSubnetTestStack"

    @pytest.fixture(scope="class", autouse=True)
    def infrastructure(self, infrastructure_setup, aws_client):
        infra = infrastructure_setup(namespace="CfnRedshiftSubnetTest", force_synth=False)
        stack = cdk.Stack(infra.cdk_app, self.STACK_NAME)

        # TODO: add a test that covers cluster security group
        #   didn't yet manage to write a sample with a cluster security group due to some cryptic error messages
        # cluster cecurity groups apparently are the legacy way to limit access, newer architectures should use EC2 primitives
        # cluster_security_group = cdk.aws_redshift.CfnClusterSecurityGroup(stack, "ClusterSecurityGroup", description="desc security group")

        vpc = cdk.aws_ec2.Vpc(stack, "Vpc", cidr="10.0.0.0/16")
        cluster_parameter_group = cdk.aws_redshift.CfnClusterParameterGroup(
            stack,
            "ClusterParameterGroup",
            parameter_group_family="redshift-1.0",
            description="desc for cluster parameters",
        )

        cluster_subnet_group = cdk.aws_redshift.CfnClusterSubnetGroup(
            stack,
            "ClusterSubnetGroup",
            subnet_ids=vpc.select_subnets(
                subnet_type=cdk.aws_ec2.SubnetType.PRIVATE_WITH_NAT
            ).subnet_ids,
            description="desc subnet group",
        )

        cluster = cdk.aws_redshift.CfnCluster(
            stack,
            "Cluster",
            db_name="initialdb",
            master_username="admin",
            master_user_password="someweird123Password",
            node_type="dc2.large",
            cluster_type="single-node",
            cluster_parameter_group_name=cluster_parameter_group.ref,
            cluster_subnet_group_name=cluster_subnet_group.ref,
        )

        cdk.CfnOutput(stack, "ClusterRef", value=cluster.ref)
        cdk.CfnOutput(stack, "ClusterParameterGroupRef", value=cluster_parameter_group.ref)
        cdk.CfnOutput(stack, "ClusterSubnetGroupRef", value=cluster_subnet_group.ref)
        cdk.CfnOutput(
            stack,
            "ClusterSubnetGroupAttSubnetGroupName",
            value=cluster_subnet_group.attr_cluster_subnet_group_name,
        )

        with infra.provisioner(skip_deployment=False, skip_teardown=False) as prov:
            yield prov

    @markers.aws.validated
    def test_docdb_resources(self, infrastructure, aws_client):
        outputs = infrastructure.get_stack_outputs(self.STACK_NAME)
        cluster_ref = outputs["ClusterRef"]
        param_group_ref = outputs["ClusterParameterGroupRef"]
        cluster_subnet_ref = outputs["ClusterSubnetGroupRef"]
        cluster_subnet_name = outputs["ClusterSubnetGroupAttSubnetGroupName"]

        assert cluster_subnet_ref == cluster_subnet_name

        clusters = aws_client.redshift.describe_clusters(ClusterIdentifier=cluster_ref)
        assert clusters["Clusters"][0]["ClusterSubnetGroupName"] == cluster_subnet_ref
        assert (
            clusters["Clusters"][0]["ClusterParameterGroups"][0]["ParameterGroupName"]
            == param_group_ref
        )
