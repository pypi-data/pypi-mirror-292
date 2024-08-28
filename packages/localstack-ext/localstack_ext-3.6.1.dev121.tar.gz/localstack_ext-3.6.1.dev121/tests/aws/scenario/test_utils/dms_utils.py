import json
from typing import TYPE_CHECKING, Callable, Literal, Optional

import pymysql

AssertFunctionType = Callable[[str], None]

if TYPE_CHECKING:
    from mypy_boto3_dms import DatabaseMigrationServiceClient
    from mypy_boto3_kinesis import KinesisClient

DEFAULT_TARGET_TYPE = "default"
NON_DEFAULT_TARGET_TYPE = "non_default"
UNFORMATTED_JSON_TARGET_TYPE = "unformatted_json"


def dict_contains_subdict(original_dict: dict, sub_dict: dict) -> bool:
    return all(original_dict.get(k) == v for k, v in sub_dict.items())


def transform_kinesis_data(
    kinesis_input: list[dict],
    assert_exec: AssertFunctionType = None,
    sorting_type: Literal["cdc", "full-load"] = "full-load",
) -> list[dict]:
    for record in kinesis_input:
        json_str = record["Data"].decode("utf-8").strip()
        if assert_exec:
            assert_exec(json_str)
        record["Data"] = json.loads(json_str)

    def _sorting_key(x):
        if sorting_type == "cdc":
            metadata = x["Data"]["metadata"]
            table_name = metadata.get("table-name", "")
            if metadata["record-type"] == "control" and metadata["operation"] == "create-table":
                if table_name == "awsdms_apply_exceptions":
                    return 0, ""
                else:
                    return 1, table_name
            return 2, metadata["timestamp"]

        prefix = ""
        if x["Data"]["metadata"]["record-type"] == "control":
            # Control type PartitionKey starts with the task id, which can change their order in between runs
            prefix = "_ZZZ"
        return prefix + x["PartitionKey"] + x["Data"]["metadata"]["timestamp"]

    sorted_data = sorted(
        kinesis_input,
        key=_sorting_key,
    )
    return sorted_data


def assert_dms_replication_task_status(
    dms_client: "DatabaseMigrationServiceClient",
    replication_task_arn: str,
    expected_status: str,
    wait_for_task_stats: bool = False,
):
    res = dms_client.describe_replication_tasks(
        Filters=[
            {
                "Name": "replication-task-arn",
                "Values": [replication_task_arn],
            }
        ],
        WithoutSettings=True,
    )
    assert len(res["ReplicationTasks"]) == 1
    assert res["ReplicationTasks"][0]["Status"] == expected_status
    if wait_for_task_stats:
        assert res["ReplicationTasks"][0].get("ReplicationTaskStats")
    return res


def assert_dms_replication_config_status(
    dms_client: "DatabaseMigrationServiceClient",
    replication_config_arn: str,
    expected_status: str,
    expected_provision_state: Optional[str] = None,
):
    res = dms_client.describe_replications(
        Filters=[
            {
                "Name": "replication-config-arn",
                "Values": [replication_config_arn],
            }
        ],
    )
    assert len(res["Replications"]) == 1
    assert res["Replications"][0]["Status"] == expected_status
    if expected_provision_state:
        assert res["Replications"][0]["ProvisionData"]["ProvisionState"] == expected_provision_state
    return res


def describe_table_statistics(
    dms_client: "DatabaseMigrationServiceClient", replication_task_arn: str
):
    res = dms_client.describe_table_statistics(
        ReplicationTaskArn=replication_task_arn,
    )
    res["TableStatistics"] = sorted(
        res["TableStatistics"], key=lambda x: (x["SchemaName"], x["TableName"])
    )
    return res


def describe_replication_table_statistics(
    dms_client: "DatabaseMigrationServiceClient", replication_config_arn: str
):
    res = dms_client.describe_replication_table_statistics(
        ReplicationConfigArn=replication_config_arn,
    )
    res["ReplicationTableStatistics"] = sorted(
        res["ReplicationTableStatistics"], key=lambda x: (x["SchemaName"], x["TableName"])
    )
    return res


def get_records_from_shard(
    kinesis_client: "KinesisClient",
    stream_arn: str,
    threshold_timestamp: float,
    expected_count: int,
):
    shard_id = kinesis_client.describe_stream(StreamARN=stream_arn)["StreamDescription"]["Shards"][
        0
    ]["ShardId"]
    shard_iterator = kinesis_client.get_shard_iterator(
        StreamARN=stream_arn,
        ShardId=shard_id,
        ShardIteratorType="TRIM_HORIZON",
    )
    shard_iter = shard_iterator["ShardIterator"]
    all_records = []
    while shard_iter is not None:
        res = kinesis_client.get_records(ShardIterator=shard_iter, Limit=50)
        shard_iter = res["NextShardIterator"]
        records = res["Records"]
        for r in records:
            if r["ApproximateArrivalTimestamp"].timestamp() > threshold_timestamp:
                all_records.append(r)
        if len(all_records) >= expected_count:
            break

    assert len(all_records) == expected_count
    return all_records


def assert_json_formatting(json_formatted: bool) -> AssertFunctionType:
    def _assert(statement: bool):
        assert statement

    if json_formatted:
        return lambda x: _assert(x.startswith("{\n\t"))
    return lambda x: _assert(x.startswith('{"'))


def run_queries_on_mysql(
    host: str,
    queries: list[str],
    database: str,
    user: str,
    password: str,
    port: int = None,
):
    db_config = {
        "user": user,
        "password": password,
        "host": host,
        "database": database,
        "cursorclass": pymysql.cursors.DictCursor,
    }
    if port:
        db_config["port"] = int(port)
    cursor = None
    cnx = None
    try:
        cnx = pymysql.connect(**db_config)
        cursor = cnx.cursor()
        for query in queries:
            cursor.execute(query)
        cnx.commit()
    finally:
        if cursor:
            cursor.close()
        if cnx:
            cnx.close()
