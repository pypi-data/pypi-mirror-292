import pytest
from localstack import config
from localstack.testing.pytest import markers


@pytest.mark.whitebox
class TestLambdaCallingLocalstack:
    """=> Keep these tests synchronized with `test_lambda_common.py` in community!"""

    @markers.multiruntime(
        scenario="endpointinjection",
        # Transparent endpoint injection is only supported for specific runtimes
        # TODO: Fix ruby3.2 TEI because certificate disabling does not work
        runtimes=["java", "nodejs", "python"],
    )
    @markers.lambda_runtime_update
    @markers.aws.validated
    def test_transparent_endpoint_injection(
        self, multiruntime_lambda, tmp_path, aws_client, monkeypatch
    ):
        """Test calling SQS from Lambda using transparent endpoint injection.
        This is only supported for a subset of runtimes in LocalStack Pro when using the DNS server.
        Run this test in Docker or with root privileges because the DNS server binds port 53 and is required.
        The code might differ depending on the SDK version shipped with the Lambda runtime.
        This test is designed to be fully AWS-compatible without any code changes.
        """
        # Additional safeguard against endpoint injection through AWS_ENDPOINT_URL once supported in newer SDKs:
        # https://docs.aws.amazon.com/sdkref/latest/guide/feature-ss-endpoints.html
        # Disabling `AWS_ENDPOINT_URL` won't work for SDK patching used for Ruby
        monkeypatch.setattr(config, "LAMBDA_DISABLE_AWS_ENDPOINT_URL", True)

        create_function_result = multiruntime_lambda.create_function(
            # Reduce cold start time, especially for Java runtimes
            MemorySize=1024,
            # java11 and java8.al2 timed out against AWS using 10 seconds
            Timeout=15,
            # Safeguard against endpoint injection through AWS_ENDPOINT_URL once supported in newer SDKs:
            # https://docs.aws.amazon.com/sdkref/latest/guide/feature-ss-endpoints.html
            Environment={"Variables": {"AWS_IGNORE_CONFIGURED_ENDPOINT_URLS": "true"}},
        )

        invocation_result = aws_client.lambda_.invoke(
            FunctionName=create_function_result["FunctionName"],
        )
        assert "FunctionError" not in invocation_result
