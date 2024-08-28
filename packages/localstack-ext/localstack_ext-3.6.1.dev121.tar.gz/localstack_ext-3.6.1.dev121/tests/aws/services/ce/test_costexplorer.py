import pytest
from localstack.testing.pytest import markers
from localstack.utils.strings import short_uid


class TestCostExplorer:
    @markers.aws.unknown
    def test_cost_categories(self, aws_client):
        client = aws_client.ce

        # create cost category
        def_name = "d-%s" % short_uid()
        rule_ver = "CostCategoryExpression.v1"
        rules = [{"Value": "test", "Rule": {}, "Type": "REGULAR"}]
        result = client.create_cost_category_definition(
            Name=def_name, RuleVersion=rule_ver, Rules=rules
        )
        cat_arn = result["CostCategoryArn"]

        # list cost categories
        result = client.list_cost_category_definitions()["CostCategoryReferences"]
        matching = any(cat["CostCategoryArn"] == cat_arn for cat in result)
        assert matching

        # describe cost category
        result = client.describe_cost_category_definition(CostCategoryArn=cat_arn)
        assert result["CostCategory"]["CostCategoryArn"] == cat_arn

        # update cost category
        rules = [{"Value": "test2", "Rule": {}}]
        result = client.update_cost_category_definition(
            CostCategoryArn=cat_arn, RuleVersion=rule_ver, Rules=rules
        )
        assert result["CostCategoryArn"] == cat_arn

        # delete cost category
        result = client.delete_cost_category_definition(CostCategoryArn=cat_arn)
        assert result["CostCategoryArn"] == cat_arn
        with pytest.raises(Exception):
            client.describe_cost_category_definition(CostCategoryArn=cat_arn)

    @markers.aws.unknown
    def test_anomaly_subscriptions(self, aws_client):
        client = aws_client.ce

        # create anomaly subscription
        subscr = {
            "AccountId": "12345",
            "SubscriptionName": "sub1",
            "Frequency": "DAILY",
            "MonitorArnList": [],
            "Subscribers": [],
            "Threshold": 111,
        }
        result = client.create_anomaly_subscription(AnomalySubscription=subscr)
        sub_arn = result["SubscriptionArn"]

        # describe anomaly subscription
        result = client.get_anomaly_subscriptions()["AnomalySubscriptions"]
        matching = [sub for sub in result if sub["SubscriptionArn"] == sub_arn]
        assert matching

        # update anomaly subscription
        result = client.update_anomaly_subscription(
            SubscriptionArn=sub_arn, Frequency="WEEKLY", Threshold=999
        )
        assert result["SubscriptionArn"] == sub_arn

        # delete anomaly subscription
        client.delete_anomaly_subscription(SubscriptionArn=sub_arn)
        result = client.get_anomaly_subscriptions()["AnomalySubscriptions"]
        matching = [sub for sub in result if sub["SubscriptionArn"] == sub_arn]
        assert not matching

    @markers.aws.unknown
    def test_anomaly_monitors(self, aws_client):
        client = aws_client.ce

        # create anomaly monitor
        monitor = {"MonitorName": "mon5463", "MonitorType": "DIMENSIONAL"}
        result = client.create_anomaly_monitor(AnomalyMonitor=monitor)
        monitor_arn = result["MonitorArn"]

        # describe anomaly monitor
        result = client.get_anomaly_monitors()["AnomalyMonitors"]
        matching = [sub for sub in result if sub["MonitorArn"] == monitor_arn]
        assert matching

        # update anomaly monitor
        result = client.update_anomaly_monitor(MonitorArn=monitor_arn, MonitorName="mon5463-new")
        assert result["MonitorArn"] == monitor_arn

        # delete anomaly monitor
        client.delete_anomaly_monitor(MonitorArn=monitor_arn)
        result = client.get_anomaly_monitors()["AnomalyMonitors"]
        matching = [sub for sub in result if sub["MonitorArn"] == monitor_arn]
        assert not matching
