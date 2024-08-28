import asyncio
import json
import os
import threading
from queue import Queue

import nest_asyncio
import pytest
import websockets
from localstack.testing.pytest import markers
from localstack.utils.run import run
from localstack.utils.threads import start_worker_thread

INIT_LOCK = threading.RLock()


def get_base_dir():
    return os.path.join(os.path.dirname(__file__), "serverless")


@pytest.fixture(scope="class")
def await_serverless_init(region_name):
    base_dir = get_base_dir()

    # deploy serverless app
    with INIT_LOCK:
        run(["npm", "run", "deploy", "--", f"--region={region_name}"], cwd=base_dir)

    yield

    # undeploy app
    with INIT_LOCK:
        run(["npm", "run", "destroy", "--", f"--region={region_name}"], cwd=base_dir)


@pytest.mark.usefixtures("await_serverless_init")
class TestServerless:
    @classmethod
    def init_async(cls):
        def _run(*args):
            with INIT_LOCK:
                base_dir = get_base_dir()
                # install dependencies
                run(["npm", "install"], cwd=base_dir)

        start_worker_thread(_run)

    @pytest.mark.skip(reason="Temporarily disabled, fix with v2!")
    @markers.only_on_amd64
    @markers.skip_offline
    @markers.aws.unknown
    def test_websocket_deployed(self, aws_client):
        # This allow an event loop running in another
        nest_asyncio.apply()

        client = aws_client.apigatewayv2
        queue = Queue()
        msg = {"action": "test-action"}

        async def start_client(uri):
            async with websockets.connect(uri) as websocket:
                await websocket.send(json.dumps(msg))
                result = await asyncio.wait_for(websocket.recv(), timeout=30)
                queue.put(json.loads(result))

        apis = client.get_apis()["Items"]
        api = [a for a in apis if "local-sls-test-websockets" in a["Name"]][0]

        url = api["ApiEndpoint"]
        asyncio.get_event_loop().run_until_complete(start_client(url))
        result = queue.get(timeout=3)
        result = result.get("body") or result
        result = json.loads(result)

        assert result == msg
