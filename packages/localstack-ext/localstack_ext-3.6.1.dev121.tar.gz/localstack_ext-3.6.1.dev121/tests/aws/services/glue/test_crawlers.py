import io
import itertools
import json
import logging

import pytest
import redshift_connector
from botocore.exceptions import ClientError
from localstack.aws.connect import ClientFactory, ServiceLevelClientFactory
from localstack.pro.core.services.athena import query_utils
from localstack.pro.core.services.athena.query_utils import canonicalize_db_name
from localstack.pro.core.utils.aws.aws_utils import run_athena_queries
from localstack.pro.core.utils.bigdata.bigdata_utils import execute_hive_query
from localstack.testing.aws.util import is_aws_cloud
from localstack.testing.config import TEST_AWS_ACCOUNT_ID, TEST_AWS_REGION_NAME
from localstack.testing.pytest import markers
from localstack.utils.aws import resources
from localstack.utils.bootstrap import is_api_enabled
from localstack.utils.strings import short_uid, to_bytes
from localstack.utils.sync import retry

from tests.aws.services.glue.conftest import skip_bigdata_in_ci

LOG = logging.getLogger(__name__)


@skip_bigdata_in_ci
class TestGlueCrawlerNonDefaultRegion:
    @pytest.fixture(autouse=True)
    def aws_client(self, aws_client_factory: ClientFactory) -> ServiceLevelClientFactory:
        """This fixture "overwrites" the default aws_client fixture and just uses a different region."""
        return aws_client_factory(
            region_name="eu-west-2" if TEST_AWS_REGION_NAME == "us-east-1" else TEST_AWS_REGION_NAME
        )

    @pytest.fixture
    def account_id(self, aws_client):
        """
        This fixture "overwrites" the default account_id to fix scope issues with the overwritten aws_client fixture,
        because account_id (session scoped) -> overwritten aws_client (function scoped) would not be allowed.
        """
        if is_aws_cloud() or is_api_enabled("sts"):
            return aws_client.sts.get_caller_identity()["Account"]
        else:
            return TEST_AWS_ACCOUNT_ID

    @pytest.fixture
    def region_name(self, aws_client):
        """
        This fixture "overwrites" the default region_name to fix scope issues with the overwritten aws_client fixture,
        because region_name (session scoped) -> overwritten region_name (function scoped) would not be allowed.
        And it also changes the region to a non-default one for all requesting tests.
        """
        if is_aws_cloud() or is_api_enabled("sts"):
            return aws_client.sts.meta.region_name
        else:
            return "eu-west-2" if TEST_AWS_REGION_NAME == "us-east-1" else TEST_AWS_REGION_NAME

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(
        [
            "$.select.ResultSet.ResultSetMetadata.ColumnInfo",
            "$.select.UpdateCount",
        ]
    )
    def test_crawler_non_default_region(
        self,
        snapshot,
        aws_client,
        s3_create_bucket,
        glue_create_database,
        create_role_with_policy_for_principal,
        glue_create_crawler,
    ):
        s3_bucket_name = s3_create_bucket()
        glue_table_name = canonicalize_db_name(s3_bucket_name)

        # create a database in Glue
        glue_database_name = glue_create_database()["Name"]

        csv_file = """
        id, name
        1, test 1
        2, test 2
        """.strip()

        # put data to S3
        aws_client.s3.put_object(
            Body=to_bytes(csv_file), Bucket=s3_bucket_name, Key="foo=123/test.csv"
        )

        # create IAM role
        role_name, role_arn = create_role_with_policy_for_principal(
            principal={"Service": "glue.amazonaws.com"}, resource="*", effect="Allow", actions=["*"]
        )
        aws_client.iam.attach_role_policy(
            RoleName=role_name, PolicyArn="arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole"
        )

        def _create_crawler():
            return glue_create_crawler(
                DatabaseName=glue_database_name,
                Role=role_arn,
                Targets={"S3Targets": [{"Path": f"s3://{s3_bucket_name}"}]},
            )

        # create crawler in a specific region (using retries, as IAM role creation may take some time)
        crawler_name = retry(_create_crawler, retries=30, sleep=1)

        snapshot.add_transformers_list(
            [
                snapshot.transform.key_value("DatabaseName", reference_replacement=True),
                snapshot.transform.key_value("Role", reference_replacement=True),
                snapshot.transform.key_value("CatalogId", reference_replacement=True),
                snapshot.transform.regex(s3_bucket_name, "<bucket-name>"),
                snapshot.transform.regex(crawler_name, "<crawler-name>"),
                snapshot.transform.regex(glue_database_name, "<database-name>"),
                snapshot.transform.regex(glue_table_name, "<table-name>"),
            ]
        )

        # retrieve the crawler info and snapshot-match it
        crawler = aws_client.glue.get_crawler(Name=crawler_name)
        snapshot.match("crawler", crawler)

        # start the crawler
        aws_client.glue.start_crawler(Name=crawler_name)

        def _check_crawler_finished():
            result = aws_client.glue.get_crawler(Name=crawler_name)["Crawler"]
            assert result["State"] == "READY"

        retry(_check_crawler_finished, retries=120, sleep=2)

        # retrieve the crawled database and tables
        database = aws_client.glue.get_database(Name=glue_database_name)
        snapshot.match("database", database)
        tables = aws_client.glue.get_tables(DatabaseName=glue_database_name)
        snapshot.match("tables", tables)

        # verify the query result on the table using athena
        query = f"SELECT * FROM {glue_table_name}"
        query_execution_context = {"Database": glue_database_name}
        result = run_athena_queries(
            query,
            QueryExecutionContext=query_execution_context,
            athena_client=aws_client.athena,
            s3_client=aws_client.s3,
        )
        snapshot.match("select", result)


@skip_bigdata_in_ci
class TestGlueCrawlers:
    @pytest.mark.parametrize(
        ("csv_content", "creates_table"),
        (("1, 2, 3, 4\n5, 6, 7, 8", True), ("1, 2, 3, 4", False), ("", False)),
    )
    @markers.aws.unknown
    def test_crawler_s3(self, csv_content, creates_table, aws_client):
        """
        Tests the basic CSV parsing and partitioning with Glue Crawlers.
        - CSV content with more than one line should create the table and partitions.
        - CSV content with one line (and less) should not create the table or partitions.
        """
        # create bucket
        bucket_name = f"b-{short_uid()}"
        resources.create_s3_bucket(bucket_name, s3_client=aws_client.s3)
        table_name = "table-123"
        canonical_table_name = canonicalize_db_name(table_name)
        s3_path = f"s3://{bucket_name}/{table_name}"
        # create the CSV files
        for month in ["Jan", "Feb"]:
            for day in ["1", "2"]:
                path_in_bucket = f"{table_name}/year=2021/month={month}/day={day}/file.csv"
                aws_client.s3.upload_fileobj(
                    io.BytesIO(to_bytes(csv_content)),
                    bucket_name,
                    path_in_bucket,
                )

        # get the list of crawler runs - should initially fail (AWS validated)
        crawler_name = f"c-{short_uid()}"
        with pytest.raises(ClientError) as exc:
            aws_client.glue.list_crawls(CrawlerName=crawler_name)
        assert exc.value.response["Error"]["Code"] == "EntityNotFoundException"
        assert (
            exc.value.response["Error"]["Message"]
            == f"Crawler entry with name {crawler_name} does not exist"
        )

        # create and start crawler
        database_name = f"db-{short_uid()}"
        aws_client.glue.create_database(DatabaseInput={"Name": database_name})
        targets = {"S3Targets": [{"Path": s3_path}]}
        result = aws_client.glue.create_crawler(
            Name=crawler_name, DatabaseName=database_name, Role="r1", Targets=targets
        )
        assert result["ResponseMetadata"]["HTTPStatusCode"] == 200
        result = aws_client.glue.start_crawler(Name=crawler_name)
        assert result["ResponseMetadata"]["HTTPStatusCode"] == 200

        # wait until crawler has finished
        def _check(*_):
            crawler = aws_client.glue.get_crawler(Name=crawler_name)["Crawler"]
            assert crawler["State"] == "READY"

        # Pulling the bigdata image can take quite some time
        retry(_check, retries=300, sleep=2)

        # get the list of crawler runs
        result = aws_client.glue.list_crawls(CrawlerName=crawler_name)
        crawler_runs = result.get("Crawls")
        assert crawler_runs
        assert crawler_runs[0]["State"] == "COMPLETED"
        assert crawler_runs[0]["StartTime"]
        assert crawler_runs[0]["EndTime"]

        # assert that tables have been created
        tables = aws_client.glue.get_tables(DatabaseName=database_name)["TableList"]
        if not creates_table:
            assert len(tables) == 0
        else:
            assert len(tables) == 1
            assert tables[0]["Name"] == canonical_table_name
            assert tables[0]["DatabaseName"] == database_name

            # assert that the partitions have been detected
            partitions = aws_client.glue.get_partitions(
                DatabaseName=database_name, TableName=canonical_table_name
            )["Partitions"]
            partitions = [p["Values"] for p in partitions]
            assert len(partitions) == 4

    @pytest.mark.parametrize(
        "file_format",
        ["json", "csv", "parquet-snappy", "parquet-gzip", "parquet-none"],
    )
    @markers.aws.unknown
    def test_crawler_s3_athena_integration(
        self, monkeypatch, file_format, glue_create_database, aws_client
    ):
        import pyarrow
        from pyarrow import parquet

        # define resource names
        bucket_name = f"b-{short_uid()}"
        table_name = "table-123"
        canonical_table_name = canonicalize_db_name(table_name)

        # create bucket
        resources.create_s3_bucket(bucket_name, s3_client=aws_client.s3)
        # create test files in S3
        perms = list(itertools.permutations(["1", "2", "3"]))
        s3_path = f"s3://{bucket_name}/{table_name}"
        for perm in perms:
            # Make sure to use special characters in a column name (like $, %, _, or &)
            if file_format == "csv":
                content = "col1,col2,col3, col4,0col5&%_$,timestamp\nv1.1',v1.2\\\",v1.3\\\\',123,,1646172627000000\nv2.1,v2.2,v2.3,45.6,,1652780743000000"
            elif file_format.startswith("parquet-"):
                compression = file_format.split("-")[1]
                outstream = io.BytesIO()
                names = ["col1", "col2", "col3", "col4", "0col5&%_$", "timestamp"]
                arrays = [
                    ["v1.1'", "v2.1"],
                    ['v1.2"', "v2.2"],
                    [r"v1.3\'", "v2.3"],
                    [123, 45.6],
                    ["", ""],
                    [1646172627000000, 1652780743000000],
                ]
                table = pyarrow.Table.from_arrays(arrays, names=names)
                parquet.write_table(table, outstream, use_dictionary=False, compression=compression)
                content = outstream.getvalue()
            else:
                entries = [
                    {
                        "col1": "v1.1'",
                        "col2": 'v1.2"',
                        "col3": r"v1.3\'",
                        "col4": 123,
                        "0col5&%_$": "",
                        "timestamp": 1646172627000000,
                    },
                    {
                        "col1": "v2.1",
                        "col2": "v2.2",
                        "col3": "v2.3",
                        "col4": 45.6,
                        "0col5&%_$": "",
                        "timestamp": 1652780743000000,
                    },
                ]
                content = "\n".join(json.dumps(entry) for entry in entries)
            aws_client.s3.upload_fileobj(
                io.BytesIO(to_bytes(content)),
                bucket_name,
                f"{table_name}/a={perm[0]}/b={perm[1]}/c={perm[2]}/file.{file_format}",
            )

        # remove the compression type from the file format
        file_format = file_format.split("-")[0]

        # create and start crawler
        database_name = glue_create_database()["Name"]
        canonical_db_name = canonicalize_db_name(database_name)
        crawler_name = f"c-{short_uid()}"
        targets = {"S3Targets": [{"Path": s3_path}]}
        result = aws_client.glue.create_crawler(
            Name=crawler_name, DatabaseName=database_name, Role="r1", Targets=targets
        )
        assert result["ResponseMetadata"]["HTTPStatusCode"] == 200
        result = aws_client.glue.start_crawler(Name=crawler_name)
        assert result["ResponseMetadata"]["HTTPStatusCode"] == 200

        # wait until crawler has finished
        def _check(*_):
            crawler = aws_client.glue.get_crawler(Name=crawler_name)["Crawler"]
            assert crawler["State"] == "READY"

        # Pulling the bigdata image can take quite some time
        retry(_check, retries=300, sleep=2)

        # assert that tables have been created
        tables = aws_client.glue.get_tables(DatabaseName=database_name)["TableList"]
        assert len(tables) == 1
        assert tables[0]["Name"] == canonicalize_db_name(table_name)
        assert tables[0]["DatabaseName"] == database_name
        assert tables[0]["Parameters"]["classification"] == file_format
        expected = [{"Name": col, "Type": "string"} for col in ["col1", "col2", "col3"]] + [
            {"Name": "col4", "Type": "double"},
            {"Name": "0col5&%_$", "Type": "string"},
            {"Name": "timestamp", "Type": "bigint"},
        ]
        col_names = ["col1", "col2", "col3", "col4", "0col5&%_$", "timestamp"]
        storage_columns = tables[0]["StorageDescriptor"]["Columns"]

        if file_format == "parquet" and storage_columns[-1]["Name"] == "col4":
            # note: binary type not properly mapped in `parquet` library yet (i.e., last column will be missing)
            expected = expected[:-1]
            col_names = col_names[:-1]
        assert storage_columns == expected
        assert tables[0]["PartitionKeys"] == [
            {"Name": part, "Type": "string"} for part in ["a", "b", "c"]
        ]

        # assert that data is available in Athena
        result = query_utils.execute_query(f"SHOW TABLES FROM {canonical_db_name}")
        assert len(result["rows"]) == 1
        assert result["rows"][0] == (canonical_table_name,)
        cols_str = ", ".join([f'"{col}"' for col in col_names])
        result = query_utils.execute_query(
            f"SELECT {cols_str} FROM {canonical_db_name}.{canonical_table_name}"
        )
        assert len(result["columns"]) == len(col_names)
        assert [col[0].split(".")[-1] for col in result["columns"]] == col_names
        assert len(result["rows"]) == 12
        line1 = ["v1.1'", 'v1.2"', "v1.3\\'", 123, "", 1646172627000000]
        line2 = ["v2.1", "v2.2", "v2.3", 45.6, "", 1652780743000000]
        assert line1[: len(col_names)] in result["rows"]
        assert line2[: len(col_names)] in result["rows"]

        # check that the partitions are created
        result = query_utils.execute_query(
            f"show partitions {canonical_db_name}.{canonical_table_name}"
        )
        assert result and "rows" in result and "columns" in result
        assert result["rows"] == [
            ("a=1/b=2/c=3",),
            ("a=1/b=3/c=2",),
            ("a=2/b=1/c=3",),
            ("a=2/b=3/c=1",),
            ("a=3/b=1/c=2",),
            ("a=3/b=2/c=1",),
        ]
        assert result["columns"] == [("partition", "STRING_TYPE")]

        # assert that partitions have been created
        partitions = aws_client.glue.get_partitions(
            DatabaseName=database_name, TableName=canonical_table_name
        )["Partitions"]
        partitions = [p["Values"] for p in partitions]
        assert len(perms) == len(partitions)
        for perm in perms:
            assert list(perm) in partitions

    @markers.aws.unknown
    def test_crawler_jdbc_redshift(
        self,
        glue_create_database,
        glue_create_crawler,
        glue_create_connection,
        redshift_create_cluster,
        aws_client,
    ):
        # create Redshift cluster
        user = "test1"
        password = "test2"
        redshift_database = "db1"
        cluster_id = short_uid()
        result = redshift_create_cluster(
            DBName=redshift_database,
            NodeType="nt1",
            ClusterIdentifier=cluster_id,
            MasterUsername=user,
            MasterUserPassword=password,
        )
        cluster = result["Cluster"]
        address = cluster["Endpoint"]["Address"]
        port = cluster["Endpoint"]["Port"]

        # connect to Redshift cluster
        conn = redshift_connector.connect(
            database=redshift_database,
            host="localhost",
            port=port,
            user=user,
            password=password,
            ssl=False,
        )

        # create a table
        table_name = "sales"
        create_query = (
            f"create table {table_name}("
            "salesid integer not null, "
            "listid integer not null, "
            "sellerid integer not null, "
            "buyerid integer not null, "
            "eventid integer not null, "
            "dateid smallint not null, "
            "qtysold smallint not null, "
            "pricepaid decimal(8,2), "
            "commission decimal(8,2), "
            "saletime timestamp)"
        )
        with conn:
            conn.autocommit = True
            with conn.cursor() as cursor:
                cursor.execute(create_query)

            # create a second table
            create_query_2 = (
                "create table users("
                "userid integer not null,"
                "username char(8),"
                "firstname varchar(30),"
                "lastname varchar(30),"
                "city varchar(30),"
                "state char(2),"
                "email varchar(100),"
                "phone char(14),"
                "likesports boolean,"
                "liketheatre boolean,"
                "likeconcerts boolean,"
                "likejazz boolean,"
                "likeclassical boolean,"
                "likeopera boolean,"
                "likerock boolean,"
                "likevegas boolean,"
                "likebroadway boolean,"
                "likemusicals boolean)"
            )
            with conn.cursor() as cursor:
                cursor.execute(create_query_2)

        # create a database in Glue
        glue_database_name = glue_create_database()["Name"]

        # create a JDBC connection
        connection_name = glue_create_connection(
            ConnectionInput={
                "ConnectionType": "JDBC",
                "ConnectionProperties": {
                    "USERNAME": user,
                    "PASSWORD": password,
                    "JDBC_CONNECTION_URL": f"jdbc:redshift://{address}:{port}/{redshift_database}",
                },
            }
        )["Name"]

        # create a crawler
        crawler_name = glue_create_crawler(
            DatabaseName=glue_database_name,
            Role="r1",
            Targets={
                "JdbcTargets": [
                    {"ConnectionName": connection_name, "Path": f"{redshift_database}/%/sales"}
                ]
            },
        )

        # start the crawler
        result = aws_client.glue.start_crawler(Name=crawler_name)
        assert result["ResponseMetadata"]["HTTPStatusCode"] == 200

        # wait until crawler has finished
        def _check(*_):
            crawler = aws_client.glue.get_crawler(Name=crawler_name)["Crawler"]
            assert crawler["State"] == "READY"

        # pulling the bigdata image can take quite some time
        retry(_check, retries=300, sleep=2)

        databases = aws_client.glue.get_databases().get("DatabaseList", [])
        assert len(databases) > 0
        database = aws_client.glue.get_database(Name=glue_database_name)["Database"]
        assert database.get("Name") == glue_database_name
        glue_table_name = f"{redshift_database}_public_{table_name}"
        table = aws_client.glue.get_table(DatabaseName=glue_database_name, Name=glue_table_name)[
            "Table"
        ]
        assert table.get("Name") == glue_table_name
        assert table.get("DatabaseName") == glue_database_name
        assert "StorageDescriptor" in table
        assert "Columns" in table["StorageDescriptor"]
        columns = table["StorageDescriptor"]["Columns"]
        expected_columns = [
            {"Name": "listid", "Type": "int"},
            {"Name": "saletime", "Type": "timestamp"},
            {"Name": "eventid", "Type": "int"},
            {"Name": "salesid", "Type": "int"},
            {"Name": "sellerid", "Type": "int"},
            {"Name": "dateid", "Type": "smallint"},
            {"Name": "commission", "Type": "decimal(8,2)"},
            {"Name": "qtysold", "Type": "smallint"},
            {"Name": "buyerid", "Type": "int"},
            {"Name": "pricepaid", "Type": "decimal(8,2)"},
        ]
        assert len(columns) == len(expected_columns) and all(
            column in columns for column in expected_columns
        )

        def _check_query():
            # Try querying the created table from Hive.
            # TODO: in the next iteration, we should query the table from Athena, potentially
            # with a fallback from Trino to Hive; Currently, we're receiving the error
            # "outputFormat should not be accessed from a null StorageFormat"
            # because Trino doesn't seem to be able to query tables created in
            # Hive via the 'STORED AS ...' JDBC connector.
            # see https://github.com/prestodb/presto/issues/6972
            db_name = canonicalize_db_name(glue_database_name)
            canonical_table_name = canonicalize_db_name(glue_table_name)
            result = query_utils.execute_query(f"SHOW TABLES FROM {db_name}")
            assert len(result["rows"]) == 1
            assert result["rows"][0] == (canonical_table_name,)
            query = f"SELECT * FROM {db_name}.{canonical_table_name}"
            result = execute_hive_query(query, database=db_name)
            assert result
            assert result.get("columns")

        retry(_check_query, sleep=1, retries=20)

    @markers.aws.unknown
    def test_crawler_jdbc_redshift_patterns(
        self,
        glue_create_database,
        glue_create_crawler,
        glue_create_connection,
        redshift_create_cluster,
        aws_client,
    ):
        # create Redshift cluster
        user = "test1"
        password = "test2"
        redshift_database = "db1"
        cluster_id = short_uid()
        result = redshift_create_cluster(
            DBName=redshift_database,
            NodeType="nt1",
            ClusterIdentifier=cluster_id,
            MasterUsername=user,
            MasterUserPassword=password,
        )
        cluster = result["Cluster"]
        address = cluster["Endpoint"]["Address"]
        port = cluster["Endpoint"]["Port"]

        # connect to Redshift cluster
        conn = redshift_connector.connect(
            database=redshift_database,
            host="localhost",
            port=port,
            user=user,
            password=password,
            ssl=False,
        )

        with conn:
            conn.autocommit = True
            with conn.cursor() as cursor:
                cursor.execute(
                    "create table user_metrics_by_hour("
                    "inserttime timestamp not null, "
                    "dateid smallint not null, "
                    "registrations smallint not null)"
                )

            with conn.cursor() as cursor:
                cursor.execute(
                    "create table sales_metrics_by_hour("
                    "inserttime timestamp not null, "
                    "dateid smallint not null, "
                    "qtysold smallint not null)"
                )

            with conn.cursor() as cursor:
                cursor.execute("create table users(userid integer not null, username char(8))")

        # create a database in Glue
        glue_database_name = glue_create_database()["Name"]

        # create a JDBC connection
        connection_name = glue_create_connection(
            ConnectionInput={
                "ConnectionType": "JDBC",
                "ConnectionProperties": {
                    "USERNAME": user,
                    "PASSWORD": password,
                    "JDBC_CONNECTION_URL": f"jdbc:redshift://{address}:{port}/{redshift_database}",
                },
            }
        )["Name"]

        # create a crawler
        crawler_name = glue_create_crawler(
            DatabaseName=glue_database_name,
            Role="r1",
            Targets={
                "JdbcTargets": [
                    {
                        "ConnectionName": connection_name,
                        "Path": f"{redshift_database}/%/%_metrics_by_hour",
                    }
                ]
            },
        )

        # start the crawler
        result = aws_client.glue.start_crawler(Name=crawler_name)
        assert result["ResponseMetadata"]["HTTPStatusCode"] == 200

        # wait until crawler has finished
        def _check(*_):
            crawler = aws_client.glue.get_crawler(Name=crawler_name)["Crawler"]
            assert crawler["State"] == "READY"

        # pulling the bigdata image can take quite some time
        retry(_check, retries=300, sleep=2)

        databases = aws_client.glue.get_databases().get("DatabaseList", [])
        assert len(databases) > 0
        database = aws_client.glue.get_database(Name=glue_database_name)["Database"]
        assert database.get("Name") == glue_database_name
        tables = aws_client.glue.get_tables(DatabaseName=glue_database_name)["TableList"]
        table_names = [table["Name"] for table in tables]
        assert f"{redshift_database}_public_user_metrics_by_hour" in table_names
        assert f"{redshift_database}_public_sales_metrics_by_hour" in table_names
        assert f"{redshift_database}_public_users" not in table_names

    @markers.aws.validated
    def test_crawler_table_prefix(
        self,
        glue_create_database,
        glue_create_crawler,
        s3_bucket,
        create_role_with_policy_for_principal,
        aws_client,
    ):
        # create a database in Glue
        glue_database_name = glue_create_database()["Name"]

        csv_file = """
        id, name
        1, test 1
        2, test 2
        """.strip()

        # put data to S3
        aws_client.s3.put_object(Body=to_bytes(csv_file), Bucket=s3_bucket, Key="foo=123/test.csv")

        # create IAM role
        role_name, role_arn = create_role_with_policy_for_principal(
            principal={"Service": "glue.amazonaws.com"}, resource="*", effect="Allow", actions=["*"]
        )
        aws_client.iam.attach_role_policy(
            RoleName=role_name, PolicyArn="arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole"
        )

        def _create_crawler():
            return glue_create_crawler(
                DatabaseName=glue_database_name,
                TablePrefix=prefix,
                Role=role_arn,
                Targets={"S3Targets": [{"Path": f"s3://{s3_bucket}"}]},
            )

        # create crawler with table prefix (using retries, as IAM role creation may take some time)
        prefix = "prefix1"
        crawler_name = retry(_create_crawler, retries=30, sleep=1)
        aws_client.glue.start_crawler(Name=crawler_name)

        def _check_crawler_finished():
            result = aws_client.glue.get_crawler(Name=crawler_name)["Crawler"]
            assert result["State"] == "READY"

        retry(_check_crawler_finished, retries=120, sleep=2)

        # assert that table with prefix has been created
        tables = aws_client.glue.get_tables(DatabaseName=glue_database_name)["TableList"]
        table_name = canonicalize_db_name(f"{prefix}{s3_bucket}")
        matching = [tab for tab in tables if tab["Name"] == table_name]
        assert matching

    @markers.aws.unknown
    def test_crawler_multiple_targets(
        self, glue_create_database, glue_create_crawler, s3_bucket, aws_client
    ):
        # create a database in Glue
        glue_database_name = glue_create_database()["Name"]

        csv_file = """
        id, name
        1, test 1
        2, test 2
        """.strip()

        # put data to S3
        aws_client.s3.put_object(
            Body=to_bytes(csv_file), Bucket=s3_bucket, Key="path/foo=123/test.csv"
        )
        aws_client.s3.put_object(
            Body=to_bytes(csv_file), Bucket=s3_bucket, Key="path-2/foo=456/test.csv"
        )

        # create crawler with two S3 targets
        crawler_name = glue_create_crawler(
            DatabaseName=glue_database_name,
            Role="r1",
            Targets={
                "S3Targets": [
                    {"Path": f"s3://{s3_bucket}/path"},
                    {"Path": f"s3://{s3_bucket}/path-2/"},
                ]
            },
        )
        aws_client.glue.start_crawler(Name=crawler_name)

        def _check_crawler_finished():
            result = aws_client.glue.get_crawler(Name=crawler_name)["Crawler"]
            assert result["State"] == "READY"

        retry(_check_crawler_finished, retries=60, sleep=2)

        # assert that tables have been created
        tables = aws_client.glue.get_tables(DatabaseName=glue_database_name)["TableList"]
        matching = [tab for tab in tables if tab["Name"] in ["path", "path_2"]]
        assert len(matching) == 2
