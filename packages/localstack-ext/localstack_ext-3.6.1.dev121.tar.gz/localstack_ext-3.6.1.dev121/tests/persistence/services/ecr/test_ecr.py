import os
import re

import pytest
from localstack.constants import DEFAULT_AWS_ACCOUNT_ID
from localstack.utils.docker_utils import DOCKER_CLIENT
from localstack.utils.files import new_tmp_dir, save_file
from localstack.utils.strings import short_uid
from localstack_snapshot.snapshots.transformer import KeyValueBasedTransformer

TEST_DOCKERFILE = """
FROM nginx
ENV foo=bar
"""

TEST_DOCKERFILE_2 = """
FROM alpine
ENV hello=world
"""


def build_and_push_docker_image(docker_file_content: str, registry_uri: str):
    """builds docker image in a temp dir, and pushes it to the registry with the given uri"""
    docker_dir_latest = new_tmp_dir()
    save_file(os.path.join(docker_dir_latest, "Dockerfile"), docker_file_content)
    DOCKER_CLIENT.build_image(dockerfile_path=docker_dir_latest, image_name=registry_uri)
    DOCKER_CLIENT.push_image(registry_uri)


@pytest.mark.parametrize(
    "region_name, access_key, custom_tag",
    [
        ("us-east-1", DEFAULT_AWS_ACCOUNT_ID, "tag1"),
        ("us-east-1", "111111111111", "tag2"),
        ("eu-central-1", "112211221122", "tag3"),
    ],
)
def test_ecr_describe_repo_and_list_images(
    persistence_validations, snapshot, region_name, access_key, custom_tag, aws_client_factory
):
    def replace_port_transformer(k: str, v: str) -> str:
        if k == "repositoryUri" and isinstance(v, str):
            matched = re.match(re.compile(r".*\w:(\d*)/.*"), v)
            if matched:
                return matched.group(1)
        return None

    snapshot.add_transformer(
        KeyValueBasedTransformer(
            replace_port_transformer, replacement="<port>", replace_reference=False
        )
    )

    ecr_client = aws_client_factory.get_client(
        service_name="ecr", region_name=region_name, aws_access_key_id=access_key
    )

    # create two repositories
    repository_name_1 = f"repository-1-{short_uid()}"
    repository_name_2 = f"repository-2-{short_uid()}"
    image_ids = []
    for repo_name in [repository_name_1, repository_name_2]:
        # add two (different) images, one tagged latest, one with custom tag
        repo = ecr_client.create_repository(repositoryName=repo_name)["repository"]
        repository_uri = repo.get("repositoryUri")
        latest = repository_uri
        tagged = f"{repository_uri}:{custom_tag}"

        build_and_push_docker_image(TEST_DOCKERFILE, latest)
        build_and_push_docker_image(TEST_DOCKERFILE_2, tagged)

    image_ids = ecr_client.list_images(repositoryName=repository_name_1)["imageIds"]

    # image_ids of both repos should be the same, as we pushed the same images, in the same order
    assert image_ids == ecr_client.list_images(repositoryName=repository_name_2)["imageIds"]

    def validate():
        # validate repo 1: describe_repositories + try to push images
        repo_1 = ecr_client.describe_repositories(repositoryNames=[repository_name_1])[
            "repositories"
        ][0]
        assert repo_1.get("registryId") == access_key
        snapshot.match(f"ecr_describe_repo_{region_name}_{access_key}_1", repo_1)
        repo_uri = repo_1.get("repositoryUri")
        DOCKER_CLIENT.pull_image(repo_uri)
        DOCKER_CLIENT.pull_image(f"{repo_uri}:{custom_tag}")

        # validate repo 2: describe_repositories + try to push images
        repo_2 = ecr_client.describe_repositories(repositoryNames=[repository_name_2])[
            "repositories"
        ][0]
        assert repo_2.get("registryId") == access_key
        snapshot.match(f"ecr_describe_repo_{region_name}_{access_key}_2", repo_2)
        repo_uri = repo_2.get("repositoryUri")
        DOCKER_CLIENT.pull_image(repo_uri)
        DOCKER_CLIENT.pull_image(f"{repo_uri}:{custom_tag}")

        assert ecr_client.list_images(repositoryName=repository_name_1)["imageIds"] == image_ids
        assert ecr_client.list_images(repositoryName=repository_name_2)["imageIds"] == image_ids

    persistence_validations.register(validate)
