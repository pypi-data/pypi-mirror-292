from urllib.parse import urljoin

import pytest
import requests
from localstack.pro.core.services.ec2.imds.constants import (
    HEADER_LOCALSTACK_IMDS_ACCOUNT,
    HEADER_LOCALSTACK_IMDS_INSTANCE,
    HEADER_LOCALSTACK_IMDS_REGION,
)
from localstack.pro.core.services.ec2.imds.server import InstanceMetadataGatewayServer
from localstack.testing.pytest import markers
from localstack.utils.net import get_free_tcp_port


class TestEC2IMDSServer:
    #
    # Fixtures
    #

    @pytest.fixture
    def instance(self, aws_client, ec2_test_ami):
        """Creates an EC2 instance and returns its details."""
        response = aws_client.ec2.run_instances(
            ImageId=ec2_test_ami[0],
            MinCount=1,
            MaxCount=1,
            InstanceType="t3.micro",
        )
        yield response["Instances"][0]
        aws_client.ec2.terminate_instances(InstanceIds=[response["Instances"][0]["InstanceId"]])

    @pytest.fixture(scope="class")
    def server(self):
        port = get_free_tcp_port()
        server = InstanceMetadataGatewayServer(lambda _: None, port=port)
        server.start()

        yield f"http://localhost:{port}"

        server.shutdown()

    @pytest.fixture
    def imds_get(self, server, account_id, region_name, instance):
        def _imds_get(path: str, headers: dict = None):
            headers = headers or {}
            headers[HEADER_LOCALSTACK_IMDS_ACCOUNT] = account_id
            headers[HEADER_LOCALSTACK_IMDS_REGION] = region_name
            headers[HEADER_LOCALSTACK_IMDS_INSTANCE] = instance["InstanceId"]

            url = urljoin(server, path)

            response = requests.get(url, headers=headers)
            return response

        return _imds_get

    @pytest.fixture
    def imds_put(self, server, account_id, region_name, instance):
        def _imds_put(path: str, headers: dict = None):
            headers = headers or {}
            url = urljoin(server, path)
            return requests.put(url, headers=headers)

        return _imds_put

    #
    # Tests
    #

    @markers.aws.only_localstack
    def test_versions(self, imds_get):
        response = imds_get("/")
        assert response.text == "latest"

    @markers.aws.only_localstack
    def test_metadata_categories(self, imds_get):
        response = imds_get("/latest/meta-data/")
        expected = """ami-id
ami-launch-index
instance-id
instance-type
local-hostname
local-ipv4
public-hostname
public-ipv4"""
        assert response.text == expected

    @markers.aws.only_localstack
    def test_imdsv2_ttl(self, imds_get, imds_put, instance):
        # Ensure TTL header is required when requesting token
        response = imds_put("/latest/api/token")
        assert response.status_code == 400

        # Assert valid TTL values when requesting token
        # Valid TTL is between 1 and 21,600 seconds
        response = imds_put(
            "/latest/api/token", headers={"x-aws-ec2-metadata-token-ttl-seconds": "0"}
        )
        assert response.status_code == 400

        response = imds_put(
            "/latest/api/token", headers={"x-aws-ec2-metadata-token-ttl-seconds": "21601"}
        )
        assert response.status_code == 400

        response = imds_put(
            "/latest/api/token", headers={"x-aws-ec2-metadata-token-ttl-seconds": "xyz"}
        )
        assert response.status_code == 400

        # Assert IMDSv2 requests
        response = imds_put(
            "/latest/api/token", headers={"x-aws-ec2-metadata-token-ttl-seconds": "300"}
        )
        response = imds_get(
            "/latest/meta-data/ami-id/", headers={"X-aws-ec2-metadata-token": response.text}
        )
        assert response.text == instance["ImageId"]

        expired_token = "MTcwNDc5NjQ1Nwo="
        response = imds_get(
            "/latest/meta-data/ami-id/", headers={"X-aws-ec2-metadata-token": expired_token}
        )
        assert response.status_code == 401

        response = imds_get(
            "/latest/meta-data/ami-id/", headers={"X-aws-ec2-metadata-token": "xyz"}
        )
        assert response.status_code == 400

    @markers.aws.only_localstack
    def test_ami_id(self, imds_get, instance):
        response = imds_get("/latest/meta-data/ami-id/")
        assert response.headers.get("content-type").startswith("text/plain")
        assert response.text == instance["ImageId"]

    @markers.aws.only_localstack
    def test_ami_launch_index(self, imds_get, instance):
        response = imds_get("/latest/meta-data/ami-launch-index/")
        assert response.headers.get("content-type").startswith("text/plain")
        assert response.text == "0"

    @markers.aws.only_localstack
    def test_instance_id(self, imds_get, instance):
        response = imds_get("/latest/meta-data/instance-id/")
        assert response.headers.get("content-type").startswith("text/plain")
        assert response.text == instance["InstanceId"]

    @markers.aws.only_localstack
    def test_instance_type(self, imds_get, instance):
        response = imds_get("/latest/meta-data/instance-type/")
        assert response.headers.get("content-type").startswith("text/plain")
        assert response.text == "t3.micro"

    @markers.aws.only_localstack
    def test_local_hostname(self, imds_get, instance):
        response = imds_get("/latest/meta-data/local-hostname/")
        assert response.headers.get("content-type").startswith("text/plain")
        assert response.text == instance["PrivateDnsName"]

    @markers.aws.only_localstack
    def test_local_ipv4(self, imds_get, instance):
        response = imds_get("/latest/meta-data/local-ipv4/")
        assert response.headers.get("content-type").startswith("text/plain")
        assert response.text == instance["PrivateIpAddress"]

    @markers.aws.only_localstack
    def test_public_hostname(self, imds_get, instance):
        response = imds_get("/latest/meta-data/public-hostname/")
        assert response.headers.get("content-type").startswith("text/plain")
        assert response.text == instance["PublicDnsName"]

    @markers.aws.only_localstack
    def test_public_ipv4(self, imds_get, instance):
        response = imds_get("/latest/meta-data/public-ipv4/")
        assert response.headers.get("content-type").startswith("text/plain")
        assert response.text == instance["PublicIpAddress"]

    @markers.aws.only_localstack
    def test_instance_identity_document(self, imds_get, instance, account_id, region_name):
        start_timestamp = instance["LaunchTime"].isoformat().replace("+00:00", ".000Z")
        expected = {
            "devpayProductCodes": None,
            "marketplaceProductCodes": ["abcdefghijklmnopqrstuvwxyz"],
            "availabilityZone": instance["Placement"]["AvailabilityZone"],
            "privateIp": instance["PrivateIpAddress"],
            "version": "2017-09-30",
            "instanceId": instance["InstanceId"],
            "billingProducts": None,
            "instanceType": instance["InstanceType"],
            "accountId": account_id,
            "imageId": instance["ImageId"],
            "pendingTime": start_timestamp,
            "architecture": instance["Architecture"],
            "kernelId": None,
            "ramdiskId": None,
            "region": region_name,
        }
        response = imds_get("/latest/dynamic/instance-identity/document")
        assert response.json() == expected
        assert response.headers.get("content-type").startswith("application/json")
