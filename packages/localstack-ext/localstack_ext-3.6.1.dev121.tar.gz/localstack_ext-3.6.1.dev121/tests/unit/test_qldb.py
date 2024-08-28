import re

from localstack.pro.core.services.qldb import partiql
from localstack.pro.core.services.qldb.partiql import inject_json_extract_into_expression
from localstack.utils.json import clone

TEST_TABLE = "table1"
TEST_STATE = {TEST_TABLE: [{"id": 1}, {"id": 2.0}, {"id": "id3"}]}


class TestQueryRewriting:
    def test_rewrite_queries(self):
        query = """
        UPDATE Wallet SET balance = ?, nominatedId = ?, ownerId = ?,
        type = ?, status = ?, tags = ?, description = ?, totalCreditAmount = ?,
        totalDebitAmount = ?, version = ? WHERE id = ? AND (version IS NULL OR version <> ?)
        """
        expected = """
            UPDATE Wallet SET data=json_set(json_set(json_set(json_set(json_set(json_set(json_set(
                json_set(json_set(json_set(data, '$.balance', ?), '$.nominatedId', ?), '$.ownerId', ?),
                '$.type', ?), '$.status', ?), '$.tags', ?), '$.description', ?),
                '$.totalCreditAmount', ?), '$.totalDebitAmount', ?), '$.version', ?)
                WHERE json_extract(data, '$.id') = ? AND (json_extract(data, '$.version') IS NULL
                OR json_extract(data, '$.version') <> ?)
        """

        # transform query
        query = partiql.transform_query_SET_clause_to_sqlite(query, parameters=None)
        query = partiql.transform_query_WHERE_clause_to_sqlite(query, parameters=None)

        # assert result
        assert self._queries_equal(query, expected)

    def test_inject_json_extract_into_expression(self):
        query = "SELECT * from test where foo = 'bar'"
        result = inject_json_extract_into_expression("foo = 'bar'", query)
        assert self._queries_equal(result, "json_extract(data, '$.foo') = 'bar'")

    def _queries_equal(self, q1: str, q2: str):
        q1 = re.sub(r"\s+", " ", q1.replace("\n", "")).replace("( ", "(").strip()
        q2 = re.sub(r"\s+", " ", q2.replace("\n", "")).replace("( ", "(").strip()
        return q1 == q2


class TestExecuteQueries:
    def test_update_delete_with_by_id_alias(self):
        table_name = "table1"
        state = {table_name: []}

        # create table data
        partiql.run_query("INSERT INTO %s {'id':1}" % table_name, state)
        partiql.run_query("INSERT INTO %s {'id':2}" % table_name, state)
        select_pid = f"SELECT * FROM {table_name} BY pid"
        result = partiql.run_query(select_pid, state)
        pid1 = result[0]["pid"]
        pid2 = result[1]["pid"]

        # update table data
        query = f'UPDATE {table_name} AS a BY pid SET a.title = "test 123" WHERE pid = "{pid1}"'
        partiql.run_query(query, state)
        result = partiql.run_query(select_pid, state)
        pid_entry = [e for e in result if e["pid"] == pid1][0]
        assert pid_entry.get("title") == "test 123"

        # assert that temporary pids are removed
        select_all = f"SELECT * FROM {table_name}"
        result = partiql.run_query(select_all, state)
        assert "pid" not in result[0]

        # delete table data
        query = f'DELETE FROM {table_name} BY pid WHERE pid = "{pid1}"'
        len_before = len(result)
        partiql.run_query(query, state)
        result = partiql.run_query(select_pid, state)
        assert len(result) == len_before - 1
        assert pid1 not in [e["pid"] for e in result]

        # select final result
        query = f"SELECT * FROM {table_name} BY pid WHERE pid = '{pid2}'"
        result = partiql.run_query(query, state)
        assert len(result) == 1

        # make sure that BY id attribute has not been inserted
        result = partiql.run_query(select_all, state)
        assert result == [{"id": 2}]

    def test_query_with_expression_using_placeholder(self):
        table_name = "account"
        state = {table_name: []}

        partiql.run_query("INSERT INTO account {'balance':123}", state)

        result = partiql.run_query("SELECT BY account_id * from account", state)
        account_id = result[0]["account_id"]

        # run a query to add to the account balance
        query = """
        UPDATE account
           BY  account_id
          SET  balance = balance + ?
        WHERE  account_id = ?
        """
        partiql.run_query(query, state, (222, account_id))

        # assert that the account balance has been updated
        result = partiql.run_query("SELECT BY account_id * from account", state)
        assert result[0]["balance"] == 123 + 222
        assert result[0]["account_id"] == account_id

    def test_partiql_create_tables(self):
        state = {}
        partiql.run_query("CREATE TABLE test1", state)
        partiql.run_query(" CREATE \n TABLE test2 ", state)
        query = "SELECT VALUE name FROM information_schema.user_tables"
        result = partiql.run_query(query, state)
        assert result == ["test1", "test2"]

    def test_partiql_create_indexes(self):
        state = {}
        # create table
        table_name = "test1"
        partiql.run_query("CREATE TABLE %s" % table_name, state)
        # create indexes
        partiql.run_query("CREATE INDEX ON %s (attr1)" % table_name, state)
        partiql.run_query("CREATE INDEX ON %s (attr2)" % table_name, state)
        # get indexes
        query = f"""
        SELECT VALUE indexes
        FROM information_schema.user_tables info, info.indexes indexes
        WHERE info.name = '{table_name}'
        """
        result = partiql.run_query(query, state)
        assert len(result) == 2
        assert "indexId" in result[0]
        assert result[0].get("status") == "ONLINE"
        # drop index
        idx1 = result[0]
        idx2 = result[1]
        partiql.run_query(
            'DROP INDEX "%s" ON %s WITH (purge = true)' % (idx1["indexId"], table_name), state
        )
        result = partiql.run_query(query, state)
        assert len(result) == 1
        assert result[0]["indexId"] == idx2["indexId"]

    def test_partiql_select_with_backtick_escape(self):
        state = {}
        partiql.run_query("CREATE TABLE test1", state)
        partiql.run_query("INSERT INTO test1 {'id':'id::123'}", state)
        query = 'SELECT * FROM test1 WHERE id = `"id::123"`'
        result = partiql.run_query(query, state)[0]
        assert result["id"] == "id::123"

    def test_partiql_select_from_by(self):
        state = {}
        partiql.run_query("CREATE TABLE test1", state)
        partiql.run_query("INSERT INTO test1 {'id':123}", state)
        query = "SELECT * FROM test1 BY pid"
        result = partiql.run_query(query, state)[0]
        assert result["id"] == 123
        assert "pid" in result

    def test_partiql_update_with_in_keyword(self):
        state = {}
        partiql.run_query("CREATE TABLE test1", state)
        partiql.run_query("INSERT INTO test1 {'id':123}", state)
        query = "UPDATE test1 SET test1.a1 =1, test1.a2 = 'abc' where id = 'xxxINxxx'"
        partiql.run_query(query, state)
        query = "SELECT * FROM test1 BY pid"
        result = partiql.run_query(query, state)[0]
        assert result["id"] == 123

    def test_partiql_select_query(self):
        query = "SELECT id from test_data"
        input_data = """
        {
            test_data: [
                {"id": 1},
                {"id": 2.0},
                {"id": 'id3'}
            ]
        }
        """
        result = partiql.run_query(query, input_data)
        assert result == [{"id": 1}, {"id": 2.0}, {"id": "id3"}]

        state = clone(TEST_STATE)
        query = f"SELECT id from {TEST_TABLE}"
        result = partiql.run_query(query, state)
        assert result == [{"id": 1}, {"id": 2.0}, {"id": "id3"}]

    def test_update_query(self):
        state = clone(TEST_STATE)
        query = "UPDATE %s SET value=123 WHERE id=2" % TEST_TABLE
        partiql.run_query_update(query, state)
        query = "SELECT * FROM %s" % TEST_TABLE
        result = partiql.run_query(query, state)
        assert {"id": 1} in result
        assert {"id": 2.0, "value": 123} in result

    def test_update_with_complex_json(self):
        state = clone(TEST_STATE)

        query = "UPDATE %s as a by pid set value={'foo':345} WHERE id=2" % TEST_TABLE
        partiql.run_query_update(query, state)
        query = "UPDATE %s AS a BY pid set value.bar=True WHERE id=2" % TEST_TABLE
        partiql.run_query_update(query, state)
        select_query = "SELECT * FROM %s" % TEST_TABLE
        result = partiql.run_query(select_query, state)
        assert {"id": 1} in result
        assert {"id": 2.0, "value": {"foo": 345, "bar": True}} in result

        query = "UPDATE %s AS a BY pid set value.bar=FALSE WHERE id=2" % TEST_TABLE
        partiql.run_query_update(query, state)
        result = partiql.run_query(select_query, state)
        assert {"id": 2.0, "value": {"foo": 345, "bar": False}} in result

    def test_update_full_obj(self):
        state = clone(TEST_STATE)

        # update entry by table alias
        query = "UPDATE %s AS a BY pid set a = {'foo': 123} WHERE id=2" % TEST_TABLE
        partiql.run_query_update(query, state)
        select_query = "SELECT * FROM %s" % TEST_TABLE
        result = partiql.run_query(select_query, state)
        assert result == [{"id": 1}, {"foo": 123}, {"id": "id3"}]

        # update entry by table name
        query = "UPDATE %s SET %s = {} WHERE id='id3'" % (TEST_TABLE, TEST_TABLE)
        partiql.run_query_update(query, state)
        result = partiql.run_query(select_query, state)
        assert result == [{"id": 1}, {"foo": 123}, {}]

        # update entry with complex content
        query = "UPDATE %s SET %s = {'a':trUE, 'b': 2.0, 'c': {'d': 3}} WHERE id=1" % (
            TEST_TABLE,
            TEST_TABLE,
        )
        partiql.run_query_update(query, state)
        result = partiql.run_query(select_query, state)
        assert result == [{"a": True, "b": 2.0, "c": {"d": 3}}, {"foo": 123}, {}]

    def test_query_empty_object(self):
        state = {TEST_TABLE: []}
        # insert empty document into table
        query = "INSERT INTO %s VALUE {}" % TEST_TABLE
        partiql.run_query(query, state)
        select_query = f"SELECT * FROM {TEST_TABLE}"
        result = partiql.run_query(select_query, state)
        assert result == [{}]
