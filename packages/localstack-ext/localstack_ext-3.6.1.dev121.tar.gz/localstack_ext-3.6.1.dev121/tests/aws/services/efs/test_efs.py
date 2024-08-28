import contextlib

import pytest
from botocore.exceptions import ClientError
from localstack.testing.aws.util import is_aws_cloud
from localstack.testing.pytest import markers
from localstack.utils.strings import short_uid
from localstack.utils.sync import poll_condition, retry


# TODO: maybe make available in conftest if needed
@pytest.fixture
def efs_create_filesystem(aws_client):
    filesystem_ids = []

    def _create_fs(**kwargs):
        response = aws_client.efs.create_file_system(**kwargs)
        filesystem_ids.append(response["FileSystemId"])

        def _is_fs_ready():
            resp = aws_client.efs.describe_file_systems(FileSystemId=response["FileSystemId"])
            return resp["FileSystems"][0]["LifeCycleState"] == "available"

        poll_condition(_is_fs_ready, timeout=60, interval=2)
        return response

    yield _create_fs

    for filesystem_id in filesystem_ids:
        # need to delete any MountTarget for the FileSystem before being able to delete it
        with contextlib.suppress(ClientError):
            mount_targets = aws_client.efs.describe_mount_targets(FileSystemId=filesystem_id)
            for mount_target in mount_targets["MountTargets"]:
                with contextlib.suppress(ClientError):
                    aws_client.efs.delete_mount_target(MountTargetId=mount_target["MountTargetId"])

            def _mount_targets_deleted():
                resp = aws_client.efs.describe_file_systems(FileSystemId=filesystem_id)
                return resp["FileSystems"][0]["NumberOfMountTargets"] == 0

            poll_condition(_mount_targets_deleted, timeout=20, interval=2)

        with contextlib.suppress(ClientError):
            aws_client.efs.delete_file_system(FileSystemId=filesystem_id)


@pytest.fixture(autouse=True)
def efs_transformers(snapshot):
    snapshot.add_transformers_list(
        [
            snapshot.transform.key_value("CreationToken"),
            snapshot.transform.key_value("FileSystemId"),
        ]
    )


@markers.snapshot.skip_snapshot_verify(
    paths=[
        "$.create-fs.LifeCycleState",
        "$.create-fs.Name",  # Moto sets it to an empty string instead of not returning the field if not set
        "$.create-fs.SizeInBytes.Timestamp",  # Moto sets it even without modification
        "$..FileSystems..SizeInBytes",  # Moto has value at 0 but AWS starts with 6144
        "$..FileSystems..Name",
        "$..ErrorCode",  # missing a field
    ]
)
class TestEfsFileSystemCrud:
    @markers.aws.validated
    @markers.only_on_amd64
    def test_create_filesystem(self, aws_client, efs_create_filesystem, snapshot):
        response = aws_client.efs.describe_file_systems()
        snapshot.match("describe-fs-before", response)
        fsystems_before = response["FileSystems"]

        token = f"token-{short_uid()}"
        mode = "generalPurpose"
        # create
        result = efs_create_filesystem(CreationToken=token, PerformanceMode=mode)
        snapshot.match("create-fs", result)
        assert "generalPurpose" == result["PerformanceMode"]
        assert "FileSystemArn" in result
        fs_id = result["FileSystemId"]

        # list
        response = aws_client.efs.describe_file_systems()
        snapshot.match("describe-fs", response)
        fsystems = response["FileSystems"]
        assert "generalPurpose" == fsystems[0]["PerformanceMode"]
        assert len(fsystems_before) + 1 == len(fsystems)

        # get
        response = aws_client.efs.describe_file_systems(FileSystemId=fs_id)
        snapshot.match("describe-fs-with-id", response)
        fsystems = response["FileSystems"]
        assert 1 == len(fsystems)
        assert fs_id == fsystems[0]["FileSystemId"]

        # delete
        response = aws_client.efs.delete_file_system(FileSystemId=fs_id)
        snapshot.match("delete-fs", response)

        # The construct 'with pytest.raises(Exception) as e + e.match()' misbehaved/did not properly work from within
        # retry(), so this construct was used instead
        def check_if_deleted():
            try:
                aws_client.efs.describe_file_systems(FileSystemId=fs_id)
                # if we reach this then the file system still shows up
                assert False
            except Exception as e:
                assert "FileSystemNotFound" in str(e)

        retry(check_if_deleted, 20, 0.15)

        with pytest.raises(ClientError) as e:
            aws_client.efs.describe_file_systems(FileSystemId=fs_id)
        snapshot.match("describe-deleted-fs", e.value.response)

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(
        paths=[
            "$..SizeInBytes.Timestamp",
        ]
    )
    def test_lifecycle_configuration(self, aws_client, snapshot, efs_create_filesystem):
        filesystem = efs_create_filesystem()
        snapshot.match("create-fs", filesystem)
        filesystem_id = filesystem["FileSystemId"]

        policies = [
            {"TransitionToIA": "AFTER_7_DAYS", "TransitionToPrimaryStorageClass": "AFTER_1_ACCESS"}
        ]
        with pytest.raises(ClientError) as e:
            aws_client.efs.put_lifecycle_configuration(
                FileSystemId=filesystem_id, LifecyclePolicies=policies
            )
        snapshot.match("malformed-put-lifecycle-conf", e.value.response)

        policies = [
            {"TransitionToIA": "AFTER_7_DAYS"},
            {"TransitionToPrimaryStorageClass": "AFTER_1_ACCESS"},
        ]
        result = aws_client.efs.put_lifecycle_configuration(
            FileSystemId=filesystem_id, LifecyclePolicies=policies
        )
        snapshot.match("put-lifecycle-conf", result)
        assert result.get("LifecyclePolicies") == policies

        result = aws_client.efs.describe_lifecycle_configuration(FileSystemId=filesystem_id)
        snapshot.match("describe-lifecycle-conf", result)
        assert result.get("LifecyclePolicies") == policies

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(
        paths=[
            "$..LifeCycleState",
            "$..SizeInBytes.Timestamp",
            "$.delete-fs-with-mount-target.Error.Message",  # wrong error message from moto
            "$.delete-fs-with-mount-target.Message",  # wrong error message from moto
        ]
    )
    def test_mount_target(self, aws_client, efs_create_filesystem, snapshot):
        """
        Only test the CRUD operations around the MountTarget, an integration test with EC2 would be needed
        See https://docs.aws.amazon.com/efs/latest/ug/API_CreateMountTarget.html
        """
        snapshot.add_transformers_list(
            [
                snapshot.transform.key_value("AvailabilityZoneId"),
                snapshot.transform.key_value("AvailabilityZoneName"),
                snapshot.transform.key_value("IpAddress"),
                snapshot.transform.key_value("MountTargetId"),
                snapshot.transform.key_value("NetworkInterfaceId"),
                snapshot.transform.key_value("SubnetId"),
                snapshot.transform.key_value("VpcId"),
            ]
        )

        filesystem = efs_create_filesystem()
        snapshot.match("create-fs", filesystem)
        filesystem_id = filesystem["FileSystemId"]

        subnet_id = aws_client.ec2.describe_subnets()["Subnets"][0]["SubnetId"]

        describe_mount_targets = aws_client.efs.describe_mount_targets(FileSystemId=filesystem_id)
        snapshot.match("describe-mount-targets", describe_mount_targets)

        create_mount_target = aws_client.efs.create_mount_target(
            FileSystemId=filesystem_id,
            SubnetId=subnet_id,
        )
        snapshot.match("create-mount-target", create_mount_target)

        describe_mount_targets = aws_client.efs.describe_mount_targets(FileSystemId=filesystem_id)
        snapshot.match("describe-mount-targets-after-create", describe_mount_targets)

        describe_fs = aws_client.efs.describe_file_systems(FileSystemId=filesystem_id)
        snapshot.match("describe-fs", describe_fs)

        with pytest.raises(ClientError) as e:
            aws_client.efs.delete_file_system(FileSystemId=filesystem_id)
        snapshot.match("delete-fs-with-mount-target", e.value.response)

        delete_mount_target = aws_client.efs.delete_mount_target(
            MountTargetId=create_mount_target["MountTargetId"]
        )
        snapshot.match("delete-mount-target", delete_mount_target)

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(
        paths=[
            "$..LifeCycleState",
            "$.describe-access-points-after-delete-exc.Error.Message",  # wrong error message from moto
            "$.describe-access-points-after-delete-exc.Message",  # wrong error message from moto
            "$..AccessPointArn",  # wrong format of the AccessPointId which gives an issue with the ARN
        ]
    )
    def test_access_point(self, aws_client, snapshot, efs_create_filesystem):
        """
        Only test the CRUD operations around the AccessPoint, an integration test with Lambda would be needed
        See:
        - https://docs.aws.amazon.com/efs/latest/ug/API_CreateAccessPoint.html
        - https://docs.aws.amazon.com/efs/latest/ug/create-access-point.html
        # TODO: add negative testing
        example: CreateAccessPoint, rootDirectory.path validation (no trailing slash)
        """
        snapshot.add_transformers_list(
            [
                snapshot.transform.key_value("AccessPointId"),
                snapshot.transform.key_value("ClientToken"),
            ]
        )
        filesystem = efs_create_filesystem()
        snapshot.match("create-fs", filesystem)
        filesystem_id = filesystem["FileSystemId"]

        describe_access_points = aws_client.efs.describe_access_points(FileSystemId=filesystem_id)
        snapshot.match("describe-access-points", describe_access_points)

        create_access_point = aws_client.efs.create_access_point(
            FileSystemId=filesystem_id,
            RootDirectory={
                "Path": "/efs/testpath/east",
                "CreationInfo": {"OwnerUid": 0, "OwnerGid": 11, "Permissions": "775"},
            },
            PosixUser={
                "Uid": 22,
                "Gid": 4,
            },
            Tags=[{"Key": "Name", "Value": "east-users"}],
        )
        snapshot.match("create-access-point", create_access_point)
        access_point_id = create_access_point["AccessPointId"]

        describe_access_points = aws_client.efs.describe_access_points(FileSystemId=filesystem_id)
        snapshot.match("describe-access-points-after-create", describe_access_points)

        delete_access_point = aws_client.efs.delete_access_point(
            AccessPointId=access_point_id,
        )
        snapshot.match("delete-access-point", delete_access_point)

        if is_aws_cloud():

            def is_access_point_deleted():
                return not aws_client.efs.describe_access_points(FileSystemId=filesystem_id)[
                    "AccessPoints"
                ]

            poll_condition(is_access_point_deleted, timeout=20, interval=2)

        describe_access_points = aws_client.efs.describe_access_points(FileSystemId=filesystem_id)
        snapshot.match("describe-access-points-after-delete", describe_access_points)

        with pytest.raises(ClientError) as e:
            aws_client.efs.describe_access_points(
                AccessPointId=access_point_id,
            )
        snapshot.match("describe-access-points-after-delete-exc", e.value.response)


# TODO: write a fully-fledged integration test using a shared EFS volume inside 2 lambdas
# https://docs.aws.amazon.com/lambda/latest/dg/services-efs.html
# https://aws.amazon.com/blogs/compute/using-amazon-efs-for-aws-lambda-in-your-serverless-applications/
# https://aws.amazon.com/blogs/aws/new-a-shared-file-system-for-your-lambda-functions/
