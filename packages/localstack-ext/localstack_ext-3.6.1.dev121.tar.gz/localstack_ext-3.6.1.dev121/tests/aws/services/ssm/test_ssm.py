import time
import uuid

import pytest
from botocore.exceptions import ClientError
from localstack.pro.core import config as ext_config
from localstack.pro.core.services.ec2.vmmanager.docker import DockerVmManager
from localstack.testing.pytest import markers
from localstack.utils.docker_utils import DOCKER_CLIENT

# Number of seconds to wait between issuing SendCommand and asserting
WAIT_BEFORE_ASSERTION = 2


@pytest.fixture
def ec2_instance(ec2_test_ami, aws_client):
    """Create an EC2 instance for test purpose."""
    ami_id, _ = ec2_test_ami
    response = aws_client.ec2.run_instances(ImageId=ami_id, MinCount=1, MaxCount=1)
    instance_id = response["Instances"][0]["InstanceId"]

    yield instance_id

    aws_client.ec2.terminate_instances(InstanceIds=[instance_id])


@pytest.mark.skipif(
    condition=ext_config.EC2_VM_MANAGER != "docker",
    reason="Tests specific to EC2 Docker VM manager",
)
class TestSSMDockerVMM:
    """Tests for SSM operations associated with EC2 Docker VMM."""

    @markers.aws.only_localstack
    def test_cancel_command(self, ec2_instance, aws_client):
        # Test must raise for invalid command ID
        with pytest.raises(ClientError) as exc:
            aws_client.ssm.cancel_command(CommandId="878c542e-face-face-face-b2419fdca76f")

        err = exc.value.response["Error"]
        assert err["Code"] == "InvalidCommandId"
        assert err["Message"] == ""

        # Test cancel command terminates the command
        invocation = aws_client.ssm.send_command(
            DocumentName="AWS-RunShellScript",
            InstanceIds=[ec2_instance],
            Parameters={
                "commands": ["sleep 69"],
            },
        )
        time.sleep(WAIT_BEFORE_ASSERTION)
        aws_client.ssm.cancel_command(CommandId=invocation["Command"]["CommandId"])
        time.sleep(WAIT_BEFORE_ASSERTION)
        output = DOCKER_CLIENT.exec_in_container(
            DockerVmManager.container_name_from_instance_id(ec2_instance),
            ["ps", "-ef"],
        )
        assert "sleep 69" not in output

    @markers.aws.only_localstack
    def test_describe_instance_information(self, ec2_instance, aws_client):
        # Test Dockerised EC2 instances are automatically registered with SSM
        actual = aws_client.ssm.describe_instance_information()["InstanceInformationList"]
        assert (ec2_instance, "Online") in [
            (inst["InstanceId"], inst["PingStatus"]) for inst in actual
        ]

    @markers.aws.only_localstack
    def test_send_command(self, ec2_instance, aws_client):
        # Test must raise for invalid instance
        with pytest.raises(ClientError) as exc:
            aws_client.ssm.send_command(
                DocumentName="AWS-RunShellScript",
                InstanceIds=["i-babadada"],
            )
        err = exc.value.response["Error"]
        assert err["Code"] == "InvalidInstanceID.NotFound"
        assert err["Message"] == "The instance ID 'i-babadada' does not exist"

        # Test without working directory param
        testfile_name = str(uuid.uuid4())
        aws_client.ssm.send_command(
            DocumentName="AWS-RunShellScript",
            InstanceIds=[ec2_instance],
            Parameters={
                "commands": [f"touch {testfile_name}"],
            },
        )
        time.sleep(WAIT_BEFORE_ASSERTION)
        # cat will return non-zero if the file doesn't exist
        DOCKER_CLIENT.exec_in_container(
            DockerVmManager.container_name_from_instance_id(ec2_instance),
            ["cat", testfile_name],
        )

        # Test with working directory param
        testfile_name = str(uuid.uuid4())
        working_dir = "/tmp"
        aws_client.ssm.send_command(
            DocumentName="AWS-RunShellScript",
            InstanceIds=[ec2_instance],
            Parameters={
                "commands": [f"touch {testfile_name}"],
                "workingDirectory": [working_dir],
            },
        )
        time.sleep(WAIT_BEFORE_ASSERTION)
        DOCKER_CLIENT.exec_in_container(
            DockerVmManager.container_name_from_instance_id(ec2_instance),
            ["cat", f"{working_dir}/{testfile_name}"],
        )

        # Test stdout stream is captured
        expected_output = "no_politics"
        output = aws_client.ssm.send_command(
            DocumentName="AWS-RunShellScript",
            InstanceIds=[ec2_instance],
            Parameters={"commands": [f"printf {expected_output}"]},
        )
        time.sleep(WAIT_BEFORE_ASSERTION)
        command_id = output["Command"]["CommandId"]
        invocation = aws_client.ssm.get_command_invocation(
            CommandId=command_id, InstanceId=ec2_instance
        )
        assert invocation["Status"] == "Success"
        assert invocation["StandardOutputContent"] == expected_output
        assert invocation["StandardErrorContent"] == ""

        # Test stderr is captured
        expected_output = "dank meme!"
        output = aws_client.ssm.send_command(
            DocumentName="AWS-RunShellScript",
            InstanceIds=[ec2_instance],
            # `logger` lets printing to stderr without resorting to shell redirection, which isn't ideal with shell exec
            Parameters={
                "commands": [f"logger --no-act --socket-errors=off --stderr {expected_output}"]
            },
        )
        time.sleep(WAIT_BEFORE_ASSERTION)
        command_id = output["Command"]["CommandId"]
        invocation = aws_client.ssm.get_command_invocation(
            CommandId=command_id, InstanceId=ec2_instance
        )
        assert invocation["Status"] == "Success"
        assert invocation["StandardOutputContent"] == ""
        assert expected_output in invocation["StandardErrorContent"]
