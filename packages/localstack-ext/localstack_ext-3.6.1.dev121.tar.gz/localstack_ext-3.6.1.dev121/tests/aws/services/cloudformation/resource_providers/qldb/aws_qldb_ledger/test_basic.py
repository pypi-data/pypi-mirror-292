# LocalStack Resource Provider Scaffolding v2
import os

import pytest
from botocore.exceptions import ClientError
from localstack.testing.pytest import markers


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
        template_path = os.path.join(
            os.path.dirname(__file__),
            "templates/basic.yaml",
        )
        assert os.path.isfile(template_path)
        stack = deploy_cfn_template(
            template_path=template_path,
            parameters={
                # TODO: test the other permission
                "PermissionsMode": "ALLOW_ALL",
            },
        )
        snapshot.match("stack-outputs", stack.outputs)

        ledger_name = stack.outputs["LedgerRef"]
        snapshot.add_transformer(snapshot.transform.regex(ledger_name, "<ledger-name>"))

        res = aws_client.qldb.describe_ledger(Name=ledger_name)
        snapshot.match("describe-resource", res)

        # verify that the delete operation works
        stack.destroy()
        with pytest.raises(ClientError):
            aws_client.qldb.describe_ledger(Name=ledger_name)
