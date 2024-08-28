import json
import typing

import pytest
import requests
import werkzeug
from localstack.http import Router
from localstack.http.dispatcher import handler_dispatcher
from localstack.pro.core.bootstrap.extensions.repository import ExtensionsRepository
from localstack.pro.core.extensions.manager import ExtensionsManager
from localstack.pro.core.extensions.resource import ExtensionsApi
from localstack.utils.files import rm_rf
from localstack.utils.net import get_free_tcp_port
from localstack.utils.serving import Server
from localstack.utils.venv import VirtualEnvironment
from werkzeug import serving

if typing.TYPE_CHECKING:
    from _typeshed.wsgi import WSGIApplication


class WerkzeugDevServer(Server):
    """
    Serves a WSGIApplication in a Werkzeug development webserver.
    """

    # TODO: move to localstack.http.werkzeug

    def __init__(self, app: "WSGIApplication", port: int, host: str = "localhost") -> None:
        super().__init__(port, host)
        self.app = app
        self.server = None

    def url_for(self, path: str):
        """
        Returns a callable URL by prefixing the server url to the given path::

          server.url_for("/my/api")

        Returns something like ``http://localhost:42069/my/api``.

        :param path: the url path
        :return: a URL with the path pointing to the server
        """
        return f"{self.url}{path}"

    def do_run(self):
        self.server = serving.make_server(self.host, self.port, self.app)
        self.server.serve_forever()

    def do_shutdown(self):
        self.server.shutdown()


@pytest.fixture()
def serve_wsgi_app():
    """Factory fixture to serve a WSGI application through WerkzeugDevServer."""
    # TODO: move to localstack.testing
    servers: list[WerkzeugDevServer] = []

    def _server_factory(app: "WSGIApplication") -> WerkzeugDevServer:
        server_ = WerkzeugDevServer(app, get_free_tcp_port())
        server_.start()
        if not server_.wait_is_up(timeout=10):
            raise TimeoutError(f"gave up waiting for server on {server_.url}")
        return server_

    yield _server_factory

    for server in servers:
        server.shutdown()


@pytest.fixture()
def serve_router(serve_wsgi_app):
    """Factory fixture to serve a localstack.http.Router through a WerkzeugDevServer."""
    # TODO: move to localstack.testing

    def _wrap(router: Router):
        return serve_wsgi_app(werkzeug.Request.application(router.dispatch))

    return _wrap


class TestExtensionsApi:
    # tests the extension-api end-to end. these are similar to the extension repository tests,
    # and have some limitations, since they cannot restart localstack, which is necessary to cleanly
    # re-load all plugins.

    @pytest.fixture()
    def api_server(self, serve_router, repository):
        api = ExtensionsApi(extension_manager=ExtensionsManager(), extension_repository=repository)
        router = Router(handler_dispatcher())
        router.add(api)
        return serve_router(router)

    @pytest.fixture()
    def repository(self, tmp_path):
        venv_path = tmp_path / "venv"
        venv_path.mkdir()
        venv = VirtualEnvironment(venv_path)
        venv.create()

        extension_repository = ExtensionsRepository(venv)
        yield extension_repository

        # venvs tend to be quite large, so make sure we remove them
        rm_rf(str(venv_path))

    def test_list_on_empty_repository(self, api_server):
        response = requests.get(api_server.url_for("/_localstack/extensions/list"))
        assert response.ok
        assert response.json() == []

    def test_install_non_existing_package(self, api_server):
        package = "package-that-does-not-exist"

        # make sure the package really doesn't exist before installing to avoid attacks
        assert requests.get(f"https://pypi.org/simple/{package}/").status_code == 404

        response = requests.post(
            api_server.url_for("/_localstack/extensions/install"),
            json={"URL": package},
            stream=True,
        )
        assert response.ok
        # TODO: could be a little less lazy here with the assertion
        assert "Could not resolve package package-that-does-not-exist" in response.text

    def test_install_with_internal_exception(self, api_server, repository, monkeypatch):
        def faulty_installer(*args, **kwargs):
            yield {"event": "status", "message": "Checking installed extensions"}
            raise OSError("oh no a pesky OS error")

        monkeypatch.setattr(repository, "run_install", faulty_installer)

        response = requests.post(
            api_server.url_for("/_localstack/extensions/install"),
            json={"URL": "localstack-extension-httpbin"},
            stream=True,
        )

        exceptions = []
        for line in response.iter_lines():
            doc = json.loads(line)
            if doc["event"] == "exception":
                exceptions.append(doc)

        assert exceptions

        # the last event should be an e
        assert exceptions[0]["event"] == "exception"
        assert "oh no a pesky OS error" in exceptions[0]["extra"]["traceback"]

    def test_install_list_uninstall(self, api_server):
        # TODO: could do with a few more assertions
        response = requests.post(
            api_server.url_for("/_localstack/extensions/install"),
            json={"URL": "localstack-extension-httpbin"},
            stream=True,
        )

        extensions = []
        events = []
        for line in response.iter_lines():
            doc = json.loads(line)
            events.append(doc)
            if doc["event"] == "extension":
                extensions.append(doc)

        assert response.ok, response.text
        assert extensions
        assert events[-1]["message"] == "Extension installation completed"
        assert extensions[0]["extra"]["distribution"]["name"] == "localstack-extension-httpbin"

        response = requests.post(
            api_server.url_for("/_localstack/extensions/install"),
            json={"URL": "localstack-extension-hello-world"},
            stream=True,
        )
        assert response.ok, response.text

        response = requests.get(api_server.url_for("/_localstack/extensions/list"))
        assert response.ok, response.text
        assert {item["distribution"]["name"] for item in response.json()} == {
            "localstack-extension-httpbin",
            "localstack-extension-hello-world",
        }, response.text

        response = requests.post(
            api_server.url_for("/_localstack/extensions/uninstall"),
            json={"distribution": "localstack-extension-hello-world"},
        )
        assert response.ok, response.text
        assert "Extension uninstall completed" in response.text

        response = requests.get(api_server.url_for("/_localstack/extensions/list"))
        assert response.ok, response.text
        assert len(response.json()) == 1
        assert response.json()[0]["distribution"]["name"] == "localstack-extension-httpbin"
