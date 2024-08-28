import pytest
from localstack.pro.core.aws.api.apigatewayv2 import Integration, Route, Stage
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
from localstack.pro.core.services.apigatewayv2.next_gen.execute_api.http.handlers.router import (
    HttpInvocationRequestRouter,
)
from localstack.pro.core.services.apigatewayv2.next_gen.execute_api.http.invoke_exceptions import (
    NotFoundError,
)
from localstack.pro.core.services.apigatewayv2.next_gen.models import V2Api, apigatewayv2_stores
from localstack.testing.config import TEST_AWS_ACCOUNT_ID, TEST_AWS_REGION_NAME
from localstack.utils.strings import short_uid
from rolo import Request, Response

TEST_API_ID = "testapi"
TEST_API_STAGE = "dev"
TEST_INTEGRATION_ID = "test-integration"
DEFAULT_TARGET = f"integrations/{TEST_INTEGRATION_ID}"


@pytest.fixture
def dummy_deployment():
    v2_api = V2Api(api_data={"ApiId": TEST_API_ID})
    v2_api.stages[TEST_API_STAGE] = Stage(StageVariables={"foo": "bar"})
    v2_api.integrations[TEST_INTEGRATION_ID] = Integration(IntegrationId="test")

    # we need to store the API in the store for the handler to be able to fetch stage variables, as they are not
    # frozen in the deployment and can be updated at runtime
    apigatewayv2_stores[TEST_AWS_ACCOUNT_ID][TEST_AWS_REGION_NAME].apis[TEST_API_ID] = v2_api

    yield freeze_http_api(
        account_id=TEST_AWS_ACCOUNT_ID,
        region=TEST_AWS_REGION_NAME,
        v2_api=v2_api,
    )

    apigatewayv2_stores.reset()


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


class TestHttpRoutingHandler:
    @pytest.fixture
    def deployment_with_routes(self, dummy_deployment):
        """
        This can be represented by the following routes:
        - GET /foo
        - PUT /foo/{param}
        - DELETE /proxy/{proxy+}
        - DELETE /proxy/bar/{param}

        - No Target for GET /foo/no-integration

        Note: we have the base `/proxy` route to not have greedy matching on the base route, and the other child routes
        are to assert the `{proxy+} has less priority than hardcoded routes

        Routes with no Integration raises NotFound as well, so we should not add those routes in our router
        """
        # put them disorderly, so we check the matching is order-insensitive
        routes = [
            Route(RouteKey="GET /foo/no-integration", RouteId=short_uid()),
            Route(RouteKey="DELETE /proxy/{proxy+}", RouteId=short_uid(), Target=DEFAULT_TARGET),
            Route(RouteKey="PUT /foo/{param}", RouteId=short_uid(), Target=DEFAULT_TARGET),
            Route(RouteKey="DELETE /proxy/bar/{param}", RouteId=short_uid(), Target=DEFAULT_TARGET),
            Route(RouteKey="GET /foo", RouteId=short_uid(), Target=DEFAULT_TARGET),
        ]

        for route in routes:
            dummy_deployment.http_api.routes[route["RouteId"]] = route

        return dummy_deployment

    @pytest.fixture
    def deployment_with_any_routes_and_default(self, dummy_deployment):
        """
        Taken from https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-develop-routes.html
        - GET /pets/dog/1
        - GET /pets/dog/{id}
        - GET /pets/{proxy+}
        - ANY /{proxy+}
        - $default
        """
        routes = [
            Route(RouteKey="ANY /{proxy+}", RouteId=short_uid(), Target=DEFAULT_TARGET),
            Route(RouteKey="GET /pets/dog/1", RouteId=short_uid(), Target=DEFAULT_TARGET),
            Route(RouteKey="GET /pets/{proxy+}", RouteId=short_uid(), Target=DEFAULT_TARGET),
            Route(RouteKey="$default", RouteId=short_uid(), Target=DEFAULT_TARGET),
            Route(RouteKey="GET /pets/dog/{id}", RouteId=short_uid(), Target=DEFAULT_TARGET),
        ]
        # test that $default is the last matched, in this case, it should never be matched at all

        for route in routes:
            dummy_deployment.http_api.routes[route["RouteId"]] = route

        return dummy_deployment

    @pytest.fixture
    def deployment_with_any_routes_order(self, dummy_deployment):
        """
        - GET /{proxy+}
        - POST /{proxy+}
        - ANY /{proxy+}
        """
        routes = [
            Route(RouteKey="ANY /{proxy+}", RouteId=short_uid(), Target=DEFAULT_TARGET),
            Route(RouteKey="POST /{proxy+}", RouteId=short_uid(), Target=DEFAULT_TARGET),
            Route(RouteKey="GET /{proxy+}", RouteId=short_uid(), Target=DEFAULT_TARGET),
        ]
        # test that ANY is the last matched, defined method should be returned first

        for route in routes:
            dummy_deployment.http_api.routes[route["RouteId"]] = route

        return dummy_deployment

    @pytest.fixture
    def deployment_with_greedy_routes_and_default(self, dummy_deployment):
        routes = [
            Route(RouteKey="$default", RouteId=short_uid(), Target=DEFAULT_TARGET),
            Route(RouteKey="POST /{proxy+}", RouteId=short_uid(), Target=DEFAULT_TARGET),
        ]
        # test that $default is the last matched, even with a greedy route

        for route in routes:
            dummy_deployment.http_api.routes[route["RouteId"]] = route

        return dummy_deployment

    @staticmethod
    def get_path_from_addressing(path: str, addressing: str) -> str:
        if addressing == "host":
            return f"/{TEST_API_STAGE}{path}"
        else:
            return f"/restapis/{TEST_API_ID}/{TEST_API_STAGE}/_user_request_/{path}"

    @pytest.mark.parametrize("addressing", ["host", "user_request"])
    def test_route_request_no_param(
        self, deployment_with_routes, parse_handler_chain, get_invocation_context, addressing
    ):
        request = Request(
            "GET",
            path=self.get_path_from_addressing("/foo", addressing),
        )

        context = get_invocation_context(request)
        context.deployment = deployment_with_routes

        parse_handler_chain.handle(context, Response())

        handler = HttpInvocationRequestRouter()
        handler(parse_handler_chain, context, Response())

        assert context.route["RouteKey"] == "GET /foo"

        assert context.integration["IntegrationId"] == "test"
        assert context.invocation_request["path_parameters"] == {}
        assert context.stage_variables == {"foo": "bar"}
        assert context.context_variables["routeKey"] == "GET /foo"

    @pytest.mark.parametrize("addressing", ["host", "user_request"])
    def test_route_request_with_path_parameter(
        self, deployment_with_routes, parse_handler_chain, get_invocation_context, addressing
    ):
        request = Request(
            "PUT",
            path=self.get_path_from_addressing("/foo/random-value", addressing),
        )

        context = get_invocation_context(request)
        context.deployment = deployment_with_routes

        parse_handler_chain.handle(context, Response())

        handler = HttpInvocationRequestRouter()
        handler(parse_handler_chain, context, Response())

        assert context.route["RouteKey"] == "PUT /foo/{param}"

        assert context.integration["IntegrationId"] == "test"

        assert context.invocation_request["path_parameters"] == {"param": "random-value"}
        assert context.context_variables["routeKey"] == "PUT /foo/{param}"

        with pytest.raises(NotFoundError):
            request = Request(
                "GET",
                path=self.get_path_from_addressing("/foo/random-value", addressing),
            )
            context = get_invocation_context(request)
            context.deployment = deployment_with_routes

            parse_handler_chain.handle(context, Response())

            handler = HttpInvocationRequestRouter()
            handler(parse_handler_chain, context, Response())

    @pytest.mark.parametrize("addressing", ["host", "user_request"])
    def test_route_request_with_greedy_parameter(
        self, deployment_with_routes, parse_handler_chain, get_invocation_context, addressing
    ):
        # assert that a path which does not contain `/proxy/bar` will be routed to {proxy+}
        request = Request(
            "DELETE",
            path=self.get_path_from_addressing("/proxy/this/is/a/proxy/req2%Fuest", addressing),
        )
        router_handler = HttpInvocationRequestRouter()

        context = get_invocation_context(request)
        context.deployment = deployment_with_routes

        parse_handler_chain.handle(context, Response())
        router_handler(parse_handler_chain, context, Response())

        assert context.route["RouteKey"] == "DELETE /proxy/{proxy+}"
        assert context.invocation_request["path_parameters"] == {
            "proxy": "this/is/a/proxy/req2%Fuest"
        }
        assert context.context_variables["routeKey"] == "DELETE /proxy/{proxy+}"

        # assert that a path which does contain `/proxy/bar` will be routed to `/proxy/bar/{param}` if it has only
        # one resource after `bar`
        request = Request(
            "DELETE",
            path=self.get_path_from_addressing("/proxy/bar/foobar", addressing),
        )
        context = get_invocation_context(request)
        context.deployment = deployment_with_routes

        parse_handler_chain.handle(context, Response())
        router_handler(parse_handler_chain, context, Response())

        assert context.route["RouteKey"] == "DELETE /proxy/bar/{param}"
        assert context.invocation_request["path_parameters"] == {"param": "foobar"}

        # assert that a path which contains more than one param after `/proxy/bar` will be routed to {proxy+} as it
        # does not conform to `/proxy/bar/{param}`
        request = Request(
            "DELETE",
            path=self.get_path_from_addressing("/proxy/bar/extra/param", addressing),
        )
        context = get_invocation_context(request)
        context.deployment = deployment_with_routes

        parse_handler_chain.handle(context, Response())
        router_handler(parse_handler_chain, context, Response())

        assert context.route["RouteKey"] == "DELETE /proxy/{proxy+}"
        assert context.invocation_request["path_parameters"] == {"proxy": "bar/extra/param"}

    @pytest.mark.parametrize("addressing", ["host", "user_request"])
    def test_route_request_no_match_on_path(
        self, deployment_with_routes, parse_handler_chain, get_invocation_context, addressing
    ):
        request = Request(
            "GET",
            path=self.get_path_from_addressing("/wrong-test", addressing),
        )

        context = get_invocation_context(request)
        context.deployment = deployment_with_routes

        parse_handler_chain.handle(context, Response())
        # manually invoking the handler here as exceptions would be swallowed by the chain
        handler = HttpInvocationRequestRouter()
        with pytest.raises(NotFoundError):
            handler(parse_handler_chain, context, Response())

    @pytest.mark.parametrize("addressing", ["host", "user_request"])
    def test_route_request_no_match_on_method(
        self, deployment_with_routes, parse_handler_chain, get_invocation_context, addressing
    ):
        request = Request(
            "POST",
            path=self.get_path_from_addressing("/test", addressing),
        )

        context = get_invocation_context(request)
        context.deployment = deployment_with_routes

        parse_handler_chain.handle(context, Response())
        # manually invoking the handler here as exceptions would be swallowed by the chain
        handler = HttpInvocationRequestRouter()
        with pytest.raises(NotFoundError):
            handler(parse_handler_chain, context, Response())

    @pytest.mark.parametrize("addressing", ["host", "user_request"])
    def test_route_request_no_target_on_route(
        self, deployment_with_routes, parse_handler_chain, get_invocation_context, addressing
    ):
        request = Request(
            "GET",
            path=self.get_path_from_addressing("/foo/no-integration", addressing),
        )

        context = get_invocation_context(request)
        context.deployment = deployment_with_routes

        parse_handler_chain.handle(context, Response())
        # manually invoking the handler here as exceptions would be swallowed by the chain
        handler = HttpInvocationRequestRouter()
        with pytest.raises(NotFoundError):
            handler(parse_handler_chain, context, Response())

    @pytest.mark.parametrize("addressing", ["host", "user_request"])
    def test_route_request_with_double_slash_and_trailing_and_encoded(
        self, deployment_with_routes, parse_handler_chain, get_invocation_context, addressing
    ):
        request = Request(
            "PUT",
            path=self.get_path_from_addressing("/foo/foo%2Fbar/", addressing),
            raw_path=self.get_path_from_addressing("//foo/foo%2Fbar/", addressing),
        )

        context = get_invocation_context(request)
        context.deployment = deployment_with_routes

        parse_handler_chain.handle(context, Response())
        handler = HttpInvocationRequestRouter()
        handler(parse_handler_chain, context, Response())
        assert context.route["RouteKey"] == "PUT /foo/{param}"
        assert context.invocation_request["path_parameters"] == {"param": "foo%2Fbar"}

    @pytest.mark.parametrize("addressing", ["host", "user_request"])
    def test_route_request_with_any(
        self,
        deployment_with_any_routes_and_default,
        parse_handler_chain,
        get_invocation_context,
        addressing,
    ):
        """
        See https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-develop-routes.html#http-api-develop-routes.evaluation
        """

        handler = HttpInvocationRequestRouter()

        def handle(_request: Request) -> HttpApiInvocationContext:
            _context = get_invocation_context(_request)
            _context.deployment = deployment_with_any_routes_and_default
            parse_handler_chain.handle(_context, Response())
            handler(parse_handler_chain, _context, Response())
            return _context

        request = Request(
            "GET",
            path=self.get_path_from_addressing("/pets/dog/1", addressing),
        )
        context = handle(request)
        # The request fully matches this static route.
        assert context.route["RouteKey"] == "GET /pets/dog/1"

        request = Request(
            "GET",
            path=self.get_path_from_addressing("/pets/dog/2", addressing),
        )
        context = handle(request)
        # The request fully matches this route.
        assert context.route["RouteKey"] == "GET /pets/dog/{id}"

        request = Request(
            "GET",
            path=self.get_path_from_addressing("/pets/cat/1", addressing),
        )

        context = handle(request)
        # The request doesn't fully match a route. The route with a GET method and a greedy path variable catches
        # this request.
        assert context.route["RouteKey"] == "GET /pets/{proxy+}"

        request = Request(
            "GET",
            path=self.get_path_from_addressing("/test/5", addressing),
        )

        context = handle(request)
        # The ANY method matches all methods that you haven't defined for a route. Routes with greedy path variables
        # have higher priority than the $default route.
        assert context.route["RouteKey"] == "ANY /{proxy+}"

    @pytest.mark.parametrize("addressing", ["host", "user_request"])
    def test_route_request_with_any_is_last(
        self,
        deployment_with_any_routes_order,
        parse_handler_chain,
        get_invocation_context,
        addressing,
    ):
        handler = HttpInvocationRequestRouter()

        def handle(_request: Request) -> HttpApiInvocationContext:
            _context = get_invocation_context(_request)
            _context.deployment = deployment_with_any_routes_order
            parse_handler_chain.handle(_context, Response())
            handler(parse_handler_chain, _context, Response())
            return _context

        request = Request(
            "GET",
            path=self.get_path_from_addressing("/test", addressing),
        )
        context = handle(request)
        assert context.route["RouteKey"] == "GET /{proxy+}"

        request = Request(
            "GET",
            path=self.get_path_from_addressing("/pets/dog/2", addressing),
        )
        context = handle(request)
        assert context.route["RouteKey"] == "GET /{proxy+}"

        request = Request(
            "POST",
            path=self.get_path_from_addressing("/pets", addressing),
        )

        context = handle(request)
        assert context.route["RouteKey"] == "POST /{proxy+}"

        request = Request(
            "DELETE",
            path=self.get_path_from_addressing("/test/5", addressing),
        )

        context = handle(request)
        assert context.route["RouteKey"] == "ANY /{proxy+}"

    @pytest.mark.parametrize("addressing", ["host", "user_request"])
    def test_route_request_default(
        self,
        deployment_with_greedy_routes_and_default,
        parse_handler_chain,
        get_invocation_context,
        addressing,
    ):
        handler = HttpInvocationRequestRouter()

        def handle(_request: Request) -> HttpApiInvocationContext:
            _context = get_invocation_context(_request)
            _context.deployment = deployment_with_greedy_routes_and_default
            parse_handler_chain.handle(_context, Response())
            handler(parse_handler_chain, _context, Response())
            return _context

        request = Request(
            "POST",
            path=self.get_path_from_addressing("/random-test", addressing),
        )
        context = handle(request)
        assert context.route["RouteKey"] == "POST /{proxy+}"

        request = Request(
            "GET",
            path=self.get_path_from_addressing("/random-test", addressing),
        )
        context = handle(request)
        assert context.route["RouteKey"] == "$default"

        request = Request(
            "GET",
            path=self.get_path_from_addressing("/pets/cat/1", addressing),
        )

        context = handle(request)
        assert context.route["RouteKey"] == "$default"
