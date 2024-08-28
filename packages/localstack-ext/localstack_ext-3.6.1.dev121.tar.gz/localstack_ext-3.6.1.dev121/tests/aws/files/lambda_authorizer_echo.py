def handler(event, context):
    print(event)
    if event["version"] == "2.0":
        resource = event["routeArn"]
    else:
        resource = event["methodArn"]

    identity_source = event["identitySource"]

    return {
        "principalId": "abcdef",
        "policyDocument": {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "execute-api:Invoke",
                    "Effect": "Allow",
                    "Resource": f"{resource}",
                }
            ],
        },
        "context": {
            "identitySource": identity_source,
        },
    }
