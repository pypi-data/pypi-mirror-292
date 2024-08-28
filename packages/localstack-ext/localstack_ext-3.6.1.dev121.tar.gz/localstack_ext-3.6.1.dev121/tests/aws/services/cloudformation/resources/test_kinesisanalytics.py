import os

import pytest
from localstack.testing.pytest import markers
from localstack.utils.strings import short_uid
from localstack_snapshot.snapshots.transformer import SortingTransformer


@markers.only_on_amd64
@markers.aws.validated
@markers.snapshot.skip_snapshot_verify(paths=["$..ApplicationDetail"])
@pytest.mark.skip_store_check(reason="recursion limit exceeded")
def test_application_with_output_and_reference(deploy_cfn_template, snapshot, aws_client):
    snapshot.add_transformer(SortingTransformer("StackResources", lambda x: x["LogicalResourceId"]))
    snapshot.add_transformer(snapshot.transform.cloudformation_api())

    app_name = f"app-{short_uid()}"
    # without application code to test without siddhi loading
    template_path = os.path.join(
        os.path.dirname(__file__), "../../../templates/kinesisanalytics_app.yml"
    )
    stack = deploy_cfn_template(template_path=template_path, parameters={"AppName": app_name})
    snapshot.match("stack_outputs", stack.outputs)

    description = aws_client.cloudformation.describe_stack_resources(StackName=stack.stack_name)
    snapshot.match("stack_resource_descriptions", description)

    app = aws_client.kinesisanalytics.describe_application(ApplicationName=app_name)
    snapshot.match("kinesisAnalyticsApp", app)
