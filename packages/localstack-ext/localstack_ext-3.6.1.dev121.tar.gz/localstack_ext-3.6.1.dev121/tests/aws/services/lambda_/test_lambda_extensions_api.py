import glob
import json
import os.path
import tempfile
import zipfile

import pytest
from localstack import config
from localstack.aws.api.lambda_ import Runtime
from localstack.testing.aws.util import is_aws_cloud
from localstack.testing.pytest import markers
from localstack.utils.strings import short_uid, to_str
from localstack.utils.sync import retry, wait_until
from localstack_snapshot.snapshots.transformer import SortingTransformer

THIS_FOLDER = os.path.dirname(__file__)
TEST_LAMBDA_LIST_DIR = os.path.join(THIS_FOLDER, "functions/lambda-echo.py")


def _load_s3_content(s3_client, bucket_name, key) -> dict:
    return json.loads(to_str(s3_client.get_object(Bucket=bucket_name, Key=key)["Body"].read()))


def _get_s3_objects(s3_client, bucket_name: str) -> dict:
    all_objs = (
        s3_client.get_paginator("list_objects_v2").paginate(Bucket=bucket_name).build_full_result()
    )
    return {
        o["Key"]: _load_s3_content(s3_client, bucket_name, o["Key"]) for o in all_objs["Contents"]
    }


class TestExtensionsApi:
    @markers.snapshot.skip_snapshot_verify(
        paths=[
            "$..shutdownReason",
            "$..['Content-Type']",
            "$..env",
        ]
    )
    @markers.aws.validated
    def test_generic_extension_full_lifecycle(
        self, create_lambda_function, cleanups, s3_create_bucket, snapshot, monkeypatch, aws_client
    ):
        function_name = f"test-ext-fn-{short_uid()}"
        layer_name = f"test-ext-layer-{short_uid()}"
        bucket_name = f"test-ext-bucket-{short_uid()}"
        extension_path = "extensions/lifecyclelog"

        if not is_aws_cloud():
            monkeypatch.setattr(config, "LAMBDA_KEEPALIVE_MS", 5_000)

        snapshot.add_transformer(snapshot.transform.lambda_api())
        snapshot.add_transformer(
            snapshot.transform.key_value(
                "CodeSha256", "<code-sha-256>", reference_replacement=False
            )
        )
        snapshot.add_transformer(
            snapshot.transform.key_value("deadlineMs", "<deadline-ms>", reference_replacement=False)
        )
        snapshot.add_transformer(
            snapshot.transform.key_value("Date", "<date>", reference_replacement=False)
        )
        snapshot.add_transformer(
            snapshot.transform.key_value(
                "Content-Length", "<content-length>", reference_replacement=False
            )
        )
        snapshot.add_transformer(
            snapshot.transform.key_value(
                "Lambda-Extension-Event-Identifier",
                "extension-event-id",
                reference_replacement=True,
            )
        )
        snapshot.add_transformer(
            snapshot.transform.key_value(
                "Lambda-Extension-Identifier", "extension-id", reference_replacement=True
            )
        )
        snapshot.add_transformer(
            snapshot.transform.jsonpath(
                "$..tracing.value", "<trace-id>", reference_replacement=False
            )
        )
        snapshot.add_transformer(SortingTransformer("env", lambda x: x))
        snapshot.add_transformer(snapshot.transform.regex(bucket_name, "<bucket>"))

        bucket = s3_create_bucket(Bucket=bucket_name)

        tempdir = tempfile.mkdtemp()
        f_name = os.path.join(tempdir, "ext.zip")
        with zipfile.ZipFile(f_name, "w") as f:
            for file in glob.glob(os.path.join(THIS_FOLDER, f"{extension_path}/**/*")):
                root = os.path.join(THIS_FOLDER, extension_path)
                rel_path = os.path.relpath(file, root)
                f.write(file, arcname=f"{rel_path}")

        with open(f_name, "rb") as fd:
            content = fd.read()

        layer_version = aws_client.lambda_.publish_layer_version(
            LayerName=layer_name, Content={"ZipFile": content}
        )
        cleanups.append(
            lambda: aws_client.lambda_.delete_layer_version(
                LayerName=layer_name, VersionNumber=layer_version["Version"]
            )
        )

        create_lambda_function(
            handler_file=TEST_LAMBDA_LIST_DIR,
            func_name=function_name,
            runtime=Runtime.python3_12,
            Environment={"Variables": {"TEST_BUCKET": bucket}},
            Layers=[layer_version["LayerVersionArn"]],
        )
        get_function = aws_client.lambda_.get_function(FunctionName=function_name)
        snapshot.match("get_function", get_function)

        aws_client.lambda_.invoke(
            FunctionName=function_name,
            InvocationType="RequestResponse",
            Payload=json.dumps({"path": "/var/task"}),
        )

        aws_client.lambda_.delete_function(FunctionName=function_name)
        # it can take quite a while for AWS to shut down the environment after deletion!

        # retry until "loop_exited" in s3 bucket as key
        def shutdown_detected():
            aws_client.s3.head_object(Bucket=bucket_name, Key="loop_exited")
            return True

        assert wait_until(shutdown_detected, wait=10, strategy="static", max_retries=120)

        all_s3_objs = _get_s3_objects(s3_client=aws_client.s3, bucket_name=bucket_name)
        snapshot.match("events", all_s3_objs)


class TestExternalExtensions:
    @pytest.mark.skip(reason="Not fully supported yet. Invoke works but EXTENSION message missing.")
    @markers.aws.validated
    def test_lambda_insights_extension(self, create_lambda_function, aws_client, snapshot):
        """
        Set `LAMBDA_INSIGHTS_LOG_LEVEL` to increase log output from the lambdainsights layer. (e.g. set to `debug` or `info`)
        The extension is written in Rust

        Since it is written in Rust we can't enable transparent endpoint injection yet.
        """
        function_name = f"lambdainsights-test-fn-{short_uid()}"
        create_lambda_function(
            handler_file=TEST_LAMBDA_LIST_DIR,
            func_name=function_name,
            runtime=Runtime.python3_12,
            # https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/Lambda-Insights-extension-versions.html
            Layers=["arn:aws:lambda:us-east-1:580247275435:layer:LambdaInsightsExtension:38"],
            Environment={"Variables": {"LAMBDA_INSIGHTS_LOG_LEVEL": "debug"}},
        )

        invoke_result = aws_client.lambda_.invoke(FunctionName=function_name)
        assert invoke_result["StatusCode"] == 200
        assert "FunctionError" not in invoke_result

        def assert_events():
            log_events = aws_client.logs.filter_log_events(
                logGroupName=f"/aws/lambda/{function_name}",
            )["events"]
            invocation_count = len(
                [event["message"] for event in log_events if event["message"].startswith("REPORT")]
            )
            assert invocation_count == 1
            extension_message = [
                event["message"] for event in log_events if event["message"].startswith("EXTENSION")
            ][0]
            snapshot.match("extension-message", extension_message)
            # TODO: add more insights DEBUG assertions

        retry(assert_events, retries=60, sleep=2)
