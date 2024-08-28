import json

from localstack.testing.pytest import markers
from localstack.utils.aws import arns
from localstack.utils.strings import short_uid

from tests.aws.services.firehose.conftest import (
    get_all_expected_messages_from_s3,
)

TABLE_NAME = "firehose_test"


SAMPLE_USERS = [
    {
        "user_id": "u14a86cdc",
        "name": "Ernst Meier",
        "age": 32,
        "country": "Austria",
        "device_id": "d49b32oed",
        "hr_value": 110,
        "novel_stress_marker": 112.5,
        "timestamp": "2021-10-01 12:00:00",
    },
    {
        "user_id": "u5d34196b",
        "name": "Jane Smith",
        "age": 33,
        "country": "Canada",
        "device_id": "d39d39dp3",
        "hr_value": 110,
        "novel_stress_marker": 112.5,
        "timestamp": "2021-10-01 12:00:00",
    },
]

SAMPLE_USER_DTYPES = {
    "user_id": "VARCHAR(10)",
    "name": "VARCHAR(255)",
    "age": "INT",
    "country": "VARCHAR(50)",
    "device_id": "VARCHAR(10)",
    "hr_value": "INT",
    "novel_stress_marker": "REAL",
    "timestamp": "TIMESTAMP",
}


class TestFirehoseIntegration:
    @markers.aws.unknown
    def test_firehose_redshift_as_target(
        self,
        kinesis_create_stream,
        s3_create_bucket,
        redshift_create_cluster,
        firehose_create_delivery_stream,
        aws_client,
        account_id,
    ):
        # define sample role arn
        role_arn = f"arn:aws:iam::{account_id}:role/Firehose-Role"

        # create kinseis stream
        stream_name = f"test-stream-{short_uid()}"
        kinesis_create_stream(StreamName=stream_name, ShardCount=2)
        stream_arn = aws_client.kinesis.describe_stream(StreamName=stream_name)[
            "StreamDescription"
        ]["StreamARN"]

        # create s3 bucket for intermediate storage
        bucket_name = f"test-bucket-redshift-{short_uid()}"
        s3_create_bucket(Bucket=bucket_name)
        bucket_arn = arns.s3_bucket_arn(bucket_name)

        # create redshift cluster
        redshift_password = "testTest"  # min len 6
        redshift_user = "test"
        cluster_id = f"redshift-{short_uid()}"
        redshift_db_name = f"firehose_test-{short_uid()}"
        redshift_create_cluster(
            cluster_id,
            master_username=redshift_user,
            master_password=redshift_password,
            db_name=redshift_db_name,
        )

        # create firehose redshift destination description
        redshift_s3_destination_configuration = {
            "RoleARN": role_arn,
            "BucketARN": bucket_arn,
            "Prefix": "firehoseTest",
            "CompressionFormat": "UNCOMPRESSED",
        }

        redshift_cluster = aws_client.redshift.describe_clusters()["Clusters"][0]
        redshift_address = redshift_cluster["Endpoint"]["Address"]
        redshift_port = redshift_cluster["Endpoint"]["Port"]
        cluster_jdbcurl = f"jdbc:redshift://{redshift_address}:{redshift_port}/{redshift_db_name}"
        redshift_destination_description = {
            "ClusterJDBCURL": cluster_jdbcurl,
            "CopyCommand": {
                "DataTableName": TABLE_NAME,
                "CopyOptions": "json 'auto' blanksasnull emptyasnull",
                # for reference of copy command options https://docs.aws.amazon.com/redshift/latest/dg/r_COPY_command_examples.html#r_COPY_command_examples-copy-from-json
                # MANIFEST json 'auto' blanksasnull emptyasnull;" required for firehose data,
                "DataTableColumns": f"{','.join(SAMPLE_USER_DTYPES.keys())}",
                # keys in json file from keys in kinesis input must be lower case
            },
            "RoleARN": role_arn,
            "S3Configuration": redshift_s3_destination_configuration,
            "Password": redshift_password,
            "Username": redshift_user,
        }

        # create firehose delivery stream
        delivery_stream_name = f"test-delivery-stream-redshift-{short_uid()}"
        firehose_create_delivery_stream(
            DeliveryStreamName=delivery_stream_name,
            DeliveryStreamType="KinesisStreamAsSource",
            KinesisStreamSourceConfiguration={
                "KinesisStreamARN": stream_arn,
                "RoleARN": role_arn,
            },
            RedshiftDestinationConfiguration=redshift_destination_description,
        )

        # prepare redshift table
        create_table_sql = f"""
                            CREATE TABLE {TABLE_NAME} (
                            user_id {SAMPLE_USER_DTYPES["user_id"]},
                            name {SAMPLE_USER_DTYPES["name"]},
                            age {SAMPLE_USER_DTYPES["age"]} ,
                            country {SAMPLE_USER_DTYPES["country"]},
                            device_id {SAMPLE_USER_DTYPES["device_id"]},
                            hr_value {SAMPLE_USER_DTYPES["hr_value"]},
                            novel_stress_marker {SAMPLE_USER_DTYPES["novel_stress_marker"]},
                            timestamp {SAMPLE_USER_DTYPES["timestamp"]}
                        );
                    """
        execute_statement = {
            "Sql": create_table_sql,
            "Database": redshift_db_name,
            "ClusterIdentifier": cluster_id,  # cluster_identifier in cluster create
        }
        response = aws_client.redshift_data.execute_statement(**execute_statement)
        assert response["ResponseMetadata"]["HTTPStatusCode"] == 200

        # insert data into kinesis stream
        for sample_user in SAMPLE_USERS:
            aws_client.kinesis.put_record(
                StreamName=stream_name,
                Data=json.dumps(sample_user),
                PartitionKey="1",
            )

        # check if data is in intermediary bucket
        bucket_data = get_all_expected_messages_from_s3(
            aws_client,
            bucket_name,
            expected_message_count=len(SAMPLE_USERS),
        )
        assert bucket_data == SAMPLE_USERS

        # read data from redshift
        read_table_sql = f"""
                    SELECT
                        *
                    FROM
                        {TABLE_NAME}
                    """
        execute_statement = {
            "Sql": read_table_sql,
            "Database": redshift_db_name,
            "ClusterIdentifier": cluster_id,  # cluster_identifier in cluster create
        }

        response = aws_client.redshift_data.execute_statement(**execute_statement)
        execute_statement_id = response["Id"]
        assert response["ResponseMetadata"]["HTTPStatusCode"] == 200
        response = aws_client.redshift_data.describe_statement(Id=execute_statement_id)
        assert response["Status"] == "FINISHED"
        result_response = aws_client.redshift_data.get_statement_result(Id=execute_statement_id)

        # check if data in redshift equal input data
        for column in result_response["ColumnMetadata"]:
            assert column["name"] in SAMPLE_USERS[0].keys()
        for row, user in zip(result_response["Records"], SAMPLE_USERS):
            for row_dict, user_value in zip(row, user.values()):
                row_value = next(iter(row_dict.values()))
                assert row_value == user_value
