import json

import pytest
from localstack.aws.handlers import run_custom_response_handlers
from localstack.http import Request, Router
from localstack.pro.core.utils.cloud_pods.ci_run_manager import (
    CIRunEventsHandler,
    CITraceLogger,
    get_ci_run_manager,
)
from localstack.utils.strings import to_str


@pytest.fixture
def trace_handler():
    handler = CITraceLogger()
    run_custom_response_handlers.append(handler)

    yield handler

    run_custom_response_handlers.remove(handler)
    handler.close()


def test_track_trace_logs(aws_client, trace_handler):
    aws_client.sqs.list_queues()
    aws_client.s3.list_buckets()

    messages = _get_traces(trace_handler, "ci:trace:")

    assert len(messages) == 2
    assert messages[0]["service"] == "sqs"
    assert messages[1]["service"] == "s3"


def test_track_trace_event_logs(aws_client, trace_handler, monkeypatch):
    events_handler = CIRunEventsHandler(trace_handler)
    ci_run_manager = get_ci_run_manager()
    monkeypatch.setattr(ci_run_manager, "ci_project_settings", {"store_traces": True})

    router = Router()
    router.add(events_handler)

    events = [
        {"type": "phase_start", "name": "test1"},
        {"type": "phase_end", "name": "test1", "result": "success"},
        {"type": "phase_start", "name": "test2"},
    ]
    for event in events:
        router.dispatch(
            Request(
                "POST",
                "/_localstack/ci/events",
                body=json.dumps(event),
                headers={"content-type": "application/json"},
            )
        )

    traces = _get_traces(trace_handler, "ci:event:")

    assert len(traces) == 3
    assert traces == events


def _get_traces(trace_handler: CITraceLogger, prefix: str) -> list[dict]:
    messages = []
    logs = trace_handler.get_trace_logs()
    for line in to_str(logs).splitlines():
        if line.startswith(prefix):
            line = line.removeprefix(prefix)
            messages.append(json.loads(line))
    return messages
