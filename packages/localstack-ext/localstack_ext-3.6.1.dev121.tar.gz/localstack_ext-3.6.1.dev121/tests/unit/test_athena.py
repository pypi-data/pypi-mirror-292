import re

import pytest
from localstack.pro.core.services.athena.query_utils import (
    extract_trino_prepared_statements,
    is_hive_ddl_query,
    prepare_query,
    rewrite_external_storage,
    rewrite_unnest_clauses,
)


def _canonicalize_query(query: str) -> str:
    """Small helper function to make processed queries comparable. Performs non-safe changes on spaces!"""
    # - Convert to lowercase and replace newlines with spaces
    query_lower = query.lower().replace("\n", " ")
    # - Replace multiple spaces with single spaces
    return re.sub(r"\s+", " ", query_lower)


class TestQueryUtils:
    # Some Hive DDL examples from https://cwiki.apache.org/confluence/display/Hive/LanguageManual+DDL
    hive_queries = [
        "CREATE TEMPORARY EXTERNAL DATABASE db1",
        "DROP TABLE table",
        "MSCK REPAIR TABLE",
        """
        create table table_name (
          id                int,
          dtDontQuery       string,
          name              string
        )
        partitioned by (date string)
        """,
        """
        CREATE TABLE page_view(viewTime INT, userid BIGINT,
            page_url STRING, referrer_url STRING,
            ip STRING COMMENT 'IP Address of the User')
        COMMENT 'This is the page view table'
        PARTITIONED BY(dt STRING, country STRING)
        STORED AS SEQUENCEFILE;
        """,
        """
        -- This is a hive query comment
        CREATE TABLE page_view(viewTime INT, userid BIGINT,
            page_url STRING, referrer_url STRING,
            ip STRING COMMENT 'IP Address of the User')
        """,
        """
        CREATE EXTERNAL TABLE page_view(viewTime INT, userid BIGINT,
            page_url STRING, referrer_url STRING,
            ip STRING COMMENT 'IP Address of the User',
            country STRING COMMENT 'country of origination')
        COMMENT 'This is the staging page view table'
        ROW FORMAT DELIMITED FIELDS TERMINATED BY '\054'
        STORED AS TEXTFILE
        LOCATION '<hdfs_location>';
        """,
        """
        ALTER TABLE page_view ADD PARTITION (dt='2008-08-08', country='us') location '/path/to/us/part080808'
                          PARTITION (dt='2008-08-09', country='us') location '/path/to/us/part080809';
        """,
        "ALTER TABLE table_name SET TBLPROPERTIES table_properties;",
        "ALTER TABLE table_name_2 EXCHANGE PARTITION (partition_spec) WITH TABLE table_name_1;",
        "CREATE TEMPORARY FUNCTION function_name AS class_name;",
        "DESCRIBE DATABASE EXTENDED db_name;",
        "DROP TABLE IF EXISTS table PURGE",
        "DROP MATERIALIZED VIEW materialized_view_name;",
        "SHOW FORMATTED INDEXES) ON table_with_index IN db_name;",
        "SHOW CREATE TABLE table1",
        "SHOW COLUMNS IN table1",
    ]

    @pytest.mark.parametrize("hive_query", hive_queries)
    def test_is_hive_ddl_query_with_ddl(self, hive_query: str):
        assert is_hive_ddl_query(hive_query)

    non_hive_queries = [
        "INSERT INTO table (column) VALUES ('MSCK REPAIR TABLE')",
        "SELECT * FROM table",
        "select * from table",
        "  select * from table",
        "\n  select * from table",
        "INSERT INTO table (column1, column2) VALUES ('value1', 'value2')",
        "SELECT 2018_b&m_capacity_(us$m) FROM table1",
        "SELECT COUNT(*) FROM table1",
        "CREATE VIEW test AS SELECT 1",
        "CREATE OR REPLACE VIEW test AS SELECT 1",
        """
        CREATE VIEW onion_referrers(url COMMENT 'URL of Referring page') COMMENT 'Referrers to The Onion website'
        AS SELECT DISTINCT referrer_url FROM page_view WHERE page_url='http://www.theonion.com';
        """,
        "DROP VIEW onion_referrers;",
    ]

    @pytest.mark.parametrize("non_hive_query", non_hive_queries)
    def test_is_hive_ddl_query_with_dql(self, non_hive_query: str):
        assert not is_hive_ddl_query(non_hive_query)

    @pytest.mark.parametrize("path", ["", "/", "/path"])
    @pytest.mark.parametrize("quote", ["'", '"'])
    @pytest.mark.parametrize("bucket", ["test-1-2-3", "mybucket1"])
    def test_rewrite_query_location(self, path, quote, bucket):
        # ensure that we always use a path, to avoid Hive error "Can not create a Path from an empty string"
        expected_path = path or "/"
        expected = f"location {quote}s3a://{bucket}{expected_path}{quote}"
        assert prepare_query(f"location {quote}s3://{bucket}{path}{quote}") == expected

    def test_rewrite_unnest_clauses(self):
        # test query that should get updated
        query = """
        SELECT items.productId, items.quantity
        FROM test1
        CROSS JOIN UNNEST(invoiceItems) AS t(items)
        """
        query = rewrite_unnest_clauses(query)
        assert "UNNEST(invoiceItems) AS items" in query
        assert "AS t(items)" not in query

        # test query that should remain unchanged
        query = """
        SELECT *
        FROM test1
        CROSS JOIN UNNEST(invoiceItems) AS t(items)
        """
        updated = rewrite_unnest_clauses(query)
        assert "AS t(items)" in query
        assert "AS items" not in query
        assert query == updated

    def test_extract_trino_prepared_statements(self):
        result = extract_trino_prepared_statements("  \n PREPARE stmt1 \tFROM SELECT  123 \n ")
        assert result == {"stmt1": "SELECT  123"}

        assert extract_trino_prepared_statements(" SELECT 123 ") == {}

    @pytest.mark.parametrize(
        "query, storage_handler",
        [
            (
                "CREATE TABLE test (c1 integer) LOCATION 's3://test' TBLPROPERTIES ( 'table_type' = 'ICEBERG' )",
                "org.apache.iceberg.mr.hive.HiveIcebergStorageHandler",
            ),
            (
                'CREATE TABLE test (c1 text) LOCATION \'s3://test\' TBLPROPERTIES (foo=1, "table_type"="iCeBeRg")',
                "org.apache.iceberg.mr.hive.HiveIcebergStorageHandler",
            ),
            ("UPDATE foobar SET 'table_type' = 'ICEBERG", None),
            (
                "CREATE TABLE test (c1 integer) LOCATION 's3://test' TBLPROPERTIES ( 'table_type' = 'DELTA' )",
                "io.delta.hive.DeltaStorageHandler",
            ),
            (
                'CREATE TABLE test (c1 text) LOCATION \'s3://test\' TBLPROPERTIES (foo=1, "table_type"="delTa")',
                "io.delta.hive.DeltaStorageHandler",
            ),
            ("UPDATE foobar SET 'table_type' = 'DELTA", None),
        ],
    )
    def test_inject_stored_by_for_external_table(self, query, storage_handler):
        modified_query = rewrite_external_storage(query)
        if storage_handler:
            # if a storage handler is expected for the query, make sure the STORED BY is inserted
            assert f"STORED BY '{storage_handler}'" in modified_query
        else:
            # if there is no storage handler, make sure the query is unmodified
            assert modified_query == query

    @pytest.mark.parametrize(
        "query, expected_result",
        [
            # classic example -> remove partitioned by, add storage handler
            (
                """
                CREATE TABLE IF NOT EXISTS table (`message_id` string, `subject` string, `countries` array<string>, `tenant_id` bigint, `dt` date)
                PARTITIONED BY (`tenant_id`, `dt`)
                LOCATION 's3://bucket/iceberg_table/'
                TBLPROPERTIES ( 'table_type' = 'ICEBERG' )
                """,
                """
                CREATE TABLE IF NOT EXISTS table (`message_id` string, `subject` string, `countries` array<string>, `tenant_id` bigint, `dt` date)
                STORED BY 'org.apache.iceberg.mr.hive.HiveIcebergStorageHandler' LOCATION 's3://bucket/iceberg_table/'
                TBLPROPERTIES ( 'table_type' = 'ICEBERG' )
                """,
            ),
            # partitioned iceberg query with additional table properties
            (
                """
                CREATE TABLE IF NOT EXISTS testdb.testtable(id bigint,test string,data_product_id string)
                PARTITIONED BY (data_product_id)
                LOCATION 's3://test-athena-random-123/data_table'
                TBLPROPERTIES ( 'table_type' ='ICEBERG', 'format'='parquet')
                """,
                """
                CREATE TABLE IF NOT EXISTS testdb.testtable(id bigint,test string,data_product_id string)
                STORED BY 'org.apache.iceberg.mr.hive.HiveIcebergStorageHandler' LOCATION 's3://test-athena-random-123/data_table'
                TBLPROPERTIES ( 'table_type' ='ICEBERG', 'format'='parquet')
                """,
            ),
            # no partitioned by -> storage handler is added
            (
                """
                CREATE TABLE IF NOT EXISTS table (`message_id` string, `subject` string, `countries` array<string>, `tenant_id` bigint, `dt` date)
                LOCATION 's3://bucket/iceberg_table/'
                TBLPROPERTIES ( 'table_type' = 'ICEBERG' )
                """,
                """
                CREATE TABLE IF NOT EXISTS table (`message_id` string, `subject` string, `countries` array<string>, `tenant_id` bigint, `dt` date)
                STORED BY 'org.apache.iceberg.mr.hive.HiveIcebergStorageHandler' LOCATION 's3://bucket/iceberg_table/'
                TBLPROPERTIES ( 'table_type' = 'ICEBERG' )
                """,
            ),
            # not an iceberg table -> no rewrite
            (
                """
                CREATE TABLE IF NOT EXISTS table (`message_id` string) PARTITIONED BY (`tenant_id` string) LOCATION 's3://bucket/iceberg_table/'
                """,
                None,
            ),
        ],
    )
    def test_remove_partition_by_for_partitioned_iceberg(self, query, expected_result):
        # if the parameter does not define an expected result, we want to check that the query is _not_ modified
        if not expected_result:
            expected_result = query
        assert _canonicalize_query(rewrite_external_storage(query)) == _canonicalize_query(
            expected_result
        )
