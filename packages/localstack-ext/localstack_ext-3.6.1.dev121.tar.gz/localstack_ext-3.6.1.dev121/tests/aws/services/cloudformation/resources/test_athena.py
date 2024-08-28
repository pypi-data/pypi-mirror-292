import os.path

from localstack.testing.pytest import markers


@markers.aws.validated
def test_athena(deploy_cfn_template, snapshot, aws_client):
    # Setup transformers
    snapshot.add_transformer(snapshot.transform.cloudformation_api())

    # Deploy the stack
    template_path = os.path.join(
        os.path.dirname(__file__), "../../../templates/athena_resources.yml"
    )
    stack = deploy_cfn_template(template_path=template_path)

    # Match the catalog
    catalog = aws_client.athena.get_data_catalog(Name=stack.outputs["DataCatalogNameOutput"])
    snapshot.match("get_data_catalog", catalog["DataCatalog"])

    # Match the named query
    named_query = aws_client.athena.get_named_query(
        NamedQueryId=stack.outputs["NamedQueryIdOutput"]
    )
    snapshot.match("get_named_query", named_query["NamedQuery"])

    # Match the work group
    work_group = aws_client.athena.get_work_group(WorkGroup=stack.outputs["WorkGroupNameOutput"])
    snapshot.match("get_work_group", work_group["WorkGroup"])
