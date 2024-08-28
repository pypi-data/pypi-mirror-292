from localstack.pro.core.services.ec2.utils import (
    get_dns_name,
    is_multipart_user_data,
    parse_multipart_user_data,
)
from localstack.utils.strings import to_str

PLAIN_USER_DATA = """
#!/bin/bash
echo "Created by bash shell script" >> /test-userscript/userscript.txt
""".strip("\n")

MULTIPART_USER_DATA = """
Content-Type: multipart/mixed; boundary=//
MIME-Version: 1.0

--//
Content-Type: text/x-shellscript; charset="us-ascii"
MIME-Version: 1.0
Content-Transfer-Encoding: 7bit
Content-Disposition: attachment; filename="userdata.txt"

#!/bin/bash
echo "Created by bash shell script" >> /test-userscript/userscript.txt

--//
""".strip("\n")


# https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/user-data.html
MULTIPART_USER_DATA_WITH_CLOUD_CONFIG = """
Content-Type: multipart/mixed; boundary="//"
MIME-Version: 1.0

--//
Content-Type: text/cloud-config; charset="us-ascii"
MIME-Version: 1.0
Content-Transfer-Encoding: 7bit
Content-Disposition: attachment; filename="cloud-config.txt"

#cloud-config
runcmd:
 - [ mkdir, /test-cloudinit ]
write_files:
 - path: /test-cloudinit/cloud-init.txt
   content: Created by cloud-init

--//
Content-Type: text/x-shellscript; charset="us-ascii"
MIME-Version: 1.0
Content-Transfer-Encoding: 7bit
Content-Disposition: attachment; filename="userdata.txt"

#!/bin/bash
  mkdir test-userscript
  touch /test-userscript/userscript.txt
  echo "Created by bash shell script" >> /test-userscript/userscript.txt
--//--
""".strip("\n")


def test_is_multipart_user_data():
    assert is_multipart_user_data(PLAIN_USER_DATA) is False

    assert is_multipart_user_data(MULTIPART_USER_DATA) is True

    assert is_multipart_user_data(MULTIPART_USER_DATA_WITH_CLOUD_CONFIG) is True


def test_parse_multipart_user_data_with_plain_user_data():
    user_data, cloud_config = parse_multipart_user_data(PLAIN_USER_DATA)

    assert to_str(user_data) == PLAIN_USER_DATA
    assert cloud_config is None


def test_test_parse_multipart_user_data_with_multipart_user_data():
    user_data, cloud_config = parse_multipart_user_data(MULTIPART_USER_DATA)

    assert to_str(user_data).startswith("#!/bin/bash")
    assert cloud_config is None


def test_test_parse_multipart_user_data_with_multipart_user_data_and_cloud_config():
    user_data, cloud_config = parse_multipart_user_data(MULTIPART_USER_DATA_WITH_CLOUD_CONFIG)

    assert to_str(user_data).startswith("#!/bin/bash")
    assert to_str(cloud_config).startswith("#cloud-config")


def test_get_dns_name():
    assert get_dns_name("10.244.0.10", "us-east-1") == "ec2-10-244-0-10.localhost.localstack.cloud"
    assert (
        get_dns_name("10.244.0.10", "ap-south-1")
        == "ec2-10-244-0-10.ap-south-1.localhost.localstack.cloud"
    )
