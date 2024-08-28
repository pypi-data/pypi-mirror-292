import json
import os
import re

import pytest
from localstack.testing.pytest import markers


class TestLambdaLayer:
    @markers.aws.unknown
    def test_lambda_layer_python(self, s3_create_reusable_bucket, deploy_cfn_template, aws_client):
        # set up s3 bucket with layer content
        bucket_name, _ = s3_create_reusable_bucket()
        with open(os.path.join(os.path.dirname(__file__), "../../lambda_/layer.zip"), "rb") as f:
            aws_client.s3.upload_fileobj(Fileobj=f, Bucket=bucket_name, Key="layer.zip")

        # deploy CloudFormation template
        result = deploy_cfn_template(
            template_path=os.path.join(
                os.path.dirname(__file__), "../../../templates/lambda_layer.yaml"
            ),
            parameters={"BucketNameParam": bucket_name},
        )
        fn_name = result.outputs["LayerFunctionName"]
        layer_version_arn = result.outputs["LayerVersionArn"]
        layer_name, layer_version = layer_version_arn.split(":")[-2:]
        layer_version_result = aws_client.lambda_.get_layer_version(
            LayerName=layer_name, VersionNumber=int(layer_version)
        )
        assert (
            layer_version_result["Content"]["CodeSha256"]
            == "/o5rQHiOzOzvkuP2LZKBr7gXwZE52Dft2kbFDgzAr0s="
        )
        assert layer_version_result["Content"]["CodeSize"] == 180
        assert re.match(
            r"arn:aws:lambda:[a-z0-9-]+:\d+:layer:[^:]+", layer_version_result["LayerArn"]
        )
        assert re.match(
            r"arn:aws:lambda:[a-z0-9-]+:\d+:layer:[^:]+:\d+",
            layer_version_result["LayerVersionArn"],
        )
        assert isinstance(layer_version_result["Version"], int)
        assert layer_version_result["CompatibleRuntimes"] == ["python3.9"]

        invoke_result = aws_client.lambda_.invoke(FunctionName=fn_name)
        assert invoke_result["StatusCode"] == 200
        payload = json.load(invoke_result["Payload"])
        assert "content" in payload["data"]


@markers.only_on_amd64
@markers.aws.validated
@pytest.mark.skip(reason="Flaky, temporarily skipped")
def test_log_group_for_custom_resource_lambda(deploy_cfn_template):
    """Test creation of a custom resource using a Lambda function, as well as a log group for that Lambda.

    When testing against a larger sample app (https://workshop.serverlesscoffee.com), we've seen a
    "ResourceAlreadyExistsException" error, as the log group is being created by the invocation of the custom
    resource Lambda, and we then attempted to create it again. This test is to avoid regressions for this case.

    botocore.errorfactory.ResourceAlreadyExistsException: An error occurred (ResourceAlreadyExistsException)
        when calling the CreateLogGroup operation: The specified log group already exists
    """

    template = """
    Resources:
      MyRole:
        Type: AWS::IAM::Role
        Properties:
          AssumeRolePolicyDocument:
            Version: '2012-10-17'
            Statement:
              - Action: sts:AssumeRole
                Effect: Allow
                Principal:
                  Service:
                    - "lambda.amazonaws.com"
      MyFunction:
        Type: AWS::Lambda::Function
        Properties:
          Handler: index.handler
          Role: !GetAtt MyRole.Arn
          Runtime: python3.7
          Timeout: 10
          Code:
            ZipFile: |
              import json
              import urllib3
              http = urllib3.PoolManager()
              def handler(event, context):
                  body = {
                      'Status': 'SUCCESS',
                      'PhysicalResourceId': 'test123',
                      'StackId': event['StackId'],
                      'RequestId': event['RequestId'],
                      'LogicalResourceId': event['LogicalResourceId'],
                  }
                  http.request('PUT', event['ResponseURL'], body=json.dumps(body))
      MyLogGroup:
        Type: AWS::Logs::LogGroup
        Properties:
          LogGroupName: !Sub "/aws/lambda/${MyFunction}"
        DependsOn:
          - MyCustom
      MyCustom:
        Type: Custom::Test
        Properties:
          ServiceToken: !GetAtt MyFunction.Arn
    Outputs:
      MyLogGroup:
        Value: !Ref MyLogGroup
    """

    stack = deploy_cfn_template(template=template)
    assert stack.outputs["MyLogGroup"].startswith("/aws/lambda/")
