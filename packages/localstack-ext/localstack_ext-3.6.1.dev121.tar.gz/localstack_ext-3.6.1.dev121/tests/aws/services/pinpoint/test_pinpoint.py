from localstack.testing.pytest import markers
from localstack.utils.strings import short_uid


class TestPinpoint:
    @markers.snapshot.skip_snapshot_verify(
        paths=[
            "$..ApplicationResponse.Arn",
            "$..ApplicationResponse.CreationDate",
            "$..ApplicationResponse.Id",
            "$..ApplicationResponse.tags",
        ]
    )
    @markers.aws.validated
    def test_pinpoint_app_operations(self, aws_client, snapshot):
        client = aws_client.pinpoint
        application_name = f"ExampleCorp-{short_uid()}"

        snapshot.add_transformer(snapshot.transform.regex(application_name, "<application_name>"))

        # Create Pinpoint App
        create_app_response = client.create_app(
            CreateApplicationRequest={"Name": application_name, "tags": {"Stack": "Test"}}
        )

        snapshot.match("create_app_response", create_app_response)

        app_id = create_app_response["ApplicationResponse"]["Id"]

        # Get details of the created Pinpoint App
        get_app_response = client.get_app(ApplicationId=app_id)
        snapshot.match("get_app_response", get_app_response)

        # delete the created Pinpoint App
        delete_app_response = client.delete_app(ApplicationId=app_id)
        snapshot.match("delete_app_response", delete_app_response)
