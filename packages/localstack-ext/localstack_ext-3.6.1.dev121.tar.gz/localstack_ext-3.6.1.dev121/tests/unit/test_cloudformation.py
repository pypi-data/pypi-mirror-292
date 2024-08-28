import pytest
from localstack.pro.core.services.cloudformation.cloudformation_extended import (
    get_aws_ecr_repo_properties,
)


@pytest.mark.parametrize(
    "url,name,tag",
    [
        ("000000000000.dkr.ecr.eu-west-1.localhost/repo_name:latest", "repo_name", "latest"),
        ("000000000000.dkr.ecr.eu-central-1.amazonaws.com/samapp/repo", "samapp/repo", None),
        ("000000000000.ecr.localhost.localstack.cloud/repo_name:latest", None, None),
    ],
)
def test_get_ecr_repo_name_and_tag(url, name, tag):
    properties = get_aws_ecr_repo_properties(url) or {}
    assert name == properties.get("name")
    assert tag == properties.get("tag")
