import json
import time

from localstack.utils.strings import short_uid


def test_describe_xray_trace(persistence_validations, snapshot, aws_client):
    current_time = int(time.time())
    hex_time = format(current_time, "x")
    guid = short_uid()
    trace_id = f"1-{hex_time}-{guid}"
    end_time = current_time + 3

    # Create a trace segment document
    trace_segment_document = {
        "trace_id": trace_id,
        "id": "6226467e3f845502",
        "start_time": f"{current_time}.37518",
        "end_time": f"{end_time}.4042",
        "name": "test.elasticbeanstalk.com",
    }

    trace_segment_json = json.dumps(trace_segment_document)

    # Send trace segment to X-Ray API
    aws_client.xray.put_trace_segments(TraceSegmentDocuments=[trace_segment_json])

    # Get trace summaries
    def validate_trace_summaries():
        snapshot.match(
            "get_trace_summaries",
            aws_client.xray.get_trace_summaries(StartTime=current_time - 600, EndTime=current_time),
        )

    # Batch get traces by trace ID
    def validate_batch_get_traces():
        snapshot.match("batch_get_traces", aws_client.xray.batch_get_traces(TraceIds=[trace_id]))

    persistence_validations.register(validate_trace_summaries)
    persistence_validations.register(validate_batch_get_traces)
