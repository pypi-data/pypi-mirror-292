import logging

import pytest
from localstack.utils.strings import short_uid

LOG = logging.getLogger(__name__)


@pytest.fixture
def create_v2_api(aws_client):
    apis = []

    def _create(**kwargs):
        if not kwargs.get("Name"):
            kwargs["Name"] = f"api-{short_uid()}"
        response = aws_client.apigatewayv2.create_api(**kwargs)
        apis.append(response)
        return response

    yield _create

    for api in apis:
        try:
            aws_client.apigatewayv2.delete_api(ApiId=api["ApiId"])
        except Exception as e:
            LOG.debug("Unable to delete API Gateway v2 API %s: %s", api, e)
