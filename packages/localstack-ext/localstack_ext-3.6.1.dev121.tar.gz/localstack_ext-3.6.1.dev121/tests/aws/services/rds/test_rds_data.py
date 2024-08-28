import json
from typing import List, Optional, TypedDict

import aws_cdk as cdk
import aws_cdk.aws_ec2 as ec2
import aws_cdk.aws_rds as rds
import pytest
from localstack.pro.core import config as ext_config
from localstack.pro.core.aws.api.rds_data import SqlParameterSets, SqlParametersList
from localstack.pro.core.services.rds.db_utils import DEFAULT_MASTER_USERNAME
from localstack.testing.aws.util import is_aws_cloud
from localstack.testing.pytest import markers
from localstack.utils.strings import short_uid
from localstack.utils.sync import retry

from tests.aws.services.rds.test_rds import (
    DEFAULT_TEST_MASTER_PASSWORD,
    skip_if_postgres_unavailable,
)


class DataApiStatement(TypedDict):
    snapshot: str
    sql: Optional[str]
    mysql: Optional[str]
    postgres: Optional[str]
    parameters: Optional[SqlParametersList]
    parameter_sets: Optional[SqlParameterSets]


@pytest.fixture
def rds_execute_statement_helper(aws_client):
    rds_data = aws_client.rds_data

    def _setup(secret_arn, resource_arn, database, include_result_metadata=True, client=None):
        client = client or rds_data

        def _invoke(statement: DataApiStatement, engine: str, **kwargs):
            sql = statement.get(engine) or statement.get("sql")
            try:
                if statement.get("parameter_sets"):
                    return client.batch_execute_statement(
                        resourceArn=resource_arn,
                        secretArn=secret_arn,
                        database=database,
                        sql=sql,
                        parameterSets=statement["parameter_sets"],
                        **kwargs,
                    )
                else:
                    return client.execute_statement(
                        secretArn=secret_arn,
                        resourceArn=resource_arn,
                        sql=sql,
                        includeResultMetadata=include_result_metadata,
                        # AWS seems to require this, otherwise it will use the admin name by default (not the dbname from the secret, as one would expect...)
                        database=database,
                        parameters=statement.get("parameters") or [],
                        **kwargs,
                    )
            except Exception as e:
                return {"error": e}

        return _invoke

    yield _setup


@skip_if_postgres_unavailable
class TestAuroraPostgresCfn:
    @pytest.fixture(scope="class", autouse=True)
    def infrastructure(self, aws_client, infrastructure_setup):
        infra = infrastructure_setup(namespace="RdsDataPostgres")
        stack = cdk.Stack(infra.cdk_app, "AuroraPostgresStack")

        # The VPC to place the cluster in
        vpc = ec2.Vpc(stack, "AuroraVpc")
        engine = rds.DatabaseClusterEngine.aurora_postgres(
            version=rds.AuroraPostgresEngineVersion.VER_13_5
        )  # noqa

        parameter_group = rds.ParameterGroup(
            stack,
            "parameterGroup",
            engine=engine,
            parameters={
                "shared_preload_libraries": "auto_explain",
            },
        )

        # Create the serverless cluster, provide all values needed to customise the database.
        cluster = rds.ServerlessCluster(
            stack,
            "AuroraCluster",
            engine=engine,
            vpc=vpc,
            credentials=rds.Credentials.from_username(username="clusteradmin"),
            default_database_name="demos",
            parameter_group=parameter_group,
            enable_data_api=True,
            removal_policy=cdk.RemovalPolicy.DESTROY,
        )
        cdk.CfnOutput(stack, "ClusterId", value=cluster.cluster_identifier)
        cdk.CfnOutput(stack, "ClusterArn", value=cluster.cluster_arn)
        cdk.CfnOutput(stack, "SecretArn", value=cluster.secret.secret_arn)
        cdk.CfnOutput(stack, "DatabaseName", value="demos")

        with infra.provisioner() as prov:
            yield prov

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(
        paths=[
            "$..create-result.numberOfRecordsUpdated",  # TODO numberOfRecordsUpdated currently always 0
            "$..insert-result.numberOfRecordsUpdated",
        ]
    )
    def test_select_char(self, aws_client, infrastructure, snapshot):
        outputs = infrastructure.get_stack_outputs(stack_name="AuroraPostgresStack")
        cluster_arn = outputs["ClusterArn"]
        secret_arn = outputs["SecretArn"]
        db_name = outputs["DatabaseName"]

        create_result = aws_client.rds_data.execute_statement(
            secretArn=secret_arn,
            resourceArn=cluster_arn,
            sql="CREATE TABLE IF NOT EXISTS organisation(country_code CHAR(2) NOT NULL)",
            includeResultMetadata=True,
            # AWS seems to require this, otherwise it will use the admin name by default (not the dbname from the secret, as one would expect...)
            database=db_name,
        )

        snapshot.match("create-result", create_result)

        insert_result = aws_client.rds_data.execute_statement(
            secretArn=secret_arn,
            resourceArn=cluster_arn,
            sql="INSERT INTO organisation(country_code) VALUES ('FR');",
            includeResultMetadata=True,
            database=db_name,
        )

        snapshot.match("insert-result", insert_result)

        query_result = aws_client.rds_data.execute_statement(
            secretArn=secret_arn,
            resourceArn=cluster_arn,
            sql="SELECT country_code FROM organisation LIMIT 1",
            includeResultMetadata=True,
            database=db_name,
        )
        snapshot.match("query-result", query_result)


@skip_if_postgres_unavailable
@pytest.mark.parametrize(
    "engine, serverless_version", [("postgres", "v1"), ("postgres", "v2"), ("mysql", "v1")]
)
class TestAuroraMultiEngine:
    @pytest.fixture(scope="class", autouse=True)
    def infrastructure(self, aws_client, infrastructure_setup):
        infra = infrastructure_setup(namespace="RdsDataMultiEngine")
        stack = cdk.Stack(infra.cdk_app, "AuroraMultiEngineStack")

        # The VPC to place the cluster in
        vpc = ec2.Vpc(stack, "AuroraVpc")

        # Creating serverless_v1 Aurora for postgres
        v1_postgres_engine = rds.DatabaseClusterEngine.aurora_postgres(
            version=rds.AuroraPostgresEngineVersion.VER_11_21
        )
        v1_postgres_cluster = rds.ServerlessCluster(
            stack,
            "V1PostgresCluster",
            engine=v1_postgres_engine,
            vpc=vpc,
            credentials=rds.Credentials.from_username(username="clusteradmin"),
            default_database_name="demos",
            enable_data_api=True,
            removal_policy=cdk.RemovalPolicy.DESTROY,
        )

        # Creating serverless_v2 Aurora for postgres
        v2_postgres_engine = rds.DatabaseClusterEngine.aurora_postgres(
            version=rds.AuroraPostgresEngineVersion.VER_16_1
        )
        v2_postgres_cluster = rds.DatabaseCluster(
            stack,
            "V2PostgresCluster",
            engine=v2_postgres_engine,
            writer=rds.ClusterInstance.serverless_v2("writer"),
            vpc=vpc,
            serverless_v2_min_capacity=0.5,
            serverless_v2_max_capacity=1,
            credentials=rds.Credentials.from_username(username="clusteradmin"),
            default_database_name="demos",
            enable_data_api=True,
            removal_policy=cdk.RemovalPolicy.DESTROY,
        )

        # Creating serverless_v1 Aurora for mysql
        v1_mysql_engine = rds.DatabaseClusterEngine.aurora_mysql(
            version=rds.AuroraMysqlEngineVersion.VER_2_11_4
        )
        # Create the serverless cluster, provide all values needed to customise the database.
        v1_mysql_cluster = rds.ServerlessCluster(
            stack,
            "V1MysqlCluster",
            engine=v1_mysql_engine,
            vpc=vpc,
            credentials=rds.Credentials.from_username(username="clusteradmin"),
            default_database_name="demos",
            enable_data_api=True,
            removal_policy=cdk.RemovalPolicy.DESTROY,
        )

        cdk.CfnOutput(stack, "v1postgresClusterId", value=v1_postgres_cluster.cluster_identifier)
        cdk.CfnOutput(stack, "v1postgresClusterArn", value=v1_postgres_cluster.cluster_arn)
        cdk.CfnOutput(stack, "v1postgresSecretArn", value=v1_postgres_cluster.secret.secret_arn)
        cdk.CfnOutput(stack, "v2postgresClusterId", value=v2_postgres_cluster.cluster_identifier)
        cdk.CfnOutput(stack, "v2postgresClusterArn", value=v2_postgres_cluster.cluster_arn)
        cdk.CfnOutput(stack, "v2postgresSecretArn", value=v2_postgres_cluster.secret.secret_arn)
        cdk.CfnOutput(stack, "v1mysqlClusterId", value=v1_mysql_cluster.cluster_identifier)
        cdk.CfnOutput(stack, "v1mysqlClusterArn", value=v1_mysql_cluster.cluster_arn)
        cdk.CfnOutput(stack, "v1mysqlSecretArn", value=v1_mysql_cluster.secret.secret_arn)
        cdk.CfnOutput(stack, "DatabaseName", value="demos")

        with infra.provisioner() as prov:
            yield prov

    @pytest.fixture
    def infrastructure_output(self, infrastructure, engine, serverless_version):
        outputs = infrastructure.get_stack_outputs(stack_name="AuroraMultiEngineStack")
        cluster_arn = outputs[f"{serverless_version}{engine}ClusterArn"]
        secret_arn = outputs[f"{serverless_version}{engine}SecretArn"]
        db_name = outputs["DatabaseName"]
        # `columnMetadata` gets filled wrong if postgres uses capital letters in the table name
        # And vice-versa for mysql table. There will be a test capturing those differences, but for now
        # we can set a different table name to simplify snapshot testing
        common_table = "commontable" if engine == "postgres" else "commonTable"
        return cluster_arn, secret_arn, db_name, common_table

    @markers.aws.validated
    def test_batch_execute_statement_setup(
        self,
        aws_client,
        rds_execute_statement_helper,
        infrastructure_output,
        engine,
        snapshot,
    ):
        cluster_arn, secret_arn, db_name, common_table = infrastructure_output
        invoker = rds_execute_statement_helper(
            secret_arn=secret_arn, resource_arn=cluster_arn, database=db_name
        )

        statement = DataApiStatement(
            snapshot="create-table",
            mysql=f"CREATE TABLE IF NOT EXISTS {common_table} (foo int(10) NOT NULL, bar varchar(10))",
            postgres=f"CREATE TABLE IF NOT EXISTS {common_table}(foo INT NOT NULL, bar VARCHAR)",
        )

        def _wait_for_db_up(statement: DataApiStatement, engine: str, **kwargs):
            result = invoker(statement, engine, **kwargs)
            assert "error" not in result
            return result

        # Serverless instances can take a long time to cold start
        result = retry(_wait_for_db_up, retries=20, sleep=3, statement=statement, engine=engine)
        snapshot.match(statement["snapshot"], result)

    @markers.snapshot.skip_snapshot_verify(
        paths=[
            # AWS only puts the value of generated fields for postgres v1. We don't add in for any.
            # AWS id deprecating Serverless v1 For EOY 2024. At which point we can remove this `skip`
            "$..updateResults..generatedFields",
            # TODO numberOfRecordsUpdated currently always 0
            "$..numberOfRecordsUpdated",
            "$..columnMetadata..precision",
            # TODO We send the wrong type for mysql v1 only
            "$..columnMetadata..type",
        ]
    )
    @markers.aws.validated
    def test_batch_execute_statement_inserts(
        self,
        aws_client,
        infrastructure_output,
        rds_execute_statement_helper,
        engine,
        snapshot,
    ):
        cluster_arn, secret_arn, db_name, common_table = infrastructure_output

        invoker = rds_execute_statement_helper(
            secret_arn=secret_arn, resource_arn=cluster_arn, database=db_name
        )

        sql_statements = [
            DataApiStatement(
                snapshot="insert-items-1",
                sql=f"INSERT INTO {common_table} (foo) VALUES (:foo)",
                parameter_sets=[
                    [{"name": "foo", "value": {"longValue": 10}}],
                    [{"name": "foo", "value": {"longValue": 11}}],
                ],
            ),
            DataApiStatement(snapshot="select-items-1", sql=f"SELECT * FROM {common_table}"),
            DataApiStatement(
                snapshot="insert-items-2",
                mysql=f"INSERT INTO {common_table}(foo, bar) VALUES (:foo, :bar)",
                postgress=f"INSERT INTO {common_table} VALUES (:foo, :bar)",
                parameter_sets=[
                    [
                        {"name": "foo", "value": {"longValue": 12}},
                        {"name": "bar", "value": {"stringValue": "first"}},
                    ],
                    [
                        {"name": "foo", "value": {"longValue": 13}},
                        {"name": "bar", "value": {"stringValue": "second"}},
                    ],
                ],
            ),
            DataApiStatement(
                snapshot="select-item-first",
                sql=f"SELECT bar FROM {common_table} WHERE bar='first'",
            ),
            DataApiStatement(snapshot="select-items-2", sql=f"SELECT * FROM {common_table}"),
            DataApiStatement(
                snapshot="batch-delete-items",
                sql=f"DELETE FROM {common_table} WHERE foo=:foo OR bar=:bar",
                parameter_sets=[
                    [
                        {"name": "foo", "value": {"longValue": 10}},
                        {"name": "bar", "value": {"stringValue": ""}},
                    ],
                    [
                        {"name": "foo", "value": {"longValue": 11}},
                        {"name": "bar", "value": {"stringValue": "second"}},
                    ],
                    [
                        {"name": "foo", "value": {"longValue": 0}},
                        {"name": "bar", "value": {"stringValue": "first"}},
                    ],
                    [
                        {"name": "foo", "value": {"longValue": 99}},
                        {"name": "bar", "value": {"stringValue": "none"}},
                    ],
                ],
            ),
            DataApiStatement(snapshot="select-items-3", sql=f"SELECT * FROM {common_table}"),
        ]

        for statement in sql_statements:
            result = invoker(statement, engine)
            snapshot.match(statement["snapshot"], result)

    @markers.snapshot.skip_snapshot_verify(
        paths=[
            "$..columnMetadata..precision",  # All engine
            # TODO Postgres doesn't return an error message. mysql has a different wording on the bad request error
            "$..missing-in-second-insert.*",
            # TODO We have the wrong type for mysql v1 only
            "$..columnMetadata..type",
        ]
    )
    @markers.aws.validated
    def test_batch_execute_validate_atomicity(
        self,
        aws_client,
        infrastructure_output,
        rds_execute_statement_helper,
        engine,
        snapshot,
    ):
        cluster_arn, secret_arn, db_name, common_table = infrastructure_output

        invoker = rds_execute_statement_helper(
            secret_arn=secret_arn, resource_arn=cluster_arn, database=db_name
        )

        sql_statements: List[DataApiStatement] = [
            DataApiStatement(
                snapshot="missing-in-second-insert",
                postgres=f"INSERT INTO {common_table} (:foo, :bar)",
                mysql=f"INSERT INTO {common_table}(foo, bar) (:foo, :bar)",
                parameter_sets=[
                    [
                        {"name": "foo", "value": {"longValue": 12}},
                        {"name": "bar", "value": {"stringValue": "first"}},
                    ],
                    [{"name": "foo", "value": {"longValue": 13}}],
                ],
            ),
            DataApiStatement(snapshot="select-all-1", sql=f"SELECT * FROM {common_table}"),
            DataApiStatement(
                snapshot="wrong-type-in-second-insert",
                sql=f"INSERT INTO {common_table}(foo, bar) (:foo, :bar)",
                parameter_sets=[
                    [
                        {"name": "foo", "value": {"longValue": 12}},
                        {"name": "bar", "value": {"stringValue": "first"}},
                    ],
                    [
                        {"name": "foo", "value": {"longValue": "string"}},
                        {"name": "bar", "value": {"stringValue": "first"}},
                    ],
                ],
            ),
            DataApiStatement(snapshot="select-all-2", sql=f"SELECT * FROM {common_table}"),
            DataApiStatement(
                snapshot="extra-parameter-in-second-insert",
                postgres=f"INSERT INTO {common_table} (:foo)",
                mysql=f"INSERT INTO {common_table}(foo) (:foo)",
                parameter_sets=[
                    [
                        {"name": "foo", "value": {"longValue": 12}},
                    ],
                    [
                        {"name": "foo", "value": {"longValue": "string"}},
                        {"name": "bar", "value": {"stringValue": "first"}},
                    ],
                ],
            ),
            DataApiStatement(snapshot="select-all-3", sql=f"SELECT * FROM {common_table}"),
        ]

        for statement in sql_statements:
            result = invoker(statement, engine)
            snapshot.match(statement["snapshot"], result)

    @markers.snapshot.skip_snapshot_verify(paths=["$..delete-all.numberOfRecordsUpdated"])
    @markers.aws.validated
    def test_batch_execute_statement_drop(
        self,
        aws_client,
        infrastructure_output,
        rds_execute_statement_helper,
        engine,
        snapshot,
    ):
        cluster_arn, secret_arn, db_name, common_table = infrastructure_output

        invoker = rds_execute_statement_helper(
            secret_arn=secret_arn, resource_arn=cluster_arn, database=db_name
        )

        sql_statements: List[DataApiStatement] = [
            DataApiStatement(snapshot="delete-all", sql=f"DELETE FROM {common_table}"),
            DataApiStatement(snapshot="drop-table", sql=f"DROP TABLE {common_table}"),
        ]

        for statement in sql_statements:
            result = invoker(statement, engine)
            snapshot.match(statement["snapshot"], result)

    @markers.snapshot.skip_snapshot_verify(
        paths=[
            # TODO The current issue with this test is the column metadata gets filled wrong when
            # there is a capital letter in the table name
            "$..columnMetadata..nullable",
            "$..columnMetadata..precision",
            "$..columnMetadata..tableName",
            "$..numberOfRecordsUpdated",
        ]
    )
    @markers.aws.validated
    def test_column_metadata_for_postgres(
        self,
        aws_client,
        infrastructure_output,
        rds_execute_statement_helper,
        engine,
        snapshot,
    ):
        if engine != "postgres":
            return pytest.skip("Test only relevant for postgres engine")
        cluster_arn, secret_arn, db_name, common_table = infrastructure_output

        common_table = "postgresWithCaps"

        invoker = rds_execute_statement_helper(
            secret_arn=secret_arn, resource_arn=cluster_arn, database=db_name
        )

        sql_statements: List[DataApiStatement] = [
            DataApiStatement(
                snapshot="create-table",
                postgres=f"CREATE TABLE IF NOT EXISTS {common_table}(foo INT NOT NULL, bar VARCHAR)",
            ),
            DataApiStatement(
                snapshot="insert-items-1",
                postgres=f"INSERT INTO {common_table} (foo) VALUES (1)",
            ),
            DataApiStatement(snapshot="select-all", sql=f"SELECT * FROM {common_table}"),
            DataApiStatement(snapshot="drop-table", sql=f"DROP TABLE {common_table}"),
        ]

        for statement in sql_statements:
            result = invoker(statement=statement, engine=engine)
            snapshot.match(statement["snapshot"], result)

    @markers.snapshot.skip_snapshot_verify(
        paths=[
            # TODO The current issue with this test is the column metadata gets filled wrong when
            # there are no capital letter in the table name
            "$..columnMetadata..precision",
            "$..columnMetadata..type",
            "$..records..booleanValue",
            "$..records..longValue",
            "$..numberOfRecordsUpdated",
        ]
    )
    @markers.aws.validated
    def test_column_metadata_for_mysql(
        self,
        aws_client,
        infrastructure_output,
        rds_execute_statement_helper,
        engine,
        snapshot,
    ):
        if engine != "mysql":
            return pytest.skip("Test only relevant for mysql engine")
        cluster_arn, secret_arn, db_name, common_table = infrastructure_output

        common_table = "mysqlnocaps"

        invoker = rds_execute_statement_helper(
            secret_arn=secret_arn, resource_arn=cluster_arn, database=db_name
        )

        sql_statements: List[DataApiStatement] = [
            DataApiStatement(
                snapshot="create-table",
                mysql=f"CREATE TABLE IF NOT EXISTS {common_table}(foo int(10) NOT NULL, bar varchar(10))",
            ),
            DataApiStatement(
                snapshot="insert-items-1",
                mysql=f"INSERT INTO {common_table} (foo) VALUES (1)",
            ),
            DataApiStatement(snapshot="select-all", sql=f"SELECT * FROM {common_table}"),
            DataApiStatement(snapshot="drop-table", sql=f"DROP TABLE {common_table}"),
        ]

        for statement in sql_statements:
            result = invoker(statement=statement, engine=engine)
            snapshot.match(statement["snapshot"], result)


@skip_if_postgres_unavailable
class TestAuroraPostgres:
    # TODO refactor to make the test more readable,
    #  ideally add test cases to the TestAuroraPostgresCfn above

    @markers.aws.validated
    # this test needs manual setup of an aurora RDS postgres cluster, as it take quite long
    # it should not be runnable directly, but with a manual setup the test is running
    @markers.snapshot.skip_snapshot_verify(
        paths=[
            "$..columnMetadata[8].precision",
            "$..records[0].[14].stringValue",
            "$..records[0].[15].stringValue",
        ]
    )
    def test_data_api(self, rds_create_db_cluster, create_secret, snapshot, aws_client, cleanups):
        # https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/data-api.html
        # How to create an RDS Aurora Postgres cluster with Data API enabled from the AWS console:
        # See the PR for a better description:
        #
        # when creating the Cluster, you need to select the proper version of Aurora PostgreSQL from this list
        # https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/Concepts.Aurora_Fea_Regions_DB-eng.Feature.Data_API.html
        # Go to the RDS page on the AWS console, and select `DB clusters`, then `Create new database`.
        # First, select Aurora (PostgreSQL compatible), then select the version: for `us-east-1`, you should select
        # Aurora Postgres 11.16 (as of 30/5/2023)
        # You can then select `Dev/Test` template, for `Settings`, leave the DB cluster identifier as is, and you can
        # select `Auto generate a password` (selecting managed by SecretsManager seems to not be supported with Aurora
        # Serverless v1) or set one manually.
        # In `Instance Configuration`, `DB instance class`, select `Serverless`, then `Serverless v1` from the dropdown
        # `Capacity range`, you can leave at 2 ACU min and set 2 ACU max.
        # For `Connectivity`, here's where we enable the Data API. You can leave everything default for the VPC
        # In `Additional configuration` as the bottom, you can click the dropdown which will reveal
        # `Web Service Data API`, where you need to click to enable `Data API`
        # You can then follow the console by click `Next`, until the cluster is being created. On the top a banner will
        # appear, you can click it to get the database credentials. By default, the user will be `postgres` and the
        # auto generated password will appear. Save those credentials to store them in SecretsManager.
        # You can then click on the newly created database in the databases list to find the database ARN in the
        # `Configuration` tab. Save it to use it in this test.

        # In SecretsManager, click to create a new secret. In the form, select `Credentials for Amazon RDS database`
        # You can then paste the credentials previously saved, and select the newly created database at the bottom
        # of the form. Create the secrets, and go on its page then to retrieve its ARN.

        # Once the database status is green and `Created`, you can use those ARNs by commenting out the resource
        # creation and hardcode them to your created resources.

        # DO NOT FORGET TO MANUALLY DELETE YOUR RDS SERVERLESS CLUSTER after you're done validating your tests
        # you should also delete the Secret used to access the database in SecretsManager

        # create secret: if running in AWS, comment out the next 2 lines and hardcode the secret_arn variable
        secret_name = f"s-{short_uid()}"
        secret = create_secret(Name=secret_name, SecretString=DEFAULT_TEST_MASTER_PASSWORD)
        secret_arn = secret["ARN"]
        db_name = "test"
        # create DB cluster: if in AWS, comment the next lines and hardcode the cluster_arn
        cluster_id = f"rds-{short_uid()}"
        db_type = "aurora-postgresql"
        result = rds_create_db_cluster(
            DBClusterIdentifier=cluster_id,
            Engine=db_type,
            DatabaseName=db_name,
            EngineMode="serverless",
        )
        cluster_arn = result["DBClusterArn"]

        database_name = "foo123"

        # run SELECT - execute_sql is deprecated, only for backward compatibility
        # AWS does NOT accept queries against this endpoint anymore
        if not is_aws_cloud():
            result = aws_client.rds_data.execute_sql(
                awsSecretStoreArn=secret_arn,
                dbClusterOrInstanceArn=cluster_arn,
                sqlStatements="SELECT 123; SELECT 'abc'; SELECT 1.2",
            )["sqlStatementResults"]
            rec1 = result[0]["resultFrame"]
            rec2 = result[1]["resultFrame"]
            rec3 = result[2]["resultFrame"]
            assert rec1["records"] == [{"values": [{"bigIntValue": 123}]}]
            assert rec2["records"] == [{"values": [{"stringValue": "abc"}]}]
            assert rec3["records"] == [{"values": [{"stringValue": "1.2"}]}]

            # run SELECT
            # execute_statement only execute the first SQL statement
            result = aws_client.rds_data.execute_statement(
                resourceArn=cluster_arn,
                secretArn=secret_arn,
                sql="SELECT 123; SELECT 'abc'; SELECT 1.2",
                includeResultMetadata=True,
            )
            assert len(result["records"]) == 1
            assert result["records"] == [[{"longValue": 123}]]
            assert result["columnMetadata"][0]["isSigned"] is True
            assert result["columnMetadata"][0]["name"] == "?column?"
            assert result["columnMetadata"][0]["typeName"] == "int4"

        # run CREATE DATABASE
        result = aws_client.rds_data.execute_statement(
            secretArn=secret_arn,
            resourceArn=cluster_arn,
            sql=f"CREATE DATABASE {database_name};",
        )
        assert "records" not in result
        assert result["generatedFields"] == []
        cleanups.append(
            lambda: aws_client.rds_data.execute_statement(
                secretArn=secret_arn,
                resourceArn=cluster_arn,
                sql=f"DROP DATABASE {database_name};",
            )
        )
        p = ("name", "col_type", "value_type", "value", "typeHint")
        type_values = [
            ("id", "serial", "longValue", None, None),
            ("int_test", "int", "longValue", 123, None),
            ("small", "smallint", "longValue", 123, None),
            ("big", "bigint", "longValue", 123, None),
            ("bool", "bool", "booleanValue", True, None),
            ("realtest", "real", "doubleValue", 1.1, None),
            ("double", "double precision", "doubleValue", 1.1, None),
            ("numeric", "numeric", "stringValue", "1.2", "DECIMAL"),
            ("varchar_test", "varchar", "stringValue", "test", None),
            ("text_test", "text", "stringValue", "test", None),
            ("uuid_test", "uuid", "stringValue", "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11", "UUID"),
            ("json_test", "json", "stringValue", json.dumps({"test": "t123"}), "JSON"),
            ("jsonb_test", "jsonb", "stringValue", json.dumps({"test": "t123"}), "JSON"),
            ("dt", "date", "stringValue", "1999-01-08", "DATE"),
            ("ts", "timestamp", "stringValue", "2022-10-02 10:10:10.101000", "TIMESTAMP"),
            ("tstz", "timestamptz", "stringValue", "2022-10-02 10:10:10.101000", "TIMESTAMP"),
            ("t", "time", "stringValue", "04:05:06", "TIME"),
            ("ttz", "timetz", "stringValue", "04:05:06", "TIME"),
        ]
        table_name = "foo"
        type_tests = [dict(zip(p, type_value)) for type_value in type_values]

        table_columns = ", ".join(
            [f"{type_test['name']} {type_test['col_type']}" for type_test in type_tests]
        )

        result = aws_client.rds_data.execute_statement(
            secretArn=secret_arn,
            resourceArn=cluster_arn,
            sql=f"CREATE TABLE {table_name} ({table_columns})",
            database=database_name,
        )
        assert "records" not in result
        assert result["generatedFields"] == []

        insert_types_test = type_tests[1:]
        columns_names = ", ".join([type_test["name"] for type_test in insert_types_test])
        param_names = ", ".join([f":{type_test['name']}" for type_test in insert_types_test])
        parameters = []
        for type_test in insert_types_test:
            param = {
                "name": type_test["name"],
                "value": {type_test["value_type"]: type_test["value"]},
            }
            if type_test["typeHint"]:
                param["typeHint"] = type_test["typeHint"]

            parameters.append(param)

        result = aws_client.rds_data.execute_statement(
            secretArn=secret_arn,
            resourceArn=cluster_arn,
            database=database_name,
            sql=f"INSERT INTO {table_name} ({columns_names}) VALUES ({param_names})",
            parameters=parameters,
        )
        assert result["ResponseMetadata"]["HTTPStatusCode"] == 200
        assert "records" not in result
        assert result["generatedFields"] == []

        result = aws_client.rds_data.execute_statement(
            secretArn=secret_arn,
            resourceArn=cluster_arn,
            database=database_name,
            sql="SELECT * FROM foo LIMIT 1",
            includeResultMetadata=True,
        )

        assert len(result["records"]) > 0

        snapshot.match("result-query", result)

        # try some query which call multiple columns for one alias: COALESCE and CASE
        column_0 = type_values[0][0]
        column_1 = type_values[1][0]
        query = f"SELECT {column_0}, {column_1}, COALESCE({column_0}, {column_1}, 1) as aliastest FROM foo"
        result = aws_client.rds_data.execute_statement(
            secretArn=secret_arn,
            resourceArn=cluster_arn,
            database=database_name,
            sql=query,
            includeResultMetadata=True,
        )
        assert len(result["records"]) > 0
        snapshot.match("result-query-coalesce", result)

        query_case = f"SELECT CASE WHEN {column_0} IS NOT NULL THEN 'Book' WHEN {column_1} IS NOT NULL THEN 'Card' ELSE 'User' END as aliastest FROM foo"
        result = aws_client.rds_data.execute_statement(
            secretArn=secret_arn,
            resourceArn=cluster_arn,
            database=database_name,
            sql=query_case,
            includeResultMetadata=True,
        )
        assert len(result["records"]) > 0
        snapshot.match("result-query-case", result)

        with pytest.raises(Exception) as exc:
            aws_client.rds_data.execute_statement(
                secretArn=secret_arn,
                resourceArn=cluster_arn,
                sql="CREATE TABLE foo (id int, s text)",
                database="invalid",
            )
        exc.match("does not exist")

        # run CREATE TABLE in a transaction
        result = aws_client.rds_data.begin_transaction(
            resourceArn=cluster_arn,
            secretArn=secret_arn,
            database=database_name,
        )
        txid = result["transactionId"]
        result = aws_client.rds_data.execute_statement(
            secretArn=secret_arn,
            resourceArn=cluster_arn,
            sql="CREATE TABLE foo2 (id int, s text)",
            transactionId=txid,
            database=database_name,
        )
        assert "records" not in result
        # TODO: try to commit a non-existent txid
        result = aws_client.rds_data.commit_transaction(
            resourceArn=cluster_arn,
            secretArn=secret_arn,
            transactionId=txid,
        )
        # TODO: test uncommitted reads/writes here..
        assert result.get("transactionStatus") == "Transaction Committed"

        # test rollback transaction
        result = aws_client.rds_data.begin_transaction(
            resourceArn=cluster_arn,
            secretArn=secret_arn,
            database=database_name,
        )
        txid = result["transactionId"]
        result = aws_client.rds_data.execute_statement(
            secretArn=secret_arn,
            resourceArn=cluster_arn,
            sql="INSERT INTO foo2(id,s) VALUES (:v, :v1)",
            parameters=[
                {"name": "v", "value": {"longValue": 0}},
                {"name": "v1", "value": {"stringValue": "will-not-be-committed"}},
            ],
            transactionId=txid,
            database=database_name,
        )
        assert result["ResponseMetadata"]["HTTPStatusCode"] == 200
        # rollback
        result = aws_client.rds_data.rollback_transaction(
            resourceArn=cluster_arn,
            secretArn=secret_arn,
            transactionId=txid,
        )
        assert result.get("transactionStatus") == "Rollback Complete"
        # check that items are not in table
        result = aws_client.rds_data.execute_statement(
            secretArn=secret_arn,
            resourceArn=cluster_arn,
            sql="SELECT * FROM foo2",
            includeResultMetadata=True,
            database=database_name,
        )
        assert result.get("records", []) == []
        # TODO: try to rollback a non-existent txid

        # run INSERT query with parameters
        result = aws_client.rds_data.execute_statement(
            secretArn=secret_arn,
            resourceArn=cluster_arn,
            sql="INSERT INTO foo2(id,s) VALUES (:v, :v1)",
            parameters=[
                {"name": "v", "value": {"longValue": 234}},
                {"name": "v1", "value": {"stringValue": "t123"}},
            ],
            database=database_name,
        )

        assert result["ResponseMetadata"]["HTTPStatusCode"] == 200
        result = aws_client.rds_data.execute_statement(
            secretArn=secret_arn,
            resourceArn=cluster_arn,
            sql="SELECT * FROM foo2",
            includeResultMetadata=True,
            database=database_name,
        )
        # test some column metadata, to at least check fields presence
        assert result["columnMetadata"] == [
            {
                "arrayBaseColumnType": 0,
                "isAutoIncrement": False,
                "isCaseSensitive": False,
                "isCurrency": False,
                "isSigned": True,
                "label": "id",
                "name": "id",
                "nullable": 1,
                "precision": 10,
                "scale": 0,
                "schemaName": "",
                "tableName": "foo2",
                "type": 4,
                "typeName": "int4",
            },
            {
                "arrayBaseColumnType": 0,
                "isAutoIncrement": False,
                "isCaseSensitive": True,
                "isCurrency": False,
                "isSigned": False,
                "label": "s",
                "name": "s",
                "nullable": 1,
                "precision": 2147483647,
                "scale": 0,
                "schemaName": "",
                "tableName": "foo2",
                "type": 12,
                "typeName": "text",
            },
        ]

        assert result["records"] == [[{"longValue": 234}, {"stringValue": "t123"}]]

        result = aws_client.rds_data.execute_statement(
            secretArn=secret_arn,
            resourceArn=cluster_arn,
            sql="SELECT * FROM foo2",
            includeResultMetadata=True,
            formatRecordsAs="JSON",
            database=database_name,
        )

        assert "records" not in result
        assert "columnMetadata" not in result
        assert json.loads(result["formattedRecords"]) == [{"id": 234, "s": "t123"}]

        # test alias
        result = aws_client.rds_data.execute_statement(
            secretArn=secret_arn,
            resourceArn=cluster_arn,
            sql="SELECT id as test FROM foo2",
            includeResultMetadata=True,
            database=database_name,
        )

        assert result["columnMetadata"][0]["name"] == "test"
        assert result["columnMetadata"][0]["typeName"] == "int4"

        # test agg functions with alias
        result = aws_client.rds_data.execute_statement(
            secretArn=secret_arn,
            resourceArn=cluster_arn,
            sql="SELECT count(id) as test2 FROM foo2",
            includeResultMetadata=True,
            database=database_name,
        )

        assert result["columnMetadata"][0]["name"] == "test2"
        assert result["columnMetadata"][0]["typeName"] == "int8"

        # test agg functions without alias
        result = aws_client.rds_data.execute_statement(
            secretArn=secret_arn,
            resourceArn=cluster_arn,
            sql="SELECT count(id) FROM foo2",
            includeResultMetadata=True,
            database=database_name,
        )
        assert result["columnMetadata"][0]["name"] == "count"
        assert result["columnMetadata"][0]["typeName"] == "int8"

        result = aws_client.rds_data.execute_statement(
            secretArn=secret_arn,
            resourceArn=cluster_arn,
            sql="SELECT count(*) as rows FROM foo2",
            includeResultMetadata=True,
            formatRecordsAs="JSON",
            database=database_name,
        )
        assert json.loads(result["formattedRecords"]) == [{"rows": 1}]


class TestAuroraMysql:
    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(paths=["$..columnMetadata..precision"])
    @pytest.mark.parametrize("use_real_mysql_engine", [False, True])
    def test_data_api(
        self,
        use_real_mysql_engine,
        rds_create_db_cluster,
        create_secret,
        snapshot,
        aws_client,
        monkeypatch,
    ):
        monkeypatch.setattr(ext_config, "RDS_MYSQL_DOCKER", use_real_mysql_engine)
        db_name = "test"
        table_name = f"t_{short_uid()}"
        snapshot.add_transformer(snapshot.transform.regex(table_name, "<table-name>"))

        db_type = "aurora-mysql"
        cluster_id = f"rds-{short_uid()}"
        result = rds_create_db_cluster(
            DBClusterIdentifier=cluster_id,
            Engine=db_type,
            DatabaseName=db_name,
            EngineMode="serverless",
            EnableHttpEndpoint=True,
        )
        cluster_arn = result["DBClusterArn"]

        # create secret
        secret_name = f"s-{short_uid()}"
        secret_dict = {
            "username": DEFAULT_MASTER_USERNAME,
            "password": DEFAULT_TEST_MASTER_PASSWORD,
        }
        secret = create_secret(Name=secret_name, SecretString=json.dumps(secret_dict))
        secret_arn = secret["ARN"]

        # create table
        # TODO: create more comprehensive mapping of different column types, like in Postgres tests above
        result = aws_client.rds_data.execute_statement(
            secretArn=secret_arn,
            resourceArn=cluster_arn,
            sql=f"CREATE TABLE {table_name} (id int, name text, num double)",
            database=db_name,
        )
        assert "records" not in result
        assert result["generatedFields"] == []

        # insert into table
        result = aws_client.rds_data.execute_statement(
            secretArn=secret_arn,
            resourceArn=cluster_arn,
            database=db_name,
            sql=f"INSERT INTO {table_name} (id, name, num) VALUES (:id, :name, :num)",
            parameters=[
                {"name": "id", "value": {"longValue": 42}},
                {"name": "name", "value": {"stringValue": "test 123"}},
                {"name": "num", "value": {"doubleValue": 123.456}},
            ],
        )
        assert "records" not in result
        assert result["generatedFields"] == []

        # select from table
        result = aws_client.rds_data.execute_statement(
            secretArn=secret_arn,
            resourceArn=cluster_arn,
            database=db_name,
            sql=f"SELECT * FROM {table_name}",
            includeResultMetadata=True,
        )
        assert len(result["records"]) > 0
        snapshot.match("select-result", result)
