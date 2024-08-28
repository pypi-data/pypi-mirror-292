import pytest
from localstack.utils.strings import short_uid


@pytest.mark.skip(reason="currently broken")
def test_costexplorer_describe_cost_category(persistence_validations, snapshot, aws_client):
    def_name = f"d-{short_uid()}"
    rule_ver = "CostCategoryExpression.v1"
    rules = [{"Value": "test", "Rule": {}, "Type": "REGULAR"}]
    arn = aws_client.ce.create_cost_category_definition(
        Name=def_name, RuleVersion=rule_ver, Rules=rules
    )["CostCategoryArn"]

    def validate():
        snapshot.match(
            "ce_describe_cost_category",
            aws_client.ce.describe_cost_category_definition(CostCategoryArn=arn),
        )

    persistence_validations.register(validate)
