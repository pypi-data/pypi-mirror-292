import pytest
from localstack.pro.core.aws.api.account import ContactInformation
from localstack.testing.pytest import markers


class TestAccount:
    @markers.aws.validated
    def test_contact_information(self, aws_client, cleanups, snapshot):
        client = aws_client.account

        contact = ContactInformation(
            FullName="Jane Doe",
            PhoneNumber="+19108085844",
            AddressLine1="123 Main St",
            City="Seattle",
            PostalCode="98101",
            CountryCode="US",
            StateOrRegion="WA",
        )

        put_contact_information = client.put_contact_information(ContactInformation=contact)

        snapshot.match("put_contact_information", put_contact_information)
        get_contact_information = client.get_contact_information()
        snapshot.match("get_contact_information", get_contact_information)

    @markers.snapshot.skip_snapshot_verify(
        paths=["$..AlternateContact.AlternateContactType", "$..Error.Message", "$..message"]
    )
    @markers.aws.validated
    def test_alternate_contact(self, aws_client, snapshot):
        client = aws_client.account

        client.put_alternate_contact(
            AlternateContactType="BILLING",
            EmailAddress="bill@ing.com",
            Name="Bill Ing",
            PhoneNumber="+1 555-555-5555",
            Title="Billing",
        )
        get_alternate_contact = client.get_alternate_contact(AlternateContactType="BILLING")
        snapshot.match("get_alternate_contact", get_alternate_contact)
        assert get_alternate_contact["AlternateContact"]["EmailAddress"] == "bill@ing.com"

        client.delete_alternate_contact(AlternateContactType="BILLING")
        with pytest.raises(Exception) as e:
            client.get_alternate_contact(AlternateContactType="BILLING")
        snapshot.match("get_alternate_contact_notfound_exc", e.value.response)

    @markers.snapshot.skip_snapshot_verify(paths=["$..Error.Message", "$..message"])
    @markers.aws.validated
    def test_unavailable_alternate_contact(self, aws_client, snapshot):
        client = aws_client.account

        with pytest.raises(Exception) as excinfo:
            client.get_alternate_contact(AlternateContactType="BILLING")
        snapshot.match("get_alternate_contact_notfound_exc", excinfo.value.response)
