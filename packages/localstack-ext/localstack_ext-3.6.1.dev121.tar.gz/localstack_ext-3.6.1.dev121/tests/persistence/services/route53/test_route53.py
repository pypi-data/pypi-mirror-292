from localstack.utils.strings import short_uid


def test_create_get_hosted_zone(persistence_validations, snapshot, aws_client):
    zone_name = f"zone-{short_uid()}"
    zone_id = aws_client.route53.create_hosted_zone(Name=zone_name, CallerReference=short_uid())[
        "HostedZone"
    ]["Id"]

    def validate():
        snapshot.match("create_get_hosted_zone", aws_client.route53.get_hosted_zone(Id=zone_id))

    persistence_validations.register(validate)
