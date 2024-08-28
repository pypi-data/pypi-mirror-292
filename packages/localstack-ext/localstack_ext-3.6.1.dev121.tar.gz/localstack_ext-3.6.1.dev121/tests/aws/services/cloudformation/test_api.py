import os
import re

import pytest
from localstack.testing.aws.util import is_aws_cloud
from localstack.testing.pytest import markers
from localstack.utils import testutil
from localstack.utils.strings import short_uid
from localstack_snapshot.snapshots.transformer import JsonpathTransformer

from tests.aws.services.rds.test_rds import get_availability_zones_transformer

# Handler that creates a custom CF resource
CUSTOM_RESOURCE_LAMBDA_CODE = """
def handler(event, context):
    try:
        import json, requests
        result = {
            'Status': 'SUCCESS',
            'PhysicalResourceId': 'phys-resource-123',
            'StackId': event.get('StackId'),
            'RequestId': event.get('RequestId'),
            'LogicalResourceId': event.get('LogicalResourceId'),
            'Data': {
                'OutputName1': 'Value1',
                'OutputName2': 'Value2'
            }
        }
        response_url = event['ResponseURL']
        print('CloudFormation custom resource creation Lambda - calling response URL: %s' % response_url)
        print(result)
        result = requests.put(response_url, data=json.dumps(result))
        if result.status_code >= 400:
            raise Exception('Unable to report result to S3 (%s): %s' % (result.status_code, result.content))
        return '{}'
    except Exception as e:
        import traceback
        print(e, traceback.format_exc())
        raise
"""


# TODO: aws_validate
class TestAPI:
    # TODO: make this more targeted
    @pytest.mark.skip(reason="Temporarily disabled, fix with v2!")
    @markers.only_on_amd64
    @markers.aws.unknown
    def test_create_stack(self, create_lambda_function, deploy_cfn_template, aws_client):
        client = aws_client.cloudformation
        apigw_client = aws_client.apigatewayv2
        cognito = aws_client.cognito_idp

        # create custom resource creation Lambda
        lambda_name = f"cf-func-{short_uid()}"
        libs = ["requests", "chardet", "certifi", "idna", "urllib3"]
        zip_file = testutil.create_lambda_archive(
            CUSTOM_RESOURCE_LAMBDA_CODE, get_content=True, libs=libs
        )
        create_lambda_function(func_name=lambda_name, zip_file=zip_file)
        lambda_arn = aws_client.lambda_.get_function(FunctionName=lambda_name)["Configuration"][
            "FunctionArn"
        ]

        # create stack
        deployment = deploy_cfn_template(
            template_path=os.path.join(
                os.path.dirname(__file__), "../../templates/cognito-apigw.sample.yml"
            ),
            parameters={
                "CrLambdaArn": lambda_arn,
                "AuthName": "auth1",
            },
        )
        stack_name = deployment.stack_name

        # assert created resources
        resources = client.describe_stack_resources(StackName=stack_name)["StackResources"]
        types = set([r.get("ResourceType") for r in resources])
        assert len(types) >= 5

        # assert API GW resources were created with names/references resolved properly
        functions = aws_client.lambda_.list_functions()["Functions"]
        functions = [lb for lb in functions if lb["FunctionName"] == "cf-apigwv2-lambda"]
        assert functions
        lambda_arn = functions[0]["FunctionArn"]
        apis = apigw_client.get_apis()["Items"]
        api = [a for a in apis if a["Name"] == "cf-apigwv2-lambda-api"][0]
        api_id = api["ApiId"]
        result = apigw_client.get_integrations(ApiId=api_id)["Items"]
        assert len(result) == 1
        integration = result[0]
        assert lambda_arn in integration["IntegrationUri"]
        assert "$" not in integration["IntegrationUri"]
        result = apigw_client.get_routes(ApiId=api_id)["Items"]
        assert result
        assert "$" not in result[0]["Target"]
        assert f"integrations/{integration['IntegrationId']}" == result[0]["Target"]

        # assert existence of Cognito resources
        def get_provider():
            providers = cognito.list_identity_providers(UserPoolId=pool_id)["Providers"]
            return [p for p in providers if p["ProviderName"] == "test-prov-9123"]

        pools = cognito.list_user_pools(MaxResults=100)["UserPools"]
        pool_id = [p for p in pools if p["Name"] == "auth1-user-pool"][0]["Id"]
        assert get_provider()

        # clean up
        deployment.destroy()
        with pytest.raises(Exception) as exc:
            get_provider()
        exc.match("ResourceNotFoundException")

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(
        paths=[
            "$..HomeRegion",  # missing for trait details
            "$..DBClusters..ActivityStreamStatus",
            "$..DBClusters..AssociatedRoles",
            "$..DBClusters..AutoMinorVersionUpgrade",
            "$..DBClusters..AvailabilityZones",
            "$..DBClusters..BackupRetentionPeriod",
            "$..DBClusters..ClusterCreateTime",
            "$..DBClusters..CopyTagsToSnapshot",
            "$..DBClusters..CrossAccountClone",
            "$..DBClusters..DBClusterParameterGroup",
            "$..DBClusters..DBSubnetGroup",
            "$..DBClusters..DatabaseName",
            "$..DBClusters..DeletionProtection",
            "$..DBClusters..DomainMemberships",
            "$..DBClusters..EarliestRestorableTime",
            "$..DBClusters..EngineMode",
            "$..DBClusters..EngineVersion",
            "$..DBClusters..EngineVersion",
            "$..DBClusters..HostedZoneId",
            "$..DBClusters..HttpEndpointEnabled",
            "$..DBClusters..LatestRestorableTime",
            "$..DBClusters..NetworkType",
            "$..DBClusters..PreferredBackupWindow",
            "$..DBClusters..PreferredMaintenanceWindow",
            "$..DBClusters..ReadReplicaIdentifiers",
            "$..DBClusters..TagList",
        ]
    )
    def test_create_misc_resources(
        self, deploy_cfn_template, lambda_su_role, aws_client, snapshot, cleanups
    ):
        trail_name = f"test-trail-{short_uid()}"
        func_name = f"cf-lambda-{short_uid()}"
        alias_name = f"func-alias-{short_uid()}"
        bucket_name = f"trail-bucket-{short_uid()}"

        snapshot.add_transformer(snapshot.transform.regex(trail_name, "trail_name"))
        snapshot.add_transformer(snapshot.transform.regex(func_name, "func_name"))
        snapshot.add_transformer(snapshot.transform.regex(alias_name, "alias_name"))
        snapshot.add_transformer(snapshot.transform.regex(bucket_name, "bucket_name"))
        snapshot.add_transformer(snapshot.transform.rds_api())
        snapshot.add_transformer(
            snapshot.transform.key_value("Endpoint", reference_replacement=False)
        )
        snapshot.add_transformer(
            JsonpathTransformer(
                "$..TagList..Value", replacement="<tag-value-replaced>", replace_reference=False
            )
        )
        snapshot.add_transformer(
            get_availability_zones_transformer(aws_client.sts.meta.region_name)
        )

        def _delete_objects_from_bucket():
            try:
                # need to cleanup bucket before stack can be deleted
                objs = aws_client.s3.list_objects_v2(Bucket=bucket_name)
                objs_num = objs["KeyCount"]
                if objs_num > 0:
                    obj_keys = [{"Key": o["Key"]} for o in objs["Contents"]]
                    aws_client.s3.delete_objects(Bucket=bucket_name, Delete={"Objects": obj_keys})
            except Exception:
                # bucket might not exist yet; or we already deleted files, because we use this
                # for cleanups + as part of the test
                pass

        cleanups.append(_delete_objects_from_bucket)

        stack = deploy_cfn_template(
            template_path=os.path.join(
                os.path.dirname(__file__), "../../templates/misc.resources.yml"
            ),
            parameters={
                "TrailName": trail_name,
                "FunctionName": func_name,
                "AliasName": alias_name,
                "FnRole": lambda_su_role,
                "BucketName": bucket_name,
            },
        )

        # assert existence of Cloud trails
        trails = aws_client.cloudtrail.list_trails()["Trails"]
        trails = [t for t in trails if t["Name"] == trail_name]
        snapshot.match("trail_details", trails)

        # assert existence of Lambda alias
        result = aws_client.lambda_.list_aliases(FunctionName=func_name)["Aliases"]
        assert result[0]["Name"] == alias_name
        assert f":function:{func_name}:{alias_name}" in result[0]["AliasArn"]
        snapshot.match("list_aliases", result)

        result = aws_client.rds.describe_db_clusters(
            DBClusterIdentifier=stack.outputs["RDSClusterId"]
        )
        snapshot.match("describe_db_clusters", result)

        if not is_aws_cloud():
            # verify LS specifics: make sure that DB cluster endpoint is returned properly
            assert re.match(
                r"^localhost.localstack.cloud:[0-9]+$", stack.outputs["ClusterEndpoint"]
            )

        # test that cloudtrail not available anymore after destroying
        # TODO not sure why we need to test this, maybe we can remove this at some point
        _delete_objects_from_bucket()  # need to delete objects from bucket first
        stack.destroy()
        result = [
            t for t in aws_client.cloudtrail.list_trails()["Trails"] if t["Name"] == trail_name
        ]
        assert not result
