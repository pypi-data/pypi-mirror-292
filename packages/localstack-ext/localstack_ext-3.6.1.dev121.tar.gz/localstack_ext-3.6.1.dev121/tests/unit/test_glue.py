from typing import Dict

import pytest
from localstack.pro.core.aws.api.glue import Table
from localstack.pro.core.services.glue.crawler_utils import (
    extract_partitions,
    get_s3_bucket_and_path,
    infer_data_type,
    is_s3_subpath_prefix,
)
from localstack.pro.core.services.glue.hive_utils import (
    InvalidTableLocation,
    construct_create_table_query,
)
from localstack.pro.core.services.glue.job_executor import JobArguments


class TestCrawler:
    @staticmethod
    def _assert(path: str, expected_partitions: Dict[str, str], prefix=None):
        result = extract_partitions(path, prefix=prefix)
        for key, value in expected_partitions.items():
            assert result.get(key)
            assert result[key] == value

    def test_named_partitions(self):
        self._assert(
            "sales/year=2019/month=Jan/day=1/part1.json",
            {
                "year": "2019",
                "month": "Jan",
                "day": "1",
            },
        )

    def test_unnamed_partitions_with_prefix(self):
        self._assert(
            "examples/githubarchive/month/data/2017/01/02/part1.json",
            {
                "partition_0": "2017",
                "partition_1": "01",
                "partition_2": "02",
            },
            "examples/githubarchive/month/data/",
        )

    def test_unnamed_partitions_without_prefix(self):
        self._assert(
            "examples/githubarchive/month/data/2017/01/02/part1.json",
            {
                "partition_0": "examples",
                "partition_1": "githubarchive",
                "partition_2": "month",
                "partition_3": "data",
                "partition_4": "2017",
                "partition_5": "01",
                "partition_6": "02",
            },
        )

    def test_infer_data_type_without_conversion(self):
        assert infer_data_type([]) == "string"
        assert infer_data_type([1, 2, 3]) == "int"
        assert infer_data_type([1, "2", "abc"]) == "string"
        assert infer_data_type([1, 2, 3.4]) == "double"
        assert infer_data_type([True, False, False]) == "boolean"
        assert infer_data_type([True, False, "foobar"]) == "string"
        assert infer_data_type([1, 2, True]) == "string"
        assert infer_data_type([1646172627000000, 1652780743000000, 3]) == "bigint"

    def test_infer_data_type_with_conversion(self):
        assert infer_data_type([], convert=True) == "string"
        assert infer_data_type(["1", "2", "3"], convert=True) == "int"
        assert infer_data_type(["1", "2", "abc"], convert=True) == "string"
        assert infer_data_type(["1", "2", "3.4"], convert=True) == "double"
        assert infer_data_type(["true", "false", "false"], convert=True) == "boolean"
        assert infer_data_type(["true", "false", "foobar"], convert=True) == "string"
        assert infer_data_type(["1", "2", "true"], convert=True) == "string"
        assert (
            infer_data_type(["1646172627000000", "1652780743000000", "3"], convert=True) == "bigint"
        )

    def test_s3_crawler_paths(self):
        assert get_s3_bucket_and_path("s3://foo") == ("foo", "/")
        assert get_s3_bucket_and_path("s3://foo/") == ("foo", "/")
        assert get_s3_bucket_and_path("s3://foo-123/bar") == ("foo-123", "/bar")
        assert get_s3_bucket_and_path("foo") == ("foo", "/")

        assert not get_s3_bucket_and_path("http://test")
        assert not get_s3_bucket_and_path("jdbc:test")
        assert not get_s3_bucket_and_path("")

    @pytest.mark.parametrize("double_slashes_child", [True, False])
    @pytest.mark.parametrize("double_slashes_parent", [True, False])
    @pytest.mark.parametrize("child_strip", [True, False])
    @pytest.mark.parametrize("parent_strip", [True, False])
    def test_subpath_prefixes(
        self, double_slashes_child, double_slashes_parent, child_strip, parent_strip
    ):
        def _subpath_prefix(child, parent):
            child = child.replace("/", "//") if double_slashes_child else child
            parent = parent.replace("/", "//") if double_slashes_parent else parent
            child = child.lstrip("/") if child_strip else child
            parent = parent.lstrip("/") if parent_strip else parent
            return is_s3_subpath_prefix(child, parent)

        assert _subpath_prefix("/", "/")
        assert _subpath_prefix("/foo/bar", "/")
        assert _subpath_prefix("/foo/bar", "/foo")
        assert _subpath_prefix("/foo/bar", "/foo/bar")
        assert _subpath_prefix("/foo/bar", "/foo/bar/")

        assert not _subpath_prefix("/foo", "/bar")
        assert not _subpath_prefix("/", "/bar")


class TestQueries:
    @pytest.mark.parametrize("location_prefix", ["s3://", "s3a://", ""])
    @pytest.mark.parametrize("location_suffix", ["", "/"])
    @pytest.mark.parametrize("location_path", ["", "/test", "/path/to/key"])
    def test_create_table_with_s3_location(self, location_prefix, location_suffix, location_path):
        location = f"{location_prefix}bucket123{location_path}{location_suffix}"
        table = Table(DatabaseName="db1", Name="table1", StorageDescriptor={"Location": location})

        if (location.startswith("s3://") or location.startswith("s3a://")) and (
            location_suffix or location_path
        ):
            result = construct_create_table_query(table)
            assert f"LOCATION '{location}'" in result
        else:
            with pytest.raises(InvalidTableLocation):
                construct_create_table_query(table)


class TestJobs:
    def test_user_job_arguments(self):
        run_details = {
            "JobName": "j-1d5c120b",
            "Arguments": {
                "--logging_level": "DEBUG",
                "__breck_s3_bucket": "test",
                "test": "test_new_value",
            },
        }
        job_args = JobArguments({}, run_details)
        args = job_args.get_user_vars()
        assert len(args) == 3
