import os

from localstack.testing.pytest import markers
from localstack.utils.strings import short_uid


@markers.aws.validated
@markers.snapshot.skip_snapshot_verify(
    paths=[
        "$..StackId",
        "$..DriftInformation",
        "$..Metadata",
        # from the get_vpc_link call which is TODO
        "$..description",
        "$..name",
        "$..statusMessage",
        "$..tags",
        "$..targetArns",
    ]
)
def test_vpc_link(deploy_cfn_template, aws_client, snapshot):
    # Example from the documentation
    # https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-vpclink.html
    # Note: internet gateway and internet gateway attachments are not currently supported by LocalStack

    template = """
    Parameters:
        description:
            Type: String
        name:
            Type: String
        IsAWS:
            Type: String
            AllowedValues:
                - "true"
                - "false"
    Conditions:
        IsAWS: !Equals
            - !Ref IsAWS
            - "true"
    Resources:
        MyVpcLink:
            Type: AWS::ApiGateway::VpcLink
            Properties:
                Description: !Ref description
                Name: !Ref name
                TargetArns:
                   - !Ref MyLoadBalancer
        MyLoadBalancer:
                Type: AWS::ElasticLoadBalancingV2::LoadBalancer
                Properties:
                    Type: network
                    Subnets:
                       - !Ref MySubnet
        MySubnet:
            Type: AWS::EC2::Subnet
            Properties:
                VpcId: !Ref MyVPC
                CidrBlock: 10.0.0.0/24
        MyVPC:
            Type: AWS::EC2::VPC
            Properties:
                CidrBlock: 10.0.0.0/16
        MyInternetGateway:
            Type: AWS::EC2::InternetGateway
            Condition: IsAWS
        MyInternetGatewayAttachment:
            Type: AWS::EC2::VPCGatewayAttachment
            Properties:
                VpcId: !Ref MyVPC
                InternetGatewayId: !Ref MyInternetGateway
            Condition: IsAWS
    Outputs:
        VpcLinkRef:
            Value: !Ref MyVpcLink
        VpcLinkIdAttr:
            Value: !GetAtt MyVpcLink.VpcLinkId
    """
    deployment = deploy_cfn_template(
        template=template,
        parameters={
            "description": "VPC Link example",
            "name": f"vpclink-{short_uid()}",
            "IsAWS": "true" if os.getenv("TEST_TARGET") == "AWS_CLOUD" else "false",
        },
        # yes it really can take this long
        max_wait=1800 if os.getenv("TEST_TARGET") == "AWS_CLOUD" else 60,
    )
    snapshot.add_transformer(snapshot.transform.regex(deployment.stack_name, "<stack-name>"))
    snapshot.add_transformer(snapshot.transform.regex(deployment.stack_id, "<stack-id>"))
    snapshot.add_transformer(
        snapshot.transform.regex(deployment.outputs["VpcLinkRef"], "<vpclink-id>")
    )

    snapshot.match("stack-outputs", deployment.outputs)

    res = aws_client.cloudformation.describe_stack_resource(
        StackName=deployment.stack_id, LogicalResourceId="MyVpcLink"
    )["StackResourceDetail"]
    snapshot.match("describe-resource", res)

    response = aws_client.apigateway.get_vpc_link(vpcLinkId=deployment.outputs["VpcLinkRef"])
    snapshot.match("get-vpc-link", response)
