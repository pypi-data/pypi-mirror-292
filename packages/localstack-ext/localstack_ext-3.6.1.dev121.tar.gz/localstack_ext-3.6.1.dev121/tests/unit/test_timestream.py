import json

from localstack.pro.core.services.timestream.postgres_extensions import interpolate_linear
from localstack.pro.core.services.timestream.server import prepare_query
from localstack.pro.core.services.timestream.utils import (
    normalize_db_name,
    normalize_table_name,
)


def test_normalize_identifiers():
    def _norm_db(s):
        return normalize_db_name(s)

    def _norm_table(s):
        return normalize_table_name(s)

    assert _norm_db("my-db1") == "my_db1"
    assert _norm_db("abc-1") == "abc_1"
    assert _norm_db("abc--1-2") == "abc_1_2"
    assert _norm_db(" abc-") == "abc_"

    assert _norm_table("table1") == "table1"
    assert _norm_table("my-table ") == "my_table"


def test_prepare_query_sequence_function():
    prepared = prepare_query("SEQUENCE(min(time), max(time), 1s)")
    assert prepared == "SEQUENCE(min(time), max(time), '1s')"

    prepared = prepare_query("SEQUENCE(min(time), max(time), 42m)")
    assert prepared == "SEQUENCE(min(time), max(time), '42m')"


def test_interpolate_linear_function():
    timeseries = [
        {"time": "2023-07-08T12:39:04", "measure_value::decimal": 1.0},
        {"time": "2023-07-08T12:39:06", "measure_value::decimal": 3.0},
        {"time": "2023-07-08T12:39:08", "measure_value::decimal": 2.0},
        {"time": "2023-07-08T12:39:10", "measure_value::decimal": 5.0},
        {"time": "2023-07-08T12:39:12", "measure_value::decimal": 4.0},
    ]
    timestamps = [
        "2023-07-08 12:39:04.000000000",
        "2023-07-08 12:39:05.000000000",
        "2023-07-08 12:39:06.000000000",
        "2023-07-08 12:39:07.000000000",
        "2023-07-08 12:39:08.000000000",
        "2023-07-08 12:39:09.000000000",
        "2023-07-08 12:39:10.000000000",
        "2023-07-08 12:39:11.000000000",
        "2023-07-08 12:39:12.000000000",
    ]

    result = interpolate_linear(json.dumps(timeseries), timestamps)
    result = json.loads(result)
    assert result == [
        {"time": "2023-07-08 12:39:04.000000000", "value": 1.0},
        {"time": "2023-07-08 12:39:05.000000000", "value": 2.0},
        {"time": "2023-07-08 12:39:06.000000000", "value": 3.0},
        {"time": "2023-07-08 12:39:07.000000000", "value": 2.5},
        {"time": "2023-07-08 12:39:08.000000000", "value": 2.0},
        {"time": "2023-07-08 12:39:09.000000000", "value": 3.5},
        {"time": "2023-07-08 12:39:10.000000000", "value": 5.0},
        {"time": "2023-07-08 12:39:11.000000000", "value": 4.5},
        {"time": "2023-07-08 12:39:12.000000000", "value": 4.0},
    ]
