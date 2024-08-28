import json

import boto3


def create_api_client(domain_name, stage):
    return boto3.client("apigatewaymanagementapi", endpoint_url=f"https://{domain_name}/{stage}")


def handler(event, *args):
    print(event)
    req_context = event["requestContext"]
    route = req_context["routeKey"]
    connection_id = req_context["connectionId"]
    domain_name = req_context["domainName"]
    stage = req_context["stage"]

    if route == "$connect":
        return {"statusCode": 200, "body": "connected"}
    elif route == "$disconnect":
        return {"statusCode": 200, "body": "disconnected"}

    s3_client = boto3.client("s3")
    try:
        bucket = json.loads(event["body"])["bucket"]
        s3_client.put_object(Bucket=bucket, Key=f"conn.{connection_id}", Body=b"")
    except Exception as e:
        print(e)
        pass
    # send additional message via API GW management client
    create_api_client(domain_name=domain_name, stage=stage).post_to_connection(
        ConnectionId=connection_id, Data=b'{"action":"_lambda_"}'
    )

    return {"statusCode": 200, "body": json.dumps(event)}
