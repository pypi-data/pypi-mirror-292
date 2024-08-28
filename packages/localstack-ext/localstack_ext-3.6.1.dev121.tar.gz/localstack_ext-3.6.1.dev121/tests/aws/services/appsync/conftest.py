import json
import logging
import os
import time
from dataclasses import dataclass

import pytest
from botocore.exceptions import ClientError
from localstack.testing.pytest.fixtures import role_policy_su
from localstack.utils.strings import short_uid, to_str
from localstack.utils.sync import poll_condition
from localstack.utils.testutil import create_lambda_archive, create_lambda_function
from werkzeug import Response

LOG = logging.getLogger(__name__)

# LAMBDA UTILS
LAMBDA_DATA_SOURCE_TYPE = "AWS_LAMBDA"
LAMBDA_MUTATION_REQUEST_TEMPLATE = json.dumps(
    {
        "version": "2017-02-28",
        "operation": "Invoke",
        "payload": {
            "op": "addPost",
            "args": {"name": "${context.arguments.name}", "time": 123},
        },
    }
)
LAMBDA_QUERY_REQUEST_TEMPLATE = json.dumps(
    {"version": "2017-02-28", "operation": "Invoke", "payload": {"op": "getPosts"}}
)
TEST_LAMBDA = """
import boto3, json, io, os
def handler(event, context):
    s3 = boto3.client("s3")
    bucket = "<bucket_name>"
    key = "test-object"
    if event["op"] == "addPost":
        try:
            s3.head_bucket(Bucket=bucket)
        except Exception as e:
            region = os.environ["AWS_REGION"]
            kwargs = {"CreateBucketConfiguration": {"LocationConstraint": region}} if region != "us-east-1" else {}
            s3.create_bucket(Bucket=bucket, **kwargs)
        s3.upload_fileobj(io.BytesIO(json.dumps(event["args"]).encode("utf-8")), bucket, key)
        return event["args"]
    if event["op"] == "getPosts":
        data = io.BytesIO()
        s3.download_fileobj(bucket, key, data)
        return [json.loads(data.getvalue().decode("utf-8"))]
"""

# DYNAMODB UTILS
DYNAMODB_DATA_SOURCE_TYPE = "AMAZON_DYNAMODB"
DYNAMODB_MUTATION_REQUEST_TEMPLATE = json.dumps(
    {
        "version": "2017-02-28",
        "operation": "PutItem",
        "key": {"name": "<name-str>"},
        "attributeValues": {"time": {"N": "123"}},
    }
).replace('"<name-str>"', '$util.dynamodb.toDynamoDBJson("${ctx.args.post.name}")')
DYNAMODB_QUERY_REQUEST_TEMPLATE = json.dumps({"version": "2017-02-28", "operation": "Scan"})

JSON_RESULT_TEMPLATE = "$util.toJson($context.result)"

# RDS UTILS
RDS_DATA_SOURCE_TYPE = "RELATIONAL_DATABASE"
RDS_MUTATION_REQUEST_TEMPLATE = json.dumps(
    {
        "version": "2018-05-29",
        "statements": [
            "CREATE TABLE IF NOT EXISTS posts (name varchar, title varchar, time int)",
            "INSERT INTO posts (name, title, time) values ('$ctx.args.name', 'test title', 123)",
            "SELECT * FROM posts WHERE name='$ctx.args.name'",
        ],
    }
)
RDS_MUTATION_RESULT_TEMPLATE = """
        #set($resObj=$utils.rds.toJsonObject($ctx.result))
        #set($resObj1=$resObj[2])
        $utils.toJson($resObj1[0])
        """
RDS_QUERY_REQUEST_TEMPLATE = json.dumps(
    {"version": "2018-05-29", "statements": ["SELECT name, title, time FROM posts"]}
)
RDS_QUERY_RESULT_TEMPLATE = """
        #set($resObj=$utils.rds.toJsonObject($ctx.result))
        $utils.toJson($resObj[0])
        """
TEST_RDS_DB_NAME = f"rds-db-{short_uid()}"
TEST_SECMGR_SECRET_NAME = f"rds-password-{short_uid()}"
TEST_RDS_CLUSTER_ID = f"rds-cluster-{short_uid()}"

# HTTP RESOLVER UTILS
HTTP_DATA_SOURCE_TYPE = "HTTP"
HTTP_MUTATION_REQUEST_TEMPLATE = json.dumps(
    {
        "version": "2018-05-29",
        "method": "POST",
        "params": {
            "headers": {
                "header1": "test123",
            },
            "query": {"q1": "foobar"},
            "body": '{"name": "${context.arguments.name}", "time": 123}',
        },
        "resourcePath": "/my/path",
    }
)
HTTP_QUERY_REQUEST_TEMPLATE = json.dumps(
    {
        "version": "2018-05-29",
        "method": "GET",
        "params": {
            "headers": {
                "header1": "test234",
            },
            "query": {"q1": "foo-bar"},
        },
        "resourcePath": "/my/path2",
    }
)
HTTP_RESULT_TEMPLATE = "$context.result.body"

# cognito auth constants
COGNITO_USER_ADMIN = "admin"
COGNITO_USER_GUEST = "guest"
COGNITO_GROUP_ADMINS = "admins"
COGNITO_GROUP_GUESTS = "guests"

# test schema
TEST_SCHEMA = """
schema {
    query: Query
    mutation: Mutation
}
type Query @aws_iam @aws_api_key {
    getPosts: [Post!]! @aws_auth(cognito_groups: ["bloggers", "<grp:guests>"])
}
type Mutation {
    addPost(name: String!): Post! @aws_auth(cognito_groups: ["bloggers", "<grp:admins>"])
        @aws_cognito_user_pools(cognito_groups: ["<grp:admins>"])
    addPostObj(post: PostInput!): Post! @aws_auth(cognito_groups: ["bloggers", "<grp:admins>"])
        @aws_cognito_user_pools(cognito_groups: ["<grp:admins>"])
}
input PostInput {
    name: String! @aws_iam @aws_cognito_user_pools
}
type Post @aws_iam {
    name: String!
    time: AWSTimestamp @aws_api_key
}
""".replace("<grp:guests>", COGNITO_GROUP_GUESTS).replace("<grp:admins>", COGNITO_GROUP_ADMINS)

role_assume_policy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {"Service": "appsync.amazonaws.com"},
            "Action": "sts:AssumeRole",
        }
    ],
}

# pipeline resolver schema
PIPELINE_RESOLVER_SCHEMA = """
schema {
    query: Query
    mutation: Mutation
}

type Mutation {
    signUp(input: Signup): User
}

type Query {
    getUser(userId: ID!): User
}

input Signup {
    username: String!
    email: String!
}

type User {
    userId: ID!
    username: String
    email: AWSEmail
}
"""


@pytest.fixture
def appsync_su_role(create_iam_role_with_policy):
    return create_iam_role_with_policy(
        RoleName=f"appsync-role-{short_uid()}",
        PolicyName=f"appsync-policy-{short_uid()}",
        RoleDefinition=role_assume_policy,
        PolicyDefinition=role_policy_su,
    )


@pytest.fixture
def appsync_create_domain_name(acm_request_certificate, aws_client):
    domain_names = list()

    def factory(**kwargs):
        if "domainName" not in kwargs:
            kwargs["domainName"] = f"test-domain-{short_uid()}.localhost.localstack.cloud"
        # When we try to make tests depending on this fixture to pass against AWS, we have to make sure
        # we create certificates in us-east-1. Otherwise AWS returns an error:
        # (BadRequestException) when calling the CreateDomainName operation: Certificate must be in us-east-1.
        #
        # We will do that later, as currently we do not have a good way to create certificates for tests either way -
        # they require validation that is too slowe and complicated for tests.
        if "certificateArn" not in kwargs:
            kwargs["certificateArn"] = acm_request_certificate(DomainName=kwargs["domainName"])[
                "CertificateArn"
            ]

        aws_client.appsync.create_domain_name(**kwargs)
        domain_names.append(kwargs["domainName"])
        return kwargs["domainName"]

    yield factory

    for domain_name in domain_names:
        try:
            aws_client.appsync.delete_domain_name(domainName=domain_name)
        except Exception as e:
            LOG.debug("Error cleaning up AppSync Domain Name: %s, %s", domain_name, e)


@pytest.fixture
def appsync_graphql_api(appsync_create_api):
    return appsync_create_api()


@pytest.fixture
def create_data_source_ddb(dynamodb_create_table, appsync_su_role, aws_client):
    data_sources = []

    def _create(
        api_id, name, table_name=None, hash_key: str = "test", existing_table: bool = False
    ):
        ds_name = name or f"ds-{short_uid()}"
        table_name = table_name or f"appsync-{short_uid()}"
        if not existing_table:
            dynamodb_create_table(table_name=table_name, partition_key=hash_key)
        result = aws_client.appsync.create_data_source(
            apiId=api_id,
            name=ds_name,
            type="AMAZON_DYNAMODB",
            dynamodbConfig={
                "awsRegion": aws_client.appsync.meta.region_name,
                "tableName": table_name,
            },
            serviceRoleArn=appsync_su_role,
        )
        data_sources.append((api_id, ds_name))
        return result["dataSource"]

    yield _create

    for api_id, ds_name in data_sources:
        aws_client.appsync.delete_data_source(apiId=api_id, name=ds_name)


@pytest.fixture
def create_data_source_lambda(create_lambda_function, appsync_su_role, aws_client):
    data_sources = []

    def _create(api_id, src, runtime):
        ds_name = f"ds_{short_uid()}"
        fn_name = f"fn-{short_uid()}"
        function_response = create_lambda_function(
            func_name=fn_name,
            handler_file=src,
            runtime=runtime,
        )
        LOG.debug("waiting for lambda data source to become ready")
        aws_client.lambda_.get_waiter("function_active_v2").wait(FunctionName=fn_name)

        # allow appsync to invoke the handler
        api_arn = aws_client.appsync.get_graphql_api(apiId=api_id)["graphqlApi"]["arn"]
        aws_client.lambda_.add_permission(
            FunctionName=fn_name,
            StatementId=f"s-{short_uid()}",
            Action="lambda:InvokeFunction",
            Principal="appsync.amazonaws.com",
            SourceArn=api_arn,
        )

        lambda_arn = function_response["CreateFunctionResponse"]["FunctionArn"]
        result = aws_client.appsync.create_data_source(
            apiId=api_id,
            name=ds_name,
            type="AWS_LAMBDA",
            lambdaConfig={
                "lambdaFunctionArn": lambda_arn,
            },
            serviceRoleArn=appsync_su_role,
        )
        data_sources.append((api_id, ds_name))
        if os.getenv("TEST_TARGET") == "AWS_CLOUD":
            LOG.debug("allowing IAM role to propagate")
            time.sleep(10)
        return result["dataSource"]

    yield _create

    delete_failures = []
    for api_id, ds_name in data_sources:
        try:
            aws_client.appsync.delete_data_source(apiId=api_id, name=ds_name)
        except Exception as e:
            LOG.debug(f"Error cleaning up AppSync lambda data source {ds_name}: {e}")
            delete_failures.append((api_id, ds_name))

    if delete_failures:
        raise RuntimeError(f"Failed to delete resources {delete_failures}")


@pytest.fixture
def create_data_source_rds(create_iam_role_with_policy, snapshot, aws_client):
    data_sources = []

    def _create(
        api_id: str,
        cluster_arn: str,
        secret_arn: str,
        database_name: str,
        region_name: str = "us-east-1",
    ):
        # create the role to access the database and secret
        # https://docs.aws.amazon.com/appsync/latest/devguide/tutorial-rds-resolvers.html#graphql-schema

        role_definition = {
            "Statement": {
                "Sid": "",
                "Effect": "Allow",
                "Principal": {"Service": "appsync.amazonaws.com"},
                "Action": "sts:AssumeRole",
            }
        }
        policy_definition = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "rds-data:DeleteItems",
                        "rds-data:ExecuteSql",
                        "rds-data:ExecuteStatement",
                        "rds-data:GetItems",
                        "rds-data:InsertItems",
                        "rds-data:UpdateItems",
                    ],
                    "Resource": [
                        cluster_arn,
                        f"{cluster_arn}:*",
                    ],
                },
                {
                    "Effect": "Allow",
                    "Action": ["secretsmanager:GetSecretValue"],
                    "Resource": [
                        secret_arn,
                        f"{secret_arn}:*",
                    ],
                },
            ],
        }
        role_name = f"role-{short_uid()}"
        policy_name = f"policy-{short_uid()}"
        snapshot.add_transformer(snapshot.transform.regex(role_name, "<ds-service-role>"))
        snapshot.add_transformer(snapshot.transform.regex(policy_name, "<ds-service-policy>"))
        role_arn = create_iam_role_with_policy(
            RoleName=role_name,
            PolicyName=policy_name,
            RoleDefinition=role_definition,
            PolicyDefinition=policy_definition,
        )

        ds_name = f"ds_{short_uid()}"
        result = aws_client.appsync.create_data_source(
            apiId=api_id,
            name=ds_name,
            type="RELATIONAL_DATABASE",
            serviceRoleArn=role_arn,
            relationalDatabaseConfig={
                "relationalDatabaseSourceType": "RDS_HTTP_ENDPOINT",
                "rdsHttpEndpointConfig": {
                    "awsRegion": region_name,
                    "dbClusterIdentifier": cluster_arn,
                    "databaseName": database_name,
                    "awsSecretStoreArn": secret_arn,
                },
            },
        )
        data_sources.append((api_id, ds_name))
        return result["dataSource"]

    yield _create

    delete_failures = []
    for api_id, ds_name in data_sources:
        try:
            aws_client.appsync.delete_data_source(apiId=api_id, name=ds_name)
        except Exception as e:
            LOG.debug(f"Error cleaning up AppSync lambda data source {ds_name}: {e}")
            delete_failures.append((api_id, ds_name))

    if delete_failures:
        raise RuntimeError(f"Failed to delete resources {delete_failures}")


@pytest.fixture
def create_resolver(create_data_source_ddb, aws_client):
    resolvers = []

    def _create_resolver(**kwargs):
        result = aws_client.appsync.create_resolver(**kwargs)
        resolvers.append((kwargs.get("apiId"), kwargs.get("typeName"), kwargs.get("fieldName")))
        return result

    yield _create_resolver
    for api_id, type_name, field_name in resolvers:
        try:
            aws_client.appsync.delete_resolver(
                apiId=api_id, typeName=type_name, fieldName=field_name
            )
        except Exception as e:
            LOG.debug("Error deleting resolver: %s", e)


@pytest.fixture(
    params=[
        {
            "integration_type": DYNAMODB_DATA_SOURCE_TYPE,
            "mutation_request_template": DYNAMODB_MUTATION_REQUEST_TEMPLATE,
            "mutation_result_template": JSON_RESULT_TEMPLATE,
            "query_request_template": DYNAMODB_QUERY_REQUEST_TEMPLATE,
            "query_result_template": JSON_RESULT_TEMPLATE,
        },
        {
            "integration_type": LAMBDA_DATA_SOURCE_TYPE,
            "mutation_request_template": LAMBDA_MUTATION_REQUEST_TEMPLATE,
            "mutation_result_template": JSON_RESULT_TEMPLATE,
            "query_request_template": LAMBDA_QUERY_REQUEST_TEMPLATE,
            "query_result_template": JSON_RESULT_TEMPLATE,
        },
        {
            "integration_type": RDS_DATA_SOURCE_TYPE,
            "mutation_request_template": RDS_MUTATION_REQUEST_TEMPLATE,
            "mutation_result_template": RDS_MUTATION_RESULT_TEMPLATE,
            "query_request_template": RDS_QUERY_REQUEST_TEMPLATE,
            "query_result_template": RDS_QUERY_RESULT_TEMPLATE,
        },
        {
            "integration_type": HTTP_DATA_SOURCE_TYPE,
            "mutation_request_template": HTTP_MUTATION_REQUEST_TEMPLATE,
            "mutation_result_template": HTTP_RESULT_TEMPLATE,
            "query_request_template": HTTP_QUERY_REQUEST_TEMPLATE,
            "query_result_template": HTTP_RESULT_TEMPLATE,
        },
    ]
)
def appsync_integrated_service(
    request, dynamodb_create_table, rds_create_db_cluster, s3_create_bucket, httpserver, aws_client
):
    match request.param["integration_type"]:
        case "AMAZON_DYNAMODB":
            table_name = f"appsync-table-{short_uid()}"
            dynamodb_create_table(table_name=table_name, partition_key="name")
            yield {"table_name": table_name, **request.param}
        case "AWS_LAMBDA":
            func_name = f"appsync-func-{short_uid()}"
            bucket_name = f"appsync-bucket-{short_uid()}"
            test_lambda_code = TEST_LAMBDA.replace("<bucket_name>", bucket_name)
            # TODO eventually refactor this to use fixtures
            zip_file = create_lambda_archive(test_lambda_code, get_content=True)
            lambda_arn = create_lambda_function(
                client=aws_client.lambda_, func_name=func_name, zip_file=zip_file
            )["CreateFunctionResponse"]["FunctionArn"]
            yield {"lambda_arn": lambda_arn, **request.param}

            # cleanup
            aws_client.lambda_.delete_function(FunctionName=func_name)
            list_response = aws_client.s3.list_objects_v2(Bucket=bucket_name)
            for k in list_response["Contents"]:
                aws_client.s3.delete_object(Bucket=bucket_name, Key=k["Key"])
            aws_client.s3.delete_bucket(Bucket=bucket_name)
        case "RELATIONAL_DATABASE":
            db_pass = f"pass-{short_uid()}"
            rds_create_db_cluster(
                MasterUsername=f"appsync-user-{short_uid()}",
                MasterUserPassword=db_pass,
                DBClusterIdentifier=TEST_RDS_CLUSTER_ID,
                Engine="aurora-postgresql",
                DatabaseName=TEST_RDS_DB_NAME,
            )
            secret = aws_client.secretsmanager.create_secret(
                Name=f"rds-password-{short_uid()}", SecretString=db_pass
            )
            yield {"secret_arn": secret["ARN"], **request.param}

            # cleanup
            aws_client.secretsmanager.delete_secret(SecretId=secret["ARN"])
        case "HTTP":

            def handler(request):
                data = request.data
                if request.method == "POST":
                    cache["request"] = request
                else:
                    data = f"[{to_str(cache['request'].data)}]"
                return Response(response=data, headers=dict(request.headers))

            cache = {}
            httpserver.expect_request("/my/path", method="POST").respond_with_handler(handler)
            httpserver.expect_request("/my/path2", method="GET").respond_with_handler(handler)
            yield {"endpoint": f"http://localhost:{httpserver.port}", **request.param}

        case _:
            yield request.param


@dataclass(frozen=True)
class TokenSet:
    id_token: str
    access_token: str


@pytest.fixture()
def appsync_create_user_pool_with_users(aws_client):
    user_pools = []

    def _create_user_pool_client():
        pool_name = f"test-user-pool-{short_uid()}"
        user_pool = aws_client.cognito_idp.create_user_pool(PoolName=pool_name)["UserPool"]
        user_pools.append(user_pool["Id"])
        client = aws_client.cognito_idp.create_user_pool_client(
            UserPoolId=user_pool["Id"],
            ClientName=f"test-client-{short_uid()}",
            ExplicitAuthFlows=[
                "ALLOW_ADMIN_USER_PASSWORD_AUTH",
                "ALLOW_USER_PASSWORD_AUTH",
                "ALLOW_REFRESH_TOKEN_AUTH",
            ],
        )
        return user_pool, client["UserPoolClient"]

    def _create_cognito_users(add_to_groups: bool = True):
        # Create Cognito Users in groups
        user_pool, client = _create_user_pool_client()
        client_id = client["ClientId"]

        admin_name = f"admin-{short_uid()}"
        guest_name = f"guest-{short_uid()}"
        admin_password = f"P4SSwd-{short_uid()}"
        guest_password = f"P4SSwd-{short_uid()}"
        aws_client.cognito_idp.sign_up(
            ClientId=client_id,
            Username=admin_name,
            Password=admin_password,
        )
        aws_client.cognito_idp.sign_up(
            ClientId=client_id,
            Username=guest_name,
            Password=guest_password,
        )
        aws_client.cognito_idp.admin_confirm_sign_up(
            UserPoolId=user_pool["Id"], Username=admin_name
        )
        aws_client.cognito_idp.admin_confirm_sign_up(
            UserPoolId=user_pool["Id"], Username=guest_name
        )

        def _waiter(username: str):
            user = aws_client.cognito_idp.admin_get_user(
                UserPoolId=user_pool["Id"], Username=username
            )
            return user["Enabled"] and user["UserStatus"] == "CONFIRMED"

        poll_condition(lambda: _waiter(admin_name), timeout=60)
        poll_condition(lambda: _waiter(guest_name), timeout=60)

        admin_group, guest_group = None, None
        if add_to_groups:
            # Create Cognito Groups
            admin_group = COGNITO_GROUP_ADMINS
            guest_group = COGNITO_GROUP_GUESTS
            aws_client.cognito_idp.create_group(UserPoolId=user_pool["Id"], GroupName=admin_group)
            aws_client.cognito_idp.create_group(UserPoolId=user_pool["Id"], GroupName=guest_group)
            aws_client.cognito_idp.admin_add_user_to_group(
                UserPoolId=user_pool["Id"], Username=admin_name, GroupName=admin_group
            )
            aws_client.cognito_idp.admin_add_user_to_group(
                UserPoolId=user_pool["Id"], Username=guest_name, GroupName=guest_group
            )

        # Create Tokens
        result = aws_client.cognito_idp.initiate_auth(
            AuthFlow="USER_PASSWORD_AUTH",
            ClientId=client_id,
            AuthParameters={"USERNAME": admin_name, "PASSWORD": admin_password},
        )
        admin_token_set = TokenSet(
            id_token=result["AuthenticationResult"]["IdToken"],
            access_token=result["AuthenticationResult"]["AccessToken"],
        )

        result = aws_client.cognito_idp.initiate_auth(
            AuthFlow="USER_PASSWORD_AUTH",
            ClientId=client_id,
            AuthParameters={"USERNAME": guest_name, "PASSWORD": guest_password},
        )
        guest_token_set = TokenSet(
            id_token=result["AuthenticationResult"]["IdToken"],
            access_token=result["AuthenticationResult"]["AccessToken"],
        )

        return admin_token_set, guest_token_set, user_pool, admin_group, guest_group

    yield _create_cognito_users

    for pool_id in user_pools:
        try:
            aws_client.cognito_idp.delete_user_pool(UserPoolId=pool_id)
        except Exception as e:
            LOG.info("Unable to clean up Cognito resources: %s", e)


@pytest.fixture
def appsync_create_api_key(appsync_create_api, aws_client):
    api_keys: list[tuple[str, str]] = []

    def _create(api_id: str):
        res = aws_client.appsync.create_api_key(apiId=api_id)["apiKey"]
        api_keys.append((api_id, res["id"]))
        return res

    yield _create

    for api_id, api_key in api_keys:
        try:
            aws_client.appsync.delete_api_key(apiId=api_id, id=api_key)
        except ClientError:
            LOG.warning("error deleting api key", exc_info=True)


@pytest.fixture()
def appsync_create_api_key_with_iam_users(
    appsync_create_api_key,
    appsync_create_user_pool_with_users,
    create_user_with_policy,
    aws_client,
    account_id,
):
    def _create_api_key_with_iam_users(api_id):
        api_key = appsync_create_api_key(api_id)["id"]

        admin_token_set, guest_token_set, _, _, _ = appsync_create_user_pool_with_users()
        # create IAM access key ID
        resource = f"arn:aws:appsync:{aws_client.appsync.meta.region_name}:{account_id}:apis/{api_id}/types/*"
        keys = create_user_with_policy("Allow", ["appsync:GraphQL"], resource)[1]
        access_key = keys["AccessKeyId"]

        return api_key, admin_token_set, guest_token_set, access_key

    return _create_api_key_with_iam_users
