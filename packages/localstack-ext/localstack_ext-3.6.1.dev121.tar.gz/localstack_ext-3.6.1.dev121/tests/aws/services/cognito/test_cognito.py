import base64
import json
import logging
import re
import socket
import textwrap
import time
import urllib.parse
from operator import itemgetter
from typing import Callable, Dict, List, Tuple
from unittest import mock
from urllib.parse import parse_qs, urlparse

import aws_cdk as cdk
import boto3
import jwt
import pyotp
import pytest
import requests
import werkzeug
from botocore.exceptions import ClientError
from localstack import config, constants
from localstack.aws.api.lambda_ import Runtime
from localstack.aws.connect import connect_to
from localstack.constants import (
    PATH_USER_REQUEST,
)
from localstack.pro.core.bootstrap.email_utils import SENT_EMAILS
from localstack.pro.core.services.cognito_idp import cognito_triggers, cognito_utils
from localstack.pro.core.services.cognito_idp.cognito_triggers import (
    TRIGGER_ADMIN_CREATE_USER,
    TRIGGER_AUTH_CREATE_CHALL,
    TRIGGER_AUTH_DEFINE_CHALL,
    TRIGGER_AUTH_VERIFY_CHALL,
    TRIGGER_SIGNUP,
    TRIGGER_TOKEN_AUTH,
)
from localstack.pro.core.services.cognito_idp.cognito_utils import get_token_claims
from localstack.pro.core.services.cognito_idp.provider import (
    COOKIE_TOKEN,
    saml_request_id_to_params,
)
from localstack.pro.core.utils.crypto import decrypt_via_aws_encryption_sdk
from localstack.testing.aws.util import is_aws_cloud
from localstack.testing.config import TEST_AWS_ACCESS_KEY_ID
from localstack.testing.pytest import markers
from localstack.testing.snapshots.transformer_utility import PATTERN_UUID
from localstack.utils import testutil
from localstack.utils.aws import arns
from localstack.utils.aws.request_context import mock_aws_request_headers
from localstack.utils.collections import remove_attributes, select_attributes
from localstack.utils.json import json_safe
from localstack.utils.strings import short_uid, to_bytes, to_str
from localstack.utils.sync import retry
from localstack.utils.time import now_utc
from localstack.utils.urls import localstack_host
from localstack_snapshot.snapshots.transformer import JsonpathTransformer, SortingTransformer
from requests_aws4auth import AWS4Auth
from warrant import aws_srp
from werkzeug import Response

from tests.aws.fixtures import UserPoolAndClient
from tests.aws.services.apigateway.apigateway_fixtures import api_invoke_url

LOG = logging.getLogger(__name__)

# TODO remove resource names from here, create random names in test methods directly
TEST_STAGE_NAME = "stage1"
TEST_PATH = "/test"
TEST_PASSWORD = "Test123!"

LAMBDA_TEST_ECHO = """
import json
def handler(event, context):
    # Just print the event that was passed to the Lambda
    json_event = json.dumps(event)
    print(json_event)
    return {
        "body": json_event,
        "statusCode": 200
    }
"""

LAMBDA_TEST = """
import json
def handler(event, context, *args):
    id = context.identity
    id = {'cognito_identity_id': id.cognito_identity_id, 'cognito_identity_pool_id': id.cognito_identity_pool_id}
    body = {'context': {'identity': id}}
    return {
        'body': json.dumps(body),
        'statusCode': 200
    }
"""

CHALLENGE_ANSWER = "resp456"

LAMBDA_TRIGGER_PRE_TOKEN_V2 = """
import json
def handler(event, *args):
    event_orig = json.loads(json.dumps(event))
    trigger, response, request = event['triggerSource'], event['response'], event['request']
    print(event_orig)

    response["claimsAndScopeOverrideDetails"] = {
        "idTokenGeneration": {
            "claimsToAddOrOverride": {
                "family_name": "Doe",
                "website": "https://localstack.cloud"
            },
            "claimsToSuppress": ["email", "phone_number"]
        },
        "accessTokenGeneration": {
            "claimsToAddOrOverride": {
                "nickname": "pikachu"
            },
            "claimsToSuppress": ["string", "string"],
            "scopesToAdd": ["openid", "email"],
            "scopesToSuppress": ["phone_number"]
        },
    }
    return event
"""

LAMBDA_TRIGGERS = """
import boto3, json
def handler(event, *args):
    event_orig = json.loads(json.dumps(event))
    print(event, args)
    trigger, response, request = event['triggerSource'], event['response'], event['request']
    user_attrs = request.get('userAttributes', {})
    username = event.get('userName')
    if trigger == 'PreSignUp_SignUp':
        assert user_attrs.get('cognito:user_status') != 'CONFIRMED'
        response['autoConfirmUser'] = 'autoconfirm' in username
    elif trigger == 'PostConfirmation_ConfirmSignUp':
        # no additional information should be returned, to avoid "Unrecognizable lambda output" error
        pass
    elif trigger == 'PreAuthentication_Authentication':
        if request.get('userNotFound') or user_attrs.get('cognito:username') == 'invalid-user':
            raise Exception('Unauthorized - invalid user')
    elif trigger == 'CustomMessage_ForgotPassword':
        response['emailSubject'] = 'Test email subject'
        response['emailMessage'] = 'Body: %s %s' % (request['usernameParameter'], request['codeParameter'])
    elif trigger == 'TokenGeneration_Authentication':
        response['claimsOverrideDetails'] = {
            'claimsToAddOrOverride': {'add_attr1': 'value1'},
            'claimsToSuppress': ['username', 'client_id'],
            'groupOverrideDetails': {
                'groupsToOverride': ['group1', 'group2']
            }
        }
    elif trigger == 'TokenGeneration_RefreshTokens':
        response['claimsOverrideDetails'] = {
            'claimsToAddOrOverride': {'add_attr2': 'value2'},
            'claimsToSuppress': ['username']
        }
    elif trigger == 'DefineAuthChallenge_Authentication':
        response['failAuthentication'] = False
        session = request.get("session", [])
        matching = [s for s in session if s["challengeName"] == "CUSTOM_CHALLENGE" and s["challengeResult"]]
        response['issueTokens'] = bool(matching)
        response['challengeName'] = 'CUSTOM_CHALLENGE' if not matching else None
    elif trigger == 'CreateAuthChallenge_Authentication':
        response['publicChallengeParameters'] = {'code': 'code123'}
        response['privateChallengeParameters'] = {'answer': '<challenge_answer>'}
    elif trigger == 'VerifyAuthChallengeResponse_Authentication':
        response['answerCorrect'] = (request['privateChallengeParameters']['answer'] == request['challengeAnswer'])
    elif trigger == 'UserMigration_Authentication':
        username = event['userName']
        if '-error' in username or 'invalid-' in username:
            raise Exception("Simulated exception - this is intended")
        response['userAttributes'] = {
            'email': username if '@' in username else 'test-trigger@example.com',
            'email_verified': 'true'
        }
        if "user-defined" in username:
            response['userAttributes']["username"] = "lambda-defined-username"
            # we are using the password to pass the type of the user pool aliases
            if 'alias_type' in request.get('validationData', {}):
                alias_type = request['validationData']['alias_type']
                response['userAttributes'][alias_type] = username

        response['finalUserStatus'] = 'CONFIRMED'
        response['messageAction'] = 'SUPPRESS'
    elif trigger == 'CustomMessage_AdminCreateUser':
        response['emailSubject'] = 'Test email subject'
        response['emailMessage'] = 'Body message'

    # send message to SQS for later inspection and assertions
    import os
    sqs_client = boto3.client("sqs", endpoint_url=os.environ.get("AWS_ENDPOINT_URL"))
    message = {"req": event_orig, "res": response}
    sqs_client.send_message(QueueUrl="<sqs_url>", MessageBody=json.dumps(message), MessageGroupId="1")

    return event
""".replace("<challenge_answer>", CHALLENGE_ANSWER)

COGNITO_AUTH_POLICY_DOC = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "mobileanalytics:PutEvents",
                "cognito-sync:*",
                "cognito-identity:*",
                "execute-api:Invoke",
                "lambda:InvokeFunction",
            ],
            "Resource": ["*"],
        }
    ],
}

COGNITO_ASSUME_ROLE_POLICY = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {"Federated": "cognito-identity.amazonaws.com"},
            "Action": "sts:AssumeRoleWithWebIdentity",
            "Condition": {
                "ForAnyValue:StringLike": {"cognito-identity.amazonaws.com:amr": "authenticated"},
            },
        }
    ],
}


def clean_trigger_logs(logs: str) -> dict:
    logs = (
        logs.replace("'", '"')
        .replace("None", "null")
        .replace("True", "true")
        .replace("False", "false")
    )
    return json.loads(logs)


@pytest.fixture
def saml_metadata_server(httpserver):
    # this is the XML content returned by a real SAML identity provider metadata endpoint (auth0)
    expected_xml = textwrap.dedent(
        """
        <EntityDescriptor entityID="urn:dev-cc74fjl4w46udioq.us.auth0.com" xmlns="urn:oasis:names:tc:SAML:2.0:metadata">
          <IDPSSODescriptor protocolSupportEnumeration="urn:oasis:names:tc:SAML:2.0:protocol">
            <KeyDescriptor use="signing">
              <KeyInfo xmlns="http://www.w3.org/2000/09/xmldsig#">
                <X509Data>
                  <X509Certificate>MIIDHTCCAgWgAwIBAgIJQGx08Hlrv/MpMA0GCSqGSIb3DQEBCwUAMCwxKjAoBgNVBAMTIWRldi1jYzc0ZmpsNHc0NnVkaW9xLnVzLmF1dGgwLmNvbTAeFw0yMzA2MjYxNDE0MDhaFw0zNzAzMDQxNDE0MDhaMCwxKjAoBgNVBAMTIWRldi1jYzc0ZmpsNHc0NnVkaW9xLnVzLmF1dGgwLmNvbTCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBAKpjXGcMCGvWj2MsNoDCvHVY9V+Ni+sB9bY7H4TAsk+HkjgwZO8rIy1hRVmEy0JQndgmbDxNl5ulBeLutqryDL8Xqoou5nt0S1mwNZMSeMoEdqSxBUbVeb4l10ww7YfOUB4wex7NALQo3UFnWTFOuZn3VQF70wHgdmfmuuqaKvsmTyFP3mIyjyCv06p151JYCw1/sGYB4exRummbOb7hKU9mrlDG5rso1StYX6OwUxc/ezcYDRPZYG12P18/PR606rGoa7pUZtUeuz5Ad4ddIWMXH1j2OPYISxd+tisWbW4OOmBDs4cftgFeEvP9a5NfSbigXQSbuc5SNuzO7rEPUksCAwEAAaNCMEAwDwYDVR0TAQH/BAUwAwEB/zAdBgNVHQ4EFgQUzt+/ZYUPg3g56C04LKPddWLswmowDgYDVR0PAQH/BAQDAgKEMA0GCSqGSIb3DQEBCwUAA4IBAQARtsmdrw0a/B46ZW2802omEM+cNlSrdfszzgyCKqRFRk3E4LsJdVROiKwYsmLbCGdlM7MoUwj7SHTQsyyCOAHffpOPyVKaylx2XHovy2UN1nC9dKvEKMnPh+1VYn29hkk74KgCB1VKhLbbefzDxQTK+nsQ+HQW91ib2SgNDgsx3+msm+jYBI3ALdcXS58cFGlLD3CQo2KL0VlazGI1No5B2HOC4UT1bD4KN72HS81epkm2PxmkA1sNH8pE7m7Us2jgrcSjlQfwBTNdVEn8qWvfTlhRkiWi+Agf8pIIkUTKzEG+HRlv0I6S8lI4EuCG5Z/MaF62bMyaFQWs/0oIfLbw</X509Certificate>
                </X509Data>
              </KeyInfo>
            </KeyDescriptor>
            <SingleLogoutService Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect" Location="https://dev-cc74fjl4w46udioq.us.auth0.com/samlp/oZKJafsuwHoLkY9dNhzoQg4us6ML9L9j/logout"/>
            <SingleLogoutService Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST" Location="https://dev-cc74fjl4w46udioq.us.auth0.com/samlp/oZKJafsuwHoLkY9dNhzoQg4us6ML9L9j/logout"/>
            <NameIDFormat>urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress</NameIDFormat>
            <NameIDFormat>urn:oasis:names:tc:SAML:2.0:nameid-format:persistent</NameIDFormat>
            <NameIDFormat>urn:oasis:names:tc:SAML:2.0:nameid-format:transient</NameIDFormat>
            <SingleSignOnService Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect" Location="https://dev-cc74fjl4w46udioq.us.auth0.com/samlp/oZKJafsuwHoLkY9dNhzoQg4us6ML9L9j"/>
            <SingleSignOnService Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST" Location="https://dev-cc74fjl4w46udioq.us.auth0.com/samlp/oZKJafsuwHoLkY9dNhzoQg4us6ML9L9j"/>
            <Attribute Name="http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri" FriendlyName="E-Mail Address" xmlns="urn:oasis:names:tc:SAML:2.0:assertion"/>
            <Attribute Name="http://schemas.xmlsoap.org/ws/2005/05/identity/claims/givenname" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri" FriendlyName="Given Name" xmlns="urn:oasis:names:tc:SAML:2.0:assertion"/>
            <Attribute Name="http://schemas.xmlsoap.org/ws/2005/05/identity/claims/name" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri" FriendlyName="Name" xmlns="urn:oasis:names:tc:SAML:2.0:assertion"/>
            <Attribute Name="http://schemas.xmlsoap.org/ws/2005/05/identity/claims/surname" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri" FriendlyName="Surname" xmlns="urn:oasis:names:tc:SAML:2.0:assertion"/>
            <Attribute Name="http://schemas.xmlsoap.org/ws/2005/05/identity/claims/nameidentifier" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri" FriendlyName="Name ID" xmlns="urn:oasis:names:tc:SAML:2.0:assertion"/>
          </IDPSSODescriptor>
        </EntityDescriptor>
        """
    )

    def _handler(*args):
        return Response(
            expected_xml,
            status=200,
            headers={"Content-Type": "application/xml"},
        )

    httpserver.expect_request("/metadata").respond_with_handler(_handler)
    http_endpoint = httpserver.url_for("/metadata")
    return http_endpoint


@pytest.fixture
def saml_response():
    # fake url for login tha triggers a POST request to saml2/idpresponse with a SAMLResponse
    xml_saml_response = textwrap.dedent(
        """
        <samlp:Response xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol"
                        ID="_f42f69fd86ac873403e7"
                        InResponseTo="{request_id}"
                        Version="2.0"
                        IssueInstant="2024-03-12T20:53:05.223Z"
                        Destination="https://localstack-staging.auth.eu-central-1.amazoncognito.com/saml2/idpresponse"
                        >
            <saml:Issuer xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion">urn:dev-cc74fjl4w46udioq.us.auth0.com</saml:Issuer>
            <samlp:Status>
                <samlp:StatusCode Value="urn:oasis:names:tc:SAML:2.0:status:Success" />
            </samlp:Status>
            <saml:Assertion xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion"
                            Version="2.0"
                            ID="_P3oonoH5X35ou5MiOmyDlmNLx4G9Ml3U"
                            IssueInstant="2024-03-12T20:53:05.219Z"
                            >
                <saml:Issuer>urn:dev-cc74fjl4w46udioq.us.auth0.com</saml:Issuer>
                <Signature xmlns="http://www.w3.org/2000/09/xmldsig#">
                    <SignedInfo>
                        <CanonicalizationMethod Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#" />
                        <SignatureMethod Algorithm="http://www.w3.org/2001/04/xmldsig-more#rsa-sha256" />
                        <Reference URI="#_P3oonoH5X35ou5MiOmyDlmNLx4G9Ml3U">
                            <Transforms>
                                <Transform Algorithm="http://www.w3.org/2000/09/xmldsig#enveloped-signature" />
                                <Transform Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#" />
                            </Transforms>
                            <DigestMethod Algorithm="http://www.w3.org/2001/04/xmlenc#sha256" />
                            <DigestValue>vRgnG/RYBl9OMFvO84DqNxnP09IwCS94H9EyQ90T3z4=</DigestValue>
                        </Reference>
                    </SignedInfo>
                    <SignatureValue>JFc7llMVQgha9FCMvO7Yg0UMzd8n6XNqQGj9JVvcLZXggRfuTX4ZtjM4d+ne3maTuHx78KEEClhF7a7GXsU84B1WllJJgAwYxX5eYpNb582RshtRid2iwlRJhZorFvoFreVSWLF8hSgGswRox+tHAZrFfGYKvXnTirttU2zEAyyKuxoCQDTZnNhKuYGsGf40YyaDMFkJJ57p+QrhEO2Nm4VPKG4SeOlPqDJrfFuMQyMu8+B1ZiqzvsrAGXwgniUxtoQ/KO/iBchnLjssWDO/DTgZfj9MpqKRsgImq6y7nC7nHqtzcOjl7rPP7ed1NdIa4YRDg7XKMh8/zK2oquSYTg==</SignatureValue>
                    <KeyInfo>
                        <X509Data>
                            <X509Certificate>MIIDHTCCAgWgAwIBAgIJQGx08Hlrv/MpMA0GCSqGSIb3DQEBCwUAMCwxKjAoBgNVBAMTIWRldi1jYzc0ZmpsNHc0NnVkaW9xLnVzLmF1dGgwLmNvbTAeFw0yMzA2MjYxNDE0MDhaFw0zNzAzMDQxNDE0MDhaMCwxKjAoBgNVBAMTIWRldi1jYzc0ZmpsNHc0NnVkaW9xLnVzLmF1dGgwLmNvbTCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBAKpjXGcMCGvWj2MsNoDCvHVY9V+Ni+sB9bY7H4TAsk+HkjgwZO8rIy1hRVmEy0JQndgmbDxNl5ulBeLutqryDL8Xqoou5nt0S1mwNZMSeMoEdqSxBUbVeb4l10ww7YfOUB4wex7NALQo3UFnWTFOuZn3VQF70wHgdmfmuuqaKvsmTyFP3mIyjyCv06p151JYCw1/sGYB4exRummbOb7hKU9mrlDG5rso1StYX6OwUxc/ezcYDRPZYG12P18/PR606rGoa7pUZtUeuz5Ad4ddIWMXH1j2OPYISxd+tisWbW4OOmBDs4cftgFeEvP9a5NfSbigXQSbuc5SNuzO7rEPUksCAwEAAaNCMEAwDwYDVR0TAQH/BAUwAwEB/zAdBgNVHQ4EFgQUzt+/ZYUPg3g56C04LKPddWLswmowDgYDVR0PAQH/BAQDAgKEMA0GCSqGSIb3DQEBCwUAA4IBAQARtsmdrw0a/B46ZW2802omEM+cNlSrdfszzgyCKqRFRk3E4LsJdVROiKwYsmLbCGdlM7MoUwj7SHTQsyyCOAHffpOPyVKaylx2XHovy2UN1nC9dKvEKMnPh+1VYn29hkk74KgCB1VKhLbbefzDxQTK+nsQ+HQW91ib2SgNDgsx3+msm+jYBI3ALdcXS58cFGlLD3CQo2KL0VlazGI1No5B2HOC4UT1bD4KN72HS81epkm2PxmkA1sNH8pE7m7Us2jgrcSjlQfwBTNdVEn8qWvfTlhRkiWi+Agf8pIIkUTKzEG+HRlv0I6S8lI4EuCG5Z/MaF62bMyaFQWs/0oIfLbw</X509Certificate>
                        </X509Data>
                    </KeyInfo>
                </Signature>
                <saml:Subject>
                    <saml:NameID Format="urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress">e2e-334528fe243b@localstack.cloud</saml:NameID>
                    <saml:SubjectConfirmation Method="urn:oasis:names:tc:SAML:2.0:cm:bearer">
                        <saml:SubjectConfirmationData NotOnOrAfter="2024-03-12T21:53:05.219Z"
                                                      Recipient="https://localstack-staging.auth.eu-central-1.amazoncognito.com/saml2/idpresponse"
                                                      InResponseTo="_48354bb4-1fd7-442a-82a3-50dc5240c74f"
                                                      />
                    </saml:SubjectConfirmation>
                </saml:Subject>
                <saml:Conditions NotBefore="2024-03-12T20:53:05.219Z"
                                 NotOnOrAfter="2024-03-12T21:53:05.219Z"
                                 >
                    <saml:AudienceRestriction>
                        <saml:Audience>urn:amazon:cognito:sp:us-east-1_idptest</saml:Audience>
                    </saml:AudienceRestriction>
                </saml:Conditions>
                <saml:AuthnStatement AuthnInstant="2024-03-12T20:53:05.219Z"
                                     SessionIndex="_0OmGDAoMr0e3pEh4x31QYBbMKCMA-0wb"
                                     >
                    <saml:AuthnContext>
                        <saml:AuthnContextClassRef>urn:oasis:names:tc:SAML:2.0:ac:classes:unspecified</saml:AuthnContextClassRef>
                    </saml:AuthnContext>
                </saml:AuthnStatement>
                <saml:AttributeStatement xmlns:xs="http://www.w3.org/2001/XMLSchema"
                                         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                                         >
                    <saml:Attribute Name="http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress"
                                    NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri"
                                    >
                        <saml:AttributeValue xsi:type="xs:string">e2e-334528fe243b@localstack.cloud</saml:AttributeValue>
                    </saml:Attribute>
                    <saml:Attribute Name="http://schemas.xmlsoap.org/ws/2005/05/identity/claims/name"
                                    NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri"
                                    >
                        <saml:AttributeValue xsi:type="xs:string">e2e-334528fe243b@localstack.cloud</saml:AttributeValue>
                    </saml:Attribute>
                </saml:AttributeStatement>
            </saml:Assertion>
        </samlp:Response>
        """
    )

    def _get_assertions(request_id: str):
        _saml_resp = xml_saml_response.format(request_id=request_id)
        return base64.b64encode(to_bytes(_saml_resp)).decode("utf-8")

    return _get_assertions


@pytest.fixture
def saml_callback_url(httpserver):
    def _handler(request: werkzeug.Request):
        code = request.args.get("code")
        return Response(
            json.dumps({"code": code}),
            status=200,
            headers={"Content-Type": "application/json"},
        )

    httpserver.expect_request("").respond_with_handler(_handler)
    http_endpoint = httpserver.url_for("/callback")
    return http_endpoint


@pytest.fixture
def trigger_lambda(create_lambda_with_invocation_forwarding):
    return create_lambda_with_invocation_forwarding(lambda_source=LAMBDA_TRIGGERS)


@pytest.fixture
def trigger_lambda_pre_token_v2(create_lambda_with_invocation_forwarding):
    return create_lambda_with_invocation_forwarding(lambda_source=LAMBDA_TRIGGER_PRE_TOKEN_V2)


@pytest.fixture
def trigger_lambda_v2(create_lambda_with_invocation_forwarding):
    def _wrapper(lambda_func: str):
        return create_lambda_with_invocation_forwarding(lambda_source=lambda_func)

    return _wrapper


@pytest.fixture
def srp_get_id_token(aws_client):
    def _get_token(username: str, password: str, pool_client: Dict):
        awssrp = aws_srp.AWSSRP(
            username=username,
            password=password,
            pool_id=pool_client["UserPoolId"],
            client_id=pool_client["ClientId"],
            client=aws_client.cognito_idp,
        )
        token = awssrp.authenticate_user()
        id_token = token["AuthenticationResult"]["IdToken"]
        assert id_token
        return id_token

    return _get_token


@pytest.fixture
def create_pool_client_and_user(create_user_pool_client, trigger_lambda, aws_client):
    def _create(**user_pool_kwargs) -> Tuple[str, str, str]:
        # create user pool and client
        result = create_user_pool_client(pool_kwargs=user_pool_kwargs)
        client_id = result.pool_client["ClientId"]
        pool_id = result.user_pool["Id"]

        # create user
        username = f"user-{short_uid()}"
        aws_client.cognito_idp.sign_up(
            ClientId=client_id,
            Username=username,
            Password=TEST_PASSWORD,
        )
        aws_client.cognito_idp.admin_confirm_sign_up(UserPoolId=pool_id, Username=username)

        return pool_id, client_id, username

    yield _create


@pytest.fixture
def add_cognito_snapshot_transformers(snapshot):
    # TODO: convert into specialized transformer!
    snapshot.add_transformer(snapshot.transform.key_value("Session", reference_replacement=False))
    snapshot.add_transformer(snapshot.transform.key_value("userName", "username"))
    snapshot.add_transformer(snapshot.transform.key_value("USERNAME", "username"))
    snapshot.add_transformer(snapshot.transform.key_value("sub"))
    snapshot.add_transformer(snapshot.transform.key_value("clientId"))
    snapshot.add_transformer(snapshot.transform.key_value("userPoolId"))
    snapshot.add_transformer(snapshot.transform.key_value("AccessToken"))
    snapshot.add_transformer(snapshot.transform.key_value("IdToken"))
    snapshot.add_transformer(snapshot.transform.key_value("RefreshToken"))
    snapshot.add_transformer(snapshot.transform.key_value("ClientId"))
    snapshot.add_transformer(snapshot.transform.key_value("UserPoolId"))
    snapshot.add_transformer(snapshot.transform.key_value("ClientName"))
    snapshot.add_transformer(snapshot.transform.key_value("ClientSecret"))
    snapshot.add_transformer(
        snapshot.transform.key_value("CreationDate", reference_replacement=False)
    )
    snapshot.add_transformer(
        snapshot.transform.key_value("LastModifiedDate", reference_replacement=False)
    )
    snapshot.add_transformer(snapshot.transform.key_value("SALT", "salt"))
    snapshot.add_transformer(snapshot.transform.key_value("SECRET_BLOCK", "secret-block"))
    snapshot.add_transformer(snapshot.transform.key_value("SRP_B", "srp-b"))
    snapshot.add_transformer(snapshot.transform.key_value("USER_ID_FOR_SRP", "srp-username"))
    snapshot.add_transformer(snapshot.transform.key_value("ActiveEncryptionCertificate"))
    snapshot.add_transformer(snapshot.transform.key_value("MetadataURL"))
    snapshot.add_transformer(snapshot.transform.key_value("SLORedirectBindingURI"))
    snapshot.add_transformer(snapshot.transform.key_value("SSORedirectBindingURI"))


@pytest.fixture
def add_cognito_jwt_token_transformers(snapshot):
    snapshot.add_transformers_list(
        [
            snapshot.transform.key_value("sub"),
            snapshot.transform.key_value("jti"),
            snapshot.transform.key_value("origin_jti"),
            snapshot.transform.key_value("iss"),
            snapshot.transform.key_value("client_id"),
            # we need to not reference-replace, because those are `int` values
            snapshot.transform.key_value("auth_time", reference_replacement=False),
            snapshot.transform.key_value("exp", reference_replacement=False),
            snapshot.transform.key_value("iat", reference_replacement=False),
        ]
    )


@pytest.fixture
def signup_and_login_user(create_role, create_policy, srp_get_id_token, aws_client):
    identity_pools = []

    def _signup_and_login(
        pool_client: Dict,
        username: str,
        password: str,
        attributes: List[Dict] = None,
        srp_authentication: bool = True,
    ):
        aws_client.cognito_idp.sign_up(
            ClientId=pool_client["ClientId"],
            Username=username,
            Password=password,
            UserAttributes=attributes or [],
        )
        aws_client.cognito_idp.admin_confirm_sign_up(
            UserPoolId=pool_client["UserPoolId"], Username=username
        )
        pool_provider_name = f"cognito-idp.{aws_client.cognito_idp.meta.region_name}.amazonaws.com/{pool_client['UserPoolId']}"

        if not srp_authentication:
            return

        id_token = srp_get_id_token(username, password, pool_client)
        logins = {pool_provider_name: id_token}

        identity_pool_name = f"identity-pool-{short_uid()}"
        id_pool_id = aws_client.cognito_identity.create_identity_pool(
            IdentityPoolName=identity_pool_name,
            CognitoIdentityProviders=[
                {"ProviderName": pool_provider_name, "ClientId": pool_client["ClientId"]}
            ],
            AllowUnauthenticatedIdentities=True,
        )["IdentityPoolId"]
        identity_pools.append(id_pool_id)
        # create roles for authenticated / unauthenticated users
        role_name = f"Cognito-role-{short_uid()}"
        cognito_role_arn = create_role(
            RoleName=role_name, AssumeRolePolicyDocument=json.dumps(COGNITO_ASSUME_ROLE_POLICY)
        )["Role"]["Arn"]
        policy_arn = create_policy(
            PolicyName=f"policy-{short_uid()}",
            PolicyDocument=json.dumps(COGNITO_AUTH_POLICY_DOC),
        )["Policy"]["Arn"]
        aws_client.iam.attach_role_policy(RoleName=role_name, PolicyArn=policy_arn)
        aws_client.cognito_identity.set_identity_pool_roles(
            IdentityPoolId=id_pool_id,
            Roles={"authenticated": cognito_role_arn, "unauthenticated": cognito_role_arn},
        )
        identity_id = aws_client.cognito_identity.get_id(IdentityPoolId=id_pool_id, Logins=logins)[
            "IdentityId"
        ]

        def get_credentials():
            return aws_client.cognito_identity.get_credentials_for_identity(
                IdentityId=identity_id, Logins=logins
            )["Credentials"]

        # wait for role to become assumable
        credentials = retry(get_credentials, sleep=2, retries=8)

        return credentials, identity_id, id_pool_id

    yield _signup_and_login
    for identity_pool in identity_pools:
        try:
            aws_client.cognito_identity.delete_identity_pool(IdentityPoolId=identity_pool)
        except Exception as e:
            LOG.debug("Error deleting identity pool %s: %s", identity_pool, e)


@pytest.fixture
def patch_send_confirmation_email():
    with mock.patch(
        "localstack.pro.core.services.cognito_idp.provider.send_confirmation_email"
    ) as p:
        yield p


@pytest.fixture
def update_user_attributes(aws_client):
    def _update_attributes(pool_id: str, username: str, value: str | None = None):
        client = aws_client.cognito_idp
        client.add_custom_attributes(
            UserPoolId=pool_id,
            CustomAttributes=[{"Name": "updated_attr1", "AttributeDataType": "String"}],
        )
        if is_aws_cloud():
            # sometimes tests fail because the custom attribute isn't defined yet
            time.sleep(1)
        attr_val = short_uid() if not value else value
        new_attr = {"Name": "custom:updated_attr1", "Value": attr_val}
        client.admin_update_user_attributes(
            UserPoolId=pool_id, Username=username, UserAttributes=[new_attr]
        )
        response = client.admin_get_user(UserPoolId=pool_id, Username=username)
        user_attrs = response.get("UserAttributes", [])
        assert new_attr in user_attrs

    return _update_attributes


def wait_until_domain_name_resolves(domain_name: str, **kwargs) -> str:
    """
    Retry loop to wait until the given domain name resolves. Useful for testing Cognito auth domains in AWS.
    Note: You may still need to flush your local DNS cache while testing.
    """

    def _resolve_name():
        return socket.gethostbyname_ex(domain_name)[2][0]

    kwargs.setdefault("sleep", 3)
    kwargs.setdefault("retries", 40)
    return retry(_resolve_name, **kwargs)


@pytest.fixture
def cognito_idp_endpoint(region_name):
    def _generate(domain_name: str, region: str | None = None) -> str:
        if is_aws_cloud():
            return f"https://{domain_name}.auth.{region or region_name}.amazoncognito.com"
        else:
            return (
                config.internal_service_url(host=f"cognito-idp.{localstack_host().host}")
                + "/_aws/cognito-idp"
            )

    return _generate


class TestCognito:
    @pytest.fixture
    def create_user_pool_authorizer_for_rest_api(
        self, account_id, create_user_pool_client, aws_client
    ):
        def _create_user_pool(rest_api_id):
            user_pool_result = create_user_pool_client(client_kwargs={"GenerateSecret": True})
            user_pool = user_pool_result.user_pool
            pool_arn = arns.cognito_user_pool_arn(
                user_pool["Id"],
                region_name=aws_client.cognito_idp.meta.region_name,
                account_id=account_id,
            )
            auth_name = f"auth-{short_uid()}"
            result = aws_client.apigateway.create_authorizer(
                restApiId=rest_api_id,
                name=auth_name,
                type="COGNITO_USER_POOLS",
                identitySource="method.request.header.Authorization",
                providerARNs=[pool_arn],
            )
            return user_pool_result, result["id"]

        return _create_user_pool

    @pytest.fixture
    def connect_api_gateway_to_lambda(self, create_lambda_function, aws_client):
        api_ids = []

        def _connect_apigateway_to_lambda(
            gateway_name, func_name, methods=None, path=None, auth_creator_func=None, auth_type=None
        ):
            create_function_result = create_lambda_function(
                func_name=func_name, handler_file=LAMBDA_TEST, runtime=Runtime.python3_12
            )
            function_arn = create_function_result["CreateFunctionResponse"]["FunctionArn"]
            aws_client.lambda_.add_permission(
                FunctionName=func_name,
                StatementId=f"c{short_uid()}",
                Action="lambda:InvokeFunction",
                Principal="apigateway.amazonaws.com",
            )
            target_arn = arns.apigateway_invocations_arn(
                function_arn, region_name=aws_client.apigateway.meta.region_name
            )
            result = testutil.connect_api_gateway_to_http_with_lambda_proxy(
                gateway_name=gateway_name,
                target_uri=target_arn,
                methods=methods,
                http_method="POST",
                path=path,
                stage_name=TEST_STAGE_NAME,
                auth_type=auth_type,
                auth_creator_func=auth_creator_func,
                client=aws_client.apigateway,
            )
            api_ids.append(result["id"])
            return result

        yield _connect_apigateway_to_lambda
        for api_id in api_ids:
            try:
                aws_client.apigateway.delete_rest_api(restApiId=api_id)
            except Exception as e:
                LOG.debug("Unable to delete rest api %s: %s", api_id, e)

    @markers.aws.validated
    def test_user_pool_error_messages(
        self,
        create_lambda_function,
        signup_and_login_user,
        create_user_pool_client,
        aws_client,
        snapshot,
    ):
        user_pool_result = create_user_pool_client()
        pool_id = user_pool_result.user_pool["Id"]
        client = user_pool_result.pool_client

        # assert that Limit parameter cannot be greater than 60 (AWS parity)
        with pytest.raises(ClientError) as exc:
            aws_client.cognito_idp.list_users(UserPoolId=pool_id, Limit=100)
        snapshot.match("error-list-users-limit", exc.value.response)

        # create user, assert that confirmation only works once
        username = f"user-{short_uid()}"
        signup_and_login_user(client, username, password="SecretPw1!")
        with pytest.raises(ClientError) as exc:
            aws_client.cognito_idp.admin_confirm_sign_up(UserPoolId=pool_id, Username=username)
        snapshot.match("error-already-confirmed", exc.value.response)

    @markers.aws.validated
    def test_delete_user(self, create_user_pool_client, aws_client, snapshot):
        snapshot.add_transformer(
            [
                snapshot.transform.key_value("AccessToken"),
                snapshot.transform.key_value("IdToken"),
                snapshot.transform.key_value("RefreshToken"),
            ]
        )

        username = f"user-{short_uid()}"
        password = "Password1!"

        result: UserPoolAndClient = create_user_pool_client()
        client_id = result.pool_client["ClientId"]
        user_pool_id = result.user_pool["Id"]

        aws_client.cognito_idp.admin_create_user(
            UserPoolId=user_pool_id,
            Username=username,
        )
        aws_client.cognito_idp.admin_set_user_password(
            UserPoolId=user_pool_id, Username=username, Password=password, Permanent=True
        )
        response = aws_client.cognito_idp.initiate_auth(
            AuthFlow="USER_PASSWORD_AUTH",
            ClientId=client_id,
            AuthParameters={"USERNAME": username, "PASSWORD": password},
        )
        snapshot.match("initiate_auth", response)
        access_token = response.get("AuthenticationResult", {}).get("AccessToken")
        assert access_token

        response = aws_client.cognito_idp.delete_user(AccessToken=access_token)
        snapshot.match("deleted_user", response)

        with pytest.raises(ClientError) as ctx:
            aws_client.cognito_idp.admin_delete_user(UserPoolId=user_pool_id, Username=username)
        snapshot.match("error-user-already-deleted", ctx.value.response)

    @markers.aws.only_localstack
    def test_user_pool_custom_id(self, create_user_pool, aws_client):
        with pytest.raises(ClientError) as exc:
            create_user_pool(UserPoolTags={"_custom_id_": "myid123"})
        assert exc.value.response["Error"]["Code"] == "InvalidParameterException"

        custom_pool_id = f"us-east-1_{short_uid()}"
        pool = create_user_pool(UserPoolTags={"_custom_id_": custom_pool_id})
        result = aws_client.cognito_idp.describe_user_pool(UserPoolId=pool["Id"])
        assert result["UserPool"]["Id"] == custom_pool_id, "custom pool id not honored"

        custom_client_id = "_custom_id_:myid123"
        result = aws_client.cognito_idp.create_user_pool_client(
            UserPoolId=custom_pool_id, ClientName=custom_client_id
        )
        assert (
            result["ResponseMetadata"]["HTTPStatusCode"] == 200
        ), "can't create client with custom pool id"
        assert result["UserPoolClient"]["ClientId"] == "myid123", "custom client id not honored"

    @markers.aws.validated
    def test_api_gateway_cognito_pool_authorizer(
        self,
        create_user_pool_authorizer_for_rest_api,
        connect_api_gateway_to_lambda,
        signup_and_login_user,
        aws_client,
    ):
        # add authorizers
        state = {}

        def create_authorizer(api_id):
            client, auth_id = create_user_pool_authorizer_for_rest_api(api_id)
            state["client"] = client
            return auth_id

        # create Lambda and API gateway
        lambda_name = f"lambda-noop-{short_uid()}"
        rest_api = connect_api_gateway_to_lambda(
            f"cognito_api_gw_{short_uid()}",
            lambda_name,
            path=TEST_PATH,
            auth_creator_func=create_authorizer,
            auth_type="COGNITO_USER_POOLS",
        )
        client = state["client"].pool_client

        # create user
        username = f"user-{short_uid()}"
        password = "SecretPw1!"
        signup_and_login_user(client, username, password, srp_authentication=False)

        url = api_invoke_url(api_id=rest_api["id"], stage=TEST_STAGE_NAME, path=TEST_PATH)

        # check successful auth with Bearer token
        result = self._attempt_user_login(
            client["ClientId"], username, password, cognito_client=aws_client.cognito_idp
        )
        token = result["IdToken"]
        result = requests.post(url, headers={"Authorization": f"Bearer {token}"})
        assert result.status_code == 200
        expected = {
            "cognito_identity_id": None,
            "cognito_identity_pool_id": None,
        }
        assert json.loads(to_str(result.content))["context"]["identity"] == expected
        response = requests.post(url, headers={"Authorization": "Bearer invalid-token"})
        assert response.status_code == 401

    @markers.aws.validated
    def test_cognito_authorizer_scopes(self, infrastructure_setup, aws_client, snapshot):
        infra = infrastructure_setup(namespace="TestCognitoAuthorizeScope")
        stack = cdk.Stack(infra.cdk_app, "CognitoAuthScopeStack")

        # Cognito Stack
        user_pool = cdk.aws_cognito.UserPool(
            stack,
            "user-pool",
            self_sign_up_enabled=True,
        )

        custom_scope_one = cdk.aws_cognito.ResourceServerScope(
            scope_name="localstack.read",
            scope_description="A scope for testing the Cognito authorizer",
        )
        custom_scope_two = cdk.aws_cognito.ResourceServerScope(
            scope_name="localstack.write",
            scope_description="A scope for testing the Cognito authorizer",
        )
        resource_server = user_pool.add_resource_server(
            "ResourceServer",
            identifier="ls-resource-server",
            scopes=[custom_scope_one, custom_scope_two],
        )

        client = user_pool.add_client(
            "user-pool-client",
            o_auth=cdk.aws_cognito.OAuthSettings(
                flows=cdk.aws_cognito.OAuthFlows(client_credentials=True),
                scopes=[
                    cdk.aws_cognito.OAuthScope.resource_server(resource_server, custom_scope_one),
                    cdk.aws_cognito.OAuthScope.resource_server(resource_server, custom_scope_two),
                ],
            ),
            generate_secret=True,
            auth_flows=cdk.aws_cognito.AuthFlow(
                user_password=True,
                user_srp=True,
            ),
        )

        domain = user_pool.add_domain(
            "user-pool-domain",
            cognito_domain=cdk.aws_cognito.CognitoDomainOptions(domain_prefix="ls-domain"),
        )

        # API Gateway Stack
        api = cdk.aws_apigateway.RestApi(
            stack,
            "test-api",
            rest_api_name="test-api",
            deploy=True,
            deploy_options=cdk.aws_apigateway.StageOptions(stage_name="prod"),
        )

        authorizer = cdk.aws_apigateway.CognitoUserPoolsAuthorizer(
            stack,
            "cognito-authorizer",
            cognito_user_pools=[user_pool],
        )

        resource = api.root.add_resource("read")
        resource.add_method(
            "GET",
            cdk.aws_apigateway.MockIntegration(
                integration_responses=[
                    cdk.aws_apigateway.IntegrationResponse(
                        status_code="200",
                        response_templates={
                            "application/json": '{"message": "LocalStack is awesome!"}'
                        },
                        response_parameters={
                            "method.response.header.Content-Type": "'application/json'"
                        },
                    )
                ],
                request_templates={"application/json": '{"statusCode": 200}'},
            ),
            method_responses=[
                cdk.aws_apigateway.MethodResponse(
                    status_code="200",
                    response_parameters={"method.response.header.Content-Type": True},
                )
            ],
            authorizer=authorizer,
            authorization_scopes=["ls-resource-server/localstack.read"],
            authorization_type=cdk.aws_apigateway.AuthorizationType.COGNITO,
        )

        cdk.CfnOutput(stack, "ClientId", value=client.user_pool_client_id)
        cdk.CfnOutput(stack, "UserPoolId", value=user_pool.user_pool_id)
        cdk.CfnOutput(stack, "apiId", value=api.rest_api_id)
        cdk.CfnOutput(stack, "Domain", value=domain.domain_name)

        with infra.provisioner() as prov:
            outputs = prov.get_stack_outputs("CognitoAuthScopeStack")
            user_pool_id = outputs["UserPoolId"]
            client_id = outputs["ClientId"]
            api_id = outputs["apiId"]
            domain_name = outputs["Domain"]

            client_secret = aws_client.cognito_idp.describe_user_pool_client(
                UserPoolId=user_pool_id, ClientId=client_id
            )["UserPoolClient"]["ClientSecret"]
            auth = base64.b64encode(f"{client_id}:{client_secret}".encode("utf-8")).decode("utf-8")

            if is_aws_cloud():
                oauth_token_prefix = f"https://{domain_name}.auth.{aws_client.cognito_idp.meta.region_name}.amazoncognito.com"
            else:
                base_url = config.internal_service_url(protocol="http")
                oauth_token_prefix = f"{base_url}/_aws/cognito-idp"

            oauth_token_url = f"{oauth_token_prefix}/oauth2/token"
            data = {
                "grant_type": "client_credentials",
                "client_id": client_id,
                "scope": "ls-resource-server/localstack.read",
            }

            def _get_oauth_client_credentials():
                return requests.post(
                    oauth_token_url,
                    headers={
                        "Content-Type": "application/x-www-form-urlencoded",
                        "Authorization": f"Basic {auth}",
                    },
                    data=data,
                )

            response = retry(_get_oauth_client_credentials, sleep=10, retries=50)
            access_token = response.json()["access_token"]
            invocation_url = api_invoke_url(api_id=api_id, stage="prod", path="/read")
            result = requests.get(
                invocation_url, headers={"Authorization": access_token}, verify=False
            )
            assert result.status_code == 200
            snapshot.match("authorized-call", result.json())

            data["scope"] = "ls-resource-server/localstack.write"
            response = retry(_get_oauth_client_credentials, sleep=10, retries=50)
            access_token = response.json()["access_token"]
            result = requests.get(
                invocation_url, headers={"Authorization": access_token}, verify=False
            )
            assert result.status_code == 401
            snapshot.match("unauthorized-call", result.text)

    @markers.aws.validated
    @pytest.mark.skip
    def test_api_gateway_cognito_identity_authorization(
        self,
        connect_api_gateway_to_lambda,
        signup_and_login_user,
        create_user_pool_client,
        aws_client,
    ):
        # create Lambda and API gateway
        lambda_name = f"lambda-noop-{short_uid()}"
        rest_api = connect_api_gateway_to_lambda(
            f"cognito_api_gw_{short_uid()}", lambda_name, path=TEST_PATH, auth_type="AWS_IAM"
        )
        user_pool_result = create_user_pool_client()
        client = user_pool_result.pool_client

        # create user
        username = f"user-{short_uid()}"
        password = "SecretPw1!"
        credentials, _, _ = signup_and_login_user(
            client,
            username,
            password,
        )
        url = api_invoke_url(api_id=rest_api["id"], stage=TEST_STAGE_NAME, path=TEST_PATH)

        # check successful auth
        awsauth = AWS4Auth(
            credentials["AccessKeyId"],
            credentials["SecretKey"],
            aws_client.cognito_idp.meta.region_name,
            "execute-api",
            session_token=credentials["SessionToken"],
        )

        def invoke_api():
            result = requests.post(url, auth=awsauth)
            assert result.status_code == 200
            return result

        result = retry(invoke_api)

        expected = {
            "cognito_identity_id": None,
            "cognito_identity_pool_id": None,
        }
        assert json.loads(to_str(result.content))["context"]["identity"] == expected

        # check invalid auth - access denied
        result = requests.post(url)
        assert result.status_code == 403
        awsauth = AWS4Auth(
            "_invalid_",
            credentials["SecretKey"],
            aws_client.cognito_idp.meta.region_name,
            "execute-api",
            session_token="_invalid_",
        )
        result = requests.post(url, auth=awsauth)
        assert result.status_code == 403

    @markers.aws.validated
    @pytest.mark.skip
    def test_lambda_invocation_cognito_identity(
        self, create_lambda_function, signup_and_login_user, create_user_pool_client, aws_client
    ):
        lambda_name = f"lambda-noop-{short_uid()}"
        create_lambda_function(
            func_name=lambda_name, handler_file=LAMBDA_TEST, runtime=Runtime.python3_12
        )

        # create Lambda and API gateway
        user_pool_result = create_user_pool_client()
        client = user_pool_result.pool_client

        # create user
        username = f"user-{short_uid()}"
        password = "SecretPw1!"
        credentials, identity_id, identity_pool_id = signup_and_login_user(
            client,
            username,
            password,
        )
        lambda_cognito_client = boto3.client(
            "lambda",
            region_name=aws_client.lambda_.meta.region_name,
            aws_access_key_id=credentials["AccessKeyId"],
            aws_secret_access_key=credentials["SecretKey"],
            aws_session_token=credentials["SessionToken"],
            endpoint_url=None if is_aws_cloud() else config.internal_service_url(),
        )

        def invoke_lambda():
            result = lambda_cognito_client.invoke(FunctionName=lambda_name, Payload=b"{}")[
                "Payload"
            ].read()
            return result

        result = retry(invoke_lambda)
        result = json.loads(to_str(result))

        expected = {
            "cognito_identity_id": identity_id,
            "cognito_identity_pool_id": identity_pool_id,
        }
        assert json.loads(result["body"])["context"]["identity"] == expected

    @markers.aws.validated
    def test_password_policy(self, create_user_pool_client, signup_and_login_user, snapshot):
        # create user pool with simple password policy
        kwargs = {
            "Policies": {
                "PasswordPolicy": {
                    "MinimumLength": 10,
                    "RequireUppercase": False,
                    "RequireLowercase": True,
                    "RequireNumbers": True,
                    "RequireSymbols": True,
                }
            }
        }
        user_pool_result = create_user_pool_client(pool_kwargs=kwargs)
        pool_client = user_pool_result.pool_client
        username = f"user-{short_uid()}"

        with pytest.raises(ClientError) as ctx:
            signup_and_login_user(pool_client, username, "Test1234!")  # too short
        snapshot.match("password-too-short", ctx.value.response)
        with pytest.raises(ClientError) as ctx:
            signup_and_login_user(pool_client, username, "testtest1234")  # no symbols
        snapshot.match("password-no-symbols", ctx.value.response)
        with pytest.raises(ClientError) as ctx:
            signup_and_login_user(pool_client, username, "testtest!#")  # no numbers
        snapshot.match("password-no-numbers", ctx.value.response)
        # valid password
        signup_and_login_user(pool_client, username, "Test1234!!")

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(
        paths=["$..Error.Message", "$..message", "$..UserAttributes..Value", "$..Username"]
    )
    def test_admin_set_permanent_invalid_password(
        self, create_user_pool_client, aws_client, snapshot
    ):
        kwargs = {
            "Policies": {
                "PasswordPolicy": {
                    "MinimumLength": 15,
                    "RequireUppercase": True,
                    "RequireLowercase": True,
                    "RequireNumbers": True,
                    "RequireSymbols": True,
                }
            }
        }
        user_pool_result = create_user_pool_client(pool_kwargs=kwargs)
        user_pool_id: str = user_pool_result.user_pool["Id"]
        username = f"username-{short_uid()}"
        aws_client.cognito_idp.admin_create_user(UserPoolId=user_pool_id, Username=username)
        with pytest.raises(ClientError) as ctx:
            aws_client.cognito_idp.admin_set_user_password(
                UserPoolId=user_pool_id, Username=username, Password="dumb pass", Permanent=True
            )
        snapshot.match("invalid-permanent-password", ctx.value.response)

        with pytest.raises(ClientError) as ctx:
            aws_client.cognito_idp.admin_set_user_password(
                UserPoolId=user_pool_id, Username=username, Password="dumb pass"
            )
        snapshot.match("invalid-not-permanent-password", ctx.value.response)

        aws_client.cognito_idp.admin_set_user_password(
            UserPoolId=user_pool_id, Username=username, Password="P#75O1jOes$jOes$jOes$j"
        )
        response = aws_client.cognito_idp.admin_get_user(Username=username, UserPoolId=user_pool_id)
        snapshot.match("valid-password-user-status", response)

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(paths=["$..AccountRecoverySetting"])
    def test_srp_login(
        self, create_user_pool_client, signup_and_login_user, srp_get_id_token, aws_client, snapshot
    ):
        # create pool client and test user
        username = f"user-{short_uid()}"
        password = TEST_PASSWORD
        user_pool_result = create_user_pool_client(
            pool_kwargs={"UsernameConfiguration": {"CaseSensitive": False}}
        )
        snapshot.match("user-pool", user_pool_result.user_pool)
        user_pool_result.pool_client["ExplicitAuthFlows"] = sorted(
            user_pool_result.pool_client["ExplicitAuthFlows"]
        )
        snapshot.match("user-pool-client", user_pool_result.pool_client)
        pool_client = user_pool_result.pool_client
        pool_id = pool_client["UserPoolId"]
        signup_and_login_user(pool_client, username, password)
        snapshot.add_transformer(
            snapshot.transform.regex(user_pool_result.user_pool["Name"], "<pool-name>")
        )
        snapshot.add_transformer(snapshot.transform.regex(pool_id, "<pool-id>"))
        snapshot.add_transformer(snapshot.transform.regex(pool_client["ClientId"], "<client-id>"))

        # log in using lower- and uppercase username
        srp_get_id_token(username, password, pool_client=pool_client)
        srp_get_id_token(username.upper(), password, pool_client=pool_client)

        # test incorrect username
        with pytest.raises(ClientError) as exc:
            srp_get_id_token("invalid", password, pool_client)
        snapshot.match("error-invalid-username", exc.value.response)

        # test incorrect password
        with pytest.raises(ClientError) as exc:
            srp_get_id_token(username, "invalid", pool_client)
        snapshot.match("error-invalid-password", exc.value.response)

        # use correct credentials
        id_token = srp_get_id_token(username, password, pool_client)
        assert id_token

        # delete users (should work case-insensitively)
        aws_client.cognito_idp.admin_delete_user(UserPoolId=pool_id, Username=username.upper())
        with pytest.raises(ClientError) as ctx:
            aws_client.cognito_idp.admin_delete_user(UserPoolId=pool_id, Username=username.upper())
        snapshot.match("error-user-already-deleted", ctx.value.response)

        # attempt to create user with same name (should work)
        aws_client.cognito_idp.admin_create_user(
            UserPoolId=pool_id, Username=username, TemporaryPassword=password
        )
        aws_client.cognito_idp.admin_delete_user(UserPoolId=pool_id, Username=username.upper())

    @markers.aws.unknown
    def test_srp_login_after_password_update(
        self, create_user_pool_client, srp_get_id_token, aws_client
    ):
        # create pool client and test user
        username = f"user-{short_uid()}"
        password1 = "Test123!"
        password2 = "Test123!2"
        password3 = "Test123!3"
        user_pool_result = create_user_pool_client(
            pool_kwargs={"UsernameConfiguration": {"CaseSensitive": False}}
        )
        pool_client = user_pool_result.pool_client
        pool_id = pool_client["UserPoolId"]

        # create user, run SRP auth
        aws_client.cognito_idp.admin_create_user(
            UserPoolId=pool_id, Username=username, TemporaryPassword=password1
        )
        srp_get_id_token(username, password1, pool_client=pool_client)

        # update user password via admin, run SRP auth again
        aws_client.cognito_idp.admin_set_user_password(
            UserPoolId=pool_id, Username=username, Password=password2
        )
        srp_get_id_token(username, password2, pool_client=pool_client)

        # change user password, run SRP auth again
        client_id = user_pool_result.pool_client["ClientId"]
        result = aws_client.cognito_idp.initiate_auth(
            AuthFlow="USER_PASSWORD_AUTH",
            ClientId=client_id,
            AuthParameters={"USERNAME": username, "PASSWORD": password2},
        )
        access_token = result.get("AuthenticationResult", {}).get("AccessToken")
        aws_client.cognito_idp.change_password(
            PreviousPassword=password2, ProposedPassword=password3, AccessToken=access_token
        )
        srp_get_id_token(username, password3, pool_client=pool_client)

    @markers.aws.validated
    def test_signup_case_insensitive_and_auth_using_srp(
        self, create_user_pool_client, srp_get_id_token, aws_client, snapshot
    ):
        # create user pool
        pool_name = f"pool-{short_uid()}"
        pool_kwargs = {
            "UsernameAttributes": ["phone_number", "email"],
            "UsernameConfiguration": {"CaseSensitive": False},
        }
        user_pool_result = create_user_pool_client(pool_name=pool_name, pool_kwargs=pool_kwargs)
        pool_client = user_pool_result.pool_client
        pool_id = pool_client["UserPoolId"]
        password = TEST_PASSWORD

        def check_srp_auth(username):
            # test lower- and upper-case login
            for user in [username, username.upper()]:
                id_token = srp_get_id_token(user, password, pool_client)
                assert id_token
                with pytest.raises(ClientError):
                    srp_get_id_token(user, "incorrectPass", pool_client)

        def check_auth(username):
            # test lower- and upper-case login
            for user in [username, username.upper()]:
                result = aws_client.cognito_idp.initiate_auth(
                    AuthFlow="USER_PASSWORD_AUTH",
                    ClientId=pool_client["ClientId"],
                    AuthParameters={"USERNAME": user, "PASSWORD": TEST_PASSWORD},
                )
                assert result.get("AuthenticationResult", {}).get("AccessToken")

        # create user via sign_up(..), then initiate auth
        username1 = f"u-{short_uid()}@gmail.com"
        aws_client.cognito_idp.sign_up(
            ClientId=pool_client["ClientId"], Username=username1, Password=password
        )
        aws_client.cognito_idp.admin_confirm_sign_up(UserPoolId=pool_id, Username=username1)
        check_auth(username1)
        check_srp_auth(username1)

        # create user via admin_create_user(..), then initiate auth
        username2 = f"u-{short_uid()}@gmail.com"
        self._create_user(aws_client.cognito_idp, pool_id, username=username2, password=password)
        check_auth(username2)
        check_srp_auth(username2)

        # delete users (should work case-insensitively)
        aws_client.cognito_idp.admin_delete_user(UserPoolId=pool_id, Username=username1)
        aws_client.cognito_idp.admin_delete_user(UserPoolId=pool_id, Username=username2.upper())
        with pytest.raises(ClientError) as ctx:
            aws_client.cognito_idp.admin_delete_user(UserPoolId=pool_id, Username=username2.upper())
        snapshot.match("error-user-already-deleted", ctx.value.response)

        # attempt to create user with same name (should work)
        aws_client.cognito_idp.admin_create_user(
            UserPoolId=pool_id, Username=username2, TemporaryPassword=password
        )
        aws_client.cognito_idp.admin_set_user_password(
            UserPoolId=pool_id, Username=username2, Password=password, Permanent=True
        )
        check_auth(username2)
        aws_client.cognito_idp.admin_delete_user(UserPoolId=pool_id, Username=username2.upper())

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(
        paths=["$..origin_jti"],  # TODO: missing from the Access and Id Tokens
    )
    def test_signup_with_email_phone_aliases(
        self,
        create_user_pool_client,
        aws_client,
        snapshot,
        add_cognito_snapshot_transformers,
        add_cognito_jwt_token_transformers,
    ):
        # note: this test contains some switches when run against AWS, due to missing phone/SMS sending config

        snapshot.add_transformer(snapshot.transform.key_value("email"))
        cognito_client = aws_client.cognito_idp

        # create user pool
        pool_name = f"pool-{short_uid()}"
        pool_kwargs = {"UsernameAttributes": ["phone_number", "email"]}
        user_pool_result = create_user_pool_client(pool_name=pool_name, pool_kwargs=pool_kwargs)
        pool_client = user_pool_result.pool_client
        pool_id = user_pool_result.user_pool["Id"]
        client_id = pool_client["ClientId"]

        # create user with email username
        email = f"{short_uid()}@example.com"
        email_pass = TEST_PASSWORD
        email_sub = self._create_user(cognito_client, pool_id, email, email_pass, confirm_pw=False)
        email_sub = email_sub["User"]["Username"]

        result = aws_client.cognito_idp.admin_get_user(UserPoolId=pool_id, Username=email)
        assert "Username" in result
        result["UserAttributes"] = {
            attr["Name"]: attr["Value"] for attr in result["UserAttributes"]
        }
        snapshot.match("get-user-email", result)
        result = aws_client.cognito_idp.admin_get_user(UserPoolId=pool_id, Username=email_sub)
        assert "Username" in result

        # create user with phone username
        if not is_aws_cloud():
            phone = "+12301230123"
            phone_pass = TEST_PASSWORD
            phone_sub = self._create_user(
                cognito_client, pool_id, phone, phone_pass, confirm_pw=False
            )
            phone_sub = phone_sub["User"]["Username"]

        # initiate auth flows
        auth_email = aws_client.cognito_idp.initiate_auth(
            AuthFlow="USER_PASSWORD_AUTH",
            ClientId=client_id,
            AuthParameters={"USERNAME": email, "PASSWORD": email_pass},
        )
        assert auth_email["ChallengeName"] == "NEW_PASSWORD_REQUIRED"
        assert "ChallengeParameters" in auth_email
        if not is_aws_cloud():
            auth_phone = aws_client.cognito_idp.initiate_auth(
                AuthFlow="USER_PASSWORD_AUTH",
                ClientId=client_id,
                AuthParameters={"USERNAME": phone, "PASSWORD": phone_pass},
            )
            assert auth_phone["ChallengeName"] == "NEW_PASSWORD_REQUIRED"
            assert "ChallengeParameters" in auth_phone

        # check list-users
        users = aws_client.cognito_idp.list_users(UserPoolId=pool_id)["Users"]
        assert len(users) == 1 if is_aws_cloud() else 2
        email_user = [u for u in users if u["Username"] == email_sub][0]
        assert {"Name": "email", "Value": email} in email_user["Attributes"]
        assert {"Name": "sub", "Value": email_user["Username"]} in email_user["Attributes"]
        if not is_aws_cloud():
            phone_user = [u for u in users if u["Username"] == phone_sub][0]
            assert {"Name": "phone_number", "Value": phone} in phone_user["Attributes"]
            assert {"Name": "sub", "Value": phone_user["Username"]} in phone_user["Attributes"]

        # get users by sub attribute
        email_user1 = aws_client.cognito_idp.admin_get_user(UserPoolId=pool_id, Username=email)
        assert email_user1["Username"] == email_sub
        if not is_aws_cloud():
            phone_user1 = aws_client.cognito_idp.admin_get_user(UserPoolId=pool_id, Username=phone)
            assert phone_user1["Username"] == phone_sub

        # initiate password change flow
        new_pass = TEST_PASSWORD + "new"
        result = aws_client.cognito_idp.respond_to_auth_challenge(
            ChallengeName="NEW_PASSWORD_REQUIRED",
            ClientId=client_id,
            Session=auth_email["Session"],
            ChallengeResponses={"NEW_PASSWORD": new_pass, "USERNAME": email},
        )
        access_token = result["AuthenticationResult"]["AccessToken"]
        claims = jwt.decode(access_token, options={"verify_signature": False}) or {}
        # we snapshot the result to make sure the username returned here is the sub, and not the email
        snapshot.match("respond-to-auth-challenge-token", claims)

        result = aws_client.cognito_idp.initiate_auth(
            AuthFlow="USER_PASSWORD_AUTH",
            ClientId=client_id,
            AuthParameters={"USERNAME": email, "PASSWORD": new_pass},
        )
        snapshot.match("initiate-auth-after-pw-update", result)
        access_token = result["AuthenticationResult"]["AccessToken"]
        claims = jwt.decode(access_token, options={"verify_signature": False}) or {}
        snapshot.match("initiate-auth-after-pw-update-access-token", claims)

        with pytest.raises(Exception):
            aws_client.cognito_idp.initiate_auth(
                AuthFlow="USER_PASSWORD_AUTH",
                ClientId=client_id,
                AuthParameters={"USERNAME": email, "PASSWORD": email_pass},
            )

        # delete user
        with pytest.raises(Exception) as ctx:
            aws_client.cognito_idp.admin_delete_user(
                UserPoolId=pool_id, Username=email.upper()
            )  # should not work with uppercase
        assert "UserNotFoundException" in str(ctx.value)
        aws_client.cognito_idp.admin_delete_user(UserPoolId=pool_id, Username=email)
        with pytest.raises(Exception) as ctx:
            aws_client.cognito_idp.admin_get_user(UserPoolId=pool_id, Username=email)
        assert "UserNotFoundException" in str(ctx.value)

        # attempt to create user with same name (should work)
        aws_client.cognito_idp.admin_create_user(
            UserPoolId=pool_id, Username=email, TemporaryPassword=email_pass
        )
        aws_client.cognito_idp.admin_delete_user(UserPoolId=pool_id, Username=email)

    @markers.aws.validated
    @pytest.mark.parametrize("use_email_verified", [True, False])
    @pytest.mark.parametrize("add_attribute", [True, False])
    @pytest.mark.parametrize("username_type", ["email", "phone_number", "name"])
    def test_user_attributes_upon_creation(
        self,
        create_user_pool,
        use_email_verified,
        username_type,
        add_attribute,
        snapshot,
        aws_client,
    ):
        client = aws_client.cognito_idp
        snapshot.add_transformer(snapshot.transform.key_value("sub"))
        snapshot.add_transformer(snapshot.transform.key_value("email"))

        # create user pool
        attributes = [{"Name": "foobar", "AttributeDataType": "String"}]
        if use_email_verified:
            attributes += [{"Name": "email_verified", "AttributeDataType": "Boolean"}]
        result = create_user_pool(AliasAttributes=["preferred_username"], Schema=attributes)
        pool_id = result["Id"]

        # TODO: snapshot default pool attributes (contains first_name, given_name, etc, which we don't support yet)
        # result["SchemaAttributes"] = {attr["Name"]: attr for attr in result["SchemaAttributes"]}
        # snapshot.match("pool-details", result)

        # create user (without email)
        if username_type == "email":
            username = f"user-{short_uid()}@example.com"
        elif username_type == "phone_number":
            username = "+1000000000"
        elif username_type == "name":
            username = f"user-{short_uid()}"

        user_attrs = [{"Name": "custom:foobar", "Value": "test123"}]
        if use_email_verified:
            user_attrs += [{"Name": "email_verified", "Value": "True"}]
            # assert exception "No email provided ..."
            with pytest.raises(ClientError) as exc:
                client.admin_create_user(
                    UserPoolId=pool_id,
                    Username=username,
                    TemporaryPassword=TEST_PASSWORD,
                    UserAttributes=user_attrs,
                )
            snapshot.match("error-no-email", exc.value.response)

        # create user (with email)
        user_attrs += [{"Name": "email", "Value": "test@example.com"}]
        response = client.admin_create_user(
            UserPoolId=pool_id,
            Username=username,
            TemporaryPassword=TEST_PASSWORD,
            UserAttributes=user_attrs,
        )["User"]
        attributes = {attr["Name"]: attr["Value"] for attr in response["Attributes"]}
        snapshot.match("create-user", attributes)

        # add username attribute
        if add_attribute and username_type in ["email", "phone_number"]:
            new_attr = {"Name": username_type, "Value": username}
            client.admin_update_user_attributes(
                UserPoolId=pool_id, Username=username, UserAttributes=[new_attr]
            )

        # get user
        response = client.admin_get_user(UserPoolId=pool_id, Username=username)
        attributes = {attr["Name"]: attr["Value"] for attr in response["UserAttributes"]}
        snapshot.match("get-user", attributes)

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(paths=["$..Username"])
    @pytest.mark.parametrize("add_custom_prefix", [True, False])
    def test_user_pool_attributes(
        self,
        add_custom_prefix,
        create_user_pool,
        aws_client,
        snapshot,
        add_cognito_snapshot_transformers,
    ):
        pool_name = f"pool-{short_uid()}"
        attribute_name = f"{'custom:' if add_custom_prefix else ''}myattr1"
        result = create_user_pool(
            pool_name,
            Schema=[{"Name": attribute_name, "AttributeDataType": "String"}],
        )
        user_pool_id: str = result["Id"]
        client_name = f"client-{short_uid()}"
        aws_client.cognito_idp.create_user_pool_client(
            ClientName=client_name, UserPoolId=user_pool_id
        )

        # try to create user with invalid attribute
        user_name = f"username-{short_uid()}"
        with pytest.raises(ClientError) as ctx:
            aws_client.cognito_idp.admin_create_user(
                UserPoolId=user_pool_id,
                Username=user_name,
                UserAttributes=[{"Name": "foo", "Value": "bar"}],
            )
        snapshot.match("error-attr-not-in-schema", ctx.value.response)

        # create user with proper attribute
        result = aws_client.cognito_idp.admin_create_user(
            UserPoolId=user_pool_id,
            Username=user_name,
            UserAttributes=[{"Name": f"custom:{attribute_name}", "Value": "admin"}],
        )
        result["User"]["Attributes"] = {
            attr["Name"]: attr["Value"] for attr in result["User"]["Attributes"]
        }
        snapshot.match("user-attributes", result["User"])

        if add_custom_prefix:
            # attempt to create a user with "custom:myattr1", which should fail as it needs to be
            #  "custom:custom:myattr1" - the attribute in the schema is defined as "custom:myattr1" and
            #  Cognito appends another "custom:" to the attribute name, resulting in "custom:custom:myattr1".
            with pytest.raises(ClientError) as exc:
                aws_client.cognito_idp.admin_create_user(
                    UserPoolId=user_pool_id,
                    Username=user_name,
                    UserAttributes=[{"Name": attribute_name, "Value": "admin"}],
                )
            snapshot.match("error-attr-not-in-schema-custom-prefix", exc.value.response)

    @markers.aws.unknown
    def test_login_with_preferred_username(
        self, monkeypatch, create_user_pool, update_user_attributes, aws_client
    ):
        cognito_client = aws_client.cognito_idp

        # set an external hostname, to test
        external_hostname = f"host-{short_uid()}"
        monkeypatch.setattr(
            config,
            "LOCALSTACK_HOST",
            config.HostAndPort(external_hostname, config.GATEWAY_LISTEN[0].port),
        )

        # create user pool
        pool_name = f"pool-{short_uid()}"
        result = create_user_pool(
            pool_name,
            AliasAttributes=["preferred_username"],
            Schema=[
                {"Name": "foobar", "AttributeDataType": "String"},
                {"Name": "to_be_removed", "AttributeDataType": "String"},
            ],
        )
        pool_id = result["Id"]
        result = cognito_client.create_user_pool_client(ClientName="c1", UserPoolId=pool_id)
        client_id = result["UserPoolClient"]["ClientId"]

        # create user
        username = f"user-{short_uid()}"
        preferred_username = f"pref-{short_uid()}"
        password = f"Pass-{short_uid()}"
        user_attrs = [
            {"Name": "custom:to_be_removed", "Value": "foobar"},
            {"Name": "preferred_username", "Value": preferred_username},
            {"Name": "custom:foobar", "Value": "test123"},
        ]
        self._create_user(
            cognito_client, pool_id, username=username, password=password, UserAttributes=user_attrs
        )

        # remove attribute
        result = cognito_client.admin_delete_user_attributes(
            UserPoolId=pool_id, Username=username, UserAttributeNames=["custom:to_be_removed"]
        )
        assert result["ResponseMetadata"]["HTTPStatusCode"] == 200
        attrs = aws_client.cognito_idp.admin_get_user(UserPoolId=pool_id, Username=username)[
            "UserAttributes"
        ]
        assert attrs
        assert not [a for a in attrs if a["Name"] == "to_be_removed"]

        # add user to group
        group_name = "testgrp1"
        cognito_client.create_group(
            UserPoolId=pool_id, GroupName=group_name, Description="Test Group 1"
        )
        cognito_client.admin_add_user_to_group(
            UserPoolId=pool_id, Username=username, GroupName=group_name
        )

        def check_custom_attr(auth_result):
            id_token = auth_result["AuthenticationResult"]["IdToken"]
            id_token = cognito_utils.get_token_claims(id_token)
            assert id_token.get("custom:foobar") == "test123"
            # TODO: parity test the assertion for cognito:username below!
            assert id_token.get("cognito:username") in [username, preferred_username]
            assert id_token.get("cognito:groups") == [group_name]
            assert id_token.get("preferred_username") == preferred_username
            assert id_token.get("sub")
            assert f"://{external_hostname}" in id_token.get("iss")

        # initiate auth flows
        result = cognito_client.initiate_auth(
            AuthFlow="USER_PASSWORD_AUTH",
            ClientId=client_id,
            AuthParameters={"USERNAME": username, "PASSWORD": password},
        )
        assert "AuthenticationResult" in result
        check_custom_attr(result)
        result = cognito_client.initiate_auth(
            AuthFlow="USER_PASSWORD_AUTH",
            ClientId=client_id,
            AuthParameters={"USERNAME": preferred_username, "PASSWORD": password},
        )
        assert "AuthenticationResult" in result
        check_custom_attr(result)

        # test changing user attributes
        update_user_attributes(pool_id, username=username)
        update_user_attributes(pool_id, username=preferred_username)

        # delete user, then attempt to re-create user with same name (should work)
        cognito_client.admin_delete_user(UserPoolId=pool_id, Username=username)
        cognito_client.admin_create_user(
            UserPoolId=pool_id, Username=username, TemporaryPassword=password
        )
        cognito_client.admin_delete_user(UserPoolId=pool_id, Username=username)

    @markers.aws.validated
    def test_login_incorrect_password(self, create_user_pool_client, aws_client, snapshot):
        kwargs = {
            "ExplicitAuthFlows": ["ALLOW_ADMIN_USER_PASSWORD_AUTH", "ALLOW_REFRESH_TOKEN_AUTH"],
        }
        user_pool_result = create_user_pool_client(client_kwargs=kwargs)
        pool_client = user_pool_result.pool_client
        client_id, user_pool_id = pool_client["ClientId"], pool_client["UserPoolId"]

        username = f"user-{short_uid()}@localstack.cloud"
        aws_client.cognito_idp.sign_up(
            ClientId=client_id, Username=username, Password=TEST_PASSWORD
        )

        aws_client.cognito_idp.admin_confirm_sign_up(
            UserPoolId=pool_client["UserPoolId"], Username=username
        )
        with pytest.raises(ClientError) as ctx:
            aws_client.cognito_idp.admin_initiate_auth(
                AuthFlow="ADMIN_USER_PASSWORD_AUTH",
                ClientId=client_id,
                UserPoolId=user_pool_id,
                AuthParameters={"USERNAME": username, "PASSWORD": f"wrong-{short_uid()}"},
            )

        snapshot.match("incorrect-pass-error", ctx.value.response)

    @markers.aws.validated
    def test_auth_prevent_user_existence_error(self, create_user_pool_client, aws_client, snapshot):
        user_pool_client = create_user_pool_client(
            client_kwargs={
                "PreventUserExistenceErrors": "ENABLED",
                "ExplicitAuthFlows": ["ALLOW_ADMIN_USER_PASSWORD_AUTH", "ALLOW_REFRESH_TOKEN_AUTH"],
            }
        )
        client_id, pool_id = (
            user_pool_client.pool_client["ClientId"],
            user_pool_client.user_pool["Id"],
        )
        username, password = f"user-{short_uid()}", f"Pass!1-{short_uid()}"
        aws_client.cognito_idp.admin_create_user(UserPoolId=pool_id, Username=username)
        aws_client.cognito_idp.admin_set_user_password(
            UserPoolId=pool_id, Username=username, Password=password, Permanent=True
        )
        with pytest.raises(ClientError) as ctx:
            aws_client.cognito_idp.admin_initiate_auth(
                UserPoolId=pool_id,
                ClientId=client_id,
                AuthFlow="ADMIN_USER_PASSWORD_AUTH",
                AuthParameters={"USERNAME": "not-example-user", "PASSWORD": "password"},
            )
        snapshot.match("error", ctx.value.response)
        assert "NotAuthorizedException" in str(ctx.value)

    @markers.aws.validated
    def test_login_with_preferred_username_attr_change(self, create_user_pool_client, aws_client):
        resources = create_user_pool_client(pool_kwargs={"AliasAttributes": ["preferred_username"]})
        client_id = resources.pool_client["ClientId"]
        pool_id = resources.user_pool["Id"]

        aws_client.cognito_idp.add_custom_attributes(
            UserPoolId=pool_id,
            CustomAttributes=[
                {
                    "Name": "to_be_removed",
                    "AttributeDataType": "String",
                    "Mutable": True,
                    "StringAttributeConstraints": {
                        "MinLength": "1",
                        "MaxLength": "256",
                    },
                }
            ],
        )

        # create user
        username = f"user-{short_uid()}"
        username_alias = "alias-%s" % short_uid()
        user_pass = "Test123!"
        aws_client.cognito_idp.sign_up(
            ClientId=client_id,
            Username=username,
            Password=user_pass,
            UserAttributes=[{"Name": "custom:to_be_removed", "Value": "foobar"}],
        )
        aws_client.cognito_idp.admin_confirm_sign_up(UserPoolId=pool_id, Username=username)

        # update user attributes
        aws_client.cognito_idp.admin_update_user_attributes(
            UserPoolId=pool_id,
            Username=username,
            UserAttributes=[
                {"Name": "preferred_username", "Value": username_alias},
                {"Name": "custom:to_be_removed", "Value": "foobar"},
            ],
        )

        result = aws_client.cognito_idp.initiate_auth(
            AuthFlow="USER_PASSWORD_AUTH",
            ClientId=client_id,
            AuthParameters={"USERNAME": username_alias, "PASSWORD": user_pass},
        )["AuthenticationResult"]
        assert "AccessToken" in result
        access_token = result["AccessToken"]

        # delete user attribute
        result = aws_client.cognito_idp.delete_user_attributes(
            UserAttributeNames=["custom:to_be_removed"], AccessToken=access_token
        )
        assert result["ResponseMetadata"]["HTTPStatusCode"] == 200
        attrs = aws_client.cognito_idp.get_user(AccessToken=access_token)["UserAttributes"]
        assert attrs
        assert not [a for a in attrs if a["Name"] == "to_be_removed"]

        # verify that 'sub' matches in attributes
        token = cognito_utils.get_token_claims(access_token)
        sub = token.get("sub")
        response = aws_client.cognito_idp.admin_get_user(UserPoolId=pool_id, Username=username)
        attrs = response.get("UserAttributes", [])
        attrs = dict([(a["Name"], a["Value"]) for a in attrs])
        assert "sub" in attrs
        assert attrs["sub"] == sub

        # verify that user metadata can be retrieved
        details = aws_client.cognito_idp.get_user(AccessToken=access_token)
        assert details.get("Username") == username

        # test changing user attributes
        user = self._update_user_attributes_with_client(
            aws_client.cognito_idp, pool_id, username=username, attr_name="custom:to_be_removed"
        )
        modified_timestamp_1 = user["UserLastModifiedDate"]
        user = self._update_user_attributes_with_client(
            aws_client.cognito_idp,
            pool_id,
            username=username_alias,
            attr_name="custom:to_be_removed",
        )
        modified_timestamp_2 = user["UserLastModifiedDate"]
        # check that the user date was modified while modifying attributes
        assert modified_timestamp_1 != modified_timestamp_2

        # test sign out
        aws_client.cognito_idp.global_sign_out(AccessToken=access_token)
        with pytest.raises(Exception) as ctx:
            aws_client.cognito_idp.get_user(AccessToken=access_token)
        assert "NotAuthorizedException" in str(ctx.value)

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(paths=["$..Error.Message", "$..message"])
    def test_get_user_with_fake_access_token(self, snapshot, aws_client):
        with pytest.raises(ClientError) as ctx:
            aws_client.cognito_idp.get_user(AccessToken="fakeAccessToken")
        snapshot.match("error", ctx.value.response)
        assert "NotAuthorizedException" in str(ctx.value)

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(paths=["$..AuthenticationResult", "$..Session"])
    def test_auth_not_authorized_user(self, aws_client, create_user_pool_client, snapshot):
        user_pool_client = create_user_pool_client()
        client_id = user_pool_client.pool_client["ClientId"]
        pool_id = user_pool_client.user_pool["Id"]

        username = "test@example.com"
        password = "TmpTest123!"
        aws_client.cognito_idp.admin_create_user(
            UserPoolId=pool_id, Username=username, TemporaryPassword=password
        )

        aws_client.cognito_idp.admin_disable_user(UserPoolId=pool_id, Username=username)

        with pytest.raises(Exception) as ctx:
            aws_client.cognito_idp.initiate_auth(
                AuthFlow="USER_PASSWORD_AUTH",
                ClientId=client_id,
                AuthParameters={"USERNAME": username, "PASSWORD": password},
            )
        snapshot.match("user-disabled-exception", ctx.value.response)

        # enable the user and re-attempt the authorization
        aws_client.cognito_idp.admin_enable_user(UserPoolId=pool_id, Username=username)
        response = aws_client.cognito_idp.initiate_auth(
            AuthFlow="USER_PASSWORD_AUTH",
            ClientId=client_id,
            AuthParameters={"USERNAME": username, "PASSWORD": password},
        )
        snapshot.match("user-re-enabled-init-auth", response)

    @markers.aws.unknown
    def test_force_alias_creation(self, create_user_pool_client, aws_client):
        cognito_client = aws_client.cognito_idp

        user_pool_result = create_user_pool_client(pool_kwargs={"AliasAttributes": ["email"]})
        pool_client = user_pool_result.pool_client
        pool_id = user_pool_result.user_pool["Id"]
        client_id = pool_client["ClientId"]

        username1 = f"user1-{short_uid()}"
        username2 = f"user2-{short_uid()}"
        email = f"user-{short_uid()}@example.com"
        user_attrs = [{"Name": "email", "Value": email}]
        password = f"Password-{short_uid()}"

        # create first user
        self._create_user(
            cognito_client,
            pool_id,
            username=username1,
            password=password,
            UserAttributes=user_attrs,
        )

        # login with email should yield first user
        result = self._attempt_user_login(client_id, email, password)
        result = cognito_client.get_user(AccessToken=result["AccessToken"])
        assert result["Username"] == username1

        # create user with same email, without ForceAliasCreation (should fail)
        with pytest.raises(Exception) as ctx:
            cognito_client.admin_create_user(
                UserPoolId=pool_id, Username=username2, UserAttributes=user_attrs
            )
        assert "An account with the email already exists" in str(ctx.value)

        # create user with same email, with ForceAliasCreation=True (should succeed)
        self._create_user(
            cognito_client,
            pool_id,
            username=username2,
            password=password,
            UserAttributes=user_attrs,
            ForceAliasCreation=True,
        )

        # login with email should now yield the second user
        result = self._attempt_user_login(client_id, email, password)
        result = cognito_client.get_user(AccessToken=result["AccessToken"])
        assert result["Username"] == username2

    @markers.aws.unknown
    def test_request_with_invalid_username_or_pool_id(self, create_user_pool_client, aws_client):
        user_pool_result = create_user_pool_client()
        pool_client = user_pool_result.pool_client
        client_id = pool_client["ClientId"]
        pool_id = user_pool_result.user_pool["Id"]

        def _check(func: Callable, *args, **kwargs):
            with pytest.raises(Exception) as exc:
                func(*args, **kwargs)
            pool_id = kwargs.get("UserPoolId") or ""
            if pool_id.endswith("-invalid"):
                exc.match(rf"User pool {pool_id} does not exist")
            else:
                exc.match(r"(Unable to find user|User does not exist|non-existing)")

        region_name = aws_client.cognito_idp.meta.region_name
        for _pool_id in [pool_id, f"{region_name}-invalid"]:
            _check(
                aws_client.cognito_idp.initiate_auth,
                AuthFlow="USER_PASSWORD_AUTH",
                ClientId=client_id,
                AuthParameters={"USERNAME": "invalid-user", "PASSWORD": "Test1234!"},
            )
            kwargs = {"UserPoolId": _pool_id, "Username": "invalid-user"}
            _check(
                aws_client.cognito_idp.admin_delete_user_attributes,
                UserAttributeNames=["test"],
                **kwargs,
            )
            _check(aws_client.cognito_idp.admin_disable_user, **kwargs)
            _check(aws_client.cognito_idp.admin_delete_user, **kwargs)

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(
        paths=[
            "$..UserAttributes",
            "$..User.Attributes",
            "$.respond-to-auth-challenge.AuthenticationResult",
            "$.respond-to-auth-challenge.ChallengeParameters",
            "$.respond-to-auth-challenge.Session",
            "$.init-auth.AuthenticationResult",
        ]
    )
    def test_admin_change_password(self, create_user_pool_client, snapshot, aws_client):
        snapshot.add_transformer(
            [
                snapshot.transform.key_value("AccessToken"),
                snapshot.transform.key_value("IdToken"),
                snapshot.transform.key_value("RefreshToken"),
                snapshot.transform.key_value("Session"),
                snapshot.transform.jsonpath("$..UserAttributes[0].Value", "user-sub"),
            ]
        )
        resources = create_user_pool_client()
        client_id = resources.pool_client["ClientId"]
        pool_id = resources.user_pool["Id"]

        # create user
        username = "test@example.com"
        tmp_pass = "TmpTest123!"
        response = aws_client.cognito_idp.admin_create_user(
            UserPoolId=pool_id, Username=username, TemporaryPassword=tmp_pass
        )
        snapshot.match("create-user", response)
        assert response["User"]["UserCreateDate"] == response["User"]["UserLastModifiedDate"]
        user_created_date = response["User"]["UserCreateDate"]
        # initiate auth
        response = aws_client.cognito_idp.admin_initiate_auth(
            AuthFlow="ADMIN_NO_SRP_AUTH",
            ClientId=client_id,
            UserPoolId=pool_id,
            AuthParameters={"USERNAME": username, "PASSWORD": tmp_pass},
        )
        snapshot.match("init-auth", response)
        assert response["ChallengeName"] == "NEW_PASSWORD_REQUIRED"

        # respond to auth challenge
        session_id = response["Session"]
        new_pass = "Test123!"
        response = aws_client.cognito_idp.admin_respond_to_auth_challenge(
            ClientId=client_id,
            UserPoolId=pool_id,
            ChallengeName="NEW_PASSWORD_REQUIRED",
            ChallengeResponses={"USERNAME": username, "NEW_PASSWORD": new_pass},
            Session=session_id,
        )
        snapshot.match("respond-to-auth-challenge", response)
        assert not response.get("ChallengeName")
        assert not response.get("ChallengeParameters")
        assert response.get("AuthenticationResult", {}).get("AccessToken")

        # assert user status is confirmed
        response = aws_client.cognito_idp.admin_get_user(UserPoolId=pool_id, Username=username)
        assert response.get("UserStatus") == "CONFIRMED"
        snapshot.match("get-user", response)
        assert response["UserLastModifiedDate"] != user_created_date

        # assert login works with new password
        self._attempt_user_login(
            client_id, username, new_pass, cognito_client=aws_client.cognito_idp
        )

    @pytest.mark.parametrize("username", ["user-{short_uid}", "user-{short_uid}@example.com"])
    @markers.snapshot.skip_snapshot_verify(paths=["$..AuthenticationResult"])
    @markers.aws.validated
    def test_change_password(
        self,
        username,
        create_user_pool_client,
        signup_and_login_user,
        update_user_attributes,
        aws_client,
        snapshot,
    ):
        snapshot.add_transformer(
            [
                snapshot.transform.key_value("AccessToken"),
                snapshot.transform.key_value("IdToken"),
                snapshot.transform.key_value("RefreshToken"),
                snapshot.transform.key_value("Session"),
                snapshot.transform.jsonpath("$..ChallengeParameters.USER_ID_FOR_SRP", "user-sub"),
            ]
        )
        username = username.format(short_uid=short_uid())
        password = "Test123!"
        new_password = "Test123!new"

        user_pool_result = create_user_pool_client()
        pool_client = user_pool_result.pool_client
        client_id = pool_client["ClientId"]
        pool_id = user_pool_result.user_pool["Id"]
        signup_and_login_user(pool_client, username, password)

        result = aws_client.cognito_idp.initiate_auth(
            AuthFlow="USER_PASSWORD_AUTH",
            ClientId=client_id,
            AuthParameters={"USERNAME": username, "PASSWORD": password},
        )
        access_token = result.get("AuthenticationResult", {}).get("AccessToken")

        # test login after user password change
        result = aws_client.cognito_idp.change_password(
            PreviousPassword=password, ProposedPassword=new_password, AccessToken=access_token
        )
        snapshot.match("change-password", result)

        result = aws_client.cognito_idp.initiate_auth(
            AuthFlow="USER_PASSWORD_AUTH",
            ClientId=client_id,
            AuthParameters={"USERNAME": username, "PASSWORD": new_password},
        )
        snapshot.match("initiate-auth-change", result)

        with pytest.raises(ClientError) as ctx:
            aws_client.cognito_idp.initiate_auth(
                AuthFlow="USER_PASSWORD_AUTH",
                ClientId=client_id,
                AuthParameters={"USERNAME": username, "PASSWORD": password},
            )
        snapshot.match("auth-invalid-pass", ctx.value.response)

        # test login after admin password change
        new_password2 = f"NewSecretPass-{short_uid()}"
        aws_client.cognito_idp.admin_set_user_password(
            UserPoolId=pool_id, Username=username, Password=new_password2
        )

        result = aws_client.cognito_idp.admin_initiate_auth(
            AuthFlow="ADMIN_USER_PASSWORD_AUTH",
            ClientId=client_id,
            UserPoolId=pool_id,
            AuthParameters={"USERNAME": username, "PASSWORD": new_password2},
        )
        snapshot.match("admin-init-auth-change", result)

        with pytest.raises(ClientError) as ctx:
            aws_client.cognito_idp.admin_initiate_auth(
                AuthFlow="ADMIN_USER_PASSWORD_AUTH",
                ClientId=client_id,
                UserPoolId=pool_id,
                AuthParameters={"USERNAME": username, "PASSWORD": new_password},
            )
        snapshot.match("admin-auth-invalid-pass", ctx.value.response)

        # test changing user attributes
        update_user_attributes(pool_id, username=username)

    @markers.aws.validated
    def test_restore_forgotten_password(
        self, create_user_pool_client, signup_and_login_user, snapshot, aws_client
    ):
        snapshot.add_transformer(snapshot.transform.key_value("sub"))

        # create pool client and test user
        username = f"user-{short_uid()}"
        user_pool_result = create_user_pool_client()
        pool_client = user_pool_result.pool_client
        signup_and_login_user(pool_client, username, TEST_PASSWORD)
        client_id = pool_client["ClientId"]
        pool_id = user_pool_result.user_pool["Id"]

        # assert that email_verified field is set
        response = aws_client.cognito_idp.admin_get_user(UserPoolId=pool_id, Username=username)
        attrs_dict = {a["Name"]: a["Value"] for a in response.get("UserAttributes", [])}
        snapshot.match("get-user", attrs_dict)

        # assert that error is raised if no email present
        with pytest.raises(ClientError) as exc:
            aws_client.cognito_idp.forgot_password(ClientId=client_id, Username=username)
        response = exc.value.response
        response.pop("ResponseMetadata", None)
        snapshot.match("error1", response)
        aws_client.cognito_idp.admin_update_user_attributes(
            UserPoolId=pool_id,
            Username=username,
            UserAttributes=[{"Name": "email", "Value": "test@example.com"}],
        )

        if is_aws_cloud():
            # note: password reset currently not yet working against real AWS
            return

        # trigger forgot password flow
        aws_client.cognito_idp.forgot_password(ClientId=client_id, Username=username)
        code = cognito_utils.CONFIRMATION_CODES[-1]
        new_pass = f"{TEST_PASSWORD}new"
        aws_client.cognito_idp.confirm_forgot_password(
            ClientId=client_id, Username=username, ConfirmationCode=code, Password=new_pass
        )

        # assert that the new password works
        result = aws_client.cognito_idp.initiate_auth(
            AuthFlow="USER_PASSWORD_AUTH",
            ClientId=client_id,
            AuthParameters={"USERNAME": username, "PASSWORD": new_pass},
        )
        assert "AccessToken" in result.get("AuthenticationResult", {})

    # TODO LS does not return username
    @markers.snapshot.skip_snapshot_verify(paths=["$..username"])
    @markers.aws.validated
    def test_login_via_web_form(
        self,
        create_user_pool_client,
        signup_and_login_user,
        aws_client,
        region_name,
        snapshot,
        cognito_idp_endpoint,
    ):
        snapshot.add_transformers_list(
            [snapshot.transform.key_value("sub"), snapshot.transform.key_value("username")],
        )
        # create pool client and test user
        username = f"user-{short_uid()}"
        password = "Test123!"
        domain_name = f"ls-{short_uid()}"
        redirect_uri = "https://example.com"
        scopes = ["openid"]  # openid scope is required to get the claims from /oauth2/userInfo
        scope_as_str = " ".join(scopes)

        user_pool_result = create_user_pool_client(
            pool_kwargs={"Schema": [{"Name": "foo", "AttributeDataType": "String"}]},
            client_kwargs={
                "AllowedOAuthFlows": ["code"],
                "AllowedOAuthFlowsUserPoolClient": True,
                "AllowedOAuthScopes": scopes,
                "CallbackURLs": [redirect_uri],
                "ExplicitAuthFlows": ["USER_PASSWORD_AUTH"],
                "SupportedIdentityProviders": ["COGNITO"],
            },
        )
        user_pool = user_pool_result.user_pool
        pool_client = user_pool_result.pool_client
        cognito_pool_id = user_pool["Id"]
        client_id = pool_client["ClientId"]

        # Create a Domain
        aws_client.cognito_idp.create_user_pool_domain(
            Domain=domain_name, UserPoolId=cognito_pool_id
        )

        signup_and_login_user(
            pool_client=pool_client,
            username=username,
            password=password,
            attributes=[
                {"Name": "given_name", "Value": "John"},
                {"Name": "family_name", "Value": "Doe"},
                {"Name": "custom:foo", "Value": "bar"},
            ],
        )

        base_url = cognito_idp_endpoint(domain_name)

        # get login form, extract CSRF token
        login_url = (
            f"{base_url}/login?response_type=code"
            f"&redirect_uri={redirect_uri}"
            f"&client_id={client_id}&state=STATE"
            f"&scope={scope_as_str}"
        )
        result = retry(lambda: requests.get(login_url), retries=10)
        assert result.ok
        match = re.search('<input [^>]*name="_csrf" [^>]*value="([^"]+)"', to_str(result.content))
        csrf_token = match.group(1)

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Cookie": f"XSRF-TOKEN={csrf_token}",
        }
        data = {"_csrf": csrf_token, "username": username, "password": password}

        # log in via Web form
        result = requests.post(login_url, data=data, headers=headers, allow_redirects=False)
        # Extract code from login response
        code = parse_qs(urlparse(result.headers.get("Location")).query).get("code")[0]  # type: ignore
        assert "state=STATE" in result.headers.get("Location")

        # attempt login with invalid password
        data["password"] = "invalid_password"
        result = requests.post(login_url, data=data, headers=headers)
        # TODO aws returns 401
        assert result.status_code in [400, 401]
        assert "Incorrect username or password" in to_str(result.content)

        token_url = f"{base_url}/oauth2/token"
        user_info_url = f"{base_url}/oauth2/userInfo"

        # exchange code for token
        data = f"grant_type=authorization_code&client_id={client_id}&code={code}&redirect_uri={redirect_uri}"
        result = requests.post(token_url, data=data, headers=headers)
        payload: dict[str, str] = json.loads(result.content)
        access_token = payload["access_token"]

        # get user info
        headers = {"Authorization": f"Bearer {access_token}"}
        result = requests.get(user_info_url, headers=headers)
        snapshot.match("userInfo", result.json())

    @markers.snapshot.skip_snapshot_verify(paths=["$..version"])
    @markers.aws.validated
    def test_login_via_web_form_with_scopes(
        self,
        create_user_pool_client,
        signup_and_login_user,
        region_name,
        aws_client,
        cognito_idp_endpoint,
        snapshot,
        add_cognito_jwt_token_transformers,
    ):
        snapshot.add_transformer(snapshot.transform.key_value("username"))
        scopes = ["openid", "email"]
        scope_as_str = " ".join(scopes)
        username = f"user-{short_uid()}"
        password = "Test123!"
        redirect_uri = "https://example.com"
        user_pool_result = create_user_pool_client(
            client_kwargs={
                "AllowedOAuthScopes": scopes,
                "AllowedOAuthFlows": ["implicit"],
                "CallbackURLs": [redirect_uri],
                "ExplicitAuthFlows": ["USER_PASSWORD_AUTH"],
                "SupportedIdentityProviders": ["COGNITO"],
                "AllowedOAuthFlowsUserPoolClient": True,
            },
        )
        pool_client = user_pool_result.pool_client
        user_pool = user_pool_result.user_pool
        client_id = pool_client["ClientId"]
        cognito_pool_id = user_pool["Id"]

        # Create a Domain
        domain_name = f"ls-{short_uid()}"
        aws_client.cognito_idp.create_user_pool_domain(
            Domain=domain_name, UserPoolId=cognito_pool_id
        )
        signup_and_login_user(
            pool_client=pool_client,
            username=username,
            password=password,
        )

        base_url = cognito_idp_endpoint(domain_name)

        # get login form, extract CSRF token
        login_url = f"{base_url}/login?response_type=token&redirect_uri={redirect_uri}&client_id={client_id}&state=STATE"

        result = retry(lambda: requests.get(login_url), retries=10)
        assert result.ok
        match = re.search('<input [^>]*name="_csrf" [^>]*value="([^"]+)"', to_str(result.content))
        csrf_token = match.group(1)

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Cookie": f"XSRF-TOKEN={csrf_token}",
        }
        data = {"_csrf": csrf_token, "username": username, "password": password}

        def _get_access_token(token_scopes: str = "", is_valid_scope: bool = True):
            if token_scopes:
                token_scopes = f"&scope={token_scopes}"
            result = requests.post(
                login_url + token_scopes, data=data, headers=headers, allow_redirects=False
            )
            if not is_valid_scope:
                return result.status_code
            location = result.headers.get("Location")
            access_token = re.search("access_token=([^&#]+)", location).group(1)
            return jwt.decode(access_token, options={"verify_signature": False})

        # get token with no scopes
        token = _get_access_token()
        snapshot.match("no-scope-provided", token)

        # get token with all scopes
        token = _get_access_token(scope_as_str)
        snapshot.match("all-scopes", token)

        # get token with + delimiter
        token = _get_access_token("+".join(scopes))
        snapshot.match("plus-delimiter-scopes", token)

        # get token with email scope
        token = _get_access_token("email")
        snapshot.match("email-scope", token)

        # get token with invalid scope
        error_code = _get_access_token("invalid", is_valid_scope=False)
        # AWS answers 405 Method Not Allowed
        assert error_code in (500, 405)

    @markers.aws.validated
    def test_invalid_pool_client_parameters(self, create_user_pool_client, snapshot):
        # invalid request: invalid auth flows combination
        with pytest.raises(ClientError) as exc:
            create_user_pool_client(
                client_kwargs={
                    "AllowedOAuthScopes": ["email", "openid"],
                    "AllowedOAuthFlows": ["code", "client_credentials"],
                    "AllowedOAuthFlowsUserPoolClient": True,
                    "GenerateSecret": True,
                }
            )
        snapshot.match("client-error-1", exc.value.response)

        # invalid request: missing CallbackURLs
        with pytest.raises(ClientError) as exc:
            create_user_pool_client(
                client_kwargs={
                    "AllowedOAuthScopes": ["email", "openid"],
                    "AllowedOAuthFlows": ["code"],
                    "AllowedOAuthFlowsUserPoolClient": True,
                }
            )
        snapshot.match("client-error-2", exc.value.response)

        # invalid request: email is not supported with client_credentials flow
        with pytest.raises(ClientError) as exc:
            create_user_pool_client(
                client_kwargs={
                    "AllowedOAuthScopes": ["email", "openid"],
                    "AllowedOAuthFlows": ["client_credentials"],
                    "AllowedOAuthFlowsUserPoolClient": True,
                    "GenerateSecret": True,
                }
            )
        snapshot.match("client-error-3", exc.value.response)

        # invalid request: client_credentials flow can not be selected if client does not have a client secret
        with pytest.raises(ClientError) as exc:
            create_user_pool_client(
                client_kwargs={
                    "AllowedOAuthScopes": ["openid"],
                    "AllowedOAuthFlows": ["client_credentials"],
                    "AllowedOAuthFlowsUserPoolClient": True,
                }
            )
        snapshot.match("client-error-4", exc.value.response)

    @markers.aws.validated
    @pytest.mark.parametrize("payload_type", ["body", "query_params"])
    @pytest.mark.parametrize("oauth_flow", ["client_credentials", "code"])
    @markers.snapshot.skip_snapshot_verify(paths=["$..AllowedOAuthScopes"])
    def test_token_endpoint(
        self,
        payload_type,
        oauth_flow,
        create_user_pool_client,
        signup_and_login_user,
        aws_client,
        snapshot,
        add_cognito_snapshot_transformers,
    ):
        cognito_idp = aws_client.cognito_idp

        # create user pool and client
        callback_url = "https://localhost.localstack.cloud:4566"
        kwargs = {"GenerateSecret": True} if oauth_flow == "client_credentials" else {}
        if oauth_flow == "code":
            scopes = ["email", "openid"]
        else:
            resource_server_id = f"resource-server-{short_uid()}"
            scope_name = f"test-scope-{short_uid()}"
            custom_scope = f"{resource_server_id}/{scope_name}"
            scopes = [custom_scope]
            snapshot.add_transformer(
                snapshot.transform.regex(custom_scope, "<custom-scope>"), priority=-1
            )
        user_pool_result = create_user_pool_client(
            client_kwargs={
                "AllowedOAuthScopes": scopes,
                "AllowedOAuthFlows": [oauth_flow],
                "AllowedOAuthFlowsUserPoolClient": True,
                "CallbackURLs": [callback_url],
                **kwargs,
            }
        )
        pool_client = json_safe(user_pool_result.pool_client)
        pool_client["ExplicitAuthFlows"] = sorted(pool_client["ExplicitAuthFlows"])
        snapshot.match("pool-client", pool_client)
        client_id = pool_client["ClientId"]

        if oauth_flow == "code":
            username = f"user-{short_uid()}"
            password = "Test123!"
            signup_and_login_user(pool_client, username, password)

        # create user pool domain
        domain_name = f"d-{short_uid()}"
        cognito_idp.create_user_pool_domain(
            Domain=domain_name, UserPoolId=user_pool_result.user_pool["Id"]
        )

        if is_aws_cloud():
            fq_domain_name = f"{domain_name}.auth.{cognito_idp.meta.region_name}.amazoncognito.com"
            wait_until_domain_name_resolves(fq_domain_name)
            # TODO: the code below currently doesn't work against AWS - we should look into implementing
            #  a browser-based approach (e.g., using Selenium) to run the actual login actions
            if oauth_flow != "client_credentials":
                return
            base_url = f"https://{fq_domain_name}"
        else:
            edge_url = config.internal_service_url(f"cognito-idp.{constants.LOCALHOST_HOSTNAME}")
            base_url = f"{edge_url}/_aws/cognito-idp"

        login_url = f"{base_url}/login"
        logout_url = f"{base_url}/logout"
        token_url = f"{base_url}/oauth2/token"

        def _run_browser_login():
            url = (
                f"{login_url}?redirect_uri={callback_url}&client_id={client_id}&response_type=code"
            )
            data = f"username={username}&password={password}"
            result = requests.post(url, data=data)
            assert result.status_code == 200
            assert f"{COOKIE_TOKEN}=" in result.headers.get("Set-Cookie", "")
            location = result.headers.get("Location", "")
            query_params = cognito_utils.parse_query_string(location.partition("?")[2])
            return query_params

        # 1. simulate a browser login request
        if oauth_flow == "code":
            query_params = _run_browser_login()
            assert query_params

        def _request_token_and_scopes(
            params: dict, headers: dict | None = None, url: str | None = None
        ) -> [dict, list]:
            req_url = url or token_url
            headers = headers or {}
            headers.update({"Content-Type": "application/x-www-form-urlencoded"})
            if payload_type == "query_params":
                result = requests.post(req_url, params=params, headers=headers or {})
            else:
                result = requests.post(req_url, data=params, headers=headers or {})
            if not result.ok:
                raise Exception(to_str(result.content))
            res_content = json.loads(to_str(result.content))
            assert result.status_code == 200

            # assert that (only) the expected fields are contained
            # see https://docs.aws.amazon.com/cognito/latest/developerguide/token-endpoint.html
            expected = ["access_token", "token_type", "expires_in"]
            if params["grant_type"] != "client_credentials":
                expected += ["id_token"]
            if params["grant_type"] == "authorization_code":
                expected += ["refresh_token"]
            assert set(res_content.keys()) == set(expected)

            # assert that claims are contained in the access token
            claims = cognito_utils.get_token_claims(res_content["access_token"])
            scope = claims.get("scope") or ""
            if oauth_flow != "client_credentials":
                assert "email" in scope
                assert "openid" in scope
            return res_content.get("refresh_token"), scope.split()

        scope = "email openid"

        # 2.a request a token via client_credentials
        if oauth_flow == "client_credentials":
            client_secret = pool_client["ClientSecret"]
            data = {
                "grant_type": "client_credentials",
                "client_id": client_id,
                "client_secret": client_secret,
                "scope": custom_scope,
                "redirect_uri": callback_url,
            }
            _, scopes = _request_token_and_scopes(params=data)
            snapshot.match("scopes", scopes)
            auth_token = to_str(base64.b64encode(to_bytes(f"{client_id}:{client_secret}")))
            refresh_token, _ = _request_token_and_scopes(
                url=f"{token_url}",
                params=data,
                headers={"Authorization": f"Basic {auth_token}"},
            )
            with pytest.raises(Exception) as exc:
                data["client_secret"] = "invalid"
                _request_token_and_scopes(params=data)
                exc.match("status 400")
                exc.match("invalid_client")

        # 2.b request a token via authorization_code
        if oauth_flow == "code":
            query_params = _run_browser_login()
            code = query_params["code"]
            data = {
                "grant_type": "authorization_code",
                "code": code,
                "client_id": client_id,
                "scope": scope,
                "redirect_uri": callback_url,
            }
            refresh_token = _request_token_and_scopes(params=data)

        # 3. request a new token via refresh_token
        if oauth_flow == "code":
            for i in range(2):
                data = {
                    "grant_type": "refresh_token",
                    "client_id": client_id,
                    "refresh_token": refresh_token,
                    "redirect_uri": callback_url,
                }
                _request_token_and_scopes(params=data)

        # 4. call /logout endpoint, assert that users are logged out (i.e., tokens no longer work)
        if oauth_flow == "code":
            url = f"{logout_url}?client_id={client_id}"
            cookie_token = {"refresh_token": refresh_token, "username": username}
            cookie_token = to_str(base64.b64encode(to_bytes(json.dumps(cookie_token))))
            headers = {"Cookie": f"{COOKIE_TOKEN}={cookie_token}"}
            result = requests.get(url, headers=headers)
            assert result
            data = {
                "grant_type": "refresh_token",
                "client_id": client_id,
                "refresh_token": refresh_token,
                "redirect_uri": callback_url,
            }
            result = requests.post(
                token_url, data=data, headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            assert "Invalid refresh token" in to_str(result.content)
            assert result.status_code == 403

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(paths=["$..client_id"])
    def test_authorize_redirects_to_login(self, aws_client, snapshot, create_user_pool_client):
        # create user pool
        callback_url = "https://localstack.cloud"
        pool_kwargs = {"UsernameAttributes": ["phone_number", "email"]}
        client_kwargs = {
            "ExplicitAuthFlows": [
                "ALLOW_ADMIN_USER_PASSWORD_AUTH",
                "ALLOW_USER_PASSWORD_AUTH",
                "ALLOW_USER_SRP_AUTH",
                "ALLOW_REFRESH_TOKEN_AUTH",
            ],
            "AllowedOAuthScopes": [
                "aws.cognito.signin.user.admin",
            ],
            "AllowedOAuthFlows": ["code"],
            "CallbackURLs": [callback_url],
        }
        user_pool_result = create_user_pool_client(
            pool_kwargs=pool_kwargs, client_kwargs=client_kwargs
        )
        pool_client = user_pool_result.pool_client
        pool_id = user_pool_result.user_pool["Id"]
        client_id = pool_client["ClientId"]
        # create domain endpoint
        domain_name = f"ls-{short_uid()}"
        aws_client.cognito_idp.create_user_pool_domain(Domain=domain_name, UserPoolId=pool_id)

        if is_aws_cloud():
            region_name = aws_client.lambda_.meta.region_name
            base_url = f"https://{domain_name}.auth.{region_name}.amazoncognito.com"
            # time for the DNS to propagate
            time.sleep(30)
        else:
            base_url = config.internal_service_url(
                host=f"cognito-idp.{constants.LOCALHOST_HOSTNAME}"
            )
            base_url = f"{base_url}/_aws/cognito-idp"

        endpoint_url = f"{base_url}/oauth2/authorize"

        state = "dbl67v3dOztFKn7p1XIxi2XWuIu4ritM"
        params = {
            "redirect_uri": callback_url,
            "client_id": client_id,
            "response_type": "code",
            "state": state,
            "scope": "aws.cognito.signin.user.admin",
        }

        params_with_cognito = {**params, "identity_provider": "COGNITO"}

        for _param in [params, params_with_cognito]:
            response = requests.get(endpoint_url, params=_param, allow_redirects=False)
            assert response.status_code in [301, 302]
            location = response.headers.get("Location")
            location = urllib.parse.unquote(location)
            assert "login" in location
            query = parse_qs(urlparse(location).query)
            assert client_id == query.get("client_id")[0]
            assert callback_url == query.get("redirect_uri")[0]
            assert state == query.get("state")[0]
            suffix = _param.get("identity_provider", "no-provider")
            snapshot.match(f"query-{suffix}", query)

    @markers.aws.validated
    def test_custom_scopes(self, create_user_pool, aws_client, snapshot):
        pool_name = f"pool-{short_uid()}"
        client_name = f"client-{short_uid()}"
        user_pool = create_user_pool(pool_name=pool_name)
        pool_id = user_pool["Id"]
        server_name = f"srv-{short_uid()}"

        with pytest.raises(Exception) as exc:
            aws_client.cognito_idp.create_user_pool_client(
                UserPoolId=pool_id,
                ClientName=client_name,
                AllowedOAuthScopes=["test/scope1"],
                GenerateSecret=True,
            )
        exc.match("Invalid scope requested")
        exc.match("ScopeDoesNotExistException")

        with pytest.raises(Exception) as exc:
            aws_client.cognito_idp.create_resource_server(
                UserPoolId=pool_id,
                Identifier="http://test123",
                Name=server_name,
                Scopes=[
                    {"ScopeName": "test/invalid-no-slash-allowed", "ScopeDescription": "scope 1"},
                ],
            )
        exc.match("InvalidParameterException")
        exc.match("Value 'test/invalid-no-slash-allowed' at")
        exc.match("Member must satisfy regular expression")

        # create resource server
        aws_client.cognito_idp.create_resource_server(
            UserPoolId=pool_id,
            Identifier="http://test123",
            Name=server_name,
            Scopes=[
                {"ScopeName": "scope1", "ScopeDescription": "scope 1"},
                {"ScopeName": "scope.2", "ScopeDescription": "scope 2"},
                {"ScopeName": "scope_3", "ScopeDescription": "scope 3"},
            ],
        )

        # create domain endpoint
        domain_name = f"ls-{short_uid()}"
        aws_client.cognito_idp.create_user_pool_domain(Domain=domain_name, UserPoolId=pool_id)
        user_pool_domain = aws_client.cognito_idp.describe_user_pool_domain(Domain=domain_name)
        # snapshot.match("user_pool_domain", user_pool_domain)

        # create pool client
        client = aws_client.cognito_idp.create_user_pool_client(
            UserPoolId=pool_id,
            ClientName=client_name,
            AllowedOAuthScopes=["http://test123/scope1", "http://test123/scope.2"],
            AllowedOAuthFlows=["client_credentials"],
            AllowedOAuthFlowsUserPoolClient=True,
            GenerateSecret=True,
        )["UserPoolClient"]

        # request access token
        if is_aws_cloud():
            region_name = aws_client.lambda_.meta.region_name
            base_url = f"https://{domain_name}.auth.{region_name}.amazoncognito.com"
        else:
            base_url = config.internal_service_url(
                host=f"cognito-idp.{constants.LOCALHOST_HOSTNAME}"
            )
            base_url = f"{base_url}/_aws/cognito-idp"

        token_url = f"{base_url}/oauth2/token"

        def _request(scope: str | None = None) -> dict:
            request_data = (
                f"grant_type=client_credentials&client_id={client['ClientId']}&"
                f"client_secret={client['ClientSecret']}&redirect_uri=..."
            )
            if scope:
                request_data = f"{request_data}&scope={scope}"
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            result = requests.post(token_url, data=request_data, headers=headers)
            assert result.ok, f"error: status {result.status_code}, {result.content}"
            content = json.loads(to_str(result.content))
            access_token = content.get("access_token")
            assert access_token, "access token not found"
            claims = jwt.decode(access_token, options={"verify_signature": False}) or {}
            assert content.get("token_type") == "Bearer"
            return claims

        if is_aws_cloud():
            time.sleep(20)  # sleep some time for DNS name to propagate

        # request valid scope
        claims = retry(lambda: _request("http://test123/scope1"), sleep=1, retries=30).get(
            "scope", {}
        )
        snapshot.match("claims-one", claims)
        # request invalid scopes
        for scope in ["scope1", "http://test123/scope-invalid"]:
            with pytest.raises(Exception) as exc:
                _request(scope)
            exc.match("status 400")
            exc.match("invalid_scope")

        # no scope requested; all authorized scopes should be returned
        claims = retry(lambda: _request(), sleep=1, retries=30).get("scope", {})
        snapshot.match("claims-all", claims)

    @markers.aws.unknown
    def test_get_signing_certificate(self, create_user_pool_client, aws_client):
        user_pool_result = create_user_pool_client()
        user_pool = user_pool_result.user_pool
        result = aws_client.cognito_idp.get_signing_certificate(UserPoolId=user_pool["Id"])
        cert = result["Certificate"]
        assert cert.startswith("MII")
        assert "--BEGIN CERTIFICATE--" not in cert

    @markers.aws.validated
    def test_update_user_mfa_preferences(
        self,
        create_user_pool_client,
        create_user_pool,
        sns_create_topic,
        signup_and_login_user,
        aws_client,
        add_cognito_snapshot_transformers,
        snapshot,
    ):
        snapshot.add_transformer(snapshot.transform.key_value("Username"))

        user_pool_result = create_user_pool_client()

        # create pool client and test user, and obtain access token
        username = f"user-{short_uid()}"
        password = "Test123!"
        pool_client = user_pool_result.pool_client
        pool_id = pool_client["UserPoolId"]
        signup_and_login_user(pool_client, username=username, password=password)
        result = aws_client.cognito_idp.initiate_auth(
            AuthFlow="USER_PASSWORD_AUTH",
            ClientId=pool_client["ClientId"],
            AuthParameters={"USERNAME": username, "PASSWORD": password},
        )
        access_token = result.get("AuthenticationResult", {}).get("AccessToken")

        # set user phone number
        new_attrs = [
            {"Name": "phone_number", "Value": "+10000000"},
            {"Name": "phone_number_verified", "Value": "true"},
        ]
        aws_client.cognito_idp.admin_update_user_attributes(
            UserPoolId=pool_id, Username=username, UserAttributes=new_attrs
        )
        response = aws_client.cognito_idp.admin_get_user(UserPoolId=pool_id, Username=username)
        response["UserAttributes"] = {
            attr["Name"]: attr["Value"] for attr in response["UserAttributes"]
        }
        snapshot.match("get-user-1", response)

        # test MFA config updates - user-triggered update
        mfa_prefs = {"SMSMfaSettings": {"Enabled": True, "PreferredMfa": False}}
        aws_client.cognito_idp.set_user_mfa_preference(AccessToken=access_token, **mfa_prefs)
        response = aws_client.cognito_idp.admin_get_user(UserPoolId=pool_id, Username=username)
        response["UserAttributes"] = {
            attr["Name"]: attr["Value"] for attr in response["UserAttributes"]
        }
        snapshot.match("updated-user-1", response)

        # test MFA config updates - admin-triggered update
        mfa_prefs["SMSMfaSettings"]["PreferredMfa"] = True
        aws_client.cognito_idp.admin_set_user_mfa_preference(
            Username=username, UserPoolId=pool_id, **mfa_prefs
        )
        response = aws_client.cognito_idp.admin_get_user(UserPoolId=pool_id, Username=username)
        response["UserAttributes"] = {
            attr["Name"]: attr["Value"] for attr in response["UserAttributes"]
        }
        snapshot.match("updated-user-2", response)

    @markers.aws.unknown
    def test_mfa_sms_config(
        self, create_user_pool_client, create_user_pool, signup_and_login_user, aws_client
    ):
        user_pool1 = create_user_pool()
        pool_id1 = user_pool1["Id"]

        # set user pool config
        sms_config = {
            "SmsAuthenticationMessage": "test auth message",
            "SmsConfiguration": {
                "SnsCallerArn": "arn:aws:sns:test12345",
                "ExternalId": "test-id-123",
            },
        }
        aws_client.cognito_idp.set_user_pool_mfa_config(
            UserPoolId=pool_id1,
            SmsMfaConfiguration=sms_config,
            SoftwareTokenMfaConfiguration={"Enabled": True},
            MfaConfiguration="OPTIONAL",
        )

        # assert user pool config
        mfa_config = aws_client.cognito_idp.get_user_pool_mfa_config(UserPoolId=pool_id1)
        assert mfa_config["SmsMfaConfiguration"] == sms_config
        assert mfa_config["SoftwareTokenMfaConfiguration"] == {"Enabled": True}
        assert mfa_config["MfaConfiguration"] == "OPTIONAL"

        # create pool client and test user, and obtain access token
        username = f"user-{short_uid()}"
        password = "Test123!"
        user_pool_result = create_user_pool_client()
        pool_client = user_pool_result.pool_client
        pool_id2 = pool_client["UserPoolId"]
        signup_and_login_user(pool_client, username, password)
        result = aws_client.cognito_idp.initiate_auth(
            AuthFlow="USER_PASSWORD_AUTH",
            ClientId=pool_client["ClientId"],
            AuthParameters={"USERNAME": username, "PASSWORD": password},
        )
        access_token = result.get("AuthenticationResult", {}).get("AccessToken")

        # set user phone number
        new_attrs = [
            {"Name": "phone_number", "Value": "+10000000"},
            {"Name": "phone_number_verified", "Value": "true"},
        ]
        aws_client.cognito_idp.admin_update_user_attributes(
            UserPoolId=pool_id2, Username=username, UserAttributes=new_attrs
        )

        # test MFA configs
        mfa_prefs = {
            "SMSMfaSettings": {"Enabled": True, "PreferredMfa": True},
            "SoftwareTokenMfaSettings": {"Enabled": True, "PreferredMfa": False},
        }
        aws_client.cognito_idp.set_user_mfa_preference(AccessToken=access_token, **mfa_prefs)
        aws_client.cognito_idp.admin_set_user_mfa_preference(
            Username=username, UserPoolId=pool_id2, **mfa_prefs
        )

        # test auth flow - should respond with an MFA challenge
        client_id = pool_client["ClientId"]
        result = aws_client.cognito_idp.initiate_auth(
            AuthFlow="USER_PASSWORD_AUTH",
            ClientId=client_id,
            AuthParameters={"USERNAME": username, "PASSWORD": password},
        )
        assert result.get("ChallengeName") == "SMS_MFA"

        # respond to MFA auth challenge
        session = result["Session"]
        result = aws_client.cognito_idp.admin_respond_to_auth_challenge(
            ClientId=client_id,
            UserPoolId=pool_id2,
            ChallengeName="SMS_MFA",
            ChallengeResponses={"SMS_MFA_CODE": "xxxxxx", "USERNAME": username},
            Session=session,
        )
        assert result["AuthenticationResult"]["AccessToken"]
        assert result["AuthenticationResult"]["RefreshToken"]
        assert result["AuthenticationResult"]["IdToken"]

    @markers.aws.unknown
    def test_software_token_mfa(self, create_user_pool_client, aws_client):
        """
        TODO: for this to behave in the same way as AWS, MFA must be turned on when creating user pool.
        This will also need an SMS configuration and auto verification for phone number.
        A possible way of doing this is updating the create_user_pool_client fixture so that we can pass a
        MFAConfiguration (e.g. "ON") and the fixture adds default values for the SMS configuration and phone number
        auto verification.
        MFA preferences will also need to be updated so that SoftwareTokenMfaSettings is enabled.
        """
        username = f"user-{short_uid()}"
        password = "Password1!"

        result: UserPoolAndClient = create_user_pool_client()
        client_id = result.pool_client["ClientId"]
        user_pool_id = result.user_pool["Id"]

        aws_client.cognito_idp.admin_create_user(
            UserPoolId=user_pool_id,
            Username=username,
        )
        aws_client.cognito_idp.admin_set_user_password(
            UserPoolId=user_pool_id, Username=username, Password=password, Permanent=True
        )
        response = aws_client.cognito_idp.initiate_auth(
            AuthFlow="USER_PASSWORD_AUTH",
            ClientId=client_id,
            AuthParameters={"USERNAME": username, "PASSWORD": password},
        )
        access_token = response.get("AuthenticationResult", {}).get("AccessToken")
        assert access_token

        with pytest.raises(Exception) as exc:
            aws_client.cognito_idp.associate_software_token(Session="non-empty-session-string")
        exc.match("InvalidParameterException")
        exc.match("Session parameter is not yet supported")

        with pytest.raises(Exception) as exc:
            aws_client.cognito_idp.associate_software_token(AccessToken="invalid_access_token")
        exc.match("NotAuthorizedException")
        exc.match("Could not verify signature for Access Token")

        with pytest.raises(Exception) as exc:
            aws_client.cognito_idp.associate_software_token()
        exc.match("NotAuthorizedException")
        exc.match("Invalid Access Token")

        # TOTP is verified successfully when created with the correct secret code / software token.
        software_token = aws_client.cognito_idp.associate_software_token(AccessToken=access_token)
        user_totp_code = pyotp.TOTP(software_token["SecretCode"]).now()
        verification_response = aws_client.cognito_idp.verify_software_token(
            AccessToken=access_token, UserCode=user_totp_code
        )
        assert verification_response["Status"] == "SUCCESS"

        with pytest.raises(Exception) as exc:
            aws_client.cognito_idp.verify_software_token(
                AccessToken=access_token, UserCode="code_that_will_fail"
            )
        exc.match("EnableSoftwareTokenMFAException")
        exc.match("Code mismatch")

    @markers.aws.unknown
    def test_describe_user_pool(self, create_user_pool_client, aws_client):
        resources = create_user_pool_client()
        pool_id = resources.user_pool["Id"]

        usernames = ["test@example.com", "test1@example.com", "test2@example.com"]
        passwords = ["TmpTest123!"] * len(usernames)

        for username, tmp_pass in zip(usernames, passwords):
            aws_client.cognito_idp.admin_create_user(
                UserPoolId=pool_id, Username=username, TemporaryPassword=tmp_pass
            )
            aws_client.cognito_idp.admin_set_user_password(
                UserPoolId=pool_id, Username=username, Password=tmp_pass, Permanent=True
            )

        response = aws_client.cognito_idp.describe_user_pool(UserPoolId=pool_id)
        assert "EstimatedNumberOfUsers" in response["UserPool"]

    @markers.aws.validated
    def test_create_user_group_in_pool(self, create_role, snapshot, cleanups, aws_client):
        pool_name = f"pool-{short_uid()}"
        snapshot.add_transformer(snapshot.transform.regex(pool_name, "<pool-name>"))
        create_user_pool_response = aws_client.cognito_idp.create_user_pool(PoolName=pool_name)
        user_pool_id = create_user_pool_response["UserPool"]["Id"]
        snapshot.add_transformer(snapshot.transform.regex(user_pool_id, "<user-pool-id>"))
        cleanups.append(lambda: aws_client.cognito_idp.delete_user_pool(UserPoolId=user_pool_id))
        snapshot.match("create_user_pool", create_user_pool_response)

        group_name = f"group-{short_uid()}"
        snapshot.add_transformer(snapshot.transform.regex(group_name, "<group-name:1>"))
        create_group_response = aws_client.cognito_idp.create_group(
            UserPoolId=user_pool_id, GroupName=group_name, Description="Managed by Terraform"
        )
        cleanups.append(
            lambda: aws_client.cognito_idp.delete_group(
                GroupName=group_name, UserPoolId=user_pool_id
            )
        )
        snapshot.match("create_group", create_group_response)

        get_group_response = aws_client.cognito_idp.get_group(
            GroupName=group_name, UserPoolId=user_pool_id
        )
        snapshot.match("get_group", get_group_response)

        role_name = f"Cognito-role-{short_uid()}"
        snapshot.add_transformer(snapshot.transform.regex(role_name, "<role-name>"))
        cognito_role_arn = create_role(
            RoleName=role_name, AssumeRolePolicyDocument=json.dumps(COGNITO_ASSUME_ROLE_POLICY)
        )["Role"]["Arn"]
        group_name_2 = f"group-{short_uid()}"
        snapshot.add_transformer(snapshot.transform.regex(group_name_2, "<group-name:2>"))
        create_group_response_arn = aws_client.cognito_idp.create_group(
            UserPoolId=user_pool_id, GroupName=group_name_2, RoleArn=cognito_role_arn
        )
        cleanups.append(
            lambda: aws_client.cognito_idp.delete_group(
                GroupName=group_name_2, UserPoolId=user_pool_id
            )
        )
        snapshot.match("create_group_with_role_arn", create_group_response_arn)

        group_name_3 = f"group-{short_uid()}"
        snapshot.add_transformer(snapshot.transform.regex(group_name_3, "<group-name:3>"))
        create_group_response_arn_doesnotexist = aws_client.cognito_idp.create_group(
            UserPoolId=user_pool_id,
            GroupName=group_name_3,
            RoleArn=f"{cognito_role_arn}-doesnotexist",
        )
        snapshot.match(
            "create_group_with_role_arn_doesnotexist", create_group_response_arn_doesnotexist
        )

    @markers.aws.unknown
    def test_user_groups(self, create_user_pool_client, signup_and_login_user, aws_client):
        username = f"user-{short_uid()}"
        password = "Test123!"

        user_pool_result = create_user_pool_client()
        pool_client = user_pool_result.pool_client
        pool_id = user_pool_result.user_pool["Id"]
        signup_and_login_user(pool_client, username, password)

        # create new group
        group_name = "group1"
        result = aws_client.cognito_idp.create_group(
            UserPoolId=pool_id, GroupName=group_name, Description="Test Group 1"
        )
        assert result.get("Group", {}).get("GroupName"), group_name
        groups = aws_client.cognito_idp.list_groups(UserPoolId=pool_id)["Groups"]
        existing = [g for g in groups if g["GroupName"] == group_name]
        assert len(existing) == 1

        # add user to group (should be idempotent)
        for i in range(3):
            aws_client.cognito_idp.admin_add_user_to_group(
                UserPoolId=pool_id, Username=username, GroupName=group_name
            )

        # list groups for user
        groups = aws_client.cognito_idp.admin_list_groups_for_user(
            Username=username, UserPoolId=pool_id
        )["Groups"]
        existing = [g for g in groups if g["GroupName"] == group_name]
        assert len(existing) == 1

        # list users for group
        users = aws_client.cognito_idp.list_users_in_group(
            GroupName=group_name, UserPoolId=pool_id
        )["Users"]
        existing = [u for u in users if u["Username"] == username]
        assert len(existing) == 1

        # delete the group
        aws_client.cognito_idp.delete_group(UserPoolId=pool_id, GroupName=group_name)

    @markers.aws.validated
    def test_user_group_deletion_with_non_existing_pool(self, aws_client):
        with pytest.raises(Exception) as ctx:
            aws_client.cognito_idp.delete_group(UserPoolId="Non_Existing", GroupName="Non_Existing")
        assert "ResourceNotFoundException" in str(ctx.value)
        assert "error occurred" in str(ctx.value)
        assert "User pool Non_Existing does not exist" in str(ctx.value)

    @markers.aws.unknown
    def test_user_group_deletion_with_non_existing_group(self, create_user_pool_client, aws_client):
        user_pool_result = create_user_pool_client()
        user_pool = user_pool_result.user_pool
        pool_id = user_pool["Id"]
        with pytest.raises(Exception) as ctx:
            aws_client.cognito_idp.delete_group(UserPoolId=pool_id, GroupName="Non-Existing")
        assert "error occurred" in str(ctx.value)
        assert "non-existing group" in str(ctx.value)

    @markers.aws.unknown
    def test_user_login_before_confirmation(self, create_user_pool_client, aws_client):
        username = f"user-{short_uid()}@example.com"
        password = "Test123!"

        # create pool and user
        user_pool_result = create_user_pool_client()
        pool_client = user_pool_result.pool_client
        client_id = pool_client["ClientId"]
        result = aws_client.cognito_idp.sign_up(
            ClientId=client_id,
            Username=username,
            Password=password,
        )
        assert result.get("UserConfirmed") is False

        def _attempt_login():
            return self._attempt_user_login(client_id, username, password)

        # assert that login fails prior to confirmation
        with pytest.raises(Exception) as exc:
            _attempt_login()
        exc.match("NotAuthorizedException")
        exc.match("status UNCONFIRMED")

        # assert that login passes after confirmation
        aws_client.cognito_idp.admin_confirm_sign_up(
            UserPoolId=pool_client["UserPoolId"], Username=username
        )
        assert _attempt_login()

    @markers.snapshot.skip_snapshot_verify
    @markers.aws.validated
    def test_create_admin_user_with_duplicate_email_but_valid_userconfiguration(
        self, snapshot, cleanups, aws_client, add_cognito_snapshot_transformers
    ):
        pool_name = f"pool-{short_uid()}"
        pool_client_name = f"pool-client-{short_uid()}"
        email = f"{short_uid()}@example.com"
        email_pass = f"Pass-{short_uid()}"

        snapshot.add_transformer(snapshot.transform.regex(email, "<email>"))
        snapshot.add_transformer(snapshot.transform.regex(pool_name, "<pool-name>"))
        snapshot.add_transformer(SortingTransformer("Attributes", lambda x: x["Name"]))

        # create user pool
        create_user_pool_response = aws_client.cognito_idp.create_user_pool(
            PoolName=pool_name,
            AliasAttributes=["preferred_username"],
            AutoVerifiedAttributes=["email"],
            UsernameConfiguration={"CaseSensitive": False},
        )
        snapshot.match("create_user_pool_response", create_user_pool_response)
        pool_id = create_user_pool_response["UserPool"]["Id"]
        cleanups.append(lambda: aws_client.cognito_idp.delete_user_pool(UserPoolId=pool_id))

        # create user pool client
        create_user_pool_client_response = aws_client.cognito_idp.create_user_pool_client(
            UserPoolId=pool_id, ClientName=pool_client_name
        )
        client_id = create_user_pool_client_response["UserPoolClient"]["ClientId"]
        snapshot.match("create_user_pool_client_response", create_user_pool_client_response)
        cleanups.append(
            lambda: aws_client.cognito_idp.delete_user_pool_client(
                UserPoolId=pool_id, ClientId=client_id
            )
        )

        # create user with username1
        admin_create_user_username1_result = aws_client.cognito_idp.admin_create_user(
            UserPoolId=pool_id,
            Username="username1",
            UserAttributes=[{"Name": "email", "Value": email}],
            TemporaryPassword=email_pass,
        )
        snapshot.add_transformer(snapshot.transform.regex(PATTERN_UUID, "<uuid>"))
        snapshot.match("admin_create_user_username1_result", admin_create_user_username1_result)

        # create user with username2 (but same email)
        admin_create_user_username2_result = aws_client.cognito_idp.admin_create_user(
            UserPoolId=pool_id,
            Username="username2",
            UserAttributes=[{"Name": "email", "Value": email}],
            TemporaryPassword=email_pass,
        )
        snapshot.match("admin_create_user_username2_result", admin_create_user_username2_result)

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify
    def test_create_admin_user_with_duplicate_email(self, snapshot, cleanups, aws_client):
        pool_name = f"pool-{short_uid()}"
        pool_client_name = f"pool-client-{short_uid()}"
        email = f"{short_uid()}@example.com"
        email_pass = f"Pass-{short_uid()}"

        snapshot.add_transformer(snapshot.transform.key_value("ClientId"))
        snapshot.add_transformer(snapshot.transform.key_value("UserPoolId"))
        snapshot.add_transformer(snapshot.transform.key_value("Username"))
        snapshot.add_transformer(snapshot.transform.key_value("ClientName"))
        snapshot.add_transformer(snapshot.transform.regex(email, "<email>"))
        snapshot.add_transformer(snapshot.transform.regex(pool_name, "<pool-name>"))

        # create user pool
        create_user_pool_response = aws_client.cognito_idp.create_user_pool(
            PoolName=pool_name,
            UsernameAttributes=["phone_number", "email"],
        )
        snapshot.match("create_user_pool_response", create_user_pool_response)
        pool_id = create_user_pool_response["UserPool"]["Id"]
        cleanups.append(lambda: aws_client.cognito_idp.delete_user_pool(UserPoolId=pool_id))

        # create user pool client
        create_user_pool_client_response = aws_client.cognito_idp.create_user_pool_client(
            UserPoolId=pool_id, ClientName=pool_client_name
        )
        client_id = create_user_pool_client_response["UserPoolClient"]["ClientId"]
        snapshot.match("create_user_pool_client_response", create_user_pool_client_response)
        cleanups.append(
            lambda: aws_client.cognito_idp.delete_user_pool_client(
                UserPoolId=pool_id, ClientId=client_id
            )
        )

        # create user with email username

        # TODO: Currently doesn't work. Should validate password requirements
        # by default password needs to have an uppercase letter
        # with pytest.raises(cognito_idp_client.exceptions.InvalidPasswordException) as e:
        #     cognito_idp_client.admin_create_user(
        #         UserPoolId=pool_id, Username=email, TemporaryPassword="all-lowercase"
        #     )
        # snapshot.match("invalid_pw_exception", e.value.response)

        # successful create user
        admin_create_user_result = aws_client.cognito_idp.admin_create_user(
            UserPoolId=pool_id, Username=email, TemporaryPassword=email_pass
        )
        snapshot.match("admin_create_user_result", admin_create_user_result)

        # same user (identical email) can't be created again
        with pytest.raises(aws_client.cognito_idp.exceptions.UsernameExistsException) as ctx:
            aws_client.cognito_idp.admin_create_user(
                UserPoolId=pool_id, Username=email, TemporaryPassword=email_pass
            )
        snapshot.match("username_exists_exc", ctx.value.response)

    @markers.aws.unknown
    def test_create_cognito_identity_pool_roles(self, aws_client, account_id, region_name):
        # create identity pool
        pool_name = f"p-{short_uid()}"

        def _find_id_pools():
            result = aws_client.cognito_identity.list_identity_pools(MaxResults=100)
            return list(
                filter(lambda x: x.get("IdentityPoolName") == pool_name, result["IdentityPools"])
            )

        assert not _find_id_pools()

        result = aws_client.cognito_identity.create_identity_pool(
            IdentityPoolName=pool_name, AllowUnauthenticatedIdentities=False
        )
        assert "IdentityPoolId" in result
        pool_id = result["IdentityPoolId"]
        roles = {"authenticated": arns.iam_role_arn("role1", account_id, region_name)}

        assert len(_find_id_pools()) == 1

        # set and get pool roles
        aws_client.cognito_identity.set_identity_pool_roles(IdentityPoolId=pool_id, Roles=roles)
        result = aws_client.cognito_identity.get_identity_pool_roles(IdentityPoolId=pool_id)
        assert result.get("Roles") == roles

        # clean up
        aws_client.cognito_identity.delete_identity_pool(IdentityPoolId=pool_id)

    @markers.aws.unknown
    def test_resource_servers(self, aws_client):
        # create user pool
        pool_name = f"pool-{short_uid()}"
        result = aws_client.cognito_idp.create_user_pool(PoolName=pool_name)
        pool_id = result["UserPool"]["Id"]

        # create resource server
        server_id = "https://my-weather-api.example.com"
        server_name = f"s-{short_uid()}"
        aws_client.cognito_idp.create_resource_server(
            UserPoolId=pool_id, Identifier=server_id, Name=server_name
        )

        # describe/list resource server
        server = aws_client.cognito_idp.describe_resource_server(
            UserPoolId=pool_id, Identifier=server_id
        )["ResourceServer"]
        assert server["Identifier"] == server_id
        assert server["Name"] == server_name
        servers = aws_client.cognito_idp.list_resource_servers(UserPoolId=pool_id)[
            "ResourceServers"
        ]
        assert len(servers) == 1

        # delete resource server
        aws_client.cognito_idp.delete_resource_server(UserPoolId=pool_id, Identifier=server_id)
        with pytest.raises(Exception) as ctx:
            aws_client.cognito_idp.describe_resource_server(
                UserPoolId=pool_id, Identifier=server_id
            )
        assert "ResourceNotFoundException" in str(ctx.value)

        # clean up
        aws_client.cognito_idp.delete_user_pool(UserPoolId=pool_id)

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(paths=["$..IdentityProvider.ProviderDetails"])
    def test_identity_providers(
        self,
        aws_client,
        create_user_pool_client,
        snapshot,
        saml_metadata_server,
        add_cognito_snapshot_transformers,
    ):
        snapshot.add_transformer(
            snapshot.transform.jsonpath("$..IdentityProvider.IdpIdentifiers[0]", "identifiers")
        )
        snapshot.add_transformer(
            snapshot.transform.jsonpath("$..IdentityProvider.UserPoolId", "user-pool-id")
        )
        snapshot.add_transformer(
            snapshot.transform.jsonpath("$..IdentityProvider.ProviderName", "provider-name")
        )

        pool_result = create_user_pool_client()
        client = pool_result.pool_client
        pool_id, client_id = client["UserPoolId"], client["ClientId"]

        provider_name = f"prov-{short_uid()}"
        idp_identifier = f"idp-identifier-{short_uid()}"

        result = aws_client.cognito_idp.create_identity_provider(
            UserPoolId=pool_id,
            ProviderName=provider_name,
            ProviderType="SAML",
            IdpIdentifiers=[idp_identifier],
            ProviderDetails={"MetadataURL": saml_metadata_server},
            AttributeMapping={
                "email": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress",
                "name": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/name",
            },
        )
        snapshot.match("create-idp-provider", result)

        result = aws_client.cognito_idp.describe_identity_provider(
            UserPoolId=pool_id, ProviderName=provider_name
        )
        snapshot.match("describe-idp-provider", result)

        result = aws_client.cognito_idp.get_identity_provider_by_identifier(
            UserPoolId=pool_id, IdpIdentifier=idp_identifier
        )
        snapshot.match("get-provider-by-identifier", result)

        result = aws_client.cognito_idp.update_identity_provider(
            UserPoolId=pool_id,
            ProviderName=provider_name,
            AttributeMapping={
                "email": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/email",
                "name": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/fistname",
            },
        )
        snapshot.match("update-idp", result)

    @markers.aws.unknown
    def test_user_pools_and_clients(self, aws_client, region_name):
        user_attrs = ["phone_number", "email"]
        pool_name = "p1"
        response = aws_client.cognito_idp.create_user_pool(
            PoolName=pool_name, UsernameAttributes=user_attrs
        )
        assert response["ResponseMetadata"]["HTTPStatusCode"] == 200
        user_pool = response["UserPool"]

        # assert that dates are in numeric format (for compatibility with Node.js AWS SDK v3)
        headers = {
            "X-Amz-Target": "ListUserPools",
            **mock_aws_request_headers(
                "cognito-idp",
                aws_access_key_id=TEST_AWS_ACCESS_KEY_ID,
                region_name=region_name,
            ),
        }
        response = requests.post(config.internal_service_url(), headers=headers)
        assert response.status_code == 200
        pools = json.loads(to_str(response.content))["UserPools"]
        for pool in pools:
            assert isinstance(pool["CreationDate"], (float, int))
            assert isinstance(pool["LastModifiedDate"], (float, int))

        pool_client = aws_client.cognito_idp.create_user_pool_client(
            UserPoolId=user_pool["Id"], ClientName="c1"
        )
        assert pool_client["ResponseMetadata"]["HTTPStatusCode"] == 200

        # clean up
        aws_client.cognito_idp.delete_user_pool(UserPoolId=user_pool["Id"])

    @markers.aws.only_localstack
    def test_saml_auth_flow(
        self,
        create_user_pool_client,
        aws_client,
        saml_metadata_server,
        saml_callback_url,
        saml_response,
        trigger_lambda,
    ):
        # This test simulates the following SAML authentication flow.
        # We do not use any real IdP for the test itself, but we use real SAML responses from Auth0 in the fixtures.
        #   ┌───────────────┐     ┌───────────────┐
        #   │8.exchange code│     │ 6.create user │
        #   │   for token   │     └───────────────┘
        #   └───────────────┘             ▲
        #           ▲                     │
        #           │                     │             2.
        #       ┌───────┐   7.code  ┌───────────┐   SAMLRequest    ┌───────────┐
        #       │       │◀──────────│           │─────────────────▶│           │
        #       │       │           │           │        5.        │           │
        #       │  App  │           │  Cognito  │   SAMLResponse   │    Idp    │
        #       │       │           │           │ saml2/idpresponse│  (Auth0)  │
        #       │       │──────────▶│           │◀─────────────────│           │
        #       └───────┘           └───────────┘                  └───────────┘
        #                      1.                                        ▲
        #      /authorize?idp_provider=myprovider                        │
        #                                                                │
        #                                                                │
        #           ┌─────────┐                                          │
        #           │         │                                          │
        #           │         │               4. validate credentials    │
        #           │ Browser │◀─────────────────────────────────────────┘
        #           │         │       3. display login page
        #           │         │
        #           └─────────┘

        # this is the callback URL that Cognito will redirect to after the SAML assertion is received
        callback_url = saml_callback_url
        client_kwargs = {
            "ExplicitAuthFlows": [
                "ALLOW_ADMIN_USER_PASSWORD_AUTH",
                "ALLOW_USER_PASSWORD_AUTH",
                "ALLOW_USER_SRP_AUTH",
                "ALLOW_REFRESH_TOKEN_AUTH",
            ],
            "AllowedOAuthScopes": [
                "aws.cognito.signin.user.admin",
                "email",
                "openid",
                "phone",
                "profile",
            ],
            "AllowedOAuthFlows": ["code"],
            "CallbackURLs": [callback_url],
        }
        pool_args = {
            "UserPoolTags": {"_custom_id_": "us-east-1_idptest"},
            "LambdaConfig": {
                "PreSignUp": trigger_lambda,
                "PostConfirmation": trigger_lambda,
            },
        }

        user_pool_and_client = create_user_pool_client(
            client_kwargs=client_kwargs, pool_kwargs=pool_args
        )
        user_pool = user_pool_and_client.user_pool
        assert user_pool["Id"] == "us-east-1_idptest"
        client_id = user_pool_and_client.pool_client["ClientId"]

        provider_name = f"provider-{short_uid()}"

        aws_client.cognito_idp.create_identity_provider(
            UserPoolId=user_pool["Id"],
            ProviderName=provider_name,
            ProviderType="SAML",
            ProviderDetails={"MetadataURL": saml_metadata_server},
            AttributeMapping={
                "email": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress",
                "name": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/name",
            },
        )

        domain_name = f"integration-{short_uid()}"
        aws_client.cognito_idp.create_user_pool_domain(
            Domain=domain_name, UserPoolId=user_pool["Id"]
        )

        edge_url = config.internal_service_url(protocol="http")
        base_url = f"{edge_url}/_aws/cognito-idp"

        url = (
            f"{base_url}/oauth2/authorize"
            f"?redirect_uri={callback_url}"
            f"&client_id={client_id}"
            f"&identity_provider={provider_name}"
            "&scope=openid+profile+aws.cognito.signin.user.admin"
            "&state=1234"
        )
        response = requests.get(url, allow_redirects=False)
        assert response.status_code == 302
        # assert that we are redirected to the IdP login page
        assert "auth0.com" in response.headers["Location"]

        # check SAMLRequest
        location = response.headers["Location"]
        location = urllib.parse.unquote(location)
        query = parse_qs(urlparse(location).query)
        saml_request = query["SAMLRequest"]
        assert saml_request

        request_id = list(saml_request_id_to_params.keys())[0]

        # Note: when we reach this step, we are redirected to the login page of the external Identity Provider.
        # After a login, the IdP sends the SAML assertions with a POST request back to Cognito at the
        # 'samls/idpresponse' endpoint.
        # The following code simulates the POST request with a real SAML response.

        response = requests.post(
            url=f"{base_url}/saml2/idpresponse",
            data={"SAMLResponse": saml_response(request_id=request_id)},
        )
        assert response.status_code == 200
        code = response.json().get("code")
        assert code

        # No we verify that we can exchange the code for a token
        token_url = f"{base_url}/oauth2/token"
        data = f"grant_type=authorization_code&client_id={client_id}&code={code}&redirect_uri={callback_url}"
        result = requests.post(
            token_url, data=data, headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        payload: dict[str, str] = json.loads(result.content)
        access_token = payload["access_token"]
        assert access_token
        token_claims = cognito_utils.get_token_claims(access_token)
        assert "e2e-334528fe243b@localstack.cloud" in token_claims.get("username")

        user = aws_client.cognito_idp.get_user(AccessToken=access_token)
        username = user["Username"]
        assert provider_name in username, "provider name not contained in the username"
        email = [attr["Value"] for attr in user["UserAttributes"] if attr["Name"] == "email"][0]
        assert email in username, "email not contained in the username"

        user = aws_client.cognito_idp.admin_get_user(UserPoolId=user_pool["Id"], Username=username)
        assert user["UserStatus"] == "EXTERNAL_PROVIDER"
        assert [attr["Value"] for attr in user["UserAttributes"] if attr["Name"] == "identities"]

        def _check_logs(filter_log: str, expected_times: int = 0):
            cognito_triggers_name = arns.lambda_function_name(trigger_lambda)
            logs = testutil.get_lambda_log_events(
                function_name=cognito_triggers_name, logs_client=aws_client.logs, delay_time=1
            )
            matching = [log for log in logs if filter_log in log]
            assert len(matching) == expected_times

        # Check that we call the right triggers when hitting /saml2/idpresponse
        retry(
            _check_logs,
            sleep=1,
            retries=15,
            filter_log="PreSignUp_ExternalProvider",
            expected_times=1,
        )
        retry(
            _check_logs,
            sleep=1,
            retries=15,
            filter_log="PostConfirmation_ConfirmSignUp",
            expected_times=1,
        )

    @markers.aws.only_localstack
    def test_oauth2_authorize_idp_provider(
        self,
        aws_client,
        create_user_pool_client,
        saml_metadata_server,
    ):
        pool_result = create_user_pool_client()
        client = pool_result.pool_client
        pool_id, client_id = client["UserPoolId"], client["ClientId"]

        provider_name = f"prov-{short_uid()}"
        idp_identifier = f"idp-identifier-{short_uid()}"

        aws_client.cognito_idp.create_identity_provider(
            UserPoolId=pool_id,
            ProviderName=provider_name,
            ProviderType="SAML",
            IdpIdentifiers=[idp_identifier],
            ProviderDetails={"MetadataURL": saml_metadata_server},
            AttributeMapping={
                "email": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress",
                "name": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/name",
            },
        )

        # check that we are able to call the oauth2/authorize endpoint using both the identity provider and the
        # idp_identifier

        edge_url = config.internal_service_url(protocol="http")
        base_url = f"{edge_url}/_aws/cognito-idp"

        url = (
            f"{base_url}/oauth2/authorize"
            f"?redirect_uri=localstack.cloud"
            f"&client_id={client_id}"
            f"&identity_provider={provider_name}"
            "&scope=openid+profile+aws.cognito.signin.user.admin"
            "&state=1234"
        )
        response = requests.get(url, allow_redirects=False)

        def _assert_authorize_response(_response):
            assert _response.status_code == 302
            location = _response.headers.get("Location")
            assert location
            saml_request = parse_qs(urllib.parse.unquote(urlparse(location).query)).get(
                "SAMLRequest"
            )
            assert saml_request

        _assert_authorize_response(response)

        url = (
            f"{base_url}/oauth2/authorize"
            f"?redirect_uri=localstack.cloud"
            f"&client_id={client_id}"
            f"&idp_identifier={idp_identifier}"
            "&scope=openid+profile+aws.cognito.signin.user.admin"
            "&state=1234"
        )
        response = requests.get(url, allow_redirects=False)
        _assert_authorize_response(response)

    @markers.aws.validated
    def test_user_pool_client_updates(self, create_user_pool_client, snapshot, aws_client):
        snapshot.add_transformer(snapshot.transform.key_value("ClientId"))
        snapshot.add_transformer(snapshot.transform.key_value("UserPoolId"))

        pool_result = create_user_pool_client()
        client = pool_result.pool_client

        kwargs = {"UserPoolId": client["UserPoolId"], "ClientId": client["ClientId"]}

        # Update #1 - set CallbackURLs
        aws_client.cognito_idp.update_user_pool_client(
            **kwargs, CallbackURLs=["https://test"], ExplicitAuthFlows=["USER_PASSWORD_AUTH"]
        )
        result = aws_client.cognito_idp.describe_user_pool_client(**kwargs)
        snapshot.match("pool_details1", result)

        # Update #2 - set SupportedIdentityProviders
        aws_client.cognito_idp.create_identity_provider(
            UserPoolId=client["UserPoolId"],
            ProviderName="test-idp",
            ProviderType="OIDC",
            ProviderDetails={
                "client_id": "c1",
                "authorize_scopes": "openid",
                "oidc_issuer": "https://example.com",
                "attributes_request_method": "GET",
                "authorize_url": "https://example.com",
                "token_url": "https://example.com",
                "attributes_url": "https://example.com",
                "jwks_uri": "https://example.com",
            },
        )
        aws_client.cognito_idp.update_user_pool_client(
            **kwargs, SupportedIdentityProviders=["test-idp"]
        )
        result = aws_client.cognito_idp.describe_user_pool_client(**kwargs)
        snapshot.match("pool_details2", result)

        # Update #3 - set ExplicitAuthFlows
        aws_client.cognito_idp.update_user_pool_client(
            **kwargs, ExplicitAuthFlows=["ALLOW_REFRESH_TOKEN_AUTH"]
        )
        result = aws_client.cognito_idp.describe_user_pool_client(**kwargs)
        snapshot.match("pool_details3", result)

    @markers.aws.unknown
    def test_well_known_paths(self, create_user_pool, aws_client):
        # create pool
        pool_name = f"pool-{short_uid()}"
        result = create_user_pool(pool_name=pool_name)
        pool_id = result["Id"]

        # retrieve JWKS key data from URL
        url = f"{config.internal_service_url()}/{pool_id}/.well-known/jwks.json"
        result = requests.get(url)
        assert result.status_code == 200
        result = json.loads(to_str(result.content))
        assert result.get("keys")

        # retrieve JWKS key data for Cognito Identity Pools from URL
        url = f"{config.internal_service_url()}/.well-known/jwks_uri"
        result = requests.get(url)
        assert result.status_code == 200
        result = json.loads(to_str(result.content))
        assert result.get("keys")

    @markers.aws.unknown
    def test_mfa_sms_authentication(self, signup_and_login_user, aws_client):
        username = f"user-{short_uid()}"
        password = "Test123!"
        pool_name = f"pool-with-mfa-{short_uid()}"
        user_pool = aws_client.cognito_idp.create_user_pool(
            PoolName=pool_name,
            MfaConfiguration="ON",
            SmsConfiguration={"SnsCallerArn": "arn:aws:iam::000000000000:role/test"},
            AutoVerifiedAttributes=["phone_number"],
        )["UserPool"]
        pool_client = aws_client.cognito_idp.create_user_pool_client(
            UserPoolId=user_pool["Id"], ClientName="client_with_mfa"
        )["UserPoolClient"]

        result = aws_client.cognito_idp.get_user_pool_mfa_config(UserPoolId=user_pool["Id"])
        assert result["MfaConfiguration"] == "ON"

        signup_and_login_user(
            pool_client,
            username,
            password=password,
            attributes=[{"Name": "phone_number", "Value": "+4179xxxxxxxxx"}],
            srp_authentication=False,
        )
        client_id = pool_client["ClientId"]

        # with MFA authenticated we should get back a SMS_MFA challenge
        result = aws_client.cognito_idp.admin_initiate_auth(
            AuthFlow="ADMIN_NO_SRP_AUTH",
            ClientId=client_id,
            UserPoolId=user_pool["Id"],
            AuthParameters={"USERNAME": username, "PASSWORD": password},
        )
        # this should be a response challenge
        assert result["ChallengeName"] == "SMS_MFA"

        session = result["Session"]
        result = aws_client.cognito_idp.admin_respond_to_auth_challenge(
            ClientId=client_id,
            UserPoolId=user_pool["Id"],
            ChallengeName="SMS_MFA",
            ChallengeResponses={"SMS_MFA_CODE": "xxxxxx", "USERNAME": username},
            Session=session,
        )
        assert result["AuthenticationResult"]["NewDeviceMetadata"]
        device_key = result["AuthenticationResult"]["NewDeviceMetadata"]["DeviceKey"]
        assert device_key

        # new login with device key should skip the MFA challenge
        result = aws_client.cognito_idp.admin_initiate_auth(
            AuthFlow="ADMIN_NO_SRP_AUTH",
            ClientId=client_id,
            UserPoolId=user_pool["Id"],
            AuthParameters={"USERNAME": username, "PASSWORD": password, "DEVICE_KEY": device_key},
        )
        assert "NewDeviceMetadata" in result["AuthenticationResult"]

    @markers.aws.unknown
    def test_incorrect_mfa_setup(self, aws_client):
        pool_name = f"pool-{short_uid()}"
        with pytest.raises(Exception) as e:
            aws_client.cognito_idp.create_user_pool(
                PoolName=pool_name,
                MfaConfiguration="ON",
                SmsAuthenticationMessage="Your authentication code is #####",
                EmailConfiguration={"EmailSendingAccount": "COGNITO_DEFAULT"},
            )
        assert "Invalid MFA configuration given" in str(e.value)

    @markers.aws.validated
    def test_create_pool_mfa_off(self, snapshot, cleanups, aws_client):
        pool_name = f"pool-{short_uid()}"
        snapshot.add_transformer(snapshot.transform.regex(pool_name, "<pool-name>"))
        snapshot.add_transformer(snapshot.transform.jsonpath("$..UserPool.Arn", "user-pool-arn"))
        snapshot.add_transformer(snapshot.transform.jsonpath("$..UserPool.Id", "user-pool-id"))

        result = aws_client.cognito_idp.create_user_pool(
            PoolName=pool_name,
            MfaConfiguration="OFF",
            # AWS validation regex: (?s).*\{####\}(?s).*
            SmsAuthenticationMessage="Your authentication code is {####}",
            EmailConfiguration={"EmailSendingAccount": "COGNITO_DEFAULT"},
        )
        user_pool_id = result["UserPool"]["Id"]
        cleanups.append(lambda: aws_client.cognito_idp.delete_user_pool(UserPoolId=user_pool_id))
        assert result["UserPool"]["Name"] == pool_name
        assert result["UserPool"]["MfaConfiguration"] == "OFF"
        snapshot.match("create_user_pool_mfa_off", result)

        mfa_config = aws_client.cognito_idp.get_user_pool_mfa_config(UserPoolId=user_pool_id)
        snapshot.match("get_user_pool_mfa_config", mfa_config)

    @markers.aws.validated
    # TODO: fix for new Lambda provider. Raises UserLambdaValidationException due to InvalidClientTokenId in Lambda
    def test_admin_create_user_should_trigger_custom_message_lambda(
        self, trigger_lambda, create_user_pool, aws_client
    ):
        pool_name = f"pool-{short_uid()}"
        new_username = f"user-{short_uid()}"
        new_password = "TestingPW123!"
        user_attributes = [
            {"Name": "email", "Value": f"{new_username}@test.com"},
            {"Name": "email_verified", "Value": "true"},
        ]

        # create user pool
        user_pool = create_user_pool(pool_name, LambdaConfig={"CustomMessage": trigger_lambda})

        # admin create user
        user_pool_id = user_pool["Id"]
        aws_client.cognito_idp.admin_create_user(
            UserPoolId=user_pool_id,
            Username=new_username,
            UserAttributes=user_attributes,
            TemporaryPassword=new_password,
        )

        # check if lambda got invoked
        def assert_lambda_invoked():
            cognito_trigger_name = arns.lambda_function_name(trigger_lambda)
            events = testutil.get_lambda_log_events(
                function_name=cognito_trigger_name, logs_client=aws_client.logs
            )
            assert len(events) > 0

        retry(assert_lambda_invoked, retries=10)

    @markers.aws.validated
    def test_tags(self, create_user_pool, aws_client):
        pool = create_user_pool()
        pool_arn = pool["Arn"]

        tags = {"t1": "foo", "t2:tag": "bar"}
        aws_client.cognito_idp.tag_resource(ResourceArn=pool_arn, Tags=tags)
        result = aws_client.cognito_idp.list_tags_for_resource(ResourceArn=pool_arn)
        assert result["Tags"] == tags

        aws_client.cognito_idp.untag_resource(ResourceArn=pool_arn, TagKeys=["t1"])
        result = aws_client.cognito_idp.list_tags_for_resource(ResourceArn=pool_arn)
        assert result["Tags"] == {"t2:tag": "bar"}

    @markers.aws.unknown
    def test_check_message_action_suppress(
        self, create_user_pool_client, patch_send_confirmation_email, aws_client
    ):
        user_pool_result = create_user_pool_client(pool_name=f"pool-{short_uid()}")

        aws_client.cognito_idp.admin_create_user(
            UserPoolId=user_pool_result.user_pool["Id"],
            Username=f"username-{short_uid()}",
            MessageAction="SUPPRESS",
            UserAttributes=[
                {"Name": "email", "Value": "test@example.com"},
                {"Name": "phone_number", "Value": "+123456789"},
            ],
        )
        patch_send_confirmation_email.assert_not_called()

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(
        paths=[
            "$..origin_jti",  # missing from Access Token
            "$.initiate-auth-id-token.'cognito:user_status'",  # AWS does not return this
            "$.initiate-auth-id-token.email_verified",  # wrong type, should be a bool and we return 'true'
            "$.initiate-auth-id-token.jti",  # missing from LS
        ]
    )
    def test_admin_create_user_username_in_token(
        self, create_user_pool_client, aws_client, snapshot
    ):
        # TODO: consolidate transformers, but we don't want some values to be transformed, like userName
        snapshot.add_transformers_list(
            [
                snapshot.transform.key_value("sub"),
                snapshot.transform.key_value("jti"),
                snapshot.transform.key_value("origin_jti"),
                snapshot.transform.key_value("iss"),
                snapshot.transform.key_value("client_id"),
                snapshot.transform.key_value("auth_time", reference_replacement=False),
                snapshot.transform.key_value("exp", reference_replacement=False),
                snapshot.transform.key_value("iat", reference_replacement=False),
            ]
        )
        aliases = ["email"]
        user_pool_result = create_user_pool_client(pool_kwargs={"AliasAttributes": aliases})
        pool_client = user_pool_result.pool_client
        user_pool = user_pool_result.user_pool
        user_pool_id = user_pool["Id"]
        client_id = pool_client["ClientId"]

        username = "my-defined-username"
        email = "test@ex.com"

        create_user_resp = aws_client.cognito_idp.admin_create_user(
            UserPoolId=user_pool_id,
            Username=username,
            UserAttributes=[
                {"Name": "email", "Value": email},
                {"Name": "email_verified", "Value": "true"},
            ],
        )
        snapshot.match("create-user", create_user_resp)

        set_user_pwd_resp = aws_client.cognito_idp.admin_set_user_password(
            UserPoolId=user_pool_id,
            Username=username,
            Password="Test123!",
            Permanent=True,
        )
        snapshot.match("admin-set-pwd", set_user_pwd_resp)
        initiate_auth = aws_client.cognito_idp.initiate_auth(
            AuthFlow="USER_PASSWORD_AUTH",
            ClientId=client_id,
            AuthParameters={
                "USERNAME": email,
                "PASSWORD": "Test123!",
            },
        )
        access_token = initiate_auth["AuthenticationResult"]["AccessToken"]
        claims = jwt.decode(access_token, options={"verify_signature": False}) or {}
        snapshot.match("initiate-auth-access-token", claims)
        id_token = initiate_auth["AuthenticationResult"]["IdToken"]
        claims_id = jwt.decode(id_token, options={"verify_signature": False}) or {}
        snapshot.match("initiate-auth-id-token", claims_id)

    # -----------------
    # HELPER FUNCTIONS
    # -----------------

    @staticmethod
    def _create_user(
        cognito_client, pool_id: str, username: str, password: str, confirm_pw=True, **kwargs
    ):
        result = cognito_client.admin_create_user(
            UserPoolId=pool_id, Username=username, TemporaryPassword=password, **kwargs
        )
        if confirm_pw:
            cognito_client.admin_set_user_password(
                UserPoolId=pool_id, Username=username, Password=password, Permanent=True
            )
        return result

    @staticmethod
    def _attempt_user_login(client_id, username: str, password: str, cognito_client=None):
        # TODO: remove connect_to() and use client fixture
        cognito_client = cognito_client or connect_to().cognito_idp
        result = cognito_client.initiate_auth(
            AuthFlow="USER_PASSWORD_AUTH",
            ClientId=client_id,
            AuthParameters={"USERNAME": username, "PASSWORD": password},
        )
        assert result["ResponseMetadata"]["HTTPStatusCode"] == 200
        return result.get("AuthenticationResult")

    @staticmethod
    def _update_user_attributes_with_client(
        cognito_idp_client, pool_id: str, username: str, attr_name: str
    ):
        attr_val = short_uid()
        cognito_idp_client.add_custom_attributes(
            UserPoolId=pool_id,
            CustomAttributes=[{"Name": attr_name, "AttributeDataType": "String"}],
        )
        new_attr = {"Name": attr_name, "Value": attr_val}
        response = cognito_idp_client.admin_update_user_attributes(
            UserPoolId=pool_id, Username=username, UserAttributes=[new_attr]
        )
        assert response["ResponseMetadata"]["HTTPStatusCode"] == 200
        response = cognito_idp_client.admin_get_user(UserPoolId=pool_id, Username=username)
        assert response["ResponseMetadata"]["HTTPStatusCode"] == 200
        user_attrs = response.get("UserAttributes", [])
        assert new_attr in user_attrs
        return response

    @staticmethod
    def _gateway_request_url(api_id, stage_name, path):
        pattern = "%s/restapis/{api_id}/{stage_name}/%s{path}" % (
            config.internal_service_url(),
            PATH_USER_REQUEST,
        )
        return pattern.format(api_id=api_id, stage_name=stage_name, path=path)

    @staticmethod
    def cleanup(pool_id, client_id):
        # TODO: use client fixture
        client = connect_to().cognito_idp
        client.delete_user_pool_client(UserPoolId=pool_id, ClientId=client_id)
        client.delete_user_pool(UserPoolId=pool_id)

    @markers.aws.validated
    @pytest.mark.parametrize(
        "access_token,id_token,refresh_token",
        [
            ("invalid", "hours", "hours"),
            ("invalid", "invalid", "hours"),
            ("invalid", "invalid", "invalid"),
        ],
    )
    def test_invalid_expiration_unit(
        self, create_user_pool_client, snapshot, access_token, id_token, refresh_token
    ):
        kwargs = {
            "TokenValidityUnits": {
                "AccessToken": access_token,
                "IdToken": id_token,
                "RefreshToken": refresh_token,
            },
            "AccessTokenValidity": 10,
            "ExplicitAuthFlows": ["ALLOW_ADMIN_USER_PASSWORD_AUTH", "ALLOW_REFRESH_TOKEN_AUTH"],
        }
        with pytest.raises(Exception) as exception:
            create_user_pool_client(client_kwargs=kwargs)
        snapshot.match("invalid-token-unit", exception.value)

    @markers.aws.validated
    @pytest.mark.parametrize(
        "validity,unit,expires_in",
        [(10, "hours", 36000), (10, "minutes", 600), (1, "days", 86400), (500, "seconds", 500)],
    )
    def test_access_token_expiration_validity(
        self,
        create_user_pool_client,
        aws_client,
        validity,
        unit,
        expires_in,
    ):
        kwargs = {
            "TokenValidityUnits": {"AccessToken": unit, "IdToken": "hours", "RefreshToken": "days"},
            "AccessTokenValidity": validity,
            "ExplicitAuthFlows": ["ALLOW_ADMIN_USER_PASSWORD_AUTH", "ALLOW_REFRESH_TOKEN_AUTH"],
        }
        user_pool_result = create_user_pool_client(client_kwargs=kwargs)
        pool_client = user_pool_result.pool_client
        client_id = pool_client["ClientId"]
        user_pool_id = pool_client["UserPoolId"]

        username = "test_user@ls.cloud"
        password = "TmpTest123!"
        aws_client.cognito_idp.sign_up(ClientId=client_id, Username=username, Password=password)

        aws_client.cognito_idp.admin_confirm_sign_up(
            UserPoolId=pool_client["UserPoolId"], Username=username
        )

        response = aws_client.cognito_idp.admin_initiate_auth(
            AuthFlow="ADMIN_USER_PASSWORD_AUTH",
            ClientId=client_id,
            UserPoolId=user_pool_id,
            AuthParameters={"USERNAME": username, "PASSWORD": password},
        )

        authentication_result = response["AuthenticationResult"]
        assert authentication_result["ExpiresIn"] == expires_in
        payload = authentication_result["AccessToken"]

        decoded = jwt.decode(jwt=payload, options={"verify_signature": False})
        assert decoded["exp"]
        assert decoded["exp"] <= now_utc() + expires_in


# TODO: move more user attribute tests from above into this class
class TestUserAttributes:
    @pytest.mark.parametrize(
        "username_attributes", [["email"], ["phone_number"], ["email", "phone_number"]]
    )
    @markers.aws.validated
    def test_signup_require_phone_email(
        self, create_user_pool, trigger_lambda, aws_client, snapshot, username_attributes
    ):
        pool_name = f"pool-{short_uid()}"
        user_pool_id = create_user_pool(
            pool_name=pool_name,
            LambdaConfig={
                "PreSignUp": trigger_lambda,
            },
            Schema=[{"Name": "attr1", "AttributeDataType": "String"}],
            UsernameAttributes=username_attributes,
        )["Id"]

        client_name = f"client-{short_uid()}"
        result = aws_client.cognito_idp.create_user_pool_client(
            UserPoolId=user_pool_id,
            ClientName=client_name,
        )
        client_id = result["UserPoolClient"]["ClientId"]

        with pytest.raises(ClientError) as ctx:
            aws_client.cognito_idp.sign_up(
                ClientId=client_id,
                Username=f"user-{short_uid()}",
                Password=TEST_PASSWORD,
            )
        snapshot.match("error", ctx.value.response)

    @pytest.mark.parametrize("username_attrs", ["email", None])
    @pytest.mark.parametrize("email_user_attr", [True, False])
    @pytest.mark.parametrize("pre_signup_trigger", [True, False])
    @markers.aws.validated
    def test_create_user_with_email_uses_sub_as_username(
        self,
        create_user_pool_client,
        aws_client,
        add_cognito_snapshot_transformers,
        username_attrs,
        email_user_attr,
        pre_signup_trigger,
        trigger_lambda,
        snapshot,
    ):
        user_pool_kwargs = {}
        if username_attrs:
            user_pool_kwargs["UsernameAttributes"] = [username_attrs]
        if pre_signup_trigger:
            user_pool_kwargs["LambdaConfig"] = {"PreSignUp": trigger_lambda}
        result = create_user_pool_client(pool_kwargs=user_pool_kwargs)
        client_id = result.pool_client["ClientId"]
        pool_id = result.user_pool["Id"]

        cognito_client = aws_client.cognito_idp

        def _check_logs(filter_log: str, _username: str):
            if not pre_signup_trigger:
                return
            cognito_triggers_name = arns.lambda_function_name(trigger_lambda)
            logs = testutil.get_lambda_log_events(
                function_name=cognito_triggers_name, logs_client=aws_client.logs, delay_time=1
            )
            matching = [log for log in logs if filter_log in log]
            assert matching
            pattern = r"'userName': '([^']*)'"
            match = re.search(pattern, matching[0])
            if match:
                assert match.group(1) == _username

        # create via admin API (AdminCreateUser)
        username = "test@example.com"
        user_kwargs = (
            {"UserAttributes": [{"Name": "email", "Value": username}]} if email_user_attr else {}
        )
        result = cognito_client.admin_create_user(
            UserPoolId=pool_id, Username=username, **user_kwargs
        )
        retry(
            _check_logs,
            sleep=1,
            retries=15,
            filter_log=TRIGGER_ADMIN_CREATE_USER,
            _username=result["User"]["Username"],
        )
        result["User"]["Attributes"] = {
            attr["Name"]: attr["Value"] for attr in result["User"]["Attributes"]
        }
        snapshot.match("create-user-response", result)

        result = cognito_client.admin_get_user(UserPoolId=pool_id, Username=username)
        result["UserAttributes"] = {
            attr["Name"]: attr["Value"] for attr in result["UserAttributes"]
        }
        snapshot.match("get-user-response", result)

        # create via user API (SignUp)
        username = "test2@example.com"
        user_kwargs = (
            {"UserAttributes": [{"Name": "email", "Value": username}]} if email_user_attr else {}
        )
        cognito_client.sign_up(
            ClientId=client_id, Username=username, Password=TEST_PASSWORD, **user_kwargs
        )

        result = cognito_client.admin_get_user(UserPoolId=pool_id, Username=username)
        retry(
            _check_logs,
            sleep=1,
            retries=15,
            filter_log=TRIGGER_SIGNUP,
            _username=result["Username"],
        )
        result["UserAttributes"] = {
            attr["Name"]: attr["Value"] for attr in result["UserAttributes"]
        }
        snapshot.match("get-user-response2", result)

    @markers.aws.validated
    def test_custom_attributes_cannot_be_required(self, create_user_pool_client, snapshot):
        pool_name = f"pool-{short_uid()}"

        with pytest.raises(ClientError) as e:
            create_user_pool_client(
                pool_kwargs={
                    "Schema": [
                        {
                            "Name": "custom_attr",
                            "AttributeDataType": "String",
                            "Required": True,
                            "Mutable": True,
                        }
                    ]
                },
                pool_name=pool_name,
            )
        snapshot.match("custom-attr-required", e.value.response["Error"])


# TODO: move more auth flow tests from above into this class
class TestAuthFlows:
    @markers.aws.validated
    @pytest.mark.parametrize("srp_value", ["COFFEEG", None])  # SRP_A needs to be set and HEX
    def test_invalid_srp_raises_error(
        self, create_user_pool_client, snapshot, srp_value, aws_client
    ):
        # create pool client and user
        username = f"user-{short_uid()}"
        password = "Test123!"
        user_pool_result = create_user_pool_client()
        pool_client = user_pool_result.pool_client
        client_id = pool_client["ClientId"]
        aws_client.cognito_idp.sign_up(
            ClientId=pool_client["ClientId"],
            Username=username,
            Password=password,
            UserAttributes=[],
        )
        aws_client.cognito_idp.admin_confirm_sign_up(
            UserPoolId=pool_client["UserPoolId"], Username=username
        )

        # create the auth parameters depending on the pytest params
        auth = {"USERNAME": username}
        if srp_value is not None:
            auth["SRP_A"] = srp_value

        # call initiate_auth with the invalid params
        with pytest.raises(Exception) as invalid_srp_exception:
            aws_client.cognito_idp.initiate_auth(
                AuthFlow="USER_SRP_AUTH",
                ClientId=client_id,
                AuthParameters=auth,
            )

        # verify the exception
        snapshot.match("invalid_srp_response", invalid_srp_exception.value)

    @markers.aws.validated
    def test_valid_srp_login(
        self, create_pool_client_and_user, snapshot, aws_client, add_cognito_snapshot_transformers
    ):
        # create user pool, client, and test user
        pool_id, client_id, username = create_pool_client_and_user()

        # create the auth parameters
        awssrp = aws_srp.AWSSRP(
            username=username,
            password=TEST_PASSWORD,
            pool_id=pool_id,
            client_id=client_id,
            client=aws_client.cognito_idp,
        )
        auth_params = awssrp.get_auth_params()

        # run auth flow
        result = aws_client.cognito_idp.initiate_auth(
            AuthFlow="USER_SRP_AUTH",
            ClientId=client_id,
            AuthParameters=auth_params,
        )
        snapshot.match("initiate-auth", result)

        # run auth flow as admin
        result = aws_client.cognito_idp.admin_initiate_auth(
            AuthFlow="USER_SRP_AUTH",
            ClientId=client_id,
            UserPoolId=pool_id,
            AuthParameters=auth_params,
        )
        snapshot.match("initiate-auth-admin", result)

    @markers.aws.validated
    def test_srp_custom_auth_flow(
        self,
        create_pool_client_and_user,
        create_lambda_with_invocation_forwarding,
        add_cognito_snapshot_transformers,
        snapshot,
        aws_client,
    ):
        cognito_client = aws_client.cognito_idp

        lambda_code = textwrap.dedent(
            """
        import boto3, json
        def handler(event, context):
            event_orig = json.loads(json.dumps(event))
            trigger, response, request = event["triggerSource"], event["response"], event["request"]
            print(trigger, event)
            session = request.get("session") or []
            if trigger == "DefineAuthChallenge_Authentication":
                challenge_name = session[-1]["challengeName"]
                response["issueTokens"] = False
                response["failAuthentication"] = False
                if len(session) == 1 and challenge_name == "SRP_A":
                    response["challengeName"] = "PASSWORD_VERIFIER"
                elif len(session) == 2 and challenge_name == "PASSWORD_VERIFIER":
                    response["challengeName"] = "CUSTOM_CHALLENGE"
                elif len(session) == 3 and challenge_name == "CUSTOM_CHALLENGE" and session[-1]["challengeResult"]:
                    response["issueTokens"] = True
                else:
                    response["failAuthentication"] = True
            if trigger == "CreateAuthChallenge_Authentication":
                if request["challengeName"] == "CUSTOM_CHALLENGE":
                    response["privateChallengeParameters"] = {"answer": "test-answer-123"}
                    response["publicChallengeParameters"] = {}
            if trigger == "VerifyAuthChallengeResponse_Authentication":
                correct_answer = request["privateChallengeParameters"]["answer"]
                response["answerCorrect"] = request["challengeAnswer"] == correct_answer
            return event
        """
        )
        trigger_lambda = create_lambda_with_invocation_forwarding(lambda_source=lambda_code)

        # create user pool, client, and test user
        pool_id, client_id, username = create_pool_client_and_user(
            LambdaConfig={
                "DefineAuthChallenge": trigger_lambda,
                "CreateAuthChallenge": trigger_lambda,
                "VerifyAuthChallengeResponse": trigger_lambda,
            }
        )

        # create the auth parameters
        awssrp = aws_srp.AWSSRP(
            username=username,
            password=TEST_PASSWORD,
            pool_id=pool_id,
            client_id=client_id,
            client=cognito_client,
        )
        auth_params = awssrp.get_auth_params()

        # run auth flow
        auth_params["CHALLENGE_NAME"] = "SRP_A"
        result = cognito_client.initiate_auth(
            AuthFlow="CUSTOM_AUTH",
            ClientId=client_id,
            AuthParameters=auth_params,
        )
        snapshot.match("initiate-auth-custom", result)

        # provide first auth challenge response (PASSWORD_VERIFIER)
        chall_responses = awssrp.process_challenge(result["ChallengeParameters"])
        result = cognito_client.respond_to_auth_challenge(
            ClientId=client_id,
            Session=result["Session"],
            ChallengeName="PASSWORD_VERIFIER",
            ChallengeResponses=chall_responses,
        )
        snapshot.match("respond-auth-1", result)

        # provide second auth challenge response (CUSTOM_CHALLENGE)
        result = cognito_client.respond_to_auth_challenge(
            ClientId=client_id,
            Session=result["Session"],
            ChallengeName="CUSTOM_CHALLENGE",
            ChallengeResponses={"USERNAME": username, "ANSWER": "test-answer-123"},
        )
        snapshot.match("respond-auth-2", result)

    @markers.aws.validated
    def test_admin_no_srp_auth_flow(
        self, create_user_pool_client, signup_and_login_user, aws_client
    ):
        # create pool client and test user
        username = f"user-{short_uid()}"
        password = "Test123!"
        user_pool_result = create_user_pool_client()
        pool_client = user_pool_result.pool_client
        user_pool = user_pool_result.user_pool
        signup_and_login_user(pool_client, username, password)
        client_id = pool_client["ClientId"]

        # initiate auth flow
        result = aws_client.cognito_idp.admin_initiate_auth(
            AuthFlow="ADMIN_NO_SRP_AUTH",
            ClientId=client_id,
            UserPoolId=user_pool["Id"],
            AuthParameters={"USERNAME": username, "PASSWORD": password},
        )
        auth_result = result.get("AuthenticationResult", {})
        assert "AccessToken" in auth_result
        access_token = cognito_utils.get_token_claims(auth_result["AccessToken"])
        assert access_token["username"] == username

        # verify that user metadata can be retrieved
        details = aws_client.cognito_idp.get_user(AccessToken=auth_result["AccessToken"])
        assert details.get("Username") == username

        # initiate invalid auth flow
        with pytest.raises(Exception) as exp:
            aws_client.cognito_idp.admin_initiate_auth(
                AuthFlow="ADMIN_NO_SRP_AUTH",
                ClientId=client_id,
                UserPoolId=user_pool["Id"],
                AuthParameters={"USERNAME": username, "PASSWORD": "__invalid__"},
            )
        exp.match("NotAuthorizedException")

        # initiate token refresh
        result = aws_client.cognito_idp.admin_initiate_auth(
            AuthFlow="REFRESH_TOKEN_AUTH",
            ClientId=client_id,
            UserPoolId=user_pool["Id"],
            AuthParameters={"REFRESH_TOKEN": auth_result["RefreshToken"]},
        )
        access_token = cognito_utils.get_token_claims(result["AuthenticationResult"]["AccessToken"])
        # REFRESH_TOKEN_AUTH AuthFlow does not return a refresh token
        assert not result["AuthenticationResult"].get("RefreshToken")
        assert access_token["username"] == username

        # test admin sign out
        aws_client.cognito_idp.admin_user_global_sign_out(
            UserPoolId=user_pool["Id"], Username=username
        )
        with pytest.raises(Exception) as exp:
            aws_client.cognito_idp.admin_initiate_auth(
                AuthFlow="REFRESH_TOKEN_AUTH",
                ClientId=client_id,
                UserPoolId=user_pool["Id"],
                AuthParameters={"REFRESH_TOKEN": auth_result["RefreshToken"]},
            )
        exp.match("NotAuthorizedException")


class TestTriggers:
    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(paths=["$..scopes", "$..userAttributes.email_verified"])
    def test_pre_generation_token_trigger_v2(
        self, create_user_pool, aws_client, snapshot, trigger_lambda_pre_token_v2
    ):
        snapshot.add_transformer(
            [
                snapshot.transform.jsonpath("$..userAttributes.sub", "user-sub"),
            ]
        )
        pool_name = f"pool-{short_uid()}"
        user_pool_id = create_user_pool(
            pool_name=pool_name,
            LambdaConfig={
                "PreTokenGenerationConfig": {
                    "LambdaArn": trigger_lambda_pre_token_v2,
                    "LambdaVersion": "V2_0",
                }
            },
            UserPoolAddOns={"AdvancedSecurityMode": "ENFORCED"},
            Schema=[{"Name": "attr1", "AttributeDataType": "String"}],
            UsernameAttributes=["phone_number", "email"],
        )["Id"]

        identifier_name = f"identifier-{short_uid()}"
        resource_name = f"resource-{short_uid()}"
        aws_client.cognito_idp.create_resource_server(
            UserPoolId=user_pool_id,
            Identifier=identifier_name,
            Name=resource_name,
            Scopes=[
                {"ScopeName": "localstack.read", "ScopeDescription": "Read access"},
                {"ScopeName": "localstack.write", "ScopeDescription": "Write access"},
            ],
        )

        client_name = f"client-{short_uid()}"
        client_id = aws_client.cognito_idp.create_user_pool_client(
            UserPoolId=user_pool_id,
            ClientName=client_name,
            ExplicitAuthFlows=["ALLOW_USER_PASSWORD_AUTH", "ALLOW_REFRESH_TOKEN_AUTH"],
            AllowedOAuthScopes=[
                f"{identifier_name}/localstack.read",
                f"{identifier_name}/localstack.write",
            ],
        )["UserPoolClient"]["ClientId"]

        username = "info@localstack.cloud"
        aws_client.cognito_idp.sign_up(
            ClientId=client_id,
            Username=username,
            Password=TEST_PASSWORD,
            UserAttributes=[{"Name": "name", "Value": "John Doe"}],
            ClientMetadata={"foo": "bar"},
            ValidationData=[{"Name": "company", "Value": "localstack"}],
        )

        aws_client.cognito_idp.admin_confirm_sign_up(UserPoolId=user_pool_id, Username=username)

        result = aws_client.cognito_idp.initiate_auth(
            AuthFlow="USER_PASSWORD_AUTH",
            ClientId=client_id,
            AuthParameters={"USERNAME": username, "PASSWORD": TEST_PASSWORD},
        )

        assert "AuthenticationResult" in result
        id_token = result["AuthenticationResult"]["IdToken"]
        id_token = cognito_utils.get_token_claims(id_token)
        assert id_token["name"] == "John Doe"
        assert id_token["website"] == "https://localstack.cloud"
        assert id_token["family_name"] == "Doe"

        access_token = result["AuthenticationResult"]["AccessToken"]
        access_token = cognito_utils.get_token_claims(access_token)
        assert access_token["nickname"] == "pikachu"
        assert "openid email" in access_token["scope"]
        assert (
            "localstack" not in access_token["scope"]
        ), "all scopes should not be added by default"

        def _check_logs(filter_log: str) -> dict:
            cognito_triggers_name = arns.lambda_function_name(trigger_lambda_pre_token_v2)
            logs = testutil.get_lambda_log_events(
                function_name=cognito_triggers_name, logs_client=aws_client.logs, delay_time=1
            )
            matching = [log for log in logs if filter_log in log]
            assert matching
            cleaned_matching = clean_trigger_logs(logs=matching[0])
            assert (
                "userName" in cleaned_matching
            ), "userName missing in the Lambda Trigger Parameters"
            return cleaned_matching["request"]

        payload = retry(_check_logs, sleep=1, retries=15, filter_log=TRIGGER_TOKEN_AUTH)
        snapshot.match("trigger-log-request", payload)

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(
        paths=["$..session", "$..userAttributes['cognito:user_status']"]
    )
    def test_signup_trigger_params(self, create_user_pool, trigger_lambda, aws_client, snapshot):
        pool_name = f"pool-{short_uid()}"
        user_pool_id = create_user_pool(
            pool_name=pool_name,
            LambdaConfig={
                "PreSignUp": trigger_lambda,
            },
            Schema=[{"Name": "attr1", "AttributeDataType": "String"}],
            UsernameAttributes=["phone_number", "email"],
        )["Id"]

        def _check_logs(filter_log: str) -> dict:
            cognito_triggers_name = arns.lambda_function_name(trigger_lambda)
            logs = testutil.get_lambda_log_events(
                function_name=cognito_triggers_name, logs_client=aws_client.logs, delay_time=1
            )
            matching = [log for log in logs if filter_log in log]
            assert matching
            cleaned_matching = (
                matching[0]
                .partition("(LambdaContext")[0]
                .replace("'", '"')
                .replace("None", "null")
                .replace("True", "true")
                .replace("False", "false")
            )
            return json.loads(cleaned_matching)["request"]

        client_name = f"client-{short_uid()}"
        result = aws_client.cognito_idp.create_user_pool_client(
            UserPoolId=user_pool_id,
            ClientName=client_name,
        )
        client_id = result["UserPoolClient"]["ClientId"]

        # sign_up with the
        aws_client.cognito_idp.sign_up(
            ClientId=client_id,
            Username="info@localstack.cloud",
            Password=TEST_PASSWORD,
            UserAttributes=[{"Name": "name", "Value": "John Doe"}],
            ClientMetadata={"foo": "bar"},
            ValidationData=[{"Name": "company", "Value": "localstack"}],
        )
        payload = retry(_check_logs, sleep=1, retries=15, filter_log="PreSignUp_SignUp")
        snapshot.match("trigger-log-request", payload)

    @markers.aws.validated
    def test_cognito_admin_create_signup_triggers(
        self, create_user_pool, trigger_lambda, aws_client, snapshot
    ):
        username1 = f"user-{short_uid()}"
        username2 = f"user-{short_uid()}"
        password = TEST_PASSWORD

        snapshot.add_transformer(snapshot.transform.key_value("Username"))
        snapshot.add_transformer(
            snapshot.transform.key_value("UserSub", reference_replacement=False)
        )
        snapshot.add_transformer(JsonpathTransformer("$..User.Attributes..Value", "sub-value"))
        # different attribute naming for "describe":
        snapshot.add_transformer(JsonpathTransformer("$..UserAttributes..Value", "sub-value"))

        # create user pool
        pool_name = f"pool-{short_uid()}"
        result = create_user_pool(
            pool_name=pool_name,
            LambdaConfig={
                "PreSignUp": trigger_lambda,
                "PostConfirmation": trigger_lambda,
            },
            Schema=[{"Name": "attr1", "AttributeDataType": "String"}],
        )
        pool_id = result["Id"]

        def _check_logs(filter_log: str, expected_times: int = 0):
            cognito_triggers_name = arns.lambda_function_name(trigger_lambda)
            logs = testutil.get_lambda_log_events(
                function_name=cognito_triggers_name, logs_client=aws_client.logs, delay_time=1
            )
            matching = [log for log in logs if filter_log in log]
            assert len(matching) == expected_times

        # create user with username
        admin_create_user_result = aws_client.cognito_idp.admin_create_user(
            UserPoolId=pool_id,
            Username=username1,
            TemporaryPassword=password,
        )
        snapshot.match("admin_create_user", admin_create_user_result)

        retry(
            _check_logs,
            sleep=1,
            retries=15,
            filter_log="PreSignUp_AdminCreateUser",
            expected_times=1,
        )
        retry(
            _check_logs,
            sleep=1,
            retries=15,
            filter_log="PostConfirmation_ConfirmSignUp",
            expected_times=0,
        )

        # AdminConfirmSignup not allowed for the status "FORCE_CHANGE_PASSWORD"
        with pytest.raises(ClientError) as ctx:
            aws_client.cognito_idp.admin_confirm_sign_up(UserPoolId=pool_id, Username=username1)

        snapshot.match("error1", ctx.value.response)
        result = aws_client.cognito_idp.admin_get_user(UserPoolId=pool_id, Username=username1)
        snapshot.match("admin_get_user_username1", result)

        # create user pool client for sign-up
        result = aws_client.cognito_idp.create_user_pool_client(
            UserPoolId=pool_id,
            ClientName="client1",
            ExplicitAuthFlows=[
                "ALLOW_USER_PASSWORD_AUTH",
                "ALLOW_CUSTOM_AUTH",
                "ALLOW_REFRESH_TOKEN_AUTH",
            ],
        )
        client_id = result["UserPoolClient"]["ClientId"]

        # sign up new user, only this way the "admin_confirm_sign_up" call is valid
        result = aws_client.cognito_idp.sign_up(
            ClientId=client_id,
            Username=username2,
            Password=password,
        )
        snapshot.match("sign_up", result)
        result = aws_client.cognito_idp.admin_get_user(UserPoolId=pool_id, Username=username2)
        snapshot.match("admin_get_user_username2_1", result)

        retry(_check_logs, sleep=1, retries=15, filter_log="PreSignUp_SignUp", expected_times=1)
        retry(
            _check_logs,
            sleep=1,
            retries=15,
            filter_log="PostConfirmation_ConfirmSignUp",
            expected_times=0,
        )

        result = aws_client.cognito_idp.admin_confirm_sign_up(
            UserPoolId=pool_id, Username=username2
        )
        snapshot.match("admin_confirm_sign_up", result)

        result = aws_client.cognito_idp.admin_get_user(UserPoolId=pool_id, Username=username2)
        snapshot.match("admin_get_user_username2_2", result)

        # verify second call for "admin_confirm_sign_up" fails because the user is already confirmed
        with pytest.raises(ClientError) as ctx:
            aws_client.cognito_idp.admin_confirm_sign_up(UserPoolId=pool_id, Username=username2)

        snapshot.match("error2", ctx.value.response)
        retry(
            _check_logs,
            sleep=1,
            retries=15,
            filter_log="PostConfirmation_ConfirmSignUp",
            expected_times=1,
        )

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(
        paths=[
            "$..request.type",
            "$..request.userAttributes.email_verified",
            "$..version",
        ]
    )
    def test_cognito_custom_email_signup(self, infrastructure_setup, aws_client, snapshot):
        infra = infrastructure_setup(namespace="Trigger_CustomEmailSender_SignUp")
        stack = cdk.Stack(infra.cdk_app, "TestCustomEmailTrigger")

        snapshot.add_transformer(snapshot.transform.cognito_idp_api())
        snapshot.add_transformer(snapshot.transform.jsonpath("$..request.code", "code"))

        key_alias = "cognito-key-alias"
        symmetric_key = cdk.aws_kms.Key(
            stack,
            "SymmetricKey",
            key_spec=cdk.aws_kms.KeySpec.SYMMETRIC_DEFAULT,
            alias=key_alias,
            enable_key_rotation=False,
        )

        custom_emailer_lambda = cdk.aws_lambda.Function(
            stack,
            "CustomEmailerLambda",
            code=cdk.aws_lambda.Code.from_inline(
                "def handler(event, *args): event['response'] = {'emailMessage': 'hello'}; print(event); return event"
            ),
            handler="index.handler",
            runtime=cdk.aws_lambda.Runtime.PYTHON_3_12,
            environment={
                "KEY_ID": symmetric_key.key_arn,
                "KEY_ALIAS": key_alias,
            },
        )

        custom_emailer_lambda.add_to_role_policy(
            statement=cdk.aws_iam.PolicyStatement(
                actions=["kms:Decrypt", "kms:DescribeKey"],
                effect=cdk.aws_iam.Effect.ALLOW,
                resources=[symmetric_key.key_arn],
            )
        )

        custom_emailer_lambda.add_permission(
            "CognitoEmailSenderInvokePermission",
            principal=cdk.aws_iam.ServicePrincipal(service="cognito-idp.amazonaws.com"),
            action="lambda:InvokeFunction",
        )

        symmetric_key.add_to_resource_policy(
            statement=cdk.aws_iam.PolicyStatement(
                actions=[
                    "kms:Decrypt",
                ],
                effect=cdk.aws_iam.Effect.ALLOW,
                principals=[
                    cdk.aws_iam.ArnPrincipal(arn=custom_emailer_lambda.role.role_arn),
                    cdk.aws_iam.ServicePrincipal(service="cognito-idp.amazonaws.com"),
                ],
                resources=["*"],
            )
        )

        user_pool = cdk.aws_cognito.UserPool(
            stack,
            "UserPool",
            custom_sender_kms_key=cdk.aws_kms.Key.from_key_arn(
                stack, "CustomEmailSenderKmsKey", key_arn=symmetric_key.key_arn
            ),
            self_sign_up_enabled=True,
            auto_verify=cdk.aws_cognito.AutoVerifiedAttrs(email=True),
            user_verification=cdk.aws_cognito.UserVerificationConfig(
                email_subject="Verify your email for our awesome app!",
                email_body="Thanks for signing up to our awesome app! Your verification code is {####}",
                email_style=cdk.aws_cognito.VerificationEmailStyle.CODE,
                sms_message="Thanks for signing up to our awesome app! Your verification code is {####}",
            ),
        )

        client = user_pool.add_client(
            "user-pool-client",
            generate_secret=False,
            auth_flows=cdk.aws_cognito.AuthFlow(
                user_password=True,
                user_srp=True,
            ),
        )

        user_pool.add_trigger(
            operation=cdk.aws_cognito.UserPoolOperation.CUSTOM_EMAIL_SENDER,
            fn=cdk.aws_lambda.Function.from_function_arn(
                stack,
                "CustomEmailSenderLambda",
                function_arn=custom_emailer_lambda.function_arn,
            ),
        )

        cdk.CfnOutput(stack, "UserPoolClientId", value=client.user_pool_client_id)
        cdk.CfnOutput(stack, "LambdaArn", value=custom_emailer_lambda.function_arn)
        cdk.CfnOutput(stack, "KeyArn", value=symmetric_key.key_arn)

        with infra.provisioner() as prov:
            outputs = prov.get_stack_outputs("TestCustomEmailTrigger")
            client_id = outputs["UserPoolClientId"]
            lambda_arn = outputs["LambdaArn"]
            key_arn = outputs["KeyArn"]

            def _check_logs() -> dict:
                cognito_triggers_name = arns.lambda_function_name(lambda_arn)
                logs = testutil.get_lambda_log_events(
                    function_name=cognito_triggers_name, logs_client=aws_client.logs, delay_time=1
                )
                matching = [
                    log for log in logs if cognito_triggers.TRIGGER_CUSTOM_EMAIL_SIGNUP in log
                ]
                assert matching
                return clean_trigger_logs(matching[0])

            result = aws_client.cognito_idp.sign_up(
                ClientId=client_id,
                Username=f"user-{short_uid()}",
                Password=TEST_PASSWORD,
                UserAttributes=[{"Name": "email", "Value": "info@localstack.cloud"}],
            )
            assert result.get("UserConfirmed") is False

            logs = retry(_check_logs, sleep=1, retries=15)
            snapshot.match("trigger-logs", logs)
            assert logs.get("callerContext", {}).get("clientId") == client_id
            code = logs["request"]["code"]
            code = base64.b64decode(to_bytes(code))
            if not is_aws_cloud():
                # the code in decrypt_via_aws_encryption_sdk calls KMS on the LocalStack endpoint when running
                #   against AWS
                code = int(decrypt_via_aws_encryption_sdk(code, key_arn))
                assert 100000 <= code < 1000000, "the code is not a number with 6 digits"

            # https://docs.aws.amazon.com/encryption-sdk/latest/developer-guide/introduction.html#intro-compatibility
            # As fair as I understand, Cognito uses the encryption SDK to encrypt the code. According to the link
            #   above, the KMD Decrypt operation should not be able to decrypt a message encrypted by the SDK.
            with pytest.raises(Exception):
                aws_client.kms.decrypt(CiphertextBlob=code, KeyId=key_arn)

    @markers.only_on_amd64
    @markers.aws.validated
    def test_cognito_triggers(self, create_user_pool, trigger_lambda, aws_client):
        # create user pool
        pool_name = f"pool-{short_uid()}"
        result = create_user_pool(
            pool_name=pool_name,
            LambdaConfig={
                "PreSignUp": trigger_lambda,
                "CustomMessage": trigger_lambda,
                "PostConfirmation": trigger_lambda,
                "PreAuthentication": trigger_lambda,
                "PostAuthentication": trigger_lambda,
                "DefineAuthChallenge": trigger_lambda,
                "CreateAuthChallenge": trigger_lambda,
                "VerifyAuthChallengeResponse": trigger_lambda,
                "PreTokenGeneration": trigger_lambda,
                "UserMigration": trigger_lambda,
            },
            Schema=[{"Name": "attr1", "AttributeDataType": "String"}],
        )
        pool_id = result["Id"]

        # create user pool client
        result = aws_client.cognito_idp.create_user_pool_client(
            UserPoolId=pool_id,
            ClientName="client1",
            ExplicitAuthFlows=[
                "ALLOW_USER_PASSWORD_AUTH",
                "ALLOW_CUSTOM_AUTH",
                "ALLOW_REFRESH_TOKEN_AUTH",
            ],
        )
        client_id = result["UserPoolClient"]["ClientId"]

        # create user that should get auto-confirmed
        result = aws_client.cognito_idp.sign_up(
            ClientId=client_id,
            Username="user_autoconfirm",
            Password=TEST_PASSWORD,
            UserAttributes=[{"Name": "custom:attr1", "Value": "test123"}],
        )
        user_sub1 = result["UserSub"]
        assert result.get("UserConfirmed") is True

        def _check_logs():
            cognito_triggers_name = arns.lambda_function_name(trigger_lambda)
            logs = testutil.get_lambda_log_events(
                function_name=cognito_triggers_name, logs_client=aws_client.logs, delay_time=1
            )
            matching = [log for log in logs if "PostConfirmation_ConfirmSignUp" in log]
            assert matching
            assert "attr1" in logs[0]
            assert "test123" in logs[0]

        # check Lambda logs
        retry(_check_logs, sleep=1, retries=15)

        # create user that should not get auto-confirmed
        result = aws_client.cognito_idp.sign_up(
            ClientId=client_id, Username="user_noconfirm", Password=TEST_PASSWORD
        )
        assert result.get("UserConfirmed") is False
        user_sub2 = result["UserSub"]

        # check list-users
        users = aws_client.cognito_idp.list_users(UserPoolId=pool_id)["Users"]
        assert len(users) == 2
        for user in users:
            assert len([a for a in user.get("Attributes", []) if a["Name"] == "sub"]) == 1
        users = aws_client.cognito_idp.list_users(
            UserPoolId=pool_id, Filter='username="user_noconfirm"'
        )["Users"]
        assert len(users) == 1
        for sub in [user_sub1, user_sub2]:
            users = aws_client.cognito_idp.list_users(UserPoolId=pool_id, Filter=f'sub="{sub}"')[
                "Users"
            ]
            assert len(users) == 1

        # check custom claims on initiate auth flow
        result = aws_client.cognito_idp.initiate_auth(
            AuthFlow="USER_PASSWORD_AUTH",
            ClientId=client_id,
            AuthParameters={
                "USERNAME": "user_autoconfirm",
                "PASSWORD": TEST_PASSWORD,
                "_skip_trigger_": "1",
            },
        )
        assert "AuthenticationResult" in result
        token = result["AuthenticationResult"]["IdToken"]
        token = cognito_utils.get_token_claims(token)
        assert token.get("add_attr1") == "value1"
        assert "client_id" not in token

        def assert_pw_email_received():
            email = SENT_EMAILS[-1]
            assert email["subject"] == "Test email subject"
            assert code in email["message"]
            assert username in email["message"]

        # run "forgot password" flows only locally, not in real AWS
        if not is_aws_cloud():
            # trigger forgot password flow with custom message
            username = "user_autoconfirm"
            aws_client.cognito_idp.admin_update_user_attributes(
                UserPoolId=pool_id,
                Username=username,
                UserAttributes=[{"Name": "email", "Value": "test@example.com"}],
            )
            aws_client.cognito_idp.forgot_password(ClientId=client_id, Username=username)
            code = cognito_utils.CONFIRMATION_CODES[-1]
            retry(assert_pw_email_received)
            aws_client.cognito_idp.admin_set_user_password(
                UserPoolId=pool_id, Username=username, Password=TEST_PASSWORD, Permanent=True
            )
            # trigger forgot password flow for non-existing user
            username = "new-user-6201"
            aws_client.cognito_idp.forgot_password(ClientId=client_id, Username=username)
            code = cognito_utils.CONFIRMATION_CODES[-1]
            retry(assert_pw_email_received)

        # trigger custom authentication flow
        result = aws_client.cognito_idp.initiate_auth(
            AuthFlow="CUSTOM_AUTH",
            ClientId=client_id,
            AuthParameters={"USERNAME": "user_autoconfirm", "PASSWORD": TEST_PASSWORD},
        )
        aws_client.cognito_idp.respond_to_auth_challenge(
            ChallengeName="CUSTOM_CHALLENGE",
            ClientId=client_id,
            Session=result["Session"],
            ChallengeResponses={"ANSWER": CHALLENGE_ANSWER, "USERNAME": "user_autoconfirm"},
        )

        # assert exception with invalid user, rejected by pre-authentication trigger Lambda
        with pytest.raises(Exception) as exc:
            aws_client.cognito_idp.initiate_auth(
                AuthFlow="USER_PASSWORD_AUTH",
                ClientId=client_id,
                AuthParameters={"USERNAME": "invalid-user", "PASSWORD": TEST_PASSWORD},
            )
        exc.match("UserNotFoundException")
        exc.match("UserMigration failed with error")

    @markers.aws.validated
    # TODO: investigate discrepancy of returned (e.g.., this test vs. test_srp_custom_auth_flow)
    @markers.snapshot.skip_snapshot_verify(paths=["$..ChallengeParameters.USERNAME"])
    def test_custom_auth_triggers(
        self,
        trigger_lambda,
        create_pool_client_and_user,
        get_lambda_invocation_events,
        add_cognito_snapshot_transformers,
        snapshot,
        aws_client,
    ):
        # TODO: fix with new Lambda provider (should contain proper version qualifier)
        snapshot.add_transformer(
            snapshot.transform.key_value("version", reference_replacement=False)
        )

        # create user pool, client, and test user
        pool_id, client_id, username = create_pool_client_and_user(
            LambdaConfig={
                "DefineAuthChallenge": trigger_lambda,
                "CreateAuthChallenge": trigger_lambda,
                "VerifyAuthChallengeResponse": trigger_lambda,
            }
        )

        # trigger custom auth flow for invalid user
        with pytest.raises(ClientError) as ctx:
            aws_client.cognito_idp.initiate_auth(
                AuthFlow="CUSTOM_AUTH",
                ClientId=client_id,
                AuthParameters={"USERNAME": "user1", "CHALLENGE_NAME": "SRP_A"},
            )
        snapshot.match("error1", ctx.value.response)

        # trigger custom auth flow
        result = aws_client.cognito_idp.initiate_auth(
            AuthFlow="CUSTOM_AUTH",
            ClientId=client_id,
            AuthParameters={"USERNAME": username, "CHALLENGE_NAME": "SRP_A"},
        )
        snapshot.match("result1", result)

        # respond to auth challenge
        result = aws_client.cognito_idp.respond_to_auth_challenge(
            ClientId=client_id,
            ChallengeName=result["ChallengeName"],
            Session=result["Session"],
            ChallengeResponses={"USERNAME": username, "ANSWER": CHALLENGE_ANSWER},
        )
        snapshot.match("result2", result)

        # receive and assert detailed events
        messages = get_lambda_invocation_events(trigger_lambda, 4)
        snapshot.match("lambda_events1", messages)

    @markers.aws.validated
    def test_auth_trigger_group_overrides(
        self,
        trigger_lambda,
        get_lambda_invocation_events,
        create_pool_client_and_user,
        snapshot,
        add_cognito_snapshot_transformers,
        aws_client,
    ):
        # TODO: fix logic - these are currently contained in the Lambda event as empty []/{}, but should be removed
        for entry in ["clientMetadata", "session", "validationData", "version"]:
            snapshot.add_transformer(
                snapshot.transform.key_value(entry, reference_replacement=False)
            )

        # create user pool, client, and test user
        pool_id, client_id, username = create_pool_client_and_user(
            LambdaConfig={
                "PreTokenGeneration": trigger_lambda,
            },
            Schema=[{"Name": "userId", "AttributeDataType": "String"}],
        )
        snapshot.add_transformer(snapshot.transform.regex(username, "<username>"))

        # add user attributes
        response = aws_client.cognito_idp.admin_get_user(UserPoolId=pool_id, Username=username)
        snapshot.match("user-details", response)
        response = aws_client.cognito_idp.admin_update_user_attributes(
            UserPoolId=pool_id,
            Username=username,
            UserAttributes=[{"Name": "custom:userId", "Value": username}],
        )
        snapshot.match("user-details-updated", response)

        # create groups
        aws_client.cognito_idp.create_group(GroupName="group1", UserPoolId=pool_id)
        aws_client.cognito_idp.create_group(GroupName="group2", UserPoolId=pool_id)
        aws_client.cognito_idp.create_group(GroupName="group3", UserPoolId=pool_id)
        aws_client.cognito_idp.create_group(GroupName="group4", UserPoolId=pool_id)
        aws_client.cognito_idp.admin_add_user_to_group(
            UserPoolId=pool_id, Username=username, GroupName="group3"
        )

        # trigger auth flow
        def _initiate_auth():
            return aws_client.cognito_idp.initiate_auth(
                AuthFlow="USER_PASSWORD_AUTH",
                ClientId=client_id,
                AuthParameters={"USERNAME": username, "PASSWORD": TEST_PASSWORD},
            )

        result = retry(_initiate_auth, retries=7, sleep=2)
        snapshot.match("auth_result", result.get("AuthenticationResult"))
        claim_attrs = [
            "client_id",
            "event_id",
            "scope",
            "sub",
            "token_use",
            "username",
            "cognito:groups",
        ]
        id_claims = get_token_claims(result["AuthenticationResult"]["IdToken"])
        id_claims = select_attributes(id_claims, claim_attrs)
        snapshot.match("id_token_claims", id_claims)
        access_claims = get_token_claims(result["AuthenticationResult"]["AccessToken"])
        access_claims = select_attributes(access_claims, claim_attrs)
        snapshot.match("access_token_claims", access_claims)

        # get groups info (should be empty, for AWS parity)
        group_users = aws_client.cognito_idp.list_users_in_group(
            UserPoolId=pool_id, GroupName="group1"
        )
        snapshot.match("group1_users", group_users["Users"])

        # get trigger Lambda events
        messages = get_lambda_invocation_events(trigger_lambda, 1)
        snapshot.match("lambda_events", messages)

    @pytest.mark.parametrize("aliases", [None, "email", "preferred_username"])
    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(
        paths=[
            "$..origin_jti",  # missing from Access Token
            "$..req.version",  # AWS returns 1, we return $LATEST
            "$.initiate-auth-id-token-defined.'cognito:user_status'",  # AWS does not return this
            "$.initiate-auth-id-token-defined.email_verified",  # wrong type, should be a bool and we return 'true'
            "$.initiate-auth-id-token-defined.jti",  # missing from LS
        ]
    )
    def test_user_migration_lambda(
        self,
        create_user_pool_client,
        aliases,
        trigger_lambda,
        update_user_attributes,
        aws_client,
        get_lambda_invocation_events,
        snapshot,
        add_cognito_jwt_token_transformers,
    ):
        # TODO: consolidate transformers, but we don't want some values to be transformed, like userName
        snapshot.add_transformer(snapshot.transform.key_value("userPoolId"))

        kwargs = {"AliasAttributes": [aliases]} if aliases else {}
        user_pool_result = create_user_pool_client(pool_kwargs=kwargs)
        pool_client = user_pool_result.pool_client
        user_pool = user_pool_result.user_pool
        client_id = pool_client["ClientId"]
        func_arn = trigger_lambda

        response = aws_client.cognito_idp.update_user_pool(
            UserPoolId=user_pool["Id"], LambdaConfig={"UserMigration": func_arn}
        )
        assert response["ResponseMetadata"]["HTTPStatusCode"] == 200

        if aliases == "preferred_username":
            usernames = ["test1234-nonexisting", "test1234@nonexisting.com"]
        elif aliases == "email":
            usernames = ["test1234-nonexisting"]
        else:
            # to avoid the following issue:
            # "Username cannot be of email format, since user pool is configured for email alias."
            usernames = ["test1234-nonexisting", "user-preferred"]

        # assert that the login works with a new / non-existing user
        for username in usernames:
            for i in range(2):
                result = aws_client.cognito_idp.initiate_auth(
                    AuthFlow="USER_PASSWORD_AUTH",
                    ClientId=client_id,
                    AuthParameters={"USERNAME": username, "PASSWORD": "test123"},
                    ClientMetadata={"foo": "bar"},
                )
                access_token = result["AuthenticationResult"]["AccessToken"]
                claims = jwt.decode(access_token, options={"verify_signature": False}) or {}
                snapshot_type = "email" if "@" in username else username
                snapshot.match(f"initiate-auth-access-{snapshot_type}-{i}", claims)

        # test changing user attributes
        update_user_attributes(
            user_pool["Id"], username="test1234-nonexisting", value="test_attr_value"
        )

        # assert that the login is denied if the migration trigger Lambda raises an error
        if aliases == "email":
            # to avoid the following issue:
            # "Username cannot be of email format, since user pool is configured for email alias."
            bad_usernames = ["test1234-nonexisting-error"]
        else:
            bad_usernames = ["test1234-nonexisting-error", "test1234@nonexisting-error.com"]

        for username in bad_usernames:
            for _ in range(2):
                with pytest.raises(Exception) as ctx:
                    aws_client.cognito_idp.initiate_auth(
                        AuthFlow="USER_PASSWORD_AUTH",
                        ClientId=client_id,
                        AuthParameters={"USERNAME": username, "PASSWORD": "test123"},
                    )
                assert "UserNotFoundException" in str(ctx.value)

        # test for the trigger to attach a new user-defined username
        if not aliases:
            with pytest.raises(ClientError) as e:
                aws_client.cognito_idp.initiate_auth(
                    AuthFlow="USER_PASSWORD_AUTH",
                    ClientId=client_id,
                    AuthParameters={"USERNAME": "user-defined-test", "PASSWORD": "test123"},
                    ClientMetadata={"foo": "bar"},
                )
            snapshot.match("no-user-attached-when-no-alias", e.value.response)

        else:
            username = "user-defined-test@ex.com" if aliases == "email" else "user-defined-test"
            result = aws_client.cognito_idp.initiate_auth(
                AuthFlow="USER_PASSWORD_AUTH",
                ClientId=client_id,
                AuthParameters={"USERNAME": username, "PASSWORD": "test123"},
                ClientMetadata={"alias_type": aliases},
            )
            access_token = result["AuthenticationResult"]["AccessToken"]
            claims = jwt.decode(access_token, options={"verify_signature": False}) or {}
            snapshot.match("initiate-auth-access-defined", claims)
            id_token = result["AuthenticationResult"]["IdToken"]
            claims_id = jwt.decode(id_token, options={"verify_signature": False}) or {}
            snapshot.match("initiate-auth-id-token-defined", claims_id)

        get_users = aws_client.cognito_idp.list_users(UserPoolId=user_pool["Id"])
        get_users["Users"].sort(key=itemgetter("Username"))
        for user in get_users["Users"]:
            user["Attributes"].sort(key=itemgetter("Name"))
        snapshot.match("get-users", get_users)

        # get trigger Lambda events
        messages = get_lambda_invocation_events(
            trigger_lambda, 3 if aliases == "preferred_username" else 2
        )
        snapshot.match("lambda_events", messages)

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(paths=["$..version", "$..iss", "$..origin_jti"])
    def test_custom_challenge_trigger_params(
        self,
        create_pool_client_and_user,
        create_user_pool_client,
        create_lambda_with_invocation_forwarding,
        add_cognito_snapshot_transformers,
        add_cognito_jwt_token_transformers,
        snapshot,
        aws_client,
    ):
        lambda_code = textwrap.dedent(
            """
        import boto3, json
        def handler(event, context):
            event_orig = json.loads(json.dumps(event))
            trigger, response, request = event["triggerSource"], event["response"], event["request"]
            print(event)
            session = request.get("session") or []
            if trigger == "DefineAuthChallenge_Authentication":
                if len(session) == 0:
                    response["issueTokens"] = False
                    response["failAuthentication"] = False
                    response["challengeName"] = "CUSTOM_CHALLENGE"
                elif len(session) == 1:
                    response["issueTokens"] = True
                    response["failAuthentication"] = False
            if trigger == "CreateAuthChallenge_Authentication":
                if request["challengeName"] == "CUSTOM_CHALLENGE":
                    response["privateChallengeParameters"] = {"answer": "test-answer-123"}
                    response["publicChallengeParameters"] = {}
            if trigger == "VerifyAuthChallengeResponse_Authentication":
                correct_answer = request["privateChallengeParameters"]["answer"]
                response["answerCorrect"] = request["challengeAnswer"] == correct_answer
            return event
        """
        )
        trigger_lambda = create_lambda_with_invocation_forwarding(lambda_source=lambda_code)
        pool_kwargs = {
            "Policies": {
                "PasswordPolicy": {
                    "MinimumLength": 8,
                    "RequireUppercase": False,
                    "RequireLowercase": False,
                    "RequireNumbers": True,
                    "RequireSymbols": True,
                }
            },
            "AliasAttributes": ["email", "phone_number"],
            "LambdaConfig": {
                "DefineAuthChallenge": trigger_lambda,
                "CreateAuthChallenge": trigger_lambda,
                "VerifyAuthChallengeResponse": trigger_lambda,
            },
        }
        client_kwargs = {
            "ExplicitAuthFlows": [
                "ALLOW_ADMIN_USER_PASSWORD_AUTH",
                "ALLOW_REFRESH_TOKEN_AUTH",
                "ALLOW_CUSTOM_AUTH",
                "ALLOW_USER_SRP_AUTH",
                "ALLOW_USER_PASSWORD_AUTH",
            ],
            "GenerateSecret": False,
        }
        pool_result = create_user_pool_client(client_kwargs=client_kwargs, pool_kwargs=pool_kwargs)
        client, user_pool = pool_result.pool_client, pool_result.user_pool

        username = f"user-{short_uid()}"
        aws_client.cognito_idp.admin_create_user(
            UserPoolId=user_pool["Id"],
            Username=username,
            UserAttributes=[
                {"Name": "email", "Value": "john@doe.com"},
                {"Name": "name", "Value": "John Doe"},
                {"Name": "phone_number", "Value": "+12131234125"},
                {"Name": "phone_number_verified", "Value": "true"},
            ],
            DesiredDeliveryMediums=["EMAIL"],
        )
        aws_client.cognito_idp.admin_set_user_password(
            Username=username, UserPoolId=user_pool["Id"], Permanent=True, Password=TEST_PASSWORD
        )
        result = aws_client.cognito_idp.initiate_auth(
            AuthFlow="CUSTOM_AUTH",
            ClientId=client["ClientId"],
            AuthParameters={
                "USERNAME": "+12131234125",
            },
        )
        snapshot.match("initiate-auth", result)

        result = aws_client.cognito_idp.admin_respond_to_auth_challenge(
            ClientId=client["ClientId"],
            UserPoolId=user_pool["Id"],
            ChallengeName="CUSTOM_CHALLENGE",
            ChallengeResponses={"USERNAME": username, "ANSWER": "test-answer-123"},
            Session=result["Session"],
        )
        snapshot.match("respond-to-auth", result)
        access_token = result["AuthenticationResult"]["AccessToken"]
        token = cognito_utils.get_token_claims(access_token)
        snapshot.match("access-token", token)

        def _get_trigger_logs(filter_log: str, expected_occurrences: int = 1) -> list[dict]:
            cognito_triggers_name = arns.lambda_function_name(trigger_lambda)
            logs = testutil.get_lambda_log_events(
                function_name=cognito_triggers_name, logs_client=aws_client.logs, delay_time=1
            )
            matching = [log for log in logs if filter_log in log]
            assert len(matching) == expected_occurrences
            return [clean_trigger_logs(logs=matching[i]) for i in range(expected_occurrences)]

        payload = retry(
            _get_trigger_logs,
            sleep=1,
            retries=15,
            filter_log=TRIGGER_AUTH_DEFINE_CHALL,
            expected_occurrences=2,
        )
        snapshot.match("trigger-define-auth-first", payload[0])
        snapshot.match("trigger-define-auth-second", payload[1])

        payload = retry(
            _get_trigger_logs,
            sleep=1,
            retries=15,
            filter_log=TRIGGER_AUTH_CREATE_CHALL,
        )
        snapshot.match("trigger-auth-create-chall", payload)

        payload = retry(
            _get_trigger_logs, sleep=1, retries=15, filter_log=TRIGGER_AUTH_VERIFY_CHALL
        )
        snapshot.match("trigger-auth-verify-chall", payload)


class TestCognitoIdentity:
    @markers.aws.validated
    def test_create_identity_get_id(
        self, signup_and_login_user, create_user_pool_client, snapshot, aws_client
    ):
        snapshot.add_transformer(snapshot.transform.key_value("IdentityPoolName"))
        snapshot.add_transformer(snapshot.transform.key_value("ClientId"))
        snapshot.add_transformer(snapshot.transform.key_value("IdentityId"))

        # create user pool
        user_pool_result = create_user_pool_client()
        client = user_pool_result.pool_client
        snapshot.add_transformer(
            snapshot.transform.regex(user_pool_result.user_pool["Id"], "<user-pool-id>")
        )

        # create user and identity pool
        username = f"user-{short_uid()}"
        password = "SecretPw1!"
        credentials, identity_id, id_pool_id = signup_and_login_user(client, username, password)
        snapshot.add_transformer(snapshot.transform.regex(id_pool_id, "<identity-pool-id>"))

        # assert details of identity pool
        result = aws_client.cognito_identity.describe_identity_pool(IdentityPoolId=id_pool_id)
        result = remove_attributes(result, ["ResponseMetadata"])
        snapshot.match("identity-pool", result)

        # attempt to get ID without specifying `logins` parameter
        result = aws_client.cognito_identity.get_id(IdentityPoolId=id_pool_id)
        result = remove_attributes(result, ["ResponseMetadata"])
        snapshot.match("id-result", result)

    @markers.aws.unknown
    def test_cognito_identity_get_id_region_matches(self, aws_client_factory):
        region_name = "us-west-2"
        aws_client = aws_client_factory(region_name=region_name)
        cognito_identity_client = aws_client.cognito_identity

        identity_pool_name = f"identity-pool-{short_uid()}"
        id_pool_id = cognito_identity_client.create_identity_pool(
            IdentityPoolName=identity_pool_name,
            CognitoIdentityProviders=[],
            AllowUnauthenticatedIdentities=True,
        )["IdentityPoolId"]

        identity_id = cognito_identity_client.get_id(IdentityPoolId=id_pool_id)["IdentityId"]
        assert region_name in identity_id
