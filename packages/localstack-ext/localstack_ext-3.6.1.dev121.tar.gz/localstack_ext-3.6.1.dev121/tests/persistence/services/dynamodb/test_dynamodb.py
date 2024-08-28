from localstack.utils.strings import short_uid


def test_create_and_scan_table(
    persistence_validations, snapshot, dynamodb_wait_for_table_active, aws_client
):
    table_name = f"table_{short_uid()}"
    aws_client.dynamodb.create_table(
        TableName=table_name,
        KeySchema=[{"AttributeName": "Username", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "Username", "AttributeType": "S"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    dynamodb_wait_for_table_active(table_name=table_name, client=aws_client.dynamodb)
    aws_client.dynamodb.put_item(TableName=table_name, Item={"Username": {"S": "persistence-user"}})

    def validate():
        dynamodb_wait_for_table_active(table_name=table_name, client=aws_client.dynamodb)

        snapshot.match("describe-table", aws_client.dynamodb.describe_table(TableName=table_name))

        scan = aws_client.dynamodb.scan(TableName=table_name)
        snapshot.match("scan", scan)

    persistence_validations.register(validate)


def test_dynamodb_streams(
    persistence_validations, snapshot, aws_client, dynamodb_wait_for_table_active
):
    table_name = f"table_{short_uid()}"
    aws_client.dynamodb.create_table(
        TableName=table_name,
        KeySchema=[{"AttributeName": "Username", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "Username", "AttributeType": "S"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
        StreamSpecification={"StreamViewType": "NEW_AND_OLD_IMAGES", "StreamEnabled": True},
    )

    dynamodb_wait_for_table_active(table_name=table_name, client=aws_client.dynamodb)

    def validate():
        dynamodb_wait_for_table_active(table_name=table_name, client=aws_client.dynamodb)
        streams: list[dict] = [
            _stream
            for _stream in aws_client.dynamodbstreams.list_streams()["Streams"]
            if _stream["TableName"] == table_name
        ]
        assert streams

    persistence_validations.register(validate)
