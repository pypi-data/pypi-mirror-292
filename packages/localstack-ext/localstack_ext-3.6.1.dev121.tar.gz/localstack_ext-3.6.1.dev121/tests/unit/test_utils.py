import pytest
from localstack.pro.core.utils.aws.endpoints import s3_aws_endpoint_to_localstack
from localstack.pro.core.utils.common import MultiKeyDict


class TestCommonUtils:
    def test_multi_key_dict(self):
        d = MultiKeyDict()

        # put item
        d["k1"] = "val1"
        assert d["k1"] == "val1"
        assert d.get("k1") == "val1"
        assert len(d) == 1

        # put another item
        d["k2"] = "val2"
        assert d["k2"] == "val2"
        assert d.get("k2") == "val2"
        assert len(d) == 2

        # set alias and assert value
        d.set_alias("k1", "k1_1")
        assert d["k1_1"] == "val1"
        assert len(d) == 2
        d.set_alias("k1", "k1_1")  # this should be a no-op

        # update aliased key and assert value
        d["k1"] = "val123"
        assert d["k1"] == "val123"
        assert d["k1_1"] == "val123"
        d["k1_1"] = "val1"
        assert d["k1"] == "val1"
        assert d["k1_1"] == "val1"

        # assert key/value iterators
        assert len(list(d.keys())) == 2
        assert set(d.values()) == {"val1", "val2"}
        assert "k1" in d
        assert "k1_1" in d
        assert "k2" in d
        assert "invalid" not in d

        # assert key errors
        with pytest.raises(KeyError):
            d.__getitem__("invalid")

        # assert pop behavior
        d["k3"] = "val234"
        d.set_alias("k3", "k3_1")
        assert d.pop("k3") == "val234"
        with pytest.raises(KeyError):
            d.pop("k3")
        with pytest.raises(KeyError):
            d.pop("k3_1")
        assert d.pop("k3", "default") == "default"

    def test_multi_key_persistence(self):
        import pickle

        d = MultiKeyDict()
        d["k1"] = "val1"
        d.set_alias("k1", "k1_1")
        assert "k1" in d
        pickled_dict = pickle.dumps(d)
        restored_dict = pickle.loads(pickled_dict)
        assert "k1" in restored_dict

    @pytest.mark.parametrize(
        "test_input, expected",
        [
            ("bucket-name.s3.us-west-2.amazonaws.com", "bucket-name.s3.localhost.localstack.cloud"),
            ("name.lb.us-west-2.amazonaws.com", ""),
        ],
    )
    def test_s3_endpoint_conversion(self, test_input, expected):
        assert s3_aws_endpoint_to_localstack(domain=test_input) == expected

    def test_list_dict_merging(self):
        from localstack.pro.core.utils.common import merge_list_dicts

        dict_1 = {
            "a": [1, 2, 3],
            "b": [4, 5, 6],
        }

        dict_2 = {
            "a": [7, 8, 9],
            "c": [10, 11, 12],
        }

        merged_dict = merge_list_dicts(dict_1, dict_2)

        assert merged_dict == {
            "a": [1, 2, 3, 7, 8, 9],
            "b": [4, 5, 6],
            "c": [10, 11, 12],
        }
