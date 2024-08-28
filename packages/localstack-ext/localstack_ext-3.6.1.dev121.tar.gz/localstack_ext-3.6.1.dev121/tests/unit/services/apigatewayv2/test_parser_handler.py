import pytest
from localstack.http import Request, Response
from localstack.pro.core.services.apigateway.models import V2Api
from localstack.pro.core.services.apigatewayv2.next_gen.execute_api.helpers import freeze_http_api
from localstack.pro.core.services.apigatewayv2.next_gen.execute_api.http.api import (
    HttpApiGatewayHandlerChain,
)
from localstack.pro.core.services.apigatewayv2.next_gen.execute_api.http.context import (
    HttpApiInvocationContext,
)
from localstack.pro.core.services.apigatewayv2.next_gen.execute_api.http.handlers.parse import (
    HttpInvocationRequestParser,
)
from localstack.testing.config import TEST_AWS_ACCOUNT_ID, TEST_AWS_REGION_NAME
from werkzeug.datastructures import Headers

TEST_API_ID = "testapi"
TEST_API_STAGE = "dev"


@pytest.fixture
def dummy_deployment():
    return freeze_http_api(
        account_id=TEST_AWS_ACCOUNT_ID,
        region=TEST_AWS_REGION_NAME,
        v2_api=V2Api(details={}),
    )


@pytest.fixture
def get_invocation_context():
    def _create_context(request: Request) -> HttpApiInvocationContext:
        context = HttpApiInvocationContext(request)
        context.api_id = TEST_API_ID
        context.stage = TEST_API_STAGE
        context.account_id = TEST_AWS_ACCOUNT_ID
        context.region = TEST_AWS_REGION_NAME
        return context

    return _create_context


@pytest.fixture
def parse_handler_chain() -> HttpApiGatewayHandlerChain:
    """Returns a dummy chain for testing."""
    return HttpApiGatewayHandlerChain(request_handlers=[HttpInvocationRequestParser()])


class TestParsingHandler:
    def test_parse_request(self, dummy_deployment, parse_handler_chain, get_invocation_context):
        host_header = f"{TEST_API_ID}.execute-api.host.com"
        headers = Headers(
            {
                "test-header": "value1",
                "test-header-multi": ["value2", "value3"],
                "host": host_header,
            }
        )
        body = b"random-body"
        request = Request(
            body=body,
            headers=headers,
            query_string="test-param=1&test-param-2=2&test-multi=val1&test-multi=val2",
            path=f"/{TEST_API_STAGE}/normal-path",
        )
        context = get_invocation_context(request)
        context.deployment = dummy_deployment

        parse_handler_chain.handle(context, Response())

        assert context.request == request
        assert context.account_id == TEST_AWS_ACCOUNT_ID
        assert context.region == TEST_AWS_REGION_NAME

        assert context.invocation_request["http_method"] == "GET"
        assert context.invocation_request["headers"] == Headers(
            {
                "host": host_header,
                "test-header": "value1",
                "test-header-multi": ["value2", "value3"],
                # TODO: this might be removed, TBD
                "content-length": 11,
            }
        )
        assert context.invocation_request["query_string_parameters"] == {
            "test-param": ["1"],
            "test-param-2": ["2"],
            "test-multi": ["val1", "val2"],
        }
        assert context.invocation_request["body"] == body
        assert (
            context.invocation_request["path"]
            == context.invocation_request["raw_path"]
            == "/normal-path"
        )

        assert context.context_variables["domainName"] == host_header
        assert context.context_variables["domainPrefix"] == TEST_API_ID
        assert context.context_variables["path"] == f"/{TEST_API_STAGE}/normal-path"

        assert "Root=" in context.trace_id

    def test_parse_raw_path(self, dummy_deployment, parse_handler_chain, get_invocation_context):
        request = Request(
            "GET",
            path=f"/{TEST_API_STAGE}/foo/bar/ed",
            raw_path=f"/{TEST_API_STAGE}//foo%2Fbar/ed",
        )

        context = get_invocation_context(request)
        context.deployment = dummy_deployment

        parse_handler_chain.handle(context, Response())

        # depending on the usage, we need the forward slashes or not
        # for example, for routing, we need the singular forward slash
        # but for passing the path to a lambda proxy event for example, we need the raw path as it was in the environ
        assert context.invocation_request["path"] == "/foo%2Fbar/ed"
        assert context.invocation_request["raw_path"] == "//foo%2Fbar/ed"

    def test_parse_user_request_path(
        self, dummy_deployment, parse_handler_chain, get_invocation_context
    ):
        # simulate a path request
        request = Request(
            "GET",
            path=f"/restapis/{TEST_API_ID}/{TEST_API_STAGE}/_user_request_/foo/bar/ed",
            raw_path=f"/restapis/{TEST_API_ID}/{TEST_API_STAGE}/_user_request_//foo%2Fbar/ed",
        )

        context = get_invocation_context(request)
        context.deployment = dummy_deployment

        parse_handler_chain.handle(context, Response())

        # assert that the user request prefix has been stripped off
        assert context.invocation_request["path"] == "/foo%2Fbar/ed"
        assert context.invocation_request["raw_path"] == "//foo%2Fbar/ed"

    @pytest.mark.parametrize("addressing", ["host", "user_request"])
    def test_parse_path_same_as_stage(
        self, dummy_deployment, parse_handler_chain, get_invocation_context, addressing
    ):
        path = TEST_API_STAGE
        if addressing == "host":
            full_path = f"/{TEST_API_STAGE}/{path}"
        else:
            full_path = f"/restapis/{TEST_API_ID}/{TEST_API_STAGE}/_user_request_/{path}"

        # simulate a path request
        request = Request("GET", path=full_path)

        context = get_invocation_context(request)
        context.deployment = dummy_deployment

        parse_handler_chain.handle(context, Response())

        # assert that the user request prefix has been stripped off
        assert context.invocation_request["path"] == f"/{TEST_API_STAGE}"
        assert context.invocation_request["raw_path"] == f"/{TEST_API_STAGE}"

    def test_parse_default_stage(
        self, dummy_deployment, parse_handler_chain, get_invocation_context
    ):
        # simulate a path request
        request = Request(
            "GET",
            path="/random-path-with-no-stage",
            raw_path="/random-path-with-no-stage",
        )

        context = get_invocation_context(request)
        context.deployment = dummy_deployment
        context.stage = "$default"

        parse_handler_chain.handle(context, Response())

        # assert that the user request prefix has been stripped off
        assert context.invocation_request["path"] == "/random-path-with-no-stage"
        assert context.invocation_request["raw_path"] == "/random-path-with-no-stage"

    def test_parse_custom_domain_base_path(
        self, dummy_deployment, parse_handler_chain, get_invocation_context
    ):
        request = Request(
            "GET",
            path="/base-path/foo/bar/ed",
            raw_path="/base-path//foo%2Fbar/ed",
        )

        context = get_invocation_context(request)
        context.deployment = dummy_deployment
        context.base_path = "/base-path"
        context.stage = "dev"

        parse_handler_chain.handle(context, Response())

        # assert that the user request prefix has been stripped off
        assert context.invocation_request["path"] == "/foo%2Fbar/ed"
        assert context.invocation_request["raw_path"] == "//foo%2Fbar/ed"

    def test_parse_custom_domain_base_path_and_stage(
        self, dummy_deployment, parse_handler_chain, get_invocation_context
    ):
        # TODO: normally, it depends how to base path mapping / api mapping was configured
        #  if the stage was set to (none) then we should remove it from the path
        #  if the stage was hardcoded, then we should not remove it as it is not part of the path but could be a route
        #  defined by the user
        request = Request(
            "GET",
            path="/base-path/dev/foo/bar/ed",
            raw_path="/base-path/dev//foo%2Fbar/ed",
        )

        context = get_invocation_context(request)
        context.deployment = dummy_deployment
        context.base_path = "/base-path"
        context.stage = "dev"

        parse_handler_chain.handle(context, Response())

        # assert that the user request prefix has been stripped off
        assert context.invocation_request["path"] == "/foo%2Fbar/ed"
        assert context.invocation_request["raw_path"] == "//foo%2Fbar/ed"
