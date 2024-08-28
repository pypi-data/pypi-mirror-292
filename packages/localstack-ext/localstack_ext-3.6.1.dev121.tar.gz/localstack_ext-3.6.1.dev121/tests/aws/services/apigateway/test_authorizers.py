import json
import os
import textwrap

import pytest
import requests
from botocore.exceptions import ClientError
from localstack.aws.api.lambda_ import Runtime
from localstack.constants import APPLICATION_JSON
from localstack.pro.core.services.cognito_idp.cognito_utils import (
    get_auth_token_via_login_form,
    get_issuer_url,
)
from localstack.testing.aws.util import is_aws_cloud
from localstack.testing.pytest import markers
from localstack.utils import testutil
from localstack.utils.aws import arns
from localstack.utils.collections import remove_attributes
from localstack.utils.strings import short_uid, to_str
from localstack.utils.sync import retry

from tests.aws.services.apigateway.apigateway_fixtures import (
    api_invoke_url,
    cognito_confirm_admin_sign_up,
    cognito_sign_up,
    create_http_authorizer,
    create_http_integration,
    create_http_route,
    create_rest_api_integration,
    create_rest_resource,
    create_rest_resource_method,
)
from tests.aws.services.apigateway.conftest import (
    LAMBDA_ECHO_EVENT,
    get_auth_login_via_token_endpoint,
    is_next_gen_api,
)
from tests.aws.services.apigateway.test_http_apis import (
    assert_lambda_authorizer_event_payload_v1,
    assert_lambda_authorizer_event_payload_v2,
    create_deployment,
)

CLOUDFRONT_SKIP_HEADERS = [
    "$..Via",
    "$..X-Amz-Cf-Id",
    "$..CloudFront-Forwarded-Proto",
    "$..CloudFront-Is-Desktop-Viewer",
    "$..CloudFront-Is-Mobile-Viewer",
    "$..CloudFront-Is-SmartTV-Viewer",
    "$..CloudFront-Is-Tablet-Viewer",
    "$..CloudFront-Viewer-ASN",
    "$..CloudFront-Viewer-Country",
]

COGNITO_SKIP_JWT_CLAIMS = [
    "$..claims.iss",
    # AWS has a second of delay between `auth_time` and `iat`
    "$..claims.iat",
    # AWS populates for access token but LS Cognito doesn't
    "$..claims.version",
    # AWS populates for id token but LS Cognito doesn't
    "$..claims.at_hash",
    "$..claims.jti",
    '$..claims["cognito:user_status"]',
]


@pytest.fixture
def create_lambda_authorizer(create_lambda_function, aws_client):
    def _create(lambda_source: str):
        function_name = f"test_apigw_auth-{short_uid()}"

        # create Lambda authorizer
        zip_file = testutil.create_lambda_archive(lambda_source, get_content=True)
        response = create_lambda_function(
            func_name=function_name, zip_file=zip_file, client=aws_client.lambda_
        )
        function_arn = response["CreateFunctionResponse"]["FunctionArn"]

        # allow cognito to call lambda functions, e.g., our trigger lambda
        for principal in ("cognito-idp.amazonaws.com", "apigateway.amazonaws.com"):
            aws_client.lambda_.add_permission(
                FunctionName=function_name,
                StatementId=f"invoke-lambda-{short_uid()}",
                Action="lambda:InvokeFunction",
                Principal=principal,
            )

        return function_arn

    yield _create


@pytest.fixture
def create_mock_integration_with_cognito_authorizer(aws_client):
    def _create_method(
        rest_api_id: str, authorizer: str, path: str, parent_id: str, auth_scope: list[str]
    ):
        if path:
            resource_id = aws_client.apigateway.create_resource(
                restApiId=rest_api_id, parentId=parent_id, pathPart=path
            )["id"]
        else:
            resource_id = parent_id

        aws_client.apigateway.put_method(
            restApiId=rest_api_id,
            resourceId=resource_id,
            httpMethod="GET",
            authorizationType="COGNITO_USER_POOLS",
            authorizationScopes=auth_scope,
            authorizerId=authorizer,
        )
        aws_client.apigateway.put_integration(
            restApiId=rest_api_id,
            resourceId=resource_id,
            httpMethod="GET",
            type="MOCK",
            integrationHttpMethod="POST",
            requestTemplates={"application/json": '{"statusCode": 200}'},
        )
        aws_client.apigateway.put_method_response(
            restApiId=rest_api_id, resourceId=resource_id, httpMethod="GET", statusCode="200"
        )
        aws_client.apigateway.put_integration_response(
            restApiId=rest_api_id,
            resourceId=resource_id,
            httpMethod="GET",
            statusCode="200",
            responseTemplates={
                "application/json": """
                    #set($claims = $context.authorizer.claims)
                    {
                        "claims": {
                            #foreach($claim in $claims.keySet())
                                "$claim": "$claims.get($claim)"
                             #if($foreach.hasNext),#end
                            #end
                        }
                    }
                """
            },
        )

    return _create_method


@pytest.fixture
def cloudfront_transformers(snapshot):
    return [
        snapshot.transform.jsonpath(
            "$..headers.CloudFront-Forwarded-Proto", value_replacement="cf-forward-proto"
        ),
        snapshot.transform.jsonpath(
            "$..headers.CloudFront-Is-Desktop-Viewer", value_replacement="cf-desktop-viewer"
        ),
        snapshot.transform.jsonpath(
            "$..headers.CloudFront-Is-Mobile-Viewer", value_replacement="cf-mobile-viewer"
        ),
        snapshot.transform.jsonpath(
            "$..headers.CloudFront-Is-SmartTV-Viewer", value_replacement="cf-smarttv-viewer"
        ),
        snapshot.transform.jsonpath(
            "$..headers.CloudFront-Is-Tablet-Viewer", value_replacement="cf-tablet-viewer"
        ),
        snapshot.transform.jsonpath(
            "$..headers.CloudFront-Viewer-ASN", value_replacement="cf-viewer-asn"
        ),
        snapshot.transform.jsonpath(
            "$..headers.CloudFront-Viewer-Country", value_replacement="cf-viewer-countrer"
        ),
        snapshot.transform.jsonpath("$..headers.X-Amz-Cf-Id", value_replacement="cf-amz-cf-id"),
        snapshot.transform.jsonpath("$..headers.Via", value_replacement="cf-via"),
    ]


@pytest.fixture
def aws_proxy_transformers(snapshot):
    return [
        snapshot.transform.jsonpath(
            "$..headers.X-Amzn-Trace-Id", value_replacement="x-amz-trace-id"
        ),
        snapshot.transform.key_value(
            "X-Forwarded-For", value_replacement="<x-forwarded-for>", reference_replacement=False
        ),
        snapshot.transform.jsonpath(
            "$..headers.X-Forwarded-Port",
            value_replacement="x-forwarded-port",
            reference_replacement=False,
        ),
    ]


@markers.aws.validated
def test_api_key_authorizer(
    create_rest_apigw,
    aws_client,
    create_lambda_function,
    echo_http_server_post,
    region_name,
    account_id,
    snapshot,
):
    """
    Test API key authorizer
    """
    snapshot.add_transformer(snapshot.transform.key_value("id", "id"))
    snapshot.add_transformer(snapshot.transform.jsonpath("$..stageKeys[0]", "stageKey"))
    snapshot.add_transformer(snapshot.transform.key_value("authorizerKey", "authorizer_key"))
    snapshot.add_transformer(snapshot.transform.key_value("identityApiKey", "authorizer_key"))

    api_id, _, root_resource_id = create_rest_apigw(
        name=f"api-{short_uid()}", apiKeySource="AUTHORIZER"
    )

    resource_id, _ = create_rest_resource(
        aws_client.apigateway, restApiId=api_id, parentId=root_resource_id, pathPart="auth"
    )

    lambda_auth_name = f"lambda_auth-{short_uid()}"
    lambda_request_api_key = os.path.join(
        os.path.dirname(__file__), "../../files/lambda_auth_apikey.py"
    )
    auth_function_response = create_lambda_function(
        handler_file=lambda_request_api_key,
        func_name=lambda_auth_name,
        runtime=Runtime.python3_12,
    )
    lambda_arn = auth_function_response["CreateFunctionResponse"]["FunctionArn"]
    auth_url = arns.apigateway_invocations_arn(lambda_arn, region_name)

    authorizer = aws_client.apigateway.create_authorizer(
        restApiId=api_id,
        name="api_key_authorizer",
        type="REQUEST",
        identitySource="method.request.querystring.apiKey",
        authorizerUri=auth_url,
    )

    source_arn = (
        f'arn:aws:execute-api:{region_name}:{account_id}:{api_id}/authorizers/{authorizer["id"]}'
    )
    aws_client.lambda_.add_permission(
        FunctionName=lambda_auth_name,
        Action="lambda:InvokeFunction",
        StatementId="lambda-authorizer-invoke-permission",
        Principal="apigateway.amazonaws.com",
        SourceArn=source_arn,
    )

    create_rest_resource_method(
        aws_client.apigateway,
        restApiId=api_id,
        resourceId=resource_id,
        httpMethod="GET",
        authorizationType="CUSTOM",
        apiKeyRequired=True,
        authorizerId=authorizer["id"],
    )

    create_rest_api_integration(
        aws_client.apigateway,
        restApiId=api_id,
        resourceId=resource_id,
        httpMethod="GET",
        type="HTTP",
        integrationHttpMethod="POST",
        uri=echo_http_server_post,
        requestTemplates={
            "application/json": '{"authorizerKey": "$context.authorizer.manuallySetKeyInContext", "identityApiKey":"$context.identity.apiKey"}'
        },
    )

    aws_client.apigateway.put_method_response(
        restApiId=api_id,
        resourceId=resource_id,
        httpMethod="GET",
        statusCode="200",
    )

    aws_client.apigateway.put_integration_response(
        restApiId=api_id,
        resourceId=resource_id,
        httpMethod="GET",
        statusCode="200",
        selectionPattern="200",
    )

    deployment_id = aws_client.apigateway.create_deployment(restApiId=api_id)["id"]

    # create stage
    stage_name = "dev"
    aws_client.apigateway.create_stage(
        restApiId=api_id, stageName=stage_name, deploymentId=deployment_id
    )

    # create api key and snapshot response API
    api_key = aws_client.apigateway.create_api_key(
        name="test_api_key",
        enabled=True,
        stageKeys=[{"restApiId": api_id, "stageName": stage_name}],
    )
    snapshot.match("create_api_key_response", api_key)

    usage_plan = aws_client.apigateway.create_usage_plan(
        name="test_usage_plan",
        apiStages=[{"apiId": api_id, "stage": stage_name}],
        throttle={"rateLimit": 10, "burstLimit": 2},
        quota={"limit": 100, "period": "MONTH"},
    )

    aws_client.apigateway.create_usage_plan_key(
        usagePlanId=usage_plan["id"], keyType="API_KEY", keyId=api_key["id"]
    )

    def call_api(api_key, expected_status_code):
        endpoint = api_invoke_url(api_id=api_id, stage=stage_name, path="/auth")
        result = requests.get(endpoint, params={"apiKey": api_key}, verify=False)
        assert result.status_code == expected_status_code
        return result

    # test a valid api key
    if is_aws_cloud():
        retries = 30
        sleep = 5
    else:
        retries = 3
        sleep = 1
    response = retry(
        call_api, retries=retries, sleep=sleep, api_key=api_key["value"], expected_status_code=200
    )
    snapshot.match("valid_api_key", response.json().get("data"))

    # test invalid api key
    response = retry(
        call_api, retries=retries, sleep=sleep, api_key="invalid", expected_status_code=403
    )
    snapshot.match("invalid_api_key", response.json())


class TestRestApiAuthorizers:
    LAMBDA_AUTH_FORWARD_TO_SQS = textwrap.dedent(
        """
    import boto3, json, os
    def handler(event, context, *args):
        # send message to SQS for later inspection and assertions
        sqs_client = client = boto3.client("sqs", endpoint_url=os.environ.get('AWS_ENDPOINT_URL'))
        message = {"event": event}
        sqs_client.send_message(QueueUrl="<sqs_url>", MessageBody=json.dumps(message), MessageGroupId="1")

        statement = {'Action': 'execute-api:Invoke', 'Effect': 'Deny', 'Resource': f'{event["methodArn"]}*'}
        policy = {'policyDocument': {'Version': '2012-10-17', 'Statement': [statement]}}
        result = {'principalId': 'principal123', **policy}
        return result
    """
    )

    LAMBDA_AUTH_ATTACH_TO_CONTEXT = textwrap.dedent(
        """
    import boto3, json, os
    def handler(event, context, *args):
        statement = {'Action': 'execute-api:Invoke', 'Effect': 'Allow', 'Resource': f'{event["methodArn"]}*'}
        policy = {'policyDocument': {'Version': '2012-10-17', 'Statement': [statement]}}
        result = {'principalId': 'principal123', **policy}
        result["context"] = {"payload": json.dumps(event)}
        return result
    """
    )

    # TODO: use this response tempalte to provide $context.identity and $context.authorizer are not returning full dict
    #  for now, it is not supported so we use AUTH_RESPONSE_TEMPLATE_SIMPLE
    AUTH_RESPONSE_TEMPLATE = textwrap.dedent(
        """
    {
        "identity": "$context.identity",
        "authorizer": "$context.authorizer",
        "identity_keys": {
        #foreach( $key in $context.identity.keySet() )
         "$key": "$context.identity.get($key)"#if($foreach.hasNext),#end
        #end
        },
        "authorizer_keys": {
        #foreach( $key in $context.authorizer.keySet() )
         "$key": "$util.escapeJavaScript($context.authorizer.get($key))"#if($foreach.hasNext),#end
        #end
        }
    }
    """
    )

    AUTH_RESPONSE_TEMPLATE_SIMPLE = textwrap.dedent(
        """
    {
        "identity_keys": {
        #foreach( $key in $context.identity.keySet() )
         "$key": "$context.identity.get($key)"#if($foreach.hasNext),#end
        #end
        },
        "authorizer_keys": {
        #foreach( $key in $context.authorizer.keySet() )
         "$key": "$util.escapeJavaScript($context.authorizer.get($key))"#if($foreach.hasNext),#end
        #end
        }
    }
    """
    )

    @pytest.fixture
    def _create_method_and_integration(self, aws_client_factory):
        def _create(
            rest_api_id: str,
            resource_id: str,
            identity_sources: list[str],
            authorizer_id: str | None = None,
            response_templates=None,
            integration_kwargs=None,
            region_name=None,
        ):
            aws_client = aws_client_factory(region_name=region_name)

            kwargs = {"authorizerId": authorizer_id} if authorizer_id else {}
            request_parameters = {source: True for source in identity_sources}
            aws_client.apigateway.put_method(
                restApiId=rest_api_id,
                resourceId=resource_id,
                httpMethod="GET",
                authorizationType="CUSTOM",
                requestParameters=request_parameters,
                **kwargs,
            )

            integration_kwargs = integration_kwargs or {}
            integration_kwargs.setdefault("type", "MOCK")
            create_rest_api_integration(
                aws_client.apigateway,
                restApiId=rest_api_id,
                resourceId=resource_id,
                httpMethod="GET",
                requestTemplates={APPLICATION_JSON: json.dumps({"statusCode": 200})},
                **integration_kwargs,
            )

            aws_client.apigateway.put_method_response(
                restApiId=rest_api_id,
                resourceId=resource_id,
                httpMethod="GET",
                statusCode="200",
            )

            kwargs = {"responseTemplates": response_templates} if response_templates else {}
            aws_client.apigateway.put_integration_response(
                restApiId=rest_api_id,
                resourceId=resource_id,
                httpMethod="GET",
                statusCode="200",
                selectionPattern="200",
                **kwargs,
            )

        return _create

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(
        paths=[
            "$..authType",
            "$..event.headers",
            "$..event.multiValueHeaders",
            "$..event.version",
            "$..authorizationToken",
            "$..requestContext.extendedRequestId",
            "$..requestContext.domainName",
            "$..requestContext.deploymentId",
            "$..requestContext.protocol",
            "$..requestContext.requestId",
            "$..requestContext.requestTime",
            "$..requestContext.requestTimeEpoch",
            "$..requestContext.identity",
        ]
    )
    def test_authorizer_event_lambda_request(
        self,
        aws_client,
        create_rest_apigw,
        apigateway_lambda_integration_role,
        create_lambda_with_invocation_forwarding,
        get_lambda_invocation_events,
        _create_method_and_integration,
        region_name,
        snapshot,
        cloudfront_transformers,
        aws_proxy_transformers,
    ):
        """
        This test check the format of the payload sent to the authorizer, this does not test authorizer behaviour but
        what we send to the lambda.
        """
        snapshot.add_transformers_list(
            [
                snapshot.transform.key_value("sourceIp"),
                snapshot.transform.key_value("requestTime"),
                snapshot.transform.key_value("requestTimeEpoch", reference_replacement=False),
                snapshot.transform.key_value("resourceId"),
                snapshot.transform.key_value("extendedRequestId"),
                snapshot.transform.key_value("userAgent"),
                snapshot.transform.key_value("authorizerArn"),
                snapshot.transform.key_value("deploymentId"),
                snapshot.transform.regex(apigateway_lambda_integration_role, "<lambda-role>"),
                *cloudfront_transformers,
                *aws_proxy_transformers,
            ]
        )
        rest_api_id, _, root_id = create_rest_apigw(name="aws lambda api")
        snapshot.add_transformer(snapshot.transform.regex(rest_api_id, "<rest-api-id>"))

        lambda_auth_arn = create_lambda_with_invocation_forwarding(self.LAMBDA_AUTH_FORWARD_TO_SQS)
        snapshot.match("authorizer", {"authorizerArn": lambda_auth_arn})

        auth_url = arns.apigateway_invocations_arn(lambda_auth_arn, region_name)

        create_authorizer_response = aws_client.apigateway.create_authorizer(
            restApiId=rest_api_id,
            name="test_authorizer_forward",
            type="REQUEST",
            identitySource="method.request.header.Authorization",
            authorizerUri=auth_url,
            authorizerCredentials=apigateway_lambda_integration_role,
            # disable authorizer caching for testing
            authorizerResultTtlInSeconds=0,
        )
        authorizer_id = create_authorizer_response["id"]
        snapshot.add_transformer(snapshot.transform.regex(authorizer_id, "<authorizer-id>"))
        snapshot.match("create-authorizer-request", create_authorizer_response)

        identity_sources = ["method.request.header.Authorization"]
        # create GET "/" method
        _create_method_and_integration(
            rest_api_id, root_id, authorizer_id=authorizer_id, identity_sources=identity_sources
        )

        # create 3 resources at /test, /{proxy+}, /test/{param} to test the different events received in the
        # authorizer
        resource = aws_client.apigateway.create_resource(
            restApiId=rest_api_id, parentId=root_id, pathPart="test"
        )
        hardcoded_resource_id = resource["id"]
        _create_method_and_integration(
            rest_api_id,
            hardcoded_resource_id,
            authorizer_id=authorizer_id,
            identity_sources=identity_sources,
        )

        resource = aws_client.apigateway.create_resource(
            restApiId=rest_api_id, parentId=root_id, pathPart="{proxy+}"
        )
        proxy_resource_id = resource["id"]
        _create_method_and_integration(
            rest_api_id,
            proxy_resource_id,
            authorizer_id=authorizer_id,
            identity_sources=identity_sources,
        )

        resource = aws_client.apigateway.create_resource(
            restApiId=rest_api_id, parentId=hardcoded_resource_id, pathPart="{param}"
        )
        param_resource_id = resource["id"]
        _create_method_and_integration(
            rest_api_id,
            param_resource_id,
            authorizer_id=authorizer_id,
            identity_sources=identity_sources,
        )

        stage_name = "dev"
        aws_client.apigateway.create_deployment(restApiId=rest_api_id, stageName=stage_name)

        for path in ("/test", "test/paramtest", "/randomproxied/test/proxy"):
            url = api_invoke_url(api_id=rest_api_id, stage=stage_name, path=path)
            result = requests.get(url, verify=False, headers={"Authorization": "test"})
            assert result.status_code == 403
            assert (
                result.json()["Message"]
                == "User is not authorized to access this resource with an explicit deny"
            )

        # retrieve the event received by the authorizer
        # assert the payload of received invocation events
        messages = get_lambda_invocation_events(lambda_auth_arn, count=3)
        for message in messages:
            path = message["event"]["path"]
            snapshot.match(f"auth-request-{path}", message)

    @markers.aws.validated
    @pytest.mark.skipif(
        condition=not is_aws_cloud() and not is_next_gen_api(),
        reason="Rendering is not properly working in Legacy",
    )
    @markers.snapshot.skip_snapshot_verify(
        paths=[
            *CLOUDFRONT_SKIP_HEADERS,
            # TODO: fix provider response
            "$.create-authorizer-request.authType",
        ]
    )
    def test_authorizer_event_lambda_request_from_context(
        self,
        aws_client,
        create_rest_apigw,
        apigateway_lambda_integration_role,
        create_lambda_authorizer,
        _create_method_and_integration,
        region_name,
        snapshot,
        cloudfront_transformers,
        aws_proxy_transformers,
    ):
        """
        This test check the format of the payload sent to the authorizer, this does not test authorizer behaviour but
        what we send to the lambda.
        """
        snapshot.add_transformers_list(
            [
                snapshot.transform.key_value("sourceIp"),
                snapshot.transform.key_value("requestTime", reference_replacement=False),
                snapshot.transform.key_value(
                    "requestTimeEpoch", reference_replacement=False, value_replacement="time-epoch"
                ),
                snapshot.transform.key_value("resourceId"),
                snapshot.transform.key_value("extendedRequestId"),
                snapshot.transform.key_value("userAgent"),
                snapshot.transform.key_value("deploymentId"),
                snapshot.transform.key_value("lambdaName"),
                snapshot.transform.key_value(
                    "X-Forwarded-Proto", reference_replacement=False, value_replacement="proto"
                ),
                snapshot.transform.key_value(
                    "X-Forwarded-Port", reference_replacement=False, value_replacement="port"
                ),
                snapshot.transform.key_value(
                    "integrationLatency",
                    reference_replacement=False,
                    value_replacement="<integration-latency>",
                ),
                snapshot.transform.regex(apigateway_lambda_integration_role, "<lambda-role>"),
                *cloudfront_transformers,
                *aws_proxy_transformers,
            ]
        )
        snapshot.add_transformer(snapshot.transform.key_value("domainName"), priority=-1)
        rest_api_id, _, root_id = create_rest_apigw(name="authorizer payload format")
        snapshot.add_transformer(snapshot.transform.regex(rest_api_id, "<rest-api-id>"))

        lambda_auth_arn = create_lambda_authorizer(self.LAMBDA_AUTH_ATTACH_TO_CONTEXT)
        snapshot.match(
            "authorizer",
            {
                "authorizerArn": lambda_auth_arn,
                "lambdaName": lambda_auth_arn.split(":")[-1],
            },
        )

        auth_url = arns.apigateway_invocations_arn(lambda_auth_arn, region_name)
        identity_sources = ["method.request.header.Authorization"]
        response_templates = {
            APPLICATION_JSON: self.AUTH_RESPONSE_TEMPLATE_SIMPLE,
        }

        create_authorizer_response = aws_client.apigateway.create_authorizer(
            restApiId=rest_api_id,
            name="test_authorizer_forward",
            type="REQUEST",
            identitySource="method.request.header.Authorization",
            authorizerUri=auth_url,
            authorizerCredentials=apigateway_lambda_integration_role,
            # disable authorizer caching for testing
            authorizerResultTtlInSeconds=0,
        )
        authorizer_id = create_authorizer_response["id"]
        snapshot.add_transformer(snapshot.transform.regex(authorizer_id, "<authorizer-id>"))
        snapshot.match("create-authorizer-request", create_authorizer_response)

        # create GET "/" method
        _create_method_and_integration(
            rest_api_id, root_id, authorizer_id=authorizer_id, identity_sources=identity_sources
        )

        # create 3 resources at /test, /{proxy+}, /test/{param} to test the different events received in the
        # authorizer
        resource = aws_client.apigateway.create_resource(
            restApiId=rest_api_id, parentId=root_id, pathPart="test"
        )
        hardcoded_resource_id = resource["id"]
        _create_method_and_integration(
            rest_api_id,
            hardcoded_resource_id,
            authorizer_id=authorizer_id,
            identity_sources=identity_sources,
            response_templates=response_templates,
        )

        resource = aws_client.apigateway.create_resource(
            restApiId=rest_api_id, parentId=root_id, pathPart="{proxy+}"
        )
        proxy_resource_id = resource["id"]
        _create_method_and_integration(
            rest_api_id,
            proxy_resource_id,
            authorizer_id=authorizer_id,
            identity_sources=identity_sources,
            response_templates=response_templates,
        )

        resource = aws_client.apigateway.create_resource(
            restApiId=rest_api_id, parentId=hardcoded_resource_id, pathPart="{param}"
        )
        param_resource_id = resource["id"]
        _create_method_and_integration(
            rest_api_id,
            param_resource_id,
            authorizer_id=authorizer_id,
            identity_sources=identity_sources,
            response_templates=response_templates,
        )

        stage_name = "dev"
        aws_client.apigateway.create_deployment(restApiId=rest_api_id, stageName=stage_name)

        def invoke_path(request_path: str) -> requests.Response:
            endpoint = api_invoke_url(api_id=rest_api_id, stage=stage_name, path=request_path)
            resp = requests.get(endpoint, verify=False, headers={"Authorization": "test"})
            assert resp.status_code == 200, resp.content
            return resp

        # we retry the first path, to know the API is online and available
        response = retry(invoke_path, retries=10, sleep=1, request_path="/test")
        snapshot.match("hardcoded-path", response.json())

        # test the different kind of path
        response = invoke_path(request_path="test/paramtest")
        snapshot.match("param-path", response.json())

        response = invoke_path(request_path="/randomproxied/test/proxy//double")
        snapshot.match("proxy-path", response.json())

    @markers.aws.validated
    @pytest.mark.skipif(
        condition=not is_aws_cloud() and not is_next_gen_api(),
        reason="Behavior is not correct in Legacy",
    )
    @markers.snapshot.skip_snapshot_verify(
        paths=[
            # TODO: fix provider response
            "$.create-authorizer-request-no-cache.authType",
            "$.create-authorizer-request-with-cache.authType",
        ]
    )
    def test_authorizer_lambda_request_identity_source(
        self,
        aws_client,
        create_rest_apigw,
        apigateway_lambda_integration_role,
        create_lambda_authorizer,
        _create_method_and_integration,
        region_name,
        snapshot,
    ):
        """
        For the REQUEST authorizer, this is required when authorization caching is enabled. The value is a
        comma-separated string of one or more mapping expressions of the specified request parameters. For example,
        if an Auth header, a Name query string parameter are defined as identity sources, this value is
        method.request.header.Auth, method.request.querystring.Name. These parameters will be used to derive
        the authorization caching key and to perform runtime validation of the REQUEST authorizer by verifying
        all the identity-related request parameters are present, not null and non-empty. Only when this is
        true does the authorizer invoke the authorizer Lambda function, otherwise, it returns a 401 Unauthorized
        response without calling the Lambda function. The valid value is a string of comma-separated mapping
        expressions of the specified request parameters. When the authorization caching is not enabled,
        this property is optional.
        https://docs.aws.amazon.com/apigateway/latest/api/API_CreateAuthorizer.html#API_CreateAuthorizer_RequestSyntax
        """
        snapshot.add_transformers_list(
            [
                snapshot.transform.regex(apigateway_lambda_integration_role, "<lambda-role>"),
                snapshot.transform.resource_name(),
                snapshot.transform.key_value("id"),
            ]
        )
        rest_api_id, _, root_id = create_rest_apigw(name="authorizer request identity source")

        lambda_auth_arn = create_lambda_authorizer(self.LAMBDA_AUTH_ATTACH_TO_CONTEXT)
        snapshot.match("authorizer", {"authorizerArn": lambda_auth_arn})

        auth_url = arns.apigateway_invocations_arn(lambda_auth_arn, region_name)
        identity_sources = ["method.request.header.TestHeader", "method.request.header.AuthHeader"]
        response_templates = {APPLICATION_JSON: json.dumps({"message": "Authorized"})}
        authorizer_request = {
            "restApiId": rest_api_id,
            "type": "REQUEST",
            "authorizerUri": auth_url,
            "authorizerCredentials": apigateway_lambda_integration_role,
        }

        create_authorizer_response_no_cache = aws_client.apigateway.create_authorizer(
            **authorizer_request,
            # disable authorizer caching for testing, do not set identity source
            name="test_authorizer_no_cache",
            authorizerResultTtlInSeconds=0,
        )
        authorizer_id_no_cache = create_authorizer_response_no_cache["id"]
        snapshot.match("create-authorizer-request-no-cache", create_authorizer_response_no_cache)

        create_authorizer_response_with_cache = aws_client.apigateway.create_authorizer(
            **authorizer_request,
            name="test_authorizer_with_cache",
            # enable the cache to verify identitySource requirement
            authorizerResultTtlInSeconds=10,
            identitySource=", ".join(identity_sources),
        )
        authorizer_id_with_cache = create_authorizer_response_with_cache["id"]
        snapshot.match(
            "create-authorizer-request-with-cache", create_authorizer_response_with_cache
        )

        with pytest.raises(ClientError) as e:
            aws_client.apigateway.create_authorizer(
                **authorizer_request,
                name="test_authorizer_with_cache_no_source",
                # enable the cache to verify identitySource requirement
                authorizerResultTtlInSeconds=10,
                # do not set the identitySource to show it is required when caching is enabled
            )
        snapshot.match("create-auth-with-cache-and-no-identity-source", e.value.response)

        # create 2 resources at /no-cache and /with-cache to test the different behaviors
        no_cache_resource = aws_client.apigateway.create_resource(
            restApiId=rest_api_id, parentId=root_id, pathPart="no-cache"
        )
        no_cache_resource_id = no_cache_resource["id"]
        _create_method_and_integration(
            rest_api_id,
            no_cache_resource_id,
            authorizer_id=authorizer_id_no_cache,
            identity_sources=identity_sources,
            response_templates=response_templates,
        )

        with_cache_resource = aws_client.apigateway.create_resource(
            restApiId=rest_api_id, parentId=root_id, pathPart="with-cache"
        )
        with_cache_resource_id = with_cache_resource["id"]
        _create_method_and_integration(
            rest_api_id,
            with_cache_resource_id,
            authorizer_id=authorizer_id_with_cache,
            identity_sources=identity_sources,
            response_templates=response_templates,
        )

        stage_name = "dev"
        aws_client.apigateway.create_deployment(restApiId=rest_api_id, stageName=stage_name)

        def invoke_path(
            request_path: str, headers: dict, expected_status_code: int
        ) -> requests.Response:
            endpoint = api_invoke_url(api_id=rest_api_id, stage=stage_name, path=request_path)
            resp = requests.get(endpoint, verify=False, headers=headers)
            assert resp.status_code == expected_status_code
            return resp

        # we retry the first path, to know the API is online and available
        identity_source_keys = [key.split(".")[-1] for key in identity_sources]
        headers_with_source = {key: "test-value" for key in identity_source_keys}
        headers_without_source = {"random": "value"}
        headers_partial_source = {identity_source_keys[0]: "value"}
        headers_bad_casing_source = {k.upper(): v for k, v in headers_with_source.items()}

        response = retry(
            invoke_path,
            retries=10,
            sleep=1,
            request_path="/no-cache",
            headers=headers_with_source,
            expected_status_code=200,
        )
        snapshot.match("no-cache-with-identity-source", response.json())

        # test the different kind of path
        response = invoke_path(
            request_path="/no-cache", headers=headers_without_source, expected_status_code=200
        )
        snapshot.match("no-cache-without-identity-source", response.json())

        response = invoke_path(
            request_path="/with-cache", headers=headers_with_source, expected_status_code=200
        )
        snapshot.match("with-cache-with-identity-source", response.json())
        # TODO: it seems APIGW v1 and REST API do not pass the `identitySource` field to the authorizer, unlike v2 even
        #  with the 1.0 format. Maybe add a test that retrieve the whole payload once again for an authorizer with
        #  identitySource required

        response = invoke_path(
            request_path="/with-cache", headers=headers_without_source, expected_status_code=401
        )
        snapshot.match("with-cache-without-identity-source", response.json())

        response = invoke_path(
            request_path="/with-cache", headers=headers_partial_source, expected_status_code=401
        )
        snapshot.match("with-cache-with-partial-identity-source", response.json())

        response = invoke_path(
            request_path="/with-cache", headers=headers_bad_casing_source, expected_status_code=200
        )
        snapshot.match("with-cache-with-bad-casing-identity-source", response.json())

    @markers.aws.validated
    @pytest.mark.skipif(
        condition=not is_aws_cloud() and not is_next_gen_api(),
        reason="Rendering is not properly working in Legacy",
    )
    @markers.snapshot.skip_snapshot_verify(
        paths=[
            *CLOUDFRONT_SKIP_HEADERS,
            # TODO: fix provider response
            "$.create-authorizer-request.authType",
        ]
    )
    def test_authorizer_event_lambda_token_from_context(
        self,
        aws_client,
        create_rest_apigw,
        apigateway_lambda_integration_role,
        create_lambda_authorizer,
        _create_method_and_integration,
        region_name,
        snapshot,
        cloudfront_transformers,
        aws_proxy_transformers,
    ):
        """
        This test check the format of the payload sent to the authorizer, this does not test authorizer behaviour but
        what we send to the lambda.
        """
        snapshot.add_transformers_list(
            [
                snapshot.transform.key_value("sourceIp"),
                snapshot.transform.key_value("userAgent"),
                snapshot.transform.key_value("lambdaName"),
                snapshot.transform.key_value(
                    "integrationLatency",
                    reference_replacement=False,
                    value_replacement="<integration-latency>",
                ),
                snapshot.transform.regex(apigateway_lambda_integration_role, "<lambda-role>"),
            ]
        )
        rest_api_id, _, root_id = create_rest_apigw(name="authorizer token payload format")
        snapshot.add_transformer(snapshot.transform.regex(rest_api_id, "<rest-api-id>"))

        lambda_auth_arn = create_lambda_authorizer(self.LAMBDA_AUTH_ATTACH_TO_CONTEXT)
        snapshot.match(
            "authorizer",
            {
                "authorizerArn": lambda_auth_arn,
                "lambdaName": lambda_auth_arn.split(":")[-1],
            },
        )

        auth_url = arns.apigateway_invocations_arn(lambda_auth_arn, region_name)
        identity_sources = ["method.request.header.TestHeader"]
        response_templates = {
            APPLICATION_JSON: self.AUTH_RESPONSE_TEMPLATE_SIMPLE,
        }

        create_authorizer_response = aws_client.apigateway.create_authorizer(
            restApiId=rest_api_id,
            name="test_authorizer_forward",
            type="TOKEN",
            identitySource="method.request.header.Authorization",
            authorizerUri=auth_url,
            authorizerCredentials=apigateway_lambda_integration_role,
            # disable authorizer caching for testing
            authorizerResultTtlInSeconds=0,
        )
        authorizer_id = create_authorizer_response["id"]
        snapshot.add_transformer(snapshot.transform.regex(authorizer_id, "<authorizer-id>"))
        snapshot.match("create-authorizer-request", create_authorizer_response)

        # create GET "/" method
        _create_method_and_integration(
            rest_api_id, root_id, authorizer_id=authorizer_id, identity_sources=identity_sources
        )

        resource = aws_client.apigateway.create_resource(
            restApiId=rest_api_id, parentId=root_id, pathPart="test"
        )
        resource_id = resource["id"]
        _create_method_and_integration(
            rest_api_id,
            resource_id,
            authorizer_id=authorizer_id,
            identity_sources=identity_sources,
            response_templates=response_templates,
        )

        stage_name = "dev"
        aws_client.apigateway.create_deployment(restApiId=rest_api_id, stageName=stage_name)

        def invoke_path(request_path: str) -> requests.Response:
            endpoint = api_invoke_url(api_id=rest_api_id, stage=stage_name, path=request_path)
            resp = requests.get(
                endpoint, verify=False, headers={"Authorization": "my-complicated-token"}
            )
            assert resp.status_code == 200, resp.content
            return resp

        # we retry the first path, to know the API is online and available
        response = retry(invoke_path, retries=10, sleep=1, request_path="/test")
        snapshot.match("test-invoke-payload", response.json())

    @markers.aws.validated
    @pytest.mark.skipif(
        condition=not is_aws_cloud() and not is_next_gen_api(),
        reason="Behavior is not correct in Legacy",
    )
    @markers.snapshot.skip_snapshot_verify(
        paths=[
            # TODO: fix provider response
            "$.create-authorizer-request.authType",
        ]
    )
    def test_authorizer_lambda_token_identity_source(
        self,
        aws_client,
        create_rest_apigw,
        apigateway_lambda_integration_role,
        create_lambda_authorizer,
        _create_method_and_integration,
        region_name,
        snapshot,
    ):
        """
        For a TOKEN or COGNITO_USER_POOLS authorizer, this is required and specifies the request header mapping
        expression for the custom header holding the authorization token submitted by the client. For example, if the
        token header name is Auth, the header mapping expression is method.request.header.Auth.
        https://docs.aws.amazon.com/apigateway/latest/api/API_CreateAuthorizer.html#API_CreateAuthorizer_RequestSyntax
        """
        snapshot.add_transformers_list(
            [
                snapshot.transform.regex(apigateway_lambda_integration_role, "<lambda-role>"),
                snapshot.transform.resource_name(),
                snapshot.transform.key_value("id"),
            ]
        )
        rest_api_id, _, root_id = create_rest_apigw(name="authorizer token identity source")

        lambda_auth_arn = create_lambda_authorizer(self.LAMBDA_AUTH_ATTACH_TO_CONTEXT)
        snapshot.match("authorizer", {"authorizerArn": lambda_auth_arn})

        auth_url = arns.apigateway_invocations_arn(lambda_auth_arn, region_name)
        identity_sources = ["method.request.header.TestHeader"]
        response_templates = {APPLICATION_JSON: json.dumps({"message": "Authorized"})}
        authorizer_request = {
            "restApiId": rest_api_id,
            "type": "TOKEN",
            "authorizerUri": auth_url,
            "authorizerCredentials": apigateway_lambda_integration_role,
        }

        create_authorizer_response = aws_client.apigateway.create_authorizer(
            **authorizer_request,
            name="test_authorizer",
            identitySource=identity_sources[0],
            authorizerResultTtlInSeconds=0,
        )
        authorizer_id = create_authorizer_response["id"]
        snapshot.match("create-authorizer-request", create_authorizer_response)

        with pytest.raises(ClientError) as e:
            aws_client.apigateway.create_authorizer(
                **authorizer_request,
                name="test_authorizer_no_source",
                # do not set the identitySource to show it is required for TOKEN
            )
        snapshot.match("create-auth-no-identity-source", e.value.response)

        with pytest.raises(ClientError) as e:
            aws_client.apigateway.create_authorizer(
                **authorizer_request,
                name="test_authorizer_wrong_location",
                identitySource="method.request.querystring.TestQS",
            )
        snapshot.match("create-auth-wrong-identity-source-location", e.value.response)

        with pytest.raises(ClientError) as e:
            aws_client.apigateway.create_authorizer(
                **authorizer_request,
                name="test_authorizer_no_source",
                # enable the cache to verify identitySource requirement
                authorizerResultTtlInSeconds=0,
                identitySource="method.request.header.TestHeader, method.request.header.TestHeaderTwo",
            )
        snapshot.match("create-auth-wrong-identity-source-composite", e.value.response)

        resource = aws_client.apigateway.create_resource(
            restApiId=rest_api_id, parentId=root_id, pathPart="test-source"
        )
        resource_id = resource["id"]
        _create_method_and_integration(
            rest_api_id,
            resource_id,
            authorizer_id=authorizer_id,
            identity_sources=identity_sources,
            response_templates=response_templates,
        )

        stage_name = "dev"
        aws_client.apigateway.create_deployment(restApiId=rest_api_id, stageName=stage_name)

        def invoke_path(
            request_path: str, headers: dict, expected_status_code: int
        ) -> requests.Response:
            endpoint = api_invoke_url(api_id=rest_api_id, stage=stage_name, path=request_path)
            resp = requests.get(endpoint, verify=False, headers=headers)
            assert resp.status_code == expected_status_code
            return resp

        # we retry the first path, to know the API is online and available
        identity_source_keys = [key.split(".")[-1] for key in identity_sources]
        headers_with_source = {key: "test-value" for key in identity_source_keys}
        headers_without_source = {"random": "value"}
        headers_bad_casing_source = {k.upper(): v for k, v in headers_with_source.items()}

        response = retry(
            invoke_path,
            retries=10,
            sleep=1,
            request_path="/test-source",
            headers=headers_with_source,
            expected_status_code=200,
        )
        snapshot.match("with-identity-source", response.json())

        # test the different kind of path
        response = invoke_path(
            request_path="/test-source", headers=headers_without_source, expected_status_code=401
        )
        snapshot.match("without-identity-source", response.json())

        response = invoke_path(
            request_path="/test-source", headers=headers_bad_casing_source, expected_status_code=200
        )
        snapshot.match("with-cache-with-bad-casing-identity-source", response.json())

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(paths=COGNITO_SKIP_JWT_CLAIMS)
    @pytest.mark.skipif(
        not is_aws_cloud() and not is_next_gen_api(),
        reason="scope implementation incorrect in legacy",
    )
    def test_authorizer_cognito_scopes(
        self,
        create_rest_apigw,
        snapshot,
        aws_client,
        region_name,
        create_user_pool_client,
        trigger_lambda_pre_token,
        create_mock_integration_with_cognito_authorizer,
    ):
        stage_name = "stage"
        rest_api_id, _, root_id = create_rest_apigw(name="test cognito authorizer")
        snapshot.add_transformers_list(
            [
                snapshot.transform.key_value("cognito_pool_id"),
                snapshot.transform.key_value("auth_time"),
            ],
            priority=-1,
        )
        snapshot.add_transformers_list(
            [
                snapshot.transform.key_value("sub"),
                snapshot.transform.key_value("iat"),
                snapshot.transform.key_value("exp"),
                snapshot.transform.key_value("jti"),
                snapshot.transform.key_value("at_hash"),
            ]
        )

        scopes = ["openid", "email", "http://example.com/scope1"]
        user_pool_result = create_user_pool_client(
            pool_kwargs={
                "UserPoolAddOns": {"AdvancedSecurityMode": "ENFORCED"},
                "LambdaConfig": {
                    "PreTokenGenerationConfig": {
                        "LambdaArn": trigger_lambda_pre_token,
                        "LambdaVersion": "V2_0",
                    }
                },
            },
            client_kwargs={
                "AllowedOAuthScopes": scopes,
                "AllowedOAuthFlows": ["code", "implicit"],
                "SupportedIdentityProviders": ["COGNITO"],
                "CallbackURLs": ["https://example.com"],
                "AllowedOAuthFlowsUserPoolClient": True,
            },
        )
        user_pool = user_pool_result.user_pool
        app_client = user_pool_result.pool_client

        cognito_pool_id = user_pool["Id"]

        # Create a Domain
        domain_name = f"ls-{short_uid()}"
        aws_client.cognito_idp.create_user_pool_domain(
            Domain=domain_name, UserPoolId=cognito_pool_id
        )
        user_pool["Domain"] = domain_name

        app_client_id = app_client["ClientId"]
        user_pool_id = user_pool["Id"]

        snapshot.add_transformer(snapshot.transform.regex(app_client_id, "<client_id>"))
        snapshot.match("cognito_pool_id", user_pool_id)

        authorizer = aws_client.apigateway.create_authorizer(
            restApiId=rest_api_id,
            name="test_cognito_authorizer",
            type="COGNITO_USER_POOLS",
            identitySource="method.request.header.Authorization",
            providerARNs=[user_pool["Arn"]],
            authorizerResultTtlInSeconds=0,
        )

        # Method with no scope
        create_mock_integration_with_cognito_authorizer(
            rest_api_id=rest_api_id,
            authorizer=authorizer["id"],
            path="no-scope",
            parent_id=root_id,
            auth_scope=[],
        )

        # Method with scope1
        create_mock_integration_with_cognito_authorizer(
            rest_api_id=rest_api_id,
            authorizer=authorizer["id"],
            path="scope1",
            parent_id=root_id,
            auth_scope=["http://example.com/scope1"],
        )

        # Method with email scope
        create_mock_integration_with_cognito_authorizer(
            rest_api_id=rest_api_id,
            authorizer=authorizer["id"],
            path="email-scope",
            parent_id=root_id,
            auth_scope=["email"],
        )

        # Method with invalid scope
        create_mock_integration_with_cognito_authorizer(
            rest_api_id=rest_api_id,
            authorizer=authorizer["id"],
            path="invalid-scope",
            parent_id=root_id,
            auth_scope=["http://example.com/scope2"],
        )

        # Method with multiple scopes
        create_mock_integration_with_cognito_authorizer(
            rest_api_id=rest_api_id,
            authorizer=authorizer["id"],
            path="multi-scope",
            parent_id=root_id,
            auth_scope=["http://example.com/scope1", "http://example.com/scope2"],
        )

        aws_client.apigateway.create_deployment(restApiId=rest_api_id, stageName=stage_name)

        # get auth token
        password = "Test123!"
        username = "user@domain.com"

        aws_client.cognito_idp.sign_up(ClientId=app_client_id, Username=username, Password=password)
        aws_client.cognito_idp.admin_confirm_sign_up(UserPoolId=user_pool_id, Username=username)
        id_token, access_token = get_auth_token_via_login_form(
            user_pool,
            app_client,
            username=username,
            password=password,
            region_name=region_name,
            scope="openid email",
        )

        _, access_token_openid = get_auth_token_via_login_form(
            user_pool,
            app_client,
            username=username,
            password=password,
            region_name=region_name,
            scope="openid",
        )

        def invoke_url(path: str):
            return api_invoke_url(rest_api_id, stage=stage_name, path=path)

        def invoke_api(path: str = "no-scope", auth_token: str = None, expected_status: int = None):
            headers = {}
            if auth_token is not None:
                headers["Authorization"] = auth_token

            _response = requests.get(invoke_url(path), headers=headers)

            if expected_status is not None:
                assert _response.status_code == expected_status

            return _response.json()

        # Missing auth Token
        response = retry(lambda: invoke_api(expected_status=401), retries=10, sleep=1)
        snapshot.match("missing-auth-token", response)

        # Access token with bearer prefix
        response = invoke_api(path="scope1", auth_token=f"Bearer {access_token}")
        snapshot.match("access_token-scope1-Bearer", response)

        # Id token with bearer prefix
        response = invoke_api(path="no-scope", auth_token=f"Bearer {id_token}")
        snapshot.match("id_token-no-scope-Bearer", response)

        for token_type, token in (
            ("id_token", id_token),
            ("access_token", access_token),
            ("access_token_openid", access_token_openid),
        ):
            # Without scope defined id token will succeed, Access Tokens will fail
            response = invoke_api(path="no-scope", auth_token=token)
            snapshot.match(f"{token_type}-no-scope", response)

            # If multiple scopes are declared, only one valid scope is sufficient for access token
            response = invoke_api(path="multi-scope", auth_token=token)
            snapshot.match(f"{token_type}-multi-scope", response)

            # With an invalid scope all token will fail
            response = invoke_api(path="invalid-scope", auth_token=token)
            snapshot.match(f"{token_type}-invalid-scope", response)

            # With a scope defined id token will fail, Access will succeed.
            # This is the scope populated by the lambda resource server
            response = invoke_api(path="scope1", auth_token=token)
            snapshot.match(f"{token_type}-scope1-scope", response)

            # Email Scope is always invalid? Both will fail
            response = invoke_api(path="email-scope", auth_token=token)
            snapshot.match(f"{token_type}-email-scope", response)

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(
        # LS cognito is populating event_id and username while AWS doesn't
        paths=[*COGNITO_SKIP_JWT_CLAIMS, "$..event_id", "$..username"]
    )
    def test_authorizer_cognito_client_credentials(
        self,
        create_rest_apigw,
        aws_client,
        region_name,
        create_user_pool_client,
        create_mock_integration_with_cognito_authorizer,
        snapshot,
    ):
        stage_name = "stage"

        rest_api_id, _, root_id = create_rest_apigw(name="test cognito authorizer")

        snapshot.add_transformers_list(
            [
                snapshot.transform.key_value("cognito_pool_id"),
                snapshot.transform.key_value("auth_time"),
            ],
            priority=-1,
        )
        snapshot.add_transformers_list(
            [
                snapshot.transform.key_value("sub"),
                snapshot.transform.key_value("iat"),
                snapshot.transform.key_value("exp"),
                snapshot.transform.key_value("jti"),
            ]
        )

        # create Cognito user pool, user pool client and resource server
        scopes = ["resource-server/scope1"]
        pool_client = create_user_pool_client(
            client_kwargs={
                "AllowedOAuthFlows": ["client_credentials"],
                "AllowedOAuthScopes": scopes,
                "SupportedIdentityProviders": ["COGNITO"],
                "AllowedOAuthFlowsUserPoolClient": True,
                "GenerateSecret": True,
            }
        )
        user_pool = pool_client.user_pool
        app_client = pool_client.pool_client
        app_client_id = app_client["ClientId"]
        user_pool_id = user_pool["Id"]

        snapshot.add_transformer(snapshot.transform.regex(app_client_id, "<client_id>"))
        snapshot.match("cognito_pool_id", user_pool_id)

        pool_domain = f"domain-{short_uid()}"
        aws_client.cognito_idp.create_user_pool_domain(Domain=pool_domain, UserPoolId=user_pool_id)

        # Create authorizer
        authorizer = aws_client.apigateway.create_authorizer(
            restApiId=rest_api_id,
            name="test_cognito_authorizer",
            type="COGNITO_USER_POOLS",
            identitySource="method.request.header.Authorization",
            providerARNs=[user_pool["Arn"]],
            authorizerResultTtlInSeconds=0,
        )

        create_mock_integration_with_cognito_authorizer(
            rest_api_id=rest_api_id,
            authorizer=authorizer["id"],
            path="",
            parent_id=root_id,
            auth_scope=scopes,
        )

        aws_client.apigateway.create_deployment(restApiId=rest_api_id, stageName=stage_name)

        access_token = get_auth_login_via_token_endpoint(
            client_id=app_client_id,
            client_secret=app_client["ClientSecret"],
            domain=pool_domain,
            region_name=region_name,
            scope=scopes[0],
        )

        invoke_url = api_invoke_url(api_id=rest_api_id, stage=stage_name)
        headers = {"Authorization": access_token}

        def _invoke():
            _response = requests.get(invoke_url, headers=headers)
            assert _response.ok
            return _response

        response = retry(_invoke, retries=10, sleep=1)
        snapshot.match("invoke-response", response.json())


class TestHttpApiAuthorizers:
    @markers.aws.validated
    @pytest.mark.parametrize("payload_format", ["1.0", "2.0"])
    @pytest.mark.parametrize("issuer_domain_fail", [True, False])
    def test_lambda_jwt_authorizer(
        self,
        payload_format,
        issuer_domain_fail,
        create_v2_api,
        apigateway_lambda_integration_role,
        create_lambda_function,
        create_user_pool_client,
        aws_client,
        region_name,
        trigger_lambda_pre_token,
    ):
        scopes = ["openid", "email"]
        user_pool_result = create_user_pool_client(
            pool_kwargs={
                "UserPoolAddOns": {"AdvancedSecurityMode": "ENFORCED"},
                "LambdaConfig": {
                    "PreTokenGenerationConfig": {
                        "LambdaArn": trigger_lambda_pre_token,
                        "LambdaVersion": "V2_0",
                    }
                },
            },
            client_kwargs={
                "AllowedOAuthScopes": scopes,
                "AllowedOAuthFlows": ["code", "implicit"],
                "CallbackURLs": ["https://example.com"],
                "ExplicitAuthFlows": ["USER_PASSWORD_AUTH"],
                "SupportedIdentityProviders": ["COGNITO"],
                "AllowedOAuthFlowsUserPoolClient": True,
            },
        )
        cognito_client_id = user_pool_result.pool_client["ClientId"]
        cognito_pool_id = user_pool_result.user_pool["Id"]
        domain_name = f"ls-{short_uid()}"
        aws_client.cognito_idp.create_user_pool_domain(
            Domain=domain_name, UserPoolId=cognito_pool_id
        )
        user_pool_result.user_pool["Domain"] = domain_name

        # create resource server and custom Cognito scopes
        aws_client.cognito_idp.create_resource_server(
            UserPoolId=cognito_pool_id,
            Identifier="http://example.com",
            Name="ressrv1",
            Scopes=[{"ScopeName": "scope1", "ScopeDescription": "test scope 1"}],
        )
        kwargs = remove_attributes(
            dict(user_pool_result.pool_client), ["CreationDate", "LastModifiedDate"]
        )
        custom_scopes = ["http://example.com/scope1"]
        kwargs["AllowedOAuthScopes"] = extended_scopes = scopes + custom_scopes
        aws_client.cognito_idp.update_user_pool_client(**kwargs)

        result = create_v2_api(ProtocolType="HTTP", Name=f"api-{short_uid()}")
        api_id = result["ApiId"]

        # TODO currently the non-working issuer domain is just ignored (as aws does not let one create an
        #  authorizer with it)
        if is_aws_cloud():
            issuer = f"https://cognito-idp.{aws_client.cognito_idp.meta.region_name}.amazonaws.com/{cognito_pool_id}"
        elif issuer_domain_fail:
            issuer = f"http://bogus/{cognito_pool_id}"
        else:
            issuer = get_issuer_url(pool_id=cognito_pool_id)

        authorizer_id = create_http_authorizer(
            aws_client.apigatewayv2,
            Name="jwt-authorizer",
            ApiId=api_id,
            AuthorizerType="JWT",
            JwtConfiguration={
                "Audience": [cognito_client_id],
                "Issuer": issuer,
            },
            IdentitySource=["$request.header.Authorization"],
        )

        # creates a lambda integration
        lambda_name = f"int-{short_uid()}"
        lambda_arn = create_lambda_function(
            handler_file=LAMBDA_ECHO_EVENT, func_name=lambda_name, runtime=Runtime.nodejs20_x
        )["CreateFunctionResponse"]["FunctionArn"]

        integration_id = create_http_integration(
            aws_client.apigatewayv2,
            ApiId=api_id,
            IntegrationType="AWS_PROXY",
            PayloadFormatVersion=payload_format,
            IntegrationMethod="ANY",
            IntegrationUri=lambda_arn,
            CredentialsArn=apigateway_lambda_integration_role,
        )

        # create a test route, with authorization scopes
        create_http_route(
            aws_client.apigatewayv2,
            ApiId=api_id,
            AuthorizationType="JWT",
            AuthorizerId=authorizer_id,
            AuthorizationScopes=["http://example.com/scope1"],
            RouteKey="POST /test/{proxy+}",
            Target=f"integrations/{integration_id}",
        )
        # create a second route, with a non-assumed authorization scopes (requests should be denied)
        create_http_route(
            aws_client.apigatewayv2,
            ApiId=api_id,
            AuthorizationType="JWT",
            AuthorizerId=authorizer_id,
            AuthorizationScopes=["http://example.com/scope2"],
            RouteKey="POST /test-denied/{proxy+}",
            Target=f"integrations/{integration_id}",
        )
        # create a third route, without authorization scopes
        create_http_route(
            aws_client.apigatewayv2,
            ApiId=api_id,
            AuthorizationType="JWT",
            AuthorizerId=authorizer_id,
            RouteKey="POST /test-noscopes/{proxy+}",
            Target=f"integrations/{integration_id}",
        )

        create_http_route(
            aws_client.apigatewayv2,
            ApiId=api_id,
            AuthorizationType="JWT",
            AuthorizerId=authorizer_id,
            RouteKey="POST /test-notoken/{proxy+}",
            Target=f"integrations/{integration_id}",
        )

        # create deployment
        stage_name = "test-stage"
        create_deployment(aws_client.apigatewayv2, api_id, stage_name=stage_name)

        # assert responses
        endpoint = api_invoke_url(api_id=api_id, stage=stage_name, path="/test/foobar")
        result = requests.post(endpoint, headers={"Authorization": ""}, verify=False)
        assert result.status_code == 401
        assert to_str(result.content) == '{"message":"Unauthorized"}'

        tokens = []

        # get auth token
        password = "Test123!"
        username = "user@domain.com"
        cognito_sign_up(
            aws_client.cognito_idp,
            ClientId=cognito_client_id,
            Username=username,
            Password=password,
        )
        cognito_confirm_admin_sign_up(
            aws_client.cognito_idp, UserPoolId=cognito_pool_id, Username=username
        )
        id_token, access_token = get_auth_token_via_login_form(
            user_pool_result.user_pool,
            user_pool_result.pool_client,
            username=username,
            password=password,
            region_name=region_name,
            scope="openid email http://example.com/scope1",
        )
        tokens.append(("id", id_token))
        tokens.append(("access", access_token))

        # run requests and assertions
        for path in ["/test/", "/test-denied/", "/test-noscopes/", "/test-notoken/"]:
            endpoint = api_invoke_url(api_id=api_id, stage=stage_name, path=f"{path}test")
            for token_type, token in tokens:
                if path == "/test/" and token_type == "id":
                    # skip auth endpoint that requires scopes, as they are not available in id
                    # tokens
                    continue

                if path == "/test-notoken/":
                    result = requests.post(endpoint, verify=False)
                else:
                    result = requests.post(endpoint, headers={"Authorization": token}, verify=False)

                if issuer_domain_fail and not is_aws_cloud():
                    assert result.status_code == 401
                elif path == "/test-denied/":
                    assert result.status_code == 403
                    assert json.loads(to_str(result.content)) == {"message": "Forbidden"}
                elif path == "/test-notoken/":
                    assert result.status_code == 401
                else:
                    assert result.status_code == 200
                    _scopes = (
                        extended_scopes if token_type == "access" and path == "/test/" else None
                    )
                    if payload_format == "1.0":
                        assert_lambda_authorizer_event_payload_v1(
                            result, scopes=_scopes, token_type=token_type
                        )
                    else:
                        assert_lambda_authorizer_event_payload_v2(
                            result, scopes=_scopes, token_type=token_type
                        )
