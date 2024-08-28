import os

import requests
from localstack.testing.aws.util import is_aws_cloud
from localstack.testing.pytest import markers
from localstack.utils.common import short_uid
from localstack.utils.strings import to_str
from localstack.utils.sync import retry


@markers.aws.validated
def test_ecs_alb_apigateway_integration(deploy_cfn_template, aws_client):
    api_name = f"api-{short_uid()}"
    deploy_cfn_template(
        template_path=os.path.join(
            os.path.dirname(__file__), "../../../templates/ecs-alb-apigw-service.yml"
        ),
        parameters={"ApiName": api_name},
        max_wait=300,
    )

    # get deployed API
    apis = aws_client.apigatewayv2.get_apis()["Items"]
    api = [api for api in apis if api["Name"] == api_name][0]
    assert api

    # invoke API
    def _invoke_api():
        endpoint = api["ApiEndpoint"]
        endpoint = f"http://{endpoint}" if "://" not in endpoint else endpoint
        url = f"{endpoint}/test"
        result = requests.get(url)
        assert "nginx" in to_str(result.content)

    retry(_invoke_api, retries=60, sleep=1)


@markers.snapshot.skip_snapshot_verify(
    paths=[
        "$..StackResourceDetail.DriftInformation",
        "$..StackResourceDetail.Metadata",
        "$..StackResourceDetail.PhysicalResourceId",
    ]
)
@markers.aws.validated
def test_capacity_providers(aws_client, deploy_cfn_template, snapshot):
    stack = deploy_cfn_template(
        template_path=os.path.join(os.path.dirname(__file__), "../../../templates/ecs-asg.yml"),
        max_wait=(1500 if is_aws_cloud() else None),
    )

    snapshot.add_transformer(snapshot.transform.cloudformation_api())

    describe_capacity_provider = aws_client.cloudformation.describe_stack_resource(
        StackName=stack.stack_name, LogicalResourceId="myProvider01647325"
    )
    snapshot.match("describe_capacity_provider", describe_capacity_provider)

    describe_capacity_cluster = aws_client.cloudformation.describe_stack_resource(
        StackName=stack.stack_name, LogicalResourceId="myCluster01C69118"
    )
    snapshot.match("describe_capacity_cluster", describe_capacity_cluster)

    # TODO: Fix physical resource id generation for ECS cluster
