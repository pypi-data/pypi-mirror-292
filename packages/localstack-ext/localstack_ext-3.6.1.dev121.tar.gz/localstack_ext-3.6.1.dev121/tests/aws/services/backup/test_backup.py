import pytest
from botocore.exceptions import ClientError
from localstack.pro.core.services.backup.core import get_backup_store
from localstack.services.events.scheduler import JobScheduler
from localstack.testing.pytest import markers
from localstack.utils.aws import arns, resources
from localstack.utils.strings import short_uid
from localstack.utils.sync import retry
from localstack_snapshot.snapshots.transformer import RegexTransformer

from tests.aws.fixtures import whitebox_internal_access


class TestBackup:
    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(
        paths=["$..BackupPlanArn", "$..BackupPlan.Rules..RuleId"]
    )
    def test_backup_plan(self, aws_client, snapshot, cleanups):
        snapshot.add_transformer(
            [
                snapshot.transform.key_value("VersionId"),
                snapshot.transform.key_value("BackupPlanId"),
            ]
        )

        client = aws_client.backup
        plan_name = f"test-plan-{short_uid()}"
        vault_name = f"vault-{short_uid()}"

        snapshot.add_transformer(RegexTransformer(plan_name, "plan-name"))
        snapshot.add_transformer(RegexTransformer(vault_name, "vault-name"))

        cleanups.append(lambda: client.delete_backup_vault(BackupVaultName=vault_name))
        client.create_backup_vault(BackupVaultName=vault_name)
        # create backup plan
        plan = {
            "BackupPlanName": plan_name,
            "Rules": [
                {
                    "RuleName": "test-rule",
                    "TargetBackupVaultName": vault_name,
                    "ScheduleExpression": "cron(0 1 ? * * *)",
                    "ScheduleExpressionTimezone": "America/Los_Angeles",
                    "StartWindowMinutes": 60,
                    "CompletionWindowMinutes": 120,
                    "Lifecycle": {"DeleteAfterDays": 1},
                }
            ],
        }
        result = client.create_backup_plan(BackupPlan=plan)
        snapshot.match("create-backup-plan", result)
        plan_id = result.get("BackupPlanId")

        # get backup plan
        result = client.get_backup_plan(BackupPlanId=plan_id)
        snapshot.match("get-backup-plan", result)

        # list backup plans
        plans_after = client.list_backup_plans().get("BackupPlansList", [])
        matching = [plan for plan in plans_after if plan["BackupPlanName"] == plan_name]
        assert matching

        # delete backup plan
        client.delete_backup_plan(BackupPlanId=plan_id)
        with pytest.raises(ClientError) as ctx:
            client.get_backup_plan(BackupPlanId=plan_id)
        snapshot.match("delete-backup-plan", ctx.value)

    @markers.aws.unknown
    def test_backup_vaults(self, aws_client):
        client = aws_client.backup
        vault_name = "vault-%s" % short_uid()

        # create backup vault
        result = client.create_backup_vault(
            BackupVaultName=vault_name, BackupVaultTags={"k1": "v1"}
        )
        assert result["ResponseMetadata"]["HTTPStatusCode"] == 200

        # get backup vault
        result = client.describe_backup_vault(BackupVaultName=vault_name)
        assert result["ResponseMetadata"]["HTTPStatusCode"] == 200

        # list backup vaults
        vaults_after = client.list_backup_vaults().get("BackupVaultList", [])
        matching = [vault for vault in vaults_after if vault["BackupVaultName"] == vault_name]
        assert matching

        # delete backup vault
        client.delete_backup_vault(BackupVaultName=vault_name)
        with pytest.raises(Exception) as e:
            client.describe_backup_vault(BackupVaultName=vault_name)
        e.match("ResourceNotFoundException")

    @markers.aws.unknown
    def test_backup_selections(self, aws_client):
        client = aws_client.backup
        sel_name = "sel-%s" % short_uid()
        plan_name = "plan-%s" % short_uid()

        # create backup plan
        plan = {"BackupPlanName": plan_name, "Rules": []}
        result = client.create_backup_plan(BackupPlan=plan)
        plan_id = result.get("BackupPlanId")
        selections = client.list_backup_selections(BackupPlanId=plan_id).get(
            "BackupSelectionsList", []
        )

        # create backup selection
        selection = {"SelectionName": sel_name, "IamRoleArn": "r1"}
        result = client.create_backup_selection(BackupPlanId=plan_id, BackupSelection=selection)
        assert result["ResponseMetadata"]["HTTPStatusCode"] == 200
        sel_id = result["SelectionId"]

        # get backup selection
        result = client.get_backup_selection(BackupPlanId=plan_id, SelectionId=sel_id)
        assert result["ResponseMetadata"]["HTTPStatusCode"] == 200

        # list backup selections
        selections_after = client.list_backup_selections(BackupPlanId=plan_id).get(
            "BackupSelectionsList", []
        )
        assert len(selections_after) == len(selections) + 1

        # delete backup selection
        client.delete_backup_selection(BackupPlanId=plan_id, SelectionId=sel_id)
        with pytest.raises(Exception) as e:
            client.get_backup_selection(BackupPlanId=plan_id, SelectionId=sel_id)
        e.match("ResourceNotFoundException")

    @markers.aws.only_localstack
    @whitebox_internal_access
    def test_scheduled_backup_and_restore(self, aws_client, account_id, region_name):
        client = aws_client.backup
        ddb_client = aws_client.dynamodb
        plan_name = "plan-%s" % short_uid()
        sel_name = "sel-%s" % short_uid()
        table_name = "table-%s" % short_uid()
        vault_name = "vault-%s" % short_uid()

        # create backup vault and plan
        client.create_backup_vault(BackupVaultName=vault_name)
        rule = {
            "RuleName": "rule1",
            "TargetBackupVaultName": vault_name,
            "ScheduleExpression": "* * * * *",
        }
        plan = {
            "BackupPlanName": plan_name,
            "Rules": [rule],
        }
        result = client.create_backup_plan(BackupPlan=plan)
        plan_id = result.get("BackupPlanId")
        result = client.get_backup_plan(BackupPlanId=plan_id)
        assert result["BackupPlan"] == plan
        assert result["BackupPlanId"] == plan_id
        assert plan_name in result["BackupPlanArn"]
        assert result.get("VersionId")
        assert result.get("CreationDate")

        def _get_scheduled_job(_job_id=None):
            plan = get_backup_store(account_id, region_name).backup_plans.get(plan_id)
            if not _job_id:
                _job_id = plan["Rules"][0].get("_jobId")
            scheduler = JobScheduler.instance()
            for job in scheduler.jobs:
                if job.job_id == _job_id:
                    return _job_id

        scheduled_job_id = _get_scheduled_job()
        try:
            # assert that job has been scheduled
            assert scheduled_job_id

            # create DynamoDB table
            num_items = 10
            resources.create_dynamodb_table(table_name, partition_key="id")
            table_arn = arns.dynamodb_table_arn(
                table_name=table_name,
                account_id=account_id,
                region_name=region_name,
            )
            for i in range(num_items):
                item = {"id": {"S": "test-%s" % i}}
                ddb_client.put_item(TableName=table_name, Item=item)

            # create backup selection
            selection = {"SelectionName": sel_name, "IamRoleArn": "r1", "Resources": [table_arn]}
            result = client.create_backup_selection(BackupPlanId=plan_id, BackupSelection=selection)
            assert result["ResponseMetadata"]["HTTPStatusCode"] == 200

            def check_recovery_points():
                points = client.list_recovery_points_by_backup_vault(
                    BackupVaultName=vault_name
                ).get("RecoveryPoints")
                assert points
                points = client.list_recovery_points_by_resource(ResourceArn=table_arn).get(
                    "RecoveryPoints"
                )
                assert points
                return points[0].get("RecoveryPointArn")

            # assert backup created after ~1 min
            recovery_point_arn = retry(check_recovery_points, sleep=5, retries=13)
            assert recovery_point_arn

            # start restore job
            metadata = {}
            res = client.start_restore_job(
                RecoveryPointArn=recovery_point_arn, Metadata=metadata, IamRoleArn="r1"
            )
            job_id = res.get("RestoreJobId")

            def assert_job_completed():
                result = client.describe_restore_job(RestoreJobId=job_id)
                assert result.get("Status") == "COMPLETED"
                return result.get("CreatedResourceArn")

            # assert that data has been restored
            new_resource_arn = retry(assert_job_completed)
            assert ":dynamodb:" in new_resource_arn
            items = ddb_client.scan(TableName=table_name).get("Items", [])
            assert len(items) == num_items

            # update backup plan - assert that job gets removed and re-added
            plan["Rules"] = []
            update_response = client.update_backup_plan(BackupPlanId=plan_id, BackupPlan=plan)
            assert update_response["ResponseMetadata"]["HTTPStatusCode"] == 200
            assert not _get_scheduled_job(scheduled_job_id)
            plan["Rules"] = [rule]
            update_response = client.update_backup_plan(BackupPlanId=plan_id, BackupPlan=plan)
            assert update_response["ResponseMetadata"]["HTTPStatusCode"] == 200
            scheduled_job_id = _get_scheduled_job()
            assert scheduled_job_id

        finally:
            # delete backup plan
            client.delete_backup_plan(BackupPlanId=plan_id)
            # assert that job is no longer scheduled
            assert not _get_scheduled_job(scheduled_job_id)
