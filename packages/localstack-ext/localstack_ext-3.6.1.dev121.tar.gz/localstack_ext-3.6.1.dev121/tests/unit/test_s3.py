from unittest.mock import MagicMock

from localstack.pro.core import config as config_ext
from localstack.pro.core.services.s3.legacy.persistence import _SaveS3SnapshotVisitor
from localstack.pro.core.services.s3.legacy.s3_mount import BucketMountConfig, S3MountConfig
from localstack.pro.core.services.s3.s3_select_utils import (
    has_jsonpath_expressions,
    rewrite_json_query,
)
from localstack.services.stores import AccountRegionBundle


class TestS3Utilities:
    def test_has_jsonpath_expressions(self):
        def has(query, expected):
            result = has_jsonpath_expressions(query)
            assert result == expected

        has("test 123", False)
        has("SELECT s.* FROM s3object s", False)
        has("SELECT s.* FROM s3object[*][*] s", False)
        has("SELECT s[*][*] FROM s3object s", False)

    def test_rewrite_query(self):
        def rewrite(query, expected):
            result = rewrite_json_query(query)
            assert result == expected

        rewrite(
            "SELECT id FROM S3Object[*].Rules[*].id WHERE id IS NOT MISSING",
            "SELECT json_extract(json_each.value, '$.id') AS id "
            "FROM S3Object, json_each(S3Object.Rules) WHERE id IS NOT NULL",
        )

        rewrite(
            "SELECT id FROM S3Object[*].Rules",
            "SELECT json_each.value AS id FROM S3Object, json_each(S3Object.Rules)",
        )

        rewrite(
            "SELECT id FROM S3Object[*].Rules.foo.bar.id",
            "SELECT json_extract(json_each.value, '$.foo.bar.id') AS id FROM S3Object, json_each(S3Object.Rules)",
        )

        rewrite("SELECT s.* FROM s3object[*][*] s", "SELECT s.* FROM S3Object s")

        query = "SELECT json_extract(json_each.value, '$.id') as id FROM json_each(S3Object) WHERE id IS NOT NULL"
        rewrite(query, query)

        rewrite(
            "SELECT * FROM s3object[*] s WHERE s.\"Country (Name)\" LIKE '%United States%'",
            "SELECT * FROM S3Object s WHERE s.\"Country (Name)\" LIKE '%United States%'",
        )

    def test_parse_bucket_mount_config(self, monkeypatch):
        monkeypatch.setattr(config_ext, "S3_DIR", "/tmp/buckets")
        config = S3MountConfig.get()
        assert config.global_dir == "/tmp/buckets"

        monkeypatch.setattr(config_ext, "S3_DIR", "/tmp/buckets:b1")
        config = S3MountConfig.get()
        assert not config.global_dir
        assert config.buckets == {"b1": BucketMountConfig(mount_dir="/tmp/buckets")}

        for delimiter in [";", ","]:
            monkeypatch.setattr(config_ext, "S3_DIR", f"/tmp/b1:b1{delimiter} /tmp/b2:b2")
            config = S3MountConfig.get()
            assert not config.global_dir
            assert config.buckets == {
                "b1": BucketMountConfig(mount_dir="/tmp/b1"),
                "b2": BucketMountConfig(mount_dir="/tmp/b2"),
            }

        monkeypatch.setattr(config_ext, "S3_DIR", "/tmp/buckets:b1:opt1:opt2")
        config = S3MountConfig.get()
        assert not config.global_dir
        assert config.buckets == {
            "b1": BucketMountConfig(mount_dir="/tmp/buckets", options=["opt1", "opt2"])
        }


class TestS3PersistenceStateVisitors:
    def test_s3_save_snapshot_visitor_dispatches_stores_correctly(self):
        # whitebox test to make sure that calling visitor.visit works correctly with subclassing
        s3_marker = MagicMock()
        encoder = MagicMock()

        visitor = _SaveS3SnapshotVisitor("s3", "/tmp/s3", s3_marker)
        visitor.encoder = encoder

        from localstack.services.s3.models import S3Store

        s3_stores = AccountRegionBundle[S3Store]("s3", S3Store)

        visitor.visit(s3_stores)

        # see the Encoder.encode interface
        encoder.encode.assert_called()
        state_container, fd = encoder.encode.call_args_list[0].args
        assert state_container is s3_stores
        assert fd.name == "/tmp/s3/s3/store.state"

    def test_s3_save_snapshot_visitor_dispatches_moto_backends_correctly(self):
        # whitebox test to make sure that calling visitor.visit works correctly with subclassing
        s3_marker = MagicMock()
        s3_marker.get_and_clear_markers = MagicMock(return_value=["mybucket"])
        encoder = MagicMock()

        visitor = _SaveS3SnapshotVisitor("s3", "/tmp/s3", s3_marker)
        visitor.encoder = encoder

        from moto.s3.models import S3Backend, S3BackendDict
        from moto.utilities.utils import PARTITION_NAMES

        s3_backends = S3BackendDict(
            S3Backend,
            service_name="s3",
            use_boto3_regions=False,
            additional_regions=PARTITION_NAMES,
        )
        # trigger the lazy-creation of the backend
        global_backend = s3_backends["000000000000"]["aws"]

        visitor.visit(s3_backends)

        # when there are no buckets in the backend, there should be at least one call to encode with the
        # tagger
        encoder.encode.assert_called()
        state_container, fd = encoder.encode.call_args_list[0].args
        assert state_container is global_backend.tagger
        assert fd.name == "/tmp/s3/s3/000000000000/tagger.state"
