import time

from localstack.pro.core.services.iot_data.provider import (
    _calculate_delta,
    _create_metadata_for_update,
    _delete_empty_nodes,
    _merge_state,
)


class TestIotShadow:
    def test_flat_delta_calculation(self):
        desired = {"key_1": "value_1", "key_2": "value_2"}
        reported = {"key_1": "value_1", "key_2": "other_value_2", "key_3": "other_value_3"}
        delta = _calculate_delta(desired, reported)
        reported.update(delta)
        assert desired.items() <= reported.items()
        assert "key_1" not in delta
        assert "key_2" in delta
        assert "key_3" not in delta
        assert "key_3" in reported
        assert delta == {"key_2": "value_2"}

    def test_nested_delta_calculation(self):
        desired = {"apa": "bipa", "ipa": {"dupa": {"dapa": "epa", "kappa": "vepa"}}}
        reported = {"apa": "bepa", "ipa": {"dupa": {"kappa": "vepa"}}}

        delta = _calculate_delta(desired, reported)
        assert delta == {"apa": "bipa", "ipa": {"dupa": {"dapa": "epa"}}}

        desired = {"apa": "bipa", "ipa": {"dupa": {"dapa": "epa", "kappa": "vepa"}}}
        reported = {"apa": "bipa", "ipa": {"dupa": {"dapa": "epa", "kappa": "vepa"}}}

        delta = _calculate_delta(desired, reported)
        assert not delta

        desired = {"apa": "bipa", "ipa": {"dupa": {"dapa": "epa", "kappa": "vepa"}}}
        reported = {"apa": "bipa", "ipa": {"dupa": {"dapa": "pepa", "kappa": "vepa"}}}

        delta = _calculate_delta(desired, reported)
        assert delta == {"ipa": {"dupa": {"dapa": "epa"}}}
        desired = {"apa": "bipa", "ipa": {"dupa": {"dapa": "epa", "kappa": "vepa"}}}
        reported = {"apa": "bipa", "ipa": "kappa"}

        delta = _calculate_delta(desired, reported)
        assert delta == {"ipa": {"dupa": {"dapa": "epa", "kappa": "vepa"}}}
        desired = {"apa": "bipa", "ipa": {"dupa": {"dapa": "epa"}}}
        reported = {"apa": "bipa", "ipa": {"dupa": {"dapa": "epa", "kappa": "vepa"}}}

        delta = _calculate_delta(desired, reported)
        assert not delta

    @staticmethod
    def _assert_flat_metadata_dict(metadata_dict):
        assert "key_1" in metadata_dict
        assert "key_2" in metadata_dict
        assert "timestamp" in metadata_dict["key_1"]
        assert "timestamp" in metadata_dict["key_2"]
        assert time.time() - metadata_dict["key_1"]["timestamp"] < 2
        assert time.time() - metadata_dict["key_2"]["timestamp"] < 2

    def test_create_metadata(self):
        start_dict = {"key_1": "value_1", "key_2": "value_2"}
        metadata_dict = _create_metadata_for_update(start_dict, calculate_for_empty=True)
        self._assert_flat_metadata_dict(metadata_dict)

    def test_create_metadata_nested(self):
        start_dict = {"desired": {"key_1": "value_1", "key_2": "value_2"}}
        metadata_dict = _create_metadata_for_update(start_dict, calculate_for_empty=True)
        assert "key_1" in metadata_dict["desired"]
        assert "key_2" in metadata_dict["desired"]
        self._assert_flat_metadata_dict(metadata_dict["desired"])

        start_dict = {
            "desired": {"key_1": "value_1", "key_2": {"key_2_1": {"key_2_1_1": "value_2_1_1"}}}
        }
        metadata_dict = _create_metadata_for_update(start_dict, calculate_for_empty=True)
        assert "key_1" in metadata_dict["desired"]
        assert "key_2" in metadata_dict["desired"]
        assert "timestamp" in metadata_dict["desired"]["key_2"]["key_2_1"]["key_2_1_1"]

    def test_create_metadata_nested_with_none_values(self):
        start_dict = {"desired": {"key_1": "value_1", "key_2": None}}
        metadata_dict = _create_metadata_for_update(start_dict, calculate_for_empty=False)
        assert "key_1" in metadata_dict["desired"]
        assert "key_2" in metadata_dict["desired"]
        assert metadata_dict["desired"]["key_2"] is None
        assert "timestamp" in metadata_dict["desired"]["key_1"]
        metadata_dict = _create_metadata_for_update(start_dict, calculate_for_empty=True)
        assert "key_1" in metadata_dict["desired"]
        assert "key_2" in metadata_dict["desired"]
        assert "timestamp" in metadata_dict["desired"]["key_1"]
        assert "timestamp" in metadata_dict["desired"]["key_2"]

    def test_merge_state(self):
        state_1 = {"reported": {"foo": "bar", "some": "value"}}
        new_state = {"reported": {"foo": "blah", "other": "someval"}}
        merged = _merge_state(state_1, new_state)
        assert "reported" in merged
        assert "foo" in merged["reported"]
        assert "blah" == merged["reported"]["foo"]
        assert "some" in merged["reported"]
        assert "value" == merged["reported"]["some"]
        assert "someval" == merged["reported"]["other"]

    def test_delete_empty_values(self):
        state = {"reported": {"someval": None}}
        deleted = _delete_empty_nodes(state)
        assert not deleted
        state = {"reported": {"someval": "", "otherval": 0}}
        deleted = _delete_empty_nodes(state)
        assert "reported" in deleted
        assert {"someval": "", "otherval": 0} == deleted["reported"]
        state = {"reported": {"someval": None}, "desired": {"otherval": "somevalue"}}
        deleted = _delete_empty_nodes(state)
        assert "reported" not in deleted
        assert "desired" in deleted
        assert {"otherval": "somevalue"} == deleted["desired"]
