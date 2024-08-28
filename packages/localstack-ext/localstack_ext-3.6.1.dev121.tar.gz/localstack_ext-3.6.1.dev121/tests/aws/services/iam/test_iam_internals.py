import json
import logging
import os

import pytest
from localstack.aws.api.lambda_ import Runtime
from localstack.pro.core.services.iam.policy_engine.engine import (
    ActionResourceExtractor,
    IAMEnforcementEngine,
)
from localstack.pro.core.services.iam.policy_engine.iam_service_plugin import IAMPluginManager
from localstack.pro.core.services.iam.policy_engine.identity_policy_retrieval import (
    AssumedRole,
    Role,
    Root,
    User,
)
from localstack.pro.core.services.iam.policy_engine.resource_policy_retrieval import (
    ResourcePolicyRetriever,
)
from localstack.testing.aws.util import RequestContextClient, create_client_with_keys
from localstack.testing.pytest import markers
from localstack.utils.strings import short_uid

from tests.aws.services.lambda_.test_lambda import TEST_LAMBDA_CONTENT

TEST_REGION = "us-east-1"
DUMMY_POLICY_DOC = """{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Action": "sts:AssumeRole",
            "Principal": {"AWS": "000000000000"},
            "Effect": "Allow"
        }
    ]
}"""

LOG = logging.getLogger(__name__)


@pytest.fixture
def engine():
    return IAMEnforcementEngine()


@pytest.fixture
def create_group(create_policy_generated_document, aws_client):
    group_names = []

    def _create_group(**kwargs):
        if "GroupName" not in kwargs:
            kwargs["GroupName"] = f"group-{short_uid()}"
        response = aws_client.iam.create_group(**kwargs)
        group_names.append(response["Group"]["GroupName"])
        return response

    yield _create_group

    for group_name in group_names:
        # remove attached users
        group_users = [
            group_user["UserName"]
            for group_user in aws_client.iam.get_group(GroupName=group_name)["Users"]
        ]
        for group_user in group_users:
            try:
                aws_client.iam.remove_user_from_group(GroupName=group_name, UserName=group_user)
            except Exception:
                LOG.debug(
                    "Could not remove group user '%s' from '%s' during cleanup",
                    group_user,
                    group_name,
                )

        # remove inline policies
        inline_policies = aws_client.iam.list_group_policies(GroupName=group_name)["PolicyNames"]
        for inline_policy in inline_policies:
            try:
                aws_client.iam.delete_group_policy(GroupName=group_name, PolicyName=inline_policy)
            except Exception:
                LOG.debug(
                    "Could not delete group policy '%s' from '%s' during cleanup",
                    inline_policy,
                    group_name,
                )

        # remove attached policies
        attached_policies = aws_client.iam.list_attached_group_policies(GroupName=group_name)[
            "AttachedPolicies"
        ]
        for attached_policy in attached_policies:
            try:
                aws_client.iam.detach_group_policy(
                    GroupName=group_name, PolicyArn=attached_policy["PolicyArn"]
                )
            except Exception:
                LOG.debug(
                    "Error detaching policy '%s' from group '%s'",
                    attached_policy["PolicyArn"],
                    group_name,
                )
        # remove group
        try:
            aws_client.iam.delete_group(GroupName=group_name)
        except Exception:
            LOG.debug("Error deleting group '%s' during test cleanup", group_name)


class TestIAMPrincipalDetection:
    @pytest.fixture(params=["role", "user", "root", "root_account_id"])
    def principal_arn_and_keys(
        self, request, create_role, wait_and_assume_role, create_user, aws_client
    ):
        account_info = aws_client.sts.get_caller_identity()
        account_id = account_info["Account"]
        if request.param == "role":
            role_name = f"role-{short_uid()}"
            session_name = f"session-{short_uid()}"
            account_arn = account_info["Arn"]
            assume_policy_doc = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Action": "sts:AssumeRole",
                        "Principal": {"AWS": account_arn},
                        "Effect": "Allow",
                    }
                ],
            }
            create_role_result = create_role(
                RoleName=role_name, AssumeRolePolicyDocument=json.dumps(assume_policy_doc)
            )
            keys = wait_and_assume_role(
                role_arn=create_role_result["Role"]["Arn"], session_name=session_name
            )
            return f"arn:aws:sts::{account_id}:assumed-role/{role_name}/{session_name}", keys
        elif request.param == "user":
            username = f"user-{short_uid()}"
            create_user(UserName=username)
            keys = aws_client.iam.create_access_key(UserName=username)["AccessKey"]
            return f"arn:aws:iam::{account_id}:user/{username}", keys
        elif request.param == "root":
            return f"arn:aws:iam::{account_id}:root", {
                "AccessKeyId": "test",
                "SecretAccessKey": "test",
            }
        elif request.param == "root_account_id":
            return f"arn:aws:iam::{account_id}:root", {
                "AccessKeyId": "000000000000",
                "SecretAccessKey": "test",
            }

    @markers.aws.only_localstack
    def test_extract_caller_principal_role(self, principal_arn_and_keys, engine):
        region = os.environ.get("AWS_DEFAULT_REGION") or TEST_REGION
        principal_arn, keys = principal_arn_and_keys
        sqs_client = create_client_with_keys(service="sqs", region_name=region, keys=keys)
        sts_client_keys = create_client_with_keys("sts", region_name=region, keys=keys)
        sqs_client = RequestContextClient(sqs_client)

        # generate request context for client action
        request_context = sqs_client.list_queues()

        # actual test
        principal, _ = engine.get_caller_principal_arn(context=request_context)
        assert principal == sts_client_keys.get_caller_identity()["Arn"]
        assert principal == principal_arn


class TestIAMPolicyRetrieval:
    @markers.aws.only_localstack
    def test_iam_role_inline_policy(self, create_role, aws_client, account_id):
        """Test getting permissions for an inline role policy"""
        role_name = f"role-{short_uid()}"
        policy_name = f"inline-policy-{short_uid()}"
        policy = {
            "Version": "2012-10-17",
            "Statement": {"Effect": "Allow", "Action": "s3:*", "Resource": "*"},
        }
        create_role(RoleName=role_name, AssumeRolePolicyDocument=DUMMY_POLICY_DOC)
        aws_client.iam.put_role_policy(
            RoleName=role_name, PolicyName=policy_name, PolicyDocument=json.dumps(policy)
        )
        role = Role(
            role_name=role_name,
            iam_client=aws_client.iam,
            arn=f"arn:aws:iam::{account_id}:role/{role_name}",
            account=account_id,
        )
        policies = role.get_policies()
        assert policy in policies
        assert len(policies) == 1
        assert not role.is_root()

    @markers.aws.only_localstack
    def test_iam_role_attached_policy(self, create_role, create_policy, aws_client, account_id):
        """Test getting permissions for an attached role policy"""
        role_name = f"role-{short_uid()}"
        policy_name = f"inline-policy-{short_uid()}"
        policy = {
            "Version": "2012-10-17",
            "Statement": {"Effect": "Allow", "Action": "s3:*", "Resource": "*"},
        }
        create_role(RoleName=role_name, AssumeRolePolicyDocument=DUMMY_POLICY_DOC)
        policy_arn = create_policy(PolicyName=policy_name, PolicyDocument=json.dumps(policy))[
            "Policy"
        ]["Arn"]
        aws_client.iam.attach_role_policy(RoleName=role_name, PolicyArn=policy_arn)
        role = Role(
            role_name=role_name,
            iam_client=aws_client.iam,
            arn=f"arn:aws:iam::{account_id}:role/{role_name}",
            account=account_id,
        )
        policies = role.get_policies()
        assert policy in policies
        assert len(policies) == 1

    @markers.aws.only_localstack
    def test_iam_role_multiple_policies(self, create_role, create_policy, aws_client, account_id):
        """Test getting permissions for multiple role policies"""
        role_name = f"role-{short_uid()}"
        policy_name = f"inline-policy-{short_uid()}"
        policy_name_attached = f"inline-policy-{short_uid()}"
        policy = {
            "Version": "2012-10-17",
            "Statement": {"Effect": "Allow", "Action": "s3:*", "Resource": "*"},
        }
        policy_attached = {
            "Version": "2012-10-17",
            "Statement": {"Effect": "Allow", "Action": "lambda:*", "Resource": "*"},
        }
        create_role(RoleName=role_name, AssumeRolePolicyDocument=DUMMY_POLICY_DOC)
        aws_client.iam.put_role_policy(
            RoleName=role_name, PolicyName=policy_name, PolicyDocument=json.dumps(policy)
        )
        policy_arn_attached = create_policy(
            PolicyName=policy_name_attached, PolicyDocument=json.dumps(policy_attached)
        )["Policy"]["Arn"]
        aws_client.iam.attach_role_policy(RoleName=role_name, PolicyArn=policy_arn_attached)
        role = Role(
            role_name=role_name,
            iam_client=aws_client.iam,
            arn=f"arn:aws:iam::{account_id}:role/{role_name}",
            account=account_id,
        )
        policies = role.get_policies()
        assert policy in policies
        assert policy_attached in policies
        assert len(policies) == 2

    @markers.aws.only_localstack
    def test_iam_user_inline_policy(self, create_user, aws_client, account_id):
        """Test getting permissions for an inline user policy"""
        user_name = f"user-{short_uid()}"
        policy_name = f"inline-policy-{short_uid()}"
        policy = {
            "Version": "2012-10-17",
            "Statement": {"Effect": "Allow", "Action": "s3:*", "Resource": "*"},
        }
        create_user(UserName=user_name)
        aws_client.iam.put_user_policy(
            UserName=user_name, PolicyName=policy_name, PolicyDocument=json.dumps(policy)
        )
        user = User(
            user_name=user_name,
            iam_client=aws_client.iam,
            arn=f"arn:aws:iam::{account_id}:user/{user_name}",
            account=account_id,
        )
        policies = user.get_policies()
        assert policy in policies
        assert len(policies) == 1
        assert not user.is_root()

    @markers.aws.only_localstack
    def test_iam_user_attached_policy(self, create_user, create_policy, aws_client, account_id):
        """Test getting permissions for an attached user policy"""
        user_name = f"user-{short_uid()}"
        policy_name = f"attached-policy-{short_uid()}"
        policy = {
            "Version": "2012-10-17",
            "Statement": {"Effect": "Allow", "Action": "s3:*", "Resource": "*"},
        }
        create_user(UserName=user_name)
        policy_arn = create_policy(PolicyName=policy_name, PolicyDocument=json.dumps(policy))[
            "Policy"
        ]["Arn"]
        aws_client.iam.attach_user_policy(UserName=user_name, PolicyArn=policy_arn)
        user = User(
            user_name=user_name,
            iam_client=aws_client.iam,
            arn=f"arn:aws:iam::{account_id}:user/{user_name}",
            account=account_id,
        )
        policies = user.get_policies()
        assert policy in policies
        assert len(policies) == 1

    @markers.aws.only_localstack
    def test_iam_user_multiple_policies(self, create_user, create_policy, aws_client, account_id):
        """Test getting permissions for multiple user policies"""
        user_name = f"user-{short_uid()}"
        policy_name = f"inline-policy-{short_uid()}"
        policy_name_attached = f"attached-policy-{short_uid()}"
        policy = {
            "Version": "2012-10-17",
            "Statement": {"Effect": "Allow", "Action": "s3:*", "Resource": "*"},
        }
        policy_attached = {
            "Version": "2012-10-17",
            "Statement": {"Effect": "Allow", "Action": "lambda:*", "Resource": "*"},
        }
        create_user(UserName=user_name)
        aws_client.iam.put_user_policy(
            UserName=user_name, PolicyName=policy_name, PolicyDocument=json.dumps(policy)
        )
        policy_arn_attached = create_policy(
            PolicyName=policy_name_attached, PolicyDocument=json.dumps(policy_attached)
        )["Policy"]["Arn"]
        aws_client.iam.attach_user_policy(UserName=user_name, PolicyArn=policy_arn_attached)
        user = User(
            user_name=user_name,
            iam_client=aws_client.iam,
            arn=f"arn:aws:iam::{account_id}:user/{user_name}",
            account=account_id,
        )
        policies = user.get_policies()
        assert policy in policies
        assert policy_attached in policies
        assert len(policies) == 2

    @markers.aws.only_localstack
    def test_iam_user_group_inline_policies(
        self, create_user, create_group, aws_client, account_id
    ):
        """Test getting permissions for an inline group policy"""
        user_name = f"user-{short_uid()}"
        group_name = f"user-group-{short_uid()}"
        policy_name = f"inline-policy-{short_uid()}"
        policy = {
            "Version": "2012-10-17",
            "Statement": {"Effect": "Allow", "Action": "s3:*", "Resource": "*"},
        }
        create_user(UserName=user_name)
        create_group(GroupName=group_name)
        aws_client.iam.put_group_policy(
            GroupName=group_name, PolicyName=policy_name, PolicyDocument=json.dumps(policy)
        )
        aws_client.iam.add_user_to_group(GroupName=group_name, UserName=user_name)
        user = User(
            user_name=user_name,
            iam_client=aws_client.iam,
            arn=f"arn:aws:iam::{account_id}:user/{user_name}",
            account=account_id,
        )
        policies = user.get_policies()
        assert policy in policies
        assert len(policies) == 1

    @markers.aws.only_localstack
    def test_iam_user_group_attached_policies(
        self,
        create_user,
        create_policy,
        create_group,
        aws_client,
        account_id,
    ):
        """Test getting permissions for an attached group policy"""
        user_name = f"user-{short_uid()}"
        group_name = f"user-group-{short_uid()}"
        policy_name = f"inline-policy-{short_uid()}"
        policy = {
            "Version": "2012-10-17",
            "Statement": {"Effect": "Allow", "Action": "s3:*", "Resource": "*"},
        }
        create_user(UserName=user_name)
        create_group(GroupName=group_name)
        policy_arn = create_policy(PolicyName=policy_name, PolicyDocument=json.dumps(policy))[
            "Policy"
        ]["Arn"]
        aws_client.iam.attach_group_policy(GroupName=group_name, PolicyArn=policy_arn)
        aws_client.iam.add_user_to_group(GroupName=group_name, UserName=user_name)
        user = User(
            user_name=user_name,
            iam_client=aws_client.iam,
            arn=f"arn:aws:iam::{account_id}:user/{user_name}",
            account=account_id,
        )
        policies = user.get_policies()
        assert policy in policies
        assert len(policies) == 1

    @markers.aws.only_localstack
    def test_iam_user_and_group_policies(
        self,
        create_user,
        create_policy,
        create_group,
        aws_client,
        account_id,
    ):
        """Test to check policy retrieval for a mixture of user and group permissions"""
        user_name = f"user-{short_uid()}"
        group_name = f"user-group-{short_uid()}"
        # create a lot of policies
        policy_name_user = f"inline-policy-{short_uid()}"
        policy_name_user_attached = f"attached-policy-{short_uid()}"
        policy_user = {
            "Version": "2012-10-17",
            "Statement": {"Effect": "Allow", "Action": "s3:*", "Resource": "*"},
        }
        policy_user_attached = {
            "Version": "2012-10-17",
            "Statement": {"Effect": "Allow", "Action": "lambda:*", "Resource": "*"},
        }
        policy_name_group = f"inline-policy-{short_uid()}"
        policy_name_group_attached = f"attached-policy-{short_uid()}"
        policy_group = {
            "Version": "2012-10-17",
            "Statement": {"Effect": "Allow", "Action": "logs:*", "Resource": "*"},
        }
        policy_group_attached = {
            "Version": "2012-10-17",
            "Statement": {"Effect": "Allow", "Action": "apigateway:*", "Resource": "*"},
        }
        # create user, group and add user to group
        create_user(UserName=user_name)
        create_group(GroupName=group_name)
        aws_client.iam.add_user_to_group(GroupName=group_name, UserName=user_name)

        # add inline policies to user and group
        aws_client.iam.put_user_policy(
            UserName=user_name, PolicyName=policy_name_user, PolicyDocument=json.dumps(policy_user)
        )
        aws_client.iam.put_group_policy(
            GroupName=group_name,
            PolicyName=policy_name_group,
            PolicyDocument=json.dumps(policy_group),
        )

        # add attached policies and add them to user and group
        policy_arn_user = create_policy(
            PolicyName=policy_name_user_attached, PolicyDocument=json.dumps(policy_user_attached)
        )["Policy"]["Arn"]
        policy_arn_group = create_policy(
            PolicyName=policy_name_group_attached, PolicyDocument=json.dumps(policy_group_attached)
        )["Policy"]["Arn"]
        aws_client.iam.attach_user_policy(UserName=user_name, PolicyArn=policy_arn_user)
        aws_client.iam.attach_group_policy(GroupName=group_name, PolicyArn=policy_arn_group)
        user = User(
            user_name=user_name,
            iam_client=aws_client.iam,
            arn=f"arn:aws:iam::{account_id}:user/{user_name}",
            account=account_id,
        )
        policies = user.get_policies()

        assert len(policies) == 4
        assert policy_group in policies
        assert policy_user in policies
        assert policy_group_attached in policies
        assert policy_user_attached in policies

    @markers.aws.only_localstack
    def test_iam_root_user(self):
        """Test if root user is marked as root"""
        user = Root(arn="arn:aws:iam::000000000000:root", account="000000000000")
        assert user.is_root()

    @markers.aws.only_localstack
    def test_get_permissions_for_role_arn(
        self, create_role, wait_and_assume_role, engine, aws_client
    ):
        role_name = f"role-{short_uid()}"
        session_name = f"session-{short_uid()}"
        policy_name = f"inline-policy-{short_uid()}"
        policy = {
            "Version": "2012-10-17",
            "Statement": {"Effect": "Allow", "Action": "s3:*", "Resource": "*"},
        }
        role_arn = create_role(RoleName=role_name, AssumeRolePolicyDocument=DUMMY_POLICY_DOC)[
            "Role"
        ]["Arn"]
        keys = wait_and_assume_role(role_arn=role_arn, session_name=session_name)
        assumed_role_arn = create_client_with_keys(
            "sts", region_name=TEST_REGION, keys=keys
        ).get_caller_identity()["Arn"]
        aws_client.iam.put_role_policy(
            RoleName=role_name, PolicyName=policy_name, PolicyDocument=json.dumps(policy)
        )
        policies = engine.get_identity_based_policies(
            engine.get_principal_entity(
                assumed_role_arn, access_key_id=keys["AccessKeyId"], region=TEST_REGION
            )
        )
        assert policy in policies
        assert len(policies) == 1

    @markers.aws.only_localstack
    def test_get_permissions_for_user_arn(self, create_user, engine, aws_client):
        user_name = f"user-{short_uid()}"
        policy_name = f"inline-policy-{short_uid()}"
        policy = {
            "Version": "2012-10-17",
            "Statement": {"Effect": "Allow", "Action": "s3:*", "Resource": "*"},
        }
        create_user(UserName=user_name)
        keys = aws_client.iam.create_access_key(UserName=user_name)["AccessKey"]
        user_arn = create_client_with_keys(
            "sts", keys=keys, region_name=TEST_REGION
        ).get_caller_identity()["Arn"]
        aws_client.iam.put_user_policy(
            UserName=user_name, PolicyName=policy_name, PolicyDocument=json.dumps(policy)
        )
        policies = engine.get_identity_based_policies(
            engine.get_principal_entity(
                user_arn, access_key_id=keys["AccessKeyId"], region=TEST_REGION
            )
        )
        assert policy in policies
        assert len(policies) == 1

    @markers.aws.only_localstack
    def test_iam_root_user_for_root_arn(self, engine, aws_client):
        """Test if root user is correctly detected as root"""
        root_arn = aws_client.sts.get_caller_identity()["Arn"]
        principal = engine.get_principal_entity(root_arn, "test", region=TEST_REGION)
        assert principal.is_root()


class TestIAMPermissionBoundaryRetrieval:
    @markers.aws.only_localstack
    def test_get_boundary_for_user(self, create_user, create_policy, aws_client, account_id):
        user_name = f"user-{short_uid()}"
        policy_name = f"boundary-policy-{short_uid()}"
        policy = {
            "Version": "2012-10-17",
            "Statement": {"Effect": "Allow", "Action": "s3:*", "Resource": "*"},
        }
        create_user(UserName=user_name)
        policy_arn = create_policy(PolicyName=policy_name, PolicyDocument=json.dumps(policy))[
            "Policy"
        ]["Arn"]
        aws_client.iam.put_user_permissions_boundary(
            UserName=user_name, PermissionsBoundary=policy_arn
        )
        user = User(
            user_name=user_name,
            iam_client=aws_client.iam,
            arn=f"arn:aws:iam::{account_id}:user/{user_name}",
            account=account_id,
        )
        permission_boundary = user.get_permissions_boundary()
        assert policy == permission_boundary

    @markers.aws.only_localstack
    def test_get_boundary_for_role(self, create_role, create_policy, aws_client, account_id):
        role_name = f"user-{short_uid()}"
        policy_name = f"boundary-policy-{short_uid()}"
        policy = {
            "Version": "2012-10-17",
            "Statement": {"Effect": "Allow", "Action": "s3:*", "Resource": "*"},
        }
        create_role(RoleName=role_name, AssumeRolePolicyDocument=DUMMY_POLICY_DOC)
        policy_arn = create_policy(PolicyName=policy_name, PolicyDocument=json.dumps(policy))[
            "Policy"
        ]["Arn"]
        aws_client.iam.put_role_permissions_boundary(
            RoleName=role_name, PermissionsBoundary=policy_arn
        )
        role = Role(
            role_name=role_name,
            iam_client=aws_client.iam,
            arn=f"arn:aws:iam::{account_id}:role/{role_name}",
            account=account_id,
        )
        permission_boundary = role.get_permissions_boundary()
        assert policy == permission_boundary


class TestIAMTagsRetrieval:
    @markers.aws.only_localstack
    def test_tags_assumed_role(self, create_role, aws_client):
        role_name = f"role-{short_uid()}"
        role_arn = create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=DUMMY_POLICY_DOC,
            Tags=[{"Key": "Role", "Value": "Value1"}, {"Key": "Overriden", "Value": "Value1"}],
        )["Role"]["Arn"]
        keys = aws_client.sts.assume_role(
            RoleArn=role_arn,
            RoleSessionName="Test",
            Tags=[{"Key": "Session", "Value": "Value2"}, {"Key": "Overriden", "Value": "Value2"}],
        )["Credentials"]

        sts_client = create_client_with_keys(service="sts", region_name="us-east-1", keys=keys)
        caller_arn = sts_client.get_caller_identity()["Arn"]
        assumed_role_1 = AssumedRole.from_assumed_role_arn(
            assumed_role_arn=caller_arn,
            iam_client=aws_client.iam,
            access_key_id=keys["AccessKeyId"],
        )
        assert assumed_role_1.get_tags() == {
            "Role": "Value1",
            "Overriden": "Value2",
            "Session": "Value2",
        }

        # assume again mit same session name
        keys = aws_client.sts.assume_role(
            RoleArn=role_arn,
            RoleSessionName="Test",
            Tags=[{"Key": "Session", "Value": "Value3"}, {"Key": "Overriden", "Value": "Value3"}],
        )["Credentials"]
        assumed_role_2 = AssumedRole.from_assumed_role_arn(
            assumed_role_arn=caller_arn,
            iam_client=aws_client.iam,
            access_key_id=keys["AccessKeyId"],
        )
        assert assumed_role_2.get_tags() == {
            "Role": "Value1",
            "Overriden": "Value3",
            "Session": "Value3",
        }
        # assumed role 1 - with the same access key id should still be the same
        assert assumed_role_1.get_tags() == {
            "Role": "Value1",
            "Overriden": "Value2",
            "Session": "Value2",
        }

    @markers.aws.only_localstack
    def test_tags_user(self, create_user, aws_client, account_id):
        user_name = f"user-{short_uid()}"
        create_user(
            UserName=user_name,
            Tags=[{"Key": "User", "Value": "Value1"}, {"Key": "AnotherKey", "Value": "Value1"}],
        )

        user = User(
            user_name=user_name,
            iam_client=aws_client.iam,
            arn=f"arn:aws:iam::{account_id}:user/{user_name}",
            account=account_id,
        )
        assert user.get_tags() == {"User": "Value1", "AnotherKey": "Value1"}


class TestIAMResourcePolicyRetrieval:
    @markers.aws.only_localstack
    def test_get_resource_policy_lambda(self, create_user, create_lambda_function, aws_client):
        user_name = f"user-{short_uid()}"
        user_arn = create_user(UserName=user_name)["User"]["Arn"]
        fn_name = f"test-function-{short_uid()}"
        create_function_response = create_lambda_function(
            handler_file=TEST_LAMBDA_CONTENT, func_name=fn_name, runtime=Runtime.python3_12
        )
        lambda_arn = create_function_response["CreateFunctionResponse"]["FunctionArn"]
        statement_id = f"s-{short_uid()}"
        aws_client.lambda_.add_permission(
            FunctionName=fn_name,
            StatementId=statement_id,
            Action="lambda:GetFunction",
            Principal=user_arn,
        )
        policy_retriever = ResourcePolicyRetriever()
        policies = policy_retriever.retrieve_policy_for_arn(lambda_arn, None)
        assert len(policies) == 1
        policy = policies[0]
        assert policy["Version"] == "2012-10-17"
        assert len(policy["Statement"]) == 1
        statement = policy["Statement"][0]
        assert statement["Sid"] == statement_id
        assert statement["Effect"] == "Allow"
        assert statement["Action"] == "lambda:GetFunction"
        assert statement["Resource"] == lambda_arn
        assert statement["Principal"]["AWS"] == user_arn

    @markers.aws.only_localstack
    def test_get_resource_policy_lambda_non_existent(self, create_lambda_function):
        fn_name = f"test-function-{short_uid()}"
        create_function_response = create_lambda_function(
            handler_file=TEST_LAMBDA_CONTENT, func_name=fn_name, runtime=Runtime.python3_12
        )
        lambda_arn = create_function_response["CreateFunctionResponse"]["FunctionArn"]
        policy_retriever = ResourcePolicyRetriever()
        policies = policy_retriever.retrieve_policy_for_arn(lambda_arn, None)
        assert policies is None
        policies = policy_retriever.retrieve_policy_for_arn(
            "arn:aws:lambda:us-east-1:000000000000:function:nonexistent", None
        )
        assert policies is None

    @markers.aws.only_localstack
    def test_get_resource_policy_sqs(
        self, create_user, sqs_create_queue, sqs_get_queue_arn, aws_client
    ):
        user_name = f"user-{short_uid()}"
        user_arn = create_user(UserName=user_name)["User"]["Arn"]
        queue_name = f"test-queue-{short_uid()}"
        queue_url = sqs_create_queue(QueueName=queue_name)
        queue_arn = sqs_get_queue_arn(queue_url)
        statement_id = f"s-{short_uid()}"
        policy = {
            "Version": "2012-10-17",
            "Id": "SqsQueuePolicy",
            "Statement": [
                {
                    "Sid": statement_id,
                    "Effect": "Allow",
                    "Principal": {"AWS": user_arn},
                    "Action": ["sqs:ReceiveMessage"],
                    "Resource": queue_arn,
                }
            ],
        }
        aws_client.sqs.set_queue_attributes(
            QueueUrl=queue_url, Attributes={"Policy": json.dumps(policy)}
        )
        policy_retriever = ResourcePolicyRetriever()
        retrieved_policies = policy_retriever.retrieve_policy_for_arn(queue_arn, None)
        assert len(retrieved_policies) == 1
        retrieved_policy = retrieved_policies[0]
        assert policy == retrieved_policy

    @markers.aws.only_localstack
    def test_get_resource_policy_sqs_non_existent(self, sqs_create_queue, sqs_get_queue_arn):
        queue_name = f"test-queue-{short_uid()}"
        queue_url = sqs_create_queue(QueueName=queue_name)
        queue_arn = sqs_get_queue_arn(queue_url)
        policy_retriever = ResourcePolicyRetriever()
        retrieved_policy = policy_retriever.retrieve_policy_for_arn(queue_arn, None)
        assert retrieved_policy is None

        retrieved_policy = policy_retriever.retrieve_policy_for_arn(
            "arn:aws:sqs:us-east-1:000000000000:nonexistent", None
        )
        assert retrieved_policy is None

    @markers.aws.only_localstack
    def test_get_resource_policy_sns(self, create_user, sns_create_topic, aws_client):
        user_name = f"user-{short_uid()}"
        user_arn = create_user(UserName=user_name)["User"]["Arn"]
        topic_name = f"test-topic-{short_uid()}"
        topic_arn = sns_create_topic(Name=topic_name)["TopicArn"]
        statement_id = f"s-{short_uid()}"
        policy = {
            "Version": "2012-10-17",
            "Id": "SnsTopicPolicy",
            "Statement": [
                {
                    "Sid": statement_id,
                    "Effect": "Allow",
                    "Principal": {"AWS": user_arn},
                    "Action": ["sns:Publish"],
                    "Resource": topic_arn,
                }
            ],
        }
        aws_client.sns.set_topic_attributes(
            TopicArn=topic_arn, AttributeName="Policy", AttributeValue=json.dumps(policy)
        )
        policy_retriever = ResourcePolicyRetriever()
        retrieved_policies = policy_retriever.retrieve_policy_for_arn(topic_arn, None)
        assert len(retrieved_policies) == 1
        retrieved_policy = retrieved_policies[0]
        assert policy == retrieved_policy

    @markers.aws.only_localstack
    def test_get_resource_policy_sns_non_existent(self, sns_create_topic):
        topic_name = f"test-topic-{short_uid()}"
        topic_arn = sns_create_topic(Name=topic_name)["TopicArn"]
        policy_retriever = ResourcePolicyRetriever()
        # all topics have a default policy set
        retrieved_policies = policy_retriever.retrieve_policy_for_arn(topic_arn, None)
        assert len(retrieved_policies) == 1
        retrieved_policy = retrieved_policies[0]
        assert retrieved_policy["Id"] == "__default_policy_ID"

        retrieved_policies = policy_retriever.retrieve_policy_for_arn(
            "arn:aws:sns:us-east-1:000000000000:nonexistent", None
        )
        assert retrieved_policies is None

    @markers.aws.only_localstack
    def test_get_resource_policy_sts(self, create_role, aws_client):
        role_name = f"user-{short_uid()}"
        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "s1",
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": "sts:AssumeRole",
                }
            ],
        }
        role_arn = create_role(RoleName=role_name, AssumeRolePolicyDocument=json.dumps(policy))[
            "Role"
        ]["Arn"]

        prep_sts_client = RequestContextClient(aws_client.sts)
        request_context = prep_sts_client.assume_role(
            RoleArn=role_arn, RoleSessionName="test-session"
        )
        policy_retriever = ResourcePolicyRetriever()
        retrieved_policies = policy_retriever.retrieve_policy_for_arn(
            role_arn, context=request_context
        )
        assert len(retrieved_policies) == 1
        retrieved_policy = retrieved_policies[0]
        assert policy == retrieved_policy


class TestIAMResourceDetection:
    @pytest.fixture(scope="class")
    def account_id(self, aws_client):
        return aws_client.sts.get_caller_identity()["Account"]

    @pytest.fixture(scope="class")
    def action_extractor(self):
        return ActionResourceExtractor(IAMPluginManager.get())

    @markers.aws.only_localstack
    def test_s3_create_bucket(self, action_extractor, aws_client):
        bucket_name = f"test-bucket-{short_uid()}"
        prep_s3_client = RequestContextClient(aws_client.s3)
        output = action_extractor.get_required_iam_actions_for_request(
            prep_s3_client.create_bucket(Bucket=bucket_name)
        )
        assert len(output) == 1
        output = output[0]
        assert output.resource == f"arn:aws:s3:::{bucket_name}"
        assert output.action == "s3:CreateBucket"

    @markers.aws.only_localstack
    def test_s3_put_object(self, action_extractor, aws_client):
        bucket_name = f"test-bucket-{short_uid()}"
        object = f"test-object-{short_uid()}"
        prep_s3_client = RequestContextClient(aws_client.s3)
        output = action_extractor.get_required_iam_actions_for_request(
            prep_s3_client.put_object(Bucket=bucket_name, Key=object, Body=b"a" * 5)
        )
        assert len(output) == 1
        output = output[0]
        assert output.resource == f"arn:aws:s3:::{bucket_name}/{object}"
        assert output.action == "s3:PutObject"

    @markers.aws.only_localstack
    def test_sqs_create_queue(self, account_id, action_extractor, aws_client):
        queue_name = f"test-queue-{short_uid()}"
        prep_sqs_client = RequestContextClient(aws_client.sqs)
        output = action_extractor.get_required_iam_actions_for_request(
            prep_sqs_client.create_queue(QueueName=queue_name)
        )
        assert len(output) == 1
        output = output[0]
        assert (
            output.resource
            == f"arn:aws:sqs:{aws_client.sqs.meta.region_name}:{account_id}:{queue_name}"
        )
        assert output.action == "sqs:CreateQueue"

    @markers.aws.only_localstack
    def test_sqs_get_queue_attributes(self, account_id, action_extractor, aws_client):
        queue_url = f"https://sqs.us-east-2.amazonaws.com/{account_id}/MyQueue"
        queue_url_ls = f"http://localhost:4566/{account_id}/MyQueue"
        prep_sqs_client = RequestContextClient(aws_client.sqs)
        output = action_extractor.get_required_iam_actions_for_request(
            prep_sqs_client.get_queue_attributes(QueueUrl=queue_url)
        )
        assert len(output) == 1
        output = output[0]
        assert (
            output.resource == f"arn:aws:sqs:{aws_client.sqs.meta.region_name}:{account_id}:MyQueue"
        )
        assert output.action == "sqs:GetQueueAttributes"

        output_ls = action_extractor.get_required_iam_actions_for_request(
            prep_sqs_client.get_queue_attributes(QueueUrl=queue_url_ls)
        )
        assert len(output_ls) == 1
        output_ls = output_ls[0]
        assert (
            output_ls.resource
            == f"arn:aws:sqs:{aws_client.sqs.meta.region_name}:{account_id}:MyQueue"
        )
        assert output_ls.action == "sqs:GetQueueAttributes"

    @markers.aws.only_localstack
    def test_lambda_create_function(self, account_id, action_extractor, aws_client):
        function_name = f"test-function-{short_uid()}"
        prep_lambda_client = RequestContextClient(aws_client.lambda_)
        output = action_extractor.get_required_iam_actions_for_request(
            prep_lambda_client.create_function(
                FunctionName=function_name,
                Code={"ZipFile": b""},
                Role=f"arn:aws:iam::{account_id}:role/role-name",
            )
        )
        assert len(output) == 2
        action_lambda = next(
            action for action in output if action.action == "lambda:CreateFunction"
        )
        assert (
            action_lambda.resource
            == f"arn:aws:lambda:{aws_client.lambda_.meta.region_name}:{account_id}:function:{function_name}"
        )
        action_iam = next(action for action in output if action.action == "iam:PassRole")
        assert action_iam.resource == f"arn:aws:iam::{account_id}:role/role-name"

    @markers.aws.only_localstack
    def test_cognito_idp_list_users(self, account_id, action_extractor, aws_client):
        cognito_user_pool = f"test-pool-{short_uid()}"
        prep_cognito_idp_client = RequestContextClient(aws_client.cognito_idp)
        output = action_extractor.get_required_iam_actions_for_request(
            prep_cognito_idp_client.list_users(UserPoolId=cognito_user_pool)
        )
        assert len(output) == 1
        output = output[0]
        assert (
            output.resource
            == f"arn:aws:cognito-idp:{aws_client.cognito_idp.meta.region_name}:{account_id}:userpool/{cognito_user_pool}"
        )
        assert output.action == "cognito-idp:ListUsers"

    @markers.aws.only_localstack
    def test_timestream_write_create_database(self, account_id, action_extractor, aws_client):
        database_name = f"test-pool-{short_uid()}"
        prep_timestream_write_client = RequestContextClient(aws_client.timestream_write)
        output = action_extractor.get_required_iam_actions_for_request(
            prep_timestream_write_client.create_database(DatabaseName=database_name)
        )
        assert len(output) == 1
        output = output[0]
        assert (
            output.resource
            == f"arn:aws:timestream:{aws_client.timestream_write.meta.region_name}:{account_id}:database/{database_name}"
        )
        assert output.action == "timestream:CreateDatabase"

    @markers.aws.only_localstack
    def test_elasticsearch_list_domains(self, account_id, action_extractor, aws_client):
        domain_1 = f"test-domain-{short_uid()}"
        domain_2 = f"test-domain-{short_uid()}"
        prep_es_client = RequestContextClient(aws_client.es)
        output = action_extractor.get_required_iam_actions_for_request(
            prep_es_client.describe_elasticsearch_domains(DomainNames=[domain_1, domain_2])
        )
        assert len(output) == 2
        output_1 = output[0]
        assert output_1.action == "es:DescribeElasticsearchDomains"
        resources = [output_1.resource]
        output_2 = output[1]
        assert output_2.action == "es:DescribeElasticsearchDomains"
        resources.append(output_2.resource)
        assert (
            f"arn:aws:es:{aws_client.es.meta.region_name}:{account_id}:domain/{domain_1}"
            in resources
        )
        assert (
            f"arn:aws:es:{aws_client.es.meta.region_name}:{account_id}:domain/{domain_2}"
            in resources
        )

    @markers.aws.only_localstack
    def test_batch_create_job_queue(self, action_extractor, account_id, aws_client):
        """Test if replacements with dot notation and array accessing works correctly"""
        queue_name = f"test-queue-{short_uid()}"
        compute_environment_1 = f"test-env-{short_uid()}"
        compute_environment_2 = f"test-env-{short_uid()}"
        prep_batch_client = RequestContextClient(aws_client.batch)
        request_context = prep_batch_client.create_job_queue(
            jobQueueName=queue_name,
            computeEnvironmentOrder=[
                {"computeEnvironment": compute_environment_1, "order": 1},
                {"computeEnvironment": compute_environment_2, "order": 1},
            ],
            priority=123,
        )
        output = action_extractor.get_required_iam_actions_for_request(request_context)
        assert len(output) == 3
        assert all(
            calculated_action.action == "batch:CreateJobQueue" for calculated_action in output
        )
        resources = [calculated_action.resource for calculated_action in output]
        assert (
            f"arn:aws:batch:{aws_client.batch.meta.region_name}:{account_id}:compute-environment/{compute_environment_1}"
            in resources
        )
        assert (
            f"arn:aws:batch:{aws_client.batch.meta.region_name}:{account_id}:compute-environment/{compute_environment_2}"
            in resources
        )
        assert (
            f"arn:aws:batch:{aws_client.batch.meta.region_name}:{account_id}:job-queue/{queue_name}"
            in resources
        )

    @markers.aws.only_localstack
    def test_batch_create_compute_environment(self, action_extractor, account_id, aws_client):
        """Test if replacements inline regex in arn overrides works correctly"""
        compute_environment = f"test-env-{short_uid()}"
        role_name = f"test-role-{short_uid()}"
        prep_batch_client = RequestContextClient(aws_client.batch)
        request_context = prep_batch_client.create_compute_environment(
            computeEnvironmentName=compute_environment,
            type="MANAGED",
            computeResources={
                "instanceRole": f"arn:aws:iam::{account_id}:role/{role_name}",
                "maxvCpus": 1,
                "instanceTypes": ["c5"],
                "type": "FARGATE",
                "subnets": [],
            },
        )
        output = action_extractor.get_required_iam_actions_for_request(request_context)
        assert len(output) == 2
        actions = [calculated_action.action for calculated_action in output]
        assert "batch:CreateComputeEnvironment" in actions
        assert "iam:PassRole" in actions
        resources = [calculated_action.resource for calculated_action in output]
        assert (
            f"arn:aws:batch:{aws_client.batch.meta.region_name}:{account_id}:compute-environment/{compute_environment}"
            in resources
        )
        assert f"arn:aws:iam::{account_id}:role/{role_name}" in resources
