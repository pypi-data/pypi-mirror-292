def handler(event, context):
    resource = event["methodArn"]
    auth_header = event["authorizationToken"]

    effect = "Allow" if auth_header == "allow" else "Deny"
    return {
        "principalId": "abcdef",
        "policyDocument": {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "execute-api:Invoke",
                    "Effect": effect,
                    "Resource": f"{resource}",
                }
            ],
        },
    }
