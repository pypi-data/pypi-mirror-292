import time
import urllib

import jsonschema
import pytest
import requests
from localstack.config import external_service_url
from localstack.pro.core.chaos.constants import (
    ENDPOINT_NETWORK_EFFECT_CONFIG,
    SCHEMA_NETWORK_EFFECT_CONFIG,
)

#
# Fixtures
#


@pytest.fixture()
def set_network_effect_config(network_effect_config_endpoint):
    """
    This fixture returns a factory that can be used to set config.
    """

    def _set_config(
        new_config: dict | str, expected_status_code: int = 200, expected_response: dict = None
    ):
        if isinstance(new_config, dict):
            _response = requests.post(network_effect_config_endpoint, json=new_config)
        else:
            _response = requests.post(network_effect_config_endpoint, data=new_config)
        assert _response.status_code == expected_status_code
        assert _response.json() == (expected_response or new_config)

    yield _set_config

    # Reset the config
    response = requests.post(network_effect_config_endpoint, json={"latency": 0})
    assert response.status_code == 200


@pytest.fixture
def network_effect_config_endpoint() -> str:
    """
    This fixture returns the REST API endpoint for the chaos configuration module.
    """
    return urllib.parse.urljoin(
        external_service_url(protocol="http"), ENDPOINT_NETWORK_EFFECT_CONFIG
    )


#
# Tests
#


class TestNetworkEffectConfigSchema:
    @pytest.mark.parametrize(
        "sample",
        [
            {"latency": 0},
            {"latency": 1},
            {"latency": 5000},
        ],
    )
    def test_valid_schema(self, sample):
        jsonschema.validate(sample, SCHEMA_NETWORK_EFFECT_CONFIG)

    @pytest.mark.parametrize(
        "sample,expected_error",
        [
            ({"latency": "abcd"}, "'abcd' is not of type 'integer'"),
            ({"latency": -3}, "-3 is less than the minimum of 0"),
            ({"latency": 6.9}, "6.9 is not of type 'integer'"),
            (
                {"latency": 64, "jitter": 32},
                "Additional properties are not allowed ('jitter' was unexpected)",
            ),
        ],
    )
    def test_invalid_schema(self, sample, expected_error):
        with pytest.raises(jsonschema.exceptions.ValidationError) as exc:
            jsonschema.validate(sample, SCHEMA_NETWORK_EFFECT_CONFIG)
        assert expected_error in str(exc)


class TestNetworkEffects:
    @pytest.mark.parametrize("current_latency", [3_000, 500])
    def test_latency(self, aws_client, set_network_effect_config, current_latency):
        set_network_effect_config({"latency": current_latency})

        before = time.time() * 1_000
        aws_client.s3.list_buckets()
        after = time.time() * 1_000

        assert after - before >= current_latency


class TestNetworkEffectsApi:
    @pytest.mark.parametrize(
        "sample",
        [
            {"latency": 0},
            {"latency": 1},
            {"latency": 5000},
        ],
    )
    def test_valid_schema(self, set_network_effect_config, network_effect_config_endpoint, sample):
        set_network_effect_config(new_config=sample)

        # Ensure GET echos set config
        response = requests.get(network_effect_config_endpoint)
        assert response.status_code == 200
        assert response.json() == {"latency": sample["latency"]}

    @pytest.mark.parametrize(
        "sample,expected_error",
        [
            ({"latency": "abcd"}, "Error validating JSON schema: 'abcd' is not of type 'integer'"),
            ({"latency": -3}, "Error validating JSON schema: -3 is less than the minimum of 0"),
            ({"latency": 6.9}, "Error validating JSON schema: 6.9 is not of type 'integer'"),
            (
                {"latency": 64, "jitter": 32},
                "Error validating JSON schema: Additional properties are not allowed ('jitter' was unexpected)",
            ),
        ],
    )
    def test_invalid_schema(self, set_network_effect_config, sample, expected_error):
        set_network_effect_config(
            new_config=sample,
            expected_status_code=400,
            expected_response={"message": expected_error},
        )

    def test_bad_config(self, set_network_effect_config):
        set_network_effect_config(
            new_config="invalidJSON",
            expected_status_code=400,
            expected_response={
                "message": "Error decoding JSON: Expecting value: line 1 column 1 (char 0)"
            },
        )

    def test_get_default_config(self, network_effect_config_endpoint):
        response = requests.get(network_effect_config_endpoint)
        assert response.status_code == 200
        assert response.json() == {"latency": 0}
