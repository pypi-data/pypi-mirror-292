import json
import time

import aws_cdk as cdk
import aws_cdk.aws_dms as dms
import aws_cdk.aws_ec2 as ec2
import aws_cdk.aws_iam as iam
import aws_cdk.aws_kinesis as kinesis
import aws_cdk.aws_s3 as s3
import pytest
from localstack.pro.core.aws.api.dms import S3Settings
from localstack.testing.aws.util import is_aws_cloud
from localstack.testing.pytest import markers
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
    transform_kinesis_data,
)

RETRIES = 100 if is_aws_cloud() else 10
RETRY_SLEEP = 5 if is_aws_cloud() else 1
SLEEP_BEFORE = 10 if is_aws_cloud() else 1

SCHEMA_NAME = "hr"
TABLE_NAME = "employee"
BUCKET_FOLDER = "sourceData"
CHANGE_DATA = "changedata"

SOURCE_CSV_EMPLOYEE_SAMPLE_DATA = """101,Smith,Bob,2014-06-04,New York
102,Smith,Bob,2015-10-08,Los Angeles
103,Smith,Bob,2017-03-13,Dallas
104,Smith,Bob,2017-03-13,Dallas"""

SOURCE_CSV_DEPARTMENT_SAMPLE_DATA = """201,HR
202,IT
203,Finance"""

SOURCE_CSV_PROJECT_SAMPLE_DATA = """301,Project1,Description1
302,Project2,Description2
303,Project3,Description3"""

CDC_FILE_SAMPLE_DATA = """INSERT,employee,hr,101,Smith,Bob,2014-06-04,New York
UPDATE,employee,hr,101,Smith,Bob,2015-10-08,Los Angeles
UPDATE,employee,hr,101,Smith,Bob,2017-03-13,Dallas
DELETE,employee,hr,101,Smith,Bob,2017-03-13,Dallas"""

DEFAULT_TABLE_MAPPING = {
    "rules": [
        {
            "rule-type": "selection",
            "rule-id": "1",
            "rule-name": "rule1",
            "object-locator": {"schema-name": SCHEMA_NAME, "table-name": "%"},
            "rule-action": "include",
        }
    ]
}


class TestDmsScenario:
    """
    Used to run tests for the S3 source and kinesis target

    There are different definitions for the target, as it can be configured with different settings, that modify the actual
    output.
    """

    STACK_NAME = "DmsS3KinesisStack"

    @pytest.fixture(scope="class")
    def infrastructure(self, infrastructure_setup):
        infra = infrastructure_setup("DmsS3Kinesis", force_synth=True)

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
                    "arn:aws:iam::aws:policy/service-role/AmazonDMSVPCManagementRole",
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
                    "arn:aws:iam::aws:policy/service-role/AmazonDMSCloudWatchLogsRole",
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

        # s3 bucket
        bucket = s3.Bucket(
            stack,
            "S3Bucket",
            bucket_name="source-bucket-s3-kinesis-dms",
            removal_policy=cdk.RemovalPolicy.DESTROY,  # required since default value is RETAIN
        )
        bucket.grant_read_write(dms_assume_role)

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

        table_structure = {
            "TableCount": "1",
            "Tables": [
                {
                    "TableName": TABLE_NAME,
                    "TablePath": f"{SCHEMA_NAME}/{TABLE_NAME}/",
                    "TableOwner": SCHEMA_NAME,
                    "TableColumns": [
                        {
                            "ColumnName": "Id",
                            "ColumnType": "INT8",
                            "ColumnNullable": "false",
                            "ColumnIsPk": "true",
                        },
                        {"ColumnName": "LastName", "ColumnType": "STRING", "ColumnLength": "20"},
                        {"ColumnName": "FirstName", "ColumnType": "STRING", "ColumnLength": "30"},
                        {"ColumnName": "HireDate", "ColumnType": "DATETIME"},
                        {
                            "ColumnName": "OfficeLocation",
                            "ColumnType": "STRING",
                            "ColumnLength": "20",
                        },
                    ],
                    "TableColumnsTotal": "5",
                }
            ],
        }

        # Source Endpoint
        source_endpoint_s3 = dms.CfnEndpoint(
            stack,
            "source-s3",
            endpoint_type="source",
            engine_name="s3",
            s3_settings=dms.CfnEndpoint.S3SettingsProperty(
                bucket_name=bucket.bucket_name,
                external_table_definition=json.dumps(table_structure),
                bucket_folder=BUCKET_FOLDER,
                service_access_role_arn=dms_assume_role.role_arn,
                cdc_path=CHANGE_DATA,
            ),
        )

        # Multiple Tables Source Endpoint
        table_structure_multiple_tables = {
            "TableCount": "3",
            "Tables": [
                {
                    "TableName": TABLE_NAME,
                    "TablePath": f"{SCHEMA_NAME}/{TABLE_NAME}/",
                    "TableOwner": SCHEMA_NAME,
                    "TableColumns": [
                        {
                            "ColumnName": "Id",
                            "ColumnType": "INT8",
                            "ColumnNullable": "false",
                            "ColumnIsPk": "true",
                        },
                        {"ColumnName": "LastName", "ColumnType": "STRING", "ColumnLength": "20"},
                        {"ColumnName": "FirstName", "ColumnType": "STRING", "ColumnLength": "30"},
                        {"ColumnName": "HireDate", "ColumnType": "DATETIME"},
                        {
                            "ColumnName": "OfficeLocation",
                            "ColumnType": "STRING",
                            "ColumnLength": "20",
                        },
                    ],
                    "TableColumnsTotal": "5",
                },
                {
                    "TableName": "department",
                    "TablePath": f"{SCHEMA_NAME}/department/",
                    "TableOwner": SCHEMA_NAME,
                    "TableColumns": [
                        {
                            "ColumnName": "Id",
                            "ColumnType": "INT8",
                            "ColumnNullable": "false",
                            "ColumnIsPk": "true",
                        },
                        {"ColumnName": "Name", "ColumnType": "STRING", "ColumnLength": "50"},
                    ],
                    "TableColumnsTotal": "2",
                },
                {
                    "TableName": "project",
                    "TablePath": f"{SCHEMA_NAME}/project/",
                    "TableOwner": SCHEMA_NAME,
                    "TableColumns": [
                        {
                            "ColumnName": "Id",
                            "ColumnType": "INT8",
                            "ColumnNullable": "false",
                            "ColumnIsPk": "true",
                        },
                        {"ColumnName": "Name", "ColumnType": "STRING", "ColumnLength": "50"},
                        {
                            "ColumnName": "Description",
                            "ColumnType": "STRING",
                            "ColumnLength": "100",
                        },
                    ],
                    "TableColumnsTotal": "3",
                },
            ],
        }
        source_endpoint_s3_multiple_tables = dms.CfnEndpoint(
            stack,
            "source-s3-multiple-tables",
            endpoint_type="source",
            engine_name="s3",
            s3_settings=dms.CfnEndpoint.S3SettingsProperty(
                bucket_name=bucket.bucket_name,
                external_table_definition=json.dumps(table_structure_multiple_tables),
                bucket_folder=BUCKET_FOLDER,
                service_access_role_arn=dms_assume_role.role_arn,
                cdc_path=CHANGE_DATA,
            ),
        )

        # s3 endpoint without total count param
        table_structure_without_total_count = {
            "TableCount": "1",
            "Tables": [
                {
                    "TableName": TABLE_NAME,
                    "TablePath": f"{SCHEMA_NAME}/{TABLE_NAME}/",
                    "TableOwner": SCHEMA_NAME,
                    "TableColumns": [
                        {
                            "ColumnName": "Id",
                            "ColumnType": "INT8",
                            "ColumnNullable": "false",
                            "ColumnIsPk": "true",
                        },
                        {"ColumnName": "LastName", "ColumnType": "STRING", "ColumnLength": "20"},
                        {"ColumnName": "FirstName", "ColumnType": "STRING", "ColumnLength": "30"},
                        {"ColumnName": "HireDate", "ColumnType": "DATETIME"},
                        {
                            "ColumnName": "OfficeLocation",
                            "ColumnType": "STRING",
                            "ColumnLength": "20",
                        },
                    ],
                }
            ],
        }
        source_endpoint_s3_without_total_count = dms.CfnEndpoint(
            stack,
            "source-s3-without-total-count",
            endpoint_type="source",
            engine_name="s3",
            s3_settings=dms.CfnEndpoint.S3SettingsProperty(
                bucket_name=bucket.bucket_name,
                external_table_definition=json.dumps(table_structure_without_total_count),
                bucket_folder=BUCKET_FOLDER,
                service_access_role_arn=dms_assume_role.role_arn,
                cdc_path=CHANGE_DATA,
            ),
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

        cdk.CfnOutput(stack, "KinesisStreamArn", value=target_stream.stream_arn)
        cdk.CfnOutput(stack, "S3BucketArn", value=bucket.bucket_arn)
        cdk.CfnOutput(stack, "S3BucketName", value=bucket.bucket_name)
        cdk.CfnOutput(stack, "S3BucketDomain", value=bucket.bucket_domain_name)
        cdk.CfnOutput(stack, "ReplicationInstanceArn", value=replication_instance.ref)
        cdk.CfnOutput(stack, "SourceEndpointS3Arn", value=source_endpoint_s3.ref)
        cdk.CfnOutput(
            stack, "SourceEndpointS3MultipleTablesArn", value=source_endpoint_s3_multiple_tables.ref
        )
        cdk.CfnOutput(
            stack,
            "SourceEndpointWithoutCountS3Arn",
            value=source_endpoint_s3_without_total_count.ref,
        )
        cdk.CfnOutput(stack, "TargetEndpointDefaultArn", value=target_endpoint.ref)
        cdk.CfnOutput(
            stack, "TargetEndpointNonDefaultArn", value=target_endpoint_non_default_settings.ref
        )
        cdk.CfnOutput(
            stack, "TargetEndpointUnformattedJsonArn", value=target_endpoint_json_unformatted.ref
        )
        cdk.CfnOutput(stack, "SuperRoleArn", value=dms_assume_role.role_arn)
        with infra.provisioner(skip_teardown=False) as prov:
            yield prov

    @pytest.fixture
    def setup_replication_task(self, dms_create_replication_task, infrastructure, aws_client):
        replication_task_arn = ""
        outputs = infrastructure.get_stack_outputs(self.STACK_NAME)

        def _setup_replication_task(**kwargs):
            nonlocal replication_task_arn
            if "target_type" not in kwargs:
                kwargs["target_type"] = "default"
            target_type = kwargs["target_type"]
            replication_instance_arn = outputs["ReplicationInstanceArn"]
            source_endpoint_arn = outputs["SourceEndpointS3Arn"]

            target_endpoint_arn: str
            if target_type == NON_DEFAULT_TARGET_TYPE:
                target_endpoint_arn = outputs["TargetEndpointNonDefaultArn"]
            elif target_type == UNFORMATTED_JSON_TARGET_TYPE:
                target_endpoint_arn = outputs["TargetEndpointUnformattedJsonArn"]
            else:
                target_endpoint_arn = outputs["TargetEndpointDefaultArn"]

            if "multiple_tables" in kwargs and kwargs["multiple_tables"]:
                source_endpoint_arn = outputs["SourceEndpointS3MultipleTablesArn"]

            replication_task = dms_create_replication_task(
                MigrationType="cdc",
                ReplicationInstanceArn=replication_instance_arn,
                SourceEndpointArn=source_endpoint_arn,
                TargetEndpointArn=target_endpoint_arn,
                TableMappings=json.dumps(DEFAULT_TABLE_MAPPING),
            )

            replication_task_arn = replication_task["ReplicationTask"]["ReplicationTaskArn"]

            # wait for task to be ready
            retry(
                lambda: assert_dms_replication_task_status(
                    aws_client.dms, replication_task_arn, expected_status="ready"
                ),
                retries=RETRIES,
                sleep=RETRY_SLEEP,
                sleep_before=SLEEP_BEFORE,
            )

            aws_client.dms.start_replication_task(
                ReplicationTaskArn=replication_task_arn,
                StartReplicationTaskType="start-replication",
            )

            # wait for task to be running
            retry(
                lambda: assert_dms_replication_task_status(
                    aws_client.dms, replication_task_arn, expected_status="running"
                ),
                retries=RETRIES,
                sleep=RETRY_SLEEP,
                sleep_before=SLEEP_BEFORE,
            )

            return replication_task_arn

        yield _setup_replication_task

        # cleanup
        aws_client.dms.stop_replication_task(ReplicationTaskArn=replication_task_arn)
        retry(
            lambda: assert_dms_replication_task_status(
                aws_client.dms, replication_task_arn, expected_status="stopped"
            ),
            retries=RETRIES,
            sleep=RETRY_SLEEP,
            sleep_before=SLEEP_BEFORE,
        )
        aws_client.dms.delete_replication_task(ReplicationTaskArn=replication_task_arn)

    @markers.aws.validated
    def test_describe_endpoints(self, infrastructure, aws_client, snapshot):
        snapshot.add_transformer(snapshot.transform.dms_api())
        outputs = infrastructure.get_stack_outputs(self.STACK_NAME)
        source_endpoint_arn = outputs["SourceEndpointS3Arn"]
        target_endpoint_arn = outputs["TargetEndpointDefaultArn"]
        target_endpoint_unformatted_arn = outputs["TargetEndpointUnformattedJsonArn"]
        target_endpoint_non_default_arn = outputs["TargetEndpointNonDefaultArn"]

        source_endpoint = aws_client.dms.describe_endpoints(
            Filters=[{"Name": "endpoint-arn", "Values": [source_endpoint_arn]}]
        )
        snapshot.match("describe-source-endpoint-s3", source_endpoint)

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

    @markers.aws.validated
    def test_s3_invalid_s3_source(self, infrastructure, aws_client, snapshot, dms_create_endpoint):
        snapshot.add_transformer(snapshot.transform.dms_api())
        outputs = infrastructure.get_stack_outputs(self.STACK_NAME)
        super_role_arn = outputs.get("SuperRoleArn")
        replication_instance_arn = outputs["ReplicationInstanceArn"]

        endpoint_identifier = f"test-endpoint-{short_uid()}"
        bucket_name = f"not-existent-bucket-{short_uid()}"
        snapshot.add_transformer(snapshot.transform.regex(bucket_name, "<bucket_name>"))
        table_definition = {
            "TableCount": "1",
            "Tables": [
                {
                    "TableName": TABLE_NAME,
                    "TablePath": f"{SCHEMA_NAME}/{TABLE_NAME}/",
                    "TableOwner": SCHEMA_NAME,
                    "TableColumns": [
                        {
                            "ColumnName": "Id",
                            "ColumnType": "INT8",
                            "ColumnNullable": "false",
                            "ColumnIsPk": "true",
                        },
                        {"ColumnName": "Name", "ColumnType": "STRING", "ColumnLength": "50"},
                    ],
                    "TableColumnsTotal": "2",
                }
            ],
        }
        s3_endpoint = dms_create_endpoint(
            EndpointIdentifier=endpoint_identifier,
            EndpointType="source",
            EngineName="s3",
            S3Settings=S3Settings(
                BucketName=bucket_name,
                ExternalTableDefinition=json.dumps(table_definition),
                ServiceAccessRoleArn=super_role_arn,
            ),
        )
        snapshot.match("create-tmp-s3-endpoint", s3_endpoint)
        s3_endpoint_arn = s3_endpoint["EndpointArn"]

        # the bucket doesn't exist so we expect the test-connection to fail
        start_test_connection = aws_client.dms.test_connection(
            ReplicationInstanceArn=replication_instance_arn, EndpointArn=s3_endpoint_arn
        )
        snapshot.match("s3-start-test-connection", start_test_connection)

        def _verify_status():
            connection = aws_client.dms.describe_connections(
                Filters=[{"Name": "endpoint-arn", "Values": [s3_endpoint_arn]}]
            ).get("Connections")[0]
            assert connection["Status"] == "failed"
            return connection

        result = retry(
            _verify_status,
            retries=30,
            sleep=10 if is_aws_cloud() else 1,
        )
        snapshot.match("s3-describe-connection-failed", result)

    @markers.aws.validated
    def test_s3_test_connection(self, infrastructure, aws_client, snapshot):
        snapshot.add_transformer(snapshot.transform.dms_api())
        outputs = infrastructure.get_stack_outputs(self.STACK_NAME)
        source_endpoint_arn = outputs["SourceEndpointS3Arn"]
        replication_instance_arn = outputs["ReplicationInstanceArn"]

        connections = aws_client.dms.describe_connections(
            Filters=[{"Name": "endpoint-arn", "Values": [source_endpoint_arn]}]
        ).get("Connections")
        if not connections or not connections[0].get("Status") == "successful":
            # this will raise an exception if the status is "testing"
            aws_client.dms.test_connection(
                ReplicationInstanceArn=replication_instance_arn, EndpointArn=source_endpoint_arn
            )

        def _verify_status():
            connection = aws_client.dms.describe_connections(
                Filters=[{"Name": "endpoint-arn", "Values": [source_endpoint_arn]}]
            ).get("Connections")[0]
            assert connection["Status"] == "successful"
            return connection

        result = retry(
            _verify_status,
            retries=30,
            sleep=10 if is_aws_cloud() else 1,
        )
        snapshot.match("s3-describe-connection", result)

    @markers.snapshot.skip_snapshot_verify(
        paths=[
            # TODO: Add support for RecoveryTimeout in replication task settings, re-run tests for mariadb use case
            "$..RecoveryTimeout",
        ]
    )
    @markers.aws.validated
    def test_run_task_no_match_external_table_definition(
        self, infrastructure, aws_client, dms_create_replication_task, snapshot
    ):
        """tests a table mapping with a schema-name that doesn't match the original table-defintion
        expects to fail as no table can be selected
        """
        snapshot.add_transformer(snapshot.transform.dms_api())
        outputs = infrastructure.get_stack_outputs(self.STACK_NAME)
        source_endpoint_arn = outputs["SourceEndpointS3Arn"]
        target_endpoint_arn = outputs["TargetEndpointDefaultArn"]
        replication_instance_arn = outputs["ReplicationInstanceArn"]
        schema_name = "my-schema-name"

        table_mapping = {
            "rules": [
                {
                    "rule-type": "selection",
                    "rule-id": "1",
                    "rule-name": "rule1",
                    "object-locator": {"schema-name": schema_name, "table-name": "%"},
                    "rule-action": "include",
                }
            ]
        }
        task = dms_create_replication_task(
            MigrationType="full-load",
            ReplicationInstanceArn=replication_instance_arn,
            SourceEndpointArn=source_endpoint_arn,
            TargetEndpointArn=target_endpoint_arn,
            TableMappings=json.dumps(table_mapping),
        )
        snapshot.match("create-s3-full-load-task", task)
        replication_task_arn = task["ReplicationTask"]["ReplicationTaskArn"]
        retry(
            lambda: assert_dms_replication_task_status(
                aws_client.dms, replication_task_arn, expected_status="ready"
            ),
            retries=RETRIES,
            sleep=RETRY_SLEEP,
            sleep_before=SLEEP_BEFORE,
        )

        start_task = aws_client.dms.start_replication_task(
            ReplicationTaskArn=replication_task_arn, StartReplicationTaskType="start-replication"
        )
        snapshot.match("start_replication_task", start_task)

        result = retry(
            lambda: assert_dms_replication_task_status(
                aws_client.dms, replication_task_arn, expected_status="failed"
            ),
            retries=RETRIES,
            sleep=RETRY_SLEEP,
            sleep_before=SLEEP_BEFORE,
        )

        snapshot.match("replication-task-failed", result)

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(
        paths=[
            # TODO: AWS returns KMS by default, we return NONE
            "$..EncryptionType",
        ]
    )
    def test_run_task_external_table_definition_invalid_format_csv(
        self, infrastructure, aws_client, dms_create_replication_task, snapshot, cleanups
    ):
        """tests a table mapping with a valid schema-name
        but the csv file doesn't match the ExternalTableDefinition
        """
        snapshot.add_transformer(snapshot.transform.dms_api())
        snapshot.add_transformer(snapshot.transform.kinesis_api())

        outputs = infrastructure.get_stack_outputs(self.STACK_NAME)
        source_endpoint_arn = outputs["SourceEndpointS3Arn"]
        target_endpoint_arn = outputs["TargetEndpointDefaultArn"]
        replication_instance_arn = outputs["ReplicationInstanceArn"]
        bucket = outputs["S3BucketName"]
        stream_arn = outputs["KinesisStreamArn"]
        threshold_timestamp = time.time()
        test_file1 = f"{BUCKET_FOLDER}/{SCHEMA_NAME}/{TABLE_NAME}/invalid.csv"
        # first entry is valid
        # second one contains null values; by default no null values are allowed as it's not specified in the
        # table definition - we expect to fail after reading 1 entry
        content = """100,Test,Bob,2015-10-08,Los Angeles
101,Smith,Bob,,
102,Smith,121
test,something,"""
        aws_client.s3.put_object(Bucket=bucket, Key=test_file1, Body=content)
        cleanups.append(lambda: aws_client.s3.delete_object(Bucket=bucket, Key=test_file1))

        test_file2 = f"{BUCKET_FOLDER}/{SCHEMA_NAME}/{TABLE_NAME}/valid-file.csv"
        content = """101,Test,Smith,2015-10-08,Dallas"""

        aws_client.s3.put_object(Bucket=bucket, Key=test_file2, Body=content)
        cleanups.append(lambda: aws_client.s3.delete_object(Bucket=bucket, Key=test_file2))

        task = dms_create_replication_task(
            MigrationType="full-load",
            ReplicationInstanceArn=replication_instance_arn,
            SourceEndpointArn=source_endpoint_arn,
            TargetEndpointArn=target_endpoint_arn,
            TableMappings=json.dumps(DEFAULT_TABLE_MAPPING),
        )
        replication_task_arn = task["ReplicationTask"]["ReplicationTaskArn"]
        retry(
            lambda: assert_dms_replication_task_status(
                aws_client.dms, replication_task_arn, expected_status="ready"
            ),
            retries=RETRIES,
            sleep=RETRY_SLEEP,
            sleep_before=SLEEP_BEFORE,
        )

        aws_client.dms.start_replication_task(
            ReplicationTaskArn=replication_task_arn, StartReplicationTaskType="start-replication"
        )

        retry(
            lambda: assert_dms_replication_task_status(
                aws_client.dms, replication_task_arn, expected_status="stopped"
            ),
            retries=RETRIES,
            sleep=RETRY_SLEEP,
            sleep_before=SLEEP_BEFORE,
        )

        res_describe_table_statistics = describe_table_statistics(
            aws_client.dms, replication_task_arn
        )
        snapshot.match("describe-table-statistics", res_describe_table_statistics)

        kinesis_records = retry(
            lambda: get_records_from_shard(
                aws_client.kinesis,
                stream_arn,
                threshold_timestamp=threshold_timestamp,
                # we expect 2 statements for create and delete for table employee
                # plus the actual data: 1 row then it should fail
                # => 2+1=3
                expected_count=3,
            ),
            retries=100,
            sleep=5 if is_aws_cloud() else 1,
        )
        formatted_records = transform_kinesis_data(
            kinesis_records, assert_exec=assert_json_formatting(True)
        )
        snapshot.match("kinesis-records", formatted_records)

    @markers.aws.validated
    @pytest.mark.parametrize("migration_type", ["full-load", "cdc"])
    @markers.snapshot.skip_snapshot_verify(
        paths=[
            # TODO: AWS returns KMS by default, we return NONE
            "$..EncryptionType",
            # TODO: Add support for RecoveryTimeout in replication task settings, re-run tests for mariadb use case
            "$..RecoveryTimeout",
            # TimeTravelSettings and RecoveryCheckpoint not supported on LS
            "$..ReplicationTaskSettings.TTSettings",
            "$..ReplicationTasks..RecoveryCheckpoint",
        ]
    )
    def test_no_csv_file(
        self,
        infrastructure,
        migration_type,
        dms_create_replication_task,
        aws_client,
        snapshot,
    ):
        snapshot.add_transformer(snapshot.transform.dms_api())
        snapshot.add_transformer(snapshot.transform.kinesis_api())

        threshold_timestamp = time.time()

        outputs = infrastructure.get_stack_outputs(self.STACK_NAME)
        source_endpoint_arn = outputs["SourceEndpointS3Arn"]
        target_endpoint_arn = outputs["TargetEndpointDefaultArn"]
        replication_instance_arn = outputs["ReplicationInstanceArn"]
        stream_arn = outputs["KinesisStreamArn"]

        replication_task = dms_create_replication_task(
            MigrationType=migration_type,
            ReplicationInstanceArn=replication_instance_arn,
            SourceEndpointArn=source_endpoint_arn,
            TargetEndpointArn=target_endpoint_arn,
            TableMappings=json.dumps(DEFAULT_TABLE_MAPPING),
        )

        snapshot.match("replication-task", replication_task)
        replication_task_arn = replication_task["ReplicationTask"]["ReplicationTaskArn"]

        retry(
            lambda: assert_dms_replication_task_status(
                aws_client.dms,
                replication_task_arn,
                expected_status="ready",
            ),
            retries=RETRIES,
            sleep=RETRY_SLEEP,
            sleep_before=SLEEP_BEFORE,
        )

        start_task = aws_client.dms.start_replication_task(
            ReplicationTaskArn=replication_task_arn, StartReplicationTaskType="start-replication"
        )
        snapshot.match("start_replication_task", start_task)

        def wait_replication_task():
            res = assert_dms_replication_task_status(
                aws_client.dms,
                replication_task_arn,
                expected_status="stopped" if migration_type == "full-load" else "running",
                wait_for_task_stats=True,
            )
            assert (
                res["ReplicationTasks"][0]["ReplicationTaskStats"]["FullLoadProgressPercent"] == 100
            )
            return res

        result = retry(
            wait_replication_task,
            retries=RETRIES,
            sleep=RETRY_SLEEP,
            sleep_before=SLEEP_BEFORE,
        )

        snapshot.match("describe-replication-task", result)

        if migration_type == "cdc":
            stopping_task = aws_client.dms.stop_replication_task(
                ReplicationTaskArn=replication_task_arn
            )
            snapshot.match("stop-replication-task", stopping_task)

            def wait_for_stop_date():
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
                retries=RETRIES,
                sleep=RETRY_SLEEP,
                sleep_before=SLEEP_BEFORE,
            )
            snapshot.match("stopped-replication-task", stopped)

        else:
            # we expect two events to be sent for kinesis
            # for create and drop table
            kinesis_records = retry(
                lambda: get_records_from_shard(
                    aws_client.kinesis,
                    stream_arn,
                    threshold_timestamp=threshold_timestamp,
                    expected_count=2,
                ),
                retries=100,
                sleep=5 if is_aws_cloud() else 1,
            )
            formatted_records = transform_kinesis_data(
                kinesis_records, assert_exec=assert_json_formatting(True)
            )
            snapshot.match("kinesis-records", formatted_records)

    @markers.aws.validated
    @pytest.mark.parametrize(
        "target_type",
        [
            DEFAULT_TARGET_TYPE,
            NON_DEFAULT_TARGET_TYPE,
            UNFORMATTED_JSON_TARGET_TYPE,
        ],
    )
    @markers.snapshot.skip_snapshot_verify(
        paths=[
            # TODO: AWS returns KMS by default, we return NONE
            "$..EncryptionType",
        ]
    )
    def test_full_load_replication_task(
        self,
        infrastructure,
        target_type,
        dms_create_replication_task,
        aws_client,
        snapshot,
        cleanups,
    ):
        snapshot.add_transformer(snapshot.transform.dms_api())
        snapshot.add_transformer(snapshot.transform.kinesis_api())

        threshold_timestamp = time.time()

        outputs = infrastructure.get_stack_outputs(self.STACK_NAME)
        source_endpoint_arn = outputs["SourceEndpointS3Arn"]
        replication_instance_arn = outputs["ReplicationInstanceArn"]
        bucket = outputs["S3BucketName"]
        stream_arn = outputs["KinesisStreamArn"]
        test_file = f"{BUCKET_FOLDER}/{SCHEMA_NAME}/{TABLE_NAME}/example.csv"

        json_formatted = True
        target_endpoint_arn: str
        if target_type == NON_DEFAULT_TARGET_TYPE:
            target_endpoint_arn = outputs["TargetEndpointNonDefaultArn"]
        elif target_type == UNFORMATTED_JSON_TARGET_TYPE:
            target_endpoint_arn = outputs["TargetEndpointUnformattedJsonArn"]
            json_formatted = False
        else:
            target_endpoint_arn = outputs["TargetEndpointDefaultArn"]

        aws_client.s3.put_object(Bucket=bucket, Key=test_file, Body=SOURCE_CSV_EMPLOYEE_SAMPLE_DATA)
        cleanups.append(lambda: aws_client.s3.delete_object(Bucket=bucket, Key=test_file))

        replication_task = dms_create_replication_task(
            MigrationType="full-load",
            ReplicationInstanceArn=replication_instance_arn,
            SourceEndpointArn=source_endpoint_arn,
            TargetEndpointArn=target_endpoint_arn,
            TableMappings=json.dumps(DEFAULT_TABLE_MAPPING),
        )

        replication_task_arn = replication_task["ReplicationTask"]["ReplicationTaskArn"]

        retry(
            lambda: assert_dms_replication_task_status(
                aws_client.dms, replication_task_arn, expected_status="ready"
            ),
            retries=RETRIES,
            sleep=RETRY_SLEEP,
            sleep_before=SLEEP_BEFORE,
        )

        aws_client.dms.start_replication_task(
            ReplicationTaskArn=replication_task_arn, StartReplicationTaskType="start-replication"
        )

        retry(
            lambda: assert_dms_replication_task_status(
                aws_client.dms,
                replication_task_arn,
                expected_status="stopped",
                wait_for_task_stats=True,
            ),
            retries=RETRIES,
            sleep=RETRY_SLEEP,
            sleep_before=SLEEP_BEFORE,
        )

        res_describe_table_statistics = describe_table_statistics(
            aws_client.dms, replication_task_arn
        )
        snapshot.match("describe-table-statistics", res_describe_table_statistics)

        kinesis_records = retry(
            lambda: get_records_from_shard(
                aws_client.kinesis,
                stream_arn,
                threshold_timestamp=threshold_timestamp,
                # we expect 2 statements for create and delete for table employee
                # plus the actual data: 4 rows
                # => 2+4=6
                expected_count=6,
            ),
            retries=100,
            sleep=5 if is_aws_cloud() else 1,
        )
        formatted_records = transform_kinesis_data(
            kinesis_records, assert_exec=assert_json_formatting(json_formatted)
        )
        snapshot.match("kinesis-records", formatted_records)

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(
        paths=[
            # TODO: Add support for RecoveryTimeout in replication task settings, re-run tests for mariadb use case
            "$..RecoveryTimeout",
            # TimeTravelSettings and RecoveryCheckpoint- not supported on LS
            "$..ReplicationTaskSettings.TTSettings",
            "$..RecoveryCheckpoint",
        ]
    )
    @pytest.mark.parametrize(
        "target_type",
        [
            DEFAULT_TARGET_TYPE,
            NON_DEFAULT_TARGET_TYPE,
            UNFORMATTED_JSON_TARGET_TYPE,
        ],
    )
    def test_cdc_replication_task_basic_response(
        self,
        infrastructure,
        target_type,
        dms_create_replication_task,
        aws_client,
        snapshot,
        cleanups,
    ):
        snapshot.add_transformer(snapshot.transform.dms_api())
        snapshot.add_transformer(snapshot.transform.kinesis_api())

        outputs = infrastructure.get_stack_outputs(self.STACK_NAME)
        source_endpoint_arn = outputs["SourceEndpointS3Arn"]
        replication_instance_arn = outputs["ReplicationInstanceArn"]

        target_endpoint_arn: str
        if target_type == NON_DEFAULT_TARGET_TYPE:
            target_endpoint_arn = outputs["TargetEndpointNonDefaultArn"]
        elif target_type == UNFORMATTED_JSON_TARGET_TYPE:
            target_endpoint_arn = outputs["TargetEndpointUnformattedJsonArn"]
        else:
            target_endpoint_arn = outputs["TargetEndpointDefaultArn"]

        replication_task = dms_create_replication_task(
            MigrationType="cdc",
            ReplicationInstanceArn=replication_instance_arn,
            SourceEndpointArn=source_endpoint_arn,
            TargetEndpointArn=target_endpoint_arn,
            TableMappings=json.dumps(DEFAULT_TABLE_MAPPING),
        )

        replication_task_arn = replication_task["ReplicationTask"]["ReplicationTaskArn"]
        snapshot.match("create-replication-task", replication_task)

        result = retry(
            lambda: assert_dms_replication_task_status(
                aws_client.dms,
                replication_task_arn,
                expected_status="ready",
                wait_for_task_stats=True,
            ),
            retries=RETRIES,
            sleep=RETRY_SLEEP,
            sleep_before=SLEEP_BEFORE,
        )
        snapshot.match("describe-replication-tasks-ready", result)

        start_task = aws_client.dms.start_replication_task(
            ReplicationTaskArn=replication_task_arn, StartReplicationTaskType="start-replication"
        )
        snapshot.match("start-replication-task", start_task)

        def wait_for_task():
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
            wait_for_task,
            retries=RETRIES,
            sleep=RETRY_SLEEP,
            sleep_before=SLEEP_BEFORE,
        )
        snapshot.match("running-replication-task", running_task)

        stopping_task = aws_client.dms.stop_replication_task(
            ReplicationTaskArn=replication_task_arn
        )
        snapshot.match("stop-replication-task", stopping_task)

        def wait_for_stop_date():
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
            retries=RETRIES,
            sleep=RETRY_SLEEP,
            sleep_before=SLEEP_BEFORE,
        )
        snapshot.match("replication-task-status", stopped)

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(
        paths=[
            # TODO: AWS returns KMS by default, we return NONE
            "$..EncryptionType",
        ]
    )
    @pytest.mark.parametrize(
        "target_type",
        [
            DEFAULT_TARGET_TYPE,
            NON_DEFAULT_TARGET_TYPE,
            UNFORMATTED_JSON_TARGET_TYPE,
        ],
    )
    def test_cdc_replication_task_cdc_files(
        self,
        infrastructure,
        target_type,
        setup_replication_task,
        aws_client,
        snapshot,
        cleanups,
    ):
        snapshot.add_transformer(snapshot.transform.dms_api())
        snapshot.add_transformer(snapshot.transform.kinesis_api())

        threshold_timestamp = time.time()
        outputs = infrastructure.get_stack_outputs(self.STACK_NAME)
        stream_arn = outputs["KinesisStreamArn"]
        bucket = outputs["S3BucketName"]
        replication_task_arn = setup_replication_task(target_type=target_type)

        snapshot.match(
            "replication-task-id",
            {
                "ReplicationTaskArn": replication_task_arn,
            },
        )

        # add a cdc file
        cdc_file = f"{BUCKET_FOLDER}/{CHANGE_DATA}/cdc0000000001.csv"

        aws_client.s3.put_object(Bucket=bucket, Key=cdc_file, Body=CDC_FILE_SAMPLE_DATA)
        cleanups.append(lambda: aws_client.s3.delete_object(Bucket=bucket, Key=cdc_file))

        expected_employees = {"AppliedInserts": 1, "AppliedDeletes": 1, "AppliedUpdates": 2}

        def _check_expected_table_stats():
            table_stats = describe_table_statistics(aws_client.dms, replication_task_arn)[
                "TableStatistics"
            ]
            assert len(table_stats) == 1
            assert table_stats[0]["TableName"] == "employee"
            assert dict_contains_subdict(table_stats[0], expected_employees)
            return table_stats

        res_describe_table_statistics = retry(
            _check_expected_table_stats,
            retries=RETRIES,
            sleep=RETRY_SLEEP,
            sleep_before=SLEEP_BEFORE,
        )
        snapshot.match("describe-table-statistics", res_describe_table_statistics)

        retry(
            lambda: assert_dms_replication_task_status(
                aws_client.dms,
                replication_task_arn,
                expected_status="running",
                wait_for_task_stats=True,
            ),
            retries=RETRIES,
            sleep=RETRY_SLEEP,
            sleep_before=SLEEP_BEFORE,
        )

        # 1 create table, 1 insert, 2 updates, 1 delete, 1 table for awsdms_apply_exceptions
        expected_count = 6

        kinesis_records = retry(
            lambda: get_records_from_shard(
                aws_client.kinesis,
                stream_arn,
                threshold_timestamp=threshold_timestamp,
                expected_count=expected_count,
            ),
            retries=RETRIES,
            sleep=RETRY_SLEEP,
            sleep_before=SLEEP_BEFORE,
        )

        json_formatted = True
        if target_type == UNFORMATTED_JSON_TARGET_TYPE:
            json_formatted = False

        formatted_records = transform_kinesis_data(
            kinesis_input=kinesis_records,
            assert_exec=assert_json_formatting(json_formatted),
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
    @pytest.mark.parametrize(
        "target_type",
        [
            DEFAULT_TARGET_TYPE,
            NON_DEFAULT_TARGET_TYPE,
            UNFORMATTED_JSON_TARGET_TYPE,
        ],
    )
    def test_cdc_replication_task_cdc_multiple_files(
        self,
        infrastructure,
        target_type,
        setup_replication_task,
        aws_client,
        snapshot,
        cleanups,
    ):
        snapshot.add_transformer(snapshot.transform.dms_api())
        snapshot.add_transformer(snapshot.transform.kinesis_api())

        threshold_timestamp = time.time()
        outputs = infrastructure.get_stack_outputs(self.STACK_NAME)
        stream_arn = outputs["KinesisStreamArn"]
        bucket = outputs["S3BucketName"]
        replication_task_arn = setup_replication_task(target_type=target_type)

        snapshot.match(
            "replication-task-id",
            {
                "ReplicationTaskArn": replication_task_arn,
            },
        )

        # add cdc files in a different lexicographical order
        cdc_file1 = f"{BUCKET_FOLDER}/{CHANGE_DATA}/cdc0000000001.csv"
        cdc_file2 = f"{BUCKET_FOLDER}/{CHANGE_DATA}/cdc0000000002.csv"
        cdc_file3 = f"{BUCKET_FOLDER}/{CHANGE_DATA}/cdc0000000003.csv"

        aws_client.s3.put_object(Bucket=bucket, Key=cdc_file1, Body=CDC_FILE_SAMPLE_DATA)
        cleanups.append(lambda: aws_client.s3.delete_object(Bucket=bucket, Key=cdc_file1))

        aws_client.s3.put_object(Bucket=bucket, Key=cdc_file3, Body=CDC_FILE_SAMPLE_DATA)
        cleanups.append(lambda: aws_client.s3.delete_object(Bucket=bucket, Key=cdc_file3))

        # it is observed that we need to wait a bit for the third upload since the time duration between the
        # second and the third upload is too short ~1s which is then considered in the lexicographical order
        time.sleep(10)

        aws_client.s3.put_object(Bucket=bucket, Key=cdc_file2, Body=CDC_FILE_SAMPLE_DATA)
        cleanups.append(lambda: aws_client.s3.delete_object(Bucket=bucket, Key=cdc_file2))

        expected_employees = {"AppliedInserts": 2, "AppliedDeletes": 2, "AppliedUpdates": 4}

        def _check_expected_table_stats():
            table_stats = describe_table_statistics(aws_client.dms, replication_task_arn)[
                "TableStatistics"
            ]
            assert len(table_stats) == 1
            assert table_stats[0]["TableName"] == "employee"
            assert dict_contains_subdict(table_stats[0], expected_employees)
            return table_stats

        res_describe_table_statistics = retry(
            _check_expected_table_stats,
            retries=RETRIES,
            sleep=RETRY_SLEEP,
            sleep_before=SLEEP_BEFORE,
        )
        snapshot.match("describe-table-statistics", res_describe_table_statistics)

        retry(
            lambda: assert_dms_replication_task_status(
                aws_client.dms,
                replication_task_arn,
                expected_status="running",
                wait_for_task_stats=True,
            ),
            retries=RETRIES,
            sleep=RETRY_SLEEP,
            sleep_before=SLEEP_BEFORE,
        )

        # 1 create table, 2 insert, 4 updates, 2 delete, 1 table for awsdms_apply_exceptions
        expected_count = 10

        kinesis_records = retry(
            lambda: get_records_from_shard(
                aws_client.kinesis,
                stream_arn,
                threshold_timestamp=threshold_timestamp,
                expected_count=expected_count,
            ),
            retries=RETRIES,
            sleep=RETRY_SLEEP,
            sleep_before=SLEEP_BEFORE,
        )

        json_formatted = True
        if target_type == UNFORMATTED_JSON_TARGET_TYPE:
            json_formatted = False

        formatted_records = transform_kinesis_data(
            kinesis_input=kinesis_records,
            assert_exec=assert_json_formatting(json_formatted),
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
    def test_replication_task_without_total_count_param(
        self,
        infrastructure,
        dms_create_replication_task,
        aws_client,
        snapshot,
        cleanups,
    ):
        snapshot.add_transformer(snapshot.transform.dms_api())
        snapshot.add_transformer(snapshot.transform.kinesis_api())

        threshold_timestamp = time.time()

        outputs = infrastructure.get_stack_outputs(self.STACK_NAME)
        source_endpoint_arn = outputs["SourceEndpointWithoutCountS3Arn"]
        replication_instance_arn = outputs["ReplicationInstanceArn"]
        bucket = outputs["S3BucketName"]
        stream_arn = outputs["KinesisStreamArn"]
        test_file = f"{BUCKET_FOLDER}/{SCHEMA_NAME}/{TABLE_NAME}/example.csv"

        target_endpoint_arn = outputs["TargetEndpointDefaultArn"]

        aws_client.s3.put_object(Bucket=bucket, Key=test_file, Body=SOURCE_CSV_EMPLOYEE_SAMPLE_DATA)
        cleanups.append(lambda: aws_client.s3.delete_object(Bucket=bucket, Key=test_file))

        replication_task = dms_create_replication_task(
            MigrationType="full-load",
            ReplicationInstanceArn=replication_instance_arn,
            SourceEndpointArn=source_endpoint_arn,
            TargetEndpointArn=target_endpoint_arn,
            TableMappings=json.dumps(DEFAULT_TABLE_MAPPING),
        )

        replication_task_arn = replication_task["ReplicationTask"]["ReplicationTaskArn"]

        retry(
            lambda: assert_dms_replication_task_status(
                aws_client.dms, replication_task_arn, expected_status="ready"
            ),
            retries=RETRIES,
            sleep=RETRY_SLEEP,
            sleep_before=SLEEP_BEFORE,
        )

        aws_client.dms.start_replication_task(
            ReplicationTaskArn=replication_task_arn, StartReplicationTaskType="start-replication"
        )

        retry(
            lambda: assert_dms_replication_task_status(
                aws_client.dms,
                replication_task_arn,
                expected_status="stopped",
                wait_for_task_stats=True,
            ),
            retries=RETRIES,
            sleep=RETRY_SLEEP,
            sleep_before=SLEEP_BEFORE,
        )

        res_describe_table_statistics = describe_table_statistics(
            aws_client.dms, replication_task_arn
        )
        snapshot.match("describe-table-statistics", res_describe_table_statistics)

        kinesis_records = retry(
            lambda: get_records_from_shard(
                aws_client.kinesis,
                stream_arn,
                threshold_timestamp=threshold_timestamp,
                # we expect 2 statements for create and delete for table employee
                # plus the actual data: 4 rows
                # => 2+4=6
                expected_count=6,
            ),
            retries=100,
            sleep=5 if is_aws_cloud() else 1,
        )
        formatted_records = transform_kinesis_data(
            kinesis_records, assert_exec=assert_json_formatting(True)
        )
        snapshot.match("kinesis-records", formatted_records)

    @pytest.mark.parametrize(
        "content, expected_count, expected_employees",
        [
            # first entry is valid
            # second one only has data but does not contain operation, table name and schema
            # third one contains null values; by default no null values are allowed as it's not specified in the
            # table definition - we expect to fail after reading 1 entry
            pytest.param(
                """INSERT,employee,hr,101,Smith,Bob,2014-06-04,New York
100,Test,Bob,2015-10-08,Los Angeles
101,Smith,Bob,,
102,Smith,121
test,something,
                        """,
                4,  # 1 create table, 2 inserts, 1 table for awsdms_apply_exceptions
                {"AppliedInserts": 2},
                id="first row valid rest invalid",
            ),
            pytest.param(
                """101,Smith,Bob,,""",
                3,  # 1 create table, 1 insert for valid csv, 1 table for awsdms_apply_exceptions
                {"AppliedInserts": 1},
                id="invalid number of columns",
            ),
            pytest.param(
                """INVALID-OPERATION,employee,hr,101,Smith,Bob,2014-06-04,New York""",
                3,  # 1 create table, 1 insert for valid csv, 1 table for awsdms_apply_exceptions
                {"AppliedInserts": 1},
                id="invalid operation",
            ),
            pytest.param(
                """INSERT,invalid-table,hr,101,Smith,Bob,2014-06-04,New York""",
                3,  # 1 create table, 1 insert for valid csv, 1 table for awsdms_apply_exceptions
                {"AppliedInserts": 1},
                id="invalid table",
            ),
            pytest.param(
                """INSERT,employee,invalid-schema,101,Smith,Bob,2014-06-04,New York""",
                3,  # 1 create table, 1 insert for valid csv, 1 table for awsdms_apply_exceptions
                {"AppliedInserts": 1},
                id="invalid schema",
            ),
            pytest.param(
                """INSERT,employee,hr
INSERT,employee,hr,101,Smith,Bob,2014-06-04,New York""",
                4,  # 1 create table, 1 insert for valid csv, 1 table for awsdms_apply_exceptions
                {"AppliedInserts": 2},
                id="no data valid data",
            ),
        ],
    )
    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(
        paths=[
            # TODO: AWS returns KMS by default, we return NONE
            "$..EncryptionType",
            # RecoveryCheckpoint not supported on LS
            "$..RecoveryCheckpoint",
        ]
    )
    def test_run_task_invalid_format_cdc_file(
        self,
        infrastructure,
        content,
        expected_count,
        expected_employees,
        dms_create_replication_task,
        aws_client,
        snapshot,
        cleanups,
    ):
        snapshot.add_transformer(snapshot.transform.dms_api())
        snapshot.add_transformer(snapshot.transform.kinesis_api())

        threshold_timestamp = time.time()
        outputs = infrastructure.get_stack_outputs(self.STACK_NAME)
        stream_arn = outputs["KinesisStreamArn"]
        source_endpoint_arn = outputs["SourceEndpointS3Arn"]
        target_endpoint_arn = outputs["TargetEndpointDefaultArn"]
        replication_instance_arn = outputs["ReplicationInstanceArn"]

        replication_task = dms_create_replication_task(
            MigrationType="cdc",
            ReplicationInstanceArn=replication_instance_arn,
            SourceEndpointArn=source_endpoint_arn,
            TargetEndpointArn=target_endpoint_arn,
            TableMappings=json.dumps(DEFAULT_TABLE_MAPPING),
        )

        replication_task_arn = replication_task["ReplicationTask"]["ReplicationTaskArn"]

        retry(
            lambda: assert_dms_replication_task_status(
                aws_client.dms, replication_task_arn, expected_status="ready"
            ),
            retries=RETRIES,
            sleep=RETRY_SLEEP,
            sleep_before=SLEEP_BEFORE,
        )

        aws_client.dms.start_replication_task(
            ReplicationTaskArn=replication_task_arn, StartReplicationTaskType="start-replication"
        )

        retry(
            lambda: assert_dms_replication_task_status(
                aws_client.dms,
                replication_task_arn,
                expected_status="running",
            ),
            retries=RETRIES,
            sleep=RETRY_SLEEP,
            sleep_before=SLEEP_BEFORE,
        )

        bucket = outputs["S3BucketName"]
        cdc_file = f"{BUCKET_FOLDER}/{CHANGE_DATA}/invalid-cdc.csv"

        aws_client.s3.put_object(Bucket=bucket, Key=cdc_file, Body=content)
        cleanups.append(lambda: aws_client.s3.delete_object(Bucket=bucket, Key=cdc_file))

        cdc_file2 = f"{BUCKET_FOLDER}/{CHANGE_DATA}/valid-cdc.csv"

        content = """INSERT,employee,hr,102,Smith,Bob,2014-06-04,New York"""
        aws_client.s3.put_object(Bucket=bucket, Key=cdc_file2, Body=content)
        cleanups.append(lambda: aws_client.s3.delete_object(Bucket=bucket, Key=cdc_file2))

        def _check_expected_table_stats():
            table_stats = describe_table_statistics(aws_client.dms, replication_task_arn)[
                "TableStatistics"
            ]
            assert len(table_stats) == 1
            assert table_stats[0]["TableName"] == "employee"
            assert dict_contains_subdict(table_stats[0], expected_employees)
            return table_stats

        res_describe_table_statistics = retry(
            _check_expected_table_stats,
            retries=RETRIES,
            sleep=RETRY_SLEEP,
            sleep_before=SLEEP_BEFORE,
        )
        snapshot.match("describe-table-statistics", res_describe_table_statistics)

        kinesis_records = retry(
            lambda: get_records_from_shard(
                aws_client.kinesis,
                stream_arn,
                threshold_timestamp=threshold_timestamp,
                expected_count=expected_count,
            ),
            retries=RETRIES,
            sleep=RETRY_SLEEP,
            sleep_before=SLEEP_BEFORE,
        )
        formatted_records = transform_kinesis_data(
            kinesis_input=kinesis_records,
            assert_exec=assert_json_formatting(True),
            sorting_type="cdc",
        )
        snapshot.match("kinesis-records", formatted_records)

        aws_client.dms.stop_replication_task(ReplicationTaskArn=replication_task_arn)

        def wait_for_stop_date():
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
            retries=RETRIES,
            sleep=RETRY_SLEEP,
            sleep_before=SLEEP_BEFORE,
        )
        snapshot.match("stopped-replication-task", stopped)

    @markers.aws.validated
    @pytest.mark.parametrize(
        "target_type",
        [
            DEFAULT_TARGET_TYPE,
            NON_DEFAULT_TARGET_TYPE,
            UNFORMATTED_JSON_TARGET_TYPE,
        ],
    )
    @markers.snapshot.skip_snapshot_verify(
        paths=[
            # TODO: AWS returns KMS by default, we return NONE
            "$..EncryptionType",
        ]
    )
    def test_full_load_replication_task_multiple_tables(
        self,
        infrastructure,
        target_type,
        dms_create_replication_task,
        aws_client,
        snapshot,
        cleanups,
    ):
        snapshot.add_transformer(snapshot.transform.dms_api())
        snapshot.add_transformer(snapshot.transform.kinesis_api())

        threshold_timestamp = time.time()

        outputs = infrastructure.get_stack_outputs(self.STACK_NAME)
        source_endpoint_arn = outputs["SourceEndpointS3MultipleTablesArn"]
        replication_instance_arn = outputs["ReplicationInstanceArn"]
        bucket = outputs["S3BucketName"]
        stream_arn = outputs["KinesisStreamArn"]

        json_formatted = True
        target_endpoint_arn: str
        if target_type == NON_DEFAULT_TARGET_TYPE:
            target_endpoint_arn = outputs["TargetEndpointNonDefaultArn"]
        elif target_type == UNFORMATTED_JSON_TARGET_TYPE:
            target_endpoint_arn = outputs["TargetEndpointUnformattedJsonArn"]
            json_formatted = False
        else:
            target_endpoint_arn = outputs["TargetEndpointDefaultArn"]

        test_file1 = f"{BUCKET_FOLDER}/{SCHEMA_NAME}/{TABLE_NAME}/LOAD001.csv"
        aws_client.s3.put_object(
            Bucket=bucket, Key=test_file1, Body=SOURCE_CSV_EMPLOYEE_SAMPLE_DATA
        )

        test_file2 = f"{BUCKET_FOLDER}/{SCHEMA_NAME}/department/LOAD002.csv"
        aws_client.s3.put_object(
            Bucket=bucket, Key=test_file2, Body=SOURCE_CSV_DEPARTMENT_SAMPLE_DATA
        )

        test_file3 = f"{BUCKET_FOLDER}/{SCHEMA_NAME}/project/LOAD003.csv"
        aws_client.s3.put_object(Bucket=bucket, Key=test_file3, Body=SOURCE_CSV_PROJECT_SAMPLE_DATA)

        for file in [test_file1, test_file2, test_file3]:
            cleanups.append(lambda: aws_client.s3.delete_object(Bucket=bucket, Key=file))

        replication_task = dms_create_replication_task(
            MigrationType="full-load",
            ReplicationInstanceArn=replication_instance_arn,
            SourceEndpointArn=source_endpoint_arn,
            TargetEndpointArn=target_endpoint_arn,
            TableMappings=json.dumps(DEFAULT_TABLE_MAPPING),
        )

        replication_task_arn = replication_task["ReplicationTask"]["ReplicationTaskArn"]

        retry(
            lambda: assert_dms_replication_task_status(
                aws_client.dms, replication_task_arn, expected_status="ready"
            ),
            retries=RETRIES,
            sleep=RETRY_SLEEP,
            sleep_before=SLEEP_BEFORE,
        )

        aws_client.dms.start_replication_task(
            ReplicationTaskArn=replication_task_arn, StartReplicationTaskType="start-replication"
        )

        retry(
            lambda: assert_dms_replication_task_status(
                aws_client.dms,
                replication_task_arn,
                expected_status="stopped",
                wait_for_task_stats=True,
            ),
            retries=RETRIES,
            sleep=RETRY_SLEEP,
            sleep_before=SLEEP_BEFORE,
        )

        res_describe_table_statistics = describe_table_statistics(
            aws_client.dms, replication_task_arn
        )
        snapshot.match("describe-table-statistics", res_describe_table_statistics)

        kinesis_records = retry(
            lambda: get_records_from_shard(
                aws_client.kinesis,
                stream_arn,
                threshold_timestamp=threshold_timestamp,
                # we expect 2 statements each for create and delete for table employee, department, project
                # plus the actual data: 4 rows for employee, 3 rows for department, 3 rows for project
                # => 2+2+2+4+3+3=16
                expected_count=16,
            ),
            retries=100,
            sleep=5 if is_aws_cloud() else 1,
        )
        formatted_records = transform_kinesis_data(
            kinesis_records, assert_exec=assert_json_formatting(json_formatted)
        )
        snapshot.match("kinesis-records", formatted_records)

    @markers.aws.validated
    @pytest.mark.parametrize(
        "target_type",
        [
            DEFAULT_TARGET_TYPE,
            NON_DEFAULT_TARGET_TYPE,
            UNFORMATTED_JSON_TARGET_TYPE,
        ],
    )
    @markers.snapshot.skip_snapshot_verify(
        paths=[
            # TODO: AWS returns KMS by default, we return NONE
            "$..EncryptionType",
        ]
    )
    def test_cdc_replication_task_multiple_tables(
        self,
        infrastructure,
        target_type,
        setup_replication_task,
        aws_client,
        snapshot,
        cleanups,
    ):
        snapshot.add_transformer(snapshot.transform.dms_api())
        snapshot.add_transformer(snapshot.transform.kinesis_api())

        threshold_timestamp = time.time()
        outputs = infrastructure.get_stack_outputs(self.STACK_NAME)
        stream_arn = outputs["KinesisStreamArn"]
        bucket = outputs["S3BucketName"]
        replication_task_arn = setup_replication_task(target_type=target_type, multiple_tables=True)

        snapshot.match(
            "replication-task-id",
            {
                "ReplicationTaskArn": replication_task_arn,
            },
        )

        # add cdc files in a different lexicographical order
        cdc_file1 = f"{BUCKET_FOLDER}/{CHANGE_DATA}/cdc0000000001.csv"
        cdc_file2 = f"{BUCKET_FOLDER}/{CHANGE_DATA}/cdc0000000002.csv"

        aws_client.s3.put_object(Bucket=bucket, Key=cdc_file1, Body=CDC_FILE_SAMPLE_DATA)
        cleanups.append(lambda: aws_client.s3.delete_object(Bucket=bucket, Key=cdc_file1))

        cdc_file2_content = """INSERT,department,hr,204,Software
INSERT,employee,hr,101,Smith,Bob,2015-10-08,Los Angeles
INSERT,project,hr,101,Project1,Description1
DELETE,project,hr,101,Project1,Description1
DELETE,department,hr,301,Software
UPDATE,employee,hr,101,Smith,Bob,2017-03-13,Dallas
DELETE,employee,hr,101,Smith,Bob,2017-03-13,Dallas"""

        aws_client.s3.put_object(Bucket=bucket, Key=cdc_file2, Body=cdc_file2_content)
        cleanups.append(lambda: aws_client.s3.delete_object(Bucket=bucket, Key=cdc_file2))

        expected = {
            "employee": {"AppliedInserts": 2, "AppliedDeletes": 2, "AppliedUpdates": 3},
            "department": {"AppliedInserts": 1, "AppliedDeletes": 1, "AppliedUpdates": 0},
            "project": {"AppliedInserts": 1, "AppliedDeletes": 1, "AppliedUpdates": 0},
        }

        def _check_expected_table_stats():
            table_stats = describe_table_statistics(aws_client.dms, replication_task_arn)[
                "TableStatistics"
            ]
            assert len(table_stats) == 3
            for stat in table_stats:
                assert dict_contains_subdict(stat, expected.get(stat["TableName"], {}))
            return table_stats

        res_describe_table_statistics = retry(
            _check_expected_table_stats,
            retries=RETRIES,
            sleep=RETRY_SLEEP,
            sleep_before=SLEEP_BEFORE,
        )
        snapshot.match("describe-table-statistics", res_describe_table_statistics)

        retry(
            lambda: assert_dms_replication_task_status(
                aws_client.dms,
                replication_task_arn,
                expected_status="running",
                wait_for_task_stats=True,
            ),
            retries=RETRIES,
            sleep=RETRY_SLEEP,
            sleep_before=SLEEP_BEFORE,
        )

        # 3 create table, 4 insert, 3 updates, 4 deletes, 1 table for awsdms_apply_exceptions
        expected_count = 15

        kinesis_records = retry(
            lambda: get_records_from_shard(
                aws_client.kinesis,
                stream_arn,
                threshold_timestamp=threshold_timestamp,
                expected_count=expected_count,
            ),
            retries=RETRIES,
            sleep=RETRY_SLEEP,
            sleep_before=SLEEP_BEFORE,
        )

        json_formatted = False if target_type == UNFORMATTED_JSON_TARGET_TYPE else True

        formatted_records = transform_kinesis_data(
            kinesis_input=kinesis_records,
            assert_exec=assert_json_formatting(json_formatted),
            sorting_type="cdc",
        )
        snapshot.match("kinesis-records", formatted_records)
