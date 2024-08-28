import queue
import time
from typing import Dict, Tuple

import pytest
from localstack import config
from localstack.aws.api import CommonServiceException, RequestContext, ServiceResponse
from localstack.aws.chain import HandlerChain
from localstack.aws.forwarder import create_aws_request_context
from localstack.aws.handlers.service import ServiceResponseParser
from localstack.aws.protocol.serializer import create_serializer
from localstack.http import Response
from localstack.pro.core.analytics.aws_request_aggregator import (
    DEFAULT_PRO_FLUSH_INTERVAL_SECS,
    EVENT_NAME,
    ProServiceRequestAggregator,
)
from localstack.pro.core.analytics.aws_request_logger import RequestLoggerHandler
from localstack.utils.analytics import EventLogger
from localstack.utils.analytics.events import Event, EventHandler
from localstack.utils.sync import retry


class EventCollector(EventHandler):
    def __init__(self):
        self.queue = queue.Queue()

    def handle(self, event: Event):
        self.queue.put(event)

    def next(self, timeout=None) -> Event:
        block = timeout is not None
        return self.queue.get(block=block, timeout=timeout)


@pytest.fixture(autouse=True)
def enable_analytics(monkeypatch):
    monkeypatch.setattr(config, "DEBUG_ANALYTICS", True)
    monkeypatch.setattr(config, "DISABLE_EVENTS", False)


@pytest.fixture
def event_collector():
    print("creating collector")
    return EventCollector()


@pytest.fixture
def test_chain(event_collector):
    return HandlerChain(
        response_handlers=[
            ServiceResponseParser(),
            RequestLoggerHandler(
                aggregator=ProServiceRequestAggregator(
                    event_logger=EventLogger(event_collector, "test_session_id")
                )
            ),
        ]
    )


def create_request_response(
    service: str, operation: str, request: Dict, response: ServiceResponse
) -> Tuple[RequestContext, Response]:
    context = create_aws_request_context(service, operation, request)
    response = create_serializer(context.service).serialize_to_response(
        response, context.operation, context.request.headers, context.request_id
    )
    return context, response


def receive_remaining_events(event_collector, num_expected_messages: int):
    api_calls = []
    total_requests_received = 0

    def _receive_all_events():
        nonlocal api_calls, total_requests_received
        last_event = event_collector.next(timeout=DEFAULT_PRO_FLUSH_INTERVAL_SECS / 2)

        for e in last_event.payload["api_calls"]:
            total_requests_received += e["count"]
            api_calls.append(e)
        assert total_requests_received == num_expected_messages

    retry(_receive_all_events, retries=4, sleep=0.01)
    return api_calls


class TestRequestLoggerHandler:
    def test_logs_response(self, test_chain, event_collector):
        context, response = create_request_response(
            "sqs",
            "CreateQueue",
            request={"QueueName": "foobar"},
            response={"QueueUrl": "http://localhost:4566/0000000000/foobar"},
        )
        test_chain.handle(context, response)
        assert context.service_response

        context, response = create_request_response(
            "sqs",
            "ListQueues",
            request={"QueueNamePrefix": "foo"},
            response={"QueueUrl": "http://localhost:4566/0000000000/foobar"},
        )
        test_chain.handle(context, response)

        event = event_collector.next(timeout=DEFAULT_PRO_FLUSH_INTERVAL_SECS * 2)
        assert event.name == EVENT_NAME
        assert event.metadata.session_id == "test_session_id"
        event_api_calls = event.payload["api_calls"]

        if len(event_api_calls) < 2:
            sum_requests_gathered = sum(event["count"] for event in event_api_calls)
            remaining_requests = receive_remaining_events(
                event_collector, 2 - sum_requests_gathered
            )
            event.payload["api_calls"].append(remaining_requests)

        # some basic formatting checks
        assert "client_time" in event_api_calls[0]
        assert event_api_calls[0]["count"] == 1
        assert event_api_calls[0]["service"] == "sqs"
        assert event_api_calls[0]["region"] == "us-east-1"
        assert not event_api_calls[0]["is_internal"]
        assert "Boto" in event_api_calls[0]["user_agent"]
        for key in ["account_id", "err_type", "err_msg"]:
            assert event_api_calls[0][key] is None

    def test_log_aggregation(self, test_chain, event_collector):
        number_of_messages = 10
        for _ in range(number_of_messages):
            context, response = create_request_response(
                "sqs",
                "CreateQueue",
                request={"QueueName": "foobar"},
                response={"QueueUrl": "http://localhost:4566/0000000000/foobar"},
            )
            test_chain.handle(context, response)
            time.sleep(0.1)

        api_calls = receive_remaining_events(event_collector, 10)

        # due to the combination of flushing intervals and client times
        # we have no guarantee on the compression level - but there must be some
        assert len(api_calls) < number_of_messages

    def test_logs_subsequent_error_only_once(self, test_chain, event_collector):
        context = create_aws_request_context("sqs", "CreateQueue", {"QueueName": "foobar"})
        context.service_exception = CommonServiceException(
            "InternalError", "test message", status_code=500
        )
        context.internal_request_params = {}  # Mark this as an internal cross-service call

        test_chain.handle(context, Response(status=500))

        # locally flaky when set too low
        event = event_collector.next(timeout=DEFAULT_PRO_FLUSH_INTERVAL_SECS * 2)
        assert event.name == EVENT_NAME
        assert event.metadata.session_id == "test_session_id"
        event_api_calls = event.payload["api_calls"]

        if len(event_api_calls) < 1:
            remaining_requests = receive_remaining_events(event_collector, 1)
            event.payload["api_calls"].append(remaining_requests)

        # if debug is enabled, this contains the entire stack trace which can change when code moves, so an assert is
        # brittle
        err_payload = event.payload["api_calls"][0]
        for key in ["err_msg", "client_time"]:
            err_payload.pop(key, None)

        assert err_payload == {
            "service": "sqs",
            "operation": "CreateQueue",
            "status_code": 500,
            "is_internal": True,
            "region": "us-east-1",
            "account_id": None,
            "user_agent": None,
            "err_type": "InternalError",
            "count": 1,
        }

        # test subsequent error is ignored
        test_chain.handle(context, Response(status=500))
        with pytest.raises(queue.Empty):
            event_collector.next(timeout=1)

        # test that next normal response is logged again
        context, response = create_request_response(
            "sqs",
            "CreateQueue",
            request={"QueueName": "foobar"},
            response={"QueueUrl": "http://localhost:4566/0000000000/foobar"},
        )
        test_chain.handle(context, response)
        event = event_collector.next(timeout=DEFAULT_PRO_FLUSH_INTERVAL_SECS * 2)

        event_api_calls = event.payload["api_calls"]
        if len(event_api_calls) < 1:
            event_api_calls = receive_remaining_events(event_collector, 1)
        assert event_api_calls[0]["operation"] == "CreateQueue"
        assert event_api_calls[0]["status_code"] == 200
