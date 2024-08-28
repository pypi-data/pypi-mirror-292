import json

import pytest
from localstack.pro.core.services.dms.exceptions import InvalidParameterValueException
from localstack.pro.core.services.dms.provider import _validate_table_mapping


class TestDmsReplicationTask:
    # TODO we could remove this test when the ckd test runs with LS
    def test_task_table_mapping(self):
        # tests exception and messages based on the snapshot recording
        # in tests/aws/scenario/dms_mariadb_kinesis/test_dms.py::TestDmsScenario::test_invalid_replication_task

        # test invalid table mapping (not json-formatted)
        with pytest.raises(InvalidParameterValueException) as e:
            _validate_table_mapping('{"rules": }')
        assert "Invalid Table Mappings document. Invalid json" == e.value.message

        # test invalid table mapping (valid json but unexpected format)
        with pytest.raises(InvalidParameterValueException) as e:
            _validate_table_mapping(json.dumps({"hello": "world"}))
        assert "Valid Table mappings is required" == e.value.message

        # test invalid table-mapping rule-type
        with pytest.raises(InvalidParameterValueException) as e:
            _validate_table_mapping(
                json.dumps(
                    {
                        "rules": [
                            {
                                "rule-type": "select",
                                "rule-id": "1",
                                "rule-name": "rule1",
                                "object-locator": {"schema-name": "testdb", "table-name": "Table%"},
                                "rule-action": "include",
                            }
                        ]
                    }
                )
            )
        assert "Invalid table mappings document." == e.value.message

        # test invalid table-mapping object-locator missing
        with pytest.raises(InvalidParameterValueException) as e:
            _validate_table_mapping(
                json.dumps(
                    {
                        "rules": [
                            {
                                "rule-type": "selection",
                                "rule-id": "1",
                                "rule-name": "rule1",
                                "rule-action": "include",
                            }
                        ]
                    }
                )
            )
        # TODO aws returns a very specific error message
        # but setting this up is a over-head in LS
        # msg: Error in mapping rules. Rule with ruleId = 1 failed validation. object locator cannot be null
        assert "Invalid table mappings document." == e.value.message

        # test invalid table-mapping rule-action
        with pytest.raises(InvalidParameterValueException) as e:
            _validate_table_mapping(
                json.dumps(
                    {
                        "rules": [
                            {
                                "rule-type": "selection",
                                "rule-id": "1",
                                "rule-name": "rule1",
                                "object-locator": {"schema-name": "testdb", "table-name": "Table%"},
                                "rule-action": "including",
                            }
                        ]
                    }
                )
            )
        assert "Invalid table mappings document." == e.value.message

        # rule-id and rule-name are not unique
        table_mapping = {
            "rules": [
                {
                    "rule-type": "selection",
                    "rule-id": "1",
                    "rule-name": "rule1",
                    "object-locator": {"schema-name": "testdb", "table-name": "Table%"},
                    "rule-action": "include",
                },
                {
                    "rule-type": "selection",
                    "rule-id": "1",
                    "rule-name": "rule1",
                    "object-locator": {"schema-name": "testdb", "table-name": "TableB"},
                    "rule-action": "exclude",
                },
            ]
        }
        with pytest.raises(InvalidParameterValueException) as e:
            _validate_table_mapping(json.dumps(table_mapping))
        assert "Error in mapping rules. Duplicate ruleid 1" == e.value.message

        # test a valid mapping to make sure the validation works
        table_mapping["rules"][1]["rule-id"] = 2  # test integer
        _validate_table_mapping(json.dumps(table_mapping))
