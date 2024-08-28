import json
import logging
from typing import TYPE_CHECKING

import pytest
from botocore.exceptions import ClientError
from localstack.testing.aws.util import is_aws_cloud
from localstack.testing.pytest import markers
from localstack.utils.aws.arns import get_partition
from localstack.utils.strings import short_uid
from localstack.utils.sync import retry

if TYPE_CHECKING:
    from mypy_boto3_dms.type_defs import CreateReplicationInstanceResponseTypeDef

from localstack.pro.core.aws.api.dms import (
    KinesisSettings,
    MessageFormatValue,
    MySQLSettings,
    PostgreSQLSettings,
    S3Settings,
)

LOG = logging.getLogger(__name__)


class TestDms:
    @markers.aws.validated
    def test_create_endpoint_invalid(
        self,
        aws_client,
        create_secret,
        create_role_with_policy_for_principal,
        region_name,
        account_id,
        snapshot,
    ):
        secret = create_secret(Name=f"dms-secret-{short_uid()}", SecretString="secretstring")
        secret_arn = secret["ARN"]
        _, dms_role_arn = create_role_with_policy_for_principal(
            principal={"Service": f"dms.{region_name}.amazonaws.com"},
            resource=secret_arn,
            effect="Allow",
            actions=["secretsmanager:GetSecretValue"],
        )

        with pytest.raises(ClientError) as e:
            aws_client.dms.create_endpoint(
                EndpointIdentifier=f"test-endpoint--{short_uid()}",
                EndpointType="source",
                EngineName="mysql",
                Password="admin",
            )
        snapshot.match("create-endpoint-invalid-identifier", e.value.response)

        with pytest.raises(ClientError) as e:
            aws_client.dms.create_endpoint(
                EndpointIdentifier=f"test-endpoint-{short_uid()}",
                EndpointType="nope",  # noqa
                EngineName="mysql",
                Password="foobar",
            )

        snapshot.match("create-endpoint-invalid-type", e.value.response)

        with pytest.raises(ClientError) as e:
            aws_client.dms.create_endpoint(
                EndpointIdentifier=f"test-endpoint-{short_uid()}",
                EndpointType="SOURCE",  # noqa
                EngineName="mysql",
                Password="foobar",
            )

        snapshot.match("create-endpoint-invalid-type-2", e.value.response)

        with pytest.raises(ClientError) as e:
            aws_client.dms.create_endpoint(
                EndpointIdentifier=f"test-endpoint-{short_uid()}",
                EndpointType="source",
                EngineName="foobared",
                Password="",
            )

        snapshot.match("create-endpoint-invalid-engine", e.value.response)

        with pytest.raises(ClientError) as e:
            aws_client.dms.create_endpoint(
                EndpointIdentifier=f"test-endpoint-{short_uid()}",
                EndpointType="source",
                EngineName="mysql",
                Password="",
            )

        snapshot.match("create-endpoint-missing-password", e.value.response)

        with pytest.raises(ClientError) as e:
            aws_client.dms.create_endpoint(
                EndpointIdentifier=f"test-endpoint-{short_uid()}",
                EndpointType="source",
                EngineName="mysql",
                Password="admin",
            )
        snapshot.match("create-endpoint-missing-username", e.value.response)

        with pytest.raises(ClientError) as e:
            aws_client.dms.create_endpoint(
                EndpointIdentifier=f"test-endpoint-{short_uid()}",
                EndpointType="source",
                EngineName="mysql",
                Password="admin",
                Username="admin",
            )
        snapshot.match("create-endpoint-missing-serverName", e.value.response)

        with pytest.raises(ClientError) as e:
            aws_client.dms.create_endpoint(
                EndpointIdentifier=f"test-endpoint-{short_uid()}",
                EndpointType="source",
                EngineName="mysql",
                Password="admin",
                Username="admin",
                ServerName="server",
            )
        snapshot.match("create-endpoint-missing-port", e.value.response)

        with pytest.raises(ClientError) as e:
            aws_client.dms.create_endpoint(
                EndpointIdentifier=f"test-endpoint-{short_uid()}",
                EndpointType="source",
                EngineName="mysql",
                Password="admin",
                Username="admin",
                ServerName="server",
                Port=0,
            )
        snapshot.match("create-endpoint-port-out-of-range", e.value.response)

        with pytest.raises(ClientError) as e:
            aws_client.dms.create_endpoint(
                EndpointIdentifier=f"test-endpoint-{short_uid()}",
                EndpointType="source",
                EngineName="mysql",
                Password="PASSWORD",
                MySQLSettings=MySQLSettings(
                    SecretsManagerAccessRoleArn=dms_role_arn,
                    SecretsManagerSecretId=secret_arn,
                ),
            )

        snapshot.match("create-endpoint-invalid-combination", e.value.response)

        with pytest.raises(ClientError) as e:
            aws_client.dms.create_endpoint(
                EndpointIdentifier=f"test-endpoint-{short_uid()}",
                EndpointType="source",
                EngineName="mysql",
                MySQLSettings=MySQLSettings(
                    SecretsManagerAccessRoleArn=dms_role_arn,
                ),
            )

        snapshot.match("create-endpoint-missing-secret", e.value.response)

        with pytest.raises(ClientError) as e:
            aws_client.dms.create_endpoint(
                EndpointIdentifier=f"test-endpoint-{short_uid()}",
                EndpointType="source",
                EngineName="mysql",
                MySQLSettings=MySQLSettings(
                    SecretsManagerSecretId=secret_arn,
                ),
            )

        snapshot.match("create-endpoint-missing-role", e.value.response)

        with pytest.raises(ClientError) as e:
            aws_client.dms.create_endpoint(
                EndpointIdentifier=f"test-endpoint-{short_uid()}",
                EndpointType="source",
                EngineName="mysql",
                MySQLSettings=MySQLSettings(
                    SecretsManagerAccessRoleArn=f"arn:{get_partition(region_name)}:iam::{account_id}:role/fictitiousRole",
                    SecretsManagerSecretId=f"arn:{get_partition(region_name)}:secretsmanager:{region_name}:{account_id}:secret:invalid-secret",
                ),
            )

        snapshot.match("create-endpoint-invalid-role", e.value.response)

        with pytest.raises(ClientError) as e:
            aws_client.dms.create_endpoint(
                EndpointIdentifier=f"test-endpoint-{short_uid()}",
                EndpointType="source",
                EngineName="mysql",
                MySQLSettings=MySQLSettings(
                    SecretsManagerAccessRoleArn=dms_role_arn,
                    SecretsManagerSecretId=f"arn:{get_partition(region_name)}:secretsmanager:{region_name}:{account_id}:secret:invalid-secret",
                ),
            )

        snapshot.match("create-endpoint-invalid-secret", e.value.response)

    @markers.aws.validated
    def test_create_source_endpoint_mysql_with_tags(
        self, dms_create_endpoint, snapshot, aws_client
    ):
        snapshot.add_transformer(snapshot.transform.dms_api())
        tags = [
            {"Key": "endpoint_test", "Value": "my_mysql_tags"},
            {"Key": "test_aws", "Value": "validated"},
        ]
        endpoint = dms_create_endpoint(
            EndpointIdentifier=f"test-endpoint-{short_uid()}",
            EndpointType="source",
            EngineName="mysql",
            # required parameters
            Password="admin",
            Username="admin",
            ServerName="my-mysql-instance.example.com",
            Port=5432,
            DatabaseName="my_db",
            MySQLSettings=MySQLSettings(
                Username="foobar",
                ServerName="ignored",
            ),
            Tags=tags,
        )
        snapshot.match("endpoint", endpoint)
        endpoint_arn = endpoint.get("EndpointArn")

        describe_endpoint = aws_client.dms.describe_endpoints(
            Filters=[{"Name": "endpoint-arn", "Values": [endpoint_arn]}]
        )
        snapshot.match("describe-endpoint-filter-endpoint-arn", describe_endpoint)

        ## Tag specific tests
        tags = aws_client.dms.list_tags_for_resource(ResourceArn=endpoint_arn)
        tags["TagList"] = sorted(tags["TagList"], key=lambda x: x["Key"])
        snapshot.match("endpoint-tags", tags)

        tags = aws_client.dms.list_tags_for_resource(ResourceArnList=[endpoint_arn])
        tags["TagList"] = sorted(tags["TagList"], key=lambda x: x["Key"])
        snapshot.match("endpoint-tags-resource-list", tags)

        aws_client.dms.add_tags_to_resource(
            ResourceArn=endpoint_arn, Tags=[{"Key": "hello", "Value": "world"}]
        )
        tags = aws_client.dms.list_tags_for_resource(ResourceArn=endpoint_arn)
        tags["TagList"] = sorted(tags["TagList"], key=lambda x: x["Key"])
        snapshot.match("endpoint-tags-2", tags)

        aws_client.dms.remove_tags_from_resource(
            ResourceArn=endpoint_arn, TagKeys=["hello", "test_aws"]
        )
        tags = aws_client.dms.list_tags_for_resource(ResourceArn=endpoint_arn)
        tags["TagList"] = sorted(tags["TagList"], key=lambda x: x["Key"])
        snapshot.match("endpoint-tags-3", tags)

        # delete endpoint
        delete_endpoint = aws_client.dms.delete_endpoint(EndpointArn=endpoint_arn)
        snapshot.match("delete-endpoint", delete_endpoint)

        def endpoint_deleted():
            try:
                endpoints = aws_client.dms.describe_endpoints(
                    Filters=[{"Name": "endpoint-arn", "Values": [endpoint_arn]}]
                )
                assert len(endpoints.get("Endpoints")) == 0
            except ClientError:
                return True

        # wait until endpoint is deleted
        retry(
            endpoint_deleted,
            retries=20 if is_aws_cloud() else 3,
            sleep_before=2,
            sleep=30 if is_aws_cloud() else 1,
        )
        # verify it's not returned anymore, and the filter throws exception now
        with pytest.raises(ClientError) as e:
            aws_client.dms.describe_endpoints(
                Filters=[{"Name": "endpoint-arn", "Values": [endpoint_arn]}]
            )
        snapshot.match("describe-endpoint-filter-does-not-exist", e.value.response)

        # verify what happens when deleting non-existing endpoint
        with pytest.raises(ClientError) as e:
            aws_client.dms.delete_endpoint(EndpointArn=endpoint_arn)
        snapshot.match("delete-endpoint-does-not-exist", e.value.response)

    @markers.aws.validated
    def test_create_mysql_endpoint_with_settings(
        self,
        dms_create_endpoint,
        aws_client,
        create_secret,
        create_role_with_policy_for_principal,
        region_name,
        snapshot,
    ):
        snapshot.add_transformer(snapshot.transform.dms_api())
        secret = create_secret(Name=f"dms-secret-{short_uid()}", SecretString="secretstring")
        role_name, dms_role_arn = create_role_with_policy_for_principal(
            principal={"Service": f"dms.{region_name}.amazonaws.com"},
            resource=secret["ARN"],
            effect="Allow",
            actions=["secretsmanager:GetSecretValue"],
        )
        endpoint = dms_create_endpoint(
            EndpointIdentifier=f"test-endpoint-{short_uid()}",
            EndpointType="source",
            EngineName="mysql",
            DatabaseName="DbName",
            MySQLSettings=MySQLSettings(
                SecretsManagerAccessRoleArn=dms_role_arn,
                SecretsManagerSecretId=secret["ARN"],
            ),
        )
        snapshot.match("endpoint-with-settings", endpoint)

    @markers.aws.validated
    def test_create_target_endpoint_kinesis(
        self,
        dms_create_endpoint,
        snapshot,
        aws_client,
        account_id,
        create_role_with_policy_for_principal,
        region_name,
    ):
        snapshot.add_transformer(snapshot.transform.dms_api())
        kinesis_arn = f"arn:{get_partition(region_name)}:kinesis:{region_name}:{account_id}:stream/lambda-stream"
        role_arn = f"arn:{get_partition(region_name)}:iam::{account_id}:role/some-role"
        with pytest.raises(ClientError) as e:
            aws_client.dms.create_endpoint(
                EndpointIdentifier=f"test-endpoint-{short_uid()}",
                EndpointType="target",
                EngineName="kinesis",
            )

        snapshot.match("create-endpoint-missing-settings", e.value.response)

        with pytest.raises(ClientError) as e:
            aws_client.dms.create_endpoint(
                EndpointIdentifier=f"test-endpoint-{short_uid()}",
                EndpointType="target",
                EngineName="kinesis",
                Password="testabc",
                KinesisSettings=KinesisSettings(StreamArn=kinesis_arn),
            )
        snapshot.match("create-endpoint-invalid-password", e.value.response)

        with pytest.raises(ClientError) as e:
            aws_client.dms.create_endpoint(
                EndpointIdentifier=f"test-endpoint-{short_uid()}",
                EndpointType="target",
                EngineName="kinesis",
                KinesisSettings=KinesisSettings(ServiceAccessRoleArn=role_arn),
            )
        snapshot.match("create-endpoint-missing-kinesis-arn", e.value.response)

        with pytest.raises(ClientError) as e:
            dms_create_endpoint(
                EndpointIdentifier=f"test-endpoint-{short_uid()}",
                EndpointType="target",
                EngineName="kinesis",
                KinesisSettings=KinesisSettings(
                    StreamArn=kinesis_arn, ServiceAccessRoleArn=role_arn
                ),
            )
        snapshot.match("create-endpoint-missing-message-format", e.value.response)

        with pytest.raises(ClientError) as e:
            dms_create_endpoint(
                EndpointIdentifier=f"test-endpoint-{short_uid()}",
                EndpointType="target",
                EngineName="kinesis",
                KinesisSettings=KinesisSettings(
                    StreamArn=kinesis_arn, ServiceAccessRoleArn=role_arn, MessageFormat="something"
                ),
            )
        snapshot.match("create-endpoint-invalid-message-format", e.value.response)

        # TODO role is already verified at this point, e.g when using role_arn:
        # An error occurred (AccessDeniedFault) when calling the CreateEndpoint operation: The IAM Role arn:aws:iam::837471453475:role/some-role is not configured properly.AccessDenied
        role_name, kinesis_role_arn = create_role_with_policy_for_principal(
            principal={"Service": "dms.amazonaws.com"}, resource="*", effect="Allow", actions=["*"]
        )

        def _create_endpoint():
            endpoint = dms_create_endpoint(
                EndpointIdentifier=f"test-endpoint-{short_uid()}",
                EndpointType="target",
                EngineName="kinesis",
                KinesisSettings=KinesisSettings(
                    StreamArn=kinesis_arn,
                    ServiceAccessRoleArn=kinesis_role_arn,
                    MessageFormat=MessageFormatValue.json,
                ),
            )
            return endpoint

        # retry as the policy needs some time on AWS
        endpoint = retry(
            _create_endpoint,
            sleep_before=2 if is_aws_cloud() else 0,
            sleep=2 if is_aws_cloud() else 1,
            retries=20 if is_aws_cloud() else 3,
        )

        snapshot.match("endpoint", endpoint)

        endpoint_id = endpoint.get("EndpointIdentifier")

        describe_endpoint = aws_client.dms.describe_endpoints(
            Filters=[{"Name": "endpoint-id", "Values": [endpoint_id]}]
        )

        snapshot.match("describe-endpoint", describe_endpoint)

    @markers.aws.validated
    def test_describe_filter(self, aws_client, snapshot, region_name, account_id):
        # test a filter name that is not supported for endpoints
        with pytest.raises(ClientError) as e:
            filters = [
                {
                    "Name": "replication-instance-arn",
                    "Values": [
                        f"arn:{get_partition(region_name)}:dms:{region_name}:{account_id}:rep:made-up-repidentifier"
                    ],
                }
            ]
            aws_client.dms.describe_endpoints(Filters=filters)

        snapshot.match("describe-connection-invalid-filter-name", e.value.response)

        # test supported filters name values are empty
        with pytest.raises(ClientError) as e:
            filters = [{"Name": "endpoint-arn", "Values": []}]
            aws_client.dms.describe_endpoints(Filters=filters)

        snapshot.match("describe-connection-values-empty", e.value.response)

        # test supported filter, with valid value but expect no result
        with pytest.raises(ClientError) as e:
            filters = [
                {
                    "Name": "endpoint-arn",
                    "Values": [
                        f"arn:{get_partition(region_name)}:dms:{region_name}:{account_id}:endpoint:made-up-identifier"
                    ],
                }
            ]
            aws_client.dms.describe_endpoints(Filters=filters)

        snapshot.match("describe-connection-no-match", e.value.response)

    @markers.snapshot.skip_snapshot_verify(
        paths=[
            "$..ReplicationSubnetGroup",
            "$..VpcSecurityGroups",
            "$..ReplicationInstanceIpv6Addresses",
            "$..ReplicationInstancePrivateIpAddress",
            "$..ReplicationInstancePrivateIpAddresses",
            "$..ReplicationInstancePublicIpAddresses",
        ]
    )
    @markers.aws.validated
    def test_connection_kinesis(
        self,
        aws_client,
        snapshot,
        dms_create_endpoint,
        dms_create_replication_instance,
        dms_wait_for_replication_instance_status,
        create_role_with_policy_for_principal,
        account_id,
        region_name,
    ):
        """The IT tests only tests a connection for a invalid kinesis connection, that we expect to fail
        For a valid connection we would need to have a replication instance with public access
        but then we also need to setup VPC
        --> we can test valid connection with the cdk scenario test
        """
        snapshot.add_transformer(snapshot.transform.dms_api())
        snapshot.add_transformer(
            snapshot.transform.key_value("SubnetIdentifier", reference_replacement=False),
        )
        # need to create instance and endpoint to test connection
        instance: CreateReplicationInstanceResponseTypeDef = dms_create_replication_instance(
            PubliclyAccessible=False
        )
        snapshot.match("create-replication-instance", instance)
        instance_arn = instance["ReplicationInstance"]["ReplicationInstanceArn"]

        # wait until the ReplicationInstanceStatus is available
        dms_wait_for_replication_instance_status(instance_arn, "available")
        filters = [{"Name": "replication-instance-arn", "Values": [instance_arn]}]
        describe_instance = aws_client.dms.describe_replication_instances(Filters=filters)
        snapshot.match("describe-replication-instances", describe_instance)

        ## kinesis endpoint doesn't exist -> expect connection to fail
        role_name, kinesis_role_arn = create_role_with_policy_for_principal(
            principal={"Service": "dms.amazonaws.com"}, resource="*", effect="Allow", actions=["*"]
        )

        # fictive kinesis arn
        non_existent_kinesis_arn = f"arn:{get_partition(region_name)}:kinesis:{region_name}:{account_id}:stream/test-stream-not-exists"

        def _create_endpoint(arn: str):
            endpoint = dms_create_endpoint(
                EndpointIdentifier=f"test-endpoint-{short_uid()}",
                EndpointType="target",
                EngineName="kinesis",
                KinesisSettings=KinesisSettings(
                    StreamArn=arn,
                    ServiceAccessRoleArn=kinesis_role_arn,
                    MessageFormat=MessageFormatValue.json_unformatted,
                ),
            )
            return endpoint

        # retry as the policy needs some time on AWS
        endpoint = retry(
            lambda: _create_endpoint(non_existent_kinesis_arn),
            sleep_before=2 if is_aws_cloud() else 0,
            sleep=2 if is_aws_cloud() else 1,
            retries=20 if is_aws_cloud() else 3,
        )

        snapshot.match("endpoint", endpoint)
        endpoint_arn_expect_failed = endpoint.get("EndpointArn")

        # try to delete non-existing connection
        with pytest.raises(ClientError) as e:
            aws_client.dms.delete_connection(
                EndpointArn=endpoint_arn_expect_failed, ReplicationInstanceArn=instance_arn
            )

        snapshot.match("delete-connection-error", e.value.response)

        # test connection for non-existent kinesis stream
        test_connection_response = aws_client.dms.test_connection(
            ReplicationInstanceArn=instance_arn, EndpointArn=endpoint_arn_expect_failed
        )
        snapshot.match("test-connection", test_connection_response)

        def _wait_connection_status(endpoint_arn: str, replication_instance_arn: str, status: str):
            filters = [
                {"Name": "endpoint-arn", "Values": [endpoint_arn]},
                {"Name": "replication-instance-arn", "Values": [replication_instance_arn]},
            ]
            res = aws_client.dms.describe_connections(Filters=filters)
            assert res["Connections"][0]["Status"] == status
            return res

        connection_response = retry(
            lambda: _wait_connection_status(
                endpoint_arn=endpoint_arn_expect_failed,
                replication_instance_arn=instance_arn,
                status="failed",
            ),
            sleep_before=2 if is_aws_cloud() else 0,
            sleep=2 if is_aws_cloud() else 1,
            retries=50 if is_aws_cloud() else 20,
        )
        snapshot.match("describe-connection-failed", connection_response)

        # try to delete endpoint, check if connection is still there
        aws_client.dms.delete_endpoint(EndpointArn=endpoint_arn_expect_failed)

        def endpoint_deleted(arn: str):
            try:
                endpoints = aws_client.dms.describe_endpoints(
                    Filters=[{"Name": "endpoint-arn", "Values": [arn]}]
                )
                assert len(endpoints.get("Endpoints")) == 0
            except ClientError:
                return True

        # wait until endpoint is deleted
        retry(
            lambda: endpoint_deleted(endpoint_arn_expect_failed),
            retries=20 if is_aws_cloud() else 3,
            sleep_before=2,
            sleep=30 if is_aws_cloud() else 1,
        )

        filters = [{"Name": "endpoint-arn", "Values": [endpoint_arn_expect_failed]}]
        with pytest.raises(ClientError) as e:
            aws_client.dms.describe_connections(Filters=filters)

        snapshot.match("describe-connection-error", e.value.response)

    @markers.aws.validated
    def test_invalid_test_connection_settings(
        self,
        aws_client,
        snapshot,
        account_id,
        region_name,
        dms_create_replication_instance,
        dms_wait_for_replication_instance_status,
    ):
        snapshot.add_transformer(snapshot.transform.dms_api())

        non_existent_endpoint_arn = (
            f"arn:{get_partition(region_name)}:dms:{region_name}:{account_id}:endpoint:identifier"
        )
        non_existent_instance_arn = (
            f"arn:{get_partition(region_name)}:dms:{region_name}:{account_id}:rep:repidentifier"
        )
        with pytest.raises(ClientError) as e:
            aws_client.dms.test_connection(
                ReplicationInstanceArn=non_existent_instance_arn,
                EndpointArn=non_existent_endpoint_arn,
            )

        snapshot.match("test-connection-error", e.value.response)

        instance: CreateReplicationInstanceResponseTypeDef = dms_create_replication_instance(
            PubliclyAccessible=False
        )
        instance_arn = instance["ReplicationInstance"]["ReplicationInstanceArn"]
        instance_identifier = instance["ReplicationInstance"]["ReplicationInstanceIdentifier"]
        snapshot.add_transformer(snapshot.transform.regex(instance_identifier, "<instance-id>"))
        with pytest.raises(ClientError) as e:
            aws_client.dms.test_connection(
                ReplicationInstanceArn=instance_arn,
                EndpointArn=non_existent_endpoint_arn,
            )

        snapshot.match("test-connection-error-instance-not-ready", e.value.response)

        # wait until the ReplicationInstanceStatus is available
        dms_wait_for_replication_instance_status(instance_arn, "available")

        with pytest.raises(ClientError) as e:
            aws_client.dms.test_connection(
                ReplicationInstanceArn=instance_arn,
                EndpointArn=non_existent_endpoint_arn,
            )

        snapshot.match("test-connection-error-endpoint", e.value.response)

    @markers.aws.validated
    def test_delete_replication_instance_error(self, aws_client, snapshot, region_name, account_id):
        snapshot.add_transformer(snapshot.transform.dms_api())

        with pytest.raises(ClientError) as e:
            aws_client.dms.delete_replication_instance(
                ReplicationInstanceArn=f"arn:{get_partition(region_name)}:dms:{region_name}:{account_id}:rep:test-instance"
            )

        snapshot.match("delete-replication-instance-error", e.value.response)

    @markers.aws.validated
    def test_replication_task(self, aws_client, snapshot, region_name, account_id):
        snapshot.add_transformer(snapshot.transform.dms_api())
        not_existent_task_arn = (
            f"arn:{get_partition(region_name)}:dms:{region_name}:{account_id}:task:test-task"
        )
        with pytest.raises(ClientError) as e:
            aws_client.dms.delete_replication_task(ReplicationTaskArn=not_existent_task_arn)

        snapshot.match("delete-replication-task-error", e.value.response)

        with pytest.raises(ClientError) as e:
            aws_client.dms.describe_replication_tasks(
                Filters=[{"Name": "engine-version", "Values": ["kinesis"]}]
            )

        snapshot.match("delete-replication-invalid-filter", e.value.response)

        with pytest.raises(ClientError) as e:
            aws_client.dms.describe_replication_tasks(
                Filters=[{"Name": "replication-task-arn", "Values": [not_existent_task_arn]}]
            )

        snapshot.match("delete-replication-no-filter-match", e.value.response)

    @markers.aws.validated
    def test_replication_subnet_groups(self, aws_client, snapshot):
        snapshot.add_transformer(snapshot.transform.dms_api())

        # filter for non-existent subnet group
        response = aws_client.dms.describe_replication_subnet_groups(
            Filters=[
                {"Name": "replication-subnet-group-id", "Values": ["custom-subnet-group-test"]}
            ]
        )
        snapshot.match("describe-replication-subnet-groups", response)

        # delete non-existent subnet-group
        with pytest.raises(ClientError) as e:
            aws_client.dms.delete_replication_subnet_group(
                ReplicationSubnetGroupIdentifier="my-custom-nonexistent-sub-id"
            )

        snapshot.match("delete-replication-subnet-group-error", e.value.response)

        # TODO add positive test cases
        # create replication instance requires properly setup dms-vpc-role (also for negative tests)

    @markers.aws.validated
    def test_create_source_endpoint_s3_with_invalid_settings(self, aws_client, snapshot):
        with pytest.raises(ClientError) as e:
            aws_client.dms.create_endpoint(
                EndpointIdentifier=f"test-endpoint-{short_uid()}",
                EndpointType="source",
                EngineName="s3",
                # required parameters for other sources
                Password="admin",
                Username="admin",
                Port=1234,
                DatabaseName="my_db",
            )

        snapshot.match("create-endpoint-error", e.value.response)

        with pytest.raises(ClientError) as e:
            aws_client.dms.create_endpoint(
                EndpointIdentifier=f"test-endpoint-{short_uid()}",
                EndpointType="source",
                EngineName="s3",
            )

        snapshot.match("create-endpoint-error-2", e.value.response)

        with pytest.raises(ClientError) as e:
            aws_client.dms.create_endpoint(
                EndpointIdentifier=f"test-endpoint-{short_uid()}",
                EndpointType="source",
                EngineName="s3",
                MySQLSettings=MySQLSettings(
                    Username="foobar",
                    ServerName="ignored",
                ),
            )

        snapshot.match("create-endpoint-error-3", e.value.response)

        with pytest.raises(ClientError) as e:
            aws_client.dms.create_endpoint(
                EndpointIdentifier=f"test-endpoint-{short_uid()}",
                EndpointType="source",
                EngineName="s3",
                S3Settings=S3Settings(),
            )

        snapshot.match("create-endpoint-error-4", e.value.response)

        with pytest.raises(ClientError) as e:
            aws_client.dms.create_endpoint(
                EndpointIdentifier=f"test-endpoint-{short_uid()}",
                EndpointType="source",
                EngineName="s3",
                S3Settings=S3Settings(BucketName="my-bucket"),
            )

        snapshot.match("create-endpoint-error-5", e.value.response)

        with pytest.raises(ClientError) as e:
            aws_client.dms.create_endpoint(
                EndpointIdentifier=f"test-endpoint-{short_uid()}",
                EndpointType="source",
                EngineName="s3",
                S3Settings=S3Settings(
                    BucketName="my-bucket", ExternalTableDefinition=json.dumps({"TableCount": "1"})
                ),
            )
        snapshot.match("create-endpoint-error-6", e.value.response)

    @markers.aws.validated
    def test_create_basic_s3_source(
        self,
        aws_client,
        snapshot,
        dms_create_endpoint,
        create_role_with_policy_for_principal,
        s3_create_bucket,
    ):
        snapshot.add_transformer(snapshot.transform.dms_api())
        table_definition = {
            "TableCount": "1",
            "Tables": [
                {
                    "TableName": "employee",
                    "TablePath": "hr/employee/",
                    "TableOwner": "hr",
                    "TableColumns": [
                        {
                            "ColumnName": "Id",
                            "ColumnType": "INT8",
                            "ColumnNullable": "false",
                            "ColumnIsPk": "true",
                        },
                        {"ColumnName": "Name", "ColumnType": "STRING", "ColumnLength": "50"},
                    ],
                    "TableColumnsTotal": "2",
                }
            ],
        }
        role_name, role_arn = create_role_with_policy_for_principal(
            principal={"Service": "dms.amazonaws.com"},
            effect="Allow",
            actions=["*"],
            resource="*",
        )
        bucket = s3_create_bucket()
        snapshot.add_transformer(snapshot.transform.regex(bucket, "<bucket-name>"))

        def create_endpoint():
            response = dms_create_endpoint(
                EndpointIdentifier=f"test-endpoint-{short_uid()}",
                EndpointType="source",
                EngineName="s3",
                S3Settings=S3Settings(
                    BucketName=bucket,
                    ExternalTableDefinition=json.dumps(table_definition),
                    ServiceAccessRoleArn=role_arn,
                ),
            )
            return response

        endpoint = retry(
            create_endpoint,
            sleep=10 if is_aws_cloud() else 0.5,
            retries=10 if is_aws_cloud() else 2,
            sleep_before=10 if is_aws_cloud() else 0,
        )

        snapshot.match("create-s3-source-endpoint", endpoint)

        with pytest.raises(ClientError) as e:
            dms_create_endpoint(
                EndpointIdentifier=f"test-endpoint-{short_uid()}",
                EndpointType="source",
                EngineName="s3",
                S3Settings=S3Settings(
                    BucketName=bucket,
                    ExternalTableDefinition="not a json",
                    ServiceAccessRoleArn=role_arn,
                ),
            )
        snapshot.match("create-endpoint-invalid-json", e.value.response)

        # there seems to be no validation for the json pattern though:
        invalid_table_definition = dms_create_endpoint(
            EndpointIdentifier=f"test-endpoint-{short_uid()}",
            EndpointType="source",
            EngineName="s3",
            S3Settings=S3Settings(
                BucketName=bucket,
                ExternalTableDefinition='{"json": "test"}',
                ServiceAccessRoleArn=role_arn,
            ),
        )
        snapshot.match("create-endpoint-invalid-table-definition", invalid_table_definition)

    #######################################################
    # Tests currently skipped - not yet implemented on LS #
    #######################################################
    @pytest.mark.skipif(
        not is_aws_cloud(), reason="postgres source not yet implemented in LocalStack"
    )
    @markers.aws.validated
    def test_create_source_endpoint_postgres_ignores_foreign_settings(
        self, dms_create_endpoint, snapshot, aws_client
    ):
        snapshot.add_transformer(snapshot.transform.dms_api())

        # when creating an endpoint for a particular engine type, any other settings will be ignored
        endpoint = dms_create_endpoint(
            EndpointIdentifier=f"test-endpoint-{short_uid()}",
            EndpointType="source",
            EngineName="postgres",
            # required parameters
            Password="admin",
            Username="admin",
            ServerName="my-postgres-instance.example.com",
            Port=5432,
            DatabaseName="my_db",
            S3Settings=S3Settings(BucketName="foo", BucketFolder="bar"),
        )

        snapshot.match("endpoint", endpoint)

        # these assert statements are just to explain the behavior
        assert "S3Settings" not in endpoint
        assert "MySQLSettings" not in endpoint
        assert "PostgreSQLSettings" in endpoint

    @pytest.mark.skipif(
        not is_aws_cloud(), reason="postgres source not yet implemented in LocalStack"
    )
    @markers.aws.validated
    def test_create_source_endpoint_postgres_overwrites_extra_settings(
        self, dms_create_endpoint, snapshot
    ):
        snapshot.add_transformer(snapshot.transform.dms_api())

        endpoint = dms_create_endpoint(
            EndpointIdentifier=f"test-endpoint-{short_uid()}",
            EndpointType="source",
            EngineName="postgres",
            # required parameters
            Password="admin",
            Username="admin",
            ServerName="my-postgres-instance.example.com",
            Port=5432,
            DatabaseName="my_db",
            PostgreSQLSettings=PostgreSQLSettings(
                ServerName="overwritten.example.com",
                Username="foobar",
                HeartbeatEnable=True,
                MaxFileSize=1000,
            ),
        )
        snapshot.match("endpoint", endpoint)

        # these assert statements are just to explain the behavior
        # the properties of PostgreSQLSettings are overwritten from the endpoint properties
        assert endpoint["PostgreSQLSettings"]["ServerName"] == "my-postgres-instance.example.com"
        assert endpoint["PostgreSQLSettings"]["DatabaseName"] == "my_db"
        assert endpoint["PostgreSQLSettings"]["Username"] == "admin"

    @markers.aws.validated
    def test_s3_cdc_without_path(
        self,
        aws_client,
        snapshot,
        account_id,
        region_name,
        dms_create_replication_instance,
        dms_create_endpoint,
        dms_wait_for_replication_instance_status,
        create_role_with_policy_for_principal,
        s3_create_bucket,
    ):
        snapshot.add_transformer(snapshot.transform.dms_api())
        snapshot.add_transformer(
            snapshot.transform.key_value("SubnetIdentifier", reference_replacement=False),
        )
        table_definition = {
            "TableCount": "1",
            "Tables": [
                {
                    "TableName": "employee",
                    "TablePath": "hr/employee/",
                    "TableOwner": "hr",
                    "TableColumns": [
                        {
                            "ColumnName": "Id",
                            "ColumnType": "INT8",
                            "ColumnNullable": "false",
                            "ColumnIsPk": "true",
                        },
                        {"ColumnName": "Name", "ColumnType": "STRING", "ColumnLength": "50"},
                    ],
                    "TableColumnsTotal": "2",
                }
            ],
        }
        role_name, role_arn = create_role_with_policy_for_principal(
            principal={"Service": "dms.amazonaws.com"},
            effect="Allow",
            actions=["*"],
            resource="*",
        )
        bucket = s3_create_bucket()

        def _create_source_endpoint():
            response = dms_create_endpoint(
                EndpointIdentifier=f"source-endpoint-{short_uid()}",
                EndpointType="source",
                EngineName="s3",
                S3Settings=S3Settings(
                    BucketName=bucket,
                    ExternalTableDefinition=json.dumps(table_definition),
                    ServiceAccessRoleArn=role_arn,
                ),
            )
            return response

        source_endpoint = retry(
            _create_source_endpoint,
            sleep=10 if is_aws_cloud() else 0.5,
            retries=10 if is_aws_cloud() else 2,
            sleep_before=10 if is_aws_cloud() else 0,
        )

        def _create_target_endpoint():
            endpoint = dms_create_endpoint(
                EndpointIdentifier=f"target-endpoint-{short_uid()}",
                EndpointType="target",
                EngineName="kinesis",
                KinesisSettings=KinesisSettings(
                    StreamArn=f"arn:{get_partition(region_name)}:kinesis:{region_name}:{account_id}:stream/lambda-stream",
                    ServiceAccessRoleArn=role_arn,
                    MessageFormat=MessageFormatValue.json,
                ),
            )
            return endpoint

        # retry as the policy needs some time on AWS
        target_endpoint = retry(
            _create_target_endpoint,
            sleep_before=2 if is_aws_cloud() else 0,
            sleep=2 if is_aws_cloud() else 1,
            retries=20 if is_aws_cloud() else 3,
        )

        instance: CreateReplicationInstanceResponseTypeDef = dms_create_replication_instance(
            PubliclyAccessible=False
        )
        instance_arn = instance["ReplicationInstance"]["ReplicationInstanceArn"]

        # wait until the ReplicationInstanceStatus is available
        dms_wait_for_replication_instance_status(instance_arn, "available")

        table_mapping = {
            "rules": [
                {
                    "rule-type": "selection",
                    "rule-id": "1",
                    "rule-name": "rule1",
                    "object-locator": {"schema-name": "hr", "table-name": "employee"},
                    "rule-action": "include",
                }
            ]
        }

        with pytest.raises(ClientError) as e:
            aws_client.dms.create_replication_task(
                ReplicationTaskIdentifier=f"repl-task-id-{short_uid()}",
                MigrationType="cdc",
                ReplicationInstanceArn=instance_arn,
                SourceEndpointArn=source_endpoint["EndpointArn"],
                TargetEndpointArn=target_endpoint["EndpointArn"],
                TableMappings=json.dumps(table_mapping),
            )
        snapshot.match("create-replication-task-error", e.value.response)
