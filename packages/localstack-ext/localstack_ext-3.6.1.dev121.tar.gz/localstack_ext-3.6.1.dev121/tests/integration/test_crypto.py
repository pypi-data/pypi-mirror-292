from localstack.pro.core.utils.crypto import (
    decrypt_via_aws_encryption_sdk,
    encrypt_via_aws_encryption_sdk,
)


def test_encrypt_via_aws_encryption_sdk(aws_client):
    key = aws_client.kms.create_key()
    key_arn = key["KeyMetadata"]["Arn"]
    plaintext = b"test data 123"

    # perform encryption/decryption roundtrip
    encrypted = encrypt_via_aws_encryption_sdk(plaintext, kms_key_arn=key_arn)
    decrypted = decrypt_via_aws_encryption_sdk(encrypted, kms_key_arn=key_arn)

    assert decrypted == plaintext
