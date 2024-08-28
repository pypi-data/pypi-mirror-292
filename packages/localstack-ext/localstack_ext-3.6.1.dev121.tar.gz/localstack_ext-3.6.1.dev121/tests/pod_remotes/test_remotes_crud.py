import pytest
from localstack import config
from localstack.pro.core.bootstrap.pods.remotes.api import CloudPodsRemotesClient
from localstack.pro.core.persistence.remotes.manager import Remote, YAMLRemoteManager
from localstack.utils.strings import short_uid


@pytest.fixture
def remote_manager(tmp_path):
    remotes_file = tmp_path / "remotes.yaml"
    yield YAMLRemoteManager(remotes_file.resolve())


def test_add_remote(remote_manager):
    name = f"test-{short_uid()}"
    remote = Remote(name=name, protocols=["http", "https"], url="http://localhost:8080")
    remote_manager.add_remote(remote)
    data: list[dict[str, str]] = remote_manager.list_remotes()
    assert len(data) == 1
    assert data[0]["name"] == name
    assert data[0]["protocols"] == ["http", "https"]
    assert data[0]["url"] == "http://localhost:8080"
    # test get remote
    remote = remote_manager.get_remote(name)
    assert remote
    assert remote.name == name
    assert not remote_manager.get_remote("not-there")


def test_read_empty_remote(remote_manager):
    results = remote_manager.list_remotes()
    assert not results


def test_delete_remote(remote_manager):
    name = f"test-{short_uid()}"
    remote = Remote(name=name, protocols=["http", "https"], url="http://localhost:8080")
    remote_manager.add_remote(remote)
    remotes = remote_manager.list_remotes()
    remotes = [remote for remote in remotes if remote["name"] == name]
    assert len(remotes) == 1

    # delete remote
    remote_manager.delete_remote(name)
    remotes = remote_manager.list_remotes()
    remotes = [remote for remote in remotes if remote["name"] == name]
    assert not remotes

    # delete remote that doesn't exist
    remote_manager.delete_remote("not-there")


def test_override_remote(remote_manager):
    name = f"test-{short_uid()}"
    remote = Remote(name=name, protocols=["http", "https"], url="http://localhost:8080")
    remote_manager.add_remote(remote)
    remote = remote_manager.get_remote(remote_name=name)
    assert remote.name == name
    assert remote.url == "http://localhost:8080"

    # override remote
    remote = Remote(name=name, protocols=["http", "https"], url="s3://localhost:8080")
    remote_manager.add_remote(remote)
    remote = remote_manager.get_remote(remote_name=name)
    assert remote.name == name
    assert remote.url == "s3://localhost:8080", "remote not overridden"


def test_remotes_client(localstack_session, monkeypatch):
    """Perform CRUD operations via the remotes client"""
    monkeypatch.setattr(
        config,
        "LOCALSTACK_HOST",
        config.HostAndPort(host="localhost.localstack.cloud", port=localstack_session.port),
    )
    remotes_client = CloudPodsRemotesClient()

    # create remote
    name = f"test-{short_uid()}"
    remotes_client.create_remote(name=name, protocols=["platform"])

    # get remote
    remote = remotes_client.get_remote(name=name)
    assert remote["name"] == name

    # list remotes
    remotes = remotes_client.get_remotes()
    remote = [remote for remote in remotes if remote["name"] == name][0]
    assert remote["name"] == name

    # delete remote
    remotes_client.delete_remote(name=name)

    # assert that remote no longer exists
    with pytest.raises(Exception):
        remotes_client.get_remote(name=name)
