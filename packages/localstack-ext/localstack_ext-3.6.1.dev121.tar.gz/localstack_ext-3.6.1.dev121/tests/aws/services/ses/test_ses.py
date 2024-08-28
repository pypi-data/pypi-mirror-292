import time
from unittest import mock

import pytest
from botocore.exceptions import ClientError
from localstack.pro.core import config as config_ext
from localstack.testing.aws.util import is_aws_cloud
from localstack.testing.pytest import markers
from localstack.utils.strings import short_uid


@pytest.fixture
def patch_smtp_send_email_message(monkeypatch):
    """This fixture sets the SMTP_HOST so that the patched SMTP handler is invoked"""
    monkeypatch.setattr(config_ext, "SMTP_HOST", "localhost")
    with mock.patch("localstack.pro.core.services.ses.provider.send_email_message") as p:
        yield p


@pytest.fixture
def patch_smtp_send_email(monkeypatch):
    """This fixture sets the SMTP_HOST so that the patched SMTP handler is invoked"""
    monkeypatch.setattr(config_ext, "SMTP_HOST", "localhost")
    with mock.patch("localstack.pro.core.services.ses.provider.send_email") as p:
        yield p


class TestSes:
    @markers.aws.unknown
    def test_send_email(self, simple_test_email, patch_smtp_send_email, aws_client):
        # Test that SMTP is called with correct email fields
        sender = "sender@example.com"
        recipients = ["recipient1@example.com", "recipient2@example.com"]

        aws_client.ses.verify_email_identity(EmailAddress=sender)
        aws_client.ses.send_email(
            Destination={"ToAddresses": recipients},
            Message=simple_test_email,
            Source=sender,
        )

        expected_subject = simple_test_email["Subject"]["Data"]
        expected_text_message = simple_test_email["Body"]["Text"]["Data"]
        expected_html_message = simple_test_email["Body"]["Html"]["Data"]

        patch_smtp_send_email.assert_called_with(
            expected_subject,
            expected_text_message,
            recipients,
            from_email=sender,
            html_message=expected_html_message,
        )

    @markers.aws.unknown
    def test_send_email_html_only(self, simple_test_email, patch_smtp_send_email, aws_client):
        # Test that SMTP is called with correct email fields
        del simple_test_email["Body"]["Text"]
        sender = "sender@example.com"
        recipients = ["recipient1@example.com", "recipient2@example.com"]

        aws_client.ses.verify_email_identity(EmailAddress=sender)
        aws_client.ses.send_email(
            Destination={"ToAddresses": recipients},
            Message=simple_test_email,
            Source=sender,
        )

        expected_subject = simple_test_email["Subject"]["Data"]
        expected_html_message = simple_test_email["Body"]["Html"]["Data"]

        patch_smtp_send_email.assert_called_with(
            expected_subject, "", recipients, from_email=sender, html_message=expected_html_message
        )

    @markers.aws.unknown
    def test_raw_email(self, raw_test_email, patch_smtp_send_email_message, aws_client):
        email_content = {"Data": raw_test_email}
        sender = "sender@example.com"

        aws_client.ses.verify_email_identity(EmailAddress=sender)
        aws_client.ses.send_raw_email(RawMessage=email_content)

        patch_smtp_send_email_message.assert_called_once()

    @markers.aws.unknown
    def test_templated_email(self, patch_smtp_send_email, aws_client):
        # Ensure templating works
        template_name = short_uid()
        to_addresses = ["recipient@example.com"]
        from_address = "sender@example.com"

        aws_client.ses.create_template(
            Template={
                "TemplateName": template_name,
                "SubjectPart": "{{name}}, your favourite animal",
                "TextPart": "Dear {{name}},\nYour favourite animal is {{animal}}.",
                "HtmlPart": "<h1>Hello {{name}},</h1><p>Your favourite animal is <b>{{animal}}</b>.</p>",
            }
        )

        template_data = '{"name":"Will Smith","animal":"slap!!"}'

        aws_client.ses.verify_email_identity(EmailAddress=from_address)
        aws_client.ses.send_templated_email(
            Source=from_address,
            Destination={"ToAddresses": to_addresses},
            Template=template_name,
            TemplateData=template_data,
        )

        expected_subject = "Will Smith, your favourite animal"
        expected_text = "Dear Will Smith,\nYour favourite animal is slap!!."
        expected_html = "<h1>Hello Will Smith,</h1><p>Your favourite animal is <b>slap!!</b>.</p>"

        patch_smtp_send_email.assert_called_with(
            expected_subject,
            expected_text,
            to_addresses,
            from_email=from_address,
            html_message=expected_html,
        )

    @markers.aws.unknown
    def test_send_bulk_templated_email(self, patch_smtp_send_email, aws_client, cleanups):
        valid_template = f"example-{short_uid()}"
        aws_client.ses.create_template(
            Template={
                "TemplateName": valid_template,
                "SubjectPart": "{{placeholder}}",
                "TextPart": "{{placeholder}}",
                "HtmlPart": "{{placeholder}}",
            }
        )
        cleanups.append(lambda: aws_client.ses.delete_template(TemplateName=valid_template))

        valid_source = "verified@localstack.cloud"
        aws_client.ses.verify_email_identity(EmailAddress=valid_source)

        # Must fail for unverified sender
        invalid_source = "invalid@localstack.cloud"
        response = aws_client.ses.send_bulk_templated_email(
            Source=invalid_source,
            Template=valid_template,
            Destinations=[{"Destination": {"ToAddresses": []}, "ReplacementTemplateData": "{}"}],
            DefaultTemplateData="{}",
        )
        assert len(response["Status"]) == 1
        assert response["Status"][0]["Status"] == "MailFromDomainNotVerified"
        assert (
            response["Status"][0]["Error"]
            == f"Email address is not verified. The following identities failed the check: {invalid_source}"
        )
        patch_smtp_send_email.assert_not_called()

        # Must fail if <1 recipient
        response = aws_client.ses.send_bulk_templated_email(
            Source=valid_source,
            Template=valid_template,
            Destinations=[{"Destination": {"ToAddresses": []}, "ReplacementTemplateData": "{}"}],
            DefaultTemplateData="{}",
        )
        assert len(response["Status"]) == 1
        assert response["Status"][0]["Status"] == "Failed"
        assert response["Status"][0]["Error"] == "Destination cannot be empty"
        patch_smtp_send_email.assert_not_called()

        # Must raise for more than 50 senders
        response = aws_client.ses.send_bulk_templated_email(
            Source=valid_source,
            Template=valid_template,
            Destinations=[
                {
                    "Destination": {"ToAddresses": 51 * [valid_source]},
                    "ReplacementTemplateData": "{}",
                }
            ],
            DefaultTemplateData="{}",
        )
        assert len(response["Status"]) == 1
        assert response["Status"][0]["Status"] == "Failed"
        assert response["Status"][0]["Error"] == "Recipient count exceeds 50"
        patch_smtp_send_email.assert_not_called()

        # Must raise if template is invalid
        invalid_template = "blah"
        response = aws_client.ses.send_bulk_templated_email(
            Source=valid_source,
            Template=invalid_template,
            Destinations=[
                {"Destination": {"ToAddresses": [valid_source]}, "ReplacementTemplateData": "{}"}
            ],
            DefaultTemplateData="{}",
        )
        assert len(response["Status"]) == 1
        assert response["Status"][0]["Status"] == "TemplateDoesNotExist"
        assert response["Status"][0]["Error"] == f"Template {invalid_template} does not exist"
        patch_smtp_send_email.assert_not_called()

        # Ensure everything works for happy path
        to_addr = ["1@example.com"]
        cc_addr = ["3@example.com", "4@example.com"]
        bcc_addr = ["2@example.com"]
        test_destinations = 3 * [
            {
                "Destination": {
                    "ToAddresses": to_addr,
                    "BccAddresses": bcc_addr,
                    "CcAddresses": cc_addr,
                },
                "ReplacementTemplateData": '{"placeholder": "templating works!"}',
            }
        ]
        response = aws_client.ses.send_bulk_templated_email(
            Source=valid_source,
            Template=valid_template,
            Destinations=test_destinations,
            DefaultTemplateData="{}",
        )
        assert len(response["Status"]) == 3
        expected_calls = 3 * [
            mock.call(
                "templating works!",
                "templating works!",
                to_addr + cc_addr + bcc_addr,
                from_email="verified@localstack.cloud",
                html_message="templating works!",
            )
        ]
        patch_smtp_send_email.assert_has_calls(expected_calls)

    @markers.aws.unknown
    def test_receipt_rule_set(self, aws_client):
        rule_set_name = f"receipt-rule-set-{short_uid()}"
        aws_client.ses.create_receipt_rule_set(RuleSetName=rule_set_name)

        # Ensure describe rule set
        response = aws_client.ses.describe_receipt_rule_set(RuleSetName=rule_set_name)
        assert response["Metadata"]["Name"] == rule_set_name
        assert len(response["Rules"]) == 0

        # Ensure ListReceiptRuleSet
        response = aws_client.ses.list_receipt_rule_sets()
        assert len(response["RuleSets"]) == 1
        assert rule_set_name in [rule_set["Name"] for rule_set in response["RuleSets"]]

        # Ensure CreateReceiptRuleSet raises for duplicate rule set names
        with pytest.raises(ClientError) as exc:
            aws_client.ses.create_receipt_rule_set(RuleSetName=rule_set_name)
        err = exc.value.response["Error"]
        assert err["Code"] == "RuleSetNameAlreadyExists"
        assert err["Message"] == "Duplicate Receipt Rule Set Name."

        # Ensure DeleteReceiptRuleSet deletes rule
        aws_client.ses.delete_receipt_rule_set(RuleSetName=rule_set_name)

        # Ensure DescribeReceiptRuleSet raises for non-existent rule sets
        with pytest.raises(ClientError) as exc:
            aws_client.ses.describe_receipt_rule_set(RuleSetName=rule_set_name)
        err = exc.value.response["Error"]
        assert err["Code"] == "RuleSetDoesNotExist"
        assert err["Message"] == f"Rule set does not exist: {rule_set_name}"

    @markers.aws.unknown
    def test_receipt_rule(self, aws_client):
        #
        # CreateReceiptRuleSet
        #

        rule_set_name = f"receipt-rule-set-{short_uid()}"
        aws_client.ses.create_receipt_rule_set(RuleSetName=rule_set_name)

        rule_name = f"rule-{short_uid()}"
        rule = {"Name": rule_name}

        # Ensure create receipt rule raises for invalid rule set
        with pytest.raises(ClientError) as exc:
            aws_client.ses.create_receipt_rule(RuleSetName="invalid", Rule=rule)
        err = exc.value.response["Error"]
        assert err["Code"] == "RuleSetDoesNotExist"
        assert err["Message"] == "Invalid Rule Set Name."

        aws_client.ses.create_receipt_rule(RuleSetName=rule_set_name, Rule=rule)

        # Ensure create receipt rule raises for duplicate rule name
        with pytest.raises(ClientError) as exc:
            aws_client.ses.create_receipt_rule(RuleSetName=rule_set_name, Rule=rule)
        err = exc.value.response["Error"]
        assert err["Code"] == "RuleAlreadyExists"
        assert err["Message"] == "Duplicate Rule Name."

        #
        # DescribeReceiptRuleSet
        #

        # Ensure Describe Receipt rule raises for invalid rule set
        with pytest.raises(ClientError) as exc:
            aws_client.ses.describe_receipt_rule(RuleSetName="invalid", RuleName=rule_name)
        err = exc.value.response["Error"]
        assert err["Code"] == "RuleSetDoesNotExist"
        assert err["Message"] == "Invalid Rule Set Name."

        # Ensure Describe Receipt rule raises for invalid rule
        invalid_rule_name = "invalid-rule"
        with pytest.raises(ClientError) as exc:
            aws_client.ses.describe_receipt_rule(
                RuleSetName=rule_set_name, RuleName=invalid_rule_name
            )
        err = exc.value.response["Error"]
        assert err["Code"] == "RuleDoesNotExist"
        assert err["Message"] == "Invalid Rule Name."

        # Ensure Describe Receipt rule
        response = aws_client.ses.describe_receipt_rule(
            RuleSetName=rule_set_name, RuleName=rule_name
        )
        assert response["Rule"]["Name"] == rule_name

        #
        # DeleteReceiptRuleSet
        #

        # Ensure Delete receipt rule raises for invlid rule set
        with pytest.raises(ClientError) as exc:
            aws_client.ses.delete_receipt_rule(RuleSetName="invalid", RuleName=rule_name)
        err = exc.value.response["Error"]
        assert err["Code"] == "RuleSetDoesNotExist"
        assert err["Message"] == "Invalid Rule Set Name."

        # Ensure Delete Receipt rule set
        aws_client.ses.delete_receipt_rule(RuleSetName=rule_set_name, RuleName=rule_name)

        # Ensure Delete Receipt rule raises for invalid rule
        with pytest.raises(ClientError) as exc:
            aws_client.ses.delete_receipt_rule(RuleSetName=rule_set_name, RuleName=rule_name)
        err = exc.value.response["Error"]
        assert err["Code"] == "RuleDoesNotExist"
        assert err["Message"] == "Invalid Rule Name."

    @markers.aws.validated
    def test_active_receipt_rule_set(self, aws_client):
        rule_set_name = f"receipt-rule-set-{short_uid()}"
        aws_client.ses.create_receipt_rule_set(RuleSetName=rule_set_name)

        # Ensure SetActiveReceiptRuleSet raises for invalid rule set
        with pytest.raises(ClientError) as exc:
            aws_client.ses.set_active_receipt_rule_set(RuleSetName="invalid")
        err = exc.value.response["Error"]
        assert err["Code"] == "RuleSetDoesNotExist"
        assert err["Message"] == "Rule set does not exist: invalid"

        # Many of the SES client operations are rate-limited to 1 operation per second
        # i.e https://docs.aws.amazon.com/ses/latest/APIReference/API_SetActiveReceiptRuleSet.html
        # > You can execute this operation no more than once per second.
        if is_aws_cloud():
            time.sleep(1)

        # Ensure SetActiveReceiptRuleSet
        aws_client.ses.set_active_receipt_rule_set(RuleSetName=rule_set_name)

        # Ensure DescribeActiveReceiptRuleSet
        response = aws_client.ses.describe_active_receipt_rule_set()
        assert response["Metadata"]["Name"] == rule_set_name

        if is_aws_cloud():
            time.sleep(1)

        # Cannot delete active rule set
        with pytest.raises(ClientError) as exc:
            aws_client.ses.delete_receipt_rule_set(RuleSetName=rule_set_name)
        err = exc.value.response["Error"]
        assert err["Code"] == "CannotDelete"
        assert err["Message"] == f"Cannot delete active rule set: {rule_set_name}"

        # Deactivate receipt rule set to allow for deletion
        aws_client.ses.set_active_receipt_rule_set()

        if is_aws_cloud():
            time.sleep(1)

        # Delete receipt rule set
        aws_client.ses.delete_receipt_rule_set(RuleSetName=rule_set_name)

        # Ensure DescribeActiveReceiptRuleSet
        response = aws_client.ses.describe_active_receipt_rule_set()
        assert "ResponseMetadata" in response
        assert "Metadata" not in response
