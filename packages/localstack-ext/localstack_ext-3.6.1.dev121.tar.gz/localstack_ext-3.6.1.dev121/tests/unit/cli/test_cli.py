import json
import re

import click
import pytest
from click.testing import CliRunner
from localstack import config
from localstack.cli.localstack import localstack as cli

cli: click.Group


@pytest.fixture
def runner():
    return CliRunner()


def test_config_show_table(runner):
    result = runner.invoke(cli, ["config", "show"])
    assert result.exit_code == 0
    assert "DATA_DIR" in result.output
    assert "DEBUG" in result.output


def test_config_show_json(runner):
    result = runner.invoke(cli, ["config", "show", "--format=json"])
    assert result.exit_code == 0

    # remove control characters and color/formatting codes like "\x1b[32m"
    output = re.sub(r"\x1b\[[;0-9]+m", "", result.output, flags=re.MULTILINE)
    doc = json.loads(output)
    assert "DATA_DIR" in doc
    assert "DEBUG" in doc
    assert type(doc["DEBUG"]) == bool


def test_config_show_plain(runner, monkeypatch):
    monkeypatch.setenv("DEBUG", "1")
    monkeypatch.setattr(config, "DEBUG", True)

    result = runner.invoke(cli, ["config", "show", "--format=plain"])
    assert result.exit_code == 0

    # using regex here, as output string may contain the color/formatting codes like "\x1b[32m"
    assert re.search(r"DATA_DIR[^=]*=", result.output)
    assert re.search(r"DEBUG[^=]*=(\x1b\[3;92m)?True", result.output)


def test_config_show_dict(runner, monkeypatch):
    monkeypatch.setenv("DEBUG", "1")
    monkeypatch.setattr(config, "DEBUG", True)

    result = runner.invoke(cli, ["config", "show", "--format=dict"])
    assert result.exit_code == 0

    assert "'DATA_DIR'" in result.output
    # using regex here, as output string may contain the color/formatting codes like "\x1b[32m"
    assert re.search(r"'DEBUG'[^:]*: [^']*True", result.output)
