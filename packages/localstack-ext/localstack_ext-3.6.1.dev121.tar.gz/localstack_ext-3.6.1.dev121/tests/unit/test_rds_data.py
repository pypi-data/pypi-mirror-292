from localstack.pro.core.services.rds_data.provider import format_metadata


class TestRDSData:
    def test_format_metadata(self):
        pg_column_metadata = {
            "table_name": "",
            "udt_name": "int4",
            "column_name": "?column?",
            "is_nullable": "YES",
            "schemaName": "",
            "isAutoIncrement": False,
        }

        formatted = format_metadata(pg_column_metadata)

        assert formatted == {
            "name": "?column?",
            "tableName": "",
            "typeName": "int4",
            "arrayBaseColumnType": 0,
            "isCurrency": False,
            "label": "?column?",
            "nullable": 1,
            "schemaName": "",
            "isAutoIncrement": False,
        }

        pg_column_metadata["is_nullable"] = "NO"
        pg_column_metadata["isAutoIncrement"] = True
        pg_column_metadata["column_default"] = "nextval"

        formatted = format_metadata(pg_column_metadata)

        assert formatted == {
            "name": "?column?",
            "tableName": "",
            "typeName": "serial",
            "arrayBaseColumnType": 0,
            "isCurrency": False,
            "label": "?column?",
            "nullable": 0,
            "schemaName": "",
            "isAutoIncrement": True,
        }
