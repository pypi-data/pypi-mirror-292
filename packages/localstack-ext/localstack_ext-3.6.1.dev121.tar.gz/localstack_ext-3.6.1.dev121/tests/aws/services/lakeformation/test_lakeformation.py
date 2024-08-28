from localstack.testing.pytest import markers

# NOTE: only adding a few simple smoke tests here - features mainly covered by TF test suite


class TestLakeFormation:
    @markers.aws.unknown
    def test_manage_permissions(self, aws_client):
        role_arn = "arn:aws:iam::000000000000:role/test-role-123"
        resource = {"DatabaseName": "test-db-1", "Name": "test-table-123"}
        principal = {"DataLakePrincipalIdentifier": role_arn}

        result = aws_client.lakeformation.grant_permissions(
            Principal=principal,
            Resource={"TableWithColumns": resource},
            Permissions=["ALL", "DELETE"],
        )
        assert result["ResponseMetadata"]["HTTPStatusCode"] == 200

        result = aws_client.lakeformation.list_permissions(
            Principal=principal,
            Resource={"Table": resource},
        )
        result = result.get("PrincipalResourcePermissions", [])
        assert result
        assert result[-1].get("Principal") == principal
        assert result[-1].get("Resource") == {"TableWithColumns": resource}
        assert result[-1].get("Permissions") == ["ALL", "DELETE"]
