import json
import logging

import pandas as pd
import psycopg2
from localstack.utils.sync import retry

LOG = logging.getLogger(__name__)


def read_s3_data(aws_client, bucket_name: str) -> dict[str, str]:
    response = aws_client.s3.list_objects(Bucket=bucket_name)
    if response.get("Contents") is None:
        raise Exception("No data in bucket yet")

    keys = [obj.get("Key") for obj in response.get("Contents")]

    bucket_data = dict()
    for key in keys:
        response = aws_client.s3.get_object(Bucket=bucket_name, Key=key)
        data = response["Body"].read().decode("utf-8")
        bucket_data[key] = data
    return bucket_data


def get_all_expected_messages_from_s3(
    aws_client,
    bucket_name: str,
    sleep: int = 5,
    retries: int = 15,
    expected_message_count: int | None = None,
) -> list[str]:
    def get_all_messages():
        bucket_data = read_s3_data(aws_client, bucket_name)
        messages = []
        for input_string in bucket_data.values():
            json_array_string = "[" + input_string.replace("}{", "},{") + "]"
            message = json.loads(json_array_string)
            LOG.debug(f"Received messages: {message}")
            messages.extend(message)
        if expected_message_count is not None and len(messages) != expected_message_count:
            raise Exception(f"Failed to receive all sent messages: {messages}")
        else:
            return messages

    all_messages = retry(get_all_messages, sleep=sleep, retries=retries)
    return all_messages


def redshift_connection_handler(connection_string, sql_command):
    try:
        conn = psycopg2.connect(connection_string)
        cursor = conn.cursor()
        cursor.execute(sql_command)
        conn.commit()
        cursor.close()
        conn.close()
        return {"status": "command executed successfully", "status_code": 200}
    except Exception as e:
        # Assuming 500 as a generic server error status code for any exception
        return {"status": "error", "error": str(e), "status_code": 500}


def redshift_read_table(connection_string, sql_query):
    try:
        conn = psycopg2.connect(connection_string)
        cursor = conn.cursor()
        records = pd.read_sql(sql_query, conn)
        cursor.close()
        conn.close()
        return records
    except Exception as e:
        return {"status": "error", "error": str(e)}


def get_expected_data_from_redshift_table(
    connection_string: str,
    sql_query: str,
    expected_row_count: int,
    retries: int = 30,
    sleep: int = 10,
) -> pd.DataFrame:
    def get_data():
        df = redshift_read_table(connection_string, sql_query)
        if df.shape[0] != expected_row_count:
            raise Exception(f"Failed to receive all expected rows: {df}")
        else:
            return df

    return retry(get_data, retries, sleep)
