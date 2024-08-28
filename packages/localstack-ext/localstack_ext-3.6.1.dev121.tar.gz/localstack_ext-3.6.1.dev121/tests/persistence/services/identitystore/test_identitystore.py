from localstack.utils.strings import short_uid


def test_identity_store(persistence_validations, snapshot, aws_client):
    identity_store_id = f"identitystore-{short_uid()}"
    client = aws_client.identitystore
    group_name = f"TestGroup-{short_uid()}"
    client.create_group(IdentityStoreId=identity_store_id, DisplayName=group_name)

    def validate():
        snapshot.match(
            "list_groups",
            client.list_groups(IdentityStoreId=identity_store_id),
        )

    persistence_validations.register(validate)
