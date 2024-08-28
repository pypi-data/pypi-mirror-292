import json
import os

from localstack.testing.pytest import markers
from localstack.utils.strings import short_uid


@markers.aws.validated
@markers.only_in_docker
def test_secretsmanager_target_attachment_maridab(deploy_cfn_template, aws_client, snapshot):
    snapshot.add_transformer(snapshot.transform.key_value("host"))
    snapshot.add_transformer(snapshot.transform.key_value("dbInstanceIdentifier"))
    snapshot.add_transformer(
        snapshot.transform.key_value("port", "<port>", reference_replacement=False)
    )
    snapshot.add_transformer(
        snapshot.transform.key_value("DB_PORT", "<port>", reference_replacement=False)
    )
    snapshot.add_transformer(snapshot.transform.key_value("password"))
    function_name = f"cfn-test-{short_uid()}"
    deployment = deploy_cfn_template(
        template_path=os.path.join(
            os.path.dirname(__file__), "../../../templates/rds_secretsmanager_lambda.yml"
        ),
        parameters={
            "FunctionName": function_name,
        },
        max_wait=6000,
    )
    secret_id = deployment.outputs["SecretId"]
    secret = aws_client.secretsmanager.get_secret_value(SecretId=secret_id)["SecretString"]
    secret = json.loads(secret)
    snapshot.match("db-secret", secret)

    environment = aws_client.lambda_.get_function(FunctionName=function_name)["Configuration"][
        "Environment"
    ]
    snapshot.match("deployed-function-env", environment)
