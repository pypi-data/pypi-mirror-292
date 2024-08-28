import os

from localstack.testing.pytest import markers
from localstack_snapshot.snapshots.transformer import SortingTransformer


@markers.snapshot.skip_snapshot_verify(
    paths=[
        "$..FileSystems..FileSystemProtection",  # missing
        "$..FileSystems..Name",  # shouldn't b ethere
        "$..FileSystems..ProvisionedThroughputInMibps",  #  1.0 (type: <class 'float'>) → 1 (type: <class 'int'>)... (expected → actual)
        "$..FileSystems..SizeInBytes.Timestamp",  # shouldn't be there
        "$..FileSystems..SizeInBytes.Value",  # 6144 → 0 ... (expected → actual)
        "$..FileSystems..SizeInBytes.ValueInArchive",  # missing
        "$..FileSystems..SizeInBytes.ValueInStandard",  # 6144 → 0 ... (expected → actual)
        "$..FileSystems..Tags",  # missing
    ]
)
@markers.aws.validated
def test_file_system_deployment(deploy_cfn_template, snapshot, aws_client):
    snapshot.add_transformer(snapshot.transform.cloudformation_api())
    snapshot.add_transformer(snapshot.transform.key_value("IpAddress"))
    snapshot.add_transformer(snapshot.transform.key_value("MountTargetId"))
    snapshot.add_transformer(snapshot.transform.key_value("NetworkInterfaceId"))
    snapshot.add_transformer(snapshot.transform.key_value("SubnetId"))
    snapshot.add_transformer(snapshot.transform.key_value("VpcId"))
    snapshot.add_transformer(snapshot.transform.key_value("ClientToken"))
    snapshot.add_transformer(snapshot.transform.key_value("AvailabilityZoneId"))
    snapshot.add_transformer(snapshot.transform.key_value("AvailabilityZoneName"))

    result = deploy_cfn_template(
        template_path=os.path.join(
            os.path.dirname(__file__), "../../../templates/efs_file_system.yml"
        ),
        max_wait=120,
    )

    snapshot.add_transformer(SortingTransformer("Outputs", lambda o: o["OutputKey"]))
    describe_response = aws_client.cloudformation.describe_stacks(StackName=result.stack_id)
    snapshot.match("stack-details", describe_response)

    outputs = describe_response["Stacks"][0]["Outputs"]
    outputs = {entry["OutputKey"]: entry["OutputValue"] for entry in outputs}
    filesystem_id = outputs.get("FileSystemRef")
    snapshot.add_transformer(snapshot.transform.regex(filesystem_id, "<filesystem-id>"))

    describe_fs = aws_client.efs.describe_file_systems(FileSystemId=filesystem_id)
    snapshot.add_transformer(snapshot.transform.key_value("CreationToken"))
    snapshot.match("fs-details", describe_fs)

    mount_target = aws_client.efs.describe_mount_targets(
        MountTargetId=result.outputs["MountTargetId"]
    )
    snapshot.match("mount-target", mount_target)

    access_point = aws_client.efs.describe_access_points(
        AccessPointId=result.outputs["AccessPointId"]
    )
    snapshot.match("access-point", access_point)
