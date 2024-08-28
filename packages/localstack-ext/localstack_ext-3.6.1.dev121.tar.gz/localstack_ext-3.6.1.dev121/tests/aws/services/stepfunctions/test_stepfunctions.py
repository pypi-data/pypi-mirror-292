import io
import json
from typing import Final

import pytest
from localstack.testing.pytest import markers
from localstack.testing.pytest.stepfunctions.utils import create_and_record_execution
from localstack.utils.strings import to_bytes

from tests.aws.services.glue.conftest import skip_bigdata_in_ci
from tests.aws.services.stepfunctions.template.integratisons.integration_template_loader import (
    IntegrationTemplate as IT,
)
from tests.aws.transformer_utility_ext import TransformerUtilityExt

_GLUE_JOB_COMMAND_BASE: Final[str] = "print('GLUE_JOB_COMMAND_BASE')"
_GLUE_JOB_COMMAND_EXCEPTION: Final[str] = "raise RuntimeException('GLUE_JOB_COMMAND_EXCEPTION')"


@markers.snapshot.skip_snapshot_verify(
    paths=[
        "$..loggingConfiguration",
        "$..tracingConfiguration",
        "$..SdkHttpMetadata",
        "$..SdkResponseMetadata",
        # The Glue provider appears to start counting attempts from 1, not 0.
        "$..Attempt",
        # The Glue provider does not return the expected error messages.
        "$..cause",
        # The Glue provider appears to not return the following fields for GetJonRun actions.
        "$..AllocatedCapacity",
        "$..Timeout",
        "$..PredecessorRuns",
        "$..MaxCapacity",
        "$..LogGroupName",
        "$..ExecutionTime",
        "$..CompletedOn",
        "$..LastModifiedOn",
        "$..StartedOn",
    ]
)
class TestBaseScenarios:
    @skip_bigdata_in_ci
    @markers.aws.validated
    @pytest.mark.parametrize(
        "state_machine_template,command",
        [
            (IT.GLUE_START_JOB_RUN, _GLUE_JOB_COMMAND_BASE),
            (IT.GLUE_START_JOB_RUN_SYNC, _GLUE_JOB_COMMAND_BASE),
            (IT.GLUE_START_JOB_RUN, _GLUE_JOB_COMMAND_EXCEPTION),
            (IT.GLUE_START_JOB_RUN_SYNC, _GLUE_JOB_COMMAND_EXCEPTION),
        ],
        ids=[
            "GLUE_START_JOB_RUN__BASE_COMMAND",
            "GLUE_START_JOB_RUN_SYNC__BASE_COMMAND",
            "GLUE_START_JOB_RUN__EXCEPTION_COMMAND",
            "GLUE_START_JOB_RUN_SYNC__EXCEPTION_COMMAND",
        ],
    )
    def test_glue_start_job(
        self,
        aws_client,
        create_iam_role_for_sfn,
        create_state_machine,
        s3_create_bucket,
        sfn_glue_create_job,
        sfn_snapshot,
        state_machine_template,
        command,
    ):
        sfn_snapshot.add_transformer(TransformerUtilityExt.glue_api())

        bucket_name = s3_create_bucket()
        aws_client.s3.upload_fileobj(io.BytesIO(to_bytes(command)), bucket_name, "job.py")

        s3_url = f"s3://{bucket_name}/job.py"
        job_name = sfn_glue_create_job(Command={"Name": "pythonshell", "ScriptLocation": s3_url})

        template = IT.load_sfn_template(state_machine_template)
        definition = json.dumps(template)
        exec_input = json.dumps({"JobName": job_name})
        create_and_record_execution(
            aws_client.stepfunctions,
            create_iam_role_for_sfn,
            create_state_machine,
            sfn_snapshot,
            definition,
            exec_input,
        )

    @markers.aws.validated
    @pytest.mark.parametrize(
        "state_machine_template",
        [IT.GLUE_START_JOB_RUN, IT.GLUE_START_JOB_RUN_SYNC],
        ids=["GLUE_START_JOB_RUN", "GLUE_START_JOB_RUN_SYNC"],
    )
    def test_glue_start_job_no_such_job(
        self,
        aws_client,
        create_iam_role_for_sfn,
        create_state_machine,
        s3_create_bucket,
        sfn_glue_create_job,
        sfn_snapshot,
        state_machine_template,
    ):
        sfn_snapshot.add_transformer(TransformerUtilityExt.glue_api())

        bucket_name = s3_create_bucket()
        aws_client.s3.upload_fileobj(
            io.BytesIO(to_bytes(_GLUE_JOB_COMMAND_BASE)), bucket_name, "job.py"
        )

        s3_url = f"s3://{bucket_name}/job.py"
        job_name = sfn_glue_create_job(Command={"Name": "pythonshell", "ScriptLocation": s3_url})
        aws_client.glue.delete_job(JobName=job_name)

        template = IT.load_sfn_template(state_machine_template)
        definition = json.dumps(template)
        exec_input = json.dumps({"JobName": job_name})
        create_and_record_execution(
            aws_client.stepfunctions,
            create_iam_role_for_sfn,
            create_state_machine,
            sfn_snapshot,
            definition,
            exec_input,
        )
