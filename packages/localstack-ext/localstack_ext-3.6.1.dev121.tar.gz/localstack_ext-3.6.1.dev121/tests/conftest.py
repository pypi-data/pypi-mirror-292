import pytest
from localstack import config

pytest_plugins = [
    "tests.aws.fixtures",
    "localstack.testing.pytest.bootstrap",
    "localstack.testing.pytest.container",
    "localstack_snapshot.pytest.snapshot",
    "localstack.testing.pytest.fixtures",
    "localstack.testing.pytest.in_memory_localstack",
    "localstack.testing.pytest.marking",
    "localstack.testing.pytest.marker_report",
    "localstack.testing.pytest.validation_tracking",
    "localstack.testing.pytest.path_filter",
    "localstack.testing.pytest.stepfunctions.fixtures",
]

if config.is_collect_metrics_mode():
    import os
    from datetime import datetime

    import localstack.testing.pytest.metric_collection
    from localstack.utils.strings import short_uid

    localstack.testing.pytest.metric_collection.BASE_PATH = os.path.join(
        os.path.dirname(__file__), "../../target/metric_reports"
    )
    localstack.testing.pytest.metric_collection.FNAME_RAW_DATA_CSV = os.path.join(
        localstack.testing.pytest.metric_collection.BASE_PATH,
        f"metric-report-raw-data-{datetime.utcnow().strftime('%Y-%m-%d__%H_%M_%S')}-{short_uid()}.csv",
    )
    pytest_plugins.append("localstack.testing.pytest.metric_collection")


# FIXME: remove this, quick hack to prevent the HTTPServer fixture to spawn non-daemon threads
def pytest_sessionstart(session):
    import threading

    try:
        from localstack.utils.patch import Patch
        from pytest_httpserver import HTTPServer, HTTPServerError
        from werkzeug.serving import make_server

        def start_non_daemon_thread(self):
            if self.is_running():
                raise HTTPServerError("Server is already running")

            self.server = make_server(
                self.host, self.port, self.application, ssl_context=self.ssl_context
            )
            self.port = self.server.port  # Update port (needed if `port` was set to 0)
            self.server_thread = threading.Thread(target=self.thread_target, daemon=True)
            self.server_thread.start()

        patch = Patch(name="start", obj=HTTPServer, new=start_non_daemon_thread)
        patch.apply()

    except ImportError:
        # this will be executed in the CLI tests as well, where we don't have the pytest_httpserver dependency
        # skip in that case
        pass


# Following fixtures are duplicated both in community codebase and ext codebase.
# This is to make sure PyCharm code completion works.


@pytest.fixture(scope="session")
def aws_session():
    """
    This fixture returns the Boto Session instance for testing.
    """
    from localstack.testing.aws.util import base_aws_session

    return base_aws_session()


@pytest.fixture(scope="session")
def secondary_aws_session():
    """
    This fixture returns the Boto Session instance for testing a secondary account.
    """
    from localstack.testing.aws.util import secondary_aws_session

    return secondary_aws_session()


@pytest.fixture(scope="session")
def aws_client_factory(aws_session):
    """
    This fixture returns a client factory for testing.

    Use this fixture if you need to use custom endpoint or Boto config.
    """
    from localstack.testing.aws.util import base_aws_client_factory

    return base_aws_client_factory(aws_session)


@pytest.fixture(scope="session")
def secondary_aws_client_factory(secondary_aws_session):
    """
    This fixture returns a client factory for testing a secondary account.

    Use this fixture if you need to use custom endpoint or Boto config.
    """
    from localstack.testing.aws.util import base_aws_client_factory

    return base_aws_client_factory(secondary_aws_session)


@pytest.fixture(scope="session")
def aws_client(aws_client_factory):
    """
    This fixture can be used to obtain Boto clients for testing.

    The clients are configured with the primary testing credentials.
    """
    from localstack.testing.aws.util import base_testing_aws_client

    return base_testing_aws_client(aws_client_factory)


@pytest.fixture(scope="session")
def secondary_aws_client(secondary_aws_client_factory):
    """
    This fixture can be used to obtain Boto clients for testing a secondary account.

    The clients are configured with the secondary testing credentials.
    """
    from localstack.testing.aws.util import base_testing_aws_client

    return base_testing_aws_client(secondary_aws_client_factory)
