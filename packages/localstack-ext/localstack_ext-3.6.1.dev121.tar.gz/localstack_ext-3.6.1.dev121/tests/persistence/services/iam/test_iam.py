from localstack.utils.strings import short_uid


def test_create_get_user(persistence_validations, snapshot, aws_client):
    user = f"user-{short_uid()}"
    aws_client.iam.create_user(UserName=user)

    def validate():
        snapshot.match("create_get_user", aws_client.iam.get_user(UserName=user))

    persistence_validations.register(validate)
