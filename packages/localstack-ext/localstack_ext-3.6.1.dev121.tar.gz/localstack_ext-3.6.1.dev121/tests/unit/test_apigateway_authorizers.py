import pytest
from localstack.pro.core.services.apigateway.authorizers import (
    BestRouteCandidate,
    CognitoAuthorizer,
    LambdaRequestAuthorizer,
    ResourceCandidate,
    ResourcePatternMatch,
)
from localstack.services.apigateway.context import ApiInvocationContext
from localstack.testing.config import TEST_AWS_ACCOUNT_ID, TEST_AWS_REGION_NAME
from moto.apigateway.models import Resource


@pytest.fixture
def api_resources():
    # /
    root = Resource(
        api_id="kc6wgyf7sf",
        resource_id="e0z7enkfkk",
        parent_id=None,
        path_part="/",
        account_id=TEST_AWS_ACCOUNT_ID,
        region_name=TEST_AWS_REGION_NAME,
    )
    # /{proxy+}
    proxy = Resource(
        api_id="kc6wgyf7sf",
        resource_id="hj3wfoy2sf",
        parent_id=None,
        path_part="{proxy+}",
        account_id=TEST_AWS_ACCOUNT_ID,
        region_name=TEST_AWS_REGION_NAME,
    )
    # /activity
    activity = Resource(
        api_id="kc6wgyf7sf",
        resource_id="erws24sh3g",
        parent_id="e0z7enkfkk",
        path_part="activity",
        account_id=TEST_AWS_ACCOUNT_ID,
        region_name=TEST_AWS_REGION_NAME,
    )
    # /activity/{id}
    activity_id = Resource(
        api_id="kc6wgyf7sf",
        resource_id="880m77qzoj",
        parent_id="erws24sh3g",
        path_part="{id}",
        account_id=TEST_AWS_ACCOUNT_ID,
        region_name=TEST_AWS_REGION_NAME,
    )
    # /activity/{id}/status
    activity_id_status = Resource(
        api_id="kc6wgyf7sf",
        resource_id="110m99qzoj",
        parent_id="880m77qzoj",
        path_part="status",
        account_id=TEST_AWS_ACCOUNT_ID,
        region_name=TEST_AWS_REGION_NAME,
    )
    # /{id}
    idr = Resource(
        api_id="kc6wgyf7sf",
        resource_id="kc3wgyf8sf",
        parent_id=None,
        path_part="{id}",
        account_id=TEST_AWS_ACCOUNT_ID,
        region_name=TEST_AWS_REGION_NAME,
    )

    return dict(
        {
            "deadb33dfe": proxy,
            "e0z7enkfkk": root,
            "erws24sh3g": activity,
            "880m77qzoj": activity_id,
            "110m99qzoj": activity_id_status,
            "kc3wgyf8sf": idr,
        }
    )


def test_resource_pattern_match_normalization(api_resources):
    rpm = ResourcePatternMatch(api_resources)
    assert all(
        r in ["/", "/activity", "/activity/{id}", "/activity/{id}/status", "/{id}", "/{proxy+}"]
        for r in list(rpm.normalize_paths().values())
    )


def test_resource_pattern_match(api_resources):
    rpm = ResourcePatternMatch(api_resources)

    assert rpm._match_path("/42")[1] == "/{id}"
    assert rpm._match_path("/foo/bar")[1] == "/{proxy+}"
    assert rpm._match_path("/activity")[1] == "/activity"
    assert rpm._match_path("/activity/42")[1] == "/activity/{id}"
    assert rpm._match_path("/activity/42/status")[1] == "/activity/{id}/status"


def test_resource_pattern_best_match():
    best_match = BestRouteCandidate()
    routes = [
        "/{proxy+}",
        "/foo/{param1}/{param2}",
        "/42",
        "/foo/{param1}/baz",
        "/{id}",
        "/api/{proxy+}",
        "/{param1}/foo/{param2}",
    ]

    def namedzip(path: str):
        return [ResourceCandidate(path, route, "abc123") for route in routes]

    best_matches = best_match.best_match(namedzip("/foo"))
    assert best_matches.resource_path == "/{id}"

    best_matches = best_match.best_match(namedzip("/foo/bar/baz"))
    assert best_matches.resource_path == "/foo/{param1}/baz"

    best_matches = best_match.best_match(namedzip("/bar/baz"))
    assert best_matches.resource_path == "/{proxy+}"


def test_when_token_doesnt_match_should_throw_exception():
    authorizer_config = {
        "id": "1040a8",
        "name": "test_authorizer",
        "type": "COGNITO_USER_POOLS",
        "providerARNs": [
            "arn:aws:cognito-idp:us-east-1:000000000000:userpool/us-east"
            "-1_694f5eb4a27f4bafae5b98330f7cf901"
        ],
        "authorizerResultTtlInSeconds": 300,
    }

    ctx = ApiInvocationContext(
        method="POST", path="/", headers={"Authorization": "Bearer xxx"}, data=b""
    )
    with pytest.raises(Exception):
        CognitoAuthorizer(authorizer_config).authorize(ctx)


def test_lambda_request_authorizer_payload():
    config = {
        "authorizerResultTtlInSeconds": 300,
        "authorizerType": "REQUEST",
        "authorizerUri": "arn:aws:apigateway:eu-west-1:lambda:path/2015-03-31/functions/arn:aws"
        ":lambda:eu-west-1:000000000000:function:lambda-auth/invocations",
        "identitySource": ["$request.header.Authorization"],
        "name": "example-authorizer",
        "apiId": "4f40c0ae",
        "createdDate": 1650880397,
        "authorizerId": "ec73f287",
    }

    context = ApiInvocationContext(method="GET", path="/", data="", headers={})
    context.region_name = "eu-west-1"
    context.api_id = "4f40c0ae"
    context.stage = "$default"
    authorizer = LambdaRequestAuthorizer(config)

    # test v1 authorizer payload
    authorizer_payload = authorizer._create_authorizer_event(context)
    v1_payload_expected_keys = [
        "version",
        "type",
        "methodArn",
        "identitySource",
        "authorizationToken",
        "resource",
        "path",
        "httpMethod",
        "headers",
        "queryStringParameters",
        "pathParameters",
        "stageVariables",
        "requestContext",
    ]
    assert all(k in authorizer_payload.keys() for k in v1_payload_expected_keys)


def test_lambda_request_authorizer_payload_v2():
    config = {
        "authorizerResultTtlInSeconds": 300,
        "authorizerType": "REQUEST",
        "authorizerUri": "arn:aws:apigateway:eu-west-1:lambda:path/2015-03-31/functions/arn:aws"
        ":lambda:eu-west-1:000000000000:function:lambda-auth/invocations",
        "identitySource": ["$request.header.Authorization"],
        "name": "example-authorizer",
        "apiId": "4f40c0ae",
        "createdDate": 1650880397,
        "authorizerId": "ec73f287",
    }

    context = ApiInvocationContext(method="GET", path="/", data="", headers={})
    context.region_name = "eu-west-1"
    context.api_id = "4f40c0ae"
    context.stage = "$default"

    class MockLambdaRequestAuthorizer(LambdaRequestAuthorizer):
        def _create_request_context(
            self, ctx: ApiInvocationContext, account_id: str, relative_path: str
        ):
            return {}

        def _is_http_api_and_v2_payload_version(self, ctx: ApiInvocationContext):
            return True

        def _find_route_integration(self, ctx: ApiInvocationContext):
            return {"integrationMethod": "GET"}

    authorizer = MockLambdaRequestAuthorizer(config)
    authorizer_payload_v2 = authorizer._create_authorizer_event(context)
    v2_payload_expected_keys = [
        "version",
        "type",
        "routeArn",
        "identitySource",
        "routeKey",
        "rawPath",
        "rawQueryString",
        "cookies",
        "headers",
        "queryStringParameters",
        "requestContext",
        "pathParameters",
        "stageVariables",
    ]
    assert all(k in authorizer_payload_v2.keys() for k in v2_payload_expected_keys)
