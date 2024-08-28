from kafka import KafkaAdminClient
from kafka.admin import NewTopic
from localstack.utils.net import wait_for_port_open
from localstack.utils.strings import short_uid
from localstack.utils.sync import retry


def test_kafka_cluster(persistence_validations, snapshot, aws_client):
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
    cluster_name = f"cluster-name-{short_uid()}"
    result = aws_client.kafka.create_cluster(
        ClusterName=cluster_name,
        BrokerNodeGroupInfo={
            "InstanceType": "kafka.m5.xlarge",
            "BrokerAZDistribution": "DEFAULT",
            "ClientSubnets": [
                "subnet-0123456789111abcd",
                "subnet-0123456789222abcd",
                "subnet-0123456789333abcd",
            ],
        },
        KafkaVersion="2.8.0",
        NumberOfBrokerNodes=3,
    )
    cluster_arn = result["ClusterArn"]

    def cluster_ready():
        describe_cluster_result = aws_client.kafka.describe_cluster(ClusterArn=cluster_arn)
        assert describe_cluster_result["ClusterInfo"]["State"] == "ACTIVE"
        return describe_cluster_result

    def validate():
        retry(cluster_ready, sleep=4, retries=10)
        describe_cluster_result = aws_client.kafka.describe_cluster(ClusterArn=cluster_arn)
        snapshot.match("describe-cluster", describe_cluster_result)

    def create_topic():
        brokers = aws_client.kafka.get_bootstrap_brokers(ClusterArn=cluster_arn)
        broker_host = brokers["BootstrapBrokerString"]
        port = int(broker_host.split(":")[-1])
        wait_for_port_open(port, sleep_time=0.8, retries=20)
        broker_host_local = f"localhost:{port}"

        admin = KafkaAdminClient(bootstrap_servers=broker_host_local)
        topic_name = f"topic-{short_uid()}"
        admin.create_topics([NewTopic(name=topic_name, num_partitions=1, replication_factor=1)])
        topics = admin.list_topics()
        assert topic_name in topics

    persistence_validations.register(validate)
    persistence_validations.register(create_topic)
