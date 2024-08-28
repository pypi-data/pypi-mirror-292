from localstack.utils.strings import short_uid


def test_backup_get_backup_plan(persistence_validations, snapshot, aws_client):
    plan = f"b-{short_uid()}"
    backup_plan_id = aws_client.backup.create_backup_plan(
        BackupPlan={"BackupPlanName": plan, "Rules": []}
    )["BackupPlanId"]

    def validate():
        snapshot.match(
            "get_backup_plan", aws_client.backup.get_backup_plan(BackupPlanId=backup_plan_id)
        )

    persistence_validations.register(validate)
