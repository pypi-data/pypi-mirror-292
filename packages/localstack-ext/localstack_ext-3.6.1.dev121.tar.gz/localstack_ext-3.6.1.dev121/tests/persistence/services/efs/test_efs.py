def test_efs_describe_file_system(persistence_validations, snapshot, aws_client):
    efs_id = aws_client.efs.create_file_system()["FileSystemId"]

    def validate():
        snapshot.match(
            "describe_file_system", aws_client.efs.describe_file_systems(FileSystemId=efs_id)
        )

    persistence_validations.register(validate)
