def test_describe_server(persistence_validations, snapshot, aws_client):
    create_server_response = aws_client.transfer.create_server()
    server_id = create_server_response["ServerId"]

    def validate():
        snapshot.match("describe_server", aws_client.transfer.describe_server(ServerId=server_id))

    persistence_validations.register(validate)
