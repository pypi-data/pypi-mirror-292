import json
import logging

import aws_cdk as cdk
import aws_cdk.aws_ec2 as ec2
import aws_cdk.aws_iam as iam
import aws_cdk.aws_kinesis as kinesis
import aws_cdk.aws_kinesisfirehose as firehose
import aws_cdk.aws_logs as logs
import aws_cdk.aws_redshift as redshift
import aws_cdk.aws_s3 as s3
import pytest
from localstack.testing.pytest import markers

from tests.aws.scenario.kinesis_firehose_redshift.helper_functions import (
    get_expected_data_from_redshift_table,
    redshift_connection_handler,
)

LOG = logging.getLogger(__name__)

STACK_NAME_1 = "KinesisFirehoseRedshiftStack1"
STACK_NAME_2 = "KinesisFirehoseRedshiftStack2"
REDSHIFT_DEFAULT_PORT = 5439
REDSHIFT_DB_NAME = "streaming_db"
TABLE_NAME = "user_health_data"

REDSHIFT_MASTER_USER = "dwh_user"
REDSHIFT_MASTER_PASSWORD = "123456789Test"

SAMPLE_USERS = [
    {
        "user_id": "u14a86cdc",
        "name": "Ernst Meier",
        "age": 32,
        "country": "Austria",
        "device_id": "d49b32oed",
        "hr_value": 110,
        "novel_stress_marker": 112.5,
        "timestamp": "2021-10-01 12:00:00",
    },
    {
        "user_id": "u5d34196b",
        "name": "Jane Smith",
        "age": 33,
        "country": "Canada",
        "device_id": "d39d39dp3",
        "hr_value": 110,
        "novel_stress_marker": 112.5,
        "timestamp": "2021-10-01 12:00:00",
    },
    {
        "user_id": "u5fd277a6",
        "name": "Emily Jones",
        "age": 20,
        "country": "USA",
        "device_id": "d39d39dp3",
        "hr_value": 110,
        "novel_stress_marker": 112.5,
        "timestamp": "2021-10-01 12:00:00",
    },
]

SAMPLE_USER_DTYPES = {
    "user_id": "VARCHAR(10)",
    "name": "VARCHAR(255)",
    "age": "INT",
    "country": "VARCHAR(50)",
    "device_id": "VARCHAR(10)",
    "hr_value": "INT",
    "novel_stress_marker": "DECIMAL(10, 2)",
    "timestamp": "TIMESTAMP",
}


class TestKinesisFirehoseScenario:
    @pytest.fixture(scope="class", autouse=True)
    def infrastructure(self, infrastructure_setup):
        infra = infrastructure_setup(
            namespace="MultiStackDeploymentKinesisFirehoseRedshift", force_synth=True
        )
        stack_1 = cdk.Stack(infra.cdk_app, STACK_NAME_1)
        stack_2 = cdk.Stack(infra.cdk_app, STACK_NAME_2)

        # kinesis stream
        kinesis_stream = kinesis.Stream(
            stack_1,
            "KinesisStream",
            stream_name="kinesis-stream",
            shard_count=1,
            stream_mode=kinesis.StreamMode("PROVISIONED"),
        )

        # s3 bucket
        bucket = s3.Bucket(
            stack_1,
            "S3Bucket",
            bucket_name="firehose-raw-data",
            removal_policy=cdk.RemovalPolicy.DESTROY,  # required since default value is RETAIN
            # auto_delete_objects=True,  # required to delete the not empty bucket
            # auto_delete requires lambda therefore not supported currently by LocalStack
        )

        # redshift s3 access role
        role_redshift_cluster = iam.Role(
            stack_1,
            "RedshiftClusterRole",
            role_name="redshift-cluster-role",
            assumed_by=iam.ServicePrincipal("redshift.amazonaws.com"),
        )
        bucket.grant_read(role_redshift_cluster)

        # create vpc for redshift cluster
        redshift_vpc = ec2.Vpc(
            stack_1,
            "RedshiftVpc",
            vpc_name="redshift-vpc",
            ip_addresses=ec2.IpAddresses.cidr("10.10.0.0/16"),
            max_azs=1,
            nat_gateways=1,
            enable_dns_support=True,
            enable_dns_hostnames=True,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="public", cidr_mask=24, subnet_type=ec2.SubnetType.PUBLIC
                ),
            ],
        )

        redshift_vpc_subnet_ids = redshift_vpc.select_subnets(
            subnet_type=ec2.SubnetType.PUBLIC
        ).subnet_ids

        # create subnet group for redshift cluster
        redshift_cluster_subnet_group = redshift.CfnClusterSubnetGroup(
            stack_1,
            "RedshiftClusterSubnetGroup",
            subnet_ids=redshift_vpc_subnet_ids,
            description="Redshift Cluster Subnet Group",
        )

        # crete security group to allow inbound traffic
        redshift_security_group = ec2.SecurityGroup(
            stack_1,
            "RedshiftSecurityGroup",
            vpc=redshift_vpc,
            security_group_name="redshift-security-group",
            description="Security group for redshift cluster",
            allow_all_outbound=True,
        )
        redshift_security_group.add_ingress_rule(
            ec2.Peer.any_ipv4(),
            ec2.Port.tcp(REDSHIFT_DEFAULT_PORT),  # allow redshift port
        )
        redshift_security_group.add_ingress_rule(
            ec2.Peer.any_ipv4(),
            ec2.Port.tcp(22),  # allow ssh,
        )

        # create redshift cluster
        redshift_cluster_name = "redshift-cluster"
        ec2_instance_type = "dc2.large"
        # using L1 construct, since the L2 alpha construct described public accessibility implementation did not work
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_redshift_alpha/README.html
        redshift_cluster = redshift.CfnCluster(
            stack_1,
            "RedshiftCluster",
            cluster_identifier=redshift_cluster_name,
            cluster_type="single-node",
            number_of_nodes=1,
            db_name=REDSHIFT_DB_NAME,
            master_username=REDSHIFT_MASTER_USER,
            master_user_password=REDSHIFT_MASTER_PASSWORD,
            iam_roles=[role_redshift_cluster.role_arn],
            node_type=f"{ec2_instance_type}",
            cluster_subnet_group_name=redshift_cluster_subnet_group.ref,
            vpc_security_group_ids=[redshift_security_group.security_group_id],
            publicly_accessible=True,
            # port=REDSHIFT_DEFAULT_PORT,
        )

        # firehose delivery stream kinesis access role
        role_firehose_kinesis = iam.Role(
            stack_1,
            "FirehoseKinesisRole",
            role_name="firehose-kinesis-role",
            assumed_by=iam.ServicePrincipal("firehose.amazonaws.com"),
        )
        kinesis_stream.grant_read(role_firehose_kinesis)

        # firehose kinesis stream source configuration
        kinesis_stream_source_configuration = (
            firehose.CfnDeliveryStream.KinesisStreamSourceConfigurationProperty(
                kinesis_stream_arn=kinesis_stream.stream_arn,
                role_arn=role_firehose_kinesis.role_arn,
            )
        )

        # cloud watch logging group and stream for firehose s3 error logging
        firehose_s3_log_group_name = "firehose-s3-log-group"
        firehose_s3_log_stream_name = "firehose-s3-log-stream"
        firehose_s3_log_group = logs.LogGroup(
            stack_1,
            "FirehoseLogGroup",
            log_group_name=firehose_s3_log_group_name,
            removal_policy=cdk.RemovalPolicy.DESTROY,  # required since default value is RETAIN
        )
        firehose_s3_log_group.add_stream(
            "FirehoseLogStream", log_stream_name=firehose_s3_log_stream_name
        )

        # firehose s3 access role
        role_firehose_s3 = iam.Role(
            stack_1,
            "FirehoseS3Role",
            role_name="firehose-s3-role",
            assumed_by=iam.ServicePrincipal("firehose.amazonaws.com"),
        )
        bucket.grant_read_write(role_firehose_s3)
        firehose_s3_log_group.grant_write(role_firehose_s3)

        # firehose redshift destination configuration
        redshift_s3_destination_configuration = firehose.CfnDeliveryStream.S3DestinationConfigurationProperty(
            bucket_arn=bucket.bucket_arn,
            role_arn=role_firehose_s3.role_arn,
            prefix="redshift-raw-data/",
            # error_output_prefix="firehose-raw-data/errors/", # not yet supported by AWS although in the documentation
            compression_format="UNCOMPRESSED",
            buffering_hints=firehose.CfnDeliveryStream.BufferingHintsProperty(
                interval_in_seconds=1, size_in_m_bs=1
            ),
            encryption_configuration=firehose.CfnDeliveryStream.EncryptionConfigurationProperty(
                no_encryption_config="NoEncryption"
            ),
            cloud_watch_logging_options=firehose.CfnDeliveryStream.CloudWatchLoggingOptionsProperty(
                enabled=True,
                log_group_name=firehose_s3_log_group_name,
                log_stream_name=firehose_s3_log_stream_name,
            ),
        )
        redshift_cluster_address = redshift_cluster.get_att(
            "Endpoint.Address"
        ).to_string()  # redshift_cluster.attr_endpoint_address
        redshift_destination_configuration = firehose.CfnDeliveryStream.RedshiftDestinationConfigurationProperty(
            cluster_jdbcurl=f"jdbc:redshift://{redshift_cluster_address}:{REDSHIFT_DEFAULT_PORT}/{REDSHIFT_DB_NAME}",
            copy_command=firehose.CfnDeliveryStream.CopyCommandProperty(
                data_table_name=TABLE_NAME,
                copy_options="json 'auto' blanksasnull emptyasnull",
                # for reference of copy command options https://docs.aws.amazon.com/redshift/latest/dg/r_COPY_command_examples.html#r_COPY_command_examples-copy-from-json
                # MANIFEST json 'auto' blanksasnull emptyasnull;" required for firehose data,
                data_table_columns=f"{','.join(SAMPLE_USER_DTYPES.keys())}",
                # keys in json file from keys in kinesis input must be lower case
            ),
            password=REDSHIFT_MASTER_PASSWORD,
            username=REDSHIFT_MASTER_USER,
            role_arn=role_firehose_s3.role_arn,
            s3_configuration=redshift_s3_destination_configuration,
            cloud_watch_logging_options=firehose.CfnDeliveryStream.CloudWatchLoggingOptionsProperty(
                enabled=True,
                log_group_name=firehose_s3_log_group_name,
                log_stream_name=firehose_s3_log_stream_name,
            ),
        )

        # using L1 construct to create firehose delivery stream, since the L2 alpha constructs connection to Redshift did not work
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_kinesisfirehose_alpha/DeliveryStream.html
        firehose_stream = firehose.CfnDeliveryStream(
            stack_2,
            "FirehoseDeliveryStream",
            delivery_stream_name="firehose-deliverystream",
            delivery_stream_type="KinesisStreamAsSource",
            kinesis_stream_source_configuration=kinesis_stream_source_configuration,
            redshift_destination_configuration=redshift_destination_configuration,
        )

        # specify resource outputs
        redshift_cluster_port = redshift_cluster.get_att("Endpoint.Port").to_string()
        cdk.CfnOutput(stack_1, "KinesisStreamName", value=kinesis_stream.stream_name)
        cdk.CfnOutput(stack_1, "BucketName", value=bucket.bucket_name)
        cdk.CfnOutput(stack_1, "RedshiftClusterName", value=redshift_cluster.cluster_identifier)
        cdk.CfnOutput(
            stack_1,
            "RedshiftClusterAddress",
            value=redshift_cluster_address,
        )  # redshift_cluster.attr_endpoint_address)
        cdk.CfnOutput(
            stack_1, "RedshiftClusterPort", value=redshift_cluster_port
        )  # redshift_cluster.attr_endpoint_port)
        cdk.CfnOutput(
            stack_2, "FirehoseDeliveryStreamName", value=firehose_stream.delivery_stream_name
        )

        with infra.provisioner() as prov:
            yield prov

    @pytest.fixture(scope="class", autouse=True)
    def setup_redshift(self, infrastructure):
        outputs_1 = infrastructure.get_stack_outputs(STACK_NAME_1)
        redshift_cluster_address = outputs_1["RedshiftClusterAddress"]
        redshift_cluster_port = outputs_1["RedshiftClusterPort"]

        # prepare redshift table
        LOG.debug("Create redshift table")
        connection_string = f"dbname={REDSHIFT_DB_NAME} user={REDSHIFT_MASTER_USER} password={REDSHIFT_MASTER_PASSWORD} host={redshift_cluster_address} port={redshift_cluster_port}"

        create_table_sql = f"""
                            CREATE TABLE {TABLE_NAME} (
                            user_id {SAMPLE_USER_DTYPES["user_id"]},
                            name {SAMPLE_USER_DTYPES["name"]},
                            age {SAMPLE_USER_DTYPES["age"]} ,
                            country {SAMPLE_USER_DTYPES["country"]},
                            device_id {SAMPLE_USER_DTYPES["device_id"]},
                            hr_value {SAMPLE_USER_DTYPES["hr_value"]},
                            novel_stress_marker {SAMPLE_USER_DTYPES["novel_stress_marker"]},
                            timestamp {SAMPLE_USER_DTYPES["timestamp"]}
                        );
                    """

        response = redshift_connection_handler(connection_string, create_table_sql)

        yield

        # empty s3 bucket
        # do not empty if additional redshift COPY commands are expected, since redshift tracks all files in the bucket

    @markers.aws.validated
    def test_kinesis_firehose_redshift(
        self,
        infrastructure,
        aws_client,
        snapshot,
    ):
        outputs_1 = infrastructure.get_stack_outputs(STACK_NAME_1)
        outputs_2 = infrastructure.get_stack_outputs(STACK_NAME_2)
        kinesis_stream_name = outputs_1["KinesisStreamName"]
        bucket_name = outputs_1["BucketName"]
        redshift_cluster_address = outputs_1["RedshiftClusterAddress"]
        redshift_cluster_port = outputs_1["RedshiftClusterPort"]

        # send data to kinesis stream
        for sample_user in SAMPLE_USERS:
            aws_client.kinesis.put_record(
                StreamName=kinesis_stream_name,
                Data=json.dumps(sample_user),
                PartitionKey="1",
            )

        # Todo: add s3 test dealing with raw and manifest files

        # read data from redshift
        connection_string = f"dbname={REDSHIFT_DB_NAME} user={REDSHIFT_MASTER_USER} password={REDSHIFT_MASTER_PASSWORD} host={redshift_cluster_address} port={redshift_cluster_port}"
        sql_query = f"""
                    SELECT
                        *
                    FROM
                        {TABLE_NAME}
                    """

        df_user_health_data = get_expected_data_from_redshift_table(
            connection_string, sql_query, len(SAMPLE_USERS), retries=30, sleep=10
        )
        snapshot.match("redshift", df_user_health_data.to_dict("records"))
