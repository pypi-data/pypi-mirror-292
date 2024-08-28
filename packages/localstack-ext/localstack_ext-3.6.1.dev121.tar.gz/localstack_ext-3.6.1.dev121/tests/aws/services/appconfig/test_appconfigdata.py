import contextlib
import logging

import pytest
from botocore.exceptions import ClientError
from localstack.testing.pytest import markers
from localstack.utils.strings import short_uid
from localstack.utils.sync import retry

LOG = logging.getLogger(__name__)


@pytest.fixture(autouse=True)
def appconfig_transformers(snapshot):
    snapshot.add_transformers_list(
        [
            snapshot.transform.key_value("Id"),
            snapshot.transform.key_value("ApplicationId"),
            snapshot.transform.key_value("Name"),
            snapshot.transform.key_value("NextPollConfigurationToken"),
        ]
    )


@pytest.fixture()
def create_config_profile(aws_client):
    profiles = []
    appconfig_client = aws_client.appconfig

    def _create(app_id, **kwargs):
        kwargs.setdefault("LocationUri", "hosted")
        result = appconfig_client.create_configuration_profile(ApplicationId=app_id, **kwargs)
        profiles.append((app_id, result["Id"]))
        return result

    yield _create

    for app_id, profile_id in profiles:
        with contextlib.suppress(ClientError):
            appconfig_client.delete_configuration_profile(
                ApplicationId=app_id, ConfigurationProfileId=profile_id
            )


class TestAppConfigData:
    @markers.aws.validated
    def test_invalid_token(self, aws_client, snapshot):
        client = aws_client.appconfigdata
        with pytest.raises(ClientError) as exc:
            client.get_latest_configuration(ConfigurationToken="invalid")
        snapshot.match("invalid-token", exc.value.response)

    @markers.aws.validated
    def test_get_latest_app_config(
        self,
        aws_client,
        snapshot,
        appconfig_application,
        create_config_profile,
        create_deployment_strategy,
    ):
        app_id = appconfig_application["Id"]

        result = create_config_profile(app_id, Name=f"config-{short_uid()}")
        profile_id = result["Id"]

        result = aws_client.appconfig.create_environment(
            ApplicationId=app_id, Name="env-1", Description="test env 1"
        )
        snapshot.match("create-env-response", result)
        env_id = result["Id"]

        result = aws_client.appconfig.create_hosted_configuration_version(
            ApplicationId=app_id,
            ConfigurationProfileId=profile_id,
            Content="test content",
            ContentType="text/plain",
        )
        version_number = result["VersionNumber"]

        strategy_name = f"s-{short_uid()}"
        result = create_deployment_strategy(Name=strategy_name)
        snapshot.match("create-strategy-response", result)
        strategy_id = result["Id"]

        aws_client.appconfig.start_deployment(
            ApplicationId=app_id,
            EnvironmentId=env_id,
            DeploymentStrategyId=strategy_id,
            ConfigurationProfileId=profile_id,
            ConfigurationVersion=str(version_number),
        )

        # assert error message for invalid env identifier
        with pytest.raises(ClientError) as exc:
            aws_client.appconfigdata.start_configuration_session(
                ApplicationIdentifier="invalid",
                EnvironmentIdentifier=env_id,
                ConfigurationProfileIdentifier=profile_id,
            )
        snapshot.match("invalid-env-app-id-response", exc.value.response)

        # assert error message for invalid env identifier
        with pytest.raises(ClientError) as exc:
            aws_client.appconfigdata.start_configuration_session(
                ApplicationIdentifier=app_id,
                EnvironmentIdentifier="invalid",
                ConfigurationProfileIdentifier=profile_id,
            )
        snapshot.match("invalid-env-id-response", exc.value.response)

        # assert error message for invalid config profile identifier
        with pytest.raises(ClientError) as exc:
            aws_client.appconfigdata.start_configuration_session(
                ApplicationIdentifier=app_id,
                EnvironmentIdentifier=env_id,
                ConfigurationProfileIdentifier="invalid",
            )
        snapshot.match("invalid-profile-id-response", exc.value.response)

        # start session
        result = aws_client.appconfigdata.start_configuration_session(
            ApplicationIdentifier=app_id,
            EnvironmentIdentifier=env_id,
            ConfigurationProfileIdentifier=profile_id,
        )
        token = result["InitialConfigurationToken"]

        # assert error message for invalid session token
        with pytest.raises(ClientError) as exc:
            aws_client.appconfigdata.get_latest_configuration(ConfigurationToken="invalid")
        snapshot.match("invalid-session-token", exc.value.response)

        def _get_config():
            return aws_client.appconfigdata.get_latest_configuration(ConfigurationToken=token)

        result = retry(_get_config, retries=5, sleep=2)
        snapshot.match("latest-config", result)

    @markers.aws.validated
    def test_get_app_config_by_name(
        self,
        aws_client,
        snapshot,
        appconfig_application,
        create_config_profile,
        create_deployment_strategy,
    ):
        app_id = appconfig_application["Id"]
        app_name = appconfig_application["Name"]
        result = create_config_profile(app_id, Name=f"config-{short_uid()}")
        profile_id = result["Id"]
        profile_name = result["Name"]

        result = aws_client.appconfig.create_environment(
            ApplicationId=app_id, Name="env-1", Description="test env 1"
        )
        snapshot.match("create-env-response", result)
        env_id = result["Id"]
        env_name = result["Name"]

        result = aws_client.appconfig.create_hosted_configuration_version(
            ApplicationId=app_id,
            ConfigurationProfileId=profile_id,
            Content="test content",
            ContentType="text/plain",
        )
        version_number = result["VersionNumber"]

        strategy_name = f"s-{short_uid()}"
        result = create_deployment_strategy(Name=strategy_name)
        snapshot.match("create-strategy-response", result)
        strategy_id = result["Id"]

        aws_client.appconfig.start_deployment(
            ApplicationId=app_id,
            EnvironmentId=env_id,
            DeploymentStrategyId=strategy_id,
            ConfigurationProfileId=profile_id,
            ConfigurationVersion=str(version_number),
        )

        def _get_config():
            return aws_client.appconfigdata.get_latest_configuration(ConfigurationToken=token)

        # List of all permutations of app, env, profile for id and name combos
        start_config_session_options = [
            (app_id, env_id, profile_id),
            (app_name, env_id, profile_id),
            (app_id, env_name, profile_id),
            (app_id, env_id, profile_name),
            (app_name, env_name, profile_id),
            (app_id, env_name, profile_name),
            (app_name, env_id, profile_name),
            (app_name, env_name, profile_name),
        ]

        # Iterate over the options to start_configuration_session
        for index, option in enumerate(start_config_session_options):
            # start session with options
            result = aws_client.appconfigdata.start_configuration_session(
                ApplicationIdentifier=option[0],
                EnvironmentIdentifier=option[1],
                ConfigurationProfileIdentifier=option[2],
            )
            token = result["InitialConfigurationToken"]
            result = retry(_get_config, retries=5, sleep=2)
            snapshot.match(f"latest-config-{index}", result)
