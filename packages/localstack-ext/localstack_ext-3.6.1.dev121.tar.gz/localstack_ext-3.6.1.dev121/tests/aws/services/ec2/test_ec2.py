import io
import logging
from urllib.parse import urljoin

import pytest
from botocore.exceptions import ClientError
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from localstack import config
from localstack.pro.core import config as ext_config
from localstack.pro.core.services.ec2.vmmanager import docker
from localstack.pro.core.services.ec2.vmmanager import docker as docker_vmmanager
from localstack.pro.core.services.ec2.vmmanager.docker import (
    AMAZONLINUX_2023_AMI,
    CLOUD_INIT_LOG_PATH,
    UBUNTU_JAMMY_AMI,
    UBUNTU_JAMMY_DOCKER_IMAGE,
    DockerVmManager,
    VmManager,
)
from localstack.pro.core.services.ec2.vmmanager.kubernetes import KubernetesVmManager
from localstack.testing.pytest import markers
from localstack.utils.container_utils.container_client import NoSuchImage
from localstack.utils.container_utils.docker_cmd_client import CmdDockerClient
from localstack.utils.container_utils.docker_sdk_client import SdkDockerClient
from localstack.utils.docker_utils import DOCKER_CLIENT
from localstack.utils.run import is_command_available
from localstack.utils.strings import short_uid, to_str
from localstack.utils.sync import retry

LOG = logging.getLogger(__name__)

# AMI with no SSHD preinstalled, used to test SSHD injection (i.e. Dropbear)
DEBIAN_BUSTER_AMI = ("ami-3ee28eb9a7e9", "debian-buster")
DEBIAN_BUSTER_DOCKER_IMAGE = "debian:buster-slim"


class TestEC2:
    """Tests applicable to all VM managers."""

    @markers.snapshot.skip_snapshot_verify(
        paths=[
            "$..Ipv6CidrBlockAssociation.Ipv6CidrBlock",
            "$..Ipv6CidrBlockAssociation.Ipv6Pool",
            "$..Ipv6CidrBlockAssociation.NetworkBorderGroup",
        ]
    )
    @markers.aws.validated
    def test_associate_and_disassociate_vpc_cidr_block(self, snapshot, cleanups, aws_client):
        snapshot.add_transformer(
            snapshot.transform.key_value("AssociationId", reference_replacement=False)
        )
        snapshot.add_transformer(snapshot.transform.key_value("VpcId", reference_replacement=False))

        vpc_config = aws_client.ec2.create_vpc(CidrBlock="10.92.0.0/24")
        vpc_id = vpc_config["Vpc"]["VpcId"]
        cleanups.append(lambda: aws_client.ec2.delete_vpc(VpcId=vpc_id))

        cidr_block_association = aws_client.ec2.associate_vpc_cidr_block(
            VpcId=vpc_id, CidrBlock="10.92.1.0/24", AmazonProvidedIpv6CidrBlock=False
        )
        snapshot.match("cidr_block_association", cidr_block_association)
        cidr_block_dissociate = aws_client.ec2.disassociate_vpc_cidr_block(
            AssociationId=cidr_block_association["CidrBlockAssociation"]["AssociationId"]
        )
        snapshot.match("cidr_block_dissociate", cidr_block_dissociate)

        ipv6_cidr_block_association = aws_client.ec2.associate_vpc_cidr_block(
            VpcId=vpc_id,
            AmazonProvidedIpv6CidrBlock=True,
        )
        snapshot.match("ipv6_cidr_block_association", ipv6_cidr_block_association)
        ipv6_cidr_block_dissociate = aws_client.ec2.disassociate_vpc_cidr_block(
            AssociationId=ipv6_cidr_block_association["Ipv6CidrBlockAssociation"]["AssociationId"]
        )
        snapshot.match("ipv6_cidr_block_dissociate", ipv6_cidr_block_dissociate)


@pytest.mark.skipif(
    condition=ext_config.EC2_VM_MANAGER != "docker",
    reason="Tests not applicable to active EC2 VM manager",
)
class TestEC2DockerVMM:
    """Tests specific to the Docker VMM."""

    #
    # Fixtures
    #

    @pytest.fixture
    def imds_endpoint(self):
        if config.is_in_docker:
            return "http://169.254.169.254/"
        return "http://host.docker.internal:8080/"

    @pytest.fixture(autouse=True)
    def setup_ami(self):
        """
        This fixture downloads test-specific Docker AMIs that are not available in the VMM by default.
        """
        ami_id, ami_name = DEBIAN_BUSTER_AMI
        docker_image = DEBIAN_BUSTER_DOCKER_IMAGE

        target_image = f"{DockerVmManager.image_name_from_ami_name(ami_name)}:{ami_id}"

        try:
            DOCKER_CLIENT.inspect_image(docker_image, pull=False)
        except NoSuchImage:
            DOCKER_CLIENT.pull_image(docker_image)

        DOCKER_CLIENT.tag_image(source_ref=docker_image, target_name=target_image)

    @pytest.fixture(
        params=[UBUNTU_JAMMY_AMI, AMAZONLINUX_2023_AMI, DEBIAN_BUSTER_AMI],
        ids=["ubuntu-22.04", "amazonlinux-2023", "debian-10"],
    )
    def ec2_ssh_connection(self, request, docker_mark_for_cleanup, aws_client):
        """
        This fixture runs an EC2 Docker instance for a given AMI and sets up SSH
        """
        # local imports, to enable running "make docker-test" from MacOS
        import paramiko
        from paramiko.rsakey import RSAKey

        ami_id, _ = request.param

        private_key = rsa.generate_private_key(
            public_exponent=65537, key_size=2048, backend=default_backend()
        )
        public_key_material = private_key.public_key().public_bytes(
            encoding=serialization.Encoding.OpenSSH, format=serialization.PublicFormat.OpenSSH
        )

        # ImportKeyPair correctly places the public key in the instance
        key_name = f"foo-{short_uid()}"
        aws_client.ec2.import_key_pair(KeyName=key_name, PublicKeyMaterial=public_key_material)
        response = aws_client.ec2.run_instances(
            ImageId=ami_id, MinCount=1, MaxCount=1, KeyName=key_name
        )["Instances"][0]
        instance_id = response["InstanceId"]
        docker_mark_for_cleanup(instance_id)

        container_name = DockerVmManager.container_name_from_instance_id(instance_id)

        # IP addressing will not work on MacOS. Docker Desktop does not expose the bridge network
        ip_address = response["PublicIpAddress"]

        private_key_material = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        )
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.WarningPolicy)
        pkey = RSAKey.from_private_key(io.StringIO(to_str(private_key_material)))
        return container_name, public_key_material, ssh_client, ip_address, pkey

    #
    # Tests
    #

    @markers.aws.only_localstack
    def test_moto_fallback(self, ec2_test_ami, aws_client):
        """Sanity test to ensure that fallbacks to Moto happen correctly for mock instances."""
        # Get an AMI from Moto and try to launch a mock instance
        response = aws_client.ec2.describe_images(
            Filters=[{"Name": "name", "Values": ["amzn2-ami-ecs-hvm-2.0.20220209-x86_64-ebs"]}]
        )
        ami_id = response["Images"][0]["ImageId"]

        response = aws_client.ec2.run_instances(ImageId=ami_id, MinCount=1, MaxCount=1)
        instance_id = response["Instances"][0]["InstanceId"]

        assert (
            aws_client.ec2.stop_instances(InstanceIds=[instance_id])["ResponseMetadata"][
                "HTTPStatusCode"
            ]
            == 200
        )
        assert (
            aws_client.ec2.start_instances(InstanceIds=[instance_id])["ResponseMetadata"][
                "HTTPStatusCode"
            ]
            == 200
        )
        assert (
            aws_client.ec2.terminate_instances(InstanceIds=[instance_id])["ResponseMetadata"][
                "HTTPStatusCode"
            ]
            == 200
        )

    @markers.aws.only_localstack
    def test_describe_images(self, ec2_test_ami, aws_client):
        """Test that Docker images which follow the naming scheme are recognised as AMIs."""
        response = aws_client.ec2.describe_images()["Images"]
        assert ec2_test_ami in [(img.get("ImageId"), img.get("Name")) for img in response]

        # Must raise for invalid images
        with pytest.raises(ClientError) as exc:
            aws_client.ec2.describe_images(ImageIds=["ami-feedbabe"])

        err = exc.value.response["Error"]
        assert err["Code"] == "InvalidAMIID.NotFound"
        assert err["Message"] == "The image id '[['ami-feedbabe']]' does not exist"

    @markers.aws.only_localstack
    def test_describe_image_with_unsupported_image_name(self, aws_client, cleanups):
        """Test that images with unsupported image names are not returned by DescribeImages."""
        describe_before_unsupported_image = aws_client.ec2.describe_images()["Images"]

        # Tag an image with an unsupported image name
        image_name = "localstack-ec2:ami-local"
        DOCKER_CLIENT.tag_image(
            source_ref=UBUNTU_JAMMY_DOCKER_IMAGE,
            target_name=image_name,
        )
        cleanups.append(lambda: DOCKER_CLIENT.remove_image(image=image_name, force=True))

        describe_after_unsupported_image = aws_client.ec2.describe_images()["Images"]
        assert len(describe_before_unsupported_image) == len(describe_after_unsupported_image)

    @markers.aws.only_localstack
    def test_describe_images_with_podman_localhost_prefix(self, ec2_test_ami, aws_client, cleanups):
        """
        Test that images created by Podman (which prepends a "localhost/" suffix) are detected and returned
        See https://github.com/localstack/localstack/issues/7744
        """
        # Note: this test will likely soon become obsolete and/or will need to get redesigned, with
        # upcoming changes in the Podman/Docker client.

        ami_name = "test-image-123"
        ami_id = f"ami-{short_uid()}"
        # use an image name that would be used by Podman (with 'localhost/' prefix)
        image_name = "localhost/{}:{}".format(
            DockerVmManager.image_name_from_ami_name(ami_name), ami_id
        )

        DOCKER_CLIENT.tag_image(
            source_ref=UBUNTU_JAMMY_DOCKER_IMAGE,
            target_name=image_name,
        )
        cleanups.append(lambda: DOCKER_CLIENT.remove_image(image=image_name, force=True))

        response = aws_client.ec2.describe_images()["Images"]
        images = [(img.get("ImageId"), img.get("Name")) for img in response]
        assert (ami_id, ami_name) in images

    @markers.aws.only_localstack
    def test_describe_instances(self, ec2_test_ami, docker_mark_for_cleanup, aws_client):
        """Test that Docker containers which follow the naming scheme are recognised as EC2 instances."""
        # Run an instance
        response = aws_client.ec2.run_instances(ImageId=ec2_test_ami[0], MinCount=1, MaxCount=1)
        instance_id = response["Instances"][0]["InstanceId"]
        docker_mark_for_cleanup(instance_id)

        public_ip = response["Instances"][0]["PublicIpAddress"]
        public_dns = response["Instances"][0]["PublicDnsName"]
        assert public_dns.endswith(".localhost.localstack.cloud")

        # Ensure RunInstances and DescribeInstances return the same network addresses
        response = aws_client.ec2.describe_instances(InstanceIds=[instance_id])
        assert public_ip == response["Reservations"][0]["Instances"][0]["PublicIpAddress"]
        assert public_dns == response["Reservations"][0]["Instances"][0]["PublicDnsName"]

        # Must raise for invalid instances
        with pytest.raises(ClientError) as exc:
            aws_client.ec2.describe_instances(InstanceIds=["i-baadf00d"])

        err = exc.value.response["Error"]
        assert err["Code"] == "InvalidInstanceID.NotFound"
        assert err["Message"] == "The instance ID 'i-baadf00d' does not exist"

    @markers.aws.only_localstack
    @pytest.mark.skip(
        reason="FIXME. Flaky. See discussion at https://www.notion.so/localstack/tests-integration-test_ec2-9c1b12b20c2c42ee92fbc3a149a492a5 for more context"
    )
    def test_create_image(self, ec2_test_ami, docker_mark_for_cleanup, aws_client):
        """Test the CreateImage creates a Docker image from a running container."""
        ami_id, _ = ec2_test_ami

        # Test CreateImage raises for invalid instance ID
        with pytest.raises(ClientError) as exc:
            aws_client.ec2.create_image(InstanceId="i-feedcode", Name="doesnt_really_matter")

        err = exc.value.response["Error"]
        assert err["Code"] == "InvalidInstanceID.NotFound"
        assert err["Message"] == "The instance ID 'i-feedcode' does not exist"

        # Start an instance
        response = aws_client.ec2.run_instances(ImageId=ami_id, MinCount=1, MaxCount=1)
        instance_id = response["Instances"][0]["InstanceId"]
        docker_mark_for_cleanup(instance_id)

        # Test CreateImage creates a docker image
        image_name = "test/create/image"
        new_ami_id = aws_client.ec2.create_image(InstanceId=instance_id, Name=image_name)["ImageId"]
        docker_image = DockerVmManager.image_from_ami_id(new_ami_id, verify=False)
        docker_mark_for_cleanup(docker_image)

        assert DOCKER_CLIENT.inspect_image(docker_image, pull=False)

        # Test that slashes in AMI name don't break Docker images
        response = aws_client.ec2.describe_images(
            Filters=[{"Name": "name", "Values": [image_name]}]
        )
        assert len(response["Images"]) == 1
        assert response["Images"][0]["ImageId"] == new_ami_id

    @markers.aws.only_localstack
    @pytest.mark.parametrize("vm_manager", ["mock", "docker", "podman"])
    @pytest.mark.parametrize("client_type", ["cmd", "sdk"])
    @pytest.mark.skip(
        reason="FIXME. Flaky. See discussion at https://www.notion.so/localstack/tests-integration-test_ec2-9c1b12b20c2c42ee92fbc3a149a492a5 for more context"
    )
    def test_run_stop_start_terminate_instances(
        self,
        ec2_test_ami,
        docker_mark_for_cleanup,
        vm_manager,
        client_type,
        monkeypatch,
        aws_client,
    ):
        """Test various workflow operations in Docker/Podman and mock provider."""

        if vm_manager == "podman":
            # note: using "podman" as a special case of Docker VM executor
            vm_manager = "docker"
            monkeypatch.setattr(config, "DOCKER_CMD", "podman")
        requires_installed_cmd = client_type == "cmd" or config.DOCKER_CMD == "podman"
        if requires_installed_cmd and not is_command_available(config.DOCKER_CMD):
            pytest.skip(f"Docker/Podman command `{config.DOCKER_CMD}` is not available")

        # patch docker client for testing
        docker_client = CmdDockerClient() if client_type == "cmd" else SdkDockerClient()
        monkeypatch.setattr(docker_vmmanager, "DOCKER_CLIENT", docker_client)

        # patch VM manager to use for testing
        monkeypatch.setattr(ext_config, "EC2_VM_MANAGER", vm_manager)
        ami_id = ec2_test_ami[0]
        if vm_manager == "mock":
            ami_id = aws_client.ec2.describe_images()["Images"][0]["ImageId"]

        # TODO: hack for Podman support, as Docker SDK client doesn't support tag_image() for Podman at this stage
        if config.DOCKER_CMD == "podman":
            client_before = docker_vmmanager.DOCKER_CLIENT
            try:
                docker_vmmanager.DOCKER_CLIENT = CmdDockerClient()
                docker_vmmanager.DockerVmManager().initialise_images()
            finally:
                docker_vmmanager.DOCKER_CLIENT = client_before

        # Test that RunInstances raises for invalid AMI ID
        with pytest.raises(ClientError) as exc:
            aws_client.ec2.run_instances(ImageId="rocket-man", MinCount=1, MaxCount=1)

        err = exc.value.response["Error"]
        assert err["Code"] == "InvalidAMIID.NotFound"
        assert err["Message"] == "The image id 'rocket-man' does not exist"

        # run instance
        response = aws_client.ec2.run_instances(ImageId=ami_id, MinCount=1, MaxCount=1)
        instance_id = response["Instances"][0]["InstanceId"]

        # Test that RunInstances starts the Docker/Podman container
        expected_container = DockerVmManager.container_name_from_instance_id(
            instance_id, verify=False
        )
        running_containers = [container["name"] for container in docker_client.list_containers()]
        if vm_manager == "docker":
            docker_mark_for_cleanup(instance_id)
            assert expected_container in running_containers
        else:
            assert expected_container not in running_containers

        # Test that StopInstances pauses the Docker/Podman container
        expected_response = [
            {
                "CurrentState": {"Code": 80, "Name": "stopped"},
                "InstanceId": instance_id,
                "PreviousState": {"Code": 16, "Name": "running"},
            }
        ]
        response = aws_client.ec2.stop_instances(InstanceIds=[instance_id])
        containers = [
            container["name"] for container in docker_client.list_containers(filter="status=paused")
        ]
        if vm_manager == "docker":
            assert expected_container in containers
            assert response["StoppingInstances"] == expected_response
        else:
            assert expected_container not in containers

        response = aws_client.ec2.describe_instances(InstanceIds=[instance_id])
        inst_response = response["Reservations"][0]["Instances"][0]
        assert inst_response["ImageId"] == ami_id
        assert inst_response["State"] == expected_response[0]["CurrentState"]

        # Test that StopInstances is idempotent
        expected_response = [
            {
                "CurrentState": {"Code": 80, "Name": "stopped"},
                "InstanceId": instance_id,
                "PreviousState": {"Code": 80, "Name": "stopped"},
            }
        ]
        response = aws_client.ec2.stop_instances(InstanceIds=[instance_id])
        assert (
            response["StoppingInstances"] == expected_response
            or response["StoppingInstances"][0]["CurrentState"]["Name"] == "stopping"
        )

        # Test that StartInstances unpauses the Docker container
        expected_response = [
            {
                "CurrentState": {"Code": 16, "Name": "running"},
                "InstanceId": instance_id,
                "PreviousState": {"Code": 80, "Name": "stopped"},
            }
        ]
        response = aws_client.ec2.start_instances(InstanceIds=[instance_id])
        assert (
            response["StartingInstances"] == expected_response
            or response["StartingInstances"][0]["CurrentState"]["Name"] == "pending"
        )

        # Test that StartInstances is idempotent
        expected_response = [
            {
                "CurrentState": {"Code": 16, "Name": "running"},
                "InstanceId": instance_id,
                "PreviousState": {"Code": 16, "Name": "running"},
            }
        ]
        response = aws_client.ec2.start_instances(InstanceIds=[instance_id])
        assert (
            response["StartingInstances"] == expected_response
            or response["StartingInstances"][0]["CurrentState"]["Name"] == "pending"
        )

        # Test that TerminateInstances stops the Docker container
        expected_response = [
            {
                "CurrentState": {"Code": 48, "Name": "terminated"},
                "InstanceId": instance_id,
                "PreviousState": {"Code": 16, "Name": "running"},
            }
        ]
        response = aws_client.ec2.terminate_instances(InstanceIds=[instance_id])
        containers = [
            container["name"] for container in docker_client.list_containers(filter="status=exited")
        ]
        if vm_manager == "docker":
            assert expected_container in containers
        else:
            assert expected_container not in containers
        assert (
            response["TerminatingInstances"] == expected_response
            or response["TerminatingInstances"][0]["CurrentState"]["Name"] == "shutting-down"
        )

        # Test that TerminateInstances is idempotent
        expected_response = [
            {
                "CurrentState": {"Code": 48, "Name": "terminated"},
                "InstanceId": instance_id,
                "PreviousState": {"Code": 48, "Name": "terminated"},
            }
        ]
        response = aws_client.ec2.terminate_instances(InstanceIds=[instance_id])
        assert (
            response["TerminatingInstances"] == expected_response
            or response["TerminatingInstances"][0]["CurrentState"]["Name"] == "shutting-down"
        )

        def _list_containers(container_name: str):
            return [
                container
                for container in docker_client.list_containers()
                if container["name"] == container_name
            ]

        # Test that RunInstances->StopInstances->TerminateInstances lifecycle works
        response = aws_client.ec2.run_instances(ImageId=ami_id, MinCount=1, MaxCount=1)
        instance_id = response["Instances"][0]["InstanceId"]
        expected_container = DockerVmManager.container_name_from_instance_id(
            instance_id, verify=False
        )
        if vm_manager == "docker":
            docker_mark_for_cleanup(instance_id)
        aws_client.ec2.stop_instances(InstanceIds=[instance_id])
        containers = _list_containers(expected_container)
        if vm_manager == "docker":
            assert containers
            assert containers[0]["status"] == "paused"
        aws_client.ec2.terminate_instances(InstanceIds=[instance_id])
        containers = _list_containers(expected_container)
        if vm_manager == "docker":
            assert containers
            assert containers[0]["status"] == "exited"

    @pytest.mark.parametrize("fn", ["start_instances", "stop_instances", "terminate_instances"])
    @markers.aws.only_localstack
    def test_stop_start_terminate_instances_for_invalid_instance_id_raises(self, fn, aws_client):
        with pytest.raises(ClientError) as exc:
            getattr(aws_client.ec2, fn)(InstanceIds=["i-aaaabbbb"])

        err = exc.value.response["Error"]
        assert err["Code"] == "InvalidInstanceID.NotFound"
        assert err["Message"] == "The instance ID 'i-aaaabbbb' does not exist"

    @markers.aws.only_localstack
    def test_ssh_key_pairs(self, ec2_ssh_connection):
        """Ensure key pairs are correctly copied on to the instance."""
        container_name, public_key_material, ssh_client, ip_address, pkey = ec2_ssh_connection

        # check if auth key is present
        def _assert_auth_key():
            stdout, _ = DOCKER_CLIENT.exec_in_container(
                container_name,
                ["cat", "/root/.ssh/authorized_keys"],
            )
            assert public_key_material in stdout

        retry(_assert_auth_key, retries=5, sleep=1)

        # Following throws paramiko.ssh_exception.AuthenticationException for failures
        def _connect():
            ssh_client.connect(ip_address, username="root", pkey=pkey)

        retry(_connect, retries=20, sleep=2)
        ssh_client.close()

    @markers.aws.only_localstack
    @pytest.mark.skipif(
        not config.use_custom_dns(), reason="Test only valid if dns server is running."
    )
    def test_connect_to_localstack(self, ec2_ssh_connection):
        """Ensure DNS resolution works inside EC2 containers."""
        container_name, public_key_material, ssh_client, ip_address, pkey = ec2_ssh_connection

        try:

            def _connect():
                ssh_client.connect(ip_address, username="root", pkey=pkey, timeout=5)

            retry(_connect, retries=20, sleep=2)

            # install curl
            stdin, stdout, stderr = ssh_client.exec_command("apt update")
            stdout.read()  # this effectively waits until the command is finished.
            stdin, stdout, stderr = ssh_client.exec_command("apt install -y curl")
            stdout.read()
            # curl a subdomain of localhost.localstack.cloud to check DNS server setup - should hit localstack
            stdin, stdout, stderr = ssh_client.exec_command(
                f"curl https://something.localhost.localstack.cloud:{config.GATEWAY_LISTEN[0].port}/_localstack/health"
            )
            output = stdout.read()
            assert '"services"' in to_str(output)
        finally:
            # close ssh connection
            ssh_client.close()

    @markers.aws.unknown
    def test_user_data(self, ec2_test_ami, docker_mark_for_cleanup, aws_client):
        """Ensure user data is executed and logged on the instance"""

        user_data = """
        #!/bin/bash
        whoami | tee /myname && echo paramiko; echo 'not printed'>/dev/null; printf "error">/dev/stderr
        """

        response = aws_client.ec2.run_instances(
            ImageId=ec2_test_ami[0], MinCount=1, MaxCount=1, UserData=user_data
        )["Instances"][0]
        instance_id = response["InstanceId"]
        docker_mark_for_cleanup(instance_id)

        container_name = DockerVmManager.container_name_from_instance_id(instance_id)

        def _assert_cat_file(_container_name: str, _filepath: str, _expected_contents: str):
            stdout, _ = DOCKER_CLIENT.exec_in_container(_container_name, ["cat", _filepath])
            assert _expected_contents in to_str(stdout).strip()

        # Ensure pipes work and files are created
        retry(lambda: _assert_cat_file(container_name, "/myname", "root"), retries=20, sleep=2)

        # Ensure shell redirection and constructs work and logged in expected location
        expected_output = "root\nparamiko\nerror"
        stdout, _ = DOCKER_CLIENT.exec_in_container(container_name, ["cat", CLOUD_INIT_LOG_PATH])
        assert expected_output == to_str(stdout).strip()

        # Ensure hashbang interpreters are invoked and naughty strings are handled
        naughty_string = "Printed with perl 𝖔𝖛𝖊𝖗 ⅛⅜ サロゲートペア 🆒"

        user_data = f'''#!/bin/env perl
        print "{naughty_string}"'''

        response = aws_client.ec2.run_instances(
            ImageId=ec2_test_ami[0], MinCount=1, MaxCount=1, UserData=user_data
        )["Instances"][0]
        instance_id = response["InstanceId"]
        docker_mark_for_cleanup(instance_id)

        container_name = DockerVmManager.container_name_from_instance_id(instance_id)

        retry(
            lambda: _assert_cat_file(container_name, CLOUD_INIT_LOG_PATH, naughty_string),
            retries=20,
            sleep=2,
        )

        def _assert_instance_status(instance_id: str, status: str):
            assert (
                aws_client.ec2.describe_instances(InstanceIds=[instance_id])["Reservations"][0][
                    "Instances"
                ][0]["State"]["Name"]
                == status
            )

        # Ensure that updated user data is executed on Stop and Start
        new_userdata = """#!/bin/bash -x
        echo 'lorem' > /first_reboot"""
        aws_client.ec2.modify_instance_attribute(
            InstanceId=instance_id, Attribute="userData", Value=new_userdata
        )
        aws_client.ec2.stop_instances(InstanceIds=[instance_id])
        retry(lambda: _assert_instance_status(instance_id, "stopped"), retries=10, sleep=1)
        aws_client.ec2.start_instances(InstanceIds=[instance_id])
        retry(lambda: _assert_instance_status(instance_id, "running"), retries=10, sleep=1)
        retry(
            lambda: _assert_cat_file(container_name, CLOUD_INIT_LOG_PATH, "lorem"),
            retries=20,
            sleep=2,
        )
        retry(
            lambda: _assert_cat_file(container_name, "/first_reboot", "lorem"), retries=5, sleep=1
        )

        # Ensure that updated user data is executed on Reboot
        new_userdata = """#!/bin/bash -x
        echo 'ipsum' > /second_reboot"""
        aws_client.ec2.modify_instance_attribute(
            InstanceId=instance_id, Attribute="userData", Value=new_userdata
        )
        aws_client.ec2.reboot_instances(InstanceIds=[instance_id])
        retry(lambda: _assert_instance_status(instance_id, "running"), retries=10, sleep=1)
        retry(
            lambda: _assert_cat_file(container_name, CLOUD_INIT_LOG_PATH, "ipsum"),
            retries=20,
            sleep=2,
        )
        retry(
            lambda: _assert_cat_file(container_name, "/second_reboot", "ipsum"), retries=5, sleep=1
        )

    @markers.aws.only_localstack
    def test_create_instance_with_ebs_create_fs(
        self, ec2_test_ami, docker_mark_for_cleanup, aws_client, monkeypatch
    ):
        """Test that we can mount an EBS block device into an EC2 container, and create a writeable filesystem on it."""
        monkeypatch.setattr(docker, "MOUNT_BLOCK_DEVICES", True)

        # note: mounting onto well-known dirs like /dev/sda1 can lead to errors like
        # "/dev/sda1 is mounted; will not make a filesystem here" in CI, hence using a different path here.
        device_path = "/ebs-dev/sda1"
        disk_mount_point = "/ebs-mounted"

        user_data = f"""
        #!/bin/bash
        set -eo
        mkdir -p {disk_mount_point}
        mkfs -t ext3 {device_path}
        mount -o loop {device_path} {disk_mount_point}
        touch {disk_mount_point}/foobar
        """.strip()

        response = aws_client.ec2.run_instances(
            ImageId=ec2_test_ami[0],
            MinCount=1,
            MaxCount=1,
            BlockDeviceMappings=[
                {
                    "DeviceName": device_path,
                    "Ebs": {
                        # note: real AWS uses size in GB, we're using MB to avoid huge volume file sizes
                        "VolumeSize": 10
                    },
                }
            ],
            UserData=user_data,
        )["Instances"][0]
        instance_id = response["InstanceId"]
        docker_mark_for_cleanup(instance_id)

        def _assert_fs_exists():
            # exec into container, make sure file system is accessible and contains the created file
            container_name = DockerVmManager.container_name_from_instance_id(instance_id)
            stdout, _ = DOCKER_CLIENT.exec_in_container(
                container_name, ["ls", "-la", disk_mount_point]
            )
            assert "foobar" in to_str(stdout)

        retry(_assert_fs_exists, retries=15, sleep=1)

    @markers.aws.only_localstack
    def test_instance_metadata_service(
        self, ec2_test_ami, docker_mark_for_cleanup, aws_client, imds_endpoint
    ):
        user_data = """#!/bin/bash
        apt update && apt install -y curl
        """

        response = aws_client.ec2.run_instances(
            ImageId=ec2_test_ami[0], MinCount=1, MaxCount=1, UserData=user_data
        )
        instance_id = response["Instances"][0]["InstanceId"]
        container_name = DockerVmManager.container_name_from_instance_id(instance_id)
        docker_mark_for_cleanup(container_name)

        def _is_curl_installed():
            stdout, _ = DOCKER_CLIENT.exec_in_container(container_name, ["which", "curl"])
            assert "/curl" in to_str(stdout)

        retry(_is_curl_installed, retries=20, sleep=2)

        # Ensure API versions
        stdout, _ = DOCKER_CLIENT.exec_in_container(container_name, ["curl", imds_endpoint])
        assert to_str(stdout).strip() == "latest"

        # Ensure API paths
        stdout, _ = DOCKER_CLIENT.exec_in_container(
            container_name, ["curl", urljoin(imds_endpoint, "/latest/meta-data/")]
        )
        assert "ami-id" in to_str(stdout).strip()
        assert "instance-id" in to_str(stdout).strip()

        # Ensure API returns expected values
        # AMI ID
        stdout, _ = DOCKER_CLIENT.exec_in_container(
            container_name, ["curl", urljoin(imds_endpoint, "/latest/meta-data/ami-id/")]
        )
        assert to_str(stdout).strip() == ec2_test_ami[0]

        # Instance ID
        stdout, _ = DOCKER_CLIENT.exec_in_container(
            container_name, ["curl", urljoin(imds_endpoint, "/latest/meta-data/instance-id/")]
        )
        assert to_str(stdout).strip() == response["Instances"][0]["InstanceId"]


@pytest.mark.skipif(
    condition=ext_config.EC2_VM_MANAGER != "kubernetes",
    reason="Tests not applicable to active EC2 VM manager",
)
class TestEC2KubernetesVMM:
    @markers.aws.only_localstack
    def test_describe_instances(self, aws_client, ec2_test_ami):
        image_name, _ = ec2_test_ami

        user_data = """#!/bin/bash
        echo 'Hello World'"""

        response = aws_client.ec2.run_instances(
            ImageId=image_name, MinCount=1, MaxCount=1, UserData=user_data
        )
        assert len(response["Instances"]) == 1
        instance_id = response["Instances"][0]["InstanceId"]

        public_ip = response["Instances"][0]["PublicIpAddress"]
        public_dns = response["Instances"][0]["PublicDnsName"]
        assert public_dns.endswith(".localhost.localstack.cloud")

        # Ensure RunInstances and DescribeInstances return the same network addresses
        response = aws_client.ec2.describe_instances(InstanceIds=[instance_id])
        returned_ip_address = response["Reservations"][0]["Instances"][0]["PublicIpAddress"]
        returned_dns_name = response["Reservations"][0]["Instances"][0]["PublicDnsName"]
        assert public_ip == returned_ip_address
        assert public_dns == returned_dns_name

        # Must raise for invalid instances
        with pytest.raises(ClientError) as exc:
            aws_client.ec2.describe_instances(InstanceIds=["i-baadf00d"])

        err = exc.value.response["Error"]
        assert err["Code"] == "InvalidInstanceID.NotFound"
        assert err["Message"] == "The instance ID 'i-baadf00d' does not exist"

        vm_manager = VmManager.get_manager()
        assert isinstance(vm_manager, KubernetesVmManager)
        deployment_name = vm_manager.deployment_name_from_instance_id(instance_id)
        assert "User data script completed" in vm_manager.read_pod_logs_from_deployment(
            deployment_name
        )
        assert "Hello World" in vm_manager.get_cloud_init_output(deployment_name)

        # Test that StopInstances actually stops the instance
        expected_response = [
            {
                "CurrentState": {"Code": 80, "Name": "stopped"},
                "InstanceId": instance_id,
                "PreviousState": {"Code": 16, "Name": "running"},
            }
        ]
        response = aws_client.ec2.stop_instances(InstanceIds=[instance_id])
        assert response["StoppingInstances"] == expected_response

        response = aws_client.ec2.describe_instances(InstanceIds=[instance_id])
        inst_response = response["Reservations"][0]["Instances"][0]
        assert inst_response["ImageId"] == image_name
        assert inst_response["State"] == expected_response[0]["CurrentState"]

        # Test that StopInstances is idempotent
        expected_response = [
            {
                "CurrentState": {"Code": 80, "Name": "stopped"},
                "InstanceId": instance_id,
                "PreviousState": {"Code": 80, "Name": "stopped"},
            }
        ]
        response = aws_client.ec2.stop_instances(InstanceIds=[instance_id])
        assert response["StoppingInstances"] == expected_response

        # Test that StartInstances actually starts the instance
        response = aws_client.ec2.start_instances(InstanceIds=[instance_id])
        assert response["StartingInstances"][0]["PreviousState"]["Name"] == "stopped" and response[
            "StartingInstances"
        ][0]["CurrentState"]["Name"] in ["running", "pending"]

        response = aws_client.ec2.terminate_instances(InstanceIds=[instance_id])
        # Ignoring the previous state since it can either be "running" or "pending"
        assert response["TerminatingInstances"][0]["CurrentState"]["Name"] == "terminated"

        # The same instance should not be found any longer
        # TODO: AWS retains a representation of a terminated instance - this is not up to parity in the
        # Kubernetes implementation yet.
        with pytest.raises(ClientError) as exc:
            response = aws_client.ec2.terminate_instances(InstanceIds=[instance_id])
        assert exc.value.response["Error"]["Code"] == "InvalidInstanceID.NotFound"

        # A random instance should not be found either
        with pytest.raises(ClientError) as exc:
            aws_client.ec2.terminate_instances(InstanceIds=["i-1234567890"])
        assert exc.value.response["Error"]["Code"] == "InvalidInstanceID.NotFound"

        # Instances should not be able to be started again after termination
        with pytest.raises(ClientError) as exc:
            aws_client.ec2.start_instances(InstanceIds=[instance_id])
        assert exc.value.response["Error"]["Code"] == "InvalidInstanceID.NotFound"

        # Instances should not be able to be stopped after termination
        with pytest.raises(ClientError) as exc:
            aws_client.ec2.stop_instances(InstanceIds=[instance_id])
        assert exc.value.response["Error"]["Code"] == "InvalidInstanceID.NotFound"
