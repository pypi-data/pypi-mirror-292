import os

from localstack.testing.aws.util import is_aws_cloud
from localstack.testing.pytest import markers
from localstack.utils.strings import short_uid
from localstack_snapshot.snapshots.transformer import SortingTransformer

from tests.aws.services.cloudformation.utils import load_template


@markers.aws.validated
def test_vpc_cidr_block_configurations(deploy_cfn_template, aws_client):
    stack = deploy_cfn_template(
        template_path=os.path.join(
            os.path.dirname(__file__), "../../../templates/ec2.vpccidrblockconfigurations.yaml"
        )
    )

    vpc_id = stack.outputs["VpcId"]
    vpc_cidr_block = stack.outputs["PrimaryCidrBlock"]
    vpc_cidr_block_association_id = stack.outputs["CidrBlockAssociation"]

    vpc_config = aws_client.ec2.describe_vpcs()["Vpcs"]
    assert vpc_id in [item["VpcId"] for item in vpc_config]
    assert vpc_cidr_block in [item["CidrBlock"] for item in vpc_config]

    vpc_cidr_block_association_set = [
        item["CidrBlockAssociationSet"] for item in vpc_config if item["VpcId"] == vpc_id
    ][0]

    assert vpc_cidr_block_association_id in [
        item["AssociationId"] for item in vpc_cidr_block_association_set
    ]


@markers.aws.validated
def test_security_group_ingress_creation(deploy_cfn_template, aws_client):
    group_name = f"g-{short_uid()}"
    template_rendered = load_template("ec2.sg.ingress.yaml")

    stack = deploy_cfn_template(template=template_rendered, parameters={"GroupName": group_name})

    groups = aws_client.ec2.describe_security_groups(
        Filters=[{"Name": "group-name", "Values": [group_name]}]
    )["SecurityGroups"]
    assert len(groups) == 1
    ip_perms = groups[0]["IpPermissions"][0]
    assert ip_perms["IpProtocol"] == "-1"
    assert ip_perms["IpRanges"] == [{"CidrIp": "10.70.0.0/20"}]

    stack.destroy()
    result_postdestroy = aws_client.ec2.describe_security_groups(
        Filters=[{"Name": "group-name", "Values": [group_name]}]
    )
    assert result_postdestroy["SecurityGroups"] == []


@markers.aws.validated
def test_security_group_ingress_creation_isolation(deploy_cfn_template, aws_client, cleanups):
    group_name = f"g-{short_uid()}"
    template_rendered = load_template("ec2.sg.ingress.isolation.yaml")

    vpc = aws_client.ec2.create_vpc(CidrBlock="10.0.0.0/20")
    vpc_id = vpc["Vpc"]["VpcId"]
    cleanups.append(lambda: aws_client.ec2.delete_vpc(VpcId=vpc_id))
    sg = aws_client.ec2.create_security_group(
        VpcId=vpc_id, GroupName=group_name, Description="Testing group"
    )
    cleanups.append(lambda: aws_client.ec2.delete_security_group(GroupId=sg["GroupId"]))

    stack = deploy_cfn_template(
        template=template_rendered, parameters={"SecurityGroupId": sg["GroupId"]}
    )

    ref = stack.outputs["SecurityGroupIngressRef"]
    assert ref.startswith("sgr-")

    groups = aws_client.ec2.describe_security_groups(
        Filters=[{"Name": "group-name", "Values": [group_name]}]
    )["SecurityGroups"]
    assert len(groups) == 1
    sg = groups[0]
    ip_perms = sg["IpPermissions"][0]
    assert ip_perms["IpProtocol"] == "-1"
    assert ip_perms["IpRanges"] == [{"CidrIp": "10.70.0.0/20"}]

    # FIXME (returns length of 4). Seems the filtering via SecurityGroupRuleIds isn't working correctly
    sgr = aws_client.ec2.describe_security_group_rules(SecurityGroupRuleIds=[ref])
    sg_rules = [r for r in sgr["SecurityGroupRules"] if r["SecurityGroupRuleId"] == ref]
    assert len(sg_rules) == 1
    assert sg_rules[0]["SecurityGroupRuleId"] == ref

    stack.destroy()

    result_postdestroy = aws_client.ec2.describe_security_groups(
        Filters=[{"Name": "group-name", "Values": [group_name]}]
    )
    sg = result_postdestroy["SecurityGroups"][0]
    assert sg["IpPermissions"] == []

    # FIXME (missing filtering in moto) see other FIXME above
    # with pytest.raises(aws_client.ec2.exceptions.ClientError):
    #     # deleted, so we can't find it anymore
    #     aws_client.ec2.describe_security_group_rules(SecurityGroupRuleIds=[ref])


@markers.aws.validated
@markers.snapshot.skip_snapshot_verify(
    paths=[
        "$..CreatedBy",
        "$..LaunchTemplateId",
        "$..LaunchTemplateName",
        "$..PhysicalResourceId",
        "$..Tags",
        "$..StackId",
        "$..StackName",
    ]
)
def test_ec2_launch_template(deploy_cfn_template, aws_client, snapshot):
    template = load_template("ec2.launchtemplate.yaml")
    stack = deploy_cfn_template(template=template)
    launch_template_id = stack.outputs["LaunchTemplateId"]

    launch_templates = aws_client.ec2.describe_launch_templates(
        LaunchTemplateIds=[launch_template_id]
    )["LaunchTemplates"]
    snapshot.match("launch_templates", launch_templates)

    describe_resource_result = aws_client.cloudformation.describe_stack_resources(
        StackName=stack.stack_name, LogicalResourceId="LaunchTemplate"
    )
    # for the information of the implementer
    snapshot.match(
        "describe_resource_result",
        describe_resource_result["StackResources"][0],
    )


@markers.aws.validated
def test_vpc_endpoint_service_configurations(deploy_cfn_template, aws_client):
    template = load_template("ec2.vpcendpointserviceconfigurations.yaml")
    stack = deploy_cfn_template(template=template, max_wait=300 if is_aws_cloud() else None)

    vpc_endpoint_id = stack.outputs["VPCEndpointId"]
    nlb_arn = stack.outputs["NLBArn"]

    vpc_endpoint_service_configurations = (
        aws_client.ec2.describe_vpc_endpoint_service_configurations()
    )
    assert len(vpc_endpoint_service_configurations["ServiceConfigurations"]) == 1
    assert (
        vpc_endpoint_service_configurations["ServiceConfigurations"][0]["ServiceId"]
        == vpc_endpoint_id
    )
    assert (
        vpc_endpoint_service_configurations["ServiceConfigurations"][0]["NetworkLoadBalancerArns"][
            0
        ]
        == nlb_arn
    )


@markers.aws.validated
def test_deploy_duplicate_security_group(deploy_cfn_template, aws_client, snapshot):
    """
    Tests what happens when the specified security group rule is a duplicate of an existing one (in this case the default)

    It seems it takes on the security group rule ID from the existing one (TODO: verify), so what happens if that is deleted? (TODO: test)
    """
    stack = deploy_cfn_template(
        template_path=os.path.join(
            os.path.dirname(__file__), "../../../templates/duplicated_security_group.yml"
        )
    )

    describe_resource_result = aws_client.cloudformation.describe_stack_resources(
        StackName=stack.stack_name
    )

    snapshot.add_transformer(SortingTransformer("StackResources", lambda x: x["LogicalResourceId"]))
    snapshot.add_transformer(
        snapshot.transform.key_value("PhysicalResourceId", "physical-resource-id")
    )
    snapshot.add_transformer(snapshot.transform.cloudformation_api())
    snapshot.match(
        "describe_resource_result",
        describe_resource_result,
    )
