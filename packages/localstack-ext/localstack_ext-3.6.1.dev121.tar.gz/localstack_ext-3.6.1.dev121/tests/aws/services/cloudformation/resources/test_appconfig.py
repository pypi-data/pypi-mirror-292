import os

from localstack.testing.pytest import markers
from localstack.utils.files import load_file
from localstack.utils.strings import short_uid
from localstack_snapshot.snapshots.transformer import SortingTransformer


@markers.aws.validated
@markers.snapshot.skip_snapshot_verify(
    paths=[
        "$..Type",
        "$..CompletedAt",
        "$..ConfigurationName",
        "$..FinalBakeTimeInMinutes",
        "$..GrowthType",
        "$..PercentageComplete",
        "$..State",
        "$..FinalBakeTimeInMinutes",
        "$..GrowthType",
    ]
)
def test_application_deployment(deploy_cfn_template, snapshot, aws_client):
    snapshot.add_transformer(snapshot.transform.key_value("ApplicationRef", "app-id"))
    snapshot.add_transformer(
        snapshot.transform.key_value("ConfigurationProfileRef", "configuration-profile-id")
    )
    snapshot.add_transformer(snapshot.transform.key_value("EnvironmentRef", "environment-id"))
    snapshot.add_transformer(
        snapshot.transform.key_value("DeploymentStrategyRef", "deployment-strategy-ref")
    )

    snapshot.add_transformer(snapshot.transform.cloudformation_api())
    snapshot.add_transformer(SortingTransformer("StackResources", lambda x: x["LogicalResourceId"]))

    app_name = f"app-{short_uid()}"
    environment_name = f"environment-{short_uid()}"
    configuration_profile_name = f"configuration-profile-{short_uid()}"
    deployment_strategy_name = f"deployment-strategy-{short_uid()}"

    snapshot.add_transformer(snapshot.transform.regex(app_name, "app-name"))
    snapshot.add_transformer(snapshot.transform.regex(environment_name, "environment-name"))
    snapshot.add_transformer(
        snapshot.transform.regex(configuration_profile_name, "configuration-profile-name")
    )
    snapshot.add_transformer(
        snapshot.transform.regex(deployment_strategy_name, "deployment-strategy-name")
    )

    template = load_file(
        os.path.join(
            os.path.dirname(__file__), "../../../templates/appconfig_application_deployment.yml"
        )
    )

    stack = deploy_cfn_template(
        template=template,
        parameters={
            "AppName": app_name,
            "EnvironmentName": environment_name,
            "ConfigurationProfileName": configuration_profile_name,
            "DeploymentStrategyName": deployment_strategy_name,
        },
    )

    snapshot.match("outputs", stack.outputs)

    app = aws_client.appconfig.get_application(ApplicationId=stack.outputs["ApplicationRef"])
    snapshot.match("app", app)

    environment = aws_client.appconfig.get_environment(
        ApplicationId=stack.outputs["ApplicationRef"], EnvironmentId=stack.outputs["EnvironmentRef"]
    )
    snapshot.match("environment", environment)

    configuration_profile = aws_client.appconfig.get_configuration_profile(
        ApplicationId=stack.outputs["ApplicationRef"],
        ConfigurationProfileId=stack.outputs["ConfigurationProfileRef"],
    )
    snapshot.match("configuration_profile", configuration_profile)

    configuration_version = aws_client.appconfig.list_hosted_configuration_versions(
        ApplicationId=stack.outputs["ApplicationRef"],
        ConfigurationProfileId=stack.outputs["ConfigurationProfileRef"],
    )
    snapshot.match("configuration_version", configuration_version["Items"][0])

    deployment_strategy = aws_client.appconfig.get_deployment_strategy(
        DeploymentStrategyId=stack.outputs["DeploymentStrategyRef"]
    )
    snapshot.match("deployment_strategy", deployment_strategy)

    deployments = aws_client.appconfig.list_deployments(
        ApplicationId=stack.outputs["ApplicationRef"], EnvironmentId=stack.outputs["EnvironmentRef"]
    )
    snapshot.match("deployment", deployments["Items"][0])

    resources = aws_client.cloudformation.describe_stack_resources(StackName=stack.stack_name)
    snapshot.match("resource", resources)
