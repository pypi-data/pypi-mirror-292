import base64
import json
import time

import pytest
from botocore.exceptions import ClientError
from localstack.aws.api.lambda_ import Runtime
from localstack.testing.aws.lambda_utils import _await_event_source_mapping_enabled
from localstack.testing.aws.util import is_aws_cloud
from localstack.testing.pytest import markers
from localstack.utils.aws.arns import get_partition
from localstack.utils.strings import short_uid
from localstack.utils.sync import poll_condition, retry

from tests.aws.services.iam.test_inter_service_enforcement import TEST_LAMBDA_ECHO


class TestLambdaCrossAccount:
    @pytest.fixture
    def assume_role_account_2(self, secondary_aws_client, aws_client_factory):
        def _assume(role_arn: str):
            return secondary_aws_client.sts.assume_role(
                RoleArn=role_arn, RoleSessionName="Account2Session"
            )["Credentials"]

        def _create_client(role_arn: str):
            creds = retry(_assume, sleep=2, retries=10, role_arn=role_arn)
            return aws_client_factory(
                aws_access_key_id=creds["AccessKeyId"],
                aws_secret_access_key=creds["SecretAccessKey"],
                aws_session_token=creds["SessionToken"],
            )

        return _create_client

    @pytest.fixture
    def assume_role_policy_account_2(self, secondary_account_id):
        return json.dumps(
            {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Action": "sts:AssumeRole",
                        "Principal": {"AWS": secondary_account_id},
                        "Effect": "Allow",
                    }
                ],
            }
        )

    @pytest.fixture(autouse=True)
    def setup_snapshots(self, snapshot):
        snapshot.add_transformer(snapshot.transform.key_value("Arn"))
        snapshot.add_transformer(snapshot.transform.key_value("RoleName"))
        snapshot.add_transformer(snapshot.transform.key_value("RoleId"))
        snapshot.add_transformer(snapshot.transform.key_value("Account"))
        snapshot.add_transformer(snapshot.transform.iam_api())

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(paths=["$..Error.Message"])
    def test_lambda_cross_account_invoke(
        self,
        aws_client,
        secondary_aws_client,
        secondary_account_id,
        create_lambda_function,
        cleanups,
        assume_role_account_2,
        assume_role_policy_account_2,
        snapshot,
    ):
        snapshot.add_transformer(snapshot.transform.key_value("CodeSha256"))
        snapshot.add_transformer(snapshot.transform.lambda_api())
        function_name = f"test-function-{short_uid()}"
        role_name = f"test-role-{short_uid()}"
        policy_name = f"test-policy-{short_uid()}"
        create_function_response = create_lambda_function(
            func_name=function_name,
            handler_file=TEST_LAMBDA_ECHO,
            runtime=Runtime.python3_12,
        )["CreateFunctionResponse"]
        snapshot.match("create-function-response", create_function_response)
        function_arn = create_function_response["FunctionArn"]

        # add snapshot ignore for current client arn replacement
        caller_identity_2 = secondary_aws_client.sts.get_caller_identity()
        snapshot.match("caller-identity-2", caller_identity_2)

        # test regular invoke within account
        invocation_response = aws_client.lambda_.invoke(
            FunctionName=function_arn, Payload=json.dumps({"test": "payload"})
        )
        snapshot.match("intra-account-invoke", invocation_response)

        with pytest.raises(ClientError) as e:
            secondary_aws_client.lambda_.invoke(
                FunctionName=function_arn, Payload=json.dumps({"test": "payload"})
            )
        snapshot.match("invalid-permissions-account-2-without-role", e.value.response)

        aws_client.lambda_.add_permission(
            FunctionName=function_name,
            StatementId="OtherAccountStatement",
            Action="lambda:InvokeFunction",
            Principal=secondary_account_id,
        )

        invocation_response = secondary_aws_client.lambda_.invoke(
            FunctionName=function_arn, Payload=json.dumps({"test": "payload"})
        )
        snapshot.match("valid-permissions-account-2-without-role", invocation_response)

        create_role_response = secondary_aws_client.iam.create_role(
            RoleName=role_name, AssumeRolePolicyDocument=assume_role_policy_account_2
        )
        snapshot.match("create-role-response", create_role_response)
        role_arn = create_role_response["Role"]["Arn"]
        cleanups.append(lambda: secondary_aws_client.iam.delete_role(RoleName=role_name))

        role_aws_clients = assume_role_account_2(role_arn)

        if is_aws_cloud():
            time.sleep(10)

        with pytest.raises(ClientError) as e:
            role_aws_clients.lambda_.invoke(
                FunctionName=function_arn, Payload=json.dumps({"test": "payload"})
            )
        snapshot.match("invalid-permissions-account-2-role", e.value.response)

        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": "lambda:InvokeFunction",
                    "Resource": function_arn,
                }
            ],
        }
        secondary_aws_client.iam.put_role_policy(
            RoleName=role_name, PolicyName=policy_name, PolicyDocument=json.dumps(policy)
        )
        cleanups.append(
            lambda: secondary_aws_client.iam.delete_role_policy(
                RoleName=role_name, PolicyName=policy_name
            )
        )

        def invoke():
            return role_aws_clients.lambda_.invoke(
                FunctionName=function_arn, Payload=json.dumps({"test": "payload"})
            )

        invocation_response = retry(invoke, sleep=10 if is_aws_cloud() else 1, retries=20)
        snapshot.match("valid-permissions-account-2-role", invocation_response)

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(
        paths=[
            "$..Error.Message",
            "$..Error.Detail",
            "$..Error.QueryErrorCode",  # TODO re-create snapshots after switching SQS to JSON again
        ]
    )
    def test_sqs_cross_account_receive(
        self,
        aws_client,
        secondary_aws_client,
        secondary_account_id,
        sqs_create_queue,
        sqs_get_queue_arn,
        cleanups,
        assume_role_account_2,
        assume_role_policy_account_2,
        snapshot,
    ):
        snapshot.add_transformer(snapshot.transform.sqs_api())
        queue_name = f"test-queue-{short_uid()}"
        role_name = f"test-role-{short_uid()}"
        policy_name = f"test-policy-{short_uid()}"
        queue_url = sqs_create_queue(QueueName=queue_name)
        queue_arn = sqs_get_queue_arn(queue_url)
        snapshot.match("queue_arn", queue_arn)

        # add snapshot ignore for current client arn replacement
        caller_identity_2 = secondary_aws_client.sts.get_caller_identity()
        snapshot.match("caller-identity-2", caller_identity_2)

        # put message into queue
        aws_client.sqs.send_message(QueueUrl=queue_url, MessageBody="test1")

        # test regular receive within account
        receive_message_response = aws_client.sqs.receive_message(
            QueueUrl=queue_url, VisibilityTimeout=0
        )
        snapshot.match("intra-account-receive-message", receive_message_response)

        with pytest.raises(ClientError) as e:
            secondary_aws_client.sqs.receive_message(QueueUrl=queue_url, VisibilityTimeout=0)
        snapshot.match("invalid-permissions-account-2-without-role", e.value.response)

        aws_client.sqs.add_permission(
            QueueUrl=queue_url,
            AWSAccountIds=[secondary_account_id],
            Actions=["ReceiveMessage"],
            Label="crossaccountpermission",
        )

        receive_message_response = secondary_aws_client.sqs.receive_message(
            QueueUrl=queue_url, VisibilityTimeout=0
        )
        snapshot.match("valid-permissions-account-2-without-role", receive_message_response)

        create_role_response = secondary_aws_client.iam.create_role(
            RoleName=role_name, AssumeRolePolicyDocument=assume_role_policy_account_2
        )
        snapshot.match("create-role-response", create_role_response)
        role_arn = create_role_response["Role"]["Arn"]
        cleanups.append(lambda: secondary_aws_client.iam.delete_role(RoleName=role_name))

        role_aws_clients = assume_role_account_2(role_arn)

        if is_aws_cloud():
            time.sleep(10)

        with pytest.raises(ClientError) as e:
            role_aws_clients.sqs.receive_message(QueueUrl=queue_url, VisibilityTimeout=0)
        snapshot.match("invalid-permissions-account-2-role", e.value.response)

        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": "sqs:ReceiveMessage",
                    "Resource": queue_arn,
                }
            ],
        }
        secondary_aws_client.iam.put_role_policy(
            RoleName=role_name, PolicyName=policy_name, PolicyDocument=json.dumps(policy)
        )
        cleanups.append(
            lambda: secondary_aws_client.iam.delete_role_policy(
                RoleName=role_name, PolicyName=policy_name
            )
        )

        def _receive():
            return role_aws_clients.sqs.receive_message(QueueUrl=queue_url, VisibilityTimeout=0)

        receive_message_response = retry(_receive, sleep=10 if is_aws_cloud() else 1, retries=20)
        snapshot.match("valid-permissions-account-2-role", receive_message_response)

    @markers.snapshot.skip_snapshot_verify(paths=["$..Error.Message"])
    @markers.aws.validated
    def test_sns_cross_account_publish(
        self,
        aws_client,
        secondary_aws_client,
        secondary_account_id,
        sns_create_topic,
        cleanups,
        assume_role_account_2,
        assume_role_policy_account_2,
        snapshot,
    ):
        snapshot.add_transformer(snapshot.transform.sns_api())
        queue_name = f"test-queue-{short_uid()}"
        role_name = f"test-role-{short_uid()}"
        policy_name = f"test-policy-{short_uid()}"
        create_topic_response = sns_create_topic(Name=queue_name)
        snapshot.match("create-topic-response", create_topic_response)
        topic_arn = create_topic_response["TopicArn"]

        # add snapshot ignore for current client arn replacement
        caller_identity_2 = secondary_aws_client.sts.get_caller_identity()
        snapshot.match("caller-identity-2", caller_identity_2)

        # test regular publish within account
        publish_response = aws_client.sns.publish(Message="test1", TopicArn=topic_arn)
        snapshot.match("intra-account-operation", publish_response)

        with pytest.raises(ClientError) as e:
            secondary_aws_client.sns.publish(Message="test1", TopicArn=topic_arn)
        snapshot.match("invalid-permissions-account-2-without-role", e.value.response)

        aws_client.sns.add_permission(
            TopicArn=topic_arn,
            AWSAccountId=[secondary_account_id],
            Label="crossaccountpermission",
            ActionName=["Publish"],
        )

        publish_response = secondary_aws_client.sns.publish(Message="test1", TopicArn=topic_arn)
        snapshot.match("valid-permissions-account-2-without-role", publish_response)

        create_role_response = secondary_aws_client.iam.create_role(
            RoleName=role_name, AssumeRolePolicyDocument=assume_role_policy_account_2
        )
        snapshot.match("create-role-response", create_role_response)
        role_arn = create_role_response["Role"]["Arn"]
        cleanups.append(lambda: secondary_aws_client.iam.delete_role(RoleName=role_name))

        role_aws_clients = assume_role_account_2(role_arn)

        if is_aws_cloud():
            time.sleep(10)

        with pytest.raises(ClientError) as e:
            role_aws_clients.sns.publish(Message="test1", TopicArn=topic_arn)
        snapshot.match("invalid-permissions-account-2-role", e.value.response)

        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": "sns:Publish",
                    "Resource": topic_arn,
                }
            ],
        }
        secondary_aws_client.iam.put_role_policy(
            RoleName=role_name, PolicyName=policy_name, PolicyDocument=json.dumps(policy)
        )
        cleanups.append(
            lambda: secondary_aws_client.iam.delete_role_policy(
                RoleName=role_name, PolicyName=policy_name
            )
        )

        def _receive():
            return aws_client.sns.publish(Message="test1", TopicArn=topic_arn)

        publish_response = retry(_receive, sleep=10 if is_aws_cloud() else 1, retries=20)
        snapshot.match("valid-permissions-account-2-role", publish_response)

    @markers.snapshot.skip_snapshot_verify(paths=["$..Error.Message"])
    @markers.aws.validated
    def test_kms_cross_account_encrypt(
        self,
        aws_client,
        secondary_aws_client,
        secondary_account_id,
        kms_create_key,
        cleanups,
        assume_role_account_2,
        assume_role_policy_account_2,
        snapshot,
        region_name,
        secondary_region_name,
    ):
        snapshot.add_transformer(snapshot.transform.kms_api())
        role_name = f"test-role-{short_uid()}"
        policy_name = f"test-policy-{short_uid()}"

        create_key_response = kms_create_key(
            KeyUsage="ENCRYPT_DECRYPT", KeySpec="SYMMETRIC_DEFAULT", Description="test"
        )
        snapshot.match("create-key-response", create_key_response)
        key_arn = create_key_response["Arn"]
        message = b"test message 123 !%$@ 1234567890"

        # add snapshot ignore for current client arn replacement
        caller_identity_2 = secondary_aws_client.sts.get_caller_identity()
        snapshot.match("caller-identity-2", caller_identity_2)

        # test regular publish within account
        encryption_response = aws_client.kms.encrypt(
            KeyId=key_arn,
            Plaintext=base64.b64encode(message),
            EncryptionAlgorithm="SYMMETRIC_DEFAULT",
        )
        snapshot.match("intra-account-operation", encryption_response)

        with pytest.raises(ClientError) as e:
            secondary_aws_client.kms.encrypt(
                KeyId=key_arn,
                Plaintext=base64.b64encode(message),
                EncryptionAlgorithm="SYMMETRIC_DEFAULT",
            )
        snapshot.match("invalid-permissions-account-2-without-role", e.value.response)

        policy = json.loads(
            aws_client.kms.get_key_policy(KeyId=key_arn, PolicyName="default")["Policy"]
        )
        old_value = policy["Statement"][0]["Principal"]["AWS"]
        policy["Statement"][0]["Principal"]["AWS"] = [
            old_value,
            f"arn:{get_partition(secondary_region_name)}:iam::{secondary_account_id}:root",
        ]
        aws_client.kms.put_key_policy(
            KeyId=key_arn, PolicyName="default", Policy=json.dumps(policy)
        )

        def _encrypt():
            return secondary_aws_client.kms.encrypt(
                KeyId=key_arn,
                Plaintext=base64.b64encode(message),
                EncryptionAlgorithm="SYMMETRIC_DEFAULT",
            )

        encryption_response = retry(_encrypt, sleep=10 if is_aws_cloud() else 2, retries=10)
        snapshot.match("valid-permissions-account-2-without-role", encryption_response)

        create_role_response = secondary_aws_client.iam.create_role(
            RoleName=role_name, AssumeRolePolicyDocument=assume_role_policy_account_2
        )
        snapshot.match("create-role-response", create_role_response)
        role_arn = create_role_response["Role"]["Arn"]
        cleanups.append(lambda: secondary_aws_client.iam.delete_role(RoleName=role_name))

        role_aws_clients = assume_role_account_2(role_arn)

        if is_aws_cloud():
            time.sleep(10)

        with pytest.raises(ClientError) as e:
            role_aws_clients.kms.encrypt(
                KeyId=key_arn,
                Plaintext=base64.b64encode(message),
                EncryptionAlgorithm="SYMMETRIC_DEFAULT",
            )
        snapshot.match("invalid-permissions-account-2-role", e.value.response)

        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": "kms:Encrypt",
                    "Resource": key_arn,
                }
            ],
        }
        secondary_aws_client.iam.put_role_policy(
            RoleName=role_name, PolicyName=policy_name, PolicyDocument=json.dumps(policy)
        )
        cleanups.append(
            lambda: secondary_aws_client.iam.delete_role_policy(
                RoleName=role_name, PolicyName=policy_name
            )
        )

        def _receive():
            return role_aws_clients.kms.encrypt(
                KeyId=key_arn,
                Plaintext=base64.b64encode(message),
                EncryptionAlgorithm="SYMMETRIC_DEFAULT",
            )

        publish_response = retry(_receive, sleep=10 if is_aws_cloud() else 1, retries=20)
        snapshot.match("valid-permissions-account-2-role", publish_response)

    @markers.snapshot.skip_snapshot_verify(paths=["$..Error.Message", "$..ServerSideEncryption"])
    @markers.aws.validated
    def test_s3_cross_account_get_object(
        self,
        aws_client,
        secondary_aws_client,
        secondary_account_id,
        s3_bucket,
        cleanups,
        assume_role_account_2,
        assume_role_policy_account_2,
        snapshot,
        region_name,
    ):
        snapshot.add_transformer(snapshot.transform.kms_api())
        role_name = f"test-role-{short_uid()}"
        policy_name = f"test-policy-{short_uid()}"

        # add snapshot ignore for current client arn replacement
        caller_identity_2 = secondary_aws_client.sts.get_caller_identity()
        snapshot.match("caller-identity-2", caller_identity_2)

        # test regular publish within account
        put_object_response = aws_client.s3.put_object(Bucket=s3_bucket, Key="test", Body=b"test")
        snapshot.match("intra-account-operation", put_object_response)

        with pytest.raises(ClientError) as e:
            secondary_aws_client.s3.put_object(Bucket=s3_bucket, Key="test", Body=b"test")
        snapshot.match("invalid-permissions-account-2-without-role", e.value.response)

        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": "s3:PutObject",
                    "Principal": {"AWS": [secondary_account_id]},
                    "Resource": [
                        f"arn:{get_partition(region_name)}:s3:::{s3_bucket}",
                        f"arn:{get_partition(region_name)}:s3:::{s3_bucket}/*",
                    ],
                }
            ],
        }
        aws_client.s3.put_bucket_policy(Bucket=s3_bucket, Policy=json.dumps(policy))

        put_object_response = secondary_aws_client.s3.put_object(
            Bucket=s3_bucket, Key="test", Body=b"test"
        )
        snapshot.match("valid-permissions-account-2-without-role", put_object_response)

        create_role_response = secondary_aws_client.iam.create_role(
            RoleName=role_name, AssumeRolePolicyDocument=assume_role_policy_account_2
        )
        snapshot.match("create-role-response", create_role_response)
        role_arn = create_role_response["Role"]["Arn"]
        cleanups.append(lambda: secondary_aws_client.iam.delete_role(RoleName=role_name))

        role_aws_clients = assume_role_account_2(role_arn)

        if is_aws_cloud():
            time.sleep(10)

        with pytest.raises(ClientError) as e:
            role_aws_clients.s3.put_object(Bucket=s3_bucket, Key="test", Body=b"test")
        snapshot.match("invalid-permissions-account-2-role", e.value.response)

        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": "s3:PutObject",
                    "Resource": [
                        f"arn:{get_partition(region_name)}:s3:::{s3_bucket}",
                        f"arn:{get_partition(region_name)}:s3:::{s3_bucket}/*",
                    ],
                }
            ],
        }
        secondary_aws_client.iam.put_role_policy(
            RoleName=role_name, PolicyName=policy_name, PolicyDocument=json.dumps(policy)
        )
        cleanups.append(
            lambda: secondary_aws_client.iam.delete_role_policy(
                RoleName=role_name, PolicyName=policy_name
            )
        )

        def _put_object():
            return role_aws_clients.s3.put_object(Bucket=s3_bucket, Key="test", Body=b"test")

        publish_response = retry(_put_object, sleep=10 if is_aws_cloud() else 1, retries=20)
        snapshot.match("valid-permissions-account-2-role", publish_response)

    @markers.aws.validated
    def test_s3_cross_account_get_object_with_role_arn_in_bucket_policy(
        self,
        aws_client,
        secondary_aws_client,
        secondary_account_id,
        s3_bucket,
        cleanups,
        assume_role_account_2,
        assume_role_policy_account_2,
        snapshot,
        region_name,
    ):
        snapshot.add_transformer(snapshot.transform.kms_api())
        role_name = f"test-role-{short_uid()}"
        policy_name = f"test-policy-{short_uid()}"

        # add snapshot ignore for secondary account replacement
        caller_identity_2 = secondary_aws_client.sts.get_caller_identity()
        snapshot.match("caller-identity-2", caller_identity_2)

        # put object to get later
        aws_client.s3.put_object(Bucket=s3_bucket, Key="test", Body=b"test")

        create_role_response = secondary_aws_client.iam.create_role(
            RoleName=role_name, AssumeRolePolicyDocument=assume_role_policy_account_2
        )
        snapshot.match("create-role-response", create_role_response)
        role_arn = create_role_response["Role"]["Arn"]
        cleanups.append(lambda: secondary_aws_client.iam.delete_role(RoleName=role_name))

        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": "s3:PutObject",
                    "Principal": {"AWS": [role_arn]},
                    "Resource": [
                        f"arn:{get_partition(region_name)}:s3:::{s3_bucket}",
                        f"arn:{get_partition(region_name)}:s3:::{s3_bucket}/*",
                    ],
                }
            ],
        }

        def _put_bucket_policy():
            return aws_client.s3.put_bucket_policy(Bucket=s3_bucket, Policy=json.dumps(policy))

        put_bucket_policy_response = retry(
            _put_bucket_policy, sleep=10 if is_aws_cloud() else 1, retries=5
        )
        snapshot.match("put-bucket-policy-response", put_bucket_policy_response)

        role_aws_clients = assume_role_account_2(role_arn)

        with pytest.raises(ClientError) as e:
            role_aws_clients.s3.put_object(Bucket=s3_bucket, Key="test", Body=b"test")
        snapshot.match("invalid-permissions-account-2-role", e.value.response)

        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": "s3:PutObject",
                    "Resource": [
                        f"arn:{get_partition(region_name)}:s3:::{s3_bucket}",
                        f"arn:{get_partition(region_name)}:s3:::{s3_bucket}/*",
                    ],
                }
            ],
        }
        secondary_aws_client.iam.put_role_policy(
            RoleName=role_name, PolicyName=policy_name, PolicyDocument=json.dumps(policy)
        )
        cleanups.append(
            lambda: secondary_aws_client.iam.delete_role_policy(
                RoleName=role_name, PolicyName=policy_name
            )
        )

        def _put_object():
            return role_aws_clients.s3.put_object(Bucket=s3_bucket, Key="test", Body=b"test")

        publish_response = retry(_put_object, sleep=10 if is_aws_cloud() else 1, retries=20)
        snapshot.match("valid-permissions-account-2-role", publish_response)

    @markers.aws.validated
    def test_cross_account_assume_role(
        self,
        aws_client,
        account_id,
        secondary_aws_client,
        assume_role_policy_account_2,
        assume_role_account_2,
        snapshot,
        cleanups,
    ):
        """The purpose of this test is to verify if a role in account 2 can assume a role in account 1 with the right permissions"""
        snapshot.add_transformer(snapshot.transform.iam_api())
        snapshot.add_transformer(snapshot.transform.key_value("AWS"))
        role_name_1 = f"test-role-{short_uid()}"
        role_name_2 = f"test-role-{short_uid()}"
        policy_name = f"test-policy-{short_uid()}"
        # this is the role the test wants to assume
        create_role_1_response = aws_client.iam.create_role(
            RoleName=role_name_1, AssumeRolePolicyDocument=assume_role_policy_account_2
        )
        cleanups.append(lambda: secondary_aws_client.iam.delete_role(RoleName=role_name_1))
        snapshot.match("create-role-1-response", create_role_1_response)
        role_arn_account_1 = create_role_1_response["Role"]["Arn"]
        # this is the role which will assume the other role
        create_role_2_response = secondary_aws_client.iam.create_role(
            RoleName=role_name_2, AssumeRolePolicyDocument=assume_role_policy_account_2
        )
        cleanups.append(lambda: secondary_aws_client.iam.delete_role(RoleName=role_name_2))
        snapshot.match("create-role-2-response", create_role_2_response)
        role_arn_account_2 = create_role_2_response["Role"]["Arn"]
        # assume role in account 2
        role_account_2_clients = assume_role_account_2(role_arn_account_2)

        with pytest.raises(ClientError) as e:
            role_account_2_clients.sts.assume_role(
                RoleArn=role_arn_account_1, RoleSessionName="TestSession"
            )
        snapshot.match("denied-assume-role-call", e.value.response)

        allow_assume_role_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {"Effect": "Allow", "Action": "sts:AssumeRole", "Resource": [role_arn_account_1]}
            ],
        }
        secondary_aws_client.iam.put_role_policy(
            RoleName=role_name_2,
            PolicyName=policy_name,
            PolicyDocument=json.dumps(allow_assume_role_policy),
        )
        cleanups.append(
            lambda: secondary_aws_client.iam.delete_role_policy(
                RoleName=role_name_2, PolicyName=policy_name
            )
        )

        def _try_assume_role():
            role_account_2_clients.sts.assume_role(
                RoleArn=role_arn_account_1, RoleSessionName="TestSession"
            )

        retry(_try_assume_role, retries=30, sleep=30 if is_aws_cloud() else 1)

        # deny assume role for account 2
        deny_assume_role_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "sts:AssumeRole",
                    "Principal": {"AWS": account_id},
                    "Effect": "Allow",
                }
            ],
        }
        aws_client.iam.update_assume_role_policy(
            RoleName=role_name_1, PolicyDocument=json.dumps(deny_assume_role_policy)
        )

        def _check_assume_role_denied():
            try:
                role_account_2_clients.sts.assume_role(
                    RoleArn=role_arn_account_1, RoleSessionName="TestSessionDenied"
                )
                return False
            except Exception:
                return True

        assert poll_condition(
            _check_assume_role_denied, timeout=300, interval=30 if is_aws_cloud() else 1
        )

    @markers.aws.validated
    def test_lambda_sqs_cross_account_event_source_mapping(
        self,
        aws_client,
        secondary_aws_client,
        secondary_account_id,
        create_lambda_function,
        cleanups,
        assume_role_account_2,
        assume_role_policy_account_2,
        snapshot,
        lambda_su_role,
        account_id,
    ):
        snapshot.add_transformer(snapshot.transform.key_value("CodeSha256"))
        snapshot.add_transformer(snapshot.transform.lambda_api())
        snapshot.add_transformer(snapshot.transform.regex(secondary_account_id, "222222222222"))
        function_name = f"test-function-{short_uid()}"
        queue_name = f"test-queue-{short_uid()}"
        create_function_response = create_lambda_function(
            func_name=function_name,
            handler_file=TEST_LAMBDA_ECHO,
            runtime=Runtime.python3_12,
            role=lambda_su_role,
        )["CreateFunctionResponse"]
        snapshot.match("create-function-response", create_function_response)

        queue_url = secondary_aws_client.sqs.create_queue(QueueName=queue_name)["QueueUrl"]
        cleanups.append(lambda: secondary_aws_client.sqs.delete_queue(QueueUrl=queue_url))
        queue_arn = secondary_aws_client.sqs.get_queue_attributes(
            QueueUrl=queue_url, AttributeNames=["QueueArn"]
        )["Attributes"]["QueueArn"]
        secondary_aws_client.sqs.add_permission(
            QueueUrl=queue_url,
            AWSAccountIds=[account_id],
            Actions=["ReceiveMessage", "DeleteMessage", "GetQueueAttributes"],
            Label="CrossAccountAccess",
        )

        create_event_source_mapping_response = aws_client.lambda_.create_event_source_mapping(
            EventSourceArn=queue_arn,
            FunctionName=function_name,
            MaximumBatchingWindowInSeconds=1,
        )
        mapping_uuid = create_event_source_mapping_response["UUID"]
        cleanups.append(lambda: aws_client.lambda_.delete_event_source_mapping(UUID=mapping_uuid))
        snapshot.match("create-event-source-mapping-response", create_event_source_mapping_response)
        _await_event_source_mapping_enabled(aws_client.lambda_, mapping_uuid)

        secondary_aws_client.sqs.send_message(
            QueueUrl=queue_url, MessageBody=json.dumps({"event": 1})
        )

        def _assert_events(expected_events: int):
            log_events = aws_client.logs.filter_log_events(
                logGroupName=f"/aws/lambda/{function_name}",
            )["events"]
            assert (
                len([e["message"] for e in log_events if e["message"].startswith("REPORT")])
                == expected_events
            )

        retry(_assert_events, expected_events=1, retries=20, sleep=2)

        rs = secondary_aws_client.sqs.receive_message(QueueUrl=queue_url)
        assert rs.get("Messages", []) == []
        secondary_aws_client.sqs.remove_permission(QueueUrl=queue_url, Label="CrossAccountAccess")

        # give time for permission changes
        retries = 20 if is_aws_cloud() else 5
        with pytest.raises(Exception):
            for i in range(retries):
                retry_id = i + 2
                secondary_aws_client.sqs.send_message(
                    QueueUrl=queue_url, MessageBody=json.dumps({"event": retry_id})
                )

                retry(
                    _assert_events,
                    expected_events=retry_id,
                    retries=20 if is_aws_cloud() else 5,
                    sleep=3 if is_aws_cloud() else 1,
                )
