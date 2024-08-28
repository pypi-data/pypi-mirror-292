import os.path
import zipfile

import pytest
from localstack.pro.core.persistence.utils.encryption import OpenSSLPasswordEncryptor
from localstack.pro.core.persistence.utils.sort import DefaultPrioritySorter
from localstack.utils.strings import short_uid


@pytest.fixture
def temp_zip_file(tmp_path):
    temp_dir = tmp_path / "temp_dir"
    temp_dir.mkdir()

    temp_zip_path = temp_dir / "tmp.zip"
    with zipfile.ZipFile(temp_zip_path, "w") as f:
        tmp_file = temp_dir / "file1.txt"
        tmp_file.write_text("some content")
        f.write(tmp_file)

    return temp_zip_path


def test_s3_order():
    sorter = DefaultPrioritySorter()
    services = ["lambda", "s3", "stepfunctions", "sqs"]
    output = sorter.sort_services(services)
    assert output[0] == "s3"


def test_empty_list():
    sorter = DefaultPrioritySorter()
    assert not sorter.sort_services([])


def test_pod_encryption(temp_zip_file, tmp_path):
    out_path = tmp_path / "out"
    assert zipfile.is_zipfile(temp_zip_file)
    key = f"key-{short_uid()}"
    encryptor = OpenSSLPasswordEncryptor(secret=key)
    encryptor.encrypt(_in=temp_zip_file, _out=out_path)
    assert os.path.exists(out_path), "encrypted output does not exist"
    assert not zipfile.is_zipfile(out_path)

    decrypt_path = tmp_path / "decr"
    encryptor.decrypt(_in=out_path, _out=decrypt_path)
    assert os.path.exists(decrypt_path)
    assert zipfile.is_zipfile(decrypt_path)

    decr_output = zipfile.ZipFile(decrypt_path, "r")
    assert "file1.txt" in decr_output.namelist()[0]


def test_encryption_wrong_passphrase(temp_zip_file, tmp_path):
    out_path = tmp_path / "out"
    key = f"key-{short_uid()}"
    encryptor = OpenSSLPasswordEncryptor(secret=key)
    encryptor.encrypt(_in=temp_zip_file, _out=out_path)

    decrypt_path = tmp_path / "decr"
    encryptor.secret = "wrong-secret"
    with pytest.raises(Exception):
        encryptor.decrypt(_in=out_path, _out=decrypt_path)
