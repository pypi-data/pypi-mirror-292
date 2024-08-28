import base64
import contextlib
import inspect
import json
import logging
import os
import textwrap
from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Callable, Dict, Tuple

import pytest
from botocore.exceptions import ClientError
from localstack import config as localstack_config
from localstack.config import is_env_true
from localstack.constants import AWS_REGION_US_EAST_1
from localstack.pro.core import config as ext_config
from localstack.pro.core.bootstrap.pods_client import reset_state
from localstack.pro.core.services.ec2.vmmanager.docker import UBUNTU_JAMMY_AMI, DockerVmManager
from localstack.pro.core.services.rds.db_utils import DEFAULT_MASTER_USERNAME
from localstack.services.plugins import SERVICE_PLUGINS
from localstack.testing.aws.util import ServiceLevelClientFactory, is_aws_cloud
from localstack.testing.pytest.fixtures import sns_create_topic
from localstack.utils import patch, testutil
from localstack.utils.aws import arns, resources
from localstack.utils.aws.arns import get_partition
from localstack.utils.aws.resources import create_dynamodb_table
from localstack.utils.bootstrap import in_ci
from localstack.utils.docker_utils import DOCKER_CLIENT
from localstack.utils.files import new_tmp_dir, rm_rf
from localstack.utils.strings import short_uid, to_str
from localstack.utils.sync import poll_condition, retry
from localstack.utils.testutil import create_lambda_function

from tests.aws.services.apigateway.apigateway_fixtures import create_state_machine
from tests.aws.services.cloudfront.test_cloudfront import get_split_certificate
from tests.aws.services.rds.test_rds import DEFAULT_TEST_MASTER_PASSWORD, wait_until_db_available
from tests.persistence.services.lambda_.test_lambda import TEST_LAMBDA_CODE

LOG = logging.getLogger(__name__)

# decorator that indicates that a test should be skipped in CI builds
skip_in_ci = pytest.mark.skipif(in_ci(), reason="Test currently skipped in CI")


# Decorator that marks a test as using direct (in-memory) access to internal state or functions,
# i.e., the test cannot be executed against real AWS and also not against LocalStack in a
# distributed test setup (with services running in different processes), which may particularly
# also limit its suitability for multi-account setups.
# TODO: currently only used as a marker, without being actually used
whitebox_internal_access = pytest.mark.skipif(
    False,
    reason="test directly accesses internal service implementations",
)


# TODO: merge with echo_http_server_post(..) fixture in community
@pytest.fixture
def echo_http_server_url(echo_http_server):
    """
    Returns an HTTP echo server URL for POST requests that work both locally and for parity tests (against real AWS)
    """
    if is_aws_cloud():
        return "https://mockbin.org/request"

    return f"{echo_http_server.rstrip('/')}/request"


@pytest.fixture(scope="session")
def iot_data_client(aws_client, aws_client_factory):
    # this switch is needed since regular data endpoint serves VeriSign certs which are untrusted by most systems
    if os.environ.get("TEST_TARGET") == "AWS_CLOUD":
        endpoint_url = aws_client.iot.describe_endpoint(endpointType="iot:Data-ATS")[
            "endpointAddress"
        ]
        return aws_client_factory(endpoint_url=f"https://{endpoint_url}").iot_data
    return aws_client.iot_data


@pytest.fixture
def create_stepfunctions(aws_client):
    arns = []

    def factory(**kwargs):
        arn = create_state_machine(aws_client.stepfunctions, **kwargs)
        arns.append(arn)
        return arn

    yield factory

    for arn in arns:
        try:
            aws_client.stepfunctions.delete_state_machine(stateMachineArn=arn)
        except Exception as e:
            LOG.debug(f"Error cleaning up stepfunctions: {arn}, {e}")


@pytest.fixture
def amplify_create_app(aws_client):
    apps = list()

    def factory(**kwargs):
        kwargs["client"] = aws_client.amplify
        if "app_name" not in kwargs:
            kwargs["app_name"] = f"test-app-{short_uid()}"

        result = aws_client.amplify.create_app(name=kwargs["app_name"])["app"]
        apps.append(result["appId"])
        return result

    yield factory

    for app in apps:
        try:
            aws_client.amplify.delete_app(appId=app)
        except Exception as e:
            LOG.debug(f"Error cleaning up amplifyapp: {app}, {e}")


@pytest.fixture
def cloudfront_create_distribution(aws_client):
    distribution_ids = list()

    def factory(**kwargs):
        result = aws_client.cloudfront.create_distribution(**kwargs)
        distribution_ids.append(result["Distribution"]["Id"])

        return result

    yield factory

    # cleanup
    for distribution_id in distribution_ids:
        try:
            aws_client.cloudfront.delete_distribution(Id=distribution_id)
        except Exception as e:
            LOG.debug(
                "error cleaning up cloudfront distribution with ID %s: %s", distribution_id, e
            )


@pytest.fixture
def dms_wait_for_replication_task_deleted(aws_client):
    def _wait_for_replication_task_deleted(task_arn: str):
        def is_task_deleted():
            filters = [{"Name": "replication-task-arn", "Values": [task_arn]}]
            try:
                aws_client.dms.describe_replication_tasks(Filters=filters)
            except ClientError:
                return True
            return False

        return poll_condition(is_task_deleted, timeout=120, interval=5 if is_aws_cloud() else 0.5)

    return _wait_for_replication_task_deleted


@pytest.fixture
def dms_wait_for_replication_task_status(aws_client):
    def _wait_for_replication_task_status(task_arn: str, task_status: str):
        filters = [{"Name": "replication-task-arn", "Values": [task_arn]}]

        def _has_task_status():
            try:
                tasks = aws_client.dms.describe_replication_tasks(Filters=filters)
                return tasks["ReplicationTasks"][0]["Status"] == task_status
            except ClientError:
                return True

        return poll_condition(_has_task_status, timeout=120, interval=5 if is_aws_cloud() else 0.5)

    return _wait_for_replication_task_status


@pytest.fixture
def dms_create_role_dms_vpc_role(aws_client, create_role):
    # create replication instance requires setup of the dms-vpc-role
    role_name = "dms-vpc-role"
    try:
        role = aws_client.iam.get_role(RoleName=role_name)
        if role:
            LOG.debug(f"role {role_name} already exists.")
            yield role["Role"]["Arn"]
            return
    except ClientError:
        pass
    # only create role if it doesn't exist yet
    # in that case we will also delete the role afterwards
    policy_arn = f"arn:{get_partition(aws_client.iam.meta.region_name)}:iam::aws:policy/service-role/AmazonDMSVPCManagementRole"
    assume_role_doc = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"Service": "dms.amazonaws.com"},
                "Action": "sts:AssumeRole",
            }
        ],
    }
    role_arn = create_role(
        RoleName=role_name, AssumeRolePolicyDocument=json.dumps(assume_role_doc)
    )["Role"]["Arn"]
    aws_client.iam.attach_role_policy(RoleName=role_name, PolicyArn=policy_arn)

    yield role_arn

    aws_client.iam.detach_role_policy(RoleName=role_name, PolicyArn=policy_arn)
    aws_client.iam.delete_role(RoleName=role_name)


@pytest.fixture
def dms_wait_for_replication_instance_status(aws_client):
    def _wait_for_replication_instance_status(instance_arn: str, status: str):
        def is_instance_status():
            filters = [{"Name": "replication-instance-arn", "Values": [instance_arn]}]
            try:
                response = aws_client.dms.describe_replication_instances(Filters=filters)
                return response["ReplicationInstances"][0]["ReplicationInstanceStatus"] == status
            except ClientError:
                return False

        return poll_condition(is_instance_status, interval=5 if is_aws_cloud() else 0.5)

    return _wait_for_replication_instance_status


@pytest.fixture
def dms_create_replication_task(
    aws_client, dms_wait_for_replication_task_deleted, dms_wait_for_replication_task_status
):
    replication_task_arns = []

    def factory(**kwargs):
        if "ReplicationTaskIdentifier" not in kwargs:
            kwargs["ReplicationTaskIdentifier"] = f"repl-task-id-{short_uid()}"
        replication_task = aws_client.dms.create_replication_task(**kwargs)
        replication_task_arn = replication_task["ReplicationTask"]["ReplicationTaskArn"]

        replication_task_arns.append(replication_task_arn)

        return replication_task

    yield factory

    # cleanup
    for arn in replication_task_arns:
        try:
            # make sure the replication task is in a valid state before trying to delete it
            try:
                tasks = aws_client.dms.describe_replication_tasks(
                    Filters=[{"Name": "replication-task-arn", "Values": [arn]}]
                )
                current_status = tasks["ReplicationTasks"][0]["Status"]
            except ClientError:
                # the replication task doesn't exist anymore
                continue
            if current_status not in ("ready", "stopped", "failed"):
                aws_client.dms.stop_replication_task(ReplicationTaskArn=arn)
                dms_wait_for_replication_task_status(arn, "stopped")
            aws_client.dms.delete_replication_task(ReplicationTaskArn=arn)
            dms_wait_for_replication_task_deleted(arn)
        except Exception as e:
            LOG.debug("error cleaning up replication task %s: %s", arn, e)


@pytest.fixture
def dms_create_replication_instance(aws_client, dms_create_role_dms_vpc_role):
    replication_instance_arns = []

    def factory(**kwargs):
        if "ReplicationInstanceIdentifier" not in kwargs:
            kwargs["ReplicationInstanceIdentifier"] = f"repl-inst-id-{short_uid()}"
        if "ReplicationInstanceClass" not in kwargs:
            kwargs["ReplicationInstanceClass"] = "dms.t2.micro"
        if "AllocatedStorage" not in kwargs:
            kwargs["AllocatedStorage"] = 5

        def create_instance():
            response = aws_client.dms.create_replication_instance(**kwargs)
            return response

        # retry as the dms-vpc-role may not be available yet
        replication_instance = retry(
            create_instance,
            retries=50 if is_aws_cloud() else 5,
            sleep_before=5 if is_aws_cloud() else 0,
            sleep=5 if is_aws_cloud() else 1,
        )
        replication_instance_arn = replication_instance["ReplicationInstance"][
            "ReplicationInstanceArn"
        ]

        replication_instance_arns.append(replication_instance_arn)

        return replication_instance

    yield factory

    # cleanup
    for arn in replication_instance_arns:
        try:
            # TODO potentially re-try as this will fail if a task using this instance still exists
            aws_client.dms.delete_replication_instance(ReplicationInstanceArn=arn)
        except Exception as e:
            LOG.debug("error cleaning up replication instance %s: %s", arn, e)


@pytest.fixture
def dms_create_replication_config(aws_client):
    replication_config_arns = []

    def factory(**kwargs):
        if "ReplicationConfigIdentifier" not in kwargs:
            kwargs["ReplicationConfigIdentifier"] = f"repl-config-id-{short_uid()}"
        replication_config = aws_client.dms.create_replication_config(**kwargs)
        replication_config_arn = replication_config["ReplicationConfig"]["ReplicationConfigArn"]

        replication_config_arns.append(replication_config_arn)

        return replication_config

    yield factory

    # cleanup
    for arn in replication_config_arns:
        try:
            # TODO make sure the config is not currently in use
            aws_client.dms.delete_replication_config(ReplicationConfigArn=arn)
            # TODO verify if we need to wait for cleanup
        except Exception as e:
            LOG.debug("error cleaning up replication config %s: %s", arn, e)


@pytest.fixture
def dms_create_endpoint(aws_client):
    endpoints = list()

    def factory(**kwargs):
        response = aws_client.dms.create_endpoint(**kwargs)

        endpoints.append(response["Endpoint"])

        return response["Endpoint"]

    yield factory

    # cleanup
    for endpoint in endpoints:
        try:
            aws_client.dms.delete_endpoint(EndpointArn=endpoint["EndpointArn"])
        except Exception as e:
            LOG.debug("error cleaning up DMS endpoint %s: %s", endpoint["EndpointArn"], e)


@pytest.fixture
def ec2_test_ami(aws_client) -> Tuple[str, str]:
    """
    This fixture returns an AMI that can be used for testing purpose.

    :return: Tuple of AMI ID and AMI name
    """

    if ext_config.EC2_VM_MANAGER == "docker":
        # This Docker image is downloaded by Docker VMM at startup
        return UBUNTU_JAMMY_AMI

    if ext_config.EC2_VM_MANAGER == "kubernetes":
        # Simply use Ubuntu Docker image until this VM manager gains proper AMI features
        return "ubuntu:22.04", ""

    elif ext_config.EC2_VM_MANAGER == "mock":
        response = aws_client.ec2.describe_images(
            Filters=[{"Name": "name", "Values": ["amzn2-ami-ecs-hvm-2.0.20220209-x86_64-ebs"]}]
        )
        return response["Images"][0]["ImageId"], response["Images"][0]["Name"]

    raise AssertionError(f"{ext_config.EC2_VM_MANAGER} VMM not supported yet")


@pytest.fixture
def docker_mark_for_cleanup():
    """Fixture that accepts AMI, instance, container and image ID/names for removal during teardown."""
    ids = []

    def _mark_for_cleanup(id_):
        ids.append(id_)

    yield _mark_for_cleanup

    for id_ in ids:
        try:
            # If container ID
            DOCKER_CLIENT.remove_container(id_, force=True)

            # If instance ID
            if id_.startswith("i-"):
                DOCKER_CLIENT.remove_container(
                    DockerVmManager.container_name_from_instance_id(id_, verify=False), force=True
                )

            # If Docker image name/ID
            DOCKER_CLIENT.remove_image(id_, force=True)

            # If AMI ID
            if id_.startswith("ami-"):
                DOCKER_CLIENT.remove_image(
                    DockerVmManager.image_from_ami_id(id_, verify=False), force=True
                )
        except Exception as e:
            LOG.debug("Unable to clean up Docker container %s: %s", id_, e)


@pytest.fixture(scope="class")
def login_docker_client(aws_client):
    def _login_client(**kwargs):
        auth_token = aws_client.ecr.get_authorization_token(**kwargs)
        # if check is necessary since registry login data is not available at LS before at least 1 repository is created
        auth_data = auth_token.get("authorizationData")
        if not auth_data:
            return
        token = auth_data[0]["authorizationToken"]
        token_decoded = to_str(base64.b64decode(to_str(token)))
        token_user, _, token_pwd = token_decoded.partition(":")
        DOCKER_CLIENT.login(
            username=token_user, password=token_pwd, registry=auth_data[0]["proxyEndpoint"]
        )

    return _login_client


@pytest.fixture()
def default_vpc(aws_client):
    vpcs = aws_client.ec2.describe_vpcs()
    for vpc in vpcs["Vpcs"]:
        if vpc.get("IsDefault"):
            return vpc
    raise Exception("Default VPC not found")


@pytest.fixture
def create_vpc(aws_client, region_name):
    vpcs = []
    subnets = []

    def create(
        cidr_block: str = "10.0.0.0/16", name: str | None = None, **kwargs
    ) -> tuple[str, list[str]]:
        """
        Create a new VPC and return (vpc_id, [subnet_id1, subnet_id2, ...])
        """
        vpc_name = name or f"vpc-{short_uid()}"
        # TODO: what if tags are specified in kwargs?
        tag_specifications = [
            {
                "ResourceType": "vpc",
                "Tags": [
                    {
                        "Key": "Name",
                        "Value": vpc_name,
                    }
                ],
            }
        ]
        vpc = aws_client.ec2.create_vpc(
            CidrBlock=cidr_block, TagSpecifications=tag_specifications, **kwargs
        )["Vpc"]
        vpc_id = vpc["VpcId"]
        vpcs.append(vpc_id)

        subnet_private_id = aws_client.ec2.create_subnet(
            VpcId=vpc_id, CidrBlock="10.0.8.0/21", AvailabilityZone=f"{region_name}a"
        )["Subnet"]["SubnetId"]
        subnets.append(subnet_private_id)

        subnet_public_id = aws_client.ec2.create_subnet(
            VpcId=vpc_id, CidrBlock="10.0.0.0/21", AvailabilityZone=f"{region_name}b"
        )["Subnet"]["SubnetId"]
        subnets.append(subnet_public_id)

        return vpc, [subnet_private_id, subnet_public_id]

    yield create

    def delete_subnet(subnet_id: str):
        aws_client.ec2.delete_subnet(SubnetId=subnet_id)

    for subnet in subnets[::-1]:
        retry(delete_subnet, subnet_id=subnet, retries=10)

    for vpc_id in vpcs[::-1]:
        retry(lambda: aws_client.ec2.delete_vpc(VpcId=vpc_id), retries=10)


@pytest.fixture
def create_vpc_endpoint(aws_client):
    endpoints = list()

    def factory(**kwargs):
        services = kwargs["Services"]
        for service_name in services:
            response = aws_client.ec2.create_vpc_endpoint(
                VpcEndpointType="Interface",
                ServiceName=service_name,
                VpcId=kwargs["VpcId"],
                SubnetIds=kwargs["SubnetIds"],
                SecurityGroupIds=kwargs["SecurityGroupIds"],
            )
            vpc_endpoint_id = response["VpcEndpoint"]["VpcEndpointId"]

            def _verify_vpc_endpoint_status():
                status = aws_client.ec2.describe_vpc_endpoints(VpcEndpointIds=[vpc_endpoint_id])[
                    "VpcEndpoints"
                ][0]["State"]
                return status == "available"

            retry(
                _verify_vpc_endpoint_status,
                retries=10 if is_aws_cloud() else 5,
                sleep=5 if is_aws_cloud() else 1,
            )
            endpoints.append(vpc_endpoint_id)

        return endpoints

    yield factory

    # cleanup
    for endpoint in endpoints:
        try:
            aws_client.ec2.delete_vpc_endpoints(VpcEndpointIds=[endpoint])

            # wait until the endpoint is deleted otherwise it will
            # fail because of conflicting DNS names of the same infra
            poll_condition(
                lambda: not aws_client.ec2.describe_vpc_endpoints(VpcEndpointIds=[endpoint])[
                    "VpcEndpoints"
                ],
                timeout=150,
                interval=5 if is_aws_cloud() else 1,
            )

        except Exception as e:
            LOG.debug("error cleaning up VPC endpoint %s: %s", endpoint, e)


@pytest.fixture
def dynamodb_create_table(aws_client):
    tables = list()

    def factory(**kwargs):
        kwargs["client"] = aws_client.dynamodb
        if "table_name" not in kwargs:
            kwargs["table_name"] = "test-table-%s" % short_uid()
        if "partition_key" not in kwargs:
            kwargs["partition_key"] = "id"

        tables.append(kwargs["table_name"])

        return create_dynamodb_table(**kwargs)

    yield factory

    # cleanup
    for table in tables:
        try:
            aws_client.dynamodb.delete_table(TableName=table)
        except Exception as e:
            LOG.debug("error cleaning up table %s: %s", table, e)


@pytest.fixture
def s3_create_bucket(aws_client):
    buckets = list()

    def factory(**kwargs) -> str:
        if "Bucket" not in kwargs:
            kwargs["Bucket"] = f"test-bucket-{short_uid()}"
        region = aws_client.s3.meta.region_name
        if region != AWS_REGION_US_EAST_1:
            kwargs["CreateBucketConfiguration"] = {"LocationConstraint": region}

        aws_client.s3.create_bucket(**kwargs)
        buckets.append(kwargs["Bucket"])
        return kwargs["Bucket"]

    yield factory

    # cleanup
    for bucket in buckets:
        try:
            # TODO: handle situations where paging is necessary
            # also needs to delete all items from the bucket, otherwise this will fail
            list_response = aws_client.s3.list_objects_v2(Bucket=bucket)
            for k in list_response["Contents"]:
                aws_client.s3.delete_object(Bucket=bucket, Key=k["Key"])
            aws_client.s3.delete_bucket(Bucket=bucket)
        except Exception as e:
            LOG.debug("error cleaning up bucket %s: %s", bucket, e)


@pytest.fixture(scope="module")
def s3_create_reusable_bucket(aws_client):
    bucket = None
    counter = 0

    def factory() -> (str, str):
        nonlocal counter, bucket
        counter += 1
        if not bucket:
            bucket = f"test-bucket-{short_uid()}"
            resources.create_s3_bucket(bucket, s3_client=aws_client.s3)

        return (bucket, f"reuse-prefix-{counter}")

    yield factory

    # cleanup
    if bucket:
        try:
            # TODO: handle situations where paging is necessary
            # also needs to delete all items from the bucket, otherwise this will fail
            list_response = aws_client.s3.list_objects_v2(Bucket=bucket)
            aws_client.s3.delete_objects(
                Bucket=bucket,
                Delete={"Objects": [{"Key": o["Key"]} for o in list_response["Contents"]]},
            )
            aws_client.s3.delete_bucket(Bucket=bucket)
        except Exception as e:
            LOG.debug("error cleaning up bucket %s: %s", bucket, e)


@pytest.fixture
def s3_bucket(s3_create_bucket) -> str:
    return s3_create_bucket()


@pytest.fixture
def kinesis_create_stream(aws_client, wait_for_stream_ready):
    stream_names = []

    def _create_stream(**kwargs):
        if "StreamName" not in kwargs:
            kwargs["StreamName"] = f"test-stream-{short_uid()}"
        if "ShardCount" not in kwargs:
            kwargs["ShardCount"] = 2
        aws_client.kinesis.create_stream(**kwargs)
        stream_names.append(kwargs["StreamName"])
        return kwargs["StreamName"]

    yield _create_stream

    for stream_name in stream_names:
        try:
            ready = wait_for_stream_ready(stream_name=stream_name)
            if ready:
                aws_client.kinesis.delete_stream(StreamName=stream_name)
            else:
                LOG.warning(
                    f"Timed out while waiting on stream {stream_name} to become ready for deletion - attempting force delete"
                )
                aws_client.kinesis.delete_stream(
                    StreamName=stream_name, EnforceConsumerDeletion=True
                )
        except Exception as e:
            LOG.debug("error cleaning up kinesis stream %s: %s", stream_name, e)


@dataclass
class UserPoolAndClient:
    user_pool: Dict[str, Any]
    pool_client: Dict[str, Any]


@pytest.fixture
def create_user_pool(aws_client):
    created = []

    def _create(pool_name=None, **kwargs):
        pool_name = pool_name or f"pool-{short_uid()}"
        user_pool = aws_client.cognito_idp.create_user_pool(PoolName=pool_name, **kwargs)[
            "UserPool"
        ]
        created.append(user_pool)
        return user_pool

    yield _create

    for user_pool in created:
        try:
            pool_id = user_pool["Id"]
            details = aws_client.cognito_idp.describe_user_pool(UserPoolId=pool_id)["UserPool"]
            domain = details.get("Domain")
            if domain:
                aws_client.cognito_idp.delete_user_pool_domain(UserPoolId=pool_id, Domain=domain)
            aws_client.cognito_idp.delete_user_pool(UserPoolId=user_pool["Id"])
        except Exception as e:
            LOG.debug("Unable to clean up user pool %s: %s", user_pool.get("Id"), e)


@pytest.fixture
def create_user_pool_client(aws_client, create_user_pool):
    def _create(**kwargs) -> UserPoolAndClient:
        client_kwargs = kwargs.setdefault("client_kwargs", {})
        if not client_kwargs.get("ExplicitAuthFlows"):
            client_kwargs["ExplicitAuthFlows"] = [
                "ALLOW_ADMIN_USER_PASSWORD_AUTH",
                "ALLOW_CUSTOM_AUTH",
                "ALLOW_USER_PASSWORD_AUTH",
                "ALLOW_USER_SRP_AUTH",
                "ALLOW_REFRESH_TOKEN_AUTH",
            ]
        pool_kwargs = kwargs.setdefault("pool_kwargs", {})
        user_pool = create_user_pool(pool_name=kwargs.get("pool_name"), **pool_kwargs)

        # create resource servers, if custom scopes are defined
        scopes = client_kwargs.get("AllowedOAuthScopes") or []
        for scope in scopes:
            if "/" in scope:
                # the scope can be http://example.com/scope1, in which case we want
                # Identifier=http://example.com, Name=example.com, ScopeName=scope1
                resource_server_id, scope_name = scope.rsplit("/", 1)
                aws_client.cognito_idp.create_resource_server(
                    UserPoolId=user_pool["Id"],
                    Identifier=resource_server_id,
                    Name=resource_server_id.rsplit("/", 1)[-1],
                    Scopes=[{"ScopeName": scope_name, "ScopeDescription": "test scope"}],
                )

        client = aws_client.cognito_idp.create_user_pool_client(
            UserPoolId=user_pool["Id"], ClientName="c1", **client_kwargs
        )
        pool_client = client["UserPoolClient"]

        return UserPoolAndClient(user_pool=user_pool, pool_client=pool_client)

    return _create


@pytest.fixture
def sqs_create_queue(aws_client):
    queue_urls = list()

    def factory(**kwargs):
        if "QueueName" not in kwargs:
            kwargs["QueueName"] = "test-queue-%s" % short_uid()

        response = aws_client.sqs.create_queue(QueueName=kwargs["QueueName"])
        url = response["QueueUrl"]
        queue_urls.append(url)

        return url

    yield factory

    # cleanup
    for queue_url in queue_urls:
        try:
            aws_client.sqs.delete_queue(QueueUrl=queue_url)
        except Exception as e:
            LOG.debug("error cleaning up queue %s: %s", queue_url, e)


@pytest.fixture
def create_repository(aws_client):
    repositories = []
    client = None

    def _create_repository(
        repositoryName: str, client_factory: ServiceLevelClientFactory = aws_client
    ):
        nonlocal client
        client = client_factory.ecr
        result = client.create_repository(repositoryName=repositoryName)
        repositories.append({"name": repositoryName})
        return result

    yield _create_repository

    assert client is not None

    for repository in repositories:
        image_ids = None
        try:
            image_ids = client.list_images(repositoryName=repository["name"])["imageIds"]
            if image_ids:
                client.batch_delete_image(repositoryName=repository["name"], imageIds=image_ids)
        except Exception as e:
            LOG.debug("error cleaning up images %s for repository %s: %s", image_ids, repository, e)
        try:
            client.delete_repository(repositoryName=repository["name"])
        except Exception as e:
            LOG.debug("error cleaning up repository %s: %s", repository, e)


@pytest.fixture
def ec2_authorize_sg_ingress(aws_client):
    """
    Authorize a given SG ingress for specified ports.
    """
    exposed_ports = []

    def _expose(sec_group_id, port):
        permissions = [
            {
                "FromPort": port,
                "IpProtocol": "tcp",
                "IpRanges": [{"CidrIp": "0.0.0.0/0"}],
                "ToPort": port,
            }
        ]
        aws_client.ec2.authorize_security_group_ingress(
            GroupId=sec_group_id, IpPermissions=permissions
        )
        exposed_ports.append((sec_group_id, permissions))

    yield _expose

    for security_group_id, permissions in exposed_ports:
        try:
            aws_client.ec2.revoke_security_group_ingress(
                GroupId=security_group_id, IpPermissions=permissions
            )
        except Exception as e:
            LOG.debug(
                "Error cleaning up rule %s for security group %s: %s",
                permissions,
                security_group_id,
                e,
            )


@pytest.fixture
def rds_create_db_cluster(aws_client_factory):
    from tests.aws.services.rds.test_rds import (
        DEFAULT_TEST_MASTER_PASSWORD,
        wait_until_db_available,
    )

    db_cluster_ids = dict()

    def _create_cluster(**kwargs):
        region = kwargs.pop("region_name", "")
        aws_client = aws_client_factory(region_name=region) if region else aws_client_factory()
        if "DBClusterIdentifier" not in kwargs:
            kwargs["DBClusterIdentifier"] = f"rds-{short_uid()}"
        if "MasterUsername" not in kwargs and "GlobalClusterIdentifier" not in kwargs:
            kwargs["MasterUsername"] = DEFAULT_MASTER_USERNAME
        if "MasterUserPassword" not in kwargs and "GlobalClusterIdentifier" not in kwargs:
            kwargs["MasterUserPassword"] = DEFAULT_TEST_MASTER_PASSWORD
        response = aws_client.rds.create_db_cluster(**kwargs)
        cluster_id = response["DBCluster"]["DBClusterIdentifier"]
        db_cluster_ids[cluster_id] = aws_client
        wait_until_db_available(aws_client.rds, cluster_id=cluster_id)
        return response["DBCluster"]

    yield _create_cluster

    def _wait_for_db_cluster_deletion(cluster_id: str):
        def _db_exists():
            try:
                aws_client.rds.describe_db_clusters(DBClusterIdentifier=cluster_id)
                return True
            except aws_client.rds.exceptions.DBClusterNotFoundFault:
                return False

        poll_condition(lambda: not _db_exists(), timeout=120, interval=2.0)

    for cluster_id, aws_client in db_cluster_ids.items():
        try:
            # delete instances first
            cluster_members = aws_client.rds.describe_db_clusters(DBClusterIdentifier=cluster_id)[
                "DBClusters"
            ][0].get("DBClusterMembers", [])
            for m in cluster_members:
                instance_id = m["DBInstanceIdentifier"]
                aws_client.rds.delete_db_instance(
                    DBInstanceIdentifier=instance_id, SkipFinalSnapshot=True
                )

            aws_client.rds.delete_db_cluster(DBClusterIdentifier=cluster_id, SkipFinalSnapshot=True)
            _wait_for_db_cluster_deletion(cluster_id)
        except Exception as e:
            LOG.debug("error cleaning up db cluster %s: %s", cluster_id, e)


@pytest.fixture
def rds_create_db_instance(ec2_authorize_sg_ingress, aws_client):
    db_instance_ids = []

    def _create_instance(expose_public_port=False, **kwargs):
        if "DBInstanceIdentifier" not in kwargs:
            kwargs["DBInstanceIdentifier"] = f"db-{short_uid()}"
        if "DBInstanceClass" not in kwargs:
            kwargs["DBInstanceClass"] = "db.t3.small"
        if "AllocatedStorage" not in kwargs and "DBClusterIdentifier" not in kwargs:
            kwargs["AllocatedStorage"] = (
                20  # setting allocated storage for a cluster member is rejected by boto in newer version
            )
        if not kwargs.get("Engine", "").startswith("aurora"):
            if "MasterUsername" not in kwargs:
                kwargs["MasterUsername"] = DEFAULT_MASTER_USERNAME
            if "MasterUserPassword" not in kwargs:
                kwargs["MasterUserPassword"] = DEFAULT_TEST_MASTER_PASSWORD
        response = aws_client.rds.create_db_instance(**kwargs)
        instance_id = response["DBInstance"]["DBInstanceIdentifier"]
        db_instance_ids.append(instance_id)

        # wait until DB is in status available
        result = wait_until_db_available(aws_client.rds, instance_id=instance_id)

        # authorize security group ingress (required for snapshot tests, to query RDS DBs in AWS)
        if expose_public_port:
            ec2_authorize_sg_ingress(
                result["VpcSecurityGroups"][0]["VpcSecurityGroupId"], result["Endpoint"]["Port"]
            )

        return result

    yield _create_instance

    for db_id in db_instance_ids:
        try:
            aws_client.rds.delete_db_instance(DBInstanceIdentifier=db_id, SkipFinalSnapshot=True)
        except Exception as e:
            LOG.debug("Error cleaning up db instance %s: %s", db_id, e)


@pytest.fixture
def create_iam_role_s3_access_lambda_invoke_for_db(create_iam_role_with_policy):
    role_name = f"test-rds-role-{short_uid()}"
    policy_name = f"test-rds-policy-{short_uid()}"
    role_doc_template = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"Service": "rds.amazonaws.com"},
                "Action": "sts:AssumeRole",
                "Condition": {"StringEquals": {"aws:SourceArn": "..."}},
            }
        ],
    }
    policy_document = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": ["s3:*", "lambda:InvokeFunction"],
                "Resource": ["*"],
            }
        ],
    }

    def _create(source_arn):
        role_document = deepcopy(role_doc_template)
        role_document["Statement"][0]["Condition"]["StringEquals"]["aws:SourceArn"] = source_arn
        return create_iam_role_with_policy(
            RoleName=role_name,
            PolicyName=policy_name,
            RoleDefinition=role_document,
            PolicyDefinition=policy_document,
        )

    return _create


@pytest.fixture
def create_iam_role_kinesis_access(create_iam_role_with_policy):
    role_name = f"test-kinesis-role-{short_uid()}"
    policy_name = f"test-kinesis-policy-{short_uid()}"
    role_doc_template = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"Service": "kinesisanalytics.amazonaws.com"},
                "Action": "sts:AssumeRole",
            }
        ],
    }
    policy_document = {
        "Version": "2012-10-17",
        "Statement": [{"Effect": "Allow", "Action": "kinesis:*", "Resource": "*"}],
    }

    def _create():
        role_document = deepcopy(role_doc_template)
        return create_iam_role_with_policy(
            RoleName=role_name,
            PolicyName=policy_name,
            RoleDefinition=role_document,
            PolicyDefinition=policy_document,
        )

    return _create


@pytest.fixture
def redshift_create_cluster(aws_client):
    cluster_ids = list()

    def _create_cluster(**kwargs):
        if "ClusterIdentifier" not in kwargs:
            kwargs["ClusterIdentifier"] = f"redshift_{short_uid()}"
        response = aws_client.redshift.create_cluster(**kwargs)
        cluster_ids.append(response["Cluster"]["ClusterIdentifier"])
        return response

    yield _create_cluster

    for cluster_id in cluster_ids:
        try:
            aws_client.redshift.delete_cluster(
                ClusterIdentifier=cluster_id, SkipFinalClusterSnapshot=True
            )
        except Exception as e:
            LOG.debug("error cleaning up redshift cluster %s: %s", cluster_id, e)


# Fixtures for SES


@pytest.fixture
def raw_test_email():
    return b"""From: sender@example.com
    To: recipient@example.com
    Subject: LocalStack test raw email with attachment
    MIME-Version: 1.0
    Content-type: Multipart/Mixed; boundary="NextPart"\n\n--NextPart
    Content-Type: text/plain\n\nThis is the message body.\n\n--NextPart
    Content-Type: text/plain;
    Content-Disposition: attachment; filename="attachment.txt"\n\nThis is the text in the attachment.\n\n--NextPart--
    """


@pytest.fixture
def simple_test_email():
    return {
        "Subject": {"Data": "LocalStack test simple email", "Charset": "UTF-8"},
        "Body": {
            "Text": {"Data": "This is the message body.", "Charset": "UTF-8"},
            "Html": {"Data": "<p><i>This</i> is the <b>message body</b>.</p>", "Charset": "UTF-8"},
        },
    }


# Helpers for EKS


@pytest.fixture(scope="class")
def set_kube_provider():
    def _set_kube_provider(test_provider):
        ext_config.EKS_K8S_PROVIDER = test_provider

    old_k8s_provider = ext_config.EKS_K8S_PROVIDER
    yield _set_kube_provider
    ext_config.EKS_K8S_PROVIDER = old_k8s_provider


# Helpers for persistence


@pytest.fixture(scope="module")
def reset_in_memory_state(request):
    """
    Resets the in-memory state of LocalStack before and after running a test.
    Mainly used by Cloud Pods integration tests (retrieving the in-memory state).
    """
    services = request.param if hasattr(request, "param") else []
    LOG.debug("Fixture: reset in memory states at module scope for services %s", services)
    reset_state(services=services)
    yield
    reset_state(services=services)


@pytest.fixture(scope="function")
def reset_service(request):
    # TODO: unify with the one above using dynamic scopes
    services = request.param
    LOG.debug("Fixture: reset in memory states at module scope for services %s", services)
    reset_state(services=services)
    yield
    reset_state(services=services)


@pytest.fixture
def enable_tmp_data_dir(monkeypatch):
    # TODO: delete this after removing the dependency from data dir
    """Create and configure a temporary DATA_DIR for the duration of a test method"""
    tmp_data_dir = new_tmp_dir()
    monkeypatch.setattr(localstack_config, "DATA_DIR", tmp_data_dir)
    monkeypatch.setattr(localstack_config.dirs, "data", tmp_data_dir)

    # Note: we should reset the state after tests by default, to ensure that processes are properly restarted
    state = {"reset_state_after": True}

    def _handle(reset_state_after=True, reset_data_dir=None, exclude_from_reset=None):
        state["reset_state_after"] = reset_state_after
        state["reset_data_dir"] = reset_data_dir
        state["exclude_from_reset"] = exclude_from_reset

    yield _handle

    rm_rf(tmp_data_dir)
    monkeypatch.undo()


# TODO: remove
@pytest.fixture
def lambda_create_function(aws_client):
    function_names = []

    def _create_function(**kwargs):
        if not kwargs.get("FunctionName"):
            kwargs["FunctionName"] = f"test-function-{short_uid()}"
        if not kwargs.get("Role"):
            kwargs["Role"] = f"test-role-{short_uid()}"
        function_names.append(kwargs["FunctionName"])
        return aws_client.lambda_.create_function(**kwargs)

    yield _create_function

    for function_name in function_names:
        try:
            aws_client.lambda_.delete_function(FunctionName=function_name)
        except Exception:
            LOG.debug("Error while deleting lambda function %s", function_name)


# TODO: move to community
@pytest.fixture
def iam_role(aws_client):
    role_name = f"r-{short_uid()}"
    result = aws_client.iam.create_role(RoleName=role_name, AssumeRolePolicyDocument="{}")
    role_arn = result["Role"]["Arn"]

    yield role_arn

    aws_client.iam.delete_role(RoleName=role_name)


# TODO: move to community
@pytest.fixture
def create_role_with_policy_for_principal(account_id, create_role_with_policy):
    def _create_role_and_policy(principal=None, **kwargs):
        principal = principal or {"AWS": account_id}
        assume_policy_doc = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "sts:AssumeRole",
                    "Principal": principal,
                    "Effect": "Allow",
                }
            ],
        }
        assume_policy_doc = json.dumps(assume_policy_doc)
        role_name, role_arn = create_role_with_policy(assume_policy_doc=assume_policy_doc, **kwargs)
        return role_name, role_arn

    return _create_role_and_policy


def should_skip_bigdata_tests() -> bool:
    """Whether to skip bigdata tests for this test suite"""
    return in_ci() and not is_env_true("RUN_BIGDATA_TESTS")


# TODO: should probably make this a hook
@pytest.fixture(scope="session", autouse=True)
def skip_starting_bigdata_container():
    if not should_skip_bigdata_tests():
        yield
        return

    from localstack.pro.core.services.emr.provider import EmrProvider
    from localstack.pro.core.services.glue import hive_utils

    def noop(*args, **kwargs):
        # skip starting up bigdata container in CI
        pass

    patches = []

    def patch_function_as_noop(func: Callable):
        _patch = patch.Patch.function(func, noop)
        _patch.apply()
        patches.append(_patch)

    # using manual patches here, as monkeypatch is made for function-scoped fixtures
    patch_function_as_noop(EmrProvider.startup_cluster)
    patch_function_as_noop(hive_utils.create_hive_database)
    patch_function_as_noop(hive_utils.create_hive_table)
    patch_function_as_noop(hive_utils.delete_hive_database)
    patch_function_as_noop(hive_utils.delete_hive_table)
    patch_function_as_noop(hive_utils.update_hive_table)

    yield

    # undo patches
    for _patch in patches:
        _patch.undo()


@pytest.fixture()
def get_test_pod_dir():
    pod_dir = new_tmp_dir()
    yield pod_dir
    rm_rf(pod_dir)
    # todo: is this removal even needed
    # rm_rf(config_context.cloud_pods_root_dir)


@pytest.fixture()
def set_pods_env(monkeypatch, get_test_pod_dir):
    monkeypatch.setenv("POD_DIR", get_test_pod_dir)


class MyFactory:
    def __init__(self, aws_client_factory):
        self.aws_client_factory = aws_client_factory

    def create_state(self, service: str):
        match service:
            case "sqs":
                return self._call(sqs_create_queue, self.aws_client_factory())
            case "cognito-idp":
                return self._call(create_user_pool, self.aws_client_factory())
            case "s3":
                return self._call(s3_create_bucket, self.aws_client_factory())
            case "qldb":
                return self._call(
                    self.aws_client_factory.get_client(service_name=service).create_ledger,
                    Name=f"ledger-{short_uid()}",
                    PermissionsMode="ALLOW_ALL",
                )
            case "sns":
                return self._call(sns_create_topic, self.aws_client_factory())
            case "dynamodb":
                return self._call(dynamodb_create_table, self.aws_client_factory())
            case "lambda":
                return self._call(
                    create_lambda_function,
                    f"lambda-{short_uid()}",
                    handler_file=TEST_LAMBDA_CODE,
                    client=self.aws_client_factory.get_client(service_name=service),
                )
            case "kinesis":
                return self._call(
                    kinesis_create_stream,
                    self.aws_client_factory(),
                    None,
                )
            case _:
                raise NotImplementedError(f"There is no implementation for {service}")

    def _call(self, fn, *args, **kwargs) -> dict:
        if hasattr(fn, "__wrapped__"):
            fn = fn.__wrapped__

        response = fn(*args, **kwargs)
        if inspect.isgenerator(response):
            return next(response)()
        return response


@pytest.fixture(name="state_factory")
def state_creator_factory(aws_client_factory):
    yield MyFactory(aws_client_factory)


@pytest.fixture()
def create_lambda_with_invocation_forwarding(
    create_lambda_function, sqs_create_queue, account_id, aws_client
):
    lambda_forward_to_sqs = textwrap.dedent(
        """
    import boto3, json, os
    def handler(event, *args):
        # send message to SQS for later inspection and assertions
        sqs_client = boto3.client("sqs")
        message = {"event": event}
        sqs_client.send_message(QueueUrl="<sqs_url>", MessageBody=json.dumps(message), MessageGroupId="1")
        result = {
            "statusCode": 200,
            "body": json.dumps(message)
        }
        return result
    """
    )

    def _create(lambda_source: str = None):
        function_name = f"test_inv_forward-{short_uid()}"

        # create SQS queue for results
        queue_name = f"{function_name}.fifo"
        queue_attrs = {"FifoQueue": "true", "ContentBasedDeduplication": "true"}
        queue_url = sqs_create_queue(QueueName=queue_name, Attributes=queue_attrs)
        aws_client.sqs.add_permission(
            QueueUrl=queue_url,
            Label=f"lambda-sqs-{short_uid()}",
            AWSAccountIds=[account_id],
            Actions=["SendMessage"],
        )

        # create forwarding Lambda
        lambda_source = lambda_source or lambda_forward_to_sqs
        lambda_code = lambda_source.replace("<sqs_url>", queue_url)
        zip_file = testutil.create_lambda_archive(lambda_code, get_content=True)
        response = create_lambda_function(
            func_name=function_name, zip_file=zip_file, client=aws_client.lambda_
        )
        function_arn = response["CreateFunctionResponse"]["FunctionArn"]

        # allow cognito to call lambda functions, e.g., our trigger lambda
        for principal in ("cognito-idp.amazonaws.com", "apigateway.amazonaws.com"):
            aws_client.lambda_.add_permission(
                FunctionName=function_name,
                StatementId=f"invoke-lambda-{short_uid()}",
                Action="lambda:InvokeFunction",
                Principal=principal,
            )

        return function_arn

    yield _create


@pytest.fixture()
def get_lambda_invocation_events(aws_client):
    def _get_trigger_events(trigger_lambda_arn: str, count: int = 1):
        # determine URL of results queue
        resource_name = arns.lambda_function_name(trigger_lambda_arn)
        queue_name = f"{resource_name}.fifo"
        queue_url = aws_client.sqs.get_queue_url(QueueName=queue_name)["QueueUrl"]

        def _receive():
            if len(result) == count:
                return
            res = aws_client.sqs.receive_message(QueueUrl=queue_url, WaitTimeSeconds=1)
            messages = res.get("Messages") or []
            # delete received messages
            if messages:
                entries = [
                    {"Id": f"msg{idx}", "ReceiptHandle": msg["ReceiptHandle"]}
                    for idx, msg in enumerate(messages)
                ]
                aws_client.sqs.delete_message_batch(QueueUrl=queue_url, Entries=entries)
            # extract parsed message bodies
            messages = [json.loads(msg["Body"]) for msg in messages]
            result.extend(messages)
            assert len(result) == count

        result = []
        retry(_receive, sleep=1, retries=20)
        return result

    yield _get_trigger_events


@contextlib.contextmanager
def set_global_service_provider(service, provider):
    """
    Context manager that allows to temporarily switch to a different service provider
    implementation, for the duration of the context manager scope.

    Example usage, setting the EKS provider to "mock":

        with set_global_service_provider("eks", "mock"):
            eks_client.create_cluster(name="c1", roleArn="r1", resourcesVpcConfig={})
            ...

    Note that tests using this context manager will *not* be parallelized, as we're
    mutating the global provider configuration.
    """

    provider_before = SERVICE_PLUGINS.provider_config.get_provider(service)
    SERVICE_PLUGINS.provider_config.set_provider(service, provider)
    plugin_before = SERVICE_PLUGINS._services.pop(service, None)

    yield

    SERVICE_PLUGINS.provider_config.set_provider(service, provider_before)
    if plugin_before:
        SERVICE_PLUGINS._services[service] = plugin_before
    else:
        SERVICE_PLUGINS._services.pop(service, None)


@pytest.fixture
def route53_create_hosted_zone(aws_client):
    hosted_zones = list()

    def factory(**kwargs) -> str:
        if "Name" not in kwargs:
            kwargs["Name"] = f"my-zone-{short_uid()}"
        if "CallerReference" not in kwargs:
            kwargs["CallerReference"] = f"r-{short_uid()}"
        response = aws_client.route53.create_hosted_zone(**kwargs)
        hosted_zone_id = response["HostedZone"]["Id"]
        hosted_zones.append(hosted_zone_id)
        return hosted_zone_id

    yield factory

    # cleanup
    for hosted_zone in hosted_zones:
        try:
            records = aws_client.route53.list_resource_record_sets(HostedZoneId=hosted_zone)[
                "ResourceRecordSets"
            ]

            for r in records:
                if r["Type"] not in ["NS", "SOA"]:
                    delete = {"Changes": [{"Action": "DELETE", "ResourceRecordSet": r}]}
                    aws_client.route53.change_resource_record_sets(
                        HostedZoneId=hosted_zone, ChangeBatch=delete
                    )
            aws_client.route53.delete_hosted_zone(Id=hosted_zone)
        except Exception as e:
            LOG.debug("error cleaning up hosted zone %s: %s", hosted_zone, e)


@pytest.fixture
def msk_create_cluster_v2(aws_client):
    cluster_arns = []

    def _create_cluster(**kwargs):
        result = aws_client.kafka.create_cluster_v2(**kwargs)
        cluster_arns.append(result["ClusterArn"])
        return result

    yield _create_cluster

    for cluster_arn in cluster_arns:
        try:
            aws_client.kafka.delete_cluster(ClusterArn=cluster_arn)
        except Exception as e:
            LOG.debug("Error cleaning up kafka cluster: %s", e)


@pytest.fixture
def mwaa_env_factory(aws_client):
    """
    Fixture that returns a factory that creates an MWAA environment, waits for
    it to be ready and returns its webserver URL.
    """
    environments = []

    def _factory(
        env_name: str, dag_s3_path: str, source_bucket_arn: str, airflow_version: str
    ) -> str:
        aws_client.mwaa.create_environment(
            Name=env_name,
            DagS3Path=dag_s3_path,
            ExecutionRoleArn="r1",
            NetworkConfiguration={},
            SourceBucketArn=source_bucket_arn,
            AirflowVersion=airflow_version,
        )
        environments.append(env_name)

        webserver_url = ""

        # wait until Airflow becomes available (this can take quite some time)
        def _check_available():
            result = aws_client.mwaa.get_environment(Name=env_name)
            assert result["Environment"]["Status"] == "AVAILABLE"
            assert result["Environment"]["Arn"].endswith(f":environment/{env_name}")
            nonlocal webserver_url
            webserver_url = result["Environment"]["WebserverUrl"]

        retry(_check_available, retries=90, sleep=2)

        return webserver_url

    yield _factory

    for env_name in environments:
        with contextlib.suppress(Exception):
            aws_client.mwaa.delete_environment(Name=env_name)


@pytest.fixture
def mq_create_broker(aws_client):
    brokers = []

    def factory(**kwargs):
        if "BrokerName" not in kwargs:
            kwargs["BrokerName"] = f"test-broker-{short_uid()}"
        if "DeploymentMode" not in kwargs:
            kwargs["DeploymentMode"] = "SINGLE_INSTANCE"
        if "EngineType" not in kwargs:
            kwargs["EngineType"] = "ACTIVEMQ"
        if "EngineVersion" not in kwargs:
            kwargs["EngineVersion"] = "5.16.6"
        if "HostInstanceType" not in kwargs:
            kwargs["HostInstanceType"] = "mq.t2.micro"
        if "AutoMinorVersionUpgrade" not in kwargs:
            kwargs["AutoMinorVersionUpgrade"] = True
        if "PubliclyAccessible" not in kwargs:
            kwargs["PubliclyAccessible"] = True
        if "Users" not in kwargs:
            kwargs["Users"] = [
                {
                    "ConsoleAccess": True,
                    "Groups": ["testgroup"],
                    "Password": "adminisagreatpassword",
                    "Username": "admin",
                }
            ]

        response = aws_client.mq.create_broker(**kwargs)
        brokers.append(response["BrokerId"])
        return response

    yield factory

    # cleanup
    for broker_id in brokers:
        try:
            aws_client.mq.delete_broker(BrokerId=broker_id)
        except Exception as e:
            LOG.debug("error deleting broker %s: %s", broker_id, e)


@pytest.fixture
def apigw_create_domain(aws_client):
    domains = list()
    certificates = list()

    def factory(**kwargs) -> dict:
        certificate_arn = kwargs.get("DomainNameConfiguration", {}).get("CertificateArn")
        if "DomainName" not in kwargs:
            kwargs["DomainName"] = f"{short_uid()}.localhost.localstack.cloud"
        if "DomainNameConfigurations" not in kwargs:
            private_key, cert, cert_chain = get_split_certificate()
            import_certificate_result = aws_client.acm.import_certificate(
                Certificate=cert, PrivateKey=private_key, CertificateChain=cert_chain
            )
            certificate_arn = import_certificate_result["CertificateArn"]
            kwargs["DomainNameConfiguration"] = [
                {
                    "CertificateArn": certificate_arn,
                    "EndpointType": "REGIONAL",
                }
            ]

        response = aws_client.apigatewayv2.create_domain_name(
            DomainName=kwargs["DomainName"],
            DomainNameConfigurations=kwargs["DomainNameConfiguration"],
        )
        domain_name = response["DomainName"]
        domains.append(domain_name)
        certificates.append(certificate_arn)
        return response

    yield factory

    # cleanup
    for domain_name, cert_arn in zip(domains, certificates):
        try:
            aws_client.apigatewayv2.delete_domain_name(DomainName=domain_name)
            retry(aws_client.acm.delete_certificate, retries=10, sleep=3, CertificateArn=cert_arn)
        except Exception as e:
            LOG.debug("error cleaning up domain name %s: %s", domain_name, e)
