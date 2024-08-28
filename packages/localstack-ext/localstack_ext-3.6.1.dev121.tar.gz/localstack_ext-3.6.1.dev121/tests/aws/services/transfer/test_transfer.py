import io
import time
from ftplib import FTP, FTP_TLS

import pytest
from localstack.pro.core.bootstrap import ftp_server
from localstack.pro.core.bootstrap.ftp_server import FTP_USER_DEFAULT_PASSWD, FTP_USER_PERMISSIONS
from localstack.testing.pytest import markers
from localstack.utils.aws import arns, resources
from localstack.utils.files import new_tmp_dir
from localstack.utils.net import get_free_tcp_port
from localstack.utils.strings import short_uid, to_bytes

# on some systems, the domain name "localhost" causes issues in the FTP lib (e.g., in Gitlab-CI)
LOCALHOST_ADDR = "127.0.0.1"


class TestAWSTransfer:
    @staticmethod
    def _do_ftp_transfer(ftp):
        port = get_free_tcp_port()
        ftp_server.start_ftp(port)
        time.sleep(1)

        # connect to FTP server
        ftp.connect(LOCALHOST_ADDR, port=port)
        ftp.login(ftp_server.ROOT_USER[0], ftp_server.ROOT_USER[1])

        username = "user_%s" % short_uid()
        user_dir = new_tmp_dir()
        ftp.sendcmd(
            "SITE ADDUSER  {} {} {} {}".format(
                username, FTP_USER_DEFAULT_PASSWD, user_dir, FTP_USER_PERMISSIONS
            )
        )

        ftp.login(username, FTP_USER_DEFAULT_PASSWD)

        # list files before
        files_before = list(ftp.mlsd())

        # upload file
        file_name = "test.file"
        file_content = to_bytes("test \nHello world.")
        ftp.storbinary("STOR %s" % file_name, io.BytesIO(file_content))

        # download file and assert content matches
        down_file = io.BytesIO()
        result = ftp.retrbinary("RETR %s" % file_name, down_file.write)
        assert "226" in result
        assert "Transfer complete" in result
        assert down_file.getvalue() == file_content

        # list files and assert that file has been uploaded
        files = list(ftp.mlsd())
        assert len(files_before) + 1 == len(files)
        assert files[0][0] == file_name

        ftp.quit()

    @markers.skip_offline
    @markers.aws.unknown
    def test_ftp_transfer(self):
        self._do_ftp_transfer(FTP())

    @markers.skip_offline
    @markers.aws.unknown
    def test_ftp_ssl_transfer(self):
        self._do_ftp_transfer(FTP_TLS())

    @markers.aws.unknown
    def test_basic_transfer_api(self, aws_client, account_id, region_name):
        transfer = aws_client.transfer
        s3 = aws_client.s3

        username = "user_%s" % short_uid()
        bucket_name = "bucket-%s" % short_uid()

        public_key_body = (
            "AAAAB3NzaC1yc2EAAAADAQABAAABAQCOtfCAis3aHfM6yc8KWAlMQxVDBHyccCde9MdLf4D..."
        )
        role_arn = arns.iam_role_arn("test", account_id, region_name)

        rs = transfer.create_server(
            EndpointType="PUBLIC",
            IdentityProviderType="SERVICE_MANAGED",
            Protocols=[
                "FTP",
            ],
            Tags=[{"Key": "env", "Value": "Testing"}],
        )

        server_id = rs["ServerId"]
        port = int(server_id[-4:])

        rs = transfer.describe_server(ServerId=server_id)
        assert rs["Server"]["ServerId"] == server_id

        rs = transfer.list_users(ServerId=server_id)
        assert len(rs["Users"]) == 0

        # connect to FTP server
        ftp = FTP()
        ftp.connect(LOCALHOST_ADDR, port=port)

        with pytest.raises(Exception) as ctx:
            ftp.login(username, FTP_USER_DEFAULT_PASSWD)
        assert "Authentication failed." in str(ctx.value)

        resources.create_s3_bucket(bucket_name, s3_client=s3)
        result = transfer.create_user(
            ServerId=server_id,
            HomeDirectory=bucket_name,
            HomeDirectoryType="PATH",
            Role=role_arn,
            UserName=username,
        )
        assert result["ServerId"] == server_id

        rs = transfer.list_users(ServerId=server_id)
        assert len(rs["Users"]) == 1
        assert rs["Users"][0]["UserName"] == username
        assert rs["Users"][0]["SshPublicKeyCount"] == 0

        # connect to FTP server
        rs = ftp.login(username, FTP_USER_DEFAULT_PASSWD)
        assert "Login successful." in rs

        file_name = "test-%s.txt" % short_uid()
        file_content = to_bytes('title "Test" \nfile content!!')

        # upload file to root dir
        ftp.storbinary("STOR %s" % file_name, io.BytesIO(file_content))
        time.sleep(1)

        rs = s3.get_object(Bucket=bucket_name, Key=file_name)
        assert rs["ContentLength"] == len(file_content)
        assert rs["Body"].read() == file_content

        # upload file to sub dir
        subdir = "subdir"
        ftp.mkd(subdir)
        ftp.cwd(subdir)
        ftp.storbinary("STOR %s" % file_name, io.BytesIO(file_content))
        time.sleep(1)

        rs = s3.get_object(Bucket=bucket_name, Key="{}/{}".format(subdir, file_name))
        assert rs["ContentLength"] == len(file_content)
        assert rs["Body"].read() == file_content

        ftp.quit()

        # import public keys
        rs = transfer.import_ssh_public_key(
            ServerId=server_id, UserName=username, SshPublicKeyBody=public_key_body
        )

        ssh_public_key_id = rs["SshPublicKeyId"]

        rs = transfer.describe_user(ServerId=server_id, UserName=username)

        assert len(rs["User"]["SshPublicKeys"]) == 1
        assert rs["User"]["SshPublicKeys"][0]["SshPublicKeyBody"] == public_key_body

        transfer.delete_ssh_public_key(
            ServerId=server_id, UserName=username, SshPublicKeyId=ssh_public_key_id
        )

        rs = transfer.describe_user(ServerId=server_id, UserName=username)
        assert rs["User"]["HomeDirectory"] == bucket_name
        assert rs["User"]["HomeDirectoryType"] == "PATH"
        assert len(rs["User"]["SshPublicKeys"]) == 0

        # update user
        transfer.update_user(
            HomeDirectory="test-bucket/home/prod",
            HomeDirectoryType="LOGICAL",
            ServerId=server_id,
            UserName=username,
        )

        rs = transfer.describe_user(ServerId=server_id, UserName=username)
        assert rs["User"]["HomeDirectory"] == "test-bucket/home/prod"
        assert rs["User"]["HomeDirectoryType"] == "LOGICAL"

        # clean up user
        transfer.delete_user(ServerId=server_id, UserName=username)

        rs = transfer.list_users(ServerId=server_id)
        assert len(rs["Users"]) == 0

        # clean up server
        transfer.delete_server(ServerId=server_id)

        with pytest.raises(Exception) as ctx:
            transfer.describe_server(ServerId=server_id)
        assert "ResourceNotFoundException" in str(ctx.value)
