import os

from localstack.testing.pytest import markers
from localstack.utils.strings import short_uid


@markers.aws.validated
@markers.snapshot.skip_snapshot_verify(
    paths=[
        "$..StackResourceDetail.DriftInformation",
        "$..StackResourceDetail.Metadata",
        "$..Actions..S3Action.KmsKeyArn",  # empty string but shouldn't be there
        "$..Actions..S3Action.ObjectKeyPrefix",  # empty string but shouldn't be there
        "$..Actions..S3Action.TopicArn",  # empty string but shouldn't be there
        "$..Recipients",  # empty list but shouldn't be there
        "$..TlsPolicy",  # missing (should be "Optional")
    ]
)
def test_create_receiptrules(deploy_cfn_template, aws_client, snapshot):
    rule_set_name = f"rule-set-{short_uid()}"
    rule_name = f"rule-{short_uid()}"

    snapshot.add_transformer(snapshot.transform.cloudformation_api())
    snapshot.add_transformer(snapshot.transform.regex(rule_set_name, "<rule-set-name>"))
    snapshot.add_transformer(snapshot.transform.regex(rule_name, "<rule-name>"))

    stack = deploy_cfn_template(
        template_path=os.path.join(
            os.path.dirname(__file__), "../../../templates/ses_receiptrule.yaml"
        ),
        parameters={"RuleSetName": rule_set_name, "RuleName": rule_name},
    )

    bucket_name = stack.outputs["BucketName"]
    snapshot.add_transformer(snapshot.transform.regex(bucket_name, "<bucket-name>"), priority=-1)

    describe_receipt_rule_set = aws_client.ses.describe_receipt_rule_set(RuleSetName=rule_set_name)
    snapshot.match("describe_receipt_rule_set", describe_receipt_rule_set)
    describe_resource_receipt_rule_set = aws_client.cloudformation.describe_stack_resource(
        StackName=stack.stack_name, LogicalResourceId="ruleset3A509FA6"
    )
    snapshot.match("describe_resource_receipt_rule_set", describe_resource_receipt_rule_set)

    describe_receipt_rule = aws_client.ses.describe_receipt_rule(
        RuleSetName=rule_set_name, RuleName=rule_name
    )["Rule"]
    snapshot.match("describe_receipt_rule", describe_receipt_rule)
    describe_resource_receipt_rule = aws_client.cloudformation.describe_stack_resource(
        StackName=stack.stack_name, LogicalResourceId="myrule48A3298E"
    )
    snapshot.match("describe_resource_receipt_rule", describe_resource_receipt_rule)


@markers.aws.validated
@markers.snapshot.skip_snapshot_verify(
    paths=["$..StackResourceDetail.DriftInformation", "$..StackResourceDetail.Metadata"]
)
def test_create_template(deploy_cfn_template, aws_client, snapshot):
    template_name = f"template-{short_uid()}"
    snapshot.add_transformer(snapshot.transform.cloudformation_api())
    snapshot.add_transformer(snapshot.transform.regex(template_name, "<template-name>"))

    stack = deploy_cfn_template(
        template_path=os.path.join(
            os.path.dirname(__file__), "../../../templates/ses_template.yaml"
        ),
        parameters={
            "TemplateName": template_name,
        },
    )

    template = aws_client.ses.get_template(TemplateName=template_name)
    snapshot.match("template", template)

    describe_resource_template = aws_client.cloudformation.describe_stack_resource(
        StackName=stack.stack_name, LogicalResourceId="MyTemplate"
    )
    snapshot.match("describe_resource_template", describe_resource_template)
