import os

import aws_cdk as cdk
import pytest
import requests
from localstack.testing.pytest import markers
from localstack.testing.scenario.provisioning import InfraProvisioner
from localstack.utils.strings import short_uid
from localstack_snapshot.snapshots.transformer import SortingTransformer


@markers.aws.validated
@markers.snapshot.skip_snapshot_verify(
    paths=[
        "$..graphqlApi.xrayEnabled",
        "$..graphqlApi.arn",
        "$..graphqlApi.dns",
        "$..graphqlApi.introspectionConfig",
        "$..graphqlApi.owner",
        "$..graphqlApi.queryDepthLimit",
        "$..graphqlApi.resolverCountLimit",
        "$..graphqlApi.uris.REALTIME",
        "$..graphqlApi.visibility",
    ]
)
def test_graphqlapi(deploy_cfn_template, snapshot, aws_client):
    snapshot.add_transformer(
        snapshot.transform.key_value("GraphUrl", "api-url", reference_replacement=False),
        priority=-1,
    )
    snapshot.add_transformer(
        snapshot.transform.key_value("GRAPHQL", "api-url", reference_replacement=False), priority=-1
    )
    snapshot.add_transformer(
        snapshot.transform.key_value("REALTIME", "api-url-realtime"), priority=-1
    )
    snapshot.add_transformer(snapshot.transform.key_value("name", "api-name"))
    snapshot.add_transformer(snapshot.transform.cloudformation_api())

    template_path = os.path.join(
        os.path.dirname(__file__), "../../../templates/appsync_graphql_api.yml"
    )
    stack = deploy_cfn_template(
        template_path=template_path, parameters={"ApiName": f"api-{short_uid()}"}
    )
    snapshot.match("stack_outputs", stack.outputs)

    description = aws_client.cloudformation.describe_stack_resources(StackName=stack.stack_name)
    snapshot.match("stack_resource_descriptions", description["StackResources"])

    api = aws_client.appsync.get_graphql_api(apiId=stack.outputs["GraphApiId"])
    snapshot.match("api", api)


@markers.aws.validated
@markers.snapshot.skip_snapshot_verify(
    paths=[
        "$..type.format",
        "$..type.definition",
        "$..SchemaRef",
    ]
)
def test_graphql_schema(deploy_cfn_template, snapshot, aws_client):
    snapshot.add_transformer(snapshot.transform.cloudformation_api())
    snapshot.add_transformer(SortingTransformer("StackResources", lambda x: x["LogicalResourceId"]))

    template_path = os.path.join(
        os.path.dirname(__file__), "../../../templates/appsync_graphql_schema.yml"
    )
    stack = deploy_cfn_template(
        template_path=template_path, parameters={"ApiName": f"api-{short_uid()}"}, max_wait=120
    )
    snapshot.match("stack_outputs", stack.outputs)

    description = aws_client.cloudformation.describe_stack_resources(StackName=stack.stack_name)
    snapshot.match("stack_resource_descriptions", description)

    model = aws_client.appsync.get_type(
        apiId=stack.outputs["ApiId"], format="JSON", typeName="Todo"
    )
    snapshot.match("model", model)


@markers.aws.validated
def test_s3_code_locations(deploy_cfn_template, s3_create_bucket, aws_client, snapshot):
    assets_bucket = s3_create_bucket()

    def upload_file(text: str, path: str):
        aws_client.s3.put_object(Bucket=assets_bucket, Key=path, Body=text.encode("utf8"))
        return f"s3://{assets_bucket}/{path}"

    schema_text = """
        type Todo {
          id: ID!
        }

        type Query {
          todo: Todo!
        }

        schema {
          query: Query
        }
    """
    schema_s3_location = upload_file(schema_text, "schema.graphql")

    resolver_code = """
    export function request(ctx) {
        return {};
    }

    export function response(ctx) {
        return ctx.prev.result;
    }
    """
    resolver_s3_location = upload_file(resolver_code, "resolver.js")

    function_code = """
    export function request(ctx) {
        return {
            payload: {
                id: "abc123",
            },
        };
    }

    export function response(ctx) {
        return ctx.result;
    }
    """
    function_s3_location = upload_file(function_code, "function.js")

    template_path = os.path.join(
        os.path.dirname(__file__),
        "../../../templates/appsync_s3_code_locations.yml",
    )
    stack = deploy_cfn_template(
        template_path=template_path,
        parameters={
            "SchemaS3Location": schema_s3_location,
            "ResolverCodeS3Location": resolver_s3_location,
            "FunctionCodeS3Location": function_s3_location,
            "ApiName": f"api-{short_uid()}",
        },
        max_wait=120,
    )

    url = stack.outputs["GraphQLUrl"]
    api_key = stack.outputs["ApiKeyValue"]

    # make request
    query = {"query": "query { todo { id } }"}
    r = requests.post(url, json=query, headers={"x-api-key": api_key})
    r.raise_for_status()

    snapshot.match("response-body", r.json())


@markers.aws.validated
class TestExpandedScenario:
    STACK_NAME = "AppSyncStack"

    @pytest.fixture(scope="class")
    def infrastructure(self, aws_client, infrastructure_setup):
        infra: InfraProvisioner = infrastructure_setup(
            namespace="AppSyncIaCTest",
        )

        stack = cdk.Stack(infra.cdk_app, self.STACK_NAME)

        api_name = f"graphql-api-{short_uid()}"
        api = cdk.aws_appsync.GraphqlApi(
            stack,
            "Api",
            name=api_name,
            definition=cdk.aws_appsync.Definition.from_file(
                os.path.join(os.path.dirname(__file__), "resources/schema.graphql")
            ),
        )

        # create the dynamodb table
        table = cdk.aws_dynamodb.Table(
            stack,
            "DynamoDBTable",
            partition_key={
                "name": "pk",
                "type": cdk.aws_dynamodb.AttributeType.STRING,
            },
            removal_policy=cdk.RemovalPolicy.DESTROY,
            billing_mode=cdk.aws_dynamodb.BillingMode.PAY_PER_REQUEST,
        )
        ddb_data_source = api.add_dynamo_db_data_source("DynamoDBDataSource", table)

        # none data source to resolve the top level object
        none_data_source = api.add_none_data_source("NoneDataSource")
        none_data_source.create_resolver(
            "RootVtlResolver",
            type_name="Query",
            field_name="vtl",
            request_mapping_template=cdk.aws_appsync.MappingTemplate.from_string(
                '{ "version": "2018-05-29", "payload": {"dynamoResult": null} }',
            ),
            response_mapping_template=cdk.aws_appsync.MappingTemplate.from_string(
                "$util.toJson($ctx.result)"
            ),
        )
        none_data_source.create_resolver(
            "RootJSResolver",
            type_name="Query",
            field_name="js",
            request_mapping_template=cdk.aws_appsync.MappingTemplate.from_string(
                '{ "version": "2018-05-29", "payload": {"dynamoResult": null} }',
            ),
            response_mapping_template=cdk.aws_appsync.MappingTemplate.from_string(
                "$util.toJson($ctx.result)"
            ),
        )

        # VTL resolvers
        # dynamodb
        ddb_data_source.create_resolver(
            "DDBDataSourceVtlResolver",
            type_name="VTLResolverResults",
            field_name="dynamoResult",
            request_mapping_template=cdk.aws_appsync.MappingTemplate.from_string(
                """
                {
                    "version" : "2017-02-28",
                    "operation" : "GetItem",
                    "key": {
                        "pk": $util.dynamodb.toDynamoDBJson("abc123")
                    }
                }
                """
            ),
            response_mapping_template=cdk.aws_appsync.MappingTemplate.from_string(
                "$util.toJson($ctx.result.type)"
            ),
        )

        # Add JS pipeline resolver on none data source to ensure JS resolvers work
        pipeline_fn = none_data_source.create_function(
            "PipelineJSFunction",
            name="jsfunction",
            runtime=cdk.aws_appsync.FunctionRuntime.JS_1_0_0,
            code=cdk.aws_appsync.Code.from_inline(
                """
                import { util } from '@aws-appsync/utils';
                export function request(ctx) {
                    return {
                        "version": "2018-05-29",
                        "payload": {
                            "value": "jsresult"
                        }
                    };
                }
                export function response(ctx) {
                    return ctx.result.value;
                }
                """,
            ),
        )

        cdk.aws_appsync.Resolver(
            stack,
            "PipelineJSResolver",
            api=api,
            type_name="JSResolverResults",
            field_name="result",
            runtime=cdk.aws_appsync.FunctionRuntime.JS_1_0_0,
            code=cdk.aws_appsync.Code.from_inline(
                """
                export function request(ctx) {
                    return {};
                }
                export function response(ctx) {
                    return ctx.prev.result;
                }
                """,
            ),
            pipeline_config=[pipeline_fn],
        )

        cdk.CfnOutput(stack, "GraphQLUrl", value=api.graphql_url)
        cdk.CfnOutput(stack, "ApiKeyOutput", value=api.api_key)
        cdk.CfnOutput(stack, "DynamoDBTableName", value=table.table_name)

        with infra.provisioner() as prov:
            yield prov

    @pytest.mark.parametrize(
        "query",
        [
            """
        query VTLDynamoResolver {
            vtl {
                dynamoResult
            }
        }
        """,
            """
        query JSPipelineResolver {
            js {
                result
            }
        }
        """,
            """
        query Full {
            vtl {
                dynamoResult
            }
            js {
                result
            }
        }
            """,
        ],
    )
    def test_deploy_scenario(self, query, infrastructure, aws_client, snapshot):
        outputs = infrastructure.get_stack_outputs(self.STACK_NAME)
        graphql_url = outputs["GraphQLUrl"]
        api_key = outputs["ApiKeyOutput"]
        table_name = outputs["DynamoDBTableName"]

        self.insert_item(aws_client.dynamodb, table_name)

        r = requests.post(
            graphql_url, headers={"X-API-Key": api_key}, json={"query": query, "variables": {}}
        )
        r.raise_for_status()

        snapshot.match("response", r.json())

    @staticmethod
    def insert_item(dynamodb_client, table_name):
        try:
            dynamodb_client.put_item(
                TableName=table_name,
                Item={
                    "pk": {"S": "abc123"},
                    "type": {"S": "dynamodb"},
                },
                ConditionExpression="attribute_not_exists(pk)",
            )
        except dynamodb_client.exceptions.ConditionalCheckFailedException:
            # This is ok since we only want a single item
            pass
