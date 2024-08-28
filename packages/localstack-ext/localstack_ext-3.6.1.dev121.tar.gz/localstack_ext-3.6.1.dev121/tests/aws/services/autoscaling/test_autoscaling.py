import logging

import pytest
from localstack.testing.aws.util import is_aws_cloud
from localstack.testing.pytest import markers
from localstack.utils.strings import short_uid

LOG = logging.getLogger(__name__)


@pytest.fixture
def create_auto_scaling_group(create_launch_configuration, aws_client):
    groups = []

    def _create(**kwargs):
        kwargs.setdefault("AutoScalingGroupName", f"asg-{short_uid()}")
        kwargs.setdefault("MinSize", 0)
        kwargs.setdefault("MaxSize", 1)
        kwargs.setdefault("AvailabilityZones", ["us-east-1a"])
        if not kwargs.get("LaunchConfigurationName"):
            config_name = kwargs["LaunchConfigurationName"] = f"lc-{short_uid()}"
            create_launch_configuration(LaunchConfigurationName=config_name)
        result = aws_client.autoscaling.create_auto_scaling_group(**kwargs)
        groups.append(kwargs["AutoScalingGroupName"])
        return result

    yield _create

    for group in groups:
        try:
            aws_client.autoscaling.delete_auto_scaling_group(AutoScalingGroupName=group)
        except Exception as e:
            LOG.info("Unable to delete auto scaling group %s: %s", group, e)


@pytest.fixture
def create_launch_configuration(get_valid_ami, aws_client):
    configs = []

    def _create(**kwargs):
        kwargs.setdefault("LaunchConfigurationName", f"lc-{short_uid()}")
        kwargs.setdefault("ImageId", get_valid_ami())
        kwargs.setdefault("InstanceType", "t2.small")
        result = aws_client.autoscaling.create_launch_configuration(**kwargs)
        configs.append(kwargs["LaunchConfigurationName"])
        return result

    yield _create

    for config in configs:
        try:
            aws_client.autoscaling.delete_launch_configuration(LaunchConfigurationName=config)
        except Exception as e:
            LOG.info("Unable to delete launch configuration: %s", e)


@pytest.fixture
def get_valid_ami(aws_client):
    def _get_ami():
        filters = []
        if is_aws_cloud():
            filters = [
                {"Name": "name", "Values": ["amzn2-ami-hvm*"]},
                {"Name": "architecture", "Values": ["x86_64"]},
                {"Name": "creation-date", "Values": ["2021-*"]},
                {"Name": "image-type", "Values": ["machine"]},
                {"Name": "virtualization-type", "Values": ["hvm"]},
            ]
        images = aws_client.ec2.describe_images(Filters=filters)["Images"]
        return images[0]["ImageId"]

    return _get_ami


class TestAutoScaling:
    @markers.aws.validated
    def test_metrics_collection(
        self, create_auto_scaling_group, create_launch_configuration, aws_client
    ):
        group_name = f"asg-{short_uid()}"
        create_auto_scaling_group(AutoScalingGroupName=group_name)

        # enable metrics
        metrics = ["GroupMinSize", "GroupInServiceInstances", "WarmPoolPendingCapacity"]
        aws_client.autoscaling.enable_metrics_collection(
            AutoScalingGroupName=group_name, Metrics=metrics, Granularity="1Minute"
        )

        # assert result
        result = aws_client.autoscaling.describe_metric_collection_types()
        assert result["Granularities"] == [{"Granularity": "1Minute"}]
        assert len(metrics) == 3
        for metric in metrics:
            assert {"Metric": metric} in result["Metrics"]

        # disable metrics
        aws_client.autoscaling.disable_metrics_collection(
            AutoScalingGroupName=group_name, Metrics=["GroupInServiceInstances"]
        )
        metrics.remove("GroupInServiceInstances")

        # assert result
        result = aws_client.autoscaling.describe_metric_collection_types()
        assert len(metrics) == 2
        for metric in metrics:
            assert {"Metric": metric} in result["Metrics"]

    @markers.aws.validated
    def test_create_asg_errors(self, create_launch_configuration, aws_client):
        group_name = f"asg-{short_uid()}"

        with pytest.raises(Exception) as exc:
            aws_client.autoscaling.create_auto_scaling_group(
                AutoScalingGroupName=group_name,
                MaxSize=5,
                MinSize=2,
            )
        exc.match("ValidationError")
        exc.match(
            "requests must contain either LaunchTemplate, LaunchConfigurationName, InstanceId or MixedInstancesPolicy"
        )

        config_name = f"lc-{short_uid()}"
        create_launch_configuration(LaunchConfigurationName=config_name)
        with pytest.raises(Exception) as exc:
            aws_client.autoscaling.create_auto_scaling_group(
                AutoScalingGroupName=group_name,
                LaunchConfigurationName=config_name,
                MaxSize=5,
                MinSize=2,
            )
        exc.match("ValidationError")
        exc.match("At least one Availability Zone or VPC Subnet is required")
