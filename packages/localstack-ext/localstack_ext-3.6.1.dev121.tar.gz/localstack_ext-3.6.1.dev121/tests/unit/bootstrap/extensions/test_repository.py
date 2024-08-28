import subprocess
import sys

import pytest
import requests
from localstack.pro.core.bootstrap.extensions.repository import (
    ExtensionsRepository,
    SubprocessLineStream,
)
from localstack.utils.files import rm_rf
from localstack.utils.venv import VirtualEnvironment


class TestSubprocessLineStream:
    def test_open_and_iterate_over_stream(self):
        with SubprocessLineStream.open([sys.executable, "--help"]) as stream:
            lines = iter(stream)

            assert "usage:" in next(lines)

            # consume the rest of the stream
            for _ in lines:
                pass

            assert stream.process.returncode == 0

    def test_raises_error(self):
        with pytest.raises(subprocess.CalledProcessError) as e:
            with SubprocessLineStream.open([sys.executable, "--foo"]) as stream:
                for _ in stream:
                    pass

            assert e.value.returncode != 0

    def test_wrapping_with_byte_mode(self):
        p = subprocess.Popen(["echo", "foobar"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        for line in SubprocessLineStream(p):
            assert line == b"foobar"

        assert p.returncode == 0


class TestExtensionRepository:
    @pytest.fixture()
    def extension_repository(self, tmp_path):
        venv_path = tmp_path / "venv"
        venv_path.mkdir()
        venv = VirtualEnvironment(venv_path)
        venv.create()

        extension_repository = ExtensionsRepository(venv)
        yield extension_repository

        # venvs tend to be quite large, so make sure we remove them
        rm_rf(str(venv_path))

    def test_pip_show(self, extension_repository):
        assert extension_repository.pip_show("localstack-extensions-stripe") is None

        pip_meta = extension_repository.pip_show("pip")
        assert pip_meta["Name"] == "pip"

        # first condition for pip<24.0.0, second condition for pip>=24.0.0
        assert pip_meta["Author"] == "The pip developers" or pip_meta["Author-email"].startswith(
            "The pip developers"
        )

    def test_install_and_uninstall(self, extension_repository):
        package = "localstack-extension-httpbin"

        # make sure it's not installed
        assert extension_repository.pip_show(package) is None

        # install it
        extensions = []
        for event in extension_repository.run_install(package):
            print(event)
            if event["event"] == "extension":
                extensions.append(event)

        assert extensions, "expected at least one extension to be returned by the installer"
        assert extensions[0]["extra"]["distribution"]["name"] == package
        assert extension_repository.pip_show(package)["Name"] == package

        # try to install it again, nothing happens but no error is raised
        extensions = []
        for event in extension_repository.run_install(package):
            print(event)
            if event["event"] == "extension":
                extensions.append(event)
        assert not extensions

        # uninstall
        for event in extension_repository.run_uninstall(package):
            print(event)

        assert extension_repository.pip_show(package) is None

    def test_install_invalid_package(self, extension_repository):
        package = "package-that-does-not-exist"

        # make sure the package really doesn't exist before installing to avoid attacks
        assert requests.get(f"https://pypi.org/simple/{package}/").status_code == 404

        installer = extension_repository.run_install(package)

        errors = []
        for event in installer:
            if event["event"] == "error":
                errors.append(event)

        assert errors
        assert f"Could not resolve package {package}" in errors[0]["message"]
