import pytest
from localstack.pro.core import config as config_ext
from localstack.pro.core.services.cloudfront.provider import get_sample_distribution_config
from localstack.testing.pytest import markers
from localstack.utils.aws import arns
from localstack.utils.bootstrap import in_ci
from localstack.utils.net import retry, wait_for_port_closed, wait_for_port_open
from localstack.utils.testutil import short_uid

pytestmark = [
    markers.aws.only_localstack,
]


def test_amplify(aws_client, cleanups, amplify_create_app, assert_host_customisation):
    response = amplify_create_app()
    assert_host_customisation(response["defaultDomain"])

    branch_name = f"branch-{short_uid()}"
    create_result = aws_client.amplify.create_webhook(
        appId=response["appId"], branchName=branch_name
    )["webhook"]
    cleanups.append(lambda: aws_client.amplify.delete_webhook(webhookId=create_result["webhookId"]))

    assert_host_customisation(create_result["webhookUrl"])


def test_apigateway_v2(aws_client, cleanups, assert_host_customisation):
    name = f"api-{short_uid()}"
    res = aws_client.apigatewayv2.create_api(
        Name=name,
        ProtocolType="HTTP",
    )
    api_id = res["ApiId"]
    cleanups.append(
        lambda: aws_client.apigatewayv2.delete_api(
            ApiId=api_id,
        )
    )

    assert_host_customisation(res["ApiEndpoint"])


class TestAppsync:
    def test_default_strategy(self, aws_client, appsync_create_api, assert_host_customisation):
        res = appsync_create_api()

        assert_host_customisation(res["uris"]["GRAPHQL"])

    def test_domain_strategy(
        self, aws_client, appsync_create_api, assert_host_customisation, monkeypatch
    ):
        monkeypatch.setattr(config_ext, "GRAPHQL_ENDPOINT_STRATEGY", "domain")
        res = appsync_create_api()

        assert_host_customisation(res["uris"]["GRAPHQL"])


def test_cloudfront(aws_client, s3_bucket, cleanups, assert_host_customisation, monkeypatch):
    # cloudfront uses the config_ext variable: `RESOURCES_BASE_DOMAIN`, which also needs to be
    # patched in this test, since it is set from the original import, and not overridden by the
    # monkeypatching of `assert_host_customisation`.
    monkeypatch.setattr(config_ext, "RESOURCES_BASE_DOMAIN_NAME", "foo.bar")

    aws_client.s3.put_object(Bucket=s3_bucket, Key="foo", Body=b"bar")
    distribution = aws_client.cloudfront.create_distribution(
        DistributionConfig=get_sample_distribution_config(domain=f"{s3_bucket}.s3.amazonaws.com"),
    )["Distribution"]
    cleanups.append(lambda: aws_client.cloudfront.delete_distribution(Id=distribution["Id"]))

    assert_host_customisation(distribution["DomainName"])


def test_ecr(create_repository, assert_host_customisation):
    repo_name = f"repo-{short_uid()}"
    result = create_repository(repositoryName=repo_name)["repository"]

    assert_host_customisation(result["repositoryUri"])


def test_elasticache(aws_client, assert_host_customisation, cleanups):
    cluster_name = f"c-{short_uid()}"
    result = aws_client.elasticache.create_cache_cluster(
        CacheClusterId=cluster_name,
        Engine="redis",
        CacheNodeType="cache.t3.small",
    )["CacheCluster"]

    cluster_port = result["ConfigurationEndpoint"]["Port"]

    def _delete_cluster():
        aws_client.elasticache.delete_cache_cluster(CacheClusterId=cluster_name)
        wait_for_port_closed(cluster_port)

    cleanups.append(_delete_cluster)

    wait_for_port_open(cluster_port)

    assert_host_customisation(result["ConfigurationEndpoint"]["Address"])


def test_iot(aws_client, assert_host_customisation):
    res = aws_client.iot.describe_endpoint()

    assert_host_customisation(res["endpointAddress"])


def test_kafka(msk_create_cluster_v2, aws_client, assert_host_customisation):
    client = aws_client.kafka

    cluster_name = f"c-{short_uid()}"
    result = msk_create_cluster_v2(
        ClusterName=cluster_name,
        Provisioned=dict(
            KafkaVersion="v1",
            BrokerNodeGroupInfo={"ClientSubnets": [], "InstanceType": "inst1"},
            NumberOfBrokerNodes=2,
        ),
    )
    cluster_arn = result["ClusterArn"]

    def cluster_ready():
        describe_cluster_result = client.describe_cluster_v2(ClusterArn=cluster_arn)
        assert describe_cluster_result["ClusterInfo"]["State"] == "ACTIVE"
        return describe_cluster_result

    ready_result = retry(cluster_ready, sleep=4, retries=1000)["ClusterInfo"]

    assert_host_customisation(ready_result["Provisioned"]["ZookeeperConnectString"])
    assert_host_customisation(ready_result["Provisioned"]["ZookeeperConnectStringTls"])


def test_mediastore(assert_host_customisation, cleanups, aws_client):
    container_name = f"c-{short_uid()}"
    res = aws_client.mediastore.create_container(ContainerName=container_name)["Container"]
    cleanups.append(lambda: aws_client.mediastore.delete_container(ContainerName=container_name))

    assert_host_customisation(res["Endpoint"])


def test_mq(assert_host_customisation, mq_create_broker, aws_client):
    broker = mq_create_broker()
    describe_result = aws_client.mq.describe_broker(BrokerId=broker["BrokerId"])

    for instance in describe_result["BrokerInstances"]:
        assert_host_customisation(instance["ConsoleURL"])
        for endpoint in instance["Endpoints"]:
            assert_host_customisation(endpoint)


@pytest.mark.skipif(in_ci(), reason="Long-running MWAA tests currently disabled in CI")
def test_mwaa(assert_host_customisation, s3_bucket, mwaa_env_factory):
    webserver_url = mwaa_env_factory(
        f"env-{short_uid()}", "/dags", arns.s3_bucket_arn(s3_bucket), "2.5.1"
    )
    assert_host_customisation(webserver_url)


def test_route53(assert_host_customisation, hosted_zone):
    zone = hosted_zone(Name="example.com")

    for name_server in zone["DelegationSet"]["NameServers"]:
        assert_host_customisation(name_server)


def test_timestream(assert_host_customisation, aws_client):
    for endpoint in aws_client.timestream_query.describe_endpoints()["Endpoints"]:
        assert_host_customisation(endpoint["Address"])

    for endpoint in aws_client.timestream_write.describe_endpoints()["Endpoints"]:
        assert_host_customisation(endpoint["Address"])
