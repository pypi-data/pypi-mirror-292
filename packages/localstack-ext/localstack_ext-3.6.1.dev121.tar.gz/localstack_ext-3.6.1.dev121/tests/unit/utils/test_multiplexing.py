import contextlib

import pytest
import requests
from localstack.constants import LOCALHOST_IP
from localstack.pro.core.utils.multiplexing import DestinationSelector, MultiplexingServer
from localstack.utils.net import get_free_tcp_port, wait_for_port_closed, wait_for_port_open
from pytest_httpserver import HTTPServer
from werkzeug import Response


@pytest.fixture
def create_httpserver():
    servers = []

    def _create():
        server = HTTPServer()
        server.start()
        servers.append(server)
        return server

    yield _create

    for server in servers:
        with contextlib.suppress(Exception):
            server.clear()
            if server.is_running():
                server.stop()
            server.check_assertions()
            server.clear()


def test_multiplexed_server(create_httpserver):
    server1 = create_httpserver()
    server1.expect_request("/test1").respond_with_handler(lambda *_: Response("server 1"))
    server2 = create_httpserver()
    server2.expect_request("/test2").respond_with_handler(lambda *_: Response("server 2"))
    port = get_free_tcp_port()

    class TestSelector(DestinationSelector):
        def __call__(self, first_bytes: bytes) -> (str, int):
            port = server1.port if first_bytes.startswith(b"GET /test1") else server2.port
            return LOCALHOST_IP, port

    server = MultiplexingServer(port, destination_selector=TestSelector())
    server.start()
    wait_for_port_open(port)

    base_url = f"http://localhost:{port}"
    result = requests.get(f"{base_url}/test1")
    assert result.content == b"server 1"
    result = requests.post(f"{base_url}/test2")
    assert result.content == b"server 2"

    server.shutdown()
    wait_for_port_closed(port)
