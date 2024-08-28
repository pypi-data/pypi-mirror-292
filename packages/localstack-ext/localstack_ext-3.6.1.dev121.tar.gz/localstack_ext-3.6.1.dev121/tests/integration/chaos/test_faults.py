import copy
import json
import urllib.parse

import botocore
import jsonschema
import pytest
import requests
from botocore.exceptions import ClientError
from localstack.config import external_service_url
from localstack.pro.core.chaos.constants import ENDPOINT_FAULT_CONFIG, SCHEMA_FAULT_CONFIG
from localstack.utils.aws.arns import sqs_queue_arn
from localstack.utils.strings import short_uid
from localstack.utils.sync import retry

EXPECTED_ERROR_MESSAGE = "Operation failed due to a simulated fault"


#
# Fixtures
#


@pytest.fixture()
def set_fault_config(fault_config_endpoint):
    """
    This fixture returns a factory that can be used to set fault config.
    """

    def _fault_config(
        new_config: dict, expected_status_code: int = 200, expected_response: dict = None
    ):
        response = requests.post(fault_config_endpoint, json=new_config)
        assert response.json() == (expected_response or new_config)
        assert response.status_code == expected_status_code

    yield _fault_config

    # Reset the config
    response = requests.post(fault_config_endpoint, json=[])
    assert response.status_code == 200


@pytest.fixture
def fault_config_endpoint() -> str:
    """
    This fixture returns the REST API endpoint for the chaos configuration module.
    """
    return urllib.parse.urljoin(external_service_url(protocol="http"), ENDPOINT_FAULT_CONFIG)


#
# Tests
#


class TestFaultConfigSchema:
    """
    Tests that validate JSON Schema for the configuration.
    """

    @pytest.mark.parametrize(
        "sample",
        [
            [{}],
            [{"region": "us-east-1"}],
            [{"region": "us-east-1"}, {"region": "ap-south-1"}],
            [{"region": "placeholder", "service": "s3"}],
            [{"region": "placeholder", "service": "acm-pca"}],
            [{"region": "placeholder", "service": "cognito_identity"}],
            [{"region": "placeholder", "service": "placeholder", "operation": "DoSomething"}],
            [{"region": "placeholder", "probability": 1}],
            [{"region": "placeholder", "probability": 1.0}],
            [{"region": "placeholder", "probability": 0.0}],
            [{"region": "placeholder", "error": {}}],
            [{"region": "placeholder", "error": {"statusCode": 400}}],
            [{"region": "placeholder", "error": {"statusCode": 400, "code": "BrainFry"}}],
            [{"description": "An empty rule that causes a global outage"}],
        ],
    )
    def test_valid_schema(self, sample):
        jsonschema.validate(sample, SCHEMA_FAULT_CONFIG)

    @pytest.mark.parametrize(
        "sample,error",
        [
            (
                [{"region": "s3", "foo": "bar"}],
                "Additional properties are not allowed ('foo' was unexpected)",
            ),
            ([{"region": "us*"}], "'us*' does not match"),
            ([{"region": ""}], "'' does not match"),
            (
                [{"region": "placeholder", "operation": "Put42Items"}],
                "'Put42Items' does not match",
            ),
            (
                [{"region": "placeholder", "probability": 1.1}],
                "1.1 is greater than the maximum of 1",
            ),
            (
                [{"region": "placeholder", "error": {"blah": 814}}],
                "Additional properties are not allowed ('blah' was unexpected)",
            ),
            (
                [{"region": "placeholder", "error": {"statusCode": 300}}],
                "300 is less than the minimum of 400",
            ),
            ([{"region": "placeholder", "error": {"code": ""}}], "'' does not match"),
        ],
    )
    def test_invalid_schema(self, sample, error):
        with pytest.raises(jsonschema.exceptions.ValidationError) as exc:
            jsonschema.validate(sample, SCHEMA_FAULT_CONFIG)
        assert error in str(exc)


class TestFaults:
    """
    Tests for fault simulation.
    """

    def test_fault_everywhere(self, aws_client_factory, set_fault_config):
        """Ensure that an empty rule causes faults for all operations in all services in all regions."""
        set_fault_config(new_config=[{}])

        for region_name in [
            "us-east-1",
            "us-east-2",
            "us-west-1",
            "us-west-2",
            "ap-east-1",
            "ap-south-1",
            "eu-west-1",
            "eu-central-1",
            "eu-central-1",
        ]:
            factory = aws_client_factory(
                region_name=region_name,
                config=botocore.config.Config(retries={"total_max_attempts": 1}),
            )

            for service, operation in [
                ("sns", "list_topics"),
                ("sqs", "list_queues"),
                ("s3", "list_buckets"),
                ("ec2", "describe_instances"),
                ("dynamodb", "list_tables"),
                ("lambda", "list_functions"),
            ]:
                client = factory.get_client(service)
                with pytest.raises(ClientError) as exc:
                    getattr(client, operation)()
                assert exc.value.response["Error"]["Code"] == "ServiceUnavailable"
                assert exc.value.response["ResponseMetadata"]["HTTPStatusCode"] == 503
                assert exc.value.response["Error"]["Message"] == EXPECTED_ERROR_MESSAGE

    def test_fault_all_services_in_region(self, aws_client_factory, set_fault_config):
        set_fault_config(
            new_config=[{"region": "eu-west-1"}],
            expected_status_code=200,
        )

        factory = aws_client_factory(region_name="eu-west-1")

        with pytest.raises(ClientError) as exc:
            factory.kms.create_key()
        assert exc.value.response["Error"]["Code"] == "ServiceUnavailable"
        assert exc.value.response["ResponseMetadata"]["HTTPStatusCode"] == 503
        assert exc.value.response["Error"]["Message"] == EXPECTED_ERROR_MESSAGE

        with pytest.raises(ClientError) as exc:
            factory.ec2.describe_regions()
        assert exc.value.response["Error"]["Code"] == "ServiceUnavailable"
        assert exc.value.response["ResponseMetadata"]["HTTPStatusCode"] == 503
        assert exc.value.response["Error"]["Message"] == EXPECTED_ERROR_MESSAGE

        with pytest.raises(ClientError) as exc:
            factory.s3.list_buckets()
        assert exc.value.response["Error"]["Code"] == "ServiceUnavailable"
        assert exc.value.response["ResponseMetadata"]["HTTPStatusCode"] == 503
        assert exc.value.response["Error"]["Message"] == EXPECTED_ERROR_MESSAGE

        # Ensure other regions isn't affected
        for region in [
            "us-east-1",
            "us-east-2",
            "us-west-1",
            "us-west-2",
            "ap-south-1",
            "eu-central-1",
        ]:
            factory = aws_client_factory(region_name=region)
            response = factory.s3.list_buckets()
            assert response["ResponseMetadata"]["HTTPStatusCode"] == 200
            response = factory.kms.list_keys()
            assert response["ResponseMetadata"]["HTTPStatusCode"] == 200
            response = factory.ec2.describe_regions()
            assert response["ResponseMetadata"]["HTTPStatusCode"] == 200

    def test_fault_specific_services_in_regions(self, aws_client_factory, set_fault_config):
        set_fault_config(
            new_config=[
                {"region": "us-west-1", "service": "kms"},
                {"region": "eu-west-1", "service": "kms"},
                {"region": "ap-south-1", "service": "s3"},
            ],
            expected_status_code=200,
        )

        # Ensure KMS is unreachable in particular regions
        for region in ["us-west-1", "eu-west-1"]:
            factory = aws_client_factory(region_name=region)

            with pytest.raises(ClientError) as exc:
                factory.kms.create_key()

            assert exc.value.response["Error"]["Code"] == "ServiceUnavailable"
            assert exc.value.response["ResponseMetadata"]["HTTPStatusCode"] == 503
            assert exc.value.response["Error"]["Message"] == EXPECTED_ERROR_MESSAGE

            # Ensure other services aren't affected
            response = factory.s3.list_buckets()
            assert response["ResponseMetadata"]["HTTPStatusCode"] == 200

        # And S3 in unreachable in one region
        s3_client = aws_client_factory(region_name="ap-south-1").s3
        with pytest.raises(ClientError) as exc:
            s3_client.list_buckets()

        assert exc.value.response["Error"]["Code"] == "ServiceUnavailable"
        assert exc.value.response["ResponseMetadata"]["HTTPStatusCode"] == 503
        assert exc.value.response["Error"]["Message"] == EXPECTED_ERROR_MESSAGE

    def test_fault_for_specific_operations(self, aws_client, region_name, set_fault_config):
        set_fault_config(
            new_config=[
                {"region": region_name, "service": "appconfig", "operation": "ListEnvironments"},
            ],
        )

        with pytest.raises(ClientError) as exc:
            aws_client.appconfig.list_environments(ApplicationId="placeholder")
        assert exc.value.response["Error"]["Code"] == "ServiceUnavailable"
        assert exc.value.response["ResponseMetadata"]["HTTPStatusCode"] == 503
        assert exc.value.response["Error"]["Message"] == EXPECTED_ERROR_MESSAGE

        # Ensure other AppConfig operations aren't affected
        assert aws_client.appconfig.list_applications()["ResponseMetadata"]["HTTPStatusCode"] == 200
        assert (
            aws_client.appconfig.list_deployment_strategies()["ResponseMetadata"]["HTTPStatusCode"]
            == 200
        )

        # Ensure other operations with same name aren't affected
        assert aws_client.mwaa.list_environments()["ResponseMetadata"]["HTTPStatusCode"] == 200

    @pytest.mark.parametrize("probability", [0.1, 0.5, 0.9])
    def test_fault_probability(
        self, aws_client_factory, region_name, set_fault_config, probability
    ):
        tolerated_delta = 0.15
        sample_size = 50

        set_fault_config(
            [
                {
                    "region": region_name,
                    "service": "ses",
                    "operation": "ListTemplates",
                    "probability": probability,
                }
            ]
        )

        ses_client = aws_client_factory(
            config=botocore.config.Config(
                retries={"total_max_attempts": 1},
            )
        ).ses

        sample_set = []

        # Try monte-carlo sampling
        for idx in range(sample_size):
            try:
                ses_client.list_templates()
            except ClientError as exc:
                sample_set.append(1)
                assert exc.response["Error"]["Code"] == "ServiceUnavailable"
                assert exc.response["Error"]["Message"] == EXPECTED_ERROR_MESSAGE
            else:
                sample_set.append(0)

        assert sample_size == len(sample_set)
        assert (
            probability - tolerated_delta
            < sum(sample_set) / len(sample_set)
            < probability + tolerated_delta
        )

    def test_fault_custom_error(self, aws_client, region_name, set_fault_config):
        expected_code = "TeaPotError"
        expected_status_code = 450

        set_fault_config(
            [
                {
                    "region": region_name,
                    "service": "mwaa",
                    "operation": "ListEnvironments",
                    "error": {"statusCode": expected_status_code, "code": expected_code},
                }
            ]
        )

        with pytest.raises(ClientError) as exc:
            aws_client.mwaa.list_environments()
        assert exc.value.response["Error"]["Code"] == expected_code
        assert exc.value.response["ResponseMetadata"]["HTTPStatusCode"] == expected_status_code

    def test_fault_cross_service_calls(
        self, aws_client, cleanups, account_id, region_name, set_fault_config
    ):
        """Ensure that faults also affect cross-service calls"""

        # Create SNS topic
        topic_name = f"topic-{short_uid()}"
        topic_arn = aws_client.sns.create_topic(Name=topic_name)["TopicArn"]
        cleanups.append(lambda: aws_client.sns.delete_topic(TopicArn=topic_arn))

        # Create SQS queue
        queue_name = f"queue-{short_uid()}"
        queue_url = aws_client.sqs.create_queue(QueueName=queue_name)["QueueUrl"]
        cleanups.append(lambda: aws_client.sqs.delete_queue(QueueUrl=queue_url))

        # Make SNS topic subscribe to SQS queue
        subscription_arn = aws_client.sns.subscribe(
            TopicArn=topic_arn,
            Protocol="sqs",
            Endpoint=sqs_queue_arn(queue_name, account_id, region_name),
        )["SubscriptionArn"]
        cleanups.append(lambda: aws_client.sns.unsubscribe(SubscriptionArn=subscription_arn))

        # Make sure the setup works by publishing a message to the SNS topic. This should be forwarded to SQS.
        aws_client.sns.publish(TopicArn=topic_arn, Message="hello")

        def _assert_sqs_receive(_message: str):
            response = aws_client.sqs.receive_message(QueueUrl=queue_url)
            assert "Messages" in response
            assert len(response["Messages"]) == 1
            body = json.loads(response["Messages"][0]["Body"])
            assert body["Message"] == _message

        # SNS shouldn't be able to talk to SQS due to the outage
        retry(lambda: _assert_sqs_receive("hello"), retries=3, sleep=1, sleep_before=1)

        # Start an outage for SQS:SendMessage
        set_fault_config(
            [
                {
                    "region": region_name,
                    "service": "sqs",
                    "operation": "SendMessage",
                }
            ]
        )

        # This should prevent SNS from forwarding messages to SQS
        aws_client.sns.publish(TopicArn=topic_arn, Message="world")
        with pytest.raises(AssertionError):
            retry(lambda: _assert_sqs_receive("world"), retries=3, sleep=1, sleep_before=1)


class TestFaultApi:
    """
    Tests for fault configuration API.
    """

    @staticmethod
    def _get_and_assert_config(
        fault_config_endpoint: str, expected_status_code: int, expected_config: dict
    ) -> None:
        response = requests.get(fault_config_endpoint)
        assert response.json() == expected_config
        assert response.status_code == expected_status_code

    @pytest.mark.parametrize(
        "config",
        [
            ([{"service": "sns", "region": "us-east-1", "invalid-key": "invalid-value"}]),
            ([{"operation": ""}]),
            ([{"service": ""}]),
            ([{"region": ""}]),
            ([{"invalid-key": ""}]),
            ([{"": ""}]),
        ],
    )
    def test_fault_invalid_fetch_update_config(
        self, fault_config_endpoint, config, set_fault_config
    ):
        with pytest.raises(jsonschema.exceptions.ValidationError) as exec:
            jsonschema.validate(config, SCHEMA_FAULT_CONFIG)
        error_message = {"message": f"Error validating JSON schema: {exec.value.message}"}

        set_fault_config(
            new_config=config, expected_status_code=400, expected_response=error_message
        )

        response = requests.patch(fault_config_endpoint, json=config)
        assert response.status_code == 400
        assert response.json() == error_message

        response = requests.delete(fault_config_endpoint, json=config)
        assert response.status_code == 400
        assert response.json() == error_message

        self._get_and_assert_config(fault_config_endpoint, 200, [])

    def test_fault_config_crud(self, fault_config_endpoint):
        """
        Test configuration via HTTP methods.
        """
        # create config
        initial_config = [
            {
                "region": "ap-south-1",
                "service": "redshift",
                "description": "This causes redshift to fail in ap-south-1 region",
            }
        ]
        response = requests.post(fault_config_endpoint, json=initial_config)
        assert response.status_code == 200
        self._get_and_assert_config(fault_config_endpoint, 200, initial_config)

        config = [{"region": "us-east-1", "service": "kms"}]
        invalid_config = copy.deepcopy(config)
        invalid_config[0]["invalid-key"] = "invalid-value"

        # overwrite the config
        response = requests.post(fault_config_endpoint, json=config)
        assert response.status_code == 200
        self._get_and_assert_config(fault_config_endpoint, 200, config)

        # add a new config rule with PATCH
        patch_config = [{"service": "kms", "region": "us-east-2"}]
        response = requests.patch(fault_config_endpoint, json=patch_config)
        assert response.status_code == 200
        self._get_and_assert_config(fault_config_endpoint, 200, config + patch_config)

        # add a bad config rule with PATCH
        response = requests.patch(fault_config_endpoint, json=invalid_config)
        assert response.status_code == 400
        with pytest.raises(jsonschema.exceptions.ValidationError) as exec:
            jsonschema.validate(invalid_config, SCHEMA_FAULT_CONFIG)
        assert response.json() == {"message": f"Error validating JSON schema: {exec.value.message}"}

        # delete a rule with DELETE
        response = requests.delete(fault_config_endpoint, json=patch_config)
        assert response.status_code == 200
        self._get_and_assert_config(fault_config_endpoint, 200, config)

        # delete a non-existent rule with DELETE
        response = requests.delete(fault_config_endpoint, json=invalid_config)
        assert response.status_code == 400
        with pytest.raises(jsonschema.exceptions.ValidationError) as exec:
            jsonschema.validate(invalid_config, SCHEMA_FAULT_CONFIG)
        assert response.json() == {"message": f"Error validating JSON schema: {exec.value.message}"}

        self._get_and_assert_config(fault_config_endpoint, 200, config)

        # clear the config
        response = requests.post(fault_config_endpoint, json=[])
        self._get_and_assert_config(fault_config_endpoint, 200, [])
