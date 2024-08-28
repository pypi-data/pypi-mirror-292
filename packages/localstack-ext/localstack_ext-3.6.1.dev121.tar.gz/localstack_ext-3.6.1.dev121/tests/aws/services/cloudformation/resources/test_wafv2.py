from operator import itemgetter

import aws_cdk as cdk
import pytest
from localstack.testing.pytest import markers
from localstack_snapshot.snapshots.transformer import SortingTransformer

STACK_NAME = "Wafv2Resources-Sample"


def split_id(id: str):
    """
    Converts the Id of WebACL, WebACLAssociation and IPSet into

    Parameters
    ----------
    id

    Returns
    -------
    dict {Name, Id, Scope}

    """
    # Note: id is composed like name|id|scope
    data = id.split("|")
    waf_data = {
        "Name": data[0],
        "Id": data[1],
    }
    if len(data) > 2:
        waf_data["Scope"] = data[2]

    return waf_data


class TestWafV2Resources:
    @pytest.fixture(scope="class", autouse=True)
    def infrastructure(self, infrastructure_setup):
        # create infra provisioner
        infra = infrastructure_setup(namespace="Wafv2Resources")
        stack = cdk.Stack(infra.cdk_app, STACK_NAME)

        api = cdk.aws_apigateway.RestApi(
            stack,
            "Api",
            description="example api gateway",
            endpoint_types=[cdk.aws_apigateway.EndpointType.REGIONAL],
            deploy_options=cdk.aws_apigateway.StageOptions(stage_name="dev"),
        )
        api.root.add_method(
            "GET", method_responses=[cdk.aws_apigateway.MethodResponse(status_code="200")]
        )
        log_group = cdk.aws_logs.CfnLogGroup(stack, "LogGroup", log_group_name="aws-waf-logs-test")

        # create wafv2 resources
        web_acl = cdk.aws_wafv2.CfnWebACL(
            stack,
            "WebACL",
            name="TestWebACL",
            scope="REGIONAL",
            default_action={"allow": {}},
            visibility_config={
                "sampledRequestsEnabled": True,
                "cloudWatchMetricsEnabled": True,
                "metricName": "TestWebACLMetric",
            },
            rules=[],
        )
        web_acl_association = cdk.aws_wafv2.CfnWebACLAssociation(
            stack,
            "WebACLAssociation",
            web_acl_arn=web_acl.attr_arn,
            resource_arn=cdk.Fn.sub(
                "arn:aws:apigateway:${AWS::Region}::/restapis/${Api}/stages/${Stage}",
                {"Api": api.rest_api_id, "Stage": api.deployment_stage.stage_name},
            ),
        )
        ip_set = cdk.aws_wafv2.CfnIPSet(
            stack,
            "IPSet",
            name="test-ip-set",
            scope="REGIONAL",
            ip_address_version="IPV4",
            addresses=["10.0.0.0/8"],
        )
        logging_config = cdk.aws_wafv2.CfnLoggingConfiguration(
            stack,
            "LoggingConfiguration",
            log_destination_configs=[log_group.attr_arn],
            resource_arn=web_acl.attr_arn,
        )

        # outputs
        cdk.CfnOutput(stack, "WebACLRef", value=web_acl.ref)
        cdk.CfnOutput(stack, "WebACLAssociationRef", value=web_acl_association.ref)
        cdk.CfnOutput(stack, "IPSetRef", value=ip_set.ref)
        cdk.CfnOutput(stack, "LoggingConfigurationRef", value=logging_config.ref)  # arn
        cdk.CfnOutput(
            stack,
            "StageRef",
            value=cdk.Fn.sub(
                "arn:aws:apigateway:${AWS::Region}::/restapis/${Api}/stages/${Stage}",
                {"Api": api.rest_api_id, "Stage": api.deployment_stage.stage_name},
            ),
        )
        cdk.CfnOutput(stack, "LogRef", value=log_group.attr_arn)

        with infra.provisioner() as prov:
            yield prov

    @markers.aws.validated
    def test_stack_resources_are_deployed(self, infrastructure, aws_client, snapshot):
        snapshot.add_transformer(
            snapshot.transform.key_value("PhysicalResourceId", reference_replacement=False),
            priority=-1,
        )
        snapshot.add_transformer(snapshot.transform.key_value("StackId"))
        snapshot.add_transformer(
            SortingTransformer("StackResources", itemgetter("LogicalResourceId"))
        )
        resources_description = aws_client.cloudformation.describe_stack_resources(
            StackName=STACK_NAME
        )
        snapshot.match("stack-resources", resources_description)

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(
        paths=[
            "$..WebACL.Capacity",
            "$..WebACL.LabelNamespace",
            "$..WebACL.ManagedByFirewallManager",
        ]
    )
    def test_web_acl(self, infrastructure, aws_client, snapshot):
        resource_id = infrastructure.get_stack_outputs(STACK_NAME)["WebACLRef"]
        web_acl_data = split_id(resource_id)
        snapshot.add_transformer(snapshot.transform.regex(web_acl_data["Id"], "<web-acl-id>"))
        snapshot.add_transformer(snapshot.transform.regex(web_acl_data["Name"], "<web-acl-name>"))
        snapshot.add_transformer(snapshot.transform.regex(web_acl_data["Scope"], "<web-acl-scope>"))
        snapshot.add_transformer(snapshot.transform.key_value("LockToken"))
        web_acl = aws_client.wafv2.get_web_acl(**web_acl_data)
        snapshot.match("WebACL", web_acl)

    @markers.aws.validated
    def test_web_acl_association(self, infrastructure, snapshot):
        resource_id = infrastructure.get_stack_outputs(STACK_NAME)["WebACLAssociationRef"]
        associate_data = split_id(resource_id)
        snapshot.add_transformer(
            snapshot.transform.regex(associate_data["Id"], "<web-acl-association-id>")
        )
        snapshot.add_transformer(
            snapshot.transform.regex(associate_data["Name"], "<associated-resource-arn>")
        )
        snapshot.match("WebAclAssociation", associate_data)

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(paths=["$..IPSet.Description"])
    def test_ip_set(self, infrastructure, aws_client, snapshot):
        resource_id = infrastructure.get_stack_outputs(STACK_NAME)["IPSetRef"]
        snapshot.add_transformer(snapshot.transform.key_value("LockToken"))
        snapshot.match("IPSet", aws_client.wafv2.get_ip_set(**split_id(resource_id)))

    @markers.aws.validated
    def test_logging_configuration(self, infrastructure, snapshot, aws_client):
        resource_id = infrastructure.get_stack_outputs(STACK_NAME)["LoggingConfigurationRef"]
        log_arn = infrastructure.get_stack_outputs(STACK_NAME)["LogRef"]
        snapshot.add_transformer(snapshot.transform.regex(log_arn, "<log-group-arn>"))
        snapshot.add_transformer(
            snapshot.transform.key_value("ResourceArn", "web-acl-resource-arn")
        )
        snapshot.match(
            "LoggingConfiguration",
            aws_client.wafv2.get_logging_configuration(ResourceArn=resource_id),
        )
