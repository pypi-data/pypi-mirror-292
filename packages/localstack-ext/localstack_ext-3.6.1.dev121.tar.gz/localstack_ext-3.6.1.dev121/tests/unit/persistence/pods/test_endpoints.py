import io
import json
import os

from localstack import config
from localstack.http import Router
from localstack.http.dispatcher import handler_dispatcher
from localstack.pro.core.persistence.pods.endpoints import PublicPodsResource
from localstack.pro.core.persistence.pods.manager import PodStateManager
from localstack.services.plugins import ServiceManager
from localstack.utils.files import mkdir
from werkzeug import Request
from werkzeug.test import Client

from tests.unit.persistence.dummy import DummyService


def test_public_pods_resource(tmp_path):
    state_dir = tmp_path / "state"
    state_dir.mkdir()

    # dummy service manager
    service_manager = ServiceManager()
    manager = PodStateManager(service_manager)

    sqs = DummyService()
    service_manager.add_service(sqs)

    sns = DummyService("sns")
    service_manager.add_service(sns)

    # create service state
    sqs.store["000000000000"]["us-east-1"].strings["foo"] = "bar"
    sqs.store["000000000000"]["us-east-2"].strings["baz"] = "ed"

    sns.store["000000000000"]["us-east-1"].strings["bar"] = "ed"

    # create endpoints wsgi application and testing client
    router = Router(handler_dispatcher())
    router.add(PublicPodsResource(manager))

    client = Client(Request.application(router.dispatch))

    # save the state into a pod
    pod_data = io.BytesIO()
    response = client.get("/_localstack/pods/state", headers={"Accept": "application/x-ndjson"})
    for chunk in response.response:
        pod_data.write(chunk)
    pod_data.seek(0)

    # assert metadata in the headers
    assert response.headers["x-localstack-pod-services"] == "sqs,sns"
    assert (size := response.headers["x-localstack-pod-size"])
    assert int(size) > 0

    # lifecycle hooks were called
    sqs.lifecycle_hook.on_before_state_save.assert_called_once()
    sqs.lifecycle_hook.on_after_state_save.assert_called_once()

    # reset state
    sqs.store.reset()

    # load the previously saved pod
    response = client.post("/_localstack/pods", data=pod_data)
    lines = response.get_data(as_text=True).strip().split("\n")
    assert len(lines) == 2
    events = [json.loads(line) for line in lines]
    assert {"service": "sqs", "status": "ok"} in events
    assert {"service": "sns", "status": "ok"} in events
    assert response.status_code == 201
    assert sqs.store["000000000000"]["us-east-1"].strings["foo"] == "bar"
    assert sqs.store["000000000000"]["us-east-2"].strings["baz"] == "ed"
    assert sns.store["000000000000"]["us-east-1"].strings["bar"] == "ed"


def test_subset_of_services(tmp_path):
    state_dir = tmp_path / "state"
    state_dir.mkdir()

    # dummy service manager
    service_manager = ServiceManager()
    manager = PodStateManager(service_manager)

    services = []
    for service_name in ["sqs", "dynamodb"]:
        service = DummyService(service_name)
        services.append(service)
        service.plugin_name = service_name

        service_manager.add_service(service)

        # create service state
        service.store["000000000000"]["us-east-1"].strings["foo"] = "bar"
        service.store["000000000000"]["us-east-2"].strings["baz"] = "ed"

    # create endpoints wsgi application and testing client
    router = Router(handler_dispatcher())
    router.add(PublicPodsResource(manager))

    c = Client(Request.application(router.dispatch))

    # save the state into a pod
    response = c.get("/_localstack/pods/state/?services=dynamodb")
    pod_data = response.get_data()

    # assert metadata in the headers
    assert response.headers["x-localstack-pod-services"] == "dynamodb"
    assert (size := response.headers["x-localstack-pod-size"])
    assert int(size) > 0

    for service in service_manager.values():
        service.store.reset()

    response = c.post("/_localstack/pods", data=pod_data)
    lines = response.get_data(as_text=True).strip().split("\n")
    assert len(lines) == 1
    events = [json.loads(line) for line in lines]
    assert {"service": "dynamodb", "status": "ok"} in events
    assert response.status_code == 201

    sqs_service = service_manager.get_service("sqs")
    assert not sqs_service.store
    dynamodb_service = service_manager.get_service("dynamodb")
    assert dynamodb_service.store["000000000000"]["us-east-1"].strings["foo"] == "bar"
    assert dynamodb_service.store["000000000000"]["us-east-2"].strings["baz"] == "ed"


def test_assets_symbolic_links(tmp_path):
    # dummy service manager
    service_manager = ServiceManager()
    manager = PodStateManager(service_manager)

    service = DummyService()
    service_manager.add_service(service)

    dummy_dir = os.path.join(config.dirs.data, "sqs")
    mkdir(dummy_dir)
    try:
        # persist two files, create a symlink to one of those, and delete the original
        # the non-existing ln would cause an error when creating the pod
        persisted_file = f"{dummy_dir}/readme.txt"
        with open(persisted_file, "w") as f:
            f.write("hello world")

        dst = f"{dummy_dir}/a.txt"
        ln = f"{dummy_dir}/a1"
        with open(dst, "w") as f:
            f.write("this file will be deleted")

        os.symlink(dst, ln)
        # verify ln + dst exist
        assert os.path.exists(ln)
        assert os.path.exists(dst)
        # rm the original dst
        os.remove(dst)
        assert not os.path.exists(ln)

        # create service state
        service.store["000000000000"]["us-east-1"].strings["foo"] = "bar"

        # create endpoints wsgi application and testing client
        router = Router(handler_dispatcher())
        router.add(PublicPodsResource(manager))

        c = Client(Request.application(router.dispatch))

        # save the state into a pod
        response = c.get("/_localstack/pods/state")
        pod_data = response.get_data()

        # assert metadata in the headers
        assert response.headers["x-localstack-pod-services"] == "sqs"
        assert (size := response.headers["x-localstack-pod-size"])
        assert int(size) > 0

        # reset state
        service.store.reset()
        service.reset_dummy_asset()
        # check files are gone
        assert not os.path.exists(ln)
        assert not os.path.exists(persisted_file)

        # load the previously saved pod
        response = c.post("/_localstack/pods", data=pod_data)
        assert response.status_code == 201
        assert service.store["000000000000"]["us-east-1"].strings["foo"] == "bar"

        # assert the persisted file is back, the symbol link is expected to be gone as it was dead
        assert not os.path.exists(ln)
        assert os.path.exists(persisted_file)
    finally:
        service.store.reset()
        service.reset_dummy_asset()
