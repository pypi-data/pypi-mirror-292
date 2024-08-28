from localstack.utils.strings import short_uid


def test_athena_get_named_query(persistence_validations, snapshot, aws_client):
    query_name = f"query-{short_uid()}"
    query_id = aws_client.athena.create_named_query(
        Name=query_name, Database="T-DB", QueryString="SELECT 1, 2, 3"
    )["NamedQueryId"]

    def validate():
        snapshot.match(
            "athena_named_query", aws_client.athena.get_named_query(NamedQueryId=query_id)
        )

    persistence_validations.register(validate)
