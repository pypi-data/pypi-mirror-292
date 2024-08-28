import json

import requests
from localstack import config
from localstack.utils.strings import short_uid

from tests.aws.services.apigateway.apigateway_fixtures import api_invoke_url


def test_apigateway_get_api_and_authorizer(persistence_validations, snapshot, aws_client):
    rest_api_name = f"api-name-{short_uid()}"
    rest_api_id = aws_client.apigateway.create_rest_api(name=rest_api_name)["id"]

    authorizer_id = aws_client.apigateway.create_authorizer(
        restApiId=rest_api_id, name=f"id-{short_uid()}", type="TOKEN"
    )["id"]

    def validate():
        snapshot.match("get_rest_api", aws_client.apigateway.get_rest_api(restApiId=rest_api_id))
        snapshot.match(
            "get_authorizer",
            aws_client.apigateway.get_authorizer(restApiId=rest_api_id, authorizerId=authorizer_id),
        )

    persistence_validations.register(validate)


def test_apigateway_restore_routes(persistence_validations, snapshot, aws_client):
    rest_api_name = f"api-name-{short_uid()}"
    rest_api_id = aws_client.apigateway.create_rest_api(name=rest_api_name)["id"]

    root_rest_api_resource = aws_client.apigateway.get_resources(restApiId=rest_api_id)
    root_id = root_rest_api_resource["items"][0]["id"]

    resource = aws_client.apigateway.create_resource(
        restApiId=rest_api_id, parentId=root_id, pathPart="test"
    )
    resource_id = resource["id"]

    response_template_get = {"statusCode": 200, "message": "Restored"}
    _create_mock_integration_with_200_response_template(
        aws_client, rest_api_id, resource_id, "GET", response_template_get
    )

    stage_name = "dev"
    aws_client.apigateway.create_deployment(restApiId=rest_api_id, stageName=stage_name)

    def validate():
        # TODO: this is needed to first load the provider. Maybe those routes should always be loaded and load the
        # provider if hit
        aws_client.apigateway.get_rest_apis()
        url = api_invoke_url(rest_api_id, stage_name, path="/test")
        req = requests.get(url, verify=False)
        assert req.ok
        assert req.json()["message"] == "Restored"

    persistence_validations.register(validate)


def test_apigateway_restore_custom_domain_routes(persistence_validations, snapshot, aws_client):
    rest_api_name = f"api-name-{short_uid()}"
    rest_api_id = aws_client.apigateway.create_rest_api(name=rest_api_name)["id"]

    root_rest_api_resource = aws_client.apigateway.get_resources(restApiId=rest_api_id)
    root_id = root_rest_api_resource["items"][0]["id"]

    resource = aws_client.apigateway.create_resource(
        restApiId=rest_api_id, parentId=root_id, pathPart="test"
    )
    resource_id = resource["id"]

    response_template_get = {"statusCode": 200, "message": "Restored"}
    _create_mock_integration_with_200_response_template(
        aws_client, rest_api_id, resource_id, "GET", response_template_get
    )

    domain_name = "test.example.com"
    base_path = "my-api"
    stage_name = "dev"
    aws_client.apigateway.create_deployment(restApiId=rest_api_id, stageName=stage_name)

    aws_client.apigateway.create_domain_name(domainName=domain_name)
    aws_client.apigateway.create_base_path_mapping(
        domainName=domain_name,
        basePath=base_path,
        restApiId=rest_api_id,
        stage=stage_name,
    )

    def validate():
        # TODO: this is needed to first load the provider. Maybe those routes should always be loaded and load the
        # provider if hit
        aws_client.apigateway.get_rest_apis()
        # url = api_invoke_url(rest_api_id, stage_name, path="/test")
        url = f"{config.external_service_url(protocol='http')}/{base_path}/test"
        req = requests.get(url, headers={"Host": domain_name}, verify=False)
        assert req.ok
        assert req.json()["message"] == "Restored"

    persistence_validations.register(validate)


def _create_mock_integration_with_200_response_template(
    client, api_id: str, resource_id: str, http_method: str, response_template: dict
):
    client.apigateway.put_method(
        restApiId=api_id,
        resourceId=resource_id,
        httpMethod=http_method,
        authorizationType="NONE",
    )

    client.apigateway.put_method_response(
        restApiId=api_id,
        resourceId=resource_id,
        httpMethod=http_method,
        statusCode="200",
    )

    client.apigateway.put_integration(
        restApiId=api_id,
        resourceId=resource_id,
        httpMethod=http_method,
        type="MOCK",
        requestTemplates={"application/json": '{"statusCode": 200}'},
    )

    client.apigateway.put_integration_response(
        restApiId=api_id,
        resourceId=resource_id,
        httpMethod=http_method,
        statusCode="200",
        selectionPattern="",
        responseTemplates={"application/json": json.dumps(response_template)},
    )
