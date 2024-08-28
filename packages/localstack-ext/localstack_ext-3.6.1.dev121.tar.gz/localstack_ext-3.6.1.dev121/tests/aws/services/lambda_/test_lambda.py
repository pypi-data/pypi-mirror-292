import base64
import hashlib
import json
import logging
import os
import tempfile
import time

import pytest
from botocore.exceptions import WaiterError
from localstack import config
from localstack.aws.api.lambda_ import Architecture, Runtime
from localstack.services.lambda_.invocation.docker_runtime_executor import docker_platform
from localstack.testing.pytest import markers
from localstack.utils import testutil
from localstack.utils.archives import create_zip_file_python
from localstack.utils.docker_utils import DOCKER_CLIENT, get_host_path_for_path_in_docker
from localstack.utils.files import mkdir, new_tmp_dir, rm_rf, save_file
from localstack.utils.strings import short_uid, to_bytes, to_str
from localstack.utils.sync import retry
from localstack.utils.testutil import get_lambda_log_events
from localstack_snapshot.snapshots.transformer import SortingTransformer

LOG = logging.getLogger(__name__)

LAYER_1_VALUE = 123
LAYER_2_VALUE = 456
LAYER_1_CONTENT = f"""
FOOBAR = {LAYER_1_VALUE}
"""
LAYER_2_CONTENT = f"""
FOOBAR = {LAYER_2_VALUE}
"""
TEST_LAMBDA_CONTENT = """
import glob
from a.b.c import mylib
def handler(event, *args, **kwargs):
    return {'value': mylib.FOOBAR, 'layer': glob.glob('/opt/**', recursive=True), "import_location": mylib.__file__}
"""
TEST_LIBS = ["boto3", "botocore", "dateutil", "jmespath", "s3transfer", "urllib3"]

TEST_LAYER_CONTENT = """
import glob
def handler(event, *args, **kwargs):
    return {'layer': glob.glob('/opt/**', recursive=True)}
"""

TEST_LAYER_CODE = """
import json

def handler(event, context):
    # Just print the event was passed to lambda
    print(json.dumps(event))
    return 0
"""
TEST_LAYER_OVERRIDES_RUNTIME_CODE = """
def handler(event, contest):
    try:
        import boto3
        can_import_boto3 = True
    except Exception:
        can_import_boto3 = False
    try:
        from boto3.test import TEST_VAR as test_var
    except Exception:
        test_var = None
    return {"can_import_boto3": can_import_boto3, "value": test_var}
"""
TEST_LAYER_OVERRIDE_LAMBDA_CONTENT = """
from pathlib import Path
import glob
def handler(event, *args, **kwargs):
    opt_contents = {}
    for file in [path for path in Path("/opt").iterdir() if path.is_file()]:
        opt_contents[str(file)] = file.read_text()
    return {'opt_contents': opt_contents}
"""
THIS_FOLDER = os.path.dirname(os.path.realpath(__file__))
LAMBDA_OVERRIDE_LAYER_1_PATH = os.path.join(THIS_FOLDER, "layer-override-test/layer-1")
LAMBDA_OVERRIDE_LAYER_2_PATH = os.path.join(THIS_FOLDER, "layer-override-test/layer-2")
LAMBDA_INTROSPECT_LAYER_PYTHON = os.path.join(THIS_FOLDER, "functions/lambda_introspect_layer.py")
LAYER_BIN_LAYER = os.path.join(THIS_FOLDER, "layers/bin_layer.zip")

LAMBDA_IMAGE_DOCKERFILE = """
FROM public.ecr.aws/lambda/nodejs:20
COPY app.js /var/task/
CMD [ "app.handler" ]
"""
LAMBDA_IMAGE_HANDLER = """
exports.handler = async (event) => {
    const response = {
        statusCode: 200,
        body: JSON.stringify({'foo': 'bar', 'env': process.env, 'value': event.value}),
    };
    console.log(`JS lambda container image handler: ${JSON.stringify(event)}`);
    return response;
};
"""
LAMBDA_IMAGE_DOCKERFILE_PYTHON_CUSTOM_RIC = """
FROM python:slim
RUN ["pip", "install", "requests"]
WORKDIR /app
RUN mkdir -p /app1
COPY app.py .
COPY app.py /app1/app_tmp.py
CMD [ "app.handler" ]
"""
LAMBDA_IMAGE_HANDLER_PYTHON = """
import os
import json
def handler(event, context):
    print(f'Python lambda container image handler: {event}')
    return {'statusCode': 200, 'body': json.dumps({'foo': 'bar', 'env': dict(os.environ), 'value': event['value']})}
if __name__ == '__main__':
    print(f"Lambda __main__ called: {__file__}")
"""
LAMBDA_IMAGE_HANDLER_PYTHON_CUSTOM_RIC = """
import os
import requests
RUNTIME_INTERFACE_URL = f"http://{os.environ.get('AWS_LAMBDA_RUNTIME_API')}/2018-06-01/runtime/invocation"
if __name__ == '__main__':
    while True:
        # get next invocation event
        response = requests.get(f"{RUNTIME_INTERFACE_URL}/next")
        invocation_id = response.headers.get("Lambda-Runtime-Aws-Request-Id")
        # return response
        return_value = {"test": "value"}
        requests.post(f"{RUNTIME_INTERFACE_URL}/{invocation_id}/response", json=return_value)
"""

LAMBDA_EXTERNAL_LAYER_HANDLER = """
import numpy as np
import json

def handler(event, context):
    return {'foo': 'bar', 'value': np.zeros(1)[0]}
"""
LAMBDA_IMAGE_DOCKERFILE_PYTHON_CHAINED = """
FROM public.ecr.aws/lambda/python:3.12
COPY app.py /var/task/
CMD [ "app.handler" ]
"""
LAMBDA_IMAGE_HANDLER_CHAINED_INVOCATIONS_1 = """
import json
import boto3
import os

if os.environ.get("AWS_ENDPOINT_URL"):
    endpoint_url = os.environ["AWS_ENDPOINT_URL"]
else:
    endpoint_url = None

def handler(event, context):
    print(f'Python lambda container image handler 1: {event}')
    region_name = (
        os.environ.get("AWS_DEFAULT_REGION") or os.environ.get("AWS_REGION") or "us-east-1"
    )
    lambda_client = boto3.client('lambda', region_name=region_name, endpoint_url=endpoint_url)
    invocation_result = lambda_client.invoke(
        FunctionName="%s",
        InvocationType="RequestResponse",
        Payload=json.dumps({
            "first-data": event.get("first-data")
        })
    )
    payload = json.loads(invocation_result["Payload"].read().decode("utf-8"))
    return payload
"""
LAMBDA_IMAGE_HANDLER_CHAINED_INVOCATIONS_2 = """
import json

def handler(event, context):
    print(f'Python lambda container image handler 2: {event}')
    return { "invoke_result": event.get("first-data") * 2 }
"""

LAMBDA_HOT_RELOADING_LAYER_TESTLIB = """
LAYER_CONSTANT = "value1"
"""
LAMBDA_HOT_RELOADING_LAYER_FUNCTION = """
from testlib import LAYER_CONSTANT
CONSTANT_VARIABLE = "value1"
COUNTER = 0


def handler(event, context):
    global COUNTER
    COUNTER += 1
    return {"counter": COUNTER, "constant": CONSTANT_VARIABLE, "layer_constant": LAYER_CONSTANT}
"""


@pytest.fixture(autouse=True)
def fixture_snapshot(snapshot):
    snapshot.add_transformer(snapshot.transform.lambda_api())
    snapshot.add_transformer(
        snapshot.transform.key_value("CodeSha256", reference_replacement=False)
    )


@pytest.fixture(scope="class")
def publish_layer_version(aws_client):
    layers = []

    def _publish_layer_version(**kwargs):
        result = aws_client.lambda_.publish_layer_version(**kwargs)
        layers.append((result["LayerArn"], result["Version"]))
        return result

    yield _publish_layer_version

    for layer_arn, layer_version in layers:
        try:
            aws_client.lambda_.delete_layer_version(
                LayerName=layer_arn, VersionNumber=layer_version
            )
        except Exception:
            LOG.debug(f"Failed to delete Lambda layer: {layer_arn=} | {layer_version=}")


@pytest.fixture(scope="class")
def login_docker_client_default_registry(login_docker_client):
    """Log in the local Docker client to the default ECR registry"""
    return login_docker_client()


@pytest.mark.usefixtures("login_docker_client_default_registry")
class TestLambdaContainer:
    @pytest.mark.parametrize(
        "lambda_image_dockerfile,lambda_image_handler,lambda_image_handler_filename",
        [
            (LAMBDA_IMAGE_DOCKERFILE, LAMBDA_IMAGE_HANDLER, "app.js"),
            (LAMBDA_IMAGE_DOCKERFILE_PYTHON_CHAINED, LAMBDA_IMAGE_HANDLER_PYTHON, "app.py"),
        ],
        ids=["node", "python"],
    )
    @markers.aws.validated
    def test_lambda_from_image(
        self,
        lambda_image_dockerfile,
        lambda_image_handler,
        lambda_image_handler_filename,
        create_repository,
        lambda_create_function,
        monkeypatch,
        lambda_su_role,
        cleanups,
        aws_client,
    ):
        # create image in ECR repo
        repo_name = f"r-{short_uid()}"
        repo = create_repository(repositoryName=repo_name)["repository"]
        repo_uri = repo["repositoryUri"]
        img_name = f"{repo_uri}:latest"
        cleanups.append(lambda: DOCKER_CLIENT.remove_image(image=img_name, force=True))

        folder = new_tmp_dir()
        save_file(os.path.join(folder, "Dockerfile"), lambda_image_dockerfile)
        save_file(os.path.join(folder, lambda_image_handler_filename), lambda_image_handler)
        DOCKER_CLIENT.build_image(
            folder, image_name=img_name, platform=docker_platform(Architecture.x86_64)
        )
        DOCKER_CLIENT.push_image(img_name)

        value = f"event-{short_uid()}"
        event = {"value": value}
        func_name = f"test-container-{short_uid()}"
        lambda_create_function(
            FunctionName=func_name,
            Role=lambda_su_role,
            Code={"ImageUri": img_name},
            PackageType="Image",
            Environment={"Variables": {"CUSTOM_ENV": "test"}},
        )
        aws_client.lambda_.get_waiter("function_active_v2").wait(FunctionName=func_name)

        def assert_invocation():
            result = aws_client.lambda_.invoke(
                FunctionName=func_name, Payload=to_bytes(json.dumps(event))
            )
            payload = json.load(result["Payload"])
            assert "FunctionError" not in result
            assert 200 == result["StatusCode"]
            payload_body = json.loads(payload["body"])
            assert "bar" == payload_body.get("foo")
            assert "test" == payload_body["env"].get("CUSTOM_ENV")
            assert value == payload_body["value"]

        for _ in range(2):
            assert_invocation()

    @markers.aws.validated
    def test_container_image_lambda_with_image_config(
        self,
        lambda_create_function,
        create_repository,
        lambda_su_role,
        snapshot,
        cleanups,
        aws_client,
    ):
        func_name = f"test-container-{short_uid()}"
        repo_name = func_name

        # create image in ECR repo
        repo_uri = create_repository(repositoryName=repo_name)["repository"]["repositoryUri"]
        img_name = f"{repo_uri}:latest"
        cleanups.append(lambda: DOCKER_CLIENT.remove_image(img_name, force=True))

        folder = new_tmp_dir()
        save_file(os.path.join(folder, "Dockerfile"), LAMBDA_IMAGE_DOCKERFILE_PYTHON_CUSTOM_RIC)
        save_file(os.path.join(folder, "app.py"), LAMBDA_IMAGE_HANDLER_PYTHON_CUSTOM_RIC)
        DOCKER_CLIENT.build_image(
            folder, image_name=img_name, platform=docker_platform(Architecture.x86_64)
        )
        DOCKER_CLIENT.push_image(img_name)

        image_config = {
            "EntryPoint": ["python"],
            "Command": ["app_tmp.py"],
            "WorkingDirectory": "/app1",
        }
        lambda_create_function(
            FunctionName=func_name,
            Role=lambda_su_role,
            Code={"ImageUri": img_name},
            PackageType="Image",
            ImageConfig=image_config,
        )
        aws_client.lambda_.get_waiter("function_active_v2").wait(FunctionName=func_name)
        result = aws_client.lambda_.invoke(FunctionName=func_name, Payload=b"{}")
        snapshot.match("invoke-container-result", result)

    @markers.aws.validated
    @pytest.mark.skip(
        reason="Error handling for init errors 'Runtime exited without providing a reason' not yet implemented"
    )
    # TODO implement init error behavior
    def test_container_image_lambda_with_image_config_init_timeout(
        self, lambda_create_function, create_repository, lambda_su_role, cleanups, aws_client
    ):
        func_name = f"test-container-{short_uid()}"
        repo_name = func_name

        # create image in ECR repo
        repo_uri = create_repository(repositoryName=repo_name)["repository"]["repositoryUri"]
        img_name = f"{repo_uri}:latest"
        cleanups.append(lambda: DOCKER_CLIENT.remove_image(img_name, force=True))

        folder = new_tmp_dir()
        save_file(os.path.join(folder, "Dockerfile"), LAMBDA_IMAGE_DOCKERFILE_PYTHON_CUSTOM_RIC)
        save_file(os.path.join(folder, "app.py"), LAMBDA_IMAGE_HANDLER_PYTHON)
        DOCKER_CLIENT.build_image(
            folder, image_name=img_name, platform=docker_platform(Architecture.x86_64)
        )
        DOCKER_CLIENT.push_image(img_name)

        image_config = {
            "EntryPoint": ["python"],
            "Command": ["app_tmp.py"],
            "WorkingDirectory": "/app1",
        }
        lambda_create_function(
            FunctionName=func_name,
            Role=lambda_su_role,
            Code={"ImageUri": img_name},
            PackageType="Image",
            ImageConfig=image_config,
        )
        aws_client.lambda_.get_waiter("function_active_v2").wait(FunctionName=func_name)
        result = aws_client.lambda_.invoke(FunctionName=func_name, Payload=b"{}")
        assert result["ResponseMetadata"]["HTTPStatusCode"]
        # Note: this is expected here, because the Lambda Runtime API expects a result to be received from the
        #  runtime running inside container, however, we're only running a custom Python script that does not
        #  report back a result to the Runtime API -> hence the invocation times out and returns FunctionError
        assert "FunctionError" in result
        assert "Runtime.ExitError" in to_str(result["Payload"].read())

        def get_events():
            events = get_lambda_log_events(
                func_name,
                regex_filter=r"Lambda __main__ called: /app1/app_tmp.py",
                logs_client=aws_client.logs,
            )
            assert len(events) > 0
            return events

        retry(get_events, retries=30, sleep=2)

    @markers.aws.validated
    def test_container_image_lambda_chained_invocation(
        self,
        lambda_create_function,
        create_repository,
        tmp_path,
        lambda_su_role,
        cleanups,
        aws_client,
    ):
        lambda_1_name = f"test-lambda-1-{short_uid()}"
        lambda_2_name = f"test-lambda-2-{short_uid()}"
        repo_1_name = lambda_1_name

        # create repository in ECR repo
        repo_uri = create_repository(repositoryName=repo_1_name)["repository"]["repositoryUri"]
        img_1_name = f"{repo_uri}:lambda1"
        img_2_name = f"{repo_uri}:lambda2"
        cleanups.append(lambda: DOCKER_CLIENT.remove_image(img_1_name, force=True))
        cleanups.append(lambda: DOCKER_CLIENT.remove_image(img_2_name, force=True))

        # build docker images
        folder_1 = tmp_path / lambda_1_name
        folder_2 = tmp_path / lambda_2_name
        save_file(os.path.join(folder_1, "Dockerfile"), LAMBDA_IMAGE_DOCKERFILE_PYTHON_CHAINED)
        save_file(
            os.path.join(folder_1, "app.py"),
            LAMBDA_IMAGE_HANDLER_CHAINED_INVOCATIONS_1 % lambda_2_name,
        )
        save_file(os.path.join(folder_2, "Dockerfile"), LAMBDA_IMAGE_DOCKERFILE_PYTHON_CHAINED)
        save_file(os.path.join(folder_2, "app.py"), LAMBDA_IMAGE_HANDLER_CHAINED_INVOCATIONS_2)
        DOCKER_CLIENT.build_image(
            str(folder_1), image_name=img_1_name, platform=docker_platform(Architecture.x86_64)
        )
        DOCKER_CLIENT.build_image(
            str(folder_2), image_name=img_2_name, platform=docker_platform(Architecture.x86_64)
        )
        DOCKER_CLIENT.push_image(img_1_name)
        DOCKER_CLIENT.push_image(img_2_name)

        lambda_create_function(
            FunctionName=lambda_2_name,
            Role=lambda_su_role,
            Code={"ImageUri": img_2_name},
            PackageType="Image",
        )
        lambda_create_function(
            FunctionName=lambda_1_name,
            Role=lambda_su_role,
            Code={"ImageUri": img_1_name},
            PackageType="Image",
            Timeout=10,
        )
        aws_client.lambda_.get_waiter("function_active_v2").wait(FunctionName=lambda_1_name)
        aws_client.lambda_.get_waiter("function_active_v2").wait(FunctionName=lambda_2_name)
        payload = {"first-data": 2}
        result = aws_client.lambda_.invoke(
            FunctionName=lambda_1_name, Payload=to_bytes(json.dumps(payload))
        )
        assert result["ResponseMetadata"]["HTTPStatusCode"]
        result_payload = json.load(result["Payload"])
        assert result_payload["invoke_result"] == 4


class TestLambdaLayerBehavior:
    @markers.only_on_amd64
    # TODO make / in container read only so .pyc and __pycache__ files cannot be created
    @markers.snapshot.skip_snapshot_verify(paths=["$..Payload.layer"])
    @markers.aws.validated
    def test_function_using_layer(
        self, create_lambda_function, publish_layer_version, snapshot, aws_client
    ):
        """Check general invocation with lambda layers providing python modules, including layer updates"""
        fn_name = f"func-{short_uid()}"
        layer_name = f"layer-{short_uid()}"

        # create layer
        content = get_layer_archive_content(LAYER_1_CONTENT)
        result = publish_layer_version(LayerName=layer_name, Content=content)
        layer_v1 = result["LayerVersionArn"]

        # create lambda with layer - TODO import from other test file
        create_lambda_function(
            handler_file=TEST_LAMBDA_CONTENT,
            func_name=fn_name,
            runtime=Runtime.python3_12,
            layers=[layer_v1],
        )

        # invoke function and assert result
        result = aws_client.lambda_.invoke(FunctionName=fn_name)
        snapshot.match("invocation-result-1", result)

        # update layer
        content = get_layer_archive_content(LAYER_2_CONTENT)
        result = publish_layer_version(LayerName=layer_name, Content=content)
        layer_v2 = result["LayerVersionArn"]

        # get function configuration and assert format of layers
        result = aws_client.lambda_.get_function_configuration(FunctionName=fn_name)
        layers = result["Layers"]
        assert len(layers) == 1
        assert layer_v1 == layers[0]["Arn"]

        # invoke func #2 - should still return the original result
        result = aws_client.lambda_.invoke(FunctionName=fn_name)
        snapshot.match("invocation-result-2", result)

        # update code of the lambda - check if layer persists?
        zip_file = testutil.create_lambda_archive(
            TEST_LAMBDA_CONTENT, get_content=True, runtime=Runtime.python3_12
        )
        aws_client.lambda_.update_function_code(
            FunctionName=fn_name, ZipFile=zip_file, Publish=True
        )
        aws_client.lambda_.get_waiter("function_updated_v2").wait(FunctionName=fn_name)

        # invoke func #3 - should still return the original result
        result = aws_client.lambda_.invoke(FunctionName=fn_name)
        snapshot.match("invocation-result-3", result)

        # update function config, pointing to new layer version
        result = aws_client.lambda_.update_function_configuration(
            FunctionName=fn_name, Layers=[layer_v2]
        )
        layers = result["Layers"]
        assert len(layers) == 1
        assert layer_v2 == layers[0]["Arn"]
        aws_client.lambda_.get_waiter("function_updated_v2").wait(FunctionName=fn_name)

        # invoke func #4 - should now return the new result
        result = aws_client.lambda_.invoke(FunctionName=fn_name)
        snapshot.match("invocation-result-4", result)

    @markers.aws.validated
    def test_file_permissions_with_layer(
        self, aws_client, create_lambda_function, publish_layer_version, snapshot
    ):
        """Test the file permissions (i.e., mode) when using layers, especially for files in the bin directory.
        Using a layer changes the permissions of /var/task to 755
        """
        layer_name = f"layer-{short_uid()}"
        with open(LAYER_BIN_LAYER, "rb") as file_obj:
            zip_file_content = file_obj.read()
        layer_version_arn = publish_layer_version(
            LayerName=layer_name, Content={"ZipFile": zip_file_content}
        )["LayerVersionArn"]

        func_name = f"func-{short_uid()}"
        create_lambda_function(
            func_name=func_name,
            handler_file=LAMBDA_INTROSPECT_LAYER_PYTHON,
            runtime=Runtime.python3_12,
            Layers=[layer_version_arn],
        )

        invoke_result = aws_client.lambda_.invoke(FunctionName=func_name)
        snapshot.match("invoke-file-permission-introspection", invoke_result)

    @markers.aws.validated
    def test_file_permissions_without_layer(
        self, aws_client, create_lambda_function, publish_layer_version, snapshot
    ):
        """Test the file permissions (i.e., mode) without using a layer because layers affect /var/task.
        Using no layer preserves the original file permissions of /var/task
        """
        func_name = f"func-{short_uid()}"
        create_lambda_function(
            func_name=func_name,
            handler_file=LAMBDA_INTROSPECT_LAYER_PYTHON,
            runtime=Runtime.python3_12,
        )

        invoke_result = aws_client.lambda_.invoke(FunctionName=func_name)
        snapshot.match("invoke-file-permission-introspection", invoke_result)

    @markers.aws.validated
    def test_function_using_layer_overriding_runtime(
        self, publish_layer_version, create_lambda_function, snapshot, aws_client
    ):
        """Check if function layer can override shipped python modules (in essence boto3)"""
        test_var = "test_value"
        layer_name = f"test_layer_{short_uid()}"
        function_name = f"test_function_{short_uid()}"

        # create layer, boto3 is a module per default in /var/runtime
        content = get_layer_archive_content(f'TEST_VAR="{test_var}"', "python/boto3/test.py")
        result = publish_layer_version(LayerName=layer_name, Content=content)
        layer = result["LayerVersionArn"]

        create_lambda_function(
            handler_file=TEST_LAYER_OVERRIDES_RUNTIME_CODE,
            func_name=function_name,
            runtime=Runtime.python3_12,
        )

        # invoke function and assert result
        result = aws_client.lambda_.invoke(FunctionName=function_name)
        snapshot.match("invocation-result-without-layer", result)

        # add layer
        aws_client.lambda_.update_function_configuration(FunctionName=function_name, Layers=[layer])
        aws_client.lambda_.get_waiter("function_updated_v2").wait(FunctionName=function_name)
        result = aws_client.lambda_.invoke(FunctionName=function_name)
        snapshot.match("invocation-result-with-layer", result)

    @markers.aws.only_localstack
    def test_cross_account_layer(self, aws_client, secondary_aws_client, create_lambda_function):
        """Test referencing a layer from another account.
        Applying layers is a pro feature.
        CAVEAT: Cannot test this against AWS because we cannot own other accounts.
        """
        # Create layer in other account
        # TODO: consider making this AWS-compatible by creating a new account for snapshot testing
        # see tests.aws.test_iam.TestIAMExtensions.test_get_user_without_username_as_user
        lambda_client_layer = secondary_aws_client.lambda_

        layer_name = f"layer-{short_uid()}"
        layer_file_path = "msg.txt"
        zip_file = testutil.create_lambda_archive(
            LAYER_1_CONTENT, get_content=True, runtime=Runtime.python3_12, file_name=layer_file_path
        )
        publish_layer_version_result = lambda_client_layer.publish_layer_version(
            LayerName=layer_name,
            CompatibleRuntimes=[Runtime.python3_12],
            Content={"ZipFile": zip_file},
            CompatibleArchitectures=[Architecture.x86_64],
        )
        layer_version_arn = publish_layer_version_result["LayerVersionArn"]
        layer_version_result = lambda_client_layer.get_layer_version_by_arn(Arn=layer_version_arn)
        zip_file_sha256 = to_str(base64.b64encode(hashlib.sha256(zip_file).digest()))
        assert layer_version_result["Content"]["CodeSha256"] == zip_file_sha256

        lambda_client_layer.add_layer_version_permission(
            LayerName=layer_name,
            VersionNumber=layer_version_result["Version"],
            Action="lambda:GetLayerVersion",
            Principal="*",
            StatementId="share_layer",
        )

        # Create function that references layer in other account
        function_name = f"test_function_{short_uid()}"
        create_lambda_function(
            handler_file=TEST_LAYER_OVERRIDE_LAMBDA_CONTENT,
            func_name=function_name,
            runtime=Runtime.python3_12,
            layers=[layer_version_arn],
        )

        invoke_result = aws_client.lambda_.invoke(FunctionName=function_name)
        assert invoke_result["StatusCode"] == 200
        assert "FunctionError" not in invoke_result
        payload = json.load(invoke_result["Payload"])
        assert f"/opt/{layer_file_path}" in payload["opt_contents"]

    @markers.only_on_amd64
    @markers.aws.validated
    def test_function_multiple_layers_override(
        self, publish_layer_version, create_lambda_function, snapshot, aws_client
    ):
        """Check multiple layers for a function and how they are unpacked in /opt"""
        layer_name_1 = f"test_layer_{short_uid()}"
        layer_name_2 = f"test_layer_{short_uid()}"
        function_name = f"test_function_{short_uid()}"

        layer_1_content = get_layer_archive(LAMBDA_OVERRIDE_LAYER_1_PATH)
        layer_2_content = get_layer_archive(LAMBDA_OVERRIDE_LAYER_2_PATH)
        result_1 = publish_layer_version(
            LayerName=layer_name_1, Content={"ZipFile": layer_1_content}
        )
        result_2 = publish_layer_version(
            LayerName=layer_name_2, Content={"ZipFile": layer_2_content}
        )
        layer1_arn = result_1["LayerVersionArn"]
        layer2_arn = result_2["LayerVersionArn"]

        create_lambda_function(
            handler_file=TEST_LAYER_OVERRIDE_LAMBDA_CONTENT,
            func_name=function_name,
            runtime=Runtime.python3_12,
            layers=[layer1_arn, layer2_arn],
        )

        # check if layer2 files override layer1 files
        result = aws_client.lambda_.invoke(FunctionName=function_name)
        snapshot.match("invocation-result-layer1-layer2", result)

        # check what happens if layer order is reversed
        aws_client.lambda_.update_function_configuration(
            FunctionName=function_name, Layers=[layer2_arn, layer1_arn]
        )
        aws_client.lambda_.get_waiter("function_updated_v2").wait(FunctionName=function_name)
        result = aws_client.lambda_.invoke(FunctionName=function_name)
        snapshot.match("invocation-result-layer2-layer1", result)


@pytest.mark.skip(
    reason="Skip temporarily because the public layer expired and we are working on a fix"
)
@markers.skip_offline  # these tests download external AWS layers and do not make sense offline
class TestExternalLayerDownload:
    @markers.aws.validated
    def test_external_layer_download(
        self, create_lambda_function, snapshot, aws_client, region_name
    ):
        """Test creating and updating functions with an external layer.
        The new provider supports cross-account lazy loading of an external layer into LocalStack.
        The old provider does NOT support importing the external layer into LocalStack.
        """
        snapshot.add_transformer(SortingTransformer("layer"))

        # Using lightweight layers from Klayers, a collection Python packages distributed as Lambda layers:
        # https://github.com/keithrozario/Klayers
        external_layer_1 = f"arn:aws:lambda:{region_name}:770693421928:layer:Klayers-p39-PyYAML:1"
        external_layer_2 = f"arn:aws:lambda:{region_name}:770693421928:layer:Klayers-p39-idna:2"

        function_name = f"test_function_{short_uid()}"
        create_function_response = create_lambda_function(
            handler_file=TEST_LAYER_CONTENT,
            func_name=function_name,
            runtime=Runtime.python3_9,
            Layers=[external_layer_1],
        )
        snapshot.match("create_function_external_layer", create_function_response)

        # The external layer is available in LocalStack
        layer_version_1 = aws_client.lambda_.get_layer_version_by_arn(Arn=external_layer_1)
        snapshot.match("get_layer_version_by_arn_cross_account_create", layer_version_1)

        invoke_result_1 = aws_client.lambda_.invoke(FunctionName=function_name)
        snapshot.match("invoke_external_layers_one", invoke_result_1)

        update_func_conf_response = aws_client.lambda_.update_function_configuration(
            FunctionName=function_name,
            Runtime=Runtime.python3_9,
            Description="Changed-Description",
            Layers=[external_layer_1, external_layer_2],
        )
        snapshot.match("update_function_configuration_external_layer", update_func_conf_response)

        layer_version_2 = aws_client.lambda_.get_layer_version_by_arn(Arn=external_layer_2)
        snapshot.match("get_layer_version_by_arn_cross_account_update", layer_version_2)

        aws_client.lambda_.get_waiter("function_updated_v2").wait(FunctionName=function_name)

        invoke_result_2 = aws_client.lambda_.invoke(FunctionName=function_name)
        snapshot.match("invoke_external_layers_two", invoke_result_2)

    @markers.only_on_amd64
    @markers.aws.validated
    def test_external_layer_specific(
        self, create_lambda_function, snapshot, aws_client, region_name
    ):
        """Test external layer with specific runtime and architecture dependencies.
        Using numpy layer (~64MB) from Klayers, a collection of Python libraries as Lambda layers.
        https://github.com/keithrozario/Klayers"""
        external_layer = f"arn:aws:lambda:{region_name}:770693421928:layer:Klayers-p312-numpy:4"
        function_name = f"test_function_{short_uid()}"

        create_lambda_function(
            handler_file=LAMBDA_EXTERNAL_LAYER_HANDLER,
            func_name=function_name,
            runtime=Runtime.python3_12,
            Architectures=[Architecture.x86_64],
            # Numpy layer only compatible with Python 3.12 and on x86_64
            Layers=[external_layer],
        )
        result = aws_client.lambda_.invoke(FunctionName=function_name)
        snapshot.match("invocation-result", result)

    @markers.aws.validated
    def test_external_layer_exceptions(
        self, create_lambda_function, snapshot, aws_client, region_name
    ):
        """Test exceptions upon creating and updating functions with an external layer.
        * CompatibleRuntimes are NOT validated and solely used for filtering ListLayers and ListLayerVersions:
        https://docs.aws.amazon.com/lambda/latest/dg/API_PublishLayerVersion.html#SSS-PublishLayerVersion-request-CompatibleRuntimes
        * Architectures are NOT validated and solely used for filtering
        https://docs.aws.amazon.com/lambda/latest/dg/foundation-arch.html
        """
        # TODO: detect user/role from context in _validate_layers()
        snapshot.transform.key_value("user/localstack-testing", "<user>")

        function_name = f"test_function_{short_uid()}"

        wrong_layer_region = "us-west-2"
        assert region_name != wrong_layer_region
        external_layer_wrong_region = (
            f"arn:aws:lambda:{wrong_layer_region}:770693421928:layer:Klayers-p39-PyYAML:1"
        )
        with pytest.raises(aws_client.lambda_.exceptions.ClientError) as e:
            create_lambda_function(
                handler_file=TEST_LAYER_CODE,
                func_name=function_name,
                runtime=Runtime.python3_9,
                Layers=[external_layer_wrong_region],
            )
        snapshot.match("create_function_wrong_layer_region", e.value.response)

        external_layer_doesnotexist = (
            f"arn:aws:lambda:{region_name}:770693421928:layer:doesnotexist:1"
        )
        with pytest.raises(aws_client.lambda_.exceptions.ClientError) as e:
            # Retries in fixture delay CI and trigger layer-fetcher lambda
            create_lambda_function(
                handler_file=TEST_LAYER_CODE,
                func_name=function_name,
                runtime=Runtime.python3_9,
                Layers=[external_layer_doesnotexist],
            )
        snapshot.match("create_function_layer_doesnotexist", e.value.response)

    @markers.aws.validated
    def test_external_layer_multiple_versions(
        self, create_lambda_function, snapshot, aws_client, region_name
    ):
        """Test external layer fetching with two distinct versions of the same layer. Motivated by a support issue."""
        snapshot.add_transformer(SortingTransformer("layer"))

        # Using lightweight layers from Klayers, a collection Python packages distributed as Lambda layers:
        # https://github.com/keithrozario/Klayers
        external_layer_v1 = f"arn:aws:lambda:{region_name}:770693421928:layer:Klayers-p39-PyYAML:1"
        external_layer_v2 = f"arn:aws:lambda:{region_name}:770693421928:layer:Klayers-p39-PyYAML:2"

        function_name = f"test_function_{short_uid()}"
        create_function_response_1 = create_lambda_function(
            handler_file=TEST_LAYER_CONTENT,
            func_name=function_name,
            runtime=Runtime.python3_9,
            Layers=[external_layer_v1],
        )
        snapshot.match("create_function_external_layer_v1", create_function_response_1)

        function_name = f"test_function_{short_uid()}"
        create_function_response_2 = create_lambda_function(
            handler_file=TEST_LAYER_CONTENT,
            func_name=function_name,
            runtime=Runtime.python3_9,
            Layers=[external_layer_v2],
        )
        snapshot.match("create_function_external_layer_v2", create_function_response_2)


class TestLayerHotReloading:
    @markers.aws.only_localstack
    def test_layer_only_hot_reloading(
        self,
        create_lambda_function_aws,
        publish_layer_version,
        lambda_su_role,
        cleanups,
        aws_client,
    ):
        """Test hot reloading of lambda code"""
        function_name = f"test-{short_uid()}"
        layer_name = f"test-hot-reloading-layer-{short_uid()}"
        hot_reloading_bucket = config.BUCKET_MARKER_LOCAL
        tmp_path = config.dirs.mounted_tmp
        hot_reloading_dir_path = os.path.join(tmp_path, f"hot-reload-{short_uid()}")
        mkdir(hot_reloading_dir_path)
        cleanups.append(lambda: rm_rf(hot_reloading_dir_path))
        hot_reloading_python_path = os.path.join(hot_reloading_dir_path, "python")
        mkdir(hot_reloading_python_path)
        layer_filename = "testlib.py"
        with open(os.path.join(hot_reloading_python_path, layer_filename), mode="wt") as f:
            f.write(LAMBDA_HOT_RELOADING_LAYER_TESTLIB)

        mount_path = get_host_path_for_path_in_docker(hot_reloading_dir_path)
        result = publish_layer_version(
            LayerName=layer_name, Content={"S3Bucket": hot_reloading_bucket, "S3Key": mount_path}
        )
        layer_arn = result["LayerVersionArn"]

        zip_file = testutil.create_lambda_archive(
            LAMBDA_HOT_RELOADING_LAYER_FUNCTION, get_content=True, runtime=Runtime.python3_12
        )
        create_lambda_function_aws(
            FunctionName=function_name,
            Handler="handler.handler",
            Code={"ZipFile": zip_file},
            Role=lambda_su_role,
            Runtime=Runtime.python3_12,
            Layers=[layer_arn],
        )
        response = aws_client.lambda_.invoke(FunctionName=function_name, Payload=b"{}")
        response_dict = json.load(response["Payload"])
        assert response_dict["counter"] == 1
        assert response_dict["constant"] == "value1"
        assert response_dict["layer_constant"] == "value1"
        response = aws_client.lambda_.invoke(FunctionName=function_name, Payload=b"{}")
        response_dict = json.load(response["Payload"])
        assert response_dict["counter"] == 2
        assert response_dict["constant"] == "value1"
        assert response_dict["layer_constant"] == "value1"

        with open(os.path.join(hot_reloading_python_path, layer_filename), mode="wt") as f:
            f.write(LAMBDA_HOT_RELOADING_LAYER_TESTLIB.replace("value1", "value2"))
        # we have to sleep here, since the hot reloading is debounced with 500ms
        time.sleep(0.6)
        response = aws_client.lambda_.invoke(FunctionName=function_name, Payload=b"{}")
        response_dict = json.load(response["Payload"])
        assert response_dict["counter"] == 1
        assert response_dict["constant"] == "value1"
        assert response_dict["layer_constant"] == "value2"
        response = aws_client.lambda_.invoke(FunctionName=function_name, Payload=b"{}")
        response_dict = json.load(response["Payload"])
        assert response_dict["counter"] == 2
        assert response_dict["constant"] == "value1"
        assert response_dict["layer_constant"] == "value2"

    @markers.aws.only_localstack
    def test_layer_and_function_hot_reloading(
        self,
        create_lambda_function_aws,
        publish_layer_version,
        lambda_su_role,
        cleanups,
        aws_client,
    ):
        """Test hot reloading of lambda code"""
        function_name = f"test-hot-reloading-function-{short_uid()}"
        layer_name = f"test-hot-reloading-layer-{short_uid()}"
        hot_reloading_bucket = config.BUCKET_MARKER_LOCAL
        tmp_path = config.dirs.mounted_tmp
        # layer paths
        hot_reloading_layer_path = os.path.join(tmp_path, f"hot-layer-{short_uid()}")
        mkdir(hot_reloading_layer_path)
        cleanups.append(lambda: rm_rf(hot_reloading_layer_path))
        # function paths
        hot_reloading_function_path = os.path.join(tmp_path, f"hot-function-{short_uid()}")
        mkdir(hot_reloading_function_path)
        cleanups.append(lambda: rm_rf(hot_reloading_function_path))

        # create hot reloading layer
        hot_reloading_layer_python_path = os.path.join(hot_reloading_layer_path, "python")
        mkdir(hot_reloading_layer_python_path)
        layer_filename = "testlib.py"
        with open(os.path.join(hot_reloading_layer_python_path, layer_filename), mode="wt") as f:
            f.write(LAMBDA_HOT_RELOADING_LAYER_TESTLIB)

        layer_mount_path = get_host_path_for_path_in_docker(hot_reloading_layer_path)
        result = publish_layer_version(
            LayerName=layer_name,
            Content={"S3Bucket": hot_reloading_bucket, "S3Key": layer_mount_path},
        )
        layer_arn = result["LayerVersionArn"]

        # create hot reloading function
        function_filename = "handler.py"
        with open(os.path.join(hot_reloading_function_path, function_filename), mode="wt") as f:
            f.write(LAMBDA_HOT_RELOADING_LAYER_FUNCTION)
        function_mount_path = get_host_path_for_path_in_docker(hot_reloading_function_path)

        create_lambda_function_aws(
            FunctionName=function_name,
            Handler="handler.handler",
            Code={"S3Bucket": hot_reloading_bucket, "S3Key": function_mount_path},
            Role=lambda_su_role,
            Runtime=Runtime.python3_12,
            Layers=[layer_arn],
        )
        response = aws_client.lambda_.invoke(FunctionName=function_name, Payload=b"{}")
        response_dict = json.load(response["Payload"])
        assert response_dict["counter"] == 1
        assert response_dict["constant"] == "value1"
        assert response_dict["layer_constant"] == "value1"
        response = aws_client.lambda_.invoke(FunctionName=function_name, Payload=b"{}")
        response_dict = json.load(response["Payload"])
        assert response_dict["counter"] == 2
        assert response_dict["constant"] == "value1"
        assert response_dict["layer_constant"] == "value1"

        # change layer and see if it reloads
        with open(os.path.join(hot_reloading_layer_python_path, layer_filename), mode="wt") as f:
            f.write(LAMBDA_HOT_RELOADING_LAYER_TESTLIB.replace("value1", "value2"))
        # we have to sleep here, since the hot reloading is debounced with 500ms
        time.sleep(0.6)
        response = aws_client.lambda_.invoke(FunctionName=function_name, Payload=b"{}")
        response_dict = json.load(response["Payload"])
        assert response_dict["counter"] == 1
        assert response_dict["constant"] == "value1"
        assert response_dict["layer_constant"] == "value2"
        response = aws_client.lambda_.invoke(FunctionName=function_name, Payload=b"{}")
        response_dict = json.load(response["Payload"])
        assert response_dict["counter"] == 2
        assert response_dict["constant"] == "value1"
        assert response_dict["layer_constant"] == "value2"

        # change function and see if it reloads
        with open(os.path.join(hot_reloading_function_path, function_filename), mode="wt") as f:
            f.write(LAMBDA_HOT_RELOADING_LAYER_FUNCTION.replace("value1", "value2"))
        # we have to sleep here, since the hot reloading is debounced with 500ms
        time.sleep(0.6)
        response = aws_client.lambda_.invoke(FunctionName=function_name, Payload=b"{}")
        response_dict = json.load(response["Payload"])
        assert response_dict["counter"] == 1
        assert response_dict["constant"] == "value2"
        assert response_dict["layer_constant"] == "value2"
        response = aws_client.lambda_.invoke(FunctionName=function_name, Payload=b"{}")
        response_dict = json.load(response["Payload"])
        assert response_dict["counter"] == 2
        assert response_dict["constant"] == "value2"
        assert response_dict["layer_constant"] == "value2"

    @markers.aws.only_localstack
    def test_multiple_hot_reloading_layers_fail(
        self,
        create_lambda_function_aws,
        publish_layer_version,
        lambda_su_role,
        cleanups,
        aws_client,
    ):
        """Test hot reloading of lambda code"""
        function_name = f"test-{short_uid()}"
        layer_1_name = f"test-hot-reloading-layer-{short_uid()}"
        layer_2_name = f"test_layer_{short_uid()}"
        hot_reloading_bucket = config.BUCKET_MARKER_LOCAL
        tmp_path = config.dirs.mounted_tmp
        # layer paths
        hot_reloading_layer_path = os.path.join(tmp_path, f"hot-layer-{short_uid()}")
        mkdir(hot_reloading_layer_path)
        cleanups.append(lambda: rm_rf(hot_reloading_layer_path))

        # create hot reloading layer
        hot_reloading_layer_python_path = os.path.join(hot_reloading_layer_path, "python")
        mkdir(hot_reloading_layer_python_path)
        layer_filename = "testlib.py"
        with open(os.path.join(hot_reloading_layer_python_path, layer_filename), mode="wt") as f:
            f.write(LAMBDA_HOT_RELOADING_LAYER_TESTLIB)

        layer_mount_path = get_host_path_for_path_in_docker(hot_reloading_layer_path)
        result = publish_layer_version(
            LayerName=layer_1_name,
            Content={"S3Bucket": hot_reloading_bucket, "S3Key": layer_mount_path},
        )
        layer_1_arn = result["LayerVersionArn"]

        # create normal additional layer

        layer_2_content = get_layer_archive(LAMBDA_OVERRIDE_LAYER_1_PATH)
        result_2 = publish_layer_version(
            LayerName=layer_2_name, Content={"ZipFile": layer_2_content}
        )
        layer_2_arn = result_2["LayerVersionArn"]

        zip_file = testutil.create_lambda_archive(
            LAMBDA_HOT_RELOADING_LAYER_FUNCTION, get_content=True, runtime=Runtime.python3_12
        )
        create_lambda_function_aws(
            FunctionName=function_name,
            Handler="handler.handler",
            Code={"ZipFile": zip_file},
            Role=lambda_su_role,
            Runtime=Runtime.python3_12,
            Layers=[layer_1_arn, layer_2_arn],
        )
        with pytest.raises(WaiterError):
            aws_client.lambda_.get_waiter("function_active_v2").wait(FunctionName=function_name)

        get_function_result = aws_client.lambda_.get_function(FunctionName=function_name)
        assert get_function_result["Configuration"]["State"] == "Failed"


def get_layer_archive_content(content, path="python/a/b/c/mylib.py"):
    zip_file = testutil.create_lambda_archive(
        content, get_content=True, runtime=Runtime.python3_12, file_name=path
    )
    content = {"ZipFile": zip_file}
    return content


def get_layer_archive(target_path: str) -> bytes:
    """
    Zips the target path and returns the bytes of the zip file
    :param target_path: Target path

    :return: Zip file bytes
    """
    with tempfile.NamedTemporaryFile(mode="rb") as file:
        create_zip_file_python(target_path, file.name)
        file.flush()
        file.seek(0)
        return file.read()
