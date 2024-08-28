"""
TODO: basic tests for provisioned & reserved concurrency when they have been implemented
"""

import json
import os

import pytest
from localstack.aws.api.dynamodb import BillingMode
from localstack.aws.api.lambda_ import Runtime
from localstack.testing.aws.lambda_utils import concurrency_update_done
from localstack.utils import testutil
from localstack.utils.container_utils.container_client import DockerPlatform
from localstack.utils.docker_utils import DOCKER_CLIENT
from localstack.utils.http import safe_requests
from localstack.utils.strings import short_uid, to_str
from localstack.utils.sync import wait_until

TEST_LAMBDA_CODE = """
def handler(event, context):
    return {"event": event, "greetings": "Hello LocalStack"}
"""

THIS_FOLDER = os.path.dirname(__file__)

TEST_LAMBDA_INVOCATION_TYPE = os.path.join(THIS_FOLDER, "functions/lambda_invocation_type.py")
TEST_LAMBDA_ECHO_PATH = os.path.join(THIS_FOLDER, "functions/echo.zip")
TEST_LAMBDA_LAYERTEST_PATH = os.path.join(THIS_FOLDER, "functions/layertest.zip")
TEST_LAMBDA_OPTCONTENT_PATH = os.path.join(THIS_FOLDER, "functions/optcontent.zip")
TEST_LAMBDA_CODEIMPORT_LAYER_PATH = os.path.join(THIS_FOLDER, "layers/codeimport.zip")

ASSUME_ROLE_POLICY = {
    "Version": "2012-10-17",
    "Statement": {
        "Effect": "Allow",
        "Principal": {"Service": "lambda.amazonaws.com"},
        "Action": "sts:AssumeRole",
    },
}


@pytest.fixture(autouse=True)
def lambda_persistence_snapshot(snapshot):
    snapshot.add_transformer(
        snapshot.transform.key_value("Location", "code-location", reference_replacement=False)
    )


def test_lambda_invoke(persistence_validations, snapshot, aws_client):
    function_name = f"test-function-{short_uid()}"

    testutil.create_lambda_function(
        func_name=function_name, handler_file=TEST_LAMBDA_CODE, client=aws_client.lambda_
    )

    def validate():
        aws_client.lambda_.get_waiter("function_active_v2").wait(FunctionName=function_name)

        function = aws_client.lambda_.get_function(FunctionName=function_name)
        snapshot.match("get_function", function)

        invoke = aws_client.lambda_.invoke(FunctionName=function_name)
        assert "FunctionError" not in invoke
        snapshot.match("invoke", invoke)

    persistence_validations.register(validate)


def test_lambda_crud(persistence_validations, snapshot, aws_client):
    fn_name = f"test-fn-{short_uid()}"
    role_name = f"test-role-{short_uid()}"
    snapshot.add_transformer(
        snapshot.transform.key_value("Location", "code-location", reference_replacement=True)
    )

    role = aws_client.iam.create_role(
        RoleName=role_name, AssumeRolePolicyDocument=json.dumps(ASSUME_ROLE_POLICY)
    )
    with open(TEST_LAMBDA_ECHO_PATH, "rb") as f:
        aws_client.lambda_.create_function(
            FunctionName=fn_name,
            Runtime=Runtime.python3_12,
            Handler="index.handler",
            Role=role["Role"]["Arn"],
            Code={"ZipFile": f.read()},
        )

    def do_assert():
        aws_client.lambda_.get_waiter("function_active_v2").wait(FunctionName=fn_name)
        snapshot.match("get_fn", aws_client.lambda_.get_function(FunctionName=fn_name))

    persistence_validations.register(do_assert)


def test_lambda_persistence_event_source_mapping_sqs(persistence_validations, snapshot, aws_client):
    queue_name = f"test-esm-queue-{short_uid()}"
    fn_name = f"test-esm-fn-{short_uid()}"
    role_name = f"test-esm-role-{short_uid()}"

    queue_url = aws_client.sqs.create_queue(QueueName=queue_name)["QueueUrl"]
    queue_arn = aws_client.sqs.get_queue_attributes(
        QueueUrl=queue_url, AttributeNames=["QueueArn"]
    )["Attributes"]["QueueArn"]

    role = aws_client.iam.create_role(
        RoleName=role_name, AssumeRolePolicyDocument=json.dumps(ASSUME_ROLE_POLICY)
    )
    with open(TEST_LAMBDA_ECHO_PATH, "rb") as f:
        aws_client.lambda_.create_function(
            FunctionName=fn_name,
            Runtime=Runtime.python3_12,
            Handler="index.handler",
            Role=role["Role"]["Arn"],
            Code={"ZipFile": f.read()},
        )
    aws_client.lambda_.get_waiter("function_active_v2").wait(FunctionName=fn_name)
    esm_uuid = aws_client.lambda_.create_event_source_mapping(
        FunctionName=fn_name, EventSourceArn=queue_arn
    )["UUID"]
    # TODO: should wait for event source mapping to be active (not relevant in the current implementation)

    def validate_esm_async_invoke():
        aws_client.lambda_.get_waiter("function_active_v2").wait(FunctionName=fn_name)
        snapshot.match("get_fn", aws_client.lambda_.get_function(FunctionName=fn_name))
        snapshot.match("get_esm", aws_client.lambda_.get_event_source_mapping(UUID=esm_uuid))

        verification_token = f"msg-verification-token-{short_uid()}"
        aws_client.sqs.send_message(QueueUrl=queue_url, MessageBody=verification_token)

        def check_logs_for_token():
            events = aws_client.logs.filter_log_events(logGroupName=f"/aws/lambda/{fn_name}")
            messages_with_token = [
                e for e in events["events"] if verification_token in e["message"]
            ]
            return len(messages_with_token) > 0

        assert wait_until(check_logs_for_token, strategy="static", _max_wait=10)

    persistence_validations.register(validate_esm_async_invoke)


@pytest.mark.skip(reason="Persistence support for dynamodb streams missing")
def test_lambda_persistence_event_source_mapping_dynamodb(
    persistence_validations, snapshot, aws_client
):
    fn_name = f"test-esm-fn-{short_uid()}"
    role_name = f"test-esm-role-{short_uid()}"
    table_name = f"test-esm-table-{short_uid()}"

    table = aws_client.dynamodb.create_table(
        TableName=table_name,
        StreamSpecification={"StreamEnabled": True, "StreamViewType": "NEW_AND_OLD_IMAGES"},
        AttributeDefinitions=[
            {
                "AttributeName": "id",
                "AttributeType": "S",
            }
        ],
        KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
        BillingMode=BillingMode.PAY_PER_REQUEST,
    )
    stream_arn = table["TableDescription"]["LatestStreamArn"]

    role = aws_client.iam.create_role(
        RoleName=role_name, AssumeRolePolicyDocument=json.dumps(ASSUME_ROLE_POLICY)
    )

    with open(TEST_LAMBDA_ECHO_PATH, "rb") as f:
        aws_client.lambda_.create_function(
            FunctionName=fn_name,
            Runtime=Runtime.python3_12,
            Handler="index.handler",
            Role=role["Role"]["Arn"],
            Code={"ZipFile": f.read()},
        )
    aws_client.lambda_.get_waiter("function_active_v2").wait(FunctionName=fn_name)
    aws_client.dynamodb.get_waiter("table_exists").wait(TableName=table_name)

    esm_uuid = aws_client.lambda_.create_event_source_mapping(
        FunctionName=fn_name,
        EventSourceArn=stream_arn,
        StartingPosition="LATEST",
    )["UUID"]
    # TODO: should wait for event source mapping to be active (not relevant in the current implementation)

    def validate_esm_async_invoke():
        aws_client.dynamodb.get_waiter("table_exists").wait(TableName=table_name)
        aws_client.lambda_.get_waiter("function_active_v2").wait(FunctionName=fn_name)
        snapshot.match("get_fn", aws_client.lambda_.get_function(FunctionName=fn_name))
        snapshot.match("get_esm", aws_client.lambda_.get_event_source_mapping(UUID=esm_uuid))

        verification_token = f"msg-verification-token-{short_uid()}"
        aws_client.dynamodb.put_item(
            TableName=table_name,
            Item={
                "id": {"S": verification_token},
            },
        )

        def check_logs_for_token():
            events = aws_client.logs.filter_log_events(logGroupName=f"/aws/lambda/{fn_name}")
            messages_with_token = [
                e for e in events["events"] if verification_token in e["message"]
            ]
            return len(messages_with_token) > 0

        assert wait_until(check_logs_for_token, strategy="linear", _max_wait=10)

    persistence_validations.register(validate_esm_async_invoke)


def test_lambda_persistence_function_url(persistence_validations, snapshot, aws_client):
    fn_name = f"test-esm-fn-{short_uid()}"
    role_name = f"test-esm-role-{short_uid()}"

    role = aws_client.iam.create_role(
        RoleName=role_name, AssumeRolePolicyDocument=json.dumps(ASSUME_ROLE_POLICY)
    )
    with open(TEST_LAMBDA_ECHO_PATH, "rb") as f:
        aws_client.lambda_.create_function(
            FunctionName=fn_name,
            Runtime=Runtime.python3_12,
            Handler="index.handler",
            Role=role["Role"]["Arn"],
            Code={"ZipFile": f.read()},
        )
    aws_client.lambda_.get_waiter("function_active_v2").wait(FunctionName=fn_name)
    url_config = aws_client.lambda_.create_function_url_config(
        FunctionName=fn_name, AuthType="NONE"
    )

    aws_client.lambda_.add_permission(
        FunctionName=fn_name,
        StatementId="urlPermission",
        Action="lambda:InvokeFunctionUrl",
        Principal="*",
        FunctionUrlAuthType="NONE",
    )

    def validate_url_request():
        aws_client.lambda_.get_waiter("function_active_v2").wait(FunctionName=fn_name)
        snapshot.match("get_fn", aws_client.lambda_.get_function(FunctionName=fn_name))
        snapshot.match(
            "get_fn_url_config", aws_client.lambda_.get_function_url_config(FunctionName=fn_name)
        )
        snapshot.match("get_fn_policy", aws_client.lambda_.get_policy(FunctionName=fn_name))

        url = f"{url_config['FunctionUrl']}custom_path/extend?test_param=test_value"
        result = safe_requests.post(url, data=b"{'key':'value'}")
        assert result.ok
        snapshot.match(
            "lambda_url_invocation",
            {
                "statuscode": result.status_code,
                "headers": {
                    "Content-Type": result.headers["Content-Type"],
                    "Content-Length": result.headers["Content-Length"],
                },
                "content": to_str(result.content),
            },
        )

    persistence_validations.register(validate_url_request)


def test_lambda_layer_invoke(persistence_validations, snapshot, aws_client):
    fn_name = f"test-layer-fn-{short_uid()}"
    layer_name = f"test-layer-layer-{short_uid()}"
    role_name = f"test-layer-role-{short_uid()}"

    role = aws_client.iam.create_role(
        RoleName=role_name, AssumeRolePolicyDocument=json.dumps(ASSUME_ROLE_POLICY)
    )
    with open(TEST_LAMBDA_CODEIMPORT_LAYER_PATH, "rb") as layer_file:
        layer_content = layer_file.read()

    layer_version = aws_client.lambda_.publish_layer_version(
        LayerName=layer_name, Content={"ZipFile": layer_content}
    )

    with open(TEST_LAMBDA_LAYERTEST_PATH, "rb") as f:
        aws_client.lambda_.create_function(
            FunctionName=fn_name,
            Runtime=Runtime.python3_12,
            Handler="index.handler",
            Role=role["Role"]["Arn"],
            Code={"ZipFile": f.read()},
            Layers=[layer_version["LayerVersionArn"]],
        )
    aws_client.lambda_.get_waiter("function_active_v2").wait(FunctionName=fn_name)

    def validate_invoke():
        aws_client.lambda_.get_waiter("function_active_v2").wait(FunctionName=fn_name)
        invoke = aws_client.lambda_.invoke(FunctionName=fn_name)
        content = to_str(invoke["Payload"].read())
        assert "hello world from imported code" in content

        snapshot.match("get_fn", aws_client.lambda_.get_function(FunctionName=fn_name))
        snapshot.match(
            "get_layer_version",
            aws_client.lambda_.get_layer_version(
                LayerName=layer_version["LayerArn"], VersionNumber=layer_version["Version"]
            ),
        )
        snapshot.match(
            "get_layer_version_by_arn",
            aws_client.lambda_.get_layer_version_by_arn(Arn=layer_version["LayerVersionArn"]),
        )

    persistence_validations.register(validate_invoke)


@pytest.mark.skip(
    reason="Skip temporarily because the public layer expired and we are working on a fix"
)
def test_lambda_public_layer_invoke(persistence_validations, snapshot, aws_client):
    fn_name = f"test-layer-fn-{short_uid()}"
    role_name = f"test-layer-role-{short_uid()}"

    public_layer_version_arn = f"arn:aws:lambda:{aws_client.lambda_.meta.region_name}:770693421928:layer:Klayers-p39-PyYAML:1"

    role = aws_client.iam.create_role(
        RoleName=role_name, AssumeRolePolicyDocument=json.dumps(ASSUME_ROLE_POLICY)
    )
    with open(TEST_LAMBDA_OPTCONTENT_PATH, "rb") as f:
        aws_client.lambda_.create_function(
            FunctionName=fn_name,
            Runtime=Runtime.python3_12,
            Handler="index.handler",
            Role=role["Role"]["Arn"],
            Code={"ZipFile": f.read()},
            Layers=[public_layer_version_arn],
        )
    aws_client.lambda_.get_waiter("function_active_v2").wait(FunctionName=fn_name)

    def validate_invoke():
        aws_client.lambda_.get_waiter("function_active_v2").wait(FunctionName=fn_name)
        invoke = aws_client.lambda_.invoke(FunctionName=fn_name)
        response_payload = to_str(invoke["Payload"].read())
        assert "PyYAML" in response_payload
        snapshot.match("invoke_response_payload", response_payload)
        snapshot.match(
            "layer_info",
            aws_client.lambda_.get_layer_version_by_arn(Arn=public_layer_version_arn),
        )

    persistence_validations.register(validate_invoke)


def test_lambda_image_fn_invoke(persistence_validations, snapshot, aws_client):
    fn_name = f"test-image-fn-{short_uid()}"
    role_name = f"test-image-role-{short_uid()}"

    role = aws_client.iam.create_role(
        RoleName=role_name, AssumeRolePolicyDocument=json.dumps(ASSUME_ROLE_POLICY)
    )

    # build image
    image_name = f"test-image-{short_uid()}"
    DOCKER_CLIENT.build_image(
        os.path.join(os.path.dirname(__file__), "image/Dockerfile"),
        image_name=image_name,
        platform=DockerPlatform.linux_amd64,
    )

    aws_client.lambda_.create_function(
        FunctionName=fn_name,
        Role=role["Role"]["Arn"],
        Code={"ImageUri": image_name},
        PackageType="Image",
    )
    aws_client.lambda_.get_waiter("function_active_v2").wait(FunctionName=fn_name)

    def validate_invoke():
        aws_client.lambda_.get_waiter("function_active_v2").wait(FunctionName=fn_name)
        invoke = aws_client.lambda_.invoke(FunctionName=fn_name)
        response_payload = to_str(invoke["Payload"].read())
        assert "hello from persisted image lambda" in response_payload
        snapshot.match("invoke_response_payload", response_payload)

    persistence_validations.register(validate_invoke)


def test_lambda_version_and_alias(persistence_validations, snapshot, aws_client):
    fn_name = f"test-versions-fn-{short_uid()}"
    role_name = f"test-versions-role-{short_uid()}"
    alias_name = f"test-alias-{short_uid()}"

    role = aws_client.iam.create_role(
        RoleName=role_name, AssumeRolePolicyDocument=json.dumps(ASSUME_ROLE_POLICY)
    )
    with open(TEST_LAMBDA_ECHO_PATH, "rb") as f:
        aws_client.lambda_.create_function(
            FunctionName=fn_name,
            Runtime=Runtime.python3_12,
            Handler="index.handler",
            Role=role["Role"]["Arn"],
            Code={"ZipFile": f.read()},
            Timeout=3,
        )
    aws_client.lambda_.get_waiter("function_active_v2").wait(FunctionName=fn_name)

    v1 = aws_client.lambda_.publish_version(FunctionName=fn_name)
    aws_client.lambda_.update_function_configuration(FunctionName=fn_name, Timeout=10)
    aws_client.lambda_.get_waiter("function_updated_v2").wait(FunctionName=fn_name)
    v2 = aws_client.lambda_.publish_version(FunctionName=fn_name)
    alias = aws_client.lambda_.create_alias(
        FunctionName=fn_name, Name=alias_name, FunctionVersion=v1["Version"]
    )
    latest_arn = aws_client.lambda_.get_function(FunctionName=fn_name)["Configuration"][
        "FunctionArn"
    ]

    def validate_invokes():
        aws_client.lambda_.get_waiter("function_active_v2").wait(FunctionName=fn_name)

        invoke = aws_client.lambda_.invoke(FunctionName=fn_name)
        assert "ErrorResponse" not in invoke
        snapshot.match("invoke", invoke)

        invoke = aws_client.lambda_.invoke(FunctionName=v1["FunctionArn"])
        assert "ErrorResponse" not in invoke
        snapshot.match("invoke_v1", invoke)

        invoke = aws_client.lambda_.invoke(FunctionName=v2["FunctionArn"])
        assert "ErrorResponse" not in invoke
        snapshot.match("invoke_v2", invoke)

        invoke = aws_client.lambda_.invoke(FunctionName=alias["AliasArn"])
        assert "ErrorResponse" not in invoke
        snapshot.match("invoke_alias", invoke)

        snapshot.match("get_fn_latest", aws_client.lambda_.get_function(FunctionName=latest_arn))
        snapshot.match("get_fn_v1", aws_client.lambda_.get_function(FunctionName=v1["FunctionArn"]))
        snapshot.match("get_fn_v2", aws_client.lambda_.get_function(FunctionName=v2["FunctionArn"]))
        snapshot.match(
            "get_alias", aws_client.lambda_.get_alias(FunctionName=fn_name, Name=alias_name)
        )

    persistence_validations.register(validate_invokes)


def test_lambda_provisioned_concurrency(persistence_validations, snapshot, aws_client):
    fn_name = f"test-provisioned-fn-{short_uid()}"
    testutil.create_lambda_function(
        func_name=fn_name, handler_file=TEST_LAMBDA_INVOCATION_TYPE, client=aws_client.lambda_
    )
    aws_client.lambda_.get_waiter("function_active_v2").wait(FunctionName=fn_name)

    v1 = aws_client.lambda_.publish_version(FunctionName=fn_name)
    aws_client.lambda_.put_provisioned_concurrency_config(
        FunctionName=fn_name, Qualifier=v1["Version"], ProvisionedConcurrentExecutions=1
    )
    assert wait_until(
        concurrency_update_done(aws_client.lambda_, fn_name, v1["Version"]), max_retries=5
    )

    def validate_invoke():
        assert wait_until(
            concurrency_update_done(aws_client.lambda_, fn_name, v1["Version"]), max_retries=5
        )
        get_provisioned_postwait = aws_client.lambda_.get_provisioned_concurrency_config(
            FunctionName=fn_name, Qualifier=v1["Version"]
        )
        snapshot.match("get_provisioned_postwait", get_provisioned_postwait)

        invoke = aws_client.lambda_.invoke(FunctionName=fn_name, Qualifier=v1["Version"])
        assert "FunctionError" not in invoke
        result1 = json.load(invoke["Payload"])
        assert result1 == "provisioned-concurrency"

    persistence_validations.register(validate_invoke)
