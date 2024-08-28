from localstack.testing.pytest import markers
from localstack.utils.aws import resources
from localstack.utils.strings import short_uid


class TestDynamoDB:
    @markers.aws.unknown
    def test_table_regions(self, aws_client_factory):
        region1 = "eu-central-1"
        region2 = "us-east-2"
        table_name = "table-%s" % short_uid()

        ddb1 = aws_client_factory(region_name=region1).dynamodb
        ddb2 = aws_client_factory(region_name=region2).dynamodb

        # fetch list of tables
        tables_before1 = ddb1.list_tables()["TableNames"]
        tables_before2 = ddb2.list_tables()["TableNames"]

        # create new table in region 1
        resources.create_dynamodb_table(table_name, partition_key="id", region_name=region1)

        # assert table has been created in correct region
        tables1 = ddb1.list_tables()["TableNames"]
        tables2 = ddb2.list_tables()["TableNames"]
        assert len(tables1) == len(tables_before1) + 1
        assert len(tables2) == len(tables_before2)
        assert table_name in tables1

        # create new table in region 2
        resources.create_dynamodb_table(table_name, partition_key="id", region_name=region2)
        tables2 = ddb2.list_tables()["TableNames"]
        assert table_name in tables2

        # put items to table1
        ddb1.put_item(TableName=table_name, Item={"id": {"S": "id1"}, "region": {"S": region1}})
        result = ddb1.scan(TableName=table_name)
        assert len(result["Items"]) == 1
        assert result["Items"][0]["region"]["S"] == region1
        result = ddb2.scan(TableName=table_name)
        assert len(result["Items"]) == 0

        # put items to table2
        ddb2.put_item(TableName=table_name, Item={"id": {"S": "id2"}, "region": {"S": region2}})
        result = ddb2.scan(TableName=table_name)
        assert len(result["Items"]) == 1
        assert result["Items"][0]["region"]["S"] == region2

        # clean up
        ddb1.delete_table(TableName=table_name)
        ddb2.delete_table(TableName=table_name)

    @markers.aws.unknown
    def test_table_backups(self, aws_client):
        client = aws_client.dynamodb

        # create table
        table_name = "tab-%s" % short_uid()
        resources.create_dynamodb_table(table_name, partition_key="id")

        # put items to table
        num_items = 150
        for i in range(num_items):
            client.put_item(TableName=table_name, Item={"id": {"S": "test-%s" % i}})

        # backup table
        result = client.create_backup(TableName=table_name, BackupName="backup1").get(
            "BackupDetails", {}
        )
        backup_arn = result["BackupArn"]

        # restore backup
        tgt_table_name = "tab-%s" % short_uid()
        client.restore_table_from_backup(TargetTableName=tgt_table_name, BackupArn=backup_arn)

        # assert items exist
        items = client.scan(TableName=tgt_table_name).get("Items", [])
        assert len(items) == num_items

        # clean up
        client.delete_backup(BackupArn=backup_arn)
        client.delete_table(TableName=table_name)
