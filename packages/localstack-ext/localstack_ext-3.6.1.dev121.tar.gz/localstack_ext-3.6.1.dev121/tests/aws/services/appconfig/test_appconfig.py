import logging
import time

import pytest
from localstack.pro.core.aws.api.appconfig import DeploymentState, ReplicateTo
from localstack.pro.core.utils.aws import arns
from localstack.testing.pytest import markers
from localstack.utils.bootstrap import in_ci
from localstack.utils.strings import short_uid
from localstack.utils.sync import retry

LOG = logging.getLogger(__name__)

appconfig_role = {
    "Version": "2012-10-17",
    "Statement": {
        "Effect": "Allow",
        "Principal": {"Service": "appconfig.amazonaws.com"},
        "Action": "sts:AssumeRole",
    },
}
ssm_permission = {
    "Version": "2012-10-17",
    "Statement": [{"Effect": "Allow", "Action": "ssm:GetParameter", "Resource": "*"}],
}


class TestAppConfig:
    @markers.aws.unknown
    def test_application_crud_workflow(self, aws_client):
        name = f"app-{short_uid()}"

        app = aws_client.appconfig.create_application(
            Name=name, Description="Test Description", Tags={"foo": "bar"}
        )
        assert app["Name"] == name
        assert app["Description"] == "Test Description"

        retrieved_app = aws_client.appconfig.get_application(ApplicationId=app["Id"])
        assert retrieved_app["Name"] == app["Name"]

        second_name = f"app-{short_uid()}"
        second_app = aws_client.appconfig.create_application(
            Name=second_name, Description="Test Description", Tags={"foo": "bar"}
        )
        apps = aws_client.appconfig.list_applications()
        names = [app["Name"] for app in apps["Items"]]
        assert name in names
        assert second_name in names

        updated_app = aws_client.appconfig.update_application(
            ApplicationId=app["Id"], Name="update"
        )
        assert updated_app["Name"] == "update"
        retrieved_updated_app = aws_client.appconfig.get_application(ApplicationId=app["Id"])
        assert retrieved_updated_app["Name"] == "update"

        aws_client.appconfig.delete_application(ApplicationId=second_app["Id"])

        apps = aws_client.appconfig.list_applications()
        names = [app["Name"] for app in apps["Items"]]
        assert second_name not in names

        with pytest.raises(aws_client.appconfig.exceptions.ResourceNotFoundException):
            aws_client.appconfig.get_application(ApplicationId=second_app["Id"])

        # cleanup
        aws_client.appconfig.delete_application(ApplicationId=app["Id"])

    @markers.aws.unknown
    def test_environment_crud_workflow(
        self, appconfig_application, aws_client, account_id, region_name
    ):
        name = f"env-{short_uid()}"

        env = aws_client.appconfig.create_environment(
            ApplicationId=appconfig_application["Id"], Name=name
        )
        assert env["Name"] == name
        assert env["State"] == "ReadyForDeployment"

        retrieved_env = aws_client.appconfig.get_environment(
            EnvironmentId=env["Id"], ApplicationId=appconfig_application["Id"]
        )
        assert retrieved_env["Name"] == env["Name"]

        second_name = f"env-{short_uid()}"
        second_env = aws_client.appconfig.create_environment(
            ApplicationId=appconfig_application["Id"],
            Name=second_name,
            Description="Test Description",
            Tags={"foo": "bar"},
        )
        assert aws_client.appconfig.list_tags_for_resource(
            ResourceArn=arns.appconfig_environment_arn(
                appconfig_application["Id"],
                second_env["Id"],
                account_id,
                region_name,
            )
        )["Tags"] == {"foo": "bar"}
        envs = aws_client.appconfig.list_environments(ApplicationId=appconfig_application["Id"])
        names = [env["Name"] for env in envs["Items"]]
        assert name in names
        assert second_name in names

        updated_env = aws_client.appconfig.update_environment(
            ApplicationId=appconfig_application["Id"], EnvironmentId=env["Id"], Name="update"
        )
        assert updated_env["Name"] == "update"
        retrieved_updated_env = aws_client.appconfig.get_environment(
            ApplicationId=appconfig_application["Id"], EnvironmentId=env["Id"]
        )
        assert retrieved_updated_env["Name"] == "update"

        aws_client.appconfig.delete_environment(
            ApplicationId=appconfig_application["Id"], EnvironmentId=second_env["Id"]
        )

        envs = aws_client.appconfig.list_environments(ApplicationId=appconfig_application["Id"])
        names = [env["Name"] for env in envs["Items"]]
        assert second_name not in names

        with pytest.raises(aws_client.appconfig.exceptions.ResourceNotFoundException):
            aws_client.appconfig.get_environment(
                ApplicationId=appconfig_application["Id"], EnvironmentId=second_env["Id"]
            )

        # cleanup
        aws_client.appconfig.delete_environment(
            ApplicationId=appconfig_application["Id"], EnvironmentId=env["Id"]
        )

    @markers.aws.unknown
    def test_configuration_profile_crud_workflow(self, appconfig_application, aws_client):
        name = f"conf-{short_uid()}"

        conf = aws_client.appconfig.create_configuration_profile(
            ApplicationId=appconfig_application["Id"],
            Name=name,
            LocationUri="http://localhost.localstack.cloud",
        )
        assert conf["Name"] == name
        assert conf["LocationUri"] == "http://localhost.localstack.cloud"

        retrieved_conf = aws_client.appconfig.get_configuration_profile(
            ConfigurationProfileId=conf["Id"], ApplicationId=appconfig_application["Id"]
        )
        assert retrieved_conf["Name"] == conf["Name"]

        second_name = f"conf-{short_uid()}"
        second_conf = aws_client.appconfig.create_configuration_profile(
            ApplicationId=appconfig_application["Id"],
            Name=second_name,
            Description="Test Description",
            LocationUri="http://localhost.localstack.cloud",
        )
        confs = aws_client.appconfig.list_configuration_profiles(
            ApplicationId=appconfig_application["Id"]
        )
        names = [conf["Name"] for conf in confs["Items"]]
        assert name in names
        assert second_name in names

        updated_conf = aws_client.appconfig.update_configuration_profile(
            ApplicationId=appconfig_application["Id"],
            ConfigurationProfileId=conf["Id"],
            Name="update",
        )
        assert updated_conf["Name"] == "update"
        retrieved_updated_conf = aws_client.appconfig.get_configuration_profile(
            ApplicationId=appconfig_application["Id"], ConfigurationProfileId=conf["Id"]
        )
        assert retrieved_updated_conf["Name"] == "update"

        aws_client.appconfig.delete_configuration_profile(
            ApplicationId=appconfig_application["Id"], ConfigurationProfileId=second_conf["Id"]
        )

        confs = aws_client.appconfig.list_configuration_profiles(
            ApplicationId=appconfig_application["Id"]
        )
        names = [conf["Name"] for conf in confs["Items"]]
        assert second_name not in names

        with pytest.raises(aws_client.appconfig.exceptions.ResourceNotFoundException):
            aws_client.appconfig.get_configuration_profile(
                ApplicationId=appconfig_application["Id"], ConfigurationProfileId=second_conf["Id"]
            )

        # cleanup
        aws_client.appconfig.delete_configuration_profile(
            ApplicationId=appconfig_application["Id"], ConfigurationProfileId=conf["Id"]
        )

    @markers.aws.unknown
    def test_deployment_strategy_crud_workflow(
        self, appconfig_application, aws_client, account_id, region_name
    ):
        name = f"strat-{short_uid()}"

        strat = aws_client.appconfig.create_deployment_strategy(
            Name=name,
            DeploymentDurationInMinutes=1,
            GrowthFactor=1.2,
            ReplicateTo=ReplicateTo.NONE,
            Tags={"foo": "bar"},
        )
        assert strat["Name"] == name
        assert strat["DeploymentDurationInMinutes"] == 1
        assert aws_client.appconfig.list_tags_for_resource(
            ResourceArn=arns.appconfig_deploymentstrategy_arn(
                strat["Id"],
                account_id,
                region_name,
            )
        )["Tags"] == {"foo": "bar"}

        retrieved_conf = aws_client.appconfig.get_deployment_strategy(
            DeploymentStrategyId=strat["Id"]
        )
        assert retrieved_conf["Name"] == strat["Name"]

        second_name = f"strat-{short_uid()}"
        second_strat = aws_client.appconfig.create_deployment_strategy(
            Name=second_name,
            DeploymentDurationInMinutes=2,
            GrowthFactor=1.3,
            ReplicateTo=ReplicateTo.NONE,
        )
        strats = aws_client.appconfig.list_deployment_strategies()
        names = [strat["Name"] for strat in strats["Items"]]
        assert name in names
        assert second_name in names

        updated_strat = aws_client.appconfig.update_deployment_strategy(
            DeploymentStrategyId=strat["Id"], GrowthFactor=3.4
        )
        assert updated_strat["GrowthFactor"] == 3.4
        assert updated_strat["Name"] == strat["Name"]
        retrieved_updated_strat = aws_client.appconfig.get_deployment_strategy(
            DeploymentStrategyId=strat["Id"],
        )
        assert retrieved_updated_strat["GrowthFactor"] == 3.4
        assert retrieved_updated_strat["Name"] == strat["Name"]

        aws_client.appconfig.delete_deployment_strategy(
            DeploymentStrategyId=second_strat["Id"],
        )

        strats = aws_client.appconfig.list_deployment_strategies()
        names = [conf["Name"] for conf in strats["Items"]]
        assert second_name not in names

        with pytest.raises(aws_client.appconfig.exceptions.ResourceNotFoundException):
            aws_client.appconfig.get_deployment_strategy(
                DeploymentStrategyId=second_strat["Id"],
            )

        # cleanup
        aws_client.appconfig.delete_deployment_strategy(DeploymentStrategyId=strat["Id"])

    @markers.aws.unknown
    def test_hosted_configuration_version_crud_workflow(
        self, appconfig_application, aws_client, account_id, region_name
    ):
        conf = aws_client.appconfig.create_configuration_profile(
            ApplicationId=appconfig_application["Id"],
            Name=f"conf-{short_uid()}",
            LocationUri="http://localhost.localstack.cloud",
            Tags={"foo": "bar"},
        )

        app_id = appconfig_application["Id"]
        conf_id = conf["Id"]

        config_profile_arn = arns.appconfig_configurationprofile_arn(
            app_id, conf_id, account_id, region_name
        )
        tags = aws_client.appconfig.list_tags_for_resource(ResourceArn=config_profile_arn)
        assert tags["Tags"] == {"foo": "bar"}

        version = aws_client.appconfig.create_hosted_configuration_version(
            ApplicationId=app_id,
            ConfigurationProfileId=conf_id,
            Content=b'{ "Name": "ExampleApplication", "Id": "ExampleID", "Rank": 7 }',
            ContentType="application/json",
        )
        assert version["VersionNumber"] == 1
        assert version["ContentType"] == "application/json"

        retrieved_version = aws_client.appconfig.get_hosted_configuration_version(
            ApplicationId=app_id,
            ConfigurationProfileId=conf_id,
            VersionNumber=1,
        )
        assert version["VersionNumber"] == retrieved_version["VersionNumber"]

        aws_client.appconfig.validate_configuration(
            ApplicationId=app_id, ConfigurationProfileId=conf_id, ConfigurationVersion="1"
        )

        retrieved_conf = aws_client.appconfig.get_configuration(
            Application=app_id,
            Configuration=conf_id,
            ClientConfigurationVersion="1",
            Environment="foo",
            ClientId="bar",
        )
        assert str(version["VersionNumber"]) == retrieved_conf["ConfigurationVersion"]

        second_version = aws_client.appconfig.create_hosted_configuration_version(
            ApplicationId=app_id,
            ConfigurationProfileId=conf_id,
            Content=b'{ "Name": "ExampleApplication", "Id": "ExampleID", "Rank": 7 }',
            ContentType="application/json",
        )
        assert second_version["VersionNumber"] == 2

        third_version = aws_client.appconfig.create_hosted_configuration_version(
            ApplicationId=app_id,
            ConfigurationProfileId=conf_id,
            Content=b'{ "Name": "ExampleApplication", "Id": "ExampleID", "Rank": 7 }',
            ContentType="application/json",
        )
        assert third_version["VersionNumber"] == 3

        versions = aws_client.appconfig.list_hosted_configuration_versions(
            ApplicationId=app_id, ConfigurationProfileId=conf_id
        )
        version_numbers = [v["VersionNumber"] for v in versions["Items"]]
        assert 1 in version_numbers
        assert 2 in version_numbers
        assert 3 in version_numbers

        aws_client.appconfig.delete_hosted_configuration_version(
            ApplicationId=app_id, ConfigurationProfileId=conf_id, VersionNumber=3
        )

        versions = aws_client.appconfig.list_hosted_configuration_versions(
            ApplicationId=app_id, ConfigurationProfileId=conf_id
        )
        version_numbers = [v["VersionNumber"] for v in versions["Items"]]
        assert 3 not in version_numbers

        with pytest.raises(aws_client.appconfig.exceptions.ResourceNotFoundException):
            aws_client.appconfig.get_hosted_configuration_version(
                ApplicationId=app_id, ConfigurationProfileId=conf_id, VersionNumber=3
            )

        # cleanup
        aws_client.appconfig.delete_configuration_profile(
            ApplicationId=app_id, ConfigurationProfileId=conf_id
        )

    @markers.aws.unknown
    def test_deployment_simulation(
        self, appconfig_application, aws_client, account_id, region_name
    ):
        app_id = appconfig_application["Id"]
        conf_id = aws_client.appconfig.create_configuration_profile(
            ApplicationId=app_id,
            Name=f"conf-{short_uid()}",
            LocationUri="http://localhost.localstack.cloud",
        )["Id"]
        env_id = aws_client.appconfig.create_environment(
            ApplicationId=appconfig_application["Id"], Name=f"env-{short_uid()}"
        )["Id"]

        deployment = aws_client.appconfig.start_deployment(
            ApplicationId=app_id,
            EnvironmentId=env_id,
            ConfigurationProfileId=conf_id,
            DeploymentStrategyId="AppConfig.AllAtOnce",
            ConfigurationVersion="1",
            Tags={"foo": "bar"},
        )
        assert deployment["DeploymentNumber"] == 1
        assert deployment["State"] == DeploymentState.BAKING
        assert deployment["GrowthType"] == "LINEAR"
        assert aws_client.appconfig.list_tags_for_resource(
            ResourceArn=arns.appconfig_deployment_arn(
                app_id,
                env_id,
                1,
                account_id,
                region_name,
            )
        )["Tags"] == {"foo": "bar"}

        second_deployment = aws_client.appconfig.start_deployment(
            ApplicationId=app_id,
            EnvironmentId=env_id,
            ConfigurationProfileId=conf_id,
            DeploymentStrategyId="AppConfig.AllAtOnce",
            ConfigurationVersion="1",
        )
        assert second_deployment["DeploymentNumber"] == 2

        third_deployment = aws_client.appconfig.start_deployment(
            ApplicationId=app_id,
            EnvironmentId=env_id,
            ConfigurationProfileId=conf_id,
            DeploymentStrategyId="AppConfig.AllAtOnce",
            ConfigurationVersion="1",
        )
        assert third_deployment["DeploymentNumber"] == 3

        deployments = aws_client.appconfig.list_deployments(
            ApplicationId=app_id, EnvironmentId=env_id
        )
        deployment_numbers = [d["DeploymentNumber"] for d in deployments["Items"]]
        assert set(deployment_numbers) == {1, 2, 3}

        if not in_ci():
            # contains long sleeps, therefore avoid doing it in CI
            self._check_deployment_state_change(aws_client.appconfig, app_id, env_id, 1)

        # cleanup
        aws_client.appconfig.delete_configuration_profile(
            ApplicationId=app_id, ConfigurationProfileId=conf_id
        )
        aws_client.appconfig.delete_environment(ApplicationId=app_id, EnvironmentId=env_id)

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(
        paths=[
            "$..EventLog",
            "$..EventLog..Description",
            "$..PercentageComplete",
            "$..ContentType",
            "$..State",
        ]
    )
    def test_specify_resources_by_name(
        self,
        appconfig_application,
        create_iam_role_with_policy,
        create_parameter,
        aws_client,
        snapshot,
    ):
        snapshot.add_transformer(
            [
                snapshot.transform.key_value("ApplicationId"),
                snapshot.transform.jsonpath("$.config-profile.Id", value_replacement="config-id"),
                snapshot.transform.jsonpath(
                    "$.config-profile.Name", value_replacement="config-name"
                ),
                snapshot.transform.jsonpath("$.environment.Id", value_replacement="env-id"),
                snapshot.transform.jsonpath("$.environment.Name", value_replacement="env-name"),
            ]
        )
        app_id = appconfig_application["Id"]
        client = aws_client.appconfig

        # create role&policy
        role = f"test-appsync-role-{short_uid()}"
        policy_name = f"test-appsync-role-policy-{short_uid()}"

        snapshot.add_transformer(snapshot.transform.regex(role, "<role-name>"))

        role_arn = create_iam_role_with_policy(
            RoleName=role,
            PolicyName=policy_name,
            RoleDefinition=appconfig_role,
            PolicyDefinition=ssm_permission,
        )

        # create parameter
        param_name = f"test-param-{short_uid()}"
        create_parameter(Name=param_name, Value="{}", Type="String")

        snapshot.add_transformer(snapshot.transform.regex(param_name, "<param-name>"))

        def _create_profile():
            return client.create_configuration_profile(
                ApplicationId=appconfig_application["Id"],
                Name=conf_name,
                LocationUri=f"ssm-parameter://{param_name}",
                RetrievalRoleArn=role_arn,
            )

        # create config profile
        conf_name = f"conf-{short_uid()}"
        # note: adding a retry here, to avoid intermittent "Error trying to assume role" in AWS
        conf = retry(_create_profile, retries=4, sleep=10)
        conf_id = conf["Id"]
        snapshot.match("config-profile", conf)

        # create environment
        env_name = f"env-{short_uid()}"
        result = client.create_environment(ApplicationId=appconfig_application["Id"], Name=env_name)
        env_id = result["Id"]
        snapshot.match("environment", result)

        # create new config version
        result = client.create_hosted_configuration_version(
            ApplicationId=app_id,
            ConfigurationProfileId=conf_id,
            Content=b"{}",
            ContentType="application/json",
            LatestVersionNumber=1,
        )
        snapshot.match("hosted-config-version", result)
        version_number = result["VersionNumber"]

        # start deployment
        result = client.start_deployment(
            ApplicationId=app_id,
            EnvironmentId=env_id,
            ConfigurationProfileId=conf_id,
            DeploymentStrategyId="AppConfig.AllAtOnce",
            ConfigurationVersion=str(version_number),
        )
        snapshot.match("start-deployment", result)
        deployment_number = result["DeploymentNumber"]

        def _deployment_ready():
            result = client.get_deployment(
                ApplicationId=app_id, EnvironmentId=env_id, DeploymentNumber=deployment_number
            )
            assert result["State"] in ["BAKING", "COMPLETE"]
            return result

        # wait for deployment
        result = retry(_deployment_ready, retries=15, sleep=1)
        snapshot.match("deployment-details", result)

        # lookup configuration get by app/env/conf name
        app_name = appconfig_application["Name"]
        result = client.get_configuration(
            Application=app_name, Environment=env_name, Configuration=conf_name, ClientId="test123"
        )
        snapshot.match("configuration", result)

    @staticmethod
    def _check_deployment_state_change(client, application_id, environment_id, deployment_number):
        first_state = client.get_deployment(
            ApplicationId=application_id,
            EnvironmentId=environment_id,
            DeploymentNumber=deployment_number,
        )
        assert first_state["State"] == DeploymentState.BAKING
        time.sleep(8)
        second_state = client.get_deployment(
            ApplicationId=application_id,
            EnvironmentId=environment_id,
            DeploymentNumber=deployment_number,
        )
        assert second_state["State"] == DeploymentState.VALIDATING
        stopped = client.stop_deployment(
            ApplicationId=application_id,
            EnvironmentId=environment_id,
            DeploymentNumber=deployment_number,
        )
        assert stopped["State"] == DeploymentState.ROLLED_BACK
