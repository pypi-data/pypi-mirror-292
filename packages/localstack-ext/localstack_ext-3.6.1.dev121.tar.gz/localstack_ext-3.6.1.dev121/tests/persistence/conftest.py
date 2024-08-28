import logging

import pytest

LOG = logging.getLogger(__name__)


@pytest.hookimpl()
def pytest_addhooks(pluginmanager):
    from localstack.pro.core.testing.pytest.persistence import PersistenceTestPlugin

    if pluginmanager.register(PersistenceTestPlugin(), "PersistenceTestPlugin") is None:
        LOG.warning(
            "Persistence test plugin is disabled! Persistence tests will not work correctly."
        )
