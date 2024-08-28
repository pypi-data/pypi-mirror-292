import requests
from localstack import config
from localstack.testing.pytest import markers
from localstack.utils.strings import short_uid
from localstack.utils.sync import retry


class TestCloudwatchReset:
    def _reset(self):
        requests.post(f"{config.internal_service_url()}/_localstack/state/cloudwatch/reset")

    @markers.aws.only_localstack
    def test_metrics_after_reset(self, aws_client):
        namespace = f"n-{short_uid()}"
        metric = f"m-{short_uid()}"
        aws_client.cloudwatch.put_metric_data(
            Namespace=namespace, MetricData=[{"MetricName": metric, "Value": 1, "Unit": "Count"}]
        )

        metrics = aws_client.cloudwatch.list_metrics(Namespace=namespace)
        assert len(metrics["Metrics"])

        self._reset()

        def validate_empty():
            metrics = aws_client.cloudwatch.list_metrics(Namespace=namespace)
            assert len(metrics["Metrics"]) == 0

        retry(validate_empty, sleep=1, retries=3)
