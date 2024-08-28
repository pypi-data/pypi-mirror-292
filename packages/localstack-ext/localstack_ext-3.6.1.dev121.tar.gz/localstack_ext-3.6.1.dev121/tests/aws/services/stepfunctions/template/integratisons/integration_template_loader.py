import os
from typing import Final

from tests.aws.services.stepfunctions.template.template_loader import TemplateLoader

_THIS_FOLDER: Final[str] = os.path.dirname(os.path.realpath(__file__))


class IntegrationTemplate(TemplateLoader):
    GLUE_START_JOB_RUN: Final[str] = os.path.join(
        _THIS_FOLDER, "statemachines/glue_start_job_run.json5"
    )
    GLUE_START_JOB_RUN_SYNC: Final[str] = os.path.join(
        _THIS_FOLDER, "statemachines/glue_start_job_run_sync.json5"
    )
