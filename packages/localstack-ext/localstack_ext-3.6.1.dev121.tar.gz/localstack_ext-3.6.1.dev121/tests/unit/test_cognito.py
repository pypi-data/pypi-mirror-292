import pytest
from localstack.pro.core.services.cognito_idp.cognito_triggers import (
    get_pre_signup_trigger_parameters,
    get_trigger_lambda_config,
)
from localstack.pro.core.services.cognito_idp.cognito_utils import (
    generate_rsa_keys,
    get_kid_from_key,
)
from localstack.pro.core.services.cognito_idp.provider import (
    check_valid_password,
    check_valid_username,
    get_attribute_from_saml_assertion,
    get_user_attributes,
    get_xml_attribute,
    get_xml_tag_text,
    is_valid_custom_pool_id,
)
from localstack.utils.collections import is_sub_dict


def test_get_user_attributes():
    user = {
        "UserAttributes": [
            {"Name": "email", "Value": "email123"},
            {"Name": "attr1", "Value": "value1"},
            {"Name": "attr2", "Value": "value2"},
        ]
    }

    result = get_user_attributes(user, "email")
    assert is_sub_dict({"email": "email123"}, result)
    result = get_user_attributes(user, ["email", "attr1"])
    assert is_sub_dict({"email": "email123", "attr1": "value1"}, result)
    result = get_user_attributes(user)
    assert is_sub_dict({"email": "email123", "attr1": "value1", "attr2": "value2"}, result)


def test_password_policy():
    def _valid(password):
        try:
            check_valid_password(password)
            return True
        except Exception:
            return False

    assert not _valid("test")
    assert not _valid("                                ")
    assert not _valid(" - ")
    assert not _valid("foo123!")
    assert not _valid("aB12!")

    assert _valid("Test1234!")


def test_get_pre_signup_trigger_event():
    user_attributes = {
        "ClientId": "wy48bl9hq0jl5h1ujtvk23g3xi",
        "Username": "user_autoconfirm",
        "Password": "Test123!",
        "SecretHash": None,
        "UserAttributes": [{"Name": "attr1", "Value": "test123"}],
        "ValidationData": [
            {"Name": "custom:familyName", "Value": "SUPER_FAMILY_NAME_VALIDATION"},
            {"Name": "custom:givenName", "Value": "SUPER_GIVEN_NAME_VALIDATION"},
        ],
        "AnalyticsMetadata": None,
        "UserContextData": None,
        "ClientMetadata": {
            "familyName": "SUPER_FAMILY_NAME_META_DATA",
            "givenName": "SUPER_GIVEN_NAME_CLIENT_META_DATA",
        },
        "UserStatus": "UNCONFIRMED",
    }
    request = get_pre_signup_trigger_parameters(user_attributes)["request"]
    assert "userAttributes" in request
    assert "validationData" in request
    assert "clientMetadata" in request


def test_kid_from_public_key():
    public_key, _ = generate_rsa_keys(2048)
    oracle = get_kid_from_key(public_key)
    assert oracle == get_kid_from_key(public_key)

    public_key, _ = generate_rsa_keys(2048)
    assert oracle != get_kid_from_key(public_key)


def test_custom_pool_id():
    assert is_valid_custom_pool_id("us-east-1_hello")
    assert is_valid_custom_pool_id("us-east-1_1234")
    assert not is_valid_custom_pool_id("us-east-1")
    assert not is_valid_custom_pool_id("hello")


def test_check_valid_username():
    with pytest.raises(Exception):
        check_valid_username("info@localstack.cloud", ["phone_number"])
        check_valid_username("+12345678901", ["email"])

    check_valid_username("+12345678901", ["phone_number"])
    check_valid_username("+12345678901", ["phone_number", "email"])
    check_valid_username("+12345678901", [])

    check_valid_username("info@localstack.cloud", ["phone_number", "email"])
    check_valid_username("info@localstack.cloud", ["email"])
    check_valid_username("info@localstack.cloud", [])


def test_get_lambda_config_pre_token_generation_config(monkeypatch):
    from localstack.pro.core.services.cognito_idp import models

    lambda_config = {
        "PreTokenGenerationConfig": {
            "LambdaArn": "arn:aws:lambda:us-east-1:000000000000:function:test_inv_forward-da4b730e",
            "LambdaVersion": "V2_0",
        },
    }
    user_pool = models.UserPool(details={"LambdaConfig": lambda_config})
    monkeypatch.setattr(models, "find_pool", lambda **kwargs: user_pool)

    config = get_trigger_lambda_config("test-pool", "TokenGeneration_Authentication")
    assert config == lambda_config["PreTokenGenerationConfig"]


def test_saml_utils():
    # example of a valid SAML assertion
    xml = """<samlp:Response xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol" ID="_ef85ab40d86fa6c960cd"  Version="2.0" IssueInstant="2024-03-05T20:03:37.828Z"  Destination="https://localhost.localstack.cloud:4566/_aws/cognito-idp/saml2/idpresponse"><saml:Issuer xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion">urn:dev-cc74fjl4w46udioq.us.auth0.com</saml:Issuer><samlp:Status><samlp:StatusCode Value="urn:oasis:names:tc:SAML:2.0:status:Success"/></samlp:Status><saml:Assertion xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion" Version="2.0" ID="_YSoKASc1xAjztcYa6GvoVrwWgfDjEVDD" IssueInstant="2024-03-05T20:03:37.823Z"><saml:Issuer>urn:dev-cc74fjl4w46udioq.us.auth0.com</saml:Issuer><Signature xmlns="http://www.w3.org/2000/09/xmldsig#"><SignedInfo><CanonicalizationMethod Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#"/><SignatureMethod Algorithm="http://www.w3.org/2001/04/xmldsig-more#rsa-sha256"/><Reference URI="#_YSoKASc1xAjztcYa6GvoVrwWgfDjEVDD"><Transforms><Transform Algorithm="http://www.w3.org/2000/09/xmldsig#enveloped-signature"/><Transform Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#"/></Transforms><DigestMethod Algorithm="http://www.w3.org/2001/04/xmlenc#sha256"/><DigestValue>9qj33TdDyuebNAecwAk1F8eh7FcBpDGP8CldVAggbdg=</DigestValue></Reference></SignedInfo><SignatureValue>EJ958QKq1yLvFCRwneW8T2GuyOGRFqDs/8ViQUy1hD7+SXjbTo2GTaTg2ZRr3u/pqRQoccYVSPoTyTeVDEKUnsF+TyHRTAZIvHloWmAPoZKx99le/WcsgZUOZxNp0q/o+E/qMKfNMkwEzeE9bKj9HA0VdQWPdY6AD8nRG2l0c20vabgeGD+vGJ9VEfQ6sssGkeY4WIQSj4hidssDB6kbQVTjX84XsQDPMeigga+T7WWUEexovCt35sCCO82DdGT2QfThGAcLQFLQt/LssciwgftZOTFGCJzQiuPj7I/eV0Q9ANX0+MHZD/jKssHb41FmZsbN0impQe3w8UKi5sTVqQ==</SignatureValue><KeyInfo><X509Data><X509Certificate>MIIDHTCCAgWgAwIBAgIJQGx08Hlrv/MpMA0GCSqGSIb3DQEBCwUAMCwxKjAoBgNVBAMTIWRldi1jYzc0ZmpsNHc0NnVkaW9xLnVzLmF1dGgwLmNvbTAeFw0yMzA2MjYxNDE0MDhaFw0zNzAzMDQxNDE0MDhaMCwxKjAoBgNVBAMTIWRldi1jYzc0ZmpsNHc0NnVkaW9xLnVzLmF1dGgwLmNvbTCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBAKpjXGcMCGvWj2MsNoDCvHVY9V+Ni+sB9bY7H4TAsk+HkjgwZO8rIy1hRVmEy0JQndgmbDxNl5ulBeLutqryDL8Xqoou5nt0S1mwNZMSeMoEdqSxBUbVeb4l10ww7YfOUB4wex7NALQo3UFnWTFOuZn3VQF70wHgdmfmuuqaKvsmTyFP3mIyjyCv06p151JYCw1/sGYB4exRummbOb7hKU9mrlDG5rso1StYX6OwUxc/ezcYDRPZYG12P18/PR606rGoa7pUZtUeuz5Ad4ddIWMXH1j2OPYISxd+tisWbW4OOmBDs4cftgFeEvP9a5NfSbigXQSbuc5SNuzO7rEPUksCAwEAAaNCMEAwDwYDVR0TAQH/BAUwAwEB/zAdBgNVHQ4EFgQUzt+/ZYUPg3g56C04LKPddWLswmowDgYDVR0PAQH/BAQDAgKEMA0GCSqGSIb3DQEBCwUAA4IBAQARtsmdrw0a/B46ZW2802omEM+cNlSrdfszzgyCKqRFRk3E4LsJdVROiKwYsmLbCGdlM7MoUwj7SHTQsyyCOAHffpOPyVKaylx2XHovy2UN1nC9dKvEKMnPh+1VYn29hkk74KgCB1VKhLbbefzDxQTK+nsQ+HQW91ib2SgNDgsx3+msm+jYBI3ALdcXS58cFGlLD3CQo2KL0VlazGI1No5B2HOC4UT1bD4KN72HS81epkm2PxmkA1sNH8pE7m7Us2jgrcSjlQfwBTNdVEn8qWvfTlhRkiWi+Agf8pIIkUTKzEG+HRlv0I6S8lI4EuCG5Z/MaF62bMyaFQWs/0oIfLbw</X509Certificate></X509Data></KeyInfo></Signature><saml:Subject><saml:NameID Format="urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress">e2e-334528fe243b@localstack.cloud</saml:NameID><saml:SubjectConfirmation Method="urn:oasis:names:tc:SAML:2.0:cm:bearer"><saml:SubjectConfirmationData NotOnOrAfter="2024-03-05T21:03:37.823Z" Recipient="https://localhost.localstack.cloud:4566/_aws/cognito-idp/saml2/idpresponse"/></saml:SubjectConfirmation></saml:Subject><saml:Conditions NotBefore="2024-03-05T20:03:37.823Z" NotOnOrAfter="2024-03-05T21:03:37.823Z"><saml:AudienceRestriction><saml:Audience>urn:amazon:cognito:sp:us-east-1_idptest</saml:Audience></saml:AudienceRestriction></saml:Conditions><saml:AuthnStatement AuthnInstant="2024-03-05T20:03:37.823Z" SessionIndex="_VqtdmWGUdGF9sch1CzcgRncWD3VUTPXD"><saml:AuthnContext><saml:AuthnContextClassRef>urn:oasis:names:tc:SAML:2.0:ac:classes:unspecified</saml:AuthnContextClassRef></saml:AuthnContext></saml:AuthnStatement><saml:AttributeStatement xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><saml:Attribute Name="email" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:basic"><saml:AttributeValue xsi:type="xs:string">e2e-334528fe243b@localstack.cloud</saml:AttributeValue></saml:Attribute><saml:Attribute Name="name" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:basic"><saml:AttributeValue xsi:type="xs:string">e2e-334528fe243b@localstack.cloud</saml:AttributeValue></saml:Attribute></saml:AttributeStatement></saml:Assertion></samlp:Response>"""

    attr = get_xml_attribute(xml_content=xml, tag="NameID", attribute="Format")
    assert attr == "urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress"

    name_id = get_xml_tag_text(xml_content=xml, tag="NameID")
    assert name_id == "e2e-334528fe243b@localstack.cloud"

    text = get_xml_tag_text(xml_content=xml, tag="Audience")
    assert text == "urn:amazon:cognito:sp:us-east-1_idptest"

    assert (
        get_attribute_from_saml_assertion(xml_content=xml, attribute="email")
        == "e2e-334528fe243b@localstack.cloud"
    )
