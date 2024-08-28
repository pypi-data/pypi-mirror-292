import base64
import contextlib
import datetime
import json
import logging
import os
import re
import time
from typing import Any

import awscrt
import pytest
from awscrt import io, mqtt
from botocore.exceptions import ClientError
from localstack import config
from localstack.aws.api.lambda_ import Runtime
from localstack.packages import PackageException
from localstack.pro.core.aws.api.iot import AttributePayload, ThingIndexingMode
from localstack.pro.core.services.iot.constants import (
    LIFECYCLE_CONNECTED_TEMPL,
    LIFECYCLE_DISCONNECTED_TEMPL,
    LIFECYCLE_SUBSCRIBE_TEMPL,
    LIFECYCLE_UNSUBSCRIBE_TEMPL,
    ROOT_CA_ENDPOINT,
)
from localstack.pro.core.services.iot.mqtt.client import (
    create_mqtt_client,
    mqtt_publish,
    mqtt_subscribe,
)
from localstack.testing.aws.util import is_aws_cloud
from localstack.testing.pytest import markers
from localstack.utils import testutil
from localstack.utils.collections import remove_none_values_from_dict
from localstack.utils.files import file_exists_not_empty, new_tmp_file, save_file
from localstack.utils.http import download
from localstack.utils.net import wait_for_port_open
from localstack.utils.strings import short_uid, to_bytes, to_str
from localstack.utils.sync import poll_condition, retry
from localstack_snapshot.snapshots.transformer import SortingTransformer

LOG = logging.getLogger(__name__)

# URL to AWS root CA pem file, see:
# https://docs.aws.amazon.com/iot/latest/developerguide/server-authentication.html#server-authentication-certs
AWS_ROOT_CA_PEM_URL = "https://www.amazontrust.com/repository/AmazonRootCA1.pem"

# simple test no-op Lambda handler
TEST_LAMBDA = """
def handler(event, context):
    pass
"""


@pytest.fixture
def create_thing(aws_client):
    thing_names = []

    def _create_thing(thing_name: str = None, **kwargs):
        thing_name = thing_name or f"thing-{short_uid()}"
        aws_client.iot.create_thing(thingName=thing_name, **kwargs)
        thing_names.append(thing_name)
        return thing_name

    yield _create_thing

    for thing_name in thing_names:
        try:
            aws_client.iot.delete_thing(thingName=thing_name)
        except Exception:
            LOG.debug("Error while deleting thing %s during test cleanup", thing_name)


@pytest.fixture
def create_thing_with_policy(create_thing, cert_and_keys, aws_client):
    thing_policies = []
    cert_arn = cert_and_keys[0]

    def _create():
        thing_name = f"thing-{short_uid()}"
        create_thing(thing_name)

        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": "iot:*",
                    "Resource": "*",
                },
            ],
        }

        # create and attach policy
        pol_name = f"{thing_name}-permit-all"
        aws_client.iot.create_policy(policyName=pol_name, policyDocument=json.dumps(policy))
        aws_client.iot.attach_thing_principal(thingName=thing_name, principal=cert_arn)
        aws_client.iot.attach_policy(policyName=pol_name, target=cert_arn)
        thing_policies.append((thing_name, pol_name))

    yield _create

    for thing_name, policy in thing_policies:
        with contextlib.suppress(Exception):
            aws_client.iot.detach_policy(policyName=policy, target=cert_arn)
            aws_client.iot.detach_thing_principal(thingName=thing_name, principal=cert_arn)


@pytest.fixture
def cert_and_keys(aws_client):
    result = aws_client.iot.create_keys_and_certificate(setAsActive=True)
    cert_arn = result["certificateArn"]

    # store cert and key files
    cert_file = new_tmp_file()
    save_file(cert_file, result["certificatePem"])
    priv_key_file = new_tmp_file()
    save_file(priv_key_file, result["keyPair"]["PrivateKey"])
    # use a static tmp file name, to avoid re-downloading the file for each fixture
    root_ca_file = os.path.join(config.dirs.tmp, "test.iot.root_ca_file.pem")
    if not file_exists_not_empty(root_ca_file):
        root_ca_pem_url = (
            AWS_ROOT_CA_PEM_URL
            if is_aws_cloud()
            else (config.internal_service_url() + ROOT_CA_ENDPOINT)
        )
        download(root_ca_pem_url, root_ca_file)

    yield cert_arn, cert_file, priv_key_file, root_ca_file

    cert_id = cert_arn.split("/")[-1]
    aws_client.iot.update_certificate(certificateId=cert_id, newStatus="INACTIVE")
    aws_client.iot.delete_certificate(certificateId=cert_id, forceDelete=True)


@pytest.fixture
def iot_topic_rule(aws_client):
    rules = list()

    def factory(**kwargs):
        if "RuleName" not in kwargs:
            kwargs["RuleName"] = f"test_topic_{short_uid()}"
        aws_client.iot.create_topic_rule(
            ruleName=kwargs["RuleName"], topicRulePayload=kwargs["TopicRulePayload"]
        )
        rules.append(kwargs["RuleName"])
        return kwargs["RuleName"]

    yield factory

    for rule in rules:
        try:
            aws_client.iot.delete_topic_rule(ruleName=rule)
        except Exception as e:
            LOG.debug(f"error while cleaning up rule {rule}: {e}")


class TestIoTCrud:
    """Tests with basic CRUD operations"""

    @markers.aws.validated
    def test_create_iot_resources(self, deploy_cfn_template, aws_client):
        # create and deploy CFN stack
        thing_name = f"t-{short_uid()}"
        rule_name = f"r_{short_uid()}"
        parameters = {
            "ThingName": thing_name,
            "RuleName": rule_name,
        }
        stack = deploy_cfn_template(
            template_path=os.path.join(os.path.dirname(__file__), "../../templates/iot.sample.yml"),
            parameters=parameters,
        )

        # check created resources
        resources = aws_client.cloudformation.describe_stack_resources(StackName=stack.stack_name)[
            "StackResources"
        ]
        types = set([r.get("ResourceType") for r in resources])
        assert len(types) == 3

        # assert thing has been created
        def _assert(things):
            things = things["things"]
            matching = [t for t in things if t["thingName"] == thing_name]
            assert len(matching) == 1
            assert f":thing/{thing_name}" in matching[0]["thingArn"]

        _assert(aws_client.iot.list_things())
        _assert(aws_client.iot.list_things(maxResults=50))

        rule_arn = aws_client.iot.get_topic_rule(ruleName=rule_name)["ruleArn"]
        rule = aws_client.iot.list_tags_for_resource(resourceArn=rule_arn)
        assert rule["tags"] == [{"Key": "foo", "Value": "bar"}]

        # best effort delete
        try:
            aws_client.iot.delete_thing(thingName=thing_name)
        except Exception as e:
            LOG.debug(f"Error while trying to delete remaining iot things: {e}")

    @markers.aws.validated
    @pytest.mark.parametrize(
        "attribute_payload",
        [
            None,
            AttributePayload(),
            AttributePayload(attributes={"AttributeName": "AttributeValue"}, merge=True),
            AttributePayload(attributes={"AttributeName": "AttributeValue"}, merge=False),
            AttributePayload(merge=True),
            AttributePayload(merge=False),
        ],
    )
    def test_create_thing_idempotency(self, snapshot, create_thing, attribute_payload, aws_client):
        thing_name = f"t-{short_uid()}"
        kwargs = {
            "thing_name": thing_name,
            "attributePayload": attribute_payload,
        }
        kwargs = remove_none_values_from_dict(kwargs)
        thing1 = create_thing(**kwargs)
        # creating the same thing again, with the same config, is successful
        thing2 = create_thing(**kwargs)

        # make sure the IDs are the same
        assert thing1 == thing2

        # check that the descriptions of the things are correct
        described_thing = aws_client.iot.describe_thing(thingName=thing_name)
        snapshot.add_transformer(
            snapshot.transform.regex(described_thing["thingName"], "<thing-name:1>")
        )
        snapshot.match("described_thing", described_thing)

    @markers.aws.validated
    def test_create_thing_idempotency_failure(self, snapshot, create_thing, aws_client):
        thing_name = f"t-{short_uid()}"
        create_thing(
            thing_name=thing_name,
            attributePayload=AttributePayload(
                attributes={"AttributeName": "AttributeValue"}, merge=False
            ),
        )
        # creating the same thing again, with a different config, is failing
        with pytest.raises(
            ClientError,
            match=re.escape(
                f"An error occurred (ResourceAlreadyExistsException) when calling the CreateThing operation: "
                f"Thing {thing_name} already exists in account with different attributes"
            ),
        ):
            create_thing(
                thing_name=thing_name,
                attributePayload=AttributePayload(
                    attributes={"DifferentAttributeName": "AttributeValue"}
                ),
            )

    @markers.aws.unknown
    def test_list_things_pagination(self, create_thing, aws_client):
        # FIXME: This test case assumes there are only 2 things prtesent.
        # Solution: We should use filters (which is not implemented at the moment)
        thing_name_1 = f"thing-{short_uid()}"
        thing_name_2 = f"thing-{short_uid()}"
        create_thing(thing_name=thing_name_1)
        create_thing(thing_name=thing_name_2)
        max_results = 1
        # check if only <max_results> number of items are returned
        list_result_1 = aws_client.iot.list_things(maxResults=max_results)
        assert len(list_result_1["things"]) == max_results
        assert "nextToken" in list_result_1

        # check if we reached the end of the result
        list_result_2 = aws_client.iot.list_things(
            maxResults=max_results, nextToken=list_result_1["nextToken"]
        )
        assert len(list_result_2["things"]) == max_results
        assert "nextToken" not in list_result_2

        # check if the names are contained in the results, regardless of the returned order
        result = {list_result_2["things"][0]["thingName"], list_result_1["things"][0]["thingName"]}
        assert thing_name_1 in result
        assert thing_name_2 in result

    @markers.aws.unknown
    def test_thing_groups(self, aws_client):
        groups_before = len(aws_client.iot.list_thing_groups()["thingGroups"])

        group_name_1 = f"grp1-{short_uid()}"
        group_name_2 = f"grp2-{short_uid()}"
        params = {
            "thingGroupName": group_name_1,
            "thingGroupProperties": {
                "thingGroupDescription": "description",
                "attributePayload": {"attributes": {"attr1": "value1"}, "merge": False},
            },
            "tags": [{"Key": "tag1", "Value": "value1"}],
        }
        response = aws_client.iot.create_thing_group(**params)
        assert response["ResponseMetadata"]["HTTPStatusCode"] == 200
        assert response.get("thingGroupName") == group_name_1
        assert f"/{group_name_1}" in response.get("thingGroupArn")
        params["thingGroupName"] = group_name_2
        params["parentGroupName"] = group_name_1
        response = aws_client.iot.create_thing_group(**params)
        assert response["ResponseMetadata"]["HTTPStatusCode"] == 200

        # list and describe thing groups
        groups = aws_client.iot.list_thing_groups()["thingGroups"]
        # TODO: fix assertion, to make tests parallelizable!
        assert len(groups) == groups_before + 2
        result = aws_client.iot.describe_thing_group(thingGroupName=group_name_2)
        assert result["thingGroupName"] == group_name_2
        assert f":thinggroup/{group_name_2}" in result["thingGroupArn"]

        # add thing to thing group
        thing_name = f"t-{short_uid()}"
        response = aws_client.iot.create_thing(thingName=thing_name)
        aws_client.iot.add_thing_to_thing_group(thingGroupName=group_name_1, thingName=thing_name)
        assert response["ResponseMetadata"]["HTTPStatusCode"] == 200
        assert response.get("thingName") == thing_name

        # describe thing
        result = aws_client.iot.describe_thing(thingName=thing_name)
        assert result["thingName"] == thing_name
        assert f":thing/{thing_name}" in result["thingArn"]

        # assert mapping between things and groups
        result = aws_client.iot.list_thing_groups_for_thing(thingName=thing_name)["thingGroups"]
        assert len(result) == 1
        result = aws_client.iot.list_things_in_thing_group(thingGroupName=group_name_1)["things"]
        assert len(result) == 1

        # remove thing from group
        aws_client.iot.remove_thing_from_thing_group(
            thingGroupName=group_name_1, thingName=thing_name
        )

        # assert mapping between things and groups
        result = aws_client.iot.list_thing_groups_for_thing(thingName=thing_name)["thingGroups"]
        assert len(result) == 0
        result = aws_client.iot.list_things_in_thing_group(thingGroupName=group_name_1)["things"]
        assert len(result) == 0

        # clean up
        aws_client.iot.delete_thing(thingName=thing_name)
        aws_client.iot.delete_thing_group(thingGroupName=group_name_2)
        aws_client.iot.delete_thing_group(thingGroupName=group_name_1)

    @markers.aws.unknown
    def test_policies(self, aws_client):
        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": "iot:Connect",
                    "Resource": "arn:aws:iot:ap-south-1:307444571635:client/client1",
                },
            ],
        }

        # create policy
        pol_name = f"p-{short_uid()}"
        result = aws_client.iot.create_policy(
            policyName=pol_name, policyDocument=json.dumps(policy)
        )
        assert result["ResponseMetadata"]["HTTPStatusCode"] == 200
        assert result.get("policyName") == pol_name

        # list and get policies
        result1 = [
            p for p in aws_client.iot.list_policies()["policies"] if p["policyName"] == pol_name
        ]
        result2 = aws_client.iot.get_policy(policyName=pol_name)

        for pol in [result1[0], result2]:
            assert pol["policyName"] == pol_name
            assert f":policy/{pol_name}" in pol["policyArn"]

        # attach a policy to a certificate
        result = aws_client.iot.register_certificate(certificatePem=short_uid())
        result = aws_client.iot.attach_policy(policyName=pol_name, target=result["certificateArn"])
        assert result["ResponseMetadata"]["HTTPStatusCode"] == 200

        # clean up
        aws_client.iot.delete_policy(policyName=pol_name)

    @markers.aws.unknown
    def test_thing_principals(self, aws_client):
        thing_name = f"t-{short_uid()}"
        result = aws_client.iot.attach_thing_principal(thingName=thing_name, principal="p1")
        assert result["ResponseMetadata"]["HTTPStatusCode"] == 200

        result = aws_client.iot.list_thing_principals(thingName=thing_name)
        assert result["ResponseMetadata"]["HTTPStatusCode"] == 200
        assert result["principals"] == ["p1"]

        result = aws_client.iot.detach_thing_principal(thingName=thing_name, principal="p1")
        assert result["ResponseMetadata"]["HTTPStatusCode"] == 200

        result = aws_client.iot.list_thing_principals(thingName=thing_name)
        assert result["principals"] == []

    @markers.aws.unknown
    def test_certificate(self, aws_client, account_id):
        result = aws_client.iot.register_certificate(certificatePem="test123")
        assert f":{account_id}:" in result["certificateArn"]

    @markers.aws.unknown
    def test_dynamic_thing_groups(self, aws_client):
        group_name = f"g-{short_uid()}"
        result = aws_client.iot.create_dynamic_thing_group(
            thingGroupName=group_name, queryString="TODO"
        )
        assert result["ResponseMetadata"]["HTTPStatusCode"] == 200
        result = aws_client.iot.update_dynamic_thing_group(
            thingGroupName=group_name,
            queryString="TODO2",
            thingGroupProperties={
                "thingGroupDescription": "d1",
                "attributePayload": {"attributes": {}},
            },
        )
        assert result["ResponseMetadata"]["HTTPStatusCode"] == 200
        result = aws_client.iot.delete_dynamic_thing_group(thingGroupName=group_name)
        assert result["ResponseMetadata"]["HTTPStatusCode"] == 200

    @markers.aws.unknown
    def test_jobs(self, aws_client):
        job_id = f"j-{short_uid()}"
        thing_name = f"t-{short_uid()}"

        result = aws_client.iot.create_thing(thingName=thing_name)
        thing_arn = result["thingArn"]
        result = aws_client.iot.create_job(jobId=job_id, targets=[thing_arn], document="{}")
        assert result["ResponseMetadata"]["HTTPStatusCode"] == 200

        result = aws_client.iot.describe_job(jobId=job_id)
        assert result["job"]["jobId"] == job_id

        result = aws_client.iot.delete_job(jobId=job_id, force=True)
        assert result["ResponseMetadata"]["HTTPStatusCode"] == 200

        with pytest.raises(ClientError) as exc:
            aws_client.iot.describe_job(jobId=job_id)
        assert exc.value.response.get("Error", {}).get("Code") == "ResourceNotFoundException"

    @markers.aws.unknown
    def test_job_executions(self, aws_client):
        job_id = f"j-{short_uid()}"
        thing_name = f"t-{short_uid()}"
        execution_number = 1

        result = aws_client.iot.create_thing(thingName=thing_name)
        thing_arn = result["thingArn"]
        aws_client.iot.create_job(jobId=job_id, targets=[thing_arn], document="{}")

        def check_job_created():
            try:
                result = aws_client.iot.describe_job_execution(
                    thingName=thing_name, jobId=job_id, executionNumber=execution_number
                )
                assert result["ResponseMetadata"]["HTTPStatusCode"] == 200
                assert result["execution"]["status"] == "QUEUED"
                return True
            except aws_client.iot.exceptions.ResourceNotFoundException:
                return False

        assert poll_condition(check_job_created, timeout=10)

        result = aws_client.iot.list_job_executions_for_thing(thingName=thing_name)
        assert result["ResponseMetadata"]["HTTPStatusCode"] == 200

        # Cleanup
        aws_client.iot.delete_thing(thingName=thing_name)
        aws_client.iot.delete_job(jobId=job_id, force=True)

    @markers.aws.unknown
    def test_search(self, aws_client):
        config = {"thingIndexingMode": ThingIndexingMode.REGISTRY}
        result = aws_client.iot.update_indexing_configuration(thingIndexingConfiguration=config)
        assert result["ResponseMetadata"]["HTTPStatusCode"] == 200

        thing_name = f"t1-{short_uid()}"
        response = aws_client.iot.create_thing(thingName=thing_name)
        assert response["ResponseMetadata"]["HTTPStatusCode"] == 200

        result = aws_client.iot.search_index(queryString=thing_name)
        assert result["ResponseMetadata"]["HTTPStatusCode"] == 200
        assert len(result["things"]) == 1

        group_name = f"grp1-{short_uid()}"
        response = aws_client.iot.create_thing_group(thingGroupName=group_name)
        assert response["ResponseMetadata"]["HTTPStatusCode"] == 200
        aws_client.iot.add_thing_to_thing_group(thingGroupName=group_name, thingName=thing_name)

        result = aws_client.iot.search_index(queryString=group_name)
        assert result["ResponseMetadata"]["HTTPStatusCode"] == 200
        # TODO: check parity of this assertion
        assert len(result["things"]) == 0

    @markers.aws.unknown
    def test_tags(self, aws_client):
        job_id = f"j-{short_uid()}"
        thing_name = f"t-{short_uid()}"

        result = aws_client.iot.create_thing(thingName=thing_name)
        thing_arn = result["thingArn"]
        result = aws_client.iot.create_job(jobId=job_id, targets=[thing_arn], document="{}")
        job_arn = result["jobArn"]
        tag = {"Key": "foo", "Value": "bar"}
        result = aws_client.iot.tag_resource(resourceArn=job_arn, tags=[tag])
        assert result["ResponseMetadata"]["HTTPStatusCode"] == 200

        result = aws_client.iot.list_tags_for_resource(resourceArn=job_arn)
        assert tag in result["tags"]

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(
        paths=[
            "$..rules..topicPattern",
            "$..topicRuleDestination.status",
            "$..topicRuleDestination.statusReason",
            "$..topicRuleDestination.vpcProperties",
        ]
    )
    def test_topic_lambda_rule(self, aws_client, snapshot, create_lambda_function):
        snapshot.add_transformer(snapshot.transform.key_value("arn", reference_replacement=False))
        snapshot.add_transformer(
            snapshot.transform.key_value("ruleArn", reference_replacement=False)
        )
        snapshot.add_transformer(
            snapshot.transform.key_value("ruleName", reference_replacement=False)
        )
        snapshot.add_transformer(
            snapshot.transform.key_value("functionArn", reference_replacement=False)
        )

        rule_name = f"rule_{short_uid()}"
        func_name = f"func-{short_uid()}"

        zip_file = testutil.create_lambda_archive(
            TEST_LAMBDA, get_content=True, runtime=Runtime.python3_12
        )
        func_arn = create_lambda_function(func_name=func_name, zip_file=zip_file)[
            "CreateFunctionResponse"
        ]["FunctionArn"]

        topic_rule_payload = {
            "sql": "SELECT * FROM 'some/topic'",
            "actions": [{"lambda": {"functionArn": func_arn}}],
            "ruleDisabled": False,
        }

        result = aws_client.iot.create_topic_rule(
            ruleName=rule_name, topicRulePayload=topic_rule_payload
        )
        snapshot.match("create-topic-rule", result)

        result = aws_client.iot.get_topic_rule(ruleName=rule_name)
        snapshot.match("get-topic-rule", result)

        result = aws_client.iot.list_topic_rules()
        snapshot.match("list-topic-rules", result)

        result = aws_client.iot.delete_topic_rule(ruleName=rule_name)
        snapshot.match("delete-topic-rule", result)

        # Delete operation is idempotent
        aws_client.iot.delete_topic_rule(ruleName=rule_name)
        snapshot.match("delete-topic-rule-2", result)

        result = aws_client.iot.list_topic_rules()
        snapshot.match("list-topic-rules-2", result)

        destination_config = {
            "httpUrlConfiguration": {"confirmationUrl": "https://example.com"},
        }
        result = aws_client.iot.create_topic_rule_destination(
            destinationConfiguration=destination_config
        )
        snapshot.match("create-topic-rule-destination", result)
        arn = result["topicRuleDestination"]["arn"]

        result = aws_client.iot.delete_topic_rule_destination(arn=arn)
        snapshot.match("delete-topic-rule-destination", result)

        with pytest.raises(ClientError) as exc:
            aws_client.iot.delete_topic_rule_destination(arn=arn)
        exc.match(
            rf"An error occurred \(UnauthorizedException\) when calling the DeleteTopicRuleDestination operation: "
            f"Access to TopicRuleDestination '{arn}' was denied"
        )

    @markers.aws.validated
    def test_crud_role_alias(self, create_role, snapshot, aws_client):
        role_name = f"test-role-{short_uid()}"
        trust_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"Service": "lambda.amazonaws.com"},
                    "Action": "sts:AssumeRole",
                },
            ],
        }
        role = create_role(RoleName=role_name, AssumeRolePolicyDocument=json.dumps(trust_policy))

        alias = f"alias-{short_uid()}"
        create_response = aws_client.iot.create_role_alias(
            roleArn=role["Role"]["Arn"], roleAlias=alias
        )
        snapshot.add_transformer(snapshot.transform.regex(alias, "role-alias"))
        snapshot.match("create_response", create_response)

        role_alias_description = aws_client.iot.describe_role_alias(roleAlias=alias)
        snapshot.add_transformer(snapshot.transform.regex(role["Role"]["Arn"], "role-arn"))
        snapshot.match("describe_response", role_alias_description)

        second_role = create_role(
            RoleName=f"{role_name}-2", AssumeRolePolicyDocument=json.dumps(trust_policy)
        )
        update_response = aws_client.iot.update_role_alias(
            roleArn=second_role["Role"]["Arn"], roleAlias=alias, credentialDurationSeconds=1000
        )
        snapshot.match("update_response", update_response)

        assert alias in aws_client.iot.list_role_aliases()["roleAliases"]

        delete_response = aws_client.iot.delete_role_alias(roleAlias=alias)
        snapshot.match("delete_response", delete_response)


class TestTopicRules:
    """Tests that involve IoT topic rules."""

    @pytest.fixture(autouse=True)
    def install_packages(self):
        # TODO this shouldn't be necessary, refactor to be more resilient for networking issues
        from localstack.pro.core.services.iot.packages import (
            iot_rule_engine_package,
            mosquitto_package,
        )

        with contextlib.suppress(PackageException):
            mosquitto_package.install()
            iot_rule_engine_package.install()

    @markers.aws.needs_fixing
    def test_topic_kinesis_rule(self, kinesis_create_stream, iot_topic_rule, aws_client):
        rule_name = f"r-{short_uid()}"
        topic_name = f"t-{short_uid()}"
        partition_key = f"k-{short_uid()}"
        stream = kinesis_create_stream()

        topic_rule_payload = {
            "sql": f"SELECT * FROM '{topic_name}' WHERE id = 1",
            "actions": [
                {
                    "kinesis": {
                        "streamName": stream,
                        "partitionKey": partition_key,
                        "roleArn": "dummy",
                    }
                }
            ],
            "ruleDisabled": False,
        }
        result = iot_topic_rule(RuleName=rule_name, TopicRulePayload=topic_rule_payload)
        assert result == rule_name

        result = aws_client.iot.get_topic_rule(ruleName=rule_name)
        assert result["ResponseMetadata"]["HTTPStatusCode"] == 200
        assert result["rule"]["ruleName"] == rule_name

    @markers.aws.needs_fixing
    def test_topic_sqs_rule(self, sqs_queue, iot_topic_rule, aws_client):
        rule_name = f"r-{short_uid()}"
        topic_name = f"t-{short_uid()}"
        queue_url = sqs_queue
        topic_rule_payload = {
            "sql": f"SELECT TOPIC(2) AS topic_2, TOPIC(3) AS topic_3, TOPIC(4) AS topic_4, TOPIC(5) AS org_id, "
            f"TOPIC(6) AS device_id, encode(*, 'base64') AS base64_data FROM '{topic_name}'",
            "ruleDisabled": False,
            "awsIotSqlVersion": "2016-03-23",
            "actions": [{"sqs": {"queueUrl": queue_url, "roleArn": "dummy"}}],
        }
        result = iot_topic_rule(RuleName=rule_name, TopicRulePayload=topic_rule_payload)
        assert result == rule_name

        result = aws_client.iot.get_topic_rule(ruleName=rule_name)
        assert result["ResponseMetadata"]["HTTPStatusCode"] == 200
        assert result["rule"]["ruleName"] == rule_name

    @markers.aws.needs_fixing
    def test_topic_rule_triggers_lambda(self, create_lambda_function, aws_client):
        topic_name = f"topic_{short_uid()}"

        # create test lambda
        func_name = f"func_{short_uid()}"
        zip_file = testutil.create_lambda_archive(
            TEST_LAMBDA, get_content=True, runtime=Runtime.python3_12
        )
        func_arn = create_lambda_function(func_name=func_name, zip_file=zip_file)[
            "CreateFunctionResponse"
        ]["FunctionArn"]

        # create topic rule
        aws_client.iot.create_topic_rule(
            ruleName=f"iot-test-lambda-{short_uid()}",
            topicRulePayload={
                "sql": f"SELECT * FROM '{topic_name}' WHERE id = 1",
                "actions": [{"lambda": {"functionArn": func_arn}}],
                "ruleDisabled": False,
            },
        )

        # publish messages via API
        aws_client.iot_data.publish(topic=topic_name, qos=1, payload=json.dumps({"id": 1}))

        # assert that lambda has been called
        def check_invocations():
            groups = aws_client.logs.describe_log_groups()
            matching = [
                g for g in groups["logGroups"] if g["logGroupName"] == f"/aws/lambda/{func_name}"
            ]
            assert matching

        retry(check_invocations, retries=10, sleep=2)

    @markers.only_on_amd64  # TODO: investigate
    @markers.aws.validated
    def test_topic_rule_triggers_firehose_put_record(
        self,
        iot_topic_rule,
        create_iam_role_with_policy,
        firehose_create_delivery_stream,
        s3_bucket,
        aws_client,
    ):
        buffering_interval = 60
        # firehose buffering interval, AWS sets this at minimum 60

        # The iam stuff is necessary to test against AWS
        iam_iot_role_def = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"Service": "iot.amazonaws.com"},
                    "Action": "sts:AssumeRole",
                }
            ],
        }
        iam_iot_policy_def = {
            "Version": "2012-10-17",
            "Statement": [{"Effect": "Allow", "Action": "firehose:*", "Resource": "*"}],
        }
        iam_firehose_role_def = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"Service": "firehose.amazonaws.com"},
                    "Action": "sts:AssumeRole",
                }
            ],
        }
        iam_firehose_policy_def = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": "s3:*",
                    "Resource": "*",
                }
            ],
        }
        topic_name = f"topic-{short_uid()}"
        firehose_role_name = f"firehose-role-{short_uid()}"
        firehose_policy_name = f"firehose_policy-{short_uid()}"
        firehose_role_arn = create_iam_role_with_policy(
            RoleName=firehose_role_name,
            PolicyName=firehose_policy_name,
            RoleDefinition=iam_firehose_role_def,
            PolicyDefinition=iam_firehose_policy_def,
        )
        delivery_stream_name = f"d-stream-{short_uid()}"
        s3_config = {
            "RoleARN": firehose_role_arn,
            "BucketARN": f"arn:aws:s3:::{s3_bucket}",
            "BufferingHints": {
                "IntervalInSeconds": buffering_interval,
            },
        }
        # TODO: clean this up, this is just to prevent the test from waiting
        if os.environ.get("TEST_TARGET") != "AWS_CLOUD":
            buffering_interval = 1

        # create firehose delivery stream
        retry(
            firehose_create_delivery_stream,
            DeliveryStreamName=delivery_stream_name,
            ExtendedS3DestinationConfiguration=s3_config,
            sleep=3,
            retries=3,
        )

        iot_role_name = f"iot-role-{short_uid()}"
        iot_policy_name = f"iot-policy-{short_uid()}"
        iot_role_arn = create_iam_role_with_policy(
            RoleName=iot_role_name,
            PolicyName=iot_policy_name,
            RoleDefinition=iam_iot_role_def,
            PolicyDefinition=iam_iot_policy_def,
        )

        # create topic rule
        retry(
            iot_topic_rule,
            TopicRulePayload={
                "sql": f"SELECT * FROM '{topic_name}' WHERE id = 1",
                "actions": [
                    {
                        "firehose": {
                            "deliveryStreamName": delivery_stream_name,
                            "roleArn": iot_role_arn,
                        }
                    }
                ],
                "ruleDisabled": False,
            },
            sleep=3,
            retries=3,
        )

        # publish messages via API
        aws_client.iot_data.publish(topic=topic_name, qos=0, payload=json.dumps({"id": 0}))
        aws_client.iot_data.publish(topic=topic_name, qos=1, payload=json.dumps({"id": 1}))

        # assert that the message made it to s3
        def check_invocations():
            list_bucket_result = aws_client.s3.list_objects(Bucket=s3_bucket)
            assert len(list_bucket_result["Contents"]) == 1
            get_object_response = aws_client.s3.get_object(
                Bucket=s3_bucket, Key=list_bucket_result["Contents"][0]["Key"]
            )
            content = get_object_response["Body"].read().decode("utf-8")
            assert json.loads(content)["id"] == 1

        retry(
            check_invocations,
            sleep_before=buffering_interval + (buffering_interval / 12),
            retries=10,
            sleep=buffering_interval / 2,
        )

    @markers.aws.validated
    def test_topic_rule_triggers_kinesis_put_record(
        self,
        iot_topic_rule,
        kinesis_create_stream,
        wait_for_stream_ready,
        create_iam_role_with_policy,
        aws_client,
    ):
        topic_name = f"topic_{short_uid()}"
        # create test kinesis stream
        stream_name = kinesis_create_stream()

        # The iam stuff is necessary to test against AWS
        iam_iot_role_def = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"Service": "iot.amazonaws.com"},
                    "Action": "sts:AssumeRole",
                }
            ],
        }
        iam_iot_policy_def = {
            "Version": "2012-10-17",
            "Statement": [{"Effect": "Allow", "Action": "kinesis:*", "Resource": "*"}],
        }
        iot_role_name = f"iot-role-{short_uid()}"
        iot_policy_name = f"iot-policy-{short_uid()}"
        iot_role_arn = create_iam_role_with_policy(
            RoleName=iot_role_name,
            PolicyName=iot_policy_name,
            RoleDefinition=iam_iot_role_def,
            PolicyDefinition=iam_iot_policy_def,
        )
        # create topic rule
        retry(
            iot_topic_rule,
            TopicRulePayload={
                "sql": f"SELECT * FROM '{topic_name}' WHERE id = 1",
                "actions": [
                    {
                        "kinesis": {
                            "streamName": stream_name,
                            "partitionKey": "1",
                            "roleArn": iot_role_arn,
                        }
                    }
                ],
                "ruleDisabled": False,
            },
            sleep=3,
            retries=3,
        )
        wait_for_stream_ready(stream_name)
        # publish messages via API
        aws_client.iot_data.publish(topic=topic_name, qos=0, payload=json.dumps({"id": 0}))
        aws_client.iot_data.publish(topic=topic_name, qos=1, payload=json.dumps({"id": 1}))

        # search in all shards
        def get_shard_iterators(stream_name, kinesis_client):
            shard_iterators = []
            for i in range(0, 4):
                response = aws_client.kinesis.describe_stream(StreamName=stream_name)
                sequence_number = (
                    response.get("StreamDescription")
                    .get("Shards")[i]
                    .get("SequenceNumberRange")
                    .get("StartingSequenceNumber")
                )
                shard_id = response.get("StreamDescription").get("Shards")[i].get("ShardId")
                response = aws_client.kinesis.get_shard_iterator(
                    StreamName=stream_name,
                    ShardId=shard_id,
                    ShardIteratorType="AT_SEQUENCE_NUMBER",
                    StartingSequenceNumber=sequence_number,
                )
                shard_iterators.append(response.get("ShardIterator"))
            return shard_iterators

        iterators = get_shard_iterators(stream_name, aws_client.kinesis)

        # assert that kinesis has received the record
        def check_stream_entries():
            found_record = False
            for iterator in iterators:
                response = aws_client.kinesis.get_records(ShardIterator=iterator)
                records = response.get("Records")
                if records:
                    record = records[0]["Data"]
                    record = bytes.decode(record, "utf-8")
                    found_record = json.loads(record)["id"] == 1
            assert found_record

        retry(check_stream_entries, retries=2, sleep_before=5)

    @markers.aws.validated
    def test_topic_rule_triggers_sqs_message(
        self, iot_topic_rule, create_iam_role_with_policy, sqs_queue, aws_client
    ):
        topic_name = "/ut/device/datapub/#"
        queue_url = sqs_queue

        # The iam stuff is necessary to test against AWS
        iam_iot_role_def = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"Service": "iot.amazonaws.com"},
                    "Action": "sts:AssumeRole",
                }
            ],
        }
        iam_iot_policy_def = {
            "Version": "2012-10-17",
            "Statement": [{"Effect": "Allow", "Action": "sqs:*", "Resource": "*"}],
        }
        iot_role_name = f"iot-role-{short_uid()}"
        iot_policy_name = f"iot-policy-{short_uid()}"
        iot_role_arn = create_iam_role_with_policy(
            RoleName=iot_role_name,
            PolicyName=iot_policy_name,
            RoleDefinition=iam_iot_role_def,
            PolicyDefinition=iam_iot_policy_def,
        )
        # create topic rule
        retry(
            iot_topic_rule,
            RuleName=f"utdevice__datachannels_{short_uid()}",
            TopicRulePayload={
                "sql": f"SELECT TOPIC(2) AS topic_2, TOPIC(3) AS topic_3, TOPIC(4) AS topic_4, TOPIC(5) AS org_id , TOPIC(6) AS device_id, encode(*, 'base64') AS base64_data FROM '{topic_name}'",
                "ruleDisabled": False,
                "awsIotSqlVersion": "2016-03-23",
                "actions": [{"sqs": {"queueUrl": queue_url, "roleArn": iot_role_arn}}],
            },
            sleep=3,
            retries=3,
        )
        # push to concrete topic, wildcards are not allowed here
        topic_name = topic_name.replace("#", "08008dca-7e0b-41f8-b2d6-bfc60d915a03/35")
        aws_client.iot_data.publish(
            topic=topic_name,
            qos=1,
            payload=json.dumps({"hello": "world"}),
        )

        def check_queue_entries():
            result = aws_client.sqs.receive_message(QueueUrl=queue_url, VisibilityTimeout=0)
            assert result.get("Messages")
            message = json.loads(result["Messages"][0]["Body"])
            assert base64.b64decode(message["base64_data"]).decode("utf-8") == json.dumps(
                {"hello": "world"}
            )

        retry(check_queue_entries, sleep=1, retries=5)

    @markers.aws.validated
    def test_topic_rule_triggers_dynamodb_v2_put_item(
        self,
        iot_topic_rule,
        dynamodb_create_table,
        create_iam_role_with_policy,
        aws_client,
        snapshot,
    ):
        """
        See https://docs.aws.amazon.com/iot/latest/apireference/API_Action.html
        dynamoDBv2
        Write to a DynamoDB table. This is a new version of the DynamoDB action. It allows you to write each attribute
        in an MQTT message payload into a separate DynamoDB column.
        """
        topic_name = f"topic_{short_uid()}"
        snapshot.add_transformer(
            [
                snapshot.transform.key_value("ruleName"),
                snapshot.transform.key_value("tableName"),
                snapshot.transform.key_value("roleArn"),
                snapshot.transform.regex(topic_name, "<topic-name>"),
            ]
        )
        topic_rule_name = f"topic_rule_name_{short_uid()}"
        # create test dynamodb table
        ddb_table = dynamodb_create_table(partition_key="thingId")
        table_name = ddb_table["TableDescription"]["TableName"]

        # The iam stuff is necessary to test against AWS
        iam_iot_role_def = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"Service": "iot.amazonaws.com"},
                    "Action": "sts:AssumeRole",
                }
            ],
        }
        # maybe could be more restrictive
        iam_iot_policy_def = {
            "Version": "2012-10-17",
            "Statement": [{"Effect": "Allow", "Action": "dynamodb:*", "Resource": "*"}],
        }

        iot_role_name = f"iot-role-{short_uid()}"
        iot_policy_name = f"iot-policy-{short_uid()}"
        iot_role_arn = create_iam_role_with_policy(
            RoleName=iot_role_name,
            PolicyName=iot_policy_name,
            RoleDefinition=iam_iot_role_def,
            PolicyDefinition=iam_iot_policy_def,
        )
        # create topic rule
        retry(
            iot_topic_rule,
            RuleName=topic_rule_name,
            TopicRulePayload={
                "sql": f"SELECT * FROM '{topic_name}' WHERE thingId = 'myid1'",
                "actions": [
                    {
                        "dynamoDBv2": {
                            "putItem": {
                                "tableName": table_name,
                            },
                            "roleArn": iot_role_arn,
                        }
                    }
                ],
                "ruleDisabled": False,
            },
            sleep=3,
            retries=3,
        )

        topic_rule_resp = aws_client.iot.get_topic_rule(ruleName=topic_rule_name)
        snapshot.match("get-topic-rule", topic_rule_resp)

        # publish messages via API
        aws_client.iot_data.publish(
            topic=topic_name, qos=0, payload=json.dumps({"thingId": "myid1", "test-col1": "mycol"})
        )
        aws_client.iot_data.publish(
            topic=topic_name, qos=1, payload=json.dumps({"thingId": "myid2", "test-col1": "mycol2"})
        )

        # assert that dynamodb has the item with myid1
        def scan_ddb_table():
            scan_result = aws_client.dynamodb.scan(TableName=table_name)
            assert scan_result["Count"] == 1
            return scan_result

        result = retry(scan_ddb_table, retries=5)
        snapshot.match("dynamodb-result", result)

    @markers.aws.validated
    def test_registry_events_with_topic_rule_triggers_dynamodb_v2_put_item(
        self,
        iot_topic_rule,
        dynamodb_create_table,
        create_iam_role_with_policy,
        aws_client,
        snapshot,
    ):
        topic_name = f"topic_{short_uid()}"
        snapshot.add_transformer(
            [
                snapshot.transform.key_value("ruleName"),
                snapshot.transform.key_value("tableName"),
                snapshot.transform.key_value("roleArn"),
                snapshot.transform.regex(topic_name, "<topic-name>"),
                snapshot.transform.jsonpath("$.dynamodb-result.Items..eventId.S", "event-id"),
            ]
        )
        snapshot.add_transformer(
            SortingTransformer("Items", lambda x: x["operation"]["S"]),
            priority=-1,
        )
        topic_rule_name = f"topic_rule_name_{short_uid()}"
        # create test dynamodb table
        ddb_table = dynamodb_create_table(partition_key="eventId")
        table_name = ddb_table["TableDescription"]["TableName"]

        # The iam stuff is necessary to test against AWS
        iam_iot_role_def = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"Service": "iot.amazonaws.com"},
                    "Action": "sts:AssumeRole",
                }
            ],
        }
        # maybe could be more restrictive
        iam_iot_policy_def = {
            "Version": "2012-10-17",
            "Statement": [{"Effect": "Allow", "Action": "dynamodb:*", "Resource": "*"}],
        }

        iot_role_name = f"iot-role-{short_uid()}"
        iot_policy_name = f"iot-policy-{short_uid()}"
        iot_role_arn = create_iam_role_with_policy(
            RoleName=iot_role_name,
            PolicyName=iot_policy_name,
            RoleDefinition=iam_iot_role_def,
            PolicyDefinition=iam_iot_policy_def,
        )
        # create topic rule
        retry(
            iot_topic_rule,
            RuleName=topic_rule_name,
            TopicRulePayload={
                "sql": "SELECT * FROM '$aws/events/thing/#'",  # this will save the message as it is in ddb
                "actions": [
                    {
                        "dynamoDBv2": {
                            "putItem": {
                                "tableName": table_name,
                            },
                            "roleArn": iot_role_arn,
                        }
                    }
                ],
                "ruleDisabled": False,
            },
            sleep=3,
            retries=5,
        )

        topic_rule_resp = aws_client.iot.get_topic_rule(ruleName=topic_rule_name)
        snapshot.match("get-topic-rule", topic_rule_resp)

        # enable Registry Events to be sent
        # see https://docs.aws.amazon.com/iot/latest/developerguide/iot-events.html#iot-events-enable
        # allows events to be published to
        # $aws/events/thing/{thingName}/created
        # $aws/events/thing/{thingName}/updated
        # $aws/events/thing/{thingName}/deleted
        resp = aws_client.iot.update_event_configurations(
            eventConfigurations={"THING": {"Enabled": True}}
        )
        snapshot.match("update-event-config", resp)

        # it seems localstack takes a while to subscribe to $aws/events/#, so we wait for a while
        if not is_aws_cloud():
            time.sleep(5)

        thing_name = f"my_thing_{short_uid()}"
        create_thing = aws_client.iot.create_thing(thingName=thing_name)
        # we have to add it this way, because there's an issue by replacing thingName in ddb result (in dict)
        snapshot.add_transformer(
            snapshot.transform.regex(create_thing["thingName"], "<thing-name:1>")
        )
        snapshot.match("create-thing", create_thing)

        update_thing = aws_client.iot.update_thing(
            thingName=thing_name,
            attributePayload={
                "attributes": {"test": "attr1"},
            },
        )
        snapshot.match("update-thing", update_thing)

        # just to compare with the event
        describe_thing = aws_client.iot.describe_thing(thingName=thing_name)
        snapshot.match("describe-thing", describe_thing)

        # delete thing
        delete_thing = aws_client.iot.delete_thing(thingName=thing_name)
        snapshot.match("delete-thing", delete_thing)

        # match all table entries
        def scan_ddb_table():
            scan_result = aws_client.dynamodb.scan(TableName=table_name)
            assert scan_result["Count"] == 3
            return scan_result

        result = retry(scan_ddb_table, retries=2, sleep_before=5)
        snapshot.match("dynamodb-result", result)
        # assert the length of the eventId format, as we skip the snapshot verify for it
        # eventId = 69a12e090c12b0d1bb772006d533ddf5
        event_id = result["Items"][0]["eventId"]["S"]
        assert len(event_id) == 32
        # assert it's an hex string
        assert int(event_id, 16)
        # manually assert the timestamp as the snapshot mangles it
        event_timestamp = result["Items"][0]["timestamp"]["N"]
        assert int(event_timestamp)
        assert datetime.datetime.fromtimestamp(float(event_timestamp) / 1000)


class TestMQTT:
    """Tests for MQTT implementation."""

    @markers.aws.needs_fixing
    def test_publish_to_mqtt_topic(self, aws_client):
        broker_address = "mqtt://" + aws_client.iot.describe_endpoint()["endpointAddress"]

        topic_name = f"test_topic_{short_uid()}"
        num_messages = 5
        messages_sent = []
        messages_received = []

        def cb_process_message(_, __, message):
            message = json.loads(to_str(message.payload))
            messages_received.append(message)

        if "amazonaws.com" in broker_address:
            broker_address = f"{broker_address}:443"

        mqtt_subscribe(broker_address, topic_name, cb_process_message)

        # test publish using an MQTT client

        for i in range(0, num_messages):
            message = {"id": i}
            messages_sent.append(message)
            message = to_bytes(json.dumps(message))
            mqtt_publish(broker_address, topic_name, message, qos=1)

        def check_finished():
            assert len(messages_received) == num_messages
            for msg in messages_received:
                assert msg in messages_sent

        retry(check_finished, retries=50, sleep=1)

        # test publish using `IOTData:Publish` operation

        messages_sent = []
        messages_received = []
        for i in range(0, num_messages):
            message = {"id": i}
            messages_sent.append(message)
            message = to_bytes(json.dumps(message))
            aws_client.iot_data.publish(topic=topic_name, qos=1, payload=message)

        retry(check_finished, retries=5, sleep=1)

    @markers.aws.needs_fixing
    def test_lifecycle_events(self, aws_client):
        broker_address = "mqtt://" + aws_client.iot.describe_endpoint()["endpointAddress"]
        client_id = f"LS-TESTS-{short_uid()}"
        test_topic = "localstack/test"

        messages = {}

        def cb_process_message(_, __, message):
            payload = json.loads(message.payload)
            messages[payload["eventType"]] = payload

        mqtt_subscribe(
            endpoint=broker_address,
            topic=LIFECYCLE_CONNECTED_TEMPL.format(client_id=client_id),
            callback=cb_process_message,
            qos=1,
        )
        mqtt_subscribe(
            endpoint=broker_address,
            topic=LIFECYCLE_SUBSCRIBE_TEMPL.format(client_id=client_id),
            callback=cb_process_message,
            qos=1,
        )
        mqtt_subscribe(
            endpoint=broker_address,
            topic=LIFECYCLE_UNSUBSCRIBE_TEMPL.format(client_id=client_id),
            callback=cb_process_message,
            qos=1,
        )
        mqtt_subscribe(
            endpoint=broker_address,
            topic=LIFECYCLE_DISCONNECTED_TEMPL.format(client_id=client_id),
            callback=cb_process_message,
            qos=1,
        )

        # Wait for subscriber loops to be up and running before connecting an MQTT client
        # TODO: Use a proper sync primitive. Barriers in `on_subscribed` for above subscriber_loop calls don't work
        time.sleep(5)

        # Each of these callbacks must emit a lifecycle events. They are chained to ensure proper order
        def on_connect(client, userdata, flags, rc):
            client.subscribe(test_topic)

        def on_subscribe(client, userdata, mid, granted_qos):
            client.unsubscribe(test_topic)

        def on_unsubscribe(client, userdata, mid):
            client.disconnect()

        def on_disconnect(client, userdata, rc):
            client.loop_stop()

        c = create_mqtt_client(
            endpoint=broker_address,
            client_id=client_id,
            on_connect=on_connect,
            on_subscribe=on_subscribe,
            on_unsubscribe=on_unsubscribe,
            on_disconnect=on_disconnect,
        )
        c.loop_start()  # Blocks until loop_stop() is called

        def assertions():
            assert "connected" in messages
            assert messages["connected"]["clientId"] == client_id

            assert "disconnected" in messages
            assert messages["disconnected"]["clientId"] == client_id
            assert messages["disconnected"]["disconnectReason"] == "CLIENT_INITIATED_DISCONNECT"
            assert messages["disconnected"]["clientInitiatedDisconnect"]

            assert "subscribed" in messages
            assert messages["subscribed"]["clientId"] == client_id
            assert messages["subscribed"]["topics"] == [test_topic]

            assert "unsubscribed" in messages
            assert messages["unsubscribed"]["clientId"] == client_id
            assert messages["unsubscribed"]["topics"] == [test_topic]

            assert len(messages) == 4

        retry(assertions, retries=3, sleep=1)

    # @markers.skip_offline  # requires downloading public cert files
    @pytest.mark.parametrize("protocol", ["mqtt", "websockets"])
    @pytest.mark.skip(reason="awsiotsdk")
    @markers.aws.validated
    def test_connect_mqtt_via_aws_iot_sdk(
        self, protocol, cert_and_keys, create_thing_with_policy, aws_client
    ):
        from awsiot import mqtt_connection_builder

        port = None
        endpoint = aws_client.iot.describe_endpoint(endpointType="iot:Data-ATS")["endpointAddress"]
        if not is_aws_cloud():
            port = int(endpoint.split(":")[-1])
            endpoint = "localhost.localstack.cloud"
            wait_for_port_open(port, retries=15, sleep_time=0.7)

        topic_name = f"test/{short_uid()}"

        # create a thing with policy which will be attached to the thing
        create_thing_with_policy()
        _, cert_file, priv_key_file, root_ca_file = cert_and_keys

        def on_message_received(topic, payload, *args, **kwargs):
            received_msgs.append(payload)

        # create connection
        received_msgs = []
        event_loop_group = io.EventLoopGroup(1)
        host_resolver = io.DefaultHostResolver(event_loop_group)
        client_bootstrap = io.ClientBootstrap(event_loop_group, host_resolver)
        auth_kwargs = {"client_bootstrap": client_bootstrap}
        kwargs = {
            "client_id": f"test-client-{short_uid()}",
            "endpoint": endpoint,
            "port": port,
            "client_bootstrap": client_bootstrap,
            "ca_filepath": root_ca_file,
            **auth_kwargs,
        }

        if protocol == "websockets":
            credentials_provider = awscrt.auth.AwsCredentialsProvider.new_default_chain(
                **auth_kwargs
            )
            connection = mqtt_connection_builder.websockets_with_default_aws_signing(
                region=aws_client.iot.meta.region_name,
                credentials_provider=credentials_provider,
                **kwargs,
            )
        else:
            # AWS MQTT endpoints expects the TLS ALPN extension to be set to use the regular MQTT protocol.
            # awsiotsdk does this automatically but only when the port is 443.
            # For other ports (as the case with LocalStack) this must be done manually.
            tls_ctx_options = awscrt.io.TlsContextOptions.create_client_with_mtls_from_path(
                cert_file, priv_key_file
            )
            tls_ctx_options.alpn_list = ["x-amzn-mqtt-ca"]
            connection = mqtt_connection_builder._builder(
                tls_ctx_options,
                cert_filepath=cert_file,
                pri_key_filepath=priv_key_file,
                **kwargs,
            )
        connection.connect().result()

        # subscribe client
        subscribe_future, packet_id = connection.subscribe(
            topic=topic_name, qos=mqtt.QoS.AT_LEAST_ONCE, callback=on_message_received
        )
        subscribe_future.result()

        # publish messages to the server
        num_messages = 3
        for i in range(num_messages):
            message = {"message": f"test message {i}"}
            connection.publish(
                topic=topic_name, payload=json.dumps(message), qos=mqtt.QoS.AT_LEAST_ONCE
            )

        def _check_received():
            assert len(received_msgs) == num_messages

        retry(_check_received, retries=10, sleep=0.7)

        # disconnect the client
        connection.disconnect().result()

    @markers.aws.needs_fixing
    @pytest.mark.parametrize(
        "payload", (b'{"json":1}', b"\x01", b""), ids=("json", "binary", "empty")
    )
    def test_payload_variety(self, aws_client, payload):
        broker_address = "mqtt://" + aws_client.iot.describe_endpoint()["endpointAddress"]
        topic = f"foo/bar/{short_uid()}"

        message_received: mqtt.MQTTMessage = None

        def cb_process_message(_, __, msg):
            nonlocal message_received
            message_received = msg

        mqtt_subscribe(broker_address, topic, cb_process_message)

        def _assert(expected_payload: Any):
            nonlocal message_received
            assert message_received is not None
            assert message_received.payload == expected_payload

        time.sleep(1)

        mqtt_publish(broker_address, topic, payload)
        retry(_assert, retries=10, sleep=1, expected_payload=payload)
