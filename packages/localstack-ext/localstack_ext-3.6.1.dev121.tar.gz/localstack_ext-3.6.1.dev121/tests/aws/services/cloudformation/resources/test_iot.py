import json
import os

from localstack.testing.pytest import markers
from localstack.utils.strings import short_uid


@markers.aws.validated
def test_role(deploy_cfn_template, snapshot, aws_client):
    template_path = os.path.join(os.path.dirname(__file__), "../../../templates/iot_topic_rule.yml")
    stack = deploy_cfn_template(template_path=template_path)
    description = aws_client.cloudformation.describe_stack_resources(StackName=stack.stack_name)

    snapshot.add_transformer(snapshot.transform.cloudformation_api())
    snapshot.match("stack_outputs", stack.outputs)
    snapshot.match("stack_resource_descriptions", description)


@markers.aws.validated
def test_role_alias(deploy_cfn_template, create_role, snapshot, aws_client):
    alias = f"alias-{short_uid()}"
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"Service": "lambda.amazonaws.com"},
                "Action": "sts:AssumeRole",
            },
        ],
    }

    role = create_role(AssumeRolePolicyDocument=json.dumps(trust_policy))

    template_path = os.path.join(os.path.dirname(__file__), "../../../templates/iot_role_alias.yml")
    stack = deploy_cfn_template(
        template_path=template_path, parameters={"Alias": alias, "RoleArn": role["Role"]["Arn"]}
    )
    description = aws_client.cloudformation.describe_stack_resources(StackName=stack.stack_name)

    snapshot.add_transformer(snapshot.transform.regex(alias, "role-alias"))
    snapshot.add_transformer(snapshot.transform.cloudformation_api())
    snapshot.match("stack_outputs", stack.outputs)
    snapshot.match("stack_resource_descriptions", description)
