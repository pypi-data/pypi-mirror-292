import requests
from localstack import config
from localstack.utils.strings import short_uid


class TestCertificateResource:
    def test_list_root_ca(self):
        assert requests.get(f"{config.external_service_url()}/_localstack/certs/ca").json() == {
            "name": "LocalStack_LOCAL_Root_CA",
            "url": "http://localhost.localstack.cloud:4566/_localstack/certs/ca/LocalStack_LOCAL_Root_CA.crt",
        }

    def test_get_root_ca(self):
        response = requests.get(f"{config.external_service_url()}/_localstack/certs/ca/foo.crt")
        assert response.status_code == 404

        response = requests.get(
            f"{config.external_service_url()}/_localstack/certs/ca/LocalStack_LOCAL_Root_CA.crt"
        )
        assert response.headers["Content-Type"] == "application/pem-certificate-chain"
        assert "-----BEGIN CERTIFICATE-----" in response.text

    def test_crud_cert(self):
        """Full CRUD cycle over certs"""
        name = f"{short_uid()}.test-domain.com"
        cert_url = f"{config.external_service_url()}/_localstack/certs/{name}"

        response = requests.get(cert_url)
        assert response.status_code == 404

        response = requests.post(cert_url)
        doc = response.json()
        assert doc["paths"]["cert"].endswith(f"var/lib/localstack/cache/certs/{name}/cert.pem")
        assert doc["paths"]["privkey"].endswith(
            f"var/lib/localstack/cache/certs/{name}/privkey.pem"
        )
        assert doc["pem"]["cert"].startswith("-----BEGIN CERTIFICATE-----")
        assert doc["pem"]["privkey"].startswith("-----BEGIN RSA PRIVATE KEY-----")

        # post is idempotent
        assert doc == requests.post(cert_url).json()

        # get returns the same response as post
        response = requests.get(cert_url)
        doc2 = response.json()
        assert doc == doc2

        response = requests.delete(cert_url)
        assert response.status_code == 200

        # deleting again returns 404
        response = requests.delete(cert_url)
        assert response.status_code == 404

    def test_list_certs_returns_correct_urls(self):
        # create a cert
        name = f"{short_uid()}.test-domain.com"
        cert_url = f"{config.external_service_url()}/_localstack/certs/{name}"
        requests.post(cert_url)

        # find the URL via list
        doc = requests.get(f"{config.external_service_url()}/_localstack/certs").json()
        cert_dict = {cert["name"]: cert["url"] for cert in doc["certs"]}
        assert name in cert_dict

        response = requests.get(cert_dict[name])
        doc = response.json()
        assert doc["paths"]["cert"].endswith(f"var/lib/localstack/cache/certs/{name}/cert.pem")
        assert doc["paths"]["privkey"].endswith(
            f"var/lib/localstack/cache/certs/{name}/privkey.pem"
        )
        assert doc["pem"]["cert"].startswith("-----BEGIN CERTIFICATE-----")
        assert doc["pem"]["privkey"].startswith("-----BEGIN RSA PRIVATE KEY-----")

        # cleanup
        requests.delete(cert_url)
