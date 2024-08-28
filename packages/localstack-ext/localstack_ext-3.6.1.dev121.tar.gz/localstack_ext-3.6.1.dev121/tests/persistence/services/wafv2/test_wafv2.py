import pytest
from localstack.utils.strings import short_uid


@pytest.mark.skip(
    reason="Test fails for cloudpods due to service naming mismatch in moto backend dict"
)
def test_describe_web_acl(persistence_validations, snapshot, aws_client):
    name = f"TestWebAcl-{short_uid()}"
    scope = "REGIONAL"
    create_web_acl = aws_client.wafv2.create_web_acl(
        Name=name,
        Scope=scope,
        DefaultAction={"Allow": {}},
        VisibilityConfig={
            "SampledRequestsEnabled": True,
            "CloudWatchMetricsEnabled": True,
            "MetricName": f"{name}Metric",
        },
    )
    acl_id = create_web_acl["Summary"]["Id"]

    def validate():
        snapshot.match(
            "create_web_acl",
            aws_client.wafv2.get_web_acl(Name=name, Scope=scope, Id=acl_id),
        )

    persistence_validations.register(validate)
