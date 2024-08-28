import json

import pytest
from botocore.exceptions import ClientError
from localstack.pro.core.aws.api.dms import KinesisSettings, MessageFormatValue, S3Settings
from localstack.testing.aws.util import is_aws_cloud
from localstack.testing.pytest import markers
from localstack.utils.strings import short_uid
from localstack.utils.sync import retry


class TestDms:
    @markers.aws.validated
    def test_invalid_source_s3(
        self,
        aws_client,
        snapshot,
        region_name,
        account_id,
        dms_create_endpoint,
        create_role_with_policy_for_principal,
        s3_create_bucket,
        dms_create_replication_config,
        partition,
    ):
        snapshot.add_transformer(snapshot.transform.dms_api())

        # create s3 source

        role_name, role_arn = create_role_with_policy_for_principal(
            principal={"Service": "dms.amazonaws.com"},
            effect="Allow",
            actions=["*"],
            resource="*",
        )
        bucket = s3_create_bucket()
        snapshot.add_transformer(snapshot.transform.regex(bucket, "<bucket-name>"))
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
        source_arn = endpoint.get("EndpointArn")

        # create target
        def _create_target_endpoint():
            endpoint = dms_create_endpoint(
                EndpointIdentifier=f"target-endpoint-{short_uid()}",
                EndpointType="target",
                EngineName="kinesis",
                KinesisSettings=KinesisSettings(
                    StreamArn=f"arn:{partition}:kinesis:{region_name}:{account_id}:stream/some-stream",
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
        snapshot.match("create-kinesis-endpoint", target_endpoint)
        target_arn = target_endpoint.get("EndpointArn")

        table_mapping = {
            "rules": [
                {
                    "rule-type": "selection",
                    "rule-id": "1",
                    "rule-name": "r1",
                    "object-locator": {"schema-name": "data", "table-name": "%"},
                    "rule-action": "include",
                }
            ]
        }
        with pytest.raises(ClientError) as e:
            dms_create_replication_config(
                SourceEndpointArn=source_arn,
                TargetEndpointArn=target_arn,
                ReplicationType="full-load",
                TableMappings=json.dumps(table_mapping),
                ComputeConfig={"MaxCapacityUnits": 1},
            )
        snapshot.match("invalid-replication-config", e.value.response)
