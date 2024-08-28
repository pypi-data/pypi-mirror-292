import aws_cdk as cdk
import aws_cdk.aws_lambda as awslambda
import aws_cdk.aws_rds as rds
from constructs import Construct
from localstack.testing.scenario.provisioning import InfraProvisioner

LAMBDA_RDS_QUERY_HELPER = "rds-lambda-helper.zip"


class AuroraPostgresConstruct(Construct):
    database_cluster: rds.DatabaseCluster
    rds_query_fn: awslambda.Function

    def __init__(
        self,
        stack: cdk.Stack,
        id: str,
        *,
        vpc: cdk.aws_ec2.Vpc,
    ):
        super().__init__(stack, id)

        engine = rds.DatabaseClusterEngine.aurora_postgres(
            version=rds.AuroraPostgresEngineVersion.VER_15_2
        )  # noqa

        parameter_group = rds.ParameterGroup(
            stack,
            "parameterGroup",
            engine=engine,
            parameters={
                "shared_preload_libraries": "pg_stat_statements,pg_tle",
            },
        )

        # Regression scenario test for GH issue https://github.com/localstack/localstack/issues/6748
        self.database_cluster = rds.DatabaseCluster(
            stack,
            "auroraCluster",
            engine=engine,
            parameter_group=parameter_group,
            vpc=vpc,
            writer=rds.ClusterInstance.serverless_v2("writer"),
            readers=[rds.ClusterInstance.serverless_v2("reader", scale_with_writer=True)],
            serverless_v2_min_capacity=0.5,
            serverless_v2_max_capacity=1,
            default_database_name="defaultDatabaseName",
            credentials=rds.Credentials.from_username(username="username"),
            removal_policy=cdk.RemovalPolicy.DESTROY,
        )

        bucket = cdk.aws_s3.Bucket.from_bucket_name(
            stack,
            "bucket_name",
            bucket_name=InfraProvisioner.get_asset_bucket_cdk(stack),
        )

        self.rds_query_fn = awslambda.Function(
            stack,
            "RDSHelperLambda",
            handler="index.handler",
            vpc=vpc,
            code=awslambda.S3Code(bucket=bucket, key=LAMBDA_RDS_QUERY_HELPER),
            runtime=awslambda.Runtime.PYTHON_3_10,
            environment={"RDS_SECRET": self.database_cluster.secret.secret_arn},
        )
        self.database_cluster.secret.grant_read(self.rds_query_fn)
        self.database_cluster.connections.allow_default_port_from_any_ipv4("Open to the world")
