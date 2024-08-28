import json
from typing import Any

import pytest
import requests
from localstack import config
from localstack.pro.core import config as ext_config
from localstack.testing.pytest import markers
from localstack.utils.strings import short_uid, to_str


@pytest.fixture(autouse=True)
def setup_soft_mode(monkeypatch):
    monkeypatch.setattr(ext_config, "IAM_SOFT_MODE", True)


@pytest.fixture(autouse=True)
def reset_summary(monkeypatch):
    response = requests.delete(f"{get_iam_endpoint()}/policies/summary")
    assert response.ok


def get_iam_endpoint():
    edge_url = config.internal_service_url()
    return f"{edge_url}/_aws/iam"


def count_statement_in_policy(target_statement: dict[str, Any], policy: dict[str, Any]) -> int:
    normalized_statements = [
        {k: v for k, v in statement.items() if k != "Sid"} for statement in policy["Statement"]
    ]
    return len([statement for statement in normalized_statements if statement == target_statement])


def is_statement_in_policy(target_statement: dict[str, Any], policy: dict[str, Any]) -> bool:
    return count_statement_in_policy(target_statement, policy) > 0


def verify_generated_policy_response(
    target_statement: dict[str, Any],
    generated_policy: bytes,
    target_resource: str,
    target_policy_type: str,
    service: str,
    operation: str,
    allowed: bool,
) -> bool:
    generated_policy = json.loads(to_str(generated_policy))
    request = generated_policy["request"]
    return (
        target_resource == generated_policy["resource"]
        and target_policy_type == generated_policy["policy_type"]
        and is_statement_in_policy(target_statement, generated_policy["policy_document"])
        and request["service"] == service
        and request["operation"] == operation
        and request["id"]
        and request["parameters"] is not None
        and request["allowed"] == allowed
    )


class TestPolicyGeneration:
    @markers.aws.only_localstack
    def test_policy_generation_stream(self, aws_client, account_id):
        """Basic test for policy stream. There is not much logic in there, basically just checks functionality"""
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
                    True,
                )
                for generated_policy in response.iter_lines()
                if generated_policy
            )

    @markers.aws.only_localstack
    def test_policy_generation_stream_as_role(
        self, aws_client, create_role, client_factory_for_role, account_id
    ):
        role_name = f"test-role-{short_uid()}"
        assume_role_trust_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "sts:AssumeRole",
                    "Principal": {"AWS": account_id},
                    "Effect": "Allow",
                }
            ],
        }
        role_arn = create_role(
            RoleName=role_name, AssumeRolePolicyDocument=json.dumps(assume_role_trust_policy)
        )["Role"]["Arn"]
        role_clients = client_factory_for_role(role_name=role_name, session_name="TestSession")

        target_statement = {"Effect": "Allow", "Action": "lambda:ListFunctions", "Resource": "*"}

        with requests.get(f"{get_iam_endpoint()}/policies/stream", stream=True) as response:
            role_clients.lambda_.list_functions()
            assert any(
                verify_generated_policy_response(
                    target_statement,
                    generated_policy,
                    role_arn,
                    "identity",
                    "lambda",
                    "ListFunctions",
                    False,
                )
                for generated_policy in response.iter_lines()
                if generated_policy
            )

    @markers.aws.only_localstack
    def test_policy_generation_summary(self, aws_client, account_id):
        """Check if the simple deduplication of entries works"""
        lambda_statement = {"Effect": "Allow", "Action": "lambda:ListFunctions", "Resource": "*"}
        sqs_statement = {"Effect": "Allow", "Action": "sqs:ListQueues", "Resource": "*"}
        target_resource = f"arn:aws:iam::{account_id}:root"
        with requests.get(
            f"{get_iam_endpoint()}/policies/summary?stream=1", stream=True
        ) as response:
            aws_client.sqs.list_queues()
            aws_client.sqs.list_queues()
            aws_client.lambda_.list_functions()
            for generated_policies in response.iter_lines():
                generated_policies = json.loads(to_str(generated_policies))
                root_generated_policies = [
                    policy for policy in generated_policies if policy["resource"] == target_resource
                ]
                if not root_generated_policies:
                    continue
                root_generated_policy = root_generated_policies[0]
                if is_statement_in_policy(
                    lambda_statement, root_generated_policy["policy_document"]
                ):
                    assert (
                        count_statement_in_policy(
                            sqs_statement, root_generated_policy["policy_document"]
                        )
                        == 1
                    )
                    return

    @markers.aws.only_localstack
    def test_policy_generation_reset(self, aws_client, account_id, cleanups):
        """Check if a summary reset works"""
        lambda_statement = {"Effect": "Allow", "Action": "lambda:ListFunctions", "Resource": "*"}
        sqs_statement = {"Effect": "Allow", "Action": "sqs:ListQueues", "Resource": "*"}
        target_resource = f"arn:aws:iam::{account_id}:root"
        with requests.get(f"{get_iam_endpoint()}/policies/summary", stream=True) as response:
            aws_client.lambda_.list_functions()
            iterator = response.iter_lines()
            for generated_policies in iterator:
                generated_policies = json.loads(to_str(generated_policies))
                root_generated_policies = [
                    policy for policy in generated_policies if policy["resource"] == target_resource
                ]
                if not root_generated_policies:
                    continue
                root_generated_policy = root_generated_policies[0]
                if is_statement_in_policy(
                    lambda_statement, root_generated_policy["policy_document"]
                ):
                    break
            response = requests.delete(f"{get_iam_endpoint()}/policies/summary")
            assert response.ok
            aws_client.sqs.list_queues()
            for generated_policies in iterator:
                generated_policies = json.loads(to_str(generated_policies))
                root_generated_policies = [
                    policy for policy in generated_policies if policy["resource"] == target_resource
                ]
                if not root_generated_policies:
                    continue
                root_generated_policy = root_generated_policies[0]
                if is_statement_in_policy(sqs_statement, root_generated_policy["policy_document"]):
                    assert not is_statement_in_policy(
                        lambda_statement, root_generated_policy["policy_document"]
                    )
                    return
