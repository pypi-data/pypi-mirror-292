from enum import Enum
from typing import Dict, Tuple

from localstack.services.apigateway.helpers import host_based_url, path_based_url
from localstack.testing.aws.util import is_aws_cloud
from localstack.utils.aws import aws_stack


def assert_response_is_200(response: Dict):
    assert_response_status(response, 200)


def assert_response_status(response: Dict, status: int):
    assert response.get("ResponseMetadata").get("HTTPStatusCode") == status


def assert_success_response_status(response: Dict):
    assert response.get("ResponseMetadata").get("HTTPStatusCode") < 400


def create_rest_api(apigateway_client, **kwargs):
    response = apigateway_client.create_rest_api(**kwargs)
    assert_response_status(response, 201)

    resources = apigateway_client.get_resources(restApiId=response.get("id"))
    root_id = next(item for item in resources["items"] if item["path"] == "/")["id"]
    return response.get("id"), response.get("name"), root_id


def get_rest_apis(apigateway_client, **kwargs):
    response = apigateway_client.get_rest_apis(**kwargs)
    assert_response_is_200(response)


def delete_rest_api(apigateway_client, **kwargs):
    response = apigateway_client.delete_rest_api(**kwargs)
    assert_success_response_status(response)


def create_rest_resource(apigateway_client, **kwargs):
    response = apigateway_client.create_resource(**kwargs)
    assert_success_response_status(response)
    return response.get("id"), response.get("parentId")


def delete_rest_resource(apigateway_client, **kwargs):
    response = apigateway_client.delete_resource(**kwargs)
    assert_response_is_200(response)


def create_rest_resource_method(apigateway_client, **kwargs):
    response = apigateway_client.put_method(**kwargs)
    assert_success_response_status(response)
    return response.get("httpMethod"), response.get("authorizerId")


def create_rest_authorizer(apigateway_client, **kwargs):
    response = apigateway_client.create_authorizer(**kwargs)
    assert_success_response_status(response)
    return response.get("id"), response.get("type")


def create_rest_api_integration(apigateway_client, **kwargs):
    response = apigateway_client.put_integration(**kwargs)
    assert_success_response_status(response)
    return response.get("uri"), response.get("type")


def create_rest_api_method_response(apigateway_client, **kwargs):
    response = apigateway_client.put_method_response(**kwargs)
    assert_success_response_status(response)
    return response.get("statusCode")


def create_rest_api_integration_response(apigateway_client, **kwargs):
    response = apigateway_client.put_integration_response(**kwargs)
    assert_success_response_status(response)
    return response.get("statusCode")


def create_domain_name(apigateway_client, **kwargs):
    response = apigateway_client.create_domain_name(**kwargs)
    assert_success_response_status(response)


def create_base_path_mapping(apigateway_client, **kwargs):
    response = apigateway_client.create_base_path_mapping(**kwargs)
    assert_success_response_status(response)
    return response.get("basePath"), response.get("stage")


def create_cognito_user_pool(cognito_idp, **kwargs):
    response = cognito_idp.create_user_pool(**kwargs)
    assert_response_is_200(response)
    return response.get("UserPool").get("Id"), response.get("UserPool").get("Arn")


def delete_cognito_user_pool(cognito_idp, **kwargs):
    response = cognito_idp.delete_user_pool(**kwargs)
    assert_response_is_200(response)


def create_cognito_user_pool_client(cognito_idp, **kwargs):
    response = cognito_idp.create_user_pool_client(**kwargs)
    assert_response_is_200(response)
    return (
        response.get("UserPoolClient").get("ClientId"),
        response.get("UserPoolClient").get("ClientName"),
    )


def create_cognito_user(cognito_idp, **kwargs):
    response = cognito_idp.sign_up(**kwargs)
    assert_response_is_200(response)


def create_cognito_sign_up_confirmation(cognito_idp, **kwargs):
    response = cognito_idp.admin_confirm_sign_up(**kwargs)
    assert_response_is_200(response)


def create_initiate_auth(cognito_idp, **kwargs):
    response = cognito_idp.initiate_auth(**kwargs)
    assert_response_is_200(response)
    return response.get("AuthenticationResult").get("IdToken")


def delete_cognito_user_pool_client(cognito_idp, **kwargs):
    response = cognito_idp.delete_user_pool_client(**kwargs)
    assert_response_is_200(response)


#
# APIv2 fixtures
#
def create_http_authorizer(apigatewayv2_client, **kwargs):
    response = apigatewayv2_client.create_authorizer(**kwargs)
    assert_success_response_status(response)
    return response.get("AuthorizerId")


def create_http_route(apigatewayv2_client, **kwargs):
    response = apigatewayv2_client.create_route(**kwargs)
    assert_success_response_status(response)
    return response.get("RouteId")


def create_http_integration(apigatewayv2_client, **kwargs):
    response = apigatewayv2_client.create_integration(**kwargs)
    assert_success_response_status(response)
    return response.get("IntegrationId")


def create_integration_response(apigatewayv2_client, **kwargs):
    response = apigatewayv2_client.create_integration_response(**kwargs)
    assert_success_response_status(response)
    return response


def update_integration_response(apigatewayv2_client, **kwargs):
    response = apigatewayv2_client.update_integration_response(**kwargs)
    assert_success_response_status(response)
    return response


def create_http_route_response(apigatewayv2_client, **kwargs):
    response = apigatewayv2_client.create_route_response(**kwargs)
    assert_success_response_status(response)
    return response.get("RouteResponseId")


def get_domain_name(apigatewayv2_client, **kwargs):
    response = apigatewayv2_client.get_domain_name(**kwargs)
    assert_response_is_200(response)
    assert response.get("DomainName") == kwargs.get("DomainName")


def create_http_domain_name(apigatewayv2_client, **kwargs):
    response = apigatewayv2_client.create_domain_name(**kwargs)
    assert_success_response_status(response)
    return response.get("DomainName")


def create_api_mapping(apigatewayv2_client, **kwargs):
    response = apigatewayv2_client.create_api_mapping(**kwargs)
    assert_success_response_status(response)
    return response.get("ApiMappingId")


def delete_http_domain_name(apigatewayv2_client, **kwargs):
    response = apigatewayv2_client.delete_domain_name(**kwargs)
    assert_success_response_status(response)


def delete_api_mapping(apigatewayv2_client, **kwargs):
    response = apigatewayv2_client.delete_api_mapping(**kwargs)
    assert_success_response_status(response)


def get_http_integrations(apigatewayv2_client, **kwargs):
    response = apigatewayv2_client.get_integrations(**kwargs)
    assert_response_is_200(response)
    return response.get("Items")


def create_import_openapi(apigatewayv2_client, **kwargs):
    response = apigatewayv2_client.import_api(**kwargs)
    assert_success_response_status(response)


def cognito_sign_up(cognito_idp_client, **kwargs):
    response = cognito_idp_client.sign_up(**kwargs)
    assert_response_is_200(response)


def cognito_confirm_admin_sign_up(cognito_idp_client, **kwargs):
    response = cognito_idp_client.admin_confirm_sign_up(**kwargs)
    assert_response_is_200(response)


def cognito_get_auth_token(cognito_idp_client, **kwargs) -> Tuple[str, str]:
    response = cognito_idp_client.initiate_auth(**kwargs)
    assert_response_is_200(response)
    auth_result = response.get("AuthenticationResult")
    return auth_result.get("IdToken"), auth_result.get("AccessToken")


def create_state_machine(stepfunctions_client, **kwargs):
    response = stepfunctions_client.create_state_machine(**kwargs)
    assert_response_is_200(response)
    return response.get("stateMachineArn")


def create_http_stage(apigatewayv2_client, **kwargs):
    response = apigatewayv2_client.create_stage(**kwargs)
    assert_success_response_status(response)
    return response.get("Stage")


def create_http_deployment(apigatevayv2_client, **kwargs):
    response = apigatevayv2_client.create_deployment(**kwargs)
    assert_success_response_status(response)
    return response.get("DeploymentId")


def create_lambda_assume_role(iam_client, **kwargs):
    response = iam_client.create_role(**kwargs)
    assert_response_is_200(response)
    return response.get("Role").get("Arn")


def delete_http_api(apigatewayv2_client, **kwargs):
    response = apigatewayv2_client.delete_api(**kwargs)
    assert_success_response_status(response)


#
# Common utilities
#


class UrlType(Enum):
    HOST_BASED = 0
    PATH_BASED = 1


def api_invoke_url(
    api_id: str, stage: str = "", path: str = "/", url_type: UrlType = UrlType.HOST_BASED
):
    path = f"/{path}" if not path.startswith("/") else path
    if is_aws_cloud():
        stage = f"/{stage}" if stage else ""
        return f"https://{api_id}.execute-api.{aws_stack.get_boto3_region()}.amazonaws.com{stage}{path}"
    if url_type == UrlType.HOST_BASED:
        return host_based_url(api_id, stage_name=stage, path=path)
    return path_based_url(api_id, stage_name=stage, path=path)
