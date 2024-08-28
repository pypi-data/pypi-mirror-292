import os

import pytest
from localstack.utils.files import load_file
from localstack.utils.strings import short_uid


@pytest.mark.skip_snapshot_verify(
    paths=["$..Stacks..StackStatus"],
    reason="In snapshot persistence, we persist with creation in progress.",
)
@pytest.mark.skip(reason="flaky due to outputs partially missing")  # FIXME
def test_cfn_describe_stack(persistence_validations, snapshot, aws_client):
    stack_name = f"stack-name{short_uid()}"
    template = load_file(
        os.path.join(os.path.dirname(__file__), "../../../aws/templates/persistence_sample.yaml")
    )
    aws_client.cloudformation.create_stack(StackName=stack_name, TemplateBody=template)
    aws_client.cloudformation.get_waiter("stack_create_complete").wait(StackName=stack_name)

    def validate():
        snapshot.match(
            "describe_stack", aws_client.cloudformation.describe_stacks(StackName=stack_name)
        )

    persistence_validations.register(validate)
