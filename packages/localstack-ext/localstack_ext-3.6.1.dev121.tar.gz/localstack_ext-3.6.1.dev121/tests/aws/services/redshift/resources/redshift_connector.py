import os

import redshift_connector


def handler(event, context):
    try:
        user = "admin"
        database = "default_db"
        table_name = "mytable"
        endpoint = os.environ["REDSHIFT_ENDPOINT"]
        host, port = endpoint.split(":")
        print(f"Endpoint is {host}:{port}")
        password = os.environ["CLUSTER_PASSWORD"]
        conn = redshift_connector.connect(
            database=database, host=host, port=port, user=user, password=password
        )
        print("connection established")
        with conn:
            conn.autocommit = True
            with conn.cursor() as cursor:
                print(f"create table {table_name}")
                cursor.execute(f"CREATE TABLE {table_name}(id int)")
                print("execute insert")
                cursor.execute(f"INSERT INTO {table_name}(id) VALUES (123)")
                print("execute select")
                query = cursor.execute(f"SELECT * FROM {table_name}")
                print("Query executed")
                assert query.fetchone() == [123]
                return {"responseMessage": "Query successfully executed"}
    except Exception as e:
        return {"responseMessage": f"An Error occurred: {e}"}
