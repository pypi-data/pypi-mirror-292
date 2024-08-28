import json
import os
from contextlib import closing

import boto3
import pg8000


def handler(event, context):
    secrets_client = boto3.client("secretsmanager")
    query = event.get("sqlQuery")
    result = secrets_client.get_secret_value(SecretId=os.getenv("RDS_SECRET"))
    secret_details = json.loads(result["SecretString"])
    print(secret_details)
    try:
        dsn = {
            "database": secret_details["dbname"],
            "user": secret_details["username"],
            "password": secret_details["password"],
            "port": secret_details["port"],
            "host": secret_details["host"],
        }
        # workaround: postgres 15 + 16 on AWS don't accept unsecure connection by default
        print(os.getenv("LOCALSTACK_HOSTNAME"))
        use_ssl = None if os.getenv("LOCALSTACK_HOSTNAME") else True
        print(use_ssl)
        connection = pg8000.connect(**dsn, ssl_context=use_ssl)
        return_result = "ok"
        print(f"running query {query}")
        with closing(connection) as conn:
            conn.autocommit = True
            with closing(conn.cursor()) as cursor:
                result = cursor.execute(query)
                print(f"result count: {result.rowcount}")
                if result.rowcount > 0 and query.lower().startswith("select"):
                    return_result = result.fetchall()

        return {"status": "SUCCESS", "results": return_result}
    except Exception as e:
        return {"status": "ERROR", "error": str(e)}
