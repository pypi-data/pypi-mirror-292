import contextlib
import logging
import os
from urllib.parse import urlparse

import pytest
import requests
from botocore.exceptions import ClientError
from localstack import config, constants
from localstack.aws.connect import connect_to
from localstack.config import HostAndPort
from localstack.constants import DEFAULT_PORT_EDGE
from localstack.pro.core.bootstrap import pods_client
from localstack.pro.core.bootstrap.licensingv2 import (
    ENV_LOCALSTACK_API_KEY,
    ENV_LOCALSTACK_AUTH_TOKEN,
)
from localstack.pro.core.bootstrap.pods.remotes.api import CloudPodsRemotesClient
from localstack.pro.core.bootstrap.pods.remotes.configs import RemoteConfigParams
from localstack.pro.core.bootstrap.pods_client import (
    CloudPodRemoteAttributes,
    CloudPodsClient,
    reset_state,
)
from localstack.pro.core.constants import API_PATH_PODS
from localstack.pro.core.persistence.pods.api.manager import get_pods_manager
from localstack.utils.aws.resources import create_s3_bucket
from localstack.utils.container_utils.container_client import PortMappings
from localstack.utils.docker_utils import DOCKER_CLIENT, reserve_available_container_port
from localstack.utils.functions import call_safe
from localstack.utils.net import get_docker_host_from_container, wait_for_port_open
from localstack.utils.strings import short_uid
from localstack.utils.sync import retry

os.environ.setdefault("AWS_ACCESS_KEY_ID", "test")
os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "test")


LOG = logging.getLogger(__name__)


@pytest.fixture
def oci_registry():
    name = f"registry-{short_uid()}"
    ports = PortMappings()
    backend_port = reserve_available_container_port()
    ports.add(backend_port, 5000)
    DOCKER_CLIENT.run_container("registry", name=name, ports=ports, detach=True, remove=True)
    wait_for_port_open(backend_port, sleep_time=1, retries=20)

    yield {"port": backend_port}

    DOCKER_CLIENT.remove_container(container_name=name)


@pytest.fixture
def remote_config_oci(oci_registry, monkeypatch):
    hostname = get_docker_host_from_container()
    monkeypatch.setenv("ORAS_USERNAME", "admin@localstack.cloud")
    monkeypatch.setenv("ORAS_PASSWORD", "ILoveLocalStack1!")
    return {"url": f"oras://{hostname}:{oci_registry['port']}"}


@pytest.fixture
def remote_config_s3(start_localstack_session):
    # start LocalStack instance to store the pods files in local S3 buckets
    start_localstack_session(
        port=DEFAULT_PORT_EDGE, disable_external_service_ports=True, bind_host="0.0.0.0"
    )
    hostname = get_docker_host_from_container()
    return {"url": f"s3://{hostname}:{DEFAULT_PORT_EDGE}/pods-storage-bucket"}


@pytest.fixture
def create_pods_manager():
    instances = []

    def _create(pod_name=None, remote_config=None):
        pod_name = pod_name or f"p-oras-{short_uid()}"
        result = get_pods_manager(pod_name=pod_name, remote_config=remote_config)
        instances.append(result)
        return result

    yield _create

    for instance in instances:
        with contextlib.suppress(Exception):
            instance.delete(remote=True)


@pytest.mark.parametrize("remote_fixture", ["remote_config_oci", "remote_config_s3"])
def test_cloudpod_remotes(remote_fixture, monkeypatch, localstack_session, request):
    remote_params = request.getfixturevalue(remote_fixture)
    protocol = urlparse(remote_params["url"]).scheme

    port = localstack_session.port

    if protocol == "oras":
        monkeypatch.setattr(
            config,
            "LOCALSTACK_HOST",
            HostAndPort(host=constants.LOCALHOST_HOSTNAME, port=localstack_session.port),
        )

    remotes_client = CloudPodsRemotesClient()
    remote_name = f"{protocol}-remote"
    remotes_client.create_remote(
        name=remote_name, protocols=[protocol], remote_url=remote_params["url"]
    )
    created_remote = remotes_client.get_remote(name=remote_name)
    assert created_remote, "remote has not been correctly created"

    remote_params = RemoteConfigParams(remote_name=remote_name)

    def _patch_get_runtime_pods_endpoint(*args) -> str:
        # make sure we target the right LS instance
        edge_url = config.external_service_url(port=port)
        return f"{edge_url}{API_PATH_PODS}"

    monkeypatch.setattr(pods_client, "get_runtime_pods_endpoint", _patch_get_runtime_pods_endpoint)

    # create some state
    client = CloudPodsClient(interactive=False)
    # create some state
    s3_client = connect_to(endpoint_url=f"http://localhost:{port}", region_name="us-east-1").s3
    bucket_name = f"q-{short_uid()}"
    create_s3_bucket(bucket_name, s3_client=s3_client)

    # create pod, push state to remote
    pod_name = f"ls-remote-{protocol}-{short_uid()}"

    client.save(pod_name=pod_name, remote=remote_params)

    # create a second pod
    pod_to_be_deleted = f"ls-remote-{protocol}-2-{short_uid()}"
    client.save(pod_name=pod_to_be_deleted, remote=remote_params)

    # assert the pod is included in the list
    pods = client.list(remote=remote_params)
    pod_names = [pod["pod_name"] for pod in pods]
    assert pod_name in pod_names
    assert pod_to_be_deleted in pod_names

    # delete the second pod
    if protocol != "oras":
        # todo: implement delete operation for the ORAS protocol
        client.delete(pod_name=pod_to_be_deleted, remote=remote_params)
        pods = client.list(remote=remote_params)
        pod_names = [pod["pod_name"] for pod in pods]
        assert pod_to_be_deleted not in pod_names

    # delete local pod, restart container, assert that state is flushed
    if protocol != "oras":
        client.delete(pod_name=pod_name, remote=remote_params, delete_from_remote=False)
    localstack_session.restart(30)
    with pytest.raises(ClientError):
        s3_client.head_bucket(Bucket=bucket_name)

    # pull and inject pod into container
    client.load(pod_name=pod_name, remote=remote_params)

    # assert state has been injected
    retry(s3_client.head_bucket, Bucket=bucket_name, retries=10, sleep=1)


class TestSmokePodPlatform:
    """
    A set of basic smoke tests for pods against the LocalStack Platform
    Note: they require proper connectivity/auth to platform!
    """

    @pytest.mark.parametrize(
        "token_type", ["api_key", pytest.param("auth_token", marks=pytest.mark.skip("flaky"))]
    )
    def test_smoke_pod_platform(self, token_type, monkeypatch, localstack_session, cleanups):
        port = localstack_session.port
        monkeypatch.setattr(
            config, "LOCALSTACK_HOST", HostAndPort(host=constants.LOCALHOST_HOSTNAME, port=port)
        )
        if token_type == "api_key":
            monkeypatch.setenv(ENV_LOCALSTACK_AUTH_TOKEN, "")
        if token_type == "auth_token":
            monkeypatch.setenv(ENV_LOCALSTACK_API_KEY, "")

        # We check fist if the pod is already on the platform, which it should not be, but we observed some
        #   flakiness in pod deletions from integration tests, so better be safe than sorry!
        #   If 'get_versions' does not raise an error, we delete call the delete operation and keep going with the test.
        pod_name = f"ls-int-tests-versions-{token_type}"
        client = CloudPodsClient(interactive=False)
        if call_safe(client.get_versions, args=(pod_name,)):
            call_safe(client.delete, args=(pod_name,))

        # create some state and push version 1
        sqs_queue = "ls-queue-version-1"
        aws_client = connect_to(endpoint_url=f"http://localhost:{port}", region_name="us-east-1")
        aws_client.sqs.create_queue(QueueName=sqs_queue)

        client = CloudPodsClient(interactive=False)
        cleanups.append(lambda: client.delete(pod_name=pod_name, delete_from_remote=True))

        try:
            client.save(
                pod_name=pod_name,
                attributes=CloudPodRemoteAttributes(
                    services=["sqs"], description="version 1", is_public=False
                ),
            )
            versions = client.get_versions(pod_name=pod_name)
            assert len(versions) == 1, f"found versions: {versions}"

            # create some state and push version 2
            sns_topic = "ls-topic-version-2"
            topic_arn = aws_client.sns.create_topic(Name=sns_topic)["TopicArn"]

            client.save(
                pod_name=pod_name,
                attributes=CloudPodRemoteAttributes(
                    services=["sqs", "sns"], description="version 2", is_public=False
                ),
            )
            versions = client.get_versions(pod_name=pod_name)
            assert len(versions) == 2, f"found versions: {versions}"

            # reset localstack
            reset_state(["sqs", "sns"])

            # load version 1
            client.load(pod_name=pod_name, version=1)

            # assert that the state has been restored
            result = aws_client.sqs.get_queue_url(QueueName=sqs_queue)
            assert result
            with pytest.raises(ClientError) as exc:
                aws_client.sns.get_topic_attributes(TopicArn=topic_arn)
            assert "not exist" in str(exc.value)

            # load version 2
            client.load(pod_name=pod_name, version=2)

            # assert that the state has been restored
            result = aws_client.sns.get_topic_attributes(TopicArn=topic_arn)
            assert result
        finally:
            client.delete(pod_name=pod_name)


class TestMergeStrategies:
    """Suite to check pod merge strategies. Require connectivity to the platform."""

    def test_pod_service_merge_strategy(self, monkeypatch, localstack_session, cleanups):
        """
        This is a simple test that check the service-merge strategy.
        It exercises 3 services, SQS (using stores), SNS (using both stores and moto backends), and DynamoDB (using
        external assets).
        The flow is the following:
        - create resources and save a pod;
        - reset the runtime state;
        - create resources for the same services;
        - load the pod with the service-merge strategy;
        - assert the resources.
        """
        port = localstack_session.port
        monkeypatch.setattr(
            config, "LOCALSTACK_HOST", HostAndPort(host=constants.LOCALHOST_HOSTNAME, port=port)
        )
        monkeypatch.setenv(ENV_LOCALSTACK_API_KEY, "")

        pod_name = "ls-int-pod-merge-service"
        client = CloudPodsClient(interactive=False)
        if call_safe(client.get_versions, args=(pod_name,)):
            call_safe(client.delete, args=(pod_name,))

        # ============= create state for pod =============
        sqs_queue = "ls-queue-version-1"
        aws_client = connect_to(endpoint_url=f"http://localhost:{port}", region_name="us-east-1")
        queue_url_pod = aws_client.sqs.create_queue(QueueName=sqs_queue)["QueueUrl"]
        sns_topic = "ls-topic-version-1"
        topic_arn_pod = aws_client.sns.create_topic(Name=sns_topic)["TopicArn"]
        table_name_pod = f"table-{short_uid()}-1"
        aws_client.dynamodb.create_table(
            TableName=table_name_pod,
            KeySchema=[
                {"AttributeName": "Artist", "KeyType": "HASH"},
                {"AttributeName": "SongTitle", "KeyType": "RANGE"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "Artist", "AttributeType": "S"},
                {"AttributeName": "SongTitle", "AttributeType": "S"},
            ],
            ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
        )
        # ============= end create state =============

        client = CloudPodsClient(interactive=False)
        cleanups.append(lambda: client.delete(pod_name=pod_name, delete_from_remote=True))

        # Create Cloud Pod
        client.save(
            pod_name=pod_name,
            attributes=CloudPodRemoteAttributes(
                services=["sqs", "sns", "dynamodb"], is_public=False
            ),
        )

        # Reset the state
        reset_state(["sqs", "sns", "dynamodb"])

        # ============= create local state =============
        sqs_queue = "ls-queue-version-2"
        aws_client = connect_to(endpoint_url=f"http://localhost:{port}", region_name="us-east-1")
        queue_url_local = aws_client.sqs.create_queue(QueueName=sqs_queue)["QueueUrl"]
        sns_topic = "ls-topic-version-2"
        topic_arn_local = aws_client.sns.create_topic(Name=sns_topic)["TopicArn"]
        table_name_local = f"table-{short_uid()}-2"
        aws_client.dynamodb.create_table(
            TableName=table_name_local,
            KeySchema=[
                {"AttributeName": "Artist", "KeyType": "HASH"},
                {"AttributeName": "SongTitle", "KeyType": "RANGE"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "Artist", "AttributeType": "S"},
                {"AttributeName": "SongTitle", "AttributeType": "S"},
            ],
            ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
        )
        # ============= end create state =============

        # Load pod with merge
        client.load(pod_name=pod_name, merge_strategy="service-merge")

        # Assert states
        queues = aws_client.sqs.list_queues()["QueueUrls"]
        assert queue_url_pod in queues
        assert queue_url_local in queues

        tables = aws_client.dynamodb.list_tables()["TableNames"]
        assert table_name_pod in tables
        assert table_name_local in tables

        topics = [t["TopicArn"] for t in aws_client.sns.list_topics()["Topics"]]
        assert topic_arn_pod in topics
        assert topic_arn_local in topics


@pytest.mark.skip(reason="Flaky, temporarily skipped")
def test_cloudpod_ci_run(start_localstack_session, monkeypatch):
    """
    Perform a test CI run and push the pod state.
    Note: requires proper authentication to platform (setting a valid API key / auth token in the environment)
    """

    # make sure that the API key is configured (required for interaction with platform)
    ls_api_key = os.getenv(ENV_LOCALSTACK_API_KEY)
    assert ls_api_key and ls_api_key != "test"

    # fetch CI runs before test
    ci_project_name = "ls-ext-integration-test"
    platform_ci_endpoint = f"{constants.API_ENDPOINT}/ci/projects"
    url = f"{platform_ci_endpoint}/{ci_project_name}"
    headers = {"ls-api-key": ls_api_key}
    response = requests.get(url, headers=headers)
    content = response.json() if response.ok else {}
    runs_before = sorted(content.get("runs", []), key=lambda run: run.get("run_number") or 0)

    # start up LS container
    session = start_localstack_session(env_vars={"CI_PROJECT": ci_project_name})
    monkeypatch.setattr(
        config, "LOCALSTACK_HOST", HostAndPort(host=constants.LOCALHOST_HOSTNAME, port=session.port)
    )

    # create some state
    aws_client = connect_to(
        endpoint_url=f"http://localhost:{session.port}", region_name="us-east-1"
    )
    bucket_name = f"test-{short_uid()}"
    aws_client.s3.create_bucket(Bucket=bucket_name)
    queue_name = f"test-{short_uid()}"
    aws_client.sqs.create_queue(QueueName=queue_name)

    # stop container -> should sync the state to platform
    session.stop(30)

    # get CI runs after test - assert that an additional run has been tracked
    response = requests.get(url, headers=headers)
    content = response.json() if response.ok else {}
    runs_after = sorted(content.get("runs", []), key=lambda run: run.get("run_number") or 0)
    assert len(runs_after) >= len(runs_before)

    # assert increasing run numbers
    max_num_before = runs_before[-1]["run_number"]
    max_num_after = runs_after[-1]["run_number"]
    assert max_num_after > max_num_before

    # make sure that the pod is deleted from local cache
    pod_name, _ = runs_after[-1]["pod"].split(":")
    pods_manager = get_pods_manager(pod_name=pod_name)
    pods_manager.delete(remote=False)

    # start new session, load pod, assert that pod state has been injected
    session = start_localstack_session()
    session.start(30)
    monkeypatch.setattr(
        config, "LOCALSTACK_HOST", HostAndPort(host=constants.LOCALHOST_HOSTNAME, port=session.port)
    )
    aws_client = connect_to(
        endpoint_url=f"http://localhost:{session.port}", region_name="us-east-1"
    )

    with pytest.raises(ClientError):
        assert aws_client.s3.head_bucket(Bucket=bucket_name)

    client = CloudPodsClient(interactive=False)
    client.load(pod_name)

    # assert that S3 resources were created
    assert aws_client.s3.head_bucket(Bucket=bucket_name)
