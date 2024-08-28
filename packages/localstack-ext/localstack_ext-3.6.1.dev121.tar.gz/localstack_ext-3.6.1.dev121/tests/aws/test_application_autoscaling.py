from localstack.testing.pytest import markers
from localstack.utils.strings import short_uid


class TestAppAutoscaling:
    @markers.aws.unknown
    def test_put_scaling_policy(self, aws_client):
        client = aws_client.application_autoscaling

        service_ns = f"ecs-{short_uid()}"
        res_id = "r1"
        pol_name = f"p{short_uid()}"
        scale_dim = "ecs:service:DesiredCount"

        # add scaling policy
        result = client.put_scaling_policy(
            PolicyName=pol_name,
            ServiceNamespace=service_ns,
            ResourceId=res_id,
            ScalableDimension=scale_dim,
            PolicyType="TargetTrackingScaling",
        )
        assert pol_name in result.get("PolicyARN")

        # receive scaling policies
        result = client.describe_scaling_policies(ServiceNamespace=service_ns)
        matching = [sp for sp in result["ScalingPolicies"] if sp["PolicyName"] == pol_name]
        assert len(matching) == 1

        # clean up
        client.delete_scaling_policy(
            PolicyName=pol_name,
            ServiceNamespace=service_ns,
            ResourceId=res_id,
            ScalableDimension=scale_dim,
        )
