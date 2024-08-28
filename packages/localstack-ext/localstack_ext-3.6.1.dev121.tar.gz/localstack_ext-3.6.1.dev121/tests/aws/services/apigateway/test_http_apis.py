import base64
import gzip
import json
import os
from typing import List
from urllib.parse import parse_qs, urlencode

import pytest
import requests
import urllib3
from botocore.exceptions import ClientError
from localstack import config, constants
from localstack.aws.api.lambda_ import Runtime
from localstack.http.request import get_full_raw_path
from localstack.pro.core.services.apigateway.apigateway_utils import get_execute_api_endpoint
from localstack.pro.core.services.apigateway.router_asf import SHARED_ROUTER
from localstack.pro.core.services.cognito_idp.cognito_utils import (
    get_auth_token_via_login_form,
)
from localstack.services.apigateway.context import ApiGatewayVersion
from localstack.services.apigateway.helpers import host_based_url, path_based_url
from localstack.testing.aws.util import is_aws_cloud
from localstack.testing.config import SECONDARY_TEST_AWS_REGION_NAME, TEST_AWS_REGION_NAME
from localstack.testing.pytest import markers
from localstack.utils import testutil
from localstack.utils.aws import arns
from localstack.utils.aws.arns import get_partition
from localstack.utils.collections import remove_attributes
from localstack.utils.docker_utils import DOCKER_CLIENT
from localstack.utils.files import load_file
from localstack.utils.strings import short_uid, to_str
from localstack.utils.sync import retry
from localstack.utils.threads import start_worker_thread
from pytest_httpserver import HTTPServer
from requests import Response
from werkzeug import Request
from werkzeug import Response as WerkzeugResponse

from tests.aws.services.apigateway.apigateway_fixtures import (
    UrlType,
    api_invoke_url,
    cognito_confirm_admin_sign_up,
    cognito_sign_up,
    create_api_mapping,
    create_http_authorizer,
    create_http_deployment,
    create_http_domain_name,
    create_http_integration,
    create_http_route,
    create_http_stage,
    delete_api_mapping,
    get_http_integrations,
)
from tests.aws.services.apigateway.conftest import (
    LAMBDA_ECHO,
    LAMBDA_ECHO_EVENT,
    LAMBDA_HELLO,
    LAMBDA_JS,
    LAMBDA_REQUEST_AUTH,
    invoke_api_using_authorizer,
)

API_SPEC_FILE = os.path.join(os.path.dirname(__file__), "../../templates", "openapi.spec.json")
THIS_FOLDER = os.path.dirname(os.path.realpath(__file__))
TEST_LAMBDA_AUTHORIZER_SIMPLE_RESPONSE = os.path.join(
    THIS_FOLDER, "../../files/py_authorizer_simple_response.py"
)

TEST_LAMBDA_AUTHORIZER_IAM_RESPONSE = os.path.join(
    THIS_FOLDER, "../../files/lambda_authorizer_echo.py"
)

LAMBDA_BASE64_RESPONSE = """
def handler(event, context):
    return {
        'statusCode': %s,
        'headers': {
            'Content-Type': 'image/png'
        },
        'body': event["body"],
        'isBase64Encoded': event["isBase64Encoded"]
    }
"""

LAMBDA_GZIP_RESPONSE = """
import gzip, json, base64
def handler(event, *args):
  headers = event["headers"]
  body = event["body"]
  is_gzipped = headers.get("accept-encoding") == "gzip"
  if is_gzipped:
    body = base64.b64encode(gzip.compress(body.encode("UTF-8"))).decode("UTF-8")
  return {
    "statusCode": 200,
    "body": body,
    "isBase64Encoded": is_gzipped,
    "headers": {"Content-Encoding": "gzip"} if is_gzipped else {}
  }
"""

STEP_FUNCTION_DEFINITION = """
{
  "Comment": "A Hello World example of the Amazon States Language using an AWS Lambda Function",
  "StartAt": "HelloWorld",
  "States": {
    "HelloWorld": {
      "Type": "Task",
      "Resource": "%s",
      "End": true
    }
  }
}
"""


def assert_lambda_authorizer_event_payload_v1(
    result: Response, scopes: List[str] = None, token_type: str = None
):
    body = json.loads(result.text)
    request_context = body.get("requestContext")
    authorizer_obj = request_context.get("authorizer")
    assert "claims" in authorizer_obj
    if token_type:
        assert authorizer_obj["claims"]["token_use"] == token_type
    assert "scopes" in authorizer_obj
    if scopes:
        assert any(scope in authorizer_obj["scopes"] for scope in scopes)
    else:
        assert authorizer_obj["scopes"] == scopes


def assert_lambda_authorizer_event_payload_v2(
    result: Response, scopes: List[str] = None, token_type: str = None
):
    body = json.loads(result.text)
    request_context = body.get("requestContext")
    authorizer_obj = request_context.get("authorizer")
    jwt_claims = authorizer_obj.get("jwt")
    assert "claims" in jwt_claims
    if token_type:
        assert jwt_claims["claims"]["token_use"] == token_type
    assert "scopes" in jwt_claims
    if scopes:
        assert any(scope in jwt_claims["scopes"] for scope in scopes)
    else:
        assert jwt_claims["scopes"] == scopes


def create_deployment(apigatewayv2_client, api_id, stage_name=None):
    stage_name = stage_name or "test-stage"
    deployment_id = apigatewayv2_client.create_deployment(ApiId=api_id)["DeploymentId"]
    apigatewayv2_client.create_stage(ApiId=api_id, StageName=stage_name, DeploymentId=deployment_id)

    def _deployment_ready():
        result = apigatewayv2_client.get_deployment(ApiId=api_id, DeploymentId=deployment_id)
        assert result["DeploymentStatus"] == "DEPLOYED"

    retry(_deployment_ready, sleep=1, retries=10)
    return deployment_id


class TestHttpApis:
    """Tests for API GW v2 HTTP APIs."""

    @markers.snapshot.skip_snapshot_verify(
        paths=[
            "$..args",
            "$..files",
            "$..form",
            "$..json",
            "$..origin",
            "$..method",
            "$..headers.X-Amzn-Trace-Id",
            "$..headers.X-Localstack-Edge",
            "$..headers.X-Localstack-Tgt-Api",
            "$..headers.Connection",
        ]
    )
    @markers.aws.validated
    def test_http_proxy_integration(
        self, aws_client, create_v2_api, echo_http_server_post, snapshot
    ):
        snapshot.add_transformer(snapshot.transform.key_value("origin"))
        snapshot.add_transformer(
            snapshot.transform.key_value("Forwarded", "forwarded", reference_replacement=False)
        )
        snapshot.add_transformer(
            snapshot.transform.jsonpath("$..headers.X-Amzn-Trace-Id", "trace-id")
        )
        snapshot.add_transformer(snapshot.transform.jsonpath("$..headers.Host", "host"))
        snapshot.add_transformer(
            snapshot.transform.jsonpath(
                "$..headers.User-Agent", "<user-agent>", reference_replacement=False
            )
        )

        result = create_v2_api(ProtocolType="HTTP", Name=f"{short_uid()}")
        api_id = result["ApiId"]

        uri = echo_http_server_post
        with pytest.raises(ClientError) as e:
            create_http_integration(
                aws_client.apigatewayv2,
                ApiId=api_id,
                IntegrationType="HTTP_PROXY",
                IntegrationMethod="ANY",
                IntegrationUri=uri,
            )
        snapshot.match("invalid-integration-req", e.value.response)

        integration_id = create_http_integration(
            aws_client.apigatewayv2,
            ApiId=api_id,
            IntegrationType="HTTP_PROXY",
            PayloadFormatVersion="1.0",
            IntegrationMethod="ANY",
            IntegrationUri=uri,
        )

        # creates the /{proxy+} route
        create_http_route(
            aws_client.apigatewayv2,
            ApiId=api_id,
            RouteKey="ANY /api/{proxy+}",
            Target=f"integrations/{integration_id}",
            AuthorizationType="NONE",
        )

        # create the /api route
        create_http_route(
            aws_client.apigatewayv2,
            ApiId=api_id,
            RouteKey="ANY /api",
            Target=f"integrations/{integration_id}",
            AuthorizationType="NONE",
        )

        stage_name = "dev"
        create_http_stage(
            aws_client.apigatewayv2,
            ApiId=api_id,
            StageName=stage_name,
            AutoDeploy=True,
        )

        # assert responses
        for path in ["/api", "/api/anything"]:

            def invoke():
                _endpoint = api_invoke_url(api_id=api_id, stage=stage_name, path=path)
                _response = requests.post(
                    _endpoint,
                    json=json.dumps({"foo": "bar"}),
                    headers={"X-Test": "test"},
                    params={"queryStringParam": "test"},
                    verify=False,
                )
                assert _response.status_code == 200
                snapshot.match(f"invoke-{path}", _response.json())

            retry(invoke, sleep=1, retries=10)

        for query_string_param, snapshot_name in (
            ("a=b&redirect_uri=http://localhost:3001/example-client/success", "qs-non-encoded"),
            (
                {"a": "b", "redirect_uri": "http://localhost:3001/example-client/success"},
                "qs-encoded",
            ),
        ):
            # assert that a request with a Query String containing a URL works
            endpoint = api_invoke_url(api_id=api_id, stage=stage_name, path="/api/test-qs")
            response = requests.post(
                endpoint,
                json=json.dumps({"foo": "bar"}),
                # this is hacky, but `requests` percent-encode requests per the standard. But AWS allows query string
                # parameters to not be URL encoded. Passing directly a string bypasses that
                params=query_string_param,
                verify=False,
            )
            assert response.status_code == 200
            response = response.json()
            if not is_aws_cloud():
                # the fixture does not return the `url` field url-encoded, we should fix it
                # TODO: there's a weird case when API Gateway proxies a non-encoded request, it does not URL-encode
                #  the ':' character. For now this is handled here, but should be looked into.
                url_no_qs, _, qs = response["url"].partition("?")
                qs_params = {k: v[0] for k, v in parse_qs(qs).items()}
                if snapshot_name == "qs-non-encoded":
                    encoded_params = urlencode(qs_params, safe=":")
                else:
                    encoded_params = urlencode(qs_params)

                response["url"] = f"{url_no_qs}?{encoded_params}"

            snapshot.match(f"invoke-{snapshot_name}-with-url", response)

    @markers.aws.validated
    def test_http_integration_invalid_use_cases(
        self, aws_client, create_v2_api, echo_http_server_post, snapshot
    ):
        """
        This is just a bunch of negative tests to our HTTP integration.
        """
        result = create_v2_api(ProtocolType="HTTP", Name=f"{short_uid()}")
        api_id = result["ApiId"]
        uri = echo_http_server_post

        with pytest.raises(ClientError) as e:
            aws_client.apigatewayv2.create_integration(
                ApiId=api_id,
                IntegrationType="HTTP",  # HTTP v2 only supports HTTP_PROXY or AWS_PROXY
                PayloadFormatVersion="1.0",
                IntegrationMethod="ANY",
                IntegrationUri=uri,
            )
        snapshot.match("invalid-integration-type", e.value.response["Error"])

        with pytest.raises(ClientError) as e:
            aws_client.apigatewayv2.create_integration(
                ApiId=api_id,
                IntegrationType="HTTP_PROXY",
                PayloadFormatVersion="2.0",  # HTTP v2 only supports 1.0
                IntegrationMethod="ANY",
                IntegrationUri=uri,
            )
        snapshot.match("invalid-payload-format-version", e.value.response["Error"])

    @markers.aws.validated
    def test_http_to_lambda_payload_v2(
        self,
        create_v2_api,
        create_lambda_function,
        add_permission_for_integration_lambda,
        aws_client,
    ):
        result = create_v2_api(ProtocolType="HTTP", Name=f"{short_uid()}")
        api_id = result["ApiId"]

        zip_file = testutil.create_lambda_archive(
            LAMBDA_HELLO, get_content=True, runtime=Runtime.nodejs20_x
        )
        lambda_name = f"{short_uid()}"
        create_lambda_function(func_name=lambda_name, zip_file=zip_file, runtime=Runtime.nodejs20_x)
        lambda_arn = aws_client.lambda_.get_function(FunctionName=lambda_name)["Configuration"][
            "FunctionArn"
        ]
        add_permission_for_integration_lambda(api_id, lambda_arn)

        integration_id = create_http_integration(
            aws_client.apigatewayv2,
            ApiId=api_id,
            IntegrationType="AWS_PROXY",
            PayloadFormatVersion="2.0",
            IntegrationMethod="ANY",
            IntegrationUri=lambda_arn,
        )
        create_http_route(
            aws_client.apigatewayv2,
            ApiId=api_id,
            AuthorizationType="NONE",
            RouteKey="POST /example",
            Target=f"integrations/{integration_id}",
        )
        create_http_route(
            aws_client.apigatewayv2,
            ApiId=api_id,
            AuthorizationType="NONE",
            RouteKey="POST /example/test",
            Target=f"integrations/{integration_id}",
        )
        create_http_route(
            aws_client.apigatewayv2,
            ApiId=api_id,
            AuthorizationType="NONE",
            RouteKey="POST /example/test/{id}",
            Target=f"integrations/{integration_id}",
        )

        create_http_stage(
            aws_client.apigatewayv2, ApiId=api_id, StageName="$default", AutoDeploy=True
        )

        def json_request():
            endpoint = api_invoke_url(api_id=api_id, path="/example/test")
            response = requests.post(
                endpoint, headers={"Content-Type": "application/json"}, verify=False
            )
            assert response.status_code == 200
            assert response.content == b'{"message":"Hello from Lambda!"}'

        retry(json_request, retries=5, sleep=1)

        def text_request(**kwargs):
            for path in kwargs.get("path"):
                if path == "/123":
                    endpoint = api_invoke_url(api_id=api_id, path=path)
                    response = requests.post(endpoint, verify=False)
                    assert response.status_code == 404
                else:
                    endpoint = api_invoke_url(api_id=api_id, path=path)
                    response = requests.post(
                        endpoint, headers={"Content-Type": "text/plain"}, verify=False
                    )
                    assert response.status_code == 200
                    assert response.content == b"Hello from Lambda!"

        retry(
            text_request,
            retries=5,
            sleep=1,
            path=["/example/test", "/example/test/123", "/example", "/123"],
        )

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(
        paths=[
            "$..Connection",
            "$..Content-Type",
            "$..X-Amzn-Trace-Id",
            "$..X-Localstack-Edge",
            "$..X-Localstack-Tgt-Api",
        ]
    )
    def test_import_and_invoke_http_api(
        self, aws_client, echo_http_server_post, import_apigw_v2, snapshot
    ):
        snapshot.add_transformer(
            snapshot.transform.key_value("Forwarded", "forwarded", reference_replacement=False)
        )
        snapshot.add_transformer(snapshot.transform.key_value("Host", "host"))
        snapshot.add_transformer(
            snapshot.transform.key_value("User-Agent", "<user-agent>", reference_replacement=False)
        )
        snapshot.add_transformer(snapshot.transform.key_value("Header1", "request-id"))
        api_spec = load_file(API_SPEC_FILE)

        result = import_apigw_v2(api_spec)
        api_id = result["ApiId"]
        # TODO: add tests for additional integrations like Lambda, etc
        params = {
            "append:header.header1": "$context.requestId",
            "append:header.header2": "test",
        }
        result = aws_client.apigatewayv2.create_integration(
            ApiId=api_id,
            IntegrationType="HTTP_PROXY",
            IntegrationUri=echo_http_server_post,
            RequestParameters=params,
            PayloadFormatVersion="1.0",
            IntegrationMethod="POST",
        )
        int_id = result["IntegrationId"]

        http_integrations = get_http_integrations(aws_client.apigatewayv2, ApiId=api_id)
        assert len(http_integrations) == 4
        assert (
            len(list(filter(lambda x: (x["IntegrationType"] == "HTTP_PROXY"), http_integrations)))
            == 3
        )

        result = aws_client.apigatewayv2.get_routes(ApiId=api_id)["Items"]
        for route in result:
            aws_client.apigatewayv2.update_route(
                ApiId=api_id, RouteId=route["RouteId"], Target=f"integrations/{int_id}"
            )

        create_http_stage(
            aws_client.apigatewayv2, ApiId=api_id, StageName="$default", AutoDeploy=True
        )

        def invoke_api():
            endpoint = api_invoke_url(api_id=api_id, stage="$default", path="/pets")
            result = requests.get(endpoint)
            assert result.ok
            response = json.loads(to_str(result.content))
            return response.get("headers")

        headers = retry(invoke_api, retries=10, sleep=1)
        snapshot.match("http-proxy-request-header-parameters", headers)

    @markers.aws.unknown
    def test_v2_dynamic_proxy_paths(self, create_v2_api, tmp_http_server, aws_client):
        test_port, invocations = tmp_http_server

        # create API
        api_name = f"api-{short_uid()}"
        result = create_v2_api(Name=api_name, ProtocolType="HTTP")
        api_id = result["ApiId"]

        # create integration
        result = aws_client.apigatewayv2.create_integration(
            ApiId=api_id,
            IntegrationType="HTTP_PROXY",
            IntegrationUri="http://localhost:%s/{proxy}" % test_port,
            PayloadFormatVersion="1.0",
            IntegrationMethod="ANY",
        )
        int_id = result["IntegrationId"]

        # create routes
        aws_client.apigatewayv2.create_route(
            ApiId=api_id, RouteKey="GET /{proxy+}", Target=f"integrations/{int_id}"
        )
        aws_client.apigatewayv2.create_route(
            ApiId=api_id, RouteKey="POST /my/param/{proxy}/1", Target=f"integrations/{int_id}"
        )

        # create custom stage (in addition to $default stage)
        stage_name = "stage1"
        aws_client.apigatewayv2.create_stage(ApiId=api_id, StageName=stage_name)

        # invoke with path using custom stage
        url = host_based_url(api_id, path="/my/test/1?p1", stage_name=stage_name)
        assert stage_name in url
        result = requests.get(url)
        assert result.status_code == 200
        # invoke with alternative path, using default stage
        url = host_based_url(api_id, path="/my/test/2?p2=2")
        result = requests.get(url)
        assert result.status_code == 200
        # invoke with alternative path, using single "{proxy}" path param
        url = host_based_url(api_id, path="/my/param/test6427/1?p3=3")
        result = requests.post(url)
        assert result.status_code == 200
        # invoke with a non-matching path, should return 404/error response
        url = host_based_url(api_id, path="/foobar")
        result = requests.post(url)
        assert result.status_code == 404

        # assert that invocations with correct paths have been received
        paths = [get_full_raw_path(inv) for inv in invocations]
        assert paths == ["/my/test/1?p1=", "/my/test/2?p2=2", "/test6427?p3=3"]

    @markers.aws.unknown
    def test_v2_status_code_mappings(self, create_v2_api, httpserver: HTTPServer, aws_client):
        def _handler(_request: Request) -> WerkzeugResponse:
            response_data = _request.get_data(as_text=True)
            if "large" in _request.path:
                response_data = response_data + "test123 test456 test789" * 100000
            response_content = {
                "method": _request.method,
                "path": _request.path,
                "data": response_data,
                "headers": dict(_request.headers),
            }
            status_code = int(_request.path.split("/")[-1])
            return WerkzeugResponse(
                json.dumps(response_content), mimetype="application/json", status=status_code
            )

        httpserver.expect_request("").respond_with_handler(_handler)
        uri = httpserver.url_for("/{proxy}")

        # create API
        api_name = f"api-{short_uid()}"
        result = create_v2_api(Name=api_name, ProtocolType="HTTP")
        api_id = result["ApiId"]

        # create integration
        result = aws_client.apigatewayv2.create_integration(
            ApiId=api_id,
            IntegrationType="HTTP_PROXY",
            IntegrationUri=uri,
            ResponseParameters={"201": {"overwrite:statuscode": "202"}},
            PayloadFormatVersion="1.0",
            IntegrationMethod="ANY",
        )
        int_id = result["IntegrationId"]

        # create routes
        aws_client.apigatewayv2.create_route(
            ApiId=api_id, RouteKey="GET /{proxy+}", Target=f"integrations/{int_id}"
        )

        # invoke with different expected status codes
        for code in [200, 201, 400, 403]:
            for payload in ["normal", "large"]:
                url = host_based_url(api_id, path=f"/test/{payload}/{code}")
                result = requests.get(url)
                expected = code + 1 if code % 100 == 1 else code
                assert result.status_code == expected

    @markers.aws.unknown
    def test_lambda_return_gzip_response(self, create_lambda_function, aws_client):
        # create Lambda
        lambda_name = f"auth-{short_uid()}"
        zip_file = testutil.create_lambda_archive(LAMBDA_GZIP_RESPONSE, get_content=True)
        lambda_arn = create_lambda_function(func_name=lambda_name, zip_file=zip_file)[
            "CreateFunctionResponse"
        ]["FunctionArn"]

        # create API
        api_name = f"api-{short_uid()}"
        api_id = aws_client.apigatewayv2.create_api(
            Name=api_name, ProtocolType="HTTP", Target=lambda_arn
        )["ApiId"]

        # invoke API
        api_endpoint = get_execute_api_endpoint(api_id, protocol="http://")
        url = f"{api_endpoint}/test/resource1"
        data = {"content": "test 123"}
        response = requests.post(url, data=json.dumps(data), headers={})
        assert response.status_code < 400
        assert data == json.loads(to_str(response.content))
        data["gzip"] = True
        response = requests.post(
            url, data=json.dumps(data), headers={"Accept-Encoding": "gzip"}, stream=True
        )
        assert response.status_code < 400
        content = response.raw.read()
        content = gzip.decompress(content)
        assert data == json.loads(to_str(content))

        # clean up
        aws_client.lambda_.delete_function(FunctionName=lambda_name)

    @pytest.mark.parametrize("payload_format_version", ["1.0", "2.0"])
    @markers.aws.unknown
    def test_lambda_request_authorizer(
        self, payload_format_version, create_lambda_function, aws_client, region_name
    ):
        def create_authorizer_v1_func(api_obj):
            return create_authorizer_func(api_obj, payload_format_version)

        def create_authorizer_v2_func(api_obj):
            return create_authorizer_func(api_obj, payload_format_version)

        def create_authorizer_func(api_obj, response_format_version):
            # create Lambda
            lambda_name = f"auth-{short_uid()}"
            lambda_code = LAMBDA_REQUEST_AUTH % response_format_version
            zip_file = testutil.create_lambda_archive(lambda_code, get_content=True)
            lambda_arn = create_lambda_function(func_name=lambda_name, zip_file=zip_file)[
                "CreateFunctionResponse"
            ]["FunctionArn"]
            # create API GW authorizer
            auth_name = f"auth-{short_uid()}"
            auth_url = arns.apigateway_invocations_arn(lambda_arn, region_name)
            return aws_client.apigatewayv2.create_authorizer(
                ApiId=api_obj["ApiId"],
                Name=auth_name,
                AuthorizerType="REQUEST",
                IdentitySource=["method.request.header.x-user"],
                AuthorizerUri=auth_url,
                AuthorizerPayloadFormatVersion=payload_format_version,
                EnableSimpleResponses=True,
            )

        valid_headers = {"X-User": "valid-user"}
        invalid_headers = {"X-User": "invalid-user"}
        # invoke API GW v2 API using authorizer response format 1.0
        invoke_api_using_authorizer(
            aws_client.apigatewayv2,
            aws_client.lambda_,
            create_lambda_function,
            create_authorizer_v1_func,
            valid_headers,
            invalid_headers,
            version=ApiGatewayVersion.V2,
        )

        # invoke API GW v2 API using authorizer response format 2.0
        invoke_api_using_authorizer(
            aws_client.apigatewayv2,
            aws_client.lambda_,
            create_lambda_function,
            create_authorizer_v2_func,
            valid_headers,
            invalid_headers,
            version=ApiGatewayVersion.V2,
        )

    @markers.aws.validated
    @pytest.mark.parametrize("method", ["POST", "ANY"])
    @pytest.mark.parametrize("payload_format", ["1.0", "2.0"])
    @pytest.mark.parametrize("url_type", [UrlType.HOST_BASED, UrlType.PATH_BASED])
    @pytest.mark.parametrize(
        "lambda_region",
        [SECONDARY_TEST_AWS_REGION_NAME, TEST_AWS_REGION_NAME],
        ids=["secondary-region", "primary-region"],
    )
    def test_http_lambda_authorizers(
        self,
        create_v2_api,
        method,
        payload_format,
        url_type,
        lambda_region,
        create_lambda_function,
        apigateway_lambda_integration_role,
        aws_client_factory,
        aws_client,
    ):
        lambda_client = aws_client_factory(region_name=lambda_region).lambda_
        # creates HTTP API
        result = create_v2_api(ProtocolType="HTTP", Name=f"{short_uid()}")
        api_id = result["ApiId"]

        # creates a lambda authorizer
        lambda_authorizer_name = f"auth-{short_uid()}"
        stage_name = "test-stage"
        # XXX Fix the lambda authorizer by using a different strategy to validate the inputs,
        # is quite confusing.
        lambda_code = LAMBDA_REQUEST_AUTH % payload_format
        zip_file = testutil.create_lambda_archive(lambda_code, get_content=True)
        auth_lambda_arn = create_lambda_function(
            func_name=lambda_authorizer_name, zip_file=zip_file, client=lambda_client
        )["CreateFunctionResponse"]["FunctionArn"]
        auth_url = arns.apigateway_invocations_arn(
            auth_lambda_arn, region_name=aws_client.apigatewayv2.meta.region_name
        )

        authorizer_id = create_http_authorizer(
            aws_client.apigatewayv2,
            Name="lambda-authorizer",
            ApiId=api_id,
            AuthorizerUri=auth_url,
            AuthorizerType="REQUEST",
            IdentitySource=[
                "$request.header.X-User"
            ],  # TODO LS should check if this header is present and return 401 if not
            AuthorizerPayloadFormatVersion=payload_format,
            AuthorizerCredentialsArn=apigateway_lambda_integration_role,
            EnableSimpleResponses=payload_format == "2.0",
        )

        # creates a lambda integration
        lambda_integration_name = f"int-{short_uid()}"
        lambda_arn = create_lambda_function(
            handler_file=LAMBDA_JS % "nice",
            func_name=lambda_integration_name,
            runtime=Runtime.nodejs20_x,
            client=lambda_client,
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

        # creates the /example/{proxy+} route for multiple routes
        create_http_route(
            aws_client.apigatewayv2,
            ApiId=api_id,
            AuthorizationType="CUSTOM",
            AuthorizerId=authorizer_id,
            RouteKey=f"{method} /example/{{proxy+}}",
            Target=f"integrations/{integration_id}",
        )
        deployment_id = aws_client.apigatewayv2.create_deployment(ApiId=api_id)["DeploymentId"]
        aws_client.apigatewayv2.create_stage(
            ApiId=api_id, StageName=stage_name, DeploymentId=deployment_id
        )

        # assert responses
        endpoint = api_invoke_url(
            api_id=api_id, stage=stage_name, path="/example/test", url_type=url_type
        )

        # tests for POST requests only the use of invalid user
        methods = ["POST"] if method == "POST" else ["POST", "GET", "PUT"]
        for method in methods:

            def _test_request():
                result = requests.request(
                    method, endpoint, headers={"X-User": "invalid-user"}, verify=False
                )
                assert result.status_code == 403
                assert to_str(result.content) == '{"message":"Forbidden"}'

            retry(_test_request, sleep=2, retries=10)
        # tests for valid authorization
        for method in methods:
            result = requests.request(
                method, endpoint, headers={"X-User": "authorized-user"}, verify=False
            )
            assert result.status_code == 200
            assert to_str(result.content) == "I am a nice API!"

    @markers.aws.unknown
    def test_lambda_authorizer_with_no_payload_format_version(
        self,
        create_v2_api,
        create_lambda_function,
        aws_client,
        region_name,
    ):
        # creates HTTP API
        result = create_v2_api(ProtocolType="HTTP", Name=f"{short_uid()}")
        api_id = result["ApiId"]

        # creates the lambda authorizer
        lambda_name = f"auth-{short_uid()}"
        lambda_code = LAMBDA_REQUEST_AUTH % "2.0"
        zip_file = testutil.create_lambda_archive(lambda_code, get_content=True)
        lambda_arn = create_lambda_function(func_name=lambda_name, zip_file=zip_file)[
            "CreateFunctionResponse"
        ]["FunctionArn"]
        auth_url = arns.apigateway_invocations_arn(lambda_arn, region_name)

        authorizer_id = create_http_authorizer(
            aws_client.apigatewayv2,
            Name="lambda-authorizer",
            ApiId=api_id,
            AuthorizerUri=auth_url,
            AuthorizerType="REQUEST",
            IdentitySource=["$request.header.x-user"],
            EnableSimpleResponses=True,
        )

        # creates the lambda integration
        lambda_name = f"int-{short_uid()}"
        lambda_arn = create_lambda_function(
            handler_file=LAMBDA_JS % "nice", func_name=lambda_name, runtime=Runtime.nodejs20_x
        )["CreateFunctionResponse"]["FunctionArn"]

        integration_id = create_http_integration(
            aws_client.apigatewayv2,
            ApiId=api_id,
            IntegrationType="AWS_PROXY",
            PayloadFormatVersion="2.0",
            IntegrationMethod="ANY",
            IntegrationUri=lambda_arn,
        )

        # creates the /example/{proxy+} route
        create_http_route(
            aws_client.apigatewayv2,
            ApiId=api_id,
            AuthorizationType="CUSTOM",
            AuthorizerId=authorizer_id,
            RouteKey="POST /example/{proxy+}",
            Target=f"integrations/{integration_id}",
        )

        # assert responses
        endpoint = api_invoke_url(api_id=api_id, stage="$default", path="/example/test")

        result = requests.post(endpoint, headers={"X-User": "invalid-user"}, verify=False)
        assert result.status_code == 403

        # tests for valid authorization
        result = requests.request("POST", endpoint, headers={"X-User": "user"}, verify=False)
        assert result.status_code == 200
        assert to_str(result.content) == "I am a nice API!"

        # tests for missing headers
        result = requests.request("POST", endpoint, headers={}, verify=False)
        assert result.status_code == 401
        assert to_str(result.content) == '{"message": "Unauthorized"}'

    @pytest.mark.parametrize("payload_format", ["1.0", "2.0"])
    @markers.aws.unknown
    def test_lambda_authorizer_with_aws_proxy_integration(
        self,
        create_v2_api,
        create_lambda_function,
        payload_format,
        aws_client,
        region_name,
    ):
        # creates HTTP API
        result = create_v2_api(ProtocolType="HTTP", Name=f"{short_uid()}")
        api_id = result["ApiId"]

        # creates a lambda authorizer
        lambda_name = f"int-{short_uid()}"
        lambda_arn = create_lambda_function(
            handler_file=TEST_LAMBDA_AUTHORIZER_SIMPLE_RESPONSE,
            func_name=lambda_name,
            runtime=Runtime.python3_12,
        )["CreateFunctionResponse"]["FunctionArn"]
        auth_url = arns.apigateway_invocations_arn(lambda_arn, region_name)
        authorizer_id = create_http_authorizer(
            aws_client.apigatewayv2,
            Name="lambda-authorizer",
            ApiId=api_id,
            AuthorizerUri=auth_url,
            AuthorizerType="REQUEST",
            IdentitySource=["$request.header.x-user"],
            AuthorizerPayloadFormatVersion=payload_format,
            EnableSimpleResponses=payload_format == "2.0",
        )

        lambda_name = f"int-{short_uid()}"
        lambda_arn = create_lambda_function(
            handler_file=LAMBDA_ECHO_EVENT,
            func_name=lambda_name,
            runtime=Runtime.nodejs20_x,
        )["CreateFunctionResponse"]["FunctionArn"]

        integration_id = create_http_integration(
            aws_client.apigatewayv2,
            ApiId=api_id,
            IntegrationType="AWS_PROXY",
            PayloadFormatVersion=payload_format,
            IntegrationMethod="ANY",
            IntegrationUri=lambda_arn,
            RequestParameters={
                "overwrite:header.x-syna-accountalias": "$context.authorizer.accountAlias",
                "overwrite:header.x-syna-accountid": "$context.authorizer.accountId",
                "overwrite:header.x-syna-permissions": "$context.authorizer.permissions",
                "overwrite:header.x-syna-projectid": "$context.authorizer.projectId",
                "overwrite:header.x-syna-tenantid": "$context.authorizer.tenantId",
                "overwrite:header.x-syna-userid": "$context.authorizer.userId",
            },
        )

        # creates the /example/{proxy+} route for multiple routes
        create_http_route(
            aws_client.apigatewayv2,
            ApiId=api_id,
            AuthorizationType="CUSTOM",
            AuthorizerId=authorizer_id,
            RouteKey="POST /example/{proxy+}",
            Target=f"integrations/{integration_id}",
        )

        endpoint = api_invoke_url(api_id=api_id, stage="$default", path="/example/test")
        result = requests.post(endpoint, headers={"x-user": "user"}, verify=False)
        if payload_format == "1.0":
            # payload format 1.0 does not support simple responses
            assert result.status_code == 403
        else:
            headers = result.json().get("headers", {})
            assert headers.get("x-syna-accountalias") == "account-alias"
            assert headers.get("x-syna-accountid") == "account-id"
            assert headers.get("x-syna-permissions") == "test-permissions"
            assert headers.get("x-syna-projectid") == "project-id"
            assert headers.get("x-syna-tenantid") == "tenant-id"

    @pytest.mark.parametrize("response_status_code", ["200", "404"])
    @markers.aws.unknown
    def test_lambda_handling_binary_data(
        self, response_status_code, create_lambda_function, aws_client
    ):
        # create Lambda
        lambda_name = f"auth-{short_uid()}"
        zip_file = testutil.create_lambda_archive(
            LAMBDA_BASE64_RESPONSE % response_status_code, get_content=True
        )
        lambda_arn = create_lambda_function(func_name=lambda_name, zip_file=zip_file)[
            "CreateFunctionResponse"
        ]["FunctionArn"]

        # create API
        api_name = f"api-{short_uid()}"
        api_id = aws_client.apigatewayv2.create_api(
            Name=api_name, ProtocolType="HTTP", Target=lambda_arn
        )["ApiId"]

        image_file = os.path.join(os.path.dirname(__file__), "nyan-cat.jpg")
        url = "%s/test/resource1" % get_execute_api_endpoint(api_id, protocol="http://")
        response = requests.post(url, data=open(image_file, "rb"), headers={})

        assert response.status_code == int(response_status_code)
        assert open(image_file, "rb").read() == response.content

        aws_client.lambda_.delete_function(FunctionName=lambda_name)

    @pytest.mark.parametrize("payload_format", ["1.0", "2.0"])
    @pytest.mark.parametrize(
        "domain_name",
        [
            "<random>.example.com",
            f"<random>.{constants.LOCALHOST}",
            f"<random>.{constants.LOCALHOST_HOSTNAME}",
        ],
    )
    @pytest.mark.parametrize("mapping_key", ["", "base1"])
    @pytest.mark.parametrize("stage", ["", "stage1"])
    @markers.aws.unknown
    def test_custom_domains(
        self,
        create_v2_api,
        create_lambda_function,
        payload_format,
        domain_name,
        mapping_key,
        stage,
        aws_client,
    ):
        domain_name = domain_name.replace("<random>", short_uid())
        cert_resp = aws_client.acm.request_certificate(
            DomainName=domain_name, ValidationMethod="DNS", IdempotencyToken=short_uid()
        )

        result = create_v2_api(ProtocolType="HTTP", Name=f"{short_uid()}")
        api_id = result["ApiId"]

        create_http_domain_name(
            aws_client.apigatewayv2,
            DomainName=domain_name,
            DomainNameConfigurations=[
                {
                    "CertificateArn": cert_resp["CertificateArn"],
                    "EndpointType": "REGIONAL",
                    "SecurityPolicy": "TLS_1_2",
                }
            ],
        )

        # let check if domain is preserved between APIs (v1, v2)
        domain_resp = aws_client.apigatewayv2.get_domain_name(DomainName=domain_name)
        assert domain_resp["DomainName"] == domain_name
        assert (
            domain_resp["DomainNameConfigurations"][0]["CertificateArn"]
            == cert_resp["CertificateArn"]
        )

        # v1 API
        domain_resp = aws_client.apigateway.get_domain_name(domainName=domain_name)
        assert domain_resp["domainName"] == domain_name
        assert domain_resp["regionalCertificateArn"] == cert_resp["CertificateArn"]

        lambda_name = f"auth-{short_uid()}"
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
        )
        create_http_route(
            aws_client.apigatewayv2,
            ApiId=api_id,
            AuthorizationType="NONE",
            RouteKey="POST /example/test",
            Target=f"integrations/{integration_id}",
        )
        if stage:
            create_http_stage(
                aws_client.apigatewayv2, ApiId=api_id, StageName=stage, AutoDeploy=True
            )

        kwargs = {"ApiMappingKey": mapping_key} if mapping_key else {}
        mapping_id = create_api_mapping(
            aws_client.apigatewayv2,
            ApiId=api_id,
            DomainName=domain_name,
            Stage=stage or "$default",
            **kwargs,
        )

        stage_prefix = stage and f"/{stage}"
        endpoint = api_invoke_url(api_id=api_id, path=f"{mapping_key}{stage_prefix}/example/test")
        # we want to add a port for a specific domain to test an edge case where the request
        # includes the port in the host header
        host_header = domain_name
        if domain_name == f"baz.{constants.LOCALHOST}":
            host_header = f"{domain_name}:{config.GATEWAY_LISTEN[0].port}"
        # using explicit header host
        result = requests.request("POST", endpoint, headers={"Host": host_header}, verify=False)
        # check result
        assert result.status_code == 200
        request_context = json.loads(result.content).get("requestContext", {})
        assert request_context.get("domainName") == domain_name
        assert request_context.get("domainPrefix") == domain_name.split(".")[0]

        # check invalid endpoint
        endpoint = api_invoke_url(api_id=api_id, path="/invalid-mapping-key/example/test")
        result = requests.request("POST", endpoint, headers={"Host": host_header}, verify=False)
        assert result.status_code == 404

        # test that deleting the api mapping also deletes internal router mapping
        delete_api_mapping(aws_client.apigatewayv2, ApiMappingId=mapping_id, DomainName=domain_name)
        assert not SHARED_ROUTER.custom_domain_rules.get(domain_name)

    @markers.aws.validated
    @pytest.mark.parametrize("payload_format", ["1.0", "2.0"])
    def test_lambda_events(
        self,
        create_v2_api,
        create_lambda_function,
        add_permission_for_integration_lambda,
        payload_format,
        snapshot,
        aws_client,
        region_name,
    ):
        result = create_v2_api(ProtocolType="HTTP", Name=f"{short_uid()}")
        api_id = result["ApiId"]

        lambda_name = f"auth-{short_uid()}"
        lambda_code = LAMBDA_REQUEST_AUTH % payload_format
        zip_file = testutil.create_lambda_archive(lambda_code, get_content=True)
        result = create_lambda_function(func_name=lambda_name, zip_file=zip_file)
        lambda_arn = result["CreateFunctionResponse"]["FunctionArn"]
        auth_url = arns.apigateway_invocations_arn(lambda_arn, region_name)
        add_permission_for_integration_lambda(api_id, lambda_arn)

        kwargs = {} if payload_format == "1.0" else {"EnableSimpleResponses": True}
        authorizer_id = create_http_authorizer(
            aws_client.apigatewayv2,
            ApiId=api_id,
            AuthorizerType="REQUEST",
            AuthorizerUri=auth_url,
            AuthorizerPayloadFormatVersion=payload_format,
            Name=f"lambda-auth-{short_uid()}",
            IdentitySource=["$request.header.X-User"],
            **kwargs,
        )

        lambda_name = f"int-{short_uid()}"
        result = create_lambda_function(
            handler_file=LAMBDA_ECHO_EVENT, func_name=lambda_name, runtime=Runtime.nodejs20_x
        )
        lambda_arn = result["CreateFunctionResponse"]["FunctionArn"]
        add_permission_for_integration_lambda(api_id, lambda_arn)

        path = "/example/test"
        integration_id = create_http_integration(
            aws_client.apigatewayv2,
            ApiId=api_id,
            IntegrationType="AWS_PROXY",
            PayloadFormatVersion=payload_format,
            IntegrationMethod="ANY",
            IntegrationUri=lambda_arn,
        )
        create_http_route(
            aws_client.apigatewayv2,
            ApiId=api_id,
            AuthorizationType="CUSTOM",
            AuthorizerId=authorizer_id,
            RouteKey=f"POST {path}",
            Target=f"integrations/{integration_id}",
        )

        # create deployment
        stage_name = "test-stage"
        create_deployment(aws_client.apigatewayv2, api_id, stage_name=stage_name)

        endpoint = api_invoke_url(api_id=api_id, stage=stage_name, path=path)

        # using explicit header host
        result = requests.post(endpoint, headers={"X-User": "user"}, verify=False)
        request_context = json.loads(result.content).get("requestContext", {})

        assert result.status_code == 200
        auth_req_context = request_context.get("authorizer")
        snapshot.match("auth-request-ctx", auth_req_context)

    @pytest.mark.parametrize("encode_response", [False, True])
    @markers.aws.unknown
    def test_lambda_handling_form_urlencoded_data(
        self, create_v2_api, encode_response, create_lambda_function, aws_client
    ):
        # create Lambda
        lambda_name = f"auth-{short_uid()}"
        lambda_fn = LAMBDA_ECHO % "true" if encode_response else LAMBDA_ECHO % "false"
        lambda_arn = create_lambda_function(
            handler_file=lambda_fn, func_name=lambda_name, runtime=Runtime.nodejs20_x
        )["CreateFunctionResponse"]["FunctionArn"]

        # create API
        api_name = f"api-{short_uid()}"
        result = create_v2_api(Name=api_name, ProtocolType="HTTP", Target=lambda_arn)
        api_id = result["ApiId"]

        url_parameters = {"param1": "value1", "param2": "value2"}
        url = f'{get_execute_api_endpoint(api_id, protocol="http://")}/test/resource1'
        response = requests.post(
            url, data=url_parameters, headers={"Content-Type": "application/x-www-form-urlencoded"}
        )

        assert response.status_code < 400
        assert response.cookies.items() == [("cookie2", "vaquarkhan")]
        if encode_response:
            assert to_str(response.content) == urlencode(url_parameters)
        else:
            assert to_str(response.content) == to_str(
                base64.b64encode(b"param1=value1&param2=value2")
            )

        aws_client.lambda_.delete_function(FunctionName=lambda_name)

    @markers.aws.validated
    def test_cors_preflight_requests(
        self,
        create_v2_api,
        create_lambda_function,
        add_permission_for_integration_lambda,
        aws_client,
    ):
        result = create_v2_api(
            ProtocolType="HTTP",
            Name=f"{short_uid()}",
            CorsConfiguration={
                "AllowCredentials": False,
                "AllowHeaders": [
                    "content-type",
                ],
                "AllowMethods": [
                    "GET",
                    "POST",
                    "PUT",
                    "PATCH",
                    "DELETE",
                    "OPTIONS",
                ],
                "AllowOrigins": ["http://localhost:4566", "https://lwn.net"],
                "MaxAge": 0,
            },
        )
        api_id = result["ApiId"]
        endpoint = result["ApiEndpoint"]

        func_name = f"func_{short_uid()}"
        zip_file = testutil.create_lambda_archive(
            LAMBDA_ECHO_EVENT, get_content=True, runtime=Runtime.nodejs20_x
        )
        create_lambda_function(func_name=func_name, zip_file=zip_file, runtime=Runtime.nodejs20_x)
        lambda_arn = aws_client.lambda_.get_function(FunctionName=func_name)["Configuration"][
            "FunctionArn"
        ]
        add_permission_for_integration_lambda(api_id, lambda_arn)

        integration_id = create_http_integration(
            aws_client.apigatewayv2,
            ApiId=api_id,
            IntegrationType="AWS_PROXY",
            PayloadFormatVersion="2.0",
            IntegrationMethod="ANY",
            IntegrationUri=lambda_arn,
        )
        create_http_route(
            aws_client.apigatewayv2,
            ApiId=api_id,
            AuthorizationType="NONE",
            RouteKey="POST /test",
            Target=f"integrations/{integration_id}",
        )

        create_http_stage(
            aws_client.apigatewayv2, ApiId=api_id, StageName="$default", AutoDeploy=True
        )

        https_endpoint = (
            f"{endpoint}/test" if "https://" in endpoint else f"https://{endpoint}/test"
        )

        # CORS Regular Request
        def validate_regular_request():
            response = requests.post(https_endpoint, headers={"Origin": "https://lwn.net"})
            assert response.status_code == 200
            assert "https://lwn.net" in response.headers["Access-Control-Allow-Origin"]

        retry(validate_regular_request, retries=5, sleep=1)

        # CORS Preflight Request
        def validate_preflight_request():
            preflight_response = requests.options(
                https_endpoint,
                headers={
                    "Origin": "https://lwn.net",
                    "Access-Control-Request-Method": "POST",
                    "Access-Control-Request-Headers": "Content-Type",
                },
            )
            assert preflight_response.status_code == 204
            assert "https://lwn.net" in preflight_response.headers["Access-Control-Allow-Origin"]
            assert all(
                r in ["HEAD", "GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
                for r in preflight_response.headers["Access-Control-Allow-Methods"].split(",")
            )
            assert "content-type" in preflight_response.headers["Access-Control-Allow-Headers"]

        retry(validate_preflight_request, retries=5, sleep=1)

    @markers.skip_offline
    @markers.aws.only_localstack
    def test_servicediscovery_ecs_integration(
        self, deploy_cfn_template, cleanup_changesets, cleanup_stacks, aws_client
    ):
        # start pulling Docker image in the background
        start_worker_thread(lambda *args: DOCKER_CLIENT.pull_image("nginx"))
        # deploy API Gateway ECS sample app
        result = deploy_cfn_template(
            template_path=os.path.join(
                os.path.dirname(__file__), "../../templates/apigateway.ecs.servicediscovery.yml"
            )
        )

        # check ECS deployment
        cluster_id = result.outputs["ECSClusterID"]
        task_arns = aws_client.ecs.list_tasks(cluster=cluster_id)["taskArns"]
        tasks = aws_client.ecs.describe_tasks(cluster=cluster_id, tasks=task_arns)["tasks"]
        # assert that host ports are defined for the deployed containers
        for task in tasks:
            assert task["containers"][0]["networkBindings"][0]["hostPort"]

        # check ServiceDiscovery deployment
        service1 = aws_client.servicediscovery.get_service(
            Id=result.outputs["ServiceDiscoveryServiceFoodstoreFoodsID"]
        )
        service2 = aws_client.servicediscovery.get_service(
            Id=result.outputs["ServiceDiscoveryServicePetstorePetsID"]
        )
        instances1 = aws_client.servicediscovery.list_instances(
            ServiceId=service1["Service"]["Id"]
        )["Instances"]
        instances2 = aws_client.servicediscovery.list_instances(
            ServiceId=service2["Service"]["Id"]
        )["Instances"]

        assert len(instances1) == 3
        assert len(instances2) == 3

        # invoke services via API Gateway
        def _invoke():
            api_id = result.outputs["APIId"]
            base_url = get_execute_api_endpoint(api_id, protocol="http://")
            response = requests.get(f"{base_url}/foodstore/foods/test")
            assert "nginx" in to_str(response.content)
            response = requests.get(f"{base_url}/petstore/pets/test")
            assert "nginx" in to_str(response.content)
            response = requests.get(f"{base_url}/invalid-path")
            assert not response.ok
            assert "nginx" not in to_str(response.content)
            assert "Not Found" in to_str(response.content)

        retry(_invoke, retries=15, sleep=1)

    @markers.aws.validated
    @pytest.mark.parametrize("payload_format", ["1.0"])  # only supports 1.0
    @pytest.mark.parametrize("url_function", [path_based_url, host_based_url])
    def test_step_functions_integration(
        self,
        create_v2_api,
        create_stepfunctions,
        create_lambda_function,
        payload_format,
        url_function,
        create_role,
        create_policy,
        aws_client,
        region_name,
    ):
        # create HTTP API
        result = create_v2_api(ProtocolType="HTTP", Name=f"http-{short_uid()}")
        api_id = result["ApiId"]
        # create IAM role and policy for API Gateway to invoke Step Functions
        role_name = f"apigw-role-{short_uid()}"
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
        apigw_role_arn = create_role(
            RoleName=role_name, AssumeRolePolicyDocument=json.dumps(assume_role_doc)
        )["Role"]["Arn"]
        aws_client.iam.attach_role_policy(
            RoleName=role_name,
            PolicyArn=f"arn:{get_partition(region_name)}:iam::aws:policy/AWSStepFunctionsFullAccess",
        )

        # create Lambda function
        lambda_name = f"{short_uid()}"
        lambda_fn = LAMBDA_JS % "Foobar"
        lambda_arn = create_lambda_function(
            handler_file=lambda_fn, func_name=lambda_name, runtime=Runtime.nodejs20_x
        )["CreateFunctionResponse"]["FunctionArn"]

        # create IAM role and policy for Step Functions to invoke Lambda
        role_name = f"sfn-role-{short_uid()}"
        assume_role_doc = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "sts:AssumeRole",
                    "Principal": {"Service": "states.amazonaws.com"},
                    "Effect": "Allow",
                }
            ],
        }
        policy_doc = {
            "Version": "2012-10-17",
            "Statement": [{"Effect": "Allow", "Action": "lambda:*", "Resource": "*"}],
        }
        role_arn = create_role(
            RoleName=role_name, AssumeRolePolicyDocument=json.dumps(assume_role_doc)
        )["Role"]["Arn"]
        policy_arn = create_policy(
            PolicyName=f"test-policy-{short_uid()}", PolicyDocument=json.dumps(policy_doc)
        )["Policy"]["Arn"]
        aws_client.iam.attach_role_policy(RoleName=role_name, PolicyArn=policy_arn)
        # create Step Functions state machine
        sfn_state_machine_arn = create_stepfunctions(
            name=f"{short_uid()}",
            definition=STEP_FUNCTION_DEFINITION % lambda_arn,
            roleArn=role_arn,
        )
        # create API Gateway integration with Step Functions
        integration_id = create_http_integration(
            aws_client.apigatewayv2,
            ApiId=api_id,
            CredentialsArn=apigw_role_arn,
            IntegrationType="AWS_PROXY",
            IntegrationSubtype="StepFunctions-StartExecution",
            PayloadFormatVersion=payload_format,
            RequestParameters={
                "StateMachineArn": sfn_state_machine_arn,
                "Input": "$request.body",
            },
        )
        # create API Gateway route targeting Step Functions service
        create_http_route(
            aws_client.apigatewayv2,
            ApiId=api_id,
            AuthorizationType="NONE",
            RouteKey="POST /test",
            Target=f"integrations/{integration_id}",
        )
        # create API Gateway stage
        create_http_stage(
            aws_client.apigatewayv2, ApiId=api_id, StageName="$default", AutoDeploy=True
        )

        # invoke API Gateway
        def check_result():
            endpoint = api_invoke_url(api_id=api_id, path="test")
            result = requests.post(
                endpoint,
                headers={"Content-Type": "application/json"},
                verify=False,
                json={"input": "{}"},
            )
            assert result.status_code == 200
            assert sfn_state_machine_arn.split(":")[-1] in result.json()["executionArn"]

        retry(check_result, retries=5, sleep=3)

    @markers.aws.validated
    @pytest.mark.parametrize("payload_version", ["1.0", "2.0"])
    @markers.snapshot.skip_snapshot_verify(
        paths=[
            "$..headers",
            "$..body",
            "$..multiValueHeaders",
            "$..requestContext",
            "$..multiValueQueryStringParameters",
            "$..pathParameters",
            "$..queryStringParameters",
            "$..stageVariables",
            "$.create-api.ApiEndpoint",  # AWS and LocalStack returns different endpoint
            # TODO: LocalStack APIGW v2 returns an incomplete response
            "$.create-api.ApiKeySelectionExpression",
            "$.create-api.CreatedDate",
            "$.create-api.DisableExecuteApiEndpoint",
            "$.create-api.RouteSelectionExpression",
        ]
    )
    def test_apigw_v2_lambda_request_authorizer(
        self,
        create_v2_api,
        create_lambda_function,
        add_permission_for_integration_lambda,
        apigateway_lambda_integration_role,
        snapshot,
        payload_version,
        aws_client_factory,
        aws_client,
        region_name,
    ):
        lambda_client = aws_client_factory(region_name="eu-west-1").lambda_

        snapshot.add_transformer(snapshot.transform.apigateway_proxy_event())
        snapshot.add_transformers_list(
            [
                snapshot.transform.key_value("Name"),
                snapshot.transform.key_value("ApiId"),
            ]
        )

        # create http api
        result = create_v2_api(
            Name=f"test-{short_uid()}-{payload_version}",
            ProtocolType="HTTP",
        )
        snapshot.match("create-api", result)
        api_id = result["ApiId"]

        # create the request lambda authorizer
        lambda_name = f"{short_uid()}"
        lambda_arn = create_lambda_function(
            lambda_client,
            handler_file=TEST_LAMBDA_AUTHORIZER_IAM_RESPONSE,
            func_name=lambda_name,
            runtime=Runtime.python3_12,
        )["CreateFunctionResponse"]["FunctionArn"]

        auth_url = arns.apigateway_invocations_arn(lambda_arn, region_name)
        authorizer_id = create_http_authorizer(
            aws_client.apigatewayv2,
            ApiId=api_id,
            Name=f"test_authorizer-{short_uid()}",
            AuthorizerType="REQUEST",
            AuthorizerCredentialsArn=apigateway_lambda_integration_role,
            AuthorizerPayloadFormatVersion=payload_version,
            IdentitySource=["$request.header.X-User"],
            AuthorizerUri=auth_url,
        )

        # create lambda integration
        lambda_name = f"{short_uid()}"
        lambda_arn = create_lambda_function(
            lambda_client,
            handler_file=LAMBDA_ECHO_EVENT,
            func_name=lambda_name,
            runtime=Runtime.nodejs20_x,
        )["CreateFunctionResponse"]["FunctionArn"]
        add_permission_for_integration_lambda(api_id, lambda_arn)

        uri = arns.apigateway_invocations_arn(lambda_arn, region_name="eu-west-1")
        integration_id = create_http_integration(
            aws_client.apigatewayv2,
            ApiId=api_id,
            IntegrationType="AWS_PROXY",
            IntegrationMethod="POST",
            IntegrationUri=uri,
            PayloadFormatVersion=payload_version,
            CredentialsArn=apigateway_lambda_integration_role,
        )

        # create GET /test route
        create_http_route(
            aws_client.apigatewayv2,
            ApiId=api_id,
            AuthorizationType="CUSTOM",
            AuthorizerId=authorizer_id,
            RouteKey="GET /test",
            Target=f"integrations/{integration_id}",
        )
        create_http_stage(
            aws_client.apigatewayv2, ApiId=api_id, StageName="$default", AutoDeploy=True
        )

        private_endpoint = api_invoke_url(api_id=api_id, path="/test")

        def _call_and_assert():
            # we need to use `urllib3` here, because `requests` strip leading slashes following this PR
            # https://github.com/psf/requests/pull/6644
            response = urllib3.request(
                "GET",
                private_endpoint,
                headers={"X-User": "valid-token", "User-Agent": "urllib3-test"},
            )
            assert response.status == 200

            # lambda authorizer passes the context into the integration lambda
            # the integration lambda returns the context in the response body
            # we can use this to verify that the authorizer rendered the correct identitySource
            body = json.loads(response.data)
            if payload_version == "2.0":
                identity_source = body["requestContext"]["authorizer"]["lambda"]["identitySource"]
            else:
                identity_source = body["requestContext"]["authorizer"]["identitySource"]

            # assertions
            assert "valid-token" in identity_source
            return response.json()

        result = retry(_call_and_assert, retries=10, sleep=2)
        snapshot.match("lambda_request_authorizer", result)

        # testing double slash in path
        private_endpoint = api_invoke_url(api_id=api_id, path="//test")
        result = retry(_call_and_assert, retries=10, sleep=2)
        snapshot.match("lambda_request_authorizer_double_slash", result)

    # TODO:
    # - HTTP_PROXY snapshot tests implemented on https://github.com/localstack/localstack-ext/pull/1491
    @markers.aws.unknown
    def test_apigw_v2_http_jwt_authorizer(
        self,
        create_v2_api,
        create_user_pool_client,
        httpserver: HTTPServer,
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
        kwargs["AllowedOAuthScopes"] = scopes + custom_scopes
        aws_client.cognito_idp.update_user_pool_client(**kwargs)

        # create http api
        result = create_v2_api(ProtocolType="HTTP", Name=f"{short_uid()}")
        api_id = result["ApiId"]

        issuer_domain = config.external_service_url()
        if is_aws_cloud():
            issuer_domain = (
                f"https://cognito-idp.{aws_client.cognito_idp.meta.region_name}.amazonaws.com"
            )

        authorizer_id = create_http_authorizer(
            aws_client.apigatewayv2,
            Name="jwt-authorizer",
            ApiId=api_id,
            AuthorizerType="JWT",
            JwtConfiguration={
                "Audience": [cognito_client_id],
                "Issuer": f"{issuer_domain}/{cognito_pool_id}",
            },
            IdentitySource=["$request.header.Authorization"],
        )
        if is_aws_cloud():
            uri = "https://httpbin.org/anything"
        else:

            def _handler(_request: Request) -> WerkzeugResponse:
                response_content = {
                    "method": _request.method,
                    "path": _request.path,
                    "query": _request.query_string.decode("utf-8"),
                    "data": _request.get_data(as_text=True),
                    "headers": dict(_request.headers),
                }
                return WerkzeugResponse(
                    json.dumps(response_content), mimetype="application/json", status=200
                )

            httpserver.expect_request("").respond_with_handler(_handler)
            uri = httpserver.url_for("/")

        result = aws_client.apigatewayv2.create_integration(
            ApiId=result["ApiId"],
            IntegrationType="HTTP_PROXY",
            IntegrationMethod="ANY",
            PayloadFormatVersion="1.0",  # HTTP_PROXY only supports 1.0
            RequestParameters={
                "append:header.UseToken": "$context.authorizer.claims.token_use",
                "append:header.Scope": "$context.authorizer.claims.scope",
                "append:header.Username": "$context.authorizer.jwt.claims.username",
                "append:header.Sub": "$context.authorizer.claims.sub",
                "append:header.ApiId": "$context.apiId",
                "append:querystring.foo": "bar",
                "append:querystring.bash": "bosh",
                "overwrite:path": "/changed/path",
            },
            IntegrationUri=uri,
        )
        int_id = result["IntegrationId"]
        create_http_route(
            aws_client.apigatewayv2,
            ApiId=api_id,
            AuthorizationType="JWT",
            AuthorizerId=authorizer_id,
            AuthorizationScopes=["http://example.com/scope1"],
            RouteKey="POST /test/{proxy+}",
            Target=f"integrations/{int_id}",
        )
        # create deployment
        stage_name = "dev"
        create_deployment(aws_client.apigatewayv2, api_id, stage_name=stage_name)

        # assert responses
        endpoint = api_invoke_url(api_id=api_id, stage=stage_name, path="/test/foobar")
        result = requests.post(endpoint, headers={"Authorization": ""}, verify=False)
        assert result.status_code == 401
        assert to_str(result.content) == '{"message":"Unauthorized"}'

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
        _, access_token = get_auth_token_via_login_form(
            user_pool_result.user_pool,
            user_pool_result.pool_client,
            username=username,
            password=password,
            region_name=region_name,
            scope="openid email http://example.com/scope1",
        )

        endpoint = api_invoke_url(api_id=api_id, stage=stage_name, path="/test/foo")
        result = requests.post(endpoint, headers={"Authorization": access_token}, verify=False)
        body = result.json()

        assert result.status_code == 200

        headers = body["headers"]
        query = body["query"]
        path = body["path"]
        scopes = headers["Scope"].split()

        # assert headers
        assert headers["Usetoken"] == "access"
        assert "http://example.com/scope1" in scopes
        assert headers["Apiid"] == api_id
        assert headers["Sub"]
        assert not headers["Username"]
        # assert query
        assert query == "foo=bar&bash=bosh"
        # assert path
        assert path == "/changed/path"

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(paths=["$..EncryptionType"])
    def test_apigw_v2_http_kinesis_integration(
        self,
        create_v2_api,
        kinesis_create_stream,
        aws_client,
        create_iam_role_and_attach_policy,
        snapshot,
        region_name,
    ):
        snapshot.add_transformer(snapshot.transform.key_value("SequenceNumber"))
        snapshot.add_transformer(snapshot.transform.key_value("ShardId"))

        stream_name = f"test-{short_uid()}"
        kinesis_create_stream(StreamName=stream_name, ShardCount=1)

        result = create_v2_api(ProtocolType="HTTP", Name=f"{short_uid()}")
        api_id = result["ApiId"]
        role_arn = create_iam_role_and_attach_policy(
            policy_arn=f"arn:{get_partition(region_name)}:iam::aws:policy/AmazonKinesisFullAccess",
        )
        integration_id = create_http_integration(
            aws_client.apigatewayv2,
            ApiId=api_id,
            IntegrationType="AWS_PROXY",
            IntegrationSubtype="Kinesis-PutRecord",
            PayloadFormatVersion="1.0",
            RequestParameters={
                "Data": "$request.body.data",
                "PartitionKey": "$request.body.partitionKey",
                "StreamName": stream_name,
            },
            CredentialsArn=role_arn,
        )
        create_http_route(
            aws_client.apigatewayv2,
            ApiId=api_id,
            AuthorizationType="NONE",
            RouteKey="POST /",
            Target=f"integrations/{integration_id}",
        )
        create_http_stage(
            aws_client.apigatewayv2, ApiId=api_id, StageName="$default", AutoDeploy=True
        )
        create_http_deployment(aws_client.apigatewayv2, ApiId=api_id)

        endpoint = api_invoke_url(api_id=api_id, path="/")
        payload = {
            "data": "J0hlbGxvLCBXb3JsZCEnCg==",
            "partitionKey": "p1",
        }

        def _invoke():
            response = requests.post(
                endpoint,
                data=json.dumps(payload),
                headers={"Content-Type": "application/json"},
                verify=False,
            )
            assert response.status_code == 200
            return response.json()

        result = retry(_invoke, retries=10)
        snapshot.match("kinesis_integration", result)

        def _invoke_no_content_type():
            response = requests.post(
                endpoint,
                data=json.dumps(payload),
                verify=False,
            )
            assert response.status_code == 200
            return response.json()

        result = retry(_invoke_no_content_type, retries=10)
        snapshot.match("kinesis_integration_no_content_type", result)

    @markers.snapshot.skip_snapshot_verify(
        paths=[
            "$.create-integration.ConnectionType",  # FIXME: parity issue
            "$.create-route.ApiKeyRequired",
            "$.create-stage.DefaultRouteSettings",
            "$.create-stage.LastUpdatedDate",
            "$.create-stage.RouteSettings",
            "$.create-stage.StageVariables",
            "$.create-stage.Tags",
            "$.invoke-api.headers.via",  # FIXME: missing header
            "$.invoke-api.headers.x-amzn-trace-id",
            "$.invoke-api.headers.x-amzn-tls-cipher-suite",  # ignore, different TLS version
            "$.invoke-api.headers.x-amzn-tls-version",
            "$.invoke-api.headers.x-forwarded-for",
            "$.invoke-api.headers.x-forwarded-proto",
            "$.invoke-api.headers.x-localstack-edge",  # FIXME: added by LS
            "$.invoke-api.origin",
        ]
    )
    @markers.aws.validated
    def test_http_integration_keeps_body_intact(
        self, aws_client, create_v2_api, create_echo_http_server, snapshot
    ):
        snapshot.add_transformer(
            [
                snapshot.transform.key_value("RouteId"),
                snapshot.transform.key_value("IntegrationId"),
                snapshot.transform.key_value("IntegrationUri"),
                snapshot.transform.key_value("domain"),
                snapshot.transform.key_value("host"),
                snapshot.transform.key_value("forwarded"),
                snapshot.transform.key_value("x-amzn-trace-id"),
                snapshot.transform.key_value("origin"),
                snapshot.transform.key_value("x-forwarded-for"),
                snapshot.transform.key_value("x-forwarded-port"),
            ]
        )
        echo_server_url = create_echo_http_server(trim_x_headers=False)

        result = create_v2_api(ProtocolType="HTTP", Name=f"test-http-{short_uid()}")
        api_id = result["ApiId"]

        create_integration = aws_client.apigatewayv2.create_integration(
            ApiId=api_id,
            IntegrationType="HTTP_PROXY",
            PayloadFormatVersion="1.0",
            IntegrationMethod="ANY",
            IntegrationUri=echo_server_url,
        )
        snapshot.match("create-integration", create_integration)
        integration_id = create_integration["IntegrationId"]

        # creates the /{proxy+} route
        create_route = aws_client.apigatewayv2.create_route(
            ApiId=api_id,
            RouteKey="ANY /api/{proxy+}",
            Target=f"integrations/{integration_id}",
            AuthorizationType="NONE",
        )
        snapshot.match("create-route", create_route)

        stage_name = "dev"
        create_stage = aws_client.apigatewayv2.create_stage(
            ApiId=api_id,
            StageName=stage_name,
            AutoDeploy=True,
        )
        snapshot.match("create-stage", create_stage)

        # multipart body
        body = (
            b"\r\n--4efd159eae0c4f4e125a5a509e073d85\r\n"
            b'Content-Disposition: form-data; name="formfield"\r\n\r\n'
            b"not a file, just a field"
            b"\r\n--4efd159eae0c4f4e125a5a509e073d85\r\n"
            b'Content-Disposition: form-data; name="foo"; filename="foo"\r\n'
            b"Content-Type: text/plain;\r\n\r\n"
            b"bar"
            b"\r\n\r\n--4efd159eae0c4f4e125a5a509e073d85--\r\n"
        )

        def invoke():
            _endpoint = api_invoke_url(api_id=api_id, stage=stage_name, path="/api/test")
            _response = requests.post(
                _endpoint,
                headers={
                    "Content-Type": "multipart/form-data; boundary=4efd159eae0c4f4e125a5a509e073d85",
                    "User-Agent": "python/test-request",
                },
                data=body,
                verify=False,
            )
            assert _response.status_code == 200
            return _response

        response = retry(invoke, sleep=1, retries=10)
        json_data = response.json()
        snapshot.match("invoke-api", json_data)

        form_data = base64.b64decode(json_data["data"])
        assert form_data == body


class TestImportAPIs:
    @markers.aws.unknown
    def test_import_apis(self, aws_client):
        client = aws_client.apigatewayv2
        api_spec = load_file(API_SPEC_FILE)

        def run_asserts(api_id):
            result = client.get_models(ApiId=api_id)["Items"]
            model_names = [m["Name"] for m in result]
            assert len(model_names) == 6
            for name in ["Pets", "Pet", "PetType", "NewPet"]:
                assert name in model_names

            all_routes = client.get_routes(ApiId=api_id)["Items"]
            routes = [r["RouteKey"] for r in all_routes]
            assert len(routes) == 3
            for route in ["GET /pets", "POST /pets", "GET /pets/{petId}"]:
                assert route in routes

            result = client.get_authorizers(ApiId=api_id)["Items"]
            authorizer = [a for a in result if a["Name"] == "my-auth-gw-imported"]
            assert len(authorizer) == 1
            assert authorizer[0].get("IdentitySource") == ["route.request.header.Authorization"]
            protected_route = [r for r in all_routes if r["RouteKey"] == "GET /pets/{petId}"][0]
            assert authorizer[0].get("AuthorizerId") == protected_route.get("AuthorizerId")

            integrations = get_http_integrations(client, ApiId=api_id)
            assert len(integrations) == 3
            aws_proxy_integration = filter(
                lambda x: (x["IntegrationType"] == "AWS_PROXY"), integrations
            )
            assert next(aws_proxy_integration)["PayloadFormatVersion"] == "2.0"

        # import API
        result = client.import_api(Basepath="/", Body=api_spec)
        api_id = result["ApiId"]
        run_asserts(api_id)

        # re-import API
        client.reimport_api(ApiId=api_id, Body=api_spec)
        run_asserts(api_id)

        # clean up
        client.delete_api(ApiId=api_id)
