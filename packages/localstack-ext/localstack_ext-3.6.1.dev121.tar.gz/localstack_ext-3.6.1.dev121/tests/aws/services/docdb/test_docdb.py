import logging
import threading

import pytest
from localstack.pro.core.services.docdb.docdb_api import MONGO_DOCKER_IMAGE
from localstack.pro.core.utils.common import get_docker_container_host
from localstack.testing.pytest import markers
from localstack.utils.docker_utils import DOCKER_CLIENT
from localstack.utils.net import get_free_tcp_port, wait_for_port_open
from localstack.utils.strings import short_uid
from localstack.utils.threads import start_worker_thread
from pymongo import MongoClient

DOCDB_INIT = threading.Event()
LOG = logging.getLogger(__name__)


def install_doc_db():
    if MONGO_DOCKER_IMAGE not in DOCKER_CLIENT.get_docker_image_names():
        DOCKER_CLIENT.pull_image(MONGO_DOCKER_IMAGE)


class TestDocDB:
    @pytest.fixture(scope="class", autouse=True)
    def wait_for_mongodb_start(self):
        if DOCDB_INIT.is_set():
            return
        self.init_async()
        assert DOCDB_INIT.wait(timeout=60)

    @classmethod
    def init_async(cls):
        def _run(*args):
            if not DOCDB_INIT.is_set():
                install_doc_db()
                DOCDB_INIT.set()

        start_worker_thread(_run)

    @pytest.fixture
    def create_docdb_cluster(self, aws_client):
        cluster_ids = []

        def _create_docdb_cluster(**kwargs):
            if "DBClusterIdentifier" not in kwargs:
                kwargs["DBClusterIdentifier"] = f"c-{short_uid()}"
            if "Engine" not in kwargs:
                kwargs["Engine"] = "docdb"

            response = aws_client.docdb.create_db_cluster(**kwargs)
            c_id = response["DBCluster"]["DBClusterIdentifier"]
            cluster_ids.append(c_id)
            return response

        yield _create_docdb_cluster

        for cluster_id in cluster_ids:
            aws_client.docdb.delete_db_cluster(DBClusterIdentifier=cluster_id)

    @markers.skip_offline  # DocDB port is bound on the host -> not available in the restricted internal network
    @markers.aws.unknown
    def test_create_query_db(self, aws_client, create_docdb_cluster):
        # create cluster
        username = "user1"
        password = "pass1"
        cluster = create_docdb_cluster(
            MasterUsername=username,
            MasterUserPassword=password,
        )["DBCluster"]
        port = cluster.get("Port")
        # by default we don't use the proxied docker container yet,
        # instead the docker container starts standalone
        host = get_docker_container_host()
        endpoint = f"http://{host}:{port}"
        wait_for_port_open(endpoint, expect_success=False, sleep_time=1, retries=10)

        # connect to cluster
        client = MongoClient(
            f"mongodb://{username}:{password}@{host}:{port}/admin?authSource=admin"
        )
        db = client.test
        result = db.my_collection.insert_one({"test": 123})
        assert result
        assert result.inserted_id

    @markers.skip_offline  # DocDB port is bound on the host -> not available in the restricted internal network
    @markers.aws.unknown
    def test_create_query_db_with_port(self, aws_client, create_docdb_cluster):
        # create cluster
        port = get_free_tcp_port()

        cluster_id = f"cluster-{short_uid()}"
        cluster = create_docdb_cluster(
            DBClusterIdentifier=cluster_id,
            Port=port,
        )["DBCluster"]
        assert cluster["Port"] == port
        assert cluster["DBClusterIdentifier"] == cluster_id
        host = get_docker_container_host()
        endpoint = f"http://{host}:{cluster['Port']}"
        wait_for_port_open(endpoint, expect_success=False, sleep_time=1, retries=10)

        # connect to cluster
        client = MongoClient(f"mongodb://{host}:{cluster['Port']}")
        db = client.test
        result = db.my_collection.insert_one({"test": 123})
        assert result
        assert result.inserted_id
