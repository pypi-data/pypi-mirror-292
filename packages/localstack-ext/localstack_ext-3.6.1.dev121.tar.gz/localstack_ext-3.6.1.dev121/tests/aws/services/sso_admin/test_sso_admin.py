from localstack.testing.pytest import markers
from localstack.utils.aws.arns import parse_arn
from localstack.utils.strings import short_uid


class TestSsoAdmin:
    @markers.aws.unknown
    def test_list_permission_sets(self, aws_client):
        instance_arn = f"arn:aws:sso:::instance/your-instance-arn-{short_uid()}"
        assert not aws_client.sso_admin.list_permission_sets(InstanceArn=instance_arn).get(
            "PermissionSets"
        )

        response = aws_client.sso_admin.create_permission_set(
            Name=f"{short_uid()}", InstanceArn=instance_arn, Description="something something"
        )
        permission_set_arn = response["PermissionSet"]["PermissionSetArn"]

        # looks something like arn:aws:sso:::instance/your-instance-arn-ff962066/ps-04c0b382106b924d
        arn_data = parse_arn(permission_set_arn)
        assert arn_data["service"] == "sso"

        sets = aws_client.sso_admin.list_permission_sets(InstanceArn=instance_arn)["PermissionSets"]

        assert permission_set_arn in sets
