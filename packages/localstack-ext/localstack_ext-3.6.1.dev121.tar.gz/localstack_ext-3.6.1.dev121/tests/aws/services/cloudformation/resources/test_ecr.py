import os
import re

import pytest
from localstack.aws.connect import ClientFactory, ServiceLevelClientFactory
from localstack.testing.pytest import markers
from localstack.utils.strings import short_uid


@markers.aws.only_localstack
@pytest.mark.parametrize(
    "ecr_account,ecr_region",
    [
        ("000000000000", "us-east-1"),
        ("111111111111", "us-east-1"),
        ("000000000000", "eu-central-2"),
        ("111111111111", "eu-central-2"),
    ],
)
def test_url_output_different_account_or_region(
    deploy_cfn_template,
    create_repository,
    aws_client_factory: ClientFactory,
    aws_client: ServiceLevelClientFactory,
    ecr_account,
    ecr_region,
):
    ecr_client_factory = aws_client_factory(region_name=ecr_region, aws_access_key_id=ecr_account)
    repo_name = f"repo-{short_uid()}"
    repo_uri = f"{ecr_account}.dkr.ecr.{ecr_region}.amazonaws.com/{repo_name}:latest"

    topic_name = f"topic-{short_uid()}"
    repository_details = create_repository(
        repositoryName=repo_name, client_factory=ecr_client_factory
    )

    stack = deploy_cfn_template(
        template_path=os.path.join(
            os.path.dirname(__file__), "../../../templates/ecr-cross-region.yml"
        ),
        parameters={"RepoUri": repo_uri, "TopicName": topic_name},
    )

    topic_arn = stack.outputs["TopicArn"]
    display_name = aws_client.sns.get_topic_attributes(TopicArn=topic_arn)["Attributes"][
        "DisplayName"
    ]

    # TODO: include tag in uri generation
    # assert display_name == repository_details["repository"]["repositoryUri"]
    assert display_name.startswith(repository_details["repository"]["repositoryUri"])


@markers.aws.only_localstack
def test_untransformed_url_when_no_repository_created(
    deploy_cfn_template, aws_client, account_id, region_name
):
    topic_name = f"topic-{short_uid()}"
    repo_name = f"repo-{short_uid()}"
    repo_uri = f"{account_id}.dkr.ecr.{region_name}.amazonaws.com/{repo_name}:latest"

    stack = deploy_cfn_template(
        template_path=os.path.join(
            os.path.dirname(__file__), "../../../templates/ecr-cross-region.yml"
        ),
        parameters={"RepoUri": repo_uri, "TopicName": topic_name},
    )

    topic_arn = stack.outputs["TopicArn"]
    display_name = aws_client.sns.get_topic_attributes(TopicArn=topic_arn)["Attributes"][
        "DisplayName"
    ]

    assert display_name == repo_uri


@markers.aws.only_localstack
def test_url_output(deploy_cfn_template, aws_client):
    repo_name = f"repo-{short_uid()}/assets"
    result = deploy_cfn_template(
        template_path=os.path.join(
            os.path.dirname(__file__), "../../../templates/ecr-url-output.yaml"
        ),
        template_mapping={"repo_name": repo_name},
    )

    describe_response = aws_client.cloudformation.describe_stacks(StackName=result.stack_id)
    outputs = describe_response["Stacks"][0]["Outputs"]
    assert len(outputs) == 2
    for key in ["RepoUriOutput", "RepoUriFromAttr"]:
        repo_uri = [o["OutputValue"] for o in outputs if o["OutputKey"] == key][0]
        assert repo_uri
        assert repo_name in repo_uri
        assert re.match(r".*localhost.*:\d+/.+", repo_uri)
