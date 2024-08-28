import click
import pytest
from click.testing import CliRunner
from localstack.cli.localstack import create_with_plugins
from localstack.utils import bootstrap

cli: click.Group


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def set_api_key_configured(monkeypatch):
    monkeypatch.setattr(bootstrap, "is_api_key_configured", lambda: True)
    from localstack.pro.core.bootstrap.licensingv2 import LicensedLocalstackEnvironment

    monkeypatch.setattr(LicensedLocalstackEnvironment, "activate_license", lambda x: None)


@pytest.fixture
def state_pod_no_op(monkeypatch):
    def _no_op(_sef, *args, **kwargs):
        return True

    def _reachable():
        return

    from localstack.pro.core.bootstrap.pods_client import CloudPodsClient, StateService
    from localstack.pro.core.cli import cli

    monkeypatch.setattr(cli, "_assert_host_reachable", _reachable)
    monkeypatch.setattr(CloudPodsClient, "load", _no_op)
    monkeypatch.setattr(StateService, "export_pod", _no_op)
    monkeypatch.setattr(StateService, "import_pod", _no_op)


def test_load_from_platform_no_login_with_key(runner, state_pod_no_op, set_api_key_configured):
    """
    Test that it is possible to use Pro cloud pods commands without being logged in, but with configured API key.
    """
    localstack_cli = create_with_plugins()
    result = runner.invoke(localstack_cli.group, ["pod", "load", "my-pod"])
    assert "successfully" in result.output
    assert result.exit_code == 0


def test_export_state(runner, state_pod_no_op, set_api_key_configured, tmp_path):
    p = tmp_path / "pod.txt"
    p.write_text("test")
    localstack_cli = create_with_plugins()
    result = runner.invoke(localstack_cli.group, ["state", "export", f"{p}"])
    assert "successfully" in result.output
    assert result.exit_code == 0


def test_import_state(runner, state_pod_no_op, tmp_path, set_api_key_configured):
    p = tmp_path / "pod.txt"
    p.write_text("test")
    localstack_cli = create_with_plugins()
    result = runner.invoke(localstack_cli.group, ["state", "import", f"{p}"])
    assert "successfully" in result.output
    assert result.exit_code == 0
