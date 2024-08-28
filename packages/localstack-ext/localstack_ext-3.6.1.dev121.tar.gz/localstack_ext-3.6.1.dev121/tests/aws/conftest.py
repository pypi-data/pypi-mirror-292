"""
Pytest configuration that spins up a single localstack instance that is shared across test modules.
See: https://docs.pytest.org/en/6.2.x/fixture.html#conftest-py-sharing-fixtures-across-multiple-files

It is thread/process safe to run with pytest-parallel, however not for pytest-xdist.
"""

import logging
import os
from typing import TYPE_CHECKING, Optional

import pytest
from localstack import config as localstack_config
from localstack.constants import DEFAULT_PORT_EDGE, ENV_INTERNAL_TEST_RUN
from localstack.pro.core.bootstrap.licensingv2 import ENV_LOCALSTACK_API_KEY
from localstack.testing.scenario.provisioning import InfraProvisioner
from localstack.testing.snapshots.transformer_utility import (
    SNAPSHOT_BASIC_TRANSFORMER,
    SNAPSHOT_BASIC_TRANSFORMER_NEW,
)
from localstack.utils.aws.arns import get_partition
from localstack.utils.http import safe_requests
from localstack_snapshot.snapshots.transformer import (
    RegexTransformer,
)

from tests.aws.services.docdb.test_docdb import TestDocDB
from tests.aws.services.kinesisanalytics.test_kinesisanalytics import TestKinesisAnalytics
from tests.aws.services.neptune.test_neptune import TestNeptune
from tests.aws.services.rds.test_rds import TestRdsMssql

from .test_serverless import TestServerless
from .test_terraform import TestTerraform

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

    # configure for localstack run
    os.environ[ENV_INTERNAL_TEST_RUN] = "1"
    if ENV_LOCALSTACK_API_KEY not in os.environ:
        os.environ[ENV_LOCALSTACK_API_KEY] = "test"

    # FIXME: note that this should be the same as in tests/integration/conftest.py since both are currently
    #  run in the same CI test step, but only one localstack instance is started for both.
    safe_requests.verify_ssl = False
    localstack_config.FORCE_SHUTDOWN = False

    if not os.environ.get("GATEWAY_LISTEN"):
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


def pytest_runtestloop(session):
    # second pytest lifecycle hook (before test runner starts)

    if not session.items:
        return

    if session.config.option.collectonly:
        return

    # initialize certain tests asynchronously to reduce overall test time
    for item in session.items:
        parent_name = str(item.parent.cls).lower()
        # set flag that terraform will be used
        if "terraform" in parent_name:
            TestTerraform.init_async()
        elif "serverless" in parent_name:
            TestServerless.init_async()
        elif "kinesisanalytics" in parent_name:
            TestKinesisAnalytics.init_async()
        elif "neptune" in parent_name:
            TestNeptune.init_async()
        elif "docdb" in parent_name:
            TestDocDB.init_async()
        elif "mssql" in parent_name:
            TestRdsMssql.init_async()


@pytest.fixture(scope="function")
def snapshot(request, _snapshot_session: "SnapshotSession", account_id, region_name):
    _snapshot_session.add_transformer(RegexTransformer(account_id, "1" * 12), priority=2)
    _snapshot_session.add_transformer(RegexTransformer(region_name, "<region>"), priority=2)
    _snapshot_session.add_transformer(
        RegexTransformer(f"arn:{get_partition(region_name)}:", "arn:<partition>:"), priority=2
    )

    from tests.aws.transformer_utility_ext import TransformerUtilityExt

    # override transformer for the snapshot fixture in community
    _snapshot_session.transform = TransformerUtilityExt()

    # TODO: this should be incrementally removed
    exemptions = [
        "tests/aws/services/amplify",
        "tests/aws/services/apigateway",
        "tests/aws/services/appconfig",
        "tests/aws/services/cloudformation",
        "tests/aws/services/cloudfront",
        "tests/aws/services/cloudtrail",
        "tests/aws/services/cognito",
        "tests/aws/services/ecr",
        "tests/aws/services/ecs",
        "tests/aws/services/efs",
        "tests/aws/services/eks",
        "tests/aws/services/elasticache",
        "tests/aws/services/elb",
        "tests/aws/services/iam",
        "tests/aws/services/iot",
        "tests/aws/services/kms",
        "tests/aws/services/kafka",
        "tests/aws/services/lambda_",
        "tests/aws/services/mq",
        "tests/aws/services/neptune",
        "tests/aws/services/qldb",
        "tests/aws/services/ram",
        "tests/aws/services/route53",
        "tests/aws/services/s3",
        "tests/aws/services/serverlessrepo",
        "tests/aws/services/timestream",
    ]

    if any([e in request.fspath.dirname for e in exemptions]):
        _snapshot_session.add_transformer(SNAPSHOT_BASIC_TRANSFORMER, priority=2)
    else:
        _snapshot_session.add_transformer(SNAPSHOT_BASIC_TRANSFORMER_NEW, priority=2)

    yield _snapshot_session


# Note: Don't move this into testing lib
@pytest.fixture(scope="session")
def cdk_template_path():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "cdk_templates"))


# Note: Don't move this into testing lib
@pytest.fixture(scope="session")
def infrastructure_setup(cdk_template_path, aws_client):
    def _infrastructure_setup(
        namespace: str, force_synth: Optional[bool] = False
    ) -> InfraProvisioner:
        """
        :param namespace: repo-unique identifier for this CDK app.
            A directory with this name will be created at `tests/aws/cdk_templates/<namespace>/`
        :param force_synth: set to True to always re-synth the CDK app
        :return: an instantiated CDK InfraProvisioner which can be used to deploy a CDK app
        """
        return InfraProvisioner(
            base_path=cdk_template_path,
            aws_client=aws_client,
            namespace=namespace,
            force_synth=force_synth,
            persist_output=True,
        )

    return _infrastructure_setup
