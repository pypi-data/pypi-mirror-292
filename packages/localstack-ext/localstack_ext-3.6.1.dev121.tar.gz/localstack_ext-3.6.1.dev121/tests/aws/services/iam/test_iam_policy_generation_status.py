import pytest
import requests
from localstack.pro.core import config as ext_config
from localstack.testing.pytest import markers

from tests.aws.services.iam.test_iam_policy_generation import (
    get_iam_endpoint,
    verify_generated_policy_response,
)


@pytest.fixture(autouse=True)
def setup_soft_mode(monkeypatch):
    monkeypatch.setattr(ext_config, "ENFORCE_IAM", False)


def enable_generator():
    response = requests.post(f"{get_iam_endpoint()}/policies/enable")
    assert response.ok


def disable_generator():
    response = requests.post(f"{get_iam_endpoint()}/policies/disable")
    assert response.ok


class TestPolicyGenerationStatus:
    @markers.aws.only_localstack
    def test_policy_generation_config_endpoint(self):
        """Checks if the endpoint is returning the correct values"""
        with requests.get(f"{get_iam_endpoint()}/config") as response:
            assert response.ok
            response_result = response.json()
            assert response_result["policy_engine_enabled"] is False
            assert response_result["iam_soft_mode"] is False
            assert response_result["enforce_iam"] is False

    @markers.aws.only_localstack
    def test_policy_generation_enabled_by_config_enforce(self, monkeypatch):
        """Checks if the endpoint is returning the correct values when ENFORCE_IAM is set"""
        monkeypatch.setattr(ext_config, "ENFORCE_IAM", True)
        with requests.get(f"{get_iam_endpoint()}/config") as response:
            assert response.ok
            response_result = response.json()
            assert response_result["policy_engine_enabled"] is True
            assert response_result["iam_soft_mode"] is False
            assert response_result["enforce_iam"] is True

    @markers.aws.only_localstack
    def test_policy_generation_enabled_by_config_soft_mode(self, monkeypatch):
        """Checks if the endpoint is returning the correct values when IAM_SOFT_MODE is set"""
        monkeypatch.setattr(ext_config, "IAM_SOFT_MODE", True)
        with requests.get(f"{get_iam_endpoint()}/config") as response:
            assert response.ok
            response_result = response.json()
            assert response_result["policy_engine_enabled"] is True
            assert response_result["iam_soft_mode"] is True
            assert response_result["enforce_iam"] is False

    @markers.aws.only_localstack
    def test_policy_generation_enable_endpoint(self, aws_client, account_id):
        """Checks if the endpoint /enable enables the policy generation"""
        enable_generator()
        with requests.get(f"{get_iam_endpoint()}/config") as response:
            assert response.ok
            response_result = response.json()
            assert response_result["policy_engine_enabled"] is True

        target_statement = {"Effect": "Allow", "Action": "lambda:ListFunctions", "Resource": "*"}
        target_resource = f"arn:aws:iam::{account_id}:root"
        with requests.get(f"{get_iam_endpoint()}/policies/stream", stream=True) as response:
            aws_client.lambda_.list_functions()
            assert any(
                verify_generated_policy_response(
                    target_statement,
                    generated_policy,
                    target_resource,
                    "identity",
                    "lambda",
                    "ListFunctions",
                    allowed=True,
                )
                for generated_policy in response.iter_lines()
                if generated_policy
            )

    @markers.aws.only_localstack
    def test_policy_generation_disable_endpoint(self, aws_client):
        """Checks if the endpoint /disable disables the policy generation"""
        enable_generator()
        disable_generator()
        with requests.get(f"{get_iam_endpoint()}/config") as response:
            assert response.ok
            response_result = response.json()
            assert response_result["policy_engine_enabled"] is False

        try:
            with requests.get(
                f"{get_iam_endpoint()}/policies/stream", stream=True, timeout=3
            ) as response:
                aws_client.lambda_.list_functions()
                assert all(not generated_policy for generated_policy in response.iter_lines())
        except Exception as error:
            assert type(error) is requests.exceptions.ConnectionError
            assert "Read timed out" in str(error)
