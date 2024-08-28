import bz2
import csv
import gzip
from io import BytesIO, StringIO

from localstack.testing.aws.util import is_aws_cloud
from localstack.testing.pytest import markers

""" Integration tests for S3 SELECT. All tests in here have been validated against AWS Cloud """
import dataclasses
import json
import logging
import os.path
import tempfile
import textwrap
import typing
from json import JSONDecodeError
from typing import Any, List, Optional

import botocore.eventstream
import pytest as pytest
from botocore.exceptions import ClientError
from localstack import config
from localstack.utils.strings import short_uid

BASEDIR = os.path.abspath(os.path.dirname(__file__))

LOG = logging.Logger(__name__)


# the reason we're not just using the strings to compare results is that it's much more clear what needs to be fixed
# by comparing the full parsed structure also it's much easier to write the 'expected' fields this way
def extract_json_records_from_stream(event_stream: botocore.eventstream.EventStream) -> List[dict]:
    """util fn to fetch the JSON output records from the S3 SELECT query"""
    records = []
    for event in event_stream:
        if "Records" in event:
            records_raw = event["Records"]["Payload"].decode("utf-8")
            for r in records_raw.split("\n"):
                if r.strip():
                    try:
                        decoded = json.loads(r)
                        records.append(decoded)
                    except JSONDecodeError as e:
                        LOG.warning(e)
                        continue
    return records


def extract_csv_records_from_stream(event_stream: botocore.eventstream.EventStream) -> List[str]:
    """util fn to fetch the CSV output records from the S3 SELECT query"""
    records = []
    for event in event_stream:
        if "Records" in event:
            records_raw = event["Records"]["Payload"].decode("utf-8")
            for r in records_raw.split("\n"):
                if r.strip():
                    records.append(r)
    return records


if typing.TYPE_CHECKING:
    from mypy_boto3_s3.type_defs import InputSerializationTypeDef, OutputSerializationTypeDef


# these three classes could probably just be replaced with a single recursive one


@dataclasses.dataclass
class S3SelectTestParameterSet:
    query: str
    input_serialization: "InputSerializationTypeDef"
    output_serialization: "OutputSerializationTypeDef"
    compression: Optional[str] = "NONE"
    file: Optional[str] = None
    content: Optional[str] = None
    expected: Optional[Any] = None
    error: Optional[str] = None


@dataclasses.dataclass
class S3SelectTestQuery:
    query: str
    expected: Optional[Any] = None
    error: Optional[str] = None
    content: Optional[str] = None
    input_serialization: Optional["InputSerializationTypeDef"] = None
    output_serialization: Optional["OutputSerializationTypeDef"] = None


@dataclasses.dataclass
class S3SelectTestGroup:
    queries: List[S3SelectTestQuery]
    # if set, these will be used as a default if the query itself doesn't set them
    input_serialization: Optional["InputSerializationTypeDef"] = None
    output_serialization: Optional["OutputSerializationTypeDef"] = None
    expected: Optional[Any] = None
    file: Optional[str] = None
    content: Optional[str] = None

    def render(self) -> List[S3SelectTestParameterSet]:
        return [
            S3SelectTestParameterSet(
                query=q.query,
                input_serialization=q.input_serialization
                if q.input_serialization is not None
                else self.input_serialization,
                output_serialization=q.output_serialization
                if q.output_serialization is not None
                else self.output_serialization,
                expected=q.expected if q.expected is not None else self.expected,
                error=q.error,
                content=q.content if q.content is not None else self.content,
                file=self.file,
            )
            for q in self.queries
        ]


TESTS_CUSTOM = S3SelectTestGroup(
    file=os.path.join(BASEDIR, "data/testdata-s3select.csv"),
    queries=[
        S3SelectTestQuery(
            query="SELECT s._2, s._1, DATE_ADD(year, 5, CAST(s._3 AS TIMESTAMP)) FROM S3Object s WHERE s._1='Jane Doe'",
            input_serialization={"CSV": {"FileHeaderInfo": "IGNORE"}, "CompressionType": "NONE"},
            output_serialization={"JSON": {}},
            expected=[{"_2": "20", "_1": "Jane Doe", "_3": "2015-01-02T00:00:00Z"}],
        ),
    ],
).render()

# TODO: extend these
TESTS_NUMBERS = S3SelectTestGroup(
    file=os.path.join(BASEDIR, "data/numbers.csv"),
    input_serialization={"CSV": {"FileHeaderInfo": "USE"}, "CompressionType": "NONE"},
    output_serialization={"JSON": {}},
    queries=[
        S3SelectTestQuery(
            query="""SELECT s.name FROM S3Object s WHERE s.num_mixed = '0'""",
            expected=[{"name": "E"}],
        ),
        S3SelectTestQuery(
            query="""SELECT s.name FROM S3Object s WHERE CAST(s.num_mixed AS INTEGER) = 0""",
            error="underflow",
        ),
        S3SelectTestQuery(
            query="""SELECT s.name FROM S3Object s WHERE CAST(s.num_mixed AS DECIMAL) = 0""",
            expected=[{"name": "E"}],
        ),
        S3SelectTestQuery(
            query="""SELECT s.name FROM S3Object s WHERE CAST(s.num_int AS INTEGER) = 9223372036854775808""",
            error="overflow",
        ),
        S3SelectTestQuery(
            query="""SELECT s.name FROM S3Object s WHERE CAST(s.num_int AS INTEGER) = -1""",
            expected=[{"name": "A"}],
        ),
        S3SelectTestQuery(
            query="""SELECT s.name FROM S3Object s WHERE CAST(s.num AS INTEGER) = 9223372036854775808""",
            error="overflow",
        ),
    ],
).render()

# specific tests that validate behavior that was fixed in relation to customer support
TESTS_CUSTOMER = S3SelectTestGroup(
    file=os.path.join(BASEDIR, "data/2022-02-customerissue-overflow.csv"),
    input_serialization={"CSV": {"FileHeaderInfo": "USE"}, "CompressionType": "NONE"},
    output_serialization={"JSON": {}},
    queries=[
        S3SelectTestQuery(
            query="SELECT s.name FROM S3Object s WHERE s.num = '9223372036854775808223423409890'",
            expected=[{"name": "B"}],
        ),
        S3SelectTestQuery(
            query="SELECT s.name FROM S3Object s WHERE CAST(s.num_int AS INTEGER) = 2",
            expected=[{"name": "B"}],
        ),
        S3SelectTestQuery(
            query="SELECT s.name FROM S3Object s WHERE CAST(s.num_int AS INTEGER) = 9223372036854775808223423409890",
            error="overflow",
        ),
    ],
).render()

# tests that have been extracted from official AWS docs

TEST_AWS_QUERIES = [
    S3SelectTestQuery(
        query="SELECT * FROM s3object s where s.\"Name\" = 'Jane'",
        expected=[
            {
                "Name": "Jane",
                "PhoneNumber": "(949) 555-6704",
                "City": "Chicago",
                "Occupation": "Developer",
            }
        ],
    ),
]
TESTS_AWS_DOCS_NONE = S3SelectTestGroup(
    file=os.path.join(BASEDIR, "data/sample_data.csv"),
    input_serialization={"CSV": {"FileHeaderInfo": "USE"}, "CompressionType": "NONE"},
    output_serialization={"JSON": {}},
    queries=TEST_AWS_QUERIES,
).render()

TESTS_AWS_DOCS_GZIP = S3SelectTestGroup(
    file=os.path.join(BASEDIR, "data/sample_data.csv.gz"),
    input_serialization={"CSV": {"FileHeaderInfo": "USE"}, "CompressionType": "GZIP"},
    output_serialization={"JSON": {}},
    queries=TEST_AWS_QUERIES,
).render()

TESTS_AWS_DOCS_BZIP2 = S3SelectTestGroup(
    file=os.path.join(BASEDIR, "data/sample_data.csv.bz2"),
    input_serialization={"CSV": {"FileHeaderInfo": "USE"}, "CompressionType": "BZIP2"},
    output_serialization={"JSON": {}},
    queries=TEST_AWS_QUERIES,
).render()
TESTS_AWS_DOCS_COMPRESSION = TESTS_AWS_DOCS_NONE + TESTS_AWS_DOCS_GZIP + TESTS_AWS_DOCS_BZIP2

TESTS_AWS_DOCS_ATTRIBUTEACCESS = S3SelectTestGroup(
    file=os.path.join(BASEDIR, "data/attributeaccess-json-example.json"),
    input_serialization={"JSON": {"Type": "DOCUMENT"}, "CompressionType": "NONE"},
    output_serialization={"JSON": {}},
    queries=[
        S3SelectTestQuery(
            query="Select s.name from S3Object s", expected=[{"name": "Susan Smith"}]
        ),
        S3SelectTestQuery(
            query="Select s.projects[0].project_name from S3Object s",
            expected=[{"project_name": "project1"}],
        ),
    ],
).render()

TESTS_AWS_DOCS_FROM_1 = S3SelectTestGroup(
    file=os.path.join(BASEDIR, "data/from-example-1.json"),
    input_serialization={"JSON": {"Type": "LINES"}, "CompressionType": "NONE"},
    output_serialization={"JSON": {}},
    queries=[
        S3SelectTestQuery(
            query="SELECT id FROM S3Object[*].Rules[*].id",
            expected=[{"id": "1"}, {}, {"id": "2"}, {}],
        ),
    ],
).render()

TESTS_AWS_DOCS_FROM_2 = S3SelectTestGroup(
    file=os.path.join(BASEDIR, "data/from-example-2.json"),
    input_serialization={"JSON": {"Type": "LINES"}, "CompressionType": "NONE"},
    output_serialization={"JSON": {}},
    queries=[
        S3SelectTestQuery(
            query="SELECT d.dir_name, d.files FROM S3Object[*] d",
            expected=[
                {
                    "dir_name": "important_docs",
                    "files": [
                        {"name": "."},
                        {"name": ".."},
                        {"name": ".aws"},
                        {"name": "downloads"},
                    ],
                },
                {
                    "dir_name": "other_docs",
                    "files": [
                        {"name": "."},
                        {"name": ".."},
                        {"name": "my stuff"},
                        {"name": "backup"},
                    ],
                },
            ],
        ),
        S3SelectTestQuery(
            query="SELECT _1.dir_name, _1.owner FROM S3Object[*]",
            expected=[
                {"dir_name": "important_docs", "owner": "AWS S3"},
                {"dir_name": "other_docs", "owner": "User"},
            ],
        ),
    ],
).render()

TESTS_AWS_DOCS = (
    TESTS_AWS_DOCS_COMPRESSION
    + TESTS_AWS_DOCS_ATTRIBUTEACCESS
    + TESTS_AWS_DOCS_FROM_1
    + TESTS_AWS_DOCS_FROM_2
)


# Minio partially implements S3 SELECT
# Unfortunately most of their implementation isn't in parity with the AWS Cloud, so the tests had to be adapted/fixed in most cases.
# Last update: 2022-03-03 (commit ref: 88fd1cba71e3d574d07e36dfbf61f7be24eea0a4)
# See: https://github.com/minio/minio/blob/master/internal/s3select/select_test.go


def load_minio_test_from_json(filename: str, parse_json: bool, with_data: bool = False) -> dict:
    result = {"ids": [], "params": []}
    with open(filename) as f:
        data = json.loads(f.read())
        for d in data:
            if not d["query"]:
                continue
            result["ids"].append(d["id"])
            mapped_data = []
            for r in d["expected"].split("\n"):
                if r.strip():
                    if parse_json:
                        mapped_data.append(json.loads(r))
                    else:
                        mapped_data.append(r)
            if with_data:
                result["params"].append(
                    {
                        "query": d["query"].replace("'", "'"),
                        "expected": mapped_data,
                        "content": d["data"],
                    }
                )
            else:
                result["params"].append(
                    {
                        "query": d["query"].replace("'", "'"),
                        "expected": mapped_data,
                    }
                )
        return result


TESTS_JSON = load_minio_test_from_json(os.path.join(BASEDIR, "data/minio/json_queries.json"), True)
TESTS_JSON_WITH_DATA = load_minio_test_from_json(
    os.path.join(BASEDIR, "data/minio/json_queries_with_data.json"), True, True
)
TESTS_CSV = load_minio_test_from_json(os.path.join(BASEDIR, "data/minio/csv_queries.json"), False)
TESTS_CSV_2 = load_minio_test_from_json(
    os.path.join(BASEDIR, "data/minio/csv_queries_2.json"), True
)
TESTS_CSV_2_NOHEADER = load_minio_test_from_json(
    os.path.join(BASEDIR, "data/minio/csv_queries_2.noheader.json"), True
)
TESTS_CSV_3 = load_minio_test_from_json(
    os.path.join(BASEDIR, "data/minio/csv_queries_3.json"), False
)

TESTS_MINIO_JSON = S3SelectTestGroup(
    file=os.path.join(BASEDIR, "data/minio/json_queries.data.ldjson"),
    input_serialization={"JSON": {"Type": "LINES"}, "CompressionType": "NONE"},
    output_serialization={"JSON": {}},
    queries=[
        S3SelectTestQuery(query=x["query"], expected=x["expected"], content=x.get("content"))
        for x in TESTS_JSON["params"]
    ],
).render()

TESTS_MINIO_JSON_WITH_DATA = S3SelectTestGroup(
    input_serialization={"JSON": {"Type": "LINES"}, "CompressionType": "NONE"},
    output_serialization={"JSON": {}},
    queries=[
        S3SelectTestQuery(query=x["query"], expected=x["expected"], content=x.get("content"))
        for x in TESTS_JSON_WITH_DATA["params"]
    ],
).render()

TESTS_MINIO_CSV = S3SelectTestGroup(
    file=os.path.join(BASEDIR, "data/minio/csv_queries.data.csv"),
    input_serialization={
        "CSV": {
            "FileHeaderInfo": "USE",
            "FieldDelimiter": ",",
            "QuoteCharacter": '"',
            "QuoteEscapeCharacter": '"',
            "RecordDelimiter": "\n",
        },
        "CompressionType": "NONE",
    },
    output_serialization={"CSV": {}},
    queries=[
        S3SelectTestQuery(query=x["query"], expected=x["expected"], content=x.get("content"))
        for x in TESTS_CSV["params"]
    ],
).render()

TESTS_MINIO_CSV_2 = S3SelectTestGroup(
    file=os.path.join(BASEDIR, "data/minio/csv_queries_2.data.csv"),
    input_serialization={
        "CSV": {"FileHeaderInfo": "USE", "QuoteCharacter": '"'},
        "CompressionType": "NONE",
    },
    output_serialization={"JSON": {}},
    queries=[
        S3SelectTestQuery(query=x["query"], expected=x["expected"], content=x.get("content"))
        for x in TESTS_CSV_2["params"]
    ],
).render()

TESTS_MINIO_CSV_2_NOHEADER = S3SelectTestGroup(
    file=os.path.join(BASEDIR, "data/minio/csv_queries_2.data.csv"),
    input_serialization={
        "CSV": {"FileHeaderInfo": "IGNORE", "QuoteCharacter": '"'},
        "CompressionType": "NONE",
    },
    output_serialization={"JSON": {}},
    queries=[
        S3SelectTestQuery(query=x["query"], expected=x["expected"], content=x.get("content"))
        for x in TESTS_CSV_2_NOHEADER["params"]
    ],
).render()

TESTS_MINIO_CSV_3 = S3SelectTestGroup(
    file=os.path.join(BASEDIR, "data/minio/csv_queries_3.data.csv"),
    input_serialization={
        "CSV": {"FileHeaderInfo": "USE", "QuoteCharacter": '"'},
        "CompressionType": "NONE",
    },
    output_serialization={"CSV": {}},
    queries=[
        S3SelectTestQuery(query=x["query"], expected=x["expected"], content=x.get("content"))
        for x in TESTS_CSV_3["params"]
    ],
).render()

TESTS_MINIO = (
    TESTS_MINIO_JSON
    + TESTS_MINIO_JSON_WITH_DATA
    + TESTS_MINIO_CSV
    + TESTS_MINIO_CSV_2
    + TESTS_MINIO_CSV_2_NOHEADER
    + TESTS_MINIO_CSV_3
)

CSV_CONTENT = """
Country,Country (Name),Population
US,United States,360000000
CH,Switzerland,9000000
DE,Germany,800000000
""".strip()

JSON_CONTENT = [
    {"Country": "US", "Country (Name)": "United States", "Population": 360000000},
    {"Country": "CH", "Country (Name)": "Switzerland", "Population": 9000000},
    {"Country": "DE", "Country (Name)": "Germany", "Population": 800000000},
]

TESTS_LEGACY_INTYPE = S3SelectTestGroup(
    expected=["US,United States,360000000", "DE,Germany,800000000"],
    output_serialization={"CSV": {}},
    queries=[
        S3SelectTestQuery(
            query="""SELECT * FROM s3object[*] as s WHERE s."Country (Name)" LIKE '%United States%' OR CAST(s.Population AS INTEGER) > 10000000""",
            content="\n".join([json.dumps(e) for e in JSON_CONTENT]),
            input_serialization={"JSON": {"Type": "LINES"}, "CompressionType": "NONE"},
        ),
        S3SelectTestQuery(
            query="""SELECT * FROM s3object[*][*] as s WHERE s."Country (Name)" LIKE '%United States%' OR CAST(s.Population AS INTEGER) > 10000000""",
            content=json.dumps(JSON_CONTENT),
            input_serialization={"JSON": {"Type": "DOCUMENT"}, "CompressionType": "NONE"},
        ),
        S3SelectTestQuery(
            query="""SELECT * FROM s3object s WHERE s."Country (Name)" LIKE '%United States%' OR CAST(s.Population AS INTEGER) > 10000000""",
            content=CSV_CONTENT,
            input_serialization={
                "CSV": {"FieldDelimiter": ",", "FileHeaderInfo": "USE"},
                "CompressionType": "NONE",
            },
        ),
    ],
).render()

# TODO: these were taken from the previous integration test but they are based on wrong assumptions.
#  Only the second (the not commented out) SELECT is correct
TESTS_LEGACY_QUERY_NESTING = S3SelectTestGroup(
    expected=["Bob Smith,value,4", "Jane Doe,other value,8"],
    content=json.dumps(
        [
            {"name": "Bob Smith", "key": "value", "somenumber": 4},
            {"name": "Jane Doe", "key": "other value", "somenumber": 8},
        ]
    ),
    input_serialization={"JSON": {"Type": "DOCUMENT"}, "CompressionType": "NONE"},
    output_serialization={"CSV": {}},
    queries=[
        # S3SelectTestQuery(query="""SELECT s.* FROM s3object[*] s"""),
        S3SelectTestQuery(query="""SELECT s.* FROM s3object[*][*] AS s"""),
        # S3SelectTestQuery(query="""SELECT s.* FROM s3object[*][*][*] s"""),
    ],
).render()

TESTS_LEGACY_JSONPATH = S3SelectTestGroup(
    expected=["1", "2"],
    content=json.dumps(
        [
            {"Rules": [{"id": "1"}, {"expr": "y > x"}, {"id": "2", "expr": "z = DEBUG"}]},
            {"created": "June 27", "modified": "July 6"},
        ]
    ),
    input_serialization={"JSON": {"Type": "DOCUMENT"}, "CompressionType": "NONE"},
    output_serialization={"CSV": {}},
    queries=[
        S3SelectTestQuery(query="""SELECT id FROM S3Object[*][*].Rules[*].id"""),
    ],
).render()

TESTS_LEGACY = TESTS_LEGACY_INTYPE + TESTS_LEGACY_QUERY_NESTING + TESTS_LEGACY_JSONPATH

ALL_TESTS = (
    TESTS_MINIO_JSON
    # TESTS_CUSTOM + TESTS_NUMBERS + TESTS_CUSTOMER + TESTS_AWS_DOCS + TESTS_MINIO + TESTS_LEGACY
)


class TestS3Select:
    # TODO: properly implement S3 SELECT and make these green :)
    @markers.aws.validated
    @pytest.mark.skip
    @pytest.mark.parametrize("params", ALL_TESTS, ids=[x.query for x in ALL_TESTS])
    def test_s3_select(
        self, s3_create_reusable_bucket, params: S3SelectTestParameterSet, aws_client
    ):
        bucket, prefix = s3_create_reusable_bucket()
        key = f"{prefix}/testdata-{short_uid()}"
        if params.file:
            aws_client.s3.upload_file(params.file, bucket, key)
        else:
            with tempfile.NamedTemporaryFile() as f:
                f.write(bytes(params.content, "utf-8"))
                f.flush()
                aws_client.s3.upload_file(f.name, Bucket=bucket, Key=key)

        def call_select():
            return aws_client.s3.select_object_content(
                Bucket=bucket,
                Key=key,
                ExpressionType="SQL",
                Expression=params.query,
                InputSerialization=params.input_serialization,
                OutputSerialization=params.output_serialization,
            )

        if params.error:
            with pytest.raises(Exception) as ctx:
                call_select()
            ctx.match(params.error)
        else:
            select_result = call_select()
            if params.output_serialization.get("JSON") is not None:
                records = extract_json_records_from_stream(select_result["Payload"])
            else:
                records = extract_csv_records_from_stream(select_result["Payload"])
            assert records == params.expected

    @markers.aws.validated
    def test_s3_select_wrong_expression_type(self, s3_bucket, snapshot, aws_client):
        key = f"test-s3-select-{short_uid()}"
        content = "\n".join([json.dumps(e) for e in JSON_CONTENT])
        query = """SELECT * FROM s3object[*] as s WHERE s."Country (Name)" LIKE '%United States%' OR CAST(s.Population AS INTEGER) > 10000000"""
        input_serialization = {"JSON": {"Type": "LINES"}, "CompressionType": "NONE"}

        with tempfile.NamedTemporaryFile() as f:
            f.write(bytes(content, "utf-8"))
            f.flush()
            aws_client.s3.upload_file(f.name, Bucket=s3_bucket, Key=key)

        with pytest.raises(ClientError) as e:
            aws_client.s3.select_object_content(
                Bucket=s3_bucket,
                Key=key,
                ExpressionType="SQL-WRONG",
                Expression=query,
                InputSerialization=input_serialization,
                OutputSerialization={"JSON": {}},
            )

        snapshot.match("error-select-expr-type", e.value.response)

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify
    def test_inconsistent_number_of_columns(self, s3_bucket, snapshot, aws_client):
        key = f"test-s3-select-{short_uid()}"
        # bad content - the first row contains two columns, the second row
        # contains three columns
        content = textwrap.dedent(
            """,
            10,20,30
            """
        ).encode("utf8")
        query = "SELECT * FROM s3object"
        input_serialization = {"CSV": {}, "CompressionType": "NONE"}
        aws_client.s3.put_object(Bucket=s3_bucket, Key=key, Body=content)

        query_res = aws_client.s3.select_object_content(
            Bucket=s3_bucket,
            Key=key,
            Expression=query,
            ExpressionType="SQL",
            InputSerialization=input_serialization,
            OutputSerialization={"CSV": {}},
        )

        # TODO: validate the result matches with snapshot testing
        # Currently the format has inconsistent whitespace and does not 100%
        # match, but the fact that this test passed means that the incorrect
        # input format is ignored as it is on AWS
        row_idx = 0
        for row in query_res["Payload"]:
            if "Records" not in row:
                continue

            raw_result_entry = row["Records"]["Payload"].decode("utf8")
            snapshot.match(f"raw-row-{row_idx}", raw_result_entry)
            row_idx += 1

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(
        condition=lambda: config.LEGACY_V2_S3_PROVIDER,
        paths=["$..ServerSideEncryption"],
    )
    @pytest.mark.parametrize("total_size", (1_000_000, 50_000_000))
    def test_big_file_query(self, s3_bucket, snapshot, aws_client, tmp_path, total_size):
        # we want to test with a file > 50MB, to test the proper streaming of the response
        # TODO: the performance is really bad for a 50mb file, so we skip it (> 30s execution)
        if total_size == 50_000_000 and not is_aws_cloud():
            pytest.skip("Skipping, implementation is too slow for tests, > 30s")

        file = tmp_path / "test.txt"
        object_key = "s3-select-test"
        # create a fake CSV
        row = b"a,b,c,d,e,f,g,h\n"
        chunk_multiplier = 62500
        chunk_size = len(row) * chunk_multiplier
        iterations = total_size // chunk_size
        with open(file, mode="w+b") as fp:
            chunk = row * chunk_multiplier
            for _ in range(iterations):
                fp.write(chunk)
            fp.seek(0)
            aws_client.s3.upload_fileobj(fp, s3_bucket, object_key)

        head_obj = aws_client.s3.head_object(Bucket=s3_bucket, Key=object_key)
        snapshot.match("head-obj", head_obj)
        assert head_obj["ContentLength"] == total_size

        query = "SELECT * FROM s3object"
        input_serialization = {"CSV": {}, "CompressionType": "NONE"}
        response = aws_client.s3.select_object_content(
            Bucket=s3_bucket,
            Key=object_key,
            Expression=query,
            ExpressionType="SQL",
            InputSerialization=input_serialization,
            OutputSerialization={"CSV": {}},
        )

        returned_size = 0
        for event in response["Payload"]:
            # If we received a `Records` event, save it to S3
            if "Records" in event:
                # after testing in AWS, it seems AWS almost always return 65000 bytes in the payload, no matter the
                # records number. AWS will cut a record in the middle if it's above the 65k mark.
                records = event["Records"]["Payload"]
                len_payload = len(records)
                assert len_payload <= 65000
                returned_size += len_payload

            # End event indicates that the request finished successfully
            elif "End" in event:
                break

        assert returned_size == total_size

    @markers.aws.validated
    def test_empty_file(self, s3_bucket, aws_client):
        key = f"test-s3-select-{short_uid()}"
        aws_client.s3.put_object(Bucket=s3_bucket, Key=key, Body="")

        query_res = aws_client.s3.select_object_content(
            Bucket=s3_bucket,
            Key=key,
            ExpressionType="SQL",
            Expression="select * from s3object",
            InputSerialization={
                "CSV": {"FileHeaderInfo": "USE", "RecordDelimiter": "\n", "FieldDelimiter": ","}
            },
            OutputSerialization={"CSV": {}},
        )

        for row in query_res["Payload"]:
            assert "Records" not in row

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(
        condition=lambda: config.LEGACY_V2_S3_PROVIDER,
        paths=["$..ServerSideEncryption"],
    )
    @pytest.mark.parametrize(
        "content_encoding,input_type",
        [
            ("gzip", "CSV"),
            ("gzip", "JSON"),
            (None, "CSV"),
            (None, "JSON"),
        ],
    )
    def test_query_on_gzip_object(
        self, s3_bucket, snapshot, aws_client, content_encoding, input_type
    ):
        object_key = "s3-select-test-gzip.gz"
        # create a fake CSV or JSON but gzipped
        if input_type == "CSV":
            data = CSV_CONTENT
            input_serialization = {"CSV": {}}
        else:
            data = "\n".join([json.dumps(e) for e in JSON_CONTENT])
            input_serialization = {"JSON": {"Type": "LINES"}}

        # Write contents to memory rather than a file.
        upload_file_object = BytesIO()
        # GZIP has the timestamp and filename in its headers, so set them to have same ETag and hash for AWS and LS
        # hardcode the timestamp, the filename will be an empty string because we're passing a BytesIO stream
        mtime = 1676569620
        with gzip.GzipFile(fileobj=upload_file_object, mode="w", mtime=mtime) as filestream:
            filestream.write(data.encode("utf-8"))

        kwargs = {"ContentEncoding": content_encoding} if content_encoding else {}

        response = aws_client.s3.put_object(
            Bucket=s3_bucket,
            Key=object_key,
            Body=upload_file_object.getvalue(),
            **kwargs,
        )
        snapshot.match("put-object", response)

        head_obj = aws_client.s3.head_object(Bucket=s3_bucket, Key=object_key)
        snapshot.match("head-obj", head_obj)

        query = "SELECT * FROM s3object"
        with pytest.raises(ClientError) as e:
            aws_client.s3.select_object_content(
                Bucket=s3_bucket,
                Key=object_key,
                Expression=query,
                ExpressionType="SQL",
                InputSerialization=input_serialization,
                OutputSerialization={"CSV": {}},
            )
        snapshot.match("no-compression-type-specified", e.value.response)

        response = aws_client.s3.select_object_content(
            Bucket=s3_bucket,
            Key=object_key,
            Expression=query,
            ExpressionType="SQL",
            InputSerialization={**input_serialization, "CompressionType": "GZIP"},
            OutputSerialization={"CSV": {}},
        )

        full_payload = b""
        for event in response["Payload"]:
            # If we received a `Records` event, save it to S3
            if "Records" in event:
                # after testing in AWS, it seems AWS almost always return 65000 bytes in the payload, no matter the
                # records number. AWS will cut a record in the middle if it's above the 65k mark.
                records = event["Records"]["Payload"]
                full_payload += records

            # End event indicates that the request finished successfully
            elif "End" in event:
                break

        result = csv.reader(StringIO(full_payload.decode("utf-8")))
        snapshot.match("query-result", {"result": list(result)})

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(
        condition=lambda: config.LEGACY_V2_S3_PROVIDER,
        paths=["$..ServerSideEncryption"],
    )
    def test_query_on_bzip2_object(self, s3_bucket, snapshot, aws_client):
        object_key = "s3-select-test-bzip2.bz2"
        # create a fake CSV but gzip
        data = CSV_CONTENT
        input_serialization = {"CSV": {}}

        # Write contents to memory rather than a file.
        upload_file_object = BytesIO()
        with bz2.BZ2File(upload_file_object, mode="w") as filestream:
            filestream.write(data.encode("utf-8"))

        response = aws_client.s3.put_object(
            Bucket=s3_bucket,
            Key=object_key,
            Body=upload_file_object.getvalue(),
        )
        snapshot.match("put-object", response)

        head_obj = aws_client.s3.head_object(Bucket=s3_bucket, Key=object_key)
        snapshot.match("head-obj", head_obj)

        query = "SELECT * FROM s3object"
        with pytest.raises(ClientError) as e:
            aws_client.s3.select_object_content(
                Bucket=s3_bucket,
                Key=object_key,
                Expression=query,
                ExpressionType="SQL",
                InputSerialization=input_serialization,
                OutputSerialization={"CSV": {}},
            )
        snapshot.match("no-compression-type-specified", e.value.response)

        with pytest.raises(ClientError) as e:
            aws_client.s3.select_object_content(
                Bucket=s3_bucket,
                Key=object_key,
                Expression=query,
                ExpressionType="SQL",
                InputSerialization={**input_serialization, "CompressionType": "RANDOM"},
                OutputSerialization={"CSV": {}},
            )
        snapshot.match("wrong-compression-type-specified", e.value.response)

        response = aws_client.s3.select_object_content(
            Bucket=s3_bucket,
            Key=object_key,
            Expression=query,
            ExpressionType="SQL",
            InputSerialization={**input_serialization, "CompressionType": "BZIP2"},
            OutputSerialization={"CSV": {}},
        )

        full_payload = b""
        for event in response["Payload"]:
            # If we received a `Records` event, save it to S3
            if "Records" in event:
                # after testing in AWS, it seems AWS almost always return 65000 bytes in the payload, no matter the
                # records number. AWS will cut a record in the middle if it's above the 65k mark.
                records = event["Records"]["Payload"]
                full_payload += records

            # End event indicates that the request finished successfully
            elif "End" in event:
                break

        result = csv.reader(StringIO(full_payload.decode("utf-8")))
        snapshot.match("query-result", {"result": list(result)})
