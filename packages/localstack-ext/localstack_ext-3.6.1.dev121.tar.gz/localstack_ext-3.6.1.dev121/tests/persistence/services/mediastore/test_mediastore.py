from localstack.utils.strings import short_uid


def test_describe_container(persistence_validations, snapshot, aws_client):
    container_name = f"container-{short_uid()}"

    # Create MediaStore Container
    aws_client.mediastore.create_container(ContainerName=container_name)

    # List MediaStore Containers
    def validate():
        snapshot.match("list_containers", aws_client.mediastore.list_containers())

    persistence_validations.register(validate)
