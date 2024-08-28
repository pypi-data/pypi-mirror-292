import aws_cdk as cdk
import pytest
from localstack.testing.pytest import markers


class TestCfnDocDbResources:
    STACK_NAME = "DocDBTestStack"

    @pytest.fixture(scope="class", autouse=True)
    def infrastructure(self, infrastructure_setup, aws_client):
        infra = infrastructure_setup(namespace="CfnDocDBTest", force_synth=False)
        stack = cdk.Stack(infra.cdk_app, self.STACK_NAME)

        db_param_group_name = cdk.aws_docdb.CfnDBClusterParameterGroup(
            stack,
            "DBClusterParams",
            family="docdb5.0",
            description="test parameter group",
            parameters={"audit_logs": "disabled", "profiler_sampling_rate": 0.5},
        )
        db_cluster = cdk.aws_docdb.CfnDBCluster(
            stack,
            "DBCluster",
            db_cluster_identifier=cdk.Fn.join("-", [stack.stack_name, "clusterid"]),
            master_username="test",
            master_user_password="test123test123",
            deletion_protection=False,
            db_cluster_parameter_group_name=db_param_group_name.ref,
        )

        cdk.CfnOutput(stack, "DbClusterRef", value=db_cluster.ref)
        # NOTE: this isn't actually supported and will result in a failure!
        # cdk.CfnOutput(stack, "DbClusterId", value=db_cluster.attr_id)
        cdk.CfnOutput(
            stack, "DbClusterClusterResourceId", value=db_cluster.attr_cluster_resource_id
        )
        cdk.CfnOutput(stack, "DbClusterPort", value=db_cluster.attr_port)
        cdk.CfnOutput(stack, "DbClusterEndpoint", value=db_cluster.attr_endpoint)
        cdk.CfnOutput(stack, "DbClusterReadEndpoint", value=db_cluster.attr_read_endpoint)
        cdk.CfnOutput(stack, "DbParamGroupRef", value=db_param_group_name.ref)
        # same here, also not supported!
        # cdk.CfnOutput(stack, "DbParamGroupId", value=db_param_group_name.attr_id)

        with infra.provisioner(skip_deployment=False, skip_teardown=False) as prov:
            yield prov

    @markers.aws.validated
    def test_docdb_resources(self, infrastructure, aws_client):
        outputs = infrastructure.get_stack_outputs(self.STACK_NAME)
        db_cluster_identifier = outputs["DbClusterRef"]
        db_param_group_name = outputs["DbParamGroupRef"]

        clusters = aws_client.docdb.describe_db_clusters(DBClusterIdentifier=db_cluster_identifier)[
            "DBClusters"
        ]
        cluster = clusters[0]
        assert cluster["Endpoint"] == outputs["DbClusterEndpoint"]
        assert cluster["ReaderEndpoint"] == outputs["DbClusterReadEndpoint"]

        # assert db parameter group created
        param_group_name = cluster.get("DBClusterParameterGroup")
        db_parameter_groups = aws_client.docdb.describe_db_cluster_parameter_groups(
            DBClusterParameterGroupName=param_group_name
        )
        db_parameter_group = db_parameter_groups["DBClusterParameterGroups"][0]
        assert db_parameter_group["DBClusterParameterGroupName"] == db_param_group_name
