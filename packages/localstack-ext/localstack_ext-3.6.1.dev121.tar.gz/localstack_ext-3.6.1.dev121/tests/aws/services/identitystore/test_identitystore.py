from localstack.testing.pytest import markers
from localstack.utils.strings import short_uid


class TestIdentityStore:
    @markers.aws.needs_fixing
    def test_create_list_describe_group(self, aws_client):
        identity_store_id = f"identitystore-{short_uid()}"
        client = aws_client.identitystore
        group_name = f"TestGroup-{short_uid()}"
        create_response = client.create_group(
            IdentityStoreId=identity_store_id, DisplayName=group_name
        )

        group_id = create_response["GroupId"]
        assert "GroupId" in create_response
        list_response = client.list_groups(IdentityStoreId=identity_store_id)
        assert any(group["GroupId"] == group_id for group in list_response["Groups"])
        describe_response = client.describe_group(
            IdentityStoreId=identity_store_id, GroupId=group_id
        )
        assert describe_response["GroupId"] == group_id
        assert describe_response.get("DisplayName") == group_name
