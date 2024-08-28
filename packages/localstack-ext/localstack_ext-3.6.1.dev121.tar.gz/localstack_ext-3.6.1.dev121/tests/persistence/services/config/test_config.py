from localstack.utils.strings import short_uid


def test_describe_config(persistence_validations, snapshot, aws_client):
    s3_bucket_name = f"config-test-{short_uid()}"
    sns_topic_name = f"config-test-topic-{short_uid()}"
    role_arn = "arn:aws:iam::000000000000:role/config-role"

    # Create S3 Bucket
    aws_client.s3.create_bucket(Bucket=s3_bucket_name)

    # Create SNS Topic
    sns_response = aws_client.sns.create_topic(Name=sns_topic_name)
    sns_topic_arn = sns_response["TopicArn"]

    # Put Configuration Recorder
    aws_client.config.put_configuration_recorder(
        ConfigurationRecorder={"name": "default", "roleARN": role_arn}
    )

    # Put Delivery Channel
    aws_client.config.put_delivery_channel(
        DeliveryChannel={
            "name": "default",
            "s3BucketName": s3_bucket_name,
            "snsTopicARN": sns_topic_arn,
            "configSnapshotDeliveryProperties": {"deliveryFrequency": "Twelve_Hours"},
        }
    )

    # Start Configuration Recorder
    aws_client.config.start_configuration_recorder(ConfigurationRecorderName="default")

    # Describe Delivery Channels
    def validate_delivery_channels():
        snapshot.match("describe_delivery_channels", aws_client.config.describe_delivery_channels())

    # Describe Configuration Recorder Status
    def validate_config_recorder_status():
        snapshot.match(
            "describe_config_recorder_status",
            aws_client.config.describe_configuration_recorder_status(),
        )

    persistence_validations.register(validate_delivery_channels)
    persistence_validations.register(validate_config_recorder_status)
