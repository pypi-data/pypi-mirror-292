from localstack.pro.core.persistence.snapshot.manager import SnapshotManager
from localstack.services.plugins import ServiceManager

from tests.unit.persistence.dummy import DummyService


def test_save_load_roundtrip(tmp_path):
    state_dir = tmp_path / "state"
    state_dir.mkdir()

    # dummy service manager
    service_manager = ServiceManager()
    manager = SnapshotManager(service_manager, str(state_dir))

    service = DummyService()
    service.plugin_name = "sqs"

    service_manager.add_service(service)

    # create service state
    service.store["000000000000"]["us-east-1"].strings["foo"] = "bar"
    service.store["000000000000"]["us-east-2"].strings["baz"] = "ed"

    # save state
    manager.save("sqs")

    # lifecycle hooks were called
    service.lifecycle_hook.on_before_state_save.assert_called_once()
    service.lifecycle_hook.on_after_state_save.assert_called_once()

    # reset state
    service.store.reset()
    assert not service.store["000000000000"]["us-east-1"].strings
    assert not service.store["000000000000"]["us-east-2"].strings

    # restore state
    manager.load("sqs")

    # lifecycle hooks were called
    service.lifecycle_hook.on_before_state_load.assert_called_once()
    service.lifecycle_hook.on_after_state_load.assert_called_once()
    # state was restored
    assert service.store["000000000000"]["us-east-1"].strings["foo"] == "bar"
    assert service.store["000000000000"]["us-east-2"].strings["baz"] == "ed"
