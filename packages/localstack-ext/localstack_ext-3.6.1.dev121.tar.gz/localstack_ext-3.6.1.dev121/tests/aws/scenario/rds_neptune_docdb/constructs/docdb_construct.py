import aws_cdk as cdk
import aws_cdk.aws_docdb as docdb
import aws_cdk.aws_ec2 as ec2
import aws_cdk.aws_lambda as awslambda
from constructs import Construct
from localstack.testing.scenario.provisioning import InfraProvisioner

LAMBDA_DOCDB_QUERY_HELPER = "docdb-lambda-helper.zip"


class DocDBConstruct(Construct):
    database_cluster: docdb.DatabaseCluster
    docdb_query_fn: awslambda.Function

    def __init__(
        self,
        stack: cdk.Stack,
        id: str,
        *,
        vpc: cdk.aws_ec2.Vpc,
    ):
        super().__init__(stack, id)
        docdb_sg = ec2.SecurityGroup(
            stack,
            "DocDBSecurityGroup",
            vpc=vpc,
            description="Allow traffic to DocDB",
            allow_all_outbound=True,  # Allows the DocDB to make outbound requests if needed
        )

        lambda_sg = ec2.SecurityGroup(
            stack,
            "LambdaSecurityGroup",
            vpc=vpc,
            description="Allow Lambda to communicate with DocDB",
            allow_all_outbound=True,  # Allows the Lambda to connect to DocDB
        )

        # Allow Lambda to connect to DocumentDB
        docdb_sg.add_ingress_rule(
            peer=lambda_sg,
            connection=ec2.Port.tcp(27017),
            description="Allow Lambda SG to connect to DocumentDB on 27017",
        )

        vpc_subnets = ec2.SubnetSelection(
            subnet_type=ec2.SubnetType.PRIVATE_WITH_NAT
        )  # Use PRIVATE for private subnets

        param_group = docdb.ClusterParameterGroup(
            stack, "ParameterGroup", family="docdb5.0", parameters={"tls": "disabled"}
        )

        self.docdb_cluster = docdb.DatabaseCluster(
            stack,
            "DocDBCluster",
            master_user=docdb.Login(
                username="myuser",  # NOTE: 'admin' is reserved by DocumentDB
            ),
            instance_type=ec2.InstanceType.of(ec2.InstanceClass.MEMORY5, ec2.InstanceSize.LARGE),
            vpc_subnets=vpc_subnets,  # Specify the subnets for the Lambda
            security_group=lambda_sg,
            vpc=vpc,
            removal_policy=cdk.RemovalPolicy.DESTROY,
            parameter_group=param_group,
        )

        bucket = cdk.aws_s3.Bucket.from_bucket_name(
            stack,
            "bucket_name_docdb",
            bucket_name=InfraProvisioner.get_asset_bucket_cdk(stack),
        )

        self.docdb_query_fn = awslambda.Function(
            stack,
            "DocDBHelperLambda",
            handler="index.handler",
            vpc=vpc,
            security_groups=[lambda_sg],
            code=awslambda.S3Code(bucket=bucket, key=LAMBDA_DOCDB_QUERY_HELPER),
            runtime=awslambda.Runtime.NODEJS_16_X,
            environment={"SECRET_NAME": self.docdb_cluster.secret.secret_arn},
        )
        self.docdb_cluster.secret.grant_read(self.docdb_query_fn)
        self.docdb_cluster.connections.allow_default_port_from_any_ipv4("Open to the world")
