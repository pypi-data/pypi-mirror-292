import base64
import datetime
import io
import itertools
import json
import logging
import time
from typing import Optional

import amazon.ion.simpleion as ion
import pytest
from amazon.ion import simpleion
from amazon.ion.core import Timestamp
from localstack import config
from localstack.pro.core.services.qldb import partiql
from localstack.testing.aws.util import is_aws_cloud
from localstack.testing.config import (
    TEST_AWS_ACCESS_KEY_ID,
    TEST_AWS_REGION_NAME,
    TEST_AWS_SECRET_ACCESS_KEY,
)
from localstack.testing.pytest import markers
from localstack.utils.aws import arns, resources
from localstack.utils.json import json_safe
from localstack.utils.kinesis import kinesis_connector
from localstack.utils.strings import short_uid, to_bytes, to_str
from localstack.utils.sync import retry
from localstack.utils.time import (
    TIMESTAMP_FORMAT_MICROS,
    parse_timestamp,
    timestamp,
    timestamp_millis,
)
from localstack_snapshot.snapshots.transformer import KeyValueBasedTransformer
from pyqldb.driver.qldb_driver import QldbDriver

from . import aws_helpers

LOG = logging.getLogger()


@pytest.fixture()
def create_ledger(aws_client):
    ledger_names = []

    def _create(name: Optional[str] = None) -> dict:
        def _ledger_ready():
            result = aws_client.qldb.describe_ledger(Name=ledger_name)
            assert result["State"] == "ACTIVE"
            return result

        ledger_name = name or f"ledger-{short_uid()}"
        aws_client.qldb.create_ledger(Name=ledger_name, PermissionsMode="ALLOW_ALL")

        ledger_names.append(ledger_name)
        result = retry(_ledger_ready, sleep=2, retries=80)
        return result

    yield _create

    for ledger_name in ledger_names:
        try:
            aws_client.qldb.update_ledger(Name=ledger_name, DeletionProtection=False)
            aws_client.qldb.delete_ledger(Name=ledger_name)
        except Exception as e:
            LOG.debug("Unable to delete ledger %s: %s", ledger_name, e)


@pytest.fixture()
def qldb_ledger(create_ledger):
    return create_ledger()


class SimpleTransaction:
    def __init__(self, ledger_name: str):
        self.ledger_name = ledger_name
        # create driver, start session and transaction
        self.driver = Utils._get_driver(ledger_name)
        self.session = self.driver._get_session(start_new_session=True)
        self.transaction = self.session._start_transaction()

    def execute_statement(self, statement: str, *parameters):
        return self.transaction._execute_statement(statement, *parameters)

    def commit(self):
        return self.transaction._commit()

    def new_transaction(self):
        return SimpleTransaction(self.ledger_name)


@pytest.fixture()
def qldb_transaction(qldb_ledger, aws_client):
    ledger_name = qldb_ledger["Name"]
    return SimpleTransaction(ledger_name)


@pytest.fixture
def snapshot_transformers(snapshot):
    snapshot.add_transformer(snapshot.transform.key_value("documentId"))
    snapshot.add_transformer(snapshot.transform.key_value("strandId", reference_replacement=False))
    snapshot.add_transformer(snapshot.transform.key_value("txId"))
    snapshot.add_transformer(snapshot.transform.key_value("id", reference_replacement=False))
    snapshot.add_transformer(snapshot.transform.key_value("hash"))
    snapshot.add_transformer(snapshot.transform.key_value("txTime", reference_replacement=False))


class Utils:
    @staticmethod
    def _create_table(driver: QldbDriver, table_name: str):
        driver.execute_lambda(lambda txn: txn.execute_statement(f"CREATE TABLE {table_name}"))

    @staticmethod
    def _create_index(driver: QldbDriver, table_name: str, index_attribute: str) -> None:
        driver.execute_lambda(
            lambda txn: txn.execute_statement(f"CREATE INDEX ON {table_name} ({index_attribute})")
        )

    @staticmethod
    def _execute_statement(driver: QldbDriver, *args, **kwargs):
        return driver.execute_lambda(lambda txn: txn.execute_statement(*args, **kwargs))

    @staticmethod
    def _get_driver(ledger_name: str):
        return get_qldb_driver(ledger_name)

    @classmethod
    def _query_data(cls, query: str, *args, ledger_name: str = None, **kwargs):
        driver = cls._get_driver(ledger_name)
        cursor = cls._execute_statement(driver, query, *args, **kwargs)
        result = []
        for entry in cursor:
            result.append(partiql.convert_ion_to_json(entry))
        return result

    @staticmethod
    def _to_ion(ob: object):
        return simpleion.loads(simpleion.dumps(ob))


class TestQLDB:
    @markers.aws.validated
    # it is unfortunate but we should skip the `State` field since we always return `ACTIVE`
    @markers.snapshot.skip_snapshot_verify(paths=["$..State"])
    @pytest.mark.parametrize("deletion_protection", [True, False, None])
    def test_create_ledger_response(self, aws_client, cleanups, snapshot, deletion_protection):
        ledger_name = f"ledger-{short_uid()}"
        snapshot.add_transformer(snapshot.transform.regex(ledger_name, "<ledger-name>"))

        create_kwargs = {
            "Name": ledger_name,
            "PermissionsMode": "ALLOW_ALL",
        }
        if deletion_protection is not None:
            create_kwargs["DeletionProtection"] = deletion_protection

        response = aws_client.qldb.create_ledger(**create_kwargs)

        def _delete_ledger():
            try:
                if deletion_protection is not False:
                    aws_client.qldb.update_ledger(Name=ledger_name, DeletionProtection=False)
                aws_client.qldb.delete_ledger(Name=ledger_name)
            except Exception as e:
                LOG.debug("Unable to delete ledger %s: %s", ledger_name, e)

        cleanups.append(_delete_ledger)
        snapshot.match("create-ledger", response)

        def _ledger_ready():
            result = aws_client.qldb.describe_ledger(Name=ledger_name)
            assert result["State"] == "ACTIVE"
            return result

        describe_response = retry(_ledger_ready, sleep=2, retries=80)
        snapshot.match("describe-active-ledger", describe_response)

    @markers.aws.unknown
    def test_list_ledgers(self, qldb_ledger, aws_client):
        ledger_name = qldb_ledger["Name"]
        result = [
            ld for ld in aws_client.qldb.list_ledgers()["Ledgers"] if ld["Name"] == ledger_name
        ]
        assert len(result) == 1

    @markers.aws.unknown
    def test_list_tables(self, qldb_ledger):
        ledger_name = qldb_ledger["Name"]
        driver = Utils._get_driver(ledger_name)

        tables = list(driver.list_tables())
        tables = partiql.convert_ion_to_json(tables)
        assert tables == []
        Utils._create_table(driver, "foobar1")
        Utils._create_table(driver, "foobar2")
        tables = list(driver.list_tables())
        tables = partiql.convert_ion_to_json(tables)
        assert tables == ["foobar1", "foobar2"]

    @markers.aws.unknown
    def test_query_with_parameters(self, qldb_ledger, aws_client):
        ledger_name = qldb_ledger["Name"]
        driver = Utils._get_driver(ledger_name)

        Utils._create_table(driver, "test")
        Utils._execute_statement(driver, "INSERT INTO test VALUE {'a':?}", 1)
        select_query = "SELECT * from test"
        result = Utils._query_data(select_query, ledger_name=ledger_name)
        assert result == [{"a": 1}]
        driver.execute_lambda(
            lambda txn: txn.execute_statement(
                "UPDATE test SET b=?, d = ? where a=?", {"c": True}, "e", 1
            )
        )
        result = Utils._query_data(select_query, ledger_name=ledger_name)
        assert result == [{"a": 1, "b": {"c": True}, "d": "e"}]

    @markers.aws.unknown
    def test_insert_multiple_docs(self, qldb_ledger):
        ledger_name = qldb_ledger["Name"]
        driver = Utils._get_driver(ledger_name)

        query = """
        INSERT INTO test123 << {
            'id': 'id1',
            'attr1': 123.45
        }, {
            'id': 'id2',
            'attr2': true
        }
        >>
        """

        Utils._create_table(driver, "test123")
        Utils._execute_statement(driver, query, 1)

        result = Utils._query_data("SELECT * from test123", ledger_name=ledger_name)
        assert result == [{"id": "id1", "attr1": 123.45}, {"id": "id2", "attr2": True}]

    @markers.aws.unknown
    def test_query_join_tables(self, qldb_ledger):
        ledger_name = qldb_ledger["Name"]
        driver = Utils._get_driver(ledger_name)

        # create tables
        Utils._create_table(driver, "Vehicle")
        Utils._create_table(driver, "VehicleRegistration")

        # insert data
        persons_to_vehicles = {"p1": ["v1"], "p2": ["v2", "v3"]}
        for person, vehicles in persons_to_vehicles.items():
            for vehicle in vehicles:
                result1 = Utils._query_data(
                    "INSERT INTO Vehicle << ? >>",
                    {"id": vehicle},
                    ledger_name=ledger_name,
                )
                result2 = Utils._query_data(
                    "INSERT INTO VehicleRegistration VALUE ?",
                    {"id": vehicle, "Owner": {"PersonId": person}},
                    ledger_name=ledger_name,
                )
                result1 = result1[0] if isinstance(result1, list) else result1
                result2 = result2[0] if isinstance(result2, list) else result2
                assert "documentId" in result1
                assert "documentId" in result2

        # run queries
        query = (
            "SELECT Vehicle FROM Vehicle INNER JOIN VehicleRegistration AS r "
            "ON Vehicle.id = r.id WHERE r.Owner.PersonId = ?"
        )

        result = []
        for pid in persons_to_vehicles.keys():
            tmp_data = Utils._query_data(query, pid, ledger_name=ledger_name)
            result.extend(tmp_data)
        assert result == [{"Vehicle": {"id": id}} for id in ["v1", "v2", "v3"]]

    @markers.aws.unknown
    def test_complex_insert(self, qldb_ledger):
        query = """
        insert into Test `{id:"d4fcbe9680784e9c8b526474df87a16f",
            rate:5.00d-2,date1:2020-07-17T14:29:42.909Z,date2:2040-07-04T12:00:00.000Z,
            another_id:"9d3cee8bf9ba4b9582999108d3cf83be",
            third_id:"82b5426afbdc4b58b209f4ecb7545198",bool_col:false,
            nullable_col:null,small_number:1.06800d-5}`
        """
        ledger_name = qldb_ledger["Name"]
        driver = Utils._get_driver(ledger_name)

        # create tables
        Utils._create_table(driver, "Test")
        result = Utils._query_data(query, ledger_name=ledger_name)
        assert "documentId" in result[0]
        result = Utils._query_data("SELECT * FROM Test", ledger_name=ledger_name)
        assert result[0]["id"] == "d4fcbe9680784e9c8b526474df87a16f"
        assert result[0]["rate"] == 0.05
        assert result[0]["bool_col"] is False
        assert result[0]["nullable_col"] is None
        assert result[0]["small_number"] == 1.068e-05

    @markers.aws.unknown
    def test_describe_and_delete_ledger(self, qldb_ledger, aws_client):
        ledger_name = qldb_ledger["Name"]
        result = aws_client.qldb.describe_ledger(Name=ledger_name)

        assert result["Name"] == ledger_name
        assert result["State"] == "ACTIVE"
        assert result["DeletionProtection"] is True

        with pytest.raises(Exception) as ctx:
            aws_client.qldb.delete_ledger(Name=ledger_name)
        assert "DeletionProtection" in str(ctx.value)

        # disable DeletionProtection
        aws_client.qldb.update_ledger(Name=ledger_name, DeletionProtection=False)

        # clean up
        aws_client.qldb.delete_ledger(Name=ledger_name)
        with pytest.raises(Exception):
            aws_client.qldb.describe_ledger(Name=ledger_name)

    @markers.aws.unknown
    def test_query_with_params_via_api(self, qldb_ledger, qldb_transaction):
        ledger_name = qldb_ledger["Name"]

        # create table
        session = Utils._get_driver(ledger_name)
        session.execute_lambda(lambda txn: txn.execute_statement("CREATE TABLE People"))

        # run query
        query = "UPDATE People SET age = ? WHERE firstName = ?"
        params = [
            {"IonBinary": base64.b64decode("4AEA6iFA")},
            {"IonBinary": base64.b64decode("4AEA6oRKb2hu")},
        ]
        qldb_transaction.execute_statement(query, *params)

        # commit transaction
        qldb_transaction.commit()

    @markers.aws.validated
    def test_update_query_response(self, qldb_ledger, qldb_transaction, snapshot):
        snapshot.add_transformer(snapshot.transform.key_value("documentId"))

        # create table, insert data
        qldb_transaction.execute_statement("CREATE TABLE People")
        query = "INSERT INTO People VALUE {'age': ?, 'firstName': ?}"
        qldb_transaction.execute_statement(query, 23, "Alice")
        result = qldb_transaction.execute_statement(query, 25, "Bob")
        result = [dict(r) for r in result]
        snapshot.match("insert-result", result)
        qldb_transaction.execute_statement(query, 21, "Charles")

        # run UPDATE query - assert that result contains entry with `documentId` attribute (via snapshot)
        query = "UPDATE People SET age = ? WHERE firstName = ?"
        result = qldb_transaction.execute_statement(query, 30, "Bob")
        result = [dict(r) for r in result]
        snapshot.match("update-result", result)

    @markers.skip_offline
    @markers.aws.unknown
    def test_stream_journal(self, qldb_ledger, aws_client, account_id, region_name):
        kinesis = aws_client.kinesis
        records = []

        def process_records(recs):
            recs = [json.loads(to_str(base64.b64decode(to_bytes(r["data"])))) for r in recs]
            records.extend(recs)

        # start Kinesis client
        kinesis_name = f"s-{short_uid()}"
        kinesis_arn = arns.kinesis_stream_arn(kinesis_name, account_id, region_name)
        resources.create_kinesis_stream(kinesis, kinesis_name, delete=True)
        thread = kinesis_connector.listen_to_kinesis(
            stream_name=kinesis_name,
            account_id=account_id,
            region_name=region_name,
            listener_func=process_records,
            wait_until_started=True,
        )

        # create ledger and stream configuration
        ledger_name = qldb_ledger["Name"]
        stream_name = f"s-{short_uid()}"
        result = aws_client.qldb.stream_journal_to_kinesis(
            LedgerName=ledger_name,
            RoleArn=arns.iam_role_arn("r1", account_id=account_id, region_name=region_name),
            StreamName=stream_name,
            KinesisConfiguration={"StreamArn": kinesis_arn},
            InclusiveStartTime=timestamp_millis(),
        )
        assert "StreamId" in result

        # insert docs into ledger
        num_entries = 3
        for i in range(num_entries):
            query = f"CREATE TABLE Test{i}; INSERT INTO Test{i} ?"
            Utils._query_data(query, {"id": i}, ledger_name=ledger_name)

        def receive_journal_stream():
            assert len(records) == num_entries
            # TODO: add assertions
            # print(records)

        # receive stream entries
        retry(receive_journal_stream)

        # clean up
        thread.stop()
        kinesis.delete_stream(StreamName=kinesis_name)

    @markers.aws.validated
    def test_query_committed_views(self, qldb_ledger, snapshot, snapshot_transformers):
        ledger_name = qldb_ledger["Name"]
        snapshot.add_transformer(
            KeyValueBasedTransformer(
                lambda _, v: v if isinstance(v, str) and ledger_name in v else None,
                replacement="ledger_name",
            )
        )

        snapshot.match("ledger", json_safe(qldb_ledger))
        driver = Utils._get_driver(ledger_name)
        table_name = f"t_{short_uid()}"

        Utils._create_table(driver, table_name)
        test_value = 123
        result = Utils._execute_statement(
            driver, f"INSERT INTO {table_name} VALUE {{'a':?}}", test_value
        )

        insert_result = list(result)
        insert_result = [dict(res) for res in insert_result]
        snapshot.match("insert_result", insert_result)

        query = f"SELECT * FROM _ql_committed_{table_name} as d"
        for idx, search_value in enumerate([None, test_value, "'invalid'"]):
            _query = f"{query} where data.a = {search_value}" if search_value else query
            result = Utils._query_data(_query, ledger_name=ledger_name)
            snapshot.match(f"metadata_result_{idx}", json_safe(result))

            if search_value == "'invalid'":
                assert not result
                continue

            assert len(result) == 1
            assert result[0].get("blockAddress")
            assert result[0].get("hash")
            assert result[0].get("metadata")

    @pytest.mark.skip
    @markers.aws.validated
    def test_aws_tutorial(self, create_ledger, aws_client):
        # 1. Create a new ledger
        # https://docs.aws.amazon.com/qldb/latest/developerguide/getting-started.python.step-1.html
        ledger_name = f"{aws_helpers.Constants.LEDGER_NAME}-{short_uid()}"
        create_ledger(ledger_name)

        driver = Utils._get_driver(ledger_name)

        # 3. Create tables, indexes, and sample data
        # https://docs.aws.amazon.com/qldb/latest/developerguide/getting-started.python.step-3.html

        # 3a. create tables
        aws_helpers.create_table(driver, aws_helpers.Constants.DRIVERS_LICENSE_TABLE_NAME)
        aws_helpers.create_table(driver, aws_helpers.Constants.PERSON_TABLE_NAME)
        aws_helpers.create_table(driver, aws_helpers.Constants.VEHICLE_TABLE_NAME)
        aws_helpers.create_table(driver, aws_helpers.Constants.VEHICLE_REGISTRATION_TABLE_NAME)

        # 3b. create indexes
        aws_helpers.create_index(
            driver,
            aws_helpers.Constants.PERSON_TABLE_NAME,
            aws_helpers.Constants.GOV_ID_INDEX_NAME,
        )
        aws_helpers.create_index(
            driver,
            aws_helpers.Constants.VEHICLE_TABLE_NAME,
            aws_helpers.Constants.VEHICLE_VIN_INDEX_NAME,
        )
        aws_helpers.create_index(
            driver,
            aws_helpers.Constants.VEHICLE_REGISTRATION_TABLE_NAME,
            aws_helpers.Constants.LICENSE_PLATE_NUMBER_INDEX_NAME,
        )
        aws_helpers.create_index(
            driver,
            aws_helpers.Constants.VEHICLE_REGISTRATION_TABLE_NAME,
            aws_helpers.Constants.VEHICLE_VIN_INDEX_NAME,
        )
        aws_helpers.create_index(
            driver,
            aws_helpers.Constants.DRIVERS_LICENSE_TABLE_NAME,
            aws_helpers.Constants.PERSON_ID_INDEX_NAME,
        )
        aws_helpers.create_index(
            driver,
            aws_helpers.Constants.DRIVERS_LICENSE_TABLE_NAME,
            aws_helpers.Constants.LICENSE_NUMBER_INDEX_NAME,
        )

        # 3c. create sample data
        aws_helpers.update_and_insert_documents(driver)

        # 5. Modify documents
        # https://docs.aws.amazon.com/qldb/latest/developerguide/getting-started.python.step-5.html

        vehicle_vin = aws_helpers.SampleData.VEHICLE[0]["VIN"]
        previous_owner = aws_helpers.SampleData.PERSON[0]["GovId"]
        new_owner = aws_helpers.SampleData.PERSON[1]["GovId"]

        aws_helpers.validate_and_update_registration(driver, vehicle_vin, previous_owner, new_owner)

        # 6. View the revision history
        # https://docs.aws.amazon.com/qldb/latest/developerguide/getting-started.python.step-6.html
        vin = aws_helpers.SampleData.VEHICLE_REGISTRATION[0]["VIN"]
        primary_owners = list(itertools.chain(aws_helpers.previous_primary_owners(driver, vin)))
        assert len(primary_owners) > 0

        # 7. Verify the documents
        # https://docs.aws.amazon.com/qldb/latest/developerguide/getting-started.python.step-7.html

        registration = aws_helpers.SampleData.VEHICLE_REGISTRATION[0]
        vin = registration["VIN"]
        aws_helpers.verify_registration(aws_client.qldb, driver, ledger_name, vin)

    @markers.aws.validated
    def test_query_ion_timestamp(self, snapshot, qldb_transaction):
        ledger_name = qldb_transaction.ledger_name

        # create table
        qldb_transaction.execute_statement("CREATE TABLE test")

        # insert test data
        test_timestamp = "2022-12-30T00:25:28.000000Z"
        ion_binary = b"\xe0\x01\x00\xea\xee\x90\x81\x83\xdd\x87\xbb\x8acreated_at\xda\x8ah\x80\x0f\xe6\x8c\x9e\x80\x99\x9c"
        qldb_transaction.execute_statement("INSERT INTO test VALUE ?", {"IonBinary": ion_binary})

        # request raw IonBinary result from QLDB, assert the IonBinary contains proper result
        result = qldb_transaction.execute_statement("SELECT * FROM test")
        values = list(result)
        snapshot.match("query-result-1", values)
        ion_obj = ion.load(io.BytesIO(values[0]["IonBinary"]))
        ts = parse_timestamp(test_timestamp)
        ion_timestamp = Timestamp(
            ts.year,
            ts.month,
            ts.day,
            ts.hour,
            ts.minute,
            ts.second,
            ts.microsecond,
            # note: copying the two parameters below for parity reasons (TODO: check discrepancy)
            tzinfo=ion_obj["created_at"].tzinfo,
            fractional_precision=ion_obj["created_at"].fractional_precision,
        )
        assert ion_obj == {"created_at": ion_timestamp}

        # commit transaction (to make test item available in next query below)
        qldb_transaction.commit()

        # run query in text mode
        result = Utils._query_data("SELECT * FROM test", ledger_name=ledger_name)
        snapshot.match("query-result-2", result)

    @markers.aws.validated
    def test_query_by_metadata(self, snapshot, qldb_transaction, snapshot_transformers):
        # create table with data
        qldb_transaction.execute_statement("CREATE TABLE test")
        qldb_transaction.execute_statement("INSERT INTO test VALUE ?", {"test": 123})
        qldb_transaction.commit()

        # select data
        transaction = qldb_transaction.new_transaction()
        result = transaction.execute_statement("SELECT * FROM test BY id")
        result = [dict(res) for res in result]
        doc_id = result[0]["id"]

        # insert second item
        transaction.execute_statement("INSERT INTO test VALUE ?", {"test": 456})
        transaction.commit()

        # TODO: fix logic and assert that data is only visible after committing the transaction

        def _snapshot_result(name, _result):
            _result = [dict(res) for res in _result]
            _result = [
                {k: dict(v) if str(v).startswith("{") else v for k, v in res.items()}
                for res in _result
            ]
            _result = [{k: v for k, v in res.items() if isinstance(v, dict)} for res in _result]
            # note: order of items is indeterministic in AWS!
            _result = sorted(
                _result, key=lambda item: item.get("test") or item["blockAddress"]["sequenceNo"]
            )
            snapshot.match(name, _result)

        # select all items
        transaction = transaction.new_transaction()
        result = transaction.execute_statement("SELECT * FROM test BY id")
        result = [dict(res) for res in result]
        _result = sorted(result, key=lambda item: item["test"])
        snapshot.match("select-all", result)

        # select all committed table data
        result = transaction.execute_statement("SELECT * FROM _ql_committed_test AS t")
        _snapshot_result("select-committed", result)

        # select committed data by metadata.id
        result = transaction.execute_statement(
            "SELECT * FROM _ql_committed_test AS t WHERE t.metadata.id = ?", doc_id
        )
        _snapshot_result("select-committed-by-id", result)

        # assert that metadata.id does not work on regular tables (empty result)
        result = transaction.execute_statement(
            "SELECT * FROM test WHERE test.metadata.id = ?", doc_id
        )
        _snapshot_result("select-by-id-regular", result)


class TestHistoryQueries:
    @markers.aws.validated
    def test_query_history(self, qldb_ledger, snapshot, snapshot_transformers):
        ledger_name = qldb_ledger["Name"]
        driver = Utils._get_driver(ledger_name)
        table_name = f"t_{short_uid()}"
        Utils._create_table(driver, table_name)

        # insert document
        result = Utils._query_data(
            "INSERT INTO %s {'id':123}" % table_name, ledger_name=ledger_name
        )
        assert "documentId" in result[0]
        doc_id = result[0]["documentId"]
        assert len(doc_id) == 22

        # run history query (twice)
        Utils._query_data(f"SELECT * FROM {table_name} AS a BY pid", ledger_name=ledger_name)
        result = Utils._query_data(
            f"SELECT * FROM history({table_name}) AS a", ledger_name=ledger_name
        )
        snapshot.match("history-1", result)
        assert len(result) > 0
        assert "blockAddress" in result[0]
        assert "data" in result[0]
        assert partiql.ATTR_ID_ALIASES not in result[0]

        # get history, filtering by ID - assert that INSERT entry is contained
        history_query = f"SELECT * FROM history({table_name}) AS a WHERE a.metadata.id = '{doc_id}'"
        result = Utils._query_data(history_query, ledger_name=ledger_name)
        assert len(result) == 1
        assert result[0]["metadata"]["id"] == doc_id
        snapshot.match("history-2", result)

        # update document
        Utils._query_data(
            f"UPDATE {table_name} BY pid SET foo=123 WHERE pid='{doc_id}'",
            ledger_name=ledger_name,
        )

        # get history and assert that new entry from UPDATE is contained
        result = Utils._query_data(history_query, ledger_name=ledger_name)
        assert len(result) == 2
        assert result[0]["metadata"]["version"] == 0
        assert result[1]["metadata"]["version"] == 1
        data_entries = [d["data"] for d in result]
        for data in data_entries:
            assert "pid" not in data
            assert partiql.ATTR_ID_ALIASES not in data
        snapshot.match("history-3", result)

    @markers.aws.validated
    def test_query_history_with_start_end_timestamps(self, qldb_transaction, snapshot):
        # create table
        transaction = qldb_transaction.new_transaction()
        transaction.execute_statement("CREATE TABLE test")
        time1 = datetime.datetime.utcnow()

        # commit first document
        result = transaction.execute_statement(
            "INSERT INTO test VALUE ?", {"attributes": {"value": "foo 1234 bar"}}
        )
        doc_id = list(result)[0]["documentId"]
        _commit(transaction)
        time2 = datetime.datetime.utcnow()

        # commit second document
        transaction = qldb_transaction.new_transaction()
        transaction.execute_statement(
            "INSERT INTO test VALUE ?", {"attributes": {"value": "foo 1234 bar2"}}
        )
        _commit(transaction)
        time3 = datetime.datetime.utcnow()

        # update first document
        transaction = qldb_transaction.new_transaction()
        transaction.execute_statement(
            f"UPDATE test BY pid SET attributes.\"value\"='foo 1234 bar3' WHERE pid='{doc_id}'"
        )
        _commit(transaction)
        time4 = datetime.datetime.utcnow()

        query_template = (
            "SELECT e.data.* FROM history(test, `<start>`, `<end>`) "
            "AS e, @e.data.attributes AS a WHERE a.\"value\" LIKE '%1234%'"
        )

        def _query(start_time, end_time, snapshot_key):
            transaction = qldb_transaction.new_transaction()
            query = query_template.replace("<start>", _ts(start_time)).replace(
                "<end>", _ts(end_time)
            )
            result = transaction.execute_statement(query)
            result = [dict(r) for r in result]
            # note: QLDB does not support ORDER BY, and we don't test for result ordering right now
            result = sorted(result, key=lambda item: str(item))
            snapshot.match(snapshot_key, result)

        # select data from different time ranges
        _query(time1, time2, "around-first-insert")
        _query(time1, time3, "first-and-second-inserts")
        _query(time2, time3, "around-second-insert")
        _query(time2, time4, "second-insert-and-update")
        # note: history(..) returns revisions that are *active* during the given time interval, and *not*
        # revisions that were committed during that interval - hence the query below also yields results
        _query(time4, datetime.datetime.utcnow(), "history-query")

    @markers.aws.validated
    def test_query_history_with_updates(self, qldb_transaction, snapshot, snapshot_transformers):
        transaction = qldb_transaction.new_transaction()
        transaction.execute_statement("CREATE TABLE test")
        _commit(transaction)

        # insert document
        time0 = datetime.datetime.utcnow()
        transaction = qldb_transaction.new_transaction()
        result = transaction.execute_statement("INSERT INTO test {'id':123}")
        doc_id = list(result)[0]["documentId"]
        _commit(transaction)

        # update #1
        time1 = datetime.datetime.utcnow()
        transaction = qldb_transaction.new_transaction()
        transaction.execute_statement(f"UPDATE test BY pid SET attr='2' WHERE pid='{doc_id}'")
        _commit(transaction)

        # update #2
        time2 = datetime.datetime.utcnow()
        transaction = qldb_transaction.new_transaction()
        transaction.execute_statement(f"UPDATE test BY pid SET attr='3' WHERE pid='{doc_id}'")
        _commit(transaction)
        time3 = datetime.datetime.utcnow()

        # construct different combinations of time periods for history scans
        times = (time0, time1, time2, time3)
        combinations = []
        for start in range(0, len(times) - 1):
            for end in range(start + 1, len(times)):
                combinations.append((times[start], times[end]))
        combinations.append((time3, time3 + datetime.timedelta(seconds=1)))

        transaction = qldb_transaction.new_transaction()
        query_template = "SELECT * FROM history(test, `<start>`, `<end>`)"
        for idx, entry in enumerate(combinations):
            start, end = entry
            result = transaction.execute_statement(
                query_template.replace("<start>", _ts(start)).replace("<end>", _ts(end))
            )
            result = [{"data": r["data"], "version": r["metadata"]["version"]} for r in result]
            snapshot.match(f"history-{idx}", result)


def _ts(time_stamp: datetime.datetime) -> str:
    return timestamp(time_stamp, format=TIMESTAMP_FORMAT_MICROS)


def _commit(transaction: SimpleTransaction):
    transaction.commit()
    if is_aws_cloud():
        # commit timestamps can fluctuate/diverge a bit in real AWS, hence adding a short sleep here
        time.sleep(2)


def get_qldb_driver(ledger_name: str) -> QldbDriver:
    if is_aws_cloud():
        kwargs = {}
    else:
        kwargs = {
            "endpoint_url": config.internal_service_url(),
            "aws_access_key_id": TEST_AWS_ACCESS_KEY_ID,
            "aws_secret_access_key": TEST_AWS_SECRET_ACCESS_KEY,
            "region_name": TEST_AWS_REGION_NAME,
        }

    return QldbDriver(ledger_name=ledger_name, **kwargs)
