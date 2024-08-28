import re

import pytest
from _pytest.python_api import raises
from localstack.constants import AWS_REGION_US_EAST_1
from localstack.pro.core.services.apigateway import apigateway_utils
from localstack.pro.core.services.apigateway.apigateway_utils import (
    UrlParts,
    V2Api,
    find_best_candidate,
    get_api_model,
)
from localstack.pro.core.services.apigateway.models import apigatewayv2_stores
from localstack.pro.core.services.apigateway.provider_v2 import resolve, resolve_ref
from localstack.services.apigateway.context import ApiGatewayVersion
from localstack.testing.config import TEST_AWS_ACCOUNT_ID
from localstack.utils.strings import short_uid
from moto.apigateway import models as apigw_models
from moto.apigateway.models import RestAPI


def test_url_parts():
    api1 = V2Api({})
    stage = {"stageName": "dev"}
    api1.stages[stage["stageName"]] = stage
    apigatewayv2_stores[TEST_AWS_ACCOUNT_ID][AWS_REGION_US_EAST_1].apis["b709aa22"] = api1

    api2 = V2Api({})
    apigatewayv2_stores[TEST_AWS_ACCOUNT_ID][AWS_REGION_US_EAST_1].apis["beef4242"] = api2

    tt = [
        {
            "url_part": UrlParts(
                method="GET",
                path="/dev/api?param=false",
                headers={"Host": "b709aa22.execute-api.localhost.localstack.cloud"},
            ),
            "expected": ("/api?param=false", "dev", "b709aa22"),
        },
        {
            "url_part": UrlParts(
                method="GET",
                path="/restapis/b709aa22/dev/_user_request_/api?param=false",
                headers={"Host": "localhost:4566"},
            ),
            "expected": ("/api?param=false", "dev", "b709aa22"),
        },
        {
            "url_part": UrlParts(
                method="GET",
                path="/dev/api?param=false",
                headers={"Host": "beef4242.execute-api.localhost.localstack.cloud"},
            ),
            "expected": ("/dev/api?param=false", None, "beef4242"),
        },
        {
            "url_part": UrlParts(
                method="GET",
                path="/restapis/beef4242/_user_request_/api?param=false",
                headers={"Host": "localhost:4566"},
            ),
            "expected": ("/api?param=false", None, "beef4242"),
        },
    ]

    for t in tt:
        assert t["url_part"].invocation_path == t["expected"][0]
        assert t["url_part"].stage == t["expected"][1]
        assert t["url_part"].api_id == t["expected"][2]


def test_resolve():
    tt = [
        {"data": 123, "expected": 123},
        {"data": {}, "expected": {}},
        {
            "data": {"some": {"nested": "data"}, "other": "stuff", "some_ref": {"$ref": "#/some"}},
            "expected": {"some_ref": {"nested": "data"}},
        },
        {
            "data": {"some": {"$ref": "#/other"}, "other": "stuff", "some_ref": {"$ref": "#/some"}},
            "expected": {"some": "stuff", "some_ref": "stuff"},
        },
        {
            "data": {"some": "data", "refs": ["item", {"$ref": "#/some"}]},
            "expected": {"refs": ["item", "data"]},
        },
    ]

    for t in tt:
        resolved = resolve(t["data"])
        if isinstance(resolved, dict):
            assert resolved == {**t["data"], **t["expected"]}
        else:
            assert resolved == t["expected"]


def test_resolve_ref_valid_path():
    data = {"something": "foo bar baz", "foo": {"bar": {"baz": {"$ref": "#/something"}}}}

    resolved = resolve_ref(data, "foo", "bar", "baz")
    assert resolved == "foo bar baz"


def test_resolve_ref_invalid_path():
    data = {"not_something": "foo bar baz", "foo": {"bar": {"baz": {"$ref": "#/something"}}}}

    with raises(ValueError):
        resolve_ref(data, "foo", "bar", "baz")


def test_custom_domain_regex():
    def _matches(host):
        return re.match(apigateway_utils.HOST_REGEX_CUSTOM_DOMAIN, host)

    for port in ["", ":4566"]:
        assert _matches(f"example.com{port}")
        assert _matches(f"test.example.com{port}")
        assert not _matches(f"apigateway.us-east-2.amazonaws.com{port}")
        assert not _matches(f"test.execute-api.us-east-2.amazonaws.com{port}")
        assert not _matches(f"test.execute-api.localhost.localstack.cloud{port}")
        assert not _matches(f"host.docker.internal{port}")
        assert not _matches(f"kubernetes.docker.internal{port}")


def test_find_best_candidate():
    tt = [
        {
            "method": "GET",
            "path": "/foo/bar",
            "resources": [("GET", "/foo/bar"), ("GET", "/foo/{proxy+}"), ("GET", "/{proxy+}")],
            "expected": ("GET", "/foo/bar"),
        },
        {
            "method": "POST",
            "path": "/foo/bar",
            "resources": [("POST", "/foo/{proxy+}"), ("POST", "/{proxy+}")],
            "expected": ("POST", "/foo/{proxy+}"),
        },
        {
            "method": "POST",
            "path": "/foo/bar",
            "resources": [("ANY", "/{proxy+}")],
            "expected": ("ANY", "/{proxy+}"),
        },
        {
            "method": "POST",
            "path": "/foo/bar",
            "resources": [("POST", "/{proxy+}"), ("ANY", "$default")],
            "expected": ("POST", "/{proxy+}"),
        },
        {
            "method": "GET",
            "path": "/foo/bar",
            "resources": [("ANY", "/foo/baz"), ("GET", "/foo/taz")],
            "expected": None,
        },
        {
            "method": "GET",
            "path": "/foo/bar",
            "resources": [("GET", "/foo/{id}"), ("GET", "/foo/{proxy+}")],
            "expected": ("GET", "/foo/{id}"),
        },
        {
            "method": "GET",
            "path": "/foo/bar",
            "resources": [("POST", "/foo/{id}"), ("GET", "/foo/{proxy+}")],
            "expected": ("GET", "/foo/{proxy+}"),
        },
        {
            "method": "GET",
            "path": "/foo/bar",
            "resources": [("POST", "/foo/{id}"), ("POST", "/foo/{proxy+}")],
            "expected": None,
        },
        {
            "method": "GET",
            "path": "/foo/bar",
            "resources": [("POST", "/foo/{id}"), ("ANY", "/foo/{proxy+}")],
            "expected": ("ANY", "/foo/{proxy+}"),
        },
        {
            "method": "GET",
            "path": "/foo/bar",
            "resources": [("ANY", "/{proxy+}")],
            "expected": ("ANY", "/{proxy+}"),
        },
        {
            "method": "GET",
            "path": "/foo/bar",
            "resources": [("GET", "/foo"), ("GET", "/id")],
            "expected": None,
        },
        {
            "method": "GET",
            "path": "/foo/bar",
            "resources": [("GET", "/{id}"), ("GET", "/{id}/{bar}")],
            "expected": ("GET", "/{id}/{bar}"),
        },
        {
            "method": "HEAD",
            "path": "/foo/bar/baz",
            "resources": [("HEAD", "/foo/{bar}/baz"), ("HEAD", "/{proxy+}")],
            "expected": ("HEAD", "/foo/{bar}/baz"),
        },
    ]

    for t in tt:
        assert find_best_candidate(t["method"], t["path"], t["resources"]) == t["expected"]


def test_lookup_api_entity_in_store(cleanups):
    def _add_api_to_store(api_id: str, region_name: str, apigw_version: ApiGatewayVersion):
        if apigw_version == ApiGatewayVersion.V1:
            store = apigw_models.apigateway_backends[TEST_AWS_ACCOUNT_ID][region_name]
            store.apis[api_id] = RestAPI(
                api_id,
                account_id=TEST_AWS_ACCOUNT_ID,
                region_name=region_name,
                name="test",
                description="test",
            )
            cleanups.append(lambda: store.apis.pop(api_id))
        elif apigw_version == ApiGatewayVersion.V2:
            store = apigatewayv2_stores[TEST_AWS_ACCOUNT_ID][region_name]
            store.apis[api_id] = V2Api({})
            cleanups.append(lambda: store.apis.pop(api_id))

    # create v1 API, assert that the model can be retrieved
    test_api_id = f"api-{short_uid()}"
    _add_api_to_store(test_api_id, "us-east-1", ApiGatewayVersion.V1)
    result = get_api_model(test_api_id, region_name="us-east-1")
    assert isinstance(result.api_object, RestAPI)
    result = get_api_model(test_api_id)
    assert isinstance(result.api_object, RestAPI)
    assert not get_api_model(test_api_id, region_name="eu-west-1")
    assert not get_api_model("invalid-id")

    # create v2 API, assert that the model can be retrieved
    test_api_id = f"api-{short_uid()}"
    _add_api_to_store(test_api_id, "us-east-1", ApiGatewayVersion.V2)
    result = get_api_model(test_api_id, region_name="us-east-1")
    assert isinstance(result.api_object, V2Api)
    result = get_api_model(test_api_id)
    assert isinstance(result.api_object, V2Api)
    assert not get_api_model(test_api_id, region_name="eu-west-1")
    assert not get_api_model("invalid-id")

    # create v1 API with the same ID, assert that an error is raised for duplicate IDs
    _add_api_to_store(test_api_id, "us-east-1", ApiGatewayVersion.V1)
    with pytest.raises(Exception) as exc:
        get_api_model(test_api_id)
    exc.match("Found multiple")
