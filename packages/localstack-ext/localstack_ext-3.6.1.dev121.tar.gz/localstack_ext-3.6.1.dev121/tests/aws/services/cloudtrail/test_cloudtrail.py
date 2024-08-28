import json
import logging
import os
import re
import time
import typing
from datetime import datetime, timedelta

import pytest
from botocore.exceptions import ClientError
from localstack.pro.core.services.cloudtrail.provider import STORAGE_BATCH_SIZE
from localstack.testing.aws.util import is_aws_cloud
from localstack.testing.pytest import markers
from localstack.utils import testutil
from localstack.utils.aws import resources
from localstack.utils.collections import select_attributes
from localstack.utils.http import download
from localstack.utils.strings import short_uid
from localstack.utils.sync import retry
from localstack.utils.testutil import create_zip_file, list_all_log_events
from localstack.utils.time import TIMESTAMP_FORMAT_TZ
from localstack_snapshot.snapshots.transformer import KeyValueBasedTransformer

if typing.TYPE_CHECKING:
    from mypy_boto3_cloudtrail.type_defs import CreateTrailResponseTypeDef

LOG = logging.getLogger(__name__)

# TODO - move to common CDK test utils
CDK_CUSTOM_RESOURCE_REPO = "https://cdn.jsdelivr.net/npm/@aws-cdk/custom-resources@1.134.0"
CDK_CUSTOM_RESOURCE_HANDLER_URL = (
    f"{CDK_CUSTOM_RESOURCE_REPO}/lib/aws-custom-resource/runtime/index.js"
)

S3_BUCKET_POLICY = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AWSCloudTrailAclCheck20150319",
            "Effect": "Allow",
            "Principal": {"Service": ["cloudtrail.amazonaws.com", "config.amazonaws.com"]},
            "Action": "s3:GetBucketAcl",
            "Resource": "arn:aws:s3:::<s3-bucket-name>",
            "Condition": {},
        },
        {
            "Sid": "AWSCloudTrailWrite20150319",
            "Effect": "Allow",
            "Principal": {"Service": ["cloudtrail.amazonaws.com", "config.amazonaws.com"]},
            "Action": "s3:PutObject",
            "Resource": "arn:aws:s3:::<s3-bucket-name>/*",
            "Condition": {"StringEquals": {"s3:x-amz-acl": "bucket-owner-full-control"}},
        },
    ],
}


@pytest.fixture
def s3_create_bucket_with_cloudtrail_policy(aws_client, s3_create_bucket):
    def factory(**kwargs) -> str:
        result = s3_create_bucket(**kwargs)
        policy = json.dumps(S3_BUCKET_POLICY).replace("<s3-bucket-name>", result)
        aws_client.s3.put_bucket_policy(Bucket=result, Policy=policy)
        return result

    yield factory


@pytest.fixture
def cloudtrail_create_trail(aws_client):
    trails = []

    def _create_trail(**kwargs) -> "CreateTrailResponseTypeDef":
        if "Name" not in kwargs:
            kwargs["Name"] = f"trail-test-{short_uid()}"

        response = aws_client.cloudtrail.create_trail(**kwargs)
        trails.append(response["Name"])
        return response

    yield _create_trail

    for trail_name in trails:
        try:
            aws_client.cloudtrail.delete_trail(Name=trail_name)
        except ClientError as e:
            LOG.debug(
                "error deleting trail %s: %s",
                trail_name,
                e,
            )


def filter_trail_list(trail_list: list[dict]) -> list[dict]:
    """
    Small helper method to filter aws-controltower default Cloudtrail trails
    """
    return [trail for trail in trail_list if "aws-controltower" not in trail.get("Name", "")]


class TestCloudTrail:
    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(
        paths=[
            "$..CloudTrailEvent.additionalEventData",
            "$..CloudTrailEvent.apiVersion",
            "$..CloudTrailEvent.recipientAccountId",
            "$..CloudTrailEvent.requestParameters.Host",
            "$..CloudTrailEvent.tlsDetails",
            "$..CloudTrailEvent.userIdentity",
            "$..Resources",
        ]
    )
    def test_record_events(self, aws_client, snapshot):
        bucket_name = f"test-{short_uid()}"

        snapshot.add_transformer(snapshot.transform.cloudtrail_api())
        snapshot.add_transformer(snapshot.transform.regex(bucket_name, "<bucket-name>"))
        snapshot.add_transformer(snapshot.transform.key_value("requestID"))

        events_before = self._get_recent_events_for_s3_bucket(aws_client.cloudtrail, bucket_name)
        assert not events_before

        # create test action
        resources.create_s3_bucket(bucket_name, s3_client=aws_client.s3)

        def _get_events():
            result = self._get_recent_events_for_s3_bucket(aws_client.cloudtrail, bucket_name)
            assert len(result) >= 1
            return result

        events = retry(_get_events, retries=100 if is_aws_cloud() else 10)
        assert events[0]["EventName"] == "CreateBucket"
        snapshot.match("s3_create_bucket_event", events)

    @markers.aws.validated
    def test_invalid_config(self, aws_client, snapshot, s3_bucket):
        with pytest.raises(ClientError) as e:
            aws_client.cloudtrail.create_trail(Name="t1", S3BucketName="trail-bucket")

        snapshot.match("invalid_name", e.value.response)

        with pytest.raises(ClientError) as e:
            aws_client.cloudtrail.create_trail(
                Name="trail1", S3BucketName="trail-bucket-not-exists"
            )

        snapshot.match("bucket_not_exists", e.value.response)

        if is_aws_cloud():
            # this must be with IAM enforcement
            with pytest.raises(ClientError) as e:
                aws_client.cloudtrail.create_trail(
                    Name="trail1",
                    S3BucketName=s3_bucket,
                )

            snapshot.match("bucket-no-policy", e.value.response)

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(
        paths=[
            "$..HasCustomEventSelectors",
            "$..HasInsightSelectors",
            "$..HomeRegion",
            "$..IncludeGlobalServiceEvents",
            "$..IsMultiRegionTrail",
            "$..IsOrganizationTrail",
        ]
    )
    def test_create_trail(
        self,
        aws_client,
        cloudtrail_create_trail,
        s3_create_bucket_with_cloudtrail_policy,
        snapshot,
        s3_bucket,
    ):
        snapshot.add_transformer(snapshot.transform.key_value("S3BucketName"))
        # create trail
        bucket_name = f"trail-{short_uid()}"
        trail_name = "trail1"
        s3_create_bucket_with_cloudtrail_policy(
            Bucket=bucket_name,
        )
        trail = cloudtrail_create_trail(Name=trail_name, S3BucketName=bucket_name)
        snapshot.match("create-trail", trail)

        describe_trails = aws_client.cloudtrail.describe_trails()
        describe_trails["trailList"] = filter_trail_list(describe_trails["trailList"])
        snapshot.match("describe-trails", describe_trails)

        list_trails = aws_client.cloudtrail.list_trails()
        list_trails["Trails"] = filter_trail_list(list_trails["Trails"])
        snapshot.match("list-trails", list_trails)

        list_objects = aws_client.s3.list_objects_v2(Bucket=bucket_name)
        snapshot.match("list-objects", list_objects)

        start_trail = aws_client.cloudtrail.start_logging(Name=trail_name)
        snapshot.match("start-trail-with-name", start_trail)

        if is_aws_cloud():
            # to be sure logging has started
            time.sleep(10)

        # generate several events
        for i in range(STORAGE_BATCH_SIZE + 1):
            aws_client.s3.put_object(Bucket=s3_bucket, Key=f"random-key-{i}")

        # get the objects list after the event are published
        def _list_objects():
            list_objects_result = aws_client.s3.list_objects_v2(Bucket=bucket_name)
            contents = list_objects_result["Contents"]
            # TODO internal requests are currently captured by cloudtrail as well
            # also, we cannot filter by bucket against LS, currently
            regex = r"AWSLogs/[0-9]+/CloudTrail/[^/]+/.*_CloudTrail_.*\.json\.gz"
            assert any(re.match(regex, _object["Key"]) for _object in contents)
            return list_objects_result

        list_objects_after = retry(
            _list_objects, sleep=8 if is_aws_cloud() else 0.5, retries=120 if is_aws_cloud() else 8
        )
        assert len(list_objects_after["Contents"]) >= 2

        bucket_2 = f"trail-2-{short_uid()}"
        s3_create_bucket_with_cloudtrail_policy(
            Bucket=bucket_2,
        )
        update_trail = aws_client.cloudtrail.update_trail(Name=trail_name, S3BucketName=bucket_2)

        snapshot.match("update-trail", update_trail)
        get_trail = aws_client.cloudtrail.get_trail(Name=trail_name)
        snapshot.match("get-trail", get_trail)

        stop_logging = aws_client.cloudtrail.stop_logging(Name=trail_name)
        snapshot.match("stop-logging-with-name", stop_logging)

        start_logging = aws_client.cloudtrail.start_logging(Name=trail_name)
        snapshot.match("re-start-logging-with-name", start_logging)

        # delete trail
        result = aws_client.cloudtrail.delete_trail(Name=trail_name)
        snapshot.match("delete-trail", result)

        describe_trails = aws_client.cloudtrail.describe_trails()
        describe_trails["trailList"] = filter_trail_list(describe_trails["trailList"])
        snapshot.match("describe-trails-after-delete", describe_trails)

        with pytest.raises(ClientError) as e:
            aws_client.cloudtrail.delete_trail(Name=trail_name)
        snapshot.match("error-delete-trail", e.value.response)

    @markers.aws.needs_fixing
    def test_no_logging_if_no_startup(
        self, aws_client, s3_create_bucket_with_cloudtrail_policy, cloudtrail_create_trail
    ):
        # create trail
        bucket_name = f"trail-{short_uid()}"
        trail_name = "trail1"
        s3_create_bucket_with_cloudtrail_policy(
            Bucket=bucket_name,
        )
        trail = cloudtrail_create_trail(Name=trail_name, S3BucketName=bucket_name)
        assert "Name" in trail
        assert trail["Name"] == trail_name  # TODO fails on AWS
        trail = select_attributes(
            trail, ["Name", "S3BucketName", "TrailARN", "LogFileValidationEnabled"]
        )
        result = aws_client.cloudtrail.describe_trails()
        assert trail in result["trailList"]
        result = aws_client.cloudtrail.list_trails()
        assert select_attributes(trail, ["Name", "TrailARN"]) in result["Trails"]

        # generate several events
        for i in range(STORAGE_BATCH_SIZE + 1):
            aws_client.s3.list_buckets()

        # assert file received
        objects = testutil.map_all_s3_objects(
            buckets=[bucket_name], to_json=False, s3_client=aws_client.s3
        )
        assert len(objects) == 1

    @markers.aws.validated
    @markers.skip_offline
    def test_cdk_trail_cw_logs(
        self, s3_bucket, s3_create_bucket, deploy_cfn_template, aws_client, tmp_path
    ):
        # download custom resource handler file to S3
        handler_dir = str(tmp_path)
        handler_file = os.path.join(handler_dir, "index.js")
        handler_zip = os.path.join(handler_dir, "handler.zip")
        download(CDK_CUSTOM_RESOURCE_HANDLER_URL, handler_file)

        # create handler zip file in S3
        handler_bucket = f"test-cdk-cloudtrail-handler-{short_uid()}"
        kwargs = {}
        if aws_client.s3.meta.region_name != "us-east-1":
            kwargs["CreateBucketConfiguration"] = {
                "LocationConstraint": aws_client.s3.meta.region_name
            }
        s3_create_bucket(Bucket=handler_bucket, **kwargs)
        create_zip_file(handler_file, handler_zip)
        aws_client.s3.upload_file(handler_zip, handler_bucket, "handler.zip")

        # create stack (CFN JSON generated from simple CDK program)
        trail_bucket = f"b-{short_uid()}"
        trail_name = f"test-trail-{short_uid()}"

        deployment = deploy_cfn_template(
            template_path=os.path.join(
                os.path.dirname(__file__), "../../templates/cdk-cloudtrail-stack.yaml"
            ),
            parameters={
                "TrailName": trail_name,
                "TrailBucket": trail_bucket,
                "UserBucket": s3_bucket,
                "HandlerBucket": handler_bucket,
            },
            max_wait=180,
        )
        # Note: setting high timeout here, as some CFn custom resources in the stack are
        #  doing "Installing latest AWS SDK v2" inside the Lambda, which can take some time

        # assert that trail has been deployed
        result = aws_client.cloudtrail.describe_trails()
        matching = [t for t in result["trailList"] if t["Name"] == trail_name]
        assert matching
        result = aws_client.cloudtrail.list_tags(ResourceIdList=[matching[0]["TrailARN"]])[
            "ResourceTagList"
        ]
        assert result[0]["TagsList"] == [
            {"Key": "tag1", "Value": "value1"},
            {"Key": "tag2", "Value": "value2"},
        ]

        # run some API calls
        key1 = f"key-{short_uid()}"
        aws_client.s3.put_object(Bucket=s3_bucket, Key=key1, Body=b"test content 123")

        log_group = deployment.outputs["LogGroupName"]

        # assert resources have been created
        def _is_correct_request(request_parameters: dict):
            return (
                request_parameters.get("bucketName") == s3_bucket
                and request_parameters.get("key") == key1
            )

        def _check():
            events = list_all_log_events(log_group, logs_client=aws_client.logs)
            messages = [json.loads(e.get("message")) for e in events]
            messages = [m.get("detail") or {} for m in messages]
            messages = [m for m in messages if m.get("eventName") == "PutObject"]
            messages = [m for m in messages if _is_correct_request(m["requestParameters"])]
            assert len(messages) == 1

        retry(_check, sleep=8 if is_aws_cloud() else 0.5, retries=120 if is_aws_cloud() else 8)

        # assert files have been logged to S3 (as IsLogging=true in the CFn template)
        def _check_objects():
            objects = aws_client.s3.list_objects_v2(Bucket=trail_bucket)["Contents"]
            keys = [object["Key"] for object in objects]
            # TODO internal requests are currently captured by cloudtrail as well
            # also, we cannot filter by bucket against LS, currently
            regex = r"AWSLogs/[0-9]+/CloudTrail/[^/]+/.*_CloudTrail_.*\.json\.gz"
            assert any(re.match(regex, key) for key in keys)

        retry(
            _check_objects, sleep=8 if is_aws_cloud() else 0.5, retries=120 if is_aws_cloud() else 8
        )

    @markers.aws.validated
    def test_get_trail_status_of_not_started(
        self, aws_client, s3_create_bucket_with_cloudtrail_policy, snapshot, cloudtrail_create_trail
    ):
        # CreateTrail.
        bucket_name = "trail-%s" % short_uid()
        trail_name = "trail1"
        s3_create_bucket_with_cloudtrail_policy(
            Bucket=bucket_name,
        )
        cloudtrail_create_trail(Name=trail_name, S3BucketName=bucket_name)

        # GetTrailStatus.
        trail_status_res = aws_client.cloudtrail.get_trail_status(Name=trail_name)
        snapshot.match("trail_status", trail_status_res)

        # DeleteTrail.
        delete_trail_res = aws_client.cloudtrail.delete_trail(Name=trail_name)
        snapshot.match("delete_trail", delete_trail_res)

    @markers.aws.validated
    def test_get_trail_status_of_started(
        self, aws_client, s3_create_bucket_with_cloudtrail_policy, snapshot, cloudtrail_create_trail
    ):
        # CreateTrail.
        bucket_name = "trail-%s" % short_uid()
        trail_name = "trail1"
        s3_create_bucket_with_cloudtrail_policy(
            Bucket=bucket_name,
        )
        cloudtrail_create_trail(Name=trail_name, S3BucketName=bucket_name)

        # StartLogging.
        start_logging_res = aws_client.cloudtrail.start_logging(Name=trail_name)
        snapshot.match("start_logging", start_logging_res)

        # GetTrailStatus.
        trail_status_res = aws_client.cloudtrail.get_trail_status(Name=trail_name)
        snapshot.match("trail_status", trail_status_res)

        # DeleteTrail.
        delete_trail_res = aws_client.cloudtrail.delete_trail(Name=trail_name)
        snapshot.match("delete_trail", delete_trail_res)

    @markers.aws.validated
    def test_get_trail_status_of_started_and_stopped(
        self, aws_client, s3_create_bucket_with_cloudtrail_policy, cloudtrail_create_trail, snapshot
    ):
        # CreateTrail.
        bucket_name = "trail-%s" % short_uid()
        trail_name = "trail1"
        s3_create_bucket_with_cloudtrail_policy(
            Bucket=bucket_name,
        )
        cloudtrail_create_trail(Name=trail_name, S3BucketName=bucket_name)

        # StartLogging.
        start_logging_res = aws_client.cloudtrail.start_logging(Name=trail_name)
        snapshot.match("start_logging", start_logging_res)

        # GetTrailStatus.
        trail_status_res = aws_client.cloudtrail.get_trail_status(Name=trail_name)
        snapshot.match("get_status", trail_status_res)

        time.sleep(1)  # 1s to ensure TZ time difference between invocations.
        # StopLogging.
        stop_logging_res = aws_client.cloudtrail.stop_logging(Name=trail_name)
        snapshot.match("stop_logging", stop_logging_res)

        # GetTrailStatus.
        trail_status_2_res = aws_client.cloudtrail.get_trail_status(Name=trail_name)
        assert datetime.strptime(
            trail_status_2_res["TimeLoggingStarted"], TIMESTAMP_FORMAT_TZ
        ) < datetime.strptime(trail_status_2_res["TimeLoggingStopped"], TIMESTAMP_FORMAT_TZ)

        assert trail_status_2_res["StartLoggingTime"] < trail_status_2_res["StopLoggingTime"]
        snapshot.match("trail_status_2", trail_status_2_res)

        # DeleteTrail.
        delete_trail_res = aws_client.cloudtrail.delete_trail(Name=trail_name)
        snapshot.match("delete_trail", delete_trail_res)

    @markers.aws.needs_fixing
    # TODO refactor tests -> tests more or less the same things
    def test_start_stop_updates(
        self, aws_client, s3_create_bucket_with_cloudtrail_policy, cloudtrail_create_trail
    ):
        # CreateTrail.
        bucket_name = "trail-%s" % short_uid()
        trail_name = "trail1"
        s3_create_bucket_with_cloudtrail_policy(
            Bucket=bucket_name,
        )
        cloudtrail_create_trail(Name=trail_name, S3BucketName=bucket_name)

        # StartLogging & StopLogging.
        aws_client.cloudtrail.start_logging(Name=trail_name)
        time.sleep(0.1)
        aws_client.cloudtrail.stop_logging(Name=trail_name)
        #
        trail_status_1_res = aws_client.cloudtrail.get_trail_status(Name=trail_name)
        assert trail_status_1_res["StartLoggingTime"] < trail_status_1_res["StopLoggingTime"]

        # StartLogging & StopLogging.
        time.sleep(0.1)
        aws_client.cloudtrail.start_logging(
            Name=trail_name
        )  # TODO raises throttling exception on AWS
        time.sleep(0.1)
        aws_client.cloudtrail.stop_logging(Name=trail_name)
        #
        trail_status_2_res = aws_client.cloudtrail.get_trail_status(Name=trail_name)
        assert trail_status_2_res["StartLoggingTime"] < trail_status_2_res["StopLoggingTime"]
        assert trail_status_1_res["StopLoggingTime"] < trail_status_2_res["StartLoggingTime"]

        # StopLogging
        time.sleep(0.1)
        aws_client.cloudtrail.stop_logging(Name=trail_name)
        #
        trail_status_3_res = aws_client.cloudtrail.get_trail_status(Name=trail_name)
        assert trail_status_3_res["StartLoggingTime"] == trail_status_2_res["StartLoggingTime"]
        assert trail_status_3_res["StopLoggingTime"] == trail_status_2_res["StopLoggingTime"]

        # StartLogging
        time.sleep(0.1)
        aws_client.cloudtrail.start_logging(Name=trail_name)
        #
        trail_status_4_res = aws_client.cloudtrail.get_trail_status(Name=trail_name)
        assert trail_status_4_res["StartLoggingTime"] > trail_status_3_res["StartLoggingTime"]
        assert trail_status_4_res["StartLoggingTime"] > trail_status_3_res["StopLoggingTime"]
        assert trail_status_4_res["StopLoggingTime"] == trail_status_3_res["StopLoggingTime"]

        # StartLogging
        time.sleep(0.1)
        aws_client.cloudtrail.start_logging(Name=trail_name)
        #
        trail_status_5_res = aws_client.cloudtrail.get_trail_status(Name=trail_name)
        assert trail_status_5_res["StartLoggingTime"] > trail_status_4_res["StartLoggingTime"]
        assert trail_status_5_res["StartLoggingTime"] > trail_status_4_res["StopLoggingTime"]
        assert trail_status_5_res["StopLoggingTime"] == trail_status_4_res["StopLoggingTime"]

        aws_client.cloudtrail.delete_trail(Name=trail_name)

    @markers.aws.validated
    def test_filter_lookup_attributes_invalid(self, snapshot, aws_client):
        # lazy load if not yet ready
        events = aws_client.cloudtrail.lookup_events()["Events"]
        if len(events) == 0:
            # create dummy events
            log_group_name = f"log-group-{short_uid()}"
            aws_client.logs.create_log_group(logGroupName=log_group_name)
            aws_client.logs.delete_log_group(logGroupName=log_group_name)
        with pytest.raises(ClientError) as e:
            aws_client.cloudtrail.lookup_events(
                LookupAttributes=[{"AttributeKey": "hello", "AttributeValue": "anything"}]
            )
        snapshot.match("expected_error", e.value.response)

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(
        paths=[
            "$..CloudTrailEvent.additionalEventData",
            "$..CloudTrailEvent.apiVersion",  # TODO this is not returned for s3
            "$..CloudTrailEvent.recipientAccountId",
            "$..CloudTrailEvent.requestID",
            "$..CloudTrailEvent.requestParameters.Host",  # Host is not part of parameters according API
            "$..CloudTrailEvent.resources",  # not yet supported
            "$..CloudTrailEvent.tlsDetails",
            "$..CloudTrailEvent.userIdentity",
            "$..Resources",
            "$..NextToken",
        ]
    )
    @pytest.mark.skip(reason="failing since 23/02/2024 needs some investigation")
    def test_s3_trails(self, aws_client, snapshot):
        bucket_name = f"my-bucket-{short_uid()}"
        snapshot.add_transformer(snapshot.transform.cloudtrail_api())
        snapshot.add_transformer(snapshot.transform.regex(bucket_name, "<bucket-name>"))
        snapshot.add_transformer(snapshot.transform.key_value("requestID"))

        # lazy load if not yet ready
        aws_client.cloudtrail.lookup_events()

        # create bucket
        aws_client.s3.create_bucket(Bucket=bucket_name)

        # list buckets
        aws_client.s3.list_buckets()

        # TODO operations on buckets are not automatically added by AWS
        # trail is required: https://docs.aws.amazon.com/AmazonS3/latest/userguide/enable-cloudtrail-logging-for-s3.html

        # delete bucket
        aws_client.s3.delete_bucket(Bucket=bucket_name)

        def _get_recent_events():
            events_s3 = self._get_recent_events_for_s3_bucket(aws_client.cloudtrail, bucket_name)
            assert len(events_s3) >= 2
            return events_s3

        events = retry(
            _get_recent_events,
            retries=100 if is_aws_cloud() else 15,
            sleep=15 if is_aws_cloud() else 1,
        )

        snapshot.match(
            "s3_cloud_trail_events",
            sorted(events, key=lambda x: x["EventName"]),
        )
        events = aws_client.cloudtrail.lookup_events(
            LookupAttributes=[{"AttributeKey": "EventName", "AttributeValue": "ListBuckets"}],
            StartTime=datetime.utcnow() - timedelta(minutes=10),
            MaxResults=1,
        )
        snapshot.match("s3_cloud_trail_list", events)

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(
        paths=[
            "$..CloudTrailEvent.recipientAccountId",  # TODO should not be principal ID?
            "$..CloudTrailEvent.tlsDetails",  # TODO missing
            "$..CloudTrailEvent.userIdentity.accountId",  # TODO should not be principal ID?
            "$..CloudTrailEvent.userIdentity.arn",  # TODO recipient-account-id vs principal-id
            "$..CloudTrailEvent.userIdentity.type",  # TODO 'IAMUser' for AWS, 'root' in LS
            "$..CloudTrailEvent.userIdentity.userName",  # TODO missing
        ]
    )
    def test_filter_lookup_attributes(self, snapshot, aws_client):
        log_group_name = f"log-group-{short_uid()}"
        snapshot.add_transformer(snapshot.transform.cloudtrail_api())
        snapshot.add_transformer(
            KeyValueBasedTransformer(
                lambda k, v: v if k == "logGroupName" and v == log_group_name else None,
                replacement="log-group",
            )
        )
        # lazy load if not yet ready
        aws_client.cloudtrail.lookup_events()
        aws_client.logs.create_log_group(logGroupName=log_group_name)
        aws_client.logs.delete_log_group(logGroupName=log_group_name)
        lookup_attributes_delete_group = [
            {"AttributeKey": "EventName", "AttributeValue": "DeleteLogGroup"},
        ]
        lookup_attributes_create_group = [
            {"AttributeKey": "EventName", "AttributeValue": "CreateLogGroup"},
        ]

        # wait until event is available
        def _get_recent_events(lookup_attributes):
            events_logs = self._get_recent_log_group_events_for_log_group(
                aws_client.cloudtrail, lookup_attributes, log_group_name
            )
            assert len(events_logs) >= 1
            return events_logs

        result = retry(
            lambda: _get_recent_events(lookup_attributes_delete_group),
            retries=100 if is_aws_cloud() else 10,
            sleep=15 if is_aws_cloud() else 1,
        )

        assert len(result) == 1
        snapshot.match("lookup_attributes_1", result[0])

        # check CreateLogGroup event
        result = retry(
            lambda: _get_recent_events(lookup_attributes_create_group),
            retries=100 if is_aws_cloud() else 10,
            sleep=15 if is_aws_cloud() else 1,
        )

        assert len(result) == 1
        snapshot.match("lookup_attributes_2", result[0])

    def _get_recent_events_for_s3_bucket(self, cloudtrail_client, bucket_name) -> list:
        lookup_attributes = [{"AttributeKey": "EventSource", "AttributeValue": "s3.amazonaws.com"}]
        events = cloudtrail_client.lookup_events(
            LookupAttributes=lookup_attributes,
            StartTime=datetime.utcnow() - timedelta(minutes=5),
        )["Events"]

        result = [
            e
            for e in events
            if json.loads(e["CloudTrailEvent"])["requestParameters"].get("bucketName", "")
            == bucket_name
        ]
        return result

    def _get_recent_log_group_events_for_log_group(
        self, cloudtrail_client, lookup_attributes, log_group_name
    ) -> list:
        events = cloudtrail_client.lookup_events(
            LookupAttributes=lookup_attributes,
            StartTime=datetime.utcnow() - timedelta(minutes=5),
        )["Events"]

        result = [
            e
            for e in events
            if json.loads(e["CloudTrailEvent"])["requestParameters"]["logGroupName"]
            == log_group_name
        ]
        return result

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(
        paths=[
            "$..HasCustomEventSelectors",
            "$..HasInsightSelectors",
            "$..HomeRegion",
            "$..IncludeGlobalServiceEvents",
            "$..IsMultiRegionTrail",
            "$..IsOrganizationTrail",
        ]
    )
    def test_trail_operations_with_arn(
        self, aws_client, cloudtrail_create_trail, s3_create_bucket_with_cloudtrail_policy, snapshot
    ):
        snapshot.add_transformer(snapshot.transform.key_value("S3BucketName"))
        # create trail
        bucket_name = f"trail-{short_uid()}"
        trail_name = "trail1"
        s3_create_bucket_with_cloudtrail_policy(
            Bucket=bucket_name,
        )
        trail = cloudtrail_create_trail(Name=trail_name, S3BucketName=bucket_name)
        trail_arn = trail["TrailARN"]
        snapshot.match("create-trail", trail)

        start_trail = aws_client.cloudtrail.start_logging(Name=trail_arn)
        snapshot.match("start-trail-with-arn", start_trail)

        trail_status = aws_client.cloudtrail.get_trail_status(Name=trail_name)
        snapshot.match("get-trail-status-with-arn", trail_status)

        bucket_2 = f"trail-2-{short_uid()}"
        s3_create_bucket_with_cloudtrail_policy(
            Bucket=bucket_2,
        )
        update_trail = aws_client.cloudtrail.update_trail(Name=trail_arn, S3BucketName=bucket_2)
        snapshot.match("update-trail-with-arn", update_trail)

        get_trail = aws_client.cloudtrail.get_trail(Name=trail_arn)
        snapshot.match("get-trail-with-arn", get_trail)

        stop_logging = aws_client.cloudtrail.stop_logging(Name=trail_arn)
        snapshot.match("stop-logging-with-arn", stop_logging)

        # delete trail
        result = aws_client.cloudtrail.delete_trail(Name=trail_arn)
        snapshot.match("delete-trail-with-arn", result)

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(
        paths=[
            "$..IncludeGlobalServiceEvents",
            "$..IsMultiRegionTrail",
            "$..IsOrganizationTrail",
        ]
    )
    def test_wrong_arn_for_trail_ops(
        self,
        aws_client,
        aws_client_factory,
        snapshot,
        s3_create_bucket_with_cloudtrail_policy,
        cloudtrail_create_trail,
        region_name,
    ):
        snapshot.add_transformer(snapshot.transform.key_value("S3BucketName"))
        # create trail
        bucket_name = f"trail-{short_uid()}"
        trail_name = "trail1"
        s3_create_bucket_with_cloudtrail_policy(
            Bucket=bucket_name,
        )
        trail = cloudtrail_create_trail(Name=trail_name, S3BucketName=bucket_name)
        trail_arn = trail["TrailARN"]
        snapshot.match("create-trail", trail)

        # we need to have a different region than the current client
        region_2 = "us-east-1" if region_name != "us-east-1" else "eu-west-1"
        client_2 = aws_client_factory(region_name=region_2)

        with pytest.raises(ClientError) as e:
            client_2.cloudtrail.get_trail_status(Name=trail_arn)
        snapshot.match("get-trail-status-from-another-region", e.value.response)

        with pytest.raises(ClientError) as e:
            bad_arn = trail_arn.replace("trail/", "badtrail/")
            aws_client.cloudtrail.get_trail_status(Name=bad_arn)
        snapshot.match("get-trail-status-bad-arn-1", e.value.response)

        with pytest.raises(ClientError) as e:
            aws_client.cloudtrail.get_trail_status(Name="arn:aws:cloudtrail")
        snapshot.match("get-trail-status-malformed-arn-1", e.value.response)

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(
        paths=[
            "$..HasCustomEventSelectors",
            "$..HasInsightSelectors",
            "$..HomeRegion",
            "$..IncludeGlobalServiceEvents",
            "$..IsMultiRegionTrail",
            "$..IsOrganizationTrail",
        ]
    )
    def test_trail_s3_key_prefix(
        self,
        aws_client,
        cloudtrail_create_trail,
        s3_create_bucket_with_cloudtrail_policy,
        snapshot,
        s3_bucket,
    ):
        snapshot.add_transformer(snapshot.transform.key_value("S3BucketName"))
        # create trail
        bucket_name = f"trail-{short_uid()}"
        trail_name = "trail1"
        s3_create_bucket_with_cloudtrail_policy(
            Bucket=bucket_name,
        )
        trail = cloudtrail_create_trail(
            Name=trail_name, S3BucketName=bucket_name, S3KeyPrefix="my-prefix"
        )
        snapshot.match("create-trail", trail)

        list_objects = aws_client.s3.list_objects_v2(Bucket=bucket_name)
        snapshot.match("list-objects", list_objects)
