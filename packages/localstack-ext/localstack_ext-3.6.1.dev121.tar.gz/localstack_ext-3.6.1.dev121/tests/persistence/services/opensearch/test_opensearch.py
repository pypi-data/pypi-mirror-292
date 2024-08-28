import json

import pytest
import requests
from localstack import config
from localstack.utils.strings import short_uid


@pytest.fixture
def configure_opensearch(monkeypatch, httpserver):
    monkeypatch.setattr(config, "OPENSEARCH_ENDPOINT_STRATEGY", "domain")
    monkeypatch.setattr(config, "OPENSEARCH_CUSTOM_BACKEND", httpserver.url_for("/"))


@pytest.mark.skip
def test_opensearch_test_search(
    persistence_validations,
    snapshot,
    opensearch_endpoint,
    opensearch_document_path,
    configure_opensearch,
):
    index = "/".join(opensearch_document_path.split("/")[:-2])
    requests.post(
        f"{opensearch_endpoint}/_refresh",
        headers={"content-type": "application/json", "Accept-encoding": "identity"},
    )

    def validate():
        search = {"query": {"match": {"last_name": "Fett"}}}
        snapshot.match(
            "opensearch_search",
            requests.get(
                f"{index}/_search",
                data=json.dumps(search),
                headers={"content-type": "application/json", "Accept-encoding": "identity"},
            ),
        )

    persistence_validations.register(validate)


@pytest.mark.skip
def test_opensearch_describe_domain(
    persistence_validations, snapshot, opensearch_wait_for_cluster, aws_client
):
    domain_name = f"opensearch-{short_uid()}"
    aws_client.opensearch.create_domain(DomainName=domain_name)

    def validate():
        opensearch_wait_for_cluster(domain_name=domain_name)
        snapshot.match(
            "opensearch_describe_domain",
            aws_client.opensearch.describe_domain(DomainName=domain_name),
        )

    persistence_validations.register(validate)
