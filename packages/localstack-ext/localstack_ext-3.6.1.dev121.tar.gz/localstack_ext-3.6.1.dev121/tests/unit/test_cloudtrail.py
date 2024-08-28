from datetime import datetime

import pytest
from localstack.pro.core.aws.api.cloudtrail import InvalidLookupAttributesException
from localstack.pro.core.services.cloudtrail.provider import (
    _filter_lookup_attributes,
    _filter_time_frame,
)

EVENT_1 = {
    "EventId": "my-id",
    "EventName": "hello",
    "ReadOnly": "true",
    "AccessKeyId": "my-access-key-id",
    "EventTime": "2022-10-01T10:00:18.510Z",
    "EventSource": "test-source",
    "Username": "hello-user",
    "Resources": [
        {
            "ResourceType": "My-Custom",
            "ResourceName": "My-Custom-Name",
        },
        {
            "ResourceType": "AnotherType",
            "ResourceName": "CLOUDWATCH_LOGS_DELIVERY_SESSION",
        },
    ],
    "CloudTrailEvent": "this is a test event",
}

EVENT_2 = {
    "EventId": "357b5f32-0eb0-4211-ab56-aed303031ef6",
    "EventName": "AssumeRole",
    "ReadOnly": "true",
    "EventTime": "2022-10-01T12:00:18.510Z",
    "EventSource": "sts.amazonaws.com",
    "Resources": [
        {
            "ResourceType": "AWS::IAM::AccessKey",
            "ResourceName": "ASIA4F7JQIER3RSPCB4G",
        },
        {
            "ResourceType": "AWS::STS::AssumedRole",
            "ResourceName": "CLOUDWATCH_LOGS_DELIVERY_SESSION",
        },
    ],
    "CloudTrailEvent": '{"eventVersion":"1.08","userIdentity":{"type":"AWSService","invokedBy":"cloudtrail.amazonaws.com"}}',
}

EVENT_3 = {
    "EventId": "a78a82a9-b45c-4764-8f2b-528a0177108f",
    "EventName": "GetCallerIdentity",
    "ReadOnly": "true",
    "AccessKeyId": "AKIA4F7JQIERVQUKPCXV",
    "EventTime": "2022-12-01T12:00:10.000Z",
    "EventSource": "sts.amazonaws.com",
    "Username": "localstack-testing",
    "Resources": [],
    "CloudTrailEvent": "",
}


class TestCloudTrail:
    @pytest.mark.parametrize(
        "attribute_key,attribute_value,expected_events",
        # filter work for: EventId | EventName | ReadOnly | Username | ResourceType |
        # ResourceName | EventSource | AccessKeyId
        [
            ("EventId", "357b5f32-0eb0-4211-ab56-aed303031ef6", [EVENT_2]),
            ("EventName", "GetCallerIdentity", [EVENT_3]),
            ("EventSource", "sts.amazonaws.com", [EVENT_2, EVENT_3]),
            ("ReadOnly", "true", [EVENT_1, EVENT_2, EVENT_3]),
            ("Username", "hello-user", [EVENT_1]),
            ("ResourceType", "AWS::IAM::AccessKey", [EVENT_2]),
            ("ResourceName", "CLOUDWATCH_LOGS_DELIVERY_SESSION", [EVENT_1, EVENT_2]),
            ("EventSource", "test-source", [EVENT_1]),
            ("AccessKeyId", "my-access-key-id", [EVENT_1]),
            ("ResourceName", "abc", []),
        ],
    )
    def test_filter_lookup_attributes(self, attribute_key, attribute_value, expected_events):
        events = [EVENT_1, EVENT_2, EVENT_3]
        lookup_attributes = [
            {"AttributeKey": attribute_key, "AttributeValue": attribute_value},
        ]

        filtered = list(filter(lambda x: _filter_lookup_attributes(x, lookup_attributes), events))
        assert expected_events == filtered

    def test_filter_lookup_attributes_invalid(self):
        lookup_attributes = [
            {"AttributeKey": "hello", "AttributeValue": "anything"},
        ]
        with pytest.raises(InvalidLookupAttributesException):
            list(
                filter(
                    lambda x: _filter_lookup_attributes(x, lookup_attributes),
                    [EVENT_1, EVENT_2, EVENT_3],
                )
            )

    @pytest.mark.parametrize(
        "start_time,end_time,expected_events",
        [
            (None, None, [EVENT_1, EVENT_2, EVENT_3]),
            (datetime(year=2022, month=1, day=1), datetime(year=2022, month=4, day=1), []),
            (datetime(year=2022, month=10, day=2), datetime(year=2022, month=12, day=2), [EVENT_3]),
            (
                datetime(year=2022, month=10, day=1),
                datetime(year=2022, month=11, day=2),
                [EVENT_1, EVENT_2],
            ),
            (
                datetime(year=2022, month=10, day=1),
                datetime(year=2022, month=12, day=30),
                [EVENT_1, EVENT_2, EVENT_3],
            ),
        ],
    )
    def test_filter_time_frame(self, start_time, end_time, expected_events):
        events = [EVENT_1, EVENT_2, EVENT_3]
        filtered = list(filter(lambda x: _filter_time_frame(x, start_time, end_time), events))
        assert expected_events == filtered
