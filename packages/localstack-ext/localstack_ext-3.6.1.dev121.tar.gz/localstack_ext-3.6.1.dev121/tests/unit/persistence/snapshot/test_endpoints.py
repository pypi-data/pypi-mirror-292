import json

from localstack.http import Router
from localstack.http.dispatcher import handler_dispatcher
from localstack.pro.core.persistence.snapshot.endpoints import StateResource
from localstack.pro.core.persistence.snapshot.manager import SnapshotManager
from localstack.services.plugins import ServiceManager
from werkzeug import Request
from werkzeug.test import Client

from tests.unit.persistence.dummy import DummyService


def test_save_load_roundtrip(tmp_path):
    state_dir = tmp_path / "state"
    state_dir.mkdir()

    # dummy service manager
    service_manager = ServiceManager()
    manager = SnapshotManager(service_manager, str(state_dir))

    # create endpoints wsgi application and testing client
    router = Router(handler_dispatcher())
    router.add(StateResource(manager))

    sqs = DummyService()
    sqs.plugin_name = "sqs"
    service_manager.add_service(sqs)

    sns = DummyService()
    sns.plugin_name = "sns"
    service_manager.add_service(sns)

    # create service state
    sqs.store["000000000000"]["us-east-1"].strings["foo"] = "bar"
    sqs.store["000000000000"]["us-east-2"].strings["baz"] = "ed"

    sns.store["000000000000"]["us-east-1"].strings["bar"] = "ed"

    # save state
    c = Client(Request.application(router.dispatch))

    # save the state into a pod
    response = c.post("/_localstack/state/save")
    assert response.mimetype == "application/x-ndjson"
    assert response.data
    lines = response.get_data(as_text=True).strip().split("\n")
    assert len(lines) == 2
    events = [json.loads(line) for line in lines]
    assert {"service": "sqs", "status": "ok"} in events
    assert {"service": "sns", "status": "ok"} in events

    # lifecycle hooks were called
    sqs.lifecycle_hook.on_before_state_save.assert_called_once()
    sqs.lifecycle_hook.on_after_state_save.assert_called_once()
    sns.lifecycle_hook.on_before_state_save.assert_called_once()
    sns.lifecycle_hook.on_after_state_save.assert_called_once()
