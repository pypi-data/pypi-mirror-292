import json
import logging
import os
import re
from datetime import datetime, timedelta

import botocore.config
import pytest
from botocore.exceptions import ClientError
from localstack import config
from localstack.constants import LOCALHOST_HOSTNAME
from localstack.pro.core import config as config_ext
from localstack.testing.aws.util import is_aws_cloud
from localstack.testing.config import SECONDARY_TEST_AWS_REGION_NAME
from localstack.testing.pytest import markers
from localstack.utils.container_utils.container_client import ContainerException
from localstack.utils.docker_utils import DOCKER_CLIENT
from localstack.utils.files import new_tmp_dir, save_file
from localstack.utils.functions import run_safe
from localstack.utils.strings import short_uid
from localstack.utils.sync import retry

LOG = logging.getLogger(__name__)

TEST_DOCKERFILE = """
FROM nginx
ENV foo=bar
"""


@pytest.fixture
def cleanup_images():
    images = []

    yield images

    for image in images:
        try:
            DOCKER_CLIENT.remove_image(image=image, force=True)
        except ContainerException as e:
            LOG.debug("Error while removing image %s: %s", image, e)


def _pull_image_if_not_exists(image_name: str):
    if image_name not in DOCKER_CLIENT.get_docker_image_names():
        DOCKER_CLIENT.pull_image(image_name)


class TestECR:
    @pytest.fixture
    def create_docker_image(self, cleanup_images):
        def _create_image(repo_uri: str, docker_file: str = TEST_DOCKERFILE) -> None:
            docker_dir = new_tmp_dir()
            save_file(os.path.join(docker_dir, "Dockerfile"), docker_file)
            DOCKER_CLIENT.build_image(dockerfile_path=docker_dir, image_name=repo_uri)
            cleanup_images.append(repo_uri)

        return _create_image

    # docker daemon on host cannot access ecr repository, since exposed ports for internal networks do not work
    # see https://github.com/moby/moby/issues/36174
    @markers.skip_offline
    @markers.aws.unknown
    def test_create_delete_image(self, create_repository, create_docker_image, aws_client):
        repos_before = aws_client.ecr.describe_repositories()["repositories"]

        # create repo/registry
        repo_name = f"repo-{short_uid()}"
        result = create_repository(repositoryName=repo_name)
        reg_id = result["repository"].get("registryId")
        repo_uri = result["repository"].get("repositoryUri")

        # assert repo exists
        result = aws_client.ecr.describe_repositories()
        assert len(repos_before) + 1 == len(result["repositories"])

        # create test image
        images_before = aws_client.ecr.list_images(repositoryName=repo_name)["imageIds"]
        create_docker_image(repo_uri=repo_uri)

        # push image to registry
        DOCKER_CLIENT.push_image(repo_uri)

        # list images
        images = aws_client.ecr.list_images(repositoryName=repo_name)["imageIds"]
        assert len(images_before) + 1 == len(images)

        # delete image from registry
        result = aws_client.ecr.batch_delete_image(
            registryId=reg_id,
            repositoryName=repo_name,
            imageIds=[{"imageDigest": images[-1]["imageDigest"], "imageTag": "latest"}],
        )
        assert result.get("imageIds")

        # list images
        images = aws_client.ecr.list_images(repositoryName=repo_name)["imageIds"]
        assert len(images_before) == len(images)

        # clean up
        DOCKER_CLIENT.remove_image(repo_uri, force=True)
        run_safe(lambda: DOCKER_CLIENT.remove_container("localstack_registry", force=True))

    @markers.aws.unknown
    def test_put_image_tag_mutability(self, create_repository, aws_client):
        repo_name = f"repo-{short_uid()}"
        rs = create_repository(repositoryName=repo_name)
        assert rs["ResponseMetadata"]["HTTPStatusCode"] == 200

        aws_client.ecr.put_image_tag_mutability(
            repositoryName=repo_name, imageTagMutability="IMMUTABLE"
        )
        assert rs["ResponseMetadata"]["HTTPStatusCode"] == 200
        rs = aws_client.ecr.describe_repositories(repositoryNames=[repo_name])
        assert len(rs["repositories"]) == 1
        assert rs["repositories"][0]["imageTagMutability"] == "IMMUTABLE"

    @markers.aws.unknown
    def test_ecr_tagging(self, create_repository, aws_client):
        """Testing resource tagging in ECR"""
        repository_name = f"repo-{short_uid()}"
        tag_key = f"some_key_{short_uid()}"
        tag_value = f"some_value_{short_uid()}"

        repository = create_repository(repositoryName=repository_name)["repository"]
        repository_arn = repository["repositoryArn"]
        put_tags = [{"Key": tag_key, "Value": tag_value}]
        aws_client.ecr.tag_resource(resourceArn=repository_arn, tags=put_tags)
        tag_list = aws_client.ecr.list_tags_for_resource(resourceArn=repository_arn)["tags"]
        assert tag_list == put_tags
        aws_client.ecr.untag_resource(resourceArn=repository_arn, tagKeys=[tag_key])
        tag_list = aws_client.ecr.list_tags_for_resource(resourceArn=repository_arn)["tags"]
        assert len(tag_list) == 0

    @markers.aws.unknown
    def test_lifecycle_policy(self, create_repository, aws_client):
        repo_name = f"repo-{short_uid()}"
        result = create_repository(repositoryName=repo_name)
        assert result["ResponseMetadata"]["HTTPStatusCode"] == 200

        # create policy
        policy = {
            "rules": [
                {
                    "rulePriority": 1,
                    "description": "test rule 123",
                    "selection": {
                        "countNumber": 14,
                        "countUnit": "days",
                        "tagStatus": "untagged",
                        "countType": "sinceImagePushed",
                    },
                    "action": {"type": "expire"},
                }
            ]
        }
        policy_text = json.dumps(policy)
        result = aws_client.ecr.put_lifecycle_policy(
            repositoryName=repo_name, lifecyclePolicyText=policy_text
        )
        assert result["ResponseMetadata"]["HTTPStatusCode"] == 200
        assert json.loads(result["lifecyclePolicyText"]) == json.loads(policy_text)

        # get policy
        result = aws_client.ecr.get_lifecycle_policy(repositoryName=repo_name)
        assert result["ResponseMetadata"]["HTTPStatusCode"] == 200
        assert json.loads(result["lifecyclePolicyText"]) == json.loads(policy_text)

        # delete policy
        result = aws_client.ecr.delete_lifecycle_policy(repositoryName=repo_name)
        assert json.loads(result["lifecyclePolicyText"]) == json.loads(policy_text)

    @markers.aws.unknown
    def test_describe_images_non_existent_repository_registry(self, aws_client):
        with pytest.raises(ClientError) as e:
            aws_client.ecr.describe_images(repositoryName="non_existent_repository")
        e.match(
            r"An error occurred \(RepositoryNotFoundException\) when calling the DescribeImages operation: "
            r"The repository with name 'non_existent_repository' does not exist in the registry with id '\d{12}'"
        )

    @markers.aws.unknown
    def test_repository_lifecycle(self, create_repository, aws_client):
        repo_name = f"test_repo_{short_uid()}"
        with pytest.raises(ClientError) as e:
            aws_client.ecr.describe_repositories(repositoryNames=[repo_name])
        e.match("RepositoryNotFound")
        creation_response = create_repository(repositoryName=repo_name)
        assert repo_name == creation_response["repository"]["repositoryName"]
        registry_id = creation_response["repository"]["registryId"]
        uri = creation_response["repository"]["repositoryUri"]
        describe_response = aws_client.ecr.describe_repositories(repositoryNames=[repo_name])
        assert repo_name == describe_response["repositories"][0]["repositoryName"]
        assert registry_id == describe_response["repositories"][0]["registryId"]
        assert uri == describe_response["repositories"][0]["repositoryUri"]
        deletion_response = aws_client.ecr.delete_repository(
            repositoryName=repo_name, registryId=registry_id
        )
        assert repo_name == deletion_response["repository"]["repositoryName"]
        assert registry_id == deletion_response["repository"]["registryId"]
        assert uri == deletion_response["repository"]["repositoryUri"]

    @markers.aws.unknown
    def test_repository_deletion_in_registry(
        self, create_repository, create_docker_image, aws_client
    ):
        repo_name = f"test_repo_{short_uid()}"
        repo_name_2 = f"test_repo_{short_uid()}"
        creation_response = create_repository(repositoryName=repo_name)
        create_repository(repositoryName=repo_name_2)
        repo_uri = creation_response["repository"]["repositoryUri"]
        create_docker_image(repo_uri=repo_uri)
        # push image to registry
        DOCKER_CLIENT.push_image(repo_uri)

        # check if image can be pulled
        DOCKER_CLIENT.pull_image(repo_uri)
        aws_client.ecr.describe_images(repositoryName=repo_name)

        # delete local image
        DOCKER_CLIENT.remove_image(repo_uri, force=True)

        # delete repository
        with pytest.raises(ClientError) as e:
            aws_client.ecr.delete_repository(repositoryName=repo_name)
        e.match("RepositoryNotEmptyException")

        image_ids = aws_client.ecr.list_images(repositoryName=repo_name)["imageIds"]
        result = aws_client.ecr.batch_delete_image(repositoryName=repo_name, imageIds=image_ids)
        assert len(result["imageIds"]) == 1
        assert len(result["failures"]) == 0
        aws_client.ecr.delete_repository(repositoryName=repo_name)

        # pulling should not be available anymore
        with pytest.raises(ContainerException):
            DOCKER_CLIENT.pull_image(repo_uri)

    @markers.aws.unknown
    def test_batch_get_image(
        self, create_repository, create_docker_image, aws_client_factory, aws_client
    ):
        repo_name = f"repo-{short_uid()}"

        with pytest.raises(ClientError) as e:
            aws_client.ecr.batch_get_image(
                repositoryName=repo_name, imageIds=[{"imageTag": "latest"}]
            )
        e.match("RepositoryNotFound")
        create_result = create_repository(repositoryName=repo_name)
        repo_uri = create_result["repository"]["repositoryUri"]
        repo_uri_tag2 = f"{repo_uri}:t2"
        create_docker_image(repo_uri=repo_uri)

        # push image to registry
        DOCKER_CLIENT.push_image(repo_uri)
        image_digest = DOCKER_CLIENT.inspect_image(repo_uri)["RepoDigests"][0].rpartition("@")[2]

        def assert_return_image(result):
            assert len(result["images"]) == 1
            assert len(result["failures"]) == 0
            image = result["images"][0]
            assert image["registryId"] == create_result["repository"]["registryId"]
            assert image["repositoryName"] == repo_name
            assert "application/vnd.docker.distribution.manifest.v2+json" in image["imageManifest"]
            assert (
                image["imageManifestMediaType"]
                == "application/vnd.docker.distribution.manifest.v2+json"
            )
            assert image["imageId"] == {"imageTag": "latest", "imageDigest": image_digest}

        # get by image tag
        result = aws_client.ecr.batch_get_image(
            repositoryName=repo_name, imageIds=[{"imageTag": "latest"}]
        )
        assert_return_image(result)
        # get by image digest
        result = aws_client.ecr.batch_get_image(
            repositoryName=repo_name, imageIds=[{"imageDigest": image_digest}]
        )
        assert_return_image(result)
        result = aws_client.ecr.batch_get_image(
            repositoryName=repo_name, imageIds=[{"imageTag": "t2"}]
        )
        assert len(result["images"]) == 0
        assert len(result["failures"]) == 1
        failure = result["failures"][0]
        assert failure["imageId"]["imageTag"] == "t2"
        assert failure["failureCode"] == "ImageNotFound"
        assert failure["failureReason"] == "Requested image not found"

        # test two ids, one with non-existent tag, one with structurally invalid digest
        # should return two failures, ImageNotFound and InvalidImageDigest
        result = aws_client.ecr.batch_get_image(
            repositoryName=repo_name,
            imageIds=[{"imageTag": "t2"}, {"imageDigest": "invalid_digest"}],
        )
        assert len(result["images"]) == 0
        assert len(result["failures"]) == 2
        failures = result["failures"]
        assert {
            "imageId": {"imageTag": "t2"},
            "failureCode": "ImageNotFound",
            "failureReason": "Requested image not found",
        } in failures
        assert {
            "imageId": {"imageDigest": "invalid_digest"},
            "failureCode": "InvalidImageDigest",
            "failureReason": "Invalid request parameters: image digest should satisfy the regex '[a-zA-Z0-9-_+.]+:[a-fA-F0-9]+'",
        } in failures
        create_docker_image(repo_uri=repo_uri_tag2)
        DOCKER_CLIENT.push_image(repo_uri_tag2)
        # get by image digest - two matching images
        result = aws_client.ecr.batch_get_image(
            repositoryName=repo_name, imageIds=[{"imageDigest": image_digest}]
        )
        assert len(result["images"]) == 2
        assert len(result["failures"]) == 0
        image_ids = [image["imageId"] for image in result["images"]]
        assert {"imageTag": "latest", "imageDigest": image_digest} in image_ids
        assert {"imageTag": "t2", "imageDigest": image_digest} in image_ids
        # get with an imageId with neither tag nor digest set - should return a failure with MissingDigestAndTag
        result = aws_client.ecr.batch_get_image(repositoryName=repo_name, imageIds=[{}])
        assert len(result["images"]) == 0
        assert len(result["failures"]) == 1
        failures = result["failures"]
        assert {
            "imageId": {},
            "failureCode": "MissingDigestAndTag",
            "failureReason": "Invalid request parameters: both tag and digest cannot be null",
        } == failures[0]
        # test call with empty list of image ids - should result in immediate failure
        ecr_client_without_parameter_validation = aws_client_factory.get_client(
            service_name="ecr", config=botocore.config.Config(parameter_validation=False)
        )
        with pytest.raises(ClientError) as e:
            ecr_client_without_parameter_validation.batch_get_image(
                repositoryName=repo_name, imageIds=[]
            )
        assert e.match(
            r"InvalidParameterException.*"
            "Invalid parameter at 'imageIds' failed to satisfy constraint: 'Member must have length greater than or equal to 1'"
        )

    @markers.aws.unknown
    def test_batch_get_images_tag_and_digest(
        self, create_repository, create_docker_image, aws_client
    ):
        repo_name = f"repo-{short_uid()}"
        create_result = create_repository(repositoryName=repo_name)
        repo_uri = create_result["repository"]["repositoryUri"]
        create_docker_image(repo_uri=repo_uri)

        # push image to registry
        DOCKER_CLIENT.push_image(repo_uri)
        image_digest = DOCKER_CLIENT.inspect_image(repo_uri)["RepoDigests"][0].rpartition("@")[2]
        # test matching with imageId containing both tag and digest
        result = aws_client.ecr.batch_get_image(
            repositoryName=repo_name, imageIds=[{"imageTag": "latest", "imageDigest": image_digest}]
        )
        images = result["images"]
        assert len(images) == 1
        assert images[0]["imageId"] == {"imageTag": "latest", "imageDigest": image_digest}
        assert len(result["failures"]) == 0
        # test matching with imageId having a non-existent tag, but correct digest
        result = aws_client.ecr.batch_get_image(
            repositoryName=repo_name,
            imageIds=[{"imageTag": "invalid_tag", "imageDigest": image_digest}],
        )
        assert len(result["images"]) == 0
        assert len(result["failures"]) == 1
        failure = result["failures"][0]
        assert failure["imageId"] == {"imageTag": "invalid_tag", "imageDigest": image_digest}
        assert failure["failureCode"] == "ImageNotFound"
        assert failure["failureReason"] == "Requested image not found"
        # test matching with imageId having a correct (existing) tag, but an invalid
        # (=not matching the tag, but structurally correct) image digest
        invalid_digest = f"sha256:{'a' * 64}"
        result = aws_client.ecr.batch_get_image(
            repositoryName=repo_name,
            imageIds=[{"imageTag": "latest", "imageDigest": invalid_digest}],
        )
        assert len(result["images"]) == 0
        assert len(result["failures"]) == 1
        failure = result["failures"][0]
        assert failure["imageId"] == {"imageTag": "latest", "imageDigest": invalid_digest}
        assert failure["failureCode"] == "ImageTagDoesNotMatchDigest"
        assert (
            failure["failureReason"]
            == "Invalid request parameters: given tag does not map to the given digest"
        )
        # test matching with both an invalid tag and invalid digest (image should not be found)
        result = aws_client.ecr.batch_get_image(
            repositoryName=repo_name,
            imageIds=[{"imageTag": "invalid_tag", "imageDigest": invalid_digest}],
        )
        assert len(result["images"]) == 0
        assert len(result["failures"]) == 1
        failure = result["failures"][0]
        assert failure["imageId"] == {"imageTag": "invalid_tag", "imageDigest": invalid_digest}
        assert failure["failureCode"] == "ImageNotFound"
        assert failure["failureReason"] == "Requested image not found"

    @markers.aws.unknown
    def test_batch_delete_images_tag_and_digest(
        self, create_repository, create_docker_image, aws_client
    ):
        repo_name = f"repo-{short_uid()}"
        create_result = create_repository(repositoryName=repo_name)
        repo_uri = create_result["repository"]["repositoryUri"]
        repo_uri_tag2 = f"{repo_uri}:t2"
        create_docker_image(repo_uri=repo_uri)

        # push image to registry
        DOCKER_CLIENT.push_image(repo_uri)
        image_digest = DOCKER_CLIENT.inspect_image(repo_uri)["RepoDigests"][0].rpartition("@")[2]
        # delete with invalid tag -> only failures
        result = aws_client.ecr.batch_delete_image(
            repositoryName=repo_name,
            imageIds=[{"imageTag": "invalid_tag", "imageDigest": image_digest}],
        )
        assert len(result["imageIds"]) == 0
        assert len(result["failures"]) == 1
        failure = result["failures"][0]
        assert failure["imageId"] == {"imageTag": "invalid_tag", "imageDigest": image_digest}
        assert failure["failureCode"] == "ImageNotFound"
        assert failure["failureReason"] == "Requested image not found"
        # delete with correct tag, but invalid (but structurally correct) image digest
        # -> Fails with ImageTagDoesNotMatchDigest
        invalid_digest = f"sha256:{'a' * 64}"
        result = aws_client.ecr.batch_delete_image(
            repositoryName=repo_name,
            imageIds=[{"imageTag": "latest", "imageDigest": invalid_digest}],
        )
        assert len(result["imageIds"]) == 0
        assert len(result["failures"]) == 1
        failure = result["failures"][0]
        assert failure["imageId"] == {"imageTag": "latest", "imageDigest": invalid_digest}
        assert failure["failureCode"] == "ImageTagDoesNotMatchDigest"
        assert (
            failure["failureReason"]
            == "Invalid request parameters: given tag does not map to the given digest"
        )
        # delete with both invalid tag and digest -> fails with ImageNotFound
        result = aws_client.ecr.batch_delete_image(
            repositoryName=repo_name,
            imageIds=[{"imageTag": "invalid_tag", "imageDigest": invalid_digest}],
        )
        assert len(result["imageIds"]) == 0
        assert len(result["failures"]) == 1
        failure = result["failures"][0]
        assert failure["imageId"] == {"imageTag": "invalid_tag", "imageDigest": invalid_digest}
        assert failure["failureCode"] == "ImageNotFound"
        assert failure["failureReason"] == "Requested image not found"
        # correctly delete image
        result = aws_client.ecr.batch_delete_image(
            repositoryName=repo_name, imageIds=[{"imageTag": "latest", "imageDigest": image_digest}]
        )
        images = result["imageIds"]
        assert len(images) == 1
        assert len(result["failures"]) == 0
        assert images[0] == {"imageTag": "latest", "imageDigest": image_digest}
        # create second image and push both to repo
        create_docker_image(repo_uri=repo_uri_tag2)
        # push image to registry
        DOCKER_CLIENT.push_image(repo_uri)
        DOCKER_CLIENT.push_image(repo_uri_tag2)
        # check if they are both returned by get image
        result = aws_client.ecr.batch_get_image(
            repositoryName=repo_name, imageIds=[{"imageDigest": image_digest}]
        )
        images = result["images"]
        assert len(images) == 2
        assert len(result["failures"]) == 0
        # delete with both tag and digest set -> should only delete tag, not image with other tag but same digest
        result = aws_client.ecr.batch_delete_image(
            repositoryName=repo_name, imageIds=[{"imageTag": "latest", "imageDigest": image_digest}]
        )
        images = result["imageIds"]
        print(images)
        assert len(images) == 1
        assert len(result["failures"]) == 0
        # other image should still be present
        result = aws_client.ecr.batch_get_image(
            repositoryName=repo_name, imageIds=[{"imageDigest": image_digest}]
        )
        images = result["images"]
        assert len(images) == 1
        assert len(result["failures"]) == 0
        # check what happens with multiple image_ids referencing the same image
        result = aws_client.ecr.batch_delete_image(
            repositoryName=repo_name, imageIds=[{"imageDigest": image_digest}, {"imageTag": "t2"}]
        )
        images = result["imageIds"]
        assert len(images) == 1
        assert images[0] == {"imageDigest": image_digest, "imageTag": "t2"}
        assert len(result["failures"]) == 0

    @markers.aws.unknown
    def test_delete_images(self, create_repository, create_docker_image, aws_client):
        repo_name = f"repo-{short_uid()}"
        create_result = create_repository(repositoryName=repo_name)
        repo_uri = create_result["repository"]["repositoryUri"]
        repo_uri_tag2 = f"{repo_uri}:t2"
        result = aws_client.ecr.list_images(repositoryName=repo_name)
        assert len(result["imageIds"]) == 0
        create_docker_image(repo_uri=repo_uri)
        DOCKER_CLIENT.push_image(repo_uri)
        image_digest = DOCKER_CLIENT.inspect_image(repo_uri)["RepoDigests"][0].rpartition("@")[2]
        result = aws_client.ecr.list_images(repositoryName=repo_name)
        assert len(result["imageIds"]) == 1
        create_docker_image(repo_uri=repo_uri_tag2)
        DOCKER_CLIENT.push_image(repo_uri_tag2)
        result = aws_client.ecr.list_images(repositoryName=repo_name)
        assert len(result["imageIds"]) == 2
        result = aws_client.ecr.batch_delete_image(
            repositoryName=repo_name, imageIds=[{"imageTag": "t2"}]
        )
        assert len(result["imageIds"]) == 1
        assert result["imageIds"][0] == {"imageDigest": image_digest, "imageTag": "t2"}
        assert len(result["failures"]) == 0
        result = aws_client.ecr.list_images(repositoryName=repo_name)
        assert len(result["imageIds"]) == 1
        image = result["imageIds"][0]
        assert image["imageTag"] == "latest"
        assert image["imageDigest"] == image_digest
        DOCKER_CLIENT.push_image(repo_uri_tag2)
        result = aws_client.ecr.list_images(repositoryName=repo_name)
        assert len(result["imageIds"]) == 2
        result = aws_client.ecr.batch_delete_image(
            repositoryName=repo_name, imageIds=[{"imageDigest": image_digest}]
        )
        assert len(result["imageIds"]) == 2
        assert len(result["failures"]) == 0

        result = aws_client.ecr.list_images(repositoryName=repo_name)
        assert len(result["imageIds"]) == 0

    @markers.aws.unknown
    def test_list_images(self, create_repository, create_docker_image, aws_client):
        repo_name = f"repo-{short_uid()}"
        create_result = create_repository(repositoryName=repo_name)
        repo_uri = create_result["repository"]["repositoryUri"]
        repo_uri_tag2 = f"{repo_uri}:t2"
        result = aws_client.ecr.list_images(repositoryName=repo_name)
        assert len(result["imageIds"]) == 0
        create_docker_image(repo_uri=repo_uri)
        # push image to registry
        DOCKER_CLIENT.push_image(repo_uri)
        image_digest = DOCKER_CLIENT.inspect_image(repo_uri)["RepoDigests"][0].rpartition("@")[2]
        result = aws_client.ecr.list_images(repositoryName=repo_name)
        assert len(result["imageIds"]) == 1
        assert {"imageTag": "latest", "imageDigest": image_digest} in result["imageIds"]

        create_docker_image(repo_uri=repo_uri_tag2)
        DOCKER_CLIENT.push_image(repo_uri_tag2)
        result = aws_client.ecr.list_images(repositoryName=repo_name)
        assert len(result["imageIds"]) == 2
        assert {"imageTag": "latest", "imageDigest": image_digest} in result["imageIds"]
        assert {"imageTag": "t2", "imageDigest": image_digest} in result["imageIds"]

    @markers.aws.unknown
    def test_describe_images(self, create_repository, create_docker_image, aws_client):
        repo_name = f"repo-{short_uid()}"
        with pytest.raises(ClientError) as e:
            aws_client.ecr.describe_images(repositoryName=repo_name)
        e.match("RepositoryNotFound")
        create_result = create_repository(repositoryName=repo_name)
        repo_uri = create_result["repository"]["repositoryUri"]
        repo_uri_tag2 = f"{repo_uri}:t2"
        result = aws_client.ecr.describe_images(repositoryName=repo_name)
        assert len(result["imageDetails"]) == 0
        with pytest.raises(ClientError):
            aws_client.ecr.describe_images(
                repositoryName=repo_name, imageIds=[{"imageTag": "non_existent_tag"}]
            )
        create_docker_image(repo_uri=repo_uri)

        # push image to registry
        DOCKER_CLIENT.push_image(repo_uri)

        result = aws_client.ecr.describe_images(repositoryName=repo_name)
        assert len(result["imageDetails"]) == 1
        image_details = result["imageDetails"][0]
        assert len(image_details["imageTags"]) == 1
        # image should be pushed less than 3 minutes ago
        assert datetime.now(tz=image_details["imagePushedAt"].tzinfo) - image_details[
            "imagePushedAt"
        ] < timedelta(minutes=3)

        create_docker_image(repo_uri=repo_uri_tag2)
        DOCKER_CLIENT.push_image(repo_uri_tag2)

        result = aws_client.ecr.describe_images(repositoryName=repo_name)
        assert len(result["imageDetails"]) == 1
        assert len(result["imageDetails"][0]["imageTags"]) == 2
        assert set(result["imageDetails"][0]["imageTags"]) == {"latest", "t2"}

        result = aws_client.ecr.describe_images(
            repositoryName=repo_name, imageIds=[{"imageTag": "latest"}]
        )
        assert len(result["imageDetails"]) == 1
        assert len(result["imageDetails"][0]["imageTags"]) == 2
        assert set(result["imageDetails"][0]["imageTags"]) == {"latest", "t2"}

        with pytest.raises(ClientError):
            aws_client.ecr.describe_images(
                repositoryName=repo_name, imageIds=[{"imageTag": "non_existent_tag"}]
            )

    @markers.aws.unknown
    def test_get_authorization_token(self, create_repository, aws_client):
        """Test the get authorization token response"""
        repo_name = f"repo-{short_uid()}"
        create_repository(repositoryName=repo_name)
        result = aws_client.ecr.get_authorization_token()
        assert len(result["authorizationData"]) > 0
        authorization_data = result["authorizationData"][0]
        assert "authorizationToken" in authorization_data
        assert authorization_data["proxyEndpoint"].startswith("http")
        assert LOCALHOST_HOSTNAME in authorization_data["proxyEndpoint"]
        assert authorization_data["expiresAt"] - datetime.now(
            tz=authorization_data["expiresAt"].tzinfo
        ) > timedelta(hours=11)

    # docker daemon on host cannot access ecr repository, since exposed ports for internal networks do not work
    # see https://github.com/moby/moby/issues/36174
    @markers.skip_offline
    @markers.aws.unknown
    def test_two_different_repositories(self, create_repository, aws_client):
        repo_name_1 = f"repo-1-{short_uid()}"
        repo_name_2 = f"repo-2-{short_uid()}"
        result = create_repository(repositoryName=repo_name_1)
        repo_uri_1 = result["repository"].get("repositoryUri")
        result = create_repository(repositoryName=repo_name_2)
        repo_uri_2 = result["repository"].get("repositoryUri")

        # create test image, push to registry
        _pull_image_if_not_exists("alpine")
        DOCKER_CLIENT.tag_image("alpine", repo_uri_1)
        DOCKER_CLIENT.push_image(repo_uri_1)

        result = aws_client.ecr.list_images(repositoryName=repo_name_1)
        assert len(result["imageIds"]) == 1

        result = aws_client.ecr.list_images(repositoryName=repo_name_2)
        assert not result["imageIds"]

        # create test image 2, push to registry
        DOCKER_CLIENT.tag_image("alpine", repo_uri_2)
        DOCKER_CLIENT.push_image(repo_uri_2)

        result = aws_client.ecr.list_images(repositoryName=repo_name_1)
        assert len(result["imageIds"]) == 1

        result = aws_client.ecr.list_images(repositoryName=repo_name_2)
        assert len(result["imageIds"]) == 1

    @markers.aws.validated
    def test_auth_token_in_different_regions(self, aws_client_factory, snapshot):
        repo_name_1 = f"repo-1-{short_uid()}"
        repo_name_2 = f"repo-2-{short_uid()}"
        region_1 = "us-east-1"
        region_2 = "eu-west-1"
        region_1_client = aws_client_factory.get_client(service_name="ecr", region_name=region_1)
        region_2_client = aws_client_factory.get_client(service_name="ecr", region_name=region_2)

        region_1_client.create_repository(repositoryName=repo_name_1)
        region_2_client.create_repository(repositoryName=repo_name_2)

        auth_tokens_1 = region_1_client.get_authorization_token()["authorizationData"]
        auth_tokens_2 = region_2_client.get_authorization_token()["authorizationData"]

        snapshot.match("amount-tokens-region-1", len(auth_tokens_1))
        snapshot.match("amount-tokens-region-2", len(auth_tokens_2))

        region_1_client.delete_repository(repositoryName=repo_name_1)
        region_2_client.delete_repository(repositoryName=repo_name_2)

    @markers.snapshot.skip_snapshot_verify(
        paths=["$..repositoryUri", "$..architecture", "$..signatures"]
    )
    @markers.aws.validated
    def test_put_image(
        self,
        create_repository,
        cleanup_images,
        login_docker_client,
        aws_client,
        account_id,
        snapshot,
    ):
        repo_name = f"repo-1-{short_uid()}"
        snapshot.add_transformer(snapshot.transform.regex(repo_name, "<repo-name>"))
        result = create_repository(repositoryName=repo_name)
        snapshot.match("repo-details", result["repository"])

        repo_uri = result["repository"].get("repositoryUri")
        if is_aws_cloud():
            registry_id = repo_uri.split(".")[0]
        else:
            registry_id = account_id

        # login to registry
        login_docker_client(registryIds=[registry_id])

        # create test image, push to registry
        _pull_image_if_not_exists("alpine")
        DOCKER_CLIENT.tag_image("alpine", repo_uri)
        DOCKER_CLIENT.push_image(repo_uri)
        cleanup_images.append(repo_uri)

        # receive manifest for given media type
        result = aws_client.ecr.list_images(registryId=registry_id, repositoryName=repo_name)
        assert len(result["imageIds"]) == 1
        result = aws_client.ecr.batch_get_image(
            registryId=registry_id, repositoryName=repo_name, imageIds=result["imageIds"]
        )
        images = result["images"]
        manifest_json = images[0]["imageManifest"]

        # TODO: snapshot manifest dict (currently too many discrepancies)
        manifest_dict = json.loads(manifest_json)

        # run assertions on manifest content
        assert manifest_dict.get("schemaVersion") == 2

        # put image under new tag
        aws_client.ecr.put_image(
            repositoryName=repo_name, imageTag="tag2", imageManifest=manifest_json
        )
        cleanup_images.append(f"{repo_uri}:tag2")

        # assert that we now have two images
        result = aws_client.ecr.list_images(repositoryName=repo_name)
        assert len(result["imageIds"]) == 2
        image_tags = [img["imageTag"] for img in result["imageIds"]]
        assert set(image_tags) == {"latest", "tag2"}

    @markers.snapshot.skip_snapshot_verify(paths=["$..repository.repositoryUri"])
    @markers.aws.validated
    def test_registry_scanning_configuration(self, aws_client, create_repository, snapshot):
        snapshot.add_transformer(snapshot.transform.key_value("repositoryName"))

        # assert response before any custom configuration has been set
        response = aws_client.ecr.get_registry_scanning_configuration()
        snapshot.match("get-registry-scanning-configuration-default", response)

        # create repository to test influence on repository-specific data
        repository_name_1 = f"test-repository-{short_uid()}"
        repository_name_2 = f"test-repository-{short_uid()}"
        result = create_repository(repositoryName=repository_name_1)
        snapshot.match("repository1-details", result)

        repo_scanning_config_result = aws_client.ecr.batch_get_repository_scanning_configuration(
            repositoryNames=[repository_name_1]
        )
        snapshot.match("batch-repo-scanning-configuration-default", repo_scanning_config_result)

        response = aws_client.ecr.put_registry_scanning_configuration(
            scanType="BASIC",
            rules=[
                {
                    "repositoryFilters": [
                        {
                            "filter": "test-repository-*",
                            "filterType": "WILDCARD",
                        }
                    ],
                    "scanFrequency": "SCAN_ON_PUSH",
                }
            ],
        )
        snapshot.match("put-registry-scanning-configuration-basic", response)

        repo_scanning_config_result = aws_client.ecr.batch_get_repository_scanning_configuration(
            repositoryNames=[repository_name_1]
        )
        snapshot.match("batch-repo-scanning-configuration-after-put", repo_scanning_config_result)

        response = aws_client.ecr.get_registry_scanning_configuration()
        snapshot.match("get-registry-scanning-configuration-after-put", response)

        # check if it applies to new repositories
        result = create_repository(repositoryName=repository_name_2)
        snapshot.match("repository2-details", result)

        def _get_repository_scanning_config_applied_to_repository_two():
            repo_scanning_config_result = (
                aws_client.ecr.batch_get_repository_scanning_configuration(
                    repositoryNames=[repository_name_1, repository_name_2]
                )
            )
            repository_2_config = [
                result
                for result in repo_scanning_config_result["scanningConfigurations"]
                if result["repositoryName"] == repository_name_2
            ][0]
            assert repository_2_config["scanFrequency"] == "SCAN_ON_PUSH"
            return repo_scanning_config_result

        repo_scanning_config_result = retry(
            _get_repository_scanning_config_applied_to_repository_two, retries=5, sleep=1
        )
        snapshot.match(
            "batch-repo-scanning-configuration-after-put-second-repo", repo_scanning_config_result
        )

        # reset to default again
        def _reset_registry_scanning_config():
            return aws_client.ecr.put_registry_scanning_configuration(scanType="BASIC", rules=[])

        response = retry(_reset_registry_scanning_config, retries=5, sleep=5)
        snapshot.match("put-registry-scanning-configuration-reset", response)

        repo_scanning_config_result = aws_client.ecr.batch_get_repository_scanning_configuration(
            repositoryNames=[repository_name_1, repository_name_2]
        )
        snapshot.match("batch-repo-scanning-configuration-after-reset", repo_scanning_config_result)

        response = aws_client.ecr.get_registry_scanning_configuration()
        snapshot.match("get-registry-scanning-configuration-after-reset", response)


class TestECREndpoints:
    @markers.aws.validated
    def test_ecr_custom_localstack_host_endpoint(
        self, aws_client, create_repository, snapshot, monkeypatch
    ):
        """Check if the default repository uri returned matches the AWS format"""
        monkeypatch.setattr(
            config, "LOCALSTACK_HOST", config.HostAndPort.parse("testhost:1234", "", 0)
        )
        repo_name = f"repo-1-{short_uid()}"
        snapshot.add_transformer(snapshot.transform.regex(repo_name, "<repo-name>"))
        snapshot.add_transformer(
            snapshot.transform.regex(
                r"(amazonaws.com)|(testhost:\d{4})", "<domain_suffix_and_port>"
            )
        )
        result = create_repository(repositoryName=repo_name)
        # snapshot will assert the proper format of the repositoryUri
        snapshot.match("repo-details", result["repository"])

    @markers.aws.validated
    def test_ecr_default_endpoint(self, aws_client, create_repository, snapshot):
        """Check if the default repository uri returned matches the AWS format"""
        repo_name = f"repo-1-{short_uid()}"
        snapshot.add_transformer(snapshot.transform.regex(repo_name, "<repo-name>"))
        snapshot.add_transformer(
            snapshot.transform.regex(
                r"(amazonaws.com)|(localhost.localstack.cloud:\d{4})", "<domain_suffix_and_port>"
            )
        )
        result = create_repository(repositoryName=repo_name)
        # snapshot will assert the proper format of the repositoryUri
        snapshot.match("repo-details", result["repository"])

    @markers.aws.only_localstack
    def test_ecr_endpoint_strategy_off(self, aws_client_factory, monkeypatch, cleanups):
        """Check if the functionality of the ECR_ENDPOINT_STRATEGY flag"""
        monkeypatch.setattr(config_ext, "ECR_ENDPOINT_STRATEGY", "off")
        repo_name = f"repo-1-{short_uid()}"
        # we can not use the default region here, as a registry is most likely already running
        # and changing the ENDPOINT STRATEGY only affects NEW registries
        ecr_client = aws_client_factory(region_name=SECONDARY_TEST_AWS_REGION_NAME).ecr
        existing_repositories = ecr_client.describe_repositories()["repositories"]
        assert (
            not existing_repositories
        ), "Secondary region repositories not empty, this test can only fail"
        result = ecr_client.create_repository(repositoryName=repo_name)
        cleanups.append(lambda: ecr_client.delete_repository(repositoryName=repo_name))
        repository_uri = result["repository"].get("repositoryUri")
        assert re.match(rf"^{LOCALHOST_HOSTNAME}:\d{{2,5}}/{repo_name}$", repository_uri)
