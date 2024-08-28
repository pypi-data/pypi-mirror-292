import os

import pytest
from localstack.pro.core.aws.api.iotanalytics import ChannelStatus
from localstack.testing.pytest import markers
from localstack.utils.strings import short_uid


class TestIotAnalytics:
    @markers.aws.unknown
    def test_create_iotanalytics_resources(self, deploy_cfn_template, aws_client):
        # create and deploy CFN stack
        thing_name = f"t-{short_uid()}"
        mapping = {"thing_name": thing_name}
        stack = deploy_cfn_template(
            template_path=os.path.join(
                os.path.dirname(__file__), "../../templates/iotanalytics.sample.yml"
            ),
            template_mapping=mapping,
        )

        # check created resources
        resources = aws_client.cloudformation.describe_stack_resources(StackName=stack.stack_name)[
            "StackResources"
        ]
        types = set([r.get("ResourceType") for r in resources])
        assert len(types) == 4

    @markers.aws.unknown
    def test_channels(self, aws_client):
        channel_name = f"ch-{short_uid()}"

        # create channel
        result = aws_client.iotanalytics.create_channel(channelName=channel_name)
        assert result["ResponseMetadata"]["HTTPStatusCode"] == 201
        assert result["channelName"] == channel_name

        # list channel
        result = aws_client.iotanalytics.list_channels()
        assert result["ResponseMetadata"]["HTTPStatusCode"] == 200
        assert len(result["channelSummaries"]) == 1

        # describe channel
        result = aws_client.iotanalytics.describe_channel(channelName=channel_name)
        assert result["ResponseMetadata"]["HTTPStatusCode"] == 200
        assert result["channel"]["status"] == ChannelStatus.ACTIVE
        assert result["channel"]["name"] == channel_name

        # delete channel
        result = aws_client.iotanalytics.delete_channel(channelName=channel_name)
        assert result["ResponseMetadata"]["HTTPStatusCode"] == 204

        with pytest.raises(aws_client.iotanalytics.exceptions.ResourceNotFoundException):
            aws_client.iotanalytics.describe_channel(channelName=channel_name)

    @markers.aws.unknown
    def test_pipelines(self, aws_client):
        channel_name = f"ch-{short_uid()}"
        pipeline_name = f"p-{short_uid()}"

        # create pipeline
        pipeline_activity = {"channel": {"name": f"foo-{short_uid()}", "channelName": channel_name}}
        result = aws_client.iotanalytics.create_pipeline(
            pipelineName=pipeline_name, pipelineActivities=[pipeline_activity]
        )
        assert result["ResponseMetadata"]["HTTPStatusCode"] == 201
        assert result["pipelineName"] == pipeline_name

        # list pipeline
        result = aws_client.iotanalytics.list_pipelines()
        assert result["ResponseMetadata"]["HTTPStatusCode"] == 200
        assert len(result["pipelineSummaries"]) == 1

        # describe pipeline
        result = aws_client.iotanalytics.describe_pipeline(pipelineName=pipeline_name)
        assert result["ResponseMetadata"]["HTTPStatusCode"] == 200
        assert result["pipeline"]["name"] == pipeline_name

        # delete pipeline
        result = aws_client.iotanalytics.delete_pipeline(pipelineName=pipeline_name)
        assert result["ResponseMetadata"]["HTTPStatusCode"] == 204

        with pytest.raises(aws_client.iotanalytics.exceptions.ResourceNotFoundException):
            aws_client.iotanalytics.describe_pipeline(pipelineName=pipeline_name)

    @markers.aws.unknown
    def test_datastores(self, aws_client):
        datastore_name = f"ds-{short_uid()}"

        # create datastore
        result = aws_client.iotanalytics.create_datastore(datastoreName=datastore_name)
        assert result["ResponseMetadata"]["HTTPStatusCode"] == 201
        assert result["datastoreName"] == datastore_name

        # list datastore
        result = aws_client.iotanalytics.list_datastores()
        assert result["ResponseMetadata"]["HTTPStatusCode"] == 200
        assert len(result["datastoreSummaries"]) == 1

        # describe datastore
        result = aws_client.iotanalytics.describe_datastore(datastoreName=datastore_name)
        assert result["ResponseMetadata"]["HTTPStatusCode"] == 200
        assert result["datastore"]["name"] == datastore_name

        # delete datastore
        result = aws_client.iotanalytics.delete_datastore(datastoreName=datastore_name)
        assert result["ResponseMetadata"]["HTTPStatusCode"] == 204

        with pytest.raises(aws_client.iotanalytics.exceptions.ResourceNotFoundException):
            aws_client.iotanalytics.describe_datastore(datastoreName=datastore_name)

    @markers.aws.unknown
    def test_datasets(self, aws_client):
        action = {"actionName": "foo"}
        dataset_name = f"ds-{short_uid()}"

        # create dataset
        result = aws_client.iotanalytics.create_dataset(datasetName=dataset_name, actions=[action])
        assert result["ResponseMetadata"]["HTTPStatusCode"] == 201
        assert result["datasetName"] == dataset_name

        # list dataset
        result = aws_client.iotanalytics.list_datasets()
        assert result["ResponseMetadata"]["HTTPStatusCode"] == 200
        assert len(result["datasetSummaries"]) == 1

        # describe dataset
        result = aws_client.iotanalytics.describe_dataset(datasetName=dataset_name)
        assert result["ResponseMetadata"]["HTTPStatusCode"] == 200
        assert result["dataset"]["name"] == dataset_name

        # delete dataset
        result = aws_client.iotanalytics.delete_dataset(datasetName=dataset_name)
        assert result["ResponseMetadata"]["HTTPStatusCode"] == 204

        with pytest.raises(aws_client.iotanalytics.exceptions.ResourceNotFoundException):
            aws_client.iotanalytics.describe_dataset(datasetName=dataset_name)
