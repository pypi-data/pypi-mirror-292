import pytest


@pytest.mark.skip(reason="flaky")  # see comment in validate below
def test_describe_organization(persistence_validations, snapshot, aws_client):
    aws_client.organizations.create_organization(FeatureSet="ALL")
    account_id = aws_client.organizations.create_account(
        Email="foobar@example.com", AccountName="foobar"
    )["CreateAccountStatus"]["AccountId"]

    def validate():
        # flaky with botocore.errorfactory.AccountNotFoundException: An error occurred (AccountNotFoundException) when calling the DescribeAccount operation: You specified an account that doesn't exist.
        snapshot.match(
            "describe_account", aws_client.organizations.describe_account(AccountId=account_id)
        )

    persistence_validations.register(validate)
