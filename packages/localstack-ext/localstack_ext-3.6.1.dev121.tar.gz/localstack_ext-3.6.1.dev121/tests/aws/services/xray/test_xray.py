import json
from datetime import datetime, timedelta

import pytest
import requests
from botocore.exceptions import ClientError
from localstack.testing.pytest import markers
from localstack.utils.functions import call_safe
from localstack.utils.strings import short_uid
from localstack.utils.urls import localstack_host

XRAY_TARGET_URL = "{xray_protocol}://{xray_host}:{xray_port}/xray_records"


def _dummy_xray_sampling_rule(rule_name):
    return {
        "RuleName": rule_name,
        "ResourceARN": "arn:aws:s3:::somebucket",
        "Priority": 123,
        "FixedRate": 1,
        "ReservoirSize": 123,
        "ServiceName": "myservice",
        "ServiceType": "myservicetype",
        "Host": "myhost",
        "HTTPMethod": "GET",
        "URLPath": "/myservice",
        "Version": 1,
    }


@pytest.fixture()
def xray_create_sampling_rule(aws_client):
    rule_names = list()

    def factory(**kwargs):
        if "RuleName" not in kwargs:
            kwargs["RuleName"] = f"xrule-{short_uid()}"

        rule = _dummy_xray_sampling_rule(kwargs["RuleName"])
        rule.update(kwargs)
        response = aws_client.xray.create_sampling_rule(SamplingRule=rule)
        rule_name = response["SamplingRuleRecord"]["SamplingRule"]["RuleName"]
        rule_names.append(rule_name)
        return rule_name

    yield factory

    for rule_name in rule_names:
        call_safe(aws_client.xray.delete_sampling_rule, kwargs={"RuleName": rule_name})


class TestXRay:
    @markers.aws.unknown
    def test_custom_xray_records_endpoint(self, aws_client):
        host_definition = localstack_host()
        url = XRAY_TARGET_URL.format(
            xray_protocol="http",
            xray_host=host_definition.host,
            xray_port=host_definition.port,
        )

        end = datetime.utcnow()
        start = datetime.utcnow()

        sample_segment = {
            "name": "example.com",
            "id": short_uid(),
            "start_time": start.timestamp(),
            "trace_id": f"1-{short_uid()}-a006649127e371903a2de979",
            "end_time": end.timestamp(),
        }
        message = '{"format":"json","version":1}\n%s' % json.dumps(sample_segment)
        requests.post(url, data=message)

        result = aws_client.xray.get_trace_summaries(
            StartTime=start - timedelta(hours=1), EndTime=end + timedelta(hours=1)
        )
        ids = [r["Id"] for r in result["TraceSummaries"]]
        assert sample_segment["trace_id"] in ids

    @markers.aws.unknown
    def test_create_and_get_sampling_rule(self, xray_create_sampling_rule, aws_client):
        rule_name = f"xrule-{short_uid()}"
        rule_data = _dummy_xray_sampling_rule(rule_name)
        xray_create_sampling_rule(**rule_data)

        # find rule
        result = aws_client.xray.get_sampling_rules()
        record = next(
            filter(
                lambda r: r["SamplingRule"]["RuleName"] == rule_name, result["SamplingRuleRecords"]
            )
        )
        rule = record["SamplingRule"]
        for k, v in rule_data.items():
            assert rule[k] == v

    @markers.aws.unknown
    def test_create_existing_sampling_rule_raises_exception(
        self, xray_create_sampling_rule, aws_client
    ):
        rule_name = xray_create_sampling_rule()
        with pytest.raises(ClientError) as e:
            aws_client.xray.create_sampling_rule(SamplingRule=_dummy_xray_sampling_rule(rule_name))
        e.match("Sampling rule already exists")

    @markers.aws.unknown
    def test_delete_sampling_rule(self, xray_create_sampling_rule, aws_client):
        rule_name = xray_create_sampling_rule()

        result = aws_client.xray.get_sampling_rules()
        rule_names = [r["SamplingRule"]["RuleName"] for r in result["SamplingRuleRecords"]]
        assert rule_name in rule_names

        aws_client.xray.delete_sampling_rule(RuleName=rule_name)

        with pytest.raises(ClientError) as e:
            aws_client.xray.delete_sampling_rule(RuleName=rule_name)
        e.match("Sampling rule does not exist")

        result = aws_client.xray.get_sampling_rules()
        rule_names = [r["SamplingRule"]["RuleName"] for r in result["SamplingRuleRecords"]]
        assert rule_name not in rule_names

    @markers.aws.unknown
    def test_update_sampling_rule(self, xray_create_sampling_rule, aws_client):
        rule_name = xray_create_sampling_rule()

        aws_client.xray.update_sampling_rule(
            SamplingRuleUpdate={
                "RuleName": rule_name,
                "Host": "updatedhost",
                "Priority": 420,
                "Attributes": {"Foo": "Bar"},
            }
        )

        result = aws_client.xray.get_sampling_rules()
        record = next(
            filter(
                lambda r: r["SamplingRule"]["RuleName"] == rule_name, result["SamplingRuleRecords"]
            )
        )

        assert record["ModifiedAt"]
        rule = record["SamplingRule"]

        assert rule["Host"] == "updatedhost"
        assert rule["Priority"] == 420
        assert rule["Attributes"] == {"Foo": "Bar"}
        assert rule["Version"] == 2, "version wasn't incremented"
        # smoke test that old attributes weren't updated
        assert rule["ServiceName"] == "myservice"

    @markers.aws.unknown
    def test_put_records(self, aws_client):
        # put records
        records = [
            {
                "Timestamp": datetime.now(),
                "SegmentsReceivedCount": 2,
                "SegmentsSentCount": 1,
                "SegmentsRejectedCount": 0,
                "BackendConnectionErrors": {},
            }
        ]
        result = aws_client.xray.put_telemetry_records(TelemetryRecords=records)
        assert result["ResponseMetadata"]["HTTPStatusCode"] == 200

    @markers.aws.unknown
    def test_put_and_get_trace_segments(self, aws_client):
        # https://docs.aws.amazon.com/xray/latest/devguide/xray-api-segmentdocuments.html
        end = datetime.utcnow()
        start = datetime.utcnow() - timedelta(seconds=10)

        sample_segment = {
            "name": "example.com",
            "id": short_uid(),
            "start_time": start.timestamp(),
            "trace_id": f"1-{short_uid()}-a006649127e371903a2de979",
            "end_time": end.timestamp(),
        }

        trace_docs = [json.dumps(sample_segment)]
        result = aws_client.xray.put_trace_segments(TraceSegmentDocuments=trace_docs)
        assert result["ResponseMetadata"]["HTTPStatusCode"] == 200
        assert not result["UnprocessedTraceSegments"]

        result = aws_client.xray.get_trace_summaries(
            StartTime=start - timedelta(hours=1), EndTime=end + timedelta(hours=1)
        )
        ids = [r["Id"] for r in result["TraceSummaries"]]
        assert sample_segment["trace_id"] in ids

        result = aws_client.xray.get_trace_summaries(
            StartTime=start + timedelta(hours=1), EndTime=end - timedelta(hours=1)
        )
        ids = [r["Id"] for r in result["TraceSummaries"]]
        assert sample_segment["trace_id"] not in ids
