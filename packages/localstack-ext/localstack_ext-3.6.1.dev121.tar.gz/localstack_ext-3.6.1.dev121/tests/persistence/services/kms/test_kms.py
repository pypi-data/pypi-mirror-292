from localstack.utils.strings import short_uid


def test_kms_describe_key(persistence_validations, snapshot, aws_client):
    key_id = aws_client.kms.create_key(
        Description=f"d-{short_uid()}",
        Tags=[{"TagKey": "foo", "TagValue": "bar"}],
    )["KeyMetadata"]["KeyId"]

    def validate():
        snapshot.match("describe_key", aws_client.kms.describe_key(KeyId=key_id))

    persistence_validations.register(validate)
