import os

import requests
from localstack.testing.pytest.container import ContainerFactory
from localstack.utils.bootstrap import ContainerConfigurators, get_gateway_url


def test_pro_startup_without_root_permissions_without_mount(
    pro_container, wait_for_localstack_ready, tmp_path, stream_container_logs
):
    # set uid to 1000
    pro_container.config.user = "1000"
    pro_container.config.volumes.mappings.clear()
    running_container = pro_container.start()
    stream_container_logs(pro_container)
    wait_for_localstack_ready(running_container, timeout=30)

    gateway_url = get_gateway_url(pro_container)

    # check if pro services are up
    response = requests.get(f"{gateway_url}/_localstack/health")
    assert response.ok
    health_result = response.json()
    assert "ecs" in health_result["services"]


def test_setting_localstack_host_only(
    container_factory: ContainerFactory, wait_for_localstack_ready, stream_container_logs
):
    pro_container = container_factory(
        configurators=[
            ContainerConfigurators.random_container_name,
            ContainerConfigurators.mount_docker_socket,
            ContainerConfigurators.debug,
            ContainerConfigurators.env_vars(
                {
                    "ACTIVATE_PRO": "1",
                    "LOCALSTACK_API_KEY": os.getenv("LOCALSTACK_API_KEY"),
                    "LOCALSTACK_HOST": "localhost.localstack.cloud:443",
                }
            ),
            ContainerConfigurators.port(443),
        ]
    )

    stream_container_logs(pro_container)
    running_container = pro_container.start()
    wait_for_localstack_ready(running_container)

    response = requests.get("http://localhost.localstack.cloud:443/_localstack/health", timeout=5)
    assert response.ok
    health_result = response.json()
    assert "ecs" in health_result["services"]
