# some generic tests to check whether store/backend serialization works
import dataclasses
from typing import Dict

from localstack.services.stores import AccountRegionBundle, BaseStore, LocalAttribute
from localstack.state import pickle

AWS_ACCOUNT_ID = "000000000000"


@dataclasses.dataclass
class SomeDataClass:
    number: int
    name: str = "foobar"


class MyStore(BaseStore):
    tags: Dict[str, Dict] = LocalAttribute(default=dict)
    data: SomeDataClass = LocalAttribute(default=lambda: SomeDataClass(10))


def test_account_region_bundle():
    obj = AccountRegionBundle("sqs", MyStore)

    obj[AWS_ACCOUNT_ID]["us-east-1"].tags["tags_01"] = {"foo": "bar"}
    obj[AWS_ACCOUNT_ID]["us-east-1"].data = SomeDataClass(11, "foo")

    # persistence roundtrip
    blob = pickle.dumps(obj)
    restored = pickle.loads(blob)

    # assert
    assert obj[AWS_ACCOUNT_ID]["us-east-1"].tags == restored[AWS_ACCOUNT_ID]["us-east-1"].tags
    assert obj[AWS_ACCOUNT_ID]["us-east-1"].tags == restored[AWS_ACCOUNT_ID]["us-east-1"].tags

    assert not restored[AWS_ACCOUNT_ID]["us-east-2"].tags


def test_account_region_bundle_acquire_locks():
    obj1 = AccountRegionBundle("sqs", MyStore)
    assert obj1[AWS_ACCOUNT_ID]["us-east-1"]

    # persistence roundtrip
    blob = pickle.dumps(obj1)
    restored = pickle.loads(blob)

    # try acquiring the locks (which should have been re-initialized on restoring)
    assert restored.lock.acquire(timeout=1)
    assert restored[AWS_ACCOUNT_ID].lock.acquire(timeout=1)
