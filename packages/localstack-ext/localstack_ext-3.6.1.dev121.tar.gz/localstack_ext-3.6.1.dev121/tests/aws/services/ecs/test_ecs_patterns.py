import json
import os.path
import socket

import aws_cdk as cdk
import pytest
import requests
from localstack.config import LOCALSTACK_HOST
from localstack.testing.aws.util import is_aws_cloud
from localstack.testing.pytest import markers
from localstack.testing.scenario.cdk_lambda_helper import generate_ecr_image_from_dockerfile
from localstack.utils.sync import retry, wait_until

from tests.aws.services.ecs.test_ecs import using_kubernetes_executor


class TestEcsFargateApplicationLoadBalanced:
    @pytest.fixture(scope="class", autouse=True)
    def infrastructure(self, infrastructure_setup):
        # create infra provisioner
        infra = infrastructure_setup(namespace="EcsSample")

        # create a stack
        stack = cdk.Stack(infra.cdk_app, "EcsFargateAppPatternsStack")

        task_def = cdk.aws_ecs.FargateTaskDefinition(
            stack,
            "TaskDef",
        )

        container = task_def.add_container(
            "Container",
            image=cdk.aws_ecs.ContainerImage.from_registry("nginx"),
            logging=cdk.aws_ecs.LogDrivers.aws_logs(stream_prefix="nginx"),
        )

        container.add_port_mappings(
            cdk.aws_ecs.PortMapping(container_port=80, protocol=cdk.aws_ecs.Protocol.TCP)
        )

        cdk.aws_ecs_patterns.ApplicationLoadBalancedFargateService(
            stack, "appLbFargate", task_definition=task_def
        )

        # you can use the contextmanager to make sure the cleanup works automatically
        with infra.provisioner() as prov:
            yield prov

    @markers.aws.validated
    def test_service_deployment(
        self,
        infrastructure,
    ):
        outputs = infrastructure.get_stack_outputs("EcsFargateAppPatternsStack")
        app_lb_fargateservice_url = next(
            (value for key, value in outputs.items() if key.startswith("appLbFargateServiceURL")),
            None,
        )

        if not is_aws_cloud():
            app_lb_fargateservice_url = f"{app_lb_fargateservice_url}:{LOCALSTACK_HOST.port}"

        response = requests.get(app_lb_fargateservice_url)
        assert response.status_code == 200


class TestEcsQueueProccesingPattern:
    @pytest.fixture(scope="class", autouse=True)
    def infrastructure(self, infrastructure_setup):
        # create infra provisioner
        infra = infrastructure_setup(namespace="EcsSample")

        # create a stack
        stack = cdk.Stack(infra.cdk_app, "QueueProccessingStack")

        task_def = cdk.aws_ecs.FargateTaskDefinition(
            stack,
            "TaskDef",
        )

        container = task_def.add_container(
            "Container",
            image=cdk.aws_ecs.ContainerImage.from_registry("nginx"),
            logging=cdk.aws_ecs.LogDrivers.aws_logs(stream_prefix="nginx"),
        )

        container.add_port_mappings(
            cdk.aws_ecs.PortMapping(container_port=80, protocol=cdk.aws_ecs.Protocol.TCP)
        )

        cdk.aws_ecs_patterns.QueueProcessingFargateService(
            stack, "queueProccessingFargate", task_definition=task_def
        )

        # you can use the contextmanager to make sure the cleanup works automatically
        with infra.provisioner() as prov:
            yield prov

    @markers.aws.validated
    def test_queue_proccessing(self, infrastructure, aws_client):
        outputs = infrastructure.get_stack_outputs("QueueProccessingStack")

        proccesing_queue = next(
            (
                value
                for key, value in outputs.items()
                if key.startswith("queueProccessingFargateSQSQueue") and "Arn" not in key
            ),
            None,
        )

        queue_url = aws_client.sqs.get_queue_url(QueueName=proccesing_queue)["QueueUrl"]
        aws_client.sqs.send_message(
            QueueUrl=queue_url, MessageBody="Hello, this is a test message."
        )

        def _assert_message_is_proccessed():
            response = aws_client.sqs.get_queue_attributes(
                QueueUrl=queue_url, AttributeNames=["ApproximateNumberOfMessages"]
            )
            num_messages = int(response["Attributes"]["ApproximateNumberOfMessages"])
            assert num_messages == 0

        wait_until(_assert_message_is_proccessed, wait=2, max_retries=60 if is_aws_cloud() else 5)


class TestEcsNetworkLoadBalancedFargate:
    @pytest.fixture(scope="class", autouse=True)
    def infrastructure(self, infrastructure_setup):
        infra = infrastructure_setup(namespace="EcsSample")
        stack = cdk.Stack(infra.cdk_app, "EcsNetworkPatternsStack")

        vpc = cdk.aws_ec2.Vpc(stack, "MyVpc", max_azs=2)

        cluster = cdk.aws_ecs.Cluster(stack, "cluster", vpc=vpc)

        service = cdk.aws_ecs_patterns.NetworkLoadBalancedFargateService(
            stack,
            "networkLbFargate",
            cluster=cluster,
            task_image_options=cdk.aws_ecs_patterns.NetworkLoadBalancedTaskImageOptions(
                image=cdk.aws_ecs.ContainerImage.from_registry("amazon/amazon-ecs-sample")
            ),
        )
        service.service.connections.security_groups[0].add_ingress_rule(
            peer=cdk.aws_ec2.Peer.ipv4(vpc.vpc_cidr_block),
            connection=cdk.aws_ec2.Port.tcp(80),
            description="Allow http inbound from VPC",
        )

        with infra.provisioner() as prov:
            yield prov

    @markers.aws.validated
    def test_port_connection(self, infrastructure, snapshot):
        outputs = infrastructure.get_stack_outputs("EcsNetworkPatternsStack")
        dns_domain = next(
            (
                value
                for key, value in outputs.items()
                if key.startswith("networkLbFargateLoadBalancer")
            ),
            None,
        )
        port = 80 if is_aws_cloud() else LOCALSTACK_HOST.port
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (dns_domain, port)
        connected = False
        try:
            sock.connect(server_address)
            connected = True
        except socket.error as e:
            print(f"Failed to connect: {e}")
        finally:
            sock.close()

        assert connected


class TestEcsNetworkLoadBalancedTargetGroupsFargate:
    @pytest.fixture(scope="class", autouse=True)
    def infrastructure(self, infrastructure_setup):
        infra = infrastructure_setup(namespace="EcsSample")
        stack = cdk.Stack(infra.cdk_app, "EcsNetworkTGPatternsStack")

        vpc = cdk.aws_ec2.Vpc(stack, "MyVpc", max_azs=2)

        cluster = cdk.aws_ecs.Cluster(stack, "cluster", vpc=vpc)

        service = cdk.aws_ecs_patterns.NetworkMultipleTargetGroupsFargateService(
            stack,
            "networkTGFargate",
            cluster=cluster,
            task_image_options=cdk.aws_ecs_patterns.NetworkLoadBalancedTaskImageProps(
                image=cdk.aws_ecs.ContainerImage.from_registry("amazon/amazon-ecs-sample")
            ),
        )
        service.service.connections.security_groups[0].add_ingress_rule(
            peer=cdk.aws_ec2.Peer.ipv4(vpc.vpc_cidr_block),
            connection=cdk.aws_ec2.Port.tcp(80),
            description="Allow http inbound from VPC",
        )

        with infra.provisioner() as prov:
            yield prov

    @markers.aws.validated
    def test_port_connection(self, infrastructure, snapshot):
        outputs = infrastructure.get_stack_outputs("EcsNetworkTGPatternsStack")
        dns_domain = next(
            (
                value
                for key, value in outputs.items()
                if key.startswith("networkTGFargateLoadBalancer")
            ),
            None,
        )
        port = 80 if is_aws_cloud() else LOCALSTACK_HOST.port
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (dns_domain, port)
        connected = False
        try:
            sock.connect(server_address)
            connected = True
        except socket.error as e:
            print(f"Failed to connect: {e}")
        finally:
            sock.close()

        assert connected


class TestEcsFirelensStackFluentBit:
    STACK_NAME = "EcsFirelensStackFluentBit"

    @pytest.fixture(scope="class")
    def infrastructure(self, infrastructure_setup, aws_client):
        infra = infrastructure_setup(namespace="EcsSample")

        stack = cdk.Stack(infra.cdk_app, self.STACK_NAME)
        kinesis_stream = cdk.aws_kinesis.Stream(
            stack, "LogStream", removal_policy=cdk.RemovalPolicy.DESTROY
        )
        task_role = cdk.aws_iam.Role(
            stack, "TaskRole", assumed_by=cdk.aws_iam.ServicePrincipal("ecs-tasks.amazonaws.com")
        )
        kinesis_stream.grant_write(task_role)

        execution_role = cdk.aws_iam.Role(
            stack,
            "ExecutionRole",
            assumed_by=cdk.aws_iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
        )

        execution_role.add_managed_policy(
            cdk.aws_iam.ManagedPolicy.from_aws_managed_policy_name("CloudWatchLogsFullAccess")
        )

        vpc = cdk.aws_ec2.Vpc(stack, "Vpc", max_azs=3)
        cluster = cdk.aws_ecs.Cluster(stack, "Cluster", vpc=vpc)

        task_definition = cdk.aws_ecs.FargateTaskDefinition(
            stack, "TaskDef", execution_role=execution_role, task_role=task_role
        )

        task_definition.add_container(
            "AppContainer",
            image=cdk.aws_ecs.ContainerImage.from_registry("debian"),
            logging=cdk.aws_ecs.LogDrivers.firelens(
                options={
                    "Name": "kinesis",
                    "region": cdk.Aws.REGION,
                    "stream": kinesis_stream.stream_name,
                }
            ),
            command=["bash", "-c", 'while :; do echo "test log"; sleep 2; done'],
        )

        fluent_log_group = cdk.aws_logs.LogGroup(stack, "FluentBitLogGroup")

        task_definition.add_firelens_log_router(
            "FireLensContainer",
            firelens_config=cdk.aws_ecs.FirelensConfig(
                type=cdk.aws_ecs.FirelensLogRouterType.FLUENTBIT,
            ),
            image=cdk.aws_ecs.ContainerImage.from_registry("amazon/aws-for-fluent-bit:stable"),
            memory_limit_mib=256,
            logging=cdk.aws_ecs.LogDrivers.aws_logs(
                stream_prefix="FireLensTestLog",
                log_group=fluent_log_group,
                mode=cdk.aws_ecs.AwsLogDriverMode.NON_BLOCKING,
                max_buffer_size=cdk.Size.mebibytes(25),
            ),
        )

        cdk.aws_ecs.FargateService(
            stack, "Service", cluster=cluster, task_definition=task_definition
        )

        cdk.CfnOutput(stack, "FireLensLogGroupName", value=fluent_log_group.log_group_name)
        cdk.CfnOutput(stack, "KinesisStreamName", value=kinesis_stream.stream_name)

        with infra.provisioner(skip_teardown=False) as prov:
            yield prov

    @markers.aws.validated
    @pytest.mark.skipif(
        condition=using_kubernetes_executor(),
        reason="Firelens not supported in kubernetes yet",
    )
    def test_log_emission(self, infrastructure, aws_client):
        outputs = infrastructure.get_stack_outputs(self.STACK_NAME)
        firelens_log_group = outputs["FireLensLogGroupName"]
        kinesis_stream_name = outputs["KinesisStreamName"]

        def _assert_fluentbit_logs():
            firelens_logs = get_log_group_logs(aws_client, firelens_log_group)
            assert any("listening on" in log for log in firelens_logs)

        retry(_assert_fluentbit_logs, retries=10, sleep=1)

        iterator = get_shard_iterator(kinesis_stream_name, aws_client.kinesis)

        def _get_records():
            nonlocal iterator
            response = aws_client.kinesis.get_records(ShardIterator=iterator)
            iterator = response["NextShardIterator"]
            json_records = response["Records"]
            assert len(json_records) > 0
            return json_records

        json_records = retry(_get_records, retries=10, sleep=2)
        first_log = json.loads(json_records[0]["Data"].decode().replace("", ""))
        assert "test log" == first_log["log"]


class TestEcsFirelensStackFluentD:
    STACK_NAME = "EcsFirelensStackFluentD"
    ECR_FLUENTD_REPOSITORY = "firelens-fluentd-repository"

    @pytest.fixture(scope="class")
    def infrastructure(self, infrastructure_setup, aws_client):
        infra = infrastructure_setup(namespace="EcsSample")

        infra.add_custom_setup(
            lambda: generate_ecr_image_from_dockerfile(
                aws_client.ecr,
                self.ECR_FLUENTD_REPOSITORY,
                os.path.join(os.path.dirname(__file__), "fluentd-image/Dockerfile"),
            )
        )
        infra.add_custom_teardown(
            cleanup_task=lambda: aws_client.ecr.delete_repository(
                repositoryName=self.ECR_FLUENTD_REPOSITORY, force=True
            )
        )

        stack = cdk.Stack(infra.cdk_app, self.STACK_NAME)
        kinesis_stream = cdk.aws_kinesis.Stream(
            stack, "LogStream", removal_policy=cdk.RemovalPolicy.DESTROY
        )
        task_role = cdk.aws_iam.Role(
            stack, "TaskRole", assumed_by=cdk.aws_iam.ServicePrincipal("ecs-tasks.amazonaws.com")
        )
        kinesis_stream.grant_write(task_role)

        execution_role = cdk.aws_iam.Role(
            stack,
            "ExecutionRole",
            assumed_by=cdk.aws_iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
        )

        execution_role.add_managed_policy(
            cdk.aws_iam.ManagedPolicy.from_aws_managed_policy_name("CloudWatchLogsFullAccess")
        )

        vpc = cdk.aws_ec2.Vpc(stack, "Vpc", max_azs=3)
        cluster = cdk.aws_ecs.Cluster(stack, "Cluster", vpc=vpc)

        task_definition = cdk.aws_ecs.FargateTaskDefinition(
            stack, "TaskDef", execution_role=execution_role, task_role=task_role
        )

        repository = cdk.aws_ecr.Repository.from_repository_name(
            stack, "FluentdRepository", self.ECR_FLUENTD_REPOSITORY
        )
        image = cdk.aws_ecs.ContainerImage.from_ecr_repository(repository)

        task_definition.add_container(
            "AppContainer",
            image=cdk.aws_ecs.ContainerImage.from_registry("debian"),
            logging=cdk.aws_ecs.LogDrivers.firelens(
                options={
                    "region": cdk.Aws.REGION,
                    "stream_name": kinesis_stream.stream_name,
                    "@type": "kinesis_streams",
                }
            ),
            command=["bash", "-c", 'while :; do echo "test log"; sleep 1; done'],
        )

        fluent_log_group = cdk.aws_logs.LogGroup(stack, "FluentDLogGroup")

        task_definition.add_firelens_log_router(
            "FireLensContainer",
            firelens_config=cdk.aws_ecs.FirelensConfig(
                type=cdk.aws_ecs.FirelensLogRouterType.FLUENTD,
            ),
            image=image,
            memory_limit_mib=256,
            logging=cdk.aws_ecs.LogDrivers.aws_logs(
                stream_prefix="FireLensTestLog",
                log_group=fluent_log_group,
                mode=cdk.aws_ecs.AwsLogDriverMode.NON_BLOCKING,
                max_buffer_size=cdk.Size.mebibytes(25),
            ),
        )

        cdk.aws_ecs.FargateService(
            stack, "Service", cluster=cluster, task_definition=task_definition
        )

        cdk.CfnOutput(stack, "FireLensLogGroupName", value=fluent_log_group.log_group_name)
        cdk.CfnOutput(stack, "KinesisStreamName", value=kinesis_stream.stream_name)

        with infra.provisioner(skip_teardown=False) as prov:
            yield prov

    @markers.aws.validated
    @pytest.mark.skipif(
        condition=using_kubernetes_executor(),
        reason="Firelens not supported in kubernetes yet",
    )
    def test_log_emission(self, infrastructure, aws_client):
        outputs = infrastructure.get_stack_outputs(self.STACK_NAME)
        firelens_log_group = outputs["FireLensLogGroupName"]
        kinesis_stream_name = outputs["KinesisStreamName"]

        def _assert_fluentd_logs():
            firelens_logs = get_log_group_logs(aws_client, firelens_log_group)
            assert any("listening port port=" in log for log in firelens_logs)

        retry(_assert_fluentd_logs, retries=10, sleep=1)

        iterator = get_shard_iterator(kinesis_stream_name, aws_client.kinesis)

        def _get_records():
            nonlocal iterator
            response = aws_client.kinesis.get_records(ShardIterator=iterator)
            iterator = response["NextShardIterator"]
            json_records = response["Records"]
            assert len(json_records) > 0
            return json_records

        json_records = retry(_get_records, retries=30, sleep=3)
        first_log = json.loads(json_records[0]["Data"].decode().replace("", ""))
        assert "test log" == first_log["log"]


def get_log_group_logs(aws_client, log_group_name: str):
    log_events = aws_client.logs.filter_log_events(logGroupName=log_group_name)["events"]
    logs = [e["message"] for e in log_events]
    return logs


def get_shard_iterator(stream_name, kinesis_client):
    response = kinesis_client.describe_stream(StreamName=stream_name)
    shard_id = response["StreamDescription"]["Shards"][0]["ShardId"]
    response = kinesis_client.get_shard_iterator(
        StreamName=stream_name, ShardId=shard_id, ShardIteratorType="TRIM_HORIZON"
    )
    return response["ShardIterator"]
