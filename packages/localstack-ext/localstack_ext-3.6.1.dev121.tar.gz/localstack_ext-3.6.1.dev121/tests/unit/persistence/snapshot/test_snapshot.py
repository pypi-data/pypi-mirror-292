from localstack.pro.core.persistence.snapshot.load import LoadSnapshotVisitor
from localstack.pro.core.persistence.snapshot.save import SaveSnapshotVisitor

from tests.unit.persistence.dummy import DummyService


def test_save_load_roundtrip(tmp_path):
    state_dir = tmp_path / "state"
    state_dir.mkdir()

    service = DummyService()
    service.store["000000000000"]["us-east-1"].strings["foo"] = "bar"
    service.store["000000000000"]["us-east-2"].strings["baz"] = "ed"
    service.backend["000000000000"]["us-east-1"].values.extend([0, 1, 2])

    save_visitor = SaveSnapshotVisitor("sqs", str(state_dir))
    service.accept_state_visitor(save_visitor)

    # restore the pickled service
    restored = DummyService()
    load_visitor = LoadSnapshotVisitor("sqs", str(state_dir))
    restored.accept_state_visitor(load_visitor)

    assert restored.store["000000000000"]["us-east-1"].strings["foo"] == "bar"
    assert restored.store["000000000000"]["us-east-2"].strings["baz"] == "ed"
    assert restored.backend["000000000000"]["us-east-1"].values == [0, 1, 2]
