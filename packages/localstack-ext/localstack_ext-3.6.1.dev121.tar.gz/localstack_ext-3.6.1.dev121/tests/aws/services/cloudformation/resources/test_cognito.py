import os.path

from localstack.testing.pytest import markers
from localstack.utils.strings import short_uid


@markers.aws.validated
@markers.snapshot.skip_snapshot_verify(
    paths=[
        "$..UserPool.SchemaAttributes",
        "$..UserPool.UserPoolTags",
        "$..UserPool.AccountRecoverySetting",
        "$..CognitoIdentityProviders..ProviderName",
    ]
)
def test_cognito_role_attachment(deploy_cfn_template, aws_client, snapshot):
    user_pool_name = f"user-pool-name-{short_uid()}"
    identity_pool_name = f"identity-pool-name-{short_uid()}"

    result = deploy_cfn_template(
        template_path=os.path.join(
            os.path.dirname(__file__),
            "../../../templates/cognito_identity_pool_role_attachment.yaml",
        ),
        template_mapping={
            "user_pool_name": user_pool_name,
            "identity_pool_name": identity_pool_name,
        },
    )
    identity_pool_id = result.outputs["IdentityPoolId"]
    identity_pool = aws_client.cognito_identity.describe_identity_pool(
        IdentityPoolId=identity_pool_id
    )
    snapshot.match("pool", identity_pool)

    roles = aws_client.cognito_identity.get_identity_pool_roles(IdentityPoolId=identity_pool_id)
    snapshot.match("role", roles)

    user_pool = aws_client.cognito_idp.describe_user_pool(UserPoolId=result.outputs["UserPoolId"])
    snapshot.match("user_pool", user_pool)

    snapshot.add_transformer(
        snapshot.transform.regex(result.outputs["UserPoolId"], "<user-pool-id>")
    )
    snapshot.add_transformer(
        snapshot.transform.regex(user_pool["UserPool"]["Name"], "<user-pool-name>")
    )
    snapshot.add_transformer(snapshot.transform.key_value("ClientId"))
    snapshot.add_transformer(snapshot.transform.key_value("ProviderName"))
    snapshot.add_transformer(snapshot.transform.key_value("IdentityPoolId"))
    snapshot.add_transformer(snapshot.transform.key_value("IdentityPoolName"))
    snapshot.add_transformer(snapshot.transform.key_value("authenticated", "auth-role"))
    snapshot.add_transformer(snapshot.transform.key_value("unauthenticated", "unauth-role"))


@markers.aws.only_localstack
def test_cognito_custom_ids(deploy_cfn_template, aws_client):
    template = """
    Parameters:
      UserPoolId:
        Type: String
      IdentityPoolId:
        Type: String
    Resources:
      UserPool:
        Type: AWS::Cognito::UserPool
        Properties:
          UserPoolTags:
            _custom_id_: !Ref UserPoolId
      IdentityPool:
        Type: AWS::Cognito::IdentityPool
        Properties:
          AllowUnauthenticatedIdentities: False
          IdentityPoolTags:
            _custom_id_: !Ref IdentityPoolId
    """

    user_pool_id = f"{aws_client.cognito_idp.meta.region_name}_{short_uid()}"
    identity_pool_id = f"test-{short_uid()}"
    deploy_cfn_template(
        template=template,
        parameters={
            "UserPoolId": user_pool_id,
            "IdentityPoolId": identity_pool_id,
        },
    )

    result = aws_client.cognito_idp.describe_user_pool(UserPoolId=user_pool_id)
    assert result["UserPool"]["Id"] == user_pool_id

    result = aws_client.cognito_identity.describe_identity_pool(IdentityPoolId=identity_pool_id)
    assert result.get("IdentityPoolId") == identity_pool_id


@markers.aws.validated
def test_user_pool_client_output(deploy_cfn_template, aws_client, snapshot):
    snapshot.add_transformer(snapshot.transform.key_value("ClientId"))
    snapshot.add_transformer(snapshot.transform.key_value("UserPoolId"))
    user_pool_name = f"user-pool-{short_uid()}"
    result = deploy_cfn_template(
        template_path=os.path.join(
            os.path.dirname(__file__),
            "../../../templates/cognito_user_pool_client.yaml",
        ),
        parameters={
            "UserPoolName": user_pool_name,
        },
    )
    client_id_output = result.outputs["ClientId"]
    user_pool_id = result.outputs["UserPoolId"]
    snapshot.match("outputs", result.outputs)

    result = aws_client.cognito_idp.list_user_pool_clients(UserPoolId=user_pool_id)
    client_id = result["UserPoolClients"][0]["ClientId"]
    assert client_id_output == client_id, "user pool client id from the CFN output does not match"
