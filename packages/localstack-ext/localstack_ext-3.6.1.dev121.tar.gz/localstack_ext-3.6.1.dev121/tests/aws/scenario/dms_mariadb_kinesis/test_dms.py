"""


Notes:
    - Some endpoints are only valid as targets (e.g. dynamodb)

Examples:
    - https://github.com/awslabs/aws-cloudformation-templates/blob/master/aws/services/DMS/DMSAuroraToS3FullLoadAndOngoingReplication.json

"""

import json
import logging
import time
from typing import Callable

import aws_cdk as cdk
import aws_cdk.aws_dms as dms
import aws_cdk.aws_ec2 as ec2
import aws_cdk.aws_iam as iam
import aws_cdk.aws_kinesis as kinesis
import aws_cdk.aws_rds as rds
import aws_cdk.aws_secretsmanager as secretsmanager
import pytest
from aws_cdk import SecretValue
from botocore.exceptions import ClientError
from localstack.pro.core.aws.api.dms import MySQLSettings
from localstack.testing.aws.util import is_aws_cloud
from localstack.testing.pytest import markers
from localstack.utils.aws.arns import get_partition
from localstack.utils.strings import short_uid
from localstack.utils.sync import retry

from tests.aws.scenario.test_utils.dms_utils import (
    DEFAULT_TARGET_TYPE,
    NON_DEFAULT_TARGET_TYPE,
    UNFORMATTED_JSON_TARGET_TYPE,
    assert_dms_replication_task_status,
    assert_json_formatting,
    describe_table_statistics,
    dict_contains_subdict,
    get_records_from_shard,
    run_queries_on_mysql,
    transform_kinesis_data,
)

USERNAME = "admin"
USER_PWD = "1Wp2Aide=z=,eLX3RrD4gJ4o54puex"
DB_NAME = "testdb"

AssertFunctionType = Callable[[str], None]


LOG = logging.getLogger(__name__)


@markers.acceptance_test
class TestDmsScenario:
    """
    Used to run tests for the mariadb (or mysql) source and kinesis target

    Currently we configure two sources (mariadb, and mysql), and target kinesis.
    There are different definitions for the target, as it can be configured with different settings, that modify the actual
    output.
    """

    STACK_NAME = "DmsMariaDBKinesisStack"

    @pytest.fixture(scope="class")
    def infrastructure(self, infrastructure_setup, region_name):
        # force-synth flag is set to True to ensure that we create the template for every run as we need to search for a free port when starting the test.
        infra = infrastructure_setup("DmsMariaDBKinesis", force_synth=True)

        stack = cdk.Stack(infra.cdk_app, self.STACK_NAME)

        # Role definitions
        assume_role_policy_document = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"Service": "dms.amazonaws.com"},
                    "Action": "sts:AssumeRole",
                }
            ],
        }
        if is_aws_cloud():
            # Those roles are important on AWS and need to have the specific name.
            # The test ended up being flaky in the pipeline, maybe a cloudformation issue that didn't fully clean up the roles?
            # As the roles are not required by Localstack, we can disable their creation for now.
            # TODO: Figure out why the role are sometimes left dangling creating pipeline flakes
            iam.CfnRole(
                stack,
                "DmsVpcRole",
                managed_policy_arns=[
                    f"arn:{get_partition(region_name)}:iam::aws:policy/service-role/AmazonDMSVPCManagementRole",
                ],
                assume_role_policy_document=assume_role_policy_document,
                role_name="dms-vpc-role",  # this exact name needs to be set
            )
            # role for creating logs
            # https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Troubleshooting.html#CHAP_Troubleshooting.General.CWL
            iam.CfnRole(
                stack,
                "DmsLogsRole",
                managed_policy_arns=[
                    f"arn:{get_partition(region_name)}:iam::aws:policy/service-role/AmazonDMSCloudWatchLogsRole",
                ],
                assume_role_policy_document=assume_role_policy_document,
                role_name="dms-cloudwatch-logs-role",  # this exact name needs to be set
            )

        dms_assume_role = iam.Role(
            stack, "SuperRole", assumed_by=iam.ServicePrincipal("dms.amazonaws.com")
        )

        # Networking definitions
        vpc = ec2.Vpc(
            stack,
            "vpc",
            vpc_name="vpc",
            create_internet_gateway=True,
            enable_dns_hostnames=True,
            enable_dns_support=True,
            nat_gateways=0,
        )
        security_group = ec2.SecurityGroup(
            stack,
            "sg",
            vpc=vpc,
            description="Security group for DMS sample",
            allow_all_outbound=True,
        )

        ### Resource definitions
        credentials = rds.Credentials.from_password(
            username=USERNAME,
            password=SecretValue.unsafe_plain_text(USER_PWD),
        )

        # Create the RDS MySQL instance
        db_parameters_config = {
            "binlog_checksum": "NONE",
            # only for read replicas "log_slave_updates": "TRUE",
            "binlog_row_image": "Full",
            "binlog_format": "ROW",
        }

        def _create_db_instance(instance_id, engine):
            return rds.DatabaseInstance(
                stack,
                instance_id,
                credentials=credentials,
                database_name=DB_NAME,
                engine=engine,
                instance_type=ec2.InstanceType("t3.micro"),
                parameters=db_parameters_config,
                publicly_accessible=True,
                removal_policy=cdk.RemovalPolicy.DESTROY,
                security_groups=[security_group],
                vpc=vpc,
                vpc_subnets=ec2.SubnetSelection(subnets=vpc.public_subnets),
            )

        # create db instances
        db_instance_mysql = _create_db_instance(
            "dbinstance", rds.DatabaseInstanceEngine.mysql(version=rds.MysqlEngineVersion.VER_8_0)
        )
        db_instance_mariadb = _create_db_instance(
            "dbinstance-mariadb",
            rds.DatabaseInstanceEngine.maria_db(version=rds.MariaDbEngineVersion.VER_10_11),
        )

        # Update Security Group Ingress Policy
        db_mysql_port_as_number = cdk.Token.as_number(db_instance_mysql.db_instance_endpoint_port)
        db_mariadb_port_as_number = cdk.Token.as_number(
            db_instance_mariadb.db_instance_endpoint_port
        )
        ports = [db_mysql_port_as_number, db_mariadb_port_as_number]
        security_group.connections.allow_from(
            other=ec2.Peer.any_ipv4(),
            port_range=ec2.Port.tcp_range(min(ports), max(ports)),
        )

        # Create secret for mysql access
        mysql_secret = secretsmanager.CfnSecret(
            stack,
            "mysql-secret",
            secret_string=json.dumps(
                {
                    "username": USERNAME,
                    "password": USER_PWD,
                    "host": db_instance_mysql.db_instance_endpoint_address,
                    "port": db_mysql_port_as_number,
                }
            ),
        )
        mysql_access_role = iam.Role(
            stack,
            "mysql-access-role",
            assumed_by=iam.ServicePrincipal(f"dms.{stack.region}.amazonaws.com"),
            inline_policies={
                "AllowSecrets": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            actions=["secretsmanager:GetSecretValue"],
                            effect=iam.Effect.ALLOW,
                            resources=[mysql_secret.ref],
                        )
                    ]
                )
            },
        )
        # Target endpoint (Kinesis stream)
        target_stream = kinesis.Stream(
            stack,
            "TargetStream",
            shard_count=1,
            retention_period=cdk.Duration.hours(24),
        )
        target_stream.grant_read_write(dms_assume_role)
        target_stream.apply_removal_policy(cdk.RemovalPolicy.DESTROY)

        # Replication Instance
        replication_subnet_group = dms.CfnReplicationSubnetGroup(
            stack,
            "ReplSubnetGroup",
            replication_subnet_group_description="Replication Subnet Group for DMS test",
            subnet_ids=[subnet.subnet_id for subnet in vpc.public_subnets],
        )

        replication_instance = dms.CfnReplicationInstance(
            stack,
            "instance",
            replication_instance_class="dms.t2.micro",
            allocated_storage=5,
            replication_subnet_group_identifier=replication_subnet_group.ref,
            allow_major_version_upgrade=False,
            auto_minor_version_upgrade=False,
            multi_az=False,
            publicly_accessible=True,
            vpc_security_group_ids=[security_group.security_group_id],
            availability_zone=vpc.public_subnets[0].availability_zone,
        )

        # Source Endpoints
        source_endpoint_mysql = dms.CfnEndpoint(
            stack,
            "source",
            database_name=DB_NAME,
            endpoint_type="source",
            engine_name="mysql",
            my_sql_settings=dms.CfnEndpoint.MySqlSettingsProperty(
                secrets_manager_access_role_arn=mysql_access_role.role_arn,
                secrets_manager_secret_id=mysql_secret.ref,
            ),
        )

        source_endpoint_mariadb = dms.CfnEndpoint(
            stack,
            "source-mariadb",
            database_name=DB_NAME,
            endpoint_type="source",
            engine_name="mariadb",
            username=credentials.username,
            password=credentials.password.unsafe_unwrap(),
            server_name=db_instance_mariadb.db_instance_endpoint_address,
            port=db_mariadb_port_as_number,
        )

        # Default Target Endpoint
        target_endpoint = dms.CfnEndpoint(
            stack,
            "target",
            endpoint_type="target",
            engine_name="kinesis",
            kinesis_settings=dms.CfnEndpoint.KinesisSettingsProperty(
                stream_arn=target_stream.stream_arn,
                message_format="json",
                service_access_role_arn=dms_assume_role.role_arn,
            ),
        )

        # JSON unformatted Target Endpoint
        target_endpoint_json_unformatted = dms.CfnEndpoint(
            stack,
            "target_json_unformatted",
            endpoint_type="target",
            engine_name="kinesis",
            kinesis_settings=dms.CfnEndpoint.KinesisSettingsProperty(
                stream_arn=target_stream.stream_arn,
                message_format="json-unformatted",
                service_access_role_arn=dms_assume_role.role_arn,
            ),
        )

        # Non-Default Endpoint
        target_endpoint_non_default_settings = dms.CfnEndpoint(
            stack,
            "target_non_default_settings",
            endpoint_type="target",
            engine_name="kinesis",
            kinesis_settings=dms.CfnEndpoint.KinesisSettingsProperty(
                stream_arn=target_stream.stream_arn,
                message_format="json",
                service_access_role_arn=dms_assume_role.role_arn,
                include_control_details=True,
                include_null_and_empty=True,
                include_partition_value=True,
                include_table_alter_operations=True,
                include_transaction_details=True,
                partition_include_schema_table=True,
            ),
        )
        table_mapping = {
            "rules": [
                {
                    "rule-type": "selection",
                    "rule-id": "1",
                    "rule-name": "rule1",
                    "object-locator": {
                        "schema-name": "something",
                        "table-name": "NotExistingTable",
                    },
                    "rule-action": "include",
                }
            ]
        }
        # just creating one task here to check if the cdk deployment works on LS
        # for the tests we will create and delete replication tasks for each test case
        replication_task = dms.CfnReplicationTask(
            stack,
            "MyCfnReplicationTask",
            migration_type="full-load",
            replication_instance_arn=replication_instance.ref,
            source_endpoint_arn=source_endpoint_mysql.ref,
            table_mappings=json.dumps(table_mapping),
            target_endpoint_arn=target_endpoint.ref,
            replication_task_identifier="replicationTaskIdentifier",
            resource_identifier="resourceIdentifier",
        )

        cdk.CfnOutput(stack, "KinesisStreamArn", value=target_stream.stream_arn)

        cdk.CfnOutput(stack, "DbInstanceMySQLArn", value=db_instance_mysql.instance_arn)
        cdk.CfnOutput(
            stack, "DbEndpointMySQL", value=db_instance_mysql.db_instance_endpoint_address
        )
        cdk.CfnOutput(stack, "DbPortMySQL", value=db_instance_mysql.db_instance_endpoint_port)

        cdk.CfnOutput(stack, "DbInstanceMariadbArn", value=db_instance_mariadb.instance_arn)
        cdk.CfnOutput(
            stack, "DbEndpointMariadb", value=db_instance_mariadb.db_instance_endpoint_address
        )
        cdk.CfnOutput(stack, "DbPortMariadb", value=db_instance_mariadb.db_instance_endpoint_port)

        cdk.CfnOutput(stack, "ReplicationInstanceArn", value=replication_instance.ref)
        cdk.CfnOutput(stack, "SourceEndpointMySQLArn", value=source_endpoint_mysql.ref)
        cdk.CfnOutput(stack, "SourceEndpointMariadbArn", value=source_endpoint_mariadb.ref)
        cdk.CfnOutput(stack, "TargetEndpointDefaultArn", value=target_endpoint.ref)
        cdk.CfnOutput(
            stack, "TargetEndpointNonDefaultArn", value=target_endpoint_non_default_settings.ref
        )
        cdk.CfnOutput(
            stack, "TargetEndpointUnformattedJsonArn", value=target_endpoint_json_unformatted.ref
        )
        cdk.CfnOutput(stack, "TestReplicationTask", value=replication_task.ref)
        with infra.provisioner(skip_teardown=False) as prov:
            yield prov

    @pytest.fixture
    def setup_replication_databases(
        self,
        infrastructure,
        aws_client,
    ):
        outputs = infrastructure.get_stack_outputs(self.STACK_NAME)

        db_endpoint = ""
        db_port = None

        def _setup_replication_databases(**kwargs):
            nonlocal db_endpoint, db_port
            if "database_type" not in kwargs:
                kwargs["database_type"] = "mariadb"

            database_type = kwargs["database_type"]
            db_endpoint = (
                outputs["DbEndpointMySQL"]
                if database_type == "mysql"
                else outputs["DbEndpointMariadb"]
            )
            db_port = (
                outputs["DbPortMySQL"] if database_type == "mysql" else outputs["DbPortMariadb"]
            )

            # configure the log-retention time  TODO we may need to implement this procedure on LS as well
            sql_config = [
                "SET autocommit=1;",
                "call mysql.rds_set_configuration('binlog retention hours', 24);",
            ]
            _run_queries_on_mysql(
                host=db_endpoint,
                port=db_port,
                queries=sql_config,
            )

            # setup source database
            queries = [
                f"USE {DB_NAME};",
                SQL_CREATE_ACCOUNTS_TABLE,
                SQL_CREATE_AUTHORS_TABLE,
                SQL_CREATE_BOOKS_TABLE,
                "CREATE TABLE test (test_id INT AUTO_INCREMENT PRIMARY KEY, description VARCHAR(255) NOT NULL, alt_text VARCHAR(100));",
            ]
            queries.extend(SQL_INSERT_ACCOUNTS_SAMPLE_DATA_LIST)
            queries.extend(SQL_INSERT_AUTHORS_SAMPLE_DATA_LIST)
            queries.append(SQL_INSERT_BOOK_SAMPLE_DATA)

            _run_queries_on_mysql(
                host=db_endpoint,
                port=db_port,
                queries=queries,
            )

            return db_endpoint

        yield _setup_replication_databases

        # cleanup
        _run_queries_on_mysql(
            host=db_endpoint,
            port=db_port,
            queries=[
                "DROP TABLE IF EXISTS books;",
                "DROP TABLE IF EXISTS authors;",
                "DROP TABLE IF EXISTS accounts;",
                "DROP TABLE IF EXISTS writers;",
                "DROP TABLE IF EXISTS test;",
            ],
        )

    @pytest.fixture
    def setup_additional_tables(self):
        db_endpoint = ""
        db_port = None

        def _setup_additional_tables(**kwargs):
            nonlocal db_endpoint, db_port
            db_endpoint = kwargs["db_endpoint"]
            db_port = kwargs["db_port"]
            _run_queries_on_mysql(
                host=db_endpoint,
                port=db_port,
                queries=[
                    "CREATE TABLE pigeons (table_id INT AUTO_INCREMENT PRIMARY KEY, description VARCHAR(255) NOT NULL, feather_count INT);",
                    "CREATE TABLE codfish (table_id INT AUTO_INCREMENT PRIMARY KEY, description VARCHAR(255) NOT NULL,  birthday DATE);",
                    "CREATE TABLE lions (table_id INT AUTO_INCREMENT PRIMARY KEY, description VARCHAR(255) NOT NULL, consumed_food_kg DOUBLE);",
                    "CREATE TABLE apes (table_id INT AUTO_INCREMENT PRIMARY KEY, description VARCHAR(255) NOT NULL, is_primate TINYINT(1));",
                ],
            )

        yield _setup_additional_tables

        _run_queries_on_mysql(
            host=db_endpoint,
            port=db_port,
            queries=[
                "DROP TABLE IF EXISTS pigeons;",
                "DROP TABLE IF EXISTS codfish;",
                "DROP TABLE IF EXISTS lions;",
                "DROP TABLE IF EXISTS apes;",
                "DROP TABLE IF EXISTS seagulls;",
            ],
        )

    @pytest.fixture
    def setup_replication_task(self, dms_create_replication_task, infrastructure, aws_client):
        replication_task_arn = ""
        outputs = infrastructure.get_stack_outputs(self.STACK_NAME)

        def _setup_replication_task(**kwargs):
            nonlocal replication_task_arn
            if "target_type" not in kwargs:
                kwargs["target_type"] = "default"
            if "database_type" not in kwargs:
                kwargs["database_type"] = "mariadb"
            target_type = kwargs["target_type"]
            replication_instance_arn = outputs["ReplicationInstanceArn"]
            database_type = kwargs["database_type"]
            source_endpoint_arn = (
                outputs["SourceEndpointMySQLArn"]
                if database_type == "mysql"
                else outputs["SourceEndpointMariadbArn"]
            )

            target_endpoint_arn: str
            if target_type == NON_DEFAULT_TARGET_TYPE:
                target_endpoint_arn = outputs["TargetEndpointNonDefaultArn"]
            else:
                target_endpoint_arn = outputs["TargetEndpointDefaultArn"]

            # create replication task
            replication_task_settings = {"Logging": {"EnableLogging": True}}

            replication_task_settings["BeforeImageSettings"] = {
                "EnableBeforeImage": True,
                "FieldName": "before-image",
                "ColumnFilter": "all",  # pk-only will only report the e.g. "author_id": 1
            }

            replication_task = dms_create_replication_task(
                MigrationType="cdc",
                ReplicationInstanceArn=replication_instance_arn,
                SourceEndpointArn=source_endpoint_arn,
                TargetEndpointArn=target_endpoint_arn,
                TableMappings=json.dumps(DEFAULT_TABLE_MAPPING),
                ReplicationTaskSettings=json.dumps(replication_task_settings),
            )
            replication_task_arn = replication_task["ReplicationTask"]["ReplicationTaskArn"]

            # wait for task to be ready
            retry(
                lambda: assert_dms_replication_task_status(
                    aws_client.dms, replication_task_arn, expected_status="ready"
                ),
                retries=100,
                sleep=5 if is_aws_cloud() else 1,
            )
            aws_client.dms.start_replication_task(
                ReplicationTaskArn=replication_task_arn,
                StartReplicationTaskType="start-replication",
            )
            # now every change on the db should be added to kinesis
            # ensure the task is running before executing queries
            retry(
                lambda: assert_dms_replication_task_status(
                    aws_client.dms, replication_task_arn, expected_status="running"
                ),
                retries=150,
                sleep=5 if is_aws_cloud() else 1,
            )

            return replication_task_arn

        yield _setup_replication_task

        # cleanup
        aws_client.dms.stop_replication_task(ReplicationTaskArn=replication_task_arn)
        retry(
            lambda: assert_dms_replication_task_status(
                aws_client.dms, replication_task_arn, expected_status="stopped"
            ),
            retries=100,
            sleep=10 if is_aws_cloud() else 1,
        )
        aws_client.dms.delete_replication_task(ReplicationTaskArn=replication_task_arn)

    @markers.aws.validated
    def test_describe_endpoints(self, infrastructure, aws_client, snapshot):
        snapshot.add_transformer(snapshot.transform.dms_api())
        outputs = infrastructure.get_stack_outputs(self.STACK_NAME)
        source_endpoint_arn = outputs["SourceEndpointMySQLArn"]
        source_endpoint_mariadb_arn = outputs["SourceEndpointMariadbArn"]
        target_endpoint_arn = outputs["TargetEndpointDefaultArn"]
        target_endpoint_unformatted_arn = outputs["TargetEndpointUnformattedJsonArn"]
        target_endpoint_non_default_arn = outputs["TargetEndpointNonDefaultArn"]

        source_endpoint = aws_client.dms.describe_endpoints(
            Filters=[{"Name": "endpoint-arn", "Values": [source_endpoint_arn]}]
        )
        snapshot.match("describe-source-endpoint-mysql", source_endpoint)

        source_endpoint_mariadb = aws_client.dms.describe_endpoints(
            Filters=[{"Name": "endpoint-arn", "Values": [source_endpoint_mariadb_arn]}]
        )
        snapshot.match("describe-source-endpoint-mariadb", source_endpoint_mariadb)

        target_endpoint = aws_client.dms.describe_endpoints(
            Filters=[{"Name": "endpoint-arn", "Values": [target_endpoint_arn]}]
        )
        snapshot.match("describe-target-endpoint", target_endpoint)

        target_endpoint_2 = aws_client.dms.describe_endpoints(
            Filters=[{"Name": "endpoint-arn", "Values": [target_endpoint_unformatted_arn]}]
        )
        snapshot.match("describe-target-endpoint-unformatted", target_endpoint_2)

        target_endpoint_3 = aws_client.dms.describe_endpoints(
            Filters=[{"Name": "endpoint-arn", "Values": [target_endpoint_non_default_arn]}]
        )
        snapshot.match("describe-target-endpoint-non-default", target_endpoint_3)

        # describe-endpoint-settings engine-name mysql/kinesis -> static response, can be tested in it-test

    @markers.aws.validated
    def test_describe_test_replication_task(self, infrastructure, aws_client, snapshot):
        snapshot.add_transformer(snapshot.transform.dms_api())
        outputs = infrastructure.get_stack_outputs(self.STACK_NAME)
        task_arn = outputs["TestReplicationTask"]

        retry(
            lambda: assert_dms_replication_task_status(
                aws_client.dms, task_arn, expected_status="ready", wait_for_task_stats=True
            ),
            retries=100,
            sleep=5 if is_aws_cloud() else 1,
        )
        result = aws_client.dms.describe_replication_tasks(
            Filters=[{"Name": "replication-task-arn", "Values": [task_arn]}]
        )
        snapshot.match("describe-test-replication-task", result)

    @markers.aws.validated
    def test_delete_replication_instance_active_task(self, infrastructure, aws_client, snapshot):
        snapshot.add_transformer(snapshot.transform.dms_api())
        outputs = infrastructure.get_stack_outputs(self.STACK_NAME)
        instance_arn = outputs["ReplicationInstanceArn"]
        instance_name = aws_client.dms.describe_replication_instances(
            Filters=[{"Name": "replication-instance-arn", "Values": [instance_arn]}]
        )["ReplicationInstances"][0]["ReplicationInstanceIdentifier"]
        snapshot.add_transformer(snapshot.transform.regex(instance_name, "<instance-name>"))

        # test deletion of replication instance when there is a task active
        with pytest.raises(ClientError) as e:
            aws_client.dms.delete_replication_instance(
                ReplicationInstanceArn=instance_arn,
            )
        snapshot.match("delete-replication-instance-failed", e.value.response)

    @markers.aws.validated
    def test_test_endpoint_connection(self, infrastructure, aws_client, snapshot):
        snapshot.add_transformer(snapshot.transform.dms_api())
        outputs = infrastructure.get_stack_outputs(self.STACK_NAME)
        replication_instance_arn = outputs["ReplicationInstanceArn"]
        mysql_source_endpoint_arn = outputs["SourceEndpointMySQLArn"]
        mariadb_source_endpoint_arn = outputs["SourceEndpointMariadbArn"]
        target_endpoint_arn = outputs["TargetEndpointDefaultArn"]
        endpoint_arns = {
            "source-mysql": mysql_source_endpoint_arn,
            "source-mariadb": mariadb_source_endpoint_arn,
            "target-kinesis": target_endpoint_arn,
        }

        def _test_connection(connection_arn):
            connections = aws_client.dms.describe_connections(
                Filters=[{"Name": "endpoint-arn", "Values": [connection_arn]}]
            ).get("Connections")
            if not connections or not connections[0].get("Status") == "successful":
                # this will raise an exception if the status is "testing"
                aws_client.dms.test_connection(
                    ReplicationInstanceArn=replication_instance_arn, EndpointArn=connection_arn
                )

        for endpoint_arn in endpoint_arns.values():
            _test_connection(endpoint_arn)

        def _verify_status(endpoint_arn: str):
            connection = aws_client.dms.describe_connections(
                Filters=[{"Name": "endpoint-arn", "Values": [endpoint_arn]}]
            ).get("Connections")[0]
            assert connection["Status"] == "successful"
            return connection

        for endpoint, endpoint_arn in endpoint_arns.items():
            result = retry(
                lambda: _verify_status(endpoint_arn),
                retries=30,
                sleep=5 if is_aws_cloud() else 1,
            )
            snapshot.match(f"{endpoint}-describe-connection", result)

    @markers.aws.validated
    def test_connection_with_secret(
        self,
        infrastructure,
        aws_client,
        create_secret,
        create_role_with_policy_for_principal,
        dms_create_endpoint,
        region_name,
        snapshot,
    ):
        snapshot.add_transformer(snapshot.transform.dms_api())
        outputs = infrastructure.get_stack_outputs(self.STACK_NAME)
        replication_instance_arn = outputs["ReplicationInstanceArn"]
        db_endpoint = outputs["DbEndpointMariadb"]
        db_port = outputs["DbPortMariadb"]

        secret = create_secret(Name=f"secret-{short_uid()}", SecretString="{}")
        secret_id = secret["ARN"]
        snapshot.match("generated-secret-id", {"secret-id": secret_id})
        role_name, role_arn = create_role_with_policy_for_principal(
            principal={"Service": f"dms.{region_name}.amazonaws.com"},
            resource=secret["ARN"],
            effect="Allow",
            actions=["secretsmanager:GetSecretValue"],
        )
        endpoint = dms_create_endpoint(
            EndpointIdentifier=f"test-endpoint-{short_uid()}",
            EndpointType="source",
            EngineName="mysql",
            DatabaseName=DB_NAME,
            MySQLSettings=MySQLSettings(
                SecretsManagerAccessRoleArn=role_arn,
                SecretsManagerSecretId=secret_id,
            ),
        )

        def _test_connection():
            aws_client.dms.test_connection(
                ReplicationInstanceArn=replication_instance_arn, EndpointArn=endpoint["EndpointArn"]
            )

        def _verify_status(endpoint_arn: str, expected_status: str):
            connection = aws_client.dms.describe_connections(
                Filters=[{"Name": "endpoint-arn", "Values": [endpoint_arn]}]
            ).get("Connections")[0]
            assert connection["Status"] == expected_status
            return connection

        # Test with invalid secret
        _test_connection()
        incomplete_secret = retry(
            lambda: _verify_status(endpoint["EndpointArn"], "failed"),
            retries=30,
            sleep=5 if is_aws_cloud() else 1,
        )
        snapshot.match("invalid-secret-describe-connection", incomplete_secret)

        # test with valid secret
        aws_client.secretsmanager.put_secret_value(
            SecretId=secret_id,
            SecretString=json.dumps(
                {
                    "host": db_endpoint,
                    "port": db_port,
                    "username": USERNAME,
                    "password": USER_PWD,
                }
            ),
        )

        def _wait_vor_secret_value():
            secret_value = aws_client.secretsmanager.get_secret_value(SecretId=secret_id)
            assert secret_value["SecretString"] != ""

        retry(
            _wait_vor_secret_value,
            retries=30,
            sleep=5 if is_aws_cloud() else 1,
        )

        _test_connection()
        valid_connection = retry(
            lambda: _verify_status(endpoint["EndpointArn"], "successful"),
            retries=30,
            sleep=5 if is_aws_cloud() else 1,
        )
        snapshot.match("valid-secret-describe-connection", valid_connection)

    @markers.aws.validated
    def test_empty_describe_table_statics(
        self,
        infrastructure,
        aws_client,
        region_name,
        account_id,
        snapshot,
        dms_create_replication_task,
    ):
        snapshot.add_transformer(snapshot.transform.dms_api())
        snapshot.add_transformer(snapshot.transform.kinesis_api())
        outputs = infrastructure.get_stack_outputs(self.STACK_NAME)
        replication_instance_arn = outputs["ReplicationInstanceArn"]
        source_endpoint_arn = outputs["SourceEndpointMySQLArn"]
        target_endpoint_arn = outputs["TargetEndpointDefaultArn"]

        not_existent_task_arn = (
            f"arn:{get_partition(region_name)}:dms:{region_name}:{account_id}:task:test-task"
        )

        with pytest.raises(ClientError) as e:
            aws_client.dms.describe_table_statistics(ReplicationTaskArn=not_existent_task_arn)
        snapshot.match("describe_table_statistics_not_existent_task_arn", e.value.response)

        with pytest.raises(ClientError) as e:
            aws_client.dms.describe_table_statistics(
                ReplicationTaskArn="M5CQ7FJE7AG3GULBS2T6GFY7YADUIWWD5WMLYBA"
            )
        snapshot.match("describe_table_statistics_invalid_arn", e.value.response)

        # create replication task
        table_mapping = {
            "rules": [
                {
                    "rule-type": "selection",
                    "rule-id": "1",
                    "rule-name": "rule1",
                    "object-locator": {
                        "schema-name": "something",
                        "table-name": "NotExistingTable",
                    },
                    "rule-action": "include",
                }
            ]
        }

        replication_task = dms_create_replication_task(
            MigrationType="full-load",
            ReplicationInstanceArn=replication_instance_arn,
            SourceEndpointArn=source_endpoint_arn,
            TargetEndpointArn=target_endpoint_arn,
            TableMappings=json.dumps(table_mapping),
        )
        replication_task_arn = replication_task["ReplicationTask"]["ReplicationTaskArn"]

        result = aws_client.dms.describe_table_statistics(ReplicationTaskArn=replication_task_arn)
        snapshot.match("describe_table_statistics", result)

        result = aws_client.dms.describe_table_statistics(
            ReplicationTaskArn=replication_task_arn,
            Filters=[{"Name": "schema-name", "Values": ["hello"]}],
        )
        snapshot.match("describe_table_statistics_empty_filter", result)

    @markers.aws.validated
    def test_invalid_replication_task(
        self, infrastructure, aws_client, snapshot, region_name, account_id
    ):
        snapshot.add_transformer(snapshot.transform.dms_api())
        snapshot.add_transformer(snapshot.transform.kinesis_api())
        outputs = infrastructure.get_stack_outputs(self.STACK_NAME)
        replication_instance_arn = outputs["ReplicationInstanceArn"]
        source_endpoint_arn = outputs["SourceEndpointMySQLArn"]
        target_endpoint_arn = outputs["TargetEndpointDefaultArn"]

        # test invalid table mapping (not json-formatted)
        with pytest.raises(ClientError) as e:
            aws_client.dms.create_replication_task(
                ReplicationTaskIdentifier=f"task-{short_uid()}",
                MigrationType="full-load",
                ReplicationInstanceArn=replication_instance_arn,
                SourceEndpointArn=source_endpoint_arn,
                TargetEndpointArn=target_endpoint_arn,
                TableMappings='{"rules": }',
            )
        # TODO from the error messages it seems they use gson
        # the error message is very specific, we may need to skip the verify for LS on the message
        #   Invalid Table Mappings document. Invalid json com.google.gson.stream.MalformedJsonException: Expected value at line 1 column 11 path $.rules
        # snapshot.match("create_replication_invalid_table_mapping", e.value.response)
        assert e.match("Invalid Table Mappings document. Invalid json")
        assert e.value.response["Error"]["Code"] == "InvalidParameterValueException"
        assert e.value.response["ResponseMetadata"]["HTTPStatusCode"] == 400

        # test invalid table mapping (valid json but unexpected format)
        with pytest.raises(ClientError) as e:
            aws_client.dms.create_replication_task(
                ReplicationTaskIdentifier=f"task-{short_uid()}",
                MigrationType="full-load",
                ReplicationInstanceArn=replication_instance_arn,
                SourceEndpointArn=source_endpoint_arn,
                TargetEndpointArn=target_endpoint_arn,
                TableMappings=json.dumps({"hello": "world"}),
            )
        snapshot.match("create_replication_unexpected_table_mapping", e.value.response)

        # test invalid table-mapping rule-type
        with pytest.raises(ClientError) as e:
            aws_client.dms.create_replication_task(
                ReplicationTaskIdentifier=f"task-{short_uid()}",
                MigrationType="full-load",
                ReplicationInstanceArn=replication_instance_arn,
                SourceEndpointArn=source_endpoint_arn,
                TargetEndpointArn=target_endpoint_arn,
                TableMappings=json.dumps(
                    {
                        "rules": [
                            {
                                "rule-type": "select",
                                "rule-id": "1",
                                "rule-name": "rule1",
                                "object-locator": {"schema-name": DB_NAME, "table-name": "Table%"},
                                "rule-action": "include",
                            }
                        ]
                    }
                ),
            )
        snapshot.match("create_replication_table_mapping_rule_type", e.value.response)

        # test invalid table-mapping object-locator missing
        with pytest.raises(ClientError) as e:
            aws_client.dms.create_replication_task(
                ReplicationTaskIdentifier=f"task-{short_uid()}",
                MigrationType="full-load",
                ReplicationInstanceArn=replication_instance_arn,
                SourceEndpointArn=source_endpoint_arn,
                TargetEndpointArn=target_endpoint_arn,
                TableMappings=json.dumps(
                    {
                        "rules": [
                            {
                                "rule-type": "selection",
                                "rule-id": "1",
                                "rule-name": "rule1",
                                "rule-action": "include",
                            }
                        ]
                    }
                ),
            )
        # TODO very specific error msg, may need to be skipped for LS
        #  Error in mapping rules. Rule with ruleId = 1 failed validation. object locator cannot be null
        # snapshot.match("create_replication_table_mapping_no_object_locator", e.value.response)
        assert e.value.response["Error"]["Code"] == "InvalidParameterValueException"
        assert e.value.response["ResponseMetadata"]["HTTPStatusCode"] == 400

        # test invalid table-mapping rule-action
        with pytest.raises(ClientError) as e:
            aws_client.dms.create_replication_task(
                ReplicationTaskIdentifier=f"task-{short_uid()}",
                MigrationType="full-load",
                ReplicationInstanceArn=replication_instance_arn,
                SourceEndpointArn=source_endpoint_arn,
                TargetEndpointArn=target_endpoint_arn,
                TableMappings=json.dumps(
                    {
                        "rules": [
                            {
                                "rule-type": "selection",
                                "rule-id": "1",
                                "rule-name": "rule1",
                                "object-locator": {"schema-name": DB_NAME, "table-name": "Table%"},
                                "rule-action": "including",
                            }
                        ]
                    }
                ),
            )
        snapshot.match("create_replication_table_mapping_rule_action", e.value.response)

        # rule-id and rule-name are not unique
        table_mapping = {
            "rules": [
                {
                    "rule-type": "selection",
                    "rule-id": "1",
                    "rule-name": "rule1",
                    "object-locator": {"schema-name": DB_NAME, "table-name": "Table%"},
                    "rule-action": "include",
                },
                {
                    "rule-type": "selection",
                    "rule-id": "1",
                    "rule-name": "rule1",
                    "object-locator": {"schema-name": DB_NAME, "table-name": "TableB"},
                    "rule-action": "exclude",
                },
            ]
        }
        # rule-id and rule-name are not unique
        with pytest.raises(ClientError) as e:
            aws_client.dms.create_replication_task(
                ReplicationTaskIdentifier=f"task-{short_uid()}",
                MigrationType="full-load",
                ReplicationInstanceArn=replication_instance_arn,
                SourceEndpointArn=source_endpoint_arn,
                TargetEndpointArn=target_endpoint_arn,
                TableMappings=json.dumps(table_mapping),
            )
        snapshot.match("create_replication_task_invalid_1", e.value.response)

        table_mapping["rules"][1]["rule-id"] = 2  # set an integer
        table_mapping["rules"][1]["rule-type"] = "something"

        # TODO according docs the rule-name needs to be unique,
        #  but test revealed that only the rule-id is validated!

        # rule-type is invalid
        with pytest.raises(ClientError) as e:
            aws_client.dms.create_replication_task(
                ReplicationTaskIdentifier=f"task-{short_uid()}",
                MigrationType="full-load",
                ReplicationInstanceArn=replication_instance_arn,
                SourceEndpointArn=source_endpoint_arn,
                TargetEndpointArn=target_endpoint_arn,
                TableMappings=json.dumps(table_mapping),
            )
        snapshot.match("create_replication_task_invalid_2", e.value.response)

        # fix table-mapping
        table_mapping["rules"][1]["rule-type"] = "selection"

        # test invalid migration-type
        invalid_endpoint = (
            f"arn:{get_partition(region_name)}:dms:{region_name}:{account_id}:endpoint:identifier"
        )
        with pytest.raises(ClientError) as e:
            aws_client.dms.create_replication_task(
                ReplicationTaskIdentifier=f"task-{short_uid()}",
                MigrationType="full-loading",
                ReplicationInstanceArn=replication_instance_arn,
                SourceEndpointArn=invalid_endpoint,
                TargetEndpointArn=target_endpoint_arn,
                TableMappings=json.dumps(table_mapping),
            )
        snapshot.match("create_replication_invalid_migration_type", e.value.response)

        # test invalid source endpoints
        invalid_endpoint = (
            f"arn:{get_partition(region_name)}:dms:{region_name}:{account_id}:endpoint:identifier"
        )
        with pytest.raises(ClientError) as e:
            aws_client.dms.create_replication_task(
                ReplicationTaskIdentifier=f"task-{short_uid()}",
                MigrationType="full-load",
                ReplicationInstanceArn=replication_instance_arn,
                SourceEndpointArn=invalid_endpoint,
                TargetEndpointArn=target_endpoint_arn,
                TableMappings=json.dumps(table_mapping),
            )
        snapshot.match("create_replication_invalid_source", e.value.response)

        # invalid target endpoint
        with pytest.raises(ClientError) as e:
            aws_client.dms.create_replication_task(
                ReplicationTaskIdentifier=f"task-{short_uid()}",
                MigrationType="full-load",
                ReplicationInstanceArn=replication_instance_arn,
                SourceEndpointArn=source_endpoint_arn,
                TargetEndpointArn=invalid_endpoint,
                TableMappings=json.dumps(table_mapping),
            )
        snapshot.match("create_replication_invalid_target", e.value.response)

        # switch target/source
        with pytest.raises(ClientError) as e:
            aws_client.dms.create_replication_task(
                ReplicationTaskIdentifier=f"task-{short_uid()}",
                MigrationType="full-load",
                ReplicationInstanceArn=replication_instance_arn,
                SourceEndpointArn=target_endpoint_arn,
                TargetEndpointArn=source_endpoint_arn,
                TableMappings=json.dumps(table_mapping),
            )
        # the message is very specific, so matching is tricky, e.g.
        #   ReplicationEngineType [id=47, name=kinesis, cdcSupported=Y, endpointType=TARGET,
        #             serviceType=AWS, externalName=Amazon Kinesis, rvn=1] endpoint must be of type SOURCE
        # snapshot.match("create_replication_invalid_endpoint", e.value.response)
        assert e.match("ReplicationEngineType .* must be of type SOURCE")
        assert e.value.response["Error"]["Code"] == "InvalidParameterValueException"
        assert e.value.response["ResponseMetadata"]["HTTPStatusCode"] == 400

        # test invalid replication instance
        with pytest.raises(ClientError) as e:
            aws_client.dms.create_replication_task(
                ReplicationTaskIdentifier=f"task-{short_uid()}",
                MigrationType="full-load",
                ReplicationInstanceArn=f"arn:{get_partition(region_name)}:dms:{region_name}:{account_id}:rep:repidentifier",
                SourceEndpointArn=source_endpoint_arn,
                TargetEndpointArn=target_endpoint_arn,
                TableMappings=json.dumps(table_mapping),
            )
        snapshot.match("create_replication_invalid_instance", e.value.response)

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(
        paths=[
            # TODO Add when starting task
            "$..ReplicationTask.RecoveryCheckpoint",
            "$..ReplicationTasks..RecoveryCheckpoint",
        ]
    )
    def test_replication_task_fail_table_does_not_exist(
        self, infrastructure, aws_client, snapshot, dms_create_replication_task
    ):
        snapshot.add_transformer(snapshot.transform.dms_api())
        snapshot.add_transformer(snapshot.transform.kinesis_api())
        outputs = infrastructure.get_stack_outputs(self.STACK_NAME)
        replication_instance_arn = outputs["ReplicationInstanceArn"]
        source_endpoint_arn = outputs["SourceEndpointMySQLArn"]
        target_endpoint_arn = outputs["TargetEndpointDefaultArn"]

        # create replication task
        table_mapping = {
            "rules": [
                {
                    "rule-type": "selection",
                    "rule-id": "1",
                    "rule-name": "rule1",
                    "object-locator": {"schema-name": DB_NAME, "table-name": "NotExistingTable"},
                    "rule-action": "include",
                }
            ]
        }
        replication_task = dms_create_replication_task(
            MigrationType="full-load",
            ReplicationInstanceArn=replication_instance_arn,
            SourceEndpointArn=source_endpoint_arn,
            TargetEndpointArn=target_endpoint_arn,
            TableMappings=json.dumps(table_mapping),
        )
        replication_task_arn = replication_task["ReplicationTask"]["ReplicationTaskArn"]

        snapshot.match("create-replication-task", replication_task)

        retry(
            lambda: assert_dms_replication_task_status(
                aws_client.dms, replication_task_arn, expected_status="ready"
            ),
            retries=150 if is_aws_cloud() else 10,
            sleep=5 if is_aws_cloud() else 1,
        )

        start_task = aws_client.dms.start_replication_task(
            ReplicationTaskArn=replication_task_arn, StartReplicationTaskType="start-replication"
        )
        snapshot.match("start_replication_task", start_task)

        result = retry(
            lambda: assert_dms_replication_task_status(
                aws_client.dms, replication_task_arn, expected_status="failed"
            ),
            retries=150 if is_aws_cloud() else 10,
            sleep=10 if is_aws_cloud() else 1,
        )
        snapshot.match("describe-replication-task-failed", result)

    @pytest.mark.parametrize(
        "database_type,target_type",
        [
            ("mysql", DEFAULT_TARGET_TYPE),
            ("mysql", NON_DEFAULT_TARGET_TYPE),
            ("mysql", UNFORMATTED_JSON_TARGET_TYPE),
            ("mariadb", DEFAULT_TARGET_TYPE),
            ("mariadb", NON_DEFAULT_TARGET_TYPE),
            ("mariadb", UNFORMATTED_JSON_TARGET_TYPE),
        ],
    )
    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(
        paths=[
            # TODO: AWS returns KMS for the kinesis records, we return NONE
            "$..EncryptionType",
            # TODO: AWS seems to add RecoveryCheckpoint (but only sometimes):
            "$..ReplicationTask.RecoveryCheckpoint",
            "$..ReplicationTasks..RecoveryCheckpoint",
            # TODO: Still a bit of work to be done with number type.
            #  Our implementation of rds appears to support Double type as Decimal which won't have the same normalization
            #  height is a Float (Decimal when json parsing) and aws doesn't appear to normalize before sending
            "$..Data.data.height",
        ]
    )
    def test_full_load_replication_task(
        self,
        infrastructure,
        aws_client,
        snapshot,
        cleanups,
        dms_create_replication_task,
        database_type,
        target_type,
    ):
        snapshot.add_transformer(snapshot.transform.dms_api())
        snapshot.add_transformer(snapshot.transform.kinesis_api())

        threshold_timestamp = time.time()
        outputs = infrastructure.get_stack_outputs(self.STACK_NAME)

        replication_instance_arn = outputs["ReplicationInstanceArn"]
        db_endpoint = (
            outputs["DbEndpointMySQL"] if database_type == "mysql" else outputs["DbEndpointMariadb"]
        )
        db_port = outputs["DbPortMySQL"] if database_type == "mysql" else outputs["DbPortMariadb"]
        source_endpoint_arn = (
            outputs["SourceEndpointMySQLArn"]
            if database_type == "mysql"
            else outputs["SourceEndpointMariadbArn"]
        )
        json_formatted = True
        target_endpoint_arn: str
        if target_type == NON_DEFAULT_TARGET_TYPE:
            target_endpoint_arn = outputs["TargetEndpointNonDefaultArn"]
        elif target_type == UNFORMATTED_JSON_TARGET_TYPE:
            target_endpoint_arn = outputs["TargetEndpointUnformattedJsonArn"]
            json_formatted = False
        else:
            target_endpoint_arn = outputs["TargetEndpointDefaultArn"]
        # create replication task
        table_mapping = {
            "rules": [
                {
                    "rule-type": "selection",
                    "rule-id": "1",
                    "rule-name": "rule1",
                    "object-locator": {"schema-name": DB_NAME, "table-name": "%"},
                    "rule-action": "include",
                },
                {
                    "rule-type": "selection",
                    "rule-id": "2",
                    "rule-name": "rule2",
                    "object-locator": {"schema-name": DB_NAME, "table-name": "books"},
                    "rule-action": "exclude",
                },
            ]
        }
        replication_task = dms_create_replication_task(
            MigrationType="full-load",
            ReplicationInstanceArn=replication_instance_arn,
            SourceEndpointArn=source_endpoint_arn,
            TargetEndpointArn=target_endpoint_arn,
            TableMappings=json.dumps(table_mapping),
        )
        replication_task_arn = replication_task["ReplicationTask"]["ReplicationTaskArn"]

        snapshot.match("create-replication-task", replication_task)
        stream_arn = outputs["KinesisStreamArn"]

        cleanups.append(
            lambda: _run_queries_on_mysql(
                host=db_endpoint,
                port=db_port,
                queries=[
                    "DROP TABLE IF EXISTS books;",
                    "DROP TABLE IF EXISTS authors;",
                    "DROP TABLE IF EXISTS accounts;",
                ],
            )
        )
        # setup source database
        queries = [
            f"USE {DB_NAME};",
            SQL_CREATE_ACCOUNTS_TABLE,
            SQL_CREATE_AUTHORS_TABLE,
            SQL_CREATE_BOOKS_TABLE,
        ]
        queries.extend(SQL_INSERT_ACCOUNTS_SAMPLE_DATA_LIST)
        queries.extend(SQL_INSERT_AUTHORS_SAMPLE_DATA_LIST)
        queries.append(SQL_INSERT_BOOK_SAMPLE_DATA)

        _run_queries_on_mysql(
            host=db_endpoint,
            port=db_port,
            queries=queries,
        )

        result = retry(
            lambda: assert_dms_replication_task_status(
                aws_client.dms,
                replication_task_arn,
                expected_status="ready",
                wait_for_task_stats=True,
            ),
            retries=100,
            sleep=5 if is_aws_cloud() else 1,
        )
        snapshot.match("describe-replication-tasks-ready", result)

        start_task = aws_client.dms.start_replication_task(
            ReplicationTaskArn=replication_task_arn, StartReplicationTaskType="start-replication"
        )
        snapshot.match("start_replication_task", start_task)

        result = retry(
            lambda: assert_dms_replication_task_status(
                aws_client.dms,
                replication_task_arn,
                expected_status="stopped",
                wait_for_task_stats=True,
            ),
            retries=100,
            sleep=30 if is_aws_cloud() else 1,
        )
        snapshot.match("describe-replication-tasks-stopped", result)
        res_describe_table_statistics = describe_table_statistics(
            aws_client.dms, replication_task_arn
        )
        snapshot.match("describe-table-statistics", res_describe_table_statistics)

        kinesis_records = retry(
            lambda: get_records_from_shard(
                aws_client.kinesis,
                stream_arn,
                threshold_timestamp=threshold_timestamp,
                # we expect 2 statements for create/delete each table (accounts + authors) = 4
                # plus the actual data: 6 for accounts + 5 for authors
                # => 4+6+5 = 15
                expected_count=15,
            ),
            retries=100,
            sleep=5 if is_aws_cloud() else 1,
        )
        formatted_records = transform_kinesis_data(
            kinesis_records, assert_exec=assert_json_formatting(json_formatted)
        )
        snapshot.match("kinesis-records", formatted_records)

    # TODO add test for full-load-and-cdc

    # TODO test before-image setting as table-mapping transformation
    # {"rule-type"="transformation"
    # "rule-action": "add-before-image-columns",
    # "before-image-def": {
    #     "column-filter": "all",  # test other values can be: pk-only / non-lob / all
    #     ## The value of column-prefix is prepended to a column name,
    #     # and the default value of column-prefix is BI_.
    #     # The value of column-suffix is appended to the column name, and the default is empty.
    #     # Don't set both column-prefix and column-suffix to empty strings.
    #     "column-prefix": "before-image-prefix",
    #     "column-suffix": "custom-suffix",
    # },

    @markers.aws.validated
    @pytest.mark.parametrize(
        "database_type, target_type",
        [("mysql", DEFAULT_TARGET_TYPE), ("mariadb", NON_DEFAULT_TARGET_TYPE)],
    )
    @markers.snapshot.skip_snapshot_verify(
        paths=[
            # TODO: these would appear and disappear between aws test runs.
            # FIXME: this potentially fails against aws because skip_verify is not skipped against AWS
            "$..RecoveryCheckpoint",
            # TODO: LS does not return the CdcStartPosition after the task is started
            "$..CdcStartPosition",
            # Logging is not supported on LS, different default value then for full-load
            "$..ReplicationTaskSettings.Logging",
            # TimeTravelSettings - not supported on LS, different default value then for full-load
            "$..ReplicationTaskSettings.TTSettings",
        ]
    )
    def test_cdc_replication_task_basic_responses(
        self,
        infrastructure,
        aws_client,
        snapshot,
        dms_create_replication_task,
        cleanups,
        database_type,
        target_type,
    ):
        snapshot.add_transformer(snapshot.transform.dms_api())
        snapshot.add_transformer(snapshot.transform.kinesis_api())
        outputs = infrastructure.get_stack_outputs(self.STACK_NAME)

        # maybe add more parameterized settings
        #  also think about using different types for before-image config (all, non-lob, pk-only)

        replication_instance_arn = outputs["ReplicationInstanceArn"]
        db_endpoint = (
            outputs["DbEndpointMySQL"] if database_type == "mysql" else outputs["DbEndpointMariadb"]
        )
        db_port = outputs["DbPortMySQL"] if database_type == "mysql" else outputs["DbPortMariadb"]
        source_endpoint_arn = (
            outputs["SourceEndpointMySQLArn"]
            if database_type == "mysql"
            else outputs["SourceEndpointMariadbArn"]
        )

        target_endpoint_arn: str
        if target_type == NON_DEFAULT_TARGET_TYPE:
            target_endpoint_arn = outputs["TargetEndpointNonDefaultArn"]
        else:
            target_endpoint_arn = outputs["TargetEndpointDefaultArn"]

        # configure the log-retention time  TODO we may need to implement this procedure on LS as well
        sql_config = [
            "SET autocommit=1;",
            "call mysql.rds_set_configuration('binlog retention hours', 24);",
        ]
        _run_queries_on_mysql(
            host=db_endpoint,
            port=db_port,
            queries=sql_config,
        )

        # create replication task
        replication_task_settings = {"Logging": {"EnableLogging": True}}

        # enable_before_image settings
        replication_task_settings["BeforeImageSettings"] = {
            "EnableBeforeImage": True,
            "FieldName": "before-image",
            "ColumnFilter": "all",  # pk-only will only report the e.g. "author_id": 1
        }

        replication_task = dms_create_replication_task(
            MigrationType="cdc",
            ReplicationInstanceArn=replication_instance_arn,
            SourceEndpointArn=source_endpoint_arn,
            TargetEndpointArn=target_endpoint_arn,
            TableMappings=json.dumps(DEFAULT_TABLE_MAPPING),
            ReplicationTaskSettings=json.dumps(replication_task_settings),
        )
        replication_task_arn = replication_task["ReplicationTask"]["ReplicationTaskArn"]
        snapshot.match("create-replication-task", replication_task)

        cleanups.append(
            lambda: _run_queries_on_mysql(
                host=db_endpoint,
                port=db_port,
                queries=[
                    "DROP TABLE IF EXISTS books;",
                    "DROP TABLE IF EXISTS authors;",
                    "DROP TABLE IF EXISTS accounts;",
                    "DROP TABLE IF EXISTS profiles;",
                    "DROP TABLE IF EXISTS test;",
                    "DROP TABLE IF EXISTS newtable;",
                ],
            )
        )
        # setup source database
        queries = [
            f"USE {DB_NAME};",
            SQL_CREATE_ACCOUNTS_TABLE,
            SQL_CREATE_AUTHORS_TABLE,
            SQL_CREATE_BOOKS_TABLE,
            "CREATE TABLE test (test_id INT AUTO_INCREMENT PRIMARY KEY, description VARCHAR(255) NOT NULL, alt_text VARCHAR(100));",
        ]
        queries.extend(SQL_INSERT_ACCOUNTS_SAMPLE_DATA_LIST)
        queries.extend(SQL_INSERT_AUTHORS_SAMPLE_DATA_LIST)
        queries.append(SQL_INSERT_BOOK_SAMPLE_DATA)

        _run_queries_on_mysql(
            host=db_endpoint,
            port=db_port,
            queries=queries,
        )

        result = retry(
            lambda: assert_dms_replication_task_status(
                aws_client.dms,
                replication_task_arn,
                expected_status="ready",
                wait_for_task_stats=True,
            ),
            retries=100,
            sleep=5 if is_aws_cloud() else 1,
        )
        snapshot.match("describe-replication-tasks-ready", result)

        start_task = aws_client.dms.start_replication_task(
            ReplicationTaskArn=replication_task_arn, StartReplicationTaskType="start-replication"
        )
        snapshot.match("start_replication_task", start_task)

        def wait_for_full_load():
            res = assert_dms_replication_task_status(
                aws_client.dms,
                replication_task_arn,
                expected_status="running",
                wait_for_task_stats=True,
            )
            assert (
                res["ReplicationTasks"][0]["ReplicationTaskStats"]["FullLoadProgressPercent"] == 100
            )
            return res

        running_task = retry(
            wait_for_full_load,
            retries=100,
            sleep=5 if is_aws_cloud() else 1,
        )
        snapshot.match("running-replication-task", running_task)

        stopping_task = aws_client.dms.stop_replication_task(
            ReplicationTaskArn=replication_task_arn
        )
        snapshot.match("stop-replication-task", stopping_task)

        def wait_for_stop_date():
            # AWS does not always populate this field immediately when setting the status to stop.
            # There is sometimes a delay
            res = assert_dms_replication_task_status(
                aws_client.dms,
                replication_task_arn,
                expected_status="stopped",
                wait_for_task_stats=True,
            )
            assert res["ReplicationTasks"][0]["ReplicationTaskStats"].get("StopDate")
            return res

        stopped = retry(
            wait_for_stop_date,
            retries=100,
            sleep=5 if is_aws_cloud() else 1,
        )
        snapshot.match("replication-task-status", stopped)

    @pytest.mark.parametrize("target_type", [DEFAULT_TARGET_TYPE, NON_DEFAULT_TARGET_TYPE])
    @markers.snapshot.skip_snapshot_verify(
        paths=[
            # TODO: AWS returns KMS by default, we return NONE
            "$..EncryptionType",
            # TODO: not really supported yet
            "$..metadata.prev-transaction-id",
            # TODO: reference counting goes wrong with LocalStack
            "$..metadata.stream-position",
            # TODO: counting of transaction record is wrong, not supported yet
            "$..metadata.transaction-record-id",
            "$..metadata.prev-transaction-record-id",
            # TODO: the binlog library does not resolve the ENUM value when `BINLOG_ROW_METADATA=FULL` is not set
            "$.kinesis-records[10].Data.data.favorite_color",
            # TODO: LS should add the following values
            "$.describe-replication-tasks..RecoveryCheckpoint",
            "$.describe-replication-tasks..CdcStartPosition",
        ]
    )
    @markers.aws.validated
    def test_cdc_load_replication_task_data_queries(
        self,
        infrastructure,
        aws_client,
        snapshot,
        target_type,
        setup_replication_databases,
        setup_replication_task,
    ):
        snapshot.add_transformer(snapshot.transform.dms_api())
        snapshot.add_transformer(snapshot.transform.kinesis_api())
        snapshot.add_transformer(snapshot.transform.key_value("stream-position"))
        snapshot.add_transformer(
            snapshot.transform.key_value(
                "prev-transaction-id", reference_replacement=False, value_replacement="12345678901"
            )
        )

        threshold_timestamp = time.time()
        outputs = infrastructure.get_stack_outputs(self.STACK_NAME)
        db_endpoint = setup_replication_databases()
        db_port = outputs["DbPortMariadb"]
        replication_task_arn = setup_replication_task(target_type=target_type)
        # partition key seems to be the id from the task-replication
        snapshot.match(
            "replication-task-id",
            {
                "ReplicationTaskArn": replication_task_arn,
            },
        )

        # more cdc-queries
        queries = [
            # data: insert -> test
            "INSERT INTO test (description) VALUES ('this is my first test'), ('this is a another test'), ('and something else');",
            # data: update -> books
            "UPDATE books SET genre = 'History and Science' where genre = 'History';",
            # data: update -> authors
            "UPDATE authors SET email = 'new.email@example.com', phone_number = '987-654-3210' WHERE author_id = 1;",
            # data: insert -> accounts
            """INSERT INTO accounts (name, age, birth_date, account_balance, is_active, signup_time, last_login, bio, profile_picture, favorite_color, height, weight)
                                    VALUES
                                    ('Alisa', 30, '1991-05-21', 1500.00, TRUE, '2021-01-08 09:00:00', '2021-03-10 08:00:00', 'Bio of Alisa', NULL, 'red', 1.77, 60);""",
            # data: delete (one data set) -> books
            "DELETE FROM books WHERE book_id = 2;",
            # data: delete  (two data sets) -> authors
            "DELETE FROM authors WHERE nationality LIKE '%ish';",
        ]
        expected = {
            "authors": {"AppliedUpdates": 1, "AppliedDeletes": 2},
            "test": {"AppliedInserts": 3},
            "accounts": {"AppliedInserts": 1},
            "books": {"AppliedUpdates": 1, "AppliedDeletes": 1},
        }

        for query in queries:
            _run_queries_on_mysql(
                host=db_endpoint,
                port=db_port,
                queries=[query],
            )

        def _check_expected_table_stats():
            table_stats = describe_table_statistics(aws_client.dms, replication_task_arn)[
                "TableStatistics"
            ]
            assert len(table_stats) == 4
            for stat in table_stats:
                assert dict_contains_subdict(stat, expected.get(stat["TableName"], {}))
            return table_stats

        retries = 100 if is_aws_cloud() else 25
        retry_sleep = 5 if is_aws_cloud() else 1

        res_describe_table_statistics = retry(
            _check_expected_table_stats,
            retries=retries,
            sleep=retry_sleep,
        )
        snapshot.match("describe-table-statistics", res_describe_table_statistics)

        describe_replication_task = retry(
            lambda: assert_dms_replication_task_status(
                aws_client.dms,
                replication_task_arn,
                expected_status="running",
                wait_for_task_stats=True,
            ),
            retries=retries,
            sleep=retry_sleep,
        )
        snapshot.match("describe-replication-tasks", describe_replication_task)

        expected_count = 9 + 5

        outputs = infrastructure.get_stack_outputs(self.STACK_NAME)
        stream_arn = outputs["KinesisStreamArn"]

        kinesis_records = retry(
            lambda: get_records_from_shard(
                aws_client.kinesis,
                stream_arn,
                threshold_timestamp=threshold_timestamp,
                expected_count=expected_count,  # it records
            ),
            retries=retries,
            sleep=retry_sleep,
        )
        formatted_records = transform_kinesis_data(
            kinesis_input=kinesis_records,
            assert_exec=assert_json_formatting(True),
            sorting_type="cdc",
        )
        snapshot.match("kinesis-records", formatted_records)

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(
        paths=[
            # TODO: AWS returns KMS by default, we return NONE
            "$..EncryptionType",
        ]
    )
    def test_cdc_load_replication_task_alter_table_queries(
        self,
        infrastructure,
        aws_client,
        snapshot,
        setup_replication_databases,
        setup_additional_tables,
        setup_replication_task,
    ):
        snapshot.add_transformer(snapshot.transform.dms_api())
        snapshot.add_transformer(snapshot.transform.kinesis_api())

        threshold_timestamp = time.time()

        outputs = infrastructure.get_stack_outputs(self.STACK_NAME)
        db_endpoint = setup_replication_databases()
        db_port = outputs["DbPortMariadb"]
        setup_additional_tables(db_endpoint=db_endpoint, db_port=db_port)
        replication_task_arn = setup_replication_task(target_type=NON_DEFAULT_TARGET_TYPE)
        # partition key seems to be the id from the task-replication
        snapshot.match(
            "replication-task-id",
            {
                "ReplicationTaskArn": replication_task_arn,
            },
        )

        # more cdc-queries
        queries = [
            # changing different columns of the same table led to inconsistencies in the reported events
            # so for now we create one table per changed column
            # control: column-type-change -> books
            "ALTER TABLE books MODIFY COLUMN isbn VARCHAR(30);",
            # control: drop-column -> accounts
            "ALTER TABLE accounts DROP COLUMN profile_picture;",
            # control: change-columns -> authors
            "ALTER TABLE authors CHANGE COLUMN phone_number phone VARCHAR(35);",
            # control: add-column with default value -> test
            "ALTER TABLE test ADD COLUMN is_tested BOOLEAN DEFAULT TRUE;",
            # control: add-column -> lions
            # used to be 2 statements (add then change to tinyint) but was not picked up as separates
            "ALTER TABLE lions ADD COLUMN is_dangerous TINYINT(1);",
            # control: change-columns -> pigeons
            "ALTER TABLE pigeons CHANGE COLUMN feather_count wingspan DOUBLE;",
        ]
        expected = {
            "books": {"AppliedDdls": 1},
            "accounts": {"AppliedDdls": 1},
            "authors": {"AppliedDdls": 1},
            "lions": {"AppliedDdls": 1},
            "pigeons": {"AppliedDdls": 1},
            "test": {"AppliedDdls": 1},
        }

        for query in queries:
            if is_aws_cloud():
                time.sleep(
                    2
                )  # The time or arrival for the alter events was indeterminate when they were executed without sleep
            _run_queries_on_mysql(
                host=db_endpoint,
                port=db_port,
                queries=[query],
            )

        def _check_expected_table_stats():
            table_stats = describe_table_statistics(aws_client.dms, replication_task_arn)[
                "TableStatistics"
            ]
            assert len(table_stats) == 8  # 8 tables are created, but we use only 7
            for stat in table_stats:
                assert dict_contains_subdict(stat, expected.get(stat["TableName"], {}))
            return table_stats

        res_describe_table_statistics = retry(
            _check_expected_table_stats,
            retries=100,
            sleep=5 if is_aws_cloud() else 1,
        )
        snapshot.match("describe-table-statistics", res_describe_table_statistics)

        expected_count = (
            1  # exception table, created by aws
            + 8  # the tables we create
            + 6  # the alter queries
        )

        outputs = infrastructure.get_stack_outputs(self.STACK_NAME)
        stream_arn = outputs["KinesisStreamArn"]

        kinesis_records = retry(
            lambda: get_records_from_shard(
                aws_client.kinesis,
                stream_arn,
                threshold_timestamp=threshold_timestamp,
                expected_count=expected_count,  # it records
            ),
            retries=20,
            sleep=5 if is_aws_cloud() else 1,
        )
        formatted_records = transform_kinesis_data(
            kinesis_input=kinesis_records,
            assert_exec=assert_json_formatting(True),
            sorting_type="cdc",
        )
        snapshot.match("kinesis-records", formatted_records)

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(
        paths=[
            # TODO: AWS returns KMS by default, we return NONE
            "$..EncryptionType",
        ]
    )
    def test_cdc_load_replication_task_misc_queries(
        self,
        infrastructure,
        aws_client,
        snapshot,
        setup_replication_databases,
        setup_replication_task,
    ):
        snapshot.add_transformer(snapshot.transform.dms_api())
        snapshot.add_transformer(snapshot.transform.kinesis_api())

        threshold_timestamp = time.time()

        outputs = infrastructure.get_stack_outputs(self.STACK_NAME)
        db_endpoint = setup_replication_databases()
        db_port = outputs["DbPortMariadb"]
        replication_task_arn = setup_replication_task(target_type=NON_DEFAULT_TARGET_TYPE)
        # partition key seems to be the id from the task-replication
        snapshot.match(
            "replication-task-id",
            {
                "ReplicationTaskArn": replication_task_arn,
            },
        )

        # more cdc-queries
        queries = [
            # TODO: possibly add more related test data
            "ALTER TABLE accounts MODIFY age INTEGER UNSIGNED;",
            # control: rename-table -> authors/writers
            "RENAME TABLE authors TO writers;",
            # control: drop-table -> test
            "DROP TABLE test;",
        ]
        expected = {"accounts": {"AppliedDdls": 1}}

        for query in queries:
            _run_queries_on_mysql(
                host=db_endpoint,
                port=db_port,
                queries=[query],
            )

        def _check_expected_table_stats():
            table_stats = describe_table_statistics(aws_client.dms, replication_task_arn)[
                "TableStatistics"
            ]
            assert len(table_stats) == 4
            for stat in table_stats:
                assert dict_contains_subdict(stat, expected.get(stat["TableName"], {}))
            return table_stats

        res_describe_table_statistics = retry(
            _check_expected_table_stats,
            retries=100 if is_aws_cloud() else 20,
            sleep=5 if is_aws_cloud() else 1,
        )
        snapshot.match("describe-table-statistics", res_describe_table_statistics)

        expected_count = (
            1  # aws table
            + 4  # our tables
            + 1
        )  # actions recorded, Drop and Rename do not seem to show

        outputs = infrastructure.get_stack_outputs(self.STACK_NAME)
        stream_arn = outputs["KinesisStreamArn"]

        kinesis_records = retry(
            lambda: get_records_from_shard(
                aws_client.kinesis,
                stream_arn,
                threshold_timestamp=threshold_timestamp,
                expected_count=expected_count,  # it records
            ),
            retries=20,
            sleep=5 if is_aws_cloud() else 1,
        )
        formatted_records = transform_kinesis_data(
            kinesis_input=kinesis_records,
            assert_exec=assert_json_formatting(True),
            sorting_type="cdc",
        )
        snapshot.match("kinesis-records", formatted_records)

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(
        paths=[
            # TODO: AWS returns KMS by default, we return NONE
            "$..EncryptionType",
            # we do not support returning the collation for columns with NATIONAL
            "$..national_char_type.collation-name",
            "$..national_varchar_type.collation-name",
            # JSON types for some reason returns a collation-name
            "$..json_type.collation-name",
        ]
    )
    def test_cdc_replication_task_data_types(
        self, infrastructure, aws_client, snapshot, cleanups, dms_create_replication_task
    ):
        # as the initial CDC and Full load table scan are using the same implementation (calling the internal
        # `information_schema.columns` table), we can only create a CDC test to verify data types.
        # Because RDS databases do not set `binlog-row-metadata=FULL`, our tests will only validate the data types
        # coming from internal tables, and not from the `BinLogStream` internal types.
        # but calling this test with a database with this setting would allow validating both

        mariadb_data_types = [
            "BIGINT",
            "BINARY",
            "BIT",
            "BLOB",
            "BOOL",
            "BOOLEAN",
            "CHAR",
            "VARCHAR(32)",  # equal to CHAR VARYING, CHARACTER VARYING, VARCHAR2, VARCHARACTER
            "LONGTEXT",
            "JSON",  # synonym of LONGTEXT
            "DATE",
            "DATETIME(6)",
            "DEC",
            "DECIMAL(10, 2)",
            "DOUBLE",
            "DOUBLE PRECISION",
            "ENUM('TEST', 'TEST2')",
            "FIXED",
            "FLOAT",
            "FLOAT4",
            "FLOAT8",
            "GEOMETRY",
            "GEOMETRYCOLLECTION",
            "INT",
            "INT1",
            "INT2",
            "INT3",
            "INT4",
            "INT8",
            "INTEGER",
            "LINESTRING",
            "LONGBLOB",
            "MEDIUMBLOB",
            "MEDIUMINT",
            "MEDIUMTEXT",  # equal to LONG, LONG CHAR VARYING, LONG CHARACTER VARYING, LONG VARCHAR, LONG VARCHARACTER
            "LONG",
            "MIDDLEINT",
            "MULTILINESTRING",
            "MULTIPOINT",
            "MULTIPOLYGON",
            "NATIONAL CHAR",
            "NATIONAL VARCHAR(32)",
            "POINT",
            "POLYGON",
            "REAL",
            "SERIAL",
            "SET('TEST', 'TEST2')",
            "SMALLINT",
            "SQL_TSI_YEAR",
            "TEXT",
            "TIME",
            "TIMESTAMP",
            "TINYBLOB",
            "TINYINT",
            "TINYTEXT",
            "VARBINARY(20)",
            "YEAR",
        ]

        def _get_db_col_name_from_type(col_type: str) -> str:
            col_name = col_type.partition("(")[0].lower()
            return f'{col_name.replace(" ", "_")}_type'

        test_table_name = "testtypes"
        snapshot.add_transformer(snapshot.transform.dms_api())
        snapshot.add_transformer(snapshot.transform.kinesis_api())
        snapshot.add_transformer(snapshot.transform.key_value("stream-position"))
        threshold_timestamp = time.time()
        outputs = infrastructure.get_stack_outputs(self.STACK_NAME)

        replication_instance_arn = outputs["ReplicationInstanceArn"]
        db_endpoint = outputs["DbEndpointMariadb"]
        db_port = outputs["DbPortMariadb"]
        source_endpoint_arn = outputs["SourceEndpointMariadbArn"]

        target_endpoint_arn: str = outputs["TargetEndpointNonDefaultArn"]

        sql_config = [
            "SET autocommit=1;",
            "call mysql.rds_set_configuration('binlog retention hours', 24);",
        ]
        _run_queries_on_mysql(
            host=db_endpoint,
            port=db_port,
            queries=sql_config,
        )

        cleanups.append(
            lambda: _run_queries_on_mysql(
                host=db_endpoint,
                port=db_port,
                queries=[
                    f"DROP TABLE IF EXISTS {test_table_name};",
                ],
            )
        )

        # setup source database with all the columns types
        # create one column for each type, with the column name <column_type>_type
        columns = ", ".join(
            f"{_get_db_col_name_from_type(col)} {col}" for col in mariadb_data_types
        )
        columns = f"(id INT PRIMARY KEY, name VARCHAR(255), {columns})"
        queries = [
            f"USE {DB_NAME};",
            f"DROP TABLE IF EXISTS {test_table_name};",
            f"CREATE TABLE {test_table_name} {columns};",
        ]

        _run_queries_on_mysql(
            host=db_endpoint,
            port=db_port,
            queries=queries,
        )

        # create replication task
        replication_task_settings = {
            "Logging": {"EnableLogging": True},
            "BeforeImageSettings": {
                "EnableBeforeImage": True,
                "FieldName": "before-image",
                "ColumnFilter": "all",
            },
        }

        replication_task = dms_create_replication_task(
            MigrationType="cdc",
            ReplicationInstanceArn=replication_instance_arn,
            SourceEndpointArn=source_endpoint_arn,
            TargetEndpointArn=target_endpoint_arn,
            TableMappings=json.dumps(DEFAULT_TABLE_MAPPING),
            ReplicationTaskSettings=json.dumps(replication_task_settings),
        )
        replication_task_arn = replication_task["ReplicationTask"]["ReplicationTaskArn"]

        # snapshotting the replication ID itself here, so that we can recognize it in the snapshots of the records, and
        # replace it accordingly, especially the last part of the task ARN, which is used.
        snapshot.match(
            "replication-task-id",
            {
                "ReplicationTaskIdentifier": replication_task["ReplicationTask"][
                    "ReplicationTaskIdentifier"
                ],
                "ReplicationTaskArn": replication_task["ReplicationTask"]["ReplicationTaskArn"],
            },
        )

        stream_arn = outputs["KinesisStreamArn"]

        retries = 100 if is_aws_cloud() else 10
        retry_sleep = 5 if is_aws_cloud() else 1

        retry(
            lambda: assert_dms_replication_task_status(
                aws_client.dms, replication_task_arn, expected_status="ready"
            ),
            retries=retries,
            sleep=retry_sleep,
        )

        aws_client.dms.start_replication_task(
            ReplicationTaskArn=replication_task_arn, StartReplicationTaskType="start-replication"
        )

        # now every change on the db should be added to kinesis
        # ensure the task is running before executing queries
        retry(
            lambda: assert_dms_replication_task_status(
                aws_client.dms, replication_task_arn, expected_status="running"
            ),
            retries=retries,
            sleep=retry_sleep,
        )

        # successful transaction
        cdc_test_queries = [
            # add to see all the columns created
            f"INSERT INTO {test_table_name} (id, name) VALUES (1, 'value1');",
            # add a query to see a ` columns` field before-image
            f"ALTER TABLE {test_table_name} ADD COLUMN added_col_test BOOLEAN DEFAULT TRUE;",
        ]
        _run_queries_on_mysql(
            host=db_endpoint,
            port=db_port,
            queries=cdc_test_queries,
        )
        expected_authors = {"AppliedInserts": 1, "AppliedDdls": 1}

        def _check_expected_table_stats():
            table_stats = aws_client.dms.describe_table_statistics(
                ReplicationTaskArn=replication_task_arn,
            )["TableStatistics"]
            assert len(table_stats) == 1
            assert table_stats[0]["TableName"] == test_table_name
            assert dict_contains_subdict(table_stats[0], expected_authors)
            return table_stats

        res_describe_table_statistics = retry(
            _check_expected_table_stats,
            retries=retries,
            sleep=retry_sleep,
        )
        snapshot.match("describe-table-statistics", res_describe_table_statistics)

        aws_client.dms.stop_replication_task(ReplicationTaskArn=replication_task_arn)

        # 1 insert data event, 1 ddl event, 1 table creation, 1 table for awsdms_apply_exceptions
        expected_count = 4

        kinesis_records = retry(
            lambda: get_records_from_shard(
                aws_client.kinesis,
                stream_arn,
                threshold_timestamp=threshold_timestamp,
                expected_count=expected_count,
            ),
            retries=20 if is_aws_cloud() else 3,
            sleep=retry_sleep,
        )
        formatted_records = transform_kinesis_data(
            kinesis_input=kinesis_records, assert_exec=assert_json_formatting(True)
        )
        snapshot.match("kinesis-records", formatted_records)
        retry(
            lambda: assert_dms_replication_task_status(
                aws_client.dms, replication_task_arn, expected_status="stopped"
            ),
            retries=retries,
            sleep=retry_sleep,
        )

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(
        paths=[
            # TODO: AWS returns KMS by default, we return NONE
            "$..EncryptionType",
        ]
    )
    def test_cdc_rollback_transaction(
        self,
        infrastructure,
        aws_client,
        snapshot,
        cleanups,
        dms_create_replication_task,
    ):
        snapshot.add_transformer(snapshot.transform.dms_api())
        snapshot.add_transformer(snapshot.transform.kinesis_api())
        snapshot.add_transformer(snapshot.transform.key_value("stream-position"))
        threshold_timestamp = time.time()
        outputs = infrastructure.get_stack_outputs(self.STACK_NAME)

        replication_instance_arn = outputs["ReplicationInstanceArn"]
        db_endpoint = outputs["DbEndpointMySQL"]
        db_port = outputs["DbPortMySQL"]

        source_endpoint_arn = outputs["SourceEndpointMySQLArn"]

        target_endpoint_arn: str = outputs["TargetEndpointNonDefaultArn"]

        sql_config = [
            "SET autocommit=1;",
            "call mysql.rds_set_configuration('binlog retention hours', 24);",
        ]
        _run_queries_on_mysql(
            host=db_endpoint,
            port=db_port,
            queries=sql_config,
        )

        # create replication task
        replication_task_settings = {
            "Logging": {"EnableLogging": True},
            "BeforeImageSettings": {
                "EnableBeforeImage": True,
                "FieldName": "before-image",
                "ColumnFilter": "all",
            },
        }

        replication_task = dms_create_replication_task(
            MigrationType="cdc",
            ReplicationInstanceArn=replication_instance_arn,
            SourceEndpointArn=source_endpoint_arn,
            TargetEndpointArn=target_endpoint_arn,
            TableMappings=json.dumps(DEFAULT_TABLE_MAPPING),
            ReplicationTaskSettings=json.dumps(replication_task_settings),
        )
        replication_task_arn = replication_task["ReplicationTask"]["ReplicationTaskArn"]

        # snapshotting the replication ID itself here, so that we can recognize it in the snapshots of the records, and
        # replace it accordingly, especially the last part of the task ARN, which is used.
        snapshot.match(
            "replication-task-id",
            {
                "ReplicationTaskIdentifier": replication_task["ReplicationTask"][
                    "ReplicationTaskIdentifier"
                ],
                "ReplicationTaskArn": replication_task["ReplicationTask"]["ReplicationTaskArn"],
            },
        )

        stream_arn = outputs["KinesisStreamArn"]

        cleanups.append(
            lambda: _run_queries_on_mysql(
                host=db_endpoint,
                port=db_port,
                queries=[
                    "DROP TABLE IF EXISTS authors;",
                ],
            )
        )

        # setup source database
        queries = [
            f"USE {DB_NAME};",
            SQL_CREATE_AUTHORS_TABLE,
        ]
        queries.extend(SQL_INSERT_AUTHORS_SAMPLE_DATA_LIST)

        _run_queries_on_mysql(
            host=db_endpoint,
            port=db_port,
            queries=queries,
        )
        retries = 100 if is_aws_cloud() else 10
        retry_sleep = 5 if is_aws_cloud() else 1

        retry(
            lambda: assert_dms_replication_task_status(
                aws_client.dms, replication_task_arn, expected_status="ready"
            ),
            retries=retries,
            sleep=retry_sleep,
        )

        aws_client.dms.start_replication_task(
            ReplicationTaskArn=replication_task_arn, StartReplicationTaskType="start-replication"
        )

        # now every change on the db should be added to kinesis
        # ensure the task is running before executing queries
        retry(
            lambda: assert_dms_replication_task_status(
                aws_client.dms, replication_task_arn, expected_status="running"
            ),
            retries=retries,
            sleep=retry_sleep,
        )

        # rollback transaction to test if it is recorded
        rollback_cdc_transaction_query = [
            "START TRANSACTION;",
            "DELETE FROM authors WHERE author_id = 1;",
            "ROLLBACK;",
        ]
        _run_queries_on_mysql(
            host=db_endpoint,
            port=db_port,
            queries=rollback_cdc_transaction_query,
        )

        # successful transaction
        cdc_test_queries = [
            "START TRANSACTION;",
            "UPDATE authors SET email = 'new.email@example.com', phone_number = '987-654-3210' WHERE author_id = 1;",
            "COMMIT;",
        ]
        _run_queries_on_mysql(
            host=db_endpoint,
            port=db_port,
            queries=cdc_test_queries,
        )
        expected_authors = {"AppliedUpdates": 1}

        def _check_expected_table_stats():
            table_stats = aws_client.dms.describe_table_statistics(
                ReplicationTaskArn=replication_task_arn,
            )["TableStatistics"]
            assert len(table_stats) == 1
            assert table_stats[0]["TableName"] == "authors"
            assert dict_contains_subdict(table_stats[0], expected_authors)
            return table_stats

        res_describe_table_statistics = retry(
            _check_expected_table_stats,
            retries=retries,
            sleep=retry_sleep,
        )
        snapshot.match("describe-table-statistics", res_describe_table_statistics)

        aws_client.dms.stop_replication_task(ReplicationTaskArn=replication_task_arn)

        # 1 update data event, 1 table creation, 1 table for awsdms_apply_exceptions
        expected_count = 3

        kinesis_records = retry(
            lambda: get_records_from_shard(
                aws_client.kinesis,
                stream_arn,
                threshold_timestamp=threshold_timestamp,
                expected_count=expected_count,
            ),
            retries=20 if is_aws_cloud() else 3,
            sleep=retry_sleep,
        )
        formatted_records = transform_kinesis_data(
            kinesis_input=kinesis_records, assert_exec=assert_json_formatting(True)
        )
        snapshot.match("kinesis-records", formatted_records)
        retry(
            lambda: assert_dms_replication_task_status(
                aws_client.dms, replication_task_arn, expected_status="stopped"
            ),
            retries=retries,
            sleep=retry_sleep,
        )

    @pytest.mark.parametrize(
        "database_type",
        [
            "mysql",
            "mariadb",
        ],
    )
    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(
        paths=[
            # TODO: AWS returns KMS by default, we return NONE
            "$..EncryptionType",
            # TODO: not really supported yet
            "$..metadata.prev-transaction-id",
            "$..metadata.prev-transaction-record-id",
        ]
    )
    def test_cdc_rename_change_column(
        self,
        infrastructure,
        aws_client,
        snapshot,
        cleanups,
        dms_create_replication_task,
        database_type,
    ):
        snapshot.add_transformer(snapshot.transform.dms_api())
        snapshot.add_transformer(snapshot.transform.kinesis_api())
        snapshot.add_transformer(snapshot.transform.key_value("stream-position"))
        snapshot.add_transformer(snapshot.transform.key_value("prev-transaction-id"))
        threshold_timestamp = time.time()
        outputs = infrastructure.get_stack_outputs(self.STACK_NAME)

        retries = 100 if is_aws_cloud() else 10
        retry_sleep = 5 if is_aws_cloud() else 1

        replication_instance_arn = outputs["ReplicationInstanceArn"]

        if database_type == "mysql":
            db_endpoint = outputs["DbEndpointMySQL"]
            db_port = outputs["DbPortMySQL"]
            source_endpoint_arn = outputs["SourceEndpointMySQLArn"]
        else:
            db_endpoint = outputs["DbEndpointMariadb"]
            db_port = outputs["DbPortMariadb"]
            source_endpoint_arn = outputs["SourceEndpointMariadbArn"]

        target_endpoint_arn: str = outputs["TargetEndpointNonDefaultArn"]

        sql_config = [
            "SET autocommit=1;",
            "call mysql.rds_set_configuration('binlog retention hours', 24);",
        ]
        _run_queries_on_mysql(
            host=db_endpoint,
            port=db_port,
            queries=sql_config,
        )

        # create replication task

        replication_task_settings = {
            "Logging": {"EnableLogging": True},
            "BeforeImageSettings": {
                "EnableBeforeImage": True,
                "FieldName": "before-image",
                "ColumnFilter": "all",
            },
        }

        replication_task = dms_create_replication_task(
            MigrationType="cdc",
            ReplicationInstanceArn=replication_instance_arn,
            SourceEndpointArn=source_endpoint_arn,
            TargetEndpointArn=target_endpoint_arn,
            TableMappings=json.dumps(DEFAULT_TABLE_MAPPING),
            ReplicationTaskSettings=json.dumps(replication_task_settings),
        )
        replication_task_arn = replication_task["ReplicationTask"]["ReplicationTaskArn"]
        # snapshotting the replication ID itself here, so that we can recognize it in the snapshots of the records, and
        # replace it accordingly, especially the last part of the task ARN, which is used.
        snapshot.match(
            "replication-task-id",
            {
                "ReplicationTaskIdentifier": replication_task["ReplicationTask"][
                    "ReplicationTaskIdentifier"
                ],
                "ReplicationTaskArn": replication_task["ReplicationTask"]["ReplicationTaskArn"],
            },
        )

        stream_arn = outputs["KinesisStreamArn"]

        cleanups.append(
            lambda: _run_queries_on_mysql(
                host=db_endpoint,
                port=db_port,
                queries=[
                    "DROP TABLE IF EXISTS test_users;",
                    "DROP TABLE IF EXISTS test_customers;",
                ],
            )
        )
        CREATE_TABLE_TEMPLATE = """CREATE TABLE {table_name} (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(50) NOT NULL,
                active INT
            );"""

        INSERT_DATA_TEMPLATE = (
            "INSERT INTO {table_name} (name, active) VALUES ('John', 1), ('Jane', 0), ('Alice', 1);"
        )

        # setup source database
        # we create two tables to get a clear result (sometimes DMS would combine the output otherwise)
        table_names = ["test_users", "test_customers"]
        queries = [
            f"USE {DB_NAME};",
            CREATE_TABLE_TEMPLATE.format(table_name=table_names[0]),
            CREATE_TABLE_TEMPLATE.format(table_name=table_names[1]),
            INSERT_DATA_TEMPLATE.format(table_name=table_names[0]),
            INSERT_DATA_TEMPLATE.format(table_name=table_names[1]),
        ]

        _run_queries_on_mysql(
            host=db_endpoint,
            port=db_port,
            queries=queries,
        )

        retry(
            lambda: assert_dms_replication_task_status(
                aws_client.dms, replication_task_arn, expected_status="ready"
            ),
            retries=retries,
            sleep=retry_sleep,
        )

        aws_client.dms.start_replication_task(
            ReplicationTaskArn=replication_task_arn, StartReplicationTaskType="start-replication"
        )

        retry(
            lambda: assert_dms_replication_task_status(
                aws_client.dms, replication_task_arn, expected_status="running"
            ),
            retries=retries,
            sleep=retry_sleep,
        )
        # run one modification on each table
        cdc_test_queries = [
            "ALTER TABLE test_users CHANGE COLUMN active active_user varchar(10);",
            "INSERT INTO test_users (name, active_user) VALUES ('Peter', '1');",
            "ALTER TABLE test_customers RENAME COLUMN name to full_name;",
            "INSERT INTO test_customers (full_name, active) VALUES ('Simon', '0');",
        ]

        for query in cdc_test_queries:
            _run_queries_on_mysql(
                host=db_endpoint,
                port=db_port,
                queries=[query],
            )

        expected_stat = {
            "AppliedDdls": 1,
            "AppliedInserts": 1,
        }

        def _check_expected_table_stats():
            table_stats = describe_table_statistics(aws_client.dms, replication_task_arn)[
                "TableStatistics"
            ]
            assert len(table_stats) == 2
            for table in table_stats:
                assert dict_contains_subdict(table, expected_stat)
            return table_stats

        res_describe_table_statistics = retry(
            _check_expected_table_stats,
            retries=retries,
            sleep=retry_sleep,
        )
        snapshot.match("describe-table-statistics", res_describe_table_statistics)

        aws_client.dms.stop_replication_task(ReplicationTaskArn=replication_task_arn)

        # for default setting (no control data) we expect:
        # - 2 insert data events
        # - 2 control data events
        # - 2 create table
        # - 1 table for awsdms_apply_exceptions
        expected_count = 7
        kinesis_records = retry(
            lambda: get_records_from_shard(
                aws_client.kinesis,
                stream_arn,
                threshold_timestamp=threshold_timestamp,
                expected_count=expected_count,
            ),
            retries=20 if is_aws_cloud() else 3,
            sleep=retry_sleep,
        )
        formatted_records = transform_kinesis_data(
            kinesis_input=kinesis_records,
            assert_exec=assert_json_formatting(True),
            sorting_type="cdc",
        )
        snapshot.match("kinesis-records", formatted_records)
        retry(
            lambda: assert_dms_replication_task_status(
                aws_client.dms, replication_task_arn, expected_status="stopped"
            ),
            retries=retries,
            sleep=retry_sleep,
        )

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(
        paths=[
            # TODO: AWS returns KMS by default, we return NONE
            "$..EncryptionType",
        ]
    )
    @pytest.mark.parametrize(
        "before_image_settings",
        [
            {
                "EnableBeforeImage": True,
                "FieldName": "custom-field",
                "ColumnFilter": "pk-only",
            },
            {"EnableBeforeImage": False},
        ],
        ids=["pk-only", "disabled"],
    )
    def test_cdc_before_image(
        self,
        infrastructure,
        aws_client,
        snapshot,
        cleanups,
        dms_create_replication_task,
        before_image_settings,
    ):
        snapshot.add_transformer(snapshot.transform.dms_api())
        snapshot.add_transformer(snapshot.transform.kinesis_api())
        snapshot.add_transformer(snapshot.transform.key_value("stream-position"))
        threshold_timestamp = time.time()
        outputs = infrastructure.get_stack_outputs(self.STACK_NAME)

        replication_instance_arn = outputs["ReplicationInstanceArn"]
        db_endpoint = outputs["DbEndpointMySQL"]
        db_port = outputs["DbPortMySQL"]

        source_endpoint_arn = outputs["SourceEndpointMySQLArn"]

        target_endpoint_arn: str = outputs["TargetEndpointNonDefaultArn"]

        sql_config = [
            "SET autocommit=1;",
            "call mysql.rds_set_configuration('binlog retention hours', 24);",
        ]
        _run_queries_on_mysql(
            host=db_endpoint,
            port=db_port,
            queries=sql_config,
        )

        # create replication task
        replication_task_settings = {
            "Logging": {"EnableLogging": True},
            "BeforeImageSettings": before_image_settings,
        }

        replication_task = dms_create_replication_task(
            MigrationType="cdc",
            ReplicationInstanceArn=replication_instance_arn,
            SourceEndpointArn=source_endpoint_arn,
            TargetEndpointArn=target_endpoint_arn,
            TableMappings=json.dumps(DEFAULT_TABLE_MAPPING),
            ReplicationTaskSettings=json.dumps(replication_task_settings),
        )
        replication_task_arn = replication_task["ReplicationTask"]["ReplicationTaskArn"]

        # snapshotting the replication ID itself here, so that we can recognize it in the snapshots of the records, and
        # replace it accordingly, especially the last part of the task ARN, which is used.
        snapshot.match(
            "replication-task-id",
            {
                "ReplicationTaskIdentifier": replication_task["ReplicationTask"][
                    "ReplicationTaskIdentifier"
                ],
                "ReplicationTaskArn": replication_task["ReplicationTask"]["ReplicationTaskArn"],
            },
        )

        stream_arn = outputs["KinesisStreamArn"]

        cleanups.append(
            lambda: _run_queries_on_mysql(
                host=db_endpoint,
                port=db_port,
                queries=[
                    "DROP TABLE IF EXISTS authors;",
                ],
            )
        )

        # setup source database
        queries = [
            f"USE {DB_NAME};",
            SQL_CREATE_AUTHORS_TABLE,
        ]
        queries.extend(SQL_INSERT_AUTHORS_SAMPLE_DATA_LIST)

        _run_queries_on_mysql(
            host=db_endpoint,
            port=db_port,
            queries=queries,
        )
        retries = 100 if is_aws_cloud() else 10
        retry_sleep = 5 if is_aws_cloud() else 1

        retry(
            lambda: assert_dms_replication_task_status(
                aws_client.dms, replication_task_arn, expected_status="ready"
            ),
            retries=retries,
            sleep=retry_sleep,
        )

        aws_client.dms.start_replication_task(
            ReplicationTaskArn=replication_task_arn, StartReplicationTaskType="start-replication"
        )

        # now every change on the db should be added to kinesis
        # ensure the task is running before executing queries
        retry(
            lambda: assert_dms_replication_task_status(
                aws_client.dms, replication_task_arn, expected_status="running"
            ),
            retries=retries,
            sleep=retry_sleep,
        )

        # successful transaction
        cdc_test_queries = [
            "UPDATE authors SET email = 'new.email@example.com', phone_number = '987-654-3210' WHERE author_id = 1;",
        ]
        _run_queries_on_mysql(
            host=db_endpoint,
            port=db_port,
            queries=cdc_test_queries,
        )
        expected_authors = {"AppliedUpdates": 1}

        def _check_expected_table_stats():
            table_stats = aws_client.dms.describe_table_statistics(
                ReplicationTaskArn=replication_task_arn,
            )["TableStatistics"]
            assert len(table_stats) == 1
            assert table_stats[0]["TableName"] == "authors"
            assert dict_contains_subdict(table_stats[0], expected_authors)
            return table_stats

        res_describe_table_statistics = retry(
            _check_expected_table_stats,
            retries=retries,
            sleep=retry_sleep,
        )
        snapshot.match("describe-table-statistics", res_describe_table_statistics)

        aws_client.dms.stop_replication_task(ReplicationTaskArn=replication_task_arn)

        # 1 update data event, 1 table creation, 1 table for awsdms_apply_exceptions
        expected_count = 3

        kinesis_records = retry(
            lambda: get_records_from_shard(
                aws_client.kinesis,
                stream_arn,
                threshold_timestamp=threshold_timestamp,
                expected_count=expected_count,
            ),
            retries=20 if is_aws_cloud() else 3,
            sleep=retry_sleep,
        )
        formatted_records = transform_kinesis_data(
            kinesis_input=kinesis_records, assert_exec=assert_json_formatting(True)
        )
        snapshot.match("kinesis-records", formatted_records)
        retry(
            lambda: assert_dms_replication_task_status(
                aws_client.dms, replication_task_arn, expected_status="stopped"
            ),
            retries=retries,
            sleep=retry_sleep,
        )

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(
        paths=[
            # TODO: AWS returns KMS by default, we return NONE
            "$..EncryptionType",
        ]
    )
    def test_cdc_table_rules_filter(
        self,
        infrastructure,
        aws_client,
        snapshot,
        cleanups,
        dms_create_replication_task,
    ):
        snapshot.add_transformer(snapshot.transform.dms_api())
        snapshot.add_transformer(snapshot.transform.kinesis_api())
        snapshot.add_transformer(snapshot.transform.key_value("stream-position"))
        threshold_timestamp = time.time()
        outputs = infrastructure.get_stack_outputs(self.STACK_NAME)

        replication_instance_arn = outputs["ReplicationInstanceArn"]
        db_endpoint = outputs["DbEndpointMySQL"]
        db_port = outputs["DbPortMySQL"]

        source_endpoint_arn = outputs["SourceEndpointMySQLArn"]
        target_endpoint_arn: str = outputs["TargetEndpointNonDefaultArn"]

        sql_config = [
            "SET autocommit=1;",
            "call mysql.rds_set_configuration('binlog retention hours', 24);",
        ]
        _run_queries_on_mysql(
            host=db_endpoint,
            port=db_port,
            queries=sql_config,
        )

        # create replication task
        replication_task_settings = {
            "Logging": {"EnableLogging": True},
            "BeforeImageSettings": {
                "EnableBeforeImage": True,
                "FieldName": "before-image",
                "ColumnFilter": "all",
            },
        }
        table_mapping = {
            "rules": [
                {
                    "rule-type": "selection",
                    "rule-id": "1",
                    "rule-name": "rule1",
                    "object-locator": {"schema-name": DB_NAME, "table-name": "%"},
                    "rule-action": "include",
                },
                {
                    "rule-type": "selection",
                    "rule-id": "2",
                    "rule-name": "rule2",
                    "object-locator": {"schema-name": DB_NAME, "table-name": "books"},
                    "rule-action": "exclude",
                },
            ]
        }

        replication_task = dms_create_replication_task(
            MigrationType="cdc",
            ReplicationInstanceArn=replication_instance_arn,
            SourceEndpointArn=source_endpoint_arn,
            TargetEndpointArn=target_endpoint_arn,
            TableMappings=json.dumps(table_mapping),
            ReplicationTaskSettings=json.dumps(replication_task_settings),
        )
        replication_task_arn = replication_task["ReplicationTask"]["ReplicationTaskArn"]

        # snapshotting the replication ID itself here, so that we can recognize it in the snapshots of the records, and
        # replace it accordingly, especially the last part of the task ARN, which is used.
        snapshot.match(
            "replication-task-id",
            {
                "ReplicationTaskIdentifier": replication_task["ReplicationTask"][
                    "ReplicationTaskIdentifier"
                ],
                "ReplicationTaskArn": replication_task["ReplicationTask"]["ReplicationTaskArn"],
            },
        )

        stream_arn = outputs["KinesisStreamArn"]

        cleanups.append(
            lambda: _run_queries_on_mysql(
                host=db_endpoint,
                port=db_port,
                queries=[
                    "DROP TABLE IF EXISTS books;",
                    "DROP TABLE IF EXISTS authors;",
                ],
            )
        )

        # setup source database
        queries = [
            "DROP TABLE IF EXISTS books;",
            "DROP TABLE IF EXISTS authors;",
            f"USE {DB_NAME};",
            SQL_CREATE_AUTHORS_TABLE,
            SQL_CREATE_BOOKS_TABLE,
            *SQL_INSERT_AUTHORS_SAMPLE_DATA_LIST,
            SQL_INSERT_BOOK_SAMPLE_DATA,
        ]

        _run_queries_on_mysql(
            host=db_endpoint,
            port=db_port,
            queries=queries,
        )
        retries = 100 if is_aws_cloud() else 10
        retry_sleep = 5 if is_aws_cloud() else 1

        retry(
            lambda: assert_dms_replication_task_status(
                aws_client.dms, replication_task_arn, expected_status="ready"
            ),
            retries=retries,
            sleep=retry_sleep,
        )

        aws_client.dms.start_replication_task(
            ReplicationTaskArn=replication_task_arn, StartReplicationTaskType="start-replication"
        )

        # now every change on the db should be added to kinesis
        # ensure the task is running before executing queries
        retry(
            lambda: assert_dms_replication_task_status(
                aws_client.dms, replication_task_arn, expected_status="running"
            ),
            retries=retries,
            sleep=retry_sleep,
        )

        # successful transaction
        cdc_test_queries = [
            "UPDATE authors SET email = 'new.email@example.com', phone_number = '987-654-3210' WHERE author_id = 1;",
            "UPDATE books SET genre = 'History and Science' where genre = 'History';",
            "ALTER TABLE books MODIFY COLUMN isbn VARCHAR(30);",
        ]
        _run_queries_on_mysql(
            host=db_endpoint,
            port=db_port,
            queries=cdc_test_queries,
        )
        expected_authors = {"AppliedUpdates": 1}

        def _check_expected_table_stats():
            table_stats = aws_client.dms.describe_table_statistics(
                ReplicationTaskArn=replication_task_arn,
            )["TableStatistics"]
            assert len(table_stats) == 1
            assert table_stats[0]["TableName"] == "authors"
            assert dict_contains_subdict(table_stats[0], expected_authors)
            return table_stats

        res_describe_table_statistics = retry(
            _check_expected_table_stats,
            retries=retries,
            sleep=retry_sleep,
        )
        snapshot.match("describe-table-statistics", res_describe_table_statistics)

        aws_client.dms.stop_replication_task(ReplicationTaskArn=replication_task_arn)

        # 1 update data event, 1 table creation, 1 table for awsdms_apply_exceptions
        # all events about `books` should not be forwarded
        expected_count = 3

        kinesis_records = retry(
            lambda: get_records_from_shard(
                aws_client.kinesis,
                stream_arn,
                threshold_timestamp=threshold_timestamp,
                expected_count=expected_count,
            ),
            retries=20 if is_aws_cloud() else 3,
            sleep=retry_sleep,
        )
        formatted_records = transform_kinesis_data(
            kinesis_input=kinesis_records, assert_exec=assert_json_formatting(True)
        )
        snapshot.match("kinesis-records", formatted_records)
        retry(
            lambda: assert_dms_replication_task_status(
                aws_client.dms, replication_task_arn, expected_status="stopped"
            ),
            retries=retries,
            sleep=retry_sleep,
        )


def _run_queries_on_mysql(
    host: str,
    queries: list[str],
    database: str = DB_NAME,
    user: str = USERNAME,
    password: str = USER_PWD,
    port: int = None,
):
    return run_queries_on_mysql(host, queries, database, user, password, port)


DEFAULT_TABLE_MAPPING = {
    "rules": [
        {
            "rule-type": "selection",
            "rule-id": "1",
            "rule-name": "rule1",
            "object-locator": {"schema-name": DB_NAME, "table-name": "%"},
            "rule-action": "include",
        }
    ]
}


SQL_CREATE_ACCOUNTS_TABLE = """CREATE TABLE accounts (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    age TINYINT UNSIGNED,
                    birth_date DATE,
                    account_balance DECIMAL(10, 2),
                    is_active BOOLEAN,
                    signup_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login DATETIME,
                    bio TEXT,
                    profile_picture BLOB,
                    favorite_color ENUM('red', 'green', 'blue'),
                    height FLOAT,
                    weight DOUBLE
                );"""
SQL_INSERT_ACCOUNTS_SAMPLE_DATA_LIST = [
    """INSERT INTO accounts
(name, age, birth_date, account_balance, is_active, signup_time, last_login, bio, profile_picture, favorite_color, height, weight)
VALUES
('Alice', 30, '1991-05-21', 1500.00, TRUE, '2021-01-08 09:00:00', '2021-03-10 08:00:00', 'Bio of Alice', NULL, 'red', 1.70, 60.5);""",
    """INSERT INTO accounts
(name, age, birth_date, account_balance, is_active, signup_time, last_login, bio, profile_picture, favorite_color, height, weight)
VALUES
('Bob', NULL, '1988-09-15', 2200.75, FALSE, '2021-02-15 10:00:00', '2021-04-12 07:30:00', NULL, NULL, 'green', 1.85, NULL);""",
    """INSERT INTO accounts
(name, age, birth_date, account_balance, is_active, signup_time, last_login, bio, profile_picture, favorite_color, height, weight)
VALUES
('Charlie', 25, NULL, NULL, TRUE, '2021-03-20 11:30:00', NULL, 'Bio of Charlie', NULL, 'blue', 1.65, 70.0);""",
    """INSERT INTO accounts
(name, age, birth_date, account_balance, is_active, signup_time, last_login, bio, profile_picture, favorite_color, height, weight)
VALUES
('Diana', 42, '1979-12-03', 3200.50, FALSE, '2021-04-25 12:45:00', '2021-05-15 09:15:00', 'Bio of Diana', NULL, 'red', NULL, 62.0);""",
    """INSERT INTO accounts
(name, age, birth_date, account_balance, is_active, signup_time, last_login, bio, profile_picture, favorite_color, height, weight)
VALUES
('Ethan', 35, '1986-07-22', 1800.00, TRUE, '2021-05-30 14:00:00', '2021-06-20 10:20:00', NULL, NULL, 'green', 1.75, 75.5);""",
    """INSERT INTO accounts
(name, age, birth_date, account_balance, is_active, signup_time, last_login, bio, profile_picture, favorite_color, height, weight)
VALUES
('Fiona', 28, '1993-02-17', 2600.25, TRUE, '2021-06-05 15:30:00', '2021-07-25 11:45:00', 'Bio of Fiona', NULL, 'blue', 1.60, 55.0);
""",
]
SQL_CREATE_AUTHORS_TABLE = """CREATE TABLE authors (
    author_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    date_of_birth DATE,
    nationality VARCHAR(50),
    biography TEXT,
    email VARCHAR(255),
    phone_number VARCHAR(20),
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);"""

SQL_INSERT_AUTHORS_SAMPLE_DATA_LIST = [
    """INSERT INTO authors (first_name, last_name, date_of_birth, nationality, biography, email, phone_number)
VALUES
('John', 'Doe', '1980-01-01', 'American', 'Biography of John Doe.', 'john.doe@example.com', '123-456-7890');""",
    """INSERT INTO authors (first_name, last_name, date_of_birth, nationality, biography, email, phone_number)
VALUES
('Jane', 'Smith', '1975-05-15', 'British', 'Biography of Jane Smith.', 'jane.smith@example.com', '123-456-7891');""",
    """INSERT INTO authors (first_name, last_name, date_of_birth, nationality, biography, email, phone_number)
VALUES
('Alice', 'Johnson', '1990-07-30', 'Canadian', 'Biography of Alice Johnson.', 'alice.johnson@example.com', '123-456-7892');""",
    """INSERT INTO authors (first_name, last_name, date_of_birth, nationality, biography, email, phone_number)
VALUES
('Bob', 'Brown', '1985-10-20', 'Australian', 'Biography of Bob Brown.', 'bob.brown@example.com', '123-456-7893');""",
    """INSERT INTO authors (first_name, last_name, date_of_birth, nationality, biography, email, phone_number)
VALUES
('Emily', 'Davis', '1992-03-22', 'Irish', 'Biography of Emily Davis.', 'emily.davis@example.com', '123-456-7894');""",
]
SQL_CREATE_BOOKS_TABLE = """CREATE TABLE books (
    book_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    author_id INT,
    publish_date DATE,
    isbn VARCHAR(20),
    genre VARCHAR(100),
    page_count INT,
    publisher VARCHAR(100),
    language VARCHAR(50),
    available_copies INT,
    total_copies INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (author_id) REFERENCES authors(author_id)
);
"""
SQL_INSERT_BOOK_SAMPLE_DATA = """INSERT INTO books (title, author_id, publish_date, isbn, genre, page_count, publisher, language, available_copies, total_copies)
VALUES
('The Great Adventure', 1, '2020-06-01', '978-3-16-148410-0', 'Adventure', 300, 'Adventure Press', 'English', 10, 20),
('Cooking with Jane', 2, '2018-11-15', '978-1-23-456789-1', 'Cookbook', 250, 'Foodie Books', 'English', 5, 10),
('History of the World', 3, '2019-03-21', '978-0-14-312779-6', 'History', 500, 'Global Publishers', 'English', 8, 15),
('Journey to the Stars', 1, '2021-04-10', '978-0-11-322456-7', 'Science Fiction', 350, 'SciFi Universe', 'English', 12, 25),
('Gardening Basics', 4, '2017-05-05', '978-0-12-345678-9', 'Gardening', 200, 'Green Thumb', 'English', 6, 12);"""
