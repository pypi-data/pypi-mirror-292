import pytest
from botocore.exceptions import ClientError
from localstack.testing.pytest import markers
from localstack.utils.strings import short_uid, to_str


class TestMediastore:
    @markers.aws.unknown
    def test_basic_mediastore_api(self, aws_client, aws_client_factory):
        container_name = "c-%s" % short_uid()
        path = "root/%s.txt" % short_uid()

        rs = aws_client.mediastore.create_container(
            ContainerName=container_name, Tags=[{"Key": "environment", "Value": "testing"}]
        )

        assert rs

        endpoint = rs["Container"]["Endpoint"]

        body = "Lorem ipsum dolor sit amet ... " * 49

        md_client = aws_client_factory(endpoint_url=endpoint).mediastore_data
        # put object
        rs = md_client.put_object(
            Body=str.encode(body),
            Path=path,
            ContentType="text/plain",
            CacheControl="",
            StorageClass="TEMPORAL",
            UploadAvailability="STANDARD",
        )
        assert rs
        assert rs["StorageClass"] == "TEMPORAL"

        etag = rs["ETag"]

        # describe object
        rs = md_client.describe_object(Path=path)
        assert rs["ETag"] == etag
        assert int(rs["ContentLength"]) == len(body)

        # retrieve object
        rs = md_client.get_object(Path=path)
        resp_body = rs["Body"].read()
        assert to_str(resp_body) == body

        # delete object
        md_client.delete_object(Path=path)

        with pytest.raises(ClientError):
            md_client.describe_object(Path=path)

        # clean resources
        aws_client.mediastore.delete_container(ContainerName=container_name)

    @markers.aws.unknown
    def test_mediastore_crud(self, aws_client):
        container_name = "c-%s" % short_uid()

        rs = aws_client.mediastore.create_container(
            ContainerName=container_name, Tags=[{"Key": "environment", "Value": "testing"}]
        )
        assert rs
        assert rs.get("Container").get("Name") == container_name
        arn = rs.get("Container").get("ARN")

        rs = aws_client.mediastore.list_containers()
        assert rs
        assert len(rs.get("Containers")) == 1
        assert rs.get("Containers")[0].get("ARN") == arn

        rs = aws_client.mediastore.describe_container(ContainerName=container_name)
        assert rs
        assert rs.get("Container").get("Name") == container_name
        assert rs.get("Container").get("ARN") == arn

        rs = aws_client.mediastore.delete_container(ContainerName=container_name)
        assert rs
        rs = aws_client.mediastore.list_containers()
        assert rs
        assert len(rs.get("Containers")) == 0

        with pytest.raises(Exception) as e:
            aws_client.mediastore.delete_container(ContainerName=container_name)
            assert "ContainerNotFoundException" in str(e.value)
