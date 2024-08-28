import pytest
from botocore.exceptions import ClientError
from localstack.testing.pytest import markers


# we cannot test organizations properly with AWS sandbox accounts, since they belong to organizations themselves and
# most likely don't have organization admin permissions
class TestOrganizations:
    @markers.aws.only_localstack
    def test_organization(self, aws_client):
        # create
        new_org = aws_client.organizations.create_organization(FeatureSet="ALL")["Organization"]
        assert "Id" in new_org
        assert "Arn" in new_org
        assert f"/{new_org['Id']}" in new_org["Arn"]

        # read
        org = aws_client.organizations.describe_organization()
        assert org["Organization"] == new_org

        # delete
        aws_client.organizations.delete_organization()

        # check it was deleted
        with pytest.raises(ClientError) as e:
            aws_client.organizations.describe_organization()
        e.match("AWSOrganizationsNotInUseException")

    @markers.aws.only_localstack
    def test_create_account_with_non_existing_org(self, aws_client):
        # make sure there's no active org
        try:
            aws_client.organizations.describe_organization()
            aws_client.organizations.delete_organization()  # delete an organization if it exists
        except ClientError:
            pass

        with pytest.raises(ClientError) as e:
            aws_client.organizations.create_account(
                Email="foobar@example.com", AccountName="foobar"
            )
        e.match("AWSOrganizationsNotInUseException")

    @markers.aws.only_localstack
    def test_create_and_describe_account(self, aws_client):
        aws_client.organizations.create_organization(FeatureSet="ALL")

        acc_status = aws_client.organizations.create_account(
            Email="foobar@example.com", AccountName="foobar"
        )["CreateAccountStatus"]
        acc_id = acc_status["AccountId"]
        assert acc_status["AccountName"] == "foobar"

        acc = aws_client.organizations.describe_account(AccountId=acc_id)["Account"]
        assert acc["Status"] == "ACTIVE"
        assert acc["Name"] == "foobar"
        assert acc["Id"] == acc_id
        assert acc["Email"] == "foobar@example.com"

        aws_client.organizations.remove_account_from_organization(AccountId=acc_id)

        aws_client.organizations.delete_organization()

    @markers.aws.only_localstack
    def test_tag_policy(self, aws_client):
        aws_client.organizations.create_organization(FeatureSet="ALL")

        response = aws_client.organizations.create_policy(
            Name="test-scp",
            Type="SERVICE_CONTROL_POLICY",
            Description="test-scp",
            Content='{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Action":["s3:*"],"Resource":["*"]}]}',
            Tags=[{"Key": "initial_tag", "Value": "foo"}],
        )

        assert response["Policy"]["PolicySummary"]["Name"] == "test-scp"
        policy_id = response["Policy"]["PolicySummary"]["Id"]

        response = aws_client.organizations.list_tags_for_resource(ResourceId=policy_id)
        assert response["Tags"] == [{"Key": "initial_tag", "Value": "foo"}]

        aws_client.organizations.tag_resource(
            ResourceId=policy_id, Tags=[{"Key": "additional_tag", "Value": "bar"}]
        )
        response = aws_client.organizations.list_tags_for_resource(ResourceId=policy_id)
        assert response["Tags"] == [
            {"Key": "initial_tag", "Value": "foo"},
            {"Key": "additional_tag", "Value": "bar"},
        ]

        aws_client.organizations.delete_policy(PolicyId=policy_id)
        aws_client.organizations.delete_organization()
