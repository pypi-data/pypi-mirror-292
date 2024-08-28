import os
from dataclasses import dataclass

from localstack import config
from localstack.config import HostAndPort, UniqueHostAndPortList
from localstack.pro.core import plugins


@dataclass
class Config:
    LOCALSTACK_HOST: HostAndPort
    GATEWAY_LISTEN: UniqueHostAndPortList


def test_defaults(monkeypatch):
    monkeypatch.delenv("GATEWAY_LISTEN", raising=False)
    res = Config(*config.populate_edge_configuration(os.environ))
    plugins.modify_gateway_listen_config(res)

    assert res.GATEWAY_LISTEN == UniqueHostAndPortList(
        [
            HostAndPort("127.0.0.1", 4566),
            HostAndPort("127.0.0.1", 443),
        ]
    )


def test_set_gateway_listen(monkeypatch):
    gateway_listen = "0.0.0.0:3000,0.0.0.0:5000"

    monkeypatch.setenv("GATEWAY_LISTEN", gateway_listen)

    res = Config(*config.populate_edge_configuration(os.environ))
    plugins.modify_gateway_listen_config(res)

    assert res.GATEWAY_LISTEN == UniqueHostAndPortList(
        [
            HostAndPort("0.0.0.0", 3000),
            HostAndPort("0.0.0.0", 5000),
        ]
    )


def test_ignore_legacy_variables(monkeypatch):
    """Providing legacy variables removed in 3.0 should not affect the default configuration.
    This test can be removed somewhere around >3.1-4.0"""
    monkeypatch.delenv("GATEWAY_LISTEN", raising=False)
    monkeypatch.setenv("EDGE_PORT", "5000")
    monkeypatch.setenv("EDGE_PORT_HTTP", "6000")
    res = Config(*config.populate_edge_configuration(os.environ))
    plugins.modify_gateway_listen_config(res)

    assert res.LOCALSTACK_HOST == "localhost.localstack.cloud:4566"
    assert res.GATEWAY_LISTEN == UniqueHostAndPortList(
        [
            HostAndPort("127.0.0.1", 4566),
            HostAndPort("127.0.0.1", 443),
        ]
    )


def test_gateway_listen_override(monkeypatch):
    monkeypatch.setenv("GATEWAY_LISTEN", "0.0.0.0:8888,0.0.0.0:9999")
    res = Config(*config.populate_edge_configuration(os.environ))
    plugins.modify_gateway_listen_config(res)

    assert res.GATEWAY_LISTEN == UniqueHostAndPortList(
        [
            HostAndPort("0.0.0.0", 8888),
            HostAndPort("0.0.0.0", 9999),
        ]
    )
