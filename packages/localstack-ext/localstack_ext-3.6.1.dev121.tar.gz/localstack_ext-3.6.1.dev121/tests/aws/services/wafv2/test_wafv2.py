from localstack.testing.pytest import markers
from localstack.utils.strings import short_uid


class TestWafV2:
    @markers.snapshot.skip_snapshot_verify(
        paths=[
            "$..NextMarker",  # missing
            "$..WebACL.Capacity",  # missing
            "$..WebACL.LabelNamespace",  # missing
            "$..WebACL.ManagedByFirewallManager",  # missing
            "$..LockToken",  # missing in some moto response, but not all
        ]
    )
    @markers.aws.validated
    def test_create_and_list_web_acl(self, aws_client, cleanups, snapshot):
        name = f"TestWebAcl-{short_uid()}"
        snapshot.add_transformer(snapshot.transform.regex(name, "<acl-name>"))
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
        snapshot.match("create_web_acl", create_web_acl)

        acl_arn = create_web_acl["Summary"]["ARN"]
        acl_id = create_web_acl["Summary"]["Id"]

        # FIXME: can be disabled when moto is fixed
        lock_token = create_web_acl["Summary"].get("LockToken", "unknown")
        if lock_token != "unknown":
            snapshot.add_transformer(snapshot.transform.regex(lock_token, "<lock-token>"))
        cleanups.append(
            lambda: aws_client.wafv2.delete_web_acl(
                Name=name, Scope=scope, Id=acl_id, LockToken=lock_token
            )
        )

        get_web_acl = aws_client.wafv2.get_web_acl(Name=name, Scope=scope, Id=acl_id)
        snapshot.match("get_web_acl", get_web_acl)

        list_response = aws_client.wafv2.list_web_acls(Scope=scope)
        assert any(acl["ARN"] == acl_arn for acl in list_response["WebACLs"])

        aws_client.wafv2.tag_resource(
            ResourceARN=acl_arn,
            Tags=[
                {"Key": "Name", "Value": "AWSWAF"},
            ],
        )

        list_tags_for_resource = aws_client.wafv2.list_tags_for_resource(ResourceARN=acl_arn)
        snapshot.match("list_tags_for_resource", list_tags_for_resource)
        assert {"Key": "Name", "Value": "AWSWAF"} in list_tags_for_resource["TagInfoForResource"][
            "TagList"
        ]
