import os.path
import shutil
from unittest.mock import Mock

from localstack import config
from localstack.services.plugins import Service, ServiceLifecycleHook
from localstack.services.stores import (
    AccountRegionBundle,
    BaseStore,
    CrossAccountAttribute,
    CrossRegionAttribute,
    LocalAttribute,
)
from localstack.state import AssetDirectory, StateVisitor
from localstack.utils.files import mkdir
from moto.core.base_backend import BackendDict, BaseBackend


class MockServiceLifecycleHook(ServiceLifecycleHook):
    def __init__(self):
        # service lifecycle hook
        self.on_after_init = Mock()
        self.on_after_init.__name__ = "on_after_init"
        self.on_before_start = Mock()
        self.on_before_start.__name__ = "on_before_start"
        self.on_before_stop = Mock()
        self.on_before_stop.__name__ = "on_before_stop"
        self.on_exception = Mock()
        self.on_exception.__name__ = "on_exception"

        # state lifecycle hook
        self.on_before_state_reset = Mock()
        self.on_before_state_reset.__name__ = "on_before_state_reset"
        self.on_after_state_reset = Mock()
        self.on_after_state_reset.__name__ = "on_after_state_reset"
        self.on_before_state_save = Mock()
        self.on_before_state_save.__name__ = "on_before_state_save"
        self.on_after_state_save = Mock()
        self.on_after_state_save.__name__ = "on_after_state_save"
        self.on_before_state_load = Mock()
        self.on_before_state_load.__name__ = "on_before_state_load"
        self.on_after_state_load = Mock()
        self.on_after_state_load.__name__ = "on_after_state_load"


class DummyStore(BaseStore):
    strings: dict[str, str] = LocalAttribute(default=dict)


class DummyCrossRegionAccountStore(BaseStore):
    local_attribute: dict[str, str] = LocalAttribute(default=dict)
    cross_region_attribute: dict[str, str] = CrossRegionAttribute(default=dict)
    cross_account_attribute: dict[str, str] = CrossAccountAttribute(default=dict)


class DummyBackend(BaseBackend):
    def __init__(self, region_name, account_id):
        super().__init__(region_name, account_id)
        self.values = []
        self.string = None


class DummyBackendWithReset(BaseBackend):
    def __init__(self, region_name, account_id):
        super().__init__(region_name, account_id)
        self.values = []
        self.string = None

    def reset(self):
        self.values = []
        self.string = "default"


class DummyService(Service):
    def __init__(self, name: str = "sqs", lifecycle_hook=None):
        super().__init__(name, lifecycle_hook=lifecycle_hook or MockServiceLifecycleHook())
        self.store = AccountRegionBundle(name, DummyStore)
        self.backend = BackendDict(DummyBackend, name)

    def accept_state_visitor(self, visitor: StateVisitor):
        visitor.visit(self.store)
        visitor.visit(self.backend)

        dummy_dir = os.path.join(config.dirs.data, self.name())
        mkdir(dummy_dir)
        with open(os.path.join(dummy_dir, "dummy.txt"), "w") as f:
            f.write("dummy")
        visitor.visit(AssetDirectory(self.name(), dummy_dir))

    def reset_dummy_asset(self):
        dummy_dir = os.path.join(config.dirs.data, self.name())
        if os.path.exists(dummy_dir):
            shutil.rmtree(dummy_dir)


class DummyCrossAccountService(DummyService):
    def __init__(self, name: str = "sqs", lifecycle_hook=None):
        super().__init__(name, lifecycle_hook)
        self.store = AccountRegionBundle(name, DummyCrossRegionAccountStore)
