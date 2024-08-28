import os.path

from localstack import constants
from localstack.pro.core.bootstrap.licensingv2 import LicenseParser
from localstack.utils.bootstrap import ContainerConfigurators


def test_api_key_activation_is_cached(
    pro_container,
    wait_for_localstack_ready,
):
    """Test to check that a license activation with an API key is done offline on the second time."""
    with pro_container.start() as running_container:
        wait_for_localstack_ready(running_container, timeout=120)

        # check license file was created and id is printed in the logs
        volume_dir = pro_container.config.volumes.find_target_mapping(
            constants.DEFAULT_VOLUME_DIR
        ).host_dir
        with open(os.path.join(volume_dir, "cache", "license.json"), "rb") as fd:
            license_ = LicenseParser().parse(fd.read())

        assert license_.id
        license_log_string = license_.to_log_string()

        logs = running_container.get_logs()
        assert f"Successfully requested and activated new license {license_log_string}" in logs

    # restart localstack and check that an offline activation was made
    with pro_container.start() as running_container:
        wait_for_localstack_ready(running_container, timeout=120)

        logs = running_container.get_logs()
        assert "Successfully requested and activated new license" not in logs
        assert f"Successfully activated cached license {license_log_string}" in logs

    # try again with a failing endpoint (should start anyway)
    pro_container.configure(
        ContainerConfigurators.env_vars({"API_ENDPOINT": "http://localhost:123456"})
    )
    with pro_container.start() as running_container:
        wait_for_localstack_ready(running_container, timeout=120)

        logs = running_container.get_logs()
        assert "Successfully requested and activated new license" not in logs
        assert f"Successfully activated cached license {license_log_string}" in logs
