import gzip
import json

import pytest as pytest
from localstack.constants import AWS_REGION_US_EAST_1
from localstack.testing.pytest import markers
from localstack.testing.snapshots.transformer_utility import TransformerUtility
from localstack.utils.strings import short_uid
from localstack.utils.sync import poll_condition, retry
from localstack.utils.time import now_utc

logs_role = {
    "Statement": {
        "Effect": "Allow",
        "Principal": {"Service": f"logs.{AWS_REGION_US_EAST_1}.amazonaws.com"},
        "Action": "sts:AssumeRole",
    }
}
kinesis_permission = {
    "Version": "2012-10-17",
    "Statement": [{"Effect": "Allow", "Action": "kinesis:PutRecord", "Resource": "*"}],
}


@pytest.fixture
def logs_log_group(aws_client):
    name = f"test-log-group-{short_uid()}"
    aws_client.logs.create_log_group(logGroupName=name)
    yield name
    aws_client.logs.delete_log_group(logGroupName=name)


@pytest.fixture
def logs_log_stream(logs_log_group, aws_client):
    name = f"test-log-stream-{short_uid()}"
    aws_client.logs.create_log_stream(logGroupName=logs_log_group, logStreamName=name)
    yield name
    aws_client.logs.delete_log_stream(logStreamName=name, logGroupName=logs_log_group)


class TestCloudWatchLogsPro:
    @markers.aws.unknown
    def test_json_metric_filters(self, logs_log_group, logs_log_stream, aws_client):
        json_filter_name_1 = f"test-filter-json-ext-{short_uid()}"
        json_filter_name_2 = f"test-filter-json-ext-{short_uid()}"
        namespace_name = f"test-metric-namespace-{short_uid()}"
        json_transform_1 = {
            "metricNamespace": namespace_name,
            "metricName": f"test-metric-{short_uid()}",
            "metricValue": "1",
            "defaultValue": 0,
        }
        json_transform_2 = {
            "metricNamespace": namespace_name,
            "metricName": f"test-metric-{short_uid()}",
            "metricValue": "1",
            "defaultValue": 0,
        }
        aws_client.logs.put_metric_filter(
            logGroupName=logs_log_group,
            filterName=json_filter_name_1,
            filterPattern='{$.message = "no_trigger"}',
            metricTransformations=[json_transform_1],
        )
        aws_client.logs.put_metric_filter(
            logGroupName=logs_log_group,
            filterName=json_filter_name_2,
            filterPattern='{$.foo = "bar"}',
            metricTransformations=[json_transform_2],
        )

        response = aws_client.logs.describe_metric_filters(
            logGroupName=logs_log_group, filterNamePrefix="test-filter-json-ext-"
        )
        assert response["ResponseMetadata"]["HTTPStatusCode"] == 200
        filter_names = [_filter["filterName"] for _filter in response["metricFilters"]]
        assert json_filter_name_1 in filter_names
        assert json_filter_name_2 in filter_names

        # put log events and assert metrics being published
        events = [
            {"timestamp": now_utc(millis=True), "message": '{"foo":"bar"}'},
            {"timestamp": now_utc(millis=True), "message": '{"foo":"baz"}'},
        ]
        aws_client.logs.put_log_events(
            logGroupName=logs_log_group, logStreamName=logs_log_stream, logEvents=events
        )

        # list metrics
        response = aws_client.cloudwatch.list_metrics(Namespace=namespace_name)
        assert len(response["Metrics"]) == 1

        # delete filters
        aws_client.logs.delete_metric_filter(
            logGroupName=logs_log_group, filterName=json_filter_name_1
        )
        aws_client.logs.delete_metric_filter(
            logGroupName=logs_log_group, filterName=json_filter_name_2
        )

        response = aws_client.logs.describe_metric_filters(
            logGroupName=logs_log_group, filterNamePrefix="test-filter-json-ext"
        )
        assert response["ResponseMetadata"]["HTTPStatusCode"] == 200
        filter_names = [_filter["filterName"] for _filter in response["metricFilters"]]
        assert json_filter_name_1 not in filter_names
        assert json_filter_name_2 not in filter_names

    log_messages = [
        "INFO 09/25/2014 12:00:00 GET /service/resource/67 1200",
        "INFO 09/25/2014 12:00:01 POST /service/resource/67/part/111 1310",
        "WARNING 09/25/2014 12:00:02 Invalid user request",
        "ERROR 09/25/2014 12:00:02 Failed to process request",
        "FOO date look_at-the=Time FOOBAR /INFO/WARNING/ERROR/00010203 over nine thousand What can we break with this message? %%[]!§$%&/()=?äöÜ`+*~''_-.:,;",
    ]

    @pytest.mark.skip(reason="Not yet implemented")
    @pytest.mark.parametrize(
        "pattern, messages",
        [
            # regular, no conditions
            ("[LogLevel, Date, Time, Method, Url, ResponseTime]", log_messages),
            # fewer labels than white-space-delimited terms, no conditions
            ("[log_level, rest]", log_messages),
            # fewer labels than wsd terms, one condition, mandatory trailing label after condition
            ("[log_level = INFO, rest]", log_messages),
            # one condition, no mandatory trailing label after condition
            ("[log_level = INFO]", log_messages),
            # one condition with all-consuming-wildcard no regex, no trailing label
            ("[log_level = IN*]", log_messages),
            # one condition with all-consuming-wildcard no regex, trailing label
            ("[log_level = IN*, rest]", log_messages),
            # one condition with erroneously, previously used wildcard as regex, trailing label
            ("[log_level = %IN*%, w2]", log_messages),
            # one condition with all-consuming-wildcard as regex, trailing label. Not bound to start
            ("[log_level = %IN.*%, w2]", log_messages),
            # one condition with all-consuming-wildcard as regex, trailing label. Bound to start
            ("[log_level = %^IN.*%]", log_messages),
            # one condition with finite length pattern as regex, no trailing label
            ("[log_level = %^IN[fF][oO]%]", log_messages),
            # examples from AWS
            (
                "[logLevel, date, time, method, url=%/service/resource/[0-9]+$%, response_time]",
                log_messages,
            ),
            (
                "[logLevel, date, time, method, url=%/service/resource/[0-9]+/part/[0-9]+$%, response_time]",
                log_messages,
            ),
            # one condition in the middle of the labels
            ("[log_level, date, time = %02%, method, url]", log_messages),
            # standard bool
            ("[w1=ERROR || w1=WARNING, w2]", log_messages),
            ("[w1!=ERROR && w1!=WARNING, w2]", log_messages),
            # whitespace behaviour check
            ("[w1 = ERROR||w1 = WARNING, w2]", log_messages),
            ("[w1!=ERROR&&w1!=WARNING, w2]", log_messages),
            # chained boolean expressions
            ("[w1 = ERROR && w1 != FOO || w1 = WARNING, w2]", log_messages),
            ("[w1 = ERROR && (w1 != FOO || w1 = WARNING), w2]", log_messages),
            # wrong bool operators
            ("[w1!=ERROR AND w1!=WARNING, w2]", log_messages),
            ("[w1=ERROR OR w1=WARNING, w2]", log_messages),
            # invalid operator sequences
            ("[w1=ERROR && || w1=WARNING, w2]", log_messages),
            ("[w1=ERROR !=== w1=WARNING, w2]", log_messages),
            ("[w1==ERROR  || w1!=WARNING, w2]", log_messages),
            ("[w1===ERROR || w1!==WARNING, w2]", log_messages),
        ],
    )
    @markers.aws.unknown
    def test_filter_log_events_with_whitespace_delimited_list(
        self, pattern, messages, logs_log_group, logs_log_stream, aws_client, snapshot
    ):
        snapshot.add_transformer(snapshot.transform.logs_api())

        events = [{"timestamp": now_utc(millis=True), "message": message} for message in messages]
        aws_client.logs.put_log_events(
            logGroupName=logs_log_group, logStreamName=logs_log_stream, logEvents=events
        )

        def check_log_events_exist():
            stored_events = aws_client.logs.get_log_events(
                logGroupName=logs_log_group, logStreamName=logs_log_stream
            ).get("events", [])
            return len(events) == len(stored_events)

        assert poll_condition(check_log_events_exist, timeout=10), "gave up waiting for log events"
        try:
            filtered_events = aws_client.logs.filter_log_events(
                logGroupName=logs_log_group, filterPattern=pattern
            )
            snapshot.match("whitespace-delimited-filter", filtered_events)
        except Exception as e:
            snapshot.match("whitespace-delimited-filter-exception", e)

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(paths=["$..nextToken", "$..searchedLogStreams"])
    @pytest.mark.parametrize(
        "pattern, messages",
        [
            ("%Success%", ["Successful message", '{"Message": Success}', "Error"]),
            ("%Message%", ["Successful message", '{"Message": Success}', "Error"]),
            ("%[mM]essage%", ["Successful message", '{"Message": Success}', "Error"]),
            (
                "%}$%",
                [
                    "Successful message",
                    '{"Message": Success}',
                    "Error: {'Hello, World'} is not a valid object",
                ],
            ),
        ],
    )
    def test_filter_log_events_with_regex(
        self, pattern, messages, logs_log_group, logs_log_stream, aws_client, snapshot
    ):
        snapshot.add_transformer(snapshot.transform.logs_api())

        events = [{"timestamp": now_utc(millis=True), "message": message} for message in messages]
        aws_client.logs.put_log_events(
            logGroupName=logs_log_group, logStreamName=logs_log_stream, logEvents=events
        )

        def check_log_events_exist():
            stored_events = aws_client.logs.get_log_events(
                logGroupName=logs_log_group, logStreamName=logs_log_stream
            ).get("events", [])
            return len(events) == len(stored_events)

        assert poll_condition(check_log_events_exist, timeout=10), "gave up waiting for log events"

        filtered_events = aws_client.logs.filter_log_events(
            logGroupName=logs_log_group, filterPattern=pattern
        )
        snapshot.match("regex-filter", filtered_events)

    @markers.snapshot.skip_snapshot_verify(paths=["$..nextToken", "$..searchedLogStreams"])
    @pytest.mark.parametrize(
        "pattern, messages",
        [
            (
                "cat",
                [
                    "cat",
                    "cats",
                    "CAT",
                    "Cat",
                    "car",
                    "tac",
                    "c a t",
                    "caterpillar",
                    "baby-cat",
                    "cart",
                    "communicate",
                    "devilspawn",
                ],
            )
        ],
    )
    @markers.aws.validated
    def test_filter_log_events_with_unstructured_pattern(
        self, pattern, messages, logs_log_group, logs_log_stream, aws_client, snapshot
    ):
        snapshot.add_transformer(snapshot.transform.logs_api())

        events = [{"timestamp": now_utc(millis=True), "message": message} for message in messages]
        aws_client.logs.put_log_events(
            logGroupName=logs_log_group, logStreamName=logs_log_stream, logEvents=events
        )

        def check_log_events_exist():
            stored_events = aws_client.logs.get_log_events(
                logGroupName=logs_log_group, logStreamName=logs_log_stream
            ).get("events", [])
            return len(events) == len(stored_events)

        assert poll_condition(check_log_events_exist, timeout=10), "gave up waiting for log events"

        filtered_events = aws_client.logs.filter_log_events(
            logGroupName=logs_log_group, filterPattern=pattern
        )
        snapshot.match(f"unstructured-filter-{pattern}", filtered_events)

    @markers.aws.unknown
    def test_filter_log_events_with_pattern(self, logs_log_group, logs_log_stream, aws_client):
        message0 = '{"somekey":"value1","foo":"bar"}'
        message1 = '{"somekey":"value1","foo":"baz"}'
        message2 = '{"otherkey":"value1","foo":"bar"}'

        events = [
            {"timestamp": now_utc(millis=True), "message": message0},
            {"timestamp": now_utc(millis=True), "message": message1},
            {"timestamp": now_utc(millis=True), "message": message2},
        ]
        aws_client.logs.put_log_events(
            logGroupName=logs_log_group, logStreamName=logs_log_stream, logEvents=events
        )

        def check_log_events_exist():
            stored_events = aws_client.logs.get_log_events(
                logGroupName=logs_log_group, logStreamName=logs_log_stream
            ).get("events", [])
            return len(events) == len(stored_events)

        assert poll_condition(check_log_events_exist, timeout=10), "gave up waiting for log events"

        # simple k=v filter
        filtered_events = aws_client.logs.filter_log_events(
            logGroupName=logs_log_group, filterPattern='{$.foo = "bar"}'
        ).get("events")
        messages = [event.get("message") for event in filtered_events]
        assert message0 in messages
        assert message2 in messages
        assert len(messages) == 2

        # conjunction filter
        filtered_events = aws_client.logs.filter_log_events(
            logGroupName=logs_log_group,
            filterPattern='{ ($.somekey = "value1") && ($.foo = "bar") }',
        ).get("events")
        messages = [event.get("message") for event in filtered_events]
        assert message0 in messages
        assert len(messages) == 1

        # disjunction filter
        filtered_events = aws_client.logs.filter_log_events(
            logGroupName=logs_log_group,
            filterPattern='{ ($.somekey = "value1") || ($.foo = "bar") }',
        ).get("events")
        messages = [event.get("message") for event in filtered_events]
        assert message0 in messages
        assert message1 in messages
        assert message2 in messages
        assert len(messages) == 3

    @markers.aws.validated
    def test_filter_log_events_with_non_json_messages(
        self, logs_log_group, logs_log_stream, aws_client, snapshot
    ):
        snapshot.add_transformer(snapshot.transform.logs_api())

        message0 = '{"somekey":"value1","foo":"bar"}'
        message1 = "mymessage"

        events = [
            {"timestamp": now_utc(millis=True), "message": message0},
            {"timestamp": now_utc(millis=True), "message": message1},
        ]
        aws_client.logs.put_log_events(
            logGroupName=logs_log_group, logStreamName=logs_log_stream, logEvents=events
        )

        def _get_filtered_events():
            # this will currently fail
            collected_events = (
                aws_client.logs.get_paginator("filter_log_events")
                .paginate(logGroupName=logs_log_group, filterPattern='{ $.somekey = "value1" }')
                .build_full_result()
                .get("events")
            )
            assert collected_events
            return collected_events

        filtered_events = retry(_get_filtered_events, sleep=10)

        snapshot.match("filtered_events", filtered_events)

    @markers.aws.validated
    def test_filter_log_events_with_json_property(
        self, logs_log_group, logs_log_stream, aws_client, snapshot
    ):
        snapshot.add_transformer(snapshot.transform.logs_api())

        message0 = {"isCool": False, "ShouldBeHidden": False, "_typeTag": "ImportantMessage"}
        message1 = {"isCool": False, "ShouldBeHidden": False, "_typeTag": "NotImportantMessage"}
        message2 = {"isCool": False, "ShouldBeHidden": False, "testing": True}

        events = [
            {"timestamp": now_utc(millis=True), "message": json.dumps(message0)},
            {"timestamp": now_utc(millis=True), "message": json.dumps(message1)},
            {"timestamp": now_utc(millis=True), "message": json.dumps(message2)},
        ]
        aws_client.logs.put_log_events(
            logGroupName=logs_log_group,
            logStreamName=logs_log_stream,
            logEvents=events,
        )

        def _get_filtered_events():
            # this will currently fail
            collected_events = (
                aws_client.logs.get_paginator("filter_log_events")
                .paginate(
                    logGroupName=logs_log_group, filterPattern='{ $._typeTag = "ImportantMessage" }'
                )
                .build_full_result()
                .get("events")
            )
            assert collected_events
            return collected_events

        filtered_events = retry(_get_filtered_events, sleep=10)

        snapshot.match("filtered_events", filtered_events)

    @pytest.mark.skip(
        reason="the current filter pattern implementation requires parens around conjunctions"
    )
    @markers.aws.unknown
    def test_filter_log_events_with_unparenthesized_pattern(
        self, logs_log_group, logs_log_stream, aws_client
    ):
        message0 = '{"somekey":"value1","foo":"bar"}'
        message1 = '{"somekey":"value1","foo":"baz"}'

        events = [
            {"timestamp": now_utc(millis=True), "message": message0},
            {"timestamp": now_utc(millis=True), "message": message1},
        ]
        aws_client.logs.put_log_events(
            logGroupName=logs_log_group, logStreamName=logs_log_stream, logEvents=events
        )

        # this will currently fail
        filtered_events = aws_client.logs.filter_log_events(
            logGroupName=logs_log_group, filterPattern='{ $.somekey = "value1" && $.foo = "bar" }'
        )
        assert message0 in filtered_events
        assert len(filtered_events) == 1

    @markers.aws.validated
    def test_put_subscription_filter_kinesis_with_filter_pattern(
        self,
        create_subscription_filter,
        aws_client,
        snapshot,
    ):
        snapshot.add_transformer(snapshot.transform.logs_api())
        snapshot.add_transformer(
            TransformerUtility.key_value("logGroup", reference_replacement=False),
        )
        snapshot.add_transformer(
            TransformerUtility.key_value("logStream", reference_replacement=False),
        )

        kinesis_name, logs_log_group, logs_log_stream, subscription_name = (
            create_subscription_filter
        )

        snapshot.add_transformer(snapshot.transform.regex(subscription_name, "<subscription-name>"))
        snapshot.add_transformer(TransformerUtility.key_value("id"))

        valid_msg_1 = json.dumps({"first": "ok", "second": "success"})
        valid_msg_2 = json.dumps({"first": "nice", "second": "success", "additional": "is fine"})
        valid_msg_3 = json.dumps({"second": "variation", "first": "should be fine"})

        # these messages should not match:
        invalid_msg_1 = "first"
        invalid_msg_2 = json.dumps({"first": "hello"})
        invalid_msg_3 = json.dumps({"first": "not enough", "info": "should not work"})

        def put_event():
            aws_client.logs.put_log_events(
                logGroupName=logs_log_group,
                logStreamName=logs_log_stream,
                logEvents=[
                    {"timestamp": now_utc(millis=True), "message": invalid_msg_1},
                    {"timestamp": now_utc(millis=True), "message": valid_msg_1},
                    {"timestamp": now_utc(millis=True), "message": invalid_msg_2},
                    {"timestamp": now_utc(millis=True), "message": invalid_msg_3},
                    {"timestamp": now_utc(millis=True), "message": valid_msg_2},
                    {"timestamp": now_utc(millis=True), "message": valid_msg_3},
                ],
            )

        retry(put_event, retries=6, sleep=10.0)

        shard_iterator = aws_client.kinesis.get_shard_iterator(
            StreamName=kinesis_name,
            ShardId="shardId-000000000000",
            ShardIteratorType="TRIM_HORIZON",
        )["ShardIterator"]

        response = aws_client.kinesis.get_records(ShardIterator=shard_iterator)
        # AWS sends messages as health checks
        assert len(response["Records"]) >= 1
        data_messages = []
        for record in response["Records"]:
            tmp = json.loads(gzip.decompress(record["Data"]))
            if tmp["messageType"] == "DATA_MESSAGE":
                data_messages.append(tmp)

        snapshot.match("data_messages", data_messages)

        log_events = data_messages[0]["logEvents"]
        snapshot.match("log_events", log_events)

        unfiltered_events = aws_client.logs.filter_log_events(
            logGroupName=logs_log_group, filterPattern=""
        ).get("events")
        snapshot.match("unfiltered_events", unfiltered_events)


@pytest.fixture
def create_subscription_filter(
    aws_client,
    create_iam_role_with_policy,
    kinesis_create_stream,
    logs_log_stream,
    logs_log_group,
    wait_for_stream_ready,
):
    kinesis_name = f"test-kinesis-{short_uid()}"
    kinesis_create_stream(StreamName=kinesis_name, ShardCount=1)

    result = aws_client.kinesis.describe_stream(StreamName=kinesis_name)["StreamDescription"]
    kinesis_arn = result["StreamARN"]
    role = f"test-kinesis-role-{short_uid()}"
    policy_name = f"test-kinesis-role-policy-{short_uid()}"
    role_arn = create_iam_role_with_policy(
        RoleName=role,
        PolicyName=policy_name,
        RoleDefinition=logs_role,
        PolicyDefinition=kinesis_permission,
    )

    subscription_name = f"subscription{short_uid()}"
    wait_for_stream_ready(stream_name=kinesis_name)

    def put_subscription_filter():
        aws_client.logs.put_subscription_filter(
            logGroupName=logs_log_group,
            filterName=subscription_name,
            filterPattern='{ ($.first = "*") && ($.second = "*") }',
            destinationArn=kinesis_arn,
            roleArn=role_arn,
        )

    # for a weird reason the put_subscription_filter fails on AWS the first time,
    # even-though we check for ACTIVE state...
    retry(put_subscription_filter, retries=6, sleep=3.0)
    yield kinesis_name, logs_log_group, logs_log_stream, subscription_name

    # clean up
    aws_client.logs.delete_subscription_filter(
        logGroupName=logs_log_group, filterName=subscription_name
    )
