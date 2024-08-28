import contextlib
import json
import logging
import os
import time
from itertools import islice
from typing import TYPE_CHECKING, Generator

import pytest
from botocore.exceptions import ClientError
from localstack import config
from localstack.pro.core import config as ext_config
from localstack.pro.core.services.ecs import provider
from localstack.testing.aws.util import is_aws_cloud
from localstack.testing.pytest import markers
from localstack.testing.snapshots.transformer_utility import PATTERN_UUID
from localstack.utils.aws.arns import get_partition
from localstack.utils.bootstrap import in_ci
from localstack.utils.docker_utils import (
    DOCKER_CLIENT,
    get_host_path_for_path_in_docker,
    reserve_available_container_port,
)
from localstack.utils.files import load_file, mkdir, save_file
from localstack.utils.strings import short_uid
from localstack.utils.sync import ShortCircuitWaitException, retry, wait_until

if TYPE_CHECKING:
    from mypy_boto3_logs import CloudWatchLogsClient

LOG = logging.getLogger(__name__)


def using_kubernetes_executor() -> bool:
    return ext_config.ECS_TASK_EXECUTOR == "kubernetes"


@pytest.fixture(scope="module", autouse=True)
def pull_images():
    if using_kubernetes_executor():
        return

    # pull images for local testing
    LOG.debug("pulling missing docker images")
    if not is_aws_cloud():
        _pull_image_if_not_exists("alpine")
        _pull_image_if_not_exists("nginx")


@pytest.fixture
def create_cluster(aws_client):
    cluster_arns = []

    def _create_cluster(*args, **kwargs) -> str:
        if "clusterName" not in kwargs:
            kwargs["clusterName"] = f"test-cluster-{short_uid()}"

        cluster_arn = aws_client.ecs.create_cluster(*args, **kwargs)["cluster"]["clusterArn"]
        cluster_arns.append(cluster_arn)
        return cluster_arn

    yield _create_cluster

    for cluster_arn in cluster_arns:
        # delete services
        for service_arn in aws_client.ecs.list_services(cluster=cluster_arn)["serviceArns"]:
            try:
                aws_client.ecs.delete_service(cluster=cluster_arn, service=service_arn, force=True)
            except Exception as e:
                LOG.debug("Error cleaning up service: %s", e)

        # stop any remaining tasks
        for task_arn in aws_client.ecs.list_tasks(cluster=cluster_arn)["taskArns"]:
            with contextlib.suppress(Exception):
                aws_client.ecs.stop_task(cluster=cluster_arn, task=task_arn)

    def _services_removed(cluster_arn):
        service_arns = aws_client.ecs.list_services(cluster=cluster_arn).get("serviceArns", [])
        # check if all remaining services are inactive. Only currently implemented for service count <= 10.
        if service_arns:
            services = aws_client.ecs.describe_services(cluster=cluster_arn, services=service_arns)[
                "services"
            ]
            services = [service for service in services if service["status"] != "INACTIVE"]
            assert not services
        result = aws_client.ecs.list_tasks(cluster=cluster_arn)
        task_arns = result.get("taskArns")
        if task_arns:
            tasks = aws_client.ecs.describe_tasks(cluster=cluster_arn, tasks=task_arns)["tasks"]
            running_tasks = [task for task in tasks if task["lastStatus"] == "RUNNING"]
            assert not running_tasks

    def assert_cluster_ready(cluster_arn):
        cluster = aws_client.ecs.describe_clusters(clusters=[cluster_arn], include=["ATTACHMENTS"])[
            "clusters"
        ][0]
        assert not cluster.get("attachmentsStatus") or cluster["attachmentsStatus"] in [
            "UPDATE_COMPLETE",
            "UPDATE_FAILED",
        ]
        assert cluster.get("status") == "ACTIVE"

    # wait until services are removed, then delete clusters
    for cluster_arn in cluster_arns:
        try:
            retry(lambda: _services_removed(cluster_arn), sleep=2, retries=30)
            if is_aws_cloud():
                retry(lambda: assert_cluster_ready(cluster_arn), sleep=2, retries=30)

            aws_client.ecs.delete_cluster(cluster=cluster_arn)
        except Exception as e:
            LOG.debug("Error while deleting test cluster %s: %s", cluster_arn, e)


@pytest.fixture
def register_task_definition(aws_client):
    task_definition_arns = []

    def _register_task_definition(**kwargs):
        if not kwargs.get("family"):
            kwargs["family"] = f"test_family_{short_uid()}"
        if not kwargs.get("containerDefinitions"):
            kwargs["containerDefinitions"] = [
                {
                    "name": f"n-{short_uid()}",
                    "image": "alpine",
                    "cpu": 10,
                    "command": ["sleep", "2"],
                    "memory": 123,
                }
            ]
        task_definition_result = aws_client.ecs.register_task_definition(**kwargs)
        task_def_arn = task_definition_result["taskDefinition"]["taskDefinitionArn"]
        task_definition_arns.append(task_def_arn)
        return task_definition_result

    yield _register_task_definition

    for task_def_arn in task_definition_arns:
        LOG.debug("Deleting task definition arn %s", task_def_arn)
        try:
            aws_client.ecs.deregister_task_definition(taskDefinition=task_def_arn)
        except Exception:
            LOG.debug("Error while deleting test task definition %s", task_def_arn)


@pytest.fixture
def execution_role(create_role, aws_client):
    execution_role = create_role(
        RoleName=f"test_role_{short_uid()}",
        AssumeRolePolicyDocument=json.dumps(
            {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Action": "sts:AssumeRole",
                        "Principal": {"Service": "ecs.amazonaws.com"},
                        "Effect": "Allow",
                    },
                    {
                        "Action": "sts:AssumeRole",
                        "Principal": {"Service": "ecs-tasks.amazonaws.com"},
                        "Effect": "Allow",
                    },
                    {
                        "Action": "sts:AssumeRole",
                        "Principal": {"Service": "logs.amazonaws.com"},
                        "Effect": "Allow",
                    },
                ],
            }
        ),
    )
    aws_client.iam.put_role_policy(
        RoleName=execution_role["Role"]["RoleName"],
        PolicyName="test_policy",
        PolicyDocument=json.dumps(
            {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Action": [
                            "logs:CreateLogGroup",
                            "logs:CreateLogStream",
                            "logs:PutLogEvents",
                        ],
                        "Resource": "*",
                    },
                ],
            }
        ),
    )
    if is_aws_cloud():
        time.sleep(15)

    return execution_role


@pytest.fixture
def dummy_task_definition(create_cluster, register_task_definition):
    create_cluster()
    return register_task_definition()


@pytest.fixture(scope="session")
def vpc_id(aws_client):
    vpc_cidr_block = "10.0.0.0/16"
    public_subnet_cidr_block = "10.0.0.0/24"
    private_subnet_cidr_block = "10.0.1.0/24"
    waiter_config = {
        "Delay": 5 if is_aws_cloud() else 1,
        "MaxAttempts": 40 if is_aws_cloud() else 10,
    }

    vpc = aws_client.ec2.create_vpc(CidrBlock=vpc_cidr_block)

    # wait for vpc to be ready
    aws_client.ec2.get_waiter("vpc_available").wait(VpcIds=[vpc["Vpc"]["VpcId"]])

    # subnet_cidr_block = f"{a}.{b}.{c}.{d}/24"
    public_subnet = aws_client.ec2.create_subnet(
        CidrBlock=public_subnet_cidr_block,
        VpcId=vpc["Vpc"]["VpcId"],
    )

    private_subnet = aws_client.ec2.create_subnet(
        CidrBlock=private_subnet_cidr_block,
        VpcId=vpc["Vpc"]["VpcId"],
    )

    # create internet gateway
    igw = aws_client.ec2.create_internet_gateway()
    aws_client.ec2.attach_internet_gateway(
        InternetGatewayId=igw["InternetGateway"]["InternetGatewayId"],
        VpcId=vpc["Vpc"]["VpcId"],
    )

    # create public route table
    public_route_table = aws_client.ec2.create_route_table(VpcId=vpc["Vpc"]["VpcId"])
    public_association_id = aws_client.ec2.associate_route_table(
        RouteTableId=public_route_table["RouteTable"]["RouteTableId"],
        SubnetId=public_subnet["Subnet"]["SubnetId"],
    )["AssociationId"]
    aws_client.ec2.create_route(
        RouteTableId=public_route_table["RouteTable"]["RouteTableId"],
        DestinationCidrBlock="0.0.0.0/0",
        GatewayId=igw["InternetGateway"]["InternetGatewayId"],
    )

    # create nat gateway
    eip = aws_client.ec2.allocate_address(Domain="vpc")
    nat_gateway = aws_client.ec2.create_nat_gateway(
        AllocationId=eip["AllocationId"],
        SubnetId=public_subnet["Subnet"]["SubnetId"],
    )

    # wait for nat to be ready
    aws_client.ec2.get_waiter("nat_gateway_available").wait(
        NatGatewayIds=[nat_gateway["NatGateway"]["NatGatewayId"]], WaiterConfig=waiter_config
    )

    # create private route table
    private_route_table = aws_client.ec2.create_route_table(VpcId=vpc["Vpc"]["VpcId"])
    private_association_id = aws_client.ec2.associate_route_table(
        RouteTableId=private_route_table["RouteTable"]["RouteTableId"],
        SubnetId=private_subnet["Subnet"]["SubnetId"],
    )["AssociationId"]
    aws_client.ec2.create_route(
        RouteTableId=private_route_table["RouteTable"]["RouteTableId"],
        DestinationCidrBlock="0.0.0.0/0",
        NatGatewayId=nat_gateway["NatGateway"]["NatGatewayId"],
    )

    # create public network acl
    public_acl_response = aws_client.ec2.create_network_acl(VpcId=vpc["Vpc"]["VpcId"])
    public_acl_id = public_acl_response["NetworkAcl"]["NetworkAclId"]
    aws_client.ec2.create_network_acl_entry(
        NetworkAclId=public_acl_id,
        RuleNumber=100,
        Protocol="-1",
        RuleAction="allow",
        CidrBlock="0.0.0.0/0",
        Egress=False,
    )
    aws_client.ec2.create_network_acl_entry(
        NetworkAclId=public_acl_id,
        RuleNumber=100,
        Protocol="-1",
        RuleAction="allow",
        CidrBlock="0.0.0.0/0",
        Egress=True,
    )

    # Create a security group that allows all traffic
    security_group = aws_client.ec2.create_security_group(
        GroupName="AllowAllTrafficSG",
        Description="Allow all inbound and outbound traffic",
        VpcId=vpc["Vpc"]["VpcId"],
    )

    yield vpc["Vpc"]["VpcId"]

    with contextlib.suppress(ClientError):
        # clean dependencies
        aws_client.ec2.delete_nat_gateway(
            NatGatewayId=nat_gateway["NatGateway"]["NatGatewayId"],
        )
        # wait nat to be deleted
        aws_client.ec2.get_waiter("nat_gateway_deleted").wait(
            NatGatewayIds=[nat_gateway["NatGateway"]["NatGatewayId"]], WaiterConfig=waiter_config
        )
        aws_client.ec2.detach_internet_gateway(
            InternetGatewayId=igw["InternetGateway"]["InternetGatewayId"],
            VpcId=vpc["Vpc"]["VpcId"],
        )
        aws_client.ec2.delete_internet_gateway(
            InternetGatewayId=igw["InternetGateway"]["InternetGatewayId"],
        )
        aws_client.ec2.disassociate_route_table(
            AssociationId=public_association_id,
        )
        aws_client.ec2.disassociate_route_table(
            AssociationId=private_association_id,
        )
        aws_client.ec2.delete_subnet(
            SubnetId=public_subnet["Subnet"]["SubnetId"],
        )
        aws_client.ec2.delete_subnet(
            SubnetId=private_subnet["Subnet"]["SubnetId"],
        )
        # disassociate and delete route table
        aws_client.ec2.delete_route_table(
            RouteTableId=public_route_table["RouteTable"]["RouteTableId"],
        )
        aws_client.ec2.delete_route_table(
            RouteTableId=private_route_table["RouteTable"]["RouteTableId"],
        )
        aws_client.ec2.delete_network_acl(
            NetworkAclId=public_acl_response["NetworkAcl"]["NetworkAclId"],
        )
        aws_client.ec2.delete_security_group(
            GroupId=security_group["GroupId"],
        )
        aws_client.ec2.delete_vpc(VpcId=vpc["Vpc"]["VpcId"])

        aws_client.ec2.release_address(
            AllocationId=eip["AllocationId"],
        )


def get_task_logs(
    logs_client: "CloudWatchLogsClient",
    log_group_name: str,
    log_stream_prefix: str,
    sentinel_value: str | None = None,
    num_iterations: int = 10,
) -> Generator[str, None, None]:
    def log_group_created():
        log_group = logs_client.describe_log_groups(logGroupNamePrefix=log_group_name)
        return len(log_group["logGroups"]) == 1

    assert wait_until(log_group_created)
    log_group = logs_client.describe_log_groups(logGroupNamePrefix=log_group_name)
    assert log_group["logGroups"][0]["logGroupName"] == log_group_name

    def log_stream_created():
        log_stream = logs_client.describe_log_streams(
            logGroupName=log_group_name, logStreamNamePrefix=log_stream_prefix
        )
        return len(log_stream["logStreams"]) == 1

    assert wait_until(log_stream_created)

    log_stream = logs_client.describe_log_streams(
        logGroupName=log_group_name,
        logStreamNamePrefix=log_stream_prefix,
    )

    def get_logs():
        logs = logs_client.get_log_events(
            logGroupName=log_group_name,
            logStreamName=log_stream["logStreams"][0]["logStreamName"],
        )
        return len(logs["events"]) > 0

    assert wait_until(get_logs)

    seen_messages = set()
    for _ in range(num_iterations):
        logs = logs_client.get_log_events(
            logGroupName=log_group_name,
            logStreamName=log_stream["logStreams"][0]["logStreamName"],
        )

        for event in logs["events"]:
            # do not emit duplicate events
            seen_messages_cache_key = (event["timestamp"], event["message"])
            if seen_messages_cache_key in seen_messages:
                continue
            seen_messages.add(seen_messages_cache_key)

            message = event["message"]
            if sentinel_value is not None and message == sentinel_value:
                return

            yield message

    if sentinel_value:
        raise TimeoutError("Did not collect all logs")


class TestClustersCrud:
    @markers.aws.validated
    def test_cluster_default_name(self, aws_client, account_id, cleanups):
        # Ensure CreateCluster uses the default cluster name when omitted
        response = aws_client.ecs.create_cluster()
        cleanups.append(lambda: aws_client.ecs.delete_cluster(cluster="default"))
        assert response["cluster"]["clusterName"] == "default"

        # Hardcode the region and account ID in the ARN for now.
        # It will be changed to TEST_ values once cross-accounts test strategy matures
        assert (
            response["cluster"]["clusterArn"]
            == f"arn:{get_partition(aws_client.ecs.meta.region_name)}:ecs:{aws_client.ecs.meta.region_name}:{account_id}:cluster/default"
        )

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(
        paths=[
            "$..cluster.attachments",
            "$..cluster.attachmentsStatus",
            "$..cluster.statistics",
            "$..cluster.tags",
        ]
    )
    def test_cluster_capacity_providers(self, create_cluster, aws_client, snapshot):
        snapshot.add_transformer(snapshot.transform.ecs_api())
        cluster_arn = create_cluster()
        result = aws_client.ecs.put_cluster_capacity_providers(
            cluster=cluster_arn,
            capacityProviders=["FARGATE"],
            defaultCapacityProviderStrategy=[
                {"capacityProvider": "FARGATE", "weight": 2, "base": 0}
            ],
        )
        snapshot.match("put-cluster-capacity-providers", result)

    @markers.aws.validated
    def test_delete_cluster_status(self, aws_client):
        def _get_state():
            result = aws_client.ecs.describe_clusters(clusters=[cluster_arn])["clusters"]
            return result[0]["status"]

        cluster_name = f"test-cluster-{short_uid()}"

        # create cluster
        cluster_arn = aws_client.ecs.create_cluster(clusterName=cluster_name)["cluster"][
            "clusterArn"
        ]
        assert _get_state() == "ACTIVE"
        # creation works multiple times
        cluster_arn = aws_client.ecs.create_cluster(clusterName=cluster_name)["cluster"][
            "clusterArn"
        ]
        assert _get_state() == "ACTIVE"
        # delete cluster
        aws_client.ecs.delete_cluster(cluster=cluster_arn)
        # assert that cluster entry still exists, in status INACTIVE
        assert _get_state() == "INACTIVE"
        # this is possible multiple times
        aws_client.ecs.delete_cluster(cluster=cluster_arn)
        # assert that cluster entry still exists, in status INACTIVE
        assert _get_state() == "INACTIVE"
        # recreating cluster sets it active again
        cluster_arn = aws_client.ecs.create_cluster(clusterName=cluster_name)["cluster"][
            "clusterArn"
        ]
        assert _get_state() == "ACTIVE"
        # deleting cluster again
        aws_client.ecs.delete_cluster(cluster=cluster_arn)
        # assert that cluster entry still exists, in status INACTIVE
        assert _get_state() == "INACTIVE"


class TestTasksCrud:
    @markers.aws.validated
    def test_tag_task_definition(self, dummy_task_definition, aws_client):
        task_definition_result = dummy_task_definition
        task_definition_arn = task_definition_result["taskDefinition"]["taskDefinitionArn"]
        tags = [{"key": "test", "value": "test123"}]
        aws_client.ecs.tag_resource(resourceArn=task_definition_arn, tags=tags)
        result = aws_client.ecs.list_tags_for_resource(resourceArn=task_definition_arn)
        assert result["tags"] == tags

    @markers.aws.validated
    def test_describe_undefined_task_definition(
        self, register_task_definition, snapshot, aws_client
    ):
        register_task_definition(
            family=f"test_family_{short_uid()}",
        )
        with pytest.raises(ClientError) as e:
            aws_client.ecs.describe_task_definition(taskDefinition=short_uid())
        snapshot.match("undefined_task_definition", e.value.response)

    @pytest.mark.parametrize(
        "name, image",
        [
            ("invalid name", "valid_image"),
            ("invalid name", "invalid image"),
            ("valid_name", "invalid image"),
            (None, None),
        ],
    )
    @markers.snapshot.skip_snapshot_verify(
        paths=[
            "$..taskDefinition.networkMode",
            "$..taskDefinition.registeredBy",
            "$..taskDefinition.requiresAttributes",
            "$..tags",
        ]
    )
    @markers.aws.validated
    def test_create_task_definition_err(
        self, register_task_definition, snapshot, aws_client, name, image
    ):
        container_definitions = [
            {
                "cpu": 10,
                "command": ["sleep", "2"],
                "memory": 123,
            }
        ]
        if name is not None:
            container_definitions[0]["name"] = name
        if image is not None:
            container_definitions[0]["image"] = image
        with pytest.raises(ClientError) as e:
            register_task_definition(containerDefinitions=container_definitions)
        snapshot.match("create_task_definition_err", e.value.response)

    @pytest.mark.parametrize(
        "container_name, image, is_valid",
        [
            ("test-container", "alpine", True),
            ("test-container", "alpine:latest", True),
            ("test-container", "alpine:3.12", True),
            (
                "test-container",
                "alpine@sha256:1fd62556954250bac80d601a196bb7fd480ceba7c10e94dd8fd4c6d1c08783d5",
                True,
            ),
            ("test-container", "docker.io/nginx", True),
            ("test-container", "library/alpine", True),
            (
                "test-container",
                "localhost.localstack.cloud:4510/cdk-hnb659fds-container-assets-111111111111-us-region-1:5f423786c2e2f4ca36a670185bfd1e7f44f59942e3f5ad1994fcf1a1d1d66ba0",
                True,
            ),
            ("test-container", "public.ecr.aws/xray/aws-xray-daemon:3.x", True),
            ("test-container", "public.ecr.aws/xray/aws-xray-daemon:v3.0.0", True),
            ("test-container", "alpin e:3.12.0", False),
            ("test-container", "alpine 3.12.0", False),
            ("test-container", "alpine@3.12.0", False),
            (
                "test-container",
                "alpine@sha256:9F86D081884C7D659A2FEAA0C55AD015A3BF4F1B2B0B822CD15D6C15B0F00A08",
                True,
            ),
            (
                "test-container",
                "alpine@sha256:9F86D081884C7D659A2FEAA0C55AD015A3BF4F1B2B0B822CD15D6C15B0F00A08@sha256:9F86D081884C7D659A2FEAA0C55AD015A3BF4F1B2B0B822CD15D6C15B0F00A08",
                False,
            ),
            (
                "test-container",
                "alpine@sha256:9F86D081884C7D659A2FEAA0C55AD015A3BF4F1B2B0B822CD15D6C15B0F00A08@",
                True,
            ),
            (
                "test-container",
                "alpine@sha384:9F86D081884C7D659A2FEAA0C55AD015A3BF4F1B2B0B822CD15D6C15B0F00A08",
                False,
            ),
            (
                "test-container",
                "alpine@sha512:9F86D081884C7D659A2FEAA0C55AD015A3BF4F1B2B0B822CD15D6C15B0F00A08",
                False,
            ),
            (
                "test-container",
                "alpine@sha256:9F86D081884C7D659A2FEAA0C55AD015A3BF4F1B2B0B822CD15D6C15B0F00A08@s",
                False,
            ),
            ("test-container", "@library/alpine:latest", False),
            ("test-container", "library/@alpine:latest", False),
            ("test-container", "library/alpine@latest", False),
            ("test-container", "library/image@name:latest", False),
            ("test-container", "library/image@name", False),
            ("test-container", "alpine@sha256:1234567890", False),
            ("test-container", "alpine:latest@sha256:1234567890", False),
            # validation for container name
            ("test container", "alpine", False),
            ("@test-container", "alpine", False),
            ("$test-container", "alpine", False),
            ("test@container", "alpine", False),
            ("a" * 255, "alpine", True),
            ("a" * 256, "alpine", False),
        ],
    )
    @markers.snapshot.skip_snapshot_verify(
        paths=[
            "$..taskDefinition.containerDefinitions..systemControls",
            "$..taskDefinition.networkMode",
            "$..taskDefinition.registeredBy",
            "$..taskDefinition.requiresAttributes",
            "$..tags",
        ]
    )
    @markers.aws.validated
    def test_create_task_definition_validation(
        self, register_task_definition, snapshot, aws_client, container_name, image, is_valid
    ):
        snapshot.add_transformer(snapshot.transform.key_value("family", "family-name"))
        container_definitions = [
            {
                "name": container_name,
                "image": image,
                "cpu": 10,
                "command": ["sleep", "1"],
                "memory": 123,
            }
        ]
        if is_valid:
            response = register_task_definition(containerDefinitions=container_definitions)
            snapshot.match("create_task_definition_valid", response)
        else:
            with pytest.raises(ClientError) as e:
                register_task_definition(containerDefinitions=container_definitions)
            snapshot.match("create_task_definition_invalid", e.value.response)

    @markers.snapshot.skip_snapshot_verify(
        paths=["$..taskDefinition.registeredBy", "$..taskDefinition.requiresAttributes"]
    )
    @markers.aws.validated
    def test_fargate_task_definition_optional_container_memory(
        self, register_task_definition, snapshot, aws_client
    ):
        snapshot.add_transformer(snapshot.transform.key_value("family", "family-name"))
        container_definitions = [
            {
                "name": "test-container",
                "image": "alpine",
                "command": ["sleep", "1"],
            }
        ]
        response = register_task_definition(
            containerDefinitions=container_definitions,
            requiresCompatibilities=["FARGATE"],
            memory="2048",
            networkMode="awsvpc",
            cpu="256",
        )
        snapshot.match("fargate_optional_container_memory", response)

    @markers.snapshot.skip_snapshot_verify(
        paths=[
            "$..taskDefinition.networkMode",
            "$..taskDefinition.registeredBy",
            "$..taskDefinition.requiresAttributes",
            "$..tags",
        ]
    )
    @pytest.mark.parametrize(
        "image_name",
        [
            "xeFs8NP5bbAJzMyZQFbimPA2TofLZDNnnISSSOBkQni02E/e9/47M6X39MaOWTd0j/1",
            "oYqqnY9b2K4sit13Wnovcu_GSPZpbeGjuwOb3L56CvxiIOOkXdnbYRpKnDZNoc9w_qQpw7bnM150",
            "f__HiUvwLQCeJZzX-0",
            "d9pkoMtZEFO8p2CDyH0rTyOj7Spnc4-biWjFiOx703/:t4yM10ps-wD1bpFkSrRo2CJAXHGQP8p_4oo16gh_67U3h5VorSdjqV-Vz6eyJwPepo2Ir55xFaHYRWgO3kK4pbyqO_2ErwmpeHk0Sd0lGssJ4HA2MvEyEu_sp/3",
            "fe9GzAA4hd/qFI6/sJcKhqlOF6OAXGbD3d",
            "4",
            "hc41/xpz24pgyiYWwnQK8hBghmY5Hgtw-cxD4scBcdi96LO_gSHvY/do6Z3T4IHz_uRrFCMgI_KWZl9hnLlkBRW1UGu0YNEmAY9EFoCOV8RDWnnkCSlBO6vSM6gxmfFBdC6wcC0WCIYSDJA60EK8X2DwGjq/30l",
            "hBupzM9E-Ajmao_PTEtKnLEXhlG_ryeYr154XNr",
            "yLY820GqBFD00C6ahzLb_LBeX-gG:ySaayu29uIp2L7fZaZJOy0q1N0F7JJBI",
            "GgzXW5Aeul2NyL-U",
            "4XgV944vEl7DEI_0u-V5Iefh34/n/tBH1LB9mQwcKrU8d46z9O5HSanNKePtt-7",
            "Bj1O3Eca4TbwL0rDcG3ygAf7McQ3gt_tg_R-qX1H1yDB71b35wABQsegTXbQ5qrkPM7Tr0ygOXgK6ZNDOAf4wREWc91mJQyxTab-GfSkorRKiA7NU21nSOnc4KmJhjFsHBZijJQ-6",
            "Tvx:JfmMbtmTUK0jUOIgqGh2G2hhU/XkTqJ16Q8m2o9PW6ujNuCHR47JpNg/kfOB9dI_18IVC7EiJzFpG9aqhbkDvyhxy77jEoy6:Tb03NQdF4NeqdFRbBqJybhk75Ww7fYaHne5wbZ9dy",
            ":::///__55::::://---:1abc::/",
            "aA9-_:./#--__::..//##----____::::....////####",
            "---//##@sha256:9F86D081884C7D659A2FEAA0C55AD015A3BF4F1B2B0B822CD15D6C15B0F00A08",
        ],
    )
    @markers.aws.validated
    def test_loose_image_name_regex(
        self, snapshot, aws_client, image_name, register_task_definition
    ):
        # This tests if the rules implied in the AWS docs are indeed so lax that they allow complete
        # nonsense image names in the task definition, using strings semi-randomly generated from said regex
        snapshot.add_transformer(snapshot.transform.key_value("family", "family-name"))

        container_definitions = [
            {
                "name": "test-container",
                "image": image_name,
                "cpu": 10,
                "command": ["sleep", "1"],
                "memory": 123,
            }
        ]
        response = register_task_definition(containerDefinitions=container_definitions)
        snapshot.match("create_task_definition_valid", response)

    @markers.snapshot.skip_snapshot_verify(
        paths=[
            "$..taskDefinition..networkMode",
            "$..taskDefinition..registeredBy",
            "$..taskDefinition.requiresAttributes",
            "$..tags",
        ]
    )
    @markers.aws.validated
    def test_create_task_definition(self, aws_client, register_task_definition, snapshot):
        snapshot.add_transformer(snapshot.transform.key_value("family", "family-name"))

        container_definitions = [
            {
                "name": "test_container",
                "image": "alpine",
            }
        ]
        with pytest.raises(ClientError) as e:
            register_task_definition(containerDefinitions=container_definitions)
        snapshot.match("create_task_definition_invalid_1", e.value.response)

        # testing default values
        container_definitions[0]["memory"] = 128
        response = register_task_definition(containerDefinitions=container_definitions)
        snapshot.match("create_task_definition_1", response)
        response = aws_client.ecs.describe_task_definition(
            taskDefinition=response["taskDefinition"]["taskDefinitionArn"]
        )
        snapshot.match("describe_task_definition_1", response)

        # added specific values
        response = register_task_definition(
            containerDefinitions=container_definitions, ephemeralStorage={"sizeInGiB": 1}
        )
        snapshot.match("create_task_definition_2", response)
        response = aws_client.ecs.describe_task_definition(
            taskDefinition=response["taskDefinition"]["taskDefinitionArn"]
        )
        snapshot.match("describe_task_definition_2", response)

    @markers.aws.unknown
    def test_describe_tasks_list_tasks(self, create_cluster, register_task_definition, aws_client):
        test_cluster = f"cluster-{short_uid()}"

        create_cluster(clusterName="default")
        create_cluster(clusterName=test_cluster)

        family = f"family-{short_uid()}"
        register_task_definition(family=family)

        # Create a task in the test cluster
        task_arn1 = aws_client.ecs.run_task(taskDefinition=family, cluster=test_cluster)["tasks"][
            0
        ]["taskArn"]
        tasks_in_test_cluster = aws_client.ecs.list_tasks(cluster=test_cluster)["taskArns"]
        assert len(tasks_in_test_cluster) == 1
        assert task_arn1 in tasks_in_test_cluster

        # Create another task in the DEFAULT cluster
        task_arn2 = aws_client.ecs.run_task(taskDefinition=family)["tasks"][0]["taskArn"]
        tasks_in_default_cluster = aws_client.ecs.list_tasks()["taskArns"]
        assert task_arn2 in tasks_in_default_cluster

        # Ensure ListTasks falls back to the 'default' cluster name when omitted
        assert tasks_in_default_cluster == aws_client.ecs.list_tasks(cluster="default")["taskArns"]

        # Ensure DescribeTasks falls back to the 'default' cluster name when omitted
        assert aws_client.ecs.describe_tasks(tasks=[task_arn2])["tasks"]

        # Ensure DescribeTasks returns failures when wrong cluster is provided
        assert aws_client.ecs.describe_tasks(tasks=[task_arn2], cluster=test_cluster)["failures"]

    @markers.aws.only_localstack
    @pytest.mark.skipif(
        condition=config.is_env_true("TEST_SKIP_LOCALSTACK_START"),
        reason="Test requires manipulating the state of the running LocalStack process",
    )
    def test_list_services_no_default_cluster(
        self, aws_client, account_id, snapshot, monkeypatch, sample_stores
    ):
        # We patch the get_store directly, since an inactive default cluster might be around, even if deleted.
        #   If there is an inactive default cluster, an empty list is returned instead
        store = sample_stores[account_id][aws_client.ecs.meta.region_name]
        store.clusters = {}
        monkeypatch.setattr(provider, "get_store", lambda x: store)

        with pytest.raises(ClientError) as e:
            aws_client.ecs.list_services()
        snapshot.match("list_services_no_default_cluster", e.value.response)

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(
        paths=[
            "$..cluster.attachments",
            "$..cluster.capacityProviders",
            "$..cluster.defaultCapacityProviderStrategy",
            "$..cluster.statistics",
            "$..cluster.tags",
        ]
    )
    def test_update_cluster(self, create_cluster, aws_client, snapshot):
        cluster_arn = create_cluster()
        snapshot.add_transformer(snapshot.transform.key_value("clusterName"))

        # update cluster
        response = aws_client.ecs.update_cluster(
            cluster=cluster_arn,
            settings=[{"name": "containerInsights", "value": "enabled"}],
        )
        snapshot.match("cluster_update_response", response)


class TestTaskExecution:
    @markers.aws.validated
    def test_run_simple_task(
        self,
        create_cluster,
        register_task_definition,
        aws_client,
        vpc_id,
        execution_role,
    ):
        cluster_arn = create_cluster()

        # list subnets id
        subnets = aws_client.ec2.describe_subnets(Filters=[{"Name": "vpc-id", "Values": [vpc_id]}])[
            "Subnets"
        ]
        subnet_ids = [subnet["SubnetId"] for subnet in subnets]

        task_family = f"test_family_{short_uid()}"
        container_name = f"test_container_{short_uid()}"

        task_definition = {
            "family": task_family,
            "executionRoleArn": execution_role["Role"]["Arn"],
            "taskRoleArn": execution_role["Role"]["Arn"],
            "requiresCompatibilities": ["FARGATE"],
            "networkMode": "awsvpc",
            "cpu": "0.5 vCPU",
            "memory": "1GB",
            "containerDefinitions": [
                {
                    "name": container_name,
                    "image": "ubuntu:latest",
                    "cpu": 128,
                    "memory": 256,
                    "command": ["bash", "-c", "true"],
                }
            ],
        }

        task_definition_result = register_task_definition(**task_definition)

        task_definition_arn = task_definition_result["taskDefinition"]["taskDefinitionArn"]
        result = aws_client.ecs.run_task(
            taskDefinition=task_definition_arn,
            cluster=cluster_arn,
            count=1,
            launchType="FARGATE",
            enableExecuteCommand=True,
            networkConfiguration={
                "awsvpcConfiguration": {
                    "subnets": subnet_ids,
                    "assignPublicIp": "ENABLED",
                }
            },
        )

        delay = 5
        max_retries = 40
        if not is_aws_cloud():
            delay = 1
            max_retries = 10
        task_arn = result["tasks"][0]["taskArn"]
        aws_client.ecs.get_waiter("tasks_stopped").wait(
            cluster=cluster_arn,
            tasks=[task_arn],
            WaiterConfig={"Delay": delay, "MaxAttempts": max_retries},
        )
        result = aws_client.ecs.describe_tasks(cluster=cluster_arn, tasks=[task_arn])

        # assert last status
        assert result["tasks"][0]["lastStatus"] == "STOPPED"
        assert result["tasks"][0]["containers"][0]["exitCode"] == 0

    @pytest.mark.skipif(
        condition=using_kubernetes_executor(),
        reason="Kubernetes pods have many more environment variables than can be listed here, and parity is not critical.",
    )
    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(
        paths=[
            "$..cpu",
            "$..memory",
            "$..registeredBy",
            "$..requiresAttributes",
            "$..containerDefinitions..systemControls",
            # environment variables captured
            # - supplied by LocalStack, not present on AWS
            "$.environment.AWS_ACCESS_KEY_ID",
            "$.environment.AWS_ENDPOINT_URL",
            "$.environment.AWS_SECRET_ACCESS_KEY",
            "$.environment.LOCALSTACK_HOSTNAME",
            # not implemented by LocalStack
            "$.environment.AWS_CONTAINER_CREDENTIALS_RELATIVE_URI",
            "$.environment.ECS_AGENT_URI",
            "$.environment.ECS_CONTAINER_METADATA_URI",
            "$.environment.ECS_CONTAINER_METADATA_URI_V4",
            "$.environment.HOSTNAME",
        ],
    )
    def test_environment_variable_expansion(
        self,
        create_cluster,
        register_task_definition,
        aws_client,
        vpc_id,
        execution_role,
        region_name,
        snapshot,
    ):
        snapshot.add_transformer(
            snapshot.transform.regex(execution_role["Role"]["RoleName"], "<execution-role-name>")
        )

        cluster_arn = create_cluster()
        log_group_name = f"log-group-{short_uid()}"
        log_stream_prefix = "ecs"
        snapshot.add_transformer(snapshot.transform.regex(log_group_name, "<log-group-name>"))

        # list subnets id
        subnets = aws_client.ec2.describe_subnets(Filters=[{"Name": "vpc-id", "Values": [vpc_id]}])[
            "Subnets"
        ]
        subnet_ids = [subnet["SubnetId"] for subnet in subnets]

        task_family = f"test_family_{short_uid()}"
        snapshot.add_transformer(snapshot.transform.regex(task_family, "<task-family>"))
        container_name = f"test_container_{short_uid()}"
        snapshot.add_transformer(snapshot.transform.regex(container_name, "<container-name>"))

        task_definition = {
            "family": task_family,
            "executionRoleArn": execution_role["Role"]["Arn"],
            "taskRoleArn": execution_role["Role"]["Arn"],
            "requiresCompatibilities": ["FARGATE"],
            "networkMode": "awsvpc",
            "cpu": "0.5 vCPU",
            "memory": "1GB",
            "containerDefinitions": [
                {
                    "name": container_name,
                    "image": "ubuntu:latest",
                    "cpu": 128,
                    "memory": 256,
                    "command": ["sh", "-c", "env; echo DONE"],
                    "environment": [
                        {"name": "MY_BASE_VAR", "value": "foo"},
                        {"name": "MY_DERIVED_VAR", "value": "${MY_BASE_VAR} foo"},
                    ],
                    "logConfiguration": {
                        "logDriver": "awslogs",
                        "options": {
                            "awslogs-create-group": "true",
                            "awslogs-group": log_group_name,
                            "awslogs-stream-prefix": log_stream_prefix,
                            "awslogs-region": region_name,
                        },
                    },
                }
            ],
        }

        task_definition_result = register_task_definition(**task_definition)["taskDefinition"]
        snapshot.match("task-definition", task_definition_result)

        aws_client.iam.put_role_policy(
            RoleName=execution_role["Role"]["RoleName"],
            PolicyName="test_policy",
            PolicyDocument=json.dumps(
                {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Action": [
                                "logs:CreateLogGroup",
                                "logs:CreateLogStream",
                                "logs:PutLogEvents",
                            ],
                            "Resource": "*",
                        },
                    ],
                }
            ),
        )
        if is_aws_cloud():
            time.sleep(15)

        task_definition_arn = task_definition_result["taskDefinitionArn"]
        result = aws_client.ecs.run_task(
            taskDefinition=task_definition_arn,
            cluster=cluster_arn,
            count=1,
            launchType="FARGATE",
            enableExecuteCommand=True,
            networkConfiguration={
                "awsvpcConfiguration": {
                    "subnets": subnet_ids,
                    "assignPublicIp": "ENABLED",
                }
            },
        )

        delay = 5
        max_retries = 40
        if not is_aws_cloud():
            delay = 1
            max_retries = 10
        task_arn = result["tasks"][0]["taskArn"]
        aws_client.ecs.get_waiter("tasks_stopped").wait(
            cluster=cluster_arn,
            tasks=[task_arn],
            WaiterConfig={"Delay": delay, "MaxAttempts": max_retries},
        )

        logs = get_task_logs(
            logs_client=aws_client.logs,
            log_group_name=log_group_name,
            log_stream_prefix=log_stream_prefix,
            sentinel_value="DONE",
        )

        environment = {}
        for line in logs:
            key, value = line.split("=", maxsplit=2)
            environment[key] = value

        # add transforms
        if hostname := environment.get("HOSTNAME"):
            snapshot.add_transformer(snapshot.transform.regex(hostname, "<hostname>"))
        if credentials_uri := environment.get("AWS_CONTAINER_CREDENTIALS_RELATIVE_URI"):
            snapshot.add_transformer(snapshot.transform.regex(credentials_uri, "<credentials-uri>"))

        snapshot.match("environment", environment)

    @markers.aws.only_localstack
    def test_run_task_non_default_region(self, aws_client_factory, cleanups):
        factory = aws_client_factory(region_name="us-west-1")
        cluster_name = f"test-cluster-{short_uid()}"
        cluster_arn = factory.ecs.create_cluster(clusterName=cluster_name)["cluster"]["clusterArn"]
        cleanups.append(lambda: factory.ecs.delete_cluster(cluster=cluster_arn))

        secret = f"my-secret-value-{short_uid()}"
        secret_name = f"my-secret-{short_uid()}"
        factory.secretsmanager.create_secret(
            Name=secret_name,
            SecretString=secret,
        )
        cleanups.append(lambda: factory.secretsmanager.delete_secret(SecretId=secret_name))
        secret_arn = factory.secretsmanager.describe_secret(SecretId=secret_name)["ARN"]

        vpc_id = factory.ec2.create_vpc(CidrBlock="10.0.0.0/16")["Vpc"]["VpcId"]
        subnet_id1 = factory.ec2.create_subnet(CidrBlock="10.0.0.0/24", VpcId=vpc_id)["Subnet"][
            "SubnetId"
        ]
        cleanups.append(lambda: factory.ec2.delete_subnet(SubnetId=subnet_id1))
        subnet_id2 = factory.ec2.create_subnet(CidrBlock="10.0.1.0/24", VpcId=vpc_id)["Subnet"][
            "SubnetId"
        ]
        cleanups.append(lambda: factory.ec2.delete_subnet(SubnetId=subnet_id2))

        subnets = factory.ec2.describe_subnets(Filters=[{"Name": "vpc-id", "Values": [vpc_id]}])[
            "Subnets"
        ]
        subnet_ids = [subnet["SubnetId"] for subnet in subnets]

        task_family = f"test_family_{short_uid()}"
        container_name = f"test_container_{short_uid()}"

        log_group_name = f"test-log-group-{short_uid()}"
        factory.logs.create_log_group(logGroupName=log_group_name)
        cleanups.append(lambda: factory.logs.delete_log_group(logGroupName=log_group_name))

        task_definition = {
            "family": task_family,
            "requiresCompatibilities": ["FARGATE"],
            "networkMode": "awsvpc",
            "cpu": "0.5 vCPU",
            "memory": "1GB",
            "containerDefinitions": [
                {
                    "name": container_name,
                    "image": "ubuntu:latest",
                    "cpu": 128,
                    "memory": 256,
                    "logConfiguration": {
                        "logDriver": "awslogs",
                        "options": {
                            "awslogs-group": log_group_name,
                            "awslogs-region": "us-west-1",
                            "awslogs-stream-prefix": "my-container",
                        },
                    },
                    "command": ["bash", "-c", "test -v MY_SECRET"],
                    "secrets": [
                        {
                            "name": "MY_SECRET",
                            "valueFrom": secret_arn,
                        },
                    ],
                }
            ],
        }
        task_def_arn = factory.ecs.register_task_definition(**task_definition)["taskDefinition"][
            "taskDefinitionArn"
        ]
        cleanups.append(lambda: factory.ecs.deregister_task_definition(taskDefinition=task_def_arn))

        result = factory.ecs.run_task(
            taskDefinition=task_def_arn,
            cluster=cluster_arn,
            count=1,
            launchType="FARGATE",
            enableExecuteCommand=True,
            networkConfiguration={
                "awsvpcConfiguration": {
                    "subnets": subnet_ids,
                    "assignPublicIp": "ENABLED",
                }
            },
        )

        task_arn = result["tasks"][0]["taskArn"]

        factory.ecs.get_waiter("tasks_stopped").wait(
            cluster=cluster_arn,
            tasks=[task_arn],
            WaiterConfig={"Delay": 1, "MaxAttempts": 10},
        )
        cleanups.append(lambda: factory.ecs.stop_task(task=task_arn, cluster=cluster_name))
        result = factory.ecs.describe_tasks(cluster=cluster_arn, tasks=[task_arn])
        assert result["tasks"][0]["lastStatus"] == "STOPPED"

    @markers.aws.validated
    @pytest.mark.parametrize(
        "launch_type",
        [
            "FARGATE",
        ],
    )  # Extend to EC2 when we have a way to run EC2 tasks
    def test_get_aws_execution_env_from_task(
        self,
        launch_type,
        create_cluster,
        execution_role,
        vpc_id,
        register_task_definition,
        cleanups,
        aws_client,
        snapshot,
    ):
        cluster_arn = create_cluster()
        subnets = aws_client.ec2.describe_subnets(Filters=[{"Name": "vpc-id", "Values": [vpc_id]}])[
            "Subnets"
        ]
        subnet_ids = [subnet["SubnetId"] for subnet in subnets]

        task_family = f"test_family_{short_uid()}"
        container_name = f"test_container_{short_uid()}"

        log_group_name = f"test-log-group-{short_uid()}"
        aws_client.logs.create_log_group(logGroupName=log_group_name)
        cleanups.append(lambda: aws_client.logs.delete_log_group(logGroupName=log_group_name))

        task_definition = {
            "family": task_family,
            "executionRoleArn": execution_role["Role"]["Arn"],
            "taskRoleArn": execution_role["Role"]["Arn"],
            "requiresCompatibilities": ["FARGATE"],
            "networkMode": "awsvpc",
            "cpu": "0.5 vCPU",
            "memory": "1GB",
            "containerDefinitions": [
                {
                    "name": container_name,
                    "image": "ubuntu:latest",
                    "cpu": 128,
                    "memory": 256,
                    "logConfiguration": {
                        "logDriver": "awslogs",
                        "options": {
                            "awslogs-group": log_group_name,
                            "awslogs-region": "us-east-1",
                            "awslogs-stream-prefix": "my-container",
                        },
                    },
                    "command": ["bash", "-c", "echo $AWS_EXECUTION_ENV"],
                }
            ],
        }

        task_definition_result = register_task_definition(**task_definition)
        task_definition_arn = task_definition_result["taskDefinition"]["taskDefinitionArn"]

        if launch_type == "FARGATE":
            result = aws_client.ecs.run_task(
                taskDefinition=task_definition_arn,
                cluster=cluster_arn,
                count=1,
                launchType="FARGATE",
                enableExecuteCommand=True,
                networkConfiguration={
                    "awsvpcConfiguration": {
                        "subnets": subnet_ids,
                        "assignPublicIp": "ENABLED",
                    }
                },
            )

        else:
            security_groups = aws_client.ec2.describe_security_groups(
                Filters=[{"Name": "vpc-id", "Values": [vpc_id]}]
            )["SecurityGroups"]
            security_group_ids = [sg["GroupId"] for sg in security_groups]
            ami_id = aws_client.ec2.describe_images(
                Owners=["amazon"],
                Filters=[
                    {"Name": "architecture", "Values": ["x86_64"]},
                    {
                        "Name": "name",
                        "Values": ["al2023-ami-ecs-hvm-2023.0.20230906-kernel-6.1-x86_64"],
                    },
                ],
            )["Images"][0]["ImageId"]
            launch_configuration_name = f"launch-config-{short_uid()}"

            script = f"""#!/bin/bash
                cat <<'EOF' >> /etc/ecs/ecs.config
                ECS_CLUSTER={cluster_arn.split("/")[-1]}
                ECS_WARM_POOLS_CHECK=true
                EOF
            """

            # create key pair
            key_pair_name = f"key-pair-{short_uid()}"
            aws_client.ec2.create_key_pair(KeyName=key_pair_name)
            cleanups.append(lambda: aws_client.ec2.delete_key_pair(KeyName=key_pair_name))

            aws_client.autoscaling.create_launch_configuration(
                LaunchConfigurationName=launch_configuration_name,
                ImageId=ami_id,  # Specify your AMI ID
                KeyName=key_pair_name,
                SecurityGroups=security_group_ids,
                InstanceType="t1.micro",
                UserData=script,  # You can customize the user data if needed
            )
            cleanups.append(
                lambda: aws_client.autoscaling.delete_launch_configuration(
                    LaunchConfigurationName=launch_configuration_name
                )
            )

            asg_name = f"asg-{short_uid()}"
            aws_client.autoscaling.create_auto_scaling_group(
                AutoScalingGroupName=asg_name,
                LaunchConfigurationName=launch_configuration_name,
                MinSize=1,
                MaxSize=1,
                DesiredCapacity=1,
                VPCZoneIdentifier=",".join(subnet_ids),
            )
            cleanups.append(
                lambda: aws_client.autoscaling.delete_auto_scaling_group(
                    AutoScalingGroupName=asg_name, ForceDelete=True
                )
            )

            autoscaling_group_arn = aws_client.autoscaling.describe_auto_scaling_groups(
                AutoScalingGroupNames=[asg_name]
            )["AutoScalingGroups"][0]["AutoScalingGroupARN"]

            capacity_provider_name = f"capacity-provider-{short_uid()}"
            aws_client.ecs.create_capacity_provider(
                name=capacity_provider_name,
                autoScalingGroupProvider={
                    "autoScalingGroupArn": autoscaling_group_arn,
                    "managedScaling": {"status": "ENABLED"},
                },
            )
            cleanups.append(
                lambda: aws_client.ecs.delete_capacity_provider(
                    capacityProvider=capacity_provider_name
                )
            )

            def _wait_for_instances():
                instances = aws_client.ec2.describe_instances(
                    Filters=[{"Name": "instance-state-name", "Values": ["running"]}]
                )["Reservations"][0]["Instances"]
                return len(instances) > 0

            retry(_wait_for_instances, retries=10, sleep=60 if is_aws_cloud() else 1)

            # associate capacity provider with cluster
            aws_client.ecs.put_cluster_capacity_providers(
                cluster=cluster_arn,
                capacityProviders=[capacity_provider_name],
                defaultCapacityProviderStrategy=[
                    {"capacityProvider": capacity_provider_name, "weight": 1, "base": 1}
                ],
            )
            result = aws_client.ecs.run_task(
                taskDefinition=task_definition_arn,
                cluster=cluster_arn,
                count=1,
                enableExecuteCommand=True,
                capacityProviderStrategy=[
                    {"capacityProvider": capacity_provider_name, "weight": 1, "base": 1}
                ],
                networkConfiguration={
                    "awsvpcConfiguration": {
                        "subnets": subnet_ids,
                    }
                },
            )

        delay = 10 if is_aws_cloud() else 1
        max_retries = 1000 if is_aws_cloud() else 10
        task_arn = result["tasks"][0]["taskArn"]

        aws_client.ecs.get_waiter("tasks_stopped").wait(
            cluster=cluster_arn,
            tasks=[task_arn],
            WaiterConfig={"Delay": delay, "MaxAttempts": max_retries},
        )

        # get logs streams
        log_streams = aws_client.logs.describe_log_streams(logGroupName=log_group_name)[
            "logStreams"
        ]

        # get logs
        logs = []
        for log_stream in log_streams:
            response = aws_client.logs.get_log_events(
                logGroupName=log_group_name,
                logStreamName=log_stream["logStreamName"],
            )
            logs.extend([event["message"] for event in response["events"]])
        snapshot.match("get_aws_execution_env_from_task", logs)

    @markers.aws.unknown
    @pytest.mark.skipif(
        condition=using_kubernetes_executor(),
        reason="Task containers ports' overlap because we don't support assigning port numbers yet",
    )
    def test_create_service_run_task(self, deploy_cfn_template, aws_client):
        service_name = f"nginx-{short_uid()}"

        # create stack 1
        cluster_name = f"c-{short_uid()}"
        stack_name1 = f"ecs-prod-stack-{short_uid()}"
        infra_template = load_file(
            os.path.join(os.path.dirname(__file__), "../../templates/ecs.infra.yml")
        )
        deploy_cfn_template(
            stack_name=stack_name1,
            template=infra_template,
            parameters={"ClusterName": cluster_name},
            max_wait=900,
        )

        # assert that the export is present
        exports = aws_client.cloudformation.list_exports()["Exports"]
        names = [e.get("Name") for e in exports]
        assert f"{stack_name1}:ECSTaskExecutionRole" in names

        # create stack 2
        stack_name2 = f"stack-{short_uid()}"
        sample_template = load_file(
            os.path.join(os.path.dirname(__file__), "../../templates/ecs.sample.yml")
        )
        deploy_cfn_template(
            stack_name=stack_name2,
            template=sample_template,
            parameters={"StackName": stack_name1, "ServiceName": service_name},
        )

        # check creation of cluster/tasks/...
        clusters = aws_client.ecs.describe_clusters(clusters=[cluster_name])["clusters"]
        cluster_arn = clusters[0]["clusterArn"]
        assert len(clusters) == 1
        assert clusters[0]["clusterName"] == cluster_name
        tasks = aws_client.ecs.list_tasks(cluster=cluster_name)["taskArns"]
        assert tasks
        tasks = aws_client.ecs.describe_tasks(tasks=tasks, cluster=cluster_name)["tasks"]
        assert tasks
        assert tasks[0]["desiredStatus"] == "RUNNING"
        assert tasks[0]["lastStatus"] == "RUNNING"
        tasks_defs = aws_client.ecs.list_task_definitions(familyPrefix=service_name)
        tasks_defs = tasks_defs["taskDefinitionArns"]
        assert tasks_defs
        tasks_def = aws_client.ecs.describe_task_definition(taskDefinition=tasks_defs[0])[
            "taskDefinition"
        ]
        assert tasks_def
        assert len(tasks_def["containerDefinitions"]) == 2
        assert len(tasks_def["containerDefinitions"]) == 2
        sidecar_container = [
            task for task in tasks_def["containerDefinitions"] if task["name"] == "sidecar-service"
        ]
        assert sidecar_container
        assert sidecar_container[0]["environment"] == [{"name": "testNumber", "value": "123"}]

        task_arn = tasks[0]["taskArn"]

        aws_client.ecs.get_waiter("tasks_running").wait(
            cluster=cluster_arn,
            tasks=[task_arn],
            WaiterConfig={"Delay": 1, "MaxAttempts": 10},
        )

        # check existence of ECR repository
        repo_name = "ecr-repo-2571"

        def check_repository_created():
            response = aws_client.ecr.describe_repositories(repositoryNames=[repo_name])[
                "repositories"
            ]
            assert response
            assert response[0]["repositoryName"] == repo_name

        retry(check_repository_created, retries=8, sleep=0.5)

        # TODO (daniel): Assure containers are removed

    @markers.aws.needs_fixing
    @pytest.mark.skipif(
        condition=using_kubernetes_executor(), reason="overrides not implemented yet"
    )
    def test_ecs_task_overrides(self, create_cluster, register_task_definition, aws_client):
        cluster_arn = create_cluster()
        task_family = f"test_family_{short_uid()}"
        container_name = f"test_container_{short_uid()}"
        task_definition_result = register_task_definition(
            family=task_family,
            containerDefinitions=[
                {
                    "name": container_name,
                    "image": "alpine",
                    "cpu": 10,
                    "memory": 128,
                    "command": ["sh", "-c", "sleep 2"],
                    "environment": [
                        {"name": "TEST_VAR", "value": "SHOULD_BE_OVERWRITTEN"},
                        {"name": "TEST_VAR_2", "value": "SHOULD_NOT_BE_OVERWRITTEN"},
                    ],
                    "logConfiguration": {
                        "logDriver": "awslogs",
                        "options": {
                            "awslogs-group": container_name,
                            "awslogs-region": aws_client.ecs.meta.region_name,
                            "awslogs-create-group": "true",
                            "awslogs-stream-prefix": "container-logs",
                        },
                    },
                }
            ],
        )
        task_definition_arn = task_definition_result["taskDefinition"]["taskDefinitionArn"]
        tasks = aws_client.ecs.run_task(
            taskDefinition=task_definition_arn,
            overrides={
                "containerOverrides": [
                    {
                        "environment": [{"name": "TEST_VAR", "value": "OVERWRITTEN"}],
                        "command": ["sh", "-c", "env && sleep 2"],
                    }
                ]
            },
            cluster=cluster_arn,
        )
        task_arn = tasks["tasks"][0]["taskArn"]

        aws_client.ecs.get_waiter("tasks_running").wait(
            cluster=cluster_arn,
            tasks=[task_arn],
            WaiterConfig={"Delay": 1, "MaxAttempts": 10},
        )

        def _check_logs():
            logs = [
                log_event["message"]
                for log_event in aws_client.logs.filter_log_events(logGroupName=container_name)[
                    "events"
                ]
            ]
            assert any("TEST_VAR=OVERWRITTEN" in log_entry for log_entry in logs)
            assert any("TEST_VAR_2=SHOULD_NOT_BE_OVERWRITTEN" in log_entry for log_entry in logs)

        retry(_check_logs, retries=10, sleep=0.7)

        aws_client.ecs.get_waiter("tasks_stopped").wait(
            cluster=cluster_arn,
            tasks=[task_arn],
            WaiterConfig={"Delay": 1, "MaxAttempts": 10},
        )
        response = aws_client.ecs.describe_tasks(tasks=[task_arn], cluster=cluster_arn)
        assert response["tasks"][0]["lastStatus"] == "STOPPED"

    @markers.aws.needs_fixing
    def test_start_task_definition_multiple_times(
        self, create_cluster, register_task_definition, aws_client
    ):
        cluster_arn = create_cluster()
        task_family = f"test_family_{short_uid()}"
        container_name = f"test_container_{short_uid()}"
        task_definition_result = register_task_definition(
            family=task_family,
            containerDefinitions=[
                {
                    "name": container_name,
                    "image": "alpine",
                    "cpu": 10,
                    "memory": 128,
                    "command": ["sleep", "2"],
                }
            ],
        )
        task_definition_arn = task_definition_result["taskDefinition"]["taskDefinitionArn"]
        tasks = aws_client.ecs.run_task(taskDefinition=task_definition_arn, cluster=cluster_arn)
        task_arn = tasks["tasks"][0]["taskArn"]

        aws_client.ecs.get_waiter("tasks_running").wait(
            cluster=cluster_arn,
            tasks=[task_arn],
            WaiterConfig={"Delay": 1, "MaxAttempts": 10},
        )
        aws_client.ecs.get_waiter("tasks_stopped").wait(
            cluster=cluster_arn,
            tasks=[task_arn],
            WaiterConfig={"Delay": 1, "MaxAttempts": 10},
        )

        tasks = aws_client.ecs.run_task(taskDefinition=task_definition_arn, cluster=cluster_arn)
        task_arn = tasks["tasks"][0]["taskArn"]

        aws_client.ecs.get_waiter("tasks_running").wait(
            cluster=cluster_arn,
            tasks=[task_arn],
            WaiterConfig={"Delay": 1, "MaxAttempts": 10},
        )
        aws_client.ecs.get_waiter("tasks_stopped").wait(
            cluster=cluster_arn,
            tasks=[task_arn],
            WaiterConfig={"Delay": 1, "MaxAttempts": 10},
        )

    @pytest.mark.skipif(
        condition=in_ci(),
        reason="BuildJet AMD64 CI Runner do not allow setting NET_ADMIN on docker container",
    )
    @pytest.mark.skipif(
        condition=using_kubernetes_executor(),
        reason="Capability changes not supported in kubernetes yet",
    )
    @markers.aws.unknown
    def test_start_task_definition_with_cap_add(
        self, create_cluster, register_task_definition, aws_client
    ):
        cluster_arn = create_cluster()
        task_family = f"test_family_{short_uid()}"
        container_name = f"test_container_{short_uid()}"
        task_definition_result = register_task_definition(
            family=task_family,
            containerDefinitions=[
                {
                    "name": container_name,
                    "image": "alpine",
                    "cpu": 10,
                    "memory": 128,
                    "command": [
                        "sh",
                        "-c",
                        "ip link add dummy0 type dummy && ip link delete dummy0 && echo success",
                    ],
                    "linuxParameters": {"capabilities": {"add": ["NET_ADMIN"]}},
                    "logConfiguration": {
                        "logDriver": "awslogs",
                        "options": {
                            "awslogs-group": container_name,
                            "awslogs-region": aws_client.ecs.meta.region_name,
                            "awslogs-create-group": "true",
                            "awslogs-stream-prefix": "container-logs",
                        },
                    },
                }
            ],
        )
        task_definition_arn = task_definition_result["taskDefinition"]["taskDefinitionArn"]
        result = aws_client.ecs.run_task(taskDefinition=task_definition_arn, cluster=cluster_arn)
        task_arn = result["tasks"][0]["taskArn"]

        def _check_logs():
            logs = [
                log_event["message"]
                for log_event in aws_client.logs.filter_log_events(logGroupName=container_name)[
                    "events"
                ]
            ]
            assert any("success" in log_entry for log_entry in logs)

        retry(_check_logs, retries=10, sleep=0.7)

        aws_client.ecs.get_waiter("tasks_stopped").wait(
            cluster=cluster_arn,
            tasks=[task_arn],
            WaiterConfig={"Delay": 1, "MaxAttempts": 10},
        )

    @markers.aws.validated
    def test_start_task_definition_with_cap_drop(
        self,
        create_cluster,
        register_task_definition,
        aws_client,
        vpc_id,
        execution_role,
    ):
        cluster_arn = create_cluster()
        task_family = f"test_family_{short_uid()}"
        container_name = f"test_container_{short_uid()}"
        task_definition_result = register_task_definition(
            family=task_family,
            taskRoleArn=execution_role["Role"]["Arn"],
            executionRoleArn=execution_role["Role"]["Arn"],
            requiresCompatibilities=["FARGATE"],
            networkMode="awsvpc",
            cpu="0.5 vCPU",
            memory="1GB",
            containerDefinitions=[
                {
                    "name": container_name,
                    "image": "alpine",
                    "command": ["chown", "nobody", "/"],
                    "linuxParameters": {"capabilities": {"drop": ["CHOWN"]}},
                    "cpu": 128,
                    "memory": 256,
                }
            ],
        )
        task_definition_arn = task_definition_result["taskDefinition"]["taskDefinitionArn"]

        subnets = aws_client.ec2.describe_subnets(Filters=[{"Name": "vpc-id", "Values": [vpc_id]}])[
            "Subnets"
        ]
        subnet_ids = [subnet["SubnetId"] for subnet in subnets]
        result = aws_client.ecs.run_task(
            taskDefinition=task_definition_arn,
            cluster=cluster_arn,
            launchType="FARGATE",
            enableExecuteCommand=True,
            networkConfiguration={
                "awsvpcConfiguration": {
                    "subnets": subnet_ids,
                    "assignPublicIp": "ENABLED",
                }
            },
        )
        task_arn = result["tasks"][0]["taskArn"]

        delay = 5
        max_retries = 40
        if not is_aws_cloud():
            delay = 1
            max_retries = 10

        aws_client.ecs.get_waiter("tasks_stopped").wait(
            cluster=cluster_arn,
            tasks=[task_arn],
            WaiterConfig={"Delay": delay, "MaxAttempts": max_retries},
        )
        response = aws_client.ecs.describe_tasks(tasks=[task_arn], cluster=cluster_arn)
        assert response["tasks"][0]["lastStatus"] == "STOPPED"

    @markers.aws.validated
    def test_start_task_state_stopped(
        self,
        create_cluster,
        register_task_definition,
        aws_client,
        vpc_id,
        execution_role,
    ):
        cluster_arn = create_cluster()
        task_family = f"test_family_{short_uid()}"
        container_name = f"test_container_{short_uid()}"
        task_definition_result = register_task_definition(
            family=task_family,
            taskRoleArn=execution_role["Role"]["Arn"],
            executionRoleArn=execution_role["Role"]["Arn"],
            requiresCompatibilities=["FARGATE"],
            networkMode="awsvpc",
            cpu="0.5 vCPU",
            memory="1GB",
            containerDefinitions=[
                {
                    "name": container_name,
                    "image": "alpine",
                    "cpu": 10,
                    "memory": 128,
                    "command": ["random-non-existent-command"],
                }
            ],
        )
        task_definition_arn = task_definition_result["taskDefinition"]["taskDefinitionArn"]
        subnets = aws_client.ec2.describe_subnets(Filters=[{"Name": "vpc-id", "Values": [vpc_id]}])[
            "Subnets"
        ]
        subnet_ids = [subnet["SubnetId"] for subnet in subnets]
        result = aws_client.ecs.run_task(
            taskDefinition=task_definition_arn,
            cluster=cluster_arn,
            launchType="FARGATE",
            enableExecuteCommand=True,
            networkConfiguration={
                "awsvpcConfiguration": {
                    "subnets": subnet_ids,
                    "assignPublicIp": "ENABLED",
                }
            },
        )
        task_arn = result["tasks"][0]["taskArn"]

        delay = 5
        max_retries = 40
        if not is_aws_cloud():
            delay = 1
            max_retries = 10

        aws_client.ecs.get_waiter("tasks_stopped").wait(
            cluster=cluster_arn,
            tasks=[task_arn],
            WaiterConfig={"Delay": delay, "MaxAttempts": max_retries},
        )
        response = aws_client.ecs.describe_tasks(tasks=[task_arn], cluster=cluster_arn)
        assert response["tasks"][0]["lastStatus"] == "STOPPED"

    @markers.aws.only_localstack
    @pytest.mark.parametrize(
        "command,requires_dns_server",
        [
            (
                [
                    "curl",
                    "-s",
                    f"https://something.localhost.localstack.cloud:{config.GATEWAY_LISTEN[0].port}/_localstack/health",
                ],
                True,
            ),
            (["sh", "-c", "curl $AWS_ENDPOINT_URL/_localstack/health"], False),
        ],
        ids=["dns", "envar"],
    )
    @pytest.mark.skipif(
        condition=using_kubernetes_executor(),
        reason="Seamless networking not supported in kubernetes yet",
    )
    def test_task_connect_to_localstack(
        self,
        create_cluster,
        register_task_definition,
        aws_client,
        command,
        requires_dns_server,
        request,
    ):
        if requires_dns_server and not config.use_custom_dns():
            pytest.skip(reason="Test only valid if dns server is running.")

        # our k8s tests do not set the required information in environment variables to support this test working
        if request.node.callspec.id == "envar" and using_kubernetes_executor():
            pytest.skip(reason="Test only works when LocalStack is launched from our helm chart")

        cluster_arn = create_cluster()
        task_family = f"test_family_{short_uid()}"
        container_name = f"test_container_{short_uid()}"
        task_definition_result = register_task_definition(
            family=task_family,
            containerDefinitions=[
                {
                    "name": container_name,
                    "image": "curlimages/curl:8.3.0",
                    "cpu": 10,
                    "memory": 128,
                    "command": command,
                    "logConfiguration": {
                        "logDriver": "awslogs",
                        "options": {
                            "awslogs-group": container_name,
                            "awslogs-region": aws_client.ecs.meta.region_name,
                            "awslogs-create-group": "true",
                            "awslogs-stream-prefix": "ls-connection",
                        },
                    },
                }
            ],
        )
        task_definition_arn = task_definition_result["taskDefinition"]["taskDefinitionArn"]
        aws_client.ecs.run_task(taskDefinition=task_definition_arn, cluster=cluster_arn)

        # inspect container and output
        def _check_logs():
            logs = [
                log_event["message"]
                for log_event in aws_client.logs.filter_log_events(logGroupName=container_name)[
                    "events"
                ]
            ]
            # assert that env var has been passed to the container
            assert any('"services"' in log_entry for log_entry in logs)

        retry(_check_logs, retries=10, sleep=0.7)

    @markers.aws.needs_fixing
    def test_describe_service_with_task_definition(
        self, create_cluster, register_task_definition, aws_client
    ):
        cluster_arn = create_cluster()
        task_family = f"test_family_{short_uid()}"
        task_definition_result = register_task_definition(
            family=task_family,
            containerDefinitions=[
                {
                    "name": "alpine",
                    "image": "alpine",
                    "cpu": 10,
                    "memory": 128,
                    "command": ["sleep", "3"],
                }
            ],
        )
        task_definition_arn = task_definition_result["taskDefinition"]["taskDefinitionArn"]

        service_name = f"test_service_{short_uid()}"
        service_creation_result = aws_client.ecs.create_service(
            serviceName=service_name,
            cluster=cluster_arn,
            taskDefinition=task_definition_arn,
            desiredCount=1,
        )
        service_arn = service_creation_result["service"]["serviceArn"]
        assert (
            service_creation_result["service"]["deployments"][0]["taskDefinition"]
            == task_definition_arn
        )
        assert service_creation_result["service"]["desiredCount"] == 1

        tasks = aws_client.ecs.list_tasks(cluster=cluster_arn, serviceName=service_name)["taskArns"]
        task_arn = tasks[0]

        aws_client.ecs.get_waiter("tasks_running").wait(
            cluster=cluster_arn,
            tasks=[task_arn],
            WaiterConfig={"Delay": 1, "MaxAttempts": 10},
        )

        service_description_result = aws_client.ecs.describe_services(
            services=[service_arn], cluster=cluster_arn
        )
        service = service_description_result["services"][0]
        assert service["deployments"][0]["taskDefinition"] == task_definition_arn
        assert service["deployments"][0]["desiredCount"] == 1
        assert service["deployments"][0]["runningCount"] == 1
        assert service["deployments"][0]["pendingCount"] == 0
        assert service["desiredCount"] == 1
        assert service["runningCount"] == 1
        assert service["pendingCount"] == 0

        aws_client.ecs.get_waiter("tasks_stopped").wait(
            cluster=cluster_arn,
            tasks=[task_arn],
            WaiterConfig={"Delay": 1, "MaxAttempts": 10},
        )

    @markers.aws.unknown
    def test_subscribe_ecs_events(
        self, create_cluster, sqs_queue, dummy_task_definition, aws_client
    ):
        cluster_arn = create_cluster()
        # subscribe to ecs events
        rule_name = f"ecs-rule-{short_uid()}"
        target_id = f"ecs-target-{short_uid()}"
        queue_arn = aws_client.sqs.get_queue_attributes(QueueUrl=sqs_queue, AttributeNames=["All"])[
            "Attributes"
        ]["QueueArn"]
        aws_client.events.put_rule(Name=rule_name, EventPattern='{"source":["aws.ecs"]}')
        aws_client.events.put_targets(Rule=rule_name, Targets=[{"Id": target_id, "Arn": queue_arn}])

        def assert_events(*args):
            response = aws_client.sqs.receive_message(
                QueueUrl=sqs_queue, MaxNumberOfMessages=1, WaitTimeSeconds=3
            )
            messages = response.get("Messages", [])
            messages = [m for m in messages if "ECS Task State Change" in str(m)]
            assert len(messages) == 1
            event = json.loads(messages[0]["Body"])
            assert event["detail-type"] == "ECS Task State Change"
            assert event["source"] == "aws.ecs"
            assert event["resources"][0] == task_arn
            aws_client.sqs.delete_message(
                QueueUrl=sqs_queue, ReceiptHandle=messages[0]["ReceiptHandle"]
            )

        try:
            # create task
            task_definition_result = dummy_task_definition
            task_definition_arn = task_definition_result["taskDefinition"]["taskDefinitionArn"]
            task_arn = aws_client.ecs.run_task(
                taskDefinition=task_definition_arn, cluster=cluster_arn
            )["tasks"][0]["taskArn"]

            # check for startup event
            retry(assert_events)
            # check for stopped event
            retry(assert_events)
        finally:
            try:
                aws_client.events.remove_targets(Rule=rule_name, Ids=[target_id])
            except Exception:
                LOG.debug("Error removing target %s from rule %s", target_id, rule_name)
            try:
                aws_client.events.delete_rule(Name=rule_name)
            except Exception:
                LOG.debug("Error deleting event rule %s", rule_name)

    @pytest.mark.slow
    @markers.aws.unknown
    def test_ecs_task_multiple(self, create_cluster, aws_client):
        cluster_arn = create_cluster()
        task_def = aws_client.ecs.register_task_definition(
            family="worker",
            memory="512",
            cpu="256",
            containerDefinitions=[
                {
                    "name": "container-img",
                    "image": "library/busybox",
                    "memory": 512,
                    "cpu": 256,
                    "command": ["sleep", "5"],
                }
            ],
        )
        task_def_arn = task_def["taskDefinition"]["taskDefinitionArn"]

        def run_task():
            return aws_client.ecs.run_task(
                taskDefinition=task_def_arn,
                cluster=cluster_arn,
                count=1,
                launchType="FARGATE",
                propagateTags="TASK_DEFINITION",
                overrides={
                    "containerOverrides": [
                        {
                            "name": "worker",
                            "environment": [{"name": "TRIGGER_TO_WORKER", "value": "working"}],
                        }
                    ],
                },
            )

        run_task_result = run_task()
        # first task is now active, but we should be able to start another one
        run_task_result_2 = run_task()

        def all_task_status():
            describe_task_result = aws_client.ecs.describe_tasks(
                cluster=cluster_arn,
                tasks=[
                    run_task_result["tasks"][0]["taskArn"],
                    run_task_result_2["tasks"][0]["taskArn"],
                ],
            )
            if describe_task_result["failures"]:
                raise ShortCircuitWaitException(f'tasks failed: {describe_task_result["failures"]}')
            return all(
                [
                    task["lastStatus"] in ["RUNNING", "STOPPED"]
                    for task in describe_task_result["tasks"]
                ]
            )

        assert wait_until(all_task_status)

    @markers.aws.validated
    @pytest.mark.skipif(
        condition=using_kubernetes_executor(),
        reason="Not implemented for kubernetes yet",
    )
    def test_task_generates_logs_live(
        self,
        vpc_id,
        register_task_definition,
        create_cluster,
        aws_client,
        cleanups,
        region_name,
        execution_role,
    ):
        cluster_arn = create_cluster()
        log_group_name = f"log-group-{short_uid()}"
        log_stream_prefix = f"stream-{short_uid()}"

        aws_client.iam.put_role_policy(
            RoleName=execution_role["Role"]["RoleName"],
            PolicyName="test_policy",
            PolicyDocument=json.dumps(
                {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Action": [
                                "logs:CreateLogGroup",
                                "logs:CreateLogStream",
                                "logs:PutLogEvents",
                            ],
                            "Resource": "*",
                        },
                    ],
                }
            ),
        )
        if is_aws_cloud():
            time.sleep(15)

        command = "while true; do echo Running; sleep 1; done"
        task_def = register_task_definition(
            family="worker",
            networkMode="awsvpc",
            cpu="0.5 vCPU",
            memory="1GB",
            executionRoleArn=execution_role["Role"]["Arn"],
            taskRoleArn=execution_role["Role"]["Arn"],
            requiresCompatibilities=[
                "FARGATE",
            ],
            containerDefinitions=[
                {
                    "name": "container-img",
                    "image": "ubuntu",
                    "memory": 512,
                    "cpu": 256,
                    "command": ["sh", "-c", command],
                    "logConfiguration": {
                        "logDriver": "awslogs",
                        "options": {
                            "awslogs-create-group": "true",
                            "awslogs-group": log_group_name,
                            "awslogs-region": region_name,
                            "awslogs-stream-prefix": log_stream_prefix,
                        },
                    },
                }
            ],
        )
        task_def_arn = task_def["taskDefinition"]["taskDefinitionArn"]

        # list subnets id
        subnets = aws_client.ec2.describe_subnets(Filters=[{"Name": "vpc-id", "Values": [vpc_id]}])[
            "Subnets"
        ]
        subnet_ids = [subnet["SubnetId"] for subnet in subnets]
        run_task_result = aws_client.ecs.run_task(
            taskDefinition=task_def_arn,
            cluster=cluster_arn,
            count=1,
            launchType="FARGATE",
            propagateTags="TASK_DEFINITION",
            networkConfiguration={
                "awsvpcConfiguration": {
                    "subnets": subnet_ids,
                    "assignPublicIp": "ENABLED",
                }
            },
        )
        task_arn = run_task_result["tasks"][0]["taskArn"]
        delay = 1
        max_attempts = 10
        if is_aws_cloud():
            # fargate can take a while to run the task
            delay = 5
            max_attempts = 20

        aws_client.ecs.get_waiter("tasks_running").wait(
            cluster=cluster_arn,
            tasks=[task_arn],
            WaiterConfig={"Delay": delay, "MaxAttempts": max_attempts},
        )

        def stop_task():
            aws_client.ecs.stop_task(task=task_arn, cluster=cluster_arn)
            aws_client.ecs.get_waiter("tasks_stopped").wait(
                cluster=cluster_arn,
                tasks=[task_arn],
                WaiterConfig={"Delay": delay, "MaxAttempts": max_attempts},
            )

        cleanups.append(stop_task)

        logs = get_task_logs(
            logs_client=aws_client.logs,
            log_group_name=log_group_name,
            log_stream_prefix=log_stream_prefix,
        )
        # make sure we receive more than one message
        for message in islice(logs, 5):
            assert "Running" in message

    @markers.aws.validated
    @pytest.mark.skipif(
        condition=using_kubernetes_executor(),
        reason="Not implemented for kubernetes yet",
    )
    def test_failed_tasks_log_to_cloudwatch(
        self,
        vpc_id,
        register_task_definition,
        create_cluster,
        aws_client,
        region_name,
        execution_role,
    ):
        cluster_arn = create_cluster()
        log_group_name = f"log-group-{short_uid()}"
        log_stream_prefix = f"stream-{short_uid()}"

        aws_client.iam.put_role_policy(
            RoleName=execution_role["Role"]["RoleName"],
            PolicyName="test_policy",
            PolicyDocument=json.dumps(
                {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Action": [
                                "logs:CreateLogGroup",
                                "logs:CreateLogStream",
                                "logs:PutLogEvents",
                            ],
                            "Resource": "*",
                        },
                    ],
                }
            ),
        )
        if is_aws_cloud():
            time.sleep(15)

        command = "echo Failing task; false"
        task_def = register_task_definition(
            family="worker",
            networkMode="awsvpc",
            cpu="0.5 vCPU",
            memory="1GB",
            executionRoleArn=execution_role["Role"]["Arn"],
            taskRoleArn=execution_role["Role"]["Arn"],
            requiresCompatibilities=[
                "FARGATE",
            ],
            containerDefinitions=[
                {
                    "name": "container-img",
                    "image": "ubuntu",
                    "memory": 512,
                    "cpu": 256,
                    "command": ["sh", "-c", command],
                    "logConfiguration": {
                        "logDriver": "awslogs",
                        "options": {
                            "awslogs-create-group": "true",
                            "awslogs-group": log_group_name,
                            "awslogs-region": region_name,
                            "awslogs-stream-prefix": log_stream_prefix,
                        },
                    },
                }
            ],
        )
        task_def_arn = task_def["taskDefinition"]["taskDefinitionArn"]

        # list subnets id
        subnets = aws_client.ec2.describe_subnets(Filters=[{"Name": "vpc-id", "Values": [vpc_id]}])[
            "Subnets"
        ]
        subnet_ids = [subnet["SubnetId"] for subnet in subnets]
        run_task_result = aws_client.ecs.run_task(
            taskDefinition=task_def_arn,
            cluster=cluster_arn,
            count=1,
            launchType="FARGATE",
            propagateTags="TASK_DEFINITION",
            networkConfiguration={
                "awsvpcConfiguration": {
                    "subnets": subnet_ids,
                    "assignPublicIp": "ENABLED",
                }
            },
        )
        task_arn = run_task_result["tasks"][0]["taskArn"]
        delay = 1
        max_attempts = 10
        if is_aws_cloud():
            # fargate can take a while to run the task
            delay = 5
            max_attempts = 20

        # wait for the task to stop
        aws_client.ecs.get_waiter("tasks_stopped").wait(
            cluster=cluster_arn,
            tasks=[task_arn],
            WaiterConfig={"Delay": delay, "MaxAttempts": max_attempts},
        )

        logs = get_task_logs(
            logs_client=aws_client.logs,
            log_group_name=log_group_name,
            log_stream_prefix=log_stream_prefix,
            num_iterations=2,
        )
        messages = list(logs)

        assert messages == ["Failing task"]

    @markers.aws.validated
    @pytest.mark.parametrize("define_secret", [True, False])
    def test_create_task_with_secrets(
        self,
        define_secret,
        create_cluster,
        register_task_definition,
        aws_client,
        cleanups,
        vpc_id,
        execution_role,
        region_name,
    ):
        cluster_arn = create_cluster()
        secret = f"my-secret-value-{short_uid()}"
        parameter_name = f"my-parameter-{short_uid()}"
        secret_name = f"my-secret-{short_uid()}"
        aws_client.ssm.put_parameter(
            Name=parameter_name,
            Value=secret,
            Type="String",
        )
        cleanups.append(lambda: aws_client.ssm.delete_parameter(Name=parameter_name))
        parameter_arn = aws_client.ssm.get_parameter(
            Name=parameter_name,
        )["Parameter"]["ARN"]
        aws_client.secretsmanager.create_secret(
            Name=secret_name,
            SecretString=secret,
        )
        cleanups.append(lambda: aws_client.secretsmanager.delete_secret(SecretId=secret_name))
        secret_arn = aws_client.secretsmanager.describe_secret(SecretId=secret_name)["ARN"]

        aws_client.iam.put_role_policy(
            RoleName=execution_role["Role"]["RoleName"],
            PolicyName="test_policy",
            PolicyDocument=json.dumps(
                {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Action": "ssm:GetParameters",
                            "Resource": parameter_arn,
                            "Effect": "Allow",
                        },
                        {
                            "Action": "secretsmanager:GetSecretValue",
                            "Resource": secret_arn,
                            "Effect": "Allow",
                        },
                        {
                            "Effect": "Allow",
                            "Action": [
                                "logs:CreateLogGroup",
                                "logs:CreateLogStream",
                                "logs:PutLogEvents",
                            ],
                            "Resource": "*",
                        },
                    ],
                }
            ),
        )
        if is_aws_cloud():
            time.sleep(15)

        # list subnets id
        subnets = aws_client.ec2.describe_subnets(Filters=[{"Name": "vpc-id", "Values": [vpc_id]}])[
            "Subnets"
        ]
        subnet_ids = [subnet["SubnetId"] for subnet in subnets]

        task_family = f"test_family_{short_uid()}"
        container_name = f"test_container_{short_uid()}"

        log_group_name = f"test-log-group-{short_uid()}"
        aws_client.logs.create_log_group(logGroupName=log_group_name)
        cleanups.append(lambda: aws_client.logs.delete_log_group(logGroupName=log_group_name))

        task_definition = {
            "family": task_family,
            "executionRoleArn": execution_role["Role"]["Arn"],
            "taskRoleArn": execution_role["Role"]["Arn"],
            "requiresCompatibilities": ["FARGATE"],
            "networkMode": "awsvpc",
            "cpu": "0.5 vCPU",
            "memory": "1GB",
            "containerDefinitions": [
                {
                    "name": container_name,
                    "image": "ubuntu:latest",
                    "cpu": 128,
                    "memory": 256,
                    "logConfiguration": {
                        "logDriver": "awslogs",
                        "options": {
                            "awslogs-group": log_group_name,
                            "awslogs-region": region_name,
                            "awslogs-stream-prefix": "my-container",
                        },
                    },
                    "command": ["bash", "-c", "test -v MY_SECRET && test -v MY_PARAMETER"],
                }
            ],
        }

        if define_secret:
            task_definition["containerDefinitions"][0]["secrets"] = [
                {
                    "name": "MY_PARAMETER",
                    "valueFrom": parameter_arn,
                },
                {
                    "name": "MY_SECRET",
                    "valueFrom": secret_arn,
                },
            ]

        task_definition_result = register_task_definition(**task_definition)

        task_definition_arn = task_definition_result["taskDefinition"]["taskDefinitionArn"]
        result = aws_client.ecs.run_task(
            taskDefinition=task_definition_arn,
            cluster=cluster_arn,
            count=1,
            launchType="FARGATE",
            enableExecuteCommand=True,
            networkConfiguration={
                "awsvpcConfiguration": {
                    "subnets": subnet_ids,
                    "assignPublicIp": "ENABLED",
                }
            },
        )

        delay = 5
        max_retries = 40
        if not is_aws_cloud():
            delay = 1
            max_retries = 10
        task_arn = result["tasks"][0]["taskArn"]
        aws_client.ecs.get_waiter("tasks_stopped").wait(
            cluster=cluster_arn,
            tasks=[task_arn],
            WaiterConfig={"Delay": delay, "MaxAttempts": max_retries},
        )
        result = aws_client.ecs.describe_tasks(cluster=cluster_arn, tasks=[task_arn])
        exit_code = result["tasks"][0]["containers"][0]["exitCode"]

        # assert last status
        assert result["tasks"][0]["lastStatus"] == "STOPPED"
        if define_secret:
            assert exit_code == 0
        else:
            assert exit_code == 1

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(
        paths=[
            "$..imageDigest",
            "$..managedAgents",
            "$..name",
            "$..networkInterfaces",
            "$..runtimeId",
            "$..attachments..details",
            "$..attachments..details..value",
            "$..attachments..status",
            "$..availabilityZone",
            "$..enableExecuteCommand",
            "$..executionStoppedAt",
            "$..group",
            "$..overrides.containerOverrides",
            "$..overrides.inferenceAcceleratorOverrides",
            "$..startedBy",
            "$..version",
            # TODO: these fields should be modelled correctly in upcoming refactorings of the service
            "$..desiredStatus",
            "$..stoppedReason",
            "$..stopCode",
        ]
    )
    @pytest.mark.parametrize(
        "use_secret_version_id,use_secret_version_stage",
        [
            (True, False),
            (False, True),
            (False, False),
        ],
    )
    def test_read_from_json_secret(
        self,
        create_secret,
        create_cluster,
        register_task_definition,
        aws_client,
        vpc_id,
        execution_role,
        snapshot,
        use_secret_version_id,
        use_secret_version_stage,
    ):
        snapshot.add_transformer(snapshot.transform.key_value("clusterArn"))
        snapshot.add_transformer(snapshot.transform.key_value("containerArn"))
        snapshot.add_transformer(snapshot.transform.key_value("taskArn"))
        snapshot.add_transformer(snapshot.transform.key_value("taskDefinitionArn"))

        cluster_arn = create_cluster()
        secret_key = "mykey"
        secret_value = "myvalue"
        raw_secret = {secret_key: secret_value}
        secret_contents = json.dumps(raw_secret)
        secret_name = f"my-secret-{short_uid()}"
        create_secret_response = create_secret(
            Name=secret_name,
            SecretString=secret_contents,
        )
        secret_arn = create_secret_response["ARN"]
        match (use_secret_version_id, use_secret_version_stage):
            case (True, False):
                version_id = create_secret_response["VersionId"]
                full_secret_arn = f"{secret_arn}:{secret_key}::{version_id}"
            case (False, True):
                full_secret_arn = f"{secret_arn}:{secret_key}:AWSCURRENT:"
            case (False, False):
                full_secret_arn = f"{secret_arn}:{secret_key}::"
            case _:
                raise ValueError("cannot specify both secret version id and stage")

        aws_client.iam.put_role_policy(
            RoleName=execution_role["Role"]["RoleName"],
            PolicyName="test_policy",
            PolicyDocument=json.dumps(
                {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Action": "secretsmanager:GetSecretValue",
                            "Resource": secret_arn,
                            "Effect": "Allow",
                        },
                        {
                            "Action": "secretsmanager:GetSecretValue",
                            "Resource": secret_arn,
                            "Effect": "Allow",
                        },
                    ],
                }
            ),
        )
        if is_aws_cloud():
            LOG.info("sleeping for IAM role propagation")
            time.sleep(15)

        # list subnets id
        subnets = aws_client.ec2.describe_subnets(Filters=[{"Name": "vpc-id", "Values": [vpc_id]}])[
            "Subnets"
        ]
        subnet_ids = [subnet["SubnetId"] for subnet in subnets]

        task_family = f"test_family_{short_uid()}"
        container_name = f"test_container_{short_uid()}"
        snapshot.add_transformer(snapshot.transform.regex(container_name, "<container-name>"))

        task_definition = {
            "family": task_family,
            "executionRoleArn": execution_role["Role"]["Arn"],
            "taskRoleArn": execution_role["Role"]["Arn"],
            "requiresCompatibilities": ["FARGATE"],
            "networkMode": "awsvpc",
            "cpu": "0.5 vCPU",
            "memory": "1GB",
            "containerDefinitions": [
                {
                    "name": container_name,
                    "image": "ubuntu:latest",
                    "cpu": 128,
                    "memory": 256,
                    "command": ["bash", "-c", f'[ "$MY_SECRET" == "{secret_value}" ]'],
                    "secrets": [
                        {
                            "name": "MY_SECRET",
                            "valueFrom": full_secret_arn,
                        },
                    ],
                }
            ],
        }

        task_definition_result = register_task_definition(**task_definition)

        task_definition_arn = task_definition_result["taskDefinition"]["taskDefinitionArn"]
        result = aws_client.ecs.run_task(
            taskDefinition=task_definition_arn,
            cluster=cluster_arn,
            count=1,
            launchType="FARGATE",
            enableExecuteCommand=True,
            networkConfiguration={
                "awsvpcConfiguration": {
                    "subnets": subnet_ids,
                    "assignPublicIp": "ENABLED",
                }
            },
        )

        delay = 1
        max_retries = 10
        if is_aws_cloud():
            delay = 5
            max_retries = 40
        task_arn = result["tasks"][0]["taskArn"]
        aws_client.ecs.get_waiter("tasks_stopped").wait(
            cluster=cluster_arn,
            tasks=[task_arn],
            WaiterConfig={"Delay": delay, "MaxAttempts": max_retries},
        )
        result = aws_client.ecs.describe_tasks(cluster=cluster_arn, tasks=[task_arn])
        describe_task_output = result["tasks"][0]
        snapshot.match("describe-task", describe_task_output)

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(
        paths=[
            "$..attachments..details..value",
            "$..clusterArn",
            "$..containerInstanceArn",
            "$..containers..imageDigest",
            "$..containers..memory",
            "$..containers..networkInterfaces",
            "$..containers..runtimeId",
            "$..group",
            "$..overrides.containerOverrides",
            "$..overrides.inferenceAcceleratorOverrides",
            "$..taskArn",
            "$..taskDefinitionArn",
            "$..version",
            "$..attachments..id",
            "$..containers..containerArn",
            "$..containers..image",
            "$..stoppedAt",
            "$..stoppingAt",
        ]
    )
    @pytest.mark.skipif(not is_aws_cloud(), reason="Does not work without log streaming")
    def test_update_service_creates_new_deployment(
        self,
        create_cluster,
        register_task_definition,
        default_vpc,
        aws_client,
        snapshot,
        execution_role,
    ):
        snapshot.add_transformer(snapshot.transform.key_value("id"))
        snapshot.add_transformer(snapshot.transform.key_value("taskArn"))
        snapshot.add_transformer(snapshot.transform.key_value("startedBy"))
        snapshot.add_transformer(snapshot.transform.key_value("runtimeId"))
        snapshot.add_transformer(snapshot.transform.key_value("imageDigest"))
        snapshot.add_transformer(snapshot.transform.key_value("availabilityZone"))
        snapshot.add_transformer(snapshot.transform.key_value("containerArn"))

        cluster_arn = create_cluster()
        task_family = f"test_task_{short_uid()}"
        log_group_name_1 = f"log_group_{short_uid()}"
        log_group_name_2 = f"log_group_{short_uid()}"
        kwargs = {
            "family": task_family,
            # using for loop below (instead of `sleep 400`), to allow container to be stopped by Docker client
            "containerDefinitions": [
                {
                    "name": "alpine-container",
                    "image": "alpine",
                    "memory": 128,
                    "command": ["sh", "-c", "echo first; for i in $(seq 1 400); do sleep 1; done"],
                    "logConfiguration": {
                        "logDriver": "awslogs",
                        "options": {
                            "awslogs-create-group": "true",
                            "awslogs-group": log_group_name_1,
                            "awslogs-region": aws_client.ecs.meta.region_name,
                            "awslogs-stream-prefix": "my-container",
                        },
                    },
                }
            ],
            "requiresCompatibilities": ["EC2", "FARGATE"],
            "networkMode": "awsvpc",
            "cpu": "0.5 vCPU",
            "memory": "1GB",
            "executionRoleArn": execution_role["Role"]["Arn"],
            "taskRoleArn": execution_role["Role"]["Arn"],
        }
        snapshot.add_transformer(snapshot.transform.regex(task_family, "<task-family>"))

        task_definition_result = register_task_definition(**kwargs)
        task_definition_arn = task_definition_result["taskDefinition"]["taskDefinitionArn"]

        # determine VPC subnets
        vpc_id = default_vpc["VpcId"]
        subnet_ids = aws_client.ec2.describe_subnets(
            Filters=[{"Name": "vpc-id", "Values": [vpc_id]}]
        )["Subnets"]
        subnet_ids = [sub["SubnetId"] for sub in subnet_ids][:2]

        # create service
        service_name = f"test_service_{short_uid()}"
        snapshot.add_transformer(snapshot.transform.regex(service_name, "<service-name>"))
        result = aws_client.ecs.create_service(
            serviceName=service_name,
            cluster=cluster_arn,
            taskDefinition=task_definition_arn,
            desiredCount=1,
            launchType="FARGATE",
            networkConfiguration={
                "awsvpcConfiguration": {
                    "subnets": subnet_ids,
                    "assignPublicIp": "ENABLED",
                }
            },
        )["service"]
        service_arn = result["serviceArn"]

        delay = 10
        max_retries = 40
        if not is_aws_cloud():
            delay = 1
            max_retries = 10
        aws_client.ecs.get_waiter("services_stable").wait(
            cluster=cluster_arn,
            services=[service_arn],
            WaiterConfig={"Delay": delay, "MaxAttempts": max_retries},
        )

        def _check_logs(log_group_name: str, target_string: str, target_count: int):
            logs = [
                log_event["message"]
                for log_event in aws_client.logs.filter_log_events(logGroupName=log_group_name)[
                    "events"
                ]
            ]
            assert (
                len([log_entry for log_entry in logs if target_string in log_entry]) == target_count
            )

        retry(
            _check_logs,
            retries=20,
            sleep=0.7,
            log_group_name=log_group_name_1,
            target_string="first",
            target_count=1,
        )
        aws_client.ecs.describe_services(cluster=cluster_arn, services=[service_arn])

        # update container definitions, use nginx instead of alpine image
        kwargs["containerDefinitions"][0]["command"] = [
            "sh",
            "-c",
            "echo second; for i in $(seq 1 400); do sleep 1; done",
        ]
        kwargs["containerDefinitions"][0]["logConfiguration"]["options"]["awslogs-group"] = (
            log_group_name_2
        )
        task_definition_result = register_task_definition(**kwargs)
        task_definition_arn = task_definition_result["taskDefinition"]["taskDefinitionArn"]

        # update service
        aws_client.ecs.update_service(
            service=service_name,
            cluster=cluster_arn,
            taskDefinition=task_definition_arn,
            desiredCount=1,
        )
        aws_client.ecs.get_waiter("services_stable").wait(
            cluster=cluster_arn,
            services=[service_arn],
            WaiterConfig={"Delay": delay, "MaxAttempts": max_retries},
        )

        # assert that new local container is started
        retry(
            _check_logs,
            retries=20,
            sleep=0.7,
            log_group_name=log_group_name_2,
            target_string="second",
            target_count=1,
        )

        # update service - same definition as before, but with forceNewDeployment=True
        aws_client.ecs.update_service(
            service=service_name, cluster=cluster_arn, forceNewDeployment=True
        )
        aws_client.ecs.get_waiter("services_stable").wait(
            cluster=cluster_arn,
            services=[service_arn],
            WaiterConfig={"Delay": delay, "MaxAttempts": max_retries},
        )

        retry(
            _check_logs,
            retries=20,
            sleep=0.7,
            log_group_name=log_group_name_2,
            target_string="second",
            target_count=2,
        )

    @markers.aws.validated
    # TODO if we support all APIs in localstack, we can consolidate the parametrization into a single test run
    @pytest.mark.parametrize(
        "task_endpoint_urls",
        [
            (
                [
                    "http://169.254.170.2/v2/metadata",
                    "http://169.254.170.2/v2/metadata/${HOSTNAME}",
                    "http://169.254.170.2/v2/stats",
                    "http://169.254.170.2/v2/stats/${HOSTNAME}",
                ]
            ),
            (
                [
                    "${ECS_CONTAINER_METADATA_URI}",
                    "${ECS_CONTAINER_METADATA_URI}/task",
                    "${ECS_CONTAINER_METADATA_URI}/stats",
                    "${ECS_CONTAINER_METADATA_URI}/task/stats",
                ]
            ),
            (
                [
                    "${ECS_CONTAINER_METADATA_URI_V4}",
                    "${ECS_CONTAINER_METADATA_URI_V4}/task",
                    "${ECS_CONTAINER_METADATA_URI_V4}/stats",
                    "${ECS_CONTAINER_METADATA_URI_V4}/task/stats",
                ]
            ),
        ],
        ids=["v2", "v3", "v4"],
    )
    @pytest.mark.skipif(
        not is_aws_cloud(), reason="ECS task metadata endpoints not implemented in localstack"
    )
    def test_ecs_task_metadata_endpoints(
        self,
        create_cluster,
        register_task_definition,
        aws_client,
        vpc_id,
        execution_role,
        snapshot,
        task_endpoint_urls,
    ):
        log_group_name = f"log-group-{short_uid()}"
        task_family = f"test_family_{short_uid()}"
        container_name = f"test_container_{short_uid()}"
        command = "; echo;".join([f"curl -s {endpoint}" for endpoint in task_endpoint_urls])
        # Amazon ECS tasks on AWS Fargate require that the container run for ~1 second prior
        # to returning the container stats.
        # https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task-metadata-endpoint-v4-fargate.html#task-metadata-endpoint-v4-fargate-paths
        command = "sleep 2; " + command

        cluster_arn = create_cluster()

        snapshot.add_transformer(
            [
                snapshot.transform.key_value("DockerName"),
                snapshot.transform.key_value("DockerId"),
                snapshot.transform.key_value("ImageID"),
                snapshot.transform.key_value("AvailabilityZone"),
                snapshot.transform.key_value("IPv4Addresses", reference_replacement=False),
                snapshot.transform.key_value("MACAddress", reference_replacement=False),
                snapshot.transform.key_value("IPv4SubnetCIDRBlock", reference_replacement=False),
                snapshot.transform.key_value("DomainNameServers", reference_replacement=False),
                snapshot.transform.key_value(
                    "SubnetGatewayIpv4Address", reference_replacement=False
                ),
                snapshot.transform.key_value("ClockErrorBound", reference_replacement=False),
                snapshot.transform.jsonpath(
                    "$..blkio_stats.*", "<blkio-stat>", reference_replacement=False
                ),
                snapshot.transform.regex(task_family, "<task-family>"),
                snapshot.transform.regex(container_name, "<container-name>"),
                snapshot.transform.regex(log_group_name, "<log-group-name>"),
                snapshot.transform.regex(cluster_arn.rpartition("/")[2], "<cluster-name>"),
                snapshot.transform.regex(PATTERN_UUID, "<uuid>"),
                snapshot.transform.structure("$..memory_stats"),
                snapshot.transform.structure("$..cpu_stats"),
                snapshot.transform.structure("$..precpu_stats"),
                snapshot.transform.structure("$..networks"),
            ]
        )

        subnets = aws_client.ec2.describe_subnets(Filters=[{"Name": "vpc-id", "Values": [vpc_id]}])[
            "Subnets"
        ]
        subnet_ids = [subnet["SubnetId"] for subnet in subnets]

        task_definition = {
            "family": task_family,
            "executionRoleArn": execution_role["Role"]["Arn"],
            "taskRoleArn": execution_role["Role"]["Arn"],
            "requiresCompatibilities": ["FARGATE"],
            "networkMode": "awsvpc",
            "cpu": "0.5 vCPU",
            "memory": "1GB",
            "containerDefinitions": [
                {
                    "name": container_name,
                    "image": "curlimages/curl:8.3.0",
                    "cpu": 128,
                    "memory": 256,
                    "command": ["sh", "-c", command],
                    "logConfiguration": {
                        "logDriver": "awslogs",
                        "options": {
                            "awslogs-create-group": "true",
                            "awslogs-group": log_group_name,
                            "awslogs-stream-prefix": "ecs",
                            "awslogs-region": aws_client.ecs.meta.region_name,
                        },
                    },
                }
            ],
        }

        task_definition_result = register_task_definition(**task_definition)

        task_definition_arn = task_definition_result["taskDefinition"]["taskDefinitionArn"]
        result = aws_client.ecs.run_task(
            taskDefinition=task_definition_arn,
            cluster=cluster_arn,
            count=1,
            launchType="FARGATE",
            enableExecuteCommand=True,
            networkConfiguration={
                "awsvpcConfiguration": {
                    "subnets": subnet_ids,
                    "assignPublicIp": "ENABLED",
                }
            },
        )

        delay = 5
        max_retries = 40
        if not is_aws_cloud():
            delay = 1
            max_retries = 10
        task_arn = result["tasks"][0]["taskArn"]
        snapshot.add_transformer(snapshot.transform.regex(task_arn.rpartition("/")[2], "<task-id>"))
        aws_client.ecs.get_waiter("tasks_stopped").wait(
            cluster=cluster_arn,
            tasks=[task_arn],
            WaiterConfig={"Delay": delay, "MaxAttempts": max_retries},
        )
        result = aws_client.ecs.describe_tasks(cluster=cluster_arn, tasks=[task_arn])

        # assert last status
        assert result["tasks"][0]["lastStatus"] == "STOPPED"
        assert result["tasks"][0]["containers"][0]["exitCode"] == 0

        def _check_logs():
            logs = [
                log_event["message"]
                for log_event in aws_client.logs.filter_log_events(logGroupName=log_group_name)[
                    "events"
                ]
            ]
            logs = [json.loads(log_entry) for log_entry in logs if "{" in log_entry]
            assert len(logs) == len(task_endpoint_urls)
            return logs

        logs = retry(_check_logs, retries=20, sleep=5 if is_aws_cloud() else 1)
        snapshot.match("endpoint-responses", logs)


class TestServiceCrud:
    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(
        paths=[
            "$..deploymentController",
            "$..enableECSManagedTags",
            "$..enableExecuteCommand",
            "$..placementConstraints",
            "$..propagateTags",
            "$..deployments",
            "$..status",
        ]
    )
    def test_create_delete_service(
        self, aws_client, snapshot, create_cluster, register_task_definition
    ):
        cluster_name = f"test_cluster-{short_uid()}"
        cluster_arn = create_cluster(clusterName=cluster_name)
        family_name = f"test_task_family-{short_uid()}"
        service_name = f"test_service_{short_uid()}"

        task_definition_result = register_task_definition(
            family=family_name,
            containerDefinitions=[
                {
                    "image": "alpine",
                    "name": "alpine",
                    "memory": 128,
                    "command": ["sh", "-c", "for i in $(seq 1 99); do sleep 1; done"],
                }
            ],
            cpu="0.5 vCPU",
            memory="1GB",
        )
        task_definition_arn = task_definition_result["taskDefinition"]["taskDefinitionArn"]

        snapshot.add_transformer(snapshot.transform.regex(service_name, "service-name"))
        snapshot.add_transformer(snapshot.transform.regex(cluster_name, "cluster-name"))
        snapshot.add_transformer(snapshot.transform.regex(cluster_arn, "cluster-arn"))
        snapshot.add_transformer(snapshot.transform.regex(family_name, "family-name"))
        snapshot.add_transformer(snapshot.transform.regex(task_definition_arn, "<task-arn"))
        snapshot.add_transformer(snapshot.transform.key_value("createdBy", "created-by"))
        snapshot.add_transformer(
            snapshot.transform.key_value("rolloutStateReason", "rollout-state-reason")
        )
        snapshot.add_transformer(snapshot.transform.key_value("rolloutState", "rollout-state"))
        snapshot.add_transformer(snapshot.transform.key_value("id", "id"))
        snapshot.add_transformer(snapshot.transform.key_value("status", "status"))

        service_creation_result = aws_client.ecs.create_service(
            serviceName=service_name,
            cluster=cluster_arn,
            taskDefinition=task_definition_arn,
            desiredCount=0,
        )
        service_arn = service_creation_result["service"]["serviceArn"]
        snapshot.add_transformer(snapshot.transform.regex(service_arn, "<service-arn>"))
        snapshot.match("service-creation-result", service_creation_result["service"])

        aws_client.ecs.get_waiter("services_stable").wait(
            cluster=cluster_arn,
            services=[service_arn],
            WaiterConfig={
                "Delay": 15 if is_aws_cloud() else 1,
                "MaxAttempts": 40 if is_aws_cloud() else 5,
            },
        )
        service_describe_result = aws_client.ecs.describe_services(
            cluster=cluster_arn,
            services=[service_arn],
        )
        snapshot.match("service-describe-result", service_describe_result["services"][0])

        service_update_result = aws_client.ecs.update_service(
            cluster=cluster_arn,
            service=service_name,
            desiredCount=0,
        )
        snapshot.match("service-update-result", service_update_result["service"])

        service_delete_result = aws_client.ecs.delete_service(
            cluster=cluster_arn,
            service=service_name,
        )
        snapshot.match("service-delete-result", service_delete_result["service"])

        aws_client.ecs.get_waiter("services_inactive").wait(
            cluster=cluster_arn,
            services=[service_arn],
            WaiterConfig={
                "Delay": 15 if is_aws_cloud() else 1,
                "MaxAttempts": 40 if is_aws_cloud() else 5,
            },
        )
        service_describe_result = aws_client.ecs.describe_services(
            cluster=cluster_arn,
            services=[service_arn],
        )
        snapshot.match("service-describe-result-2", service_describe_result["services"][0])


@pytest.mark.skipif(
    condition=using_kubernetes_executor(),
    reason="Tests rely on docker client per design",
)
class TestEcsDocker:
    @staticmethod
    def assert_app_started(container_name_prefix: str):
        containers = DOCKER_CLIENT.list_containers(all=True)
        container_name = None
        for container in containers:
            if container["name"].startswith(container_name_prefix):
                container_name = container["name"]
                assert container["status"] == "running"
                break
        assert container_name
        return container_name

    @staticmethod
    def _cluster_name_from_arn(cluster_arn: str) -> str:
        return cluster_arn.split("/")[-1]

    @classmethod
    def _container_name_prefix(cls, cluster_arn: str, task_id: str) -> str:
        cluster_name = cls._cluster_name_from_arn(cluster_arn)
        task_id = task_id.split("/")[-1]
        return f"ls-ecs-{cluster_name}-{task_id}"

    @classmethod
    def _get_task_docker_container_id(cls, cluster_arn: str, task_id: str):
        """
        Return the Docker container ID of a task container.
        Note: currently only works if the task has a single running container associated.
        """
        container_name_prefix = cls._container_name_prefix(cluster_arn=cluster_arn, task_id=task_id)
        containers = DOCKER_CLIENT.list_containers(all=True)
        containers = [
            container for container in containers if container_name_prefix in container["name"]
        ]
        if len(containers) > 1:
            raise Exception(
                f"Found multiple task containers, fetching logs currently only works for a single one: {containers}"
            )
        return containers[0]["id"]

    @classmethod
    def _get_task_container_logs(cls, cluster_arn: str, task_id: str):
        """
        Return the Docker container logs of a task container.
        Note: currently only works if the task has a single running container associated.
        """
        container_id = cls._get_task_docker_container_id(cluster_arn=cluster_arn, task_id=task_id)
        return DOCKER_CLIENT.get_container_logs(container_id)

    @pytest.mark.parametrize("spawn_type", ["run_task", "start_task"])
    @markers.aws.only_localstack
    def test_start_and_stop_task(
        self,
        spawn_type,
        create_cluster,
        register_task_definition,
        aws_client,
        monkeypatch,
    ):
        cluster_arn = create_cluster()
        task_family = f"test_family_{short_uid()}"
        container_name = f"test_container_{short_uid()}"
        task_definition_result = register_task_definition(
            family=task_family,
            containerDefinitions=[
                {
                    "name": container_name,
                    "image": "alpine",
                    "memory": 10,
                    # using for loop below (instead of `sleep 99`), to allow container to be stopped by Docker client
                    "command": ["sh", "-c", "for i in $(seq 1 99); do sleep 1; done"],
                }
            ],
        )
        task_definition_arn = task_definition_result["taskDefinition"]["taskDefinitionArn"]

        kwargs = {}
        if spawn_type == "start_task":
            # Note: start_task(..) requires us to register a container instance and place the task on it explicitly.
            # We're registering a container instance with a dummy EC2 instance ID which will be mocked internally.
            monkeypatch.setattr(ext_config, "EC2_VM_MANAGER", "mock")
            image_id = aws_client.ec2.describe_images()["Images"][0]["ImageId"]
            response = aws_client.ec2.run_instances(ImageId=image_id, MinCount=1, MaxCount=1)
            instance_id = response["Instances"][0]["InstanceId"]
            aws_client.ecs.register_container_instance(
                cluster=cluster_arn,
                instanceIdentityDocument=json.dumps({"instanceId": instance_id}),
            )
            instances = aws_client.ecs.list_container_instances(cluster=cluster_arn)
            kwargs["containerInstances"] = instances["containerInstanceArns"]

        # spawn new task container
        start_method = getattr(aws_client.ecs, spawn_type)
        result = start_method(taskDefinition=task_definition_arn, cluster=cluster_arn, **kwargs)
        task_arn = result["tasks"][0]["taskArn"]
        aws_client.ecs.get_waiter("tasks_running").wait(
            cluster=cluster_arn,
            tasks=[task_arn],
            WaiterConfig={"Delay": 1, "MaxAttempts": 10},
        )

        # stop task, assert that the container has been stopped
        aws_client.ecs.stop_task(task=task_arn, cluster=cluster_arn)
        aws_client.ecs.get_waiter("tasks_stopped").wait(
            cluster=cluster_arn,
            tasks=[task_arn],
            WaiterConfig={"Delay": 1, "MaxAttempts": 10},
        )

    @markers.aws.only_localstack
    def test_set_apparmor_profile(self, create_cluster, register_task_definition, aws_client):
        """Test setting apparmor profile into docker security options. We should look into a better test for this"""
        cluster_arn = create_cluster()
        task_family = f"test_family_{short_uid()}"
        container_name = f"test_container_{short_uid()}"
        task_definition_result = register_task_definition(
            family=task_family,
            containerDefinitions=[
                {
                    "name": container_name,
                    "image": "alpine",
                    "cpu": 10,
                    "memory": 128,
                    "command": ["sleep", "2"],
                    "dockerSecurityOptions": ["apparmor=docker-default"],
                }
            ],
        )
        task_definition_arn = task_definition_result["taskDefinition"]["taskDefinitionArn"]
        tasks = aws_client.ecs.run_task(taskDefinition=task_definition_arn, cluster=cluster_arn)
        task_arn = tasks["tasks"][0]["taskArn"]

        aws_client.ecs.get_waiter("tasks_running").wait(
            cluster=cluster_arn,
            tasks=[task_arn],
            WaiterConfig={"Delay": 1, "MaxAttempts": 10},
        )
        container_name_prefix = self._container_name_prefix(
            cluster_arn, task_id=tasks["tasks"][0]["taskArn"]
        )

        container_name = retry(
            self.assert_app_started,
            retries=12,
            sleep=0.5,
            container_name_prefix=container_name_prefix,
        )
        assert ["apparmor=docker-default"] == DOCKER_CLIENT.inspect_container(
            container_name_or_id=container_name
        )["HostConfig"]["SecurityOpt"]
        aws_client.ecs.get_waiter("tasks_stopped").wait(
            cluster=cluster_arn,
            tasks=[task_arn],
            WaiterConfig={"Delay": 1, "MaxAttempts": 10},
        )

    @markers.aws.only_localstack
    def test_start_task_docker_flags(
        self, create_cluster, register_task_definition, aws_client, monkeypatch
    ):
        host_name = f"test-host-{short_uid()}"
        host_ip = "127.0.0.1"
        env_var = f"TEST{short_uid()}"
        env_var_value = f"test-{short_uid()}"
        port = reserve_available_container_port()
        monkeypatch.setattr(
            ext_config,
            "ECS_DOCKER_FLAGS",
            f"-e {env_var}={env_var_value} -p {port}:{port} --add-host {host_name}:{host_ip}",
        )

        cluster_arn = create_cluster()
        task_family = f"test_family_{short_uid()}"
        container_name = f"test_container_{short_uid()}"
        task_definition_result = register_task_definition(
            family=task_family,
            containerDefinitions=[
                {
                    "name": container_name,
                    "image": "alpine",
                    "cpu": 10,
                    "memory": 128,
                    "command": ["sh", "-c", f"echo ${env_var}; ping -c 1 {host_name}; sleep 5"],
                }
            ],
        )
        task_definition_arn = task_definition_result["taskDefinition"]["taskDefinitionArn"]
        result = aws_client.ecs.run_task(taskDefinition=task_definition_arn, cluster=cluster_arn)
        task_arn = result["tasks"][0]["taskArn"]

        # inspect container and output
        def _check_logs():
            logs = self._get_task_container_logs(cluster_arn=cluster_arn, task_id=task_arn)
            # assert that env var has been passed to the container
            assert env_var_value in logs
            # assert that host mapping has been passed to the container
            assert host_ip in logs

        retry(_check_logs, retries=10, sleep=0.7)

        # assert that port mapping has been added to the container
        container_id = self._get_task_docker_container_id(cluster_arn=cluster_arn, task_id=task_arn)
        details = DOCKER_CLIENT.inspect_container(container_id)
        ports = details["HostConfig"]["PortBindings"]
        assert f"{port}" in ports or f"{port}/tcp" in ports

    @markers.aws.only_localstack
    def test_task_mount_host_volume(self, create_cluster, register_task_definition, aws_client):
        cluster_arn = create_cluster()
        task_family = f"test_family_{short_uid()}"
        container_name = f"test_container_{short_uid()}"
        file_content = f"test content {short_uid()}"

        # create source file on the host
        host_dir = os.path.join(config.dirs.mounted_tmp, short_uid())
        container_dir = "/path/in/container"
        mkdir(host_dir)
        save_file(f"{host_dir}/source", file_content)
        mountable_host_dir = get_host_path_for_path_in_docker(host_dir)

        # create task that copies source file to target mounted dir
        task_definition_result = register_task_definition(
            family=task_family,
            containerDefinitions=[
                {
                    "name": container_name,
                    "image": "alpine",
                    "memory": 128,
                    "command": ["cp", f"{container_dir}/source", f"{container_dir}/target"],
                    "mountPoints": [
                        {"containerPath": container_dir, "sourceVolume": "test-volume"}
                    ],
                }
            ],
            volumes=[{"host": {"sourcePath": mountable_host_dir}, "name": "test-volume"}],
        )
        task_def_arn = task_definition_result["taskDefinition"]["taskDefinitionArn"]
        aws_client.ecs.run_task(taskDefinition=task_def_arn, cluster=cluster_arn)

        def _check_file_copied():
            target_file = os.path.join(host_dir, "target")
            assert os.path.exists(target_file)
            assert load_file(target_file) == file_content

        # assert that the task was started and the file copied properly
        retry(_check_file_copied, retries=10, sleep=1)

    @markers.aws.only_localstack
    def test_correct_number_of_containers(
        self, create_cluster, register_task_definition, aws_client, cleanups
    ):
        cluster_arn = create_cluster()
        task_family = f"family-{short_uid()}"

        task_definition_result = register_task_definition(
            family=task_family,
            containerDefinitions=[
                {
                    "name": "container",
                    "image": "alpine",
                    "memory": 128,
                    "command": ["sh", "-c", "while true; do echo Running; sleep 1; done"],
                }
            ],
        )
        task_def_arn = task_definition_result["taskDefinition"]["taskDefinitionArn"]

        service_name = f"svc-{short_uid()}"

        num_containers = 3
        create_service_result = aws_client.ecs.create_service(
            serviceName=service_name,
            cluster=cluster_arn,
            taskDefinition=task_def_arn,
            desiredCount=num_containers,
        )
        service_arn = create_service_result["service"]["serviceArn"]

        aws_client.ecs.get_waiter("services_stable").wait(
            services=[service_arn], cluster=cluster_arn
        )
        cleanups.append(
            lambda: aws_client.ecs.delete_service(
                service=service_arn, cluster=cluster_arn, force=True
            )
        )

        container_name_prefix = f"ls-ecs-{self._cluster_name_from_arn(cluster_arn)}"
        matching_containers = [
            container
            for container in DOCKER_CLIENT.list_containers()
            if container["name"].startswith(container_name_prefix)
        ]
        assert len(matching_containers) == num_containers

        container_labels = [container["labels"] for container in matching_containers]
        assert all(label["cluster-arn"] == cluster_arn for label in container_labels)
        assert all(label["service"] == service_name for label in container_labels)
        task_ids = {label["task-id"] for label in container_labels}
        assert len(task_ids) == 3

        list_tasks_result = aws_client.ecs.list_tasks(cluster=cluster_arn, serviceName=service_name)
        list_tasks_ids = {task_id.rpartition("/")[2] for task_id in list_tasks_result["taskArns"]}
        assert task_ids == list_tasks_ids


def _pull_image_if_not_exists(image_name: str):
    if image_name not in DOCKER_CLIENT.get_docker_image_names():
        DOCKER_CLIENT.pull_image(image_name)
