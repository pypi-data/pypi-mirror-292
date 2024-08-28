"""
Pytest configuration that spins up a single localstack instance that is shared across test modules.
See: https://docs.pytest.org/en/6.2.x/fixture.html#conftest-py-sharing-fixtures-across-multiple-files

It is thread/process safe to run with pytest-parallel, however not for pytest-xdist.
"""

import logging
import os
from typing import TYPE_CHECKING

import pytest
from localstack import config as localstack_config
from localstack.constants import DEFAULT_PORT_EDGE, ENV_INTERNAL_TEST_RUN
from localstack.pro.core.bootstrap.licensingv2 import ENV_LOCALSTACK_API_KEY
from localstack.utils.bootstrap import in_ci
from localstack.utils.http import safe_requests

if TYPE_CHECKING:
    from localstack_snapshot.snapshots import SnapshotSession

LOG = logging.getLogger(__name__)


@pytest.hookimpl()
def pytest_addhooks(pluginmanager):
    from localstack.pro.core.testing.pytest.store_check import StoreSerializationCheckerPlugin

    pluginmanager.register(StoreSerializationCheckerPlugin())


@pytest.hookimpl()
def pytest_configure(config):
    config.option.start_localstack = True

    # FIXME: note that this should be the same as in tests/aws/conftest.py since both are currently
    #  run in the same CI test step, but only one localstack instance is started for both.
    # configure for localstack run
    os.environ[ENV_INTERNAL_TEST_RUN] = "1"
    if ENV_LOCALSTACK_API_KEY not in os.environ:
        os.environ[ENV_LOCALSTACK_API_KEY] = "test"

    safe_requests.verify_ssl = False
    localstack_config.FORCE_SHUTDOWN = False

    localstack_config.GATEWAY_LISTEN = localstack_config.UniqueHostAndPortList(
        [
            localstack_config.HostAndPort(host="0.0.0.0", port=DEFAULT_PORT_EDGE),
            localstack_config.HostAndPort(host="0.0.0.0", port=443),
        ]
    )
    os.environ["GATEWAY_LISTEN"] = "0.0.0.0:4566,0.0.0.0:443"

    # TODO this should be moved to become a LocalStack feature in general (authorize dockerhub pulls)
    if os.environ.get("DOCKERHUB_USERNAME", None) and os.environ.get("DOCKERHUB_PASSWORD", None):
        logging.info("DockerHub credentials set. Performing login.")
        from localstack.utils.docker_utils import DOCKER_CLIENT

        DOCKER_CLIENT.login(
            username=os.environ.get("DOCKERHUB_USERNAME"),
            password=os.environ.get("DOCKERHUB_PASSWORD"),
        )
    else:
        LOG.debug("No DockerHub credentials set. Not performing a login.")


@pytest.fixture(scope="function")
def snapshot(_snapshot_session: "SnapshotSession"):
    from tests.aws.transformer_utility_ext import TransformerUtilityExt

    # override transformer for the snapshot fixture in community
    _snapshot_session.transform = TransformerUtilityExt()
    yield _snapshot_session


def pytest_collection_modifyitems(config, items):
    from localstack import config as localstack_config
    from localstack.testing.aws.util import is_aws_cloud
    from localstack.utils.platform import get_arch

    is_offline = config.getoption("--offline")
    is_in_docker = localstack_config.is_in_docker
    is_in_ci = in_ci()
    is_amd64 = get_arch() == "amd64"
    is_real_aws = is_aws_cloud()

    if is_real_aws or (is_in_docker and is_amd64 and not is_offline):
        # Do not skip any tests if they are executed either (1) against real AWS, or (2) in AMD64 Docker and not offline
        return

    skip_offline = pytest.mark.skip(
        reason="Test cannot be executed offline / in a restricted network environment. "
        "Add network connectivity and remove the --offline option when running "
        "the test."
    )
    only_in_docker = pytest.mark.skip(
        reason="Test requires execution inside Docker (e.g., to install system packages)"
    )
    only_on_amd64 = pytest.mark.skip(
        reason="Test uses features which are currently only supported for AMD64. Skipping in CI."
    )

    for item in items:
        if is_offline and "skip_offline" in item.keywords:
            item.add_marker(skip_offline)
        if not is_in_docker and "only_in_docker" in item.keywords:
            item.add_marker(only_in_docker)
        if is_in_ci and not is_amd64 and "only_on_amd64" in item.keywords:
            item.add_marker(only_on_amd64)
