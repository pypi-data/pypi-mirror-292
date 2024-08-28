import base64
import contextlib
import inspect
import json
import logging
import os
import textwrap
from dataclasses import dataclass
from typing import Any, Callable, Dict

import pytest
from localstack import config as localstack_config
from localstack.config import is_env_true
from localstack.constants import AWS_REGION_US_EAST_1
from localstack.pro.core import config as ext_config
from localstack.pro.core.bootstrap.pods_client import reset_state
from localstack.pro.core.services.ec2.vmmanager.docker import DockerVmManager
from localstack.pro.core.services.rds.db_utils import DEFAULT_MASTER_USERNAME
from localstack.services.plugins import SERVICE_PLUGINS
from localstack.testing.aws.util import is_aws_cloud
from localstack.testing.pytest.fixtures import sns_create_topic
from localstack.utils import patch, testutil
from localstack.utils.aws import arns, resources
from localstack.utils.aws.resources import create_dynamodb_table
from localstack.utils.bootstrap import in_ci
from localstack.utils.docker_utils import DOCKER_CLIENT
from localstack.utils.files import new_tmp_dir, rm_rf
from localstack.utils.strings import short_uid, to_str
from localstack.utils.sync import retry
from localstack.utils.testutil import create_lambda_function

from tests.aws.services.apigateway.apigateway_fixtures import create_state_machine
from tests.persistence.services.test_lambda import TEST_LAMBDA_CODE

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
                resource_server_id, _, scope_name = scope.partition("/")
                aws_client.cognito_idp.create_resource_server(
                    UserPoolId=user_pool["Id"],
                    Identifier=resource_server_id,
                    Name=resource_server_id,
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

    def _create_repository(repositoryName: str):
        result = aws_client.ecr.create_repository(repositoryName=repositoryName)
        repositories.append({"name": repositoryName})
        return result

    yield _create_repository

    for repository in repositories:
        image_ids = None
        try:
            image_ids = aws_client.ecr.list_images(repositoryName=repository["name"])["imageIds"]
            aws_client.ecr.batch_delete_image(repositoryName=repository["name"], imageIds=image_ids)
        except Exception as e:
            LOG.debug("error cleaning up images %s for repository %s: %s", image_ids, repository, e)
        try:
            aws_client.ecr.delete_repository(repositoryName=repository["name"])
        except Exception as e:
            LOG.debug("error cleaning up repository %s: %s", repository, e)


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
        if "MasterUsername" not in kwargs:
            kwargs["MasterUsername"] = DEFAULT_MASTER_USERNAME
        if "MasterUserPassword" not in kwargs:
            kwargs["MasterUserPassword"] = DEFAULT_TEST_MASTER_PASSWORD
        response = aws_client.rds.create_db_cluster(**kwargs)
        cluster_id = response["DBCluster"]["DBClusterIdentifier"]
        db_cluster_ids[cluster_id] = aws_client
        wait_until_db_available(aws_client.rds, cluster_id=cluster_id)
        return response["DBCluster"]

    yield _create_cluster

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
        except Exception as e:
            LOG.debug("error cleaning up db cluster %s: %s", cluster_id, e)


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
    import boto3, json
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
