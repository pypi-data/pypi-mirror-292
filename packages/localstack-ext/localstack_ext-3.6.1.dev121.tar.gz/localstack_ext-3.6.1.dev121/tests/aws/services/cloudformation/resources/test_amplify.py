import os

import aws_cdk as cdk
import pytest
from localstack.testing.pytest import markers
from localstack.utils.strings import short_uid


class TestCfnAmplifyResources:
    @pytest.fixture(scope="class", autouse=True)
    def infrastructure(self, infrastructure_setup, aws_client):
        infra = infrastructure_setup(namespace="CfnAmplifyTest")
        stack = cdk.Stack(infra.cdk_app, "AmplifyTestStack")

        app_name = f"my-app-{short_uid()}"
        app = cdk.aws_amplify.CfnApp(stack, "app", name=app_name, description="My amplify app")
        branch = cdk.aws_amplify.CfnBranch(
            stack, "branch", app_id=app.attr_app_id, branch_name="master", stage="PRODUCTION"
        )

        cdk.CfnOutput(stack, "AppName", value=app.attr_app_name)
        cdk.CfnOutput(stack, "AppId", value=app.attr_app_id)
        cdk.CfnOutput(stack, "AppArn", value=app.attr_arn)
        cdk.CfnOutput(stack, "AppDefaultDomain", value=app.attr_default_domain)
        cdk.CfnOutput(stack, "AppRef", value=app.ref)
        cdk.CfnOutput(stack, "BranchName", value=branch.attr_branch_name)
        cdk.CfnOutput(stack, "BranchArn", value=branch.attr_arn)
        cdk.CfnOutput(stack, "BranchRef", value=branch.ref)

        with infra.provisioner(skip_deployment=False, skip_teardown=False) as prov:
            yield prov

    @markers.snapshot.skip_snapshot_verify(
        paths=[
            # all missing from response
            "$..branches..backend",
            "$..branches..createTime",
            "$..branches..enableAutoBuild",
            "$..branches..enableBasicAuth",
            "$..branches..enableNotification",
            "$..branches..enablePerformanceMode",
            "$..branches..enablePullRequestPreview",
            "$..branches..totalNumberOfJobs",
            "$..branches..updateTime",
        ]
    )
    @markers.aws.validated
    def test_amplify_resources(self, infrastructure, aws_client, snapshot):
        outputs = infrastructure.get_stack_outputs("AmplifyTestStack")
        snapshot.match("outputs", outputs)

        app_name = outputs["AppName"]
        snapshot.add_transformer(snapshot.transform.regex(app_name, "<app-name>"))
        app_id = outputs["AppId"]
        snapshot.add_transformer(snapshot.transform.regex(app_id, "<app-id>"))
        branch_name = outputs["BranchName"]
        snapshot.add_transformer(snapshot.transform.regex(branch_name, "<branch-name>"))

        domain_name = outputs["AppDefaultDomain"]
        domain_suffix = domain_name.replace(f"{app_id}.", "")
        snapshot.add_transformer(snapshot.transform.regex(domain_suffix, "<domain-suffix>"))

        branches = aws_client.amplify.list_branches(appId=app_id)
        snapshot.match("branches", branches)
        apps = aws_client.amplify.get_app(appId=app_id)
        snapshot.match("apps", apps)


@markers.aws.validated
def test_amplify_env_variables(deploy_cfn_template, snapshot, aws_client):
    snapshot.add_transformer(snapshot.transform.dynamodb_api())
    stack = deploy_cfn_template(
        template_path=os.path.join(
            os.path.dirname(__file__), "../../../templates/amplify_env_variables.yml"
        ),
    )
    app_id = stack.outputs["AmplifyAppId"]
    snapshot.add_transformer(snapshot.transform.regex(app_id, "<app-id>"))

    snapshot.add_transformer(snapshot.transform.regex("appARN", "<app-arn>"))

    domain_name = stack.outputs["AppDefaultDomain"]
    domain_suffix = domain_name.replace(f"{app_id}.", "")
    snapshot.add_transformer(snapshot.transform.regex(domain_suffix, "<domain-suffix>"))

    description = aws_client.amplify.get_app(appId=app_id)
    snapshot.match("app_description", description)
