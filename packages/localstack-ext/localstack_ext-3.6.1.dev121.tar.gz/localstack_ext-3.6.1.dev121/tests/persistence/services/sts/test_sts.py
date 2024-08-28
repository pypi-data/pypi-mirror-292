from localstack.utils.strings import short_uid


def test_assume_role(aws_client, persistence_validations, snapshot):
    iam = aws_client.iam

    user = f"localstack-user-{short_uid()}"
    iam.create_user(UserName=user)

    role_name = "localstack-role"
    iam.create_access_key(UserName=user)
    response = iam.create_role(
        RoleName=role_name,
        AssumeRolePolicyDocument='{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":{"AWS":"arn:aws:iam::000000000000:root"},"Action":"sts:AssumeRole"}]}',
    )
    role_arn = response["Role"]["Arn"]
    iam.attach_role_policy(
        RoleName=role_name, PolicyArn="arn:aws:iam::aws:policy/AdministratorAccess"
    )

    def validation():
        response = aws_client.sts.assume_role(
            RoleArn=role_arn, RoleSessionName="localstack-sessions"
        )
        arn = response["AssumedRoleUser"]["Arn"]
        snapshot.match("sts-arn", arn)

    persistence_validations.register(validation)
