from typing import Dict, List, Optional
from urllib.parse import parse_qs

from localstack.pro.core.services.apigateway.apigateway_utils import (
    RestApiBasePathMapping,
    V1V2CasingDict,
    render_template,
)
from localstack.pro.core.services.apigateway.integrations import (
    IntegrationDirection,
    apply_route_param_to_message,
)
from localstack.services.apigateway.context import ApiInvocationContext
from localstack.utils.collections import select_attributes
from localstack.utils.json import clone
from requests.structures import CaseInsensitiveDict


def initialize_context_for_base_path_mappings(
    invocation_context: ApiInvocationContext, mappings: List[Dict]
) -> Optional[ApiInvocationContext]:
    """Small helper method to apply base path mapping to a list of mapping objects"""
    api_mapping = RestApiBasePathMapping(invocation_context)
    for mapping in mappings:
        if not api_mapping.is_invocation_matching(mapping):
            continue
        api_mapping.initialize_context(mapping)
        return invocation_context


def test_apply_route_params():
    def _apply_params(from_path, to_path, route_context):
        return apply_route_param_to_message(
            {}, from_path, to_path, clone(route_context), IntegrationDirection.REQUEST
        )

    from_path = "route.request.querystring.q1"
    to_path = "integration.request.header.authToken"
    route_context = {"route": {"request": {"querystring": {"q1": "abc"}}}}
    message = _apply_params(from_path, to_path, route_context)
    assert message == {"headers": {"authToken": "abc"}}

    def _assert_headers(message, headers):
        assert CaseInsensitiveDict(message["headers"]) == CaseInsensitiveDict(headers)

    # test request params on headers
    from_path = "value1"
    route_context = {"route": {"request": {"header": {"x-api-key": "abc", "k1": "v1"}}}}
    to_path = "overwrite:header.X-Api-key"
    message = _apply_params(from_path, to_path, route_context)
    _assert_headers(message, {"x-api-key": "value1", "k1": "v1"})
    to_path = "remove:header.X-ApI-keY"  # should work case-insensitively
    message = _apply_params(from_path, to_path, route_context)
    _assert_headers(message, {"k1": "v1"})
    to_path = "append:header.X-Api-key"
    message = _apply_params(from_path, to_path, route_context)
    _assert_headers(message, {"x-api-key": "abcvalue1", "k1": "v1"})

    # test request params on query strings
    from_path = "value1"
    route_context = {"route": {"request": {"querystring": "foo1=bar1&foo2=bar2"}}}
    to_path = "overwrite:querystring.foo1"
    message = _apply_params(from_path, to_path, route_context)
    assert parse_qs(message["querystring"]) == {"foo1": ["value1"], "foo2": ["bar2"]}
    to_path = "remove:querystring.foo1"  # should work case-insensitively
    message = _apply_params(from_path, to_path, route_context)
    assert parse_qs(message["querystring"]) == {"foo2": ["bar2"]}
    to_path = "append:querystring.foo2"
    message = _apply_params(from_path, to_path, route_context)
    assert parse_qs(message["querystring"]) == {"foo1": ["bar1"], "foo2": ["bar2value1"]}

    # test request params on path
    from_path = "/value1"
    route_context = {"route": {"request": {"path": "/test"}}}
    to_path = "overwrite:path"
    message = _apply_params(from_path, to_path, route_context)
    assert select_attributes(message, ["path"]) == {"path": "/value1"}


def test_initialize_context_for_base_path_mapping():
    def _ctx(method="GET", path="/base/foo/bar", data="{}", host="test.example.com"):
        return ApiInvocationContext(method, path, data=data, headers={"Host": host})

    def _mapping(base_path="/base", stage="stage", api_id="api123"):
        return {"basePath": base_path, "stage": stage, "restApiId": api_id}

    def _mappings(base_path="/base", stage="stage", api_id="api123"):
        return [
            _mapping(f"{base_path}{i}", stage if stage == "(none)" else f"{stage}{i}", api_id)
            for i in range(3)
        ]

    # matching base path mapping
    result = initialize_context_for_base_path_mappings(_ctx(path="/base/foo/bar"), [_mapping()])
    assert result.path_with_query_string == "/foo/bar"
    assert result.stage == "stage"

    # base path mapping with "(none)" stage (i.e., extracted from first path element)
    result = initialize_context_for_base_path_mappings(
        _ctx(path="/base/foo/bar"), [_mapping(stage="(none)")]
    )
    assert result.path_with_query_string == "/foo/bar"
    assert result.stage == "base"

    # matching path with multiple base path mappings
    for i in range(3):
        result = initialize_context_for_base_path_mappings(
            _ctx(path=f"/base{i}/foo/bar"), _mappings()
        )
        assert result.path_with_query_string == "/foo/bar"
        assert result.stage == f"stage{i}"
        result = initialize_context_for_base_path_mappings(
            _ctx(path=f"/base{i}/foo{i}"), _mappings(stage="(none)")
        )
        assert result.path_with_query_string == f"/foo{i}"
        assert result.stage == f"base{i}"

    # non-matching request with empty list of mappings
    assert not initialize_context_for_base_path_mappings(_ctx(), [])

    # non-matching combinations of paths / base paths
    assert not initialize_context_for_base_path_mappings(
        _ctx(path="/base-invalid/foo/bar"), [_mapping()]
    )
    assert not initialize_context_for_base_path_mappings(
        _ctx(path="/base/foo/bar"), [_mapping("/base-invalid")]
    )


def test_case_insensitive_dict():
    d = V1V2CasingDict({"k1": 1, "K2": 2, "authorizer": "test"})

    assert d["authorizer"]
    assert d["Authorizer"]
    assert d["authorizer"] == d["Authorizer"]

    for key in ["k1", "k2"]:
        upper = key.upper()
        lower = key.lower()
        assert upper in d
        assert lower in d
        assert d.get(upper)
        assert d.get(upper) == d.get(lower)


class TestTemplating:
    def test_headers(self):
        template = """
        $method.request.header.X-My-Header
        """
        variables = {"method": {"request": {"header": {"X-My-Header": "my-header-value"}}}}
        result = render_template(template, variables).strip()
        assert result == "my-header-value"
