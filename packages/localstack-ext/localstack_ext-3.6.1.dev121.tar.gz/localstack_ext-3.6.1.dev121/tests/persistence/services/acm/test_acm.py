import pytest


@pytest.mark.skip("To investigate")
def test_request_certificate(persistence_validations, snapshot, aws_client):
    arn = aws_client.acm.request_certificate(DomainName="example.com")["CertificateArn"]

    def validate():
        snapshot.match(
            "request_certificate", aws_client.acm.describe_certificate(CertificateArn=arn)
        )

    persistence_validations.register(validate)
