import contextlib
import logging

import pytest
from botocore.exceptions import ClientError
from localstack.utils.collections import select_attributes
from localstack.utils.strings import short_uid

LOG = logging.getLogger(__name__)


@pytest.fixture(scope="function")
def appconfig_create_application(aws_client):
    applications = list()
    client = aws_client.appconfig

    def factory(**kwargs):
        if "Name" not in kwargs:
            kwargs["Name"] = f"test-application-{short_uid()}"

        created_app = client.create_application(**kwargs)
        applications.append(created_app)
        return created_app

    yield factory

    # cleanup (needs nested calls for proper cleanup in AWS)
    for app in applications:
        for profile in client.list_configuration_profiles(ApplicationId=app["Id"])["Items"]:
            for version in client.list_hosted_configuration_versions(
                ApplicationId=app["Id"], ConfigurationProfileId=profile["Id"]
            )["Items"]:
                kwargs = select_attributes(
                    version, ["ApplicationId", "ConfigurationProfileId", "VersionNumber"]
                )
                with contextlib.suppress(Exception):
                    client.delete_hosted_configuration_version(**kwargs)
            with contextlib.suppress(Exception):
                client.delete_configuration_profile(
                    ApplicationId=app["Id"], ConfigurationProfileId=profile["Id"]
                )
        for env in client.list_environments(ApplicationId=app["Id"])["Items"]:
            with contextlib.suppress(Exception):
                client.delete_environment(ApplicationId=app["Id"], EnvironmentId=env["Id"])
        try:
            client.delete_application(ApplicationId=app["Id"])
        except Exception as e:
            LOG.debug("Error cleaning up AppConfig application %s: %s", app["Id"], e)


@pytest.fixture(scope="function")
def appconfig_application(appconfig_create_application):
    return appconfig_create_application()


@pytest.fixture(scope="function")
def create_deployment_strategy(aws_client):
    strategies = []

    def _create(**kwargs):
        kwargs.setdefault("DeploymentDurationInMinutes", 0)
        kwargs.setdefault("GrowthFactor", 100.0)
        result = aws_client.appconfig.create_deployment_strategy(**kwargs)
        strategies.append(result)
        return result

    yield _create

    for strategy in strategies:
        with contextlib.suppress(ClientError):
            aws_client.appconfig.delete_deployment_strategy(DeploymentStrategyId=strategy["Id"])
