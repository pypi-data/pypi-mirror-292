import logging

import aws_cdk as cdk
import pymysql
import pytest
import requests
from localstack.testing.aws.util import is_aws_cloud
from localstack.testing.pytest import markers
from localstack.utils.sync import retry

LOG = logging.getLogger(__name__)


@markers.acceptance_test
class TestWordpressBlogScenario:
    STACK_NAME = "WordpressStack"
    DB_USER = "wordpress"
    DB_PASSWORD = "wordpress-password"
    DB_NAME = "wordpress"

    @pytest.fixture(scope="class", autouse=True)
    def infrastructure(self, aws_client, infrastructure_setup):
        infra = infrastructure_setup(namespace="WordpressBlog", force_synth=True)
        stack = cdk.Stack(infra.cdk_app, self.STACK_NAME)
        vpc = cdk.aws_ec2.Vpc(
            stack,
            "VPC",
            nat_gateways=1,
            create_internet_gateway=True,
            enable_dns_hostnames=True,
            enable_dns_support=True,
            cidr="10.0.0.0/16",
            subnet_configuration=[
                cdk.aws_ec2.SubnetConfiguration(
                    name="public", subnet_type=cdk.aws_ec2.SubnetType.PUBLIC, cidr_mask=24
                ),
                cdk.aws_ec2.SubnetConfiguration(
                    name="private",
                    subnet_type=cdk.aws_ec2.SubnetType.PRIVATE_WITH_EGRESS,
                    cidr_mask=24,
                ),
            ],
        )
        security_group = cdk.aws_ec2.SecurityGroup(
            stack,
            "cluster-sec-group",
            security_group_name="cluster-sec-group",
            vpc=vpc,
            allow_all_outbound=True,
        )

        database = cdk.aws_rds.DatabaseInstance(
            stack,
            "WordpressDatabase",
            credentials=cdk.aws_rds.Credentials.from_password(
                username=self.DB_USER, password=cdk.SecretValue.unsafe_plain_text(self.DB_PASSWORD)
            ),
            database_name=self.DB_NAME,
            engine=cdk.aws_rds.DatabaseInstanceEngine.MYSQL,
            vpc=vpc,
            publicly_accessible=True,  # For testing purposes, make the database publicly accessible
            removal_policy=cdk.RemovalPolicy.DESTROY,
            security_groups=[security_group],
            vpc_subnets=cdk.aws_ec2.SubnetSelection(subnets=vpc.public_subnets),
        )

        # ECS cluster
        cluster = cdk.aws_ecs.Cluster(stack, "ServiceCluster", vpc=vpc)

        wp_health_check = cdk.aws_ecs.HealthCheck(
            command=[
                "CMD-SHELL",
                'curl -s -o /dev/null -w "%{http_code}" http://localhost | grep -qE "200|301|302"',
            ],
            start_period=cdk.Duration.minutes(2),
        )

        log_group = cdk.aws_logs.LogGroup(
            stack,
            "WordpressLogGroup",
            removal_policy=cdk.RemovalPolicy.DESTROY,
            retention=cdk.aws_logs.RetentionDays.ONE_DAY,
        )

        docker_image = cdk.aws_ecs.ContainerImage.from_registry("wordpress")
        web_service = cdk.aws_ecs_patterns.ApplicationLoadBalancedFargateService(
            stack,
            "Wordpress",
            cluster=cluster,
            target_protocol=cdk.aws_elasticloadbalancingv2.ApplicationProtocol.HTTP,
            protocol=cdk.aws_elasticloadbalancingv2.ApplicationProtocol.HTTP,
            health_check=wp_health_check,
            desired_count=1,
            cpu=512,
            memory_limit_mib=2048,
            task_image_options=cdk.aws_ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
                image=docker_image,
                container_port=80,
                container_name="webapp",
                enable_logging=True,
                log_driver=cdk.aws_ecs.LogDriver.aws_logs(
                    stream_prefix="Wordpress", log_group=log_group
                ),
                environment={
                    "WORDPRESS_DB_HOST": f"{database.db_instance_endpoint_address}:{database.db_instance_endpoint_port}",
                    "WORDPRESS_DB_USER": self.DB_USER,
                    "WORDPRESS_DB_PASSWORD": self.DB_PASSWORD,
                    "WORDPRESS_DB_NAME": self.DB_NAME,
                },
            ),
        )

        web_service.target_group.configure_health_check(
            path="/index.php",
            healthy_http_codes="200,301,302",
            interval=cdk.Duration.seconds(120),
            unhealthy_threshold_count=10,
        )
        database_port = cdk.Token.as_number(database.db_instance_endpoint_port)

        security_group.connections.allow_from(
            port_range=cdk.aws_ec2.Port.tcp_range(database_port, database_port),
            other=web_service.service.connections,
        )

        # For testing purposes, allow all traffic to the database
        database.connections.allow_from(
            port_range=cdk.aws_ec2.Port.tcp_range(database_port, database_port),
            other=cdk.aws_ec2.Peer.any_ipv4(),
        )

        cdk.CfnOutput(stack, "WordpressURL", value=web_service.load_balancer.load_balancer_dns_name)
        cdk.CfnOutput(
            stack, "WordpressDatabaseEndpoint", value=database.db_instance_endpoint_address
        )
        cdk.CfnOutput(stack, "WordpressDatabasePort", value=database.db_instance_endpoint_port)
        cdk.CfnOutput(stack, "DBInstanceIdentifier", value=database.instance_identifier)
        cdk.CfnOutput(stack, "WordpressLogGroupName", value=log_group.log_group_name)

        with infra.provisioner() as prov:
            yield prov

    @markers.aws.validated
    def test_get_wordpress(self, infrastructure, aws_client):
        endpoint = infrastructure.get_stack_outputs(self.STACK_NAME)["WordpressURL"]

        url = f"http://{endpoint.lower()}"
        if not is_aws_cloud():
            url += ":4566"

        def assert_status_code():
            response = requests.get(url)

            assert response.status_code == 200
            assert "WordPress" in response.text

        retry(assert_status_code)

    @markers.aws.validated
    def test_db_connection(self, infrastructure):
        db_endpoint = infrastructure.get_stack_outputs(self.STACK_NAME)["WordpressDatabaseEndpoint"]
        db_port = infrastructure.get_stack_outputs(self.STACK_NAME)["WordpressDatabasePort"]

        db_config = {
            "user": self.DB_USER,
            "password": self.DB_PASSWORD,
            "host": db_endpoint,
            "port": int(db_port),
            "database": self.DB_NAME,
            "cursorclass": pymysql.cursors.DictCursor,
        }

        def assert_db_connection():
            connection = None
            try:
                connection = pymysql.connect(**db_config)
                assert connection is not None
            finally:
                if connection:
                    connection.close()

        retry(assert_db_connection)

    @markers.aws.validated
    def test_cloudwatch_logs(self, infrastructure, aws_client):
        log_group_name = infrastructure.get_stack_outputs(self.STACK_NAME)["WordpressLogGroupName"]

        def check_log_streams():
            log_streams = aws_client.logs.describe_log_streams(logGroupName=log_group_name)[
                "logStreams"
            ]
            assert len(log_streams) > 0

        retry(check_log_streams, sleep=1, retries=30)

        log_stream_name = aws_client.logs.describe_log_streams(logGroupName=log_group_name)[
            "logStreams"
        ][0]["logStreamName"]

        def check_log_events():
            log_events = aws_client.logs.get_log_events(
                logGroupName=log_group_name, logStreamName=log_stream_name
            )["events"]
            assert len(log_events) > 0

        retry(check_log_events, sleep=1, retries=30)
