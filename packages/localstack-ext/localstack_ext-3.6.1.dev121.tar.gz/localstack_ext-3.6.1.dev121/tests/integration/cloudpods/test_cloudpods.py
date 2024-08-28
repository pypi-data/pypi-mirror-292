import io
import os
import traceback
import zipfile

import localstack.pro.core.persistence.pods.api.manager
import pytest
import requests
from localstack import config, constants
from localstack.pro.core.bootstrap.pods.constants import STATE_ZIP
from localstack.pro.core.bootstrap.pods_client import (
    CloudPodRemoteAttributes,
    CloudPodsClient,
    reset_state,
)
from localstack.pro.core.constants import MOTO_BACKEND_STATE_FILE, STORE_STATE_FILE
from localstack.pro.core.persistence.pods.api.manager import get_pods_manager
from localstack.pro.core.persistence.pods.service_state.service_state_types import (
    AccountRegion,
    ServiceKey,
)
from localstack.pro.core.persistence.state_metamodel import active_service_regions
from localstack.pro.core.persistence.utils.adapters import ServiceStateMarshaller
from localstack.pro.core.persistence.utils.common import get_pods_root_dir
from localstack.pro.core.services.cognito_idp.models import CognitoIdpStore
from localstack.state import pickle
from localstack.state.pickle import loads
from localstack.utils.aws.aws_stack import get_valid_regions_for_service
from localstack.utils.strings import short_uid
from requests import Response


@pytest.fixture
def assert_no_pickling(monkeypatch):
    """
    Fixture that disables the unmarshall_object() function and asserts that it is not being called from
    pods CLI commands. This is crucial, as the pods CLI in general has no access to the protected modules.
    """

    error = "Object unmarshalling should not be called directly from the pods CLI"

    def _unmarshall_object(*args, **kwargs):
        stack_str = "".join(traceback.format_stack())
        is_server_side_call = "localstack/http/router.py" in stack_str
        if not is_server_side_call:
            raise Exception(error)
        return _unmarshall_object_orig(*args, **kwargs)

    _unmarshall_object_orig = pickle.loads
    monkeypatch.setattr(pickle, "loads", _unmarshall_object)
    with pytest.raises(Exception) as exc:
        pickle.loads(pickle.dumps(CognitoIdpStore()))
    exc.match(error)


def get_container_state() -> Response:
    return requests.get(f"{config.internal_service_url()}/_localstack/pods/state")


class TestPodsServer:
    @pytest.mark.parametrize("windows_path_sep", [True, False])
    def test_retrieve_state_from_memory(
        self, state_factory, monkeypatch, windows_path_sep, account_id
    ):
        tested_services = ["cognito-idp", "sns"]
        if windows_path_sep:
            monkeypatch.setattr(os, "sep", "\\")
        try:
            for _service in tested_services:
                state_factory.create_state(_service)

            # retrieve the state from memory
            result = get_container_state()

            assert result.content

            # assert the headers contain the list of extracted services
            extracted_services: list[str] = result.headers["x-localstack-pod-services"].split(",")
            assert set(tested_services).issubset(set(extracted_services))

            # convert the zip and check the retrieved states
            state_retrieved = ServiceStateMarshaller.unmarshall(
                zip_content=result.content, raw_bytes=True, unmarshall_function=loads
            )

            # check we have the same services
            retrieved_services = [s.service for s in state_retrieved.state.keys()]
            assert set(tested_services).issubset(set(retrieved_services))

            # assert that SNS has two backends, a store.state and a backend.state
            sns_backends = state_retrieved.state[
                ServiceKey(account_id, constants.AWS_REGION_US_EAST_1, "sns")
            ]
            assert sns_backends.backends[STORE_STATE_FILE]
            assert sns_backends.backends[MOTO_BACKEND_STATE_FILE]

        finally:
            reset_state(tested_services)

    def test_reset_service_state(self, state_factory, aws_client):
        tested_services = ["cognito-idp", "sns"]
        try:
            for _service in tested_services:
                state_factory.create_state(_service)

            topics = aws_client.sns.list_topics()["Topics"]
            assert len(topics) >= 0
            reset_state(services=["sns", "cognito-idp"])

            topics = aws_client.sns.list_topics()["Topics"]
            assert len(topics) == 0
            user_pools = aws_client.cognito_idp.list_user_pools(MaxResults=10)["UserPools"]
            assert len(user_pools) == 0
        finally:
            reset_state(tested_services)

    def test_subsequent_retrieve_state(self, state_factory, aws_client, account_id):
        try:
            # create some state
            state_factory.create_state("cognito-idp")

            # check that we can extract such a state in memory

            oracle_key = ServiceKey(account_id, constants.AWS_REGION_US_EAST_1, "cognito-idp")

            response = get_container_state()
            state_retrieved = ServiceStateMarshaller.unmarshall(
                zip_content=response.content, unmarshall_function=loads
            )
            assert oracle_key in state_retrieved.state

            # add new state
            state_factory.create_state("sns")

            # check that we have the complete state in memory
            result = get_container_state()
            oracle_key = ServiceKey(account_id, constants.AWS_REGION_US_EAST_1, "sns")

            state_retrieved = ServiceStateMarshaller.unmarshall(
                zip_content=result.content, unmarshall_function=loads
            )
            assert oracle_key in state_retrieved.state
        finally:
            reset_state(["cognito-idp", "sns"])

    def test_merge_region_backends(self, state_factory, aws_client):
        try:
            state_factory.create_state("cognito-idp")

            from localstack.pro.core.services.cognito_idp.models import cognito_idp_stores

            backend = cognito_idp_stores["000000000000"]["us-east-1"]

            assert isinstance(backend, CognitoIdpStore)
            cognito_region = CognitoIdpStore()

            from localstack.pro.core.persistence.pods.merge.state_merge import (
                deep_merge_object_state,
            )

            deep_merge_object_state(backend, cognito_region)
            assert isinstance(backend, CognitoIdpStore)
            assert backend.user_pools
        finally:
            reset_state(["cognito-idp"])

    def test_merge_deletion_region_backends(self, state_factory, aws_client):
        try:
            state_factory.create_state("cognito-idp")

            from localstack.pro.core.services.cognito_idp.models import cognito_idp_stores

            backend = cognito_idp_stores["000000000000"]["us-east-1"]

            assert isinstance(backend, CognitoIdpStore)
            cognito_region = CognitoIdpStore()

            from localstack.pro.core.persistence.pods.merge.state_merge import (
                deep_merge_object_state,
            )

            deep_merge_object_state(backend, cognito_region, backend)
            assert isinstance(backend, CognitoIdpStore)
            assert not backend.user_pools
        finally:
            reset_state(["cognito-idp"])

    def test_reset_states_for_services_with_assets(self, state_factory, account_id):
        services = ["lambda", "dynamodb", "kinesis"]
        try:
            for service in services:
                state_factory.create_state(service)

            reset_state(services=services)

            result = get_container_state()
            assert result
            state_retrieved = ServiceStateMarshaller.unmarshall(
                zip_content=result.content, unmarshall_function=loads
            )

            for service in services:
                assert not state_retrieved.state.get(
                    ServiceKey.for_region_and_service(
                        AccountRegion(account_id, constants.AWS_REGION_US_EAST_1), service
                    )
                )
            assert not state_retrieved.assets.get("lambda")
            # When restarting dynamodb, we list the tables to make sure the server is active again. This operation
            # triggers the creation of a single .db file.
            assert len(state_retrieved.assets.get("dynamodb")) == 1
        finally:
            reset_state(services)


@pytest.mark.usefixtures("assert_no_pickling")
class TestPodsClient:
    client = CloudPodsClient()

    @staticmethod
    def _get_pod_root_dir(pods_name: str) -> str:
        """
        Note: since we ask for a new manager, the pod rood dir does not take into account the pods name; this is due
        to the fact the `set_context` is called during an `init` or `push` operation (this can be further
        optimized).
        :param pods_name: name of the pods
        :return: the local path where the pods related files are stored
        """
        pods_manager = localstack.pro.core.persistence.pods.api.manager.get_pods_manager(
            pod_name=pods_name
        )
        return pods_manager.pods_fs_ops.config_context.pod_root_dir

    def test_pod_client_can_init_cloud_pods(self):
        pod_name = f"pod-{short_uid()}"
        self.client.save(pod_name=pod_name, local=True)
        pod_root_dir = self._get_pod_root_dir(pods_name=pod_name)
        assert os.path.isdir(pod_root_dir)
        # clean resources
        self.client.delete(pod_name, delete_from_remote=False)

    @pytest.mark.parametrize("reset_in_memory_state", [["sqs"]], indirect=True)
    def test_pod_inspect_state(self, state_factory, reset_in_memory_state, account_id):
        pod_name = f"pod-{short_uid()}"

        state_factory.create_state("sqs")
        self.client.save(pod_name=pod_name, attributes={"services": ["sqs"]}, local=True)
        metamodel = self.client.get_state_data()
        assert metamodel[account_id]["SQS"][constants.AWS_REGION_US_EAST_1]

    @pytest.mark.parametrize("reset_in_memory_state", [["sqs"]], indirect=True)
    def test_dir_structure(self, state_factory, reset_in_memory_state, account_id):
        pod_name = f"pod-{short_uid()}"

        state_factory.create_state("sqs")
        self.client.save(pod_name=pod_name, attributes={"services": ["sqs"]}, local=True)

        result = get_container_state()
        assert result.content

        z = zipfile.ZipFile(io.BytesIO(result.content))
        assert f"api_states/{account_id}/sqs/us-east-1/{STORE_STATE_FILE}" in z.namelist()

        self.client.delete(pod_name, delete_from_remote=False)

    def test_assets_folder_layout(self, state_factory):
        pod_name = f"pod-{short_uid()}"
        services = ["sqs", "dynamodb"]
        try:
            for service in services:
                state_factory.create_state(service)
            self.client.save(pod_name=pod_name, local=True)
            pods_manager = localstack.pro.core.persistence.pods.api.manager.get_pods_manager(
                pod_name=pod_name
            )
            pods_directory: str = pods_manager.pods_fs_ops.config_context.pod_root_dir
            assert os.path.exists(pods_directory)
            assert os.path.exists(os.path.join(pods_directory, "pod_state-1.zip"))
            with zipfile.ZipFile(os.path.join(pods_directory, "pod_state-1.zip")) as zip_file:
                assert [name for name in zip_file.namelist() if name.startswith("assets/dynamodb")]
        finally:
            reset_state(services)

    def test_selective_push(self, state_factory):
        pod_name = f"pod-{short_uid()}"
        state_factory.create_state("cognito-idp")
        state_factory.create_state("sqs")
        self.client.save(pod_name, attributes={"services": ["cognito-idp"]}, local=True)

        version_path = os.path.join(get_pods_root_dir(), pod_name, f"{STATE_ZIP}-1.zip")
        service = ServiceStateMarshaller.unmarshall(zipfile.ZipFile(version_path), raw_bytes=True)
        assert service.get_services() == ["cognito-idp"]


class TestInjectState:
    """Cloud pods tests which inject or reset the local state (resulting in re-starts of external processes)"""

    client = CloudPodsClient()

    def test_can_inject_version_state_after_push(self, state_factory, aws_client):
        pod_name = f"pod-{short_uid()}"
        # use a well known service we are sure where persistence works,
        # test pods support for arbitrary services in its own integration test
        topic_arn = state_factory.create_state(service="sns")["TopicArn"]

        self.client.save(
            pod_name=pod_name, attributes=CloudPodRemoteAttributes(services=["sns"]), local=True
        )
        backend = get_pods_manager(pod_name=pod_name)
        backend.inject(version=1)

        topics = [_topic.get("TopicArn") for _topic in aws_client.sns.list_topics()["Topics"]]
        assert topic_arn in topics
        self.client.delete(pod_name=pod_name, delete_from_remote=False)

    def test_working_with_multiple_pods(self, state_factory, aws_client):
        pod_name_1 = "pod-1"
        pod_name_2 = "pod-2"

        # Make sure to start from a clean state
        reset_state(["sns", "sqs"])

        # create mutual state for both pods
        state_factory.create_state("sns")

        self.client.save(pod_name=pod_name_1, local=True)

        state_factory.create_state("sqs")

        self.client.save(pod_name=pod_name_2, local=True)
        reset_state()

        manager = get_pods_manager(pod_name_1)
        manager.inject(version=1)
        response = aws_client.sns.list_topics()["Topics"]
        assert response
        assert not aws_client.sqs.list_queues().get("QueueUrls")

        reset_state()

        manager = get_pods_manager(pod_name_2)
        manager.inject(version=1)
        response = aws_client.sns.list_topics()["Topics"]
        assert response
        assert aws_client.sqs.list_queues().get("QueueUrls")

        # clean pods
        self.client.delete(pod_name_1, delete_from_remote=False)
        self.client.delete(pod_name_2, delete_from_remote=False)


class TestMetamodelUtils:
    @pytest.mark.parametrize("service_name", ["s3", "appsync", "sns"])
    def test_active_service_regions(
        self, set_pods_env, service_name, s3_bucket, sns_create_topic, aws_client, account_id
    ):
        # create resources
        resource_name = f"r-{short_uid()}"
        resource_id = None
        if service_name == "appsync":
            result = aws_client.appsync.create_graphql_api(
                name=resource_name, authenticationType="NONE"
            )
            resource_id = result["graphqlApi"]["apiId"]
        elif service_name == "sns":
            sns_create_topic()

        try:
            # determine regions
            regions = active_service_regions(service_name)
            all_regions = get_valid_regions_for_service(service_name)
            regions_current_account = [
                region for region in regions if region.account_id == account_id
            ]
            # assert that only the active (and not all) regions were returned
            assert len(regions) >= 1
            # S3 is a global service, and its usage of CrossAccountAttribute will create an entry in each region
            # not sure if it's a bug or not, but adapt the test for it
            if service_name == "s3" and not config.LEGACY_V2_S3_PROVIDER:
                assert len(regions_current_account) == len(regions)
            else:
                assert len(regions_current_account) == 1
                assert len(regions) < len(all_regions)
        finally:
            # clean up
            if service_name == "appsync":
                aws_client.appsync.delete_graphql_api(apiId=resource_id)
