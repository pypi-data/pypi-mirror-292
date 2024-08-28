import logging
import time
import uuid
from typing import Dict

import pytest
from localstack.pro.core.services.rds.engine_postgres import DBBackendPostgres
from localstack.testing.pytest import markers
from localstack.utils.strings import short_uid
from localstack.utils.sync import retry
from moto.ssm.models import ssm_backends

LOG = logging.getLogger(__name__)

# TODO: design a better template to be able to run tests against AWS
DUMMY_EXPERIMENT_TEMPLATE_REQUEST = {
    "description": "Test instance termination",
    "targets": {
        "to-terminate": {
            "resourceType": "aws:ec2:instance",
            "resourceTags": {"env": "test"},
            "selectionMode": "COUNT(3)",
        }
    },
    "actions": {
        "TerminateInstances": {
            "actionId": "localstack:do-nothing",
            "description": "terminate instances",
            "targets": {"Instances": "to-terminate"},
        }
    },
    "stopConditions": [{"source": "none"}],
    "roleArn": "arn:aws:iam:123456789012:role/ExperimentRole",
    "tags": {"some template tag name": "some template tag value"},
}


API_FAULTS_TEMPLATE = {
    "actions": {
        "Some test action": {
            "actionId": "localstack:generic:api-error",
            "parameters": {"errorCode": "400"},
        }
    },
    "description": "template for a test action",
    "stopConditions": [{"source": "none"}],
    "roleArn": "arn:aws:iam:123456789012:role/ExperimentRole",
}

# We use errorCode 400 here, as the default 500 results in automatic retries by our test environment, which results
# in unnecessary delays.
# We also split the parameters from the template config itself, as our tests are not isolated, several tests use this
# template, and we want to reset the params to this default for each test. We could perform a deep copy of the
# template config instead.
API_FAULTS_TEMPLATE_PARAMETERS = {"errorCode": "400"}


def _get_api_faults_template_with_parameter(parameters: Dict):
    template = API_FAULTS_TEMPLATE
    # We use update() here instead of assignment, as we want the errorCode of 400 to stay there by default and to be
    # only overwritten if it is set explicitly to something else.
    template["actions"]["Some test action"]["parameters"] = API_FAULTS_TEMPLATE_PARAMETERS.copy()
    template["actions"]["Some test action"]["parameters"].update(parameters)
    return template


@pytest.fixture()
def create_experiment_template(aws_client):
    experiment_template_ids = list()

    def factory(**kwargs):
        if not kwargs:
            kwargs = DUMMY_EXPERIMENT_TEMPLATE_REQUEST
        result = aws_client.fis.create_experiment_template(**kwargs)
        experiment_template_ids.append(result["experimentTemplate"]["id"])
        return result

    yield factory

    for experiment_template_id in experiment_template_ids:
        try:
            aws_client.fis.delete_experiment_template(id=experiment_template_id)
        except Exception as e:
            # Some tests clean after themselves, so an absent template is not an error.
            if "ResourceNotFoundException" not in str(e):
                LOG.debug(
                    "Error cleaning up FIS Experiment Template ID: %s, %s",
                    experiment_template_id,
                    e,
                )


@pytest.fixture()
def start_experiment(create_experiment_template, aws_client):
    experiment_ids = list()

    def factory(experiment_request=None, template_request=None):
        if not experiment_request and not template_request:
            raise ValueError("Either experiment_request or template_request is supposed to be set")
        if not experiment_request:
            experiment_template_id = create_experiment_template(**template_request)[
                "experimentTemplate"
            ]["id"]
            experiment_request = {}
            experiment_request["experimentTemplateId"] = experiment_template_id
        result = aws_client.fis.start_experiment(**experiment_request)
        experiment_ids.append(result["experiment"]["id"])
        return result

    yield factory

    for experiment_id in experiment_ids:
        try:
            aws_client.fis.stop_experiment(id=experiment_id)
        except Exception as e:
            LOG.debug("Error stopping FIS Experiment ID: %s, %s", experiment_id, e)


# When an experiment runs in FIS, actions get new attributes - startTime and endTime. Such attributes are absent from
# templates those experiments are based on. And since these attributes are a few levels inside of a dict for
# an experiment (experiment -> actions -> action_name -> startTime/endTime) it is too much bother to match such
# structures properly. But since this is just for tests, we can break stuff a bit by removing those attributes from
# actions before we do the matching.
def _remove_start_and_end_times_from_actions(stuff):
    if "actions" not in stuff:
        return stuff
    for action in stuff["actions"].values():
        action.pop("startTime", None)
        action.pop("endTime", None)
    return stuff


def _do_outputs_match_inputs(outputs, inputs, attributes_to_match):
    outputs = _remove_start_and_end_times_from_actions(outputs)
    for attribute_to_match in attributes_to_match:
        if attribute_to_match not in inputs:
            if attribute_to_match in outputs:
                LOG.debug(
                    "Matching error: attribute %s is in outputs, but not in inputs",
                    attribute_to_match,
                )
                return False
            continue
        if attribute_to_match not in outputs:
            LOG.debug("Matching error: attribute %s is not in outputs", attribute_to_match)
            return False
        if outputs.get(attribute_to_match) != inputs.get(attribute_to_match):
            LOG.debug(
                "Matching error: values for attribute '%s' do not match between outputs and inputs: %s != %s",
                attribute_to_match,
                outputs.get(attribute_to_match),
                inputs.get(attribute_to_match),
            )
            return False
    return True


def _does_experiment_template_match_request(
    experiment_template, creation_request, template_is_a_summary=False
):
    attributes_to_match = {
        "actions",
        "description",
        "logConfiguration",
        "roleArn",
        "stopConditions",
        "tags",
        "targets",
    }
    if template_is_a_summary:
        attributes_to_match = {"description", "tags"}
    return _do_outputs_match_inputs(experiment_template, creation_request, attributes_to_match)


def _does_experiment_match_request_and_template(
    experiment, creation_request, experiment_template, experiment_is_a_summary=False
):
    attributes_to_match = {
        "actions",
        "logConfiguration",
        "roleArn",
        "stopConditions",
        "tags",
        "targets",
    }
    if experiment_is_a_summary:
        attributes_to_match = {"tags"}
    everything_mashed_together = experiment_template.copy()
    everything_mashed_together.update(creation_request)
    if "tags" not in creation_request and "tags" in everything_mashed_together:
        everything_mashed_together.pop("tags")
    return _do_outputs_match_inputs(experiment, everything_mashed_together, attributes_to_match)


# Tests using this function might fail if some other process during a test adds/removes counted objects.
def _get_experiment_templates_count(fis_client):
    next_token = None
    count = 0
    while True:
        kwargs = {"nextToken": next_token} if next_token else {}
        response = fis_client.list_experiment_templates(**kwargs)
        count += len(response["experimentTemplates"])
        if "nextToken" not in response:
            break
        next_token = response["nextToken"]
    return count


def _get_experiment_template_summary_from_list(fis_client, experiment_template_id):
    next_token = None
    while True:
        kwargs = {"nextToken": next_token} if next_token else {}
        response = fis_client.list_experiment_templates(**kwargs)
        for experiment_template_summary in response["experimentTemplates"]:
            if experiment_template_summary["id"] == experiment_template_id:
                return experiment_template_summary
        if not response["nextToken"]:
            break
        next_token = response["nextToken"]
    return None


# Tests using this function might fail if some other process during a test adds/removes counted objects.
def _get_experiments_count(fis_client):
    next_token = None
    count = 0
    while True:
        kwargs = {"nextToken": next_token} if next_token else {}
        response = fis_client.list_experiments(**kwargs)
        count += len(response["experiments"])
        if "nextToken" not in response:
            break
        next_token = response["nextToken"]
    return count


def _get_experiment_summary_from_list(fis_client, experiment_id):
    next_token = None
    while True:
        kwargs = {"nextToken": next_token} if next_token else {}
        response = fis_client.list_experiments(**kwargs)
        for experiment_summary in response["experiments"]:
            if experiment_summary["id"] == experiment_id:
                return experiment_summary
        if not response["nextToken"]:
            break
        next_token = response["nextToken"]
    return None


class TestFis:
    @markers.aws.unknown
    def test_create_experiment_template(self, create_experiment_template, aws_client):
        response = create_experiment_template(**DUMMY_EXPERIMENT_TEMPLATE_REQUEST)
        assert response["ResponseMetadata"]["HTTPStatusCode"] == 200
        assert "experimentTemplate" in response
        assert _does_experiment_template_match_request(
            response["experimentTemplate"], DUMMY_EXPERIMENT_TEMPLATE_REQUEST
        )
        assert "id" in response["experimentTemplate"]

    @markers.aws.unknown
    def test_list_experiment_templates(self, create_experiment_template, aws_client):
        response = aws_client.fis.list_experiment_templates()
        assert response["ResponseMetadata"]["HTTPStatusCode"] == 200
        assert "experimentTemplates" in response

        experiment_templates_count = _get_experiment_templates_count(aws_client.fis)
        response = create_experiment_template(**DUMMY_EXPERIMENT_TEMPLATE_REQUEST)
        assert _get_experiment_templates_count(aws_client.fis) == experiment_templates_count + 1

        experiment_template_id = response["experimentTemplate"]["id"]
        experiment_template_summary = _get_experiment_template_summary_from_list(
            aws_client.fis, experiment_template_id
        )
        assert experiment_template_summary
        assert _does_experiment_template_match_request(
            experiment_template_summary,
            DUMMY_EXPERIMENT_TEMPLATE_REQUEST,
            template_is_a_summary=True,
        )
        assert "id" in experiment_template_summary
        assert experiment_template_summary["id"] == experiment_template_id

    @markers.aws.unknown
    def test_get_experiment_template(self, create_experiment_template, aws_client):
        response = create_experiment_template(**DUMMY_EXPERIMENT_TEMPLATE_REQUEST)
        experiment_template_id = response["experimentTemplate"]["id"]
        response = aws_client.fis.get_experiment_template(id=experiment_template_id)
        assert response["ResponseMetadata"]["HTTPStatusCode"] == 200
        assert "experimentTemplate" in response
        assert _does_experiment_template_match_request(
            response["experimentTemplate"], DUMMY_EXPERIMENT_TEMPLATE_REQUEST
        )
        assert "id" in response["experimentTemplate"]
        assert response["experimentTemplate"]["id"] == experiment_template_id

    @markers.aws.unknown
    def test_delete_experiment_template(self, create_experiment_template, aws_client):
        experiment_templates_count = _get_experiment_templates_count(aws_client.fis)
        experiment_template_id = create_experiment_template()["experimentTemplate"]["id"]
        assert _get_experiment_templates_count(aws_client.fis) == experiment_templates_count + 1
        response = aws_client.fis.delete_experiment_template(id=experiment_template_id)
        assert _get_experiment_templates_count(aws_client.fis) == experiment_templates_count
        assert response["ResponseMetadata"]["HTTPStatusCode"] == 200
        assert "experimentTemplate" in response
        assert _does_experiment_template_match_request(
            response["experimentTemplate"], DUMMY_EXPERIMENT_TEMPLATE_REQUEST
        )
        assert "id" in response["experimentTemplate"]
        assert response["experimentTemplate"]["id"] == experiment_template_id
        with pytest.raises(Exception) as e:
            aws_client.fis.delete_experiment_template(id=experiment_template_id)
        e.match("ResourceNotFoundException")
        # Checking if it didn't delete some other template by mistake.
        assert response["experimentTemplate"]["id"] == experiment_template_id

    @markers.aws.unknown
    def test_idempotency_of_create_experiment_template(
        self, create_experiment_template, aws_client
    ):
        experiment_templates_count = _get_experiment_templates_count(aws_client.fis)
        # Can't use a fixed token, as tests are not isolated from each other.
        first_client_token = str(uuid.uuid4())
        response = create_experiment_template(
            **DUMMY_EXPERIMENT_TEMPLATE_REQUEST, clientToken=first_client_token
        )
        assert _does_experiment_template_match_request(
            response["experimentTemplate"], DUMMY_EXPERIMENT_TEMPLATE_REQUEST
        )
        first_template_id = response["experimentTemplate"]["id"]
        assert _get_experiment_templates_count(aws_client.fis) == experiment_templates_count + 1

        # Supposed to get the same template without creating a new one.
        response = create_experiment_template(
            **DUMMY_EXPERIMENT_TEMPLATE_REQUEST, clientToken=first_client_token
        )
        assert _does_experiment_template_match_request(
            response["experimentTemplate"], DUMMY_EXPERIMENT_TEMPLATE_REQUEST
        )
        assert response["experimentTemplate"]["id"] == first_template_id
        assert _get_experiment_templates_count(aws_client.fis) == experiment_templates_count + 1

        # A change of the token should result in a new experiment template.
        second_client_token = first_client_token + " and something else"
        response = create_experiment_template(
            **DUMMY_EXPERIMENT_TEMPLATE_REQUEST, clientToken=second_client_token
        )
        assert _does_experiment_template_match_request(
            response["experimentTemplate"], DUMMY_EXPERIMENT_TEMPLATE_REQUEST
        )
        assert response["experimentTemplate"]["id"] != first_template_id
        assert _get_experiment_templates_count(aws_client.fis) == experiment_templates_count + 2

    @markers.aws.unknown
    def test_start_experiment(self, create_experiment_template, start_experiment, aws_client):
        experiment_template = create_experiment_template()["experimentTemplate"]
        experiment_template_id = experiment_template["id"]
        start_experiment_request = {"experimentTemplateId": experiment_template_id}
        response = start_experiment(start_experiment_request)
        assert response["ResponseMetadata"]["HTTPStatusCode"] == 200
        assert "experiment" in response
        experiment = response["experiment"]
        assert _does_experiment_match_request_and_template(
            experiment, start_experiment_request, experiment_template
        )
        assert "id" in experiment
        assert "experimentTemplateId" in experiment
        assert experiment["experimentTemplateId"] == experiment_template_id
        assert "state" in experiment
        assert "status" in experiment["state"]
        assert experiment["state"]["status"] != "stopped"

    @markers.aws.unknown
    def test_list_experiments(self, create_experiment_template, start_experiment, aws_client):
        response = aws_client.fis.list_experiments()
        assert response["ResponseMetadata"]["HTTPStatusCode"] == 200
        assert "experiments" in response
        experiment_template = create_experiment_template()["experimentTemplate"]
        experiment_template_id = experiment_template["id"]

        experiments_count = _get_experiments_count(aws_client.fis)
        start_experiment_request = {"experimentTemplateId": experiment_template_id}
        response = start_experiment(start_experiment_request)
        assert _get_experiments_count(aws_client.fis) == experiments_count + 1
        experiment_id = response["experiment"]["id"]
        experiment_summary = _get_experiment_summary_from_list(aws_client.fis, experiment_id)
        assert experiment_summary
        assert _does_experiment_match_request_and_template(
            response["experiment"],
            start_experiment_request,
            experiment_template,
            experiment_is_a_summary=True,
        )
        assert "id" in experiment_summary
        assert experiment_summary["id"] == experiment_id

    @markers.aws.unknown
    def test_get_experiment(self, create_experiment_template, start_experiment, aws_client):
        experiment_template = create_experiment_template()["experimentTemplate"]
        experiment_template_id = experiment_template["id"]
        start_experiment_request = {"experimentTemplateId": experiment_template_id}
        response = start_experiment(start_experiment_request)
        experiment_id = response["experiment"]["id"]
        response = aws_client.fis.get_experiment(id=experiment_id)
        assert response["ResponseMetadata"]["HTTPStatusCode"] == 200
        assert "experiment" in response
        assert _does_experiment_match_request_and_template(
            response["experiment"],
            start_experiment_request,
            experiment_template,
        )
        assert "id" in response["experiment"]
        assert response["experiment"]["id"] == experiment_id

    @markers.aws.unknown
    def test_stop_experiment(self, create_experiment_template, start_experiment, aws_client):
        experiment_template = create_experiment_template()["experimentTemplate"]
        experiment_template_id = experiment_template["id"]
        start_experiment_request = {"experimentTemplateId": experiment_template_id}

        experiment_id = start_experiment(start_experiment_request)["experiment"]["id"]
        response = aws_client.fis.stop_experiment(id=experiment_id)
        assert response["ResponseMetadata"]["HTTPStatusCode"] == 200
        assert "experiment" in response
        experiment = response["experiment"]
        assert _does_experiment_match_request_and_template(
            experiment,
            start_experiment_request,
            experiment_template,
        )
        assert "id" in experiment
        assert experiment["id"] == experiment_id
        assert "state" in experiment
        assert "status" in experiment["state"]
        assert experiment["state"]["status"] == "stopped"

    @markers.aws.unknown
    def test_idempotency_of_start_experiment(
        self, create_experiment_template, start_experiment, aws_client
    ):
        experiment_template = create_experiment_template()["experimentTemplate"]
        experiment_template_id = experiment_template["id"]
        # Can't use a fixed token, as tests are not isolated from each other.
        first_client_token = str(uuid.uuid4())
        start_first_experiment_request = {
            "experimentTemplateId": experiment_template_id,
            "clientToken": first_client_token,
        }
        experiments_count = _get_experiments_count(aws_client.fis)
        response = start_experiment(start_first_experiment_request)
        assert _get_experiments_count(aws_client.fis) == experiments_count + 1
        assert "experiment" in response
        assert _does_experiment_match_request_and_template(
            response["experiment"], start_first_experiment_request, experiment_template
        )
        first_experiment_id = response["experiment"]["id"]

        # Supposed to get the same experiment without creating a new one.
        response = start_experiment(start_first_experiment_request)
        assert _get_experiments_count(aws_client.fis) == experiments_count + 1
        assert "experiment" in response
        assert _does_experiment_match_request_and_template(
            response["experiment"], start_first_experiment_request, experiment_template
        )
        assert response["experiment"]["id"] == first_experiment_id

        # A change of the token should result in a new experiment.
        second_client_token = first_client_token + " and something else"
        start_second_experiment_request = start_first_experiment_request.copy()
        start_second_experiment_request["clientToken"] = second_client_token
        response = start_experiment(start_second_experiment_request)
        assert _get_experiments_count(aws_client.fis) == experiments_count + 2
        assert "experiment" in response
        assert _does_experiment_match_request_and_template(
            response["experiment"], start_first_experiment_request, experiment_template
        )
        assert response["experiment"]["id"] != first_experiment_id

    @pytest.mark.skip(
        reason="FIXME. Flaky. See discussion at https://www.notion.so/localstack/tests-integration-test_ec2-9c1b12b20c2c42ee92fbc3a149a492a5 for more context"
    )
    @markers.aws.unknown
    def test_action_ec2_stop_instances(self, ec2_test_ami, start_experiment, aws_client):
        def _check_status(status):
            response = aws_client.ec2.describe_instance_status(InstanceIds=[instance_id])
            assert response["InstanceStatuses"][0]["InstanceState"]["Name"] == status

        # Have to use tags unique to the testing library, as tests are not isolated, so if two tests use the same
        # tags - the results might be weird, like code failing when a terminate_instances test is trying to terminate
        # a stopped instance.
        tag_name = "test_action_ec2_stop_instances test tag"
        tag_value = "test_action_ec2_stop_instances test value"
        tags_for_ec2_instance = [
            {"ResourceType": "instance", "Tags": [{"Key": tag_name, "Value": tag_value}]}
        ]
        tags_for_experiment_target = {tag_name: tag_value}

        # run instance and wait until status is "running"
        response = aws_client.ec2.run_instances(
            ImageId=ec2_test_ami[0],
            MinCount=1,
            MaxCount=1,
            TagSpecifications=tags_for_ec2_instance,
        )
        instance_id = response["Instances"][0]["InstanceId"]
        retry(lambda: _check_status("running"), sleep=1, retries=10)

        experiment_template = {
            "actions": {
                "StopInstance": {
                    "actionId": "aws:ec2:stop-instances",
                    "targets": {"Instances": "InstancesToStop"},
                    "description": "stop instances",
                },
            },
            "targets": {
                "InstancesToStop": {
                    "resourceType": "aws:ec2:instance",
                    "resourceTags": tags_for_experiment_target,
                    "selectionMode": "COUNT(1)",
                }
            },
            "description": "template for a test action",
            "stopConditions": [{"source": "none"}],
            "roleArn": "arn:aws:iam:123456789012:role/ExperimentRole",
        }
        start_experiment(template_request=experiment_template)
        # wait until the status of the EC2 instance is "stopped"
        retry(lambda: _check_status("stopped"), sleep=1, retries=10)

    @pytest.mark.skip(
        reason="FIXME. Flaky. See discussion at https://www.notion.so/localstack/tests-integration-test_ec2-9c1b12b20c2c42ee92fbc3a149a492a5 for more context"
    )
    @markers.aws.unknown
    def test_action_ec2_terminate_instances(self, ec2_test_ami, start_experiment, aws_client):
        def _check_status(status):
            response = aws_client.ec2.describe_instance_status(InstanceIds=[instance_id])
            assert response["InstanceStatuses"][0]["InstanceState"]["Name"] == status

        # Have to use tags unique to the testing library, as tests are not isolated, so if two tests use the same
        # tags - the results might be weird, like code failing when a terminate_instances test is trying to terminate
        # a stopped instance.
        tag_name = "test_action_ec2_terminate_instances test tag"
        tag_value = "test_action_ec2_terminate_instances test value"
        tags_for_ec2_instance = [
            {"ResourceType": "instance", "Tags": [{"Key": tag_name, "Value": tag_value}]}
        ]
        tags_for_experiment_target = {tag_name: tag_value}

        response = aws_client.ec2.run_instances(
            ImageId=ec2_test_ami[0],
            MinCount=1,
            MaxCount=1,
            TagSpecifications=tags_for_ec2_instance,
        )
        instance_id = response["Instances"][0]["InstanceId"]
        retry(lambda: _check_status("running"), sleep=1, retries=10)

        experiment_template = {
            "actions": {
                "StopInstance": {
                    "actionId": "aws:ec2:terminate-instances",
                    "targets": {"Instances": "InstancesToTerminate"},
                    "description": "terminate instances",
                },
            },
            "targets": {
                "InstancesToTerminate": {
                    "resourceType": "aws:ec2:instance",
                    "resourceTags": tags_for_experiment_target,
                    "selectionMode": "COUNT(1)",
                }
            },
            "description": "template for a test action",
            "stopConditions": [{"source": "none"}],
            "roleArn": "arn:aws:iam:123456789012:role/ExperimentRole",
        }
        start_experiment(template_request=experiment_template)
        # wait until the status of the EC2 instance is "stopped"
        retry(lambda: _check_status("terminated"), sleep=1, retries=10)

    @markers.aws.only_localstack
    @pytest.mark.skip(
        reason="FIXME. Flaky. See discussion at https://www.notion.so/localstack/tests-integration-test_ec2-9c1b12b20c2c42ee92fbc3a149a492a5 for more context"
    )
    def test_action_ssm_send_command(
        self,
        ec2_test_ami,
        start_experiment,
        monkeypatch,
        aws_client,
        account_id,
        region_name,
    ):
        def _check_status(status):
            response = aws_client.ec2.describe_instance_status(InstanceIds=[instance_id])
            assert response["InstanceStatuses"][0]["InstanceState"]["Name"] == status

        # Have to use tags unique to the testing library, as tests are not isolated, so if two tests use the same
        # tags - the results might be weird, like code failing when a terminate_instances test is trying to terminate
        # a stopped instance.
        tag_name = "test_action_ssm_send_command tag name"
        tag_value = "test_action_ssm_send_command tag value"
        tags_for_ec2_instance = [
            {"ResourceType": "instance", "Tags": [{"Key": tag_name, "Value": tag_value}]}
        ]
        tags_for_experiment_target = {tag_name: tag_value}

        response = aws_client.ec2.run_instances(
            ImageId=ec2_test_ami[0],
            MinCount=1,
            MaxCount=1,
            TagSpecifications=tags_for_ec2_instance,
        )
        instance_id = response["Instances"][0]["InstanceId"]
        retry(lambda: _check_status("running"), sleep=1, retries=10)

        document_arn = "arn:aws:ssm:region::document/AWSFIS-Run-CPU-Stress"
        experiment_template = {
            "actions": {
                "runCpuStress": {
                    "actionId": "aws:ssm:send-command",
                    "parameters": {
                        "documentArn": document_arn,
                        "documentParameters": '{"DurationSeconds": "120"}',
                    },
                    "targets": {"Instances": "testInstance"},
                }
            },
            "targets": {
                "testInstance": {
                    "resourceType": "aws:ec2:instance",
                    "resourceTags": tags_for_experiment_target,
                    "selectionMode": "COUNT(1)",
                }
            },
            "description": "template for a test action",
            "stopConditions": [{"source": "none"}],
            "roleArn": "arn:aws:iam:123456789012:role/ExperimentRole",
        }
        start_experiment(template_request=experiment_template)

        def _check_command_received():
            commands = ssm_backends[account_id][region_name].get_commands_by_instance_id(
                instance_id
            )
            assert commands
            assert commands[-1].document_name == document_arn
            assert commands[-1].parameters.get("DurationSeconds")

        retry(_check_command_received, retries=7, sleep=1)

    @markers.aws.only_localstack
    def test_action_rds_reboot_db_instances(
        self, rds_create_db_instance, start_experiment, monkeypatch, aws_client
    ):
        # Note: this test will only work when running in Docker (requires some Postgres extensions for the RDS DB)

        # "self" here refers to the "self" argument for DBBackendPostgres.reboot_db_instance we monkeypatch with this
        # _reboot_db_instance function, has nothing to do with the test class itself.
        def _reboot_db_instance(self, instance, *args, **kwargs):
            reboots.append(instance)

        reboots = []
        db_engine = "postgres"
        db_id = f"db-{short_uid()}"

        # note: currently implementing this as a whitebox test, until RDS DB reboots are fully available
        monkeypatch.setattr(DBBackendPostgres, "reboot_db_instance", _reboot_db_instance)

        response = rds_create_db_instance(
            DBInstanceIdentifier=db_id, DBInstanceClass="db.m6g.large", Engine=db_engine
        )
        instance_arn = response["DBInstanceArn"]

        experiment_template = {
            "actions": {
                "StopInstance": {
                    "actionId": "aws:rds:reboot-db-instances",
                    "targets": {"Instances": "InstancesToReboot"},
                    "description": "reboot instances",
                },
            },
            "targets": {
                "InstancesToReboot": {
                    "resourceType": "aws:ec2:instance",
                    "resourceArns": [instance_arn],
                    "selectionMode": "COUNT(1)",
                }
            },
            "description": "template for a test action",
            "stopConditions": [{"source": "none"}],
            "roleArn": "arn:aws:iam:123456789012:role/ExperimentRole",
        }
        start_experiment(template_request=experiment_template)

        def _check_db_reboot():
            assert reboots
            assert reboots[0]["DBInstanceArn"] == instance_arn

        retry(_check_db_reboot, retries=7, sleep=1)

    # Tests if pre-configured API fault implementations work.
    # KMS ListKeys is used here just because we had to use something. Can replace with any other call to any service
    # as long as this tests GenericAPIErrorAction in actions.py.
    @markers.aws.only_localstack
    def test_api_injection_fault_action(self, start_experiment, aws_client):
        response = aws_client.kms.list_keys()
        assert response["ResponseMetadata"]["HTTPStatusCode"] == 200

        experiment_template = {
            "actions": {
                "Some test action": {
                    "actionId": "localstack:kms:inject-api-internal-error",
                    "parameters": {"percentage": "100"},
                }
            },
            "description": "template for a test action",
            "stopConditions": [{"source": "none"}],
            "roleArn": "arn:aws:iam:123456789012:role/ExperimentRole",
        }
        experiment_id = start_experiment(template_request=experiment_template)["experiment"]["id"]

        def _check_kms_fails():
            try:
                aws_client.kms.list_keys()
                # if we reach this then the request has succeeded
                assert False
            except Exception as e:
                assert "InternalError" in str(e)
                assert "Failing as per Fault Injection Simulator configuration" in str(e)

        retry(_check_kms_fails, retries=7, sleep=1)

        aws_client.fis.stop_experiment(id=experiment_id)

        def _check_kms_succeeds():
            response = aws_client.kms.list_keys()
            assert response["ResponseMetadata"]["HTTPStatusCode"] == 200

        retry(_check_kms_succeeds, retries=7, sleep=1)

    @markers.aws.only_localstack
    def test_api_injection_parametrized_exception(self, start_experiment, aws_client):
        response = aws_client.kms.list_keys()
        assert response["ResponseMetadata"]["HTTPStatusCode"] == 200

        exception_name = "SomeVerySpecificException"
        experiment_template = _get_api_faults_template_with_parameter({"exception": exception_name})
        experiment_id = start_experiment(template_request=experiment_template)["experiment"]["id"]

        def _check_kms_fails():
            try:
                aws_client.kms.list_keys()
                # if we reach this then the request has succeeded
                assert False
            except Exception as e:
                assert exception_name in str(e)
                assert "Failing as per Fault Injection Simulator configuration" in str(e)

        retry(_check_kms_fails, retries=7, sleep=1)

        aws_client.fis.stop_experiment(id=experiment_id)

        def _check_kms_succeeds():
            response = aws_client.kms.list_keys()
            assert response["ResponseMetadata"]["HTTPStatusCode"] == 200

        retry(_check_kms_succeeds, retries=7, sleep=1)

    @markers.aws.only_localstack
    def test_api_injection_parametrized_service(self, start_experiment, aws_client):
        # We use both ListKeys and ListAliases to make sure that FIS disables both of them with a configuration,
        # that is supposed to disable the service as a whole. The same time we use SQS ListQueues to make sure that
        # SQL still works even when KMS stops working.
        response = aws_client.kms.list_keys()
        assert response["ResponseMetadata"]["HTTPStatusCode"] == 200
        response = aws_client.kms.list_aliases()
        assert response["ResponseMetadata"]["HTTPStatusCode"] == 200
        response = aws_client.sqs.list_queues()
        assert response["ResponseMetadata"]["HTTPStatusCode"] == 200

        experiment_template = _get_api_faults_template_with_parameter({"service": "kms"})
        experiment_id = start_experiment(template_request=experiment_template)["experiment"]["id"]

        def _check_operation_fails(operation):
            try:
                operation()
                # if we reach this then the request has succeeded
                assert False
            except Exception as e:
                assert "InternalError" in str(e)
                assert "Failing as per Fault Injection Simulator configuration" in str(e)

        retry(_check_operation_fails, retries=7, sleep=1, operation=aws_client.kms.list_keys)
        retry(_check_operation_fails, retries=7, sleep=1, operation=aws_client.kms.list_aliases)
        response = aws_client.sqs.list_queues()
        assert response["ResponseMetadata"]["HTTPStatusCode"] == 200

        aws_client.fis.stop_experiment(id=experiment_id)

        def _check_kms_succeeds():
            response = aws_client.kms.list_keys()
            assert response["ResponseMetadata"]["HTTPStatusCode"] == 200
            response = aws_client.kms.list_aliases()
            assert response["ResponseMetadata"]["HTTPStatusCode"] == 200

        retry(_check_kms_succeeds, retries=7, sleep=1)
        response = aws_client.sqs.list_queues()
        assert response["ResponseMetadata"]["HTTPStatusCode"] == 200

    @markers.aws.only_localstack
    def test_api_injection_parametrized_operation(self, start_experiment, aws_client):
        response = aws_client.kms.list_keys()
        assert response["ResponseMetadata"]["HTTPStatusCode"] == 200
        response = aws_client.kms.list_aliases()
        assert response["ResponseMetadata"]["HTTPStatusCode"] == 200

        experiment_template = _get_api_faults_template_with_parameter(
            {"service": "kms", "operation": "ListKeys"}
        )
        experiment_id = start_experiment(template_request=experiment_template)["experiment"]["id"]

        def _check_operation_fails(operation):
            try:
                operation()
                # if we reach this then the request has succeeded
                assert False
            except Exception as e:
                assert "InternalError" in str(e)
                assert "Failing as per Fault Injection Simulator configuration" in str(e)

        retry(_check_operation_fails, retries=7, sleep=1, operation=aws_client.kms.list_keys)
        response = aws_client.kms.list_aliases()
        assert response["ResponseMetadata"]["HTTPStatusCode"] == 200

        aws_client.fis.stop_experiment(id=experiment_id)

        def _check_kms_succeeds():
            response = aws_client.kms.list_keys()
            assert response["ResponseMetadata"]["HTTPStatusCode"] == 200
            response = aws_client.kms.list_aliases()
            assert response["ResponseMetadata"]["HTTPStatusCode"] == 200

        retry(_check_kms_succeeds, retries=7, sleep=1)
        response = aws_client.kms.list_aliases()
        assert response["ResponseMetadata"]["HTTPStatusCode"] == 200

    @markers.aws.only_localstack
    def test_api_injection_parametrized_region(
        self, start_experiment, aws_client_factory, aws_client
    ):
        region_to_fail = "us-west-1"
        region_to_compare_to = "eu-central-1"
        kms_client_for_region_to_fail = aws_client_factory(region_name=region_to_fail).kms
        kms_client_for_region_to_compare_to = aws_client_factory(
            region_name=region_to_compare_to
        ).kms
        response = kms_client_for_region_to_fail.list_keys()
        assert response["ResponseMetadata"]["HTTPStatusCode"] == 200
        response = kms_client_for_region_to_compare_to.list_keys()
        assert response["ResponseMetadata"]["HTTPStatusCode"] == 200

        experiment_template = _get_api_faults_template_with_parameter({"region": region_to_fail})
        experiment_id = start_experiment(template_request=experiment_template)["experiment"]["id"]

        def _check_kms_fails():
            try:
                kms_client_for_region_to_fail.list_keys()
                # if we reach this then the request has succeeded
                assert False
            except Exception as e:
                assert "InternalError" in str(e)
                assert "Failing as per Fault Injection Simulator configuration" in str(e)

        retry(_check_kms_fails, retries=7, sleep=1)
        response = kms_client_for_region_to_compare_to.list_keys()
        assert response["ResponseMetadata"]["HTTPStatusCode"] == 200

        aws_client.fis.stop_experiment(id=experiment_id)

        def _check_kms_succeeds():
            response = kms_client_for_region_to_fail.list_keys()
            assert response["ResponseMetadata"]["HTTPStatusCode"] == 200

        retry(_check_kms_succeeds, retries=7, sleep=1)
        response = kms_client_for_region_to_compare_to.list_keys()
        assert response["ResponseMetadata"]["HTTPStatusCode"] == 200

    @markers.aws.only_localstack
    def test_api_failure_with_latency(self, start_experiment, aws_client):
        DEFAULT_LATENCY_MS = 3000
        kms_list_keys_operation = aws_client.kms.list_keys
        s3_list_buckets_operation = aws_client.s3.list_buckets

        def _return_api_call_response_time(operation) -> int:
            start_time = time.time()
            response = operation()
            end_time = time.time()
            response_time_in_ms = (end_time - start_time) * 1000
            assert response["ResponseMetadata"]["HTTPStatusCode"] == 200
            return response_time_in_ms

        def _check_operations_succeed_without_latency() -> None:
            kms_list_keys_response_time = _return_api_call_response_time(
                operation=kms_list_keys_operation
            )
            s3_list_buckets_response_time = _return_api_call_response_time(
                operation=s3_list_buckets_operation
            )
            # pass until its less than DEFAULT_LATENCY_MS
            assert kms_list_keys_response_time < DEFAULT_LATENCY_MS
            assert s3_list_buckets_response_time < DEFAULT_LATENCY_MS

        def _check_kms_list_keys_fails_with_latency() -> None:
            try:
                start_time = time.time()
                kms_list_keys_operation()
                # if we reach this then the request has succeeded
                assert False
            except Exception as e:
                end_time = time.time()
                response_time_in_ms = (end_time - start_time) * 1000
                assert response_time_in_ms > DEFAULT_LATENCY_MS
                assert "InternalError" in str(e)
                assert "Failing as per Fault Injection Simulator configuration" in str(e)

        _check_operations_succeed_without_latency()

        # KMS's ListKeys should fail with latency
        # S3's ListBuckets should succeed with latency
        experiment_template = {
            "actions": {
                "kmsLatency": {
                    "actionId": "localstack:generic:latency",
                    "parameters": {
                        "service": "kms",
                        "operation": "ListKeys",
                        "latencyMilliseconds": str(DEFAULT_LATENCY_MS),
                    },
                },
                "internalServerError": {
                    "actionId": "localstack:generic:api-error",
                    "parameters": {
                        "service": "kms",
                        "operation": "ListKeys",
                        "percentage": "100",
                    },
                },
                "s3Latency": {
                    "actionId": "localstack:generic:latency",
                    "parameters": {
                        "service": "s3",
                        "operation": "ListBuckets",
                        "latencyMilliseconds": str(DEFAULT_LATENCY_MS),
                    },
                },
            },
            "description": "template for a test action",
            "stopConditions": [{"source": "none"}],
            "roleArn": "arn:aws:iam:123456789012:role/ExperimentRole",
        }
        experiment_id = start_experiment(template_request=experiment_template)["experiment"]["id"]
        retry(_check_kms_list_keys_fails_with_latency, retries=5, sleep=1)
        s3_list_buckets_response_time = _return_api_call_response_time(
            operation=s3_list_buckets_operation
        )
        assert s3_list_buckets_response_time > DEFAULT_LATENCY_MS

        aws_client.fis.stop_experiment(id=experiment_id)

        _check_operations_succeed_without_latency()
