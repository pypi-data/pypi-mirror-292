from localstack.utils.strings import short_uid


def test_appsync_get_graphql_api(persistence_validations, snapshot, aws_client):
    api_name = f"apin-{short_uid()}"
    api_id = aws_client.appsync.create_graphql_api(name=api_name, authenticationType="API_KEY")[
        "graphqlApi"
    ]["apiId"]

    def validate():
        snapshot.match("get_graphql_api", aws_client.appsync.get_graphql_api(apiId=api_id))

    persistence_validations.register(validate)
