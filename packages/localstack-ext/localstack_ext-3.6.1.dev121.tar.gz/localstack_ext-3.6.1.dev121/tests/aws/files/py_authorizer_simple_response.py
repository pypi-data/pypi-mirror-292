def handler(event, context):
    print(event)

    # context from the authorizer will be passed into the request input of the integration
    return {
        "isAuthorized": True,
        "context": {
            "userId": 42,
            "Content-Type": "application/json",
            "accountAlias": "account-alias",
            "accountId": "account-id",
            "projectId": "project-id",
            "permissions": "test-permissions",
            "tenantId": "tenant-id",
        },
    }
