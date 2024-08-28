import json
import logging
import time
from typing import Dict, Optional

import paho.mqtt.client as mqtt
import pytest
from botocore.exceptions import ClientError
from localstack.pro.core.services.iot.mqtt.client import mqtt_publish, mqtt_subscribe
from localstack.testing.pytest import markers
from localstack.utils.strings import short_uid, to_bytes
from localstack.utils.sync import retry

LOG = logging.getLogger(__name__)


@pytest.fixture
def create_thing(aws_client):
    thing_names = []

    def _create_thing(thing_name: str, **kwargs):
        aws_client.iot.create_thing(thingName=thing_name, **kwargs)
        thing_names.append(thing_name)

    yield _create_thing

    for thing_name in thing_names:
        try:
            aws_client.iot.delete_thing(thingName=thing_name)
        except Exception:
            LOG.debug("Error while deleting thing %s during test cleanup", thing_name)


@pytest.fixture
def update_and_get_thing(aws_client):
    def _inner(thing_name: str, payload: Dict, shadow_name: Optional[str]) -> Dict:
        kwargs = {}

        if shadow_name:
            kwargs["shadowName"] = shadow_name

        aws_client.iot_data.update_thing_shadow(
            thingName=thing_name, payload=to_bytes(json.dumps(payload)), **kwargs
        )
        shadow = aws_client.iot_data.get_thing_shadow(thingName=thing_name, **kwargs)
        return json.load(shadow["payload"])

    return _inner


class TestDeviceShadowServiceREST:
    @markers.aws.validated
    @pytest.mark.parametrize("use_named_shadow", [True, False], ids=["named", "classic"])
    def test_thing_shadow(self, create_thing, update_and_get_thing, aws_client, use_named_shadow):
        thing_name = f"test-thing-{short_uid()}"
        shadow_name = f"shadow-name-{short_uid()}" if use_named_shadow else None
        create_thing(thing_name=thing_name)

        expected_version = 1

        # Create desired property
        payload_desired = {"state": {"desired": {"key": "value"}}}
        shadow = update_and_get_thing(thing_name, payload_desired, shadow_name)
        assert payload_desired["state"]["desired"] == shadow["state"]["desired"]
        assert payload_desired["state"]["desired"] == shadow["state"]["delta"]
        assert shadow["version"] == expected_version
        expected_version += 1

        # Create reported property
        payload_reported = {"state": {"reported": {"key": "value"}}}
        shadow = update_and_get_thing(thing_name, payload_reported, shadow_name)
        assert payload_desired["state"]["desired"] == shadow["state"]["desired"]
        assert payload_reported["state"]["reported"] == shadow["state"]["reported"]
        assert "delta" not in shadow["state"]
        assert shadow["version"] == expected_version
        expected_version += 1

        # Create additional desire
        payload_desired_update = {"state": {"desired": {"other_key": "other_value"}}}
        shadow = update_and_get_thing(thing_name, payload_desired_update, shadow_name)
        assert (
            dict(payload_desired_update["state"]["desired"], **payload_desired["state"]["desired"])
            == shadow["state"]["desired"]
        )
        assert payload_desired_update["state"]["desired"] == shadow["state"]["delta"]
        assert payload_reported["state"]["reported"] == shadow["state"]["reported"]
        assert shadow["version"] == expected_version
        expected_version += 1

        # Delete additional desire
        payload_desired_delete = {"state": {"desired": {"other_key": None}}}
        shadow = update_and_get_thing(thing_name, payload_desired_delete, shadow_name)
        assert payload_desired["state"]["desired"] == shadow["state"]["desired"]
        assert payload_reported["state"]["reported"] == shadow["state"]["reported"]
        assert "delta" not in shadow["state"]
        assert "other_key" not in shadow["state"]["desired"]
        assert shadow["version"] == expected_version
        expected_version += 1

        # Overwrite desire
        payload_desired_update = {"state": {"desired": {"key": "other_value"}}}
        shadow = update_and_get_thing(thing_name, payload_desired_update, shadow_name)
        assert payload_desired_update["state"]["desired"] == shadow["state"]["desired"]
        assert payload_desired_update["state"]["desired"] == shadow["state"]["delta"]
        assert shadow["version"] == expected_version
        expected_version += 1

        # Update reported
        payload_reported_update = {"state": {"reported": {"key": "other_value"}}}
        shadow = update_and_get_thing(thing_name, payload_reported_update, shadow_name)
        assert payload_desired_update["state"]["desired"] == shadow["state"]["desired"]
        assert payload_reported_update["state"]["reported"] == shadow["state"]["reported"]
        assert "delta" not in shadow["state"]
        assert shadow["version"] == expected_version

    @markers.aws.needs_fixing
    def test_thing_shadow_input_errors(self, create_thing, aws_client):
        thing_name = f"test-thing-{short_uid()}"
        create_thing(thing_name=thing_name)

        # state property has to be present
        with pytest.raises(aws_client.iot_data.exceptions.InvalidRequestException):
            payload = {"random": "data"}
            aws_client.iot_data.update_thing_shadow(
                thingName=thing_name, payload=to_bytes(json.dumps(payload))
            )

        # only reported and desired is allowed for state
        with pytest.raises(aws_client.iot_data.exceptions.InvalidRequestException):
            payload = {"state": {"delta": {"key": "value"}}}
            aws_client.iot_data.update_thing_shadow(
                thingName=thing_name, payload=to_bytes(json.dumps(payload))
            )

    @markers.aws.validated
    def test_thing_shadow_metadata(self, create_thing, update_and_get_thing, aws_client):
        thing_name = f"test-thing-{short_uid()}"
        create_thing(thing_name=thing_name)
        payload_desired = {"state": {"desired": {"key": "value"}}}
        shadow_1 = update_and_get_thing(thing_name, payload_desired, None)
        assert "desired" in shadow_1["metadata"]
        assert "reported" not in shadow_1["metadata"]
        assert int(time.time()) >= shadow_1["metadata"]["desired"]["key"]["timestamp"]
        assert int(time.time()) >= shadow_1["timestamp"]

        # sleep 1 sec so the unix time has to change
        time.sleep(1)
        payload_reported = {"state": {"reported": {"other_key": "value"}}}
        shadow_2 = update_and_get_thing(thing_name, payload_reported, None)
        assert "desired" in shadow_2["metadata"]
        assert "reported" in shadow_2["metadata"]
        assert "delta" not in shadow_2["metadata"]
        assert (
            shadow_1["metadata"]["desired"]["key"]["timestamp"]
            == shadow_2["metadata"]["desired"]["key"]["timestamp"]
        )
        assert (
            shadow_1["metadata"]["desired"]["key"]["timestamp"]
            != shadow_2["metadata"]["reported"]["other_key"]["timestamp"]
        )
        assert int(time.time()) >= shadow_2["metadata"]["reported"]["other_key"]["timestamp"]
        assert shadow_2["timestamp"] >= shadow_1["timestamp"]

        # test deletion of metadata with properties
        payload_desired_delete = {"state": {"desired": {"key": None}}}
        shadow_3 = update_and_get_thing(thing_name, payload_desired_delete, None)
        assert "desired" not in shadow_3["metadata"]
        assert "reported" in shadow_3["metadata"]
        assert "delta" not in shadow_3["metadata"]
        assert (
            shadow_2["metadata"]["reported"]["other_key"]["timestamp"]
            == shadow_3["metadata"]["reported"]["other_key"]["timestamp"]
        )
        assert "desired" not in shadow_3["metadata"]
        assert shadow_3["timestamp"] >= shadow_2["timestamp"]

    @markers.aws.validated
    @pytest.mark.parametrize("use_named_shadow", [True, False], ids=["named", "classic"])
    def test_delete_shadow(
        self, create_thing, update_and_get_thing, aws_client, snapshot, use_named_shadow
    ):
        thing_name = f"test-thing-{short_uid()}"
        create_thing(thing_name=thing_name)

        kwargs = {}
        shadow_name = f"shadow-name-{short_uid()}" if use_named_shadow else None
        if shadow_name:
            kwargs["shadowName"] = shadow_name

        payload_desired = {"state": {"desired": {"key": "value"}}}
        update_and_get_thing(thing_name, payload_desired, shadow_name)

        response = aws_client.iot_data.get_thing_shadow(thingName=thing_name, **kwargs)
        snapshot.match("get_thing_shadow", response)

        response = aws_client.iot_data.delete_thing_shadow(thingName=thing_name, **kwargs)
        snapshot.match("delete_thing_shadow", response)

        with pytest.raises(ClientError) as exc:
            aws_client.iot_data.delete_thing_shadow(thingName=thing_name, **kwargs)
        shadow_identifier = thing_name + "~" + shadow_name if shadow_name else thing_name
        exc.match(f"No shadow exists with name: '{shadow_identifier}'")

    @markers.aws.validated
    def test_update_shadow_response(self, create_thing, aws_client):
        thing_name = f"test-thing-{short_uid()}"
        create_thing(thing_name=thing_name)
        payload_desired = {"state": {"desired": {"key": "value"}}}
        response = aws_client.iot_data.update_thing_shadow(
            thingName=thing_name, payload=to_bytes(json.dumps(payload_desired))
        )
        response = json.load(response["payload"])
        assert "state" in response
        assert "metadata" in response
        assert response["state"] == payload_desired["state"]

        payload_reported = {"state": {"reported": {"key": "value"}}}
        response = aws_client.iot_data.update_thing_shadow(
            thingName=thing_name, payload=to_bytes(json.dumps(payload_reported))
        )
        response = json.load(response["payload"])
        assert response["state"] == payload_reported["state"]

    @markers.aws.validated
    def test_thing_shadow_update_reported_null_value(
        self, create_thing, update_and_get_thing, snapshot
    ):
        thing_name = f"test-thing-{short_uid()}"
        shadow_name = f"shadow-name-{short_uid()}"
        create_thing(thing_name=thing_name)

        # update reported state with variable values
        payload_reported_update = {
            "state": {"reported": {"key1": "value1", "key2": 1, "key3": "value3", "key4": "value4"}}
        }
        shadow = update_and_get_thing(thing_name, payload_reported_update, shadow_name)
        snapshot.match("shadow_update_reported", shadow)

        # update reported state with null values
        payload_reported_update_null = {
            "state": {"reported": {"key1": "value1", "key2": None, "key3": "", "key4": 0}}
        }
        shadow = update_and_get_thing(thing_name, payload_reported_update_null, shadow_name)
        snapshot.match("shadow_update_reported_null_values", shadow)

    @markers.aws.validated
    def test_shadow_after_thing_deletion(self, create_thing, update_and_get_thing, aws_client):
        thing_name = f"test-thing-{short_uid()}"
        create_thing(thing_name=thing_name)

        payload_desired = {"state": {"desired": {"key": "value"}}}
        shadow = update_and_get_thing(thing_name, payload_desired, None)
        assert "desired" in shadow["state"]

        aws_client.iot.delete_thing(thingName=thing_name)
        response = aws_client.iot_data.get_thing_shadow(thingName=thing_name)
        shadow = json.load(response["payload"])
        assert "desired" in shadow["state"]

        aws_client.iot.create_thing(thingName=thing_name)
        response = aws_client.iot_data.get_thing_shadow(thingName=thing_name)
        shadow = json.load(response["payload"])
        assert "desired" in shadow["state"]


class TestDeviceShadowServiceMQTT:
    # Note for tests are marked as `needs_fixing`: These tests can be AWS validated by adding additional setup when
    # connecting to the MQTT endpoint by using the awsiotsdk framework.

    def _topic(self, thing_name: str, shadow_name: Optional[str], operation: str) -> str:
        # https://docs.aws.amazon.com/iot/latest/developerguide/reserved-topics.html#reserved-topics-shadow
        return (
            f"$aws/things/{thing_name}/shadow"
            + (f"/name/{shadow_name}" if shadow_name else "")
            + f"/{operation}"
        )

    @markers.aws.needs_fixing
    @pytest.mark.parametrize("use_named_shadow", [True, False], ids=["named", "classic"])
    def test_get_device_shadow(
        self, create_thing, update_and_get_thing, aws_client, use_named_shadow
    ):
        broker_address = "mqtt://" + aws_client.iot.describe_endpoint()["endpointAddress"]

        thing_name = f"thing-{short_uid()}"
        shadow_name: Optional[str] = f"shadow-{short_uid()}" if use_named_shadow else None

        create_thing(thing_name)
        desired_payload = {"state": {"desired": {"key": "value"}}}
        update_and_get_thing(thing_name, desired_payload, shadow_name)

        messages_accepted = []
        messages_rejected = []

        topic_get_good = self._topic(thing_name, shadow_name, "get")
        topic_get_accepted = topic_get_good + "/accepted"

        topic_get_bad = self._topic("bad-thing", shadow_name, "get")
        topic_get_rejected = topic_get_bad + "/rejected"

        def cb_get_accepted(_, __, message):
            messages_accepted.append(message)

        def cb_get_rejected(_, __, message):
            messages_rejected.append(message)

        def check_finished(messages: list, number_of_messages: int):
            assert len(messages) == number_of_messages

        mqtt_subscribe(broker_address, topic_get_accepted, cb_get_accepted)
        mqtt_subscribe(broker_address, topic_get_rejected, cb_get_rejected)

        # Get a thing which exists
        mqtt_publish(broker_address, topic_get_good, b"payload is ignored", qos=1)

        # Get a thing which does not exist
        mqtt_publish(broker_address, topic_get_bad, b"blah blah blah", qos=1)

        retry(check_finished, retries=15, sleep=1, messages=messages_accepted, number_of_messages=1)
        retry(check_finished, retries=15, sleep=1, messages=messages_rejected, number_of_messages=1)

        accepted_response_document = json.loads(messages_accepted[0].payload)
        assert accepted_response_document["state"]["desired"] == desired_payload["state"]["desired"]
        assert accepted_response_document["state"]["delta"] == desired_payload["state"]["desired"]
        assert "desired" in accepted_response_document["metadata"]
        assert "reported" not in accepted_response_document["metadata"]
        assert (
            int(time.time())
            >= accepted_response_document["metadata"]["desired"]["key"]["timestamp"]
        )
        assert int(time.time()) >= accepted_response_document["timestamp"]
        assert accepted_response_document["version"] == 1
        assert "timestamp" in accepted_response_document

        error_response_document = json.loads(messages_rejected[0].payload)
        assert error_response_document["code"] == 404
        assert error_response_document["message"] == "No shadow exists with name: 'bad-thing'"
        assert "timestamp" in error_response_document

    @markers.aws.needs_fixing
    @pytest.mark.parametrize("use_named_shadow", [True, False], ids=["named", "classic"])
    def test_update_device_shadow(self, create_thing, aws_client, use_named_shadow):
        broker_address = "mqtt://" + aws_client.iot.describe_endpoint()["endpointAddress"]

        thing_name = f"thing-{short_uid()}"
        create_thing(thing_name)
        shadow_name: Optional[str] = f"shadow-{short_uid()}" if use_named_shadow else None

        topic_update = self._topic(thing_name, shadow_name, "update")
        topic_update_accepted = f"{topic_update}/accepted"
        topic_update_documents = f"{topic_update}/documents"
        topic_update_delta = f"{topic_update}/delta"
        topic_update_rejected = f"{topic_update}/rejected"

        messages_update: list[mqtt.MQTTMessage] = []
        messages_update_accepted: list[mqtt.MQTTMessage] = []
        messages_update_documents: list[mqtt.MQTTMessage] = []
        messages_update_delta: list[mqtt.MQTTMessage] = []
        messages_update_rejected: list[mqtt.MQTTMessage] = []

        def cb_update(_, __, msg):
            messages_update.append(msg)

        def cb_update_accepted(_, __, msg):
            messages_update_accepted.append(msg)

        def cb_update_documents(_, __, msg):
            messages_update_documents.append(msg)

        def cb_update_delta(_, __, msg):
            messages_update_delta.append(msg)

        def cb_update_rejected(_, __, msg):
            messages_update_rejected.append(msg)

        mqtt_subscribe(broker_address, topic_update, cb_update)
        mqtt_subscribe(broker_address, topic_update_accepted, cb_update_accepted)
        mqtt_subscribe(broker_address, topic_update_documents, cb_update_documents)
        mqtt_subscribe(broker_address, topic_update_delta, cb_update_delta)
        mqtt_subscribe(broker_address, topic_update_rejected, cb_update_rejected)

        def check_finished(messages: list, number_of_messages: int):
            assert len(messages) == number_of_messages

        # First update
        message = {"hello": "world", "state": {}}
        mqtt_publish(broker_address, topic_update, json.dumps(message), qos=1)

        retry(check_finished, retries=10, sleep=1, messages=messages_update, number_of_messages=1)
        assert json.loads(messages_update[-1].payload) == message
        retry(
            check_finished,
            retries=10,
            sleep=1,
            messages=messages_update_accepted,
            number_of_messages=1,
        )
        update_accepted_response_document = json.loads(messages_update_accepted[-1].payload)
        assert update_accepted_response_document["state"] == {}
        assert update_accepted_response_document["metadata"] == {}
        assert update_accepted_response_document["version"] == 1
        assert "timestamp" in update_accepted_response_document
        retry(
            check_finished,
            retries=10,
            sleep=1,
            messages=messages_update_documents,
            number_of_messages=1,
        )
        retry(
            check_finished,
            retries=10,
            sleep=1,
            messages=messages_update_delta,
            number_of_messages=0,
        )
        retry(
            check_finished,
            retries=10,
            sleep=1,
            messages=messages_update_rejected,
            number_of_messages=0,
        )

        # Second update
        message = {"hello": "world"}
        mqtt_publish(broker_address, topic_update, json.dumps(message), qos=1)

        retry(check_finished, retries=10, sleep=1, messages=messages_update, number_of_messages=2)
        assert json.loads(messages_update[-1].payload) == message
        retry(
            check_finished,
            retries=10,
            sleep=1,
            messages=messages_update_accepted,
            number_of_messages=1,
        )
        retry(
            check_finished,
            retries=10,
            sleep=1,
            messages=messages_update_documents,
            number_of_messages=1,
        )
        retry(
            check_finished,
            retries=10,
            sleep=1,
            messages=messages_update_delta,
            number_of_messages=0,
        )
        retry(
            check_finished,
            retries=10,
            sleep=1,
            messages=messages_update_rejected,
            number_of_messages=1,
        )
        rejected_response_document = json.loads(messages_update_rejected[-1].payload)
        assert rejected_response_document["code"] == 400
        assert rejected_response_document["message"] == "Missing required node: state"
        assert "timestamp" in rejected_response_document

        # Third update
        desired_state = {"att1": "forty-two"}
        message = {"hello": "world", "state": {"desired": desired_state}}
        mqtt_publish(broker_address, topic_update, json.dumps(message), qos=1)

        retry(check_finished, retries=10, sleep=1, messages=messages_update, number_of_messages=3)
        assert json.loads(messages_update[-1].payload) == message
        retry(
            check_finished,
            retries=10,
            sleep=1,
            messages=messages_update_accepted,
            number_of_messages=2,
        )
        retry(
            check_finished,
            retries=10,
            sleep=1,
            messages=messages_update_documents,
            number_of_messages=2,
        )
        retry(
            check_finished,
            retries=10,
            sleep=1,
            messages=messages_update_delta,
            number_of_messages=1,
        )
        assert json.loads(messages_update_delta[-1].payload) == desired_state
        retry(
            check_finished,
            retries=10,
            sleep=1,
            messages=messages_update_rejected,
            number_of_messages=1,
        )

    @markers.aws.needs_fixing
    @pytest.mark.parametrize("use_named_shadow", [True, False], ids=["named", "classic"])
    def test_delete_device_shadow(
        self, create_thing, aws_client, update_and_get_thing, use_named_shadow
    ):
        broker_address = "mqtt://" + aws_client.iot.describe_endpoint()["endpointAddress"]

        thing_name = f"thing-{short_uid()}"
        shadow_name: Optional[str] = f"shadow-{short_uid()}" if use_named_shadow else None

        create_thing(thing_name)
        desired_payload = {"state": {"desired": {"key": "value"}}}
        update_and_get_thing(thing_name, desired_payload, shadow_name)

        messages_accepted: list[mqtt.MQTTMessage] = []
        messages_rejected: list[mqtt.MQTTMessage] = []

        topic_delete = self._topic(thing_name, shadow_name, "delete")
        topic_delete_accepted = topic_delete + "/accepted"
        topic_delete_rejected = topic_delete + "/rejected"

        def cb_delete_accepted(_, __, message):
            messages_accepted.append(message)

        def cb_delete_rejected(_, __, message):
            messages_rejected.append(message)

        def check_finished(messages: list, number_of_messages: int):
            assert len(messages) == number_of_messages

        mqtt_subscribe(broker_address, topic_delete_accepted, cb_delete_accepted)
        mqtt_subscribe(broker_address, topic_delete_rejected, cb_delete_rejected)

        mqtt_publish(broker_address, topic_delete, b"whatever", qos=1)
        mqtt_publish(broker_address, topic_delete, None, qos=1)

        retry(check_finished, retries=15, sleep=1, messages=messages_accepted, number_of_messages=1)
        retry(check_finished, retries=15, sleep=1, messages=messages_rejected, number_of_messages=1)

        assert messages_accepted[0].payload == b""

        error_response_document = json.loads(messages_rejected[0].payload)
        assert error_response_document["code"] == 404
        shadow_identifier = thing_name + "~" + shadow_name if shadow_name else thing_name
        assert (
            error_response_document["message"]
            == f"No shadow exists with name: '{shadow_identifier}'"
        )
