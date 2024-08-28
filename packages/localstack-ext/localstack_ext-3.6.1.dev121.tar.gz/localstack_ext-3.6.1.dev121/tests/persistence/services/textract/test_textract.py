def test_detect_document_text(persistence_validations, snapshot, aws_client):
    client = aws_client.textract

    response = client.start_document_text_detection(
        DocumentLocation={"S3Object": {"Bucket": "bucket", "Name": "document"}}
    )

    job_id = response["JobId"]

    def validate():
        snapshot.match(
            "get_document_text_detection",
            client.get_document_text_detection(JobId=job_id),
        )

    persistence_validations.register(validate)
