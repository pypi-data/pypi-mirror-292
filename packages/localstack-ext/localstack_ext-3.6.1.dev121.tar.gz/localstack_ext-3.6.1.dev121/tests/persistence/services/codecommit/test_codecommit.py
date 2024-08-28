from localstack.utils.strings import short_uid


def test_codecommit_get_repository(persistence_validations, snapshot, aws_client):
    repository_name = f"name-{short_uid()}"
    aws_client.codecommit.create_repository(repositoryName=repository_name)

    def validate():
        snapshot.match(
            "get_repository", aws_client.codecommit.get_repository(repositoryName=repository_name)
        )

    persistence_validations.register(validate)
