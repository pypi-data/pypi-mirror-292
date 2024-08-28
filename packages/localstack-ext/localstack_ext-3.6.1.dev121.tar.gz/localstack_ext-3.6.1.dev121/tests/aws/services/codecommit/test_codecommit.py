import logging
import os
import re
import shutil

import pytest
from localstack.constants import AWS_REGION_US_EAST_1
from localstack.pro.core.services.codecommit.repository import Repository
from localstack.testing.pytest import markers
from localstack.utils.files import mkdir, save_file
from localstack.utils.net import port_can_be_bound, wait_for_port_closed
from localstack.utils.strings import long_uid, short_uid
from localstack.utils.sync import poll_condition

NON_EXISTING_REPO_NAME = "this-repository-does-not-exist"
NON_EXISTING_BRANCH_NAME = "this-branch-does-not-exist"

LOG = logging.getLogger(__name__)

GIT_URL_REGEX = r"^git://([^:]+):(?P<port>\d+)/.*$"


@pytest.fixture
def create_codecommit_repository(aws_client):
    repositories = []

    def _create_repository(repository_name: str):
        result = aws_client.codecommit.create_repository(
            repositoryName=repository_name, repositoryDescription="generated test description"
        )
        clone_url_ssh = result["repositoryMetadata"]["cloneUrlSsh"]
        port = int(re.match(GIT_URL_REGEX, clone_url_ssh).group("port"))
        repositories.append({"name": repository_name, "port": port})
        return result

    yield _create_repository

    for repository in repositories:
        try:
            aws_client.codecommit.delete_repository(repositoryName=repository["name"])
            shutil.rmtree(Repository.get_path(AWS_REGION_US_EAST_1, repository["name"]))
            wait_for_port_closed(repository["port"])
        except Exception as e:
            LOG.debug("Exception during cleanup: %s", e)
    for repository in repositories:
        assert poll_condition(lambda: port_can_be_bound(repository["port"]), timeout=10)


@pytest.fixture
def codecommit_repository(create_codecommit_repository):
    return create_codecommit_repository(f"repo-{short_uid()}")


@pytest.fixture
def codecommit_repository_with_commit(create_codecommit_repository, aws_client):
    repository = create_codecommit_repository(f"repo-{short_uid()}")
    repository_name = repository["repositoryMetadata"]["repositoryName"]

    new_file_name = f"file-{short_uid()}"
    new_file_path = os.path.join(
        Repository.get_path(AWS_REGION_US_EAST_1, repository_name), new_file_name
    )
    save_file(new_file_path, "Hello.")

    result = aws_client.codecommit.create_commit(
        repositoryName=repository_name,
        branchName="master",
        authorName="Local Stack",
        email="tester@localstack.cloud",
        commitMessage=f"commit-{short_uid()}",
        putFiles=[{"filePath": new_file_path}],
    )
    return {"repository": repository, "commitId": result["commitId"], "fileName": new_file_name}


@pytest.fixture
def codecommit_repository_with_directory_commit(create_codecommit_repository, aws_client):
    repository = create_codecommit_repository(f"repo-{short_uid()}")
    repository_name = repository["repositoryMetadata"]["repositoryName"]
    repository_path = Repository.get_path(AWS_REGION_US_EAST_1, repository_name)

    new_file_dir_name = f"dir-{short_uid()}"
    new_file_dir_path = os.path.join(repository_path, new_file_dir_name)
    mkdir(new_file_dir_path)
    new_file_name = f"file-{short_uid()}"
    new_file_path = os.path.join(new_file_dir_path, new_file_name)
    save_file(new_file_path, "Hello.")

    result = aws_client.codecommit.create_commit(
        repositoryName=repository_name,
        branchName="master",
        authorName="Local Stack",
        email="tester@localstack.cloud",
        commitMessage=f"commit-{short_uid()}",
        putFiles=[{"filePath": new_file_path}],
    )
    return {
        "repository": repository,
        "commitId": result["commitId"],
        "fileName": new_file_name,
        "dirName": new_file_dir_name,
    }


class TestCodeCommit:
    @markers.aws.unknown
    def test_create_repository(self, aws_client):
        # create repository
        repository_name = f"repo-{short_uid()}"
        repository_description = "test repository description"
        result = aws_client.codecommit.create_repository(
            repositoryName=repository_name, repositoryDescription=repository_description
        )
        assert result["repositoryMetadata"]["repositoryName"] == repository_name
        assert result["repositoryMetadata"]["repositoryDescription"] == repository_description

        aws_client.codecommit.delete_repository(repositoryName=repository_name)
        shutil.rmtree(Repository.get_path(AWS_REGION_US_EAST_1, repository_name))
        clone_url_ssh = result["repositoryMetadata"]["cloneUrlSsh"]
        port = int(re.match(GIT_URL_REGEX, clone_url_ssh).group("port"))
        wait_for_port_closed(port)
        assert port_can_be_bound(port)

    @markers.aws.unknown
    def test_create_repository_with_invalid_name_raises_error(self, aws_client):
        repository_name = f"repo-{short_uid()}"
        repository_description = "test repository description"

        with pytest.raises(Exception) as e:
            aws_client.codecommit.create_repository(
                repositoryName=repository_name + "][", repositoryDescription=repository_description
            )

        assert e.typename == "InvalidRepositoryNameException"

    @markers.aws.unknown
    def test_get_non_existing_repository_raises_error(self, aws_client):
        with pytest.raises(Exception) as e:
            aws_client.codecommit.get_repository(repositoryName=NON_EXISTING_REPO_NAME)

        assert e.typename == "RepositoryDoesNotExistException"

    @markers.aws.unknown
    def test_delete_non_existing_repository_raises_error(self, aws_client):
        with pytest.raises(Exception) as e:
            aws_client.codecommit.delete_repository(repositoryName=NON_EXISTING_REPO_NAME)

        assert e.typename == "RepositoryDoesNotExistException"

    @markers.aws.unknown
    def test_get_repository_matches_created_repository(self, codecommit_repository, aws_client):
        repository_name = codecommit_repository["repositoryMetadata"]["repositoryName"]
        repository_description = codecommit_repository["repositoryMetadata"][
            "repositoryDescription"
        ]

        result = aws_client.codecommit.get_repository(repositoryName=repository_name)
        assert result["repositoryMetadata"]["repositoryName"] == repository_name
        assert result["repositoryMetadata"]["repositoryDescription"] == repository_description

    @markers.aws.unknown
    def test_delete_repository_matches_created_repository(self, codecommit_repository, aws_client):
        repository_name = codecommit_repository["repositoryMetadata"]["repositoryName"]
        repository_id = codecommit_repository["repositoryMetadata"]["repositoryId"]

        result = aws_client.codecommit.delete_repository(repositoryName=repository_name)
        assert result["repositoryId"] == repository_id

    @markers.aws.unknown
    def test_create_commit(self, codecommit_repository, aws_client):
        repository_name = codecommit_repository["repositoryMetadata"]["repositoryName"]

        new_file_path = os.path.join(
            Repository.get_path(AWS_REGION_US_EAST_1, repository_name), "new.txt"
        )
        save_file(new_file_path, "Hello.")

        result = aws_client.codecommit.create_commit(
            repositoryName=repository_name,
            branchName="master",
            authorName="Local Stack",
            email="tester@localstack.cloud",
            commitMessage="adding_new_file",
            putFiles=[{"filePath": new_file_path}],
        )

        assert "commitId" in result

    @markers.aws.unknown
    def test_commit_to_non_existing_repository_raises_error(self, aws_client):
        new_file_path = os.path.join(
            Repository.get_path(AWS_REGION_US_EAST_1, NON_EXISTING_REPO_NAME), "new.txt"
        )

        with pytest.raises(Exception) as e:
            aws_client.codecommit.create_commit(
                repositoryName=NON_EXISTING_REPO_NAME,
                branchName="master",
                authorName="Local Stack",
                email="tester@localstack.cloud",
                commitMessage="adding_new_file",
                putFiles=[{"filePath": new_file_path}],
            )

        assert e.typename == "RepositoryDoesNotExistException"

    @markers.aws.unknown
    def test_create_branch(self, codecommit_repository_with_commit, aws_client):
        repository_name = codecommit_repository_with_commit["repository"]["repositoryMetadata"][
            "repositoryName"
        ]
        commit_id = codecommit_repository_with_commit["commitId"]

        aws_client.codecommit.create_branch(
            repositoryName=repository_name,
            branchName=f"branch-{short_uid()}",
            commitId=commit_id,
        )

    @markers.aws.unknown
    def test_create_branch_on_non_existing_repository_raises_error(self, aws_client):
        with pytest.raises(Exception) as e:
            aws_client.codecommit.create_branch(
                repositoryName=NON_EXISTING_REPO_NAME,
                branchName=f"branch-{short_uid()}",
                commitId=long_uid(),
            )

        assert e.typename == "RepositoryDoesNotExistException"

    @markers.aws.unknown
    def test_get_branch(self, codecommit_repository_with_commit, aws_client):
        repository_name = codecommit_repository_with_commit["repository"]["repositoryMetadata"][
            "repositoryName"
        ]
        commit_id = codecommit_repository_with_commit["commitId"]
        branch_name = f"branch-{short_uid()}"

        aws_client.codecommit.create_branch(
            repositoryName=repository_name,
            branchName=branch_name,
            commitId=commit_id,
        )

        result = aws_client.codecommit.get_branch(
            repositoryName=repository_name, branchName=branch_name
        )

        assert result["branch"]["branchName"] == branch_name
        assert result["branch"]["commitId"] == commit_id

    @markers.aws.unknown
    def test_get_non_existing_branch(self, codecommit_repository_with_commit, aws_client):
        repository_name = codecommit_repository_with_commit["repository"]["repositoryMetadata"][
            "repositoryName"
        ]

        with pytest.raises(Exception) as e:
            aws_client.codecommit.get_branch(
                repositoryName=repository_name,
                branchName=NON_EXISTING_BRANCH_NAME,
            )

        assert e.typename == "BranchDoesNotExistException"

    @markers.aws.unknown
    def test_delete_branch(self, codecommit_repository_with_commit, aws_client):
        repository_name = codecommit_repository_with_commit["repository"]["repositoryMetadata"][
            "repositoryName"
        ]
        commit_id = codecommit_repository_with_commit["commitId"]
        branch_name = f"branch-{short_uid()}"

        aws_client.codecommit.create_branch(
            repositoryName=repository_name,
            branchName=branch_name,
            commitId=commit_id,
        )

        result = aws_client.codecommit.delete_branch(
            repositoryName=repository_name, branchName=branch_name
        )

        assert result["deletedBranch"]["branchName"] == branch_name
        assert result["deletedBranch"]["commitId"] == commit_id

    @markers.aws.unknown
    def test_delete_non_existing_branch(self, codecommit_repository_with_commit, aws_client):
        repository_name = codecommit_repository_with_commit["repository"]["repositoryMetadata"][
            "repositoryName"
        ]

        with pytest.raises(Exception) as e:
            aws_client.codecommit.delete_branch(
                repositoryName=repository_name,
                branchName=NON_EXISTING_BRANCH_NAME,
            )

        assert e.typename == "BranchDoesNotExistException"

    @markers.aws.unknown
    def test_get_file(self, codecommit_repository_with_commit, aws_client):
        repository_name = codecommit_repository_with_commit["repository"]["repositoryMetadata"][
            "repositoryName"
        ]
        commit_id = codecommit_repository_with_commit["commitId"]
        file_name = codecommit_repository_with_commit["fileName"]

        result = aws_client.codecommit.get_file(
            repositoryName=repository_name, filePath=file_name, commitSpecifier=commit_id
        )

        assert result["commitId"] == commit_id
        assert result["filePath"] == file_name
        assert result["fileContent"] == b"Hello."

    @markers.aws.unknown
    def test_get_folder(self, codecommit_repository_with_directory_commit, aws_client):
        repository_name = codecommit_repository_with_directory_commit["repository"][
            "repositoryMetadata"
        ]["repositoryName"]
        commit_id = codecommit_repository_with_directory_commit["commitId"]
        dir_name = codecommit_repository_with_directory_commit["dirName"]
        file_name = codecommit_repository_with_directory_commit["fileName"]

        result = aws_client.codecommit.get_folder(
            repositoryName=repository_name, folderPath=dir_name, commitSpecifier=commit_id
        )

        assert result["commitId"] == commit_id
        assert result["files"][0]["absolutePath"] == os.path.join(dir_name, file_name)
        assert result["folderPath"] == dir_name

    # FIXME
    @markers.aws.unknown
    def test_create_pull_request(self, codecommit_repository_with_commit, aws_client):
        repository_name = codecommit_repository_with_commit["repository"]["repositoryMetadata"][
            "repositoryName"
        ]
        commit_id = codecommit_repository_with_commit["commitId"]
        pr_title = f"pr-{short_uid()}"
        pr_description = "pr description"
        source_branch = f"source-branch-{short_uid()}"
        dest_branch = f"destination-branch-{short_uid()}"
        token = long_uid()

        aws_client.codecommit.create_branch(
            repositoryName=repository_name, branchName=source_branch, commitId=commit_id
        )
        aws_client.codecommit.create_branch(
            repositoryName=repository_name, branchName=dest_branch, commitId=commit_id
        )

        result = aws_client.codecommit.create_pull_request(
            title=pr_title,
            description=pr_description,
            targets=[
                {
                    "repositoryName": repository_name,
                    "sourceReference": source_branch,
                    "destinationReference": dest_branch,
                }
            ],
            clientRequestToken=token,
        )

        assert result["pullRequest"]["title"] == pr_title
        assert result["pullRequest"]["description"] == pr_description
        assert result["pullRequest"]["pullRequestTargets"][0]["repositoryName"] == repository_name
        assert result["pullRequest"]["pullRequestTargets"][0]["sourceReference"] == source_branch
        assert result["pullRequest"]["pullRequestTargets"][0]["destinationReference"] == dest_branch

    @markers.aws.unknown
    def test_list_pull_requests(self, codecommit_repository_with_commit, aws_client):
        repository_name = codecommit_repository_with_commit["repository"]["repositoryMetadata"][
            "repositoryName"
        ]
        commit_id = codecommit_repository_with_commit["commitId"]
        pr_title = f"pr-{short_uid()}"
        pr_description = "pr description"
        source_branch = f"source-branch-{short_uid()}"
        dest_branch = f"destination-branch-{short_uid()}"
        token = long_uid()

        aws_client.codecommit.create_branch(
            repositoryName=repository_name, branchName=source_branch, commitId=commit_id
        )
        aws_client.codecommit.create_branch(
            repositoryName=repository_name, branchName=dest_branch, commitId=commit_id
        )

        result = aws_client.codecommit.create_pull_request(
            title=pr_title,
            description=pr_description,
            targets=[
                {
                    "repositoryName": repository_name,
                    "sourceReference": source_branch,
                    "destinationReference": dest_branch,
                }
            ],
            clientRequestToken=token,
        )

        pr_id = result["pullRequest"]["pullRequestId"]

        result = aws_client.codecommit.list_pull_requests(repositoryName=repository_name)

        assert pr_id in result["pullRequestIds"]

    @markers.aws.unknown
    def test_repository_lifecycle(self, aws_client):
        repository_name = f"repo-{short_uid()}"
        repository_description = "test repository description"

        creation_result = aws_client.codecommit.create_repository(
            repositoryName=repository_name, repositoryDescription=repository_description
        )
        repository_metadata = creation_result["repositoryMetadata"]
        assert repository_name == repository_metadata["repositoryName"]
        assert repository_description == repository_metadata["repositoryDescription"]

        clone_url_ssh = repository_metadata["cloneUrlSsh"]
        port_regex = r"^git://([^:]+):(?P<port>\d+)/.*$"
        port = int(re.match(port_regex, clone_url_ssh).group("port"))
        deletion_result = aws_client.codecommit.delete_repository(repositoryName=repository_name)
        assert repository_metadata["repositoryId"] == deletion_result["repositoryId"]

        wait_for_port_closed(port)

    @markers.aws.unknown
    def test_tagging(self, aws_client):
        # TODO there is currently no validation that the resource exists, so we use a fake one for this test
        arn = "arn:aws:codecommit:us-east-1:000000000000:repo-96bf11ec"
        tags = {"test": "hello", "test2": "helloagain", "test3": "bye"}
        aws_client.codecommit.tag_resource(resourceArn=arn, tags=tags)
        tags_response = aws_client.codecommit.list_tags_for_resource(resourceArn=arn)
        assert tags_response.get("tags") == tags

        aws_client.codecommit.untag_resource(resourceArn=arn, tagKeys=["test", "test3"])
        tags_response = aws_client.codecommit.list_tags_for_resource(resourceArn=arn)
        assert tags_response.get("tags") == {"test2": "helloagain"}
