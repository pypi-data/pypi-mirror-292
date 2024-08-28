import logging
import os
import re
import secrets
import string

import aws_cdk
import aws_cdk as cdk
import aws_cdk.aws_ec2 as ec2
import aws_cdk.aws_lambda as lambda_
import aws_cdk.aws_redshift_alpha as redshift
import pg8000
import pytest
import redshift_connector
from localstack.constants import LOCALHOST_HOSTNAME
from localstack.testing.aws.util import is_aws_cloud
from localstack.testing.pytest import markers
from localstack.testing.scenario.cdk_lambda_helper import load_python_lambda_to_s3
from localstack.testing.scenario.provisioning import InfraProvisioner
from localstack.utils.strings import short_uid

LOG = logging.getLogger(__name__)


class TestRedshift:
    @markers.aws.unknown
    def test_create_cluster(self, redshift_create_cluster, aws_client):
        user = "test1"
        password = "test2"
        database = "db1"
        cluster_id = short_uid()
        table_name = "foobar"

        # create cluster
        result = redshift_create_cluster(
            DBName=database,
            NodeType="nt1",
            ClusterIdentifier=cluster_id,
            MasterUsername=user,
            MasterUserPassword=password,
        )
        assert "Cluster" in result
        cluster = result["Cluster"]
        assert cluster["MasterUsername"] == user
        port = cluster["Endpoint"]["Port"]
        address = cluster["Endpoint"]["Address"]
        match_result = re.match(
            r"^(?P<cluster_id>[^.]+)\..*\.(?P<hostname>[^.]+\.[^.]+\.[^.]+)$", address
        )
        assert match_result.group("cluster_id") == cluster_id
        assert match_result.group("hostname") == LOCALHOST_HOSTNAME

        # connect to DB
        with pg8000.connect(port=port, user=user, password=password, database=database) as conn:
            conn.autocommit = True
            with conn.cursor() as cursor:
                cursor.execute(f"CREATE TABLE {table_name}(id int)")
                cursor.execute(f"SELECT * FROM {table_name}")

        # describe clusters
        clusters = aws_client.redshift.describe_clusters()["Clusters"]
        matching = [c for c in clusters if c["ClusterIdentifier"] == cluster_id]
        assert matching
        assert matching[0]["MasterUsername"] == user
        assert matching[0]["DBName"] == database
        assert matching[0]["Endpoint"]["Port"] == port
        assert matching[0]["Endpoint"]["Address"] == address
        assert matching[0]["ClusterAvailabilityStatus"] == "Available"
        assert matching[0]["AvailabilityZoneRelocationStatus"] == "disabled"

        # list databases
        dbs = aws_client.redshift_data.list_databases(
            ClusterIdentifier=cluster_id, Database=database
        )
        assert "Databases" in dbs
        assert dbs["Databases"] == [database]

        # list tables
        tables = aws_client.redshift_data.list_tables(
            ClusterIdentifier=cluster_id, Database=database
        )
        assert "Tables" in tables
        assert tables["Tables"] == [{"name": table_name, "schema": "public", "type": "TABLE"}]

        def _query(sql):
            return aws_client.redshift_data.execute_statement(
                ClusterIdentifier=cluster_id, Database=database, Sql=sql
            )

        # run queries
        result = _query(f"INSERT INTO {table_name}(id) VALUES (123)")
        assert result["ResponseMetadata"]["HTTPStatusCode"] == 200
        select_query = f"SELECT * FROM {table_name}"
        result = _query(select_query)
        statement_id = result.get("Id")
        assert statement_id
        result = aws_client.redshift_data.get_statement_result(Id=statement_id)
        assert result["ColumnMetadata"] == [{"name": "id", "typeName": "INTEGER"}]
        assert result["Records"] == [[{"longValue": 123}]]
        assert result["TotalNumRows"] == 1

        # describe statement and table
        result = aws_client.redshift_data.describe_statement(Id=statement_id)
        assert result["ClusterIdentifier"] == cluster_id
        assert result["Database"] == database
        assert result["QueryString"] == select_query
        result = aws_client.redshift_data.describe_table(
            ClusterIdentifier=cluster_id, Database=database, Table=table_name
        )
        assert result["ColumnList"] == [
            {"name": "id", "nullable": 1, "tableName": "foobar", "typeName": "integer"}
        ]
        assert result["TableName"] == table_name

        # delete cluster
        aws_client.redshift.delete_cluster(ClusterIdentifier=cluster_id)
        clusters = aws_client.redshift.describe_clusters()["Clusters"]
        matching = [c for c in clusters if c["ClusterIdentifier"] == cluster_id]
        assert not matching
        # assert that the DB instance has terminated
        with pytest.raises(Exception):
            pg8000.connect(port=port, user=user, password=password, database=database)

    @markers.aws.unknown
    def test_parameter_group(self, aws_client):
        result = aws_client.redshift.create_cluster_parameter_group(
            ParameterGroupName="g1", ParameterGroupFamily="f1", Description="desc"
        )
        assert result["ClusterParameterGroup"]["ParameterGroupName"] == "g1"

        result = aws_client.redshift.describe_cluster_parameter_groups(ParameterGroupName="g1")
        assert len(result["ParameterGroups"]) == 1
        assert result["ParameterGroups"][0]["ParameterGroupName"] == "g1"

        def _assert_params(params):
            assert len(params) > 10
            assert {"ParameterName": "auto_analyze", "ParameterValue": "true"} in params
            assert {"ParameterName": "datestyle", "ParameterValue": "ISO,MDY"} in params
            assert {"ParameterName": "search_path", "ParameterValue": "$user,public"} in params

        result = aws_client.redshift.describe_default_cluster_parameters(ParameterGroupFamily="f1")
        params = result["DefaultClusterParameters"]
        assert params["ParameterGroupFamily"] == "f1"
        _assert_params(params["Parameters"])

        result = aws_client.redshift.describe_cluster_parameters(ParameterGroupName="g1")
        _assert_params(result["Parameters"])

    @markers.aws.unknown
    def test_redshift_connector(self, redshift_create_cluster, aws_client):
        user = "test1"
        password = "test2"
        database = "db1"
        cluster_id = short_uid()
        table_name = "foobar"
        # create cluster
        result = redshift_create_cluster(
            DBName=database,
            NodeType="nt1",
            ClusterIdentifier=cluster_id,
            MasterUsername=user,
            MasterUserPassword=password,
        )
        cluster = result["Cluster"]
        port = cluster["Endpoint"]["Port"]
        # Connects to Redshift cluster using AWS credentials
        conn = redshift_connector.connect(
            database=database,
            host="localhost",
            port=port,
            user=user,
            password=password,
            ssl=False,
        )

        with conn:
            conn.autocommit = True
            with conn.cursor() as cursor:
                cursor.execute(f"CREATE TABLE {table_name}(id int)")
                cursor.execute(f"INSERT INTO {table_name}(id) VALUES (123)")
                query = cursor.execute(f"SELECT * FROM {table_name}")
                assert query.fetchone() == [123]

        # delete cluster
        aws_client.redshift.delete_cluster(ClusterIdentifier=cluster_id)
        clusters = aws_client.redshift.describe_clusters()["Clusters"]
        matching = [c for c in clusters if c["ClusterIdentifier"] == cluster_id]
        assert not matching
        # assert that the DB instance has terminated

        with pytest.raises((redshift_connector.error.InterfaceError, ConnectionResetError)):  # noqa
            redshift_connector.connect(
                database=database,
                port=port,
                user=user,
                password=password,
                ssl=False,
            )


LAMBDA_FN_HELPER_KEY = "redshift-test-helper-fn"
INFRA_STACK_NAME = "RedshiftTestStack1"


class TestRedshiftCdk:
    @pytest.fixture(scope="class", autouse=True)
    def infrastructure(self, aws_client, infrastructure_setup):
        infra = infrastructure_setup(namespace="RedshiftCdk")
        stack = cdk.Stack(infra.cdk_app, INFRA_STACK_NAME)
        vpc = ec2.Vpc(stack, "Vpc")

        # TODO: change the username/password approach to a Secrets Manager one
        #   password should be obtainable from the Login object
        master_username = "admin"
        alphabet = string.ascii_letters + string.digits
        master_password = "".join(secrets.choice(alphabet) for i in range(20))
        cluster = redshift.Cluster(
            stack,
            f"{INFRA_STACK_NAME}Cluster",
            master_user=redshift.Login(
                master_username=master_username,
                master_password=aws_cdk.SecretValue.unsafe_plain_text(master_password),
            ),
            vpc=vpc,
            cluster_type=redshift.ClusterType.SINGLE_NODE,
            removal_policy=aws_cdk.RemovalPolicy.DESTROY,
            publicly_accessible=True,
        )
        cluster.connections.allow_default_port_from_any_ipv4("Open to the world")
        fn_path = os.path.join(os.path.dirname(__file__), "resources/redshift_connector.py")
        infra.add_custom_setup_provisioning_step(
            lambda: load_python_lambda_to_s3(
                aws_client.s3,
                infra.get_asset_bucket(),
                LAMBDA_FN_HELPER_KEY,
                fn_path,
                additional_python_packages=["redshift_connector"],
            )
        )

        bucket = cdk.aws_s3.Bucket.from_bucket_name(
            stack,
            "bucket_name",
            bucket_name=InfraProvisioner.get_asset_bucket_cdk(stack),
        )
        function = lambda_.Function(
            stack,
            "RedshiftConnectionLambda",
            handler="index.handler",
            vpc=vpc,
            code=lambda_.S3Code(bucket=bucket, key=LAMBDA_FN_HELPER_KEY),
            runtime=lambda_.Runtime.PYTHON_3_10,
            environment={
                "REDSHIFT_ENDPOINT": cluster.cluster_endpoint.socket_address,
                "CLUSTER_PASSWORD": master_password,
            },
        )

        cdk.CfnOutput(stack, "RedshiftClusterName", value=cluster.cluster_name)
        cdk.CfnOutput(stack, "HelperFnName", value=function.function_name)

        with infra.provisioner(skip_teardown=False) as prov:
            yield prov

    @markers.aws.validated
    @pytest.mark.skipif(
        not is_aws_cloud(),
        reason="resource creation doesn't work against LocalStack, needs fixing",
    )
    def test_cdk_cluster_creation(self, aws_client, infrastructure, snapshot):
        snapshot.add_transformer(snapshot.transform.redshift_api())
        describe_clusters = aws_client.redshift.describe_clusters()
        snapshot.match("describe_clusters", describe_clusters)

    @markers.aws.validated
    @pytest.mark.skipif(
        not is_aws_cloud(),
        reason="resource creation doesn't work against LocalStack, needs fixing",
    )
    def test_redshift_cluster_connection(self, infrastructure, aws_client, snapshot):
        # "Actual" test code can be found in ./resources/redshift_connector.py,
        # since the redshift cluster seems to be unavailable from outside the vpc in aws,
        # and is therefore deployed in a lambda.
        function_name = infrastructure.get_stack_outputs(stack_name=INFRA_STACK_NAME)[
            "HelperFnName"
        ]
        basic_table_insert_lambda = aws_client.lambda_.invoke(FunctionName=function_name)
        snapshot.match("basic_table_insert_lambda", basic_table_insert_lambda)

    @markers.aws.validated
    @pytest.mark.skipif(
        not is_aws_cloud(), reason="resource creation doesn't work against LocalStack, needs fixing"
    )
    def test_redshift_describe_cluster_parameters(self, infrastructure, aws_client, snapshot):
        describe_clusters = aws_client.redshift.describe_clusters()
        parameter_group = describe_clusters["Clusters"][0]["ClusterParameterGroups"][0][
            "ParameterGroupName"
        ]
        describe_parameter_groups = aws_client.redshift.describe_cluster_parameter_groups(
            ParameterGroupName=parameter_group
        )
        snapshot.match("describe_parameter_groups", describe_parameter_groups)
        describe_parameters = aws_client.redshift.describe_cluster_parameters(
            ParameterGroupName=parameter_group
        )
        snapshot.match("describe_parameters", describe_parameters)
