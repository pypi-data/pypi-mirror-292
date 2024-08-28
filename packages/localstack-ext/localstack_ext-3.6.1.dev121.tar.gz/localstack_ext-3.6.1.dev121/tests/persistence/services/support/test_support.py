def test_support(persistence_validations, snapshot, aws_client):
    client = aws_client.support
    client.create_case(
        subject="Test Case",
        serviceCode="test",
        severityCode="low",
        categoryCode="test",
        communicationBody="Test",
    )

    def validate():
        snapshot.match("describe_cases", client.describe_cases)

    persistence_validations.register(validate)
