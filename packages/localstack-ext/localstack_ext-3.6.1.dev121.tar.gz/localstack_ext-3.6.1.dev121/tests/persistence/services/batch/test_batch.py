from localstack.utils.strings import short_uid


def test_describe_compute_environment(persistence_validations, snapshot, aws_client):
    compute_environment_name = f"compute-env-{short_uid()}"
    role_name = f"r-batch-{short_uid()}"
    result = aws_client.iam.create_role(RoleName=role_name, AssumeRolePolicyDocument="{}")
    role_arn = result["Role"]["Arn"]

    aws_client.batch.create_compute_environment(
        computeEnvironmentName=compute_environment_name, type="UNMANAGED", serviceRole=role_arn
    )

    def validate():
        snapshot.match(
            "describe_compute_environment",
            aws_client.batch.describe_compute_environments(
                computeEnvironments=[compute_environment_name]
            ),
        )

    persistence_validations.register(validate)
