import os.path

import pytest
from botocore.exceptions import ClientError
from localstack.testing.pytest import markers
from localstack_snapshot.snapshots.transformer import SortingTransformer


@markers.snapshot.skip_snapshot_verify(
    paths=[
        "$..StackResourceDetail.DriftInformation",
        "$..StackResourceDetail.Metadata",
        "$..LoadBalancerAddresses",
        "$..DNSName",
        "$..SecurityGroupsOutput",  # TODO: GetAtt for SecurityGroups broken due to engine issues
        "$..AlpnPolicy",
        "$..DefaultActions..ForwardConfig",
        "$..Port",
        "$..SslPolicy",
        "$..LoadBalancerArns",
        "$..Error.Code",
        "$..Error.Message",
    ]
)
@markers.aws.validated
def test_elbv2_loadbalancer_resource(deploy_cfn_template, snapshot, aws_client):
    stack = deploy_cfn_template(
        template_path=os.path.join(
            os.path.dirname(__file__), "../../../templates/elbv2_loadbalancer.yaml"
        ),
        max_wait=360,
    )

    snapshot.match("outputs", stack.outputs)

    stack_resource_lb = aws_client.cloudformation.describe_stack_resource(
        StackName=stack.stack_id, LogicalResourceId="MyAlbC124CC0D"
    )
    snapshot.match("stack_resource_lb", stack_resource_lb)

    lb_arn = stack.outputs["LoadBalancerArnOutput"]
    describe_result = aws_client.elbv2.describe_load_balancers(LoadBalancerArns=[lb_arn])
    snapshot.match("describe_lbs", describe_result)
    lb = describe_result["LoadBalancers"][0]

    assert lb["LoadBalancerName"] in lb["DNSName"]

    snapshot.add_transformer(snapshot.transform.cloudformation_api())
    snapshot.add_transformer(snapshot.transform.key_value("VpcId"))
    snapshot.add_transformer(snapshot.transform.key_value("CanonicalHostedZoneId"))
    snapshot.add_transformer(snapshot.transform.key_value("SubnetId"))
    snapshot.add_transformer(snapshot.transform.key_value("LoadBalancerName"))
    snapshot.add_transformer(
        snapshot.transform.key_value("DNSName", reference_replacement=True), priority=-1
    )
    snapshot.add_transformer(
        snapshot.transform.regex(lb["SecurityGroups"][0], "<security-group-id>")
    )
    snapshot.add_transformer(
        SortingTransformer("AvailabilityZones", lambda x: x["ZoneName"][-1]), priority=-1
    )

    # describe is target groups of the listener and then the rules of the listener
    listener = aws_client.elbv2.describe_listeners(LoadBalancerArn=lb["LoadBalancerArn"])[
        "Listeners"
    ][0]
    snapshot.match("describe_listener", listener)

    target_group_arn = listener["DefaultActions"][0]["TargetGroupArn"]
    target_group = aws_client.elbv2.describe_target_groups(TargetGroupArns=[target_group_arn])[
        "TargetGroups"
    ][0]
    snapshot.match("describe_target_group", target_group)

    snapshot.add_transformer(snapshot.transform.key_value("TargetGroupName"))
    snapshot.add_transformer(snapshot.transform.key_value("TargetGroupArn"))
    snapshot.add_transformer(snapshot.transform.regex(lb["LoadBalancerArn"], "load-balancer-arn"))

    stack.destroy()
    with pytest.raises(ClientError) as e:
        aws_client.elbv2.describe_load_balancers(LoadBalancerArns=[lb_arn])

    snapshot.match("describe_lbs_after_destroy", e.value.response)
