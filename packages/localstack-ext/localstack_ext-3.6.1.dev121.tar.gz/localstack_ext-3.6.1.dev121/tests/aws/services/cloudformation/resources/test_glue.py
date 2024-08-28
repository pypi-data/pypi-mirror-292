import os

import pytest
from localstack.testing.pytest import markers
from localstack.utils.strings import short_uid
from localstack_snapshot.snapshots.transformer import SortingTransformer


@pytest.fixture
def deploy_glue_schema(deploy_cfn_template):
    def _deploy_glue_schema(registry_name, schema_name):
        template_path = os.path.join(
            os.path.dirname(__file__), "../../../templates/glue_schema.yml"
        )
        stack = deploy_cfn_template(
            template_path=template_path,
            parameters={"RegistryName": registry_name, "SchemaName": schema_name},
        )
        return stack

    return _deploy_glue_schema


@markers.aws.validated
@markers.snapshot.skip_snapshot_verify(
    paths=[
        "$..Job.AllocatedCapacity",
        "$..Job.Command.PythonVersion",
        "$..Job.ExecutionProperty",
        "$..Job.GlueVersion",
        "$..Job.MaxCapacity",
        "$..Job.MaxRetries",
        "$..Job.Timeout",
    ]
)
def test_job(deploy_cfn_template, snapshot, aws_client):
    snapshot.add_transformer(snapshot.transform.resource_name())
    snapshot.add_transformer(snapshot.transform.iam_api())
    snapshot.add_transformer(snapshot.transform.key_value("Role", "role"))
    snapshot.add_transformer(snapshot.transform.key_value("JobRef", "job"))
    snapshot.add_transformer(snapshot.transform.cloudformation_api())
    snapshot.add_transformer(SortingTransformer("StackResources", lambda x: x["LogicalResourceId"]))

    job_name = f"job-{short_uid()}"

    template_path = os.path.join(os.path.dirname(__file__), "../../../templates/glue_job.yml")
    stack = deploy_cfn_template(template_path=template_path, parameters={"JobName": job_name})

    snapshot.match("stack_outputs", stack.outputs)

    description = aws_client.cloudformation.describe_stack_resources(StackName=stack.stack_name)
    snapshot.match("stack_resource_descriptions", description)

    job = aws_client.glue.get_job(JobName=job_name)
    snapshot.match("job", job)


@markers.aws.validated
@markers.snapshot.skip_snapshot_verify(
    paths=[
        "$..Database.CreateTableDefaultPermissions",
        "$..Database.Parameters",
    ]
)
def test_database(deploy_cfn_template, snapshot, aws_client):
    snapshot.add_transformer(snapshot.transform.resource_name())
    snapshot.add_transformer(snapshot.transform.key_value("Name", "database-name"))
    snapshot.add_transformer(snapshot.transform.cloudformation_api())

    database_name = f"database-{short_uid()}"

    template_path = os.path.join(os.path.dirname(__file__), "../../../templates/glue_database.yml")
    stack = deploy_cfn_template(
        template_path=template_path, parameters={"DatabaseName": database_name}
    )

    snapshot.match("stack_outputs", stack.outputs)

    description = aws_client.cloudformation.describe_stack_resources(StackName=stack.stack_name)
    snapshot.match("stack_resource_descriptions", description["StackResources"])

    database = aws_client.glue.get_database(Name=database_name)
    snapshot.match("database", database)


@markers.aws.validated
@markers.snapshot.skip_snapshot_verify(paths=["$..GrokClassifier.Version"])
def test_classifier(deploy_cfn_template, snapshot, aws_client):
    snapshot.add_transformer(snapshot.transform.resource_name())
    snapshot.add_transformer(snapshot.transform.key_value("Name", "classifier-name"))
    snapshot.add_transformer(snapshot.transform.cloudformation_api())

    classifier_name = f"classifier-{short_uid()}"

    template_path = os.path.join(
        os.path.dirname(__file__), "../../../templates/glue_classifier.yml"
    )
    stack = deploy_cfn_template(
        template_path=template_path, parameters={"ClassifierName": classifier_name}
    )

    snapshot.match("stack_outputs", stack.outputs)

    description = aws_client.cloudformation.describe_stack_resources(StackName=stack.stack_name)
    snapshot.match("stack_resource_descriptions", description["StackResources"])

    classifier = aws_client.glue.get_classifier(Name=classifier_name)
    snapshot.match("classifier", classifier["Classifier"])


@markers.aws.validated
@markers.snapshot.skip_snapshot_verify(
    paths=[
        "$..CreatedBy",
        "$..IsRegisteredWithLakeFormation",
        "$..IsMultiDialectView",
        "$..VersionId",
    ]
)
def test_table(deploy_cfn_template, snapshot, aws_client):
    snapshot.add_transformer(snapshot.transform.resource_name())
    snapshot.add_transformer(snapshot.transform.key_value("DatabaseName", "database-name"))
    snapshot.add_transformer(snapshot.transform.key_value("Name", "table-name"))
    snapshot.add_transformer(snapshot.transform.cloudformation_api())

    database_name = f"database-{short_uid()}"
    table_name = f"table-{short_uid()}"

    template_path = os.path.join(
        os.path.dirname(__file__), "../../../templates/glue_database_table.yml"
    )
    stack = deploy_cfn_template(
        template_path=template_path,
        parameters={"DatabaseName": database_name, "TableName": table_name},
    )

    snapshot.match("stack_outputs", stack.outputs)

    description = aws_client.cloudformation.describe_stack_resources(StackName=stack.stack_name)
    snapshot.match("stack_resource_descriptions", description["StackResources"])

    table = aws_client.glue.get_table(
        DatabaseName=database_name, Name=table_name, CatalogId=stack.outputs["CatalogId"]
    )
    snapshot.match("table", table["Table"])


@markers.aws.validated
def test_workflow(deploy_cfn_template, snapshot, aws_client):
    snapshot.add_transformer(snapshot.transform.resource_name())
    snapshot.add_transformer(snapshot.transform.key_value("Name", "workflow-name"))
    snapshot.add_transformer(snapshot.transform.cloudformation_api())

    workflow_name = f"workflow-{short_uid()}"

    template_path = os.path.join(os.path.dirname(__file__), "../../../templates/glue_workflow.yml")
    stack = deploy_cfn_template(
        template_path=template_path,
        parameters={"WorkflowName": workflow_name},
    )

    snapshot.match("stack_outputs", stack.outputs)

    description = aws_client.cloudformation.describe_stack_resources(StackName=stack.stack_name)
    snapshot.match("stack_resource_descriptions", description["StackResources"])

    workflow = aws_client.glue.get_workflow(Name=workflow_name)
    snapshot.match("workflow", workflow["Workflow"])


@markers.aws.validated
def test_trigger(deploy_cfn_template, snapshot, aws_client):
    snapshot.add_transformer(snapshot.transform.resource_name())
    snapshot.add_transformer(snapshot.transform.key_value("Name", "trigger-name"))
    snapshot.add_transformer(snapshot.transform.cloudformation_api())

    trigger_name = f"trigger-{short_uid()}"

    template_path = os.path.join(os.path.dirname(__file__), "../../../templates/glue_trigger.yml")
    stack = deploy_cfn_template(
        template_path=template_path,
        parameters={"TriggerName": trigger_name},
    )
    snapshot.match("stack_outputs", stack.outputs)

    description = aws_client.cloudformation.describe_stack_resources(StackName=stack.stack_name)
    snapshot.match("stack_resource_description", description["StackResources"])

    trigger = aws_client.glue.get_trigger(Name=trigger_name)
    snapshot.match("trigger", trigger["Trigger"])


@markers.aws.validated
def test_registry(deploy_cfn_template, snapshot, aws_client):
    snapshot.add_transformer(snapshot.transform.resource_name())
    snapshot.add_transformer(snapshot.transform.key_value("Name", "registry-name"))
    snapshot.add_transformer(snapshot.transform.cloudformation_api())

    registry_name = f"registry-{short_uid()}"

    template_path = os.path.join(os.path.dirname(__file__), "../../../templates/glue_registry.yml")
    stack = deploy_cfn_template(
        template_path=template_path,
        parameters={"RegistryName": registry_name},
    )
    snapshot.match("stack_outputs", stack.outputs)

    description = aws_client.cloudformation.describe_stack_resources(StackName=stack.stack_name)
    snapshot.match("stack_resource_description", description["StackResources"])

    registry = aws_client.glue.get_registry(RegistryId={"RegistryName": registry_name})
    snapshot.match("registry", registry)


@markers.aws.validated
def test_schema(deploy_glue_schema, snapshot, aws_client):
    snapshot.add_transformer(snapshot.transform.resource_name())
    snapshot.add_transformer(snapshot.transform.key_value("Name", "schema-name"))
    snapshot.add_transformer(snapshot.transform.cloudformation_api())

    registry_name = f"registry-{short_uid()}"
    schema_name = f"schema-{short_uid()}"

    stack = deploy_glue_schema(registry_name, schema_name)
    snapshot.match("stack_outputs", stack.outputs)

    description = aws_client.cloudformation.describe_stack_resources(StackName=stack.stack_name)
    snapshot.match("stack_resource_description", description["StackResources"])

    schema = aws_client.glue.get_schema(
        SchemaId={
            "SchemaName": schema_name,
            "RegistryName": registry_name,
        }
    )
    snapshot.match("schema", schema)


@markers.aws.validated
def test_schema_version(deploy_glue_schema, snapshot, aws_client):
    snapshot.add_transformer(snapshot.transform.resource_name())
    snapshot.add_transformer(snapshot.transform.key_value("VersionId", "version-id"))
    snapshot.add_transformer(snapshot.transform.cloudformation_api())

    registry_name = f"registry-{short_uid()}"
    schema_name = f"schema-{short_uid()}"

    stack = deploy_glue_schema(registry_name, schema_name)
    snapshot.match("stack_outputs", stack.outputs)

    description = aws_client.cloudformation.describe_stack_resources(StackName=stack.stack_name)
    snapshot.match("stack_resource_description", description["StackResources"])

    schema_version = aws_client.glue.get_schema_version(
        SchemaVersionId=stack.outputs["SchemaVersionRef"],
    )
    snapshot.match("schema_version", schema_version)


@markers.aws.validated
@markers.snapshot.skip_snapshot_verify(paths=["$..MetadataInfoMap.foo.OtherMetadataValueList"])
def test_schema_version_metadata(deploy_glue_schema, snapshot, aws_client):
    snapshot.add_transformer(snapshot.transform.resource_name())
    snapshot.add_transformer(snapshot.transform.key_value("Key", "key"))
    snapshot.add_transformer(snapshot.transform.cloudformation_api())

    registry_name = f"registry-{short_uid()}"
    schema_name = f"schema-{short_uid()}"

    stack = deploy_glue_schema(registry_name, schema_name)
    snapshot.match("stack_outputs", stack.outputs)

    description = aws_client.cloudformation.describe_stack_resources(StackName=stack.stack_name)
    snapshot.match("stack_resource_description", description["StackResources"])

    schema_version_metadata = aws_client.glue.query_schema_version_metadata(
        SchemaVersionId=stack.outputs["SchemaVersionRef"],
    )
    snapshot.match("schema_version_metadata", schema_version_metadata)


@markers.aws.validated
@markers.snapshot.skip_snapshot_verify(
    paths=["$..Connection.LastUpdatedBy", "$..Connection.LastUpdatedTime"]
)
def test_connection(deploy_cfn_template, snapshot, aws_client):
    snapshot.add_transformer(snapshot.transform.resource_name())
    snapshot.add_transformer(snapshot.transform.key_value("Name", "connection-name"))
    snapshot.add_transformer(snapshot.transform.cloudformation_api())

    connection_name = f"connection-{short_uid()}"

    template_path = os.path.join(
        os.path.dirname(__file__), "../../../templates/glue_connection.yml"
    )
    stack = deploy_cfn_template(
        template_path=template_path,
        parameters={
            "ConnectionName": connection_name,
            "SubnetId": "subnet-1234567890abcdef0",
            "SecurityGroupId": "sg-1234567890abcdef0",
        },
    )
    snapshot.match("stack_outputs", stack.outputs)

    description = aws_client.cloudformation.describe_stack_resources(StackName=stack.stack_name)
    snapshot.match("stack_resource_description", description["StackResources"])

    connection = aws_client.glue.get_connection(Name=connection_name)
    snapshot.match("connection", connection)
