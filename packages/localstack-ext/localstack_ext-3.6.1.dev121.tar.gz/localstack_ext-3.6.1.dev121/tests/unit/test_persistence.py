import queue
import threading

import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric.padding import PKCS1v15
from localstack.pro.core.persistence.pods.merge.state_merge import add_missing_attributes
from localstack.pro.core.services.iot.models import IotStore
from localstack.services.stores import AccountRegionBundle
from localstack.state import pickle
from localstack.testing.config import TEST_AWS_ACCOUNT_ID, TEST_AWS_REGION_NAME
from localstack.utils.objects import Mock
from localstack.utils.threads import start_worker_thread
from moto.acm.models import CertBundle
from moto.ssm.models import ParameterDict, SimpleSystemManagerBackend


class A:
    pass


class B:
    pass


@pytest.fixture(scope="class", autouse=True)
def register_reducers():
    from localstack.pro.core.persistence.pickling.reducers import register

    register()


class TestPersistence:
    def test_store_object(self):
        obj1 = A()
        obj1.child = B()
        obj1.child.val = "test 123"
        obj1.child.grandchild = B()
        obj1.child.grandchild.num = 123

        blob = pickle.dumps(obj1)
        restored = pickle.loads(blob)

        assert restored.child.val == obj1.child.val
        assert restored.child.grandchild.num == obj1.child.grandchild.num

    def test_store_backend_with_lock_and_queue(self):
        obj1 = A()
        obj1.lock = threading.RLock()
        obj1.queue = queue.PriorityQueue()

        # acquire lock, put item to queue
        obj1.lock.acquire()
        obj1.queue.put(123)

        # persistence roundtrip
        blob = pickle.dumps(obj1)
        restored = pickle.loads(blob)

        # assert that the lock can be acquired by new thread again
        def _acquire(*_):
            restored.lock.acquire()
            _value = restored.queue.get(timeout=1)
            assert _value == 123
            result_queue.put(None)

        result_queue = queue.Queue()
        start_worker_thread(_acquire)
        result_queue.get(timeout=2)

    def test_restore_bundle_acquire_locks(self):
        obj1 = AccountRegionBundle("iot", IotStore)
        assert obj1[TEST_AWS_ACCOUNT_ID]["us-east-1"]

        # persistence roundtrip
        blob = pickle.dumps(obj1)
        restored = pickle.loads(blob)

        # try acquiring the locks (which should have been re-initialized on restoring)
        assert restored.lock.acquire(timeout=1)
        assert restored[TEST_AWS_ACCOUNT_ID].lock.acquire(timeout=1)

    def test_pickle_lock_different_owner(self):
        obj1 = Mock()
        obj1.lock = threading.Lock()
        obj1.rlock = threading.RLock()
        event = threading.Event()

        def _acquire(*args):
            obj1.lock.acquire()
            obj1.rlock.acquire()
            event.set()

        # acquire the lock in a different thread
        start_worker_thread(_acquire)
        assert event.wait(timeout=5)

        # persistence roundtrip
        blob = pickle.dumps(obj1)
        restored = pickle.loads(blob)

        # try acquiring the locks (which should have been re-initialized on restoring)
        assert restored.lock.acquire(timeout=1)
        assert restored.rlock.acquire(timeout=1)

    def test_add_missing_attributes(self):
        backend = SimpleSystemManagerBackend(
            region_name=TEST_AWS_REGION_NAME, account_id=TEST_AWS_ACCOUNT_ID
        )
        backend.put_parameter(
            name="param1",
            description="test 123",
            value="test",
            parameter_type="String",
            allowed_pattern="test",
            keyid="test",
            overwrite=True,
            tags=None,
            data_type="text",
            tier=None,
            policies=None,
        )

        # call add_missing_attributes, then marshall backend
        add_missing_attributes({TEST_AWS_REGION_NAME: backend})
        blob = pickle.dumps(backend)

        # roundtrip of restoring the backend from the binary blob
        restored = pickle.loads(blob)
        result = restored.get_parameter("param1")
        assert result.description == "test 123"

    def test_unpickle_defaultdict(self):
        obj = ParameterDict(account_id=TEST_AWS_ACCOUNT_ID, region_name=TEST_AWS_REGION_NAME)
        obj["p1"].append("v1")
        assert obj.region_name == TEST_AWS_REGION_NAME

        # marshalling roundtrip
        blob = pickle.dumps(obj)
        restored = pickle.loads(blob)

        # assert result
        assert restored["p1"] == ["v1"]
        assert restored.region_name == TEST_AWS_REGION_NAME

    def test_pickle_cryptography_rsa_key(self):
        obj = rsa.generate_private_key(public_exponent=65537, key_size=2048)

        plaintext = b"foobar 123"
        encrypted = obj.public_key().encrypt(plaintext, PKCS1v15())

        # perform key serialization roundtrip
        blob = pickle.dumps(obj)
        restored_key = pickle.loads(blob)

        # decrypt bytes with restored key
        result = restored_key.decrypt(
            encrypted,
            PKCS1v15(),
        )
        assert result == plaintext

    def test_pickle_acm_certificate(self):
        obj = CertBundle.generate_cert(
            "test@domain.com",
            account_id=TEST_AWS_ACCOUNT_ID,
            region="us-east-1",
        )
        # marshalling roundtrip
        blob = pickle.dumps(obj)
        restored: CertBundle = pickle.loads(blob)  # noqa
        assert obj._cert == restored._cert
