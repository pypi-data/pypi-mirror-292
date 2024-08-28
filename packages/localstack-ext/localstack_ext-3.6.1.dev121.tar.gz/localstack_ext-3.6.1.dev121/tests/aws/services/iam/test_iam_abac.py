import json

import pytest
from botocore.exceptions import ClientError
from localstack.testing.pytest import markers
from localstack.utils.aws import arns
from localstack.utils.aws.arns import get_partition
from localstack.utils.strings import short_uid


@pytest.fixture(scope="module")
def assume_role_policy_document_account(account_id):
    return json.dumps(
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": ["sts:AssumeRole", "sts:TagSession"],
                    "Principal": {"AWS": account_id},
                    "Effect": "Allow",
                }
            ],
        }
    )


@pytest.fixture
def role_with_policy_trust_account(aws_client, create_role, assume_role_policy_document_account):
    def _create_role_with_policy(policy_document: dict, **kwargs):
        policy_name = f"policy-{short_uid()}"
        create_role_result = create_role(
            AssumeRolePolicyDocument=assume_role_policy_document_account, **kwargs
        )
        aws_client.iam.put_role_policy(
            RoleName=create_role_result["Role"]["RoleName"],
            PolicyName=policy_name,
            PolicyDocument=json.dumps(policy_document),
        )
        return create_role_result

    return _create_role_with_policy


class TestIAMABAC:
    @pytest.fixture(autouse=True)
    def snapshot_transformers(self, snapshot):
        snapshot.add_transformer(snapshot.transform.iam_api())
        snapshot.add_transformer([snapshot.transform.key_value("Name")])

    @markers.aws.validated
    def test_s3_iam_principal_tag_on_session(
        self,
        aws_client,
        role_with_policy_trust_account,
        client_factory_for_role,
        s3_bucket,
        snapshot,
        region_name,
    ):
        policy = {
            "Version": "2012-10-17",
            "Statement": {
                "Effect": "Allow",
                "Action": "s3:ListBucket",
                "Resource": [arns.s3_bucket_arn(s3_bucket, region=region_name)],
                "Condition": {"StringEquals": {"aws:PrincipalTag/test": "test"}},
            },
        }
        role_name = role_with_policy_trust_account(policy)["Role"]["RoleName"]

        role_client = client_factory_for_role(role_name=role_name, session_name="Session1")
        with pytest.raises(ClientError) as e:
            role_client.s3.list_objects_v2(Bucket=s3_bucket)
        snapshot.match("denied-no-tags", e.value.response)

        role_client = client_factory_for_role(
            role_name=role_name, session_name="Session2", Tags=[{"Key": "test", "Value": "wrong"}]
        )
        with pytest.raises(ClientError) as e:
            role_client.s3.list_objects_v2(Bucket=s3_bucket)
        snapshot.match("denied-wrong-tag", e.value.response)

        role_client = client_factory_for_role(
            role_name=role_name, session_name="Session3", Tags=[{"Key": "test", "Value": "test"}]
        )
        response = role_client.s3.list_objects_v2(Bucket=s3_bucket)
        snapshot.match("allowed-right-tag", response)

    @markers.aws.validated
    def test_s3_iam_principal_tag_on_session_independence(
        self,
        aws_client,
        role_with_policy_trust_account,
        client_factory_for_role,
        s3_bucket,
        snapshot,
        region_name,
    ):
        policy = {
            "Version": "2012-10-17",
            "Statement": {
                "Effect": "Allow",
                "Action": "s3:ListBucket",
                "Resource": [arns.s3_bucket_arn(s3_bucket, region=region_name)],
                "Condition": {"StringEquals": {"aws:PrincipalTag/test": "test"}},
            },
        }
        role_name = role_with_policy_trust_account(policy)["Role"]["RoleName"]

        # same session - should not influence tags
        role_client_1 = client_factory_for_role(
            role_name=role_name, session_name="Session", Tags=[{"Key": "test", "Value": "test"}]
        )
        role_client_2 = client_factory_for_role(
            role_name=role_name, session_name="Session", Tags=[{"Key": "test", "Value": "wrong"}]
        )
        response = role_client_1.s3.list_objects_v2(Bucket=s3_bucket)
        snapshot.match("allowed-right-tag", response)
        with pytest.raises(ClientError) as e:
            role_client_2.s3.list_objects_v2(Bucket=s3_bucket)
        snapshot.match("denied-wrong-tag", e.value.response)

    @markers.aws.validated
    def test_s3_iam_principal_tag_on_role(
        self,
        aws_client,
        role_with_policy_trust_account,
        client_factory_for_role,
        s3_bucket,
        snapshot,
        region_name,
    ):
        policy = {
            "Version": "2012-10-17",
            "Statement": {
                "Effect": "Allow",
                "Action": "s3:ListBucket",
                "Resource": [arns.s3_bucket_arn(s3_bucket, region=region_name)],
                "Condition": {"StringEquals": {"aws:PrincipalTag/test": "test"}},
            },
        }
        role_name = role_with_policy_trust_account(policy, Tags=[{"Key": "test", "Value": "test"}])[
            "Role"
        ]["RoleName"]
        role_client = client_factory_for_role(
            role_name=role_name, session_name="Session1", Tags=[{"Key": "test", "Value": "wrong"}]
        )
        with pytest.raises(ClientError) as e:
            role_client.s3.list_objects_v2(Bucket=s3_bucket)
        snapshot.match("denied-wrong-tag-override", e.value.response)

        role_client = client_factory_for_role(role_name=role_name, session_name="Session2")
        response = role_client.s3.list_objects_v2(Bucket=s3_bucket)
        snapshot.match("allowed-right-tag", response)

    @markers.aws.validated
    def test_s3_iam_principal_tag_in_policy_resource_arn(
        self,
        aws_client,
        role_with_policy_trust_account,
        client_factory_for_role,
        s3_bucket,
        snapshot,
        region_name,
    ):
        policy = {
            "Version": "2012-10-17",
            "Statement": {
                "Effect": "Allow",
                "Action": [
                    "s3:ListMultipartUploadParts",
                    "s3:AbortMultipartUpload",
                    "s3:GetObject",
                    "s3:PutObject",
                    "s3:PutObjectTagging",
                    "s3:PutObjectVersionTagging",
                    "s3:SelectObjectContent",
                    "s3:ListObjects",
                    "s3:ListObjectsV2",
                ],
                "Resource": [
                    f"arn:{get_partition(region_name)}:s3:::${{aws:PrincipalTag/BucketTag}}/${{aws:PrincipalTag/KeyTag}}",
                    f"arn:{get_partition(region_name)}:s3:::${{aws:PrincipalTag/BucketTag}}/${{aws:PrincipalTag/KeyTag}}/*",
                ],
            },
        }
        role_name = role_with_policy_trust_account(policy)["Role"]["RoleName"]

        role_client = client_factory_for_role(
            role_name=role_name,
            session_name="Session1",
            Tags=[
                {"Key": "BucketTag", "Value": "wrong-bucket"},
                {"Key": "KeyTag", "Value": "right-key"},
            ],
        )
        with pytest.raises(ClientError) as e:
            role_client.s3.put_object(
                Bucket=s3_bucket, Key="right-key/some-file", Body=b"filecontent"
            )
        snapshot.match("denied-wrong-bucket-tag", e.value.response)

        role_client = client_factory_for_role(
            role_name=role_name,
            session_name="Session2",
            Tags=[
                {"Key": "BucketTag", "Value": s3_bucket},
                {"Key": "KeyTag", "Value": "wrong-key"},
            ],
        )
        with pytest.raises(ClientError) as e:
            role_client.s3.put_object(
                Bucket=s3_bucket, Key="right-key/some-file", Body=b"filecontent"
            )
        snapshot.match("denied-wrong-key-tag", e.value.response)

        role_client = client_factory_for_role(
            role_name=role_name,
            session_name="Session3",
            Tags=[
                {"Key": "BucketTag", "Value": s3_bucket},
                {"Key": "KeyTag", "Value": "right-key"},
            ],
        )
        # "root" key should be allowed
        role_client.s3.put_object(Bucket=s3_bucket, Key="right-key", Body=b"filecontent")
        # all keys with the right prefix should be allowed
        role_client.s3.put_object(Bucket=s3_bucket, Key="right-key/some-file", Body=b"filecontent")
        # wrong leading keys should not be allowed
        with pytest.raises(ClientError) as e:
            role_client.s3.put_object(
                Bucket=s3_bucket, Key="wrong-key/some-file", Body=b"filecontent"
            )
        snapshot.match("denied-wrong-leading-key", e.value.response)
        # wrong leading keys with right key in the middle should not be allowed
        with pytest.raises(ClientError) as e:
            role_client.s3.put_object(
                Bucket=s3_bucket, Key="wrong-key/right-key/some-file", Body=b"filecontent"
            )
        snapshot.match("denied-wrong-leading-key-right-key-nested", e.value.response)

    @markers.aws.validated
    def test_s3_iam_principal_tag_list_bucket_prefix(
        self,
        aws_client,
        role_with_policy_trust_account,
        client_factory_for_role,
        s3_bucket,
        snapshot,
        region_name,
    ):
        policy = {
            "Version": "2012-10-17",
            "Statement": {
                "Sid": "S3AccessListBucketForKeyTag",
                "Effect": "Allow",
                "Action": ["s3:ListBucket"],
                "Resource": [
                    f"arn:{get_partition(region_name)}:s3:::${{aws:PrincipalTag/BucketTag}}"
                ],
                "Condition": {
                    "StringLike": {
                        "s3:prefix": [
                            "${aws:PrincipalTag/KeyTag}",
                            "${aws:PrincipalTag/KeyTag}/*",
                        ]
                    }
                },
            },
        }
        role_name = role_with_policy_trust_account(policy)["Role"]["RoleName"]
        aws_client.s3.put_object(Bucket=s3_bucket, Key="right-key/some-file", Body=b"filecontent")

        role_client = client_factory_for_role(
            role_name=role_name,
            session_name="Session1",
            Tags=[
                {"Key": "BucketTag", "Value": s3_bucket},
                {"Key": "KeyTag", "Value": "wrong-key"},
            ],
        )
        # wrong key tag set - should fail
        with pytest.raises(ClientError) as e:
            role_client.s3.list_objects_v2(Bucket=s3_bucket, Prefix="right-key")
        snapshot.match("denied-wrong-key-tag", e.value.response)

        role_client = client_factory_for_role(
            role_name=role_name,
            session_name="Session2",
            Tags=[
                {"Key": "BucketTag", "Value": s3_bucket},
                {"Key": "KeyTag", "Value": "right-key"},
            ],
        )
        # without prefix - should fail
        with pytest.raises(ClientError) as e:
            role_client.s3.list_objects_v2(Bucket=s3_bucket)
        snapshot.match("denied-no-prefix", e.value.response)
        # right prefix and right tag - should succeed
        response = role_client.s3.list_objects_v2(Bucket=s3_bucket, Prefix="right-key")
        snapshot.match("allowed-list-objects", response)

    @markers.aws.validated
    def test_secretsmanager_tags_on_resource_and_principal(
        self,
        aws_client,
        role_with_policy_trust_account,
        client_factory_for_role,
        create_secret,
        snapshot,
        account_id,
        region_name,
    ):
        policy = {
            "Version": "2012-10-17",
            "Statement": {
                "Effect": "Allow",
                "Action": "secretsmanager:GetSecretValue",
                "Resource": [
                    f"arn:{get_partition(region_name)}:secretsmanager:{region_name}:{account_id}:secret:*"
                ],
                "Condition": {
                    "StringEquals": {"aws:ResourceTag/TestTag": "${aws:PrincipalTag/TestTag}"}
                },
            },
        }
        create_role_result = role_with_policy_trust_account(policy)
        snapshot.match("create-role-result", create_role_result)
        role_name = create_role_result["Role"]["RoleName"]
        create_secret_result = create_secret(
            Name=f"test-secret-{short_uid()}",
            SecretString="test",
            Tags=[{"Key": "TestTag", "Value": "TagValue"}],
        )
        secret_arn = create_secret_result["ARN"]
        snapshot.add_transformer(
            snapshot.transform.secretsmanager_secret_id_arn(create_secret_result, 0)
        )

        role_client = client_factory_for_role(role_name=role_name, session_name="Session1")
        with pytest.raises(ClientError) as e:
            role_client.secretsmanager.get_secret_value(SecretId=secret_arn)
        snapshot.match("denied-no-tag", e.value.response)

        role_client = client_factory_for_role(
            role_name=role_name,
            session_name="Session2",
            Tags=[{"Key": "TestTag", "Value": "TagValue1"}],
        )
        with pytest.raises(ClientError) as e:
            role_client.secretsmanager.get_secret_value(SecretId=secret_arn)
        snapshot.match("denied-wrong-tag", e.value.response)

        role_client = client_factory_for_role(
            role_name=role_name,
            session_name="Session3",
            Tags=[{"Key": "TestTag", "Value": "TagValue"}],
        )
        response = role_client.secretsmanager.get_secret_value(SecretId=secret_arn)
        snapshot.match("allowed-right-tag", response)

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(
        paths=[
            "$..TableDescription.BillingModeSummary.LastUpdateToPayPerRequestDateTime",
            "$..TableDescription.DeletionProtectionEnabled",
            "$..TableDescription.ProvisionedThroughput.LastDecreaseDateTime",
            "$..TableDescription.ProvisionedThroughput.LastIncreaseDateTime",
            "$..TableDescription.TableStatus",
        ]
    )
    def test_dynamodb_leading_keys_tags(
        self,
        aws_client,
        role_with_policy_trust_account,
        client_factory_for_role,
        dynamodb_create_table_with_parameters,
        snapshot,
        account_id,
        region_name,
    ):
        snapshot.add_transformer(snapshot.transform.key_value("TableName"))
        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "ProvideAccessToDynamoDbItemsMatchingTags",
                    "Effect": "Allow",
                    "Action": [
                        "dynamodb:DescribeTable",
                        "dynamodb:GetItem",
                        "dynamodb:BatchGetItem",
                        "dynamodb:Query",
                        "dynamodb:PutItem",
                        "dynamodb:UpdateItem",
                        "dynamodb:BatchWriteItem",
                        "dynamodb:DeleteItem",
                    ],
                    "Resource": [
                        f"arn:{get_partition(region_name)}:dynamodb:*:{account_id}:table/${{aws:PrincipalTag/TableTag}}",
                        f"arn:{get_partition(region_name)}:dynamodb:*:{account_id}:table/${{aws:PrincipalTag/TableTag}}/index/*",
                    ],
                    "Condition": {
                        "ForAllValues:StringLike": {
                            "dynamodb:LeadingKeys": [
                                "${aws:PrincipalTag/KeyTag}",
                                "${aws:PrincipalTag/KeyTag}-*",
                            ]
                        }
                    },
                }
            ],
        }
        create_role_result = role_with_policy_trust_account(policy)
        snapshot.match("create-role-result", create_role_result)
        role_name = create_role_result["Role"]["RoleName"]
        create_table_result = dynamodb_create_table_with_parameters(
            AttributeDefinitions=[{"AttributeName": "TestAttribute", "AttributeType": "S"}],
            KeySchema=[{"AttributeName": "TestAttribute", "KeyType": "HASH"}],
            BillingMode="PAY_PER_REQUEST",
        )
        snapshot.match("create-table-result", create_table_result)
        table_name = create_table_result["TableDescription"]["TableName"]

        # Test wrong attribute name
        role_client = client_factory_for_role(
            role_name=role_name,
            session_name="Session1",
            Tags=[
                {"Key": "TableTag", "Value": table_name},
                {"Key": "KeyTag", "Value": "RightKey"},
            ],
        )
        # wrong key should be denied
        with pytest.raises(ClientError) as e:
            role_client.dynamodb.put_item(
                TableName=table_name, Item={"TestAttribute": {"S": "WrongKey"}}
            )
        snapshot.match("denied-wrong-key", e.value.response)
        # right key should work
        response = role_client.dynamodb.put_item(
            TableName=table_name, Item={"TestAttribute": {"S": "RightKey"}}
        )
        snapshot.match("right-key", response)
        # also matching the regex
        response = role_client.dynamodb.put_item(
            TableName=table_name, Item={"TestAttribute": {"S": "RightKey-suffix"}}
        )
        snapshot.match("right-key-prefix", response)

        # test batch write operations - one valid and one invalid (permission wise) key
        with pytest.raises(ClientError) as e:
            role_client.dynamodb.batch_write_item(
                RequestItems={
                    table_name: [
                        {
                            "PutRequest": {
                                "Item": {
                                    "AdditionalAttribute": {"S": "SomeKey"},
                                    "TestAttribute": {"S": "RightKey"},
                                }
                            }
                        },
                        {
                            "PutRequest": {
                                "Item": {
                                    "AdditionalAttribute": {"S": "SomeKey"},
                                    "TestAttribute": {"S": "WrongKey"},
                                }
                            }
                        },
                    ]
                }
            )
        snapshot.match("denied-batch-write-one-wrong-key", e.value.response)

        # test batch operations - two valid keys
        response = role_client.dynamodb.batch_write_item(
            RequestItems={
                table_name: [
                    {
                        "PutRequest": {
                            "Item": {
                                "TestAttribute": {"S": "RightKey"},
                                "AdditionalAttribute": {"S": "SomeKey"},
                            }
                        }
                    },
                    {
                        "PutRequest": {
                            "Item": {
                                "AdditionalAttribute": {"S": "SomeKey"},
                                "TestAttribute": {"S": "RightKey-suffix1"},
                            }
                        }
                    },
                ]
            }
        )
        snapshot.match("right-batch-write", response)

        # test batch read operations - one valid and one invalid (permission wise) key
        with pytest.raises(ClientError) as e:
            role_client.dynamodb.batch_get_item(
                RequestItems={
                    table_name: {
                        "Keys": [
                            {
                                "TestAttribute": {"S": "RightKey"},
                            },
                            {
                                "TestAttribute": {"S": "WrongKey"},
                            },
                        ]
                    }
                }
            )
        snapshot.match("denied-batch-get-one-wrong-key", e.value.response)

        # test batch operations - two valid keys
        response = role_client.dynamodb.batch_get_item(
            RequestItems={
                table_name: {
                    "Keys": [
                        {
                            "TestAttribute": {"S": "RightKey"},
                        },
                        {
                            "TestAttribute": {"S": "RightKey-suffix1"},
                        },
                    ]
                }
            }
        )
        snapshot.match("right-batch-get", response)
