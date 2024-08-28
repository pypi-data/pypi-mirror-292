import os
from typing import Dict

from localstack.testing.pytest import markers
from localstack.utils.strings import short_uid
from localstack_snapshot.snapshots.transformer import GenericTransformer, SortingTransformer

TEST_TEMPLATE = """
Parameters:
  BucketName:
    Type: String
Resources:
  MyBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Ref BucketName
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
                - "edgelambda.amazonaws.com"
  MyFunction:
    Type: AWS::Lambda::Function
    Properties:
      Runtime: nodejs12.x
      Role: !GetAtt MyRole.Arn
      Handler: index.handler
      Code:
        ZipFile: |
          exports.handler = (event, context) => {};
  MyFunctionVersion:
    Type: AWS::Lambda::Version
    Properties:
      FunctionName: !Ref MyFunction
  MyDistribution:
    Type: AWS::CloudFront::Distribution
    Properties:
      DistributionConfig:
        DefaultCacheBehavior:
          CachePolicyId: 658327ea-f89d-4fab-a63d-7e88639e58f6
          Compress: true
          TargetOriginId: TmpStackApiCloudFrontDistributionOrigin1D9F0BD14
          ViewerProtocolPolicy: allow-all
          LambdaFunctionAssociations:
          - EventType: origin-request
            IncludeBody: true
            LambdaFunctionARN: !Ref MyFunctionVersion
          ForwardedValues:
            Cookies:
              Forward: whitelist
              WhitelistedNames: [c1, test-cookie2]
            Headers:
              - header-1
              - test
            QueryString: true
            QueryStringCacheKeys:
              - q1
        Enabled: true
        IPV6Enabled: true
        Logging:
          Bucket: !GetAtt MyBucket.DomainName
        Origins:
        - CustomOriginConfig:
            OriginProtocolPolicy: https-only
            OriginSSLProtocols:
            - TLSv1.2
          DomainName: example.com
          Id: TmpStackApiCloudFrontDistributionOrigin1D9F0BD14
Outputs:
  DistributionId:
    Value: !Ref MyDistribution
  DomainName:
    Value:
      !GetAtt MyDistribution.DomainName
"""


def _sort_config_lists(match_key: str, config_parent_key: str, config_child_key: str):
    def _transformer(snapshot_content: Dict, *args) -> Dict:
        # TODO: replace with SortingTransformer once it supports JSON paths
        policy = snapshot_content.get(match_key)
        config = policy.get(config_parent_key, {}).get(config_child_key)
        config.pop("LastModifiedTime", None)
        paths_to_lists = (
            ("CookiesConfig", "Cookies"),
            ("HeadersConfig", "Headers"),
            ("QueryStringsConfig", "QueryStrings"),
        )
        for key1, key2 in paths_to_lists:
            if config.get(key1, {}).get(key2, {}).get("Items"):
                config[key1][key2]["Items"] = sorted(config[key1][key2]["Items"])
        return snapshot_content

    return _transformer


@markers.aws.validated
def test_cloudfront_distribution_with_logging(deploy_cfn_template, snapshot, aws_client):
    snapshot.add_transformer(snapshot.transform.cloudformation_api())
    snapshot.add_transformer(snapshot.transform.key_value("CallerReference"))
    snapshot.add_transformer(snapshot.transform.key_value("ETag"))
    snapshot.add_transformer(snapshot.transform.key_value("Bucket", reference_replacement=False))
    snapshot.add_transformer(
        snapshot.transform.key_value("DomainName", reference_replacement=False)
    )

    result = deploy_cfn_template(
        template=TEST_TEMPLATE, parameters={"BucketName": f"bucket-{short_uid()}"}, max_wait=300
    )
    snapshot.match("stack_outputs", result.outputs)

    result = aws_client.cloudfront.get_distribution(Id=result.outputs["DistributionId"])
    snapshot.match("distribution", result)


@markers.aws.validated
def test_origin_request_policies(snapshot, deploy_cfn_template, aws_client):
    template = """
Parameters:
  PolicyName:
    Type: String
Resources:
  MyPolicy:
    Type: AWS::CloudFront::OriginRequestPolicy
    Properties:
      OriginRequestPolicyConfig:
        Name: !Ref PolicyName
        Comment: test comment
        CookiesConfig:
          CookieBehavior: whitelist
          Cookies:
            - test
            - foo123
        HeadersConfig:
          HeaderBehavior: whitelist
          Headers:
            - test123
            - Content-Type
        QueryStringsConfig:
          QueryStringBehavior: whitelist
          QueryStrings:
            - xyz-123
            - foobar
Outputs:
  PolicyId:
    Value: !Ref MyPolicy
    """

    snapshot.add_transformer(snapshot.transform.cloudformation_api())
    snapshot.add_transformer(snapshot.transform.key_value("ETag"))
    snapshot.add_transformer(snapshot.transform.key_value("Name"))
    snapshot.add_transformer(snapshot.transform.key_value("PolicyId"))

    snapshot.add_transformer(
        GenericTransformer(
            _sort_config_lists(
                "origin_request_policy", "OriginRequestPolicy", "OriginRequestPolicyConfig"
            )
        )
    )

    policy_name = f"pol-{short_uid()}"
    deploy_result = deploy_cfn_template(template=template, parameters={"PolicyName": policy_name})
    snapshot.match("stack_outputs", deploy_result.outputs)

    result = aws_client.cloudfront.get_origin_request_policy(Id=deploy_result.outputs["PolicyId"])
    snapshot.match("origin_request_policy", result)


@markers.aws.validated
def test_cache_policies(snapshot, deploy_cfn_template, aws_client):
    template = """
Parameters:
  CachePolicyName:
    Type: String
Resources:
  MyCachePolicy:
    Type: AWS::CloudFront::CachePolicy
    Properties:
      CachePolicyConfig:
        Name: !Ref CachePolicyName
        DefaultTTL: 86400
        MaxTTL: 31536000
        MinTTL: 1
        ParametersInCacheKeyAndForwardedToOrigin:
          EnableAcceptEncodingGzip: true
          CookiesConfig:
            CookieBehavior: whitelist
            Cookies:
              - test
              - foo123
          HeadersConfig:
            HeaderBehavior: whitelist
            Headers:
              - test123
              - Content-Type
          QueryStringsConfig:
            QueryStringBehavior: whitelist
            QueryStrings:
              - xyz-123
              - foobar
Outputs:
  PolicyId:
    Value: !Ref MyCachePolicy
  PolicyModDate:
    Value: !GetAtt MyCachePolicy.LastModifiedTime
    """

    snapshot.add_transformer(snapshot.transform.cloudformation_api())
    snapshot.add_transformer(snapshot.transform.key_value("ETag"))
    snapshot.add_transformer(snapshot.transform.key_value("Name"))
    snapshot.add_transformer(snapshot.transform.key_value("Id"))

    snapshot.add_transformer(
        GenericTransformer(
            _sort_config_lists(
                "cache_policy", "CachePolicyConfig", "ParametersInCacheKeyAndForwardedToOrigin"
            )
        )
    )

    policy_name = f"pol-{short_uid()}"
    deploy_result = deploy_cfn_template(
        template=template, parameters={"CachePolicyName": policy_name}
    )
    snapshot.match("stack_outputs", deploy_result.outputs)

    result = aws_client.cloudfront.get_cache_policy(Id=deploy_result.outputs["PolicyId"])
    snapshot.match("cache_policy", result["CachePolicy"])


@markers.aws.validated
def test_origin_access_control(deploy_cfn_template, snapshot, aws_client):
    result = deploy_cfn_template(
        template_path=os.path.join(
            os.path.dirname(__file__), "../../../templates/cloudfront_origin_access_control.yml"
        ),
        parameters={"ConfigName": f"config{short_uid()}"},
    )
    description = aws_client.cloudformation.describe_stack_resources(StackName=result.stack_name)

    snapshot.add_transformer(snapshot.transform.key_value("OACId", "origin-access-control-id"))
    snapshot.add_transformer(snapshot.transform.cloudformation_api())
    snapshot.match("stack_outputs", result.outputs)
    snapshot.match("stack_resource_descriptions", description)


@markers.aws.validated
@markers.snapshot.skip_snapshot_verify(paths=["$..StackResources..PhysicalResourceId"])
def test_create_stack_cloudfront(deploy_cfn_template, snapshot, aws_client):
    result = deploy_cfn_template(
        template_path=os.path.join(
            os.path.dirname(__file__), "../../../templates/cloudfront.sample.yml"
        ),
        parameters={
            "ContentBucketName": f"bucket-{short_uid()}",
            "UploadBucketName": f"bucket-{short_uid()}",
        },
    )
    description = aws_client.cloudformation.describe_stack_resources(StackName=result.stack_name)

    snapshot.add_transformer(snapshot.transform.key_value("CdnDistribution"))
    snapshot.add_transformer(snapshot.transform.cloudformation_api())
    snapshot.add_transformer(
        SortingTransformer(key="StackResources", sorting_fn=lambda x: x["LogicalResourceId"])
    )

    snapshot.match("stack_outputs", result.outputs)
    snapshot.match("stack_resource_descriptions", description)
