import base64

import pytest
from localstack.pro.core.bootstrap import auth
from localstack.pro.core.bootstrap.auth import get_auth_headers
from localstack.utils.strings import to_bytes, to_str

TEST_CREDENTIALS_AUTH_TOKEN = "ls-wuku4263-vila-zeji-4925-motaqexi39ff"


@pytest.fixture
def _get_auth_cache(monkeypatch):
    monkeypatch.setattr(
        auth, "get_auth_cache", lambda: {"LOCALSTACK_AUTH_TOKEN": TEST_CREDENTIALS_AUTH_TOKEN}
    )


def test_get_auth_headers_from_auth_cache():
    def _assert(auth_cache, auth_header):
        result = get_auth_headers(auth_cache)
        assert result == {"authorization": auth_header}

    # internal token (legacy format)
    _assert({"token": "internal foo123"}, "internal foo123")
    _assert({"token": "foo123", "provider": "internal"}, "internal foo123")

    # bearer token (new Cognito format)
    _assert({"token": "Bearer foo.123"}, "Bearer foo.123")
    # even if "provider=internal" is still in the cache, it should not prefix the token with "internal"
    _assert({"token": "Bearer foo123", "provider": "internal"}, "Bearer foo123")
    _assert({"token": "Bearer foo123", "provider": "cognito"}, "Bearer foo123")


def test_get_auth_token_from_cache(_get_auth_cache):
    # read token from cache
    headers = get_auth_headers()
    auth_token_encoded = to_str(base64.b64encode(to_bytes(f":{TEST_CREDENTIALS_AUTH_TOKEN}")))
    assert headers["Authorization"] == f"Basic {auth_token_encoded}"
