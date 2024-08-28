import json

import boto3


def handler(event, context):
    print("Received event: " + str(event))
    print("Received context: " + str(context))

    req_context = event["requestContext"]
    route = req_context["routeKey"]
    connection_id = req_context["connectionId"]
    domain_name = req_context["domainName"]
    stage = req_context["stage"]
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
        "Access-Control-Allow-Credentials": "true",
    }

    if route == "$connect":
        return {"statusCode": 200, "headers": headers, "body": "connected"}
    elif route == "$disconnect":
        return {"statusCode": 200, "headers": headers, "body": "disconnected"}

    data = json.loads(event["body"])
    create_api_client(env=data.get("env"), domain_name=domain_name, stage=stage).post_to_connection(
        Data='{"message": "%s"}' % route,
        ConnectionId=connection_id,
    )
    return {"statusCode": 200, "headers": headers, "body": route}


def create_api_client(env, domain_name, stage):
    if env == "local":
        return boto3.client("apigatewaymanagementapi")
    return boto3.client("apigatewaymanagementapi", endpoint_url=f"https://{domain_name}/{stage}")
