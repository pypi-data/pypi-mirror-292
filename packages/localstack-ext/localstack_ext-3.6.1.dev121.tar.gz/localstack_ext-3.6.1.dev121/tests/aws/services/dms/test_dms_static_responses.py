import pytest
from localstack.pro.core.services.dms.static_data import VALID_ENGINE_NAMES
from localstack.testing.pytest import markers


class TestDmsStaticResponses:
    @markers.aws.validated
    @pytest.mark.parametrize(
        "engine_name",
        list(set(VALID_ENGINE_NAMES.get("source") + VALID_ENGINE_NAMES.get("target"))),
    )
    def test_describe_endpoint_settings(self, aws_client, snapshot, engine_name):
        response = aws_client.dms.describe_endpoint_settings(EngineName=engine_name)

        snapshot.match("describe_endpoint_settings-kinesis", response)

    @markers.aws.validated
    def test_describe_endpoint_types(self, aws_client, snapshot):
        # this test is just for keeping track of endpoint types that AWS has
        response = aws_client.dms.describe_endpoint_types()
        snapshot.match("describe-endpoint-response", response)
