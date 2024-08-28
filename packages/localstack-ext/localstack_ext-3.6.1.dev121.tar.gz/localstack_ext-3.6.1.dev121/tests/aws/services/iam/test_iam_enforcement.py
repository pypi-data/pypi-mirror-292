import json
import logging
import os
import time
from contextlib import ExitStack
from datetime import datetime, timedelta
from typing import TYPE_CHECKING

import pytest
from boto3.exceptions import S3UploadFailedError
from boto3.s3.transfer import KB, TransferConfig
from botocore.exceptions import ClientError
from localstack.aws.api.lambda_ import Architecture, Runtime
from localstack.testing.aws.util import create_client_with_keys, is_aws_cloud, wait_for_user
from localstack.testing.pytest import markers
from localstack.utils.aws import arns, resources
from localstack.utils.aws.arns import get_partition, sqs_queue_arn
from localstack.utils.strings import short_uid
from localstack.utils.sync import poll_condition, retry
from localstack.utils.testutil import create_lambda_archive

if TYPE_CHECKING:
    from mypy_boto3_ecr import ECRClient
    from mypy_boto3_lambda import LambdaClient
    from mypy_boto3_sns import SNSClient
    from mypy_boto3_sqs import SQSClient

TEST_SIMPLE_LAMBDA = """
def handler(event, context):
    return "ok"
"""
ROLE_ASSUME_POLICY_LAMBDA = """
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
""".strip()

LOG = logging.getLogger(__name__)


@pytest.fixture
def create_client_for_user(aws_client, region_name):
    def _create_client_for_user(user_name: str, service: str):
        keys = aws_client.iam.create_access_key(UserName=user_name)["AccessKey"]
        wait_for_user(keys, region_name)
        return create_client_with_keys(service=service, keys=keys, region_name=region_name)

    return _create_client_for_user


class TestIAMEnforcementIdentityBasedPolicies:
    @markers.aws.validated
    def test_enforce_policy_lambda(
        self,
        client_for_new_user,
        create_and_assume_role,
        create_role_with_policy,
        wait_until_lambda_ready,
    ):
        # create ALLOW/DENY policies and users
        actions = [
            "lambda:CreateFunction",
            "lambda:DeleteFunction",
            "lambda:InvokeFunction",
            "iam:PassRole",
        ]
        lambda_client_allow = client_for_new_user("lambda", "Allow", actions)
        lambda_client_deny = client_for_new_user("lambda", "Deny", actions)

        # attempt to create lambda - ALLOW
        func_name = short_uid()
        zip_file = create_lambda_archive(TEST_SIMPLE_LAMBDA, get_content=True, file_name="main.py")
        role_name, role_arn = create_role_with_policy(
            "Allow", ["lambda:InvokeFunction"], ROLE_ASSUME_POLICY_LAMBDA
        )
        kwargs = {
            "Runtime": "python3.8",
            "Role": role_arn,
            "Handler": "main.handler",
            "Code": {"ZipFile": zip_file},
        }

        def create_function():
            lambda_client_allow.create_function(FunctionName=func_name, **kwargs)

        # retry since in AWS it takes time before you are able to assume a role
        retry(create_function, sleep=5, retries=4)

        # attempt to create lambda - DENY
        self.assert_access_denied(
            lambda_client_deny.create_function, FunctionName=short_uid(), **kwargs
        )
        wait_until_lambda_ready(function_name=func_name)

        # attempt to invoke lambda - ALLOW
        invoke_response = lambda_client_allow.invoke(FunctionName=func_name)
        assert invoke_response["ResponseMetadata"]["HTTPStatusCode"] == 200

        # attempt to invoke lambda - DENY
        self.assert_access_denied(lambda_client_deny.invoke, FunctionName=func_name)

        # clean up
        lambda_client_allow.delete_function(FunctionName=func_name)

    @markers.aws.validated
    def test_enforce_policy_sqs(self, client_for_new_user):
        # create ALLOW/DENY policies and users
        actions = ["sqs:CreateQueue", "sqs:DeleteQueue"]
        sqs_client_allow = client_for_new_user("sqs", "Allow", actions)
        sqs_client_deny = client_for_new_user("sqs", "Deny", actions)

        # attempt to create queue - ALLOW
        queue_url = sqs_client_allow.create_queue(QueueName=short_uid())["QueueUrl"]

        # attempt to create queue - DENY
        self.assert_access_denied(sqs_client_deny.create_queue, QueueName=short_uid())

        # clean up
        sqs_client_allow.delete_queue(QueueUrl=queue_url)

    @markers.aws.validated
    def test_enforce_policy_kinesis(self, client_for_new_user):
        # create ALLOW/DENY policies and users
        actions = ["kinesis:CreateStream", "kinesis:DeleteStream"]
        kinesis_client_allow = client_for_new_user("kinesis", "Allow", actions)
        kinesis_client_deny = client_for_new_user("kinesis", "Deny", actions)

        # attempt to create - ALLOW
        stream_name = short_uid()
        kinesis_client_allow.create_stream(StreamName=stream_name, ShardCount=1)
        # sleep some time to let the stream initialize (TODO: replace with status polling once fixtures of community can be reused)
        time.sleep(1)

        # attempt to create - DENY
        self.assert_access_denied(
            kinesis_client_deny.create_stream, StreamName=short_uid(), ShardCount=1
        )

        # clean up
        kinesis_client_allow.delete_stream(StreamName=stream_name)

    @markers.aws.validated
    def test_enforce_policy_dynamodb(self, client_for_new_user):
        # create ALLOW/DENY policies and users
        actions = ["dynamodb:CreateTable", "dynamodb:DescribeTable", "dynamodb:DeleteTable"]
        dynamodb_client_allow = client_for_new_user("dynamodb", "Allow", actions)
        dynamodb_client_deny = client_for_new_user("dynamodb", "Deny", actions)

        # attempt to create - ALLOW
        table_name = short_uid()
        resources.create_dynamodb_table(
            table_name=table_name, partition_key="id", client=dynamodb_client_allow
        )

        # attempt to create - DENY
        self.assert_access_denied(
            resources.create_dynamodb_table,
            table_name=short_uid(),
            partition_key="id",
            client=dynamodb_client_deny,
        )

        def wait_for_table_created():
            return (
                dynamodb_client_allow.describe_table(TableName=table_name)["Table"]["TableStatus"]
                == "ACTIVE"
            )

        poll_condition(wait_for_table_created, timeout=30)

        # clean up
        dynamodb_client_allow.delete_table(TableName=table_name)

    @markers.aws.validated
    def test_enforce_policy_cloudformation(self, client_for_new_user):
        # create ALLOW/DENY policies and users
        actions = ["cloudformation:ListStacks"]
        cloudformation_client_allow = client_for_new_user("cloudformation", "Allow", actions)
        cloudformation_client_deny = client_for_new_user("cloudformation", "Deny", actions)

        # attempt to list stacks - ALLOW
        cloudformation_client_allow.list_stacks()

        # attempt to list stacks - DENY
        self.assert_access_denied(cloudformation_client_deny.list_stacks)

    @markers.aws.validated
    def test_enforce_policy_s3(self, client_for_new_user, tmpdir):
        # create ALLOW/DENY policies and users
        actions = ["s3:CreateBucket", "s3:PutObject", "s3:DeleteBucket", "s3:DeleteObject"]
        s3_client_allow = client_for_new_user("s3", "Allow", actions)
        s3_client_deny = client_for_new_user("s3", "Deny", actions)
        # attempt to create bucket - ALLOW
        bucket_name = short_uid()
        with ExitStack() as stack:
            resources.create_s3_bucket(bucket_name, s3_client=s3_client_allow)
            stack.callback(s3_client_allow.delete_bucket, Bucket=bucket_name)
            s3_client_allow.put_object(Bucket=bucket_name, Key="test1", Body="abc")
            stack.callback(s3_client_allow.delete_object, Bucket=bucket_name, Key="test1")

            # test CreateMultipartUpload, UploadPart and CompleteMultipartUpload actions (using s3:PutObject permission)
            # https://docs.aws.amazon.com/AmazonS3/latest/userguide/mpuoverview.html#mpuAndPermissions
            transfer_config = TransferConfig(multipart_threshold=5 * KB, multipart_chunksize=1 * KB)
            file = tmpdir / "test-file.bin"
            data = b"1" * (6 * KB)  # create 6 kilobytes of ones
            file.write(data=data, mode="w")
            s3_client_allow.upload_file(
                Bucket=bucket_name,
                Key="allow_multipart",
                Filename=str(file.realpath()),
                Config=transfer_config,
            )
            stack.callback(s3_client_allow.delete_object, Bucket=bucket_name, Key="allow_multipart")

            # attempt to create bucket/object - DENY
            self.assert_access_denied(
                resources.create_s3_bucket,
                short_uid(),
                s3_client=s3_client_deny,
            )
            self.assert_access_denied(
                s3_client_deny.put_object, Bucket=bucket_name, Key="denied", Body="abc"
            )
            with pytest.raises(S3UploadFailedError):
                s3_client_deny.upload_file(
                    Bucket=bucket_name,
                    Key="denied_multipart",
                    Filename=str(file.realpath()),
                    Config=transfer_config,
                )
            # TODO uncomment once service specific exceptions are supported
            # e.match("An error occurred \(AccessDenied\) when calling the CreateMultipartUpload operation: Access Denied")

    @markers.aws.validated
    def test_enforce_policy_apigateway(self, client_for_new_user):
        # create ALLOW/DENY policies and users
        actions = ["apigateway:POST", "apigateway:DELETE"]
        apigateway_client_allow = client_for_new_user("apigateway", "Allow", actions)
        apigateway_client_deny = client_for_new_user("apigateway", "Deny", actions)

        # attempt to create REST API - ALLOW
        api_name = short_uid()
        api_id = apigateway_client_allow.create_rest_api(name=api_name)["id"]

        # attempt to create REST API - DENY
        # returns AccessDeniedException with 403
        self.assert_access_denied(apigateway_client_deny.create_rest_api, name=short_uid())

        # clean up
        apigateway_client_allow.delete_rest_api(restApiId=api_id)

    @markers.aws.validated
    def test_enforce_policy_events(self, client_for_new_user):
        # create ALLOW/DENY policies and users
        actions = ["events:CreateEventBus", "events:DeleteEventBus"]
        events_client_allow = client_for_new_user("events", "Allow", actions)
        events_client_deny = client_for_new_user("events", "Deny", actions)

        # attempt to create event bus - ALLOW
        bus_name = short_uid()
        events_client_allow.create_event_bus(Name=bus_name)

        # attempt to create event bus - DENY
        self.assert_access_denied(events_client_deny.create_event_bus, Name=short_uid())

        # clean up
        events_client_allow.delete_event_bus(Name=bus_name)

    @markers.aws.validated
    def test_enforce_policy_secretsmanager_create(
        self, client_for_new_user, account_id, aws_client, region_name
    ):
        # create ALLOW/DENY policies and users
        secret_name = f"secret-{short_uid()}"
        resource = f"arn:{get_partition(region_name)}:secretsmanager:{region_name}:{account_id}:secret:{secret_name}*"
        actions = ["secretsmanager:CreateSecret", "secretsmanager:DeleteSecret"]
        secrets_client_allow = client_for_new_user("secretsmanager", "Allow", actions, resource)
        secrets_client_deny = client_for_new_user("secretsmanager", "Deny", actions)

        # attempt to create secret - ALLOW
        secrets_client_allow.create_secret(Name=secret_name)

        # attempt to create secret - DENY
        self.assert_access_denied(secrets_client_deny.create_secret, Name=short_uid())

        # clean up
        secrets_client_allow.delete_secret(SecretId=secret_name)

    @markers.aws.validated
    def test_enforce_policy_secretsmanager_get_value(
        self, create_user, client_factory_for_user, cleanups, aws_client, snapshot
    ):
        snapshot.add_transformer(snapshot.transform.resource_name())
        snapshot.add_transformer(snapshot.transform.iam_api())
        create_response = aws_client.secretsmanager.create_secret(
            Name=f"test-secret-{short_uid()}", SecretString="test-secret-value"
        )
        cleanups.append(
            lambda: aws_client.secretsmanager.delete_secret(
                SecretId=create_response["ARN"], ForceDeleteWithoutRecovery=True
            )
        )
        snapshot.add_transformer(snapshot.transform.key_value("Name", "test-secret-name"))
        snapshot.match("create-secret", create_response)

        user_name = f"test-user-{short_uid()}"
        policy_name = f"policy-{short_uid()}"
        create_user_response = create_user(UserName=user_name)
        snapshot.match("create-user", create_user_response)

        secretsmanager_client_user = client_factory_for_user(user_name=user_name).secretsmanager
        with pytest.raises(ClientError) as e:
            secretsmanager_client_user.get_secret_value(SecretId=create_response["ARN"])
        snapshot.match("get-secret-value", e.value.response)

        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "s1",
                    "Effect": "Allow",
                    "Action": ["secretsmanager:GetSecretValue"],
                    "Resource": create_response["ARN"],
                }
            ],
        }
        aws_client.iam.put_user_policy(
            UserName=user_name, PolicyName=policy_name, PolicyDocument=json.dumps(policy)
        )

        def _get_secret():
            secretsmanager_client_user.get_secret_value(SecretId=create_response["ARN"])

        retry(_get_secret, sleep=4 if is_aws_cloud() else 1, retries=10)

    @markers.aws.validated
    def test_enforce_policy_elasticsearch_two_domains(
        self, client_for_new_user, account_id, aws_client, region_name
    ):
        # create ALLOW/DENY policies and users
        actions = ["es:DescribeElasticsearchDomains"]
        domain_name = f"test-domain-{short_uid()}"
        domain_name_2 = f"test-domain-{short_uid()}"
        resources = [
            f"arn:{get_partition(region_name)}:es:{region_name}:{account_id}:domain/{domain_name}",
            f"arn:{get_partition(region_name)}:es:{region_name}:{account_id}:domain/{domain_name_2}",
        ]
        print(resources)
        es_client_allow = client_for_new_user("es", "Allow", actions, resource=resources)
        es_client_allow_only_one = client_for_new_user(
            "es",
            "Allow",
            actions,
            resource=[
                f"arn:{get_partition(region_name)}:es:{region_name}:{account_id}:domain/{domain_name}"
            ],
        )
        es_client_deny = client_for_new_user("es", "Deny", actions)

        # attempt to describe ES domains - ALLOW
        es_client_allow.describe_elasticsearch_domains(DomainNames=[domain_name, domain_name_2])
        # attempt to describe ES domains - only one requested domain allowed
        self.assert_access_denied(
            es_client_allow_only_one.describe_elasticsearch_domains,
            DomainNames=[domain_name, domain_name_2],
        )

        # attempt to describe ES domains - DENY
        # returns AccessDeniedException with 403
        self.assert_access_denied(es_client_deny.describe_elasticsearch_domains, DomainNames=[])

    @markers.aws.validated
    def test_enforce_policy_elasticsearch(self, client_for_new_user, account_id, aws_client):
        # create ALLOW/DENY policies and users
        actions = ["es:DescribeElasticsearchDomains"]
        es_client_allow = client_for_new_user("es", "Allow", actions)
        es_client_deny = client_for_new_user("es", "Deny", actions)

        # attempt to describe ES domains - ALLOW
        es_client_allow.describe_elasticsearch_domains(DomainNames=[])

        # attempt to describe ES domains - DENY
        # returns AccessDeniedException with 403
        self.assert_access_denied(es_client_deny.describe_elasticsearch_domains, DomainNames=[])

    @markers.aws.validated
    def test_enforce_policy_acm(self, client_for_new_user):
        # create ALLOW/DENY policies and users
        actions = ["acm:*"]
        acm_client_allow = client_for_new_user("acm", "Allow", actions)
        acm_client_deny = client_for_new_user("acm", "Deny", actions)

        # attempt to list certificates - ALLOW
        acm_client_allow.list_certificates()

        # attempt to list certificates - DENY
        self.assert_access_denied(acm_client_deny.list_certificates)

    @markers.aws.validated
    def test_enforce_policy_cloudwatch(self, client_for_new_user):
        # create ALLOW/DENY policies and users
        actions = ["cloudwatch:*"]
        cloudwatch_client_allow = client_for_new_user("cloudwatch", "Allow", actions)
        cloudwatch_client_deny = client_for_new_user("cloudwatch", "Deny", actions)

        # attempt to put metric data - ALLOW
        data = [
            {
                "MetricName": "some-metric",
                "Dimensions": [{"Name": "foo", "Value": "bar"}],
                "Timestamp": datetime.now() - timedelta(days=1),
                "Unit": "Seconds",
                "Values": [50],
            }
        ]
        cloudwatch_client_allow.put_metric_data(Namespace="ns1", MetricData=data)

        # attempt to put metric data - DENY
        self.assert_access_denied(
            cloudwatch_client_deny.put_metric_data, Namespace="ns1", MetricData=data
        )

    @markers.aws.validated
    def test_enforce_policy_logs(self, client_for_new_user):
        # create ALLOW/DENY policies and users
        actions = ["logs:*"]
        logs_client_allow = client_for_new_user("logs", "Allow", actions)
        logs_client_deny = client_for_new_user("logs", "Deny", actions)

        # attempt to list log groups - ALLOW
        group_name = f"log-{short_uid()}"
        logs_client_allow.create_log_group(logGroupName=group_name)

        # attempt to list log groups - DENY
        self.assert_access_denied(logs_client_deny.create_log_group, logGroupName=group_name)

        # clean up
        logs_client_allow.delete_log_group(logGroupName=group_name)

    @markers.aws.validated
    def test_enforce_policy_kms(self, client_for_new_user):
        # create ALLOW/DENY policies and users
        actions = ["kms:*"]
        kms_client_allow = client_for_new_user("kms", "Allow", actions)
        kms_client_deny = client_for_new_user("kms", "Deny", actions)

        # attempt to create key - ALLOW
        key_data = kms_client_allow.create_key()["KeyMetadata"]
        assert "KeyId" in key_data

        # attempt to create key - DENY
        self.assert_access_denied(kms_client_deny.create_key)

    @markers.aws.needs_fixing
    def test_enforce_policy_redshift(self, client_for_new_user):
        # create ALLOW/DENY policies and users
        actions = ["redshift:*", "redshift-data:ListDatabases"]

        # attempt to describe clusters - ALLOW
        redshift_client_allow = client_for_new_user("redshift", "Allow", actions)
        redshift_client_allow.describe_clusters()

        # attempt to describe clusters - DENY
        redshift_client_deny = client_for_new_user("redshift", "Deny", actions)
        self.assert_access_denied(redshift_client_deny.describe_clusters)

        # attempt to list databases - ALLOW (should raise 404)
        redshift_data_client_allow = client_for_new_user("redshift-data", "Allow", actions)
        with pytest.raises(Exception) as ctx:
            redshift_data_client_allow.list_databases(
                ClusterIdentifier="non-existing", Database="test"
            )
        assert ctx.match("ValidationException")

        # attempt to list databases - DENY
        redshift_data_client_deny = client_for_new_user("redshift-data", "Deny", actions)
        self.assert_access_denied(
            redshift_data_client_deny.list_databases, ClusterIdentifier="c1", Database="test"
        )

    @markers.aws.validated
    def test_enforce_policy_stepfunctions(
        self, client_for_new_user, create_role_with_policy, region_name
    ):
        # create ALLOW/DENY policies and users
        actions = ["states:CreateStateMachine", "states:DeleteStateMachine", "iam:PassRole"]
        client_allow = client_for_new_user("stepfunctions", "Allow", actions)

        sm_name = short_uid()
        definition = {
            "StartAt": "s1",
            "States": {
                "s1": {
                    "Type": "Task",
                    "Resource": "arn:aws:lambda:us-east-1:0000:function:f1",
                    "End": True,
                }
            },
        }
        role_name, role_arn = create_role_with_policy(
            effect="Allow",
            actions=["iam:PassRole"],
            assume_policy_doc=json.dumps(
                {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Action": "sts:AssumeRole",
                            "Principal": {"Service": f"states.{region_name}.amazonaws.com"},
                        }
                    ],
                }
            ),
        )

        sm_arn = client_allow.create_state_machine(
            name=sm_name, definition=json.dumps(definition), roleArn=role_arn
        )["stateMachineArn"]

        # attempt to create bucket/object - DENY
        client_deny = client_for_new_user("stepfunctions", "Deny", actions)
        self.assert_access_denied(
            client_deny.create_state_machine,
            name=short_uid(),
            definition=json.dumps(definition),
            roleArn=role_arn,
        )

        # clean up
        client_allow.delete_state_machine(stateMachineArn=sm_arn)

    #
    # Assume role tests
    #
    @markers.aws.validated
    def test_assume_role_cw_logs(self, client_with_assumed_role):
        # create ALLOW/DENY policies and clients
        actions = ["logs:*"]
        logs_client_allow = client_with_assumed_role("logs", "Allow", actions)
        logs_client_deny = client_with_assumed_role("logs", "Deny", actions)

        # attempt to list log groups - ALLOW
        group_name = f"log-{short_uid()}"
        logs_client_allow.create_log_group(logGroupName=group_name)

        # attempt to list log groups - DENY
        self.assert_access_denied(logs_client_deny.create_log_group, logGroupName=group_name)

        # clean up
        logs_client_allow.delete_log_group(logGroupName=group_name)

    @markers.aws.validated
    def test_assume_role_sqs_with_put_role_policy(
        self, client_with_assumed_role, account_id, aws_client
    ):
        # create ALLOW/DENY policies and roles
        queue_name = f"test-queue-{short_uid()}"
        actions = ["sqs:CreateQueue", "sqs:DeleteQueue", "sqs:ReceiveMessage"]
        # note: passing in attach=False here, to create the IAM policy via put_role_policy(..) below
        sqs_allow = client_with_assumed_role(
            "sqs",
            "Allow",
            actions,
            resource=sqs_queue_arn(
                queue_name,
                account_id=account_id,
                region_name=aws_client.sqs.meta.region_name,
            ),
            attach=False,
        )

        # attempt to create queue - ALLOW
        queue_url = sqs_allow.create_queue(QueueName=queue_name)["QueueUrl"]
        result = sqs_allow.receive_message(QueueUrl=queue_url)
        assert result.get("ResponseMetadata")

        sqs_deny = client_with_assumed_role("sqs", "Deny", actions, attach=False)
        # attempt to create queue - DENY
        self.assert_access_denied(sqs_deny.create_queue, QueueName=short_uid())

        def assert_denied_received_message():
            self.assert_access_denied(sqs_deny.receive_message, QueueUrl=queue_url)

        retry(assert_denied_received_message)

        # clean up
        sqs_allow.delete_queue(QueueUrl=queue_url)

    @markers.aws.validated
    def test_user_with_permissions_boundary(
        self, create_user, create_policy, aws_client, region_name
    ):
        username = f"test-user-{short_uid()}"
        boundary_policy_name = f"perm-boundary-{short_uid()}"
        policy_name = f"policy-{short_uid()}"
        queue_name = f"queue-{short_uid()}"
        policy = {
            "Version": "2012-10-17",
            "Statement": {"Effect": "Allow", "Action": "sqs:*", "Resource": "*"},
        }
        permissions_boundary = {
            "Version": "2012-10-17",
            "Statement": {"Effect": "Allow", "Action": "sqs:CreateQueue", "Resource": "*"},
        }
        boundary_arn = create_policy(
            PolicyName=boundary_policy_name, PolicyDocument=json.dumps(permissions_boundary)
        )["Policy"]["Arn"]
        create_user(UserName=username, PermissionsBoundary=boundary_arn)
        aws_client.iam.put_user_policy(
            UserName=username, PolicyName=policy_name, PolicyDocument=json.dumps(policy)
        )
        keys = aws_client.iam.create_access_key(UserName=username)["AccessKey"]
        wait_for_user(keys, region_name)
        sqs_user_client = create_client_with_keys(
            "sqs", keys=keys, region_name=aws_client.sqs.meta.region_name
        )
        queue_url = None
        try:
            queue_url = sqs_user_client.create_queue(QueueName=queue_name)["QueueUrl"]
            with pytest.raises(ClientError):
                sqs_user_client.get_queue_attributes(QueueUrl=queue_url, AttributeNames=["All"])
            # TODO uncomment once service specific exceptions are supported
            # e.match(r"An error occurred \(AccessDenied\) when calling the GetQueueAttributes operation: Access to the resource .* is denied.")
        finally:
            aws_client.sqs.delete_queue(QueueUrl=queue_url)

    @markers.aws.validated
    def test_role_with_permissions_boundary(
        self, create_role, wait_and_assume_role, create_policy, account_id, aws_client
    ):
        role_name = f"test-role-{short_uid()}"
        boundary_policy_name = f"perm-boundary-{short_uid()}"
        policy_name = f"policy-{short_uid()}"
        queue_name = f"queue-{short_uid()}"
        policy = {
            "Version": "2012-10-17",
            "Statement": {"Effect": "Allow", "Action": "sqs:*", "Resource": "*"},
        }
        permissions_boundary = {
            "Version": "2012-10-17",
            "Statement": {"Effect": "Allow", "Action": "sqs:CreateQueue", "Resource": "*"},
        }
        assume_policy_doc = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "sts:AssumeRole",
                    "Principal": {"AWS": account_id},
                    "Effect": "Allow",
                }
            ],
        }
        boundary_arn = create_policy(
            PolicyName=boundary_policy_name, PolicyDocument=json.dumps(permissions_boundary)
        )["Policy"]["Arn"]
        result = create_role(
            RoleName=role_name,
            PermissionsBoundary=boundary_arn,
            AssumeRolePolicyDocument=json.dumps(assume_policy_doc),
        )
        role_arn = result["Role"]["Arn"]
        aws_client.iam.put_role_policy(
            RoleName=role_name, PolicyName=policy_name, PolicyDocument=json.dumps(policy)
        )
        keys = wait_and_assume_role(role_arn=role_arn)
        sqs_user_client = create_client_with_keys(
            "sqs", keys=keys, region_name=aws_client.sqs.meta.region_name
        )
        queue_url = None
        try:

            def create_queue():
                return sqs_user_client.create_queue(QueueName=queue_name)["QueueUrl"]

            queue_url = retry(create_queue)
            with pytest.raises(ClientError):
                sqs_user_client.get_queue_attributes(QueueUrl=queue_url, AttributeNames=["All"])
            # TODO uncomment once service specific exceptions are supported
            # e.match(r"An error occurred \(AccessDenied\) when calling the GetQueueAttributes operation: Access to the resource .* is denied.")
        finally:
            aws_client.sqs.delete_queue(QueueUrl=queue_url)

    @markers.aws.validated
    def test_user_with_path(self, create_user, create_policy, aws_client, region_name, cleanups):
        username = f"test-user-{short_uid()}"
        path = "/user/prefix/"
        policy_name = f"policy-{short_uid()}"
        queue_name = f"queue-{short_uid()}"
        policy = {
            "Version": "2012-10-17",
            "Statement": {"Effect": "Allow", "Action": "sqs:CreateQueue", "Resource": "*"},
        }
        create_user(UserName=username, Path=path)
        aws_client.iam.put_user_policy(
            UserName=username, PolicyName=policy_name, PolicyDocument=json.dumps(policy)
        )
        keys = aws_client.iam.create_access_key(UserName=username)["AccessKey"]
        wait_for_user(keys, region_name)
        sqs_user_client = create_client_with_keys(
            "sqs", keys=keys, region_name=aws_client.sqs.meta.region_name
        )

        def create_queue():
            return sqs_user_client.create_queue(QueueName=queue_name)["QueueUrl"]

        queue_url = retry(create_queue)
        cleanups.append(lambda: aws_client.sqs.delete_queue(QueueUrl=queue_url))
        with pytest.raises(ClientError):
            sqs_user_client.get_queue_attributes(QueueUrl=queue_url, AttributeNames=["All"])

    @markers.aws.validated
    def test_enforce_policy_elasticsearch_two_domains_two_policies(
        self, create_user, account_id, aws_client, region_name
    ):
        """Tests if two domains allowed in two statements in different policies will still be correctly allowed"""
        user_name = f"test-user-{short_uid()}"
        domain_name_1 = f"test-domain-{short_uid()}"
        domain_name_2 = f"test-domain-{short_uid()}"
        policy_name_1 = f"test-policy-{short_uid()}"
        policy_name_2 = f"test-policy-{short_uid()}"
        policy_1 = {
            "Version": "2012-10-17",
            "Statement": {
                "Effect": "Allow",
                "Action": "es:DescribeElasticsearchDomains",
                "Resource": f"arn:{get_partition(aws_client.es.meta.region_name)}:es:{aws_client.es.meta.region_name}:{account_id}:domain/{domain_name_1}",
            },
        }
        policy_2 = {
            "Version": "2012-10-17",
            "Statement": {
                "Effect": "Allow",
                "Action": "es:DescribeElasticsearchDomains",
                "Resource": f"arn:{get_partition(aws_client.es.meta.region_name)}:es:{aws_client.es.meta.region_name}:{account_id}:domain/{domain_name_2}",
            },
        }
        create_user(UserName=user_name)
        aws_client.iam.put_user_policy(
            UserName=user_name, PolicyName=policy_name_1, PolicyDocument=json.dumps(policy_1)
        )
        aws_client.iam.put_user_policy(
            UserName=user_name, PolicyName=policy_name_2, PolicyDocument=json.dumps(policy_2)
        )
        keys = aws_client.iam.create_access_key(UserName=user_name)["AccessKey"]
        wait_for_user(keys, region_name)
        es_user_client = create_client_with_keys(
            "es", keys=keys, region_name=aws_client.es.meta.region_name
        )
        es_user_client.describe_elasticsearch_domains(DomainNames=[domain_name_1, domain_name_2])

    @markers.aws.needs_fixing
    def test_batch_create_compute_environment(
        self, create_user, create_role, account_id, aws_client, region_name
    ):
        is_localstack = os.environ.get("TEST_TARGET") != "AWS_CLOUD"
        user_name = f"test-user-{short_uid()}"
        role_name = f"role-user-{short_uid()}"
        assume_policy_doc = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "sts:AssumeRole",
                    "Principal": {"AWS": account_id},
                    "Effect": "Allow",
                }
            ],
        }
        compute_environment = f"test-env-{short_uid()}"
        create_user(UserName=user_name)
        create_role(RoleName=role_name, AssumeRolePolicyDocument=json.dumps(assume_policy_doc))
        policy_name_1 = f"test-policy-{short_uid()}"
        policy_1 = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": "batch:CreateComputeEnvironment",
                    "Resource": f"arn:{get_partition(region_name)}:batch:{region_name}:{account_id}:compute-environment/{compute_environment}",
                },
                {
                    "Effect": "Allow",
                    "Action": "iam:PassRole",
                    "Resource": f"arn:{get_partition(region_name)}:iam::{account_id}:role/{role_name}",
                },
                {
                    "Effect": "Allow",
                    "Action": "iam:CreateServiceLinkedRole",
                    "Resource": f"arn:{get_partition(region_name)}:iam::*:role/aws-service-role/*",
                },
            ],
        }
        instance_profile_arn = aws_client.iam.create_instance_profile(
            InstanceProfileName=role_name
        )["InstanceProfile"]["Arn"]
        aws_client.iam.add_role_to_instance_profile(
            InstanceProfileName=role_name, RoleName=role_name
        )
        aws_client.iam.put_user_policy(
            UserName=user_name, PolicyName=policy_name_1, PolicyDocument=json.dumps(policy_1)
        )
        keys = aws_client.iam.create_access_key(UserName=user_name)["AccessKey"]
        wait_for_user(keys, region_name)
        allowed_batch_client = create_client_with_keys(
            "batch", keys=keys, region_name=aws_client.batch.meta.region_name
        )
        with ExitStack() as stack:
            subnet_id = aws_client.ec2.describe_subnets()["Subnets"][0]["SubnetId"]
            security_group_id = aws_client.ec2.describe_security_groups()["SecurityGroups"][0][
                "GroupId"
            ]
            allowed_batch_client.create_compute_environment(
                computeEnvironmentName=compute_environment,
                type="MANAGED",
                serviceRole=f"arn:{get_partition(region_name)}:iam::{account_id}:role/{role_name}"
                if is_localstack
                else None,
                computeResources={
                    "instanceRole": instance_profile_arn,
                    "minvCpus": 1,
                    "maxvCpus": 1,
                    "instanceTypes": ["c5"],
                    "type": "EC2",
                    "subnets": [subnet_id],
                    "securityGroupIds": [security_group_id],
                },
            )
            stack.callback(
                lambda: retry(
                    aws_client.batch.delete_compute_environment,
                    computeEnvironment=compute_environment,
                )
            )
            stack.callback(
                lambda: retry(
                    aws_client.batch.update_compute_environment,
                    computeEnvironment=compute_environment,
                    state="DISABLED",
                )
            )

    @markers.aws.validated
    def test_enforce_policy_sqs_not_resource_all(
        self, create_user, account_id, aws_client, region_name
    ):
        """Test if not resource correctly respects an asterisk to not match anything"""
        user_name_1 = f"test-user-{short_uid()}"
        user_name_2 = f"test-user-{short_uid()}"
        queue_name_1 = f"test-queue-{short_uid()}"
        queue_name_2 = f"test-queue-{short_uid()}"
        policy_name_1 = f"test-policy-{short_uid()}"
        policy_name_2 = f"test-policy-{short_uid()}"
        policy_1 = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Deny",
                    "Action": "sqs:CreateQueue",
                    "NotResource": "*",
                },
                {
                    "Effect": "Allow",
                    "Action": "sqs:CreateQueue",
                    "Resource": "*",
                },
            ],
        }
        policy_2 = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": "sqs:CreateQueue",
                    "NotResource": "*",
                }
            ],
        }
        create_user(UserName=user_name_1)
        create_user(UserName=user_name_2)
        aws_client.iam.put_user_policy(
            UserName=user_name_1, PolicyName=policy_name_1, PolicyDocument=json.dumps(policy_1)
        )
        aws_client.iam.put_user_policy(
            UserName=user_name_2, PolicyName=policy_name_2, PolicyDocument=json.dumps(policy_2)
        )
        keys = aws_client.iam.create_access_key(UserName=user_name_1)["AccessKey"]
        wait_for_user(keys, region_name)
        sqs_user_client = create_client_with_keys(
            "sqs", keys=keys, region_name=aws_client.sqs.meta.region_name
        )
        with ExitStack() as stack:
            queue_url = sqs_user_client.create_queue(QueueName=queue_name_1)["QueueUrl"]
            stack.callback(aws_client.sqs.delete_queue, QueueUrl=queue_url)
        keys = aws_client.iam.create_access_key(UserName=user_name_2)["AccessKey"]
        wait_for_user(keys, region_name)
        sqs_user_client_2 = create_client_with_keys(
            "sqs", keys=keys, region_name=aws_client.sqs.meta.region_name
        )
        # make sure that the request won't pass even after some retries
        self.assert_access_denied(retry, sqs_user_client_2.create_queue, QueueName=queue_name_2)

    @markers.aws.validated
    def test_enforce_s3_admin_policy(
        self, create_user, create_client_for_user, snapshot, aws_client, region_name
    ):
        """Test if not resource correctly respects an asterisk to not match anything"""
        user_name = f"test-user-{short_uid()}"
        create_user(UserName=user_name)
        s3_user_client = create_client_for_user(user_name=user_name, service="s3")
        with pytest.raises(ClientError) as e:
            s3_user_client.list_buckets()
        snapshot.match("not-allowed-list-buckets", e.value.response)
        aws_client.iam.attach_user_policy(
            UserName=user_name,
            PolicyArn=f"arn:{get_partition(region_name)}:iam::aws:policy/AdministratorAccess",
        )

        # creating a new client _should_ not be necessary, but speeds up the process immensely against AWS
        s3_user_client = create_client_for_user(user_name=user_name, service="s3")

        def _list_buckets():
            s3_user_client.list_buckets()

        retry(_list_buckets, sleep=2, retries=15)

    @markers.aws.validated
    def test_logs_policy(
        self,
        create_user,
        client_factory_for_user,
        snapshot,
        aws_client,
        account_id,
    ):
        snapshot.add_transformer(snapshot.transform.iam_api())
        user_name = f"user-{short_uid()}"
        policy_name = f"policy-{short_uid()}"
        log_group_name = f"test-group-{short_uid()}"
        log_stream_name = f"test-stream-{short_uid()}"
        snapshot.add_transformer(snapshot.transform.regex(log_group_name, "<log-group-name>"))
        snapshot.add_transformer(snapshot.transform.regex(log_stream_name, "<log-stream-name>"))
        create_user_response = create_user(UserName=user_name)
        snapshot.match("create-user-response", create_user_response)

        logs_client_user = client_factory_for_user(user_name=user_name).logs

        with pytest.raises(ClientError) as e:
            logs_client_user.create_log_group(logGroupName=log_group_name)
        snapshot.match("create-log-group-failed", e.value.response)

        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "s1",
                    "Effect": "Allow",
                    "Action": ["logs:CreateLogGroup"],
                    "Resource": [
                        f"arn:{get_partition(logs_client_user.meta.region_name)}:logs:{logs_client_user.meta.region_name}:{account_id}:log-group:{log_group_name}:log-stream:"
                    ],
                }
            ],
        }
        aws_client.iam.put_user_policy(
            UserName=user_name, PolicyName=policy_name, PolicyDocument=json.dumps(policy)
        )

        def test():
            logs_client_user.create_log_group(logGroupName=log_group_name)

        retry(test, sleep=(10 if is_aws_cloud() else 1), retries=15)

        with pytest.raises(ClientError) as e:
            logs_client_user.create_log_stream(
                logGroupName=log_group_name, logStreamName=log_stream_name
            )
        snapshot.match("create-log-stream-failed", e.value.response)

    @markers.aws.validated
    def test_sns_create_topic_policy(
        self, create_user, client_factory_for_user, snapshot, aws_client, account_id, cleanups
    ):
        snapshot.add_transformer(snapshot.transform.iam_api())
        user_name = f"user-{short_uid()}"
        policy_name = f"policy-{short_uid()}"
        topic_name = f"test-topic-{short_uid()}"
        snapshot.add_transformer(snapshot.transform.regex(topic_name, "<topic-name>"))

        create_user_response = create_user(UserName=user_name)
        snapshot.match("create-user-response", create_user_response)

        sns_client_user = client_factory_for_user(user_name=user_name).sns
        topic_arn = f"arn:{get_partition(sns_client_user.meta.region_name)}:sns:{sns_client_user.meta.region_name}:{account_id}:{topic_name}"
        cleanups.append(lambda: aws_client.sns.delete_topic(TopicArn=topic_arn))

        with pytest.raises(ClientError) as e:
            sns_client_user.create_topic(Name=topic_name)
        snapshot.match("create-sns-topic-failed", e.value.response)

        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "s1",
                    "Effect": "Allow",
                    "Action": ["sns:CreateTopic"],
                    "Resource": [topic_arn],
                }
            ],
        }
        aws_client.iam.put_user_policy(
            UserName=user_name, PolicyName=policy_name, PolicyDocument=json.dumps(policy)
        )

        def test():
            sns_client_user.create_topic(Name=topic_name)

        retry(test, sleep=(10 if is_aws_cloud() else 1), retries=15)

    @markers.aws.validated
    def test_s3_delete_intelligent_bucket_tiering_config(
        self,
        s3_bucket,
        create_user,
        client_factory_for_user,
        snapshot,
        aws_client,
        region_name,
        cleanups,
    ):
        snapshot.add_transformer(snapshot.transform.iam_api())
        user_name = f"user-{short_uid()}"
        policy_name = f"policy-{short_uid()}"

        create_user_response = create_user(UserName=user_name)
        snapshot.match("create-user-response", create_user_response)

        s3_client_user = client_factory_for_user(user_name=user_name).s3
        aws_client.s3.put_bucket_intelligent_tiering_configuration(
            Bucket=s3_bucket,
            Id="Example",
            IntelligentTieringConfiguration={
                "Id": "Example",
                "Status": "Enabled",
                "Tierings": [{"AccessTier": "ARCHIVE_ACCESS", "Days": 90}],
            },
        )

        with pytest.raises(ClientError) as e:
            s3_client_user.delete_bucket_intelligent_tiering_configuration(
                Bucket=s3_bucket, Id="Example"
            )
        snapshot.match("delete-bucket-tiering-config-failed", e.value.response)

        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "s1",
                    "Effect": "Allow",
                    "Action": ["s3:PutIntelligentTieringConfiguration"],
                    "Resource": [arns.s3_bucket_arn(s3_bucket, region=region_name)],
                }
            ],
        }
        aws_client.iam.put_user_policy(
            UserName=user_name, PolicyName=policy_name, PolicyDocument=json.dumps(policy)
        )

        def test():
            s3_client_user.delete_bucket_intelligent_tiering_configuration(
                Bucket=s3_bucket, Id="Example"
            )

        retry(test, sleep=(10 if is_aws_cloud() else 1), retries=15)

    @markers.aws.validated
    @pytest.mark.parametrize(
        "prefix", ["/", ""], ids=["with-leading-slash", "without-leading-slash"]
    )
    def test_ssm_get_attribute(
        self, prefix, create_user, client_factory_for_user, snapshot, aws_client, cleanups
    ):
        snapshot.add_transformer(snapshot.transform.iam_api())
        user_name = f"user-{short_uid()}"
        policy_name = f"policy-{short_uid()}"
        parameter_name = f"{prefix}something-attr-{short_uid()}"
        snapshot.add_transformer(snapshot.transform.regex(parameter_name, "<attribute-name>"))

        aws_client.ssm.put_parameter(Name=parameter_name, Value="test", Type="String")
        cleanups.append(lambda: aws_client.ssm.delete_parameter(Name=parameter_name))
        parameter_arn = aws_client.ssm.get_parameter(Name=parameter_name)["Parameter"]["ARN"]

        create_user_response = create_user(UserName=user_name)
        snapshot.match("create-user-response", create_user_response)

        ssm_client_user = client_factory_for_user(user_name=user_name).ssm

        with pytest.raises(ClientError) as e:
            ssm_client_user.get_parameter(Name=parameter_name)
        snapshot.match("get-parameter-failed", e.value.response)

        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "s1",
                    "Effect": "Allow",
                    "Action": ["ssm:GetParameter"],
                    "Resource": [parameter_arn],
                }
            ],
        }
        aws_client.iam.put_user_policy(
            UserName=user_name, PolicyName=policy_name, PolicyDocument=json.dumps(policy)
        )

        def _get_param():
            return ssm_client_user.get_parameter(Name=parameter_name)

        get_parameter_response = retry(_get_param, sleep=(10 if is_aws_cloud() else 1), retries=15)
        snapshot.match("get-parameter-response", get_parameter_response)

    @markers.aws.validated
    def test_dynamodb_batch_write_item(
        self,
        create_user,
        client_factory_for_user,
        snapshot,
        aws_client,
        account_id,
        dynamodb_create_table_with_parameters,
        dynamodb_wait_for_table_active,
    ):
        snapshot.add_transformer(snapshot.transform.iam_api())
        user_name = f"user-{short_uid()}"
        policy_name = f"policy-{short_uid()}"
        table_name = f"test-table-{short_uid()}"
        snapshot.add_transformer(snapshot.transform.regex(table_name, "<table-name>"))

        create_user_response = create_user(UserName=user_name)
        snapshot.match("create-user-response", create_user_response)

        dynamodb_create_table_with_parameters(
            TableName=table_name,
            KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
            ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
        )

        dynamodb_wait_for_table_active(table_name)

        dynamodb_client_user = client_factory_for_user(user_name=user_name).dynamodb

        with pytest.raises(ClientError) as e:
            dynamodb_client_user.batch_write_item(
                RequestItems={table_name: [{"PutRequest": {"Item": {"id": {"S": "PutTest"}}}}]}
            )
        snapshot.match("batch-write-item-failed", e.value.response)

        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "s1",
                    "Effect": "Allow",
                    "Action": ["dynamodb:BatchWriteItem"],
                    "Resource": [
                        f"arn:{get_partition(dynamodb_client_user.meta.region_name)}:dynamodb:{dynamodb_client_user.meta.region_name}:{account_id}:table/{table_name}"
                    ],
                }
            ],
        }
        aws_client.iam.put_user_policy(
            UserName=user_name, PolicyName=policy_name, PolicyDocument=json.dumps(policy)
        )

        def test():
            dynamodb_client_user.batch_write_item(
                RequestItems={table_name: [{"PutRequest": {"Item": {"id": {"S": "PutTest"}}}}]}
            )

        retry(test, sleep=(30 if is_aws_cloud() else 1), retries=15)

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(
        # TODO introduce exact stack id matching with store lookup, removing $..Error.Message
        paths=["$..Stacks..LastUpdatedTime", "$..Stacks..StackStatusReason", "$..Error.Message"]
    )
    def test_cloudformation_stack_operations(
        self,
        create_user,
        client_factory_for_user,
        snapshot,
        aws_client,
        account_id,
        region_name,
        cleanups,
    ):
        snapshot.add_transformer(snapshot.transform.iam_api())
        snapshot.add_transformer(snapshot.transform.cloudformation_api())
        user_name = f"user-{short_uid()}"
        policy_name = f"policy-{short_uid()}"
        stack_name = f"repeated-stack-{short_uid()}"

        # create cfn stack to do operations over
        cleanups.append(lambda: aws_client.cloudformation.delete_stack(StackName=stack_name))
        template = """
        Resources:
            SimpleParam:
                Type: AWS::SSM::Parameter
                Properties:
                    Value: test
                    Type: String
        """
        stack = aws_client.cloudformation.create_stack(StackName=stack_name, TemplateBody=template)
        stack_id = stack["StackId"]
        describe_stack_response = aws_client.cloudformation.describe_stacks(StackName=stack_name)
        snapshot.match("describe-stack-response", describe_stack_response)

        create_user_response = create_user(UserName=user_name)
        snapshot.match("create-user-response", create_user_response)

        cfn_client_user = client_factory_for_user(user_name=user_name).cloudformation

        # by stack id
        with pytest.raises(ClientError) as e:
            cfn_client_user.update_termination_protection(
                EnableTerminationProtection=False, StackName=stack_id
            )
        snapshot.match("update-termination-protection-failed-id", e.value.response)
        with pytest.raises(ClientError) as e:
            cfn_client_user.describe_stack_events(StackName=stack_id)
        snapshot.match("describe-stack-events-failed-id", e.value.response)
        # by stack name
        with pytest.raises(ClientError) as e:
            cfn_client_user.update_termination_protection(
                EnableTerminationProtection=False, StackName=stack_name
            )
        snapshot.match("update-termination-protection-failed-name", e.value.response)
        with pytest.raises(ClientError) as e:
            cfn_client_user.describe_stack_events(StackName=stack_name)
        snapshot.match("describe-stack-events-failed-name", e.value.response)

        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "s1",
                    "Effect": "Allow",
                    "Action": [
                        "cloudformation:UpdateTerminationProtection",
                        "cloudformation:DescribeStackEvents",
                    ],
                    "Resource": [
                        f"arn:{get_partition(region_name)}:cloudformation:{region_name}:{account_id}:stack/{stack_name}/*"
                    ],
                }
            ],
        }
        aws_client.iam.put_user_policy(
            UserName=user_name, PolicyName=policy_name, PolicyDocument=json.dumps(policy)
        )

        def test():
            # by id
            cfn_client_user.update_termination_protection(
                EnableTerminationProtection=False, StackName=stack_id
            )
            cfn_client_user.describe_stack_events(StackName=stack_id)
            # by name
            cfn_client_user.update_termination_protection(
                EnableTerminationProtection=False, StackName=stack_name
            )
            cfn_client_user.describe_stack_events(StackName=stack_name)

        retry(test, sleep=(30 if is_aws_cloud() else 1), retries=15)

    @markers.aws.validated
    def test_role_assumes_itself(
        self,
        create_role,
        client_factory_for_role,
        snapshot,
        aws_client,
        account_id,
    ):
        snapshot.add_transformer(snapshot.transform.iam_api())
        role_name = f"test-role-{short_uid()}"
        policy_name = f"policy-{short_uid()}"

        assume_policy_doc = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "sts:AssumeRole",
                    "Principal": {"AWS": account_id},
                    "Effect": "Allow",
                }
            ],
        }
        create_role_response = create_role(
            RoleName=role_name, AssumeRolePolicyDocument=json.dumps(assume_policy_doc)
        )
        snapshot.match("create-role-response", create_role_response)
        role_arn = create_role_response["Role"]["Arn"]
        role_clients = client_factory_for_role(role_name=role_name, session_name="TestSession")

        # check if role can assume itself without additional permissions
        with pytest.raises(ClientError) as e:
            role_clients.sts.assume_role(RoleArn=role_arn, RoleSessionName="TestSessionDenied")

        snapshot.match("assume-role-denied", e.value.response)

        # add policy to allow self-assumption
        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "s1",
                    "Effect": "Allow",
                    "Action": ["sts:AssumeRole"],
                    "Resource": [role_arn],
                }
            ],
        }
        aws_client.iam.put_role_policy(
            RoleName=role_name, PolicyName=policy_name, PolicyDocument=json.dumps(policy)
        )

        def _try_assume():
            role_clients.sts.assume_role(RoleArn=role_arn, RoleSessionName="TestSessionDenied")

        retry(_try_assume, retries=30, sleep=30 if is_aws_cloud() else 1)

    # ---------------
    # HELPER METHODS
    # ---------------
    @pytest.fixture
    def client_with_assumed_role(self, create_and_assume_role, region_name):
        def _create_client_with_role(service: str, effect, actions, resource=None, attach=True):
            _, _, keys = create_and_assume_role(
                effect=effect, actions=actions, resource=resource, attach=attach
            )
            return create_client_with_keys(service=service, keys=keys, region_name=region_name)

        return _create_client_with_role

    @pytest.fixture
    def client_for_new_user(self, create_user_with_policy, region_name):
        def _client_for_new_user(service: str, effect, actions, resource=None):
            _, keys = create_user_with_policy(effect=effect, actions=actions, resource=resource)
            wait_for_user(keys, region_name)

            return create_client_with_keys(service=service, keys=keys, region_name=region_name)

        return _client_for_new_user

    def assert_access_denied(self, func, *args, **kwargs):
        with pytest.raises(Exception) as ctx:
            func(*args, **kwargs)
        self.assert_access_denied_response(ctx.value.response)

    def assert_access_denied_response(self, response):
        # TODO figure out when AccessDeniedException is returned, and when AccessDenied
        # and use correct assertions for requests yielding them
        error_code = response.get("Error", {}).get("Code")
        status_code = response.get("ResponseMetadata", {}).get("HTTPStatusCode")
        match error_code:
            case "AccessDeniedException":
                # TODO find out when 400 or 403 is returned
                assert status_code in [400, 403]
            case "AccessDenied":
                assert status_code == 403
            case _:
                assert False, "Unexpected exception"

    @pytest.fixture
    def create_and_assume_role(self, account_id, create_role_with_policy, wait_and_assume_role):
        def _create_and_assume_role(effect, actions, resource=None, attach=True):
            assume_policy_doc = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Action": "sts:AssumeRole",
                        "Principal": {"AWS": account_id},
                        "Effect": "Allow",
                    }
                ],
            }
            assume_policy_doc = json.dumps(assume_policy_doc)
            role_name, role_arn = create_role_with_policy(
                effect=effect,
                actions=actions,
                assume_policy_doc=assume_policy_doc,
                resource=resource,
                attach=attach,
            )

            keys = wait_and_assume_role(role_arn=role_arn)
            return role_name, role_arn, keys

        return _create_and_assume_role


class TestIAMEnforcementResourceBasedPolicies:
    @pytest.fixture
    def create_client_for_role(self, wait_and_assume_role, aws_client, region_name):
        def _create_client_for_role(role_name: str, service: str, session_name: str):
            role_arn = aws_client.iam.get_role(RoleName=role_name)["Role"]["Arn"]
            keys = wait_and_assume_role(role_arn=role_arn, session_name=session_name)
            return create_client_with_keys(service=service, keys=keys, region_name=region_name)

        return _create_client_for_role

    @pytest.fixture(autouse=True)
    def configure_snapshots(self, snapshot):
        snapshot.add_transformer(snapshot.transform.lambda_api())
        snapshot.add_transformer(snapshot.transform.iam_api())
        snapshot.add_transformer(snapshot.transform.sqs_api())
        snapshot.add_transformer(snapshot.transform.sns_api())

    @markers.aws.validated
    def test_lambda_invoke(
        self,
        create_lambda_function,
        create_user,
        create_client_for_user,
        snapshot,
        aws_client,
        account_id,
    ):
        snapshot.add_transformer(snapshot.transform.key_value("CodeSha256"))
        function_name = f"test-function-{short_uid()}"
        user_name = f"test-user-{short_uid()}"
        create_function_result = create_lambda_function(
            func_name=function_name,
            handler_file=TEST_SIMPLE_LAMBDA,
            runtime=Runtime.python3_12,
        )
        snapshot.match("create-function-result", create_function_result)
        lambda_result_default_client = aws_client.lambda_.invoke(FunctionName=function_name)
        snapshot.match("invoke-default-client", lambda_result_default_client)

        create_user_response = create_user(UserName=user_name)
        snapshot.match("create-user-response", create_user_response)

        lambda_user_client = create_client_for_user(user_name=user_name, service="lambda")
        # random user may not invoke client
        with pytest.raises(ClientError) as e:
            lambda_user_client.invoke(FunctionName=function_name)
        snapshot.match("invoke-user-client-denied", e.value.response)

        aws_client.lambda_.add_permission(
            FunctionName=function_name,
            StatementId=f"s-{short_uid()}",
            Action="lambda:InvokeFunction",
            Principal=create_user_response["User"]["Arn"],
        )

        # resource based permission should be enough to allow
        lambda_result_user_client = lambda_user_client.invoke(FunctionName=function_name)
        snapshot.match("invoke-user-client-allowed", lambda_result_user_client)

    @markers.snapshot.skip_snapshot_verify(paths=["$..repository.repositoryUri"])
    @markers.aws.validated
    def test_ecr_repository_policies(
        self, create_repository, create_user, create_client_for_user, snapshot, aws_client
    ):
        user_name = f"user-{short_uid()}"
        repository_name = f"repo-{short_uid()}"
        create_repository_result = create_repository(repositoryName=repository_name)
        snapshot.match("create-repository-result", create_repository_result)

        default_client_describe_images = aws_client.ecr.describe_images(
            repositoryName=repository_name
        )
        snapshot.match("default_client_describe_images", default_client_describe_images)

        create_user_response = create_user(UserName=user_name)
        snapshot.match("create-user-response", create_user_response)
        ecr_user_client: "ECRClient" = create_client_for_user(user_name=user_name, service="ecr")
        # random user may not invoke client
        with pytest.raises(ClientError) as e:
            ecr_user_client.describe_images(repositoryName=repository_name)
        snapshot.match("describe-images-user-client-denied", e.value.response)

        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "s1",
                    "Effect": "Allow",
                    "Principal": {"AWS": create_user_response["User"]["Arn"]},
                    "Action": ["ecr:DescribeImages"],
                }
            ],
        }
        aws_client.ecr.set_repository_policy(
            repositoryName=repository_name, policyText=json.dumps(policy)
        )

        describe_image_response = ecr_user_client.describe_images(repositoryName=repository_name)
        snapshot.match("describe-images-user-client-allowed", describe_image_response)

    @markers.aws.validated
    def test_get_lambda_layer(
        self, create_user, create_client_for_user, cleanups, snapshot, aws_client
    ):
        layer_name = f"testlayer-{short_uid()}"

        fd = open(os.path.join(os.path.dirname(__file__), "../lambda_/layer.zip"), "rb")
        dummylayer = fd.read()

        publish_result = aws_client.lambda_.publish_layer_version(
            LayerName=layer_name,
            CompatibleRuntimes=[Runtime.python3_12],
            Content={"ZipFile": dummylayer},
            CompatibleArchitectures=[Architecture.x86_64],
        )
        cleanups.append(
            lambda: aws_client.lambda_.delete_layer_version(
                LayerName=layer_name, VersionNumber=publish_result["Version"]
            )
        )
        snapshot.match("create-layer-result", publish_result)

        user_name = f"test-user-{short_uid()}"
        create_user_response = create_user(UserName=user_name)
        snapshot.match("create-user-response", create_user_response)

        lambda_user_client: "LambdaClient" = create_client_for_user(
            user_name=user_name, service="lambda"
        )
        with pytest.raises(ClientError) as e:
            lambda_user_client.get_layer_version(
                LayerName=layer_name, VersionNumber=publish_result["Version"]
            )
        snapshot.match("get-layer-user-client-denied", e.value.response)

        aws_client.lambda_.add_layer_version_permission(
            LayerName=layer_name,
            StatementId=f"s-{short_uid()}",
            VersionNumber=publish_result["Version"],
            Action="lambda:GetLayerVersion",
            Principal="*",  # This parameter only accepts account root arn or *
        )
        get_layer_response = lambda_user_client.get_layer_version(
            LayerName=layer_name, VersionNumber=publish_result["Version"]
        )
        snapshot.match("get-layer-user-client-allowed", get_layer_response)

    # TODO test addPermission as well, if feasible
    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(
        paths=[
            "$..Error.Detail",
        ]
    )  # Not able to serialize as in the spec
    @pytest.mark.parametrize("sqs_service_name", ["sqs", "sqs_query"], ids=["sqs", "sqs_query"])
    def test_sqs_receive_queue_attributes(
        self,
        create_user,
        client_factory_for_user,
        sqs_create_queue,
        sqs_get_queue_arn,
        snapshot,
        aws_client,
        sqs_service_name,
    ):
        queue_name = f"test-queue-{short_uid()}"
        user_name = f"test-user-{short_uid()}"

        queue_url = sqs_create_queue(QueueName=queue_name)
        queue_arn = sqs_get_queue_arn(queue_url)
        snapshot.match("queue-arn", queue_arn)

        create_user_response = create_user(UserName=user_name)
        snapshot.match("user-arn", create_user_response["User"]["Arn"])

        sqs_user_client = getattr(client_factory_for_user(user_name=user_name), sqs_service_name)

        aws_client.sqs.send_message(QueueUrl=queue_url, MessageBody="test")

        # try receiving without permissions
        with pytest.raises(ClientError) as e:
            sqs_user_client.receive_message(QueueUrl=queue_url)
        snapshot.match("receive-user-client-denied", e.value.response)

        policy = {
            "Version": "2012-10-17",
            "Id": "SqsQueuePolicy",
            "Statement": [
                {
                    "Sid": "s1",
                    "Effect": "Allow",
                    "Principal": {"AWS": create_user_response["User"]["Arn"]},
                    "Action": ["sqs:ReceiveMessage"],
                    "Resource": queue_arn,
                }
            ],
        }
        aws_client.sqs.set_queue_attributes(
            QueueUrl=queue_url, Attributes={"Policy": json.dumps(policy)}
        )

        receive_message_response = sqs_user_client.receive_message(QueueUrl=queue_url)
        snapshot.match("receive-user-client-allowed", receive_message_response)

    @markers.aws.validated
    def test_sns_publish_topic_attributes(
        self, create_user, create_client_for_user, sns_create_topic, snapshot, aws_client
    ):
        topic_name = f"test-topic-{short_uid()}"
        user_name = f"test-user-{short_uid()}"

        topic_arn = sns_create_topic(Name=topic_name)["TopicArn"]
        snapshot.match("topic-arn", topic_arn)

        create_user_response = create_user(UserName=user_name)
        snapshot.match("create-user-response", create_user_response)

        sns_user_client: "SNSClient" = create_client_for_user(user_name=user_name, service="sns")
        # TODO remove override default permissions as soon as statement evaluation is working
        policy = {
            "Version": "2012-10-17",
            "Id": "SnsTopicPolicy",
            "Statement": [
                {
                    "Sid": "s1",
                    "Effect": "Allow",
                    "Principal": {"AWS": create_user_response["User"]["Arn"]},
                    "Action": ["sns:DeleteTopic"],
                    "Resource": topic_arn,
                }
            ],
        }
        aws_client.sns.set_topic_attributes(
            TopicArn=topic_arn, AttributeName="Policy", AttributeValue=json.dumps(policy)
        )

        # try receiving without permissions
        with pytest.raises(ClientError) as e:
            sns_user_client.publish(TopicArn=topic_arn, Message="test-message")
        snapshot.match("publish-user-client-denied", e.value.response)

        policy = {
            "Version": "2012-10-17",
            "Id": "SnsTopicPolicy",
            "Statement": [
                {
                    "Sid": "s1",
                    "Effect": "Allow",
                    "Principal": {"AWS": create_user_response["User"]["Arn"]},
                    "Action": ["sns:Publish"],
                    "Resource": topic_arn,
                }
            ],
        }
        aws_client.sns.set_topic_attributes(
            TopicArn=topic_arn, AttributeName="Policy", AttributeValue=json.dumps(policy)
        )

        receive_message_response = sns_user_client.publish(
            TopicArn=topic_arn, Message="test-message"
        )
        snapshot.match("publish-user-client-allowed", receive_message_response)

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(
        paths=[
            "$..Error.Detail",
            "$..Error.Message",  # TODO provide policy for denial to iam plugin to get proper error messages
        ]
    )  # Not able to serialize as in the spec
    @pytest.mark.parametrize("sqs_service_name", ["sqs", "sqs_query"], ids=["sqs", "sqs_query"])
    def test_sqs_receive_queue_attributes_resource_deny(
        self,
        create_user,
        client_factory_for_user,
        sqs_create_queue,
        sqs_get_queue_arn,
        snapshot,
        aws_client,
        sqs_service_name,
    ):
        """Test policy enforcement of a user which is allowed by identity policy but denied by resource policy"""
        queue_name = f"test-queue-{short_uid()}"
        user_name = f"test-user-{short_uid()}"

        queue_url = sqs_create_queue(QueueName=queue_name)
        queue_arn = sqs_get_queue_arn(queue_url)
        snapshot.match("queue-arn", queue_arn)

        create_user_response = create_user(UserName=user_name)
        snapshot.match("user-arn", create_user_response["User"]["Arn"])

        aws_client.iam.put_user_policy(
            UserName=user_name,
            PolicyName=f"p{short_uid()}",
            PolicyDocument=json.dumps(
                {
                    "Version": "2012-10-17",
                    "Id": "SqsIdentityPolicy",
                    "Statement": [
                        {
                            "Sid": f"s{short_uid()}",
                            "Effect": "Allow",
                            "Action": ["sqs:ReceiveMessage"],
                            "Resource": queue_arn,
                        }
                    ],
                }
            ),
        )

        sqs_user_client = getattr(client_factory_for_user(user_name=user_name), sqs_service_name)

        aws_client.sqs.send_message(QueueUrl=queue_url, MessageBody="test")

        # try receiving with identity permissions
        receive_message_response = sqs_user_client.receive_message(QueueUrl=queue_url)
        snapshot.match("receive-user-allowed", receive_message_response)

        # set resource based policy to Deny and check if the action gets denied
        policy = {
            "Version": "2012-10-17",
            "Id": "SqsQueuePolicy",
            "Statement": [
                {
                    "Sid": "s1",
                    "Effect": "Deny",
                    "Principal": {"AWS": create_user_response["User"]["Arn"]},
                    "Action": ["sqs:ReceiveMessage"],
                    "Resource": queue_arn,
                }
            ],
        }
        aws_client.sqs.set_queue_attributes(
            QueueUrl=queue_url, Attributes={"Policy": json.dumps(policy)}
        )

        def _receive():
            try:
                sqs_user_client.receive_message(QueueUrl=queue_url)
                return False
            except Exception:
                return True

        assert poll_condition(_receive, timeout=20)
        with pytest.raises(ClientError) as e:
            sqs_user_client.receive_message(QueueUrl=queue_url)
        snapshot.match("receive-user-denied", e.value.response)

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(
        paths=[
            "$..Error.QueryErrorCode",  # TODO re-create snapshots after switching SQS to JSON again
            "$..Error.Detail",
            "$..Error.Message",  # TODO provide policy for denial to iam plugin to get proper error messages
        ]
    )  # Not able to serialize as in the spec
    @pytest.mark.parametrize("sqs_service_name", ["sqs", "sqs_query"], ids=["sqs", "sqs_query"])
    def test_sqs_receive_queue_attributes_role_permission_boundary(
        self,
        create_role,
        client_factory_for_role,
        sqs_create_queue,
        sqs_get_queue_arn,
        create_policy,
        account_id,
        snapshot,
        aws_client,
        sqs_service_name,
        region_name,
    ):
        """
        Test policy enforcement of a role with an implicit deny by its permission boundary but an allow for the session
        """
        queue_name = f"test-queue-{short_uid()}"
        role_name = f"test-role-{short_uid()}"
        session_name = f"test-session-{short_uid()}"
        permission_boundary_policy_name = f"perm-boundary-{short_uid()}"

        snapshot.add_transformers_list(
            [
                snapshot.transform.regex(queue_name, "<queue-name>"),
                snapshot.transform.regex(role_name, "<role-name>"),
                snapshot.transform.regex(session_name, "<session-name>"),
            ]
        )

        queue_url = sqs_create_queue(QueueName=queue_name)
        queue_arn = sqs_get_queue_arn(queue_url)

        assume_policy_doc = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "sts:AssumeRole",
                    "Principal": {"AWS": account_id},
                    "Effect": "Allow",
                }
            ],
        }
        create_role_response = create_role(
            RoleName=role_name, AssumeRolePolicyDocument=json.dumps(assume_policy_doc)
        )

        sqs_role_client = getattr(
            client_factory_for_role(role_name=role_name, session_name=session_name),
            sqs_service_name,
        )

        aws_client.sqs.send_message(QueueUrl=queue_url, MessageBody="test")

        policy = {
            "Version": "2012-10-17",
            "Id": "SqsQueuePolicy",
            "Statement": [
                {
                    "Sid": "s1",
                    "Effect": "Allow",
                    "Principal": {"AWS": create_role_response["Role"]["Arn"]},
                    "Action": ["sqs:ReceiveMessage"],
                    "Resource": queue_arn,
                }
            ],
        }
        aws_client.sqs.set_queue_attributes(
            QueueUrl=queue_url, Attributes={"Policy": json.dumps(policy)}
        )

        # try receiving
        def _try_receive(expected: int):
            response = sqs_role_client.receive_message(QueueUrl=queue_url)
            messages = response.get("Messages", [])
            assert len(messages) == expected
            if expected == 1:
                aws_client.sqs.delete_message(
                    QueueUrl=queue_url, ReceiptHandle=messages[0]["ReceiptHandle"]
                )
            return response

        receive_message_response = retry(_try_receive, retries=10, expected=1)
        snapshot.match("receive-role-allowed", receive_message_response)

        permission_boundary = {
            "Version": "2012-10-17",
            "Id": "PermissionBoundary",
            "Statement": [
                {
                    "Sid": "permbound1",
                    "Effect": "Allow",
                    "Action": ["sqs:SendMessage"],
                    "Resource": queue_arn,
                }
            ],
        }
        policy_arn = create_policy(
            PolicyName=permission_boundary_policy_name,
            PolicyDocument=json.dumps(permission_boundary),
        )["Policy"]["Arn"]
        aws_client.iam.put_role_permissions_boundary(
            RoleName=role_name, PermissionsBoundary=policy_arn
        )

        def _receive():
            try:
                sqs_role_client.receive_message(QueueUrl=queue_url)
                return False
            except Exception:
                return True

        assert poll_condition(_receive, timeout=40)
        with pytest.raises(ClientError) as e:
            sqs_role_client.receive_message(QueueUrl=queue_url)
        snapshot.match("receive-role-denied", e.value.response)

        # try setting the principal to the assumed role session instead of the role
        policy = {
            "Version": "2012-10-17",
            "Id": "SqsQueuePolicy",
            "Statement": [
                {
                    "Sid": "s1",
                    "Effect": "Allow",
                    "Principal": {
                        "AWS": f"arn:{get_partition(region_name)}:sts::{account_id}:assumed-role/{role_name}/{session_name}"
                    },
                    "Action": ["sqs:ReceiveMessage"],
                    "Resource": queue_arn,
                }
            ],
        }
        aws_client.sqs.set_queue_attributes(
            QueueUrl=queue_url, Attributes={"Policy": json.dumps(policy)}
        )

        receive_message_response = retry(_try_receive, retries=10, expected=0)
        snapshot.match("receive-session-allowed", receive_message_response)

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(
        paths=["$..Error.Detail"]
    )  # Not able to serialize as in the spec
    def test_sqs_receive_queue_attributes_user_permission_boundary(
        self,
        create_user,
        create_client_for_user,
        sqs_create_queue,
        sqs_get_queue_arn,
        create_policy,
        snapshot,
        aws_client,
    ):
        """Test policy enforcement of a user with an implicit deny by its permission boundary but an allow by a resource based policy"""
        queue_name = f"test-queue-{short_uid()}"
        user_name = f"test-user-{short_uid()}"
        permission_boundary_policy_name = f"perm-boundary-{short_uid()}"

        queue_url = sqs_create_queue(QueueName=queue_name)
        queue_arn = sqs_get_queue_arn(queue_url)

        create_user_response = create_user(UserName=user_name)

        aws_client.sqs.send_message(QueueUrl=queue_url, MessageBody="test")

        permission_boundary = {
            "Version": "2012-10-17",
            "Id": "PermissionBoundary",
            "Statement": [
                {
                    "Sid": "permbound1",
                    "Effect": "Allow",
                    "Action": ["sqs:SendMessage"],
                    "Resource": queue_arn,
                }
            ],
        }
        policy_arn = create_policy(
            PolicyName=permission_boundary_policy_name,
            PolicyDocument=json.dumps(permission_boundary),
        )["Policy"]["Arn"]
        aws_client.iam.put_user_permissions_boundary(
            UserName=user_name, PermissionsBoundary=policy_arn
        )

        policy = {
            "Version": "2012-10-17",
            "Id": "SqsQueuePolicy",
            "Statement": [
                {
                    "Sid": "s1",
                    "Effect": "Allow",
                    "Principal": {"AWS": create_user_response["User"]["Arn"]},
                    "Action": ["sqs:ReceiveMessage"],
                    "Resource": queue_arn,
                }
            ],
        }
        aws_client.sqs.set_queue_attributes(
            QueueUrl=queue_url, Attributes={"Policy": json.dumps(policy)}
        )

        sqs_user_client: "SQSClient" = create_client_for_user(user_name=user_name, service="sqs")

        # try receiving
        receive_message_response = sqs_user_client.receive_message(QueueUrl=queue_url)
        snapshot.match("receive-user-allowed", receive_message_response)

    @markers.aws.validated
    def test_kms_key(
        self, cleanups, account_id, create_client_for_user, create_user, snapshot, aws_client
    ):
        key = aws_client.kms.create_key()["KeyMetadata"]
        key_id = key["KeyId"]
        cleanups.append(
            lambda: aws_client.kms.schedule_key_deletion(KeyId=key_id, PendingWindowInDays=7)
        )
        snapshot.match("kms-key", key)

        user_name = f"test-user-{short_uid()}"
        create_user_response = create_user(UserName=user_name)
        snapshot.match("create-user", create_user_response)

        user_client = create_client_for_user(user_name=user_name, service="kms")
        with pytest.raises(ClientError) as e:
            user_client.describe_key(KeyId=key_id)
        snapshot.match("describe-key-denied", e.value.response)

        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "s1",
                    "Effect": "Allow",
                    "Action": ["kms:*"],
                    "Resource": key["Arn"],
                    "Principal": {"AWS": create_user_response["User"]["Arn"]},
                },
                {
                    "Sid": "s2",
                    "Effect": "Allow",
                    "Action": ["kms:*"],
                    "Resource": key["Arn"],
                    "Principal": {"AWS": account_id},
                },
            ],
        }
        aws_client.kms.put_key_policy(KeyId=key_id, PolicyName="default", Policy=json.dumps(policy))

        def test():
            user_client.describe_key(KeyId=key_id)

        retry(test, sleep=4, retries=30)

    @markers.aws.validated
    def test_secretsmanager_policy(
        self, cleanups, create_user, create_client_for_user, snapshot, aws_client
    ):
        create_response = aws_client.secretsmanager.create_secret(
            Name=f"test-secret-{short_uid()}", SecretString="test-secret-value"
        )
        cleanups.append(
            lambda: aws_client.secretsmanager.delete_secret(
                SecretId=create_response["ARN"], ForceDeleteWithoutRecovery=True
            )
        )
        snapshot.add_transformer(snapshot.transform.key_value("Name", "test-secret-name"))
        snapshot.match("create-secret", create_response)

        user_name = f"test-user-{short_uid()}"
        create_user_response = create_user(UserName=user_name)
        snapshot.match("create-user", create_user_response)

        client_user = create_client_for_user(user_name=user_name, service="secretsmanager")
        with pytest.raises(ClientError) as e:
            client_user.get_secret_value(SecretId=create_response["ARN"])
        snapshot.match("get-secret-value", e.value.response)

        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "s1",
                    "Effect": "Allow",
                    "Principal": {"AWS": create_user_response["User"]["Arn"]},
                    "Action": ["secretsmanager:*"],
                    "Resource": create_response["ARN"],
                }
            ],
        }
        aws_client.secretsmanager.put_resource_policy(
            ResourcePolicy=json.dumps(policy), SecretId=create_response["ARN"]
        )
        client_user.get_secret_value(SecretId=create_response["ARN"])

    @markers.aws.validated
    def test_backup_vault(
        self, snapshot, create_user, create_client_for_user, cleanups, account_id, aws_client
    ):
        vault_name = f"vault-{short_uid()}"
        create_response = aws_client.backup.create_backup_vault(BackupVaultName=vault_name)
        cleanups.append(lambda: aws_client.backup.delete_backup_vault(BackupVaultName=vault_name))
        snapshot.match("create-vault", create_response)

        user_name = f"user-{short_uid()}"
        create_user_response = create_user(UserName=user_name)
        snapshot.match("create-user-response", create_user_response)

        client_user = create_client_for_user(user_name=user_name, service="backup")
        with pytest.raises(ClientError) as e:
            client_user.describe_backup_vault(BackupVaultName=vault_name)
        snapshot.match("describe-vault-denied", e.value.response)

        policy = {
            "Version": "2012-10-17",
            "Id": "BackupVaultPolicy",
            "Statement": [
                {
                    "Sid": "s1",
                    "Effect": "Allow",
                    "Principal": {"AWS": create_user_response["User"]["Arn"]},
                    "Action": ["backup:DescribeBackupVault"],
                    "Resource": f"arn:{get_partition(aws_client.backup.meta.region_name)}:backup:{aws_client.backup.meta.region_name}:{account_id}:backup-vault:{vault_name}",
                }
            ],
        }

        aws_client.backup.put_backup_vault_access_policy(
            BackupVaultName=vault_name, Policy=json.dumps(policy)
        )
        client_user.describe_backup_vault(BackupVaultName=vault_name)

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(
        paths=[
            "$..CreationToken",
            "$..Encrypted",
            "$..LifeCycleState",
            "$..Name",
            "$..NumberOfMountTargets",
            "$..OwnerId",
            "$..PerformanceMode",
            "$..SizeInBytes",
            "$..Tags",
            "$..ThroughputMode",
        ]
    )
    def test_efs_file_system_policy(
        self, create_user, create_client_for_user, cleanups, snapshot, aws_client
    ):
        create_response = aws_client.efs.create_file_system()
        cleanups.append(
            lambda: aws_client.efs.delete_file_system(FileSystemId=create_response["FileSystemId"])
        )
        snapshot.match("create", create_response)

        user_name = f"user-{short_uid()}"
        create_user_response = create_user(UserName=user_name)
        snapshot.match("create-user-response", create_user_response)

        client_user = create_client_for_user(user_name=user_name, service="efs")
        with pytest.raises(ClientError) as e:
            client_user.describe_file_systems(FileSystemId=create_response["FileSystemId"])
        snapshot.match("describe-file-systems-user-denied", e.value.response)

        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "s1",
                    "Effect": "Allow",
                    "Principal": {"AWS": create_user_response["User"]["Arn"]},
                    "Action": ["elasticfilesystem:*"],
                    "Resource": create_response["FileSystemArn"],
                }
            ],
        }
        aws_client.efs.put_file_system_policy(
            FileSystemId=create_response["FileSystemId"],
            Policy=json.dumps(policy),
            BypassPolicyLockoutSafetyCheck=True,
        )

        describe_response = client_user.describe_file_systems(
            FileSystemId=create_response["FileSystemId"]
        )
        snapshot.match("describe-file-systems-user-allowed", describe_response)

    @markers.aws.validated
    def test_eventbridge_policies(
        self, create_user, create_client_for_user, cleanups, snapshot, aws_client
    ):
        event_bus_name = f"test-event-bus-{short_uid()}"
        event_bus_response = aws_client.events.create_event_bus(Name=event_bus_name)
        cleanups.append(lambda: aws_client.events.delete_event_bus(Name=event_bus_name))
        snapshot.match("event-bus", event_bus_response)

        user_name = f"test-user-{short_uid()}"
        create_user_response = create_user(UserName=user_name)
        snapshot.match("user", create_user_response)
        user_client = create_client_for_user(user_name=user_name, service="events")

        with pytest.raises(ClientError) as e:
            user_client.put_events(
                Entries=[
                    {
                        "Source": "test",
                        "DetailType": "test",
                        "Detail": "{}",
                        "EventBusName": event_bus_name,
                    }
                ]
            )
        snapshot.match("put-events-denied", e.value.response)

        aws_client.events.put_permission(
            EventBusName=event_bus_name,
            Policy=json.dumps(
                {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Sid": "test",
                            "Effect": "Allow",
                            "Principal": {"AWS": create_user_response["User"]["Arn"]},
                            "Action": ["events:PutEvents"],
                            "Resource": event_bus_response["EventBusArn"],
                        }
                    ],
                }
            ),
        )

        response = user_client.put_events(
            Entries=[
                {
                    "Source": "test",
                    "DetailType": "test",
                    "Detail": "{}",
                    "EventBusName": event_bus_name,
                }
            ]
        )
        snapshot.match("put-events-allowed", response)

    @markers.aws.validated
    def test_s3_bucket_policy(
        self, create_user, create_client_for_user, snapshot, s3_bucket, aws_client, region_name
    ):
        bucket_name = s3_bucket

        user_name = f"user-{short_uid()}"
        create_user_response = create_user(UserName=user_name)
        snapshot.match("create-user-response", create_user_response)

        client_user = create_client_for_user(user_name=user_name, service="s3")

        with pytest.raises(ClientError) as e:
            client_user.list_objects(Bucket=bucket_name)
        snapshot.match("list-objects-user-denied", e.value.response)

        with pytest.raises(ClientError) as e:
            client_user.put_object(Bucket=bucket_name, Key="test", Body=b"test")
        snapshot.match("put-object-user-denied", e.value.response)

        with pytest.raises(ClientError) as e:
            client_user.get_object(Bucket=bucket_name, Key="test")
        snapshot.match("get-object-user-denied", e.value.response)

        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "s1",
                    "Effect": "Allow",
                    "Principal": {"AWS": create_user_response["User"]["Arn"]},
                    "Action": ["s3:*"],
                    "Resource": [
                        f"arn:{get_partition(region_name)}:s3:::{bucket_name}/*",
                        f"arn:{get_partition(region_name)}:s3:::{bucket_name}",
                    ],
                }
            ],
        }
        aws_client.s3.put_bucket_policy(Bucket=bucket_name, Policy=json.dumps(policy))

        def test():
            client_user.list_objects(Bucket=bucket_name)
            client_user.put_object(Bucket=bucket_name, Key="test", Body=b"test")
            client_user.get_object(Bucket=bucket_name, Key="test")

        retry(test, sleep=(10 if is_aws_cloud() else 1), retries=3)

    @markers.aws.validated
    def test_iam_trust_policy(
        self, aws_client, client_factory_for_user, create_user, create_role, snapshot
    ):
        snapshot.add_transformer(snapshot.transform.key_value("RoleId"))
        user_name = f"user-{short_uid()}"
        role_name = f"role-{short_uid()}"
        allow_policy_name = f"policy-{short_uid()}"
        deny_policy_name = f"policy-{short_uid()}"
        create_user_response = create_user(UserName=user_name)
        snapshot.match("create-user-response", create_user_response)
        user_arn = create_user_response["User"]["Arn"]

        # statements cannot be empty, so we just deny access to lambda here
        trust_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Deny",
                    "Principal": {"Service": "lambda.amazonaws.com"},
                    "Action": "sts:AssumeRole",
                }
            ],
        }

        create_role_response = create_role(
            RoleName=role_name, AssumeRolePolicyDocument=json.dumps(trust_policy)
        )
        snapshot.match("create-role-response", create_role_response)
        role_arn = create_role_response["Role"]["Arn"]

        sts_client = client_factory_for_user(user_name=user_name).sts
        with pytest.raises(ClientError) as e:
            sts_client.assume_role(RoleArn=role_arn, RoleSessionName=f"test-session-{short_uid()}")
        snapshot.match("assume-role-without-permission", e.value.response)

        # try adding an identity based permission - should not succeed
        identity_assume_permission = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "sts:AssumeRole",
                    ],
                    "Resource": role_arn,
                }
            ],
        }
        aws_client.iam.put_user_policy(
            PolicyName=allow_policy_name,
            PolicyDocument=json.dumps(identity_assume_permission),
            UserName=user_name,
        )

        with pytest.raises(ClientError) as e:
            sts_client.assume_role(RoleArn=role_arn, RoleSessionName=f"test-session-{short_uid()}")
        snapshot.match("assume-role-only-identity", e.value.response)

        # add trust policy correctly
        trust_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {"Effect": "Allow", "Principal": {"AWS": user_arn}, "Action": "sts:AssumeRole"}
            ],
        }
        aws_client.iam.update_assume_role_policy(
            RoleName=role_name, PolicyDocument=json.dumps(trust_policy)
        )

        def _assume():
            sts_client.assume_role(RoleArn=role_arn, RoleSessionName=f"test-session-{short_uid()}")

        # against aws, we need to wait at least 60s between requests to avoid caching of the access deny
        retry(_assume, retries=5, sleep=60 if is_aws_cloud() else 1)

        # remove identity policy, should still work
        aws_client.iam.delete_user_policy(UserName=user_name, PolicyName=allow_policy_name)

        sts_client.assume_role(RoleArn=role_arn, RoleSessionName=f"test-session-{short_uid()}")

        # Explicitly deny using identity based permission
        identity_assume_denied_permission = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Deny",
                    "Action": [
                        "sts:AssumeRole",
                    ],
                    "Resource": role_arn,
                }
            ],
        }
        aws_client.iam.put_user_policy(
            PolicyName=deny_policy_name,
            PolicyDocument=json.dumps(identity_assume_denied_permission),
            UserName=user_name,
        )

        def _assume_denied():
            try:
                sts_client.assume_role(
                    RoleArn=role_arn, RoleSessionName=f"test-session-{short_uid()}"
                )
                return False
            except Exception:
                return True

        assert poll_condition(_assume_denied, timeout=360, interval=60 if is_aws_cloud() else 4)

        with pytest.raises(ClientError) as e:
            sts_client.assume_role(RoleArn=role_arn, RoleSessionName=f"test-session-{short_uid()}")
        snapshot.match("assume-role-identity-denied", e.value.response)


class TestIAMConditions:
    @markers.aws.validated
    def test_s3_create_bucket_secure_connection(
        self, create_user, client_factory_for_user, snapshot, aws_client, region_name, cleanups
    ):
        snapshot.add_transformer(snapshot.transform.iam_api())
        user_name = f"user-{short_uid()}"
        policy_name = f"policy-{short_uid()}"
        bucket_name = f"bucket-{short_uid()}"

        create_user_response = create_user(UserName=user_name)
        snapshot.match("create-user-response", create_user_response)

        kwargs = {}
        if region_name != "us-east-1":
            kwargs = {"CreateBucketConfiguration": {"LocationConstraint": region_name}}
        s3_client_user = client_factory_for_user(user_name=user_name).s3
        cleanups.append(lambda: aws_client.s3.delete_bucket(Bucket=bucket_name))

        with pytest.raises(ClientError) as e:
            s3_client_user.create_bucket(Bucket=bucket_name, **kwargs)

        snapshot.match("create-bucket-failed", e.value.response)

        policy = {
            "Id": "AccessControl",
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "AllowAll",
                    "Action": "s3:*",
                    "Effect": "Allow",
                    "Resource": [
                        f"arn:{get_partition(region_name)}:s3:::{bucket_name}",
                        f"arn:{get_partition(region_name)}:s3:::{bucket_name}/*",
                    ],
                },
                {
                    "Sid": "DenyInsecureRequests",
                    "Action": "s3:*",
                    "Effect": "Deny",
                    "Resource": [
                        f"arn:{get_partition(region_name)}:s3:::{bucket_name}",
                        f"arn:{get_partition(region_name)}:s3:::{bucket_name}/*",
                    ],
                    "Condition": {"Bool": {"aws:SecureTransport": "false"}},
                },
            ],
        }
        aws_client.iam.put_user_policy(
            UserName=user_name, PolicyName=policy_name, PolicyDocument=json.dumps(policy)
        )

        def _create_bucket():
            return s3_client_user.create_bucket(Bucket=bucket_name, **kwargs)

        retry(_create_bucket, sleep=(10 if is_aws_cloud() else 1), retries=15)
