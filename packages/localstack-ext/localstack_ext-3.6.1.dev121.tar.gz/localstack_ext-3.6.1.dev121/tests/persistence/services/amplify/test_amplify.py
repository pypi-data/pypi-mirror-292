from localstack.utils.strings import short_uid


def test_get_app(persistence_validations, snapshot, aws_client):
    app_name = f"app-{short_uid()}"
    app_id = aws_client.amplify.create_app(name=app_name)["app"]["appId"]

    def validate():
        snapshot.match("get_app_id", aws_client.amplify.get_app(appId=app_id))

    persistence_validations.register(validate)
