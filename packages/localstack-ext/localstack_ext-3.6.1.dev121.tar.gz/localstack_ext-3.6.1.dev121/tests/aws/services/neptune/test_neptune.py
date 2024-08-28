import json
import logging
import re
import threading

import pytest
import requests as requests
from gremlin_python.driver import client as gremlin_client
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection
from gremlin_python.process.anonymous_traversal import traversal
from gremlin_python.process.traversal import T
from localstack.pro.core.constants import S3_ASSETS_BUCKET_URL
from localstack.pro.core.services.neptune import packages as neptune_packages
from localstack.pro.core.services.neptune.packages import (
    NEPTUNE_TRANSACTION_VERSION,
    TINKERPOP_DEFAULT_VERSION,
    tinkerpop_package,
)
from localstack.testing.aws.util import is_aws_cloud
from localstack.testing.pytest import markers
from localstack.utils.net import wait_for_port_open
from localstack.utils.strings import short_uid
from localstack.utils.sync import retry
from localstack.utils.threads import start_worker_thread
from neo4j import GraphDatabase

from tests.aws.services.rds.test_rds import wait_until_db_available

LOG = logging.getLogger(__name__)

INIT_LOCK = threading.RLock()

# this can be any UUID string, not just UUID4
# according to edge ID definition in
# https://docs.aws.amazon.com/neptune/latest/userguide/access-graph-gremlin-differences.html
UUID_PATTERN = r"[a-f0-9]{8}-([a-f0-9]{4}-){3}[a-f0-9]{12}"

# patch download location to use our S3 bucket, to speed up the tests
assert neptune_packages.GREMLIN_SERVER_URL_TEMPLATE
neptune_packages.GREMLIN_SERVER_URL_TEMPLATE = (
    f"{S3_ASSETS_BUCKET_URL}/apache-tinkerpop-gremlin-server-{{version}}-bin.zip"
)


class GraphConnection:
    def __init__(self, endpoint: str, message_serializer=None):
        self.endpoint = endpoint
        self.message_serializer = message_serializer

    def __enter__(self):
        self.connection = DriverRemoteConnection(
            self.endpoint, "g", message_serializer=self.message_serializer
        )
        return traversal().withRemote(self.connection)

    def __exit__(self, type, value, traceback):
        self.connection.close()


@pytest.fixture
def neptune_db_cluster(aws_client):
    cluster_ids = []

    def _create_cluster(**kwargs):
        cluster_id = f"c-{short_uid()}"
        cluster = aws_client.neptune.create_db_cluster(
            DBClusterIdentifier=cluster_id, Engine="neptune", **kwargs
        )["DBCluster"]
        cluster_ids.append(cluster_id)

        if is_aws_cloud():
            wait_until_db_available(aws_client.neptune, cluster_id=cluster_id)
        else:
            wait_for_port_open(
                cluster["Port"],
                http_path="/status",
                retries=120,
                sleep_time=2,
            )
        return cluster

    yield _create_cluster

    # clean up
    for cluster_id in cluster_ids:
        try:
            aws_client.neptune.delete_db_cluster(
                DBClusterIdentifier=cluster_id, SkipFinalSnapshot=True
            )
        except Exception as e:
            LOG.info("Unable to clean up Neptune test resources: %s", e)


class TestNeptune:
    @pytest.fixture(scope="class", autouse=True)
    def setup_neptune(cls):
        with INIT_LOCK:
            pass

    @classmethod
    def init_async(cls):
        def _run(*args):
            with INIT_LOCK:
                tinkerpop_package.install()

        start_worker_thread(_run)

    @pytest.mark.parametrize(
        "neptune_version, expected_version, transaction",
        [
            (None, TINKERPOP_DEFAULT_VERSION, False),
            ("1.1.0.0", "3.4.11", False),
            ("1.2.0.1", "3.5.2", False),
            ("1.2.1.0", "3.6.2", False),
            (None, TINKERPOP_DEFAULT_VERSION, True),
        ],
    )
    @markers.resource_heavy
    @markers.aws.unknown
    def test_create_query_db(
        self, neptune_db_cluster, neptune_version, expected_version, transaction, monkeypatch
    ):
        # create cluster
        kwargs = {}
        if neptune_version:
            kwargs["EngineVersion"] = neptune_version
        if transaction:
            from localstack.pro.core import config as ext_config

            monkeypatch.setattr(ext_config, "NEPTUNE_ENABLE_TRANSACTION", 1)
            expected_version = NEPTUNE_TRANSACTION_VERSION

        cluster = neptune_db_cluster(**kwargs)

        port = cluster["Port"]
        hostname = "localhost" if not is_aws_cloud() else cluster["Endpoint"]

        status_response = requests.get(f"http://{hostname}:{port}/status")
        status_dict = json.loads(status_response.content.decode("utf-8"))
        assert status_dict.get("gremlin", {}).get("version") == f"tinkerpop-{expected_version}"

        # test DriverRemoteConnection API
        conn = DriverRemoteConnection(f"ws://{hostname}:{port}/gremlin", "g")
        g = traversal().withRemote(conn)
        result = g.V().limit(5).toList()
        assert type(result) == list
        vertices_before = len(result)

        # test Vertex and Edge IDs
        # See https://docs.aws.amazon.com/neptune/latest/userguide/
        #    access-graph-gremlin-differences.html#w3aac15c18c10c15c25
        v1 = g.addV("label1").property(T.id, "id123").next()
        with pytest.raises(Exception) as ex:
            g.addV("label2").property(T.id, "id123").next()
        assert "already exists" in str(ex)
        v2 = g.addV("label3").next()
        # check if generated vertex ID is a UUID
        assert re.match(UUID_PATTERN, v2.id)

        result = g.V().limit(10).toList()
        vertices_after = len(result)
        assert vertices_after == vertices_before + 2
        e1 = g.V(v1).addE("link").to(v2).next()
        # check if edge ID is a UUID as well
        assert re.match(UUID_PATTERN, e1.id)

        connection = g.V().hasLabel("label1").out("link").next()
        assert v2 == connection

        conn.close()

        # test Client API

        graph_client = gremlin_client.Client(f"ws://localhost:{cluster['Port']}/gremlin", "g")

        result_set = graph_client.submit("[1,2,3,4]")
        future_results = result_set.all()
        results = future_results.result()
        assert results == [1, 2, 3, 4]

        def _assert_done():
            assert result_set.done.done()

        future_result_set = graph_client.submit_async("[1,2,3,4]")
        result_set = future_result_set.result()
        result = result_set.one()
        assert result
        assert results == [1, 2, 3, 4]
        retry(_assert_done, sleep=0.5, retries=7)
        graph_client.close()

    @markers.resource_heavy
    @markers.aws.unknown
    @pytest.mark.parametrize("transaction", (False, True))
    def test_vertex_multi_label(self, neptune_db_cluster, transaction, monkeypatch):
        if transaction:
            from localstack.pro.core import config as ext_config

            monkeypatch.setattr(ext_config, "NEPTUNE_ENABLE_TRANSACTION", 1)
        cluster = neptune_db_cluster()

        port = cluster["Port"]
        hostname = "localhost" if not is_aws_cloud() else cluster["Endpoint"]
        conn = DriverRemoteConnection(f"ws://{hostname}:{port}/gremlin", "g")
        g = traversal().withRemote(conn)

        # create multi-level vertex
        multi_label = "label1::label2::label3"
        g.addV(multi_label).property(T.id, "id123").next()

        # assert that vertex can be found for each individual label
        for label in ("label1", "label2", "label3"):
            vertex_label = g.V().hasLabel(label).label().next()
            assert vertex_label == multi_label

        # assert label select for a list
        vertex_label = g.V().hasLabel("label2", "label4", "anotherlabel").label().next()
        assert vertex_label == multi_label

        # assert that invalid label does not match a vertex
        with pytest.raises(StopIteration):
            g.V().hasLabel("label4").label().next()

        with pytest.raises(StopIteration):
            g.V().hasLabel("label4", "differentlabel").label().next()

    @markers.aws.unknown
    def test_create_query_db_tags(self, neptune_db_cluster, aws_client):
        cluster = neptune_db_cluster()

        res_name = cluster["DBClusterArn"]
        aws_client.neptune.add_tags_to_resource(
            ResourceName=res_name, Tags=[{"Key": "my-key", "Value": "my-value"}]
        )
        tags = aws_client.neptune.list_tags_for_resource(ResourceName=res_name)["TagList"]
        assert tags[0]["Value"] == "my-value"

    @markers.aws.unknown
    def test_create_cluster_with_tags(self, neptune_db_cluster, aws_client):
        cluster = neptune_db_cluster(Tags=[{"Key": "my-key", "Value": "my-value"}])

        res_name = cluster["DBClusterArn"]
        tags = aws_client.neptune.list_tags_for_resource(ResourceName=res_name)["TagList"]
        assert tags[0]["Value"] == "my-value"

    @markers.aws.unknown
    def test_create_neo4j_cluster(self, neptune_db_cluster, monkeypatch, aws_client):
        from localstack.pro.core import config as ext_config

        monkeypatch.setattr(ext_config, "NEPTUNE_DB_TYPE", "neo4j")

        # create cluster
        cluster = neptune_db_cluster()
        port = cluster["Port"]

        # connect to Neo4J via bolt
        driver = GraphDatabase.driver(f"bolt://localhost:{port}", encrypted=False)

        name = short_uid()
        with driver.session() as session:
            session.run("CREATE (a:Person {name: $name})", name=name)

        with driver.session() as session:
            result = session.run("MATCH (p:Person) RETURN p")
            entries = list(result)
            # should have only one entry, as we're querying a fresh instance
            assert len(entries) == 1
            assert entries[0]["p"]["name"] == name

        with driver.session() as session:
            result = session.run(
                "MATCH (p:Person) WHERE p.name = $name RETURN p.name AS name", name=name
            )
            entries = list(result)
            assert len(entries) == 1
            assert entries[0]["name"] == name
