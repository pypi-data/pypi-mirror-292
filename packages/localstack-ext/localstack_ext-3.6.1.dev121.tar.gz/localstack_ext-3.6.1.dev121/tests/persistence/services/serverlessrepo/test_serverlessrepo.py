from localstack.utils.strings import short_uid


def test_serverlessrepo_get_application(persistence_validations, snapshot, aws_client):
    repo_id = aws_client.serverlessrepo.create_application(
        Author="sample-author", Description="sample", Name=f"name-{short_uid()}"
    )["ApplicationId"]

    def validate():
        snapshot.match(
            "serverlessrepo_get_application",
            aws_client.serverlessrepo.get_application(ApplicationId=repo_id),
        )

    persistence_validations.register(validate)
