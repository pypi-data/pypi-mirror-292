import logging
import os
import textwrap

import requests
from localstack import config, constants
from localstack.utils.bootstrap import get_gateway_url
from localstack.utils.container_utils.container_client import VolumeBind

LOG = logging.getLogger(__name__)


def test_extensions_auto_install_from_config_dir(
    pro_container, wait_for_localstack_ready, tmp_path, stream_container_logs
):
    config_dir = tmp_path / "conf.d"
    config_dir.mkdir()

    extensions_txt = config_dir / "extensions.txt"
    extensions_txt.write_text(
        textwrap.dedent(
            """
            localstack-extension-hello-world
            localstack-extension-httpbin
            """
        )
    )

    pro_container.config.volumes.add(
        VolumeBind(str(config_dir), config.Directories.defaults().config),
    )

    with pro_container.start() as running_container:
        stream_container_logs(pro_container)
        wait_for_localstack_ready(running_container, timeout=120)

        # check that the extensions directory was created on disk
        volume = pro_container.config.volumes.find_target_mapping(constants.DEFAULT_VOLUME_DIR)
        venv_path = os.path.join(volume.host_dir, "lib/extensions/python_venv")
        assert os.path.exists(venv_path)

        # check that the extensions list returns endpoint returns the correct extensions
        response = requests.get(get_gateway_url(pro_container) + "/_localstack/extensions/list")
        assert response.ok
        extensions = response.json()
        assert len(extensions) == 2, f"invalid number of extensions in {extensions}"
        extensions.sort(key=lambda v: v["distribution"]["name"])

        assert extensions[0]["distribution"]["name"] == "localstack-extension-hello-world"
        assert extensions[0]["status"] == {
            "is_initialized": True,
            "is_loaded": True,
            "load_error": False,
        }

        assert extensions[1]["distribution"]["name"] == "localstack-extension-httpbin"
        assert extensions[1]["status"] == {
            "is_initialized": True,
            "is_loaded": True,
            "load_error": False,
        }

    # make sure that, when we start the container again, the extensions are not re-installed
    with pro_container.start() as running_container:
        stream_container_logs(pro_container)
        wait_for_localstack_ready(running_container, timeout=120)
        logs = running_container.get_logs()
        assert "Requirement already satisfied: localstack-extension-hello-world" in logs
        assert "Requirement already satisfied: localstack-extension-httpbin" in logs


def test_extensions_auto_install_from_env_var(
    pro_container, wait_for_localstack_ready, stream_container_logs
):
    pro_container.config.env_vars["EXTENSION_AUTO_INSTALL"] = (
        "localstack-extension-httpbin,localstack-extension-hello-world"
    )

    with pro_container.start() as running_container:
        stream_container_logs(pro_container)
        wait_for_localstack_ready(running_container, timeout=120)

        # check that the extensions directory was created on disk
        volume = pro_container.config.volumes.find_target_mapping(constants.DEFAULT_VOLUME_DIR)
        venv_path = os.path.join(volume.host_dir, "lib/extensions/python_venv")
        assert os.path.exists(venv_path)

        # check that the extensions list returns endpoint returns the correct extensions
        response = requests.get(get_gateway_url(pro_container) + "/_localstack/extensions/list")
        assert response.ok
        extensions = response.json()
        assert len(extensions) == 2, f"invalid number of extensions in {extensions}"
        extensions.sort(key=lambda v: v["distribution"]["name"])

        assert extensions[0]["distribution"]["name"] == "localstack-extension-hello-world"
        assert extensions[0]["status"] == {
            "is_initialized": True,
            "is_loaded": True,
            "load_error": False,
        }

        assert extensions[1]["distribution"]["name"] == "localstack-extension-httpbin"
        assert extensions[1]["status"] == {
            "is_initialized": True,
            "is_loaded": True,
            "load_error": False,
        }

    # make sure that, when we start the container again, the extensions are not re-installed
    with pro_container.start() as running_container:
        stream_container_logs(pro_container)
        wait_for_localstack_ready(running_container, timeout=120)
        logs = running_container.get_logs()
        assert (
            "Extension localstack-extension-httpbin (LocalStack Extension: httpbin by LocalStack) already "
            "installed" in logs
        )
        assert (
            "Extension localstack-extension-hello-world (LocalStack Extension: Hello World by Thomas Rausch) "
            "already installed" in logs
        )
