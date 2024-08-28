import pytest


@pytest.fixture
def state_machine_get_arn(aws_client):
    def _machine_arn(state_machine_name: str) -> str | None:
        if state_machines := aws_client.stepfunctions.list_state_machines()["stateMachines"]:
            arn = [m["stateMachineArn"] for m in state_machines if m["name"] == state_machine_name][
                0
            ]
        return arn

    return _machine_arn
