import os
from unittest import mock

from localstack.pro.core.config import is_api_key_configured


@mock.patch.dict(os.environ, {"LOCALSTACK_API_KEY": ""}, clear=True)
def test_api_key_configured_with_empty_api_key():
    assert not is_api_key_configured()


@mock.patch.dict(os.environ, {"LOCALSTACK_API_KEY": " "}, clear=True)
def test_api_key_configured_with_spaces_only_api_key():
    assert not is_api_key_configured()


@mock.patch.dict(os.environ, {}, clear=True)
def test_api_key_configured_without_api_key():
    assert not is_api_key_configured()


@mock.patch.dict(os.environ, {"LOCALSTACK_API_KEY": "GxobLV9hSiA"}, clear=True)
def test_api_key_configured_with_api_key():
    assert is_api_key_configured()
