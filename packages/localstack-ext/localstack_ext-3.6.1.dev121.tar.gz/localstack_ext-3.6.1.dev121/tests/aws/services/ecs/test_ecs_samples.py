import os.path
from collections import Counter

import aws_cdk as cdk
import pytest
import requests
from localstack.config import LOCALSTACK_HOST
from localstack.testing.aws.util import is_aws_cloud
from localstack.testing.pytest import markers
from localstack.testing.scenario.cdk_lambda_helper import (
    generate_ecr_image_from_dockerfile,
)
from localstack.utils.sync import retry

from .test_ecs import using_kubernetes_executor


class TestDurableStorageSample:
    # Sample from https://containersonaws.com/pattern/elastic-file-system-ecs-cdk

    @pytest.fixture(scope="class", autouse=True)
    def infrastructure(self, infrastructure_setup):
        infra = infrastructure_setup(namespace="EcsSample")
        stack = cdk.Stack(infra.cdk_app, "DurableStorageWithFargateStack")

        vpc = cdk.aws_ec2.Vpc(stack, "Vpc", max_azs=2)
        cluster = cdk.aws_ecs.Cluster(stack, "EcsCluster", vpc=vpc)
        cluster.add_capacity(
            "DefaultAutoScalingGroup",
            instance_type=cdk.aws_ec2.InstanceType.of(
                cdk.aws_ec2.InstanceClass.T2, cdk.aws_ec2.InstanceSize.MICRO
            ),
        )

        file_system = cdk.aws_efs.FileSystem(
            stack,
            "Filesystem",
            vpc=vpc,
            lifecycle_policy=cdk.aws_efs.LifecyclePolicy.AFTER_1_DAY,
            performance_mode=cdk.aws_efs.PerformanceMode.GENERAL_PURPOSE,  # default
            out_of_infrequent_access_policy=cdk.aws_efs.OutOfInfrequentAccessPolicy.AFTER_1_ACCESS,
        )

        task_definition = cdk.aws_ecs.FargateTaskDefinition(stack, "TaskDef")
        container = task_definition.add_container(
            "nginx",
            image=cdk.aws_ecs.ContainerImage.from_registry("public.ecr.aws/nginx/nginx"),
            memory_limit_mib=256,
            logging=cdk.aws_ecs.AwsLogDriver(stream_prefix="nginx"),
        )
        container.add_port_mappings(
            cdk.aws_ecs.PortMapping(container_port=80, protocol=cdk.aws_ecs.Protocol.TCP)
        )

        task_definition.add_volume(
            efs_volume_configuration=cdk.aws_ecs.EfsVolumeConfiguration(
                file_system_id=file_system.file_system_id,
                root_directory="/",
                transit_encryption="ENABLED",
            ),
            name="web-content",
        )

        efs_mount_policy = cdk.aws_iam.PolicyStatement(
            actions=[
                "elasticfilesystem:ClientMount",
                "elasticfilesystem:ClientWrite",
                "elasticfilesystem:ClientRootAccess",
            ],
            resources=[file_system.file_system_arn],
        )
        task_definition.add_to_task_role_policy(efs_mount_policy)

        container.add_mount_points(
            cdk.aws_ecs.MountPoint(
                container_path="/usr/share/nginx/html", read_only=False, source_volume="web-content"
            )
        )

        service = cdk.aws_ecs.FargateService(
            stack,
            "Service",
            cluster=cluster,
            task_definition=task_definition,
            desired_count=2,
            enable_execute_command=True,
        )

        file_system.connections.allow_default_port_from(service)

        lb = cdk.aws_elasticloadbalancingv2.ApplicationLoadBalancer(
            stack, "LB", vpc=vpc, internet_facing=True
        )
        listener = lb.add_listener("PublicListener", port=80, open=True)

        listener.add_targets(
            "ECS",
            port=80,
            targets=[service.load_balancer_target(container_name="nginx", container_port=80)],
            health_check={
                "healthy_http_codes": "200,404",
                "interval": cdk.Duration.seconds(60),
                "path": "/health",
                "timeout": cdk.Duration.seconds(5),
            },
        )

        cdk.CfnOutput(stack, "LoadBalancerDNS", value=lb.load_balancer_dns_name)

        with infra.provisioner() as prov:
            yield prov

    @markers.aws.validated
    @markers.only_on_amd64
    def test_listener(self, infrastructure, snapshot):
        outputs = infrastructure.get_stack_outputs("DurableStorageWithFargateStack")
        listener_url = f"http://{outputs['LoadBalancerDNS'].lower()}"
        if not is_aws_cloud():
            listener_url = f"{listener_url}:{LOCALSTACK_HOST.port}"

        def _assert_service():
            response = requests.get(listener_url)
            assert "nginx" in response.text

        retry(retries=20 if is_aws_cloud() else 5, sleep=2, function=_assert_service)


@pytest.mark.skipif(
    condition=using_kubernetes_executor(),
    reason="Test relies on Docker which is not available on Kubernetes",
)
class TestSharedResourcesSample:
    # Sample from https://containersonaws.com/pattern/cdk-shared-alb-for-amazon-ecs-fargate-service

    @pytest.fixture(scope="class", autouse=True)
    def infrastructure(self, infrastructure_setup, aws_client):
        infra = infrastructure_setup(namespace="EcsSample")
        repository_name = "sample-service-one-repository"
        infra.add_custom_setup(
            lambda: generate_ecr_image_from_dockerfile(
                aws_client.ecr,
                repository_name,
                os.path.join(os.path.dirname(__file__), "sample_dockerfile"),
            )
        )
        infra.add_custom_teardown(
            cleanup_task=lambda: aws_client.ecr.delete_repository(
                repositoryName=repository_name, force=True
            )
        )

        repository_name2 = "sample-service-two-repository"
        infra.add_custom_setup(
            lambda: generate_ecr_image_from_dockerfile(
                aws_client.ecr,
                repository_name2,
                os.path.join(os.path.dirname(__file__), "second_sample_dockerfile"),
            )
        )
        infra.add_custom_teardown(
            cleanup_task=lambda: aws_client.ecr.delete_repository(
                repositoryName=repository_name2, force=True
            )
        )

        stack = cdk.Stack(infra.cdk_app, "SharedResources")

        vpc = cdk.aws_ec2.Vpc(stack, "Vpc", max_azs=2)
        cluster = cdk.aws_ecs.Cluster(stack, "EcsCluster", vpc=vpc)

        lb = cdk.aws_elasticloadbalancingv2.ApplicationLoadBalancer(
            stack, "lb", vpc=vpc, internet_facing=True
        )

        listener = lb.add_listener("listener", port=80, open=True)

        listener.add_action(
            "fixed-action",
            action=cdk.aws_elasticloadbalancingv2.ListenerAction.fixed_response(
                200, content_type="text/plain", message_body="OK"
            ),
        )

        self.create_service_stack(
            infra.cdk_app, "service-one", cluster, listener, repository_name, "/service-one*", 1
        )
        self.create_service_stack(
            infra.cdk_app, "service-two", cluster, listener, repository_name2, "/service-two*", 2
        )

        cdk.CfnOutput(stack, "listener", value=listener.load_balancer.load_balancer_dns_name)

        with infra.provisioner() as prov:
            yield prov

    def create_service_stack(
        self, cdk_app, id, cluster, listener, repository_name, web_path, priority
    ):
        service_stack = cdk.Stack(cdk_app, id)
        task_definition = cdk.aws_ecs.FargateTaskDefinition(service_stack, f"{id}-task-def")

        repository = cdk.aws_ecr.Repository.from_repository_name(
            service_stack, "repo", repository_name=repository_name
        )

        container = task_definition.add_container(
            "web",
            image=cdk.aws_ecs.ContainerImage.from_ecr_repository(repository=repository),
            memory_limit_mib=256,
            logging=cdk.aws_ecs.LogDrivers.aws_logs(
                stream_prefix=id,
                mode=cdk.aws_ecs.AwsLogDriverMode.NON_BLOCKING,
                max_buffer_size=cdk.Size.mebibytes(25),
            ),
        )

        container.add_port_mappings(
            cdk.aws_ecs.PortMapping(container_port=8080, protocol=cdk.aws_ecs.Protocol.TCP)
        )

        service = cdk.aws_ecs.FargateService(
            service_stack, f"{id}-service", cluster=cluster, task_definition=task_definition
        )

        listener.add_targets(
            f"{id}-target",
            priority=priority,
            conditions=[cdk.aws_elasticloadbalancingv2.ListenerCondition.path_patterns([web_path])],
            port=80,
            targets=[service.load_balancer_target(container_name="web", container_port=8080)],
            health_check={
                "interval": cdk.Duration.seconds(10),
                "path": "/",
                "timeout": cdk.Duration.seconds(5),
            },
            deregistration_delay=cdk.Duration.seconds(10),
        )

    @markers.aws.validated
    def test_listener_services_are_accessible_and_returning_expected_content(self, infrastructure):
        outputs = infrastructure.get_stack_outputs("SharedResources")

        listener_url = f"http://{outputs['listener'].lower()}"
        if not is_aws_cloud():
            listener_url = f"{listener_url}:{LOCALSTACK_HOST.port}"

        def _fetch_content(path):
            url = listener_url + path
            response = requests.get(url)
            return response.text

        def _assert_content():
            assert _fetch_content("/").strip() == "OK"
            assert _fetch_content("/service-one/").strip() == "Hello from service one"
            assert _fetch_content("/service-two/").strip() == "Hello from service two"

        retry(retries=20 if is_aws_cloud() else 5, sleep=2, function=_assert_content)

    @markers.aws.validated
    def test_deployed_resources(self, infrastructure, snapshot, aws_client):
        cfn_client = aws_client.cloudformation
        shared_resources = cfn_client.list_stack_resources(StackName="SharedResources")[
            "StackResourceSummaries"
        ]
        service_one_resources = cfn_client.list_stack_resources(StackName="service-one")[
            "StackResourceSummaries"
        ]
        service_two_resources = cfn_client.list_stack_resources(StackName="service-two")[
            "StackResourceSummaries"
        ]

        shared_resources_count = Counter(
            [resource["ResourceType"] for resource in shared_resources]
        )
        service_one_resources_count = Counter(
            [resource["ResourceType"] for resource in service_one_resources]
        )
        service_two_resources_count = Counter(
            [resource["ResourceType"] for resource in service_two_resources]
        )

        total_counts = (
            shared_resources_count + service_one_resources_count + service_two_resources_count
        )
        snapshot.match("resources_deployed", dict(total_counts.items()))
