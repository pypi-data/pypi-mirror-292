import os
import textwrap
import time

import pytest
import requests
from localstack.testing.aws.util import is_aws_cloud
from localstack.testing.pytest import markers
from localstack.utils.strings import short_uid


class TestApiGwV2Authorizers:
    # TODO: extend with snapshot when available in -ext
    @pytest.mark.skip(reason="probably due to missing update for AWS::Apigatewayv2::Route")
    @markers.aws.validated
    def test_apigwv2_authorizer(self, deploy_cfn_template, aws_client):
        """
        Tests stack update that removes the authorizer from a route after which it should be available freely again.
        """

        # 1. deploy stack with authorizer
        stack = deploy_cfn_template(
            template_file_name="apigatewayv2_authorizer.yaml",
            template_mapping={"use_authorizer": True},
        )
        endpoint = stack.outputs["apiOutput"]
        route_id = stack.outputs["routeIdOutput"]
        api_id = stack.outputs["apiIdOutput"]

        # fallback if CFn output doesn't include protocol
        # TODO: localstack should also provide protocol for the output here
        if not endpoint.startswith("http"):
            endpoint = f"http://{endpoint}"

        route = aws_client.apigatewayv2.get_route(ApiId=api_id, RouteId=route_id)
        authorizer_id = route["AuthorizerId"]
        authorizer = aws_client.apigatewayv2.get_authorizer(
            ApiId=api_id, AuthorizerId=authorizer_id
        )

        assert authorizer["AuthorizerType"] == "JWT"
        assert authorizer["AuthorizerId"] == authorizer_id

        result = requests.get(endpoint)
        assert result.status_code == 401
        assert result.json()["message"] == "Unauthorized"

        # 2. update stack to remove authorizer
        deploy_cfn_template(
            template_file_name="apigatewayv2_authorizer.yaml",
            template_mapping={"use_authorizer": False},
            is_update=True,
        )

        time.sleep(
            2
        )  # otherwise the test against AWS is flaky. Seems some resources report their status before this is actually propagated

        with pytest.raises(aws_client.apigatewayv2.exceptions.NotFoundException):
            aws_client.apigatewayv2.get_authorizer(ApiId=api_id, AuthorizerId=authorizer_id)

        route2 = aws_client.apigatewayv2.get_route(ApiId=api_id, RouteId=route_id)
        assert route2["AuthorizationType"] == "NONE"
        assert not route2.get("AuthorizerId")

        result2 = requests.get(endpoint)
        assert result2.status_code == 200
        assert result2.text == "hello"

    @markers.aws.unknown
    def test_create_apigateway_authorizer(self, deploy_cfn_template, aws_client):
        api_name = f"api-{short_uid()}"
        deploy_cfn_template(
            template_path=os.path.join(
                os.path.dirname(__file__), "../../../templates/apigatewayv1.resources.yml"
            ),
            template_mapping={"apiName": api_name},
        )
        apis = aws_client.apigateway.get_rest_apis()["items"]
        matching = [api for api in apis if api["name"] == api_name]
        assert matching
        authorizers = aws_client.apigateway.get_authorizers(restApiId=matching[0]["id"])["items"]
        assert authorizers
        assert authorizers[0]["name"] == "TestAuthorizer"
        assert authorizers[0]["type"] == "REQUEST"

    @markers.aws.validated
    def test_apigwv2_api(self, deploy_cfn_template, aws_client):
        # 1. deploy stack
        stack = deploy_cfn_template(
            template_path=os.path.join(
                os.path.dirname(__file__),
                "../../../templates/apigatewayv2_api.yaml",
            ),
            template_mapping={"use_authorizer": True},
        )

        # check if the stack endpoint was created
        endpoint = stack.outputs["ApiEndpoint"]
        assert endpoint is not None

    @markers.aws.unknown
    def test_create_apigateway_authorizer_client_credentials(self, deploy_cfn_template, aws_client):
        result = deploy_cfn_template(
            template_path=os.path.join(
                os.path.dirname(__file__),
                "../../../templates/cognito_authorizer_client_credentials.yaml",
            )
        )

        resource_servers = aws_client.cognito_idp.list_resource_servers(
            UserPoolId=result.outputs["UserPoolId"]
        )

        assert resource_servers["ResourceServers"][0]["Name"] == "InventoryAPI"


class TestApiGwV2Apis:
    @markers.aws.unknown
    def test_create_apigatewayv2_resources(self, deploy_cfn_template, aws_client):
        # create stack
        stack = deploy_cfn_template(
            template_path=os.path.join(
                os.path.dirname(__file__), "../../../templates/apigatewayv2.sample.yml"
            )
        )

        def _check_api(expected: int):
            apis = aws_client.apigatewayv2.get_apis().get("Items", [])
            apis = [a for a in apis if a["Name"] == "test-proxy-7534"]
            assert len(apis) == expected
            return apis

        # assert API resources have been created
        api_id = _check_api(1)[0]["ApiId"]

        integrations = aws_client.apigatewayv2.get_integrations(ApiId=api_id).get("Items")
        # expecting 2 integrations - 1 defined in the CFn template, and 1 as part of "Target" API GW attribute
        assert len(integrations) == 2
        proxy_int = [r for r in integrations if r["IntegrationType"] == "AWS_PROXY"]
        assert len(proxy_int) == 2
        integration = [
            intgr for intgr in integrations if intgr["IntegrationUri"] == "http://test123"
        ]
        assert integration
        int_id = integration[0]["IntegrationId"]

        int_responses = aws_client.apigatewayv2.get_integration_responses(
            ApiId=api_id, IntegrationId=int_id
        ).get("Items")
        assert len(int_responses) == 1
        assert int_responses[0]["IntegrationResponseKey"] == "/200/"

        # destroy stack, assert that API resources have been deleted
        stack.destroy()
        _check_api(0)

    @markers.aws.unknown
    def test_api_mapping_deployment(self, deploy_cfn_template, aws_client):
        stack = deploy_cfn_template(
            template_path=os.path.join(
                os.path.dirname(__file__), "../../../templates/apigwv2_api_mapping.yml"
            ),
            parameters={"StageName": f"stage-{short_uid()}", "ApiName": f"api-{short_uid()}"},
        )

        assert aws_client.apigatewayv2.get_api_mapping(
            ApiMappingId=stack.outputs["MappingRef"], DomainName="mydomain.us-east-1.com"
        )

    @markers.snapshot.skip_snapshot_verify(paths=["$..Tags"])
    @markers.aws.validated
    def test_domain_name_attributes(self, deploy_cfn_template, snapshot, aws_client):
        snapshot.add_transformer(snapshot.transform.cloudformation_api())
        snapshot.add_transformer(snapshot.transform.key_value("HostedZoneId"))
        snapshot.add_transformer(snapshot.transform.key_value("RegionalDomainName"))
        snapshot.add_transformer(snapshot.transform.key_value("RegionalHostedZoneId"))

        template = textwrap.dedent(
            """
        AWSTemplateFormatVersion: 2010-09-09
        Parameters:
          DomainName:
            Type: String
        Resources:
          Certificate:
            Type: AWS::CertificateManager::Certificate
            Properties:
              DomainName: !Ref DomainName
              ValidationMethod: DNS
          ApiDomainName:
            Type: AWS::ApiGatewayV2::DomainName
            Properties:
              DomainName: !Ref DomainName
              DomainNameConfigurations:
                - CertificateArn: !Ref Certificate
                  EndpointType: REGIONAL
        Outputs:
          RegionalDomainName:
            Value: !Sub ${ApiDomainName.RegionalDomainName}
          RegionalHostedZoneId:
            Value: !Sub ${ApiDomainName.RegionalHostedZoneId}
        """
        )

        domain_name = f"test-{short_uid()}.localstack.cloud"
        snapshot.add_transformer(snapshot.transform.regex(domain_name, "<domain-name>"))

        # note: snapshot testing requires domain verification by adding an entry to our DNS records
        kwargs = {"max_wait": 600} if is_aws_cloud() else {}
        stack = deploy_cfn_template(
            template=template, parameters={"DomainName": domain_name}, **kwargs
        )
        snapshot.add_transformer(snapshot.transform.regex(stack.stack_name, "<stack-name>"))
        snapshot.match("stack-outputs", stack.outputs)

        domain_name = aws_client.apigatewayv2.get_domain_name(DomainName=domain_name)
        snapshot.match("domain-name", domain_name)

    @markers.aws.validated
    def test_sam_api_tagging(
        self,
        deploy_cfn_template,
        snapshot,
        aws_client,
    ):
        """
        Tests tagging of a AWS::Serverless::HttpApi resource which will create a AWS::ApiGatewayV2::Api resource

        If running on localstack we also test if setting a custom ID works
        """
        custom_id = f"mycustomid{short_uid()}"
        stack = deploy_cfn_template(
            template_path=os.path.join(
                os.path.dirname(__file__), "../../../templates/sam_api_tagging.yaml"
            ),
            parameters={"ApiGwCustomId": custom_id},
        )
        api_id = stack.outputs["MyApiId"]
        if not is_aws_cloud():
            assert api_id == custom_id

        api = aws_client.apigatewayv2.get_api(ApiId=api_id)
        assert api["Tags"]["_custom_id_"] == custom_id
