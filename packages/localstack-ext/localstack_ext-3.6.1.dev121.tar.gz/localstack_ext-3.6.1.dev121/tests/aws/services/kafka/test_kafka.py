import base64
import json
import logging
from collections import defaultdict
from typing import Union

import pytest
from botocore.exceptions import ClientError
from kafka import KafkaAdminClient, KafkaConsumer, KafkaProducer
from kafka.admin import NewTopic
from localstack import config
from localstack.testing.aws.util import is_aws_cloud
from localstack.testing.pytest import markers
from localstack.testing.snapshots.transformer_utility import PATTERN_UUID
from localstack.utils import testutil
from localstack.utils.net import wait_for_port_closed, wait_for_port_open
from localstack.utils.strings import short_uid, to_bytes, to_str
from localstack.utils.sync import poll_condition, retry

TEST_LAMBDA_CODE = """
import json
def handler(event, context):
    print(json.dumps(event))
"""

LOG = logging.getLogger(__name__)


class TestKafka:
    @markers.aws.only_localstack
    def test_interact_with_cluster(self, aws_client, cleanups):
        client = aws_client.kafka

        # create cluster
        cluster_name = f"c-{short_uid()}"
        result = client.create_cluster(
            ClusterName=cluster_name,
            KafkaVersion="2.2.1",
            BrokerNodeGroupInfo={"ClientSubnets": [], "InstanceType": "inst1"},
            NumberOfBrokerNodes=2,
        )
        cluster_arn = result.get("ClusterArn")
        assert f":cluster/{cluster_name}" in cluster_arn

        assert (
            cluster_arn.split("/")[-1] != cluster_name
        )  # this is a random UUID that's part of the arn
        assert cluster_arn.split("/")[-2] == cluster_name

        # describe clusters
        result = client.list_clusters()
        clusters = result.get("ClusterInfoList", [])
        assert clusters

        # describe cluster - wait until ready
        def cluster_ready():
            result = client.describe_cluster(ClusterArn=cluster_arn)
            cluster = result.get("ClusterInfo", {})
            assert cluster["State"] == "ACTIVE"
            return cluster

        cluster = retry(cluster_ready, sleep=2, retries=18)
        zk_host = cluster["ZookeeperConnectString"]
        wait_for_port_open(f"http://{zk_host}")

        response = client.get_bootstrap_brokers(ClusterArn=cluster["ClusterArn"])
        bootstrap_brokers = response["BootstrapBrokerString"]

        # connect kafka client to zookeeper
        producer = KafkaProducer(bootstrap_servers=bootstrap_brokers)
        cleanups.append(producer.close)

        # produce messages
        messages = [to_bytes(f"test message {i}") for i in range(4)]
        for msg in messages:
            producer.send(topic="test", value=msg)

        # consume messages
        consumer = KafkaConsumer(
            "test",
            bootstrap_servers=bootstrap_brokers,
            auto_offset_reset="earliest",
            enable_auto_commit=False,
            consumer_timeout_ms=10_000,
        )
        cleanups.append(consumer.close)

        received = []

        for message in consumer:
            received.append(message)
            if len(received) >= len(messages):
                break

        values = [record.value for record in received]
        assert values == [
            b"test message 0",
            b"test message 1",
            b"test message 2",
            b"test message 3",
        ]

        # clean up
        client.delete_cluster(ClusterArn=cluster_arn)
        self._assert_closed(f"http://{zk_host}")

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(
        paths=[
            "$..BrokerNodeGroupInfo.ConnectivityInfo",
            "$..BrokerNodeGroupInfo.SecurityGroups",
            "$..BrokerNodeGroupInfo.StorageInfo",
            "$..BrokerNodeGroupInfo.ZoneIds",
            "$..ClusterArn",  # almost fine, only ends with -25 and AWS ends with -4
            "$..ClusterInfo.BrokerNodeGroupInfo.ZoneIds",
            "$..ClusterInfo.Provisioned.BrokerNodeGroupInfo.ZoneIds",
            "$..CurrentBrokerSoftwareInfo.KafkaVersion",
            "$..CurrentVersion",
            "$..EncryptionInfo",
            "$..EnhancedMonitoring",
            "$..OpenMonitoring",
            "$..Provisioned.BrokerNodeGroupInfo.ZoneIds",
            "$..StorageMode",
            "$..Tags",
        ]
    )
    def test_cluster_v2_lifecycle(self, msk_create_cluster_v2, snapshot, aws_client):
        snapshot.add_transformer(snapshot.transform.key_value("ClusterName"))
        snapshot.add_transformer(
            snapshot.transform.key_value(
                "ZookeeperConnectString",
                value_replacement="<zookeeper-connect-string>",
                reference_replacement=False,
            )
        )
        snapshot.add_transformer(
            snapshot.transform.key_value(
                "ZookeeperConnectStringTls",
                value_replacement="<zookeeper-connect-string>",
                reference_replacement=False,
            )
        )
        snapshot.add_transformer(snapshot.transform.regex(PATTERN_UUID, "<uuid>"))
        # cannot use reference replacement for lists
        snapshot.add_transformer(
            snapshot.transform.key_value("ClientSubnets", reference_replacement=False)
        )
        snapshot.add_transformer(
            snapshot.transform.key_value("SecurityGroups", reference_replacement=False)
        )
        # create cluster
        cluster_name = f"c-{short_uid()}"
        # we are kind of faking the subnets here, but as only the lifecycle is important here,
        # it didn't seem worth the effort
        subnets = aws_client.ec2.describe_subnets()["Subnets"]
        # NOTE(srw): I have multiple subnets so group by vpc
        by_vpc = defaultdict(list)
        for subnet in subnets:
            by_vpc[subnet["VpcId"]].append(subnet)

        subnets = []
        for vpc in by_vpc:
            if len(by_vpc[vpc]) >= 2:
                subnets = by_vpc[vpc]
                break

        if len(subnets) >= 2:
            client_subnets = subnets[:2]
            subnet_ids = [subnet["SubnetId"] for subnet in client_subnets]
            broker_nodes = len(set([subnet["AvailabilityZone"] for subnet in client_subnets]))
        elif is_aws_cloud():
            # as we do not care about connectivity, we just need two subnets
            pytest.fail("Please configure at least two subnets in your AWS account")
        else:
            subnet_ids = []
            broker_nodes = 2

        create_cluster_result = msk_create_cluster_v2(
            ClusterName=cluster_name,
            Provisioned={
                "KafkaVersion": "3.3.1",
                "BrokerNodeGroupInfo": {
                    "ClientSubnets": subnet_ids,
                    "InstanceType": "kafka.m5.large",
                    "BrokerAZDistribution": "DEFAULT",
                },
                "NumberOfBrokerNodes": broker_nodes,
            },
        )
        snapshot.match("create-cluster-v2-result", create_cluster_result)
        cluster_arn = create_cluster_result["ClusterArn"]
        assert f":cluster/{cluster_name}" in cluster_arn

        assert (
            cluster_arn.split("/")[-1] != cluster_name
        )  # this is a random UUID that's part of the arn
        assert cluster_arn.split("/")[-2] == cluster_name

        # list and describe clusters - both v1 and v2 apis
        list_cluster_v2_result = aws_client.kafka.list_clusters_v2()["ClusterInfoList"]
        # make sure to filter only the matching cluster is listed, to avoid side effects with other tests
        list_cluster_v2_result = [
            c for c in list_cluster_v2_result if c["ClusterName"] == cluster_name
        ]
        assert list_cluster_v2_result
        snapshot.match("list-clusters-v2-result-before-ready", list_cluster_v2_result)
        list_cluster_result = aws_client.kafka.list_clusters()["ClusterInfoList"]
        list_cluster_result = [c for c in list_cluster_result if c["ClusterName"] == cluster_name]
        snapshot.match("list-clusters-result-before-ready", list_cluster_result)
        describe_cluster_result = aws_client.kafka.describe_cluster_v2(ClusterArn=cluster_arn)
        snapshot.match("describe-cluster-v2-result-before-ready", describe_cluster_result)
        describe_cluster_result = aws_client.kafka.describe_cluster(ClusterArn=cluster_arn)
        snapshot.match("describe-cluster-result-before-ready", describe_cluster_result)

        # describe cluster - wait until ready
        def cluster_ready():
            describe_cluster_result = aws_client.kafka.describe_cluster_v2(ClusterArn=cluster_arn)
            assert describe_cluster_result["ClusterInfo"]["State"] == "ACTIVE"
            return describe_cluster_result

        # list and describe clusters - both v1 and v2 apis
        describe_cluster_result = retry(cluster_ready, sleep=4, retries=1000)
        snapshot.match("describe-cluster-v2-result-after-ready", describe_cluster_result)
        describe_cluster_result = aws_client.kafka.describe_cluster(ClusterArn=cluster_arn)
        snapshot.match("describe-cluster-result-after-ready", describe_cluster_result)
        list_cluster_v2_result = aws_client.kafka.list_clusters_v2()["ClusterInfoList"]
        list_cluster_v2_result = [
            c for c in list_cluster_v2_result if c["ClusterName"] == cluster_name
        ]
        snapshot.match("list-clusters-v2-result-after-ready", list_cluster_v2_result)
        list_cluster_result = aws_client.kafka.list_clusters()["ClusterInfoList"]
        list_cluster_result = [c for c in list_cluster_result if c["ClusterName"] == cluster_name]
        snapshot.match("list-clusters-result-after-ready", list_cluster_result)

    @markers.aws.validated
    def test_create_function_v2_exceptions(self, snapshot, aws_client):
        # create cluster without serverless and provisioned config
        with pytest.raises(ClientError) as e:
            aws_client.kafka.create_cluster_v2(ClusterName="test-cluster")
        snapshot.match("create-cluster-without-config", e.value.response)

        # create cluster with both serverless and provisioned config
        with pytest.raises(ClientError) as e:
            aws_client.kafka.create_cluster_v2(
                ClusterName="test-cluster",
                Provisioned={
                    "KafkaVersion": "3.3.1",
                    "BrokerNodeGroupInfo": {
                        "ClientSubnets": [],
                        "InstanceType": "kafka.m5.large",
                        "BrokerAZDistribution": "DEFAULT",
                    },
                    "NumberOfBrokerNodes": 2,
                },
                Serverless={
                    "VpcConfigs": [
                        {
                            "SubnetIds": [],
                        }
                    ],
                    "ClientAuthentication": {},
                },
            )
        snapshot.match("create-cluster-with-both-config", e.value.response)

    @markers.aws.unknown
    def test_create_configurations(self, aws_client):
        client = aws_client.kafka

        # CREATE configuration
        descr = "test config 1"
        result = client.create_configuration(
            Description=descr, KafkaVersions=["2.5"], Name="config1", ServerProperties=b""
        )
        assert result["Name"] == "config1"
        config_arn = result["Arn"]

        # LIST
        configs = client.list_configurations()["Configurations"]
        config = [c for c in configs if c["Name"] == "config1"]
        assert config

        # DESCRIBE
        result = client.describe_configuration(Arn=config_arn)
        assert result["State"] == "ACTIVE"
        assert result.get("CreationTime")

        # UPDATE
        result = client.update_configuration(
            Arn=config_arn, Description="desc 345", ServerProperties=b"foo = 123"
        )
        result = client.describe_configuration(Arn=config_arn)
        assert result["Description"] == "desc 345"
        result = client.describe_configuration(Arn=config_arn)
        assert result["LatestRevision"]["Revision"] == 2

        # REVISIONS
        result = client.list_configuration_revisions(Arn=config_arn)["Revisions"]
        revisions = [r["Revision"] for r in result]
        assert revisions == [1, 2]
        result = client.describe_configuration_revision(Arn=config_arn, Revision=1)
        assert result["Arn"] == config_arn
        assert result["Revision"] == 1
        result = client.describe_configuration_revision(Arn=config_arn, Revision=2)
        assert result["Arn"] == config_arn
        assert result["Revision"] == 2
        with pytest.raises(Exception):
            client.describe_configuration_revision(Arn=config_arn, Revision=3)

        # DELETE
        client.delete_configuration(Arn=config_arn)
        with pytest.raises(Exception):
            client.describe_configuration(Arn=config_arn)

    @markers.aws.only_localstack
    @markers.only_on_amd64
    @pytest.mark.parametrize("create_topic_preemptively", [True, False])
    def test_kafka_lambda_event_source_mapping(
        self, monkeypatch, create_topic_preemptively, create_lambda_function, aws_client, cleanups
    ):
        # TODO: this test is not great, should be snapshot tested

        # renaming to make test a bit clearer
        msk_client = aws_client.kafka

        # run test with arbitrary external hostname configured
        external_host = f"test-host-{short_uid()}"
        monkeypatch.setattr(
            config,
            "LOCALSTACK_HOST",
            config.HostAndPort(external_host, config.GATEWAY_LISTEN[0].port),
        )

        # create Lambda function
        func_name = f"kafka-{short_uid()}"
        create_lambda_function(func_name=func_name, handler_file=TEST_LAMBDA_CODE)

        # create Kafka stream
        cluster_name = f"msk-{short_uid()}"
        cluster = msk_client.create_cluster(
            ClusterName=cluster_name,
            BrokerNodeGroupInfo={"ClientSubnets": [], "InstanceType": "kafka.m5.large"},
            NumberOfBrokerNodes=1,
            KafkaVersion="v1",
        )
        cluster_arn = cluster.get("ClusterArn")
        cleanups.append(lambda: msk_client.delete_cluster(ClusterArn=cluster_arn))
        brokers = msk_client.get_bootstrap_brokers(ClusterArn=cluster_arn)
        broker_host = brokers["BootstrapBrokerString"]
        # assert external_host in broker_host

        # wait until cluster becomes ready ...
        def _cluster_ready():
            state = msk_client.describe_cluster(ClusterArn=cluster_arn)["ClusterInfo"]["State"]
            return "ACTIVE" == state

        port = int(broker_host.split(":")[-1])
        wait_for_port_open(port, sleep_time=0.8, retries=20)
        assert poll_condition(_cluster_ready, timeout=20), "gave up waiting for cluster to be ready"

        # use localhost for local connection, regardless of the returned broker host
        broker_host_local = f"localhost:{port}"

        # if a topic already exists event source mapping should still be successful
        topics = ["t1", "t2"]
        if create_topic_preemptively:
            k_admin = KafkaAdminClient(bootstrap_servers=broker_host_local)
            k_admin.create_topics(
                [NewTopic(name=topics[0], num_partitions=1, replication_factor=1)]
            )

        # create event source mapping
        event_source_mapping = aws_client.lambda_.create_event_source_mapping(
            EventSourceArn=cluster_arn,
            FunctionName=func_name,
            Topics=topics,
            StartingPosition="LATEST",
        )
        cleanups.append(
            lambda: aws_client.lambda_.delete_event_source_mapping(
                UUID=event_source_mapping["UUID"]
            )
        )

        producer = KafkaProducer(bootstrap_servers=broker_host_local)
        cleanups.append(producer.close)

        messages = []
        for topic in topics:
            message = {"test": f"topic {topic}"}
            messages.append(message)
            producer.send(
                topic=topic,
                value=to_bytes(json.dumps(message)),
                headers=[
                    ("foo", b"bar"),
                    ("foo", b"ed"),
                    ("baz", b"fizz"),
                ],
            )
        messages_b64 = [to_str(base64.b64encode(to_bytes(json.dumps(msg)))) for msg in messages]

        # assert that Lambda has been invoked
        def check_invoked():
            logs = testutil.get_lambda_log_events(function_name=func_name, delay_time=15)
            logs = [log for log in logs if any(msg in str(log) for msg in messages_b64)]
            assert len(logs) == len(topics)
            return logs

        events = retry(check_invoked, retries=10, sleep=1)

        # group records by topic
        topic_records: dict[str, list] = defaultdict(list)
        for event in events:
            for topic, records in event["records"].items():
                topic_records[topic].extend(records)

        # assert lambda event format
        record = topic_records["t2-1"][0]
        assert record["topic"] == "t2"
        assert record["timestampType"] == "CREATE_TIME"
        assert record["value"] == "eyJ0ZXN0IjogInRvcGljIHQyIn0="  # b64 encoded "topic t2"
        assert record["headers"] == [
            {"foo": [98, 97, 114]},
            {"foo": [101, 100]},
            {"baz": [102, 105, 122, 122]},
        ]

    @markers.aws.only_localstack
    def test_list_nodes(self, aws_client):
        # uses non-existing subnets, but output format was verified against AWS
        cluster_name = f"my-cluster-{short_uid()}"
        cluster = aws_client.kafka.create_cluster(
            ClusterName=cluster_name,
            BrokerNodeGroupInfo={
                "InstanceType": "kafka.m5.xlarge",
                "BrokerAZDistribution": "DEFAULT",
                "ClientSubnets": ["subnet-0123456789111abcd", "subnet-0123456789333abcd"],
            },
            KafkaVersion="2.2.1",
            NumberOfBrokerNodes=2,
        )

        def cluster_is_read():
            response = aws_client.kafka.describe_cluster(ClusterArn=cluster["ClusterArn"])
            return response["ClusterInfo"]["State"] == "ACTIVE"

        # would have to wait >= 15 minutes on AWS to provision a cluster
        assert poll_condition(
            cluster_is_read, timeout=30, interval=1
        ), "gave up waiting for kafka cluster"

        response = aws_client.kafka.list_nodes(ClusterArn=cluster["ClusterArn"])
        nodes = response["NodeInfoList"]
        assert len(nodes) == 2

        for node in nodes:
            assert node["NodeType"] == "BROKER"
            assert cluster_name in node["NodeARN"]
            assert node["AddedToClusterTime"]
            assert node["InstanceType"] == "t3.small"

        assert nodes[0]["NodeARN"] != nodes[1]["NodeARN"]

        assert int(nodes[0]["BrokerNodeInfo"]["BrokerId"]) == 1
        assert int(nodes[1]["BrokerNodeInfo"]["BrokerId"]) == 2

        aws_client.kafka.delete_cluster(ClusterArn=cluster["ClusterArn"])

    def _assert_closed(self, url_or_port: Union[str, int]):
        # assert that the cluster port is closed, note that this may fail when running the tests against a running
        # container because ports may be considered open regardless
        wait_for_port_closed(url_or_port)
