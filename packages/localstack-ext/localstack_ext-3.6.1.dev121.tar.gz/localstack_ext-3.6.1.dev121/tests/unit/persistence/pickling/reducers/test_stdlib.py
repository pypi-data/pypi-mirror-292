import contextvars
import queue
import threading
from collections import defaultdict

from localstack.state import pickle


class Dummy:
    pass


def test_store_backend_with_lock_and_queue():
    obj1 = Dummy()
    obj1.lock = threading.RLock()
    obj1.queue = queue.PriorityQueue()

    # acquire lock, put item to queue
    obj1.lock.acquire()
    obj1.queue.put(123)

    # persistence roundtrip
    blob = pickle.dumps(obj1)
    restored = pickle.loads(blob)

    done = threading.Event()

    # assert that the lock can be acquired by new thread again
    def _acquire():
        assert restored.lock.acquire(timeout=2)
        _value = restored.queue.get(timeout=2)
        assert _value == 123
        done.set()

    threading.Thread(target=_acquire).start()

    assert done.wait(2)


class DefaultdictWithProperties(defaultdict):
    tags: dict[str, str]
    number: int

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


def test_defaultdict_with_properties():
    obj = DefaultdictWithProperties(list)

    obj.tags = {"foo": "bar"}
    obj.number = 10

    obj["list1"].append(1)
    obj["list1"].append(2)

    # persistence roundtrip
    blob = pickle.dumps(obj)
    restored = pickle.loads(blob)

    assert restored.tags == obj.tags
    assert restored.number == obj.number
    assert obj["list1"] == restored["list1"]


class DictWithProperties(dict):
    tags: dict[str, str]
    number: int

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


def test_dict_with_properties():
    obj = DictWithProperties({"list1": [1, 2]})

    obj.tags = {"foo": "bar"}
    obj.number = 10

    # persistence roundtrip
    blob = pickle.dumps(obj)
    restored = pickle.loads(blob)

    assert restored.tags == obj.tags
    assert restored.number == obj.number
    assert obj["list1"] == restored["list1"]


def test_empty_defaultdict():
    obj = defaultdict(dict)

    # persistence roundtrip
    blob = pickle.dumps(obj)
    restored = pickle.loads(blob)

    assert restored == obj


def test_defaultdict_with_lambda():
    obj = defaultdict(lambda: "foo")

    assert obj["bar"] == "foo"

    # persistence roundtrip
    blob = pickle.dumps(obj)
    restored = pickle.loads(blob)

    assert restored["baz"] == "foo"

    assert restored == {
        "bar": "foo",
        "baz": "foo",
    }


def test_pickle_contextvars_context_var():
    var = contextvars.ContextVar("my_var")
    var.set("Is set")

    blob = pickle.dumps(var)
    restored = pickle.loads(blob)

    assert restored.get() == "Is set"


def test_pickle_contextvars_context():
    # more details here https://peps.python.org/pep-0567/
    original_context = contextvars.Context()
    var = contextvars.ContextVar("var")
    var.set("spam")

    # set new value for the var in the context
    original_context.run(var.set, "ham")
    # outside the context the value of the var should still be 'spam'
    assert var.get() == "spam"
    # the variable inside the context has changed to 'ham'
    assert original_context[var] == "ham"
    blob = pickle.dumps(original_context)

    # check that a new context does not impact the previous one
    new_context = contextvars.copy_context()
    new_context.run(var.set, "jam")
    assert new_context[var] == "jam"
    assert original_context[var] == "ham"

    restored = pickle.loads(blob)
    # check the original asserts after the unmarshalling
    assert restored[var] == "ham"
    assert var.get() == "spam"
