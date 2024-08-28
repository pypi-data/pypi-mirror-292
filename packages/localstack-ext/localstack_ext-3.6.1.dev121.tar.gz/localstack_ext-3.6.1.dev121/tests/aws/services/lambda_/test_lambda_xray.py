import datetime
import json
import os
import time

import pytest
from localstack.aws.api.lambda_ import Runtime
from localstack.testing.aws.util import is_aws_cloud
from localstack.testing.pytest import markers
from localstack.utils.platform import Arch
from localstack.utils.strings import short_uid
from localstack.utils.sync import retry, wait_until
from localstack_snapshot.snapshots.transformer import SortingTransformer

TEST_LAMBDA_POWERTOOLS = os.path.join(
    os.path.dirname(__file__), "functions/xray-tracing-powertools.py"
)
TEST_LAMBDA_POWERTOOLS_SDKCALL = os.path.join(
    os.path.dirname(__file__), "functions/xray-tracing-powertools-sdkcall.py"
)
TEST_LAMBDA_XRAY = os.path.join(os.path.dirname(__file__), "functions/xray-tracing.py")
TEST_LAMBDA_SNS_PUBLISH = os.path.join(os.path.dirname(__file__), "functions/lambda-sns-publish.py")


@pytest.fixture(autouse=True)
def fixture_snapshot(snapshot):
    snapshot.add_transformer(snapshot.transform.lambda_api())
    snapshot.add_transformer(
        snapshot.transform.key_value("CodeSha256", reference_replacement=False)
    )


def get_powertools_layer_arn(region: str, architecture: Arch = Arch.amd64) -> str:
    """https://docs.powertools.aws.dev/lambda/python/latest/#lambda-layer"""
    arch_suffix = ""
    if architecture == Arch.arm64:
        arch_suffix = "-Arm64"
    return f"arn:aws:lambda:{region}:017000801446:layer:AWSLambdaPowertoolsPythonV2{arch_suffix}:69"


class TestLambdaXrayIntegration:
    @staticmethod
    def register_xray_transformers(snapshot):
        snapshot.add_transformer(
            snapshot.transform.key_value("Id", "trace-id", reference_replacement=True)
        )
        snapshot.add_transformer(
            snapshot.transform.key_value("id", "segment-id", reference_replacement=True)
        )
        snapshot.add_transformer(
            snapshot.transform.key_value("start_time", "<start_time>", reference_replacement=False)
        )
        snapshot.add_transformer(
            snapshot.transform.key_value("end_time", "<end_time>", reference_replacement=False)
        )
        snapshot.add_transformer(
            snapshot.transform.key_value("Duration", "<duration>", reference_replacement=False)
        )
        snapshot.add_transformer(
            snapshot.transform.key_value("Coverage", "<coverage>", reference_replacement=False)
        )
        snapshot.add_transformer(
            snapshot.transform.key_value(
                "ResponseTime", "<response-time>", reference_replacement=False
            )
        )
        snapshot.add_transformer(
            snapshot.transform.key_value(
                "TracesProcessedCount", "<traces-processed>", reference_replacement=False
            )
        )
        snapshot.add_transformer(
            snapshot.transform.key_value("Revision", "<revision>", reference_replacement=False)
        )
        snapshot.add_transformer(snapshot.transform.regex("Lineage=[a-z0-9-]+:[0-9]+", "<lineage>"))
        snapshot.add_transformer(
            SortingTransformer("Segments", lambda s: s["Document"]["start_time"]), priority=-1
        )
        snapshot.add_transformer(
            SortingTransformer("subsegments", lambda s: s["start_time"]), priority=-1
        )
        snapshot.add_transformer(
            SortingTransformer("ServiceIds", lambda s: f'{s["Type"]}{s["Name"]}'), priority=-1
        )
        snapshot.add_transformer(
            SortingTransformer("ResourceARNs", lambda s: s["ARN"]), priority=-1
        )

    @staticmethod
    @pytest.mark.skipif(condition=not is_aws_cloud(), reason="missing x-ray features")
    def capture_xray_traces(xray_client, snapshot, summary_filter_expression: str):
        now = datetime.datetime.now(datetime.timezone.utc)
        before = now - datetime.timedelta(minutes=30)
        after = now + datetime.timedelta(minutes=10)

        if is_aws_cloud():
            # give X-Ray some time to process the traces after the invocation
            time.sleep(30)
        else:
            time.sleep(10)

        def get_trace_sums():
            return (
                xray_client.get_paginator("get_trace_summaries")
                .paginate(
                    StartTime=before.isoformat(),
                    EndTime=after.isoformat(),
                    FilterExpression=summary_filter_expression,
                )
                .build_full_result()
            )

        def wait_for_summaries_processed():
            trace_sums = get_trace_sums()
            return len(trace_sums["TraceSummaries"]) > 0

        assert wait_until(wait_for_summaries_processed)

        trace_summaries = get_trace_sums()
        snapshot.match("trace_summaries", trace_summaries)

        trace_ids = [ts["Id"] for ts in trace_summaries["TraceSummaries"]]
        assert wait_until(
            lambda: len(xray_client.batch_get_traces(TraceIds=trace_ids)["Traces"]) > 0
        )
        traces = (
            xray_client.get_paginator("batch_get_traces")
            .paginate(TraceIds=trace_ids)
            .build_full_result()
        )

        # parse the documents in the traces for proper snapshotting
        for trace in traces["Traces"]:
            for segment in trace["Segments"]:
                segment["Document"] = json.loads(segment["Document"])

        snapshot.match("traces", traces)

    @markers.aws.validated
    @pytest.mark.skipif(condition=not is_aws_cloud(), reason="missing x-ray features")
    def test_lambda_xray_active_tracing(
        self, create_lambda_function, snapshot, lambda_su_role, aws_client
    ):
        fn_name = f"test-xray-fn-{short_uid()}"

        create_lambda_function(
            func_name=fn_name,
            handler_file=TEST_LAMBDA_XRAY,
            runtime=Runtime.python3_12,
            role=lambda_su_role,
            TracingConfig={"Mode": "Active"},
        )

        get_fn_response = aws_client.lambda_.get_function(FunctionName=fn_name)
        snapshot.match("get_function", get_fn_response)

        invoke_result = aws_client.lambda_.invoke(FunctionName=fn_name)
        snapshot.match("invoke_result", invoke_result)

        self.register_xray_transformers(snapshot)
        self.capture_xray_traces(
            aws_client.xray,
            snapshot,
            summary_filter_expression=f'service(id(name: "{fn_name}", type: "AWS::Lambda::Function"))',
        )

    @markers.aws.validated
    @pytest.mark.skipif(condition=not is_aws_cloud(), reason="missing x-ray features")
    def test_lambda_xray_passive_tracing(
        self,
        create_lambda_function,
        lambda_su_role,
        snapshot,
        sns_create_topic,
        cleanups,
        aws_client,
    ):
        """
        This is generally not something we support yet, since this will need "active" instrumentation in the source services!

        Scenario: Lambda (Active) => SNS (Passive) => Lambda (Passive)
        """
        fn_name_active = f"test-xray-passive-active-fn-{short_uid()}"
        fn_name_passive = f"test-xray-passive-passive-fn-{short_uid()}"
        topic_name = f"test-xray-passive-{short_uid()}"

        snapshot.add_transformer(
            snapshot.transform.key_value("PolicyName", reference_replacement=True)
        )

        region = aws_client.lambda_.meta.region_name
        powertools_layer_arn = get_powertools_layer_arn(region)

        create_topic = sns_create_topic(Name=topic_name)
        snapshot.match("create_topic", create_topic)
        topic_arn = create_topic["TopicArn"]

        account_id = aws_client.sts.get_caller_identity()["Account"]
        region_name = aws_client.sts.meta.region_name
        doc = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "SNSAccess",
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "sns.amazonaws.com",
                    },
                    "Action": [
                        "xray:PutTraceSegments",
                        "xray:GetSamplingRules",
                        "xray:GetSamplingTargets",
                    ],
                    "Resource": "*",
                    "Condition": {
                        "StringEquals": {"aws:SourceAccount": account_id},
                        "StringLike": {
                            "aws:SourceArn": f"arn:aws:sns:{region_name}:{account_id}:*"
                        },
                    },
                }
            ],
        }

        sns_policy_name = f"AllowSnsXray{short_uid()}"
        xray_put_policy = aws_client.xray.put_resource_policy(
            PolicyName=sns_policy_name, PolicyDocument=json.dumps(doc)
        )
        snapshot.match("xray_put_policy", xray_put_policy)
        cleanups.append(lambda: aws_client.xray.delete_resource_policy(PolicyName=sns_policy_name))

        create_lambda_function(
            func_name=fn_name_active,
            handler_file=TEST_LAMBDA_SNS_PUBLISH,
            runtime=Runtime.python3_12,
            role=lambda_su_role,
            TracingConfig={"Mode": "Active"},
            Environment={"Variables": {"SNS_TOPIC_ARN": topic_arn}},
            Layers=[powertools_layer_arn],
        )

        create_lambda_function(
            func_name=fn_name_passive,
            handler_file=TEST_LAMBDA_XRAY,
            runtime=Runtime.python3_12,
            role=lambda_su_role,
            TracingConfig={"Mode": "PassThrough"},
        )

        add_permission = aws_client.lambda_.add_permission(
            FunctionName=fn_name_passive,
            StatementId="allowsns",
            Action="lambda:InvokeFunction",
            Principal="sns.amazonaws.com",
            SourceArn=topic_arn,
        )
        snapshot.match("add_permission", add_permission)

        get_function_passive = aws_client.lambda_.get_function(FunctionName=fn_name_passive)
        snapshot.match("get_function_passive", get_function_passive)

        get_function_active = aws_client.lambda_.get_function(FunctionName=fn_name_active)
        snapshot.match("get_function_active", get_function_active)

        subscribe_response = aws_client.sns.subscribe(
            TopicArn=create_topic["TopicArn"],
            Protocol="lambda",
            Endpoint=get_function_passive["Configuration"]["FunctionArn"],
        )
        snapshot.match("subscribe_response", subscribe_response)

        active_invoke_result = aws_client.lambda_.invoke(
            FunctionName=fn_name_active, Payload=json.dumps({"message": "hi"})
        )
        snapshot.match("active_invoke_result", active_invoke_result)

        def check_lambda_invoked():
            return (
                len(
                    aws_client.logs.filter_log_events(
                        logGroupName=f"/aws/lambda/{fn_name_passive}"
                    )["events"]
                )
                > 0
            )

        assert wait_until(check_lambda_invoked)

        self.register_xray_transformers(snapshot)
        self.capture_xray_traces(
            aws_client.xray,
            snapshot,
            summary_filter_expression=f'service(id(name: "{fn_name_active}", type: "AWS::Lambda::Function"))',
        )

    @pytest.mark.skipif(condition=not is_aws_cloud(), reason="missing x-ray features")
    @markers.aws.validated
    def test_lambda_xray_manual_instrumentation(
        self, create_lambda_function, lambda_su_role, snapshot, aws_client
    ):
        fn_name = f"test-xray-manual-fn-{short_uid()}"

        region = aws_client.lambda_.meta.region_name
        powertools_layer_arn = get_powertools_layer_arn(region)

        create_lambda_function(
            func_name=fn_name,
            handler_file=TEST_LAMBDA_POWERTOOLS,
            runtime=Runtime.python3_12,
            role=lambda_su_role,
            TracingConfig={"Mode": "Active"},
            Layers=[powertools_layer_arn],
        )

        get_fn_response = aws_client.lambda_.get_function(FunctionName=fn_name)
        snapshot.match("get_function", get_fn_response)

        invoke_result = aws_client.lambda_.invoke(FunctionName=fn_name)
        snapshot.match("invoke_result", invoke_result)

        self.register_xray_transformers(snapshot)
        self.capture_xray_traces(
            aws_client.xray,
            snapshot,
            summary_filter_expression=f'service(id(name: "{fn_name}", type: "AWS::Lambda::Function"))',
        )

    @markers.only_on_amd64
    @markers.snapshot.skip_snapshot_verify
    @markers.aws.validated
    def test_basic_xray_integration(
        self, create_lambda_function, lambda_su_role, snapshot, aws_client
    ):
        """
        This is a very basic version of an xray integration test and the only one working with localstack right now.

        For the other ones to work, we'll need to improve the X-Ray service implementation in LocalStack.

        A few issues:
        * timezones are not respected
        * filter expressions are not implemented
        * paging for list operations not implemented
        * trace summaries missing most of the useful information

        """
        fn_name = f"test-xray-basic-fn-{short_uid()}"

        region = aws_client.lambda_.meta.region_name
        powertools_layer_arn = get_powertools_layer_arn(region)

        create_lambda_function(
            func_name=fn_name,
            handler_file=TEST_LAMBDA_POWERTOOLS_SDKCALL,
            runtime=Runtime.python3_12,
            role=lambda_su_role,
            TracingConfig={"Mode": "Active"},
            Layers=[powertools_layer_arn],
        )

        get_fn_response = aws_client.lambda_.get_function(FunctionName=fn_name)
        snapshot.match("get_function", get_fn_response)

        before = datetime.datetime.now(tz=datetime.timezone.utc)
        invoke_result = aws_client.lambda_.invoke(FunctionName=fn_name)
        snapshot.match("invoke_result", invoke_result)
        after = datetime.datetime.now(tz=datetime.timezone.utc)

        self.register_xray_transformers(snapshot)

        def get_trace_sum():
            if is_aws_cloud():
                ts = aws_client.xray.get_trace_summaries(
                    StartTime=(before - datetime.timedelta(minutes=1)).isoformat(),
                    EndTime=(after + datetime.timedelta(minutes=1)).isoformat(),
                    FilterExpression=f'service(id(name: "{fn_name}", type: "AWS::Lambda::Function"))',
                )
            else:
                ts = aws_client.xray.get_trace_summaries(
                    StartTime=(before - datetime.timedelta(seconds=1)),
                    EndTime=(after + datetime.timedelta(seconds=10)),
                )  # this might be flaky since other invocations / xray integration might influence this without a filter

            assert len(ts["TraceSummaries"]) == 1
            return ts

        if is_aws_cloud():
            # give X-Ray some time to process the traces after the invocation
            time.sleep(30)
        else:
            # LocalStack currently doesn't much
            time.sleep(5)

        # This might be flaky because we need to wait until all trace segments arrived and are processed
        trace_sums = retry(get_trace_sum, retries=30, sleep=2)
        snapshot.match("trace_sums", trace_sums)
        traces = aws_client.xray.batch_get_traces(TraceIds=[trace_sums["TraceSummaries"][0]["Id"]])
        snapshot.match("traces", traces)

        # TODO: extend when xray implementation is extended
        assert "ListFunctions" in json.dumps(traces["Traces"])
