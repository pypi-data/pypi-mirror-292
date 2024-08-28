from localstack.utils.strings import short_uid


def test_lakeformation_describe_resource(persistence_validations, snapshot, aws_client):
    role_arn = f"arn:aws:iam::000000000000:role/test-role-{short_uid()}"
    resource_arn = aws_client.sns.create_topic(Name=f"t-{short_uid()}")["TopicArn"]
    aws_client.lakeformation.register_resource(ResourceArn=resource_arn, RoleArn=role_arn)

    def validate():
        snapshot.match(
            "lakeformation_describe_resource",
            aws_client.lakeformation.describe_resource(ResourceArn=resource_arn),
        )

    persistence_validations.register(validate)
