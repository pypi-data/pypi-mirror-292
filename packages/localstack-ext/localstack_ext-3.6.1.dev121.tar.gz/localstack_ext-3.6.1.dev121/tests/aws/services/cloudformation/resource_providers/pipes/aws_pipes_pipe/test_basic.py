# LocalStack Resource Provider Scaffolding v2
import os

import pytest
from botocore.exceptions import ClientError
from localstack.testing.pytest import markers

THIS_FOLDER = os.path.dirname(os.path.realpath(__file__))


class TestBasicCRD:
    @markers.aws.validated
    def test_black_box(self, deploy_cfn_template, aws_client, snapshot):
        """
        Simple test that
        - deploys a stack containing the resource
        - verifies that the resource has been created correctly by querying the service directly
        - deletes the stack ensuring that the delete operation has been implemented correctly
        - verifies that the resource no longer exists by querying the service directly
        """
        stack = deploy_cfn_template(
            template_path=os.path.join(THIS_FOLDER, "templates/basic.yaml"),
        )
        snapshot.match("stack-outputs", stack.outputs)

        pipe_name = stack.outputs["MyRef"]
        snapshot.add_transformer(snapshot.transform.regex(pipe_name, "<pipe-name>"))
        role_arn = stack.outputs["RoleName"]
        snapshot.add_transformer(snapshot.transform.regex(role_arn, "<role-name>"))
        source = stack.outputs["SourceQueueName"]
        snapshot.add_transformer(snapshot.transform.regex(source, "<source-queue-name>"))
        target = stack.outputs["TargetQueueName"]
        snapshot.add_transformer(snapshot.transform.regex(target, "<target-queue-name>"))

        describe_pipe_response = aws_client.pipes.describe_pipe(Name=pipe_name)
        snapshot.match("describe_pipe_response", describe_pipe_response)

        # verify that the delete operation works
        stack.destroy()

        with pytest.raises(ClientError) as e:
            aws_client.pipes.describe_pipe(Name=pipe_name)
        snapshot.match("descripe_pipe_exception_post_destroy", e.value.response)
