import time

from localstack.utils.strings import short_uid


def test_kinesis_describe_stream(persistence_validations, snapshot, aws_client):
    stream_name = f"ks-{short_uid()}"
    aws_client.kinesis.create_stream(StreamName=stream_name, ShardCount=1)
    # Note: there is a delay between creating the service and writing to persistence, default
    #   $PERSIST_INTERVAL in kinesis-mock is 5s - TODO find a way to flush Kinesis state on shutdown
    time.sleep(5.5)

    def validate():
        snapshot.match(
            "describe_stream", aws_client.kinesis.describe_stream(StreamName=stream_name)
        )

    persistence_validations.register(validate)


def test_kinesis_get_records(persistence_validations, snapshot, wait_for_stream_ready, aws_client):
    stream_name = f"ks-{short_uid()}"
    aws_client.kinesis.create_stream(StreamName=stream_name, ShardCount=1)
    wait_for_stream_ready(stream_name)

    stream_description = aws_client.kinesis.describe_stream(StreamName=stream_name)[
        "StreamDescription"
    ]
    shard_id = stream_description.get("Shards")[0].get("ShardId")
    sequence_number = (
        stream_description.get("Shards")[0].get("SequenceNumberRange").get("StartingSequenceNumber")
    )
    dummy_data = {"persistence", "tests", "are", "cool"}
    for _data in dummy_data:
        aws_client.kinesis.put_record(
            StreamName=stream_name,
            Data=_data,
            PartitionKey="1",
        )
    time.sleep(5.5)

    def validate():
        shard_iterator = aws_client.kinesis.get_shard_iterator(
            StreamName=stream_name,
            ShardId=shard_id,
            ShardIteratorType="AT_SEQUENCE_NUMBER",
            StartingSequenceNumber=sequence_number,
        )["ShardIterator"]

        response_records = aws_client.kinesis.get_records(ShardIterator=shard_iterator).get(
            "Records"
        )
        response_records.sort(key=lambda k: k.get("Data"))
        snapshot.match("Records", response_records)

    persistence_validations.register(validate)
