import pytest
from localstack.utils.strings import short_uid


@pytest.mark.skip(reason="Persistence not yet implemented for MQ")
def test_describe_broker(persistence_validations, snapshot, aws_client):
    """This one should fail"""
    create_broker_request = {
        "BrokerName": f"test-broker-{short_uid()}",
        "DeploymentMode": "SINGLE_INSTANCE",
        "EngineType": "ACTIVEMQ",
        "EngineVersion": "5.16.6",
        "HostInstanceType": "mq.t2.micro",
        "AutoMinorVersionUpgrade": True,
        "PubliclyAccessible": True,
        "Users": [
            {
                "ConsoleAccess": True,
                "Groups": ["testgroup"],
                "Password": "adminisagreatpassword",
                "Username": "admin",
            }
        ],
    }

    response = aws_client.mq.create_broker(**create_broker_request)

    def validate():
        description = aws_client.mq.describe_broker(BrokerId=response["BrokerId"])
        snapshot.match("describe_broker", description)

    persistence_validations.register(validate)
