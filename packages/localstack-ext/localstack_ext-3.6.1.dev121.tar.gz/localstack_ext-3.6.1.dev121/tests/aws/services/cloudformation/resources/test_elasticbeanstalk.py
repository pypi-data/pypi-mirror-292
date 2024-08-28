import os.path

from localstack.testing.pytest import markers


@markers.aws.validated
@markers.snapshot.skip_snapshot_verify(
    paths=[
        "$..ApplicationVersions",
        "$..ConfigurationSettings..ApplicationName",
        "$..ConfigurationSettings..DateUpdated",
        "$..ConfigurationSettings..OptionSettings",
        "$..ConfigurationSettings..PlatformArn",
        "$..ConfigurationSettings..TemplateName",
        "$..Applications",
        "$..Environments",
    ]
)
def test_application_with_version_and_environment(deploy_cfn_template, snapshot, aws_client):
    stack = deploy_cfn_template(
        template_path=os.path.join(
            os.path.dirname(__file__), "../../../templates/elasticbeanstalk_app.yml"
        ),
        max_wait=360,
    )

    app_name = stack.outputs["ApplicationName"]
    env_name = stack.outputs["AppEnvironment"]
    version_label = stack.outputs["AppVersion"]
    config_template = stack.outputs["AppConfig"]

    snapshot.add_transformer(snapshot.transform.key_value("ApplicationName", "app-name"))
    snapshot.add_transformer(snapshot.transform.key_value("EnvironmentName", "env-name"))
    snapshot.add_transformer(snapshot.transform.key_value("VersionLabel", "app-version"))
    snapshot.add_transformer(snapshot.transform.key_value("TemplateName", "app-config"))

    elasticbeanstalk = aws_client.elasticbeanstalk

    # check that the application exists
    app = elasticbeanstalk.describe_applications(ApplicationNames=[app_name])
    snapshot.match("app", app)

    # check that the application version exists
    app_version = elasticbeanstalk.describe_application_versions(
        ApplicationName=app_name, VersionLabels=[version_label]
    )
    snapshot.match("app_version", app_version)

    # check that the environment exists
    env = elasticbeanstalk.describe_environments(EnvironmentNames=[env_name])
    snapshot.match("env", env)

    # check that the configuration template exists
    template = elasticbeanstalk.describe_configuration_settings(
        ApplicationName=app_name, TemplateName=config_template
    )
    snapshot.match("template", template)
