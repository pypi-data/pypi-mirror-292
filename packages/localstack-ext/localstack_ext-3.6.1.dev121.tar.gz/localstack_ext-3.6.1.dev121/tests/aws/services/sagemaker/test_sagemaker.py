import base64
import json
import logging
import os.path
import random
import time

import boto3
import numpy as np
import pytest
from localstack.constants import AWS_REGION_US_EAST_1
from localstack.pro.core.aws.api.sagemaker import (
    ProductionVariantInstanceType,
)
from localstack.testing.aws.util import is_aws_cloud
from localstack.testing.pytest import markers
from localstack.testing.snapshots.transformer_utility import TransformerUtility
from localstack.utils.container_utils.container_client import DockerPlatform
from localstack.utils.docker_utils import DOCKER_CLIENT
from localstack.utils.files import new_tmp_file
from localstack.utils.http import download
from localstack.utils.platform import Arch, get_arch
from localstack.utils.strings import short_uid, to_str
from localstack.utils.sync import wait_until
from localstack_snapshot.snapshots.transformer import JsonpathTransformer

from tests.aws.fixtures import skip_in_ci
from tests.aws.services.sagemaker.mnist_utils import get_mnist_data, normalize

LOG = logging.getLogger(__name__)

REPO = "https://github.com/awslabs/amazon-sagemaker-examples"
COMMIT = "490034eeaf3f9933abdb8553a51d4b146d772182"
MNIST_SCRIPT_URL = f"{REPO}/raw/{COMMIT}/sagemaker-python-sdk/tensorflow_script_mode_training_and_serving/mnist-2.py"

TRAINING_BUCKET = f"sagemaker-sample-data-{AWS_REGION_US_EAST_1}"
DIR = "tensorflow/mnist"

TRAINING_DATA_URI = f"s3://{TRAINING_BUCKET}/{DIR}"
FILES_NAMES = ["eval_data.npy", "eval_labels.npy", "train_data.npy", "train_labels.npy"]
FILES_TO_COPY = [f"{DIR}/{file}" for file in FILES_NAMES]

base_dir = os.path.dirname(os.path.abspath(__file__))
CONTAINER_IMAGE = "763104351884.dkr.ecr.us-east-1.amazonaws.com/pytorch-inference:1.5.0-cpu-py3"
CUSTOM_CONTAINER_IMAGE = "localstack/sagemaker-dummy-byom"
MODEL_TAR_FILE = f"{base_dir}/sagemaker/data/model.tar.gz"
EXECUTION_ROLE_ARN = "arn:aws:iam::0000000000000:role/sagemaker-role"

TRANSFORMERS = [
    TransformerUtility.key_value("ModelName"),
    TransformerUtility.key_value("EndpointConfigName"),
    TransformerUtility.key_value("EndpointName"),
    TransformerUtility.key_value("ModelArn"),
    TransformerUtility.key_value("EndpointConfigArn"),
    TransformerUtility.key_value("EndpointArn"),
    TransformerUtility.key_value("ModelDataUrl"),
    TransformerUtility.key_value("ExecutionRoleArn"),
    TransformerUtility.key_value("PrimaryContainer"),
    TransformerUtility.key_value("Image"),
    TransformerUtility.key_value("ModelDataUrl"),
    JsonpathTransformer("$..ProductionVariants..ResolvedImage", "resolved-image"),
    JsonpathTransformer("$..ProductionVariants..SpecifiedImage", "specified-image"),
]


@pytest.fixture
def sagemaker_execution_role(aws_client):
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"Service": "sagemaker.amazonaws.com"},
                "Action": "sts:AssumeRole",
            }
        ],
    }
    permission_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": ["s3:GetObject", "s3:PutObject"],
                "Resource": ["arn:aws:s3:::*"],
            },
            {
                "Effect": "Allow",
                "Action": [
                    "ecr:ReplicateImage",
                    "ecr:GetAuthorizationToken",
                    "ecr:BatchCheckLayerAvailability",
                    "ecr:GetDownloadUrlForLayer",
                    "ecr:BatchGetImage",
                ],
                "Resource": ["*"],
            },
        ],
    }
    role_name = "sagemaker-execution-role"
    try:
        response = aws_client.iam.get_role(RoleName=role_name)
        role_arn = response["Role"]["Arn"]
        LOG.info(f"Role {role_name} already exists with ARN {role_arn}")
        return role_arn
    except aws_client.iam.exceptions.NoSuchEntityException:
        LOG.info(f"Role {role_name} does not exist. Creating...")

    response = aws_client.iam.create_role(
        RoleName=role_name,
        AssumeRolePolicyDocument=json.dumps(trust_policy),
    )
    role_arn = response["Role"]["Arn"]
    aws_client.iam.put_role_policy(
        RoleName=role_name,
        PolicyName=f"{role_name}-policy",
        PolicyDocument=json.dumps(permission_policy),
    )
    LOG.info(f"Created role {role_name} with ARN {role_arn}. Waiting for propagation...")
    if is_aws_cloud():
        time.sleep(120)
    LOG.info("Finished waiting for role propagation.")
    return role_arn


@pytest.fixture
def mirror_s3_bucket(s3_create_bucket, aws_client):
    def _mirror_s3_bucket(bucket_name, file_paths):
        s3_create_bucket(Bucket=bucket_name)

        for file_path in file_paths:
            tmp_file = new_tmp_file()
            download(f"http://{bucket_name}.s3.amazonaws.com/{file_path}", tmp_file)
            aws_client.s3.upload_file(Filename=tmp_file, Bucket=bucket_name, Key=file_path)

    yield _mirror_s3_bucket


@pytest.fixture
def sagemaker_create_model(aws_client):
    models = []

    def _model_exists(model_name):
        try:
            aws_client.sagemaker.describe_model(ModelName=model_name)
            return True
        except aws_client.sagemaker.exceptions.ResourceNotFound:
            return False

    def _create_model(**kwargs):
        response = aws_client.sagemaker.create_model(**kwargs)
        wait_until(lambda: _model_exists(kwargs["ModelName"]))
        models.append(kwargs["ModelName"])
        return response["ModelArn"]

    yield _create_model

    for model in models:
        aws_client.sagemaker.delete_model(ModelName=model)


@pytest.fixture
def sagemaker_create_endpoint_config(aws_client):
    endpoint_configs = []

    def _endpoint_config_exists(config_name):
        try:
            aws_client.sagemaker.describe_endpoint_config(EndpointConfigName=config_name)
            return True
        except aws_client.sagemaker.exceptions.ResourceNotFound:
            return False

    def _create_endpoint_config(**kwargs):
        response = aws_client.sagemaker.create_endpoint_config(**kwargs)
        wait_until(lambda: _endpoint_config_exists(kwargs["EndpointConfigName"]))
        endpoint_configs.append(kwargs["EndpointConfigName"])
        return response["EndpointConfigArn"]

    yield _create_endpoint_config

    for config in endpoint_configs:
        aws_client.sagemaker.delete_endpoint_config(EndpointConfigName=config)


@pytest.fixture
def sagemaker_create_endpoint(aws_client):
    endpoints = []

    def _endpoint_exists(endpoint_name):
        try:
            aws_client.sagemaker.describe_endpoint(EndpointName=endpoint_name)
            return True
        except aws_client.sagemaker.exceptions.ResourceNotFound:
            return False

    def _create_endpoint(**kwargs):
        response = aws_client.sagemaker.create_endpoint(**kwargs)
        wait_until(lambda: _endpoint_exists(kwargs["EndpointName"]))
        endpoints.append(kwargs["EndpointName"])
        return response["EndpointArn"]

    yield _create_endpoint

    for endpoint in endpoints:
        aws_client.sagemaker.delete_endpoint(EndpointName=endpoint)


class TestSagemaker:
    # FIXME look into the latest sagemaker (+python sdk) features for local execution
    @pytest.mark.skip
    @markers.aws.unknown
    def test_train_tensorflow(self, mirror_s3_bucket, aws_client):
        try:
            from tests.aws.services.sagemaker import TensorFlow

            from .services import sagemaker

        except Exception as e:
            pytest.skip(f"TensorFlow/SageMaker libs not available - skipping test: {e}")
            return

        response = aws_client.iam.create_role(RoleName="r1", AssumeRolePolicyDocument="{}")
        role_arn = response["Role"]["Arn"]
        sagemaker_session = sagemaker.LocalSession(
            boto_session=boto3.Session(),
            s3_endpoint_url="http://localhost:4566",
        )
        mirror_s3_bucket(TRAINING_BUCKET, FILES_TO_COPY)

        mnist_script = new_tmp_file()
        download(MNIST_SCRIPT_URL, mnist_script)

        mnist_estimator = TensorFlow(
            entry_point=mnist_script,
            role=role_arn,
            framework_version="2.8.0",
            py_version="py39",
            sagemaker_session=sagemaker_session,
            instance_count=1,
            instance_type="local",
        )
        mnist_estimator.fit(TRAINING_DATA_URI, logs=False)

    # skip in ci to avoid big image pull
    @skip_in_ci
    @markers.aws.unknown
    def test_model_deployment_workflow(self, s3_create_bucket, aws_client):
        bucket = f"model-bucket-{short_uid()}"
        model = f"model-{short_uid()}"
        ep_config = f"endpoint-config-{short_uid()}"
        endpoint = f"endpoint-{short_uid()}"
        # create Bucket for model storage
        s3_create_bucket(Bucket=bucket)

        # put model tarfile into bucket
        aws_client.s3.upload_file(MODEL_TAR_FILE, bucket, "model.tar.gz")

        # create model and endpoint
        aws_client.sagemaker.create_model(
            ModelName=model,
            ExecutionRoleArn=EXECUTION_ROLE_ARN,
            PrimaryContainer={
                "Image": CONTAINER_IMAGE,
                "ModelDataUrl": f"s3://{bucket}/model.tar.gz",
            },
        )
        aws_client.sagemaker.create_endpoint_config(
            EndpointConfigName=ep_config,
            ProductionVariants=[
                {
                    "VariantName": short_uid(),
                    "ModelName": model,
                    "InitialInstanceCount": 1,
                    "InstanceType": "ml.m5.large",
                }
            ],
        )
        aws_client.sagemaker.create_endpoint(EndpointName=endpoint, EndpointConfigName=ep_config)

        # get input dir
        sample_size = 3
        X, Y = get_mnist_data(train=False)
        mask = random.sample(range(X.shape[0]), sample_size)
        samples = X[mask]
        samples = normalize(samples.astype(np.float32), axis=(1, 2))
        inputs = {"inputs": np.expand_dims(samples, axis=1).tolist()}
        response = aws_client.sagemaker_runtime.invoke_endpoint(
            EndpointName=endpoint,
            Body=json.dumps(inputs),
            Accept="application/json",
            ContentType="application/json",
        )
        outputs = json.loads(response["Body"].read())
        predictions = np.argmax(np.array(outputs, dtype=np.float32), axis=1).tolist()
        assert len(predictions) == sample_size

    @markers.aws.validated
    @pytest.mark.skip_store_check(reason="cannot pickle 'socket' object")
    def test_custom_model_deployment(
        self,
        snapshot,
        aws_client,
        sagemaker_execution_role,
        sagemaker_create_model,
        sagemaker_create_endpoint_config,
        sagemaker_create_endpoint,
        create_repository,
    ):
        snapshot.add_transformer(TRANSFORMERS)

        # pull pre-built image
        container_client = DOCKER_CLIENT

        match get_arch():
            case Arch.amd64:
                container_client.pull_image(
                    CUSTOM_CONTAINER_IMAGE, platform=DockerPlatform.linux_amd64
                )
            case Arch.arm64:
                container_client.pull_image(
                    CUSTOM_CONTAINER_IMAGE, platform=DockerPlatform.linux_arm64
                )

        # create ECR repository for image
        repository_name = f"sagemaker-dummy-byom-{short_uid()}"
        try:
            repositories = aws_client.ecr.describe_repositories(repositoryNames=[repository_name])
            repository = repositories["repositories"][0]
        except aws_client.ecr.exceptions.RepositoryNotFoundException:
            repository = create_repository(repositoryName=repository_name)["repository"]
        repository_uri = repository["repositoryUri"]

        # login to ECR and push image
        auth_data = aws_client.ecr.get_authorization_token()["authorizationData"][0]
        token = auth_data["authorizationToken"]
        username, password = to_str(base64.b64decode(token)).split(":")
        container_client.login(username, password, auth_data["proxyEndpoint"])
        container_client.tag_image(CUSTOM_CONTAINER_IMAGE, repository_uri)
        container_client.push_image(repository_uri)

        # create model, endpoint config and endpoint
        model = f"model-{short_uid()}"
        ep_config = f"endpoint-config-{short_uid()}"
        endpoint = f"endpoint-{short_uid()}"

        sagemaker_create_model(
            ModelName=model,
            ExecutionRoleArn=sagemaker_execution_role,
            PrimaryContainer={"Image": repository_uri, "Environment": {"FOO": "bar"}},
        )

        match get_arch():
            case Arch.arm64:
                instance_type = ProductionVariantInstanceType.ml_c7g_large
            case Arch.amd64:
                instance_type = ProductionVariantInstanceType.ml_m5_large
            case _:
                instance_type = ProductionVariantInstanceType.ml_m5_large

        sagemaker_create_endpoint_config(
            EndpointConfigName=ep_config,
            ProductionVariants=[
                {
                    "ModelName": model,
                    "VariantName": "AllTraffic",
                    "InitialInstanceCount": 1,
                    "InitialVariantWeight": 1,
                    "InstanceType": instance_type,
                }
            ],
        )

        sagemaker_create_endpoint(EndpointName=endpoint, EndpointConfigName=ep_config)

        endpoint_description = aws_client.sagemaker.describe_endpoint(EndpointName=endpoint)
        snapshot.match("endpoint_after_creation", endpoint_description)

        # wait for endpoint to be in service
        def _endpoint_in_service():
            response = aws_client.sagemaker.describe_endpoint(EndpointName=endpoint)
            return response["EndpointStatus"] == "InService"

        wait_until(_endpoint_in_service)

        endpoint_description = aws_client.sagemaker.describe_endpoint(EndpointName=endpoint)
        snapshot.match("endpoint_in_service", endpoint_description)

        # invoke endpoint
        invocation_result = aws_client.sagemaker_runtime.invoke_endpoint(
            EndpointName=endpoint,
            Body=json.dumps({"input": 1}),
            ContentType="application/json",
        )
        snapshot.match("invocation_result", invocation_result)

    @markers.aws.validated
    def test_unknown_endpoint(self, aws_client, snapshot):
        try:
            response = aws_client.sagemaker_runtime.invoke_endpoint(
                EndpointName="unknown-endpoint",
                Body=json.dumps({"input": 1}),
                ContentType="application/json",
            )
        except aws_client.sagemaker_runtime.exceptions.ValidationError as e:
            response = e.response
        snapshot.match("unknown_endpoint_response", response)
