import gzip
import json
import logging
import os
import re
import textwrap
from pathlib import Path
from typing import Dict

import pytest
from botocore.exceptions import ClientError
from localstack import config
from localstack.pro.core.services.athena.models import DEFAULT_WORKGROUP_NAME
from localstack.pro.core.services.glue.crawler_utils import TableParserParquet
from localstack.pro.core.utils.aws import arns
from localstack.pro.core.utils.aws.aws_utils import run_athena_queries
from localstack.testing.config import TEST_AWS_ACCESS_KEY_ID, TEST_AWS_SECRET_ACCESS_KEY
from localstack.testing.pytest import markers
from localstack.utils.collections import select_attributes
from localstack.utils.strings import short_uid, to_bytes, to_str
from localstack.utils.sync import retry
from localstack.utils.testutil import map_all_s3_objects
from pyathena import connect

from tests.aws.services.glue.conftest import skip_bigdata_in_ci, wait_for_db_available_in_hive

LOG = logging.getLogger(__name__)


@pytest.fixture
def athena_db(aws_client):
    db_name = f"db{short_uid()}"
    TestAthena.run_query(f"CREATE DATABASE {db_name}", aws_client.athena, s3_client=aws_client.s3)

    yield db_name

    try:
        TestAthena.run_query(
            f"DROP DATABASE {db_name} CASCADE", aws_client.athena, s3_client=aws_client.s3
        )
    except Exception as e:
        LOG.info("Unable to drop Athena database %s: %s", db_name, e)


@pytest.fixture
def create_prepared_statement(aws_client):
    statements = []

    def _create(**kwargs):
        if not kwargs.get("StatementName"):
            kwargs["StatementName"] = f"stmt_{short_uid()}"
        aws_client.athena.create_prepared_statement(**kwargs)
        statements.append(kwargs)
        return kwargs

    yield _create

    for s in statements:
        try:
            aws_client.athena.delete_prepared_statement(
                WorkGroup=s["WorkGroup"], StatementName=s["StatementName"]
            )
        except Exception as e:
            LOG.debug("Unable to delete Athena prepared statement %s: %s", s, e)


@pytest.fixture
def athena_workgroup(aws_client):
    wg_name = f"wg-{short_uid()}"
    kwargs = {"Name": wg_name, "Description": "test work group"}
    aws_client.athena.create_work_group(**kwargs)

    yield kwargs

    aws_client.athena.delete_work_group(WorkGroup=wg_name)


@pytest.fixture
def run_athena_query(aws_client):
    def _run(query, **kwargs):
        return TestAthena.run_query(
            query, athena_client=aws_client.athena, s3_client=aws_client.s3, **kwargs
        )

    return _run


@skip_bigdata_in_ci
@markers.skip_offline
class TestAthena:
    """Heavy-weight tests (using the bigdata container) that are skipped in CI"""

    @markers.aws.unknown
    def test_simple_query(self, s3_bucket, aws_client):
        # start query
        query = "SELECT 1, 2, 3"
        result = aws_client.athena.start_query_execution(
            QueryString=query, ResultConfiguration={"OutputLocation": f"s3://{s3_bucket}/output"}
        )
        query_id = result["QueryExecutionId"]

        # get query executions
        result = aws_client.athena.list_query_executions()["QueryExecutionIds"]
        assert query_id in result

        # get query execution details
        result = aws_client.athena.get_query_execution(QueryExecutionId=query_id)["QueryExecution"]
        assert result["QueryExecutionId"] == query_id
        assert "State" in result["Status"]
        assert "SubmissionDateTime" in result["Status"]

        # get query result
        def check_result():
            rows = aws_client.athena.get_query_results(QueryExecutionId=query_id)["ResultSet"][
                "Rows"
            ]
            assert len(rows) == 2
            expected_column_headers = [
                {"VarCharValue": "_col0"},
                {"VarCharValue": "_col1"},
                {"VarCharValue": "_col2"},
            ]
            expected = [{"VarCharValue": "1"}, {"VarCharValue": "2"}, {"VarCharValue": "3"}]
            assert rows[0]["Data"] == expected_column_headers
            assert rows[1]["Data"] == expected

        # note: can take a long time in CI until all bigdata installations are bootstrapped
        retry(check_result, retries=50, sleep=6)

    @markers.aws.unknown
    def test_query_execution_without_result_config(self, athena_db, aws_client):
        """Test query executions in Athena without specifying a result configuration"""

        # start query
        query = "SELECT 1, 2, 3"
        result = aws_client.athena.start_query_execution(
            QueryString=query, QueryExecutionContext={"Database": athena_db}
        )
        query_id = result["QueryExecutionId"]

        # get query executions
        result = aws_client.athena.list_query_executions()["QueryExecutionIds"]
        assert query_id in result

        # get query execution details
        result = aws_client.athena.get_query_execution(QueryExecutionId=query_id)["QueryExecution"]
        assert result["QueryExecutionId"] == query_id
        assert "State" in result["Status"]
        assert "SubmissionDateTime" in result["Status"]

        # get query result
        def check_result():
            rows = aws_client.athena.get_query_results(QueryExecutionId=query_id)["ResultSet"][
                "Rows"
            ]
            assert len(rows) == 2
            assert "Data" in rows[0]
            assert len(rows[0]["Data"]) == 3

        retry(check_result, retries=13, sleep=6)

    @markers.aws.unknown
    def test_count_query(self, aws_client):
        # start query
        query = "select count(*)"
        result = aws_client.athena.start_query_execution(QueryString=query)
        query_id = result["QueryExecutionId"]

        # get query executions
        result = aws_client.athena.list_query_executions()["QueryExecutionIds"]
        assert query_id in result

        # get query execution details
        result = aws_client.athena.get_query_execution(QueryExecutionId=query_id)["QueryExecution"]
        assert result["QueryExecutionId"] == query_id
        assert "State" in result["Status"]
        assert "SubmissionDateTime" in result["Status"]

        # get query result
        def check_result():
            rows = aws_client.athena.get_query_results(QueryExecutionId=query_id)["ResultSet"][
                "Rows"
            ]
            assert len(rows) == 2
            assert rows[0].get("Data") == [{"VarCharValue": "_col0"}]
            assert rows[1].get("Data") == [{"VarCharValue": "1"}]

        retry(check_result, retries=13, sleep=6)

    @markers.aws.unknown
    def test_query_pyathena_pandas(self, region_name):
        from pyathena.pandas.cursor import PandasCursor

        conn = connect(
            s3_staging_dir="s3://s3-results-bucket/output/",
            cursor_class=PandasCursor,
            region_name=region_name,
            endpoint_url=config.internal_service_url(),
            aws_access_key_id=TEST_AWS_ACCESS_KEY_ID,
            aws_secret_access_key=TEST_AWS_SECRET_ACCESS_KEY,
        )
        cursor = conn.cursor()

        df = cursor.execute("SELECT 1,2,3 AS test").as_pandas()
        assert not df.empty, "DataFrame should not be empty"
        assert list(df.columns.values) == ["_col0", "_col1", "test"], "Column names are not correct"
        assert list(df.head(1).values[0]) == [1, 2, 3], "Row data is not correct"

    @markers.aws.unknown
    def test_query_pyathena(self, region_name):
        db_name = f"db{short_uid()}"

        def _connect(schema_name="default"):
            connection = connect(
                s3_staging_dir="s3://test/path/",
                endpoint_url=config.internal_service_url(),
                schema_name=schema_name,
                region_name=region_name,
                aws_access_key_id=TEST_AWS_ACCESS_KEY_ID,
                aws_secret_access_key=TEST_AWS_SECRET_ACCESS_KEY,
            )
            return connection.cursor()

        # create database schema
        with _connect() as cursor:
            cursor.execute(f"CREATE DATABASE {db_name}")
        # assert queries can be run against the specified schema name
        with _connect(db_name) as cursor:
            cursor.execute("CREATE TABLE table1(id int)")
            cursor.execute("INSERT INTO table1(id) VALUES (123)")
            result = cursor.execute("SELECT * FROM table1")
            assert list(result) == [(123,)]

        # clean up
        with _connect() as cursor:
            cursor.execute(f"DROP TABLE {db_name}.table1")
            cursor.execute(f"DROP DATABASE {db_name}")

    @markers.aws.unknown
    def test_unnest_function(self):
        table = f"t{short_uid()}"

        # create tmp table with array/struct definition
        query = f"""
        CREATE TABLE IF NOT EXISTS {table}(
            invoiceitems array<struct<productid:string,unitamount:double,quantity:int>>)
        """
        self.run_query(query)

        # insert row into table
        query = f"""
        INSERT INTO {table} SELECT ARRAY[CAST(ROW('id1', 12.3, 1) AS
            ROW(productid VARCHAR, unitamount DOUBLE, quantity INTEGER))]
        """
        self.run_query(query)

        # select data from table using UNNEST(..)
        query = f"""
        SELECT items.productId, items.quantity
        FROM {table} i
        CROSS JOIN UNNEST(invoiceItems) t(items)
        """
        result = self.run_query(query)
        result = result["ResultSet"]["Rows"][1]["Data"]
        assert result == [{"VarCharValue": "id1"}, {"VarCharValue": "1"}]

        # clean up
        self.run_query(f"DROP TABLE {table}")

    @pytest.mark.parametrize("use_partitions", [True, False])
    @markers.aws.unknown
    def test_query_from_s3_external_table(self, s3_bucket, use_partitions, aws_client):
        table = f"t{short_uid()}"
        prefix = "prefix/"

        # create data files
        entries = [{"id": "i1", "number": 1}, {"id": "i2", "number": 2}, {"id": "i3", "number": 3}]
        content = "\n".join(json.dumps(obj) for obj in entries)
        key = f"{prefix}{'p1=foo/p2=bar/' if use_partitions else ''}entries.json"
        aws_client.s3.put_object(Bucket=s3_bucket, Key=key, Body=to_bytes(content))

        # create external table
        query = f"""
        CREATE EXTERNAL TABLE {table}(`id` STRING, `number` INT)
        ROW FORMAT SERDE 'org.apache.hive.hcatalog.data.JsonSerDe' WITH SERDEPROPERTIES ('paths'='id,number')
        STORED AS INPUTFORMAT 'org.apache.hadoop.mapred.TextInputFormat'
            OUTPUTFORMAT 'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat'
        LOCATION 's3://{s3_bucket}/{prefix}'
        TBLPROPERTIES ('classification'='json', 'compressionType'='none', 'typeOfData'='file')
        """
        if use_partitions:
            query = query.replace(
                "ROW FORMAT", "PARTITIONED BY (`p1` STRING, `p2` STRING) ROW FORMAT"
            )
        self.run_query(query)
        if use_partitions:
            # ensure that partitions are sync'ed into metastore
            self.run_query(f"MSCK REPAIR TABLE {table}")

        # run select query
        result = self.run_query(f"SELECT * FROM {table}")
        title_row = {"Data": [{"VarCharValue": "id"}, {"VarCharValue": "number"}]}
        data_rows = [
            {"Data": [{"VarCharValue": f"i{i}"}, {"VarCharValue": str(i)}]} for i in range(1, 4)
        ]
        if use_partitions:
            title_row["Data"].extend([{"VarCharValue": "p1"}, {"VarCharValue": "p2"}])
            for i in range(0, 3):
                data_rows[i]["Data"].extend([{"VarCharValue": "foo"}, {"VarCharValue": "bar"}])
        expected = [title_row] + data_rows
        assert result["ResultSet"]["Rows"] == expected

        # clean up
        self.run_query(f"DROP TABLE {table}")

    @markers.aws.only_localstack
    def test_parallel_table_creations(self, s3_bucket, aws_client, athena_db):
        """Ensures that Athena tables can be created in parallel in LocalStack."""
        tables = [f"t{short_uid()}" for _ in range(0, 10)]
        queries = [f"CREATE EXTERNAL TABLE {table}(id int)" for table in tables]

        results = run_athena_queries(
            queries, QueryExecutionContext={"Database": athena_db}, timeout=150
        )
        assert all(results)

    @pytest.mark.parametrize("skip_header_line", [True, False])
    @pytest.mark.parametrize("simple_serde", [True, False])
    @markers.aws.unknown
    def test_query_csv_files_from_s3(self, s3_bucket, skip_header_line, simple_serde, aws_client):
        table = f"t{short_uid()}"
        prefix = "prefix/test-123/"

        # create CSV data files
        entries = ("i1,123,true", "i2,456,false")
        if skip_header_line:
            entries = ("id,number,test",) + entries
        content = "\n".join(entries)
        key = f"{prefix}entries.csv"
        aws_client.s3.put_object(Bucket=s3_bucket, Key=key, Body=to_bytes(content))

        # prepare query
        if simple_serde:
            row_format = "DELIMITED FIELDS TERMINATED BY ','"
        else:
            row_format = (
                r"SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde' "
                r"WITH SERDEPROPERTIES ('separatorChar' = ',','quoteChar' = '\"','escapeChar' = '\\')"
            )

        tbl_props = "TBLPROPERTIES ('skip.header.line.count'='1')" if skip_header_line else ""

        # run query to create external table
        query = rf"""
        CREATE EXTERNAL TABLE {table}(`id` STRING, `number` INT, `test` BOOLEAN)
        ROW FORMAT {row_format}
        STORED AS TEXTFILE
        LOCATION 's3://{s3_bucket}/{prefix}'
        {tbl_props}
        """
        self.run_query(query)

        # run select query
        result = self.run_query(f"SELECT * FROM {table}")
        rows = result["ResultSet"]["Rows"]
        cols = result["ResultSet"]["ResultSetMetadata"]["ColumnInfo"]
        expected_rows = [
            {
                "Data": [
                    {"VarCharValue": "id"},
                    {"VarCharValue": "number"},
                    {"VarCharValue": "test"},
                ]
            },
            {"Data": [{"VarCharValue": "i1"}, {"VarCharValue": "123"}, {"VarCharValue": "true"}]},
            {"Data": [{"VarCharValue": "i2"}, {"VarCharValue": "456"}, {"VarCharValue": "false"}]},
        ]
        expected_cols = [
            {"Name": "id", "Type": "varchar"},
            {"Name": "number", "Type": "integer"},
            {"Name": "test", "Type": "boolean"},
        ]
        if not simple_serde:
            # note: OpenCSVSerde does not preserve types, converts all columns to varchar
            for col in expected_cols:
                col["Type"] = "varchar"
        assert rows == expected_rows
        short_cols = [select_attributes(col, ["Name", "Type"]) for col in cols]
        assert short_cols == expected_cols

        # clean up
        self.run_query(f"DROP TABLE {table}")

    @markers.aws.validated
    def test_csv_serde_alter_table(self, athena_db, s3_create_bucket, run_athena_query, snapshot):
        bucket_name = f"ls-tmp-test-{short_uid()}"
        s3_create_bucket(Bucket=bucket_name)

        # create table
        table_name = f"t{short_uid()}"
        query = f"""
        CREATE EXTERNAL TABLE IF NOT EXISTS {athena_db}.{table_name} (`test` string )
        ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
        WITH SERDEPROPERTIES ('separatorChar' = ',')
        STORED AS TEXTFILE LOCATION 's3://{bucket_name}/test'
        """
        result = run_athena_query(query)
        snapshot.match("create-table", result)

        # add column to table
        query = f"ALTER TABLE {athena_db}.{table_name} ADD COLUMNS (test2 string)"
        result = run_athena_query(query)
        snapshot.match("alter-table", result)

        # describe table
        query = f"DESCRIBE {athena_db}.{table_name}"
        result = run_athena_query(query)
        # Note: Weirdly, Athena is concatenating the values of each row into a single cell, separated by "\t",
        #  even though the column metadata contains 3 col definitions. Preparing the result here, to allow for
        #  snapshot comparison (in future we may adjust the returned values for parity, but still need to confirm
        #  if the same format is used for all DESCRIBE queries).
        rows = result["ResultSet"]["Rows"]
        for row in rows:
            if len(row["Data"]) == 1:
                values = re.split(r"\s*\t", row["Data"][0]["VarCharValue"].strip())
                row["Data"] = [{"VarCharValue": val} for val in values]
            # ignore column type comment (3rd cell) for now - value is "from deserializer" in real AWS
            row["Data"][2]["VarCharValue"] = "<comment>"
        snapshot.match("describe-table", result)

    @markers.aws.validated
    def test_list_databases(self, athena_db, aws_client):
        # get data catalog
        catalog = aws_client.athena.list_data_catalogs()["DataCatalogsSummary"][0]["CatalogName"]

        # list databases
        result = aws_client.athena.list_databases(CatalogName=catalog)
        databases = [db["Name"] for db in result["DatabaseList"]]
        assert athena_db in databases
        # get database
        result = aws_client.athena.get_database(DatabaseName=athena_db, CatalogName=catalog)
        assert result["Database"]["Name"] == athena_db

    @markers.aws.unknown
    def test_query_with_tmp_table_multiline(self, athena_db, aws_client):
        # create table, insert data
        self.run_query("CREATE TABLE table1(id int)", QueryExecutionContext={"Database": athena_db})
        self.run_query(
            "INSERT INTO table1(id) VALUES (1), (2), (3)",
            QueryExecutionContext={"Database": athena_db},
        )

        query1 = """
        with tmp as (SELECT * FROM table1
            )
        select *
        from tmp
        """
        query2 = """ with tmp as (SELECT * FROM table1) select * from tmp """
        for query in [query1, query2]:
            result = self.run_query(query, QueryExecutionContext={"Database": athena_db})
            rows = [row["Data"][0]["VarCharValue"] for row in result["ResultSet"]["Rows"]]
            assert rows == ["id", "1", "2", "3"]

    @markers.aws.unknown
    def test_create_prepared_statements(
        self, athena_workgroup, create_prepared_statement, aws_client
    ):
        # create
        wg_name = athena_workgroup["Name"]
        statement = create_prepared_statement(WorkGroup=wg_name, QueryStatement="SELECT 123")
        stmt_name = statement["StatementName"]

        # query
        result = self.run_query(f"EXECUTE {stmt_name}", WorkGroup=wg_name)
        result_rows = result["ResultSet"]["Rows"]
        assert result_rows == [
            {"Data": [{"VarCharValue": "_col0"}]},
            {"Data": [{"VarCharValue": "123"}]},
        ]
        result_cols = result["ResultSet"]["ResultSetMetadata"]["ColumnInfo"]
        result_cols = [select_attributes(col, ["Name", "Type"]) for col in result_cols]
        assert result_cols == [{"Name": "_col0", "Type": "integer"}]

        # get
        result = aws_client.athena.get_prepared_statement(
            WorkGroup=wg_name, StatementName=stmt_name
        )
        assert result["PreparedStatement"]["WorkGroupName"] == wg_name
        assert result["PreparedStatement"]["QueryStatement"] == "SELECT 123"

        with pytest.raises(ClientError) as e:
            aws_client.athena.get_prepared_statement(WorkGroup="_invalid_", StatementName=stmt_name)
        assert e.value.response["Error"]["Code"] == "InvalidRequestException"
        with pytest.raises(ClientError) as e:
            aws_client.athena.get_prepared_statement(WorkGroup=wg_name, StatementName="_invalid_")
        assert e.value.response["Error"]["Code"] == "ResourceNotFoundException"

        # list
        result = aws_client.athena.list_prepared_statements(WorkGroup=wg_name)
        statements = [stmt["StatementName"] for stmt in result["PreparedStatements"]]
        assert statements == [stmt_name]

        # delete
        aws_client.athena.delete_prepared_statement(WorkGroup=wg_name, StatementName=stmt_name)
        with pytest.raises(ClientError) as e:
            aws_client.athena.get_prepared_statement(WorkGroup=wg_name, StatementName=stmt_name)

    @markers.aws.unknown
    def test_query_prepared_statement(self, athena_db, aws_client):
        self.run_query("CREATE TABLE table1(id int)", QueryExecutionContext={"Database": athena_db})
        self.run_query(
            "INSERT INTO table1(id) VALUES (1), (2), (3)",
            QueryExecutionContext={"Database": athena_db},
        )
        self.run_query(
            "PREPARE prep_stmt FROM SELECT * FROM table1 WHERE id = ? ORDER BY id DESC",
            QueryExecutionContext={"Database": athena_db},
        )
        result = self.run_query(
            "EXECUTE prep_stmt USING 2", QueryExecutionContext={"Database": athena_db}
        )
        result_rows = result["ResultSet"]["Rows"]
        assert result_rows == [
            {"Data": [{"VarCharValue": "id"}]},
            {"Data": [{"VarCharValue": "2"}]},
        ]
        result_cols = result["ResultSet"]["ResultSetMetadata"]["ColumnInfo"]
        result_cols = [select_attributes(col, ["Name", "Type"]) for col in result_cols]
        assert result_cols == [{"Name": "id", "Type": "integer"}]

    @markers.aws.unknown
    def test_query_via_awswrangler(self, monkeypatch, aws_client, region_name):
        import awswrangler

        # set wrangler endpoints
        edge_url = config.internal_service_url()
        awswrangler.config.athena_endpoint_url = edge_url
        awswrangler.config.glue_endpoint_url = edge_url
        awswrangler.config.s3_endpoint_url = edge_url
        awswrangler.config.sts_endpoint_url = edge_url
        monkeypatch.setenv("AWS_DEFAULT_REGION", region_name)
        monkeypatch.setenv("AWS_ACCESS_KEY_ID", TEST_AWS_ACCESS_KEY_ID)
        monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", TEST_AWS_SECRET_ACCESS_KEY)

        # create database
        db_name = f"db_{short_uid()}"
        awswrangler.catalog.create_database(db_name, exist_ok=True)
        wait_for_db_available_in_hive(db_name)

        # query data - note: "CTAS" stands for "Create Table AS"
        result = awswrangler.athena.read_sql_query(
            "SELECT 1 AS test", database=db_name, ctas_approach=True
        )
        assert result.query_metadata["Status"]["State"] == "SUCCEEDED"
        assert result.query_metadata["Statistics"]["DataManifestLocation"]

        # assert that DB is propagated into Glue catalog
        result = aws_client.glue.get_database(Name=db_name)
        assert result["Database"]["Name"] == db_name

    @pytest.mark.parametrize("query_engine", ["trino", "hive"])
    @markers.aws.unknown
    def test_create_iceberg_table_queries(self, s3_bucket, query_engine, aws_client):
        table_name = f"test{short_uid()}"
        if query_engine == "trino":
            # note: currently still required to specify the fully qualified name with catalog "iceberg" explicitly
            table_name = f"iceberg.default.{table_name}"
            query = f"""
                CREATE TABLE {table_name} (c1 integer, c2 varchar, c3 double)
                WITH (format='PARQUET', partitioning=ARRAY['c1','c2'], location='s3://{s3_bucket}/prefix/')
                """
        else:
            query = f"""
                CREATE TABLE {table_name} (c1 integer, c2 string, c3 double)
                LOCATION 's3://{s3_bucket}/prefix/' TBLPROPERTIES ( 'table_type' = 'ICEBERG' )
                """
        self.run_query(query)

        # assert that table properties are recorded in Glue catalog (for Hive query with `table_type`)
        if query_engine == "hive":
            tables = aws_client.glue.get_tables(DatabaseName="default")["TableList"]
            matching = [tab for tab in tables if tab["Name"] == table_name]
            assert len(matching) == 1
            assert matching[0]["Parameters"].get("table_type") == "ICEBERG"

        # insert data
        self.run_query(f"INSERT INTO {table_name}(c1, c2, c3) VALUES (1, '2022-01-01', 2)")
        self.run_query(f"INSERT INTO {table_name}(c1, c2, c3) VALUES (3, '2022-01-02', 4)")
        # query data from table
        result = self.run_query(f"SELECT * FROM {table_name}")
        assert len(result["ResultSet"]["Rows"]) == 3

        # assert that Iceberg metadata files have been created in S3
        result = map_all_s3_objects(to_json=False, buckets=[s3_bucket], s3_client=aws_client.s3)
        expected_keys = [
            r".+\.avro$",
            r".+\.metadata.json$",
            r".+\.parquet$",
        ]
        if query_engine == "trino":
            expected_keys += [".+data/c1=1/c2=2022-01-01/", ".+data/c1=3/c2=2022-01-02/"]
        for expected in expected_keys:
            matching = [entry for entry in result if re.match(expected, entry)]
            assert matching

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(
        [
            "$..ResultSet.ResultSetMetadata.ColumnInfo..CaseSensitive",
            "$..ResultSet.ResultSetMetadata.ColumnInfo..Precision",
            "$..ResultSet.ResultSetMetadata.ColumnInfo..Type",
            "$..ResultSet.Rows..Data..VarCharValue",
            "$..UpdateCount",
        ]
    )
    def test_iceberg_table_partitioning(
        self, s3_bucket, aws_client, athena_db, run_athena_query, snapshot
    ):
        """
        Test that creates a table in Hive syntax with partitioning, and then inserts/selects data in Trino syntax.
        This transparent switch between catalogs is enabled by the following configs we're setting:
            - hive.iceberg-catalog-name=iceberg
            - iceberg.hive-catalog-name=hive
        """
        query_table = f"{athena_db}.iceberg_table"

        # Create Iceberg table (Hive syntax)
        query = f"""
        CREATE TABLE IF NOT EXISTS {query_table} (`message_id` string, `subject` string, `countries` array<string>, `tenant_id` bigint, `dt` date)
        PARTITIONED BY (`tenant_id`, `dt`)
        LOCATION 's3://{s3_bucket}/iceberg_table/'
        TBLPROPERTIES ( 'table_type' = 'ICEBERG' )
        """
        result = run_athena_query(query)
        snapshot.match("create-table", result)

        # Insert data (Presto/Trino syntax, with 'ARRAY[...]')
        query = f"""
        INSERT INTO {query_table} (tenant_id, dt, message_id, subject, countries)
        VALUES (123, date '2022-01-01', 'msg1', 'sub 123', ARRAY['c1', 'c2'])
        """
        result = run_athena_query(query)
        snapshot.match("insert-data", result)

        # Select data
        query = f"SELECT * FROM {query_table}"
        result = run_athena_query(query)
        snapshot.match("select-data", result)

        # update the data
        query = f"UPDATE {query_table} SET message_id='msg1_updated' WHERE tenant_id=123"
        run_athena_query(query)

        # Select updated data
        query = f"SELECT * FROM {query_table}"
        result = run_athena_query(query)
        snapshot.match("select-updated-data", result)

        # TODO re-enable checking parititons once the partition support is properly implemented for Iceberg
        # assert partitioned paths are created in S3
        # result = map_all_s3_objects(to_json=False, buckets=[s3_bucket], s3_client=aws_client.s3)
        # prefix = f"{s3_bucket}/iceberg_table/data/tenant_id=123/dt=2022-01-01/"
        # matching = [k for k in result.keys() if k.startswith(prefix)]
        # assert len(matching) == 2
        # assert all(match.endswith(".parquet") for match in matching)

    @pytest.mark.parametrize("define_columns", [True, pytest.param(False, marks=pytest.mark.skip)])
    @pytest.mark.aws_validated
    @markers.snapshot.skip_snapshot_verify(
        # TODO: some column headers in SELECT result still have a mismatch
        paths=[
            "$..ResultSet.ResultSetMetadata.ColumnInfo",
            "$..UpdateCount",
        ]
    )
    def test_create_deltalake_table_queries(
        self, define_columns, aws_client, athena_db, s3_create_bucket, run_athena_query, snapshot
    ):
        if not define_columns:
            # TODO define_columns=False currently fails, because it does not detect the column definition yet
            # - https://docs.aws.amazon.com/athena/latest/ug/delta-lake-tables.html
            # - "Note the omission of column definitions, SerDe library, and other table properties.
            #    Unlike traditional Hive tables, Delta Lake table metadata are inferred from the Delta Lake
            #    transaction log and synchronized directly to AWS Glue."
            # - This means we need crawler abilities to detect the schema.
            # - BUT: The first deltalake metadata file seems to contain this already?
            LOG.warning("Auto-detecting Delta Lake table columns currently not yet supported")

        # upload the deltalake table data to S3
        bucket_name = s3_create_bucket()
        path = Path(os.path.join(os.path.dirname(__file__), "./deltalake/"))
        for file_path in path.rglob("*"):
            if file_path.is_dir():
                continue
            relative_path = os.path.relpath(file_path, path)
            path_in_bucket = os.path.join("test", relative_path)
            aws_client.s3.upload_file(str(file_path), Bucket=bucket_name, Key=path_in_bucket)

        column_defs = ""
        if define_columns:
            column_defs = "(letter string, number bigint)"

        # create table
        table_name = f"t{short_uid()}"
        query = (
            f"CREATE EXTERNAL TABLE {athena_db}.{table_name} {column_defs} "
            f"LOCATION 's3://{bucket_name}/test/' "
            f"TBLPROPERTIES ('table_type' = 'DELTA')"
        )
        result = run_athena_query(query)
        snapshot.match("create-table", result)

        # describe table
        query = f"DESCRIBE {athena_db}.{table_name}"
        result = run_athena_query(query)
        assert result["ResultSet"]["ResultSetMetadata"]
        assert result["ResultSet"]["Rows"]
        # TODO: lots of mismatches in the DESCRIBE result - to be fixed!
        # snapshot.match("describe-table", result)

        # select all data
        # Note: adding catalog prefix "deltalake." apparently required (otherwise getting
        #   error "Cannot query Delta Lake table"). See also Iceberg query tests above.
        query = f"SELECT * FROM deltalake.{athena_db}.{table_name}"
        result = run_athena_query(query)
        snapshot.match("select", result)

    @pytest.mark.parametrize("file_format", ["PARQUET", "JSON"])
    @pytest.mark.aws_validated
    def test_execute_unload_query_to_s3(
        self, aws_client, file_format, s3_create_bucket, run_athena_query, snapshot
    ):
        bucket_name = s3_create_bucket()

        # execute UNLOAD query to S3 bucket
        query = textwrap.dedent(
            f"""
            UNLOAD (SELECT * FROM (VALUES (1, 'a'), (2, 'b'), (3, 'c')) AS t (id, name))
            TO 's3://{bucket_name}/test/' WITH (format = '{file_format}')
        """
        )
        run_athena_query(query)

        # list file contents from S3 bucket
        result = map_all_s3_objects(to_json=False, buckets=[bucket_name], s3_client=aws_client.s3)
        assert len(result) == 1

        # assert that data file contains result of the query
        file_content = list(result.values())[0]
        if file_format == "JSON":
            file_content = gzip.decompress(file_content)
            data_rows = []
            for line in to_str(file_content).splitlines():
                if line.strip():
                    data_rows.append(json.loads(line))
        else:
            table = TableParserParquet().parse(content=file_content)
            assert len(table.rows) == 3
            data_rows = [dict(row) for row in table.rows]
        snapshot.match("query-result-file-content", data_rows)

    @markers.aws.validated
    def test_create_and_query_view(
        self, run_athena_query, snapshot, cleanups, s3_bucket, aws_client
    ):
        table_name = f"t_{short_uid()}"
        view_name = f"v_{short_uid()}"

        # create simple CSV data file
        content = "foo\nbar\nbaz"
        aws_client.s3.put_object(Bucket=s3_bucket, Key="test/datas.csv", Body=to_bytes(content))

        # create table
        query = f"""
        CREATE EXTERNAL TABLE IF NOT EXISTS {table_name} (`test` string )
        ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
        STORED AS TEXTFILE LOCATION 's3://{s3_bucket}/test'
        """
        run_athena_query(query)
        cleanups.append(lambda: run_athena_query(f"DROP TABLE {table_name}"))

        query = f"CREATE VIEW {view_name} AS (SELECT * FROM {table_name})"
        run_athena_query(query)
        cleanups.append(lambda: run_athena_query(f"DROP VIEW {view_name}"))
        result = run_athena_query(f"SELECT * FROM {view_name}")
        snapshot.match("result", result["ResultSet"]["Rows"])

    # TODO: implement support for information_schema.columns queries!
    @pytest.mark.skip(reason="information_schema.* queries currently not yet supported")
    @markers.aws.validated
    def test_query_info_schema_columns(
        self, run_athena_query, snapshot, s3_bucket, aws_client, cleanups
    ):
        # create table
        table_name = f"t_{short_uid()}"
        query = f"""
        CREATE EXTERNAL TABLE IF NOT EXISTS {table_name} (`col1` string )
        ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
        STORED AS TEXTFILE LOCATION 's3://{s3_bucket}/test'
        """
        run_athena_query(query)
        cleanups.append(lambda: run_athena_query(f"DROP TABLE {table_name}"))

        query = f"SELECT * FROM information_schema.columns WHERE table_name='{table_name}'"
        result = run_athena_query(query)
        snapshot.match("select-columns", result["ResultSet"]["Rows"])

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(
        paths=["$..ResultSet.ResultSetMetadata.ColumnInfo..Precision", "$..UpdateCount"]
    )
    def test_create_with_inferred_location(
        self, run_athena_query, s3_bucket, cleanups, aws_client, snapshot
    ):
        source_table = f"t_{short_uid()}"
        no_loc_table = f"t_{short_uid()}"
        conf = {"OutputLocation": f"s3://{s3_bucket}/results"}

        # Create a source table
        run_athena_query(
            query=f"""CREATE EXTERNAL TABLE default.{source_table} (id INT)
             LOCATION 's3://{s3_bucket}/table-{source_table}'""",
            ResultConfiguration=conf,
        )
        cleanups.append(lambda: run_athena_query(f"DROP TABLE default.{source_table}"))
        run_athena_query(
            query=f"INSERT INTO default.{source_table} (id) VALUES 1, 2, 3",
            ResultConfiguration=conf,
        )

        # Create an internal table from the source table
        query = f"""CREATE TABLE default.{no_loc_table} WITH (format='JSON')
            AS SELECT * FROM default.{source_table}"""
        run_athena_query(
            query=query,
            ResultConfiguration=conf,
        )
        cleanups.append(
            lambda: run_athena_query(f"DROP TABLE default.{no_loc_table}", ResultConfiguration=conf)
        )

        # Query the data from internal table
        no_loc_select = run_athena_query(
            f"SELECT * FROM default.{no_loc_table}", ResultConfiguration=conf
        )
        snapshot.match("select-all", no_loc_select)

    @classmethod
    def run_query(cls, query: str, athena_client=None, s3_client=None, **kwargs) -> Dict:
        result = run_athena_queries(
            query, timeout=150, athena_client=athena_client, s3_client=s3_client, **kwargs
        )
        return result[0]


class TestAthenaCrud:
    """Light-weight tests that are also executed in CI"""

    @markers.aws.unknown
    def test_create_named_query(self, aws_client):
        query = "SELECT 1, 2, 3"
        result = aws_client.athena.create_named_query(Name="q1", Database="db1", QueryString=query)
        query_id = result["NamedQueryId"]

        result = aws_client.athena.list_named_queries()
        assert query_id in result["NamedQueryIds"]

        aws_client.athena.delete_named_query(NamedQueryId=query_id)

        result = aws_client.athena.list_named_queries()
        assert query_id not in result["NamedQueryIds"]

    @markers.aws.unknown
    def test_create_workgroup(self, aws_client):
        wg_name = f"wg-{short_uid()}"

        def assert_size(name, count):
            result = aws_client.athena.list_work_groups()["WorkGroups"]
            filtered = [g for g in result if g["Name"] == name]
            assert len(filtered) == count

        # assert that default workgroup is present
        assert_size(DEFAULT_WORKGROUP_NAME, 1)

        aws_client.athena.create_work_group(Name=wg_name, Description="work group 123")
        assert_size(wg_name, 1)

        result = aws_client.athena.get_work_group(WorkGroup=wg_name)["WorkGroup"]
        assert result["Name"] == wg_name

        aws_client.athena.delete_work_group(WorkGroup=wg_name)
        assert_size(wg_name, 0)

    @markers.aws.unknown
    def test_create_data_catalog(self, aws_client):
        name = "dc1"

        def assert_size(size):
            result = aws_client.athena.list_data_catalogs()["DataCatalogsSummary"]
            filtered = [g for g in result if g["CatalogName"] == name]
            assert len(filtered) == size

        aws_client.athena.create_data_catalog(Name=name, Type="HIVE")
        assert_size(1)

        result = aws_client.athena.get_data_catalog(Name=name).get("DataCatalog")
        assert result["Name"] == name
        assert result["Type"] == "HIVE"

        aws_client.athena.delete_data_catalog(Name=name)
        assert_size(0)

    @markers.aws.unknown
    def test_list_tags_for_resource(self, aws_client, account_id, region_name):
        name = "wg1"

        aws_client.athena.create_work_group(
            Name=name, Description="work group 123", Tags=[{"Key": "test", "Value": "sample"}]
        )
        arn = arns.athena_work_group_arn(name, account_id, region_name)
        result = aws_client.athena.list_tags_for_resource(ResourceARN=arn)
        assert "Tags" in result

        # add tags
        tags = [{"Key": "k1", "Value": "v1"}]
        aws_client.athena.tag_resource(ResourceARN=arn, Tags=tags)
        result = aws_client.athena.list_tags_for_resource(ResourceARN=arn)
        assert tags[0] in result["Tags"]

        # remove tags
        aws_client.athena.untag_resource(ResourceARN=arn, TagKeys=["k1", "test"])
        result = aws_client.athena.list_tags_for_resource(ResourceARN=arn)
        assert result["Tags"] == []

        # clean up
        aws_client.athena.delete_work_group(WorkGroup=name)
