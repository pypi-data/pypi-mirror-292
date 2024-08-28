import pytest
from localstack.pro.core import config as ext_config
from localstack.testing.aws.util import wait_for_user


@pytest.fixture(autouse=True)
def setup_iam_enforcement(monkeypatch):
    monkeypatch.setattr(ext_config, "ENFORCE_IAM", True)


@pytest.fixture
def client_factory_for_user(aws_client_factory, aws_client, region_name):
    def _create_factory(user_name):
        keys = aws_client.iam.create_access_key(UserName=user_name)["AccessKey"]
        wait_for_user(keys, region_name)
        return aws_client_factory(
            aws_access_key_id=keys["AccessKeyId"], aws_secret_access_key=keys["SecretAccessKey"]
        )

    return _create_factory


@pytest.fixture
def client_factory_for_role(aws_client, aws_client_factory, wait_and_assume_role):
    def _factory_for_role(role_name: str, session_name: str, **kwargs):
        role_arn = aws_client.iam.get_role(RoleName=role_name)["Role"]["Arn"]
        keys = wait_and_assume_role(role_arn=role_arn, session_name=session_name, **kwargs)
        return aws_client_factory(
            aws_access_key_id=keys["AccessKeyId"],
            aws_secret_access_key=keys["SecretAccessKey"],
            aws_session_token=keys["SessionToken"],
        )

    return _factory_for_role
