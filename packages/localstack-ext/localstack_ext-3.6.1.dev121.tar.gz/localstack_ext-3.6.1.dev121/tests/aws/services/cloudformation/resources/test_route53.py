import os

import aws_cdk as cdk
import pytest
from localstack.testing.pytest import markers
from localstack.utils.strings import short_uid
from localstack.utils.sync import wait_until

from tests.aws.services.cloudformation.utils import load_template


@pytest.fixture(autouse=True)
def route53_snapshot_transformer(snapshot):
    snapshot.add_transformer(snapshot.transform.route53_api())


@pytest.mark.parametrize(
    "zone_suffix",
    [".example.com", ".example.com."],
    ids=["without_trailing_dot", "with_trailing_dot"],
)
@markers.aws.unknown
def test_hostedzone_optionaltrailingdot(
    cleanup_stacks,
    cleanup_changesets,
    is_change_set_created_and_available,
    is_stack_created,
    zone_suffix,
    aws_client,
):
    stack_name = f"stack-{short_uid()}"
    change_set_name = f"change-set-{short_uid()}"
    zone_name = f"{short_uid()}{zone_suffix}"
    template_rendered = load_template("route53_hostedzone.yaml", zone_name=zone_name)

    response = aws_client.cloudformation.create_change_set(
        StackName=stack_name,
        ChangeSetName=change_set_name,
        TemplateBody=template_rendered,
        ChangeSetType="CREATE",
    )
    change_set_id = response["Id"]
    stack_id = response["StackId"]

    try:
        wait_until(is_change_set_created_and_available(change_set_id))
        aws_client.cloudformation.execute_change_set(ChangeSetName=change_set_id)
        wait_until(is_stack_created(stack_id))

    finally:
        cleanup_changesets([change_set_id])
        cleanup_stacks([stack_id])


@markers.aws.validated
@markers.snapshot.skip_snapshot_verify(
    paths=["$..HostedZone.CallerReference", "$..DelegationSet.Id", "$..HostedZone.Id"]
)
def test_hostedzone_without_comment(deploy_cfn_template, snapshot, aws_client):
    zone_name = f"foo.{short_uid()}.com"
    snapshot.add_transformer(snapshot.transform.regex(zone_name, "<zone-name>"))

    stack = deploy_cfn_template(
        template_path=os.path.join(
            os.path.dirname(__file__), "../../../templates/route53_hostedzone.yaml"
        ),
        template_mapping={"zone_name": zone_name},
    )

    hosted_zone_id = stack.outputs["HostedZoneId"]
    res = aws_client.route53.get_hosted_zone(Id=hosted_zone_id)
    snapshot.match("zone-details", res)


@markers.aws.validated
@markers.snapshot.skip_snapshot_verify(paths=["$..MaxItems"])
def test_private_hostedzone(deploy_cfn_template, snapshot, aws_client, region_name):
    zone_name = f"foo.{short_uid()}.com"
    snapshot.add_transformer(snapshot.transform.regex(zone_name, "<zone-name>"))
    stack = deploy_cfn_template(
        template_path=os.path.join(
            os.path.dirname(__file__), "../../../templates/route53_private_hostedzone.yaml"
        ),
        parameters={
            "ZoneName": zone_name,
            "Region": region_name,
        },
    )

    hosted_zone_id = stack.outputs["HostedZoneId"]

    res = aws_client.route53.get_hosted_zone(Id=hosted_zone_id)
    snapshot.match("zone-details", res)

    vpc_id = stack.outputs["VpcId"]
    snapshot.add_transformer(snapshot.transform.regex(vpc_id, "<vpc-id>"))

    response = aws_client.route53.list_hosted_zones_by_vpc(VPCId=vpc_id, VPCRegion=region_name)
    snapshot.match("list_hosted_zones_by_vpc", response)

    response = aws_client.route53.list_hosted_zones()
    zones = [zone for zone in response["HostedZones"] if zone_name in zone["Name"]]
    snapshot.match("list_hosted_zones", zones)


@markers.aws.validated
@markers.snapshot.skip_snapshot_verify(
    paths=["$..HostedZone.CallerReference", "$..DelegationSet.Id", "$..HostedZone.Id"]
)
def test_hostedzone_with_comment(deploy_cfn_template, snapshot, aws_client):
    stack = deploy_cfn_template(
        template_path=os.path.join(
            os.path.dirname(__file__), "../../../templates/route53_hostedzone_with_comment.yml"
        )
    )

    hosted_zone_id = stack.outputs["HostedZoneId"]

    snapshot.add_transformers_list(
        [
            snapshot.transform.key_value("CallerReference", reference_replacement=False),
            snapshot.transform.key_value("NameServers", reference_replacement=False),
            snapshot.transform.regex(hosted_zone_id, "<hosted_zone_id>"),
        ]
    )

    res = aws_client.route53.get_hosted_zone(Id=hosted_zone_id)
    snapshot.match("zone-details", res)


#   - Make this test compatible with community by using a different alias
@markers.snapshot.skip_snapshot_verify(
    paths=[
        "$..StackResourceDetail.Metadata",  # missing
        "$..MaxItems",  # 100 => 300
        "$..AliasTarget.DNSName",  # probably an issue in route53. domains aren't adding `.` suffix
        "$..ResourceRecordSets..Name",  # probably an issue in route53. domains aren't adding `.` suffix
        "$..ResourceRecordSets..ResourceRecords..Value",  # awsdns-hostmaster.amazon.com. vs hostmaster.example.com.
    ]
)
@markers.aws.validated
def test_record_set_with_alias_record(aws_client, infrastructure_setup, snapshot):
    stack_name = "CfnRoute53RecordSetAliasStack"
    infra = infrastructure_setup(namespace="CfnRoute53RecordSetAlias")
    stack = cdk.Stack(infra.cdk_app, stack_name)

    zone = cdk.aws_route53.HostedZone(stack, "zone", zone_name="fake.localstack.cloud")
    vpc = cdk.aws_ec2.Vpc(stack, "vpc")
    alb = cdk.aws_elasticloadbalancingv2.ApplicationLoadBalancer(stack, "alb", vpc=vpc)
    rr = cdk.aws_route53.ARecord(
        stack,
        "rr",
        target=cdk.aws_route53.RecordTarget.from_alias(
            cdk.aws_route53_targets.LoadBalancerTarget(alb)
        ),
        zone=zone,
        record_name="api.fake.localstack.cloud",
        ttl=cdk.Duration.minutes(5),
    )
    raw_rr: cdk.aws_route53.CfnRecordSet = rr.node.default_child
    raw_rr.override_logical_id("CustomResourceRecord")

    cdk.CfnOutput(stack, "RecordId", value=raw_rr.ref)
    cdk.CfnOutput(stack, "HostedZoneId", value=zone.hosted_zone_id)
    cdk.CfnOutput(stack, "AlbDnsName", value=alb.load_balancer_dns_name)
    cdk.CfnOutput(stack, "AlbHostedZoneId", value=alb.load_balancer_canonical_hosted_zone_id)

    with infra.provisioner() as prov:
        # outputs
        record_id = prov.get_stack_outputs(stack_name=stack_name)["RecordId"]
        zone_id = prov.get_stack_outputs(stack_name=stack_name)["HostedZoneId"]
        alb_dns_name = prov.get_stack_outputs(stack_name=stack_name)["AlbDnsName"]
        alb_hosted_zone_id = prov.get_stack_outputs(stack_name=stack_name)["AlbHostedZoneId"]

        # transformations
        snapshot.add_transformer(snapshot.transform.cloudformation_api())
        snapshot.add_transformer(snapshot.transform.regex(record_id, "<resource-record-id>"))
        snapshot.add_transformer(snapshot.transform.regex(zone_id, "<zone-id>"))
        snapshot.add_transformer(snapshot.transform.regex(alb_dns_name, "<alb-dns-name>"))
        snapshot.add_transformer(
            snapshot.transform.regex(alb_dns_name.lower(), "<alb-dns-name-lowercase>"), priority=-1
        )
        snapshot.add_transformer(snapshot.transform.regex(alb_hosted_zone_id, "<alb-zone-id>"))
        snapshot.add_transformer(snapshot.transform.key_value("Value", reference_replacement=True))

        # cloudformation resource, check physical resource ID, status, etc.
        describe_resource_record_resource = aws_client.cloudformation.describe_stack_resource(
            StackName=stack_name, LogicalResourceId="CustomResourceRecord"
        )
        assert (
            record_id
            == describe_resource_record_resource["StackResourceDetail"]["PhysicalResourceId"]
        )
        snapshot.match("describe_resource_record_resource", describe_resource_record_resource)

        # API-level check
        resource_record_sets = aws_client.route53.list_resource_record_sets(HostedZoneId=zone_id)
        snapshot.match("resource_record_sets", resource_record_sets)
