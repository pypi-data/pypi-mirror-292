from localstack.utils.strings import short_uid


def test_iot_describe_thing(persistence_validations, snapshot, aws_client):
    thing_name = f"thing-{short_uid()}"
    aws_client.iot.create_thing(thingName=thing_name)

    def validate():
        snapshot.match("describe_thing", aws_client.iot.describe_thing(thingName=thing_name))

    persistence_validations.register(validate)
