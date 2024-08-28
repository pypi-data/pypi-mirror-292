import pytest
from localstack.pro.core.services.dms.replication_task.dms_models import ControlEventOperation
from localstack.pro.core.services.dms.replication_task.mariadb.utils import get_columns_from_query
from localstack.pro.core.services.dms.replication_task.utils import get_allowed_schema_tables


def test_get_allowed_schema_tables():
    db_name = "testdb"
    values = [
        (db_name, "authors"),
        (db_name, "accounts"),
        (db_name, "books"),
        ("TEST", "test"),
    ]

    rules = [
        {
            "rule-type": "selection",
            "rule-id": "1",
            "rule-name": "rule1",
            "object-locator": {"schema-name": db_name, "table-name": "%"},
            "rule-action": "include",
        },
        {
            "rule-type": "selection",
            "rule-id": "2",
            "rule-name": "rule2",
            "object-locator": {"schema-name": db_name, "table-name": "books"},
            "rule-action": "exclude",
        },
    ]

    filtered = get_allowed_schema_tables(rules, values)

    assert sorted(filtered) == [("testdb", "accounts"), ("testdb", "authors")]

    rules = [
        {
            "rule-type": "selection",
            "rule-id": "1",
            "rule-name": "rule1",
            "object-locator": {"table-name": "test_[a-z]able"},
            "rule-action": "include",
        },
        {
            "rule-type": "selection",
            "rule-id": "2",
            "rule-name": "rule2",
            "object-locator": {"table-name": "test_%_test"},
            "rule-action": "include",
        },
    ]

    values = [
        (db_name, "authors"),
        (db_name, "accounts"),
        (db_name, "books"),
        ("TEST", "test"),
        ("TEST", "test_table"),
        ("TEST", "test_table_test"),
        ("TEST", "test_random_test"),
        ("TEST", "test_1able"),
    ]

    filtered = get_allowed_schema_tables(rules, values)
    assert sorted(filtered) == [
        ("TEST", "test_random_test"),
        ("TEST", "test_table"),
        ("TEST", "test_table_test"),
    ]


@pytest.mark.parametrize(
    "op,query,columns",
    [
        (
            ControlEventOperation.AddColumn,
            "ALTER TABLE test ADD COLUMN is_tested BOOLEAN DEFAULT TRUE;",
            ["is_tested"],
        ),
        (
            ControlEventOperation.ChangeColumns,
            "ALTER TABLE test_users CHANGE COLUMN active active_user varchar(10);",
            ["active", "active_user"],
        ),
        (
            ControlEventOperation.ChangeColumns,
            "ALTER TABLE pigeons CHANGE COLUMN feather_count wingspan DOUBLE;",
            ["feather_count", "wingspan"],
        ),
        (
            ControlEventOperation.ColumnTypeChange,
            "ALTER TABLE books MODIFY COLUMN isbn VARCHAR(30);",
            ["isbn"],
        ),
        (
            ControlEventOperation.DropColumn,
            "ALTER TABLE accounts DROP COLUMN profile_picture;",
            ["profile_picture"],
        ),
        (
            ControlEventOperation.RenameColumn,
            "ALTER TABLE test_customers RENAME COLUMN name to full_name;",
            ["name", "full_name"],
        ),
        (
            ControlEventOperation.ColumnTypeChange,
            "ALTER TABLE accounts MODIFY age INTEGER UNSIGNED;",
            ["age"],
        ),
        # wrong query now for negative testing
    ],
)
def test_alter_query_column_parser(op, query, columns):
    assert get_columns_from_query(op, query) == columns
