from localstack.testing.pytest import markers


class TestACMPCA:
    @markers.aws.validated
    def test_create_describe_tag_ca(self, aws_client, cleanups):
        client = aws_client.acm_pca

        create_response = client.create_certificate_authority(
            CertificateAuthorityConfiguration={
                "KeyAlgorithm": "RSA_2048",
                "SigningAlgorithm": "SHA256WITHRSA",
                "Subject": {
                    "Country": "US",
                    "Organization": "Example Corp",
                    "OrganizationalUnit": "Sales",
                    "State": "WA",
                    "Locality": "Seattle",
                    "CommonName": "www.example.com",
                },
            },
            RevocationConfiguration={"OcspConfiguration": {"Enabled": True}},
            CertificateAuthorityType="ROOT",
            Tags=[{"Key": "Name", "Value": "MyPCA"}],
        )
        cleanups.append(
            lambda: aws_client.acm_pca.delete_certificate_authority(
                CertificateAuthorityArn=create_response["CertificateAuthorityArn"]
            )
        )

        ca_arn = create_response["CertificateAuthorityArn"]

        describe_response = client.describe_certificate_authority(CertificateAuthorityArn=ca_arn)
        assert describe_response["CertificateAuthority"]["Arn"] == ca_arn

        client.tag_certificate_authority(
            CertificateAuthorityArn=ca_arn, Tags=[{"Key": "Admin", "Value": "Alice"}]
        )

        tag_response = client.list_tags(CertificateAuthorityArn=ca_arn)
        assert {"Key": "Admin", "Value": "Alice"} in tag_response["Tags"]
