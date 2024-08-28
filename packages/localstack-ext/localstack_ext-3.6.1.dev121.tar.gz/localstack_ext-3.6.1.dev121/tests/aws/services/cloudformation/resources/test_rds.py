import os

import pytest
from localstack.testing.aws.util import is_aws_cloud
from localstack.testing.pytest import markers
from localstack.utils.strings import short_uid


@markers.aws.validated
@markers.snapshot.skip_snapshot_verify(paths=["$..DbAddress"])
def test_db_instance_deployment(deploy_cfn_template, snapshot, aws_client):
    stack = deploy_cfn_template(
        template_path=os.path.join(os.path.dirname(__file__), "../../../templates/rds.yml"),
        max_wait=1200 if is_aws_cloud() else 200,
    )

    snapshot.add_transformer(snapshot.transform.key_value("DbRef", "db-identifier"))
    snapshot.add_transformer(snapshot.transform.key_value("DbPort", "db-port"))
    snapshot.add_transformer(snapshot.transform.key_value("DbAddress", "db-address"))
    snapshot.match("db_instance_atts", stack.outputs)

    snapshot.add_transformer(snapshot.transform.cloudformation_api())
    description = aws_client.cloudformation.describe_stack_resources(StackName=stack.stack_name)[
        "StackResources"
    ][0]
    snapshot.match("db_resource_description", description)


@markers.aws.validated
@pytest.mark.parametrize("template_name", ["rds_cluster.yml", "rds_serverless_cluster.yml"])
def test_db_cluster_deployment(template_name, deploy_cfn_template, snapshot, aws_client):
    stack = deploy_cfn_template(
        template_path=os.path.join(os.path.dirname(__file__), "../../../templates/", template_name),
        max_wait=1200 if is_aws_cloud() else 200,
        parameters={"DatabaseName": f"test{short_uid()}"},
    )

    snapshot.add_transformer(snapshot.transform.key_value("EndpointAddress", "db-address", False))
    snapshot.add_transformer(
        snapshot.transform.key_value("ReadEndpointAddress", "read-address", False)
    )
    snapshot.add_transformer(snapshot.transform.key_value("DBClusterIdentifier", "db-identifier"))
    snapshot.add_transformer(snapshot.transform.key_value("EndpointPort", "db-port"))
    snapshot.match("db_instance_atts", stack.outputs)

    snapshot.add_transformer(snapshot.transform.cloudformation_api())
    description = aws_client.cloudformation.describe_stack_resources(StackName=stack.stack_name)[
        "StackResources"
    ][0]
    snapshot.match("db_resource_description", description)


@markers.aws.unknown
def test_db_proxy(deploy_cfn_template, aws_client):
    # TODO the test is not yet AWS validated because of config issues on AWS (probably related to security groups)
    #   the deployment fails, proxy target group stays in 'unavailable'
    db_id = f"db-{short_uid()}"
    proxy_name = f"proxy-{short_uid()}"
    param_group = f"db-group-{short_uid()}"
    deploy_cfn_template(
        template_path=os.path.join(os.path.dirname(__file__), "../../../templates/rds_proxy.yml"),
        max_wait=1200 if is_aws_cloud() else 200,
        parameters={
            "DatabaseIdentifier": db_id,
            "ProxyName": proxy_name,
            "DBParameterGroupName": param_group,
        },
    )
    result = aws_client.rds.describe_db_instances(DBInstanceIdentifier=db_id)
    db_instance = result["DBInstances"][0]
    assert db_instance["DBParameterGroups"][0]["DBParameterGroupName"] == param_group
    endpoint = f"{db_instance['Endpoint']['Address']}:{db_instance['Endpoint']['Port']}"

    result = aws_client.rds.describe_db_proxies(DBProxyName=proxy_name)
    db_proxy = result["DBProxies"][0]
    assert db_proxy["Endpoint"] == endpoint
    assert db_proxy["Status"] == "available"

    result = aws_client.rds.describe_db_proxy_targets(
        DBProxyName=proxy_name, TargetGroupName="default"
    )
    proxy_target = result["Targets"][0]
    assert proxy_target["Endpoint"] == db_instance["Endpoint"]["Address"]
    assert proxy_target["Port"] == db_instance["Endpoint"]["Port"]
    assert proxy_target["Type"] == "RDS_INSTANCE"


@markers.aws.validated
def test_rds_cluster_with_kms(deploy_cfn_template, snapshot, aws_client):
    stack = deploy_cfn_template(
        template_path=os.path.join(
            os.path.dirname(__file__), "../../../templates/rds_cluster_with_kms.yml"
        ),
    )
    snapshot.add_transformer(snapshot.transform.key_value("DBClusterIdentifier"))
    snapshot.add_transformer(snapshot.transform.key_value("ClusterSecretArn"))
    snapshot.add_transformer(snapshot.transform.key_value("KMSKeyArn"))
    snapshot.match("db_cluster_with_secret_arn", stack.outputs)


@markers.aws.validated
def test_parameter_group_creation(deploy_cfn_template, snapshot, aws_client):
    stack = deploy_cfn_template(
        template_path=os.path.join(
            os.path.dirname(__file__), "../../../templates/rds_db_parameter_group.yml"
        ),
    )
    snapshot.add_transformer(snapshot.transform.cloudformation_api())
    description = aws_client.cloudformation.describe_stack_resources(StackName=stack.stack_name)[
        "StackResources"
    ][0]
    snapshot.match("db_parameter_group_description", description)


@markers.aws.validated
def test_cluster_parameter_group_creation(deploy_cfn_template, snapshot, aws_client):
    stack = deploy_cfn_template(
        template_path=os.path.join(
            os.path.dirname(__file__), "../../../templates/rds_cluster_db_parameter_group.yml"
        ),
    )
    snapshot.add_transformer(snapshot.transform.cloudformation_api())
    description = aws_client.cloudformation.describe_stack_resources(StackName=stack.stack_name)[
        "StackResources"
    ][0]
    snapshot.match("db_cluster_parameter_group_description", description)
    parameter_group = aws_client.rds.describe_db_cluster_parameter_groups(
        DBClusterParameterGroupName="testgroup"
    )
    snapshot.match("describe_db_cluster_parameter_group", parameter_group)
    parameters = aws_client.rds.describe_db_cluster_parameters(
        DBClusterParameterGroupName="testgroup", Source="user"
    )["Parameters"]
    parameters = {
        parameter["ParameterName"]: parameter["ParameterValue"] for parameter in parameters
    }
    snapshot.match("describe_db_cluster_parameters", parameters)
