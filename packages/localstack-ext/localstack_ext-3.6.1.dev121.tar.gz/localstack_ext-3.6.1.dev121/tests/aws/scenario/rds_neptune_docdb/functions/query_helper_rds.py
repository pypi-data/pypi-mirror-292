import json
import os
from contextlib import closing

import boto3
import pg8000


def handler(event, context):
    if os.environ.get("AWS_ENDPOINT_URL"):
        secrets_client = boto3.client("secretsmanager", endpoint_url=os.environ["AWS_ENDPOINT_URL"])
    else:
        secrets_client = boto3.client("secretsmanager")

    query = event.get("sqlQuery")
    result = secrets_client.get_secret_value(SecretId=os.getenv("RDS_SECRET"))
    secret_details = json.loads(result["SecretString"])

    try:
        dsn = {
            "database": secret_details["dbname"],
            "user": secret_details["username"],
            "password": secret_details["password"],
            "port": secret_details["port"],
            "host": secret_details["host"],
        }

        connection = pg8000.connect(**dsn)
        return_result = "ok"
        with closing(connection) as conn:
            conn.autocommit = True
            with closing(conn.cursor()) as cursor:
                result = cursor.execute(query)
                if result.rowcount > 0 and query.lower().startswith("select"):
                    return_result = result.fetchall()

        return {"status": "SUCCESS", "results": return_result}
    except Exception as e:
        return {"status": "ERROR", "error": str(e)}
