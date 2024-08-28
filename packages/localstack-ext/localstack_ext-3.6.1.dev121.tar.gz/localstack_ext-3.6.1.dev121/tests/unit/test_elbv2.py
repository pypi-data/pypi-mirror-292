import pytest
from localstack.pro.core.services.elb.routing import load_balancer_id, translate_url
from localstack.pro.core.services.elbv2.provider import apply_moto_patches
from localstack.pro.core.utils.aws.arns import elb_listener_arn, elb_loadbalancer_arn
from localstack.testing.config import TEST_AWS_ACCOUNT_ID, TEST_AWS_REGION_NAME
from moto.elbv2 import models as elbv2_models
from moto.elbv2 import utils as elbv2_utils


def test_extract_load_balancer_id():
    assert (
        load_balancer_id(
            elb_listener_arn("my-lb", "lb123", "list123", TEST_AWS_ACCOUNT_ID, TEST_AWS_REGION_NAME)
        )
        == "lb123"
    )
    assert (
        load_balancer_id(
            elb_loadbalancer_arn("my-lb", "lb123", TEST_AWS_ACCOUNT_ID, TEST_AWS_REGION_NAME)
        )
        == "lb123"
    )
    assert load_balancer_id("lb123") == "lb123"


def test_unique_load_balancer_arn():
    apply_moto_patches()

    # note: if this assertion starts failing, it means that we can remove our patch in elb/provider.py!
    arn1 = elbv2_utils.make_arn_for_load_balancer(
        account_id="000000", name="lb1", region_name="us-east-1"
    )
    arn2 = elbv2_utils.make_arn_for_load_balancer(
        account_id="000000", name="lb1", region_name="us-east-1"
    )
    assert arn1 == arn2

    arn1 = elbv2_models.make_arn_for_load_balancer(
        account_id="000000", name="lb1", region_name="us-east-1"
    )
    arn2 = elbv2_models.make_arn_for_load_balancer(
        account_id="000000", name="lb1", region_name="us-east-1"
    )
    assert arn1 != arn2


@pytest.mark.parametrize(
    "input,mapping,expected",
    [
        # single changes
        ("http://example.com:5000/foo", {}, "http://example.com:5000/foo"),
        ("http://example.com:5000/foo", {"Port": 8000}, "http://example.com:8000/foo"),
        ("http://example.com:5000/foo", {"Host": "foo.bar"}, "http://foo.bar:5000/foo"),
        ("http://example.com:5000/foo", {"Protocol": "https"}, "https://example.com:5000/foo"),
        ("http://example.com:5000/foo", {"Path": "/bar"}, "http://example.com:5000/bar"),
        ("http://example.com:5000/foo", {"Query": "test"}, "http://example.com:5000/foo?test"),
        # multiple changes
        (
            "http://example.com:5000/foo",
            {"Port": 8000, "Host": "foo.bar"},
            "http://foo.bar:8000/foo",
        ),
        (
            "http://example.com:5000/foo",
            {"Port": 8000, "Host": "foo.bar", "Protocol": "https", "Path": "/bar", "Query": "test"},
            "https://foo.bar:8000/bar?test",
        ),
    ],
    ids=[
        "no-input",
        "change-port",
        "change-host",
        "change-scheme",
        "change-path",
        "change-query",
        "change-port-and-host",
        "change-all",
    ],
)
def test_translate_url(input: str, mapping: dict, expected: str):
    assert translate_url(input, mapping) == expected
