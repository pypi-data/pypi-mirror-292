from localstack.pro.core.aws.api.fis import Experiment
from localstack.pro.core.services.fis.actions import ACTION_NAME_TO_CLASS, Action
from localstack.pro.core.services.fis.scheduler import (
    EmulatedExperimentScheduler,
)
from localstack.utils.strings import short_uid
from localstack.utils.sync import retry


class TestExperimentRunner:
    def test_run_experiment(self, monkeypatch):
        # define test action
        class TestAction(Action):
            def start(self):
                executed_actions.append(self.action)

        executed_actions = []
        action_id = short_uid()
        ACTION_NAME_TO_CLASS[action_id] = TestAction

        # define and start experiment
        scheduler = EmulatedExperimentScheduler()
        experiment = Experiment(id="exp123")
        experiment["actions"] = {"test": {"actionId": action_id}}
        account_id = "123456789"
        region = "us-west-1"
        scheduler.start_experiment(experiment, account_id, region)

        # assert that action was invoked
        def _check_executed():
            assert len(executed_actions) == 1

        retry(_check_executed, sleep=0.8, retries=7)

        # clean up
        scheduler.stop_experiment(experiment)
        ACTION_NAME_TO_CLASS.pop(action_id)
