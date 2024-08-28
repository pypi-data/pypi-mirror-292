import os

import pytest
from botocore.exceptions import ClientError
from localstack import config
from localstack.pro.core import config as config_ext
from localstack.testing.pytest import markers
from localstack.utils.aws import resources
from localstack.utils.collections import select_attributes
from localstack.utils.files import mkdir, save_file
from localstack.utils.strings import short_uid


class TestS3:
    @pytest.mark.skipif(
        reason="Streaming/native providers do not support mounting buckets",
        condition=not config.LEGACY_V2_S3_PROVIDER,
    )
    @pytest.mark.parametrize("global_dir", [True, False])
    @markers.aws.only_localstack
    def test_bucket_mounting(self, tmpdir, global_dir, monkeypatch, aws_client):
        prefix = f"s-{short_uid()}"
        content = "test content 123"

        if global_dir:
            monkeypatch.setattr(config_ext, "S3_DIR", tmpdir)
        else:
            monkeypatch.setattr(config_ext, "S3_DIR", f"{tmpdir}/{prefix}-1:{prefix}-1")

        # set up filesystem layout - 3 buckets with one test object each
        for bucket in [f"{prefix}-1", f"{prefix}-2", f"{prefix}-3"]:
            path = os.path.join(tmpdir, bucket, "my/path")
            mkdir(path)
            save_file(os.path.join(path, "testfile"), content)

        def _bucket_exists(bucket_name):
            buckets = [b["Name"] for b in aws_client.s3.list_buckets()["Buckets"]]
            return bucket_name in buckets

        # list buckets
        assert _bucket_exists(f"{prefix}-1")
        assert _bucket_exists(f"{prefix}-2") == global_dir

        # create bucket
        resources.create_s3_bucket(f"{prefix}-new")
        assert _bucket_exists(f"{prefix}-new")

        # list objects
        objects = aws_client.s3.list_objects(Bucket=f"{prefix}-1")["Contents"]
        objects = [select_attributes(o, ["Key", "Size"]) for o in objects]
        assert objects == [{"Key": "my/path/testfile", "Size": len(content)}]

        # put object
        objects = aws_client.s3.list_objects(Bucket=f"{prefix}-new").get("Contents", [])
        assert objects == []
        content_new = "foobar"
        aws_client.s3.put_object(Bucket=f"{prefix}-new", Key="my/path/testfile2", Body=content_new)
        objects = aws_client.s3.list_objects(Bucket=f"{prefix}-new")["Contents"]
        objects = [select_attributes(o, ["Key", "Size"]) for o in objects]
        assert objects == [{"Key": "my/path/testfile2", "Size": len(content_new)}]
        assert (
            os.path.exists(os.path.join(tmpdir, f"{prefix}-new", "my/path/testfile2")) == global_dir
        )

        # put object in mounted bucket
        aws_client.s3.put_object(Bucket=f"{prefix}-1", Key="my/path/testfile2", Body=content_new)
        assert len(aws_client.s3.list_objects(Bucket=f"{prefix}-1")["Contents"]) == 2

        # delete buckets/objects
        with pytest.raises(Exception) as e:
            # should raise an exception if bucket still contains contents
            aws_client.s3.delete_bucket(Bucket=f"{prefix}-new")
        assert e.match("BucketNotEmpty")
        aws_client.s3.delete_object(Bucket=f"{prefix}-new", Key="my/path/testfile2")
        aws_client.s3.delete_bucket(Bucket=f"{prefix}-new")
        assert not _bucket_exists(f"{prefix}-new")
        assert f"{prefix}-new" not in os.listdir(tmpdir)

    @markers.aws.validated
    def test_object_key_length(self, aws_client, s3_bucket, snapshot):
        # https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-keys.html
        # TODO: once the feature flag `S3_TRUNCATE_KEYS` is fully removed from -ext, move this test to community
        key_name_1000 = "/".join(["a" * 100 for _ in range(10)])
        put_obj_1000_len = aws_client.s3.put_object(
            Bucket=s3_bucket, Key=key_name_1000, Body="test"
        )
        snapshot.match("object-key-length-1000", put_obj_1000_len)

        get_obj_1000_len = aws_client.s3.get_object(Bucket=s3_bucket, Key=key_name_1000)
        snapshot.match("get-object-key-length-1000", get_obj_1000_len)

        key_name_300 = "a" * 300
        put_obj_300_between_slashes = aws_client.s3.put_object(
            Bucket=s3_bucket, Key=key_name_300, Body="test"
        )
        snapshot.match("object-key-length-300-between-slashes", put_obj_300_between_slashes)

        get_obj_300_between_slashes = aws_client.s3.get_object(Bucket=s3_bucket, Key=key_name_300)
        snapshot.match("get-object-key-length-300-between-slashes", get_obj_300_between_slashes)

        key_name_550_small_dir = "/".join(["a" * 10 for _ in range(50)])
        put_obj_550_small_dir = aws_client.s3.put_object(
            Bucket=s3_bucket, Key=key_name_550_small_dir, Body="test"
        )
        snapshot.match("object-key-length-550-small-dir", put_obj_550_small_dir)

        get_obj_550_small_dir = aws_client.s3.get_object(
            Bucket=s3_bucket, Key=key_name_550_small_dir
        )
        snapshot.match("get-object-key-length-550-small-dir", get_obj_550_small_dir)

        with pytest.raises(ClientError) as e:
            key_name_1030 = "/".join(["a" * 103 for _ in range(10)])
            aws_client.s3.put_object(Bucket=s3_bucket, Key=key_name_1030, Body="test")
        snapshot.match("object-key-length-1030", e.value.response)

        key_name_1024 = "a" * 1024
        put_object_1024 = aws_client.s3.put_object(Bucket=s3_bucket, Key=key_name_1024, Body="test")
        snapshot.match("object-key-length-1024", put_object_1024)

        with pytest.raises(ClientError) as e:
            key_name_1025 = "a" * 1025
            aws_client.s3.put_object(Bucket=s3_bucket, Key=key_name_1025, Body="test")
        snapshot.match("object-key-length-1025", e.value.response)

        with pytest.raises(ClientError) as e:
            key_name_1030 = "/".join(["ä" * 103 for _ in range(10)])
            aws_client.s3.put_object(Bucket=s3_bucket, Key=key_name_1030, Body="test")
        snapshot.match("object-key-length-1030-special-char", e.value.response)

        with pytest.raises(ClientError) as e:
            key_name_1025 = "a" * 1025
            aws_client.s3.put_object(Bucket=s3_bucket, Key=key_name_1025, Body="test")
            aws_client.s3.copy_object(
                Bucket=s3_bucket, Key=key_name_1025, CopySource=f"{s3_bucket}/{key_name_300}"
            )
        snapshot.match("copy-object-key-length-1025", e.value.response)
