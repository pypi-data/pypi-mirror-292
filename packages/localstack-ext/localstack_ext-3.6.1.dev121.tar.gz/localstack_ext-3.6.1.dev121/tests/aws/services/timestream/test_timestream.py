import contextlib
import re
from datetime import datetime, timedelta
from typing import Dict, List

import pytest
from botocore.exceptions import ClientError
from localstack.pro.core.aws.api.timestream_query import ValidationException
from localstack.pro.core.services.timestream.postgres_extensions import TIME_FORMAT
from localstack.testing.pytest import markers
from localstack.testing.snapshots.transformer_utility import TransformerUtility
from localstack.utils.numbers import format_number
from localstack.utils.strings import short_uid
from localstack.utils.time import now_utc, timestamp


@pytest.fixture
def create_db_and_table(aws_client):
    db_tables = {}

    def _create(
        db_name: str = None, table_name: str = None, db_tags: List = [], table_tags: List = []
    ):
        if not db_name:
            db_name = f"db{short_uid()}"
            aws_client.timestream_write.create_database(DatabaseName=db_name, Tags=db_tags)
            db_tables.setdefault(db_name, [])
        if not table_name:
            table_name = f"table{short_uid()}"
            aws_client.timestream_write.create_table(
                DatabaseName=db_name, TableName=table_name, Tags=table_tags
            )
            db_tables.setdefault(db_name, []).append(table_name)
        return db_name, table_name

    yield _create

    for db_name, tables in db_tables.items():
        _delete_database(db_name, tables, aws_client.timestream_write)


@pytest.fixture(autouse=True)
def timestream_snapshot_transformer(snapshot):
    snapshot.add_transformer(
        [
            TransformerUtility.key_value("QueryId", "<query_id>", reference_replacement=False),
            TransformerUtility.key_value(
                "CumulativeBytesMetered", "<bytes_metered>", reference_replacement=False
            ),
            TransformerUtility.key_value(
                "CumulativeBytesScanned", "<bytes_scanned>", reference_replacement=False
            ),
            TransformerUtility.key_value("Time", "<time>", reference_replacement=False),
        ]
    )


def _delete_database(db_name: str, table_names: List[str], timestream_write_client):
    for table in table_names:
        with contextlib.suppress(Exception):
            timestream_write_client.delete_table(DatabaseName=db_name, TableName=table)
    with contextlib.suppress(Exception):
        timestream_write_client.delete_database(DatabaseName=db_name)


@pytest.fixture
def create_table_with_data(create_db_and_table, aws_client, region_name):
    def _insert_data(
        db_name: str = None,
        table_name: str = None,
        num_entries: int = 5,
        data_type: str = None,
        start_time: int = None,
        dimensions: List[Dict] = None,
    ):
        db_name, table_name = create_db_and_table(db_name=db_name, table_name=table_name)

        dimensions = dimensions or [
            {
                "Name": "region",
                "Value": region_name,
                "DimensionValueType": "VARCHAR",
            }
        ]

        start_time = start_time or now_utc() - 10
        test_records = [
            {"MeasureValue": "1", "Time": str(start_time)},
            {"MeasureValue": "3", "Time": str(start_time + 2)},
            {"MeasureValue": "2", "Time": str(start_time + 4)},
            {"MeasureValue": "5", "Time": str(start_time + 6)},
            {"MeasureValue": "4", "Time": str(start_time + 8)},
        ]
        for i in range(len(test_records), num_entries):
            record = {"MeasureValue": str(i), "Time": str(start_time + 8 + i)}
            test_records.append(record)

        aws_client.timestream_write.write_records(
            DatabaseName=db_name,
            TableName=table_name,
            CommonAttributes={
                "Dimensions": dimensions,
                "MeasureName": "cpu",
                "MeasureValueType": data_type or "DOUBLE",
                "TimeUnit": "SECONDS",
            },
            Records=test_records,
        )
        return db_name, table_name, test_records

    yield _insert_data


class TestTimestreamQueries:
    @pytest.mark.parametrize(
        "db_name,table_name",
        [
            (
                "db-{short_uid}",
                "table{short_uid}",
            ),
            ("DB_TEST", "MY_TABLE_NAME"),
        ],
    )
    @markers.aws.unknown
    def test_timestream_query(
        self, create_table_with_data, db_name, table_name, aws_client, cleanups
    ):
        db_name = db_name.format(short_uid=short_uid())
        table_name = table_name.format(short_uid=short_uid())
        # create db
        result = aws_client.timestream_write.create_database(DatabaseName=db_name)
        db_details = result.get("Database", {})
        assert db_details.get("DatabaseName") == db_name
        assert "Arn" in db_details

        # create table
        result = aws_client.timestream_write.create_table(
            DatabaseName=db_name, TableName=table_name
        )
        table = result.get("Table", {})
        assert table.get("TableName") == table_name
        assert table.get("DatabaseName") == db_name

        # clean up table/DB at end of the test
        cleanups.append(lambda: _delete_database(db_name, tables, aws_client.timestream_write))

        # describe db
        result = aws_client.timestream_write.describe_database(DatabaseName=db_name)
        db_details = result.get("Database", {})
        assert db_details.get("DatabaseName") == db_name
        assert "Arn" in db_details

        # list db
        result = aws_client.timestream_write.list_databases()
        existing = [db for db in result.get("Databases", []) if db["DatabaseName"] == db_name]
        assert len(existing) == 1

        # list tables
        result = aws_client.timestream_write.list_tables(DatabaseName=db_name)
        tables = result["Tables"]
        assert tables
        assert tables[0]["TableName"] == table_name
        assert tables[0]["DatabaseName"] == db_name
        assert tables[0]["TableStatus"] == "ACTIVE"

        self.run_queries(
            db_name,
            table_name,
            aws_client=aws_client,
            create_table_with_data=create_table_with_data,
        )

    @markers.aws.validated
    def test_query_pagination(self, create_table_with_data, aws_client, snapshot):
        # insert data
        num_entries = 50
        db_name, table_name, test_records = create_table_with_data(num_entries=num_entries)

        # query data in loop, assert all records are retrieved
        query = f"SELECT * FROM {db_name}.{table_name} WHERE measure_name='cpu'"
        max_rows = 4
        all_records = []
        kwargs = {}
        # note: some iterations may yield empty results in AWS, hence adding more loop iterations here
        for i in range(num_entries):
            result = aws_client.timestream_query.query(
                QueryString=query, MaxRows=max_rows, **kwargs
            )
            if len(all_records) >= num_entries:
                break
            kwargs["NextToken"] = result.get("NextToken")
            not kwargs["NextToken"] and kwargs.pop("NextToken")
            all_records.extend(result["Rows"])
        snapshot.match("num-records-1", len(all_records))

        # run query using boto3 paginator
        all_records = []
        iterations = 0
        paginator = aws_client.timestream_query.get_paginator("query")
        for result in paginator.paginate(QueryString=query, MaxRows=max_rows):
            all_records.extend(result["Rows"])
            iterations += 1
        assert iterations >= 13
        snapshot.match("num-records-2", len(all_records))

    @markers.aws.validated
    def test_insert_different_data_types(self, create_table_with_data, aws_client):
        num_rows = 7
        for data_type in ["DOUBLE", "VARCHAR"]:
            db_name, table_name, test_records = create_table_with_data(
                data_type=data_type, num_entries=num_rows
            )
            query = f"SELECT * FROM {db_name}.{table_name} WHERE measure_name='cpu'"
            result = aws_client.timestream_query.query(QueryString=query)
            assert len(result["Rows"]) == num_rows

    @markers.aws.needs_fixing
    @pytest.mark.skip(reason="BIGINT has double precision")
    @pytest.mark.parametrize("data_type", ["DOUBLE", "BIGINT"])
    def test_output_precision(self, data_type, aws_client, create_table_with_data, snapshot):
        num_rows = 3
        db_name, table_name, test_records = create_table_with_data(
            data_type=data_type, num_entries=num_rows
        )
        query = f"SELECT sum(measure_value::{data_type.lower()}) FROM {db_name}.{table_name}"
        result = aws_client.timestream_query.query(QueryString=query)

        snapshot.match(f"sum-result-{data_type}", result["Rows"][0]["Data"])

    @markers.aws.validated
    def test_multi_records(self, create_db_and_table, aws_client, snapshot):
        db_name, table_name = create_db_and_table()
        snapshot.add_transformer(
            snapshot.transform.regex(r"\d{4}-\d{2}-\d{2} [\d.:]+", "timestamp")
        )

        # not great to snapshot, but it must be a recent timestamp due to timestream's retention policy
        start_time = now_utc() - 10
        test_records = []

        # not the most efficient way to write records (could use CommonAttributes)
        # but this formatting originates directly from a customer support-case
        dimensions = [{"Name": "key_name", "Value": "test_key", "DimensionValueType": "VARCHAR"}]
        record = {
            "Dimensions": dimensions,
            "MeasureName": "test_measure",
            "MeasureValueType": "MULTI",
            "TimeUnit": "SECONDS",
        }

        for i in range(3):
            values = [
                {"Name": f"test_type{i*2}", "Value": str(i * 10), "Type": "BIGINT"},
                {"Name": f"test_type{(i*2)+1}", "Value": str(i * 20), "Type": "BIGINT"},
            ]
            new_record = {**record, "Time": str(start_time + i), "MeasureValues": values}
            test_records.append(new_record)

        aws_client.timestream_write.write_records(
            DatabaseName=db_name, TableName=table_name, Records=test_records
        )

        result = aws_client.timestream_query.query(
            QueryString=f"select * from {db_name}.{table_name}"
        )
        col_names = [c["Name"] for c in result["ColumnInfo"]]
        result["ColumnInfo"] = {c["Name"]: c["Type"] for c in result["ColumnInfo"]}
        rows = []
        for row in result["Rows"]:
            row = {col: row["Data"][idx] for idx, col in enumerate(col_names)}
            rows.append(row)
        result["Rows"] = rows
        snapshot.match("select-all-multi-measure", result)

    @markers.aws.validated
    def test_sum_by_reference(self, aws_client, create_db_and_table, snapshot):
        db_name, table_name = create_db_and_table()
        dimensions = [{"Name": "key_name", "Value": "test_key", "DimensionValueType": "VARCHAR"}]
        record = {
            "Dimensions": dimensions,
            "MeasureName": "test_measure",
            "MeasureValueType": "MULTI",
            "TimeUnit": "SECONDS",
        }

        start_time = now_utc() - 10
        test_records = []

        for i in range(3):
            values = [
                {"Name": f"test_type{i*2}", "Value": str(i * 10.5), "Type": "DOUBLE"},
                {"Name": f"test_type{(i*2)+1}", "Value": str(i * 20), "Type": "BIGINT"},
            ]
            new_record = {**record, "Time": str(start_time + i), "MeasureValues": values}
            test_records.append(new_record)

        aws_client.timestream_write.write_records(
            DatabaseName=db_name, TableName=table_name, Records=test_records
        )

        result = aws_client.timestream_query.query(
            QueryString=f"select sum(test_type4) from {db_name}.{table_name}"
        )

        snapshot.match("sum-column-reference-double-result", result["Rows"][0]["Data"])

    def run_queries(self, db_name, table_name, aws_client, create_table_with_data):
        # create test data
        start_time = now_utc() - 10
        num_entries = 5
        _, _, test_records = create_table_with_data(
            db_name=db_name, table_name=table_name, num_entries=num_entries, start_time=start_time
        )

        # run simple query
        query = "SELECT 1"
        result = aws_client.timestream_query.query(QueryString=query)
        rows = result["Rows"]
        assert rows == [{"Data": [{"ScalarValue": "1"}]}]

        # run query with different table ref formats
        for table_ref in ['"%s".%s', '"%s"."%s"']:
            table_ref = table_ref % (db_name, table_name)
            query = f"""SELECT region, CREATE_TIME_SERIES(time, measure_value::double) as cpu
                FROM {table_ref} WHERE measure_name='cpu' GROUP BY region"""
            result = aws_client.timestream_query.query(QueryString=query)
            rows = result["Rows"]
            assert len(rows) == 1
            row = rows[0]["Data"]
            assert row[0] == {"ScalarValue": "us-east-1"}
            assert "TimeSeriesValue" in row[1]
            timeseries = row[1]["TimeSeriesValue"]
            assert len(timeseries) == len(test_records)
            expected_start_time = timestamp(time=start_time, format=TIME_FORMAT)
            expected_end_time = timestamp(time=start_time + 8, format=TIME_FORMAT)
            assert timeseries[0] == {"Time": expected_start_time, "Value": {"ScalarValue": "1.0"}}
            assert timeseries[-1] == {"Time": expected_end_time, "Value": {"ScalarValue": "4.0"}}

        # run query with different attribute refs
        for attrs in ["ALL *", "*"]:
            query = f"SELECT {attrs} FROM \"{db_name}\".{table_name} WHERE measure_name='cpu'"
            result = aws_client.timestream_query.query(QueryString=query)
            rows = result["Rows"]
            cols = {col["Name"]: col["Type"]["ScalarType"] for col in result["ColumnInfo"]}
            assert cols == {
                "time": "TIMESTAMP",
                "measure_name": "VARCHAR",
                "measure_value::double": "DOUBLE",
                "region": "VARCHAR",
            }
            for row in rows:
                assert len(row["Data"]) == len(cols)

        # run query with bin function using "time" column reference
        query = f"""SELECT "time", BIN("time", 5m) AS "time_bin_5m" FROM "{db_name}".{table_name}"""
        result = aws_client.timestream_query.query(QueryString=query)
        rows = result["Rows"]
        assert len(rows) == num_entries

        def _match(entry, _date):
            # note: not implementing actual bin(..) function here in python, instead using simple regex
            regex = rf"{timestamp(time=_date, format='%Y-%m-%d')} [0-9:]+\.000000000"
            assert re.match(regex, entry["ScalarValue"])

        # assert times are correct in the result
        _match(rows[0]["Data"][0], start_time)
        _match(rows[0]["Data"][1], start_time - 100)
        assert result["ColumnInfo"][1] == {
            "Name": "time_bin_5m",
            "Type": {"ScalarType": "TIMESTAMP"},
        }

    @markers.snapshot.skip_snapshot_verify(paths=["$..Rows..Data..ScalarValue"])
    @markers.aws.validated
    def test_ago_function(self, aws_client, snapshot):
        ago_str = "7d"
        result = aws_client.timestream_query.query(QueryString=f"SELECT ago({ago_str})")
        # TODO: find longterm solution to snapshot test this
        # the result changes with each execution, we would need a dynamic date transformer
        snapshot.match("ago_func", result)

        ago_str = "'7d'"
        with pytest.raises((ClientError, ValidationException)) as e_info:
            result = aws_client.timestream_query.query(QueryString=f"SELECT ago({ago_str})")
        # TODO: this doesn't conform with AWS
        # it raises: "The query syntax is invalid at line"
        # snapshot.match("FailingAgoResponse", e_info.value)
        assert "Unexpected parameters for function" in str(e_info.value)

    # TODO: fix bin function for minutes - only works for days
    @pytest.mark.parametrize("interval_str", ["3d"])
    @markers.aws.validated
    def test_bin_function(self, aws_client, interval_str, snapshot):
        timestamp = "2021-11-15 11:18:42"
        result = aws_client.timestream_query.query(
            QueryString=f"SELECT bin('{timestamp}', {interval_str}), 1"
        )
        snapshot.match(f"bin_{interval_str}", result)

    @markers.aws.validated
    def test_parse_duration_func(self, aws_client, snapshot):
        interval_str = "3h"
        result = aws_client.timestream_query.query(
            QueryString=f"SELECT parse_duration('{interval_str}')"
        )
        snapshot.match("ThreeHoursDuration", result)

        interval_str = "3 hours"
        with pytest.raises((ClientError, ValidationException)) as e_info:
            result = aws_client.timestream_query.query(
                QueryString=f"SELECT parse_duration({interval_str})"
            )
        # TODO: this doesn't conform with AWS
        # it raises: "The query syntax is invalid at line"
        assert "Unknown time unit: hours" in str(e_info.value)

    @markers.aws.validated
    @pytest.mark.parametrize("timestamp_val", ["2021-11-15T11:18:42.573Z", "2021-11-15T11:18:42"])
    def test_from_iso8601_timestamp(self, aws_client, timestamp_val, snapshot):
        result = aws_client.timestream_query.query(
            QueryString=f"SELECT from_iso8601_timestamp('{timestamp_val}')"
        )
        snapshot.match("FromIso8601Value", result)

    @markers.aws.validated
    def test_from_iso8601_date(self, aws_client, snapshot):
        result = aws_client.timestream_query.query(
            QueryString="SELECT from_iso8601_date('2021-11-23')"
        )
        snapshot.match("FromIso8601Date", result)

    @markers.aws.validated
    def test_from_milliseconds_func(self, aws_client, snapshot):
        result = aws_client.timestream_query.query(QueryString="SELECT from_milliseconds(1)")
        snapshot.match("from-milliseconds-one", result["Rows"][0]["Data"])

        result = aws_client.timestream_query.query(
            QueryString="SELECT from_milliseconds(1690501686000)"
        )
        snapshot.match("from-milliseconds-real", result["Rows"][0]["Data"])

    @markers.snapshot.skip_snapshot_verify(
        paths=["$..ColumnInfo..Type.ScalarType"], reason="bigint vs integer"
    )
    @markers.aws.validated
    def test_to_milliseconds_func(self, aws_client, snapshot):
        result = aws_client.timestream_query.query(
            QueryString="SELECT to_milliseconds('2011-05-17 10:40:28.876944')"
        )
        snapshot.match("ToMilliseconds", result)

    @markers.snapshot.skip_snapshot_verify(
        paths=[
            "$..ColumnInfo..Name",
            "$..ColumnInfo..Type.ArrayColumnInfo",
            "$..ColumnInfo..Type.ScalarType",
        ],
        reason="todo - first arrayvalue postgres",
    )
    @markers.aws.validated
    def test_sequence_time_func(self, aws_client, snapshot):
        result = aws_client.timestream_query.query(
            QueryString="SELECT sequence('2023-04-02 19:26:12.941000000', '2023-04-03 19:26:12.941000000', 2h)"
        )
        snapshot.match("SequenceTime2hSteps", result)

    @markers.aws.validated
    @pytest.mark.parametrize("cast_timestamp", [True, False])
    # TODO: enhance parity around result set column names
    @markers.snapshot.skip_snapshot_verify(paths=["$..ColumnInfo..Name"])
    def test_interpolation_function(
        self, create_table_with_data, cast_timestamp, aws_client, snapshot
    ):
        # create table with test data
        time_now = now_utc()
        db_name, table_name, _ = create_table_with_data(start_time=time_now)

        # select time series
        query = (
            f"SELECT CREATE_TIME_SERIES(time, measure_value::double) FROM {db_name}.{table_name}"
        )
        result = aws_client.timestream_query.query(QueryString=query)
        snapshot.match("select-time-series", result)

        # select linear interpolation from time series
        start_time = result["Rows"][0]["Data"][0]["TimeSeriesValue"][0]["Time"]
        start_time = datetime.strptime(start_time, TIME_FORMAT)
        later_time = start_time + timedelta(seconds=1, milliseconds=500)
        later_time = timestamp(later_time, format=TIME_FORMAT)
        query = f"""
        SELECT interpolate_linear(
            CREATE_TIME_SERIES(time, measure_value::double), {'TIMESTAMP' if cast_timestamp else ''} '{later_time}'
        ) FROM {db_name}.{table_name}
        """
        result = aws_client.timestream_query.query(QueryString=query)
        snapshot.match("select-interpolate-linear-timestamp", result)

        # select fill interpolation from time series (single timestamp)
        query = f"""
        SELECT interpolate_fill(
            CREATE_TIME_SERIES(time, measure_value::double), {'TIMESTAMP' if cast_timestamp else ''} '{later_time}', 0
        ) FROM {db_name}.{table_name}
        """
        result = aws_client.timestream_query.query(QueryString=query)
        snapshot.match("select-interpolate-fill-timestamp", result)

        # select fill interpolation from time series (sequence of timestamps)
        query = f"""
        SELECT interpolate_fill(
            CREATE_TIME_SERIES(time, measure_value::double),
            SEQUENCE(min(time), max(time), 1s),
            0
        )
        FROM {db_name}.{table_name}
        """
        result = aws_client.timestream_query.query(QueryString=query)
        snapshot.match("select-interpolate-fill-sequence", result)

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(paths=["$..ColumnInfo..Name"])
    def test_unnest_function(self, create_table_with_data, aws_client, snapshot):
        # create table with test data
        time_now = now_utc()
        db_name, table_name, _ = create_table_with_data(start_time=time_now)

        query = f"""
        WITH interpolated_timeseries AS (
            SELECT region, measure_name,
                INTERPOLATE_LINEAR(
                    CREATE_TIME_SERIES(time, measure_value::double),
                        SEQUENCE(min(time), max(time), 1s)) AS interpolated_series
            FROM {db_name}.{table_name}
            GROUP BY region, measure_name
            )
        SELECT region, measure_name, avg(value)
        FROM interpolated_timeseries
        CROSS JOIN UNNEST(interpolated_series)
        GROUP BY region, measure_name
        """
        # run query
        result = aws_client.timestream_query.query(QueryString=query)

        # slightly adjust result, to avoid rounding errors like 3.0555555555555554 → 3.055555555555556
        value = result["Rows"][0]["Data"][2]["ScalarValue"]
        if re.match(r"\d+\.\d{10,}", value):
            result["Rows"][0]["Data"][2]["ScalarValue"] = format_number(float(value), decimals=10)

        snapshot.match("unnest", result)


class TestTimestreamBasic:
    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(paths=["$..Address"])
    def test_describe_endpoints(self, create_table_with_data, aws_client, snapshot):
        db_name, table_name, _ = create_table_with_data(num_entries=5)
        endpoints = aws_client.timestream_write.describe_endpoints()["Endpoints"]
        snapshot.match("endpoints", endpoints)

        aws_client.timestream_write.delete_table(DatabaseName=db_name, TableName=table_name)
        aws_client.timestream_write.delete_database(DatabaseName=db_name)

    @markers.aws.validated
    def test_list_tags_for_resource(self, aws_client, create_db_and_table, snapshot):
        tags = [{"Key": "k1", "Value": "v1"}]

        # create db with tags
        db_name, _ = create_db_and_table(db_tags=tags)
        describe_result = aws_client.timestream_write.describe_database(DatabaseName=db_name)
        arn = describe_result["Database"]["Arn"]
        result = aws_client.timestream_write.list_tags_for_resource(ResourceARN=arn)
        snapshot.match("database_with_tags", result)

        # create db without tags
        db_name, _ = create_db_and_table()
        describe_result = aws_client.timestream_write.describe_database(DatabaseName=db_name)
        arn = describe_result["Database"]["Arn"]
        result_no_tags = aws_client.timestream_write.list_tags_for_resource(ResourceARN=arn)
        snapshot.match("database_without_tags", result_no_tags)

        # tag it
        aws_client.timestream_write.tag_resource(ResourceARN=arn, Tags=tags)
        result_added_tags = aws_client.timestream_write.list_tags_for_resource(ResourceARN=arn)
        snapshot.match("database_added_tags", result_added_tags)

        # remove tags
        aws_client.timestream_write.untag_resource(ResourceARN=arn, TagKeys=["k1", "test"])
        result_removed_tags = aws_client.timestream_write.list_tags_for_resource(ResourceARN=arn)
        snapshot.match("database_removed_tags", result_removed_tags)
