from localstack.utils.strings import short_uid


def test_describe_swf_domain(persistence_validations, snapshot, aws_client):
    domain_name = f"test-domain-{short_uid()}"
    aws_client.swf.register_domain(name=domain_name, workflowExecutionRetentionPeriodInDays="1")

    def validate_describe_domain():
        snapshot.match("describe_domain", aws_client.swf.describe_domain(name=domain_name))

    def validate_list_domains():
        snapshot.match("list_domains", aws_client.swf.list_domains(registrationStatus="REGISTERED"))

    persistence_validations.register(validate_describe_domain)
    persistence_validations.register(validate_list_domains)
