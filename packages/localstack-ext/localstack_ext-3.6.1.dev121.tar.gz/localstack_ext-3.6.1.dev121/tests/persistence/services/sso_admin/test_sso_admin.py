from localstack.utils.strings import short_uid


def test_sso_admin(persistence_validations, snapshot, aws_client):
    instance_arn = f"arn:aws:sso:::instance/your-instance-arn-{short_uid()}"
    response = aws_client.sso_admin.create_permission_set(
        Name=f"{short_uid()}", InstanceArn=instance_arn, Description="something something"
    )

    def validate():
        snapshot.match(
            "list_permission_sets",
            aws_client.sso_admin.list_permission_sets(InstanceArn=instance_arn),
        )

    persistence_validations.register(validate)
