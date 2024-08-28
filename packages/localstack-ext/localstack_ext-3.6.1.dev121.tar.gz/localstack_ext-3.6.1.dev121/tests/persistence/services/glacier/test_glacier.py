from localstack.utils.strings import short_uid


def test_describe_glacier(persistence_validations, snapshot, aws_client):
    vault_name = f"sample-vault-{short_uid()}"

    # Create Glacier Vault
    aws_client.glacier.create_vault(vaultName=vault_name, accountId="-")

    # Describe Glacier Vault
    def validate():
        snapshot.match(
            "describe_vault", aws_client.glacier.describe_vault(vaultName=vault_name, accountId="-")
        )

    persistence_validations.register(validate)
