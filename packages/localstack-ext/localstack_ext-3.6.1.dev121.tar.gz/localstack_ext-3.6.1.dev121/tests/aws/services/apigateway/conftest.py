import base64
import json
import logging
import os
import textwrap
import time
from typing import Callable

import pytest
import requests
from localstack import config, constants
from localstack.aws.api.lambda_ import Runtime
from localstack.http import Request, Response
from localstack.pro.core import config as ext_config
from localstack.pro.core.services.cognito_idp.cognito_utils import get_endpoint_base_url
from localstack.services.apigateway.context import ApiGatewayVersion
from localstack.services.apigateway.helpers import path_based_url
from localstack.testing.aws.util import is_aws_cloud
from localstack.testing.config import TEST_AWS_REGION_NAME
from localstack.utils import testutil
from localstack.utils.aws import arns, resources
from localstack.utils.strings import short_uid, to_str
from localstack.utils.sync import retry

LOG = logging.getLogger(__name__)

S3_BUCKET_WS_CONNS = f"ws-connections-{short_uid()}"
LAMBDA_WEBSOCKET = """
import os, boto3, json

def mgmt_client(event):
    return boto3.client("apigatewaymanagementapi",
        endpoint_url = "https://" + event["requestContext"]["domainName"] +
        "/" + event["requestContext"]["stage"])

def handler(event, *args):
    print(event)
    if "body" in event:
        body = json.loads(event['body'])
        if body.get('id') == 0:
            conn_id = event["requestContext"]["connectionId"]
            # store connection ID to S3 for later lookup
            s3_client = boto3.client("s3")
            try:
                s3_client.put_object(Bucket="S3_BUCKET_WS_CONNS", Key=f"conn.{conn_id}", Body=b"")
            except Exception:
                pass
        # send additional message via API GW management client
        result = mgmt_client(event).post_to_connection(ConnectionId=conn_id, Data=b'{"action":"_lambda_"}')
    return {
        "statusCode": 200,
        "body": json.dumps(event)
    }
""".replace("S3_BUCKET_WS_CONNS", S3_BUCKET_WS_CONNS)

LAMBDA_WEBSOCKET_ERROR = """
def handler(event, *args):
    raise Exception("Simulated exception - this is intended")
"""

LAMBDA_REQUEST_AUTH = """
import json
authorizer_response_format = '%s'
def handler(event, context, *args):
    print(json.dumps(event))
    req_ctx = event.get('requestContext')
    if not event.get('type'):
        return {
            'body': json.dumps({
                'result': 'protected content',
                'auth_context': req_ctx.get('authorizer'),
                'auth_identity': req_ctx.get('identity'),
                'req_context': req_ctx
            }),
            'statusCode': 200
        }
    # assert event structure
    assert event.get('type') == 'REQUEST'
    assert req_ctx.get('apiId')
    assert event.get('headers')
    assert event.get('requestContext')
    context = {'context': {'ctx.foo': 'bar'}}
    headers = event.get('headers')
    specified_user = headers.get('X-User') or headers.get('x-user')
    is_authorized = specified_user != 'invalid-user'

    if authorizer_response_format == '2.0':
        print(req_ctx)
        http = req_ctx.get("http")
        assert http["method"] is not None
        assert isinstance(event.get('rawQueryString'), str)
        result = {'isAuthorized': is_authorized, **context}
        return result

    statement = {'Action': 'execute-api:Invoke', 'Effect': 'Deny', 'Resource': f'{event["methodArn"]}*'}
    policy = {'policyDocument': {'Version': '2012-10-17', 'Statement': [statement]}}
    if is_authorized:
        statement['Effect'] = 'Allow'
    result = {'principalId': 'principal123', **context, **policy}
    print(json.dumps(result))
    return result
"""

LAMBDA_JS = """
exports.handler = async function(event, context) {
  console.info('EVENT ' + JSON.stringify(event, null, 2));
  return {
    statusCode: 200,
    body: 'I am a %s API!',
  };
}
"""

LAMBDA_ECHO_EVENT = """
exports.handler = async function(event, content) {
  console.info('Received event: ' + JSON.stringify(event, null, 2));
  return {
    statusCode: 200,
    body: JSON.stringify(event)
  };
}
"""

LAMBDA_ECHO = """
exports.handler = async function(event, context) {
  console.info('EVENT ' + JSON.stringify(event, null, 2));
  return {
    statusCode: 200,
    body: event.body,
    headers: {
      "Set-Cookie": "cookie2=vaquarkhan"
    },
    isBase64Encoded: %s,
  };
}
"""

LAMBDA_HELLO = """
exports.handler = async function(event, context) {
   console.log(event)
   let content_type = event["headers"]["content-type"];
   console.log(content_type)
   if (content_type == "application/json") {
     return { "message": "Hello from Lambda!" };
   }
   return "Hello from Lambda!";
};
"""

# Authorizer input event:
# https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-lambda-authorizer-input.html
LAMBDA_TOKEN_AUTH = """
exports.handler = function(event, context, callback) {
    console.log('methodArn: ' + event.methodArn);
    var token = event.authorizationToken;
    switch (token) {
        case 'allow':
            callback(null, generatePolicy('user', 'Allow', event.methodArn));
            break;
        case 'deny':
            callback(null, generatePolicy('user', 'Deny', event.methodArn));
            break;
        case 'unauthorized':
            callback("Unauthorized");   // Return a 401 Unauthorized response
            break;
        default:
            callback("Error: Invalid token"); // Return a 500 Invalid token response
    }
};

// Help function to generate an IAM policy
var generatePolicy = function(principalId, effect, resource) {
    var authResponse = {};

    authResponse.principalId = principalId;
    if (effect && resource) {
        var policyDocument = {};
        policyDocument.Version = '2012-10-17';
        policyDocument.Statement = [];
        var statementOne = {};
        statementOne.Action = 'execute-api:Invoke';
        statementOne.Effect = effect;
        statementOne.Resource = resource;
        policyDocument.Statement[0] = statementOne;
        authResponse.policyDocument = policyDocument;
    }

    // Optional output with custom properties of the String, Number or Boolean type.
    authResponse.context = {
        "stringKey": "stringval",
        "numberKey": 123,
        "booleanKey": true,
        "methodArn": resource
    };
    return authResponse;
}
"""

LAMBDA_REQUEST_WS_AUTH = os.path.join(
    os.path.dirname(__file__), "../../files/lambda_request_ws_auth.js"
)

LAMBDA_ROUTES_WS = os.path.join(os.path.dirname(__file__), "../../files/lambda_routes_ws.py")

LAMBDA_MGMT_WS = os.path.join(os.path.dirname(__file__), "../../files/lambda_mgmt_ws.py")

LAMBDA_INT_RESPONSES = os.path.join(
    os.path.dirname(__file__), "../../files/lambda_int_responses.py"
)

#
# assume policies
#

APIGW_ASSUME_ROLE_POLICY = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {"Service": "apigateway.amazonaws.com"},
            "Action": "sts:AssumeRole",
        }
    ],
}

LAMBDA_ASSUME_ROLE_POLICY = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Action": "sts:AssumeRole",
            "Principal": {"Service": "lambda.amazonaws.com"},
            "Effect": "Allow",
        }
    ],
}

UrlParser = Callable[[str], str]


@pytest.fixture
def url_parser(url_secure) -> UrlParser:
    def parse_url(url):
        if url_secure:
            return url.replace("ws:", "wss:")
        return url

    return parse_url


@pytest.fixture
def trigger_lambda_pre_token(create_lambda_with_invocation_forwarding):
    lambda_source = textwrap.dedent(
        """
    def handler(event, *args):
        trigger, response, request = event['triggerSource'], event['response'], event['request']
        response["claimsAndScopeOverrideDetails"] = {
            "accessTokenGeneration": {
                "scopesToAdd": ["http://example.com/scope1"],
            },
        }
        return event
       """
    )
    return create_lambda_with_invocation_forwarding(lambda_source=lambda_source)


@pytest.fixture
def create_websocket_api(handler_error, create_lambda_function, aws_client):
    def _create(int_type="AWS_PROXY", int_uri=None):
        resources.get_or_create_bucket(S3_BUCKET_WS_CONNS, s3_client=aws_client.s3)
        func_name = f"lst_test_websocket_{short_uid()}"

        if not int_uri:
            # create handler Lambda
            handler_script = LAMBDA_WEBSOCKET_ERROR if handler_error else LAMBDA_WEBSOCKET
            zip_file = testutil.create_lambda_archive(handler_script, get_content=True)
            int_uri = create_lambda_function(func_name=func_name, zip_file=zip_file)[
                "CreateFunctionResponse"
            ]["FunctionArn"]

        # create WebSocket API
        api_name = f"ws-{short_uid()}"
        response = aws_client.apigatewayv2.create_api(
            Name=api_name, ProtocolType="WEBSOCKET", RouteSelectionExpression="$request.body.action"
        )
        api_id = response["ApiId"]
        url = response["ApiEndpoint"]

        # create integration
        template = """{
            "connId": "$context.connectionId",
            "body": $input.body,
            "payload": $input.json('$.message'),
            "queryParams": $input.params(),
            "userAgent": "$context.identity.userAgent"
        }"""
        response = aws_client.apigatewayv2.create_integration(
            ApiId=api_id,
            IntegrationType=int_type,
            IntegrationMethod="POST",
            IntegrationUri=int_uri,
            RequestTemplates={constants.APPLICATION_JSON: template},
            PayloadFormatVersion="1.0",
        )
        int_id = response["IntegrationId"]

        # create routes
        aws_client.apigatewayv2.create_route(
            ApiId=api_id, RouteKey="$connect", Target=f"integrations/{int_id}"
        )

        route_id = aws_client.apigatewayv2.create_route(
            ApiId=api_id, RouteKey="$default", Target=f"integrations/{int_id}"
        )["RouteId"]

        # check if route was created
        response = aws_client.apigatewayv2.get_route(ApiId=api_id, RouteId=route_id)
        assert response["RouteId"] == route_id

        state["api_id"] = api_id
        return func_name, api_id, url, int_id

    state = {}
    yield _create

    aws_client.apigatewayv2.delete_api(ApiId=state["api_id"])


@pytest.fixture
def create_v2_api(aws_client):
    apis = []

    def _create(**kwargs):
        if not kwargs.get("Name"):
            kwargs["Name"] = f"api-{short_uid()}"
        response = aws_client.apigatewayv2.create_api(**kwargs)
        apis.append(response)
        return response

    yield _create

    for api in apis:
        try:
            aws_client.apigatewayv2.delete_api(ApiId=api["ApiId"])
        except Exception as e:
            LOG.debug("Unable to delete API Gateway v2 API %s: %s", api, e)


@pytest.fixture
def import_apigw_v2(aws_client):
    apis = []

    def _import(spec, base_path="ignore"):
        response = aws_client.apigatewayv2.import_api(
            Body=spec, Basepath=base_path, FailOnWarnings=False
        )
        apis.append(response)
        return response

    yield _import

    for api in apis:
        try:
            aws_client.apigatewayv2.delete_api(ApiId=api["ApiId"])
        except Exception as e:
            LOG.debug("Unable to delete API Gateway v2 API %s: %s", api, e)


@pytest.fixture
def tmp_http_server(httpserver):
    invocations = []

    def _handler(_request: Request) -> Response:
        invocations.append(_request)
        return Response(status=200)

    httpserver.expect_request("").respond_with_handler(_handler)
    yield httpserver.port, invocations


@pytest.fixture
def apigateway_lambda_integration_role(create_role, create_policy, aws_client):
    role_name = f"apigw-lambda-integration-{short_uid()}"
    assume_role_doc = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Action": "sts:AssumeRole",
                "Principal": {"Service": "apigateway.amazonaws.com"},
                "Effect": "Allow",
            }
        ],
    }
    policy_doc = {
        "Version": "2012-10-17",
        "Statement": [{"Effect": "Allow", "Action": "lambda:InvokeFunction", "Resource": "*"}],
    }
    role_arn = create_role(
        RoleName=role_name, AssumeRolePolicyDocument=json.dumps(assume_role_doc)
    )["Role"]["Arn"]
    policy_arn = create_policy(
        PolicyName=f"test-policy-{short_uid()}", PolicyDocument=json.dumps(policy_doc)
    )["Policy"]["Arn"]
    aws_client.iam.attach_role_policy(RoleName=role_name, PolicyArn=policy_arn)
    return role_arn


@pytest.fixture
def create_iam_role_and_attach_policy(create_role, aws_client):
    """
    Creates an IAM role and attaches a policy to it. The role is deleted after the test.
    NOTE: use and abuse of this fixture and use existing AWS policies like,
    'arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess' or
    'arn:aws:iam::aws:policy/AmazonKinesisFullAccess' instead of creating a new policy.
    """

    def _create(policy_arn: str, assume_role_policy: dict = APIGW_ASSUME_ROLE_POLICY):
        role_name = f"role-{short_uid()}"
        # Create the IAM role
        response = create_role(
            RoleName=role_name, AssumeRolePolicyDocument=json.dumps(assume_role_policy)
        )

        # Get the newly created role ARN
        role_arn = response["Role"]["Arn"]

        # Attach the policy to the role
        aws_client.iam.attach_role_policy(PolicyArn=policy_arn, RoleName=role_name)
        return role_arn

    yield _create


# ---------------
# UTIL FUNCTIONS
# ---------------


def invoke_api_using_authorizer(
    apigateway_client,
    lambda_client,
    create_lambda_function,
    create_authorizer_func,
    valid_headers,
    invalid_headers,
    version: ApiGatewayVersion = ApiGatewayVersion.V1,
    iam_user_name: str = None,
):
    # TODO split this util into several tests, it currently does too much and will not work against AWS
    # create API gateway
    gateway_name = f"gw-{short_uid()}"
    lambda_name = f"auth-{short_uid()}"
    stage_name = "test"
    path = "/test"

    # create v1 REST API
    if version == ApiGatewayVersion.V1:
        function_arn = create_lambda_function(
            func_name=lambda_name, handler_file=LAMBDA_REQUEST_AUTH, client=lambda_client
        )["CreateFunctionResponse"]["FunctionArn"]
        target_arn = arns.apigateway_invocations_arn(function_arn, TEST_AWS_REGION_NAME)

        api_obj = testutil.connect_api_gateway_to_http_with_lambda_proxy(
            gateway_name,
            target_arn,
            stage_name=stage_name,
            path=path,
            methods=[],
            auth_type="REQUEST",
        )
        api_id = api_obj.get("id")
        # find target resource ID
        matching = (
            item["id"]
            for item in apigateway_client.get_resources(restApiId=api_id)["items"]
            if item["path"] == path
        )
        resource_id = next(matching, None)

    # create v2 HTTP API
    else:
        api_obj = apigateway_client.create_api(Name=gateway_name, ProtocolType="HTTP")
        api_id = api_obj.get("ApiId")
        function_arn = create_lambda_function(
            func_name=lambda_name, handler_file=LAMBDA_REQUEST_AUTH, client=lambda_client
        )["CreateFunctionResponse"]["FunctionArn"]
        target_arn = arns.apigateway_invocations_arn(function_arn, TEST_AWS_REGION_NAME)
        result = apigateway_client.create_integration(
            ApiId=api_id,
            IntegrationType="AWS_PROXY",
            IntegrationUri=target_arn,
            IntegrationMethod="POST",
            PayloadFormatVersion="2.0",
        )
        int_id = result["IntegrationId"]
        route_id = apigateway_client.create_route(
            ApiId=api_id, RouteKey="GET /{proxy+}", Target=f"integrations/{int_id}"
        )["RouteId"]

    # create API authorizer
    authorizer = create_authorizer_func(api_obj)
    authorizer_type = authorizer.get("type") or authorizer.get("AuthorizerType")
    assert authorizer_type

    # attach authorizer to API method/route
    if version == ApiGatewayVersion.V1:
        auth_type = (
            authorizer_type if authorizer_type in ("AWS_IAM", "COGNITO_USER_POOLS") else "CUSTOM"
        )
        apigateway_client.update_method(
            restApiId=api_id,
            resourceId=resource_id,
            httpMethod="GET",
            patchOperations=[
                {
                    "op": "replace",
                    "path": "/authorizationType",
                    "value": auth_type,
                },
                {"op": "replace", "path": "/authorizerId", "value": authorizer["id"]},
            ],
        )
        apigateway_client.create_deployment(restApiId=api_id, stageName=stage_name)
    elif version == ApiGatewayVersion.V2:
        apigateway_client.update_route(
            ApiId=api_id,
            AuthorizerId=authorizer["AuthorizerId"],
            AuthorizationType="CUSTOM",
            RouteId=route_id,
        )

    # invoke API GW endpoint
    endpoint = path_based_url(api_id, stage_name, path)
    result = requests.get(endpoint, headers=valid_headers, verify=False)
    assert result.ok
    result = json.loads(to_str(result.content))
    assert "protected content" in result.get("result")
    if authorizer_type == "REQUEST":
        auth_context = result.get("auth_context") or {}
        # TODO: the check below seems to be breaking with the latest version
        # if result.get("req_context", {}).get("version") == "2.0":
        if auth_context.get("lambda"):
            auth_context = auth_context.get("lambda")
        assert auth_context.get("ctx.foo") == "bar"
        assert auth_context.get("principalId") in [None, "principal123"]

    elif authorizer_type == "AWS_IAM":
        assert f"user/{iam_user_name}" in result["auth_identity"]["userArn"]

    # invoke API GW with invalid credentials
    result = requests.get(endpoint, headers=invalid_headers, verify=False)
    if authorizer_type == "AWS_IAM" and not ext_config.ENFORCE_IAM:
        # TODO: update this, now it depends on the implementation
        content = json.loads(result.content)
        if not is_next_gen_api():
            # by default (and if ENFORCE_IAM is disabled), IAM returns the single dummy root user
            assert ":root" in content["auth_identity"]["userArn"]
        else:
            assert result.status_code == 403
            assert "not a valid key=value pair" in content["message"]
    if authorizer_type == "REQUEST":
        assert 403 == result.status_code
        content = to_str(result.content)
        if version == ApiGatewayVersion.V1:
            assert (
                '{"Message":"User is not authorized to access this resource with an explicit '
                'deny"}' == content
            )
        else:
            assert '{"message":"Forbidden"}' == content
    if authorizer_type == "COGNITO_USER_POOLS":
        assert '{"message": "Unauthorized"}' in to_str(result.content)
        assert 401 == result.status_code

    # clean up
    if version == ApiGatewayVersion.V1:
        apigateway_client.delete_rest_api(restApiId=api_id)
    elif version == ApiGatewayVersion.V2:
        apigateway_client.delete_api(ApiId=api_id)


@pytest.fixture
def authorizer_lambda_arn(create_lambda_function, region_name):
    """Create a Lambda authorizer and return its API Gateway invocation ARN"""
    auth_lambda_name = f"auth-{short_uid()}"
    response = create_lambda_function(
        handler_file=LAMBDA_REQUEST_WS_AUTH,
        func_name=auth_lambda_name,
        runtime=Runtime.nodejs20_x,
    )
    lambda_arn = response["CreateFunctionResponse"]["FunctionArn"]
    return arns.apigateway_invocations_arn(lambda_arn, region_name)


@pytest.fixture
def add_permission_for_integration_lambda(aws_client):
    def _add_permission(api_id, lambda_arn):
        aws_account_id = aws_client.sts.get_caller_identity()["Account"]

        source_arn = "arn:aws:execute-api:{}:{}:{}/*/*".format(
            aws_client.apigatewayv2._client_config.region_name, aws_account_id, api_id
        )

        aws_client.lambda_.add_permission(
            FunctionName=lambda_arn,
            StatementId=str(short_uid()),
            Action="lambda:InvokeFunction",
            Principal="apigateway.amazonaws.com",
            SourceArn=source_arn,
        )

    yield _add_permission


def get_auth_login_via_token_endpoint(
    client_id: str, client_secret: str, domain: str, region_name: str, scope: str
) -> str:
    # base64 encode basic auth
    basic_auth = base64.b64encode(f"{client_id}:{client_secret}".encode("utf-8")).decode("utf-8")

    issuer_domain = f"{get_endpoint_base_url()}/_aws/cognito-idp/oauth2/token"
    if is_aws_cloud():
        issuer_domain = f"https://{domain}.auth.{region_name}.amazoncognito.com/oauth2/token"
        # sleep some time for DNS name to propagate
        time.sleep(10)

    def _issue_access_token():
        resp = requests.post(
            issuer_domain,
            headers={
                "Authorization": f"Basic {basic_auth}",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            data=f"grant_type=client_credentials&scope={scope}",
            verify=False,
        )
        # assert we got a valid access token
        assert resp.status_code == 200
        return resp.json()["access_token"]

    return retry(_issue_access_token, retries=10)


def is_next_gen_api():
    return config.APIGW_NEXT_GEN_PROVIDER and not is_aws_cloud()
