import pytest
from localstack.utils.strings import short_uid


@pytest.mark.skip(reason="flaky")
def test_pinpoint(persistence_validations, snapshot, aws_client):
    client = aws_client.pinpoint
    application_name = f"ExampleCorp-{short_uid()}"

    create_app_response = client.create_app(
        CreateApplicationRequest={"Name": application_name, "tags": {"Stack": "Test"}}
    )

    app_id = create_app_response["ApplicationResponse"]["Id"]

    def validate():
        snapshot.match("get_app", client.get_app(ApplicationId=app_id))

    persistence_validations.register(validate)
