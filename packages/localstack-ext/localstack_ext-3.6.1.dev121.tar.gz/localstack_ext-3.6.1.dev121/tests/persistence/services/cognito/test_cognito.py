from localstack.utils.strings import short_uid
from warrant import aws_srp


def test_describe_user_pool(persistence_validations, snapshot, aws_client):
    pool_id = aws_client.cognito_idp.create_user_pool(PoolName=f"pool-{short_uid()}")["UserPool"][
        "Id"
    ]

    def validate():
        snapshot.match(
            "describe_user_pool", aws_client.cognito_idp.describe_user_pool(UserPoolId=pool_id)
        )

    persistence_validations.register(validate)


def test_srp_auth(persistence_validations, snapshot, aws_client_factory):
    aws_client = aws_client_factory(region_name="eu-central-1")
    pool_name = f"pool-{short_uid()}"
    client_name = f"client-{short_uid()}"
    user_name = f"user{short_uid()}@example.org"
    pw = "SomePassword123!"
    user_pool = aws_client.cognito_idp.create_user_pool(
        PoolName=pool_name,
        UsernameAttributes=["email"],
    )
    pool_id = user_pool["UserPool"]["Id"]

    user_pool_client = aws_client.cognito_idp.create_user_pool_client(
        UserPoolId=pool_id,
        ClientName=client_name,
    )
    client_id = user_pool_client["UserPoolClient"]["ClientId"]

    aws_client.cognito_idp.admin_create_user(
        UserPoolId=pool_id, Username=user_name, MessageAction="SUPPRESS", TemporaryPassword=pw
    )
    aws_client.cognito_idp.admin_set_user_password(
        UserPoolId=pool_id, Username=user_name, Password=pw
    )

    def validate():
        user_pools = aws_client.cognito_idp.list_user_pools(MaxResults=10)
        assert pool_id in [p["Id"] for p in user_pools["UserPools"]]

        snapshot.match(
            "admin_get_user",
            aws_client.cognito_idp.admin_get_user(UserPoolId=pool_id, Username=user_name),
        )
        snapshot.match(
            "describe_user_pool", aws_client.cognito_idp.describe_user_pool(UserPoolId=pool_id)
        )
        snapshot.match(
            "describe_client",
            aws_client.cognito_idp.describe_user_pool_client(
                UserPoolId=pool_id, ClientId=client_id
            ),
        )

        awssrp = aws_srp.AWSSRP(
            username=user_name,
            password=pw,
            pool_id=pool_id,
            client_id=client_id,
            client=aws_client.cognito_idp,
        )
        token = awssrp.authenticate_user()
        id_token = token["AuthenticationResult"]["IdToken"]
        assert id_token

    persistence_validations.register(validate)


def test_create_and_describe_identity_pool(persistence_validations, snapshot, aws_client):
    pool_name = f"pool-{short_uid()}"
    identity_pool_id = aws_client.cognito_identity.create_identity_pool(
        IdentityPoolName=pool_name, AllowUnauthenticatedIdentities=False
    )["IdentityPoolId"]

    def validate():
        pools = aws_client.cognito_identity.list_identity_pools(MaxResults=10)["IdentityPools"]
        assert len(pools) >= 1
        snapshot.match(
            "describe_identity_pool",
            aws_client.cognito_identity.describe_identity_pool(IdentityPoolId=identity_pool_id),
        )

    persistence_validations.register(validate)
