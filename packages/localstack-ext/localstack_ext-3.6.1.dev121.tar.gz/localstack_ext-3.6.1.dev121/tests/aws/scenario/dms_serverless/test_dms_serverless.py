import json
import time

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
from localstack.testing.aws.util import is_aws_cloud
from localstack.testing.pytest import markers
from localstack.utils.sync import retry

from tests.aws.scenario.test_utils.dms_utils import (
    assert_dms_replication_config_status,
    assert_json_formatting,
    describe_replication_table_statistics,
    dict_contains_subdict,
    get_records_from_shard,
    run_queries_on_mysql,
    transform_kinesis_data,
)

USERNAME = "dms_user"
USER_PWD = "bLML-dGn=S#=9z36"
DB_NAME = "production"
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

DEFAULT_VPC_ENDPOINT_SERVICES = ["secretsmanager", "kinesis-streams"]


class TestDmsScenario:
    """
    Used to test the serverless deployment for DMS
    Currently only mariadb or mysql can be used, as s3 is not supported for serverless by AWS
    """

    STACK_NAME = "DmsServerlessStack"

    @pytest.fixture(scope="class")
    def patch_dms_deprovision_status_change_time(self):
        """patching the DMS_SERVERLESS_DEPROVISIONING_DELAY and DMS_SERVERLESS_STATUS_CHANGE_WAITING_TIME env"""
        from _pytest.monkeypatch import MonkeyPatch
        from localstack.pro.core import config as ext_config

        mpatch = MonkeyPatch()
        mpatch.setattr(ext_config, "DMS_SERVERLESS_DEPROVISIONING_DELAY", 5)
        mpatch.setattr(ext_config, "DMS_SERVERLESS_STATUS_CHANGE_WAITING_TIME", 3)
        yield mpatch
        mpatch.undo()

    @pytest.fixture(scope="class")
    def infrastructure(self, infrastructure_setup, patch_dms_deprovision_status_change_time):
        infra = infrastructure_setup("DmsServerless", force_synth=True)

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
        # this ingress rule is required to setup the vpc-endpoints for secretsmanager/kinesis
        security_group.add_ingress_rule(
            peer=ec2.Peer.ipv4(vpc.vpc_cidr_block),
            connection=ec2.Port.tcp(443),
            description=f"from {vpc.vpc_cidr_block}:443",
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

        # create db instances
        db_instance_mysql = rds.DatabaseInstance(
            stack,
            "dbinstance",
            credentials=credentials,
            database_name=DB_NAME,
            engine=rds.DatabaseInstanceEngine.mysql(version=rds.MysqlEngineVersion.VER_8_0),
            instance_type=ec2.InstanceType("t3.micro"),
            parameters=db_parameters_config,
            publicly_accessible=True,
            removal_policy=cdk.RemovalPolicy.DESTROY,
            security_groups=[security_group],
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnets=vpc.public_subnets),
        )

        # Update Security Group Ingress Policy
        db_mysql_port_as_number = cdk.Token.as_number(db_instance_mysql.db_instance_endpoint_port)

        port = db_mysql_port_as_number
        security_group.connections.allow_from(
            other=ec2.Peer.any_ipv4(),
            port_range=ec2.Port.tcp_range(port, port),
        )

        # Create a secret
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

        subnet_ids = [subnet.subnet_id for subnet in vpc.public_subnets]

        replication_subnet_group = dms.CfnReplicationSubnetGroup(
            stack,
            "ReplSubnetGroup",
            replication_subnet_group_description="Replication Subnet Group for DMS Serverless",
            subnet_ids=subnet_ids,
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

        # Target Endpoint
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
        # test if setting up serverless is supported with cdk
        replication_config = dms.CfnReplicationConfig(
            stack,
            "test-replication-config",
            compute_config=dms.CfnReplicationConfig.ComputeConfigProperty(max_capacity_units=1),
            source_endpoint_arn=source_endpoint_mysql.ref,
            target_endpoint_arn=target_endpoint.ref,
            replication_type="full-load",
            table_mappings=DEFAULT_TABLE_MAPPING,
            replication_config_identifier="test-replication-config",
        )

        cdk.CfnOutput(stack, "ReplicationConfigArn", value=replication_config.ref)
        cdk.CfnOutput(stack, "KinesisStreamArn", value=target_stream.stream_arn)

        cdk.CfnOutput(stack, "DbInstanceMySQLArn", value=db_instance_mysql.instance_arn)
        cdk.CfnOutput(
            stack, "DbEndpointMySQL", value=db_instance_mysql.db_instance_endpoint_address
        )
        cdk.CfnOutput(stack, "DbPortMySQL", value=db_instance_mysql.db_instance_endpoint_port)

        cdk.CfnOutput(stack, "SourceEndpointMySQLArn", value=source_endpoint_mysql.ref)
        cdk.CfnOutput(stack, "TargetEndpointDefaultArn", value=target_endpoint.ref)

        cdk.CfnOutput(stack, "SecurityGroup", value=security_group.security_group_id)
        cdk.CfnOutput(stack, "ReplicationSubnetGroup", value=replication_subnet_group.ref)
        cdk.CfnOutput(stack, "AvailabilityZone", value=vpc.public_subnets[0].availability_zone)

        cdk.CfnOutput(stack, "MysqlSecretArn", value=mysql_secret.ref)

        cdk.CfnOutput(stack, "VpcId", value=vpc.vpc_id)

        cdk.CfnOutput(stack, "SubnetIds", value=",".join(subnet_ids))

        with infra.provisioner(skip_teardown=False) as prov:
            yield prov

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(
        paths=[
            # weird behavior on AWS: create and delete return the ReplicationConfigUpdateTime, but describe doesn't
            "$..describe_replication_config.ReplicationConfigs..ReplicationConfigUpdateTime",
        ]
    )
    def test_resource_replication_config(
        self,
        infrastructure,
        aws_client,
        snapshot,
    ):
        snapshot.add_transformer(snapshot.transform.dms_api())
        outputs = infrastructure.get_stack_outputs(self.STACK_NAME)
        replication_config_arn = outputs["ReplicationConfigArn"]

        config = aws_client.dms.describe_replication_configs(
            Filters=[
                {
                    "Name": "replication-config-arn",
                    "Values": [replication_config_arn],
                }
            ]
        )
        snapshot.match("describe_replication_config", config)

        status = aws_client.dms.describe_replications(
            Filters=[{"Name": "replication-config-arn", "Values": [replication_config_arn]}]
        )
        snapshot.match("describe_replications", status)

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(
        paths=[
            # weird behavior on AWS: create and delete return the ReplicationConfigUpdateTime, but describe doesn't
            "$..describe_replication_config.ReplicationConfigs..ReplicationConfigUpdateTime",
        ]
    )
    def test_create_describe_replication_config(
        self,
        infrastructure,
        dms_create_replication_config,
        aws_client,
        snapshot,
        region_name,
        account_id,
        partition,
    ):
        snapshot.add_transformer(snapshot.transform.dms_api())
        snapshot.add_transformer(snapshot.transform.key_value("ReplicationConfigIdentifier"))
        outputs = infrastructure.get_stack_outputs(self.STACK_NAME)
        source_arn = outputs["SourceEndpointMySQLArn"]
        target_arn = outputs["TargetEndpointDefaultArn"]
        table_mapping = {
            "rules": [
                {
                    "rule-type": "selection",
                    "rule-id": "1",
                    "rule-name": "r1",
                    "object-locator": {"schema-name": "data", "table-name": "%"},
                    "rule-action": "include",
                }
            ]
        }

        # test invalid config
        with pytest.raises(ClientError) as e:
            dms_create_replication_config(
                SourceEndpointArn=source_arn,
                TargetEndpointArn=target_arn,
                ReplicationType="full-load",
                TableMappings=json.dumps(table_mapping),
                ComputeConfig={},
            )
        snapshot.match("create-config-invalid-computeconfig", e.value.response)

        compute_config = {
            "MaxCapacityUnits": 1,
            # others are optional
            # TODO - nice to have: verify input for other values
            # "AvailabilityZone": "string",
            # "DnsNameServers": "string",
            # "KmsKeyId": "string",
            # "MinCapacityUnits": 1,
            # "MultiAZ": False,
            # "PreferredMaintenanceWindow": "string",
            # "ReplicationSubnetGroupId": "string",
            # "VpcSecurityGroupIds": ["string", ...],
        }
        with pytest.raises(ClientError) as e:
            dms_create_replication_config(
                SourceEndpointArn=source_arn,
                TargetEndpointArn=target_arn,
                ReplicationType="full",
                TableMappings=json.dumps(table_mapping),
                ComputeConfig=compute_config,
            )
        snapshot.match("create-config-invalid-replicationtype", e.value.response)

        with pytest.raises(ClientError) as e:
            dms_create_replication_config(
                SourceEndpointArn=source_arn,
                TargetEndpointArn=target_arn,
                ReplicationType="full-load",
                TableMappings=json.dumps(table_mapping),
                ComputeConfig={
                    "MaxCapacityUnits": 1,
                    "MinCapacityUnits": 2,
                },
            )
        snapshot.match("create-config-invalid-computeconfig-2", e.value.response)

        # invalid source/target
        # test invalid source endpoints
        invalid_endpoint = f"arn:{partition}:dms:{region_name}:{account_id}:endpoint:identifier"
        with pytest.raises(ClientError) as e:
            dms_create_replication_config(
                ReplicationType="full-load",
                SourceEndpointArn=invalid_endpoint,
                TargetEndpointArn=target_arn,
                TableMappings=json.dumps(table_mapping),
                ComputeConfig=compute_config,
            )
        snapshot.match("create_replication_config_valid_source", e.value.response)

        # invalid target endpoint
        with pytest.raises(ClientError) as e:
            dms_create_replication_config(
                ReplicationType="full-load",
                SourceEndpointArn=source_arn,
                TargetEndpointArn=invalid_endpoint,
                TableMappings=json.dumps(table_mapping),
                ComputeConfig=compute_config,
            )
        snapshot.match("create_replication_config_invalid_target", e.value.response)

        # switch target/source
        with pytest.raises(ClientError) as e:
            dms_create_replication_config(
                ReplicationType="full-load",
                SourceEndpointArn=target_arn,
                TargetEndpointArn=source_arn,
                TableMappings=json.dumps(table_mapping),
                ComputeConfig=compute_config,
            )
        # the message is very specific, so matching is tricky, e.g.
        #   ReplicationEngineType [id=47, name=kinesis, cdcSupported=Y, endpointType=TARGET,
        #             serviceType=AWS, externalName=Amazon Kinesis, rvn=1] endpoint must be of type SOURCE
        # snapshot.match("create_replication_config_invalid_endpoint", e.value.response)
        assert e.match("ReplicationEngineType .* must be of type SOURCE")
        assert e.value.response["Error"]["Code"] == "InvalidParameterValueException"
        assert e.value.response["ResponseMetadata"]["HTTPStatusCode"] == 400

        # invalid table mapping
        # rule-type is invalid
        table_mapping["rules"][0]["rule-id"] = 2  # set an integer
        table_mapping["rules"][0]["rule-type"] = "something"
        with pytest.raises(ClientError) as e:
            dms_create_replication_config(
                ReplicationType="full-load",
                SourceEndpointArn=source_arn,
                TargetEndpointArn=target_arn,
                TableMappings=json.dumps(table_mapping),
                ComputeConfig=compute_config,
            )
        snapshot.match("create_replication_task_invalid_2", e.value.response)
        # fix table-mapping
        table_mapping["rules"][0]["rule-type"] = "selection"

        replication_config = dms_create_replication_config(
            SourceEndpointArn=source_arn,
            TargetEndpointArn=target_arn,
            ReplicationType="full-load",
            TableMappings=json.dumps(table_mapping),
            ComputeConfig=compute_config,
        )
        snapshot.match("create-replication-config", replication_config)

        # describe with unknown replication-config-arn
        with pytest.raises(ClientError) as e:
            aws_client.dms.describe_replication_configs(
                Filters=[
                    {
                        "Name": "replication-config-arn",
                        "Values": [
                            f"arn:{partition}:dms:{region_name}:{account_id}:replication-config:does-not-exist"
                        ],
                    }
                ]
            )
        snapshot.match("describe_replication_config_unknown_arn", e.value.response)

        # describe with unknown filter
        with pytest.raises(ClientError) as e:
            aws_client.dms.describe_replication_configs(
                Filters=[{"Name": "migration-type", "Values": ["full-load"]}]
            )
        snapshot.match("describe_replication_invalid_filter", e.value.response)

        # describe valid filter
        replication_config_arn = replication_config["ReplicationConfig"]["ReplicationConfigArn"]
        describe_replication_config = aws_client.dms.describe_replication_configs(
            Filters=[{"Name": "replication-config-arn", "Values": [replication_config_arn]}]
        )
        snapshot.match("describe_replication_config", describe_replication_config)

        # describe replication
        replications = aws_client.dms.describe_replications(
            Filters=[{"Name": "replication-config-arn", "Values": [replication_config_arn]}]
        )
        snapshot.match("describe_replications", replications)

        # delete unknown replication config
        with pytest.raises(ClientError) as e:
            aws_client.dms.delete_replication_config(
                ReplicationConfigArn=f"arn:{partition}:dms:{region_name}:{account_id}:replication-config:does-not-exist"
            )
        snapshot.match("delete_replication_config_unknown", e.value.response)

        # delete replication config
        response = aws_client.dms.delete_replication_config(
            ReplicationConfigArn=replication_config_arn
        )
        snapshot.match("delete_replication_config", response)

        # describe replications that doesn't exist
        with pytest.raises(ClientError) as e:
            aws_client.dms.describe_replications(
                Filters=[
                    {
                        "Name": "replication-config-arn",
                        "Values": [
                            f"arn:{partition}:dms:{region_name}:{account_id}:replication-config:does-not-exist"
                        ],
                    }
                ]
            )
        snapshot.match("describe_replications_unknown", e.value.response)

        # describe already deleted replication
        def describe_deleted_replication():
            try:
                describe = aws_client.dms.describe_replications(
                    Filters=[{"Name": "replication-config-arn", "Values": [replication_config_arn]}]
                )
                # initially the status is 'deleting' and only afterwards it will throw exception
                assert not describe
            except ClientError as e:
                snapshot.match("describe_replications_already_deleted", e.response)

        retry(
            describe_deleted_replication,
            retries=20 if is_aws_cloud() else 2,
            sleep_before=2 if is_aws_cloud() else 0,
        )

        # TODO test deleting if task is running (needs to be covered in another test case)

    @markers.aws.validated
    def test_describe_replication_table_statistics(
        self,
        infrastructure,
        aws_client,
        account_id,
        region_name,
        snapshot,
        dms_create_replication_config,
        partition,
    ):
        snapshot.add_transformer(snapshot.transform.dms_api())
        snapshot.add_transformer(snapshot.transform.key_value("ReplicationConfigIdentifier"))

        outputs = infrastructure.get_stack_outputs(self.STACK_NAME)
        source_arn = outputs["SourceEndpointMySQLArn"]
        target_arn = outputs["TargetEndpointDefaultArn"]

        not_existent_replication_config_arn = (
            f"arn:{partition}:dms:{region_name}:{account_id}:replication-config:test-config"
        )

        with pytest.raises(ClientError) as e:
            describe_replication_table_statistics(
                aws_client.dms, not_existent_replication_config_arn
            )
        snapshot.match("describe_replication_table_non_existent_config", e.value.response)

        with pytest.raises(ClientError) as e:
            describe_replication_table_statistics(aws_client.dms, "invalid-regexp-arn")
        snapshot.match("describe_replication_table_statistics_invalid_arn", e.value.response)

        compute_config = {
            "MaxCapacityUnits": 1,
        }

        replication_config = dms_create_replication_config(
            SourceEndpointArn=source_arn,
            TargetEndpointArn=target_arn,
            ReplicationType="full-load",
            TableMappings=json.dumps(DEFAULT_TABLE_MAPPING),
            ComputeConfig=compute_config,
            ReplicationSettings=json.dumps({"Logging": {"EnableLogging": True}}),
        )

        replication_config_arn = replication_config["ReplicationConfig"]["ReplicationConfigArn"]

        result = describe_replication_table_statistics(aws_client.dms, replication_config_arn)
        snapshot.match("describe_replication_table_statistics", result)

        # no filter match
        result = aws_client.dms.describe_replication_table_statistics(
            ReplicationConfigArn=replication_config_arn,
            Filters=[{"Name": "schema-name", "Values": ["hello"]}],
        )
        snapshot.match("describe_replication_table_statistics_empty_filters", result)

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(
        paths=[
            # TODO: AWS returns KMS for the kinesis records, we return NONE
            "$..EncryptionType",
            # another inconsistency on AWS: sometimes this parameter was included, sometimes not - probably added at a later point
            #   IMO it makes sense to keep it when the status is stopped though
            # "$..describe-replication-stopped..ReplicationStats.StopDate",
        ]
    )
    def test_full_load_replication(
        self,
        infrastructure,
        aws_client,
        snapshot,
        cleanups,
        dms_create_replication_config,
        create_vpc_endpoint,
        region_name,
    ):
        snapshot.add_transformer(snapshot.transform.dms_api())
        snapshot.add_transformer(snapshot.transform.kinesis_api())
        snapshot.add_transformer(snapshot.transform.key_value("ReplicationConfigIdentifier"))

        threshold_timestamp = time.time()
        outputs = infrastructure.get_stack_outputs(self.STACK_NAME)

        source_arn = outputs["SourceEndpointMySQLArn"]
        target_arn = outputs["TargetEndpointDefaultArn"]
        db_endpoint = outputs["DbEndpointMySQL"]
        db_port = outputs["DbPortMySQL"]
        stream_arn = outputs["KinesisStreamArn"]

        security_group = outputs["SecurityGroup"]
        replication_subnet_gp = outputs["ReplicationSubnetGroup"]
        az = outputs["AvailabilityZone"]

        subnet_ids = outputs["SubnetIds"].split(",")

        create_vpc_endpoint(
            VpcId=outputs["VpcId"],
            SubnetIds=subnet_ids,
            SecurityGroupIds=[security_group],
            Services=[
                f"com.amazonaws.{region_name}.{service}"
                for service in DEFAULT_VPC_ENDPOINT_SERVICES
            ],
        )

        compute_config = {
            # TODO: verify output for other combination of values as well
            "MaxCapacityUnits": 1,
            "AvailabilityZone": az,
            "MultiAZ": False,
            "ReplicationSubnetGroupId": replication_subnet_gp,
            "VpcSecurityGroupIds": [security_group],
        }

        replication_config = dms_create_replication_config(
            SourceEndpointArn=source_arn,
            TargetEndpointArn=target_arn,
            ReplicationType="full-load",
            TableMappings=json.dumps(DEFAULT_TABLE_MAPPING),
            ComputeConfig=compute_config,
            ReplicationSettings=json.dumps({"Logging": {"EnableLogging": True}}),
        )

        replication_config_arn = replication_config["ReplicationConfig"]["ReplicationConfigArn"]

        cleanups.append(
            lambda: _run_queries_on_mysql(
                host=db_endpoint,
                port=db_port,
                queries=[
                    "DROP TABLE IF EXISTS ORDERS;",
                    "DROP TABLE IF EXISTS CUSTOMER;",
                    "DROP TABLE IF EXISTS AGENTS;",
                ],
            )
        )

        # setup source database
        queries = [
            f"USE {DB_NAME};",
            SQL_CREATE_AGENTS_TABLE,
            SQL_CREATE_CUSTOMER_TABLE,
            SQL_CREATE_ORDERS_TABLE,
        ]
        queries.extend(SQL_INSERT_AGENT_SAMPLE_DATA_LIST)
        queries.extend(SQL_INSERT_CUSTOMER_SAMPLE_DATA_LIST)
        queries.extend(SQL_INSERT_ORDERS_SAMPLE_DATA_LIST)

        _run_queries_on_mysql(
            host=db_endpoint,
            port=db_port,
            queries=queries,
        )

        start_task = aws_client.dms.start_replication(
            ReplicationConfigArn=replication_config_arn, StartReplicationType="start-replication"
        )
        snapshot.match("start_replication", start_task)
        # Status 'initializing',
        # 'preparing_metadata_resources',
        # 'testing_connection',
        # 'calculating_capacity',
        # 'provisioning_capacity'
        # 'replication_starting'
        # 'running'
        # 'stopped'
        # 'stopped' and deprovisioned -> only then the config can be deleted
        # this takes forever on AWS
        result = retry(
            lambda: assert_dms_replication_config_status(
                aws_client.dms,
                replication_config_arn,
                expected_status="preparing_metadata_resources",
            ),
            retries=200 if is_aws_cloud() else 50,
            sleep=60 * 2 if is_aws_cloud() else 1,
        )
        snapshot.match("describe-replication-config-preparing", result)

        result = retry(
            lambda: assert_dms_replication_config_status(
                aws_client.dms,
                replication_config_arn,
                expected_status="provisioning_capacity",
            ),
            retries=200 if is_aws_cloud() else 50,
            sleep=60 if is_aws_cloud() else 1,
        )
        snapshot.match("describe-replication-provisioning", result)

        result = retry(
            lambda: assert_dms_replication_config_status(
                aws_client.dms,
                replication_config_arn,
                expected_status="replication_starting",
            ),
            retries=500 if is_aws_cloud() else 10,
            sleep=2 if is_aws_cloud() else 1,
        )
        snapshot.match("describe-replication-starting", result)

        # verify that the replication config cannot be deleted at this point
        with pytest.raises(ClientError) as e:
            aws_client.dms.delete_replication_config(ReplicationConfigArn=replication_config_arn)
        snapshot.match("delete-replication-config-fails", e.value.response)

        result = retry(
            lambda: assert_dms_replication_config_status(
                aws_client.dms,
                replication_config_arn,
                expected_status="running",
            ),
            retries=500 if is_aws_cloud() else 40,
            sleep=1 if is_aws_cloud() else 0.1,
        )
        # this snapshot is not really comparable between runs as it may already be progressing/finished at the time
        # the data is inconsistent, but it's still good to check for the status "running"
        # if is_aws_cloud():
        #    snapshot.match("describe-replication-running", result)

        result = retry(
            lambda: assert_dms_replication_config_status(
                aws_client.dms,
                replication_config_arn,
                expected_status="stopped",
            ),
            retries=500 if is_aws_cloud() else 10,
            sleep=1,
        )
        snapshot.match("describe-replication-stopped", result)

        res_describe_table_statistics = describe_replication_table_statistics(
            aws_client.dms, replication_config_arn
        )
        snapshot.match("describe-replication-table-statistics", res_describe_table_statistics)

        kinesis_records = retry(
            lambda: get_records_from_shard(
                aws_client.kinesis,
                stream_arn,
                threshold_timestamp=threshold_timestamp,
                # we expect 2 statements for create/delete each table (agenets, customers, orders) = 6
                # plus the actual data: 4 for agents, 3 for customers, 3 for orders
                # => 6+4+3+3 = 16
                expected_count=16,
            ),
            retries=100,
            sleep=5 if is_aws_cloud() else 1,
        )
        formatted_records = transform_kinesis_data(
            kinesis_records, assert_exec=assert_json_formatting(True)
        )
        # we need to transform the server-id, which only seems to be visible in the kinesis records
        # example: 'PartitionKey'='serv-res-id-1722361971936-yel.production.AGENTS'
        # the last one will be a create-statement which contains the entire server-id
        server_id_partition_key = formatted_records[-1]["PartitionKey"].split(".")[0]
        snapshot.add_transformer(snapshot.transform.regex(server_id_partition_key, "<server-id>"))

        snapshot.match("kinesis-records", formatted_records)

        # wait until the config is stopped + deprovisioned (only afterwards the config can be deleted)
        result = retry(
            lambda: assert_dms_replication_config_status(
                aws_client.dms,
                replication_config_arn,
                expected_status="stopped",
                expected_provision_state="deprovisioned",
            ),
            retries=500 if is_aws_cloud() else 60,
            sleep=2,
        )
        snapshot.match("describe-replication-config-deprovisioned", result)

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(
        paths=[
            # TODO: AWS returns KMS for the kinesis records, we return NONE
            "$..EncryptionType",
            # TODO not sure why the full-load start and finish date are set at all
            #  maybe a bug on AWS?
            "$..ReplicationStats.FullLoadFinishDate",
            "$..ReplicationStats.FullLoadStartDate",
            # StopDate is already set when stopping the replication on LS, on AWS it may happen later
            "$..Replication.ReplicationStats.StopDate",
        ]
    )
    def test_cdc_replication_data_queries(
        self,
        infrastructure,
        aws_client,
        snapshot,
        cleanups,
        dms_create_replication_config,
        create_vpc_endpoint,
        region_name,
    ):
        snapshot.add_transformer(snapshot.transform.dms_api())
        snapshot.add_transformer(snapshot.transform.kinesis_api())
        snapshot.add_transformer(snapshot.transform.key_value("ReplicationConfigIdentifier"))

        threshold_timestamp = time.time()
        outputs = infrastructure.get_stack_outputs(self.STACK_NAME)

        source_arn = outputs["SourceEndpointMySQLArn"]
        target_arn = outputs["TargetEndpointDefaultArn"]
        db_endpoint = outputs["DbEndpointMySQL"]
        db_port = outputs["DbPortMySQL"]
        stream_arn = outputs["KinesisStreamArn"]

        security_group = outputs["SecurityGroup"]
        replication_subnet_gp = outputs["ReplicationSubnetGroup"]
        az = outputs["AvailabilityZone"]

        subnet_ids = outputs["SubnetIds"].split(",")

        create_vpc_endpoint(
            VpcId=outputs["VpcId"],
            SubnetIds=subnet_ids,
            SecurityGroupIds=[security_group],
            Services=[
                f"com.amazonaws.{region_name}.{service}"
                for service in DEFAULT_VPC_ENDPOINT_SERVICES
            ],
        )

        compute_config = {
            # TODO: verify output for other combination of values as well
            "MaxCapacityUnits": 1,
            "AvailabilityZone": az,
            "MultiAZ": False,
            "ReplicationSubnetGroupId": replication_subnet_gp,
            "VpcSecurityGroupIds": [security_group],
        }

        replication_config = dms_create_replication_config(
            SourceEndpointArn=source_arn,
            TargetEndpointArn=target_arn,
            ReplicationType="cdc",
            TableMappings=json.dumps(DEFAULT_TABLE_MAPPING),
            ComputeConfig=compute_config,
            ReplicationSettings=json.dumps({"Logging": {"EnableLogging": True}}),
        )
        replication_config_arn = replication_config["ReplicationConfig"]["ReplicationConfigArn"]

        cleanups.append(
            lambda: _run_queries_on_mysql(
                host=db_endpoint,
                port=db_port,
                queries=[
                    "DROP TABLE IF EXISTS ORDERS;",
                    "DROP TABLE IF EXISTS CUSTOMER;",
                    "DROP TABLE IF EXISTS AGENTS;",
                ],
            )
        )

        # configure the log-retention time
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
            SQL_CREATE_AGENTS_TABLE,
            SQL_CREATE_CUSTOMER_TABLE,
            SQL_CREATE_ORDERS_TABLE,
        ]
        queries.extend(SQL_INSERT_AGENT_SAMPLE_DATA_LIST)
        queries.extend(SQL_INSERT_CUSTOMER_SAMPLE_DATA_LIST)
        queries.extend(SQL_INSERT_ORDERS_SAMPLE_DATA_LIST)

        _run_queries_on_mysql(
            host=db_endpoint,
            port=db_port,
            queries=queries,
        )

        start_task = aws_client.dms.start_replication(
            ReplicationConfigArn=replication_config_arn, StartReplicationType="start-replication"
        )
        snapshot.match("start_replication", start_task)

        result = retry(
            lambda: assert_dms_replication_config_status(
                aws_client.dms,
                replication_config_arn,
                expected_status="running",
            ),
            retries=500 * 3 if is_aws_cloud() else 50,
            sleep=60 * 2 if is_aws_cloud() else 4,
        )
        snapshot.match("describe-replication-running", result)

        queries = [
            # update agents row
            "UPDATE AGENTS SET PHONE_NO='075-12458970' WHERE AGENT_CODE='A001';",
            # update customer row
            "UPDATE CUSTOMER SET OUTSTANDING_AMT=5000.00 WHERE CUST_CODE='C0001';",
            # delete orders
            "DELETE FROM ORDERS WHERE ORD_NUM='O200102';",
            # insert new orders row
            """INSERT INTO ORDERS (ORD_NUM, ORD_AMOUNT, ADVANCE_AMOUNT, ORD_DATE, CUST_CODE, AGENT_CODE, ORD_DESCRIPTION)
                                VALUES
                                ('O200103', '4500.00', '900.00', STR_TO_DATE('5/7/2024','%d/%m/%Y'), 'C00001', 'A001', 'SOD');""",
            # update the above inserted orders row
            "UPDATE ORDERS SET ORD_AMOUNT=5000.00 WHERE ORD_NUM='O200103';",
        ]
        expected = {
            "AGENTS": {"AppliedUpdates": 1},
            "CUSTOMER": {"AppliedUpdates": 1},
            "ORDERS": {"AppliedUpdates": 1, "AppliedInserts": 1, "AppliedDeletes": 1},
        }

        for query in queries:
            _run_queries_on_mysql(
                host=db_endpoint,
                port=db_port,
                queries=[query],
            )

        def _check_expected_table_stats():
            table_stats = describe_replication_table_statistics(
                aws_client.dms, replication_config_arn
            )["ReplicationTableStatistics"]
            assert len(table_stats) == 3
            for stat in table_stats:
                assert dict_contains_subdict(stat, expected.get(stat["TableName"], {}))
            return table_stats

        res_describe_table_statistics = retry(
            _check_expected_table_stats,
            retries=100 if is_aws_cloud() else 25,
            sleep=5 if is_aws_cloud() else 1,
        )
        snapshot.match("describe-replication-table-statistics", res_describe_table_statistics)

        kinesis_records = retry(
            lambda: get_records_from_shard(
                aws_client.kinesis,
                stream_arn,
                threshold_timestamp=threshold_timestamp,
                expected_count=5
                + 3
                + 1,  # 5 data queries, 3 create table, 1 awsdms_apply_exceptions
            ),
            retries=100,
            sleep=5 if is_aws_cloud() else 1,
        )
        formatted_records = transform_kinesis_data(
            kinesis_records, assert_exec=assert_json_formatting(True)
        )
        # the create-table operation has a server-id in the partition-key which needs to be replaced
        server_id_partition_key = formatted_records[0]["PartitionKey"].split(".")[0]
        snapshot.add_transformer(snapshot.transform.regex(server_id_partition_key, "<server-id>"))

        snapshot.match("kinesis-records", formatted_records)

        # stop the replication
        stop_task = aws_client.dms.stop_replication(ReplicationConfigArn=replication_config_arn)
        snapshot.match("stop_replication", stop_task)

        # Wait until the config is stopped state
        # In the end, the replication config gets deleted by the cleanup fixture
        # AWS automatically deprovisions the resources after it gets stopped
        # the status during the deprovisioning and deleting state is 'deprovisioning'
        retry(
            lambda: assert_dms_replication_config_status(
                aws_client.dms,
                replication_config_arn,
                expected_status="stopped",
            ),
            retries=500 if is_aws_cloud() else 10,
            sleep=2,
        )

    @markers.aws.validated
    @pytest.mark.skipif(condition=not is_aws_cloud(), reason="Not yet implemented")
    @pytest.mark.parametrize(
        "service",
        [
            pytest.param(None, id="without-secret-manager"),
            pytest.param("secretsmanager", id="without-kinesis-streams"),
        ],
    )
    def test_vpc_endpoints(
        self,
        infrastructure,
        aws_client,
        snapshot,
        cleanups,
        service,
        dms_create_replication_config,
        create_vpc_endpoint,
        region_name,
    ):
        snapshot.add_transformer(snapshot.transform.dms_api())
        snapshot.add_transformer(snapshot.transform.key_value("ReplicationConfigIdentifier"))

        outputs = infrastructure.get_stack_outputs(self.STACK_NAME)

        source_arn = outputs["SourceEndpointMySQLArn"]
        target_arn = outputs["TargetEndpointDefaultArn"]

        secret_arn = outputs["MysqlSecretArn"]
        security_group = outputs["SecurityGroup"]

        subnet_ids = outputs["SubnetIds"].split(",")

        if service is not None:
            create_vpc_endpoint(
                VpcId=outputs["VpcId"],
                SubnetIds=subnet_ids,
                SecurityGroupIds=[security_group],
                Services=[f"com.amazonaws.{region_name}.{service}"],
            )

        source_identifier = aws_client.dms.describe_endpoints(
            Filters=[{"Name": "endpoint-arn", "Values": [source_arn]}]
        )["Endpoints"][0]["EndpointIdentifier"]

        target_identifier = aws_client.dms.describe_endpoints(
            Filters=[{"Name": "endpoint-arn", "Values": [target_arn]}]
        )["Endpoints"][0]["EndpointIdentifier"]

        snapshot.add_transformer(snapshot.transform.regex(secret_arn, "<secret-arn>"))
        snapshot.add_transformer(snapshot.transform.regex(source_identifier, "<source-endpoint>"))
        snapshot.add_transformer(snapshot.transform.regex(target_identifier, "<target-endpoint>"))

        replication_subnet_gp = outputs["ReplicationSubnetGroup"]
        az = outputs["AvailabilityZone"]

        compute_config = {
            # TODO: verify output for other combination of values as well
            "MaxCapacityUnits": 1,
            "AvailabilityZone": az,
            "MultiAZ": False,
            "ReplicationSubnetGroupId": replication_subnet_gp,
            "VpcSecurityGroupIds": [security_group],
        }

        replication_config = dms_create_replication_config(
            SourceEndpointArn=source_arn,
            TargetEndpointArn=target_arn,
            ReplicationType="full-load",
            TableMappings=json.dumps(DEFAULT_TABLE_MAPPING),
            ComputeConfig=compute_config,
            ReplicationSettings=json.dumps({"Logging": {"EnableLogging": True}}),
        )

        replication_config_arn = replication_config["ReplicationConfig"]["ReplicationConfigArn"]

        aws_client.dms.start_replication(
            ReplicationConfigArn=replication_config_arn, StartReplicationType="start-replication"
        )

        result = retry(
            lambda: assert_dms_replication_config_status(
                aws_client.dms,
                replication_config_arn,
                expected_status="failed",
            ),
            retries=500 if is_aws_cloud() else 10,
            sleep=60 if is_aws_cloud() else 1,
        )
        snapshot.match("replication-failed-testing-connections", result)


def _run_queries_on_mysql(
    host: str,
    queries: list[str],
    database: str = DB_NAME,
    user: str = USERNAME,
    password: str = USER_PWD,
    port: int = None,
):
    return run_queries_on_mysql(host, queries, database, user, password, port)


SQL_CREATE_AGENTS_TABLE = """CREATE TABLE AGENTS (
                    AGENT_CODE CHAR(6) NOT NULL PRIMARY KEY,
                    AGENT_NAME CHAR(40),
                    WORKING_AREA CHAR(35),
                    COMMISSION FLOAT(10,2),
                    PHONE_NO CHAR(15),
                    COUNTRY VARCHAR(25)
);"""

SQL_CREATE_CUSTOMER_TABLE = """CREATE TABLE CUSTOMER (
                    CUST_CODE VARCHAR(6) NOT NULL PRIMARY KEY,
                    CUST_NAME VARCHAR(40) NOT NULL,
                    CUST_CITY CHAR(35),
                    WORKING_AREA VARCHAR(35) NOT NULL,
                    CUST_COUNTRY VARCHAR(20) NOT NULL,
                    GRADE FLOAT,
                    OPENING_AMT FLOAT(12,2) NOT NULL,
                    RECEIVE_AMT FLOAT(12,2) NOT NULL,
                    PAYMENT_AMT FLOAT(12,2) NOT NULL,
                    OUTSTANDING_AMT FLOAT(12,2) NOT NULL,
                    PHONE_NO VARCHAR(17) NOT NULL,
                    AGENT_CODE CHAR(6) NOT NULL REFERENCES AGENTS
);"""

SQL_CREATE_ORDERS_TABLE = """CREATE TABLE ORDERS (
                    ORD_NUM VARCHAR(7) NOT NULL PRIMARY KEY,
                    ORD_AMOUNT FLOAT(12,2) NOT NULL,
                    ADVANCE_AMOUNT FLOAT(12,2) NOT NULL,
                    ORD_DATE DATE NOT NULL,
                    CUST_CODE VARCHAR(6) NOT NULL REFERENCES CUSTOMER,
                    AGENT_CODE CHAR(6) NOT NULL REFERENCES AGENTS,
                    ORD_DESCRIPTION VARCHAR(60) NOT NULL
);"""


SQL_INSERT_AGENT_SAMPLE_DATA_LIST = [
    """
    INSERT INTO AGENTS
(AGENT_CODE, AGENT_NAME, WORKING_AREA, COMMISSION, PHONE_NO, COUNTRY)
VALUES
('A001', 'Alex ', 'London', '13.00', '075-12458969', 'UK');""",
    """
    INSERT INTO AGENTS
(AGENT_CODE, AGENT_NAME, WORKING_AREA, COMMISSION, PHONE_NO, COUNTRY)
VALUES
('A002', 'Alford', 'New York', '12.00', '044-25874365', 'USA');""",
    """
    INSERT INTO AGENTS
(AGENT_CODE, AGENT_NAME, WORKING_AREA, COMMISSION, PHONE_NO, COUNTRY)
VALUES
('A003', 'Ivan', 'Toronto', '15.00', '008-22544166', 'Canada');""",
    """
    INSERT INTO AGENTS
(AGENT_CODE, AGENT_NAME, WORKING_AREA, COMMISSION, PHONE_NO, COUNTRY)
VALUES
('A004', 'Anderson', 'Mumbai', '14.00', '077-12346674', 'India');""",
]

SQL_INSERT_CUSTOMER_SAMPLE_DATA_LIST = [
    """
    INSERT INTO CUSTOMER
(CUST_CODE, CUST_NAME, CUST_CITY, WORKING_AREA, CUST_COUNTRY, GRADE, OPENING_AMT, RECEIVE_AMT, PAYMENT_AMT, OUTSTANDING_AMT, PHONE_NO, AGENT_CODE)
VALUES
('C0001', 'Holmes', 'London', 'London', 'UK', '2', '6000.00', '5000.00', '7000.00', '4000.00', 'BBBBBBB', 'A001');""",
    """
    INSERT INTO CUSTOMER
(CUST_CODE, CUST_NAME, CUST_CITY, WORKING_AREA, CUST_COUNTRY, GRADE, OPENING_AMT, RECEIVE_AMT, PAYMENT_AMT, OUTSTANDING_AMT, PHONE_NO, AGENT_CODE)
VALUES
('C00002', 'Micheal', 'New York', 'New York', 'USA', '2', '3000.00', '5000.00', '2000.00', '6000.00', 'CCCCCCC', 'A002');""",
    """
    INSERT INTO CUSTOMER
(CUST_CODE, CUST_NAME, CUST_CITY, WORKING_AREA, CUST_COUNTRY, GRADE, OPENING_AMT, RECEIVE_AMT, PAYMENT_AMT, OUTSTANDING_AMT, PHONE_NO, AGENT_CODE)
VALUES
('C00003', 'Albert', 'New York', 'New York', 'USA', '3', '5000.00', '7000.00', '6000.00', '6000.00', 'BBBBSBB', 'A002');""",
]

SQL_INSERT_ORDERS_SAMPLE_DATA_LIST = [
    """
    INSERT INTO ORDERS
(ORD_NUM, ORD_AMOUNT, ADVANCE_AMOUNT, ORD_DATE, CUST_CODE, AGENT_CODE, ORD_DESCRIPTION)
VALUES
('O200100', '1000.00', '600.00', STR_TO_DATE('8/3/2024','%d/%m/%Y'), 'C00002', 'A002', 'SOD');""",
    """
    INSERT INTO ORDERS
(ORD_NUM, ORD_AMOUNT, ADVANCE_AMOUNT, ORD_DATE, CUST_CODE, AGENT_CODE, ORD_DESCRIPTION)
VALUES
('O200101', '3000.00', '500.00', STR_TO_DATE('3/7/2024','%d/%m/%Y'), 'C00003', 'A002', 'SOD');""",
    """
    INSERT INTO ORDERS
(ORD_NUM, ORD_AMOUNT, ADVANCE_AMOUNT, ORD_DATE, CUST_CODE, AGENT_CODE, ORD_DESCRIPTION)
VALUES
('O200102', '4500.00', '900.00', STR_TO_DATE('5/7/2024','%d/%m/%Y'), 'C00001', 'A001', 'SOD');""",
]
