import json


def handler(event, context):
    print("Received event: " + str(event))

    headers = {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
        "Access-Control-Allow-Credentials": "true",
    }

    data = event["message"]
    if data == "A":
        response = {"statusCode": 200, "body": json.dumps({"value": "A"}), "headers": headers}
        return response
    raise Exception("error message!")
