from localstack.utils.strings import short_uid


def test_application_auto_scaling(persistence_validations, snapshot, aws_client):
    client = aws_client.application_autoscaling
    service_ns = f"ecs-{short_uid()}"
    res_id = "r1"
    pol_name = f"p{short_uid()}"
    scale_dim = "ecs:service:DesiredCount"

    result = client.put_scaling_policy(
        PolicyName=pol_name,
        ServiceNamespace=service_ns,
        ResourceId=res_id,
        ScalableDimension=scale_dim,
        PolicyType="TargetTrackingScaling",
    )

    def validate():
        snapshot.match(
            "describe_scaling_policies",
            client.describe_scaling_policies(ServiceNamespace=service_ns),
        )

    persistence_validations.register(validate)
