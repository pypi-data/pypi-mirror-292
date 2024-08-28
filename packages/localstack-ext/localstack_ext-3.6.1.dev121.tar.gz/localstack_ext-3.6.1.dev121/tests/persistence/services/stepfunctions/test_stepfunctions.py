import json

import pytest
from localstack.utils.json import clone
from localstack.utils.strings import short_uid


@pytest.mark.skip(reason="Temporarily disabled, fix with v2!")
def test_stepfunctions(persistence_validations, snapshot, aws_client):
    definition = {
        "Comment": "A description of my state machine",
        "StartAt": "Lambda Invoke",
        "States": {
            "Lambda Invoke": {
                "Type": "Task",
                "Resource": "arn:aws:states:::lambda:invoke",
                "OutputPath": "$.Payload",
                "Parameters": {"Payload.$": "$", "FunctionName": "test"},
                "Retry": [
                    {
                        "ErrorEquals": [
                            "Lambda.ServiceException",
                            "Lambda.AWSLambdaException",
                            "Lambda.SdkClientException",
                        ],
                        "IntervalSeconds": 2,
                        "MaxAttempts": 6,
                        "BackoffRate": 2,
                    }
                ],
                "End": True,
            }
        },
    }
    machine_name = f"sfn-{short_uid()}"
    state_machine_arn = aws_client.stepfunctions.create_state_machine(
        name=machine_name,
        loggingConfiguration={},
        definition=clone(json.dumps(definition)),
        roleArn="arn:aws:iam::000000000000:role/sfn_role",
    )["stateMachineArn"]

    def validate():
        snapshot.match(
            "sfn_describe_state_machine",
            aws_client.stepfunctions.describe_state_machine(stateMachineArn=state_machine_arn),
        )

    persistence_validations.register(validate)
