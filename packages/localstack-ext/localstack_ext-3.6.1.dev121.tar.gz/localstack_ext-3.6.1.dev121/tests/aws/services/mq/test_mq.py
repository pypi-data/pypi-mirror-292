import json
import logging
import time

import pytest
import requests
import stomp
from botocore.exceptions import ClientError
from localstack.constants import APPLICATION_JSON
from localstack.pro.core.aws.api.mq import NotFoundException
from localstack.testing.pytest import markers
from localstack.testing.snapshots.transformer_utility import RegexTransformer
from localstack.utils.strings import short_uid
from stomp.listener import TestListener

LOG = logging.getLogger(__name__)


@pytest.fixture
def mq_create_configuration(aws_client):
    def factory(**kwargs):
        if "EngineType" not in kwargs:
            kwargs["EngineType"] = "ACTIVEMQ"
        if "EngineVersion" not in kwargs:
            kwargs["EngineVersion"] = "5.16.6"
        if "Name" not in kwargs:
            kwargs["Name"] = f"test-configuration-{short_uid()}"
        if "AuthenticationStrategy" not in kwargs:
            kwargs["AuthenticationStrategy"] = "simple"

        response = aws_client.mq.create_configuration(**kwargs)
        return response

    yield factory


@pytest.fixture(autouse=True)
def transcribe_snapshot_transformer(snapshot):
    snapshot.add_transformer(
        [
            RegexTransformer(
                r"([a-zA-Z0-9-_.]*)?test-broker-([a-zA-Z0-9-_.]*)?", replacement="<broker-name>"
            ),
            RegexTransformer(
                r"([a-zA-Z0-9-_.]*)?test-configuration-([a-zA-Z0-9-_.]*)?",
                replacement="<configuration-name>",
            ),
            RegexTransformer(
                r"[bc]-[a-zA-Z0-9-_.]{8}-[a-zA-Z0-9-_.]{4}-[a-zA-Z0-9-_.]{4}-[a-zA-Z0-9-_.]{4}-[a-zA-Z0-9-_.]{12}",
                replacement="<id>",
            ),
            RegexTransformer(
                r"[a-zA-Z0-9-_.]{8}-[a-zA-Z0-9-_.]{4}-[a-zA-Z0-9-_.]{4}-[a-zA-Z0-9-_.]{4}-[a-zA-Z0-9-_.]{12}",
                replacement="<paging_token>",
            ),
            RegexTransformer(
                r"amazonaws.com:[1-9]{4,5}",
                replacement="<url_port>",
            ),
            RegexTransformer(
                r"\b(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25["
                r"0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b",
                replacement="<ip_address>",
            ),
        ]
    )


@pytest.fixture
def connect():
    connections = []

    def _connect(host: str = "localhost", port: int = 61613) -> stomp.Connection:
        _connection = stomp.Connection(host_and_ports=[(host, port)])
        _connection.set_listener("test_listener", TestListener(print_to_log=True))
        _connection.connect("admin", "admin", wait=True)
        connections.append(_connection)
        return _connection

    yield _connect

    for connection in connections:
        connection.disconnect(receipt=None)


class TestMQ:
    @markers.aws.validated
    def test_create_broker(self, mq_create_broker, snapshot):
        response = mq_create_broker()
        snapshot.match("CreateBrokerResponse", response)

    @markers.aws.only_localstack(reason="aws takes 20min to boot a broker")
    def test_send_to_active_mq(self, mq_create_broker, connect, aws_client):
        response = mq_create_broker()
        describe = aws_client.mq.describe_broker(BrokerId=response["BrokerId"])

        stomp_endpoint = [x for x in describe["BrokerInstances"][0]["Endpoints"] if "stomp" in x][0]
        port = int(stomp_endpoint.split(":")[-1])

        conn = connect(port=port)
        conn.subscribe(destination="/queue/test", id="1", ack="auto")
        conn.send(body="test message", destination="/queue/test")
        time.sleep(2)

        def validate_send(_conn, listener_name: str = "test_listener"):
            listener = _conn.get_listener(listener_name)

            assert listener.connections == 1, "should have received 1 connection acknowledgement"
            assert listener.messages == 1, "should have received 1 message"
            assert listener.errors == 0, "should not have received any errors"

        validate_send(conn)

    @markers.aws.only_localstack(reason="aws takes 20min to boot a broker")
    def test_send_to_activemq_curl(self, mq_create_broker, aws_client):
        response = mq_create_broker()
        time.sleep(3)
        broker_id = response["BrokerId"]

        description = aws_client.mq.describe_broker(BrokerId=broker_id)
        url = description["BrokerInstances"][0]["ConsoleURL"]
        url = url[7:]  # removing the http:// from the url
        payload = {"body": "message"}

        requests.post(
            f"http://admin:admin@{url}/api/message?destination=queue://test",
            json=payload,
            headers={"content-type": APPLICATION_JSON},
            verify=False,
        )

        message = requests.get(
            f"http://admin:admin@{url}/api/message?destination=queue://test&json=true&oneShot=true",
            verify=False,
        )
        message_content = json.loads(message.content)
        assert payload == message_content

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(
        paths=[
            "$..body",
            "$..BrokerState",  # because AWS is too slow
            "$..MaintenanceWindowStartTime",
            "$..Users",
            "$..AuthenticationStrategy",
            "$..AutoMinorVersionUpgrade",
            "$..BrokerInstances",
            "$..EncryptionOptions",
            "$..Logs",
            "$..Configurations",
            "$..EngineVersion",
            "$..PubliclyAccessible",
            "$..SecurityGroups",
            "$..StorageType",
            "$..SubnetIds",
        ]
    )
    def test_describe_broker(self, mq_create_broker, snapshot, aws_client):
        response = mq_create_broker()
        description = aws_client.mq.describe_broker(BrokerId=response["BrokerId"])

        snapshot.match("DescribeBroker", description)

    @markers.aws.only_localstack(reason="aws takes 20min to boot a broker")
    def test_delete_broker(self, mq_create_broker, snapshot, aws_client):
        # first, create a broker
        response = mq_create_broker()

        # successful delete
        delete_response = aws_client.mq.delete_broker(BrokerId=response["BrokerId"])
        snapshot.match("DeleteBrokerResponse", delete_response)

        # deleting a nonexistent broker
        with pytest.raises((ClientError, NotFoundException)) as e_info:
            aws_client.mq.delete_broker(BrokerId="foo")

        snapshot.match("FailingDeleteBrokerResponse", e_info.value)

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(
        paths=[
            "$..BrokerState",  # because AWS is too slow
            "$..EngineType",  # ActiveMQ vs ACTIVEMQ
        ]
    )
    def test_list_brokers(self, mq_create_broker, snapshot, aws_client):
        # locally only 1 broker will be present, AWS might contain multiple
        # therefore we do some filtering of results below

        # create 1 and test it
        config = mq_create_broker()
        brokers = aws_client.mq.list_brokers()["BrokerSummaries"]
        relevant_brokers = [
            element for element in brokers if element["BrokerArn"] == config["BrokerArn"]
        ]
        snapshot.match("ListBrokers", relevant_brokers)

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(paths=["$..BrokerEngineTypes..EngineVersions"])
    def test_describe_broker_engine_types(self, snapshot, aws_client):
        response = aws_client.mq.describe_broker_engine_types()
        snapshot.match("BrokerEngineTypesAll", response)

        response = aws_client.mq.describe_broker_engine_types(EngineType="ACTIVEMQ")
        snapshot.match("BrokerEngineTypesActiveMQ", response)

        response = aws_client.mq.describe_broker_engine_types(EngineType="rabbitmq")
        snapshot.match("BrokerEngineTypesRabbitMQ", response)

        with pytest.raises(ClientError) as e_info:
            aws_client.mq.describe_broker_engine_types(EngineType="foo")
        snapshot.match("BrokerEngineTypesInvalid", e_info.value)

    @markers.aws.validated
    def test_create_tags(self, mq_create_broker, snapshot, aws_client):
        # 1. invalid resource
        with pytest.raises(ClientError) as e_info:
            aws_client.mq.create_tags(ResourceArn="foo")
        snapshot.match("CreateTagsInvalidResource", e_info.value)

        response = mq_create_broker()
        resource_arn = response["BrokerArn"]

        # 2. missing tags (first need a valid resource)
        with pytest.raises(ClientError) as e_info:
            aws_client.mq.create_tags(ResourceArn=resource_arn)
        snapshot.match("CreateTagsMissing", e_info.value)
        with pytest.raises(ClientError) as e_info:
            aws_client.mq.create_tags(ResourceArn=resource_arn, Tags={})
        snapshot.match("CreateTagsEmpty", e_info.value)

        # 3. valid
        aws_client.mq.create_tags(ResourceArn=resource_arn, Tags={"foo": "bar", "foo1": "bar1"})
        response = aws_client.mq.list_tags(ResourceArn=resource_arn)
        snapshot.match("CreateTagsValid", response)

        # 4. override
        aws_client.mq.create_tags(ResourceArn=resource_arn, Tags={"foo": "bar1"})
        response = aws_client.mq.list_tags(ResourceArn=resource_arn)
        snapshot.match("CreateTagsValidOverride", response)

    @markers.aws.validated
    def test_delete_tags(self, mq_create_broker, snapshot, aws_client):
        response = mq_create_broker()
        resource_arn = response["BrokerArn"]

        aws_client.mq.create_tags(ResourceArn=resource_arn, Tags={"foo": "bar", "foo1": "bar1"})

        response = aws_client.mq.list_tags(ResourceArn=resource_arn)
        snapshot.match("DeleteTagsBefore", response)

        aws_client.mq.delete_tags(ResourceArn=resource_arn, TagKeys=["foo"])
        response = aws_client.mq.list_tags(ResourceArn=resource_arn)
        snapshot.match("DeleteTagsAfter", response)

    @markers.aws.only_localstack(reason="aws is unreasonably flaky in list_configs()")
    @markers.snapshot.skip_snapshot_verify(paths=["$..LatestRevision", "$..EngineVersion"])
    def test_create_configuration(self, mq_create_configuration, snapshot, aws_client):
        # invalid engine type
        with pytest.raises(ClientError):
            mq_create_configuration(EngineType="foo")

        # invalid engine version
        with pytest.raises(ClientError):
            mq_create_configuration(EngineVersion="0.1")

        # invalid authentication strategy
        with pytest.raises(ClientError):
            mq_create_configuration(AuthenticationStrategy="foo")

        # valid request
        configuration_name = f"test-configuration-{short_uid()}"
        response = mq_create_configuration(Name=configuration_name)
        snapshot.match("ValidConfigCreated", response)

        # valid request with tags
        response = mq_create_configuration(Name=configuration_name, Tags={"foo": "bar"})
        snapshot.match("ValidConfigWithTagsCreated", response)

        # Note - it's not possible to delete configurations on AWS as of this writing
        # locally only 1 configuration will be present, AWS might contain multiple
        configs = aws_client.mq.list_configurations()["Configurations"]
        # only extracting the created one (filtering out AWS results)
        relevant_configs = [element for element in configs if element["Name"] == configuration_name]

        assert len(relevant_configs) == 2

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(
        paths=[
            "$..Tags",
            "$..Description",
            "$..EngineType",
            "$..EngineVersion",
            "$..LatestRevision",
        ]
    )
    def test_describe_configuration(self, mq_create_configuration, snapshot, aws_client):
        with pytest.raises(ClientError) as e_info:
            aws_client.mq.describe_configuration(ConfigurationId="foo")
        snapshot.match("NotFoundConfiguration", e_info.value)

        create_response = mq_create_configuration()

        describe_response = aws_client.mq.describe_configuration(
            ConfigurationId=create_response["Id"]
        )
        snapshot.match("DescribeConfiguration", describe_response)
