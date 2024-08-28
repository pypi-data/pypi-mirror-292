import os
from typing import Optional

# TODO: seems like we're using `mysql-connector-python` as well as `pymysql` - unify?
import mysql.connector
import pytest
from localstack.testing.aws.util import is_aws_cloud
from localstack.testing.pytest import markers
from localstack.utils.strings import get_random_hex
from localstack.utils.sync import retry
from python_terraform import IsNotFlagged, Terraform


@pytest.fixture
def deploy_terraform():
    terraform_client = Terraform()

    def _apply(terraform_dir: Optional[str] = None, variables: Optional[dict] = None):
        terraform_client.variables = variables
        terraform_client.working_dir = os.path.realpath(terraform_dir)
        terraform_client.init(capture_output="yes", no_color=IsNotFlagged)
        terraform_client.apply(capture_output="yes", no_color=IsNotFlagged, skip_plan=True)
        return terraform_client.output()

    yield _apply

    terraform_client.destroy(
        capture_output="yes", no_color=IsNotFlagged, force=IsNotFlagged, auto_approve=True
    )


@pytest.mark.skipif(not is_aws_cloud(), reason="DMS service not implemented in LocalStack")
@markers.aws.validated
def test_dms_rds_kinesis(deploy_terraform, snapshot, aws_client):
    # NOTE:
    # - Update the "profile" name in the terraform file to use the correct profile: ./dms_rds_kinesis/dms_rds_kinesis.tf

    snapshot.add_transformer(snapshot.transform.dms_api())
    snapshot.add_transformer(
        snapshot.transform.key_value("SubnetIdentifier"),
    )
    db_name = "test"
    db_pass = get_random_hex(18)
    db_user = "admin"
    db_table = "test"

    variables = {
        "region_name": "us-east-1",
        "db_name": db_name,
        "db_pass": db_pass,
        "db_user": db_user,
    }

    output = deploy_terraform(terraform_dir="dms_rds_kinesis", variables=variables)
    kinesis_stream_arn = output["kinesis_stream_arn"]["value"]
    rds_endpoint = output["rds_endpoint"]["value"]
    replication_task_arn = output["replication_task_arn"]["value"]
    dms_source_endpoint_arn = output["dms_source_endpoint_arn"]["value"]
    dms_target_endpoint_arn = output["dms_target_endpoint_arn"]["value"]
    dms_replication_instance_arn = output["dms_replication_instance_arn"]["value"]

    res_target_describe_endpoints = aws_client.dms.describe_endpoints(
        Filters=[
            {
                "Name": "endpoint-arn",
                "Values": [dms_target_endpoint_arn],
            },
        ]
    )
    snapshot.match("target_describe_endpoints", res_target_describe_endpoints)

    res_source_describe_endpoints = aws_client.dms.describe_endpoints(
        Filters=[
            {
                "Name": "endpoint-arn",
                "Values": [dms_source_endpoint_arn],
            },
        ]
    )
    snapshot.match("source_describe_endpoints", res_source_describe_endpoints)

    res_describe_replication_instance = aws_client.dms.describe_replication_instances(
        Filters=[
            {
                "Name": "replication-instance-arn",
                "Values": [dms_replication_instance_arn],
            },
        ]
    )
    snapshot.match("describe_replication_instance", res_describe_replication_instance)

    response = aws_client.dms.describe_endpoint_settings(
        EngineName="mysql",
    )
    snapshot.match("mysql_describe_endpoint_settings", response)

    response = aws_client.dms.describe_endpoint_settings(
        EngineName="kinesis",
    )
    snapshot.match("kinesis_describe_endpoint_settings", response)

    config = {
        "user": db_user,
        "password": db_pass,
        "host": rds_endpoint,
        "database": db_name,
    }

    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()

    cursor.execute(f"USE {db_name}")
    cursor.execute(
        f"CREATE TABLE {db_table} (id INT NOT NULL AUTO_INCREMENT, name VARCHAR(255), PRIMARY KEY (id))"
    )

    for i in range(2):
        cursor.execute(f"INSERT INTO {db_table} (name) VALUES ('value{i}')")
    cnx.commit()

    cursor.close()
    cnx.close()

    def _dms_replication_task_status(status: str):
        res = aws_client.dms.describe_replication_tasks(
            Filters=[
                {
                    "Name": "replication-task-arn",
                    "Values": [replication_task_arn],
                }
            ],
            WithoutSettings=True,
        )
        assert len(res["ReplicationTasks"]) == 1
        assert res["ReplicationTasks"][0]["Status"] == status

    retry(_dms_replication_task_status, retries=100, sleep=5, status="ready")

    res_describe_replication_tasks = aws_client.dms.describe_replication_tasks(
        Filters=[
            {
                "Name": "replication-task-arn",
                "Values": [replication_task_arn],
            },
        ],
        WithoutSettings=True,
    )
    snapshot.match("describe_replication_tasks", res_describe_replication_tasks)

    res_start_replication_task = aws_client.dms.start_replication_task(
        ReplicationTaskArn=replication_task_arn, StartReplicationTaskType="start-replication"
    )
    snapshot.match("start_replication_task", res_start_replication_task)

    retry(_dms_replication_task_status, retries=200, sleep=5, status="stopped")

    def _describe_table_statistics():
        res = aws_client.dms.describe_table_statistics(
            ReplicationTaskArn=replication_task_arn,
        )
        assert len(res["TableStatistics"]) == 1
        assert res["TableStatistics"][0]["FullLoadRows"] == 2

    retry(_describe_table_statistics, retries=100, sleep=5)

    shard_id = aws_client.kinesis.describe_stream(StreamARN=kinesis_stream_arn)[
        "StreamDescription"
    ]["Shards"][0]["ShardId"]

    def _get_records():
        shard_iterator = aws_client.kinesis.get_shard_iterator(
            StreamARN=kinesis_stream_arn,
            ShardId=shard_id,
            ShardIteratorType="TRIM_HORIZON",
        )
        shard_iter = shard_iterator["ShardIterator"]
        record_count = 0
        while shard_iter is not None:
            res = aws_client.kinesis.get_records(ShardIterator=shard_iter, Limit=10)
            shard_iter = res["NextShardIterator"]
            records = res["Records"]
            record_count += len(records)
            if record_count >= 4:
                break
        assert record_count == 4

    retry(_get_records, retries=100, sleep=5)

    res_describe_table_statistics = aws_client.dms.describe_table_statistics(
        ReplicationTaskArn=replication_task_arn,
    )
    snapshot.match("describe_table_statistics", res_describe_table_statistics)
