import base64
import datetime
import json
import logging
import os
import re
import textwrap
import time
import uuid
from queue import Queue
from typing import TYPE_CHECKING, Any
from urllib.parse import urlparse

import pytest
import requests
import websockets
from botocore.exceptions import ClientError
from localstack.aws.connect import ServiceLevelClientFactory
from localstack.constants import TAG_KEY_CUSTOM_ID
from localstack.utils.aws.request_context import mock_aws_request_headers

if TYPE_CHECKING:
    from mypy_boto3_appsync import AppSyncClient

from botocore.auth import SigV4Auth
from localstack import config
from localstack.aws.api.lambda_ import Runtime
from localstack.config import in_docker
from localstack.pro.core.services.appsync.data_sources import DataSourceHandler
from localstack.pro.core.services.appsync.resolvers import (
    ResolverProcessingContext,
    render_template,
)
from localstack.pro.core.utils.aws.aws_utils import HEADER_API_KEY
from localstack.testing.aws.util import is_aws_cloud
from localstack.testing.pytest import markers
from localstack.utils.asyncio import AsyncThread
from localstack.utils.collections import select_attributes
from localstack.utils.strings import short_uid, to_str
from localstack.utils.sync import retry, wait_until
from localstack.utils.testutil import assert_objects, create_lambda_archive

from .conftest import PIPELINE_RESOLVER_SCHEMA, TEST_RDS_CLUSTER_ID, TEST_RDS_DB_NAME, TEST_SCHEMA

LOG = logging.getLogger(__name__)

LAMBDA_AUTHORIZATION_HANDLER = """
def handler(event, context):
    if event.get("authorizationToken") != "valid_token":
        return {}
    return {"isAuthorized": True, "deniedFields": [], "resolverContext": {"userId": "testUserId"}}
"""


def prepend_assertion_functions(original_source: str) -> str:
    """
    Bundle a standard library of sorts of assertion functions for use within
    javascript resolvers
    """
    if is_aws_cloud():
        # use utilities from the util package
        target_specific_assert_code = """
        function assertEqual(value, expected, message) {
          if (value !== expected) {
              util.error("Assertion failed", "AssertionError", null, { value, expected, message });
          }
        }

        """
    else:
        # TODO: add implementation functions to the util package
        target_specific_assert_code = """
        function assertEqual(value, expected, message) {
          if (value !== expected) {
            throw { message: "Assertion failed", type: "AssertionError", data: null, extra: { value, expected, message }};
          }
        }
        """

    imports = """
    import { util } from '@aws-appsync/utils';
    """
    general_assert_code = """
    function assertTypeOf(value, expectedType, message) {
        assertEqual(typeof(value), expectedType, message);
    }
    function assertTrue(condition, message) {
        assertEqual(condition, true, message);
    }
    """
    full_code = "\n".join(
        [
            imports,
            target_specific_assert_code,
            general_assert_code,
            textwrap.dedent(original_source).strip(),
        ]
    )
    return full_code


@pytest.fixture(
    params=[("id", False), ("id", True), ("access", False), ("access", True)],
    ids=[
        "id no bearer",
        "id with bearer",
        "access no bearer",
        "access with bearer",
    ],
)
def api_with_bearer_token(request, appsync_create_api, appsync_create_api_key_with_iam_users):
    appsync_graphql_api = appsync_create_api(authenticationType="AMAZON_COGNITO_USER_POOLS")
    api_id = appsync_graphql_api["apiId"]
    token_set = appsync_create_api_key_with_iam_users(api_id)[2]

    token_type, with_bearer = request.param
    if token_type == "id":
        token = token_set.id_token
    elif token_type == "access":
        token = token_set.access_token
    else:
        raise NotImplementedError

    if with_bearer:
        token = f"Bearer {token}"

    return api_id, token


@pytest.fixture
def create_dynamodb_table(aws_client):
    tables = []

    def _create(table_name: str, *args, **kwargs):
        tables.append(table_name)
        res = aws_client.dynamodb.create_table(TableName=table_name, *args, **kwargs)
        aws_client.dynamodb.get_waiter("table_exists").wait(TableName=table_name)
        return res

    yield _create

    for table_name in tables[::-1]:
        try:
            aws_client.dynamodb.delete_table(TableName=table_name)
            aws_client.dynamodb.get_waiter("table_not_exists").wait(TableName=table_name)
        except Exception:
            LOG.debug(
                "failed to delete dynamo table %s",
                table_name,
                exc_info=LOG.isEnabledFor(logging.DEBUG),
            )


@pytest.fixture
def create_function(aws_client):
    functions = []

    def _create(api_id: str, *args, **kwargs):
        function = aws_client.appsync.create_function(apiId=api_id, *args, **kwargs)
        function_id = function["functionConfiguration"]["functionId"]
        functions.append((api_id, function_id))
        return function

    yield _create

    for api_id, function_id in functions[::-1]:
        aws_client.appsync.delete_function(apiId=api_id, functionId=function_id)


@pytest.fixture
def create_graphql_schema(aws_client):
    def _create(api_id: str, **kwargs):
        api_id = api_id or kwargs.pop("apiId")
        result = aws_client.appsync.start_schema_creation(apiId=api_id, **kwargs)
        wait_until_schema_ready(api_id=api_id, aws_client=aws_client)
        return result

    return _create


def wait_until_schema_ready(api_id: str, aws_client):
    def is_schema_ready():
        status = aws_client.appsync.get_schema_creation_status(apiId=api_id)["status"]
        if status == "FAILED":
            raise Exception("Schema creation failed")
        return status in ("ACTIVE", "SUCCESS")

    wait_until(is_schema_ready)


class TestAppSync:
    """Tests for AppSync APIs using proper backend data sources, resolvers, auth configs, etc"""

    @markers.only_on_amd64
    @pytest.mark.skip(reason="Flaky, temporarily skipped")
    @markers.aws.unknown
    def test_integration_and_request(
        self,
        appsync_graphql_api,
        appsync_integrated_service,
        appsync_create_api_key_with_iam_users,
        create_graphql_schema,
        aws_client,
        region_name,
    ):
        api_id = appsync_graphql_api["apiId"]
        integration_type = appsync_integrated_service.get("integration_type")

        if integration_type == "RELATIONAL_DATABASE" and not in_docker():
            pytest.skip("RDS integration is only supposed to work in Docker")

        # Create some test schema in API handling posts with names
        create_graphql_schema(api_id=api_id, definition=TEST_SCHEMA)

        # Create API Key
        (
            api_key,
            admin_token_set,
            guest_token_set,
            access_key,
        ) = appsync_create_api_key_with_iam_users(api_id)

        # Receive schema in JSON format
        result = aws_client.appsync.get_introspection_schema(apiId=api_id, format="JSON")
        schema = json.loads(to_str(result["schema"].read()))
        assert "data" in schema
        assert schema["data"].get("__schema")

        # Create data source
        data_source_name = f"source-{short_uid()}"

        match integration_type:
            case "AMAZON_DYNAMODB":
                aws_client.appsync.create_data_source(
                    apiId=api_id,
                    name=data_source_name,
                    type="AMAZON_DYNAMODB",
                    dynamodbConfig={
                        "awsRegion": region_name,
                        "tableName": appsync_integrated_service["table_name"],
                    },
                )
            case "AWS_LAMBDA":
                aws_client.appsync.create_data_source(
                    apiId=api_id,
                    name=data_source_name,
                    type="AWS_LAMBDA",
                    lambdaConfig={"lambdaFunctionArn": appsync_integrated_service["lambda_arn"]},
                )
            case "RELATIONAL_DATABASE":
                aws_client.appsync.create_data_source(
                    apiId=api_id,
                    name=data_source_name,
                    type="RELATIONAL_DATABASE",
                    relationalDatabaseConfig={
                        "rdsHttpEndpointConfig": {
                            "databaseName": TEST_RDS_DB_NAME,
                            "dbClusterIdentifier": TEST_RDS_CLUSTER_ID,
                            "awsSecretStoreArn": appsync_integrated_service["secret_arn"],
                        }
                    },
                )
            case "HTTP":
                aws_client.appsync.create_data_source(
                    apiId=api_id,
                    name=data_source_name,
                    type="HTTP",
                    httpConfig={"endpoint": appsync_integrated_service["endpoint"]},
                )
            case _:
                pytest.fail(f"Unknown integration type: {integration_type}")

        # Create Query Resolver
        response = aws_client.appsync.create_resolver(
            apiId=api_id,
            typeName="Query",
            fieldName="getPosts",
            dataSourceName=data_source_name,
            requestMappingTemplate=appsync_integrated_service["query_request_template"],
            responseMappingTemplate=appsync_integrated_service["query_result_template"],
        )
        assert "resolver" in response

        # Test List Resolvers
        response = aws_client.appsync.list_resolvers(apiId=api_id, typeName="Query")
        assert len(response["resolvers"]) == 1

        # Create Mutation Resolvers
        for field in ["addPost", "addPostObj"]:
            aws_client.appsync.create_resolver(
                apiId=api_id,
                typeName="Mutation",
                fieldName=field,
                dataSourceName=data_source_name,
                requestMappingTemplate=appsync_integrated_service["mutation_request_template"],
                responseMappingTemplate=appsync_integrated_service["mutation_result_template"],
            )

        # Test Get Resolver
        aws_client.appsync.get_resolver(apiId=api_id, typeName="Mutation", fieldName="addPostObj")

        # Request URL
        url = f"{config.internal_service_url()}/graphql/{api_id}"

        # Assert API Key Auth required
        unauthenticated_request = json.dumps({"query": "query { getPosts{name,time} }"})
        result = requests.post(
            url, data=unauthenticated_request, headers={HEADER_API_KEY: "invalid-key"}
        )
        assert (
            result.status_code == 401
        ), f"Expected AppSync request to fail with invalid API key (received code {result.status_code})"

        test_runs = [f"with-value-{short_uid()}", f"with-variable-{short_uid()}"]
        auth_headers_admin = {
            HEADER_API_KEY: api_key,
            "Authorization": f"Bearer {admin_token_set.id_token}",
        }
        auth_headers_guest = {
            HEADER_API_KEY: api_key,
            "Authorization": f"Bearer {guest_token_set.id_token}",
        }

        for test_run in test_runs:
            # Do Mutation
            match integration_type:
                case "AMAZON_DYNAMODB":
                    mutation_query = "addPostObj(post: {{name: {0}}})"
                case _:
                    mutation_query = "addPost(name: {0})"

            variable_definitions = ""
            variables = {}
            if "with-variable" in test_run:
                mutation_query = mutation_query.format("$name")
                variable_definitions = "($name: String!)"
                variables = {"name": test_run}
            else:
                mutation_query = mutation_query.format(f'"{test_run}"')

            mutation_request = json.dumps(
                {
                    "query": f"mutation {variable_definitions} {{ {mutation_query}{{name}} }}",
                    "variables": variables,
                }
            )

            result = requests.post(url, data=mutation_request, headers=auth_headers_admin)
            assert (
                result.status_code < 400
            ), f"AppSync request failed ({result.status_code}): {result.content}"

            content = json.loads(to_str(result.content))
            assert "errors" not in content

            result = requests.post(url, data=mutation_request, headers=auth_headers_guest)
            assert (
                result.status_code == 200
            ), "Access should be granted to guest users with a valid API Key"

            result = requests.post(
                url,
                data=mutation_request,
                headers=select_attributes(auth_headers_guest, ["Authorization"]),
            )
            assert (
                "errors" in result.json()
            ), "Access should not be granted to guest users without a valid API Key"

            # Do Query
            query_request = {"query": "query { getPosts{name,time} }"}

            result = requests.post(url, json=query_request, headers={HEADER_API_KEY: api_key})
            assert (
                result.status_code < 400
            ), f"AppSync request failed ({result.status_code}): {result.content}"

            content = json.loads(to_str(result.content))
            assert "errors" not in content
            assert {"name": test_run, "time": 123} in content["data"]["getPosts"]

            result = requests.post(url, json=query_request)
            assert result.status_code == 401, "Access should be denied without IAM user"
            auth_header = mock_aws_request_headers(
                service="appsync",
                aws_access_key_id=access_key,
                region_name=region_name,
            )
            headers = select_attributes(auth_header, ["Authorization"])
            result = requests.post(url, json=query_request, headers=headers)
            assert result
            content = json.loads(to_str(result.content))
            # TODO: "time" attribute is currently replaced with None - should be removed entirely from result!
            assert {"name": test_run, "time": None} in content["data"][
                "getPosts"
            ], "Access should be granted with IAM user"

    @markers.aws.unknown
    def test_dynamodb_resolvers(self, dynamodb_create_table):
        table_name = f"table-{short_uid()}"
        dynamodb_create_table(table_name=table_name, partition_key="name")
        data_source = {"dynamodbConfig": {"tableName": table_name}}

        handler = DataSourceHandler.get("AMAZON_DYNAMODB")

        # test PutItem
        request = {"operation": "PutItem", "key": {"name": {"S": "123"}}, "attributeValues": {}}
        handler.send_request(data_source, request)
        request = {"operation": "PutItem", "key": {"name": {"S": "abc"}}, "attributeValues": {}}
        handler.send_request(data_source, request)

        # test BatchPutItem
        request = {
            "operation": "BatchPutItem",
            "tables": {
                table_name: [
                    {"name": {"S": "batch1"}},
                    {"name": {"S": "batch2"}},
                    {"name": {"S": "batch3"}},
                    {"name": {"S": "map"}, "map": {"M": {"foo": {"S": "t"}}}},
                ]
            },
        }
        result = handler.send_request(data_source, request)
        assert result == {
            "data": {
                table_name: [
                    {"name": "batch1"},
                    {"name": "batch2"},
                    {"name": "batch3"},
                    {"name": "map", "map": {"foo": "t"}},
                ]
            },
            "unprocessedItems": {},
        }

        # test GetItem
        request = {"operation": "GetItem", "key": {"name": {"S": "abc"}}}
        result = handler.send_request(data_source, request)
        assert result == {"name": "abc"}

        # test UpdateItem
        request = {
            "operation": "UpdateItem",
            "key": {"name": {"S": "abc"}},
            "update": {
                "expression": "SET test = :test",
                "expressionValues": {":test": {"S": "test"}},
            },
        }
        result = handler.send_request(data_source, request)
        assert result == {}

        # test Query
        request = {
            "operation": "Query",
            "query": {
                "expression": "#name = :name",
                "expressionNames": {"#name": "name"},
                "expressionValues": {":name": {"S": "123"}},
            },
        }
        result = handler.send_request(data_source, request)
        assert_objects([{"name": "123"}], result)

        # test Scan
        request = {"operation": "Scan", "query": {"consistentRead": True}}
        result = handler.send_request(data_source, request)
        assert_objects(
            [
                {"name": "123"},
                {"name": "abc", "test": "test"},
                {"name": "batch1"},
                {"name": "batch2"},
                {"name": "batch3"},
                {"name": "map", "map": {"foo": "t"}},
            ],
            result,
        )

        # test TransactWriteItems
        request = {
            "operation": "TransactWriteItems",
            "transactItems": [
                {
                    "table": table_name,
                    "operation": "PutItem",
                    "key": {"name": {"S": "def"}},
                    "condition": {"expression": "attribute_not_exists(name)"},
                    "attributeValues": {"attr1": {"S": "value1"}},
                }
            ],
        }
        result = handler.send_request(data_source, request)
        assert "keys" in result

    @markers.aws.validated
    def test_query_before_definition(
        self,
        appsync_create_api,
        appsync_create_api_key,
        create_graphql_schema,
        aws_client,
        snapshot,
    ):
        # get API and request headers
        appsync_graphql_api = appsync_create_api()
        api_id = appsync_graphql_api["apiId"]
        api_key = appsync_create_api_key(api_id)["id"]

        # create test schema
        schema = """
                type Data {
                  a: Int
                  b: Int
                  c: Int
                }
                type Query {
                  data: Data!
                }
                """
        create_graphql_schema(api_id=api_id, definition=schema)

        # create data source
        aws_client.appsync.create_data_source(
            apiId=api_id,
            name="ds1",
            type="NONE",
        )

        # create resolver
        aws_client.appsync.create_resolver(
            apiId=api_id,
            typeName="Query",
            fieldName="data",
            dataSourceName="ds1",
            requestMappingTemplate="""{
                  "version": "2017-02-28",
                  "payload": {}
                }""",
            responseMappingTemplate="""
                {
                  "a": 1,
                  "b": 2,
                  "c": 3
                }
                    """,
        )

        query_request = {
            "query": "{ data { ...dataFields } } fragment dataFields on Data { a b c } "
        }
        url = appsync_graphql_api["uris"]["GRAPHQL"]

        # run query
        def run_query():
            headers = {"x-api-key": api_key}
            result = requests.post(url, json=query_request, headers=headers)
            result.raise_for_status()
            return result

        result = retry(run_query, sleep=1, retries=10)
        content = to_str(result.content)
        assert result.ok
        snapshot.match("result", json.loads(content))

    @markers.aws.validated
    def test_none_resolver(
        self,
        appsync_create_api,
        appsync_create_api_key,
        create_graphql_schema,
        aws_client,
        snapshot,
    ):
        # get API and request headers
        appsync_graphql_api = appsync_create_api()
        api_id = appsync_graphql_api["apiId"]
        api_key = appsync_create_api_key(api_id)["id"]

        # create test schema
        schema = """
        type Response {
          some: String!
        }
        type Query {
          test: Response!
        }
        """
        create_graphql_schema(api_id=api_id, definition=schema)

        # create data source
        aws_client.appsync.create_data_source(
            apiId=api_id,
            name="ds1",
            type="NONE",
        )

        # create resolver
        aws_client.appsync.create_resolver(
            apiId=api_id,
            typeName="Query",
            fieldName="test",
            dataSourceName="ds1",
            requestMappingTemplate="""{
                "version": "2018-05-29",
                "payload": $utils.toJson({ "some": "value" })
            }""",
            responseMappingTemplate="""
            $utils.toJson($ctx.result)
            """,
        )

        query_request = {"query": "query { test { some }}"}
        url = appsync_graphql_api["uris"]["GRAPHQL"]

        # run query
        def run_query():
            headers = {"x-api-key": api_key}
            result = requests.post(url, json=query_request, headers=headers)
            result.raise_for_status()
            return result

        result = retry(run_query, sleep=1, retries=10)
        content = to_str(result.content)
        assert result.ok
        snapshot.match("result", json.loads(content))

    @markers.aws.unknown
    def test_websocket_subscriptions_relay_sample(
        self, appsync_create_api_key, deploy_cfn_template, aws_client, snapshot
    ):
        mappings = {"api_key_expiry": "3000000001", "req_key_id": "$context.args.input.id"}
        # deploy AppSync app via CF
        result = deploy_cfn_template(
            template_path=os.path.join(
                os.path.dirname(__file__), "../../templates/appsync.sample.yml"
            ),
            template_mapping=mappings,
        )
        stack_name = result.stack_name

        def get_api_id():
            resources = aws_client.cloudformation.describe_stack_resources(StackName=stack_name)
            resources = resources["StackResources"]
            resource = [r for r in resources if r["ResourceType"] == "AWS::AppSync::GraphQLApi"]
            assert resource
            # TODO: we'd expect "CREATE_COMPLETE" here, but looks like we're seeing "UPDATE_COMPLETE" in CI
            assert resource[0]["ResourceStatus"] in ["CREATE_COMPLETE", "UPDATE_COMPLETE"]
            api_arn = resource[0]["PhysicalResourceId"]
            assert api_arn
            api_id = api_arn.split("/")[-1]
            return api_id

        # get AppSync GraphQL API ID
        api_id = retry(get_api_id, retries=6, sleep=2)

        # assert that API key has been created via CFN
        def _assert_api_key():
            keys = aws_client.appsync.list_api_keys(apiId=api_id).get("apiKeys", [])
            assert len(keys) == 1
            assert keys[0].get("description") == f"Generated API key for AppSync API ID {api_id}"
            outputs = aws_client.cloudformation.describe_stacks(StackName=stack_name)["Stacks"][0][
                "Outputs"
            ]
            cfn_api_key = [o["OutputValue"] for o in outputs if o["OutputKey"] == "AppSyncApiKey"]
            assert cfn_api_key[0] == keys[0]["id"]

        _assert_api_key()
        # re-deploy stack with updated API key expiry, assert that still 1 API key exists, and that resolver is updated
        mappings = {"api_key_expiry": "3000000001", "req_key_id": "$context.args.input.id"}
        deploy_cfn_template(
            template_path=os.path.join(
                os.path.dirname(__file__), "../../templates/appsync.sample.yml"
            ),
            template_mapping=mappings,
            stack_name=stack_name,
            is_update=True,
        )
        _assert_api_key()
        # check resolvers
        resolver = aws_client.appsync.get_resolver(
            apiId=api_id, typeName="Mutation", fieldName="createTodo"
        )
        template = resolver["resolver"]["requestMappingTemplate"]
        assert "toDynamoDBJson($context.args.input.id)" in template
        assert "toDynamoDBJson($context.args.input.invalid-id)" not in template

        # create API key
        api_key = appsync_create_api_key(api_id).get("id")

        # get AppSync websocket URL
        result = aws_client.appsync.get_graphql_api(apiId=api_id)
        api_url = result["graphqlApi"]["uris"].get("GRAPHQL")
        ws_url = result["graphqlApi"]["uris"].get("REALTIME")

        async def start_client(uri, msg):
            async with websockets.connect(uri) as websocket:
                await websocket.send(msg)
                result = await websocket.recv()
                queue.put(result)

        # start subscription client
        queue = Queue()
        subscribe_message = "subscription mySub {createdTodo {id}}"

        def async_func_gen(loop, shutdown_event):
            return start_client(ws_url, subscribe_message)

        AsyncThread.run_async(async_func_gen)
        # allow sufficient time for the WS subscription to initialize
        time.sleep(3)

        # trigger mutation query
        test_id = short_uid()
        data = {"query": 'mutation {createTodo(input: {id: "%s"}){id}}' % test_id}
        result = requests.post(api_url, data=json.dumps(data), headers={HEADER_API_KEY: api_key})
        assert result

        # assert that mutation details are received from subscription
        result = queue.get(timeout=4)
        assert result == json.dumps({"createdTodo": {"id": test_id}})

    @markers.aws.validated
    @pytest.mark.skip(reason="WIP")
    def test_websocket_subscriptions(
        self,
        appsync_graphql_api,
        appsync_create_api_key,
        create_graphql_schema,
        aws_client,
        snapshot,
    ):
        api_id = appsync_graphql_api["apiId"]
        api_key = appsync_create_api_key(api_id=api_id)["id"]

        schema = """
        type Item {
            id: ID!
        }

        type Query {
            dummy: String
        }

        type Mutation {
            create(id: ID!): Item!
        }

        type Subscription {
            created: Item
            @aws_subscribe(mutations: ["create"])
        }

        schema {
            query: Query
            mutation: Mutation
            subscription: Subscription
        }
        """
        create_graphql_schema(api_id=api_id, definition=schema)

        # create data source
        ds_name = f"ds{short_uid()}"
        aws_client.appsync.create_data_source(
            apiId=api_id,
            name=ds_name,
            type="NONE",
        )

        # create mutation resolver
        aws_client.appsync.create_resolver(
            apiId=api_id,
            typeName="Mutation",
            fieldName="create",
            dataSourceName=ds_name,
            requestMappingTemplate="""{
                "version": "2017-02-28",
                "payload": $utils.toJson($ctx.arguments)
            }""",
            responseMappingTemplate="$utils.toJson($context.result)",
        )

        api_url = appsync_graphql_api["uris"]["GRAPHQL"]
        ws_url = appsync_graphql_api["uris"]["REALTIME"]

        # start subscription client
        subscribe_message = """
        subscription MySub {
            created {
                id
            }
        }
        """
        queue = Queue()

        async def start_client(uri, subscription_msg, queue):
            host_header_value = urlparse(api_url).hostname
            headers = base64.b64encode(
                json.dumps(
                    {
                        "host": host_header_value,
                        "x-api-key": api_key,
                    }
                ).encode()
            ).decode()
            payload = base64.b64encode(json.dumps({}).encode()).decode()
            appsync_realtime_uri = f"{ws_url}?header={headers}&payload={payload}"
            LOG.warning("Realtime URL: %s", appsync_realtime_uri)
            try:
                async with websockets.connect(
                    appsync_realtime_uri, subprotocols=["graphql-ws"]
                ) as websocket:
                    # send init message
                    await websocket.send(
                        json.dumps(
                            {
                                "type": "connection_init",
                            }
                        )
                    )
                    init_response = json.loads(await websocket.recv())
                    assert init_response["type"] == "connection_ack"

                    # create the subscription
                    subscription_payload = {
                        "id": str(uuid.uuid4()),
                        "type": "start",
                        "payload": {
                            "data": json.dumps(
                                {
                                    "query": subscription_msg,
                                    "variables": {},
                                }
                            ),
                            "extensions": {
                                "authorization": {
                                    "x-api-key": api_key,
                                    "host": host_header_value,
                                },
                            },
                        },
                    }
                    await websocket.send(json.dumps(subscription_payload))

                    while True:
                        result = await websocket.recv()
                        if json.loads(result)["type"] in {"ka", "start_ack"}:
                            continue

                        queue.put(result)
            except Exception:
                LOG.exception("websocket subscriber failed")

        def async_func_gen(loop, shutdown_event):
            return start_client(ws_url, subscribe_message, queue)

        AsyncThread.run_async(async_func_gen)
        # allow sufficient time for the WS subscription to initialize
        time.sleep(3)

        # trigger mutation query
        test_id = short_uid()
        snapshot.add_transformer(snapshot.transform.regex(test_id, "<test-id>"))

        payload = {
            "query": """
            mutation MyMutation($id:ID!) {
                create(id:$id) {
                    id
                }
            }
            """,
            "variables": {
                "id": test_id,
            },
        }

        result = requests.post(api_url, json=payload, headers={HEADER_API_KEY: api_key})
        snapshot.match("response", {"status_code": result.status_code, "body": result.json()})

        # assert that mutation details are received from subscription
        result = queue.get(timeout=4)
        snapshot.match("websocket-result", result)

    @markers.aws.validated
    def test_lambda_authorization(
        self,
        appsync_create_api,
        create_lambda_function,
        create_graphql_schema,
        create_role_with_policy_for_principal,
        aws_client,
    ):
        # create authorizer Lambda
        function_name = f"test-appsync-auth-{short_uid()}"
        response = create_lambda_function(
            func_name=function_name, handler_file=LAMBDA_AUTHORIZATION_HANDLER
        )
        function_arn = response["CreateFunctionResponse"]["FunctionArn"]

        # get API and request headers
        appsync_graphql_api = appsync_create_api(
            authenticationType="AWS_LAMBDA",
            lambdaAuthorizerConfig={"authorizerUri": function_arn},
        )
        api_id = appsync_graphql_api["apiId"]

        # grant AppSync API access to invoke the authorizer Lambda
        aws_client.lambda_.add_permission(
            FunctionName=function_name,
            StatementId=f"s-{short_uid()}",
            Action="lambda:InvokeFunction",
            Principal="appsync.amazonaws.com",
            SourceArn=appsync_graphql_api["arn"],
        )
        _, role_arn = create_role_with_policy_for_principal(
            principal={"Service": "appsync.amazonaws.com"},
            resource=function_arn,
            effect="Allow",
            actions=["lambda:InvokeFunction"],
        )

        # create test schema
        schema = " type Query { test: String @aws_lambda } "
        create_graphql_schema(api_id=api_id, definition=schema)

        # create data source
        aws_client.appsync.create_data_source(
            apiId=api_id,
            name="ds1",
            type="AWS_LAMBDA",
            lambdaConfig={"lambdaFunctionArn": function_arn},
            serviceRoleArn=role_arn,
        )

        # create resolver
        aws_client.appsync.create_resolver(
            apiId=api_id,
            typeName="Query",
            fieldName="test",
            dataSourceName="ds1",
            requestMappingTemplate="""{
                "version": "2017-02-28",
                "operation": "Invoke",
                "payload": {
                    "field": "test",
                    "arguments": $utils.toJson($context.arguments)
                }
            }""",
            responseMappingTemplate="$utils.toJson($context.result)",
        )

        # run query - invalid credentials
        query_request = {"query": "query { test }"}
        url = appsync_graphql_api["uris"]["GRAPHQL"]
        result = requests.post(
            url, json=query_request, headers={"Authorization": "invalidtoken123"}
        )
        assert not result.ok
        assert result.status_code == 401
        expected = {
            "errorType": "UnauthorizedException",
            "message": "You are not authorized to make this call.",
        }
        assert json.loads(to_str(result.content)) == {"errors": [expected]}

        # run query - valid credentials
        def run_query():
            headers = {"Authorization": "valid_token"}
            result = requests.post(url, json=query_request, headers=headers)
            content = to_str(result.content)
            assert result.ok
            assert "errors" not in content
            assert json.loads(content) == {"data": {"test": "{}"}}

        retry(run_query, sleep=1, retries=10)

    @markers.aws.validated
    def test_lambda_authorization_context(
        self,
        appsync_create_api,
        create_lambda_function,
        create_graphql_schema,
        create_role_with_policy_for_principal,
        aws_client,
        snapshot,
    ):
        # create authorizer Lambda
        function_name = f"test-appsync-auth-{short_uid()}"
        response = create_lambda_function(
            func_name=function_name, handler_file=LAMBDA_AUTHORIZATION_HANDLER
        )
        auth_function_arn = response["CreateFunctionResponse"]["FunctionArn"]

        # get API and request headers
        appsync_graphql_api = appsync_create_api(
            authenticationType="AWS_LAMBDA",
            lambdaAuthorizerConfig={"authorizerUri": auth_function_arn},
        )
        api_id = appsync_graphql_api["apiId"]

        # grant AppSync API access to invoke the authorizer Lambda
        aws_client.lambda_.add_permission(
            FunctionName=function_name,
            StatementId=f"s-{short_uid()}",
            Action="lambda:InvokeFunction",
            Principal="appsync.amazonaws.com",
            SourceArn=appsync_graphql_api["arn"],
        )
        _, role_arn = create_role_with_policy_for_principal(
            principal={"Service": "appsync.amazonaws.com"},
            resource=auth_function_arn,
            effect="Allow",
            actions=["lambda:InvokeFunction"],
        )

        # create test schema
        schema = """
        type Response {
          userId: String!
        }
        type Query {
          test: Response! @aws_lambda
        }
        """
        create_graphql_schema(api_id=api_id, definition=schema)

        # create data source
        aws_client.appsync.create_data_source(
            apiId=api_id,
            name="ds1",
            type="NONE",
        )

        # create resolver
        aws_client.appsync.create_resolver(
            apiId=api_id,
            typeName="Query",
            fieldName="test",
            dataSourceName="ds1",
            requestMappingTemplate="""{
                "version": "2018-05-29",
                "payload": $utils.toJson($ctx.identity.resolverContext)
            }""",
            responseMappingTemplate="""
            $utils.toJson($ctx.result)
            """,
        )

        # run query - invalid credentials
        query_request = {"query": "query { test { userId }}"}
        url = appsync_graphql_api["uris"]["GRAPHQL"]
        result = requests.post(
            url, json=query_request, headers={"Authorization": "invalidtoken123"}
        )
        assert not result.ok
        assert result.status_code == 401
        expected = {
            "errorType": "UnauthorizedException",
            "message": "You are not authorized to make this call.",
        }
        assert json.loads(to_str(result.content)) == {"errors": [expected]}

        # run query - valid credentials
        def run_query():
            headers = {"Authorization": "valid_token"}
            result = requests.post(url, json=query_request, headers=headers)
            result.raise_for_status()
            return result

        result = retry(run_query, sleep=1, retries=10)
        content = to_str(result.content)
        assert result.ok
        snapshot.match("result", json.loads(content))

    @markers.aws.validated
    def test_lambda_authorization_cross_region(
        self,
        appsync_create_api,
        create_graphql_schema,
        create_role_with_policy_for_principal,
        aws_client,
        aws_client_factory,
        lambda_su_role,
        snapshot,
        cleanups,
    ):
        other_region = (
            "us-east-1" if aws_client.appsync.meta.region_name != "us-east-1" else "us-east-2"
        )
        # create authorizer Lambda
        function_name = f"test-appsync-auth-{short_uid()}"
        lambda_archive = create_lambda_archive(LAMBDA_AUTHORIZATION_HANDLER, get_content=True)
        lambda_client = aws_client_factory(region_name=other_region).lambda_
        response = lambda_client.create_function(
            FunctionName=function_name,
            Code={"ZipFile": lambda_archive},
            Role=lambda_su_role,
            Runtime=Runtime.python3_12,
            Handler="handler.handler",
        )
        cleanups.append(lambda: lambda_client.delete_function(FunctionName=function_name))
        lambda_client.get_waiter("function_active_v2").wait(FunctionName=function_name)
        function_arn = response["FunctionArn"]

        # get API and request headers
        appsync_graphql_api = appsync_create_api(
            authenticationType="AWS_LAMBDA",
            lambdaAuthorizerConfig={"authorizerUri": function_arn},
        )
        api_id = appsync_graphql_api["apiId"]

        # grant AppSync API access to invoke the authorizer Lambda
        lambda_client.add_permission(
            FunctionName=function_name,
            StatementId=f"s-{short_uid()}",
            Action="lambda:InvokeFunction",
            Principal="appsync.amazonaws.com",
            SourceArn=appsync_graphql_api["arn"],
        )
        _, role_arn = create_role_with_policy_for_principal(
            principal={"Service": "appsync.amazonaws.com"},
            resource=function_arn,
            effect="Allow",
            actions=["lambda:InvokeFunction"],
        )

        # create test schema
        schema = " type Query { test: String @aws_lambda } "
        create_graphql_schema(api_id=api_id, definition=schema)

        # create data source
        aws_client.appsync.create_data_source(
            apiId=api_id,
            name="ds1",
            type="AWS_LAMBDA",
            lambdaConfig={"lambdaFunctionArn": function_arn},
            serviceRoleArn=role_arn,
        )

        # create resolver
        aws_client.appsync.create_resolver(
            apiId=api_id,
            typeName="Query",
            fieldName="test",
            dataSourceName="ds1",
            requestMappingTemplate="""{
                "version": "2017-02-28",
                "operation": "Invoke",
                "payload": {
                    "field": "test",
                    "arguments": $utils.toJson($context.arguments)
                }
            }""",
            responseMappingTemplate="$utils.toJson($context.result)",
        )

        # run query - invalid credentials
        query_request = {"query": "query { test }"}
        url = appsync_graphql_api["uris"]["GRAPHQL"]
        result = requests.post(
            url, json=query_request, headers={"Authorization": "invalidtoken123"}
        )
        assert not result.ok
        assert result.status_code == 401
        snapshot.match("unauthorized_error", result.json())

        # run query - valid credentials
        def run_query():
            headers = {"Authorization": "valid_token"}
            result = requests.post(url, json=query_request, headers=headers)
            content = to_str(result.content)
            assert result.ok
            assert "errors" not in content
            return json.loads(content)

        response = retry(run_query, sleep=1, retries=10)
        snapshot.match("valid_response", response)

    @markers.aws.unknown
    def test_cognito_authorization(
        self,
        appsync_create_api,
        appsync_create_api_key_with_iam_users,
        create_data_source_ddb,
        create_graphql_schema,
        aws_client,
    ):
        # get API and request headers
        appsync_graphql_api = appsync_create_api(authenticationType="AMAZON_COGNITO_USER_POOLS")
        api_id = appsync_graphql_api["apiId"]
        (
            api_key,
            admin_token_set,
            guest_token_set,
            access_key,
        ) = appsync_create_api_key_with_iam_users(api_id)
        auth_headers_guest = {"Authorization": f"Bearer {guest_token_set.id_token}"}

        # create test schema
        schema = " type Query { test: String } "
        create_graphql_schema(api_id=api_id, definition=schema)

        # create data source and resolver
        create_data_source_ddb(api_id, name="ds1")
        aws_client.appsync.create_resolver(
            apiId=api_id,
            typeName="Query",
            fieldName="test",
            dataSourceName="ds1",
        )

        # run query - invalid credentials
        query_request = json.dumps({"query": "query { test }"})
        url = f"{config.internal_service_url()}/graphql/{api_id}"
        result = requests.post(
            url, data=query_request, headers={"Authorization": "Bearer invalidtoken123"}
        )
        assert not result.ok
        assert result.status_code == 401

        # run query - valid credentials
        result = requests.post(url, data=query_request, headers=auth_headers_guest)
        assert result.ok

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(
        paths=[
            "$..data.getTest",  # our templating engine renders [] as empty string
            "$..data.getAllTest",  # our templating engine renders [] as empty string
            "$..errors..data",  # currently missing from payload, as not clear what's supposed to go there
            "$..errors..errorInfo",  # currently missing from payload, as not clear what's supposed to go there
            "$..errors..locations..sourceName",
            # currently missing from payload, as not clear what's supposed to go there
            "$..errors..message",  # not matching error message for invalid JWT, need to add actual jwt usage
        ]
    )
    def test_cognito_authorization_group_enforcement(
        self,
        appsync_create_api,
        appsync_create_user_pool_with_users,
        create_data_source_ddb,
        create_resolver,
        create_graphql_schema,
        snapshot,
        aws_client,
    ):
        """Tests proper authorization of different groups in the cognito user pool"""
        # get API and request headers
        (
            admin_token_set,
            guest_token_set,
            user_pool,
            admin_group,
            guest_group,
        ) = appsync_create_user_pool_with_users()
        appsync_graphql_api = appsync_create_api(
            authenticationType="AMAZON_COGNITO_USER_POOLS",
            userPoolConfig={
                "userPoolId": user_pool["Id"],
                "awsRegion": aws_client.cognito_idp.meta.region_name,
                "defaultAction": "DENY",
            },
        )
        api_id = appsync_graphql_api["apiId"]
        auth_headers_admin = {"Authorization": f"Bearer {admin_token_set.id_token}"}
        auth_headers_guest = {"Authorization": f"Bearer {guest_token_set.id_token}"}
        auth_headers_invalid_token = {"Authorization": "Bearer invalid"}

        # create test schema
        schema = f"""
            type Query {{
                getTest: String
                @aws_auth(cognito_groups: ["{admin_group}", "{guest_group}"])
                getAllTest: String
                @aws_auth(cognito_groups: ["{admin_group}"])
            }}
            """
        create_graphql_schema(api_id=api_id, definition=schema)

        # On AWS, we do not need to create a resolver to test auth. Since in LS, the datasource is used
        # before authorization, we need it to test it.
        # FIXME can be deleted once group authorization is properly before the execution of the request
        request_mapping_template = """
            {
                "version" : "2017-02-28",
                "operation" : "Scan"
            }"""
        response_mapping_template = "$utils.toJson($context.result.items)"
        create_data_source_ddb(api_id, name="ds1")
        create_resolver(
            apiId=api_id,
            typeName="Query",
            fieldName="getTest",
            dataSourceName="ds1",
            requestMappingTemplate=request_mapping_template,
            responseMappingTemplate=response_mapping_template,
        )
        create_resolver(
            apiId=api_id,
            typeName="Query",
            fieldName="getAllTest",
            dataSourceName="ds1",
            requestMappingTemplate=request_mapping_template,
            responseMappingTemplate=response_mapping_template,
        )

        # get url
        url = appsync_graphql_api["uris"]["GRAPHQL"]
        query_request = json.dumps({"query": "query { getTest }"})
        # run query - admin credentials
        result = requests.post(url, data=query_request, headers=auth_headers_admin)
        assert result.ok
        assert "errors" not in result.json()
        snapshot.match("query-admin-1", result.json())

        # run query - guest credentials
        result = requests.post(url, data=query_request, headers=auth_headers_guest)
        assert result.ok
        snapshot.match("query-guest-1", result.json())

        query_request = json.dumps({"query": "query { getAllTest }"})
        # run query - admin credentials
        result = requests.post(url, data=query_request, headers=auth_headers_admin)
        assert result.ok
        snapshot.match("query-admin-2", result.json())

        # run query - guest credentials
        result = requests.post(url, data=query_request, headers=auth_headers_guest)
        assert result.ok
        result_json = result.json()
        snapshot.match("query-guest-2", result_json)
        assert result_json["errors"]
        assert result_json["errors"][0]["errorType"] == "Unauthorized"

        # get both fields
        query_request = json.dumps({"query": "query { getTest getAllTest }"})
        # run query - admin credentials
        result = requests.post(url, data=query_request, headers=auth_headers_admin)
        assert result.ok
        snapshot.match("query-admin-3", result.json())

        # run query - guest credentials
        result = requests.post(url, data=query_request, headers=auth_headers_guest)
        assert result.ok
        result_json = result.json()
        snapshot.match("query-guest-3", result_json)
        assert result_json["errors"]
        assert result_json["errors"][0]["errorType"] == "Unauthorized"
        # run query - invalid credentials
        result = requests.post(url, data=query_request, headers=auth_headers_invalid_token)
        assert not result.ok
        assert result.status_code == 401
        result_json = result.json()
        snapshot.match("query-invalid-1", result_json)
        assert result_json["errors"]
        assert result_json["errors"][0]["errorType"] == "UnauthorizedException"

    @markers.aws.unknown
    def test_cognito_authorization_bearer_configuration(
        self,
        appsync_create_api,
        appsync_create_api_key_with_iam_users,
        create_data_source_ddb,
        create_graphql_schema,
        api_with_bearer_token,
        aws_client,
    ):
        api_id, bearer_token = api_with_bearer_token
        auth_headers_guest = {"Authorization": bearer_token}

        # create test schema
        schema = " type Query { test: String } "
        create_graphql_schema(api_id=api_id, definition=schema)

        # create data source and resolver
        create_data_source_ddb(api_id, name="ds1")
        aws_client.appsync.create_resolver(
            apiId=api_id,
            typeName="Query",
            fieldName="test",
            dataSourceName="ds1",
        )
        query_request = json.dumps({"query": "query { test }"})
        url = f"{config.internal_service_url()}/graphql/{api_id}"

        result = requests.post(url, data=query_request, headers=auth_headers_guest)

        assert result.ok

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(
        paths=[
            "$..args",
            "$..identity.claims.event_id",
            "$..identity.claims.jti",
            "$..identity.claims.origin_jti",
            "$..identity.defaultAuthStrategy",
            "$..identity.sourceIp",
            "$..info.selectionSetGraphQL",
            "$..prev",
            "$..request",
            "$..source",
            "$..stash",
        ]
    )
    def test_cognito_authorization_auth_context_propagated(
        self,
        appsync_create_user_pool_with_users,
        appsync_create_api,
        create_data_source_lambda,
        create_resolver,
        create_graphql_schema,
        snapshot,
        aws_client,
    ):
        (
            _,
            guest_token_set,
            user_pool,
            _,
            guest_group,
        ) = appsync_create_user_pool_with_users()

        snapshot.add_transformer(snapshot.transform.key_value("username"))
        snapshot.add_transformer(snapshot.transform.key_value("aud"))
        snapshot.add_transformer(
            snapshot.transform.key_value("auth_time", reference_replacement=False)
        )
        snapshot.add_transformer(snapshot.transform.key_value("exp", reference_replacement=False))
        snapshot.add_transformer(snapshot.transform.key_value("iat", reference_replacement=False))
        snapshot.add_transformer(snapshot.transform.key_value("iss"))
        snapshot.add_transformer(snapshot.transform.key_value("sub"))
        snapshot.add_transformer(snapshot.transform.regex(user_pool["Id"], "<user-pool-id>"))
        snapshot.add_transformer(snapshot.transform.key_value("authorization"))

        appsync_graphql_api = appsync_create_api(
            authenticationType="AMAZON_COGNITO_USER_POOLS",
            userPoolConfig={
                "userPoolId": user_pool["Id"],
                "awsRegion": aws_client.cognito_idp.meta.region_name,
                "defaultAction": "DENY",
            },
        )
        api_id = appsync_graphql_api["apiId"]

        schema = f"""
        type Query {{
            event: String!
            @aws_auth(cognito_groups: ["{guest_group}"])
        }}
        """
        create_graphql_schema(api_id=api_id, definition=schema)

        lambda_source = textwrap.dedent(
            """
        import json
        def handler(event, context):
            return str(json.dumps(event))
        """
        )

        res = create_data_source_lambda(
            api_id,
            src=lambda_source,
            runtime=Runtime.python3_12,
        )
        create_resolver(
            apiId=api_id,
            typeName="Query",
            fieldName="event",
            dataSourceName=res["name"],
        )

        query_request = json.dumps({"query": "{ event }"})
        url = appsync_graphql_api["uris"]["GRAPHQL"]

        def _assert_snapshot(token, snapshot_key):
            auth_headers = {"Authorization": f"Bearer {token}"}
            query_result = requests.post(url, data=query_request, headers=auth_headers)
            assert query_result.ok
            assert "errors" not in query_result.json()

            payload = query_result.json()
            event = json.loads(payload["data"]["event"])
            snapshot.match(snapshot_key, event)

        _assert_snapshot(guest_token_set.id_token, "id-token")
        _assert_snapshot(guest_token_set.access_token, "access-token")

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(
        paths=[
            "$..args",
            "$..identity.claims.event_id",
            "$..identity.claims.jti",
            "$..identity.claims.origin_jti",
            "$..identity.defaultAuthStrategy",
            "$..identity.sourceIp",
            "$..info.selectionSetGraphQL",
            "$..prev",
            "$..request",
            "$..source",
            "$..stash",
        ]
    )
    def test_cognito_authorization_auth_context_propagated_without_groups(
        self,
        appsync_create_user_pool_with_users,
        appsync_create_api,
        create_data_source_lambda,
        create_resolver,
        create_graphql_schema,
        snapshot,
        aws_client,
    ):
        (
            _,
            guest_token_set,
            user_pool,
            _,
            _,
        ) = appsync_create_user_pool_with_users(add_to_groups=False)

        snapshot.add_transformer(snapshot.transform.key_value("username"))
        snapshot.add_transformer(snapshot.transform.key_value("aud"))
        snapshot.add_transformer(
            snapshot.transform.key_value("auth_time", reference_replacement=False)
        )
        snapshot.add_transformer(snapshot.transform.key_value("exp", reference_replacement=False))
        snapshot.add_transformer(snapshot.transform.key_value("iat", reference_replacement=False))
        snapshot.add_transformer(snapshot.transform.key_value("iss"))
        snapshot.add_transformer(snapshot.transform.key_value("sub"))
        snapshot.add_transformer(snapshot.transform.regex(user_pool["Id"], "<user-pool-id>"))
        snapshot.add_transformer(snapshot.transform.key_value("authorization"))

        appsync_graphql_api = appsync_create_api(
            authenticationType="AMAZON_COGNITO_USER_POOLS",
            userPoolConfig={
                "userPoolId": user_pool["Id"],
                "awsRegion": aws_client.cognito_idp.meta.region_name,
                "defaultAction": "ALLOW",
            },
        )
        api_id = appsync_graphql_api["apiId"]

        schema = """
        type Query {
            event: String!
        }
        """
        create_graphql_schema(api_id=api_id, definition=schema)

        lambda_source = textwrap.dedent(
            """
        import json
        def handler(event, context):
            return str(json.dumps(event))
        """
        )

        res = create_data_source_lambda(
            api_id,
            src=lambda_source,
            runtime=Runtime.python3_12,
        )
        create_resolver(
            apiId=api_id,
            typeName="Query",
            fieldName="event",
            dataSourceName=res["name"],
        )

        query_request = json.dumps({"query": "{ event }"})
        url = appsync_graphql_api["uris"]["GRAPHQL"]

        def _assert_snapshot(token, snapshot_key):
            auth_headers = {"Authorization": f"Bearer {token}"}
            query_result = requests.post(url, data=query_request, headers=auth_headers)
            assert query_result.ok
            assert "errors" not in query_result.json()

            payload = query_result.json()
            event = json.loads(payload["data"]["event"])
            snapshot.match(snapshot_key, event)

        _assert_snapshot(guest_token_set.id_token, "id-token")
        _assert_snapshot(guest_token_set.access_token, "access-token")

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(
        paths=[
            "$..uris.GRAPHQL",
            "$..uris.REALTIME",
            "$..requestMappingTemplate",
            "$..errors..data",
            "$..errors..errorInfo",
            "$..errors..errorType",
            "$..errors..locations..sourceName",
        ]
    )
    def test_pipeline_resolver(
        self,
        appsync_create_api_key,
        appsync_graphql_api,
        create_graphql_schema,
        snapshot,
        aws_client,
    ):
        """
        Based on: https://docs.aws.amazon.com/appsync/latest/devguide/pipeline-resolvers.html
        """
        snapshot.add_transformer(snapshot.transform.appsync_api())
        snapshot.add_transformer(snapshot.transform.key_value("userId"))

        snapshot.match("graphql_api", appsync_graphql_api)
        api_id = appsync_graphql_api["apiId"]
        graphql_endpoint = appsync_graphql_api["uris"]["GRAPHQL"]
        create_graphql_schema(api_id=api_id, definition=PIPELINE_RESOLVER_SCHEMA)

        before_mapping_template = '$util.qr($ctx.stash.put("email", $ctx.args.input.email))\n{}'
        after_mapping_template = "$util.toJson($ctx.result)"

        aws_client.appsync.create_data_source(apiId=api_id, name="NONE", type="NONE")

        req_template = r"""
            #set($valid = $util.matches("^[a-zA-Z0-9_.+-]+@(?:(?:[a-zA-Z0-9-]+\.)?[a-zA-Z]+\.)?(local)\.stack", $ctx.stash.email))
            #if (!$valid)
                $util.error("$ctx.stash.email is not a valid email.")
            #end
            {
                "payload": { "email": $util.toJson(${ctx.stash.email}) }
            }
            """.strip()
        validate_email = aws_client.appsync.create_function(
            apiId=api_id,
            name="validateEmail",
            dataSourceName="NONE",
            requestMappingTemplate=req_template,
            responseMappingTemplate="$util.toJson($ctx.result)",
            functionVersion="2018-05-29",
        )["functionConfiguration"]
        snapshot.match("validate_email_function_configuration", validate_email)

        save_user = aws_client.appsync.create_function(
            apiId=api_id,
            name="saveUser",
            dataSourceName="NONE",
            requestMappingTemplate=r"""
            ## $ctx.prev.result contains the signup input values. We could have also
            ## used $ctx.args.input.
            {
                "payload": $util.toJson($ctx.prev.result)
            }
            """.strip(),
            responseMappingTemplate="""
            ## an id is required so let's add a unique random identifier to the output
            $util.qr($ctx.result.put("userId", $util.autoId()))
            $util.toJson($ctx.result)
            """.strip(),
            functionVersion="2018-05-29",
        )["functionConfiguration"]
        snapshot.match("save_user_function_configuration", save_user)

        pipeline_resolver = aws_client.appsync.create_resolver(
            apiId=api_id,
            typeName="Mutation",
            fieldName="signUp",
            kind="PIPELINE",
            requestMappingTemplate=before_mapping_template,
            responseMappingTemplate=after_mapping_template,
            pipelineConfig={"functions": [validate_email["functionId"], save_user["functionId"]]},
        )
        snapshot.match("pipeline_resolver", pipeline_resolver)

        api_key = appsync_create_api_key(api_id).get("id")
        mutation_template = """mutation {{
          signUp(input: {{
            email: "{email}"
            username: "stacky"
          }}) {{
            userId
          }}
        }}""".strip()
        valid_mutation = {
            "query": mutation_template.format(email="stacky@local.stack"),
        }
        invalid_mutation = {
            "query": mutation_template.format(email="bob@non-local.stack"),
        }

        result = requests.post(
            graphql_endpoint, json=valid_mutation, headers={"x-api-key": api_key}
        )
        snapshot.match("valid_mutation_result_code", result.status_code)
        snapshot.match("valid_mutation_result_content", result.json())

        result = requests.post(
            graphql_endpoint, json=invalid_mutation, headers={"x-api-key": api_key}
        )
        snapshot.match("invalid_mutation_result_code", result.status_code)
        snapshot.match("invalid_mutation_result_content", result.json())

    @markers.aws.validated
    def test_pipeline_js_resolver(
        self,
        appsync_graphql_api,
        appsync_create_api_key,
        create_graphql_schema,
        aws_client,
        snapshot,
    ):
        api_id = appsync_graphql_api["apiId"]
        snapshot.add_transformer(snapshot.transform.regex(api_id, "<api-id>"))

        definition = textwrap.dedent(
            """
        schema {
            query: Query
        }
        type Item {
            name: String!
        }
        type Query {
            getItem(id: String!): Item!
        }
        """
        ).strip()
        create_graphql_schema(api_id=api_id, definition=definition)

        aws_client.appsync.create_data_source(apiId=api_id, name="NONE", type="NONE")

        func_code = textwrap.dedent(
            """
        import { util } from '@aws-appsync/utils';
        export function request(ctx) {
          return {"payload": ctx.args.id}
        }
        export function response(ctx) {
          return "response-payload: " + ctx.result;
        }
        """
        ).strip()
        get_item_func = aws_client.appsync.create_function(
            apiId=api_id,
            name="getItem",
            dataSourceName="NONE",
            code=func_code,
            runtime={"name": "APPSYNC_JS", "runtimeVersion": "1.0.0"},
        )["functionConfiguration"]
        snapshot.add_transformer(snapshot.transform.regex(get_item_func["functionId"], "<func-id>"))
        snapshot.match("function_config", get_item_func)

        mapping_code = textwrap.dedent(
            """
        export function request(ctx) {
          // not relevant for NONE data source
        }
        export function response(ctx) {
          // the `Item` type
          return {
              name: ctx.prev.result,
          };
        }
        """
        ).strip()

        pipeline_resolver = aws_client.appsync.create_resolver(
            apiId=api_id,
            typeName="Query",
            fieldName="getItem",
            kind="PIPELINE",
            code=mapping_code,
            runtime={"name": "APPSYNC_JS", "runtimeVersion": "1.0.0"},
            pipelineConfig={"functions": [get_item_func["functionId"]]},
        )
        snapshot.match("pipeline-resolver", pipeline_resolver)

        api_key = appsync_create_api_key(api_id).get("id")
        graphql_endpoint = appsync_graphql_api["uris"]["GRAPHQL"]

        item_id = short_uid()
        snapshot.add_transformer(snapshot.transform.regex(item_id, "<item-id>"))
        query_request = {
            "query": "query($id:String!) { getItem(id: $id) { name } }",
            "variables": {"id": item_id},
        }
        result = requests.post(graphql_endpoint, json=query_request, headers={"x-api-key": api_key})
        snapshot.match("response-code", result.status_code)
        # make sure the code does not generate an error when running against AWS
        response_body = result.json()
        assert "errors" not in response_body

        snapshot.match("response-content", response_body)

    @markers.aws.validated
    @pytest.mark.parametrize(
        "name,version",
        [
            # valid
            ("APPSYNC_JS", "1.0.0"),
            # invalid
            ("APPSYNC_JS2", "1.0.0"),
            ("APPSYNC_JS", "1.0.1"),
            ("APPSYNC_JS", "1.1.0"),
            ("APPSYNC_JS2", "1.1.0"),
        ],
    )
    def test_create_js_resolver_runtime_validation(
        self, aws_client, appsync_graphql_api, create_graphql_schema, snapshot, name, version
    ):
        api_id = appsync_graphql_api["apiId"]
        snapshot.add_transformer(snapshot.transform.regex(api_id, "<api-id>"))

        schema = """
        schema {
            query: Query
        }

        type Query {
            stub: String!
        }
        """
        create_graphql_schema(api_id=api_id, definition=schema)

        resolver_code = """
        export function request(ctx) {
        }

        export function response(ctx) {
        }
        """
        ds_name = f"ds{short_uid()}"
        snapshot.add_transformer(snapshot.transform.regex(ds_name, "<ds-name>"))
        aws_client.appsync.create_data_source(apiId=api_id, name=ds_name, type="NONE")

        try:
            res = aws_client.appsync.create_resolver(
                apiId=api_id,
                typeName="Query",
                fieldName="stub",
                dataSourceName=ds_name,
                kind="UNIT",
                code=resolver_code,
                runtime={"name": name, "runtimeVersion": version},
            )
            snapshot.match("result", res)
        except ClientError as e:
            snapshot.match("client-error", e.response)

    @markers.aws.validated
    def test_js_utils(
        self,
        appsync_graphql_api,
        appsync_create_api_key,
        create_graphql_schema,
        create_resolver,
        aws_client,
        snapshot,
    ):
        api_id = appsync_graphql_api["apiId"]
        schema = """
        schema {
            query: Query
        }

        type Query {
            getValue: String!
        }
        """
        create_graphql_schema(api_id=api_id, definition=schema)

        aws_client.appsync.create_data_source(apiId=api_id, name="NONE", type="NONE")

        func_code = """
        import { util } from '@aws-appsync/utils';

        export function request(ctx) {
            return {
                payload: JSON.stringify(util.dynamodb.toString("test")),
            };
        }

        export function response(ctx) {
            return ctx.result;
        }
        """

        resolver_code = """
        export function request(ctx) {
            return {}
        }
        export function response(ctx) {
            return ctx.prev.result;
        }
        """
        func = aws_client.appsync.create_function(
            apiId=api_id,
            name="get",
            dataSourceName="NONE",
            code=func_code,
            runtime={"name": "APPSYNC_JS", "runtimeVersion": "1.0.0"},
        )["functionConfiguration"]

        aws_client.appsync.create_resolver(
            apiId=api_id,
            typeName="Query",
            fieldName="getValue",
            kind="PIPELINE",
            code=resolver_code,
            runtime={"name": "APPSYNC_JS", "runtimeVersion": "1.0.0"},
            pipelineConfig={"functions": [func["functionId"]]},
        )

        api_key = appsync_create_api_key(api_id)["id"]
        graphql_endpoint = appsync_graphql_api["uris"]["GRAPHQL"]
        query_request = {"query": "query { getValue }"}
        result = requests.post(graphql_endpoint, json=query_request, headers={"x-api-key": api_key})

        snapshot.match("response-code", result.status_code)
        snapshot.match("response-content", result.json())

    @markers.aws.validated
    def test_nested_resolvers(
        self,
        snapshot,
        appsync_graphql_api,
        appsync_create_api_key,
        aws_client,
        create_graphql_schema,
        create_resolver,
        cleanups,
    ):
        api_id = appsync_graphql_api["apiId"]
        api_key = appsync_create_api_key(api_id).get("id")

        aws_client.appsync.create_data_source(apiId=api_id, name="None", type="NONE")
        cleanups.append(lambda: aws_client.appsync.delete_data_source(apiId=api_id, name="None"))

        definition = textwrap.dedent(
            """
            schema { query: Query }
            type Query { listUsers: [User]! }
            type User { id: ID! name: String! posts: [Post!]! }
            type Post { id: ID! title: String! }
        """
        ).strip()

        create_graphql_schema(api_id=api_id, definition=definition)

        create_resolver(
            apiId=api_id,
            typeName="Query",
            fieldName="listUsers",
            dataSourceName="None",
            kind="UNIT",
            requestMappingTemplate='{"version": "2018-05-29", "payload": $util.toJson($context.arguments)}',
            responseMappingTemplate='$utils.toJson([{"id": "1", "name": "U1"}, {"id": "2", "name": "U2"}])',
        )

        create_resolver(
            apiId=api_id,
            typeName="User",
            fieldName="posts",
            dataSourceName="None",
            kind="UNIT",
            requestMappingTemplate='{"version": "2018-05-29", "payload": $util.toJson($context.arguments)}',
            responseMappingTemplate=textwrap.dedent(
                """
                $utils.toJson([
                    {"id": "user_${context.source.id}_post_1", "title": "Post 1 for ${context.source.name}"},
                    {"id": "user_${context.source.id}_post_1", "title": "Post 2 for ${context.source.name}"}
                ])
                """
            ).replace("\n", ""),
        )

        graphql_endpoint = appsync_graphql_api["uris"]["GRAPHQL"]
        query_request = {"query": "query { listUsers { id name posts { id title } } }"}

        response = requests.post(
            graphql_endpoint, json=query_request, headers={"x-api-key": api_key}
        )

        snapshot.match("response-code", response.status_code)
        snapshot.match("response-content", response.json())

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(paths=["$..code"])
    def test_http_data_source_detailed(
        self,
        appsync_graphql_api,
        appsync_create_api_key,
        create_graphql_schema,
        aws_client,
        snapshot,
        echo_http_server_url,
    ):
        api_id = appsync_graphql_api["apiId"]
        snapshot.add_transformer(snapshot.transform.regex(api_id, "<api-id>"))

        definition = textwrap.dedent(
            """
        schema { query: Query }
        type Query { getItem: String }
        """
        ).strip()
        create_graphql_schema(api_id=api_id, definition=definition)

        ds_name = "http_ds1"
        aws_client.appsync.create_data_source(
            apiId=api_id, name=ds_name, type="HTTP", httpConfig={"endpoint": echo_http_server_url}
        )

        func_code = prepend_assertion_functions(
            """
        export function request(ctx) {
          assertTypeOf(ctx, "object", "function.request.ctx");
          assertTypeOf(ctx.prev, "object", "function.request.ctx.prev");
          // ctx.prev.result is "ctx" from the pipeline resolver
          assertTypeOf(ctx.prev.result, "object", "function.request.ctx.prev.result");

          return {
            method: 'POST',
            params: {
              headers: {
                'Content-Type': 'application/json',
                'Authorization': 'auth 123'
              },
              body: 'test body 123',
            },
            resourcePath: '/request/my/path'
          };
        }
        export function response(ctx) {
          assertTypeOf(ctx, "object", "function.response.ctx");
          assertTypeOf(ctx.result, "object", "function.response.ctx.result");
          assertTypeOf(ctx.result.statusCode, "number", "function.response.result.statusCode");
          assertTypeOf(ctx.result.body, "string", "function.response.ctx.result.body");

          return ctx.result.body;
        }
        """
        )
        function = aws_client.appsync.create_function(
            apiId=api_id,
            name="getItem",
            dataSourceName=ds_name,
            code=func_code,
            runtime={"name": "APPSYNC_JS", "runtimeVersion": "1.0.0"},
        )["functionConfiguration"]
        snapshot.add_transformer(snapshot.transform.regex(function["functionId"], "<func-id>"))
        snapshot.match("function", function)

        resolver_code = prepend_assertion_functions(
            """
        export function request(ctx) {
          assertTypeOf(ctx, "object", "pipeline.request.ctx");
          return ctx;
        }
        export function response(ctx) {
          assertTypeOf(ctx, "object", "pipeline.response.ctx");
          assertTypeOf(ctx.prev, "object", "pipeline.response.ctx.prev");
          assertTypeOf(ctx.prev.result, "string", "pipeline.response.ctx.prev.result");

          return ctx.prev.result;
        }
        """
        )

        resolver = aws_client.appsync.create_resolver(
            apiId=api_id,
            typeName="Query",
            fieldName="getItem",
            kind="PIPELINE",
            code=resolver_code,
            runtime={"name": "APPSYNC_JS", "runtimeVersion": "1.0.0"},
            pipelineConfig={"functions": [function["functionId"]]},
        )
        snapshot.match("resolver", resolver)

        # create API key, make request
        api_key = appsync_create_api_key(api_id).get("id")
        graphql_endpoint = appsync_graphql_api["uris"]["GRAPHQL"]
        query_request = {"query": "query { getItem }"}
        result = requests.post(graphql_endpoint, json=query_request, headers={"x-api-key": api_key})
        snapshot.match("response-code", result.status_code)
        content = json.loads(result.json()["data"]["getItem"])

        # extract request body payload (`data` for local, `postData` from mockbin.org for parity testing)
        body = content.get("data") or content["postData"]["text"]
        headers = {key.lower(): value for key, value in content["headers"].items()}
        headers = select_attributes(headers, ["content-type", "authorization"])

        result = {
            "method": content["method"],
            "body": body,
            "path": urlparse(content["url"]).path,
            "headers": headers,
            "response_code": result.status_code,
        }
        snapshot.match("response-content", result)

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(paths=["$..code"])
    def test_http_data_source_return_object(
        self,
        appsync_graphql_api,
        appsync_create_api_key,
        create_graphql_schema,
        aws_client,
        snapshot,
        echo_http_server_url,
    ):
        api_id = appsync_graphql_api["apiId"]
        snapshot.add_transformer(snapshot.transform.regex(api_id, "<api-id>"))

        definition = textwrap.dedent(
            """
        schema { query: Query }
        type Item { name: String! }
        type Query { getItem: Item! }
        """
        ).strip()
        create_graphql_schema(api_id=api_id, definition=definition)

        ds_name = "http_ds1"
        aws_client.appsync.create_data_source(
            apiId=api_id, name=ds_name, type="HTTP", httpConfig={"endpoint": echo_http_server_url}
        )

        func_code = prepend_assertion_functions(
            """
        export function request(ctx) {
          assertTypeOf(ctx, "object", "function.request.ctx");
          assertTypeOf(ctx.prev, "object", "function.request.ctx.prev");
          // ctx.prev.result is "ctx" from the pipeline resolver
          assertTypeOf(ctx.prev.result, "object", "function.request.ctx.prev.result");

          return {
            method: 'POST',
            params: {
              headers: {
                'Content-Type': 'application/json',
                'Authorization': 'auth 123'
              },
              body: '{"name":"my-name"}',
            },
            resourcePath: '/request/my/path'
          };
        }
        export function response(ctx) {
          assertTypeOf(ctx, "object", "function.response.ctx");
          assertTypeOf(ctx.result, "object", "function.response.ctx.result");
          assertTypeOf(ctx.result.statusCode, "number", "function.response.result.statusCode");
          assertTypeOf(ctx.result.body, "string", "function.response.ctx.result.body");

          return ctx.result.body;
        }
        """
        )
        function = aws_client.appsync.create_function(
            apiId=api_id,
            name="getItem",
            dataSourceName=ds_name,
            code=func_code,
            runtime={"name": "APPSYNC_JS", "runtimeVersion": "1.0.0"},
        )["functionConfiguration"]
        snapshot.add_transformer(snapshot.transform.regex(function["functionId"], "<func-id>"))
        snapshot.match("function", function)

        resolver_code = prepend_assertion_functions(
            """
            export function request(ctx) {
              assertTypeOf(ctx, "object", "pipeline.request.ctx");
              return ctx;
            }
            export function response(ctx) {
              assertTypeOf(ctx, "object", "pipeline.response.ctx");
              assertTypeOf(ctx.prev, "object", "pipeline.response.ctx.prev");
              assertTypeOf(ctx.prev.result, "string", "pipeline.response.ctx.prev.result");

              const response = JSON.parse(ctx.prev.result);
              if (response.postData) {
                  // from mockbin
                  return JSON.parse(response.postData.text);
              } else {
                  return JSON.parse(response.data);
              }
            }
        """
        )

        resolver = aws_client.appsync.create_resolver(
            apiId=api_id,
            typeName="Query",
            fieldName="getItem",
            kind="PIPELINE",
            code=resolver_code,
            runtime={"name": "APPSYNC_JS", "runtimeVersion": "1.0.0"},
            pipelineConfig={"functions": [function["functionId"]]},
        )
        snapshot.match("resolver", resolver)

        # create API key, make request
        api_key = appsync_create_api_key(api_id).get("id")
        graphql_endpoint = appsync_graphql_api["uris"]["GRAPHQL"]
        query_request = {"query": "query { getItem { name } }"}
        result = requests.post(graphql_endpoint, json=query_request, headers={"x-api-key": api_key})
        snapshot.match("response-code", result.status_code)
        content = result.json()
        snapshot.match("content", content)

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(paths=["$..code"])
    def test_http_data_source_return_simple(
        self,
        appsync_graphql_api,
        appsync_create_api_key,
        create_graphql_schema,
        aws_client,
        snapshot,
        echo_http_server_url,
    ):
        api_id = appsync_graphql_api["apiId"]
        snapshot.add_transformer(snapshot.transform.regex(api_id, "<api-id>"))

        definition = textwrap.dedent(
            """
        schema { query: Query }
        type Query { getItem: String! }
        """
        ).strip()
        create_graphql_schema(api_id=api_id, definition=definition)

        ds_name = "http_ds1"
        aws_client.appsync.create_data_source(
            apiId=api_id, name=ds_name, type="HTTP", httpConfig={"endpoint": echo_http_server_url}
        )

        func_code = prepend_assertion_functions(
            """
        export function request(ctx) {
          assertTypeOf(ctx, "object", "function.request.ctx");
          assertTypeOf(ctx.prev, "object", "function.request.ctx.prev");
          // ctx.prev.result is "ctx" from the pipeline resolver
          assertTypeOf(ctx.prev.result, "object", "function.request.ctx.prev.result");

          return {
            method: 'POST',
            params: {
              headers: {
                'Content-Type': 'application/json',
                'Authorization': 'auth 123'
              },
              body: 'hello world',
            },
            resourcePath: '/request/my/path'
          };
        }
        export function response(ctx) {
          assertTypeOf(ctx, "object", "function.response.ctx");
          assertTypeOf(ctx.result, "object", "function.response.ctx.result");
          assertTypeOf(ctx.result.statusCode, "number", "function.response.result.statusCode");
          assertTypeOf(ctx.result.body, "string", "function.response.ctx.result.body");

          return ctx.result.body;
        }
        """
        )
        function = aws_client.appsync.create_function(
            apiId=api_id,
            name="getItem",
            dataSourceName=ds_name,
            code=func_code,
            runtime={"name": "APPSYNC_JS", "runtimeVersion": "1.0.0"},
        )["functionConfiguration"]
        snapshot.add_transformer(snapshot.transform.regex(function["functionId"], "<func-id>"))
        snapshot.match("function", function)

        resolver_code = prepend_assertion_functions(
            """
            export function request(ctx) {
              assertTypeOf(ctx, "object", "pipeline.request.ctx");
              return ctx;
            }
            export function response(ctx) {
              assertTypeOf(ctx, "object", "pipeline.response.ctx");
              assertTypeOf(ctx.prev, "object", "pipeline.response.ctx.prev");
              assertTypeOf(ctx.prev.result, "string", "pipeline.response.ctx.prev.result");

              const response = JSON.parse(ctx.prev.result);
              if (response.postData) {
                  // from mockbin
                  return response.postData.text;
              } else {
                  return response.data;
              }
            }
        """
        )

        resolver = aws_client.appsync.create_resolver(
            apiId=api_id,
            typeName="Query",
            fieldName="getItem",
            kind="PIPELINE",
            code=resolver_code,
            runtime={"name": "APPSYNC_JS", "runtimeVersion": "1.0.0"},
            pipelineConfig={"functions": [function["functionId"]]},
        )
        snapshot.match("resolver", resolver)

        # create API key, make request
        api_key = appsync_create_api_key(api_id).get("id")
        graphql_endpoint = appsync_graphql_api["uris"]["GRAPHQL"]
        query_request = {"query": "query { getItem }"}
        result = requests.post(graphql_endpoint, json=query_request, headers={"x-api-key": api_key})
        snapshot.match("response-code", result.status_code)
        content = result.json()
        snapshot.match("content", content)

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(
        paths=[
            "$..headers",
        ]
    )
    def test_http_data_source_vtl_template(
        self,
        appsync_graphql_api,
        appsync_create_api_key,
        create_graphql_schema,
        aws_client,
        snapshot,
        echo_http_server_url,
    ):
        api_id = appsync_graphql_api["apiId"]
        snapshot.add_transformer(snapshot.transform.regex(api_id, "<api-id>"))

        definition = textwrap.dedent(
            """
        schema { query: Query }
        type Query { getItem: String! }
        """
        ).strip()
        create_graphql_schema(api_id=api_id, definition=definition)

        ds_name = "http_ds1"
        aws_client.appsync.create_data_source(
            apiId=api_id, name=ds_name, type="HTTP", httpConfig={"endpoint": echo_http_server_url}
        )

        # create resolver
        aws_client.appsync.create_resolver(
            apiId=api_id,
            typeName="Query",
            fieldName="getItem",
            dataSourceName=ds_name,
            requestMappingTemplate="""{
                "version": "2018-05-29",
                "method": "POST",
                "params": {
                    "headers": {
                        "Content-Type": "application/json"
                    },
                    "body": {
                        "query": "query { listProjects { id name } }"
                    }
                },
                "resourcePath": "/request/my/path"
            }""",
            responseMappingTemplate="""
            $utils.toJson($ctx.result.body)
            """,
        )

        # create API key, make request
        api_key = appsync_create_api_key(api_id).get("id")
        graphql_endpoint = appsync_graphql_api["uris"]["GRAPHQL"]
        query_request = {"query": "query { getItem }"}
        result = requests.post(graphql_endpoint, json=query_request, headers={"x-api-key": api_key})
        snapshot.match("response-code", result.status_code)
        response = json.loads(result.json()["data"]["getItem"])
        # response is different depending on if the request is made to the echo server or httpbin
        headers = response["headers"]
        if response.get("postData"):
            # mockbin
            content = json.loads(response["postData"]["text"])
        else:
            # echo server
            content = json.loads(response["data"])

        snapshot.match("content", {"body": content, "headers": headers})

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(
        paths=[
            "$..body.data.create.ctx.request.domainName",
            "$..body.data.create.ctx.request.headers",
            "$..body.data.create.context.request.domainName",
            "$..body.data.create.context.request.headers",
            "$..info.selectionSetList",
        ]
    )
    @pytest.mark.parametrize("resolver_language", ["VTL", "JS"])
    def test_lambda_data_source(
        self,
        appsync_graphql_api,
        appsync_create_api_key,
        create_data_source_lambda,
        create_resolver,
        create_graphql_schema,
        snapshot,
        resolver_language,
    ):
        api_id = appsync_graphql_api["apiId"]
        schema = textwrap.dedent(
            """
            type Mutation {
                create: String!
            }
            type Query {
                _empty: String
            }
            schema {
                query: Query
                mutation: Mutation
            }
            """
        )
        create_graphql_schema(api_id, definition=schema)

        lambda_source = textwrap.dedent(
            """
            import json
            def handler(event, context):
                return json.dumps(event)
            """
        )
        res = create_data_source_lambda(
            api_id,
            src=lambda_source,
            runtime=Runtime.python3_12,
        )

        if resolver_language == "VTL":
            req_template = """
            {
                "version": "2018-05-29",
                "operation": "Invoke",
                "payload": {"context": $util.toJson($context), "ctx": $util.toJson($ctx)}
            }
            """

            res_template = "$util.toJson($context.result)"

            create_resolver(
                apiId=api_id,
                typeName="Mutation",
                fieldName="create",
                dataSourceName=res["name"],
                requestMappingTemplate=req_template,
                responseMappingTemplate=res_template,
            )
        elif resolver_language == "JS":
            code = """
            export function request(ctx) {
                return {
                    operation: "Invoke",
                    payload: {
                        ctx,
                    },
                };
            }

            export function response(ctx) {
                return ctx.result;
            }
            """

            create_resolver(
                apiId=api_id,
                typeName="Mutation",
                fieldName="create",
                dataSourceName=res["name"],
                code=code,
                runtime={"name": "APPSYNC_JS", "runtimeVersion": "1.0.0"},
                kind="UNIT",
            )
        else:
            raise ValueError(f"Invalid resolver language: {resolver_language}")

        api_key = appsync_create_api_key(api_id)["id"]
        graphql_endpoint = appsync_graphql_api["uris"]["GRAPHQL"]
        query = "mutation RunCreate { create }"
        query_payload = {"query": query}

        if is_aws_cloud():
            # TODO: potentially replace with retry mechanism
            LOG.warning("sleeping for IAM role propagation")
            time.sleep(10)

        response = requests.post(
            graphql_endpoint, json=query_payload, headers={"x-api-key": api_key}
        )
        result = {
            "status_code": response.status_code,
            "body": response.json(),
        }
        snapshot.match("response", result)
        # as headers are pretty hard to snapshot, we manually assert that the header we passed is present in the
        # lambda request context object
        payload = json.loads(result["body"]["data"]["create"])
        assert "x-api-key" in payload["ctx"]["request"]["headers"]
        if resolver_language == "VTL":
            assert "x-api-key" in payload["context"]["request"]["headers"]

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(
        # TODO AWS constructs the messages in a different manner than Graphql
        paths=["$..body.errors..errorType", "$..body.errors..locations", "$..body.errors..message"]
    )
    def test_lambda_bool_types(
        self,
        appsync_graphql_api,
        appsync_create_api_key,
        create_data_source_lambda,
        create_resolver,
        create_graphql_schema,
        snapshot,
    ):
        api_id = appsync_graphql_api["apiId"]
        schema = textwrap.dedent(
            """
            schema {
              query: Query
            }


            type Query {
              listItems: [Item]
            }


            type Item {
                isTrue: Boolean
                isTrueAsInt: Boolean
                isTrueCapitalized: Boolean
                isFalse: Boolean
                isFalseAnyString: Boolean
                isFalseAnyStrInt: Boolean
                isFalseAsInt: Boolean
                isFalseArray: Boolean
                isFalseDict: Boolean
                stringTrue: String
                stringFalse: String
            }
            """
        )
        create_graphql_schema(api_id, definition=schema)

        lambda_source = textwrap.dedent(
            """
            import json
            def handler(event, context):
                return [
                    {
                        "isTrue": "true",
                        "isTrueAsInt": 1,
                        "isTrueCapitalized": "TruE",
                        "isFalse": "false",
                        "isFalseAnyString": "RandomString",
                        "isFalseAnyStrInt": "1",
                        "isFalseAsInt": 0,
                        "isFalseArray": [],
                        "isFalseDict": {},
                        "stringTrue": "true",
                        "stringFalse": "false",
                    }
                ]
            """
        )
        res = create_data_source_lambda(
            api_id,
            src=lambda_source,
            runtime=Runtime.python3_12,
        )

        create_resolver(
            apiId=api_id,
            typeName="Query",
            fieldName="listItems",
            dataSourceName=res["name"],
        )

        api_key = appsync_create_api_key(api_id)["id"]
        graphql_endpoint = appsync_graphql_api["uris"]["GRAPHQL"]
        query_payload = {
            "query": """
                {
                    listItems
                        {
                            isTrue
                            isTrueAsInt
                            isTrueCapitalized
                            isFalse
                            isFalseAnyString
                            isFalseAnyStrInt
                            isFalseAsInt
                            isFalseArray
                            isFalseDict
                            stringTrue
                            stringFalse
                        }
                    }
                """
        }

        if is_aws_cloud():
            # TODO: potentially replace with retry mechanism
            LOG.warning("sleeping for IAM role propagation")
            time.sleep(10)

        response = requests.post(
            graphql_endpoint, json=query_payload, headers={"x-api-key": api_key}
        )
        result = {
            "status_code": response.status_code,
            "body": response.json(),
        }
        snapshot.match("response", result)

    @pytest.mark.aws_validated
    @pytest.mark.skip_snapshot_verify(
        paths=[
            "$..payload.data.getItem.event.field.identity",
            "$..payload.data.getItem.event.field.source",
            "$..payload.data.getItem.event.field.request",
            "$..payload.data.simple.field.identity",
            "$..payload.data.simple.field.source",
            "$..payload.data.simple.field.request",
            # TODO add GraphQL extraction
            "$..info.selectionSetGraphQL",
            # TODO add variable to simple query
            "$..info.variables",
        ]
    )
    def test_lambda_payload(
        self,
        appsync_graphql_api,
        create_data_source_lambda,
        create_resolver,
        appsync_create_api_key,
        create_graphql_schema,
        aws_client,
        snapshot,
    ):
        api_id = appsync_graphql_api["apiId"]
        definition = textwrap.dedent(
            """
        schema {
          query: Query
        }
        type SubItem {
          field: String!
        }
        type Item {
          event: SubItem!
        }
        type Query {
          getItem(id:ID!): Item!
          simple: SubItem!
        }
        """
        ).strip()

        create_graphql_schema(api_id=api_id, definition=definition)

        lambda_source = textwrap.dedent(
            """
            import json
            def handler(event, context):
                field_name = event["info"]["fieldName"]
                if field_name == "simple":
                    return {"field": json.dumps(event)}
                elif field_name == "getItem":
                    return {"event": {"field": json.dumps(event)}}
                else:
                    raise ValueError(type_name)
            """
        )
        res = create_data_source_lambda(
            api_id,
            src=lambda_source,
            runtime=Runtime.python3_12,
        )
        create_resolver(
            apiId=api_id,
            typeName="Query",
            fieldName="simple",
            dataSourceName=res["name"],
        )
        create_resolver(
            apiId=api_id,
            typeName="Query",
            fieldName="getItem",
            dataSourceName=res["name"],
        )

        api_key = appsync_create_api_key(api_id)["id"]

        query = textwrap.dedent(
            """
            query GetItem($id: ID!) {
              getItem(id: $id) {
                event {
                  field
                }
              }
              simple {
                field
              }
            }
            """
        )
        variables = {"id": "123"}
        query_payload = {"query": query, "variables": variables}
        url = appsync_graphql_api["uris"]["GRAPHQL"]
        response = requests.post(url, json=query_payload, headers={"x-api-key": api_key})

        snapshot.match("result", {"status_code": response.status_code, "payload": response.json()})

    @markers.aws.validated
    def test_rds_data_source(
        self,
        rds_create_db_cluster,
        appsync_graphql_api,
        appsync_create_api_key,
        create_graphql_schema,
        create_data_source_rds,
        create_resolver,
        aws_client_factory,
        snapshot,
        region_name,
        secondary_region_name,
    ):
        """
        General RDS test exercising
        * Querying an RDS database
        * in a region that's different to the AppSync instance
        * using variablesMap
        """

        # check we are deploying to a different region than the AppSync API
        assert secondary_region_name != region_name

        aws_client = aws_client_factory(region_name=secondary_region_name)
        db_id = f"rds{short_uid()}"
        snapshot.add_transformer(snapshot.transform.regex(db_id, "<db-id>"))
        snapshot.add_transformer(
            snapshot.transform.regex(secondary_region_name, "<secondary-region>")
        )

        user = "test"
        password = "Test123!"
        db_name = "messages"
        snapshot.add_transformer(snapshot.transform.regex(db_name, "<db-name>"))

        result = rds_create_db_cluster(
            DBClusterIdentifier=db_id,
            DatabaseName=db_name,
            Engine="aurora-postgresql",
            EngineMode="serverless",
            MasterUsername=user,
            MasterUserPassword=password,
            EnableHttpEndpoint=True,
            region_name=secondary_region_name,
        )
        db_arn = result["DBClusterArn"]

        # set up credentials as secret
        secret_name = f"secret-{short_uid()}"
        snapshot.add_transformer(
            # regex taken from SecretsmanagerProvider._validate_secret_id
            snapshot.transform.regex(f"{secret_name}[A-Za-z0-9/_+=.@-]+", "<credentials-secret-id>")
        )
        secret_arn = aws_client.secretsmanager.create_secret(
            Name=secret_name,
            SecretString=json.dumps(
                {
                    "username": user,
                    "password": password,
                }
            ),
        )["ARN"]

        # create the table
        aws_client.rds_data.execute_statement(
            database=db_name,
            resourceArn=db_arn,
            secretArn=secret_arn,
            sql="create table messages (id serial not null, text varchar not null)",
        )

        # insert some data
        aws_client.rds_data.execute_statement(
            database=db_name,
            resourceArn=db_arn,
            secretArn=secret_arn,
            sql="insert into messages (id, text) values (1, 'hello world')",
        )
        aws_client.rds_data.execute_statement(
            database=db_name,
            resourceArn=db_arn,
            secretArn=secret_arn,
            sql="insert into messages (id, text) values (2, 'goodbye world')",
        )

        api_id = appsync_graphql_api["apiId"]
        snapshot.add_transformer(snapshot.transform.regex(api_id, "<api-id>"))

        api_key = appsync_create_api_key(api_id)["id"]

        schema = """
        type Message {
            id: ID!
            text: String!
        }

        type Query {
            getAllMessages: [Message!]!
        }
        """
        create_graphql_schema(api_id, definition=schema)

        ds = create_data_source_rds(
            api_id=api_id,
            cluster_arn=db_arn,
            secret_arn=secret_arn,
            database_name=db_name,
            region_name=secondary_region_name,
        )
        snapshot.add_transformer(snapshot.transform.regex(ds["name"], "<data-source-name>"))
        snapshot.match("data-source-definition", ds)

        req_template = """
        {
            "version": "2018-05-29",
            "statements": [
                $util.toJson("select * from messages where id = :ID")
            ],
            "variableMap": {
                ":ID": 1
            }
        }
        """

        res_template = """
        $utils.toJson($utils.rds.toJsonObject($ctx.result)[0])
        """

        create_resolver(
            apiId=api_id,
            typeName="Query",
            fieldName="getAllMessages",
            dataSourceName=ds["name"],
            kind="UNIT",
            requestMappingTemplate=req_template,
            responseMappingTemplate=res_template,
        )

        # Make a request into the API
        graphql_endpoint = appsync_graphql_api["uris"]["GRAPHQL"]
        query = """
        {
            getAllMessages {
                id
                text
            }
        }
        """
        query_payload = {"query": query}

        # wait for IAM propagation
        if is_aws_cloud():
            LOG.debug("Sleeping for IAM role propagation")
            time.sleep(20)

        response = requests.post(
            graphql_endpoint, json=query_payload, headers={"x-api-key": api_key}
        )

        snapshot.match(
            "response", {"payload": response.json(), "status-code": response.status_code}
        )

    @markers.aws.validated
    def test_rds_data_source_rds_utils(
        self,
        create_vpc,
        rds_create_db_cluster,
        appsync_graphql_api,
        appsync_create_api_key,
        create_graphql_schema,
        create_data_source_rds,
        create_resolver,
        aws_client,
        snapshot,
        cleanups,
        region_name,
    ):
        db_id = f"rds{short_uid()}"
        snapshot.add_transformer(snapshot.transform.regex(db_id, "<db-id>"))

        user = "test"
        password = "Test123!"
        db_name = "properties"
        snapshot.add_transformer(snapshot.transform.regex(db_name, "<db-name>"))

        # no default vpc in default region
        _, subnet_ids = create_vpc()

        db_subnet_group_name = f"test_db_subnet_group_{short_uid()}"
        aws_client.rds.create_db_subnet_group(
            DBSubnetGroupName=db_subnet_group_name,
            DBSubnetGroupDescription="description",
            SubnetIds=subnet_ids,
        )
        cleanups.append(
            lambda: aws_client.rds.delete_db_subnet_group(DBSubnetGroupName=db_subnet_group_name)
        )

        result = rds_create_db_cluster(
            DBClusterIdentifier=db_id,
            DatabaseName=db_name,
            Engine="aurora-mysql",
            EngineMode="serverless",
            MasterUsername=user,
            MasterUserPassword=password,
            EnableHttpEndpoint=True,
            DBSubnetGroupName=db_subnet_group_name,
        )
        db_arn = result["DBClusterArn"]

        # set up credentials as secret
        secret_name = f"secret-{short_uid()}"
        snapshot.add_transformer(
            # regex taken from SecretsmanagerProvider._validate_secret_id
            snapshot.transform.regex(f"{secret_name}[A-Za-z0-9/_+=.@-]+", "<credentials-secret-id>")
        )
        secret_arn = aws_client.secretsmanager.create_secret(
            Name=secret_name,
            SecretString=json.dumps(
                {
                    "username": user,
                    "password": password,
                }
            ),
        )["ARN"]

        # create the table
        property_id = str(uuid.uuid4())

        created_at = datetime.date(2023, 2, 3)
        updated_at = datetime.date(2023, 3, 14)

        snapshot.add_transformer(snapshot.transform.regex(str(created_at), "<created-at>"))
        snapshot.add_transformer(snapshot.transform.regex(str(updated_at), "<updated-at>"))

        ddl = [
            """
        create table properties (
            id varchar(36) primary key,
            owner_id varchar(36) not null,
            title varchar(255),
            description varchar(4096),
            status varchar(32),
            price decimal,
            created_at datetime,
            updated_at datetime
        )
        """,
            f"""
            insert into properties (id, owner_id, title, description, status, price, created_at, updated_at) values (
                '{property_id}',
                '{uuid.uuid4()}',
                'title',
                'my description',
                'NEW',
                100.2,
                '{created_at}',
                '{updated_at}'
            )
            """,
        ]
        for statement in ddl:
            aws_client.rds_data.execute_statement(
                database=db_name,
                resourceArn=db_arn,
                secretArn=secret_arn,
                sql=statement,
            )

        api_id = appsync_graphql_api["apiId"]
        snapshot.add_transformer(snapshot.transform.regex(api_id, "<api-id>"))

        api_key = appsync_create_api_key(api_id)["id"]

        schema = """
        type Property {
            id: ID!
            ownerid: String!
            title: String
            description: String
            status: String
            price: Float
            createdat: String
            updatedat: String
        }

        type Query {
            getProperty(id: ID!): Property
        }
        """
        create_graphql_schema(api_id, definition=schema)

        ds = create_data_source_rds(
            api_id=api_id,
            cluster_arn=db_arn,
            secret_arn=secret_arn,
            database_name=db_name,
            region_name=region_name,
        )
        snapshot.add_transformer(snapshot.transform.regex(ds["name"], "<data-source-name>"))
        snapshot.match("data-source-definition", ds)

        req_template = """
        {
            "version": "2018-05-29",
            "statements": [
                "select id, owner_id as ownerid, title, description, status, price, DATE_FORMAT(created_at, '%Y-%m-%d') as createdat, DATE_FORMAT(updated_at, '%Y-%m-%d') as updatedat FROM properties where id=:ID"
            ],
            "variableMap": {
                ":ID": $util.toJson($ctx.arguments.id)
            }
        }
        """

        res_template = """
        #if($utils.rds.toJsonObject($ctx.result)[0].isEmpty())
          null
        #else
          $utils.toJson($utils.rds.toJsonObject($ctx.result)[0][0])
        #end
        """

        create_resolver(
            apiId=api_id,
            typeName="Query",
            fieldName="getProperty",
            dataSourceName=ds["name"],
            kind="UNIT",
            requestMappingTemplate=req_template,
            responseMappingTemplate=res_template,
        )

        # Make a request into the API
        graphql_endpoint = appsync_graphql_api["uris"]["GRAPHQL"]
        query = """
        query MyQuery($id:ID!) {
          getProperty(id: $id) {
            title
            id
            description
            price
            status
            ownerid
            updatedat
            createdat
          }
        }
        """

        # wait for IAM propagation
        if is_aws_cloud():
            LOG.debug("Sleeping for IAM role propagation")
            time.sleep(20)

        query_payload = {"query": query, "variables": {"id": property_id}}
        response = requests.post(
            graphql_endpoint, json=query_payload, headers={"x-api-key": api_key}
        )

        snapshot.match(
            "response-with-item", {"payload": response.json(), "status-code": response.status_code}
        )

        # capture a snapshot where the item does not exist
        query_payload = {"query": query, "variables": {"id": "invalid-id"}}
        response = requests.post(
            graphql_endpoint, json=query_payload, headers={"x-api-key": api_key}
        )

        snapshot.match(
            "response-without-item",
            {"payload": response.json(), "status-code": response.status_code},
        )

    @pytest.mark.skip(reason="TODO")
    @markers.aws.unknown
    def test_value_propagation_in_pipeline_resolver(self):
        """
        Test that the context result is propagated properly in pipeline
        resolver, i.e. that the result of the nth response mapping template is
        propagated to the ctx.prev.result of the (n+1)th.
        """
        raise NotImplementedError

    @markers.aws.validated
    def test_iam_authorization(
        self,
        appsync_create_api,
        create_lambda_function,
        create_resolver,
        create_graphql_schema,
        create_role_with_policy_for_principal,
        aws_client,
        aws_http_client_factory,
        snapshot,
    ):
        # create lambda
        function_name = f"test-appsync-auth-{short_uid()}"
        response = create_lambda_function(
            func_name=function_name, handler_file=LAMBDA_AUTHORIZATION_HANDLER
        )
        function_arn = response["CreateFunctionResponse"]["FunctionArn"]

        # get API and request headers
        appsync_graphql_api = appsync_create_api(
            authenticationType="AWS_IAM",
        )
        api_id = appsync_graphql_api["apiId"]

        # grant AppSync API access to invoke the authorizer Lambda
        aws_client.lambda_.add_permission(
            FunctionName=function_name,
            StatementId=f"s-{short_uid()}",
            Action="lambda:InvokeFunction",
            Principal="appsync.amazonaws.com",
            SourceArn=appsync_graphql_api["arn"],
        )
        _, role_arn = create_role_with_policy_for_principal(
            principal={"Service": "appsync.amazonaws.com"},
            resource=function_arn,
            effect="Allow",
            actions=["lambda:InvokeFunction"],
        )

        # create test schema
        schema = textwrap.dedent(
            """
            type Mutation {
                create: String! @aws_iam
            }
            type Query {
                test: String @aws_iam
            }
            schema {
                query: Query
                mutation: Mutation
            }
            """
        )

        create_graphql_schema(api_id=api_id, definition=schema)
        req_template = """
                {
                    "version": "2018-05-29",
                    "operation": "Invoke",
                    "payload": $util.toJson($context)
                }
                """

        res_template = "$util.toJson($context.result)"

        # create data source
        aws_client.appsync.create_data_source(
            apiId=api_id,
            name="ds1",
            type="AWS_LAMBDA",
            lambdaConfig={"lambdaFunctionArn": function_arn},
            serviceRoleArn=role_arn,
        )

        # create resolver
        create_resolver(
            apiId=api_id,
            typeName="Query",
            fieldName="test",
            dataSourceName="ds1",
            requestMappingTemplate=req_template,
            responseMappingTemplate=res_template,
        )

        create_resolver(
            apiId=api_id,
            typeName="Mutation",
            fieldName="create",
            dataSourceName="ds1",
            requestMappingTemplate=req_template,
            responseMappingTemplate=res_template,
        )

        queries = [
            ("query", "query { test }"),
            ("mutation", "mutation RunCreate { create }"),
        ]
        url = appsync_graphql_api["uris"]["GRAPHQL"]
        for query_type, query in queries:
            # run query - invalid credentials
            query_request = json.dumps({"query": query})
            result = requests.post(
                url, data=query_request, headers={"Authorization": "invalidtoken123"}
            )
            assert not result.ok
            if is_aws_cloud():
                expected = {
                    "errorType": "IncompleteSignatureException",
                    "message": "Authorization header requires 'Credential' parameter. Authorization header requires 'Signature' parameter. Authorization header requires 'SignedHeaders' parameter. Authorization header requires existence of either a 'X-Amz-Date' or a 'Date' header. Authorization=invalidtoken123",
                }
                expected_status_code = 403
                snapshot.match(
                    f"invalid-credentials-{query_type}",
                    {"payload": result.json(), "statusCode": result.status_code},
                )
            else:
                # FIXME: raise the proper exception from Appsync
                expected = {
                    "errorType": "UnauthorizedException",
                    "message": "You are not authorized to make this call.",
                }
                expected_status_code = 401

            assert result.status_code == expected_status_code
            assert json.loads(to_str(result.content)) == {"errors": [expected]}

            # run query - valid credentials
            def run_query():
                # using a valid Signature so that the request can be authenticated
                # https://docs.aws.amazon.com/appsync/latest/devguide/security-authz.html#aws-iam-authorization
                # this test with the root account, so it does not really check permission/authorization, but that it at
                # least works and is authorized
                appsync_http_client = aws_http_client_factory("appsync", signer_factory=SigV4Auth)
                _result = appsync_http_client.post(url, data=query_request)
                content = to_str(_result.content)
                assert _result.ok
                assert "errors" not in content
                field_assert = "test" if query_type == "query" else "create"
                assert json.loads(content) == {"data": {field_assert: "{}"}}

            retry(run_query, sleep=1, retries=10)

    @markers.aws.validated
    def test_dynamodb_resolver_scan(
        self,
        appsync_graphql_api,
        appsync_create_api_key,
        create_graphql_schema,
        create_data_source_ddb,
        create_resolver,
        snapshot,
        aws_client,
    ):
        api_id = appsync_graphql_api["apiId"]
        schema = textwrap.dedent(
            """
            type Row {
                test: String!
                value: String!
            }

            type Query {
                value: [Row!]!
            }
            schema {
                query: Query
            }
            """
        )
        create_graphql_schema(api_id, definition=schema)

        dynamo_table_name = f"table-{short_uid()}"
        res = create_data_source_ddb(api_id=api_id, name="ddb", table_name=dynamo_table_name)

        # insert some data
        aws_client.dynamodb.put_item(
            TableName=dynamo_table_name, Item={"test": {"S": "a"}, "value": {"S": "b"}}
        )
        aws_client.dynamodb.put_item(
            TableName=dynamo_table_name, Item={"test": {"S": "c"}, "value": {"S": "d"}}
        )
        aws_client.dynamodb.put_item(
            TableName=dynamo_table_name, Item={"test": {"S": "e"}, "value": {"S": "d"}}
        )

        req_template = """
        {
            "version": "2018-05-29",
            "operation": "Scan",
            "filter": {
              "expression": "#value = :value",
              "expressionNames": {
                "#value": "value"
              },
              "expressionValues": {
                ":value": $util.dynamodb.toDynamoDBJson("d")
              }
            }
        }
        """

        res_template = "$util.toJson($context.result.items)"

        create_resolver(
            apiId=api_id,
            typeName="Query",
            fieldName="value",
            dataSourceName=res["name"],
            requestMappingTemplate=req_template,
            responseMappingTemplate=res_template,
        )

        api_key = appsync_create_api_key(api_id)["id"]
        graphql_endpoint = appsync_graphql_api["uris"]["GRAPHQL"]
        query = "query MyQuery { value { test value } }"
        query_payload = {"query": query}

        if is_aws_cloud():
            # TODO: potentially replace with retry mechanism
            LOG.warning("sleeping for IAM role propagation")
            time.sleep(10)

        response = requests.post(
            graphql_endpoint, json=query_payload, headers={"x-api-key": api_key}
        )
        result = {
            "status_code": response.status_code,
            "body": sorted(response.json()["data"]["value"], key=lambda d: d["test"]),
        }
        snapshot.match("response", result)

    @markers.aws.validated
    def test_aws_scalar_in_schema_declaration(
        self,
        appsync_create_api_key,
        create_graphql_schema,
        aws_client,
        snapshot,
        appsync_graphql_api,
    ):
        # get API and request headers
        api_id = appsync_graphql_api["apiId"]
        api_key = appsync_create_api_key(api_id)["id"]

        # create test schema
        schema = """
        scalar AWSDate
        type Response {
          awsDate: AWSDate!
        }
        type Query {
          test: Response!
        }
        """
        create_graphql_schema(api_id=api_id, definition=schema)

        # create data source
        aws_client.appsync.create_data_source(
            apiId=api_id,
            name="ds1",
            type="NONE",
        )

        # create resolver
        aws_client.appsync.create_resolver(
            apiId=api_id,
            typeName="Query",
            fieldName="test",
            dataSourceName="ds1",
            requestMappingTemplate="""{
                "version": "2018-05-29",
                "payload": $utils.toJson({ "awsDate": "2200-02-07" })
            }""",
            responseMappingTemplate="""
            $utils.toJson($ctx.result)
            """,
        )

        query_request = {"query": "query { test { awsDate }}"}
        url = appsync_graphql_api["uris"]["GRAPHQL"]

        def run_query():
            headers = {"x-api-key": api_key}
            result = requests.post(url, json=query_request, headers=headers)
            result.raise_for_status()
            return result

        result = retry(run_query, sleep=1, retries=10)
        content = to_str(result.content)
        assert result.ok
        snapshot.match("result", json.loads(content))

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(
        # TODO AWS constructs the messages in a different manner than Graphql
        paths=["$..errors..errorType", "$..errors..locations", "$..errors..message"]
    )
    def test_inline_fragment_union(
        self,
        appsync_create_api_key,
        create_graphql_schema,
        aws_client,
        snapshot,
        appsync_graphql_api,
    ):
        # get API and request headers
        api_id = appsync_graphql_api["apiId"]
        api_key = appsync_create_api_key(api_id)["id"]

        # create test schema
        schema = """
        type Query {
            getClients (success: Boolean!): [Client!]
        }
        union Client = MainClient | SecondaryClient
        type MainClient {
            clientId: Int!
            name: String!
            main: String!
        }
        type SecondaryClient {
            clientId: Int!
            name: String!
            secondary: String!
        }
        """
        create_graphql_schema(api_id=api_id, definition=schema)

        # create data source
        aws_client.appsync.create_data_source(
            apiId=api_id,
            name="ds1",
            type="NONE",
        )

        # create resolver
        aws_client.appsync.create_resolver(
            apiId=api_id,
            typeName="Query",
            fieldName="getClients",
            dataSourceName="ds1",
            requestMappingTemplate="""
            {
                "version": "2018-05-29",
                "payload": [
                    #if ( $context.arguments.success == true )
                        {
                            "name": "main_client",
                            "clientId": 1,
                            "main": "from main client",
                            "__typename": "MainClient"
                        },
                        {
                            "name": "secondary_client",
                            "clientId": 1,
                            "secondary": "from secondary client",
                            "__typename": "SecondaryClient"
                        }
                    #else
                        {
                            "name": "missing main",
                            "clientId": 2,
                            "secondary": "wrong key",
                            "__typename": "MainClient"
                        }
                    #end
                ]
            }
            """,
            responseMappingTemplate="""
            $utils.toJson($ctx.result)
            """,
        )

        query = """
                query GetClients {
                    getClients ( success: %s ) {
                        __typename
                        ...on MainClient{
                            clientId
                            name
                            main
                        }
                        ...on SecondaryClient{
                            clientId
                            name
                            secondary
                        }
                    }
                }
            """
        url = appsync_graphql_api["uris"]["GRAPHQL"]

        def run_query(success: bool = True):
            headers = {"x-api-key": api_key}
            success = "true" if success else "false"
            result = requests.post(url, json={"query": query % success}, headers=headers)
            result.raise_for_status()
            return result

        result = retry(run_query, sleep=1, retries=10)
        content = result.json()
        snapshot.match("successful-query", content)

        result = run_query(success=False)
        content = json.loads(result.content)
        snapshot.match("wrong-type", content)
        assert "Cannot return null for non-nullable" in content["errors"][0]["message"]


class TestAppSyncDynamoDB:
    @markers.aws.validated
    def test_filter_expressions(
        self,
        appsync_graphql_api,
        appsync_create_api_key,
        create_graphql_schema,
        create_data_source_ddb,
        create_function,
        create_resolver,
        create_dynamodb_table,
        aws_client,
        snapshot,
    ):
        api_id = appsync_graphql_api["apiId"]

        schema = """
        type Row {
            name: String!
            sk: String!
            shift: String!
            value: String!
        }

        input ValueArgs {
            name: String!
            shift: String!
        }

        type Query {
            getValue(filter: ValueArgs): [Row!]!
        }

        schema {
            query: Query
        }
        """
        create_graphql_schema(api_id=api_id, definition=schema)

        dynamo_table_name = f"table-{short_uid()}"
        create_dynamodb_table(
            table_name=dynamo_table_name,
            KeySchema=[
                {"AttributeName": "name", "KeyType": "HASH"},
                {"AttributeName": "sk", "KeyType": "RANGE"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "name", "AttributeType": "S"},
                {"AttributeName": "sk", "AttributeType": "S"},
            ],
            BillingMode="PAY_PER_REQUEST",
        )
        ds = create_data_source_ddb(
            api_id=api_id,
            name="ddb",
            table_name=dynamo_table_name,
            hash_key="name",
            existing_table=True,
        )

        # resolver setup
        resolver_code = prepend_assertion_functions(
            """
        export function request(ctx) {
            return {
                operation: "Query",
                select : "ALL_ATTRIBUTES",
                query: {
                    "expression" : "#name = :name",
                    "expressionNames": {
                        "#name": "name",
                    },
                    "expressionValues" : {
                        ":name" : util.dynamodb.toDynamoDB(ctx.arguments.filter.name),
                    }
                },
                filter: {
                    "expression" : "#shift = :shift",
                    "expressionNames": {
                        "#shift": "shift",
                    },
                    "expressionValues" : {
                        ":shift" : util.dynamodb.toDynamoDB(ctx.arguments.filter.shift),
                    }
                },
            };
        }

        export function response(ctx) {
            assertTrue(Array.isArray(ctx.result.items), "ctx.result.items");
            return ctx.result.items;
        }
        """
        )
        function = create_function(
            api_id=api_id,
            name="getValue",
            dataSourceName=ds["name"],
            code=resolver_code,
            runtime={"name": "APPSYNC_JS", "runtimeVersion": "1.0.0"},
        )["functionConfiguration"]

        pipeline_code = prepend_assertion_functions(
            """
        export function request(ctx) {
          assertTypeOf(ctx, "object", "pipeline.request.ctx");
          return ctx;
        }
        export function response(ctx) {
          assertTypeOf(ctx, "object", "pipeline.response.ctx");
          assertTypeOf(ctx.prev, "object", "pipeline.response.ctx.prev");
          assertTypeOf(ctx.prev.result, "object", "pipeline.response.ctx.prev.result");

          return ctx.prev.result;
        }
        """
        )
        create_resolver(
            apiId=api_id,
            typeName="Query",
            fieldName="getValue",
            kind="PIPELINE",
            code=pipeline_code,
            runtime={"name": "APPSYNC_JS", "runtimeVersion": "1.0.0"},
            pipelineConfig={"functions": [function["functionId"]]},
        )

        # insert some data
        # four items to check both name and filter
        items = [
            {
                "name": "query-match",
                "sk": "sk1",
                "shift": "shift1",
                "value": "foo",
            },
            {
                "name": "query-match",
                "sk": "sk2",
                "shift": "shift2",
                "value": "foo",
            },
            {
                "name": "query-match-bad",
                "sk": "sk1",
                "shift": "shift1",
                "value": "foo",
            },
            {
                "name": "query-match-bad",
                "sk": "sk2",
                "shift": "shift2",
                "value": "foo",
            },
        ]
        for item in items:
            aws_client.dynamodb.put_item(
                TableName=dynamo_table_name,
                Item={key: {"S": value} for (key, value) in item.items()},
            )

        query = """
        query MyQuery($filter: ValueArgs) {
            getValue(filter: $filter) {
                name
                sk
                shift
                value
            }
        }
        """

        api_key = appsync_create_api_key(api_id)["id"]
        graphql_endpoint = appsync_graphql_api["uris"]["GRAPHQL"]

        def make_request(snapshot_prefix: str, filter: dict):
            query_request = {"query": query, "variables": {"filter": filter}}
            result = requests.post(
                graphql_endpoint, json=query_request, headers={"x-api-key": api_key}
            )
            snapshot.match(f"{snapshot_prefix}-response-code", result.status_code)
            json_response = result.json()
            if errors := json_response.get("errors"):
                snapshot.match(f"{snapshot_prefix}-errors", errors)
            if data := json_response.get("data"):
                snapshot.match(f"{snapshot_prefix}-response-data", data)

        make_request("pk-and-filter", {"name": "query-match", "shift": "shift1"})
        make_request("pk-only", {"name": "query-match", "shift": "no-shift1"})
        make_request("filter-only", {"name": "no-query-match", "shift": "shift1"})
        make_request("no-match", {"name": "no-query-match", "shift": "no-shift1"})


class TestAppSyncCrud:
    """Basic resource CRUD tests that do not require full integration with data sources, resolvers, etc"""

    @markers.aws.only_localstack
    def test_graphql_custom_id(self, aws_client):
        api_name = f"graphql-api-{short_uid()}"
        api_id = "customid"
        api = aws_client.appsync.create_graphql_api(
            name=api_name, authenticationType="API_KEY", tags={TAG_KEY_CUSTOM_ID: api_id}
        )["graphqlApi"]
        assert api["name"] == api_name
        assert api["apiId"] == api_id

        # cleanup
        aws_client.appsync.delete_graphql_api(apiId=api_id)

    @markers.aws.validated
    def test_api_key(self, appsync_graphql_api, aws_client):
        api_id = appsync_graphql_api["apiId"]

        # The time after which the API key expires. The date is represented as seconds since the epoch, rounded down
        # to the nearest hour.
        now = datetime.datetime.now(tz=datetime.timezone.utc)
        now_rounded_down = datetime.datetime(now.year, now.month, now.day, now.hour)

        expires = now + datetime.timedelta(days=5)
        expires_timestamp = int(expires.timestamp())

        expires_rounded_down = now_rounded_down + datetime.timedelta(days=5)
        expires_rounded_down_timestamp = int(expires_rounded_down.timestamp())

        result = aws_client.appsync.create_api_key(apiId=api_id)
        assert "apiKey" in result
        assert result["apiKey"].get("id")
        api_key = result["apiKey"].get("id")

        keys = aws_client.appsync.list_api_keys(apiId=api_id)["apiKeys"]
        assert len([k for k in keys if k["id"] == api_key]) == 1

        result = aws_client.appsync.update_api_key(
            apiId=api_id, id=api_key, description="updated", expires=expires_timestamp
        )
        assert result["apiKey"]["description"] == "updated"
        assert result["apiKey"]["expires"] == expires_rounded_down_timestamp

    @markers.aws.only_localstack
    def test_create_domain_name(self, appsync_create_domain_name, aws_client):
        domain_names = aws_client.appsync.list_domain_names()["domainNameConfigs"]
        assert len(domain_names) == 0
        domain_name = f"test-domain-{short_uid()}.localhost.localstack.cloud"
        appsync_create_domain_name(domainName=domain_name)

        domain_names = aws_client.appsync.list_domain_names()["domainNameConfigs"]
        assert len(domain_names) == 1
        assert domain_names[0]["domainName"] == domain_name

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(
        paths=[
            "$..requestMappingTemplate",
            "$..responseMappingTemplate",
        ]
    )
    def test_function(self, appsync_graphql_api, aws_client, snapshot):
        snapshot.add_transformer(snapshot.transform.appsync_api())
        func_name = f"function_{short_uid()}"
        api_id = appsync_graphql_api["apiId"]
        snapshot.add_transformer(snapshot.transform.regex(api_id, "<api-id>"))

        ds_name = "ds1"
        aws_client.appsync.create_data_source(
            apiId=api_id,
            name=ds_name,
            type="NONE",
        )

        result = aws_client.appsync.create_function(
            apiId=api_id,
            dataSourceName=ds_name,
            functionVersion="2018-05-29",
            name=func_name,
            requestMappingTemplate="""{
                "version": "2018-05-29",
                "payload": $utils.toJson({ "some": "value" })
            }""",
            responseMappingTemplate="$utils.toJson($ctx.result)",
        )["functionConfiguration"]
        snapshot.match("create-function", result)

        func_id = result["functionId"]
        funcs = aws_client.appsync.list_functions(apiId=api_id)["functions"]
        snapshot.match("list-functions", funcs)

        func = aws_client.appsync.get_function(apiId=api_id, functionId=func_id)[
            "functionConfiguration"
        ]
        snapshot.match("get-function", func)

    @markers.aws.unknown
    def test_resolver_with_cache(self, appsync_graphql_api, create_data_source_ddb, aws_client):
        api_id = appsync_graphql_api["apiId"]
        mut_res_tmpl = "$util.toJson($context.result)"
        qry_req_tmpl = json.dumps(
            {"version": "2017-02-28", "operation": "Invoke", "payload": {"op": "getPosts"}}
        )
        create_data_source_ddb(api_id, name="ds1")
        response = aws_client.appsync.create_resolver(
            apiId=api_id,
            typeName="Query",
            fieldName="getPosts",
            dataSourceName="ds1",
            requestMappingTemplate=qry_req_tmpl,
            responseMappingTemplate=mut_res_tmpl,
        )
        assert "resolver" in response

        caching_config = {"ttl": 1231}
        response = aws_client.appsync.update_resolver(
            apiId=api_id, typeName="Query", fieldName="getPosts", cachingConfig=caching_config
        )
        assert response["resolver"]["cachingConfig"] == caching_config
        response = aws_client.appsync.create_api_cache(
            apiId=api_id,
            ttl=123,
            transitEncryptionEnabled=True,
            atRestEncryptionEnabled=True,
            apiCachingBehavior="FULL_REQUEST_CACHING",
            type="T2_SMALL",
        )
        assert "apiCache" in response
        assert response["apiCache"]["type"] == "T2_SMALL"

        # update API cache
        response = aws_client.appsync.update_api_cache(
            apiId=api_id, ttl=123, apiCachingBehavior="PER_RESOLVER_CACHING", type="T2_MEDIUM"
        )
        assert response["apiCache"]["type"] == "T2_MEDIUM"

    @markers.aws.unknown
    def test_associate_api(self, appsync_graphql_api, appsync_create_domain_name, aws_client):
        api_id = appsync_graphql_api["apiId"]
        domain_name = f"test-domain-{short_uid()}.localhost.localstack.cloud"
        appsync_create_domain_name(domainName=domain_name)

        response = aws_client.appsync.associate_api(domainName=domain_name, apiId=api_id)
        assert response["apiAssociation"]["domainName"] == domain_name
        assert response["apiAssociation"]["apiId"] == api_id

    @markers.aws.unknown
    def test_get_api_association(self, appsync_graphql_api, appsync_create_domain_name, aws_client):
        api_id = appsync_graphql_api["apiId"]
        domain_name = f"test-domain-{short_uid()}.localhost.localstack.cloud"
        appsync_create_domain_name(domainName=domain_name)

        aws_client.appsync.associate_api(domainName=domain_name, apiId=api_id)
        response = aws_client.appsync.get_api_association(domainName=domain_name)
        assert response["apiAssociation"]["domainName"] == domain_name
        assert response["apiAssociation"]["apiId"] == api_id

    @markers.aws.unknown
    def test_disassociate_api(self, appsync_graphql_api, appsync_create_domain_name, aws_client):
        api_id = appsync_graphql_api["apiId"]
        domain_name = f"test-domain-{short_uid()}.localhost.localstack.cloud"
        appsync_create_domain_name(domainName=domain_name)
        aws_client.appsync.associate_api(domainName=domain_name, apiId=api_id)

        aws_client.appsync.disassociate_api(domainName=domain_name)
        with pytest.raises(Exception) as e:
            aws_client.appsync.get_api_association(domainName=domain_name)
        e.match("NotFoundException")

    @markers.aws.validated
    def test_introspection_schema(self, appsync_graphql_api, create_graphql_schema, aws_client):
        api_id = appsync_graphql_api["apiId"]

        with pytest.raises(Exception) as exc:
            aws_client.appsync.get_introspection_schema(apiId=api_id, format="SDL")
        exc.match("InvalidSyntaxError")

        create_graphql_schema(api_id=api_id, definition=TEST_SCHEMA)

        result = aws_client.appsync.get_introspection_schema(apiId=api_id, format="SDL")
        schema = to_str(result["schema"].read())
        assert schema == TEST_SCHEMA

    @markers.aws.unknown
    def test_tags(self, appsync_graphql_api, aws_client):
        api_arn = appsync_graphql_api["arn"]
        tags = {"Name": "test", "Env": "test"}
        aws_client.appsync.tag_resource(resourceArn=api_arn, tags=tags)
        response = aws_client.appsync.list_tags_for_resource(resourceArn=api_arn)
        assert response["tags"] == tags

    @markers.aws.validated
    def test_introspection_schema_with_directive_declarations(
        self, appsync_graphql_api, aws_client, create_graphql_schema
    ):
        api_id = appsync_graphql_api["apiId"]
        # trying with a weird user provided schema resulting from the serverless-appsync plugin which can merge lots
        # of schema together
        # also, the schema has a directive on an input type when it's been explicitly not enabled, because AWS will
        # ignore those
        schema_with_directives = textwrap.dedent(
            """
        directive @aws_cognito_user_pools(
          cognito_groups: [String]
        ) on OBJECT | FIELD_DEFINITION
        directive @aws_api_key on OBJECT | FIELD_DEFINITION
        directive @aws_subscribe(mutations: [String!]!) on FIELD_DEFINITION
        schema {
            query: Query
            mutation: Mutation
            subscription: Subscription
        }

        type Query {
            getPostsDDB: [Post!]!
        }

        type Mutation {
            addPostDDB(id: String!): Post!
        }

        type Subscription {
            addedPost: Post
            @aws_subscribe(mutations: ["addPostDDB"])
        }

        type Post {
            id: String!
            time: AWSTimestamp
        }

        type DateObject @aws_cognito_user_pools @aws_api_key {
          date: Int
          offset: Int
          timezoneName: String
        }

        input DateObjectInput @aws_api_key {
          date: Int!
          offset: Int
          timezoneName: String
        }

        type FontObject @aws_cognito_user_pools @aws_api_key {
          name: String
          path: String
        }

        type RelationshipId @aws_cognito_user_pools @aws_api_key {
          id: String
          name: String
          primarySortNumber: Int
        }

        type RelationshipResult @aws_cognito_user_pools @aws_api_key {
          items: [RelationshipId]
          nextToken: String
        }
        """
        )

        create_graphql_schema(api_id=api_id, definition=schema_with_directives)

        result = aws_client.appsync.get_introspection_schema(apiId=api_id, format="SDL")
        schema = to_str(result["schema"].read())
        assert "directive" not in schema
        assert "input" in schema


class TestEvaluateCodeEndpoints:
    @markers.aws.validated
    @pytest.mark.parametrize(
        "function_body",
        [
            'return "ok";',
            "return {a: 10}",
            """
        console.log("Something");
        return 10;
        """,
        ],
        ids=["return-string", "return-dictionary", "log"],
    )
    def test_js_code_evaluation(
        self, aws_client: ServiceLevelClientFactory, function_body, snapshot, request
    ):
        if request.node.callspec.id == "log" and not is_aws_cloud():
            pytest.skip(reason="TODO")

        code = (
            """
        export function request(ctx) {
            %s
        }

        export function response(ctx) {
        }
        """
            % function_body
        )

        context = {}

        res = aws_client.appsync.evaluate_code(
            runtime={"name": "APPSYNC_JS", "runtimeVersion": "1.0.0"},
            code=code,
            context=json.dumps(context),
            function="request",
        )

        snapshot.match("result", res)

    @markers.aws.validated
    @pytest.mark.parametrize(
        "template,context",
        [
            (
                "$util.toJson(10)",
                {},
            ),
            # TODO: ctx.args is not present
            (
                "$util.toJson($ctx.arguments.id)",
                {"arguments": {"id": 10}},
            ),
        ],
        ids=[
            "constant",
            "argument",
        ],
    )
    def test_vtl_code_evaluation(
        self,
        aws_client: ServiceLevelClientFactory,
        snapshot,
        template,
        context,
    ):
        res = aws_client.appsync.evaluate_mapping_template(
            template=template,
            context=json.dumps(context),
        )

        snapshot.match("result", res)

    @markers.aws.validated
    @pytest.mark.parametrize(
        "name,version",
        [
            # valid
            ("APPSYNC_JS", "1.0.0"),
            # invalid
            ("APPSYNC_JS2", "1.0.0"),
            ("APPSYNC_JS", "1.0.1"),
            ("APPSYNC_JS", "1.1.0"),
            ("APPSYNC_JS2", "1.1.0"),
        ],
    )
    def test_supported_js_runtimes(self, name, version, aws_client, snapshot):
        function_body = """
        export function request(ctx) {
        }

        export function response(ctx) {
        }
        """
        context = {}
        try:
            res = aws_client.appsync.evaluate_code(
                runtime={"name": name, "runtimeVersion": version},
                code=function_body,
                context=json.dumps(context),
                function="request",
            )

            snapshot.match("result", res)
        except ClientError as e:
            snapshot.match("client-error", e.response)


class TestTemplateRendering:
    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(
        # currently a mismatch between None (expected) and "" (actual) for `condition`
        paths=["$..condition"]
    )
    def test_template_rendering_with_newlines(self, snapshot, aws_client):
        template = r"""
        #set( $modelObjectKey = {
          "userId": $util.dynamodb.toDynamoDB($ctx.args.input.userId),
          "domain": $util.dynamodb.toDynamoDB($ctx.args.input.domain)
        } )

        {
          "version": "2018-05-29",
          "operation": "PutItem",
          "key": #if( $modelObjectKey ) $util.toJson($modelObjectKey) #else {
          "id":   $util.dynamodb.toDynamoDBJson($ctx.args.input.id)
        } #end,
          "attributeValues": $util.dynamodb.toMapValuesJson($context.args.input),
          "condition": $util.toJson($condition)
        }
        """
        context = ResolverProcessingContext()
        context.arguments["input"] = {
            "userId": "my-user-id",
            "domain": "my-domain",
            "id": "my-id",
        }

        result = self.process_template_rendering(template, aws_client.appsync, context=context)
        snapshot.match("resolved-template", result)

    @markers.aws.validated
    def test_null_rendering(self, snapshot, aws_client):
        template = r"""
        #set($myMap = {})
        $util.qr($myMap.put('myKey', null))
        $util.qr($myMap.put('myOtherKey', 10))
        $util.toJson($myMap)
        """

        result = self.process_template_rendering(template, aws_client.appsync)

        snapshot.match("resolved-template", result)

    @markers.aws.validated
    @pytest.mark.parametrize(
        "sort_list_arguments",
        [
            '[{"userid":"user3", "age":85}, {"userid":"user1", "age":5}, {"userid":"user2", "age":45}], true, "userid"',
            '[{"userid":"user3", "age":85}, {"userid":"user1", "age":5}, {"userid":"user2", "age":45}], false, "userid"',
            '[{"userid":"user3", "age":85}, {"age":5}, {"userid":"user2", "age":45}], false, "userid"',
            '[{"userid":"user3", "age":85}, {"userid":"user1", "age":5}, 1, "1", "String"], false, "userid"',
            '["user3", "user1", "user2"], false, "random"',
            '["user3", "user1", "user2"], true, "random"',
            '["user3", "user1", "user2", 1], true, "random"',
            '["3", "1", "2", 1], true, "random"',
            '[3, 1, 2], false, "random"',
            '[3, 1, 2], true, "random"',
        ],
    )
    def test_template_rendering_with_list_sort_list(
        self, aws_client, snapshot, sort_list_arguments
    ):
        template = rf"""
        $util.toJson(
            $util.list.sortList({sort_list_arguments})
        )
        """
        result = self.process_template_rendering(template, aws_client.appsync)
        snapshot.match("resolved-template", result)

    @markers.aws.validated
    @pytest.mark.parametrize(
        "list1, list2",
        [
            ([1, 2, 3], [2, 3]),
            ([], [2, 3]),
            ([1, 2, 3], []),
            ([{"id": 1}, {"id": 2}, {"id": 3}], [{"id": 2}, {"id": 3}]),
            (
                [
                    {"userid": "user3", "age": 85},
                    {"userid": "user1", "age": 5},
                    {"userid": "user2", "age": 45},
                ],
                [{"userid": "user2", "age": 45}, {"userid": "user3", "age": 85}],
            ),
            (
                [
                    {"userid": "user3", "age": 85},
                    {"userid": "user1", "age": 5},
                    {"userid": "user2", "age": 45},
                ],
                [{"userid": "user2"}],
            ),
            (
                [
                    {"userid": "user3", "age": {"years": 85, "months": 2}},
                    {"userid": "user1", "age": 5},
                    {"userid": "user2", "age": 45},
                ],
                [{"userid": "user3", "age": {"years": 85, "months": 2}}],
            ),
            (
                [
                    {"userid": "user3", "age": {"years": 85, "months": 2}},
                    {"userid": "user1", "age": 5},
                    {"userid": "user2", "age": 45},
                ],
                [{"userid": "user3", "age": {"years": 85}}],
            ),
        ],
    )
    def test_template_rendering_list_copy_and_retain_all(self, aws_client, snapshot, list1, list2):
        template = rf"""
        $util.toJson(
            $util.list.copyAndRetainAll({list1}, {list2})
        )
        """
        result = self.process_template_rendering(template, aws_client.appsync)
        snapshot.match("resolved-template", result)

    @markers.aws.validated
    @pytest.mark.parametrize(
        "list1, list2",
        [
            ([1, 2, 3], [2, 3]),
            ([1, 2, 3], [1, 2, 3]),
            ([], [2, 3]),
            ([1, 2, 3], []),
            ([{"id": 1}, {"id": 2}, {"id": 3}], [{"id": 2}, {"id": 3}]),
            (
                [
                    {"userid": "user3", "age": 85},
                    {"userid": "user1", "age": 5},
                    {"userid": "user2", "age": 45},
                ],
                [{"userid": "user2", "age": 45}, {"userid": "user3", "age": 85}],
            ),
            (
                [
                    {"userid": "user3", "age": 85},
                    {"userid": "user1", "age": 5},
                    {"userid": "user2", "age": 45},
                ],
                [{"userid": "user2"}],
            ),
            (
                [
                    {"userid": "user3", "age": {"years": 85, "months": 2}},
                    {"userid": "user1", "age": 5},
                    {"userid": "user2", "age": 45},
                ],
                [{"userid": "user3", "age": {"years": 85, "months": 2}}],
            ),
            (
                [
                    {"userid": "user3", "age": {"years": 85, "months": 2}},
                    {"userid": "user1", "age": 5},
                    {"userid": "user2", "age": 45},
                ],
                [{"userid": "user3", "age": {"years": 85}}],
            ),
        ],
    )
    def test_template_rendering_list_copy_and_remove_all(self, aws_client, snapshot, list1, list2):
        template = rf"""
        $util.toJson(
            $util.list.copyAndRemoveAll({list1}, {list2})
        )
        """
        result = self.process_template_rendering(template, aws_client.appsync)
        snapshot.match("resolved-template", result)

    @markers.aws.validated
    @pytest.mark.parametrize(
        "util_func, expected_regex",
        [
            ("$util.time.nowISO8601()", r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d{3}Z$"),
            ("$util.time.nowEpochSeconds()", r"\d{10}$"),
            ("$util.time.nowEpochMilliSeconds()", r"\d{13}$"),
            (
                "$util.time.parseISO8601ToEpochMilliSeconds('2018-02-01T17:21:05.180+08:00')",
                "1517476865180",
            ),
            ("$util.time.epochMilliSecondsToSeconds(1517943695758)", "1517943695"),
            ("$util.time.epochMilliSecondsToISO8601(1517943695758)", "2018-02-06T19:01:35.758Z"),
        ],
    )
    def test_template_rendering_time(self, aws_client, util_func, expected_regex):
        template = rf"""
        $util.toJson(
        {util_func}
        )
        """
        result = self.process_template_rendering(template, aws_client.appsync)
        assert re.match(expected_regex, str(result))

    def process_template_rendering(
        self,
        template: str,
        appsync_client: "AppSyncClient",
        context: ResolverProcessingContext | None = None,
    ) -> Any:
        context = context or ResolverProcessingContext()
        if is_aws_cloud():
            return self.render_template_with_aws(template, context.to_dict(), appsync_client)
        else:
            return render_template(template, context_obj=context)

    @staticmethod
    def render_template_with_aws(
        template: str, context: dict, appsync_client: "AppSyncClient"
    ) -> Any:
        res = appsync_client.evaluate_mapping_template(
            template=template, context=json.dumps(context)
        )
        return json.loads(res["evaluationResult"])
