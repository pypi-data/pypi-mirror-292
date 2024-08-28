from localstack.pro.core.persistence.reset import reset

from tests.unit.persistence.dummy import DummyService, MockServiceLifecycleHook


def test_reset_service():
    # setup fixture
    lifecycle_hook = MockServiceLifecycleHook()
    service = DummyService(lifecycle_hook=lifecycle_hook)

    service.store["000000000000"]["us-east-1"].strings["foo"] = "bar"
    service.store["000000000000"]["us-east-2"].strings["baz"] = "ed"
    service.backend["000000000000"]["us-east-1"].values.extend([0, 1, 2])

    # run state
    reset.reset_state(service)

    # check lifecycle hooks were called
    lifecycle_hook.on_before_state_reset.assert_called_once()
    lifecycle_hook.on_after_state_reset.assert_called_once()

    # check state was cleared
    assert not service.store["000000000000"]["us-east-1"].strings
    assert not service.store["000000000000"]["us-east-2"].strings
    assert not service.backend["000000000000"]["us-east-1"].values
