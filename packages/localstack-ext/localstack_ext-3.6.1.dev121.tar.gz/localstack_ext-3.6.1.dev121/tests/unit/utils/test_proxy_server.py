import pytest
import requests
from localstack.aws.api import RequestContext
from localstack.aws.chain import Handler, HandlerChain
from localstack.aws.gateway import Gateway
from localstack.config import HostAndPort
from localstack.constants import LOCALHOST_HOSTNAME
from localstack.http import Response
from localstack.http.duplex_socket import enable_duplex_socket
from localstack.http.hypercorn import GatewayServer
from localstack.pro.core.utils.proxy_server import start_ssl_proxy
from localstack.utils.net import get_free_tcp_port, wait_for_port_open


@pytest.fixture
def create_ssl_server():
    server = None

    def _create(handler: Handler) -> int:
        nonlocal server

        # explicitly enable the duplex socket support here
        enable_duplex_socket()

        gateway = Gateway()
        gateway.request_handlers.append(handler)
        port = get_free_tcp_port()
        gateway_listen = HostAndPort(host="127.0.0.1", port=port)
        server = GatewayServer(gateway, gateway_listen, use_ssl=True)
        server.start()
        server.wait_is_up(timeout=10)
        return port

    yield _create
    if server:
        server.shutdown()


def test_ssl_proxy_server(create_ssl_server):
    invocations = []

    def echo_request_handler(_: HandlerChain, context: RequestContext, response: Response):
        invocations.append(context.request)
        response.set_json({"foo": "bar"})
        response.status_code = 200

    port = create_ssl_server(echo_request_handler)

    # start SSL proxy
    proxy_port = get_free_tcp_port()
    proxy = start_ssl_proxy(proxy_port, port, asynchronous=True)
    wait_for_port_open(proxy_port)

    # invoke SSL proxy server
    url = f"https://{LOCALHOST_HOSTNAME}:{proxy_port}"
    num_requests = 3
    for i in range(num_requests):
        get_response = requests.get(url, verify=False)
        assert get_response.status_code == 200

    # assert backend server has been invoked
    assert len(invocations) == num_requests

    # clean up
    proxy.stop()
