import pytest
from localstack.pro.core.testing.pytest.persistence import (
    LocalstackDevContainerServer,
    LocalstackPersistenceMode,
    LocalstackSession,
)
from localstack.utils.bootstrap import ContainerConfigurators
from localstack.utils.docker_utils import reserve_available_container_port
from localstack.utils.patch import Patch


@pytest.fixture
def localstack_session(start_localstack_session):
    return start_localstack_session()


@pytest.fixture
def start_localstack_session(tmp_path):
    sessions = []

    def _create(
        env_vars: dict | None = None,
        port: int | None = None,
        bind_host: str | None = None,
        disable_external_service_ports: bool = False,
    ):
        port = port or reserve_available_container_port()
        session = LocalstackSession(
            LocalstackPersistenceMode.cloudpods,
            port=port,
            tmp_dir=str(tmp_path),
            bind_host=bind_host,
        )

        # disable DNS server, to avoid issues when resolving domain names for S3 presigned URLs from real AWS
        session.env_vars["DNS_ADDRESS"] = "0"

        # disable extended service ports, to avoid port conflicts
        patch = None
        if disable_external_service_ports:

            def _get_container_configurators(fn, self):
                result = fn(self)
                result = [cfg for cfg in result if cfg != ContainerConfigurators.service_port_range]
                return result

            patch = Patch.function(
                LocalstackDevContainerServer._get_container_configurators,
                _get_container_configurators,
            )
            patch.apply()

        try:
            session.env_vars.update(env_vars or {})
            session.start(60)
            sessions.append(session)
        finally:
            patch and patch.undo()

        return session

    yield _create

    for session in sessions:
        session.stop(30)
