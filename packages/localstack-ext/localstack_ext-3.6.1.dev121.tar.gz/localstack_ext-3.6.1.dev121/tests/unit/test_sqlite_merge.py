import json
import shutil
import sqlite3
from typing import List, Set, Tuple

from localstack.pro.core.persistence.pods.merge.state_merge_ddb import deep_merge_sqlite_dbs
from localstack.utils.files import new_tmp_file
from localstack.utils.strings import to_bytes

from tests.aws.fixtures import skip_in_ci


class DBCon:
    def __init__(self, file_path: str):
        self._file_path = file_path
        self._con: sqlite3.Connection = sqlite3.connect(file_path)
        self.cur: sqlite3.Cursor = self._con.cursor()

    def commit_and_close(self):
        self._con.commit()
        self.close()

    def close(self):
        self.cur.close()
        self._con.close()

    def reconnect(self):
        self._con: sqlite3.Connection = sqlite3.connect(self._file_path)
        self.cur: sqlite3.Cursor = self._con.cursor()

    @staticmethod
    def sql_get_table_names() -> str:
        return "SELECT name FROM sqlite_master WHERE type='table';"

    def assert_table_names(self, table_names: Set[str]):
        self.cur.execute(self.sql_get_table_names())
        names: List[Tuple[str]] = self.cur.fetchall()
        assert {x[0] for x in names} == table_names

    @staticmethod
    def sql_select_all_from(table_name: str) -> str:
        return f'SELECT * FROM "{table_name}";'

    def assert_records(self, table_name: str, records: Set[Tuple]):
        self.cur.execute(self.sql_select_all_from(table_name))
        record_specs: List[Tuple] = self.cur.fetchall()
        assert set(record_specs) == records

    @staticmethod
    def sql_add_attribute(table_name: str, col_stmt: str) -> str:
        return f'ALTER TABLE "{table_name}" ADD {col_stmt};'

    def add_attribute(self, table_name: str, col_stmt: str):
        self.cur.execute(self.sql_add_attribute(table_name, col_stmt))

    def assert_schema_contains(self, stmt):
        def norm_sql_stmt(s: str):
            if s:
                return s.strip().replace("'", '"').replace(", ", ",").replace(";", "").lower()
            return s

        self.cur.execute("select sql from sqlite_master;")
        sql_stmt_ts: List[Tuple] = self.cur.fetchall()
        sql_stmt: Set[str] = {norm_sql_stmt(s[0]) for s in sql_stmt_ts}
        assert norm_sql_stmt(stmt) in sql_stmt


class TestSQLiteDatabaseMerge:
    def test_empty_table_addition_no_ancestor(self):
        file_inject = new_tmp_file()
        file_current = new_tmp_file()

        db_inj = DBCon(file_inject)
        db_inj.cur.execute(
            "CREATE TABLE 'Users' (code TEXT NOT NULL PRIMARY KEY, name TEXT NOT NULL);"
        )
        #
        db_inj.commit_and_close()

        db_cur = DBCon(file_current)
        db_cur.cur.execute("CREATE TABLE 'Socks' (size INTEGER, color TEXT);")
        #
        db_cur.commit_and_close()

        deep_merge_sqlite_dbs(file_current, file_inject)

        db_cur.reconnect()
        db_cur.assert_table_names({"Users", "Socks"})
        db_cur.close()

    def test_2way_record_update(self):
        file_inject = new_tmp_file()
        file_current = new_tmp_file()

        db_inj = DBCon(file_inject)
        db_inj.cur.execute(
            "CREATE TABLE 'Users' (code TEXT NOT NULL PRIMARY KEY, name TEXT NOT NULL);"
        )
        db_inj.cur.execute(
            "INSERT INTO 'Users' (code, name) VALUES ('U1', 'NameU1'), ('U2', 'NameU2Updated');"
        )
        #
        db_inj.commit_and_close()

        shutil.copyfile(file_inject, file_current)

        db_cur = DBCon(file_current)
        db_cur.cur.execute("UPDATE 'Users' SET name='NameU2' WHERE code='U2';")
        #
        db_cur.commit_and_close()

        deep_merge_sqlite_dbs(file_current, file_inject)

        db_cur.reconnect()
        db_cur.assert_records("Users", {("U1", "NameU1"), ("U2", "NameU2Updated")})
        db_cur.close()

    def test_empty_table_deletion(self):
        file_inject = new_tmp_file()
        file_current = new_tmp_file()
        file_ancestor = new_tmp_file()

        create_table_users_v0 = (
            "CREATE TABLE 'Users' (code TEXT NOT NULL PRIMARY KEY, name TEXT NOT NULL);"
        )

        db_anc = DBCon(file_ancestor)
        db_anc.cur.execute(create_table_users_v0)
        db_anc.cur.execute("CREATE TABLE 'Socks' (size INTEGER, color TEXT);")
        #
        db_anc.commit_and_close()

        db_inj = DBCon(file_inject)
        db_inj.cur.execute(create_table_users_v0)
        #
        db_inj.commit_and_close()

        shutil.copyfile(file_ancestor, file_current)

        db_cur = DBCon(file_current)
        db_cur.cur.execute("CREATE TABLE 'Something' (size INTEGER, color TEXT);")
        #
        db_cur.commit_and_close()

        deep_merge_sqlite_dbs(file_current, file_inject, file_ancestor)

        db_cur.reconnect()
        db_cur.assert_table_names({"Users", "Something"})
        db_cur.close()

    def test_non_empty_table_addition_no_ancestor(self):
        file_inject = new_tmp_file()
        file_current = new_tmp_file()

        db_inj = DBCon(file_inject)
        db_inj.cur.execute(
            "CREATE TABLE 'Users' (code TEXT NOT NULL PRIMARY KEY, name TEXT NOT NULL);"
        )
        db_inj.cur.execute(
            "INSERT INTO 'Users' (code, name) VALUES ('U1', 'NameU1'), ('U2', 'NameU2');"
        )
        #
        db_inj.commit_and_close()

        db_cur = DBCon(file_current)
        db_cur.cur.execute("CREATE TABLE 'Socks' (size INTEGER, color TEXT);")
        db_cur.cur.execute(
            "INSERT INTO 'Socks' (size, color) VALUES ('45', 'Black'), ('46', 'Blue');"
        )
        #
        db_cur.commit_and_close()

        deep_merge_sqlite_dbs(file_current, file_inject)

        db_cur.reconnect()
        db_cur.assert_table_names({"Users", "Socks"})
        db_cur.assert_records("Users", {("U1", "NameU1"), ("U2", "NameU2")})
        db_cur.assert_records("Socks", {(45, "Black"), (46, "Blue")})
        db_cur.close()

    def test_record_addition_no_ancestor(self):
        file_inject = new_tmp_file()
        file_current = new_tmp_file()

        db_inj = DBCon(file_inject)
        db_inj.cur.execute(
            "CREATE TABLE 'Users' (code TEXT NOT NULL PRIMARY KEY, name TEXT NOT NULL);"
        )
        db_inj.cur.execute(
            "INSERT INTO 'Users' (code, name) VALUES ('U1', 'NameU1'), ('U2', 'NameU2');"
        )
        #
        db_inj.commit_and_close()

        db_cur = DBCon(file_current)
        db_cur.cur.execute(
            "CREATE TABLE 'Users' (code TEXT NOT NULL PRIMARY KEY, name TEXT NOT NULL);"
        )
        db_cur.cur.execute(
            "INSERT INTO 'Users' (code, name) VALUES ('U3', 'NameU3'), ('U4', 'NameU4');"
        )
        #
        db_cur.commit_and_close()

        deep_merge_sqlite_dbs(file_current, file_inject)

        db_cur.reconnect()
        db_cur.assert_records(
            "Users", {("U1", "NameU1"), ("U2", "NameU2"), ("U3", "NameU3"), ("U4", "NameU4")}
        )
        db_cur.close()

    def test_table_and_record_addition_no_ancestor(self):
        file_inject = new_tmp_file()
        file_current = new_tmp_file()

        db_inj = DBCon(file_inject)
        create_table_users_v0 = (
            "CREATE TABLE 'Users' (code TEXT NOT NULL PRIMARY KEY, name TEXT NOT NULL);"
        )
        db_inj.cur.execute(create_table_users_v0)
        db_inj.cur.execute(
            "INSERT INTO 'Users' (code, name) VALUES ('U1', 'NameU1'), ('U2', 'NameU2');"
        )
        #
        db_inj.commit_and_close()

        db_cur = DBCon(file_current)
        db_cur.cur.execute("CREATE TABLE 'Socks' (size INTEGER, color TEXT);")
        db_cur.cur.execute(
            "INSERT INTO 'Socks' (size, color) VALUES ('45', 'Black'), ('46', 'Blue');"
        )
        #
        db_cur.commit_and_close()

        deep_merge_sqlite_dbs(file_current, file_inject)

        db_cur.reconnect()
        db_cur.assert_table_names({"Users", "Socks"})
        db_cur.assert_records("Users", {("U1", "NameU1"), ("U2", "NameU2")})
        db_cur.assert_records("Socks", {(45, "Black"), (46, "Blue")})
        db_cur.close()

    def test_record_deletion(self):
        file_inject = new_tmp_file()
        file_current = new_tmp_file()
        file_ancestor = new_tmp_file()

        db_anc = DBCon(file_ancestor)
        db_anc.cur.execute(
            "CREATE TABLE 'Users' (code TEXT NOT NULL PRIMARY KEY, name TEXT NOT NULL);"
        )
        db_anc.cur.execute(
            "INSERT INTO 'Users' (code, name) VALUES ('U1', 'NameU1'), ('U2', 'NameU2');"
        )
        #
        db_anc.commit_and_close()

        shutil.copyfile(file_ancestor, file_inject)

        db_inj = DBCon(file_inject)
        db_inj.cur.execute("DELETE FROM 'Users' WHERE Users.code='U2';")
        #
        db_inj.commit_and_close()

        shutil.copyfile(file_ancestor, file_current)

        db_cur = DBCon(file_current)
        db_cur.cur.execute(
            "INSERT INTO 'Users' (code, name) VALUES ('U3', 'NameU3'), ('U4', 'NameU4');"
        )
        #
        db_cur.commit_and_close()

        deep_merge_sqlite_dbs(file_current, file_inject, file_ancestor)

        db_cur.reconnect()
        db_cur.assert_records("Users", {("U1", "NameU1"), ("U3", "NameU3"), ("U4", "NameU4")})
        db_cur.close()

    def test_record_update(self):
        file_inject = new_tmp_file()
        file_current = new_tmp_file()
        file_ancestor = new_tmp_file()

        db_anc = DBCon(file_ancestor)
        db_anc.cur.execute(
            "CREATE TABLE 'Users' (code TEXT NOT NULL PRIMARY KEY, name TEXT NOT NULL);"
        )
        db_anc.cur.execute(
            "INSERT INTO 'Users' (code, name) VALUES ('U1', 'NameU1'), ('U2', 'NameU2');"
        )
        #
        db_anc.commit_and_close()

        shutil.copyfile(file_ancestor, file_inject)

        db_inj = DBCon(file_inject)
        db_inj.cur.execute("UPDATE 'Users' SET name='NameU2Updated' WHERE code='U2';")
        #
        db_inj.commit_and_close()

        shutil.copyfile(file_ancestor, file_current)

        db_cur = DBCon(file_current)
        db_cur.cur.execute(
            "INSERT INTO 'Users' (code, name) VALUES ('U3', 'NameU3'), ('U4', 'NameU4');"
        )
        #
        db_cur.commit_and_close()

        deep_merge_sqlite_dbs(file_current, file_inject, file_ancestor)

        db_cur.reconnect()
        db_cur.assert_records(
            "Users",
            {
                ("U1", "NameU1"),
                ("U2", "NameU2Updated"),
                ("U3", "NameU3"),
                ("U4", "NameU4"),
            },
        )
        db_cur.close()

    def test_record_update_inject_and_current_conflict(self):
        file_inject = new_tmp_file()
        file_current = new_tmp_file()
        file_ancestor = new_tmp_file()

        db_anc = DBCon(file_ancestor)
        db_anc.cur.execute(
            "CREATE TABLE 'Users' (code TEXT NOT NULL PRIMARY KEY, name TEXT NOT NULL);"
        )
        db_anc.cur.execute(
            "INSERT INTO 'Users' (code, name) VALUES ('U1', 'NameU1'), ('U2', 'NameU2');"
        )
        #
        db_anc.commit_and_close()

        shutil.copyfile(file_ancestor, file_inject)

        db_inj = DBCon(file_inject)
        db_inj.cur.execute("UPDATE 'Users' SET name='NameU2Updated' WHERE code='U2';")
        #
        db_inj.commit_and_close()

        shutil.copyfile(file_ancestor, file_current)

        db_cur = DBCon(file_current)
        db_cur.cur.execute(
            "INSERT INTO 'Users' (code, name) VALUES ('U3', 'NameU3'), ('U4', 'NameU4');"
        )
        db_cur.cur.execute("UPDATE 'Users' SET name='NameU2UpdatedInCurrent' WHERE code='U2';")
        #
        db_cur.commit_and_close()

        deep_merge_sqlite_dbs(file_current, file_inject, file_ancestor)

        db_cur.reconnect()
        db_cur.assert_records(
            "Users",
            {
                ("U1", "NameU1"),
                ("U2", "NameU2Updated"),
                ("U3", "NameU3"),
                ("U4", "NameU4"),
            },
        )
        db_cur.close()

    def test_attribute_deletion(self):
        file_inject = new_tmp_file()
        file_current = new_tmp_file()
        file_ancestor = new_tmp_file()

        db_anc = DBCon(file_ancestor)
        db_anc.cur.execute(
            "CREATE TABLE 'Users' (code TEXT NOT NULL PRIMARY KEY, name TEXT NOT NULL, attr TEXT NOT NULL);"
        )
        db_anc.cur.execute(
            "INSERT INTO 'Users' (code, name, attr) VALUES ('U1', 'NameU1', 'attrU1'), ('U2', 'NameU2', 'attrU2');"
        )
        #
        db_anc.commit_and_close()

        db_inj = DBCon(file_inject)
        db_inj.cur.execute(
            "CREATE TABLE 'Users' (code TEXT NOT NULL PRIMARY KEY, name TEXT NOT NULL);"
        )
        db_inj.cur.execute(
            "INSERT INTO 'Users' (code, name) VALUES ('U1', 'NameU1'), ('U2', 'NameU2');"
        )
        #
        db_inj.commit_and_close()

        shutil.copyfile(file_ancestor, file_current)

        db_cur = DBCon(file_current)
        db_cur.cur.execute(
            "INSERT INTO 'Users' (code, name, attr) VALUES ('U3', 'NameU3', 'attrU3'), ('U4', 'NameU4', 'attrU4');"
        )
        #
        db_cur.commit_and_close()

        deep_merge_sqlite_dbs(file_current, file_inject, file_ancestor)

        db_cur.reconnect()
        db_cur.assert_records(
            "Users",
            {
                ("U1", "NameU1"),
                ("U2", "NameU2"),
                ("U3", "NameU3"),
                ("U4", "NameU4"),
            },
        )
        db_cur.close()

    def test_record_deletion_and_attribute_deletion(self):
        file_inject = new_tmp_file()
        file_current = new_tmp_file()
        file_ancestor = new_tmp_file()

        db_anc = DBCon(file_ancestor)
        db_anc.cur.execute(
            "CREATE TABLE 'Users' (code TEXT NOT NULL PRIMARY KEY, name TEXT NOT NULL, attr TEXT NOT NULL);"
        )
        db_anc.cur.execute(
            "INSERT INTO 'Users' (code, name, attr) VALUES ('U1', 'NameU1', 'attrU1'), ('U2', 'NameU2', 'attrU2');"
        )
        #
        db_anc.commit_and_close()

        db_inj = DBCon(file_inject)
        db_inj.cur.execute(
            "CREATE TABLE 'Users' (code TEXT NOT NULL PRIMARY KEY, name TEXT NOT NULL);"
        )
        #
        db_inj.commit_and_close()

        shutil.copyfile(file_ancestor, file_current)

        db_cur = DBCon(file_current)
        db_cur.cur.execute(
            "INSERT INTO 'Users' (code, name, attr) VALUES ('U3', 'NameU3', 'attrU3'), ('U4', 'NameU4', 'attrU4');"
        )
        #
        db_cur.commit_and_close()

        deep_merge_sqlite_dbs(file_current, file_inject, file_ancestor)

        db_cur.reconnect()
        db_cur.assert_records(
            "Users",
            {
                ("U3", "NameU3"),
                ("U4", "NameU4"),
            },
        )
        db_cur.close()

    def test_attribute_replace_schema_update(self):
        file_inject = new_tmp_file()
        file_current = new_tmp_file()
        file_ancestor = new_tmp_file()

        db_anc = DBCon(file_ancestor)
        db_anc.cur.execute(
            "CREATE TABLE 'Users' (code TEXT NOT NULL PRIMARY KEY, name TEXT NOT NULL, attr TEXT NOT NULL);"
        )
        db_anc.cur.execute(
            "INSERT INTO 'Users' (code, name, attr) VALUES ('U1', 'NameU1', 'attrU1'), ('U2', 'NameU2', 'attrU2');"
        )
        #
        db_anc.commit_and_close()

        db_inj = DBCon(file_inject)
        db_inj.cur.execute(
            "CREATE TABLE 'Users' (code TEXT NOT NULL PRIMARY KEY, name TEXT NOT NULL, attr2 INT NOT NULL DEFAULT 144);"
        )
        db_inj.cur.execute(
            "INSERT INTO 'Users' (code, name, attr2) VALUES ('U1', 'NameU1', 11), ('U2', 'NameU2', 22);"
        )
        #
        db_inj.commit_and_close()

        shutil.copyfile(file_ancestor, file_current)

        db_cur = DBCon(file_current)
        db_cur.cur.execute(
            "INSERT INTO 'Users' (code, name, attr) VALUES ('U3', 'NameU3', 'attrU3'), ('U4', 'NameU4', 'attrU4');"
        )
        #
        db_cur.commit_and_close()

        deep_merge_sqlite_dbs(file_current, file_inject, file_ancestor)

        db_cur.reconnect()
        db_cur.assert_records(
            "Users",
            {
                ("U1", "NameU1", 11),
                ("U2", "NameU2", 22),
                ("U3", "NameU3", 144),
                ("U4", "NameU4", 144),
            },
        )
        db_cur.close()

    def test_attribute_schema_update(self):
        file_inject = new_tmp_file()
        file_current = new_tmp_file()
        file_ancestor = new_tmp_file()

        db_anc = DBCon(file_ancestor)
        db_anc.cur.execute(
            "CREATE TABLE 'Users' (code TEXT NOT NULL PRIMARY KEY, name TEXT NOT NULL, attr TEXT NOT NULL);"
        )
        db_anc.cur.execute(
            "INSERT INTO 'Users' (code, name, attr) VALUES ('U1', 'NameU1', 'attrU1'), ('U2', 'NameU2', 'attrU2');"
        )
        #
        db_anc.commit_and_close()

        db_inj = DBCon(file_inject)
        db_inj.cur.execute(
            "CREATE TABLE 'Users' (code TEXT NOT NULL PRIMARY KEY, name TEXT NOT NULL, attr INT NOT NULL DEFAULT 144);"
        )
        db_inj.cur.execute(
            "INSERT INTO 'Users' (code, name, attr) VALUES ('U1', 'NameU1', 11), ('U2', 'NameU2', 22);"
        )
        #
        db_inj.commit_and_close()

        shutil.copyfile(file_ancestor, file_current)

        db_cur = DBCon(file_current)
        db_cur.cur.execute(
            "INSERT INTO 'Users' (code, name, attr) VALUES ('U3', 'NameU3', 'attrU3'), ('U4', 'NameU4', 'attrU4');"
        )
        #
        db_cur.commit_and_close()

        deep_merge_sqlite_dbs(file_current, file_inject, file_ancestor)

        db_cur.reconnect()
        db_cur.assert_records(
            "Users",
            {
                ("U1", "NameU1", 11),
                ("U2", "NameU2", 22),
                ("U3", "NameU3", 144),
                ("U4", "NameU4", 144),
            },
        )
        db_cur.close()

    @skip_in_ci
    def test_attribute_replace_and_addition_schema_update(self):
        file_inject = new_tmp_file()
        file_current = new_tmp_file()
        file_ancestor = new_tmp_file()

        db_anc = DBCon(file_ancestor)
        db_anc.cur.execute(
            "CREATE TABLE 'Users' (code TEXT NOT NULL PRIMARY KEY, name TEXT NOT NULL, attr TEXT NOT NULL);"
        )
        db_anc.cur.execute(
            "INSERT INTO 'Users' (code, name, attr) VALUES ('U1', 'NameU1', 'attrU1'), ('U2', 'NameU2', 'attrU2');"
        )
        #
        db_anc.commit_and_close()

        db_inj = DBCon(file_inject)
        db_inj.cur.execute(
            "CREATE TABLE 'Users' (code TEXT NOT NULL PRIMARY KEY, name TEXT NOT NULL, "
            "attr INT NOT NULL DEFAULT 144, attr2 Text NOT NULL);"
        )
        db_inj.cur.execute(
            "INSERT INTO 'Users' (code, name, attr, attr2) VALUES "
            "('U1', 'NameU1', 1, 'attr2_1'), ('U2', 'NameU2', 2, 'attr2_2');"
        )
        #
        db_inj.commit_and_close()

        shutil.copyfile(file_ancestor, file_current)

        db_cur = DBCon(file_current)
        db_cur.cur.execute(
            "INSERT INTO 'Users' (code, name, attr) VALUES ('U3', 'NameU3', 'attrU3'), ('U4', 'NameU4', 'attrU4');"
        )
        #
        db_cur.commit_and_close()

        deep_merge_sqlite_dbs(file_current, file_inject, file_ancestor)

        db_cur.reconnect()
        db_cur.assert_records(
            "Users",
            {
                ("U1", "NameU1", 1, "attr2_1"),
                ("U2", "NameU2", 2, "attr2_2"),
                ("U3", "NameU3", 144, ""),
                ("U4", "NameU4", 144, ""),
            },
        )
        db_cur.close()

    def test_attribute_addition_nullable(self):
        file_inject = new_tmp_file()
        file_current = new_tmp_file()

        db_inj = DBCon(file_inject)
        create_table_users_v0 = (
            "CREATE TABLE 'Users' (code TEXT NOT NULL PRIMARY KEY, name TEXT NOT NULL);"
        )
        db_inj.cur.execute(create_table_users_v0)
        db_inj.cur.execute(
            "INSERT INTO 'Users' (code, name) VALUES ('U1', 'NameU1'), ('U2', 'NameU2');"
        )
        #
        db_inj.commit_and_close()

        db_cur = DBCon(file_current)
        db_cur.cur.execute(create_table_users_v0)
        db_cur.add_attribute("Users", "age INTEGER")
        db_cur.cur.execute(
            "INSERT INTO 'Users' (code, name, age) VALUES ('U3', 'NameU3', 33), ('U4', 'NameU4', 44);"
        )
        #
        db_cur.commit_and_close()

        deep_merge_sqlite_dbs(file_current, file_inject)

        db_cur.reconnect()
        db_cur.assert_records(
            "Users",
            {
                ("U1", "NameU1", None),
                ("U2", "NameU2", None),
                ("U3", "NameU3", 33),
                ("U4", "NameU4", 44),
            },
        )
        db_cur.close()

    def test_attribute_addition_not_nullable_default_integer(self):
        file_inject = new_tmp_file()
        file_current = new_tmp_file()

        db_inj = DBCon(file_inject)
        create_table_users_v0 = (
            "CREATE TABLE 'Users' (code TEXT NOT NULL PRIMARY KEY, name TEXT NOT NULL);"
        )
        db_inj.cur.execute(create_table_users_v0)
        db_inj.cur.execute(
            "INSERT INTO 'Users' (code, name) VALUES ('U1', 'NameU1'), ('U2', 'NameU2');"
        )
        #
        db_inj.commit_and_close()

        db_cur = DBCon(file_current)
        db_cur.cur.execute(create_table_users_v0)
        db_cur.add_attribute("Users", "age INTEGER NOT NULL DEFAULT 100")
        db_cur.cur.execute(
            "INSERT INTO 'Users' (code, name, age) VALUES ('U3', 'NameU3', 33), ('U4', 'NameU4', 44);"
        )
        #
        db_cur.commit_and_close()

        deep_merge_sqlite_dbs(file_current, file_inject)

        db_cur.reconnect()
        db_cur.assert_records(
            "Users",
            {
                ("U1", "NameU1", 100),
                ("U2", "NameU2", 100),
                ("U3", "NameU3", 33),
                ("U4", "NameU4", 44),
            },
        )
        db_cur.close()

    def test_attribute_addition_not_nullable_default_text(self):
        file_inject = new_tmp_file()
        file_current = new_tmp_file()

        db_inj = DBCon(file_inject)
        create_table_users_v0 = (
            "CREATE TABLE 'Users' (code TEXT NOT NULL PRIMARY KEY, name TEXT NOT NULL);"
        )
        db_inj.cur.execute(create_table_users_v0)
        db_inj.cur.execute(
            "INSERT INTO 'Users' (code, name) VALUES ('U1', 'NameU1'), ('U2', 'NameU2');"
        )
        #
        db_inj.commit_and_close()

        db_cur = DBCon(file_current)
        db_cur.cur.execute(create_table_users_v0)
        db_cur.add_attribute("Users", "field TEXT NOT NULL DEFAULT SomeDefault")
        db_cur.cur.execute(
            "INSERT INTO 'Users' (code, name, field) VALUES ('U3', 'NameU3', 'Hello'), ('U4', 'NameU4', 'World');"
        )
        #
        db_cur.commit_and_close()

        deep_merge_sqlite_dbs(file_current, file_inject)

        db_cur.reconnect()
        db_cur.assert_records(
            "Users",
            {
                ("U1", "NameU1", "SomeDefault"),
                ("U2", "NameU2", "SomeDefault"),
                ("U3", "NameU3", "Hello"),
                ("U4", "NameU4", "World"),
            },
        )
        db_cur.close()

    def test_attribute_addition_not_nullable_no_default_text(self):
        file_inject = new_tmp_file()
        file_current = new_tmp_file()

        db_inj = DBCon(file_inject)
        db_inj.cur.execute(
            "CREATE TABLE 'Users' (code TEXT NOT NULL PRIMARY KEY, name TEXT NOT NULL);"
        )
        db_inj.cur.execute(
            "INSERT INTO 'Users' (code, name) VALUES ('U1', 'NameU1'), ('U2', 'NameU2');"
        )
        #
        db_inj.commit_and_close()

        db_cur = DBCon(file_current)
        db_cur.cur.execute(
            "CREATE TABLE 'Users' (code TEXT NOT NULL PRIMARY KEY, name TEXT NOT NULL, field TEXT NOT NULL);"
        )
        db_cur.cur.execute(
            "INSERT INTO 'Users' (code, name, field) VALUES ('U3', 'NameU3', 'Hello'), ('U4', 'NameU4', 'World');"
        )
        #
        db_cur.commit_and_close()

        deep_merge_sqlite_dbs(file_current, file_inject)

        db_cur.reconnect()
        db_cur.assert_records(
            "Users",
            {
                ("U1", "NameU1", ""),
                ("U2", "NameU2", ""),
                ("U3", "NameU3", "Hello"),
                ("U4", "NameU4", "World"),
            },
        )
        db_cur.close()

    def test_attribute_addition_not_nullable_no_default_real(self):
        file_inject = new_tmp_file()
        file_current = new_tmp_file()

        db_inj = DBCon(file_inject)
        db_inj.cur.execute(
            "CREATE TABLE 'Users' (code TEXT NOT NULL PRIMARY KEY, name TEXT NOT NULL);"
        )
        db_inj.cur.execute(
            "INSERT INTO 'Users' (code, name) VALUES ('U1', 'NameU1'), ('U2', 'NameU2');"
        )
        #
        db_inj.commit_and_close()

        db_cur = DBCon(file_current)
        db_cur.cur.execute(
            "CREATE TABLE 'Users' (code TEXT NOT NULL PRIMARY KEY, name TEXT NOT NULL, field REAL NOT NULL);"
        )
        db_cur.cur.execute(
            "INSERT INTO 'Users' (code, name, field) VALUES ('U3', 'NameU3', 3.14), ('U4', 'NameU4', 4.14);"
        )
        #
        db_cur.commit_and_close()

        deep_merge_sqlite_dbs(file_current, file_inject)

        db_cur.reconnect()
        db_cur.assert_records(
            "Users",
            {
                ("U1", "NameU1", 0.0),
                ("U2", "NameU2", 0.0),
                ("U3", "NameU3", 3.14),
                ("U4", "NameU4", 4.14),
            },
        )
        db_cur.close()

    def test_attribute_addition_not_nullable_no_default_numeric(self):
        file_inject = new_tmp_file()
        file_current = new_tmp_file()

        db_inj = DBCon(file_inject)
        db_inj.cur.execute(
            "CREATE TABLE 'Users' (code TEXT NOT NULL PRIMARY KEY, name TEXT NOT NULL);"
        )
        db_inj.cur.execute(
            "INSERT INTO 'Users' (code, name) VALUES ('U1', 'NameU1'), ('U2', 'NameU2');"
        )
        #
        db_inj.commit_and_close()

        db_cur = DBCon(file_current)
        db_cur.cur.execute(
            "CREATE TABLE 'Users' (code TEXT NOT NULL PRIMARY KEY, name TEXT NOT NULL, field BOOLEAN NOT NULL);"
        )
        db_cur.cur.execute(
            "INSERT INTO 'Users' (code, name, field) VALUES ('U3', 'NameU3', True), ('U4', 'NameU4', False);"
        )
        #
        db_cur.commit_and_close()

        deep_merge_sqlite_dbs(file_current, file_inject)

        db_cur.reconnect()
        db_cur.assert_records(
            "Users",
            {
                ("U1", "NameU1", False),
                ("U2", "NameU2", False),
                ("U3", "NameU3", True),
                ("U4", "NameU4", False),
            },
        )
        db_cur.close()

    def test_attribute_addition_not_nullable_no_default_blob(self):
        file_inject = new_tmp_file()
        file_current = new_tmp_file()

        db_inj = DBCon(file_inject)
        db_inj.cur.execute(
            "CREATE TABLE 'Users' (code TEXT NOT NULL PRIMARY KEY, name TEXT NOT NULL);"
        )
        db_inj.cur.execute(
            "INSERT INTO 'Users' (code, name) VALUES ('U1', 'NameU1'), ('U2', 'NameU2');"
        )
        #
        db_inj.commit_and_close()

        db_cur = DBCon(file_current)
        db_cur.cur.execute(
            "CREATE TABLE 'Users' (code TEXT NOT NULL PRIMARY KEY, name TEXT NOT NULL, field BLOB NOT NULL);"
        )
        db_cur.cur.execute(
            "INSERT INTO 'Users' (code, name, field) VALUES ('U3', 'NameU3', 'field3'), ('U4', 'NameU4', 'field4');"
        )
        #
        db_cur.commit_and_close()

        deep_merge_sqlite_dbs(file_current, file_inject)

        db_cur.reconnect()
        db_cur.assert_records(
            "Users",
            {
                ("U1", "NameU1", b""),
                ("U2", "NameU2", b""),
                ("U3", "NameU3", b"field3"),
                ("U4", "NameU4", b"field4"),
            },
        )
        db_cur.close()

    def test_item_addition_composite_primary_key(self):
        file_inject = new_tmp_file()
        file_current = new_tmp_file()

        db_inj = DBCon(file_inject)
        create_table_users_v0 = "CREATE TABLE 'Users' (code TEXT NOT NULL, name TEXT NOT NULL, PRIMARY KEY(code, name));"
        db_inj.cur.execute(create_table_users_v0)
        db_inj.cur.execute(
            "INSERT INTO 'Users' (code, name) VALUES ('U1', 'NameU1'), ('U2', 'NameU2');"
        )
        #
        db_inj.commit_and_close()

        db_cur = DBCon(file_current)
        db_cur.cur.execute(create_table_users_v0)
        db_cur.cur.execute(
            "INSERT INTO 'Users' (code, name) VALUES ('U3', 'NameU3'), ('U4', 'NameU4');"
        )
        #
        db_cur.commit_and_close()

        deep_merge_sqlite_dbs(file_current, file_inject)

        db_cur.reconnect()
        db_cur.assert_records(
            "Users",
            {
                ("U1", "NameU1"),
                ("U2", "NameU2"),
                ("U3", "NameU3"),
                ("U4", "NameU4"),
            },
        )
        db_cur.close()

    def test_item_update_composite_primary_key(self):
        file_inject = new_tmp_file()
        file_current = new_tmp_file()

        db_inj = DBCon(file_inject)
        create_table_users_v0 = "CREATE TABLE 'Users' (code TEXT NOT NULL, name TEXT NOT NULL, age INTEGER, PRIMARY KEY(code, name));"
        db_inj.cur.execute(create_table_users_v0)
        db_inj.cur.execute(
            "INSERT INTO 'Users' (code, name, age) VALUES ('U1', 'NameU1', 1), ('U2', 'NameU2', 2);"
        )
        #
        db_inj.commit_and_close()

        db_cur = DBCon(file_current)
        db_cur.cur.execute(create_table_users_v0)
        db_cur.cur.execute(
            "INSERT INTO 'Users' (code, name, age) VALUES ('U1', 'NameU1', 111), ('U3', 'NameU3', 3);"
        )
        #
        db_cur.commit_and_close()

        deep_merge_sqlite_dbs(file_current, file_inject)

        db_cur.reconnect()
        db_cur.assert_records(
            "Users",
            {
                ("U1", "NameU1", 1),
                ("U2", "NameU2", 2),
                ("U3", "NameU3", 3),
            },
        )
        db_cur.close()

    def test_index_addition_2way(self):
        file_inject = new_tmp_file()
        file_current = new_tmp_file()

        db_inj = DBCon(file_inject)
        table_stmt = "CREATE TABLE 'Users' (code TEXT NOT NULL PRIMARY KEY, name TEXT NOT NULL);"
        db_inj.cur.execute(table_stmt)
        index_stmt = "CREATE INDEX 'Users_name' on 'Users' ('name');"
        db_inj.cur.execute(index_stmt)
        #
        db_inj.commit_and_close()

        db_cur = DBCon(file_current)
        db_cur.cur.execute(table_stmt)
        #
        db_cur.commit_and_close()

        deep_merge_sqlite_dbs(file_current, file_inject)

        db_cur.reconnect()
        db_cur.assert_schema_contains(index_stmt)
        db_cur.close()

    def test_index_field_addition(self):
        file_inject = new_tmp_file()
        file_current = new_tmp_file()

        db_inj = DBCon(file_inject)
        table_stmt = "CREATE TABLE 'Users' (code TEXT NOT NULL PRIMARY KEY, name TEXT NOT NULL);"
        db_inj.cur.execute(table_stmt)
        index_stmt = "CREATE INDEX 'Users_name' on 'Users' ('code', 'name');"
        db_inj.cur.execute(index_stmt)
        #
        db_inj.commit_and_close()

        db_cur = DBCon(file_current)
        db_cur.cur.execute(table_stmt)
        db_cur.cur.execute("CREATE INDEX 'Users_name' on 'Users' ('name');")
        #
        db_cur.commit_and_close()

        deep_merge_sqlite_dbs(file_current, file_inject)

        db_cur.reconnect()
        db_cur.assert_schema_contains(index_stmt)
        db_cur.close()

    def test_index_field_deletion(self):
        file_current = new_tmp_file()
        file_ancestor = new_tmp_file()

        db_anc = DBCon(file_ancestor)
        db_anc.cur.execute(
            "CREATE TABLE 'Users' (code TEXT NOT NULL PRIMARY KEY, name TEXT NOT NULL, surname TEXT NOT NULL);"
        )
        db_anc.cur.execute("CREATE INDEX 'Users_name' on 'Users' ('name', 'surname');")
        #
        db_anc.commit_and_close()

        db_cur = DBCon(file_current)
        db_cur.cur.execute(
            "CREATE TABLE 'Users' (code TEXT NOT NULL PRIMARY KEY, name TEXT NOT NULL)"
        )
        db_cur.cur.execute("CREATE INDEX 'Users_name' on 'Users' ('name');")
        #
        db_cur.commit_and_close()

        deep_merge_sqlite_dbs(file_current, file_ancestor, file_ancestor)

        db_cur.reconnect()
        db_cur.assert_schema_contains("CREATE INDEX 'Users_name' on 'Users' ('name');")
        db_cur.close()

    def test_object_json_merge(self):
        file_current = new_tmp_file()
        file_inject = new_tmp_file()

        create_table = (
            'CREATE TABLE "Table1" (hashKey TEXT, ObjectJSON BLOB NOT NULL, PRIMARY KEY(hashKey));'
        )

        db_cur = DBCon(file_current)
        db_cur.cur.execute(create_table)
        db_cur.cur.execute(
            'INSERT INTO "Table1" ("hashKey", "ObjectJSON") VALUES (?, ?);',
            (
                "hashkey1",
                json.dumps({"data1": "data1_cur", "data2": "data2_cur", "data3": [1, 2, {"3": 3}]}),
            ),
        )
        #
        db_cur.commit_and_close()

        db_inj = DBCon(file_inject)
        db_inj.cur.execute(create_table)
        db_inj.cur.execute(
            'INSERT INTO "Table1" ("hashKey", "ObjectJSON") VALUES (?, ?);',
            (
                "hashkey1",
                json.dumps(
                    {"data1": "data1_inj", "data3": [111, 222, {"444": 444}], "data4": "data4_inj"}
                ),
            ),
        )
        #
        db_inj.commit_and_close()

        deep_merge_sqlite_dbs(file_current, file_inject)

        merged_objectjson: str = json.dumps(
            {
                "data1": "data1_inj",
                "data2": "data2_cur",
                "data3": [111, 222, {"3": 3, "444": 444}],
                "data4": "data4_inj",
            }
        )

        db_cur.reconnect()
        db_cur.assert_records("Table1", {("hashkey1", to_bytes(merged_objectjson))})
        db_cur.close()
