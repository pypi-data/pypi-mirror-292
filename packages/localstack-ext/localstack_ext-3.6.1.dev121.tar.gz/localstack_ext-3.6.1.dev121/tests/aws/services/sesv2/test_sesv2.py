import base64
from unittest import mock

import pytest
from botocore.exceptions import ClientError
from localstack.pro.core import config as config_ext
from localstack.testing.pytest import markers
from localstack.utils.strings import short_uid


@pytest.fixture
def patch_smtp_send_email_message(monkeypatch):
    """This fixture sets the SMTP_HOST so that the patched SMTP handler is invoked"""
    monkeypatch.setattr(config_ext, "SMTP_HOST", "localhost")
    with mock.patch("localstack.pro.core.services.sesv2.provider.send_email_message") as p:
        yield p


@pytest.fixture
def patch_smtp_send_email(monkeypatch):
    """This fixture sets the SMTP_HOST so that the patched SMTP handler is invoked"""
    monkeypatch.setattr(config_ext, "SMTP_HOST", "localhost")
    with mock.patch("localstack.pro.core.services.sesv2.provider.send_email") as p:
        yield p


class TestSesv2:
    @markers.aws.unknown
    def test_email_identities(self, aws_client):
        test_domain = f"{short_uid()}.local"
        test_email = f"foo@{test_domain}"

        # Ensure that identity type is detected
        response = aws_client.sesv2.create_email_identity(EmailIdentity=test_email)
        assert response["IdentityType"] == "EMAIL_ADDRESS"
        response = aws_client.sesv2.create_email_identity(EmailIdentity=test_domain)
        assert response["IdentityType"] == "DOMAIN"

        # Ensure ListEmailIdentity
        response = aws_client.sesv2.list_email_identities()
        assert {"IdentityType": "EMAIL_ADDRESS", "IdentityName": test_email} in response[
            "EmailIdentities"
        ]
        assert {"IdentityType": "DOMAIN", "IdentityName": test_domain} in response[
            "EmailIdentities"
        ]

        # Ensure GetEmailIdentity raises for invalid IDs
        with pytest.raises(ClientError) as exc:
            aws_client.sesv2.get_email_identity(EmailIdentity="invalid.identity")
        err = exc.value.response["Error"]
        assert err["Code"] == "NotFoundException"
        assert err["Message"] == "Email identity 'invalid.identity' does not exist"

        # Ensure GetEmailIdentity returns correct type
        response = aws_client.sesv2.get_email_identity(EmailIdentity=test_domain)
        assert response["IdentityType"] == "DOMAIN"
        response = aws_client.sesv2.get_email_identity(EmailIdentity=test_email)
        assert response["IdentityType"] == "EMAIL_ADDRESS"

        # Ensure DeleteEmailIdentity
        aws_client.sesv2.delete_email_identity(EmailIdentity=test_domain)
        with pytest.raises(ClientError) as exc:
            aws_client.sesv2.get_email_identity(EmailIdentity=test_domain)
        err = exc.value.response["Error"]
        assert err["Code"] == "NotFoundException"
        assert err["Message"] == f"Email identity '{test_domain}' does not exist"

    @markers.aws.unknown
    def test_send_email(self, raw_test_email, simple_test_email, aws_client):
        raw = {"Data": base64.b64encode(raw_test_email)}
        email_content = {"Simple": simple_test_email, "Raw": raw}

        # Must raise when 1+ email types (Raw, Simple or Template) are set in content
        with pytest.raises(ClientError) as exc:
            aws_client.sesv2.send_email(Content=email_content)
        err = exc.value.response["Error"]
        assert err["Code"] == "BadRequestException"
        assert err["Message"] == "Content must have a single content type"

    @markers.aws.unknown
    def test_send_email_raw(self, raw_test_email, patch_smtp_send_email_message, aws_client):
        # Assert that SMTP helper is called
        email_content = {"Raw": {"Data": base64.b64encode(raw_test_email)}}
        aws_client.sesv2.send_email(Content=email_content)
        patch_smtp_send_email_message.assert_called_once()

    @markers.aws.unknown
    def test_send_email_simple(self, simple_test_email, patch_smtp_send_email, aws_client):
        # Assert that SMTP helper is called with correct args
        email_content = {"Simple": simple_test_email}
        to_addresses = ["recipient@example.com"]
        from_address = "sender@example.com"

        aws_client.sesv2.send_email(
            Content=email_content,
            Destination={"ToAddresses": to_addresses},
            FromEmailAddress=from_address,
        )

        subject = simple_test_email["Subject"]["Data"]
        html_message = simple_test_email["Body"]["Html"]["Data"]
        text_message = simple_test_email["Body"]["Text"]["Data"]

        patch_smtp_send_email.assert_called_with(
            subject, text_message, to_addresses, from_email=from_address, html_message=html_message
        )

    @markers.aws.unknown
    def test_send_email_template(self, patch_smtp_send_email, aws_client):
        # Ensure that email templating works correctly
        template_name = short_uid()
        to_addresses = ["recipient@example.com"]
        from_address = "sender@example.com"

        aws_client.sesv2.create_email_template(
            TemplateName=template_name,
            TemplateContent={
                "Subject": "{{name}}, your favourite animal",
                "Text": "Dear {{name}},\nYour favourite animal is {{animal}}.",
                "Html": "<h1>Hello {{name}},</h1><p>Your favourite animal is <b>{{animal}}</b>.</p>",
            },
        )

        template_data = '{"name":"Linus","animal":"penguin"}'

        aws_client.sesv2.send_email(
            Content={"Template": {"TemplateName": template_name, "TemplateData": template_data}},
            Destination={"ToAddresses": to_addresses},
            FromEmailAddress=from_address,
        )

        expected_subject = "Linus, your favourite animal"
        expected_text = "Dear Linus,\nYour favourite animal is penguin."
        expected_html = "<h1>Hello Linus,</h1><p>Your favourite animal is <b>penguin</b>.</p>"

        patch_smtp_send_email.assert_called_with(
            expected_subject,
            expected_text,
            to_addresses,
            from_email=from_address,
            html_message=expected_html,
        )

    @markers.aws.unknown
    def test_send_bulk_email(self, patch_smtp_send_email, aws_client):
        valid_template = "lorem"
        aws_client.sesv2.create_email_template(
            TemplateName=valid_template,
            TemplateContent={
                "Html": "{{placeholder}}",
                "Subject": "{{placeholder}}",
                "Text": "{{placeholder}}",
            },
        )

        valid_sender = "foo@example.com"
        aws_client.sesv2.create_email_identity(EmailIdentity=valid_sender)

        to_addr = ["1@example.com"]
        cc_addr = ["2@example.com"]
        bcc_addr = ["3@example.com"]
        entries = [
            {
                "Destination": dict(
                    ToAddresses=to_addr, CcAddresses=cc_addr, BccAddresses=bcc_addr
                ),
                "ReplacementEmailContent": {
                    "ReplacementTemplate": {
                        "ReplacementTemplateData": '{"placeholder": "templating works!"}'
                    }
                },
            }
        ]

        # Must raise if sender email address is not verified
        invalid_email = "bar@example.com"
        with pytest.raises(ClientError) as exc:
            aws_client.sesv2.send_bulk_email(
                FromEmailAddress=invalid_email,
                BulkEmailEntries=entries,
                DefaultContent={
                    "Template": {
                        "TemplateData": "{}",
                        "TemplateName": valid_template,
                    }
                },
            )
        err = exc.value.response["Error"]
        assert err["Code"] == "MessageRejected"
        assert (
            err["Message"]
            == f"Email address is not verified. The following identities failed the check: {invalid_email}"
        )

        # Must raise if default template name is invalid
        invalid_template = "invalid_template123"
        with pytest.raises(ClientError) as exc:
            aws_client.sesv2.send_bulk_email(
                FromEmailAddress=valid_sender,
                BulkEmailEntries=entries,
                DefaultContent={
                    "Template": {
                        "TemplateData": "{}",
                        "TemplateName": invalid_template,
                    }
                },
            )
        err = exc.value.response["Error"]
        assert err["Code"] == "NotFoundException"
        assert err["Message"] == f"Template {invalid_template} does not exist"

        # Expect error if <1 recipient
        entries_without_recipients = [
            {**entry, "Destination": {"ToAddresses": []}} for entry in entries
        ]
        response = aws_client.sesv2.send_bulk_email(
            FromEmailAddress=valid_sender,
            BulkEmailEntries=entries_without_recipients,
            DefaultContent={
                "Template": {
                    "TemplateData": "{}",
                    "TemplateName": valid_template,
                }
            },
        )
        assert len(response["BulkEmailEntryResults"]) == 1
        assert response["BulkEmailEntryResults"][0]["Status"] == "INVALID_PARAMETER"
        assert response["BulkEmailEntryResults"][0]["Error"] == "Destination cannot be empty"

        # Fallback to default template data if not available
        entries_without_template_data = [
            {
                **entry,
                "ReplacementEmailContent": {"ReplacementTemplate": {"ReplacementTemplateData": ""}},
            }
            for entry in entries
        ]
        response = aws_client.sesv2.send_bulk_email(
            FromEmailAddress=valid_sender,
            BulkEmailEntries=entries_without_template_data,
            DefaultContent={
                "Template": {
                    "TemplateData": '{"placeholder": "cake!"}',
                    "TemplateName": valid_template,
                }
            },
        )
        expected_call = mock.call(
            "cake!",
            "cake!",
            ["1@example.com", "2@example.com", "3@example.com"],
            from_email="foo@example.com",
            html_message="cake!",
        )
        patch_smtp_send_email.assert_has_calls([expected_call])
        patch_smtp_send_email.reset_mock()
        assert len(response["BulkEmailEntryResults"]) == 1
        assert response["BulkEmailEntryResults"][0]["Status"] == "SUCCESS"

        # Test happy path
        response = aws_client.sesv2.send_bulk_email(
            FromEmailAddress=valid_sender,
            BulkEmailEntries=3 * entries,
            DefaultContent={
                "Template": {
                    "TemplateData": "{}",
                    "TemplateName": valid_template,
                }
            },
        )
        assert len(response["BulkEmailEntryResults"]) == 3
        expected_calls = 3 * [
            mock.call(
                "templating works!",
                "templating works!",
                ["1@example.com", "2@example.com", "3@example.com"],
                from_email="foo@example.com",
                html_message="templating works!",
            )
        ]
        patch_smtp_send_email.assert_has_calls(expected_calls)
