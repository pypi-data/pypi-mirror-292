from operator import itemgetter

import aws_cdk as cdk
import pytest
from localstack.testing.pytest import markers
from localstack.testing.scenario.cdk_lambda_helper import generate_ecr_image_from_docker_image
from localstack.utils.strings import short_uid
from localstack_snapshot.snapshots.transformer import SortingTransformer


def _get_resource_name_from_arn(arn):
    return arn.split("/")[-1]


# FIXME only execute them on AMD until they are not flaky anymore
@markers.only_on_amd64
@pytest.mark.skip_store_check(reason="Skip store check for SageMakerEndpointStack tests")
class TestSageMakerEndpointStack:
    @pytest.fixture(scope="class", autouse=True)
    def infrastructure(self, infrastructure_setup, aws_client):
        infra = infrastructure_setup(namespace="SageMakerEndpointStack", force_synth=True)
        stack = cdk.Stack(infra.cdk_app, "SageMakerEndpointStack")

        repository_name = f"dummy-repository-{short_uid()}"
        infra.add_custom_setup(
            lambda: generate_ecr_image_from_docker_image(
                aws_client.ecr, repository_name, "localstack/sagemaker-dummy-byom"
            )
        )
        infra.add_custom_teardown(
            cleanup_task=lambda: aws_client.ecr.delete_repository(
                repositoryName=repository_name, force=True
            )
        )

        model_image_uri = (
            cdk.aws_ecr.Repository.from_repository_name(
                stack, "Repository", repository_name
            ).repository_uri
            + ":latest"
        )

        execution_role = cdk.aws_iam.Role(
            stack,
            "SageMakerExecutionRole",
            assumed_by=cdk.aws_iam.ServicePrincipal("sagemaker.amazonaws.com"),
            managed_policies=[
                cdk.aws_iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSageMakerFullAccess")
            ],
        )

        model = cdk.aws_sagemaker.CfnModel(
            stack,
            "Model",
            execution_role_arn=execution_role.role_arn,
            primary_container=cdk.aws_sagemaker.CfnModel.ContainerDefinitionProperty(
                image=model_image_uri,
            ),
        )

        # Create the SageMaker Endpoint Configuration
        endpoint_config = cdk.aws_sagemaker.CfnEndpointConfig(
            stack,
            "EndpointConfig",
            production_variants=[
                cdk.aws_sagemaker.CfnEndpointConfig.ProductionVariantProperty(
                    initial_instance_count=1,
                    initial_variant_weight=1.0,
                    instance_type="ml.t2.medium",
                    model_name=model.attr_model_name,
                    variant_name=model.attr_model_name,
                )
            ],
        )

        # Create the SageMaker Endpoint
        endpoint = cdk.aws_sagemaker.CfnEndpoint(
            stack,
            "Endpoint",
            endpoint_config_name=endpoint_config.attr_endpoint_config_name,
        )

        cdk.CfnOutput(stack, "ModelRef", value=model.ref)
        cdk.CfnOutput(stack, "EndpointRef", value=endpoint.ref)
        cdk.CfnOutput(stack, "EndpointConfigRef", value=endpoint_config.ref)

        with infra.provisioner() as prov:
            yield prov

    @markers.aws.validated
    def test_stack_resources_are_deployed(self, infrastructure, aws_client, snapshot):
        snapshot.add_transformer(
            snapshot.transform.key_value("PhysicalResourceId", reference_replacement=False),
            priority=-1,
        )
        snapshot.add_transformer(snapshot.transform.key_value("StackId"))
        snapshot.add_transformer(
            SortingTransformer("StackResources", itemgetter("LogicalResourceId"))
        )
        resources_description = aws_client.cloudformation.describe_stack_resources(
            StackName="SageMakerEndpointStack"
        )
        snapshot.match("stack-resources", resources_description)

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(
        paths=[
            "$..DeploymentRecommendation",
            "$..EnableNetworkIsolation",
            "$..PrimaryContainer.Mode",
        ]
    )
    def test_model_description(self, infrastructure, aws_client, snapshot):
        resource_name = _get_resource_name_from_arn(
            infrastructure.get_stack_outputs("SageMakerEndpointStack")["ModelRef"]
        )
        description = aws_client.sagemaker.describe_model(ModelName=resource_name)
        snapshot.match("model-description", description)
        snapshot.add_transformer(snapshot.transform.key_value("ExecutionRoleArn"))
        snapshot.add_transformer(snapshot.transform.key_value("ModelArn"))
        snapshot.add_transformer(snapshot.transform.key_value("ModelName"))
        snapshot.add_transformer(snapshot.transform.key_value("Image"), priority=-1)

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(paths=["$..EndpointStatus", "$..ProductionVariants"])
    def test_endpoint_description(self, infrastructure, aws_client, snapshot):
        resource_name = _get_resource_name_from_arn(
            infrastructure.get_stack_outputs("SageMakerEndpointStack")["EndpointRef"]
        )
        description = aws_client.sagemaker.describe_endpoint(EndpointName=resource_name)
        snapshot.match("endpoint-description", description)
        snapshot.add_transformer(snapshot.transform.key_value("EndpointArn"))
        snapshot.add_transformer(snapshot.transform.key_value("EndpointConfigName"))
        snapshot.add_transformer(snapshot.transform.key_value("EndpointName"))

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(paths=["$..EnableNetworkIsolation"])
    def test_endpoint_config_description(self, infrastructure, aws_client, snapshot):
        resource_name = _get_resource_name_from_arn(
            infrastructure.get_stack_outputs("SageMakerEndpointStack")["EndpointConfigRef"]
        )
        description = aws_client.sagemaker.describe_endpoint_config(
            EndpointConfigName=resource_name
        )
        snapshot.match("endpoint-config-description", description)
        snapshot.add_transformer(snapshot.transform.key_value("EndpointConfigArn"))
        snapshot.add_transformer(snapshot.transform.key_value("EndpointConfigName"))
        snapshot.add_transformer(snapshot.transform.key_value("ModelName"))
        snapshot.add_transformer(snapshot.transform.key_value("VariantName"))

    @markers.aws.validated
    def test_resource_deletion(self, infrastructure, aws_client):
        outputs = infrastructure.get_stack_outputs("SageMakerEndpointStack")

        model_name = _get_resource_name_from_arn(outputs["ModelRef"])
        endpoint_name = _get_resource_name_from_arn(outputs["EndpointRef"])
        endpoint_config_name = _get_resource_name_from_arn(outputs["EndpointConfigRef"])

        aws_client.cloudformation.delete_stack(StackName="SageMakerEndpointStack")
        aws_client.cloudformation.get_waiter("stack_delete_complete").wait(
            StackName="SageMakerEndpointStack"
        )

        with pytest.raises(aws_client.sagemaker.exceptions.ClientError):
            aws_client.sagemaker.describe_model(ModelName=model_name)
        with pytest.raises(aws_client.sagemaker.exceptions.ClientError):
            aws_client.sagemaker.describe_endpoint(EndpointName=endpoint_name)
        with pytest.raises(aws_client.sagemaker.exceptions.ClientError):
            aws_client.sagemaker.describe_endpoint_config(EndpointConfigName=endpoint_config_name)
