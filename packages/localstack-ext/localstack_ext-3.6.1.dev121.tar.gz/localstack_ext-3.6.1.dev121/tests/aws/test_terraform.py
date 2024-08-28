import os
import re
import threading

import pytest
from localstack.packages.terraform import terraform_package
from localstack.testing.config import (
    TEST_AWS_ACCESS_KEY_ID,
    TEST_AWS_REGION_NAME,
    TEST_AWS_SECRET_ACCESS_KEY,
)
from localstack.testing.pytest import markers
from localstack.utils.files import rm_rf
from localstack.utils.run import is_command_available, run
from localstack.utils.threads import start_worker_thread
from packaging import version

INIT_LOCK = threading.RLock()


# FIXME: lots of code duplication with test_terraform.py in community

# set after calling install()
TERRAFORM_BIN = None


def check_terraform_version():
    if not is_command_available(TERRAFORM_BIN):
        return False, None

    ver_string = run([TERRAFORM_BIN, "-version"])
    ver_string = re.search(r"v(\d+\.\d+\.\d+)", ver_string).group(1)

    if ver_string is None:
        return False, None
    return version.parse(ver_string) >= version.parse("0.15"), ver_string


@pytest.fixture(scope="class", autouse=True)
def setup_tf(account_id, region_name):
    def startup_cluster(*args, **kwargs):
        # skip starting up bigdata container in CI
        pass

    env_vars = {
        "AWS_ACCESS_KEY_ID": account_id,
        "AWS_SECRET_ACCESS_KEY": account_id,
        "AWS_REGION": region_name,
    }

    with INIT_LOCK:
        available, version = check_terraform_version()

        if not available:
            msg = "could not find a compatible version of terraform"
            if version:
                msg += f" (version = {version})"
            else:
                msg += " (command not found)"

            return pytest.skip(msg)

        run(
            [TERRAFORM_BIN, "apply", "-input=false", "tfplan"],
            cwd=get_base_dir(),
            env_vars=env_vars,
        )

    yield

    run([TERRAFORM_BIN, "destroy", "-auto-approve"], cwd=get_base_dir(), env_vars=env_vars)


def get_base_dir():
    return os.path.join(os.path.dirname(__file__), "terraform")


@markers.skip_offline
class TestTerraform:
    @classmethod
    def init_async(cls):
        def _run(*args):
            with INIT_LOCK:
                global TERRAFORM_BIN
                installer = terraform_package.get_installer()
                installer.install()
                TERRAFORM_BIN = installer.get_executable_path()
                base_dir = get_base_dir()
                env_vars = {
                    "AWS_ACCESS_KEY_ID": TEST_AWS_ACCESS_KEY_ID,
                    "AWS_SECRET_ACCESS_KEY": TEST_AWS_SECRET_ACCESS_KEY,
                    "AWS_REGION": TEST_AWS_REGION_NAME,
                }
                if not os.path.exists(os.path.join(base_dir, ".terraform", "plugins")):
                    run([TERRAFORM_BIN, "init", "-input=false"], cwd=base_dir, env_vars=env_vars)
                # remove any cache files from previous runs
                for tf_file in [
                    "tfplan",
                    "terraform.tfstate",
                    "terraform.tfstate.backup",
                ]:
                    rm_rf(os.path.join(base_dir, tf_file))
                # create TF plan
                run(
                    [TERRAFORM_BIN, "plan", "-out=tfplan", "-input=false"],
                    cwd=base_dir,
                    env_vars=env_vars,
                )

        start_worker_thread(_run)

    @markers.aws.unknown
    def test_appsync_deployed(self, aws_client):
        # assert existence of resources created via Terraform
        client = aws_client.appsync
        apis = client.list_graphql_apis()["graphqlApis"]
        api = [a for a in apis if a["name"] == "tf-test-1634"]
        assert api

    @markers.aws.unknown
    def test_emr_deployed(self, aws_client):
        # assert existence of resources created via Terraform
        clusters = aws_client.emr.list_clusters()["Clusters"]
        matching = [c for c in clusters if c["Name"] == "tf-emr-test-73451"]
        assert matching

    @markers.aws.unknown
    def test_glacier_deployed(self, aws_client):
        # assert existence of resources created via Terraform
        result = aws_client.glacier.list_vaults()
        vault_names = [v["VaultName"] for v in result["VaultList"]]
        assert "test-vault-73240" in vault_names
