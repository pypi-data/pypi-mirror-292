import os

from localstack.testing.pytest import markers
from localstack.testing.snapshots.transformer_utility import PATTERN_UUID
from localstack.utils.strings import short_uid


@markers.aws.validated
@markers.snapshot.skip_snapshot_verify(
    paths=[
        "$..AutoScalingGroups..AvailabilityZones",
        "$..AutoScalingGroups..CapacityRebalance",
        "$..AutoScalingGroups..EnabledMetrics",
        "$..AutoScalingGroups..HealthCheckGracePeriod",
        "$..AutoScalingGroups..Tags",
        "$..AutoScalingGroups..TrafficSources",
    ]
)
def test_autoscaling_group(deploy_cfn_template, aws_client, snapshot):
    snapshot.add_transformer(snapshot.transform.key_value("AutoScalingGroupName"))
    snapshot.add_transformer(snapshot.transform.key_value("LaunchConfigurationName"))
    snapshot.add_transformer(snapshot.transform.key_value("InstanceId"))
    snapshot.add_transformer(snapshot.transform.key_value("VPCZoneIdentifier"))
    snapshot.add_transformer(snapshot.transform.key_value("AvailabilityZone"))
    snapshot.add_transformer(
        snapshot.transform.regex(rf":{PATTERN_UUID.pattern}:", ":<autoscaling-group-uuid>:")
    )
    autoscaling_group_name = f"autoscaling-group-{short_uid()}"
    launch_configuration_name = f"launch-configuration-{short_uid()}"
    stack_result = deploy_cfn_template(
        template_path=os.path.join(
            os.path.dirname(__file__), "../../../templates/autoscaling_vpc.yml"
        ),
        parameters={
            "AutoscalingGroupName": autoscaling_group_name,
            "LaunchConfigurationName": launch_configuration_name,
        },
        max_wait=300,
    )
    snapshot.add_transformer(snapshot.transform.regex(stack_result.stack_id, "cfn-stack-id"))
    snapshot.add_transformer(snapshot.transform.regex(stack_result.stack_name, "cfn-stack-name"))

    autoscaling_groups = aws_client.autoscaling.describe_auto_scaling_groups(
        AutoScalingGroupNames=[autoscaling_group_name]
    )
    snapshot.match("autoscaling-groups", autoscaling_groups)

    autoscaling_resources = sorted(
        [
            resource
            for resource in aws_client.cloudformation.describe_stack_resources(
                StackName=stack_result.stack_name
            )["StackResources"]
            if resource.get("PhysicalResourceId")
            in [autoscaling_group_name, launch_configuration_name]
        ],
        key=lambda elem: elem["LogicalResourceId"],
    )
    snapshot.match("stack-resources-autoscaling", autoscaling_resources)
