import os.path
from zipfile import ZipFile

import pytest
from localstack import config
from localstack.pro.core import constants
from localstack.pro.core.persistence.pods.diff.models import BackendType, OperationType
from localstack.pro.core.persistence.pods.load import CloudPodArchive
from localstack.pro.core.persistence.pods.manager import PodStateManager
from localstack.pro.core.persistence.pods.merge.visitors import DiffStateVisitor
from localstack.pro.core.persistence.reset import reset
from localstack.services.plugins import ServiceManager

from tests.unit.persistence.dummy import DummyCrossAccountService, DummyService


@pytest.fixture(name="dirs_data")
def patch_config_dirs_data(monkeypatch, tmp_path):
    monkeypatch.setattr("localstack.config.dirs.data", str(tmp_path))


@pytest.fixture
def patch_require_service(monkeypatch):
    monkeypatch.setattr(ServiceManager, "require", lambda *args: DummyService())


def test_save_load_roundtrip(tmp_path, dirs_data, patch_require_service):
    state_dir = tmp_path / "state"
    state_dir.mkdir()

    pod_path = state_dir / "my-pod.zip"

    # dummy service manager
    service_manager = ServiceManager()
    manager = PodStateManager(service_manager)

    service = DummyService()
    service.plugin_name = "sqs"

    service_manager.add_service(service)

    # create service state
    service.store["000000000000"]["us-east-1"].strings["foo"] = "bar"
    service.store["000000000000"]["us-east-2"].strings["baz"] = "ed"

    # save state
    with ZipFile(pod_path, "w") as pod:
        manager.extract_into(pod)
        archive = CloudPodArchive(zip_file=pod)
        assert archive.asset_directories
        # assume that a service sqs has assets under assets/sqs
        assert archive.asset_directories["sqs"] == f"{constants.ASSETS_DIRECTORY}/sqs"

    # lifecycle hooks were called
    service.lifecycle_hook.on_before_state_save.assert_called_once()
    service.lifecycle_hook.on_after_state_save.assert_called_once()

    # reset state
    reset.reset_state(service)

    assert not os.path.exists(os.path.join(config.dirs.data, "sqs"))
    assert not service.store["000000000000"]["us-east-1"].strings
    assert not service.store["000000000000"]["us-east-2"].strings

    # restore state
    with ZipFile(pod_path) as pod:
        manager.inject(pod)

    # check that the assets have been correctly restored
    assert os.path.exists(os.path.join(config.dirs.data, "sqs"))

    # lifecycle hooks were called
    service.lifecycle_hook.on_before_state_load.assert_called_once()
    service.lifecycle_hook.on_after_state_load.assert_called_once()
    # state was restored
    assert service.store["000000000000"]["us-east-1"].strings["foo"] == "bar"
    assert service.store["000000000000"]["us-east-2"].strings["baz"] == "ed"


def test_cross_account_and_region_restore(tmp_path, dirs_data, patch_require_service):
    state_dir = tmp_path / "state"
    state_dir.mkdir()

    pod_path = state_dir / "my-cross-pod.zip"

    # dummy service manager
    service_manager = ServiceManager()
    manager = PodStateManager(service_manager)

    service = DummyCrossAccountService()
    service.plugin_name = "s3"

    service_manager.add_service(service)

    # create local service state
    service.store["000000000000"]["us-east-1"].local_attribute["foo"] = "bar"
    service.store["000000000000"]["us-east-2"].local_attribute["baz"] = "ed"

    # create cross region service state
    service.store["000000000000"]["us-east-1"].cross_region_attribute["foo"] = "global"

    # create cross account service state
    service.store["000000000000"]["us-east-1"].cross_account_attribute["foo"] = "universal"

    # save state
    with ZipFile(pod_path, "w") as pod:
        manager.extract_into(pod)
        archive = CloudPodArchive(zip_file=pod)
        assert archive.asset_directories
        # assume that a service sqs has assets under assets/sqs
        assert archive.asset_directories["s3"] == f"{constants.ASSETS_DIRECTORY}/s3"

    # lifecycle hooks were called
    service.lifecycle_hook.on_before_state_save.assert_called_once()
    service.lifecycle_hook.on_after_state_save.assert_called_once()

    # reset state
    reset.reset_state(service)

    assert not os.path.exists(os.path.join(config.dirs.data, "s3"))
    assert not service.store["000000000000"]["us-east-1"].local_attribute
    assert not service.store["000000000000"]["us-east-2"].local_attribute

    assert not service.store["000000000000"]["us-east-1"].cross_region_attribute
    assert not service.store["000000000000"]["eu-west-1"].cross_region_attribute
    assert not service.store["000000000000"]["us-east-1"].cross_account_attribute
    assert not service.store["000000000001"]["us-east-1"].cross_account_attribute

    # restore state
    with ZipFile(pod_path) as pod:
        manager.inject(pod)

    # check that the assets have been correctly restored
    assert os.path.exists(os.path.join(config.dirs.data, "s3"))

    # lifecycle hooks were called
    service.lifecycle_hook.on_before_state_load.assert_called_once()
    service.lifecycle_hook.on_after_state_load.assert_called_once()

    # local state was restored
    assert service.store["000000000000"]["us-east-1"].local_attribute["foo"] == "bar"
    assert service.store["000000000000"]["us-east-2"].local_attribute["baz"] == "ed"
    assert not service.store["000000000000"]["eu-west-1"].local_attribute

    # cross region state was restored and is properly linked
    assert (
        service.store["000000000000"]["us-east-1"].cross_region_attribute
        is service.store["000000000000"]["eu-west-1"].cross_region_attribute
    )
    assert service.store["000000000000"]["eu-west-1"].cross_region_attribute["foo"] == "global"
    assert service.store["000000000000"]["us-east-1"].cross_region_attribute["foo"] == "global"
    assert service.store["000000000000"]["ap-south-1"].cross_region_attribute["foo"] == "global"

    # cross region state was restored and is properly linked
    assert (
        service.store["000000000000"]["us-east-1"].cross_account_attribute
        is service.store["000000000001"]["eu-west-1"].cross_account_attribute
    )
    assert service.store["000000000001"]["eu-west-1"].cross_account_attribute["foo"] == "universal"
    assert service.store["000000000002"]["us-east-1"].cross_account_attribute["foo"] == "universal"
    assert service.store["000000000003"]["ap-south-1"].cross_account_attribute["foo"] == "universal"


def test_account_and_region_addition(tmp_path, dirs_data, patch_require_service):
    state_dir = tmp_path / "state"
    state_dir.mkdir()

    pod_path = state_dir / "my-cross-pod.zip"

    # dummy service manager
    service_manager = ServiceManager()
    manager = PodStateManager(service_manager)

    service = DummyCrossAccountService("sns")

    service_manager.add_service(service)

    # create pod state
    service.store["000000000000"]["us-east-1"].local_attribute["foo"] = "bar"
    service.store["000000000001"]["us-east-1"].local_attribute["foo"] = "bar"

    with ZipFile(pod_path, "w") as pod:
        manager.extract_into(pod)
        archive = CloudPodArchive(zip_file=pod)

        # crate local state
        visitor = DiffStateVisitor(archive.zip)
        service = DummyCrossAccountService("sns")
        service_manager.add_service(service)
        service.store["000000000000"]["eu-central-1"].local_attribute["foo"] = "bar"

        visitor.visit(service.store)
        services_changes = visitor.operations["sns"]

        additions = [
            op for op in services_changes if op["operation_type"] == OperationType.ADDITION
        ]

        assert additions == [
            {
                "account_id": "000000000000",
                "region": "us-east-1",
                "service": "sns",
                "backend": BackendType.STORE,
                "operation_type": OperationType.ADDITION,
            },
            {
                "account_id": "000000000001",
                "region": "us-east-1",
                "service": "sns",
                "backend": BackendType.STORE,
                "operation_type": OperationType.ADDITION,
            },
        ]


def test_store_additions_and_modifications(tmp_path, dirs_data, patch_require_service):
    state_dir = tmp_path / "state"
    state_dir.mkdir()

    pod_path = state_dir / "my-cross-pod.zip"

    # dummy service manager
    service_manager = ServiceManager()
    manager = PodStateManager(service_manager)

    service = DummyCrossAccountService("sns")

    service_manager.add_service(service)

    # create pod state
    service.store["000000000000"]["us-east-1"].local_attribute["foo"] = "bar"
    service.store["000000000000"]["us-east-2"].local_attribute["foo"] = "bar"

    with ZipFile(pod_path, "w") as pod:
        manager.extract_into(pod)
        archive = CloudPodArchive(zip_file=pod)

        visitor = DiffStateVisitor(archive.zip)

        # create local state
        service = DummyCrossAccountService("sns")
        service_manager.add_service(service)
        service.store["000000000000"]["us-east-1"].local_attribute["foo"] = "bar"
        service.store["000000000000"]["us-east-2"].local_attribute["pippo"] = "pluto"

        visitor.visit(service.store)
        services_changes = visitor.operations["sns"]

        modifications = [
            op for op in services_changes if op["operation_type"] == OperationType.MODIFICATION
        ]
        additions = [
            op for op in services_changes if op["operation_type"] == OperationType.ADDITION
        ]

        assert modifications == [
            {
                "account_id": "000000000000",
                "region": "us-east-1",
                "service": "sns",
                "backend": BackendType.STORE,
                "operation_type": OperationType.MODIFICATION,
                "resources": [{"attribute": "attr_local_attribute", "attribute_key": "foo"}],
            }
        ]
        assert additions == [
            {
                "account_id": "000000000000",
                "region": "us-east-2",
                "service": "sns",
                "backend": BackendType.STORE,
                "operation_type": OperationType.ADDITION,
                "resources": [{"attribute": "attr_local_attribute", "attribute_key": "foo"}],
            }
        ]
