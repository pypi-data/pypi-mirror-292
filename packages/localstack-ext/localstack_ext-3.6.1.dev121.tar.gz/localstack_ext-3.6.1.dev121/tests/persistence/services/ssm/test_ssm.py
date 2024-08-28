import json

from localstack.utils.strings import short_uid


def test_ssm_get_doc(persistence_validations, snapshot, aws_client):
    doc = {
        "schemaVersion": "2.2",
        "description": "Example document",
        "parameters": {
            "Message": {
                "type": "String",
                "description": "Example parameter",
                "default": "Hello World",
            }
        },
        "mainSteps": [
            {
                "action": "aws:runPowerShellScript",
                "name": "example",
                "inputs": {"runCommand": ["Write-Output {{Message}}"]},
            }
        ],
    }
    doc_name = f"doc-{short_uid()}"
    aws_client.ssm.create_document(
        Content=json.dumps(doc),
        Name=doc_name,
        DocumentType="Command",
        DocumentFormat="JSON",
    )

    def validate():
        snapshot.match(
            "ssm_get_doc",
            aws_client.ssm.list_documents(Filters=[{"Key": "Name", "Values": [doc_name]}]),
        )

    persistence_validations.register(validate)
