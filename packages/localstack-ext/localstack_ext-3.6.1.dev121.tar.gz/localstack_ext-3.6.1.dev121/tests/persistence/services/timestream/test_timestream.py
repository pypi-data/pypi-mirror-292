from localstack.pro.core.testing import persistence
from localstack.testing.pytest import markers
from localstack.utils.strings import short_uid


def test_describe_database(persistence_validations, snapshot, aws_client):
    db_name = f"db-{short_uid()}"
    aws_client.timestream_write.create_database(DatabaseName=db_name)

    def validate():
        snapshot.match(
            "describe_database", aws_client.timestream_write.describe_database(DatabaseName=db_name)
        )

    persistence_validations.register(validate)


@persistence.skip_cloudpods
@markers.snapshot.skip_snapshot_verify(paths=["$..QueryId"])
def test_timestream_write_query(persistence_validations, snapshot, aws_client):
    db_name = f"db-{short_uid()}"
    table_name = f"table-{short_uid()}"
    aws_client.timestream_write.create_database(DatabaseName=db_name)

    aws_client.timestream_write.create_table(DatabaseName=db_name, TableName=table_name)

    test_records = [
        {"MeasureName": "cpu", "MeasureValue": "60", "TimeUnit": "SECONDS", "Time": "1636986409"},
        {"MeasureName": "cpu", "MeasureValue": "80", "TimeUnit": "SECONDS", "Time": "1636986412"},
        {"MeasureName": "cpu", "MeasureValue": "70", "TimeUnit": "SECONDS", "Time": "1636986414"},
    ]

    aws_client.timestream_write.write_records(
        DatabaseName=db_name,
        TableName=table_name,
        Records=test_records,
    )

    def validate():
        query = f"SELECT CREATE_TIME_SERIES(time, measure_value::double) FROM {db_name}.{table_name} where measure_name = 'cpu'"
        result = aws_client.timestream_query.query(QueryString=query)
        snapshot.match("select-time-series", result)

    persistence_validations.register(validate)
