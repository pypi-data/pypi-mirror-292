from localstack.utils.strings import short_uid


def test_get_application(persistence_validations, snapshot, aws_client):
    app_name = f"app-{short_uid()}"
    app_id = aws_client.appconfig.create_application(Name=app_name)["Id"]

    def validate():
        snapshot.match(
            "get_application", aws_client.appconfig.get_application(ApplicationId=app_id)
        )

    persistence_validations.register(validate)
