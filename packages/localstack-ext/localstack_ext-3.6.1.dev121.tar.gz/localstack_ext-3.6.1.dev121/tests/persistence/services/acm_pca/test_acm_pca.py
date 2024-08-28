from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import Encoding
from cryptography.x509.oid import NameOID


def generate_csr():
    # Generate a 2048-bit RSA private key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    csr = (
        x509.CertificateSigningRequestBuilder()
        .subject_name(
            x509.Name(
                [
                    x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
                    x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Washington"),
                    x509.NameAttribute(NameOID.LOCALITY_NAME, "Seattle"),
                    x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Example Corp"),
                    x509.NameAttribute(NameOID.COMMON_NAME, "www.example.com"),
                ]
            )
        )
        .sign(private_key, hashes.SHA256())
    )

    return csr.public_bytes(Encoding.PEM).decode()


def test_issue_get_certificate(persistence_validations, snapshot, aws_client):
    create_response = aws_client.acm_pca.create_certificate_authority(
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

    ca_arn = create_response["CertificateAuthorityArn"]
    csr_pem = generate_csr()

    issue_response = aws_client.acm_pca.issue_certificate(
        CertificateAuthorityArn=ca_arn,
        Csr=csr_pem,
        SigningAlgorithm="SHA256WITHRSA",
        Validity={"Value": 365, "Type": "DAYS"},
    )

    certificate_arn = issue_response["CertificateArn"]

    def validate():
        snapshot.match("issue_certificate", issue_response)

        get_cert_response = aws_client.acm_pca.get_certificate(
            CertificateAuthorityArn=ca_arn, CertificateArn=certificate_arn
        )
        snapshot.match("get_certificate", get_cert_response)

    persistence_validations.register(validate)
