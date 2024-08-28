from localstack.utils.strings import short_uid


def test_describe_secret(persistence_validations, snapshot, aws_client):
    secret_name = f"secret-{short_uid()}"
    aws_client.secretsmanager.create_secret(Name=secret_name)

    def validate():
        snapshot.match(
            "describe_secret", aws_client.secretsmanager.describe_secret(SecretId=secret_name)
        )

    persistence_validations.register(validate)
