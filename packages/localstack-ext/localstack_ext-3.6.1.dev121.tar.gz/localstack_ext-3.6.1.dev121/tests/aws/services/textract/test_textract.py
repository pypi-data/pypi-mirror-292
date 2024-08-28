from localstack.testing.pytest import markers


class TestTextract:
    @markers.aws.only_localstack
    def test_detect_document_text(self, aws_client):
        client = aws_client.textract

        response = client.detect_document_text(
            Document={"S3Object": {"Bucket": "bucket", "Name": "document"}}
        )

        # Validate the response
        assert response["DocumentMetadata"]["Pages"]["Pages"] is not None
        assert response["Blocks"] == []
        assert response["DetectDocumentTextModelVersion"] == "1.0"
