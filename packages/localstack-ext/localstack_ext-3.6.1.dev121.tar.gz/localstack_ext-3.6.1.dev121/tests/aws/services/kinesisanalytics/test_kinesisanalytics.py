import json
import logging
import threading
import time

import pytest as pytest
from localstack.pro.core.services.kinesisanalytics.packages import siddhi_package
from localstack.pro.core.services.kinesisanalytics.query_utils import run_siddhi_query
from localstack.testing.aws.util import is_aws_cloud
from localstack.testing.config import TEST_AWS_ACCESS_KEY_ID
from localstack.testing.pytest import markers
from localstack.utils.aws import arns
from localstack.utils.aws.arns import kinesis_stream_arn
from localstack.utils.kinesis import kinesis_connector
from localstack.utils.strings import short_uid, to_bytes
from localstack.utils.sync import retry
from localstack.utils.threads import start_worker_thread

LOG = logging.getLogger(__name__)

INIT_LOCK = threading.RLock()

# test query
KA_INPUTS = {
    "NamePrefix": "IN_STREAM",
    "KinesisStreamsInput": {
        "ResourceARN": "TO_REPLACE",
    },
    "InputParallelism": {"Count": 1},
    "InputSchema": {
        "RecordFormat": {
            "RecordFormatType": "JSON",
            "MappingParameters": {"JSONMappingParameters": {"RecordRowPath": "$"}},
        },
        "RecordColumns": [
            {"Name": "SYMBOL", "SqlType": "VARCHAR(20)", "Mapping": "$.SYMBOL"},
            {"Name": "PRICE", "SqlType": "DOUBLE", "Mapping": "$.PRICE"},
            {"Name": "VOLUME", "SqlType": "INTEGER", "Mapping": "$.VOLUME"},
        ],
    },
}
KA_OUTPUTS = {
    "Name": "OUT_STREAM",
    "KinesisStreamsOutput": {
        "ResourceARN": "TO_REPLACE",
    },
    "DestinationSchema": {"RecordFormatType": "JSON"},
}

# input test events
TEST_INPUTS = [
    ["IBM", 700.0, 100],
    ["WSO2", 60.5, 200],
    ["GOOG", 50, 30],
    ["IBM", 76.6, 400],
    ["WSO2", 45.6, 50],
]
# test query
TEST_QUERY = """
CREATE OR REPLACE STREAM "OUT_STREAM"
  (SYMBOL VARCHAR(20), PRICE REAL, VOLUME INT);
CREATE OR REPLACE PUMP "STREAM_PUMP" AS INSERT INTO "OUT_STREAM"
SELECT STREAM SYMBOL, PRICE, VOLUME
FROM "IN_STREAM_001"
WHERE VOLUME < 150;
"""


@pytest.fixture
def kinesisanalytics_create_application(
    kinesis_create_stream, aws_client, account_id, region_name, create_iam_role_kinesis_access
):
    apps = list()
    threads = list()

    def factory(**kwargs):
        if "StreamNameIn" not in kwargs:
            kwargs["StreamNameIn"] = "analytics-in-%s" % short_uid()
        if "StreamNameOut" not in kwargs:
            kwargs["StreamNameOut"] = "analytics-out-%s" % short_uid()

        # create the role first, it doesn't seem to be ready to use right away with create_application in AWS
        role_arn = create_iam_role_kinesis_access()

        kinesis_create_stream(StreamName=kwargs["StreamNameIn"], ShardCount=1)
        kinesis_create_stream(StreamName=kwargs["StreamNameOut"], ShardCount=1)

        def process_results(records):
            results.extend(records)

        results = []
        from localstack.utils.kinesis import kinesis_connector

        kinesis_thrd = kinesis_connector.listen_to_kinesis(
            stream_name=kwargs["StreamNameOut"],
            account_id=TEST_AWS_ACCESS_KEY_ID,
            region_name=region_name,
            listener_func=process_results,
            wait_until_started=False,
        )
        threads.append(kinesis_thrd)
        if "AppName" not in kwargs:
            kwargs["AppName"] = "app-%s" % short_uid()
        app_name = kwargs["AppName"]
        app_description = "test analytics app"
        inputs = dict(KA_INPUTS)
        outputs = dict(KA_OUTPUTS)
        inputs["KinesisStreamsInput"] = {
            "ResourceARN": arns.kinesis_stream_arn(
                kwargs["StreamNameIn"],
                account_id,
                region_name,
            )
        }
        inputs["KinesisStreamsInput"].update({"RoleARN": role_arn})

        outputs["KinesisStreamsOutput"] = {
            "ResourceARN": arns.kinesis_stream_arn(
                kwargs["StreamNameOut"],
                account_id,
                region_name,
            )
        }
        outputs["KinesisStreamsOutput"].update({"RoleARN": role_arn})

        retry(
            aws_client.kinesisanalytics.create_application,
            retries=5,
            sleep=2,
            ApplicationName=app_name,
            ApplicationDescription=app_description,
            Inputs=[inputs],
            Outputs=[outputs],
            ApplicationCode=TEST_QUERY,
        )
        apps.append(app_name)

        def check_status():
            status = aws_client.kinesisanalytics.describe_application(ApplicationName=app_name)[
                "ApplicationDetail"
            ]
            assert status["ApplicationStatus"] in ["READY", "RUNNING"]

        retry(check_status, sleep=2, retries=60)
        return app_name

    yield factory

    # cleanup
    for app in apps:
        try:
            app_detail = aws_client.kinesisanalytics.describe_application(ApplicationName=app)[
                "ApplicationDetail"
            ]
            aws_client.kinesisanalytics.delete_application(
                ApplicationName=app, CreateTimestamp=app_detail.get("CreateTimestamp")
            )
        except Exception as e:
            LOG.debug(f"error cleaning up application {app}: {e}")
    for thread in threads:
        try:
            thread.stop()
        except Exception as e:
            LOG.debug(f"error stopping thread {thread}: {e}")


@pytest.fixture(scope="class")
def wait_for_init_done():
    # acquire lock to ensure initialization is completed
    with INIT_LOCK:
        pass


@markers.only_on_amd64
@pytest.mark.usefixtures("wait_for_init_done")
@pytest.mark.skip_store_check(reason="recursion limit exceeded")
class TestKinesisAnalytics:
    @classmethod
    def init_async(cls):
        def _run(*args):
            with INIT_LOCK:
                siddhi_package.install()

        start_worker_thread(_run)

    @pytest.mark.skip(reason="flaky after upgrading amazon_kclpy (#6502)")
    @markers.aws.unknown
    def test_run_query(
        self,
        wait_for_stream_ready,
        kinesis_create_stream,
        aws_client,
        account_id,
        region_name,
        cleanups,
    ):
        # create Kinesis stream
        stream_name_in = f"analytics-in-{short_uid()}"
        stream_name_out = f"analytics-out-{short_uid()}"
        kinesis_create_stream(StreamName=stream_name_in, ShardCount=1)
        kinesis_create_stream(StreamName=stream_name_out, ShardCount=1)
        wait_for_stream_ready(stream_name_in)
        wait_for_stream_ready(stream_name_out)

        # create application
        app_name = f"app-{short_uid()}"
        aws_client.kinesisanalytics.create_application(
            ApplicationName=app_name,
            ApplicationDescription="test analytics app",
            Inputs=[
                {
                    "NamePrefix": "input1",
                    "KinesisStreamsInput": {
                        "ResourceARN": arns.kinesis_stream_arn(
                            stream_name_in,
                            account_id,
                            region_name,
                        ),
                        "RoleARN": "role1",
                    },
                    "InputParallelism": {"Count": 2},
                    "InputSchema": {
                        "RecordFormat": {"RecordFormatType": "JSON"},
                        "RecordColumns": [
                            {"Name": "symbol", "SqlType": "VARCHAR(20)"},
                            {"Name": "price", "SqlType": "FLOAT"},
                            {"Name": "volume", "SqlType": "LONG"},
                        ],
                    },
                }
            ],
            Outputs=[
                {
                    "Name": "OutStream",
                    "KinesisStreamsOutput": {
                        "ResourceARN": arns.kinesis_stream_arn(
                            stream_name_out,
                            account_id,
                            region_name,
                        ),
                        "RoleARN": "r2",
                    },
                    "DestinationSchema": {"RecordFormatType": "JSON"},
                }
            ],
            ApplicationCode=TEST_QUERY,
        )
        cleanups.append(
            lambda: aws_client.kinesisanalytics.delete_application(
                ApplicationName=app_name, CreateTimestamp=app_details["CreateTimestamp"]
            )
        )

        # start result listener

        def process_results(records):
            results.extend(records)

        results = []
        thread = kinesis_connector.listen_to_kinesis(
            stream_name=stream_name_out,
            account_id=TEST_AWS_ACCESS_KEY_ID,
            region_name=region_name,
            listener_func=process_results,
            wait_until_started=True,
        )
        cleanups.append(lambda: thread.stop())

        # wait for application to be ready

        def _await_ready_status():
            status = aws_client.kinesisanalytics.describe_application(ApplicationName=app_name)[
                "ApplicationDetail"
            ]
            assert status["ApplicationStatus"] in ["READY", "RUNNING"]
            return status

        app_details = retry(_await_ready_status, sleep=2, retries=15)

        # send test events to stream

        for event in TEST_INPUTS:
            message = {"symbol": event[0], "price": event[1], "volume": event[2]}
            aws_client.kinesis.put_record(
                StreamName=stream_name_in, Data=to_bytes(json.dumps(message)), PartitionKey=event[0]
            )
            time.sleep(0.1)

        def _check_received():
            assert len(results) == 3

        # assert that results have been received
        retry(_check_received, sleep=3, retries=10)

    @markers.aws.unknown
    @pytest.mark.skip(reason="The current query transformation cannot handle valid AWS requests")
    def test_run_siddhi_query(self):
        # FIXME: Right now the query engine we use cannot handle the present query that works on AWS.
        #   Without this, we cannot properly run kinesis data analytics apps. Once it is fixed
        #   we can test if it also works end-to-end (input stream -> app -> output stream)
        def handler(events, *args, **kwargs):
            results.extend(events)

        # start engine
        results = []
        input_streams = {"IN_STREAM_001": {}}
        query_manager = run_siddhi_query(
            TEST_QUERY, input_streams=input_streams, result_handler=handler
        )

        # feed inputs
        for entry in TEST_INPUTS:
            input_streams["IN_STREAM_001"]["input_handler"]([entry])

        def _received():
            assert len(results) == 3

        # wait for results, then shut down
        retry(_received, sleep=3, retries=10)
        query_manager.shutdown()


@markers.only_on_amd64
@pytest.mark.skip_store_check(reason="recursion limit exceeded")
class TestKinesisAnalyticsProvider:
    @markers.aws.unknown
    def test_list_and_update_applications(self, kinesisanalytics_create_application, aws_client):
        stream_name_in = f"analytics-stream-in-{short_uid()}"
        stream_name_out = f"analytics-stream-out-{short_uid()}"

        app = kinesisanalytics_create_application(
            StreamNameIn=stream_name_in, StreamNameOut=stream_name_out
        )
        list_result = aws_client.kinesisanalytics.list_applications()["ApplicationSummaries"]
        list_result = [_app for _app in list_result if _app["ApplicationName"] == app]
        assert len(list_result) == 1

        describe_result = aws_client.kinesisanalytics.describe_application(ApplicationName=app)[
            "ApplicationDetail"
        ]
        input_id = describe_result["InputDescriptions"][0]["InputId"]
        version_id = describe_result["ApplicationVersionId"]
        parallelism_update = 3
        app_code_update = """
        CREATE OR REPLACE STREAM input1_001 (
            symbol VARCHAR(20), price float, volume LONG)
        DESCRIPTION 'updated code';
        SELECT STREAM * FROM input1_001 WHERE volume < 150;
        """
        input_update = {
            "InputId": input_id,
            "InputParallelismUpdate": {"CountUpdate": parallelism_update},
        }

        application_update = {
            "ApplicationCodeUpdate": app_code_update,
            "InputUpdates": [input_update],
        }
        aws_client.kinesisanalytics.update_application(
            ApplicationName=app,
            ApplicationUpdate=application_update,
            CurrentApplicationVersionId=version_id,
        )
        describe_result = aws_client.kinesisanalytics.describe_application(ApplicationName=app)[
            "ApplicationDetail"
        ]
        assert describe_result["ApplicationVersionId"] == version_id + 1
        assert (
            describe_result["InputDescriptions"][0]["InputParallelism"]["Count"]
            == parallelism_update
        )
        assert describe_result["ApplicationCode"] == app_code_update

    @markers.aws.unknown
    def test_tag_list_tag_untag_resource(self, kinesisanalytics_create_application, aws_client):
        app = kinesisanalytics_create_application()
        describe_result = aws_client.kinesisanalytics.describe_application(ApplicationName=app)[
            "ApplicationDetail"
        ]
        application_arn = describe_result["ApplicationARN"]
        list_result = aws_client.kinesisanalytics.list_tags_for_resource(
            ResourceARN=application_arn
        )
        # TODO: check against AWS is this is correct
        assert list_result["Tags"] == []
        tags = [{"Key": "Key1", "Value": "Value1"}, {"Key": "Key2", "Value": "Value2"}]
        aws_client.kinesisanalytics.tag_resource(ResourceARN=application_arn, Tags=tags)

        list_result = aws_client.kinesisanalytics.list_tags_for_resource(
            ResourceARN=application_arn
        )
        assert list_result["Tags"] == tags

        tag_keys = [k["Key"] for k in tags]
        aws_client.kinesisanalytics.untag_resource(ResourceARN=application_arn, TagKeys=tag_keys)
        list_result = aws_client.kinesisanalytics.list_tags_for_resource(
            ResourceARN=application_arn
        )
        assert list_result["Tags"] == []

    @markers.aws.unknown
    def test_input_processing_configuration(self, kinesisanalytics_create_application, aws_client):
        app = kinesisanalytics_create_application()
        describe_result = aws_client.kinesisanalytics.describe_application(ApplicationName=app)[
            "ApplicationDetail"
        ]
        version_id = describe_result["ApplicationVersionId"]
        input_id = describe_result["InputDescriptions"][0]["InputId"]
        input_processing_configuration = {
            "InputLambdaProcessor": {
                "ResourceARN": "arn:mock",
                "RoleARN": "arn:role1",
            }
        }
        aws_client.kinesisanalytics.add_application_input_processing_configuration(
            ApplicationName=app,
            CurrentApplicationVersionId=version_id,
            InputId=input_id,
            InputProcessingConfiguration=input_processing_configuration,
        )
        describe_result = aws_client.kinesisanalytics.describe_application(ApplicationName=app)[
            "ApplicationDetail"
        ]
        assert (
            describe_result["InputDescriptions"][0]["InputProcessingConfigurationDescription"][
                "InputLambdaProcessorDescription"
            ]["ResourceARN"]
            == input_processing_configuration["InputLambdaProcessor"]["ResourceARN"]
        )
        assert (
            describe_result["InputDescriptions"][0]["InputProcessingConfigurationDescription"][
                "InputLambdaProcessorDescription"
            ]["RoleARN"]
            == input_processing_configuration["InputLambdaProcessor"]["RoleARN"]
        )
        version_id = version_id + 1
        assert describe_result["ApplicationVersionId"] == version_id
        aws_client.kinesisanalytics.delete_application_input_processing_configuration(
            ApplicationName=app, CurrentApplicationVersionId=version_id, InputId=input_id
        )

        describe_result = aws_client.kinesisanalytics.describe_application(ApplicationName=app)[
            "ApplicationDetail"
        ]
        version_id = version_id + 1
        assert describe_result["ApplicationVersionId"] == version_id
        assert (
            "InputProcessingConfigurationDescription" not in describe_result["InputDescriptions"][0]
        )

    @pytest.mark.skipif(
        condition=not is_aws_cloud(),
        reason="current implementation does not work sufficiently on LS",
    )
    @markers.aws.validated
    def test_application_output(
        self,
        kinesisanalytics_create_application,
        kinesis_create_stream,
        wait_for_stream_ready,
        aws_client,
        account_id,
        region_name,
    ):
        # TODO: This test works against AWS and can therefore act as baseline for our implementation and what it should
        #   be able to do. The syntax of AWS is pretty different from the engine we use in the background ->
        #   our current implementation is not really functional. This depends on test_run_siddhi_query working.
        stream_name_in = f"input-stream-{short_uid()}"
        stream_name_out = f"output-stream-{short_uid()}"
        app = kinesisanalytics_create_application(
            StreamNameIn=stream_name_in, StreamNameOut=stream_name_out
        )
        describe_app_result = aws_client.kinesisanalytics.describe_application(ApplicationName=app)[
            "ApplicationDetail"
        ]
        version_id = describe_app_result["ApplicationVersionId"]
        role_arn = describe_app_result["InputDescriptions"][0]["KinesisStreamsInputDescription"][
            "RoleARN"
        ]

        # create a new stream and add it to the application
        new_output_stream_name = f"new-output-stream-{short_uid()}"
        new_output_stream = kinesis_create_stream(StreamName=new_output_stream_name, ShardCount=1)
        new_stream_arn = kinesis_stream_arn(new_output_stream, account_id, region_name)
        new_output = {
            "Name": "KinesisOutputStream",
            "KinesisStreamsOutput": {
                "ResourceARN": new_stream_arn,
                "RoleARN": role_arn,
            },
            "DestinationSchema": {"RecordFormatType": "JSON"},
        }
        aws_client.kinesisanalytics.add_application_output(
            ApplicationName=app, CurrentApplicationVersionId=version_id, Output=new_output
        )
        describe_result = aws_client.kinesisanalytics.describe_application(ApplicationName=app)[
            "ApplicationDetail"
        ]
        assert len(describe_result["OutputDescriptions"]) == 2
        assert (
            describe_result["OutputDescriptions"][1]["KinesisStreamsOutputDescription"]
            == new_output["KinesisStreamsOutput"]
        )
        version_id = version_id + 1
        assert describe_result["ApplicationVersionId"] == version_id

        input_configuration = {
            "Id": describe_app_result["InputDescriptions"][0]["InputId"],
            "InputStartingPositionConfiguration": {"InputStartingPosition": "TRIM_HORIZON"},
        }
        aws_client.kinesisanalytics.start_application(
            ApplicationName=app, InputConfigurations=[input_configuration]
        )
        wait_for_stream_ready(stream_name=new_output_stream_name)

        retries = 240 if is_aws_cloud() else 15

        def check_status():
            status = aws_client.kinesisanalytics.describe_application(ApplicationName=app)[
                "ApplicationDetail"
            ]
            assert status["ApplicationStatus"] in ["RUNNING"]

        retry(check_status, sleep=2, retries=retries)

        for event in TEST_INPUTS:
            message = {"SYMBOL": event[0], "PRICE": event[1], "VOLUME": event[2]}
            aws_client.kinesis.put_record(
                StreamName=stream_name_in, Data=to_bytes(json.dumps(message)), PartitionKey=event[0]
            )
            time.sleep(0.1)

        outputs_1 = []
        outputs_2 = []
        describe_out_stream_1 = aws_client.kinesis.describe_stream(StreamName=stream_name_out)
        describe_out_stream_2 = aws_client.kinesis.describe_stream(
            StreamName=new_output_stream_name
        )
        iterator_1 = aws_client.kinesis.get_shard_iterator(
            StreamName=stream_name_out,
            ShardId=describe_out_stream_1["StreamDescription"]["Shards"][0]["ShardId"],
            ShardIteratorType="TRIM_HORIZON",
        )["ShardIterator"]
        iterator_2 = aws_client.kinesis.get_shard_iterator(
            StreamName=new_output_stream_name,
            ShardId=describe_out_stream_2["StreamDescription"]["Shards"][0]["ShardId"],
            ShardIteratorType="TRIM_HORIZON",
        )["ShardIterator"]

        def get_records():
            outputs_1.extend(aws_client.kinesis.get_records(ShardIterator=iterator_1)["Records"])
            outputs_2.extend(aws_client.kinesis.get_records(ShardIterator=iterator_2)["Records"])
            assert len(outputs_1) == 3
            assert len(outputs_2) == 0

        retry(get_records)
