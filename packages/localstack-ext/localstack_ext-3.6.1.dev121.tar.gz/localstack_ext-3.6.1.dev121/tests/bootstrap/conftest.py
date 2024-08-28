import os
from pathlib import Path

import pytest
from localstack import config, constants
from localstack.dev.run.configurators import (
    EntryPointMountConfigurator,
    SourceVolumeMountConfigurator,
)
from localstack.dev.run.paths import HostPaths
from localstack.testing.pytest.container import ENV_TEST_CONTAINER_MOUNT_SOURCES, ContainerFactory
from localstack.utils.bootstrap import Container, ContainerConfigurators
from localstack.utils.container_utils.container_client import ContainerConfigurator


@pytest.fixture
def pro_container_configurators(
    tmp_path,
    docker_network,
) -> list[ContainerConfigurator]:
    # TODO: is this re-usable? if so: where to put it?

    volume = tmp_path / "localstack-volume"
    volume.mkdir(parents=True, exist_ok=True)

    configurators = [
        ContainerConfigurators.random_gateway_port,
        ContainerConfigurators.random_container_name,
        ContainerConfigurators.mount_docker_socket,
        ContainerConfigurators.mount_localstack_volume(volume),
        ContainerConfigurators.debug,
        ContainerConfigurators.network(docker_network),
        ContainerConfigurators.env_vars(
            {
                "ACTIVATE_PRO": "1",
            }
        ),
    ]

    if config.is_env_true(ENV_TEST_CONTAINER_MOUNT_SOURCES):
        workspace_dir = os.path.join(constants.LOCALSTACK_VENV_FOLDER, "..", "..")
        host_paths = HostPaths(workspace_dir=Path(workspace_dir).absolute(), volume_dir=volume)
        configurators.append(SourceVolumeMountConfigurator(host_paths=host_paths, pro=True))
        configurators.append(EntryPointMountConfigurator(host_paths=host_paths, pro=True))
    elif not os.getenv("LOCALSTACK_API_KEY"):
        raise ValueError("Cannot start LocalStack pro without LOCALSTACK_API_KEY")
    else:
        configurators.append(
            ContainerConfigurators.env_vars({"LOCALSTACK_API_KEY": os.getenv("LOCALSTACK_API_KEY")})
        )

    return configurators


@pytest.fixture
def pro_container(
    container_factory: ContainerFactory,
    pro_container_configurators,
) -> Container:
    return container_factory(configurators=pro_container_configurators)
