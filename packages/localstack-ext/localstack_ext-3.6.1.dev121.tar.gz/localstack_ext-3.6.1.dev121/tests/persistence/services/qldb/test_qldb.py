import pytest
from localstack.utils.strings import short_uid


@pytest.mark.skip(reason="flaky")
def test_qldb_creation(persistence_validations, snapshot, aws_client):
    ledger_name = f"qldb-l-{short_uid()}"
    aws_client.qldb.create_ledger(Name=ledger_name, PermissionsMode="ALLOW_ALL")

    def validate():
        # TODO fix botocore.errorfactory.ResourceNotFoundException flakyness
        snapshot.match("describe_ledger", aws_client.qldb.describe_ledger(Name=ledger_name))

    persistence_validations.register(validate)
