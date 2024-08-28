import os

import pytest
from localstack.testing.pytest import markers
from localstack.utils.strings import short_uid


@pytest.fixture
def eks_snapshot_transforms(snapshot):
    snapshot.add_transformer(
        snapshot.transform.key_value("endpoint", "<endpoint>", reference_replacement=False)
    )
    snapshot.add_transformer(
        snapshot.transform.key_value("issuer", "<issuer>", reference_replacement=False)
    )
    snapshot.add_transformer(
        snapshot.transform.key_value(
            "clusterSecurityGroupId", "<sec-group-id>", reference_replacement=False
        )
    )
    snapshot.add_transformer(
        snapshot.transform.key_value("issuer", "<issuer>", reference_replacement=False)
    )
    snapshot.add_transformer(
        snapshot.transform.key_value(
            "certificateAuthority", "<cert-auth>", reference_replacement=False
        )
    )
    snapshot.add_transformer(snapshot.transform.key_value("roleArn", reference_replacement=False))

    # this is unfortunately not deterministic. can be either eks.6 or eks.5 right now
    snapshot.add_transformer(
        snapshot.transform.key_value(
            "platformVersion", "<platform-version>", reference_replacement=False
        )
    )


@markers.snapshot.skip_snapshot_verify(
    paths=[
        "$..cluster.certificateAuthority",
        "$..cluster.endpoint",
        "$..cluster.kubernetesNetworkConfig",
        "$..cluster.logging",
        "$..cluster.platformVersion",
        "$..cluster.resourcesVpcConfig.clusterSecurityGroupId",
        "$..cluster.resourcesVpcConfig.vpcId",
        "$..cluster.status",
        "$..cluster.tags",
        "$..cluster.version",
        "$..fargateProfile..labels",
    ]
)
@markers.aws.validated
def test_eks_fargate_cluster(deploy_cfn_template, eks_snapshot_transforms, snapshot, aws_client):
    """creates an EKS cluster + fargate profile + required secondary resources (vpc, subnets, role)"""

    deployment = deploy_cfn_template(
        template_path=os.path.join(
            os.path.dirname(__file__), "../../../templates/eks_cluster.yaml"
        ),
        max_wait=60 * 30,  # on AWS this might take a long time!
    )

    stack_id_uuid = deployment.stack_id.split("/")[-1]
    cluster_name = deployment.outputs["ClusterName"]
    fargateprofile_id = deployment.outputs["FargateProfilePhysicalId"]

    describe_cluster_response = aws_client.eks.describe_cluster(name=cluster_name)
    fargateprofile_name = fargateprofile_id.split("|")[1]
    assert fargateprofile_id.split("|")[0] == cluster_name

    fargate_profile = aws_client.eks.describe_fargate_profile(
        clusterName=cluster_name, fargateProfileName=fargateprofile_name
    )
    arn_uuid = fargate_profile["fargateProfile"]["fargateProfileArn"].split("/")[-1]

    snapshot.match("stack_outputs", deployment.outputs)
    snapshot.match("describe_cluster", describe_cluster_response)
    snapshot.match("fargate_profile", fargate_profile)

    snapshot.add_transformer(snapshot.transform.regex(stack_id_uuid, "<stack-uuid>"))
    snapshot.add_transformer(
        snapshot.transform.regex(deployment.outputs["PodExecutionRole"], "<pod-role-name>")
    )

    snapshot.add_transformer(snapshot.transform.regex(deployment.outputs["VpcId"], "<vpc-id>"))
    snapshot.add_transformer(
        snapshot.transform.regex(deployment.outputs["Subnet1Id"], "<subnet1-id>")
    )
    snapshot.add_transformer(
        snapshot.transform.regex(deployment.outputs["Subnet2Id"], "<subnet2-id>")
    )
    snapshot.add_transformer(
        snapshot.transform.regex(deployment.outputs["PrivateSubnetId"], "<private-subnet-id>")
    )
    snapshot.add_transformer(snapshot.transform.regex(cluster_name, "<cluster-name>"))
    snapshot.add_transformer(
        snapshot.transform.regex(fargateprofile_name, "<fargate-profile-name>")
    )
    snapshot.add_transformer(snapshot.transform.regex(deployment.stack_name, "<stack-name>"))
    snapshot.add_transformer(snapshot.transform.regex(arn_uuid, "<fargate-profile-uuid>"))

    deployment.destroy()
    with pytest.raises(aws_client.eks.exceptions.ResourceNotFoundException):
        aws_client.eks.describe_cluster(name=cluster_name)


@markers.snapshot.skip_snapshot_verify(
    paths=[
        "$..SecurityGroup",
        "$..ServiceRoleARN",
        "$..NodeGroupId",
    ]
)
@markers.aws.validated
def test_eksctl_stack(deploy_cfn_template, aws_client, eks_snapshot_transforms, snapshot):
    # deploy the first stack
    cluster_name = f"cluster-{short_uid()}"
    stack = deploy_cfn_template(
        template_path=os.path.join(
            os.path.dirname(__file__), "../../../templates/k8s_ingress.json"
        ),
        max_wait=1800,
        parameters={"ClusterName": cluster_name},
    )

    # ordering is important here
    for key in [
        "NodeGroupId",
        "ServiceRoleARN",
        "ARN",
        "CertificateAuthorityData",
        "ClusterSecurityGroupId",
        "ClusterStackName",
        "ClusterName",
        "Endpoint",
        "SharedNodeSecurityGroup",
        "SubnetsPrivate",
        "SubnetsPublic",
        "SecurityGroup",
        "VPC",
    ]:
        snapshot.add_transformer(snapshot.transform.key_value(key, reference_replacement=True))

    snapshot.match("outputs", stack.outputs)

    # get the value used in the second stack
    cluster_security_group_id = stack.outputs["ClusterSecurityGroupId"]
    subnets = stack.outputs["SubnetsPrivate"]

    # and the second stack
    stack2 = deploy_cfn_template(
        template_path=os.path.join(
            os.path.dirname(__file__), "../../../templates/k8s_ingress_2.json"
        ),
        max_wait=1800,
        parameters={
            "SecurityGroupId": cluster_security_group_id,
            "ClusterName": cluster_name,
            "Subnets": subnets,
        },
    )

    snapshot.match("outputs2", stack2.outputs)
