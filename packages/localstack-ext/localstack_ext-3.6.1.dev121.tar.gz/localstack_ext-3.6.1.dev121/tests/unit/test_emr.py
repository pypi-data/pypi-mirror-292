from localstack.pro.core.services.emr.provider import SparkAppStep
from localstack.pro.core.utils.bigdata.bigdata_utils import (
    ENV_HIVE_PROPERTIES,
    get_additional_hive_user_configs,
)


def test_inject_hive_configs():
    step = SparkAppStep()
    cmd = ["spark-submit", "--class", "test123"]
    new_cmd = step.inject_hive_configs(cmd)

    assert [c for c in new_cmd if c.startswith("spark.yarn.dist.files=")]
    assert "spark.hadoop.dfs.client.datanode-restart.timeout=30" in new_cmd
    assert "test123" in new_cmd


def test_additional_hive_user_configs(monkeypatch):
    monkeypatch.setenv(ENV_HIVE_PROPERTIES, '{"foo":"bar"}')
    assert get_additional_hive_user_configs() == {"foo": "bar"}
    monkeypatch.setenv(ENV_HIVE_PROPERTIES, '{"invalid-json"}')
    assert get_additional_hive_user_configs() == {}
