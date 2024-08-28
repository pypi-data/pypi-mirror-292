from localstack.testing.pytest import markers
from localstack.utils.strings import short_uid


class TestKMS:
    @markers.aws.validated
    def test_create_key(self, aws_client, snapshot, cleanups):
        client = aws_client.kms
        result = client.create_key(Description="test", Tags=[{"TagKey": "t1", "TagValue": "v1"}])
        cleanups.append(lambda: client.schedule_key_deletion(KeyId=result["KeyMetadata"]["KeyId"]))
        snapshot.match("create_key", result)
        assert "KeyMetadata" in result
        key_id = result["KeyMetadata"]["KeyId"]
        result = client.describe_key(KeyId=key_id)
        assert result["KeyMetadata"]["KeyId"] == key_id

    @markers.aws.validated
    def test_create_key_alias(self, aws_client, snapshot, cleanups):
        client = aws_client.kms

        # create key and alias
        result = client.create_key(Description="test", Tags=[{"TagKey": "t1", "TagValue": "v1"}])
        key_id = result["KeyMetadata"]["KeyId"]
        alias_name = "alias/key-%s" % short_uid()
        client.create_alias(AliasName=alias_name, TargetKeyId=key_id)
        cleanups.append(lambda: client.schedule_key_deletion(KeyId=key_id))
        snapshot.match("create_key_alias", result)
        # list aliases
        response = client.list_aliases()
        assert response["Aliases"]
