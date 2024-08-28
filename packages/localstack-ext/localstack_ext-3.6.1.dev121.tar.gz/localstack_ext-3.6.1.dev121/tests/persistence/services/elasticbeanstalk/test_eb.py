from localstack.utils.strings import short_uid


def test_elasticbeanstalk_create_and_describe_application(
    persistence_validations, snapshot, aws_client
):
    application_name = f"my-app-{short_uid()}"

    # Create Elastic Beanstalk Application
    aws_client.elasticbeanstalk.create_application(ApplicationName=application_name)

    # Describe Elastic Beanstalk Applications
    def validate_describe_applications():
        snapshot.match(
            "describe_applications",
            aws_client.elasticbeanstalk.describe_applications(ApplicationNames=[application_name]),
        )

    persistence_validations.register(validate_describe_applications)
