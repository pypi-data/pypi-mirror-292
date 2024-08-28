import json
from datetime import datetime
from typing import TYPE_CHECKING

from dateutil.tz import tzutc
from localstack.utils.strings import short_uid
from localstack.utils.sync import retry

if TYPE_CHECKING:
    from mypy_boto3_cloudwatch import CloudWatchClient


def wait_for_alarm_state(cloudwatch_client: "CloudWatchClient", alarm: str, expected_state: str):
    def check_alarm_state():
        response = cloudwatch_client.describe_alarms(AlarmNames=[alarm])
        assert response["MetricAlarms"][0]["StateValue"] == expected_state

    # evaluation will take a little time
    retry(check_alarm_state, sleep=2, retries=60)


def test_cloudwatch_describe_alarms(persistence_validations, snapshot, aws_client):
    namespace = "my/namespace"
    metric_name = "mymetric"
    dimensions = [{"Name": "foo", "Value": "bar"}]
    data = [
        {
            "MetricName": metric_name,
            "Dimensions": dimensions,
            "Timestamp": datetime(2022, 1, 3, tzinfo=tzutc()),
            "Unit": "Seconds",
            "Value": 123,
        },
        {
            "MetricName": metric_name,
            "Dimensions": dimensions,
            "Timestamp": datetime(2022, 1, 4, tzinfo=tzutc()),
            "Unit": "Seconds",
            "Value": 2,
        },
    ]
    alarm = f"my-alarm-{short_uid()}"

    aws_client.cloudwatch.put_metric_data(Namespace=namespace, MetricData=data)
    aws_client.cloudwatch.put_metric_alarm(
        AlarmName=alarm,
        MetricName=metric_name,
        Namespace=namespace,
        EvaluationPeriods=1,
        ComparisonOperator="GreaterThanThreshold",
        ActionsEnabled=True,
        Period=30,
        Threshold=2,
        Dimensions=dimensions,
        Statistic="Average",
        TreatMissingData="breaching",
    )

    def validate():
        metric_data_response = aws_client.cloudwatch.get_metric_data(
            MetricDataQueries=[
                {
                    "Id": "some",
                    "MetricStat": {
                        "Metric": {
                            "Namespace": namespace,
                            "MetricName": metric_name,
                            "Dimensions": dimensions,
                        },
                        "Period": 60,
                        "Stat": "Sum",
                    },
                },
            ],
            StartTime=datetime(2022, 1, 3, tzinfo=tzutc()),
            EndTime=datetime(2022, 1, 5, tzinfo=tzutc()),
        )
        snapshot.match("get-metric-data", metric_data_response)

        wait_for_alarm_state(aws_client.cloudwatch, alarm, "ALARM")
        snapshot.match("describe_alarms", aws_client.cloudwatch.describe_alarms(AlarmNames=[alarm]))

    persistence_validations.register(validate)


def test_dashboards_descriptions(persistence_validations, snapshot, aws_client):
    dashboard_name = f"test-{short_uid()}"
    dashboard_body = {
        "widgets": [
            {
                "type": "metric",
                "x": 0,
                "y": 0,
                "width": 6,
                "height": 6,
                "properties": {
                    "metrics": [["AWS/EC2", "CPUUtilization", "InstanceId", "i-12345678"]],
                    "region": "us-east-1",
                    "view": "timeSeries",
                    "stacked": False,
                },
            }
        ]
    }
    aws_client.cloudwatch.put_dashboard(
        DashboardName=dashboard_name, DashboardBody=json.dumps(dashboard_body)
    )

    def validate():
        response = aws_client.cloudwatch.get_dashboard(DashboardName=dashboard_name)
        snapshot.add_transformer(snapshot.transform.key_value("DashboardName"))
        snapshot.match("get_dashboard", response)

    persistence_validations.register(validate)
