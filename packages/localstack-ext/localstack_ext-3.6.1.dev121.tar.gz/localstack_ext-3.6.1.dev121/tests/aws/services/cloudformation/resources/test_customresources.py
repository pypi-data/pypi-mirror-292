import os

import pytest
from localstack.testing.pytest import markers
from localstack.utils.strings import short_uid


@markers.aws.validated
def test_customresource_lambda_backed(deploy_cfn_template, aws_client):
    """tests a custom resource that creates a dynamodb table with the given name"""
    table_name = f"localstack-test-table-{short_uid()}"
    result = deploy_cfn_template(
        template_path=os.path.join(
            os.path.dirname(__file__), "../../../templates/customresource-lambda-backed.yaml"
        ),
        parameters={"tableNameParam": table_name},
    )

    # verify custom 'Data' properties are set and resolved correctly
    assert "custom-data" == result.outputs["CustomOutput"]

    table = aws_client.dynamodb.describe_table(TableName=table_name)
    assert table_name in result.outputs["masterTableArn"]
    assert table_name in table["Table"]["TableArn"]

    # TODO: currently not supported
    # deploy_cfn_template(
    #     is_update=True,
    #     stack_name=result.stack_name,
    #     template_path=os.path.join(
    #         os.path.dirname(__file__), "../../templates/customresource-lambda-backed.yaml"
    #     ),
    #     parameters={"tableNameParam": f"change-name-{short_uid()}" },
    # )

    aws_client.cloudformation.delete_stack(StackName=result.stack_id)
    aws_client.cloudformation.get_waiter("stack_delete_complete").wait(StackName=result.stack_id)

    # TODO: currently not supported
    # Implementation is blocked by the fact that the lambda function might be deleted before the custom resource
    # with pytest.raises(aws_client.dynamodb.exceptions.ResourceNotFoundException):
    #     aws_client.dynamodb.describe_table(TableName=table_name)


@pytest.mark.skip(reason="Temporarily disabled, fix with v2!")
@markers.aws.validated
def test_customresource_sns_backed(deploy_cfn_template, aws_client):
    """
    equivalent to test_customresource_lambda_backed but with a different set of resources
    with an SNS-backed custom resource representing the DynamoDB Table
    """
    table_name = f"localstack-test-table-{short_uid()}"
    result = deploy_cfn_template(
        template_path=os.path.join(
            os.path.dirname(__file__), "../../../templates/customresource-sns-backed.yml"
        ),
        parameters={"tableNameParam": table_name},
        max_wait=240,
    )

    # verify custom 'Data' properties are set and resolved correctly
    assert "custom-data" == result.outputs["CustomOutput"]

    tables = aws_client.dynamodb.list_tables()["TableNames"]
    assert table_name in result.outputs["masterTableArn"]
    assert table_name in tables
