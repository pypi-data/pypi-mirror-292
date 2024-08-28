import logging

import pytest as pytest
from localstack.testing.config import TEST_AWS_ACCESS_KEY_ID
from localstack.testing.pytest import markers
from localstack.utils.aws import arns
from localstack.utils.aws.arns import kinesis_stream_arn
from localstack.utils.strings import short_uid
from localstack.utils.sync import retry

from tests.aws.services.kinesisanalytics.test_kinesisanalytics import KA_INPUTS, KA_OUTPUTS

LOG = logging.getLogger(__name__)


@pytest.fixture
def kinesisanalytics_v2_create_application(
    kinesis_create_stream, aws_client, account_id, region_name
):
    apps = list()
    threads = list()

    def factory(**kwargs):
        if "StreamNameIn" not in kwargs:
            kwargs["StreamNameIn"] = "analytics-in-%s" % short_uid()
        if "StreamNameOut" not in kwargs:
            kwargs["StreamNameOut"] = "analytics-out-%s" % short_uid()
        kinesis_create_stream(StreamName=kwargs["StreamNameIn"])
        kinesis_create_stream(StreamName=kwargs["StreamNameOut"])

        def process_results(records):
            results.extend(records)

        results = []
        from localstack.utils.kinesis import kinesis_connector

        kinesis_thread = kinesis_connector.listen_to_kinesis(
            stream_name=kwargs["StreamNameOut"],
            account_id=TEST_AWS_ACCESS_KEY_ID,
            region_name=region_name,
            listener_func=process_results,
            wait_until_started=False,
        )
        threads.append(kinesis_thread)
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
        outputs["KinesisStreamsOutput"] = {
            "ResourceARN": arns.kinesis_stream_arn(
                kwargs["StreamNameOut"],
                account_id,
                region_name,
            )
        }
        application_config = {
            "SqlApplicationConfiguration": {
                "Inputs": [inputs],
                "Outputs": [outputs],
            }
        }

        aws_client.kinesisanalyticsv2.create_application(
            ApplicationName=app_name,
            ApplicationDescription=app_description,
            RuntimeEnvironment=kwargs["RuntimeEnvironment"],
            ServiceExecutionRole="test_role",
            ApplicationConfiguration=application_config,
        )
        apps.append(app_name)

        def check_status():
            status = aws_client.kinesisanalyticsv2.describe_application(ApplicationName=app_name)[
                "ApplicationDetail"
            ]
            assert status["ApplicationStatus"] in ["READY", "RUNNING"]

        retry(check_status, sleep=2, retries=50)
        return app_name

    yield factory

    # cleanup
    for app in apps:
        try:
            app_detail = aws_client.kinesisanalyticsv2.describe_application(ApplicationName=app)[
                "ApplicationDetail"
            ]
            aws_client.kinesisanalyticsv2.delete_application(
                ApplicationName=app, CreateTimestamp=app_detail.get("CreateTimestamp")
            )
        except Exception as e:
            LOG.debug(f"error cleaning up application {app}: {e}")
    for thread in threads:
        try:
            thread.stop()
        except Exception as e:
            LOG.debug(f"error stopping thread {thread}: {e}")


# TODO: investigate and fix these tests (ideally aws-validated) and/or KCL startup
@pytest.mark.skip(reason="Unblock CI from KCL startup timeout error")
@pytest.mark.skip_store_check(reason="recursion limit exceeded")
class TestKinesisAnalyticsV2Provider:
    @markers.aws.unknown
    def test_list_and_update_applications(self, kinesisanalytics_v2_create_application, aws_client):
        stream_name_in = f"analytics-stream-in-{short_uid()}"
        stream_name_out = f"analytics-stream-out-{short_uid()}"
        app_name = f"app-{short_uid()}"

        app = kinesisanalytics_v2_create_application(
            RuntimeEnvironment="SQL-1_0",
            StreamNameIn=stream_name_in,
            StreamNameOut=stream_name_out,
            AppName=app_name,
        )
        list_result = aws_client.kinesisanalyticsv2.list_applications()["ApplicationSummaries"]
        list_result = [_app for _app in list_result if _app["ApplicationName"] == app]
        assert len(list_result) == 1
        assert list_result[0]["ApplicationName"] == app_name

        describe_result = aws_client.kinesisanalyticsv2.describe_application(ApplicationName=app)[
            "ApplicationDetail"
        ]
        input_id = describe_result["ApplicationConfigurationDescription"][
            "SqlApplicationConfigurationDescription"
        ]["InputDescriptions"][0]["InputId"]
        version_id = describe_result["ApplicationVersionId"]
        parallelism_update = 3
        input_update = {
            "InputId": input_id,
            "InputParallelismUpdate": {"CountUpdate": parallelism_update},
        }

        application_configuration_update = {
            "SqlApplicationConfigurationUpdate": {"InputUpdates": [input_update]}
        }
        aws_client.kinesisanalyticsv2.update_application(
            ApplicationName=app,
            ApplicationConfigurationUpdate=application_configuration_update,
            CurrentApplicationVersionId=version_id,
        )
        describe_result = aws_client.kinesisanalyticsv2.describe_application(ApplicationName=app)[
            "ApplicationDetail"
        ]
        assert describe_result["ApplicationVersionId"] == version_id + 1
        assert (
            describe_result["ApplicationConfigurationDescription"][
                "SqlApplicationConfigurationDescription"
            ]["InputDescriptions"][0]["InputParallelism"]["Count"]
            == parallelism_update
        )

    @markers.aws.unknown
    def test_tag_list_tag_untag_resource(self, kinesisanalytics_v2_create_application, aws_client):
        stream_name_in = f"analytics-stream-in-{short_uid()}"
        stream_name_out = f"analytics-stream-out-{short_uid()}"

        app = kinesisanalytics_v2_create_application(
            RuntimeEnvironment="SQL-1_0", StreamNameIn=stream_name_in, StreamNameOut=stream_name_out
        )
        describe_result = aws_client.kinesisanalyticsv2.describe_application(ApplicationName=app)[
            "ApplicationDetail"
        ]
        application_arn = describe_result["ApplicationARN"]
        list_result = aws_client.kinesisanalyticsv2.list_tags_for_resource(
            ResourceARN=application_arn
        )
        # TODO: check against AWS is this is correct
        assert list_result["Tags"] == []
        tags = [{"Key": "Key1", "Value": "Value1"}, {"Key": "Key2", "Value": "Value2"}]
        aws_client.kinesisanalyticsv2.tag_resource(ResourceARN=application_arn, Tags=tags)

        list_result = aws_client.kinesisanalyticsv2.list_tags_for_resource(
            ResourceARN=application_arn
        )
        assert list_result["Tags"] == tags

        tag_keys = [k["Key"] for k in tags]
        aws_client.kinesisanalyticsv2.untag_resource(ResourceARN=application_arn, TagKeys=tag_keys)
        list_result = aws_client.kinesisanalyticsv2.list_tags_for_resource(
            ResourceARN=application_arn
        )
        assert list_result["Tags"] == []

    @markers.aws.unknown
    def test_input_processing_configuration(
        self, kinesisanalytics_v2_create_application, aws_client
    ):
        stream_name_in = f"analytics-stream-in-{short_uid()}"
        stream_name_out = f"analytics-stream-out-{short_uid()}"

        app = kinesisanalytics_v2_create_application(
            RuntimeEnvironment="SQL-1_0", StreamNameIn=stream_name_in, StreamNameOut=stream_name_out
        )
        describe_result = aws_client.kinesisanalyticsv2.describe_application(ApplicationName=app)[
            "ApplicationDetail"
        ]
        version_id = describe_result["ApplicationVersionId"]
        input_id = describe_result["ApplicationConfigurationDescription"][
            "SqlApplicationConfigurationDescription"
        ]["InputDescriptions"][0]["InputId"]
        input_processing_configuration = {
            "InputLambdaProcessor": {
                "ResourceARN": "arn:mock",
            }
        }
        aws_client.kinesisanalyticsv2.add_application_input_processing_configuration(
            ApplicationName=app,
            CurrentApplicationVersionId=version_id,
            InputId=input_id,
            InputProcessingConfiguration=input_processing_configuration,
        )
        describe_result = aws_client.kinesisanalyticsv2.describe_application(ApplicationName=app)[
            "ApplicationDetail"
        ]
        assert (
            describe_result["ApplicationConfigurationDescription"][
                "SqlApplicationConfigurationDescription"
            ]["InputDescriptions"][0]["InputProcessingConfigurationDescription"][
                "InputLambdaProcessorDescription"
            ]["ResourceARN"]
            == input_processing_configuration["InputLambdaProcessor"]["ResourceARN"]
        )
        version_id = version_id + 1
        assert describe_result["ApplicationVersionId"] == version_id
        aws_client.kinesisanalyticsv2.delete_application_input_processing_configuration(
            ApplicationName=app, CurrentApplicationVersionId=version_id, InputId=input_id
        )

        describe_result = aws_client.kinesisanalyticsv2.describe_application(ApplicationName=app)[
            "ApplicationDetail"
        ]
        version_id = version_id + 1
        assert describe_result["ApplicationVersionId"] == version_id
        assert (
            "InputProcessingConfigurationDescription"
            not in describe_result["ApplicationConfigurationDescription"][
                "SqlApplicationConfigurationDescription"
            ]["InputDescriptions"][0]
        )

    @markers.aws.unknown
    def test_application_output(
        self,
        kinesisanalytics_v2_create_application,
        kinesis_create_stream,
        aws_client,
        account_id,
        region_name,
    ):
        stream_name_in = f"analytics-stream-in-{short_uid()}"
        stream_name_out = f"analytics-stream-out-{short_uid()}"

        app = kinesisanalytics_v2_create_application(
            RuntimeEnvironment="SQL-1_0", StreamNameIn=stream_name_in, StreamNameOut=stream_name_out
        )
        describe_result = aws_client.kinesisanalyticsv2.describe_application(ApplicationName=app)[
            "ApplicationDetail"
        ]
        version_id = describe_result["ApplicationVersionId"]
        application_stream_name = "stream-TODO-0"
        new_stream = kinesis_create_stream()
        stream_arn = kinesis_stream_arn(
            new_stream,
            account_id,
            region_name,
        )
        output = {
            "Name": application_stream_name,
            "KinesisStreamsOutput": {"ResourceARN": stream_arn},
            "DestinationSchema": {"RecordFormatType": "JSON"},
        }
        aws_client.kinesisanalyticsv2.add_application_output(
            ApplicationName=app, CurrentApplicationVersionId=version_id, Output=output
        )
        describe_result = aws_client.kinesisanalyticsv2.describe_application(ApplicationName=app)[
            "ApplicationDetail"
        ]
        # TODO: check if original outstream not showing here is correct behaviour
        assert (
            describe_result["ApplicationConfigurationDescription"][
                "SqlApplicationConfigurationDescription"
            ]["OutputDescriptions"][0]["KinesisStreamsOutputDescription"]
            == output["KinesisStreamsOutput"]
        )
        version_id = version_id + 1
        assert describe_result["ApplicationVersionId"] == version_id
        # TODO: check if the new outstream is functional == receives test inputs
        # TODO: delete_output
