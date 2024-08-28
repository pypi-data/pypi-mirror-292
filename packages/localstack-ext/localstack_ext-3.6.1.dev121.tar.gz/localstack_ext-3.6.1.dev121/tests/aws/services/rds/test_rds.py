import io
import json
import logging
import os
import textwrap
import threading
import time

import pymysql
import pytest
import requests as requests
from botocore.exceptions import ClientError
from localstack import config
from localstack.constants import LOCALHOST_IP
from localstack.pro.core import config as ext_config
from localstack.pro.core.services.rds.db_utils import (
    DEFAULT_MASTER_USERNAME,
    DBBackend,
)
from localstack.pro.core.services.rds.engine_mssql import DOCKER_IMAGE_MSSQL
from localstack.pro.core.services.rds.engine_postgres import POSTGRES_DEFAULT_VERSION
from localstack.testing.aws.util import is_aws_cloud
from localstack.testing.pytest import markers
from localstack.utils import testutil
from localstack.utils.aws import arns, resources
from localstack.utils.common import external_service_ports
from localstack.utils.docker_utils import DOCKER_CLIENT
from localstack.utils.net import wait_for_port_closed, wait_for_port_open
from localstack.utils.platform import get_arch
from localstack.utils.run import is_command_available
from localstack.utils.strings import short_uid, to_bytes
from localstack.utils.sync import retry
from localstack.utils.threads import start_worker_thread
from localstack_snapshot.snapshots.transformer import KeyValueBasedTransformer
from psycopg2.extensions import make_dsn

LOG = logging.getLogger(__name__)

# default DB/user names
db_name = "test"
db_user = DEFAULT_MASTER_USERNAME
# For parity reasons, we need to define a test password here - our default for Postgres is "test",
#  which is too short for use in real AWS. TODO discuss whether we want to change this.
DEFAULT_TEST_MASTER_PASSWORD = "Test123!"

TEST_CSV = """
1\tvalue 1
2\tvalue 2
3\tvalue 3
"""

TEST_LAMBDA_ECHO = """
import json
def handler(event, context):
    print(event)
    return event
"""

INIT_LOCK_MSSQL = threading.RLock()

# username used for testing RDS IAM auth
TEST_IAM_USERNAME = "test_iam_user"

# marker to skip tests if Postgres is not available (enables both, local and
#  in-Docker testing)
skip_if_postgres_unavailable = pytest.mark.skipif(
    not is_aws_cloud() and not config.is_in_docker and not is_command_available("postgres"),
    reason="Skipping test outside of Docker or if `postgres` is not available",
)

# skip verify attributes
SKIP_VERIFY_DB_INSTANCE_POSTGRES = [
    # missing:
    "$..ActivityStreamStatus",
    "$..AssociatedRoles",
    "$..BackupTarget",
    "$..CACertificateIdentifier",
    "$..CustomerOwnedIpEnabled",
    "$..DBSubnetGroup",
    "$..DomainMemberships",
    "$..MonitoringInterval",
    "$..CertificateDetails",
    "$..StorageThroughput",
    "$..NetworkType",
    "$..PendingModifiedValues",
    "$..PerformanceInsightsEnabled",
    "$..Endpoint.HostedZoneId",
    "$..LatestRestorableTime",
    # different pattern in AWS:
    # different values:
    "$..PubliclyAccessible",
    "$..AutoMinorVersionUpgrade",
    "$..OptionGroupName",
    "$..DbInstancePort",  # probably because of different status
    # according to API: Valid values: license-included | bring-your-own-license | general-public-license
    # AWS returned "postgresql-license"
    "$..LicenseModel",
    # added in LocalStack (caused by different status?):
    "$..InstanceCreateTime",
    "$..StatusInfos",
    "$..EnabledCloudwatchLogsExports",
]
SKIP_VERIFY_DB_CLUSTER_POSTGRES = [
    # missing:
    "$..ActivityStreamStatus",
    "$..AvailabilityZones",
    "$..BackupRetentionPeriod",
    "$..ClusterCreateTime",
    "$..CopyTagsToSnapshot",
    "$..CrossAccountClone",
    "$..DeletionProtection",
    "$..EarliestRestorableTime",
    "$..EngineMode",
    "$..HostedZoneId",
    "$..HttpEndpointEnabled",
    "$..LatestRestorableTime",
    "$..PreferredBackupWindow",
    "$..PreferredMaintenanceWindow",
    "$..ReadReplicaIdentifiers",
    # different value:
    "$..DBClusterMembers..IsClusterWriter",
    "$..DBClusterParameterGroup",
    "$..Port",
]


def get_availability_zones_transformer(region: str):
    return KeyValueBasedTransformer(
        lambda k, v: v
        if k == "AvailabilityZones"
        and isinstance(v, list)
        and len(v) == 3
        and all(zone.startswith(region) for zone in v)
        else None,
        replacement="availability-zones",
        replace_reference=False,
    )


def get_availability_zone_transformer(region: str):
    return KeyValueBasedTransformer(
        lambda k, v: v
        if k == "AvailabilityZone" and isinstance(v, str) and v.startswith(region)
        else None,
        replacement="availability-zone",
        replace_reference=False,
    )


def wait_until_db_available(
    rds_client, cluster_id: str = None, instance_id: str = None, global_cluster_id: str = None
):
    def check_running():
        if cluster_id:
            result = rds_client.describe_db_clusters(DBClusterIdentifier=cluster_id)["DBClusters"]
        elif instance_id:
            result = rds_client.describe_db_instances(DBInstanceIdentifier=instance_id)[
                "DBInstances"
            ]
        else:
            result = rds_client.describe_global_clusters(GlobalClusterIdentifier=global_cluster_id)[
                "GlobalClusters"
            ]
        status = result[0].get("DBInstanceStatus") or result[0].get("Status")
        assert status == "available"
        return result[0]

    retries = 500 if is_aws_cloud() else 60
    sleep = 10 if is_aws_cloud() else 1
    return retry(check_running, sleep=sleep, retries=retries)


@pytest.fixture
def rds_create_db_parameter_group(aws_client):
    db_parameter_groups = list()

    def _create_db_parameter_group(**kwargs):
        response = aws_client.rds.create_db_parameter_group(**kwargs)
        db_parameter_groups.append(response["DBParameterGroup"]["DBParameterGroupName"])
        return response

    yield _create_db_parameter_group

    for group_name in db_parameter_groups:
        try:
            aws_client.rds.delete_db_parameter_group(DBParameterGroupName=group_name)
        except Exception as e:
            LOG.debug("error cleaning up db parameter group name %s: %s", group_name, e)


@pytest.fixture
def rds_copy_db_parameter_group(aws_client):
    db_parameter_groups = list()

    def _copy_db_parameter_group(**kwargs):
        response = aws_client.rds.copy_db_parameter_group(**kwargs)
        db_parameter_groups.append(response["DBParameterGroup"]["DBParameterGroupName"])
        return response

    yield _copy_db_parameter_group

    for group_name in db_parameter_groups:
        try:
            aws_client.rds.delete_db_parameter_group(DBParameterGroupName=group_name)
        except Exception as e:
            LOG.debug("error cleaning up db parameter group name %s: %s", group_name, e)


@pytest.fixture
def rds_create_db_proxy(aws_client):
    db_proxy_list = list()

    def _create_db_proxy(**kwargs):
        response = aws_client.rds.create_db_proxy(**kwargs)
        db_proxy_list.append(response["DBProxy"]["DBProxyName"])
        return response

    yield _create_db_proxy

    for proxy in db_proxy_list:
        try:
            aws_client.rds.delete_db_proxy(DBProxyName=proxy)
        except Exception as e:
            LOG.debug("error cleaning up db proxy %s: %s", proxy, e)


@pytest.fixture
def rds_create_db_cluster_parameter_group(aws_client):
    parameter_group_names = list()

    def _create_parameter_group(**kwargs):
        response = aws_client.rds.create_db_cluster_parameter_group(**kwargs)
        parameter_group_names.append(
            response["DBClusterParameterGroup"]["DBClusterParameterGroupName"]
        )
        return response

    yield _create_parameter_group

    for group_name in parameter_group_names:
        try:
            aws_client.rds.delete_db_cluster_parameter_group(DBClusterParameterGroupName=group_name)
        except Exception as e:
            LOG.debug("error cleaning up db cluster parameter group %s: %s", group_name, e)


@pytest.fixture
def rds_create_db_cluster_endpoint(aws_client):
    cluster_endpoints = list()

    def _create_cluster_endpoint(**kwargs):
        response = aws_client.rds.create_db_cluster_endpoint(**kwargs)
        endpoint_id = response["DBClusterEndpointIdentifier"]
        cluster_endpoints.append(endpoint_id)

        def check_running():
            result = aws_client.rds.describe_db_cluster_endpoints(
                DBClusterEndpointIdentifier=endpoint_id
            )
            assert result["DBClusterEndpoints"][0]["Status"] == "available"

        retry(check_running, sleep=1, retries=60)
        return response

    yield _create_cluster_endpoint

    for endpoint in cluster_endpoints:
        try:
            aws_client.rds.delete_db_cluster_endpoint(DBClusterEndpointIdentifier=endpoint)
        except Exception as e:
            LOG.debug("error cleaning up db cluster endpoint %s: %s", endpoint, e)


@pytest.fixture
def rds_restore_db_cluster_from_snapshot(aws_client):
    cluster_ids = []

    def _restore_from_snapshot(**kwargs):
        rds_client = kwargs.pop("rds_client", aws_client.rds)
        response = rds_client.restore_db_cluster_from_snapshot(**kwargs)
        cluster_ids.append((response["DBCluster"]["DBClusterIdentifier"], rds_client))
        return response

    yield _restore_from_snapshot

    for cluster_id, client in cluster_ids:
        try:
            client.delete_db_cluster(DBClusterIdentifier=cluster_id, SkipFinalSnapshot=True)
        except Exception as e:
            LOG.debug("Error cleaning up db cluster, restored from snapshot %s: %s", cluster_id, e)


@pytest.fixture
def rds_restore_db_instance_from_snapshot(aws_client):
    instance_ids = []

    def _restore_from_snapshot(**kwargs):
        rds_client = kwargs.pop("rds_client", aws_client.rds)
        response = rds_client.restore_db_instance_from_db_snapshot(**kwargs)
        instance_ids.append((response["DBInstance"]["DBInstanceIdentifier"], rds_client))
        return response

    yield _restore_from_snapshot

    for instance_id, client in instance_ids:
        try:
            client.delete_db_instance(DBInstanceIdentifier=instance_id, SkipFinalSnapshot=True)
        except Exception as e:
            LOG.debug(
                "error cleaning up db instance, restored from snapshot %s: %s", instance_id, e
            )


@pytest.fixture
def create_db_instance_with_iam_auth(rds_create_db_instance):
    def _create_db(with_block: bool = False):
        db_pass = "Test123!"
        result = rds_create_db_instance(
            Engine="postgres",
            DBName=db_name,
            MasterUsername=DEFAULT_MASTER_USERNAME,
            MasterUserPassword=db_pass,
            EnableIAMDatabaseAuthentication=True,
            expose_public_port=True,
        )
        hostname = result["Endpoint"]["Address"]
        port = result["Endpoint"]["Port"]
        assert result["IAMDatabaseAuthenticationEnabled"]

        if with_block:
            # wrap the call in a block, to validate that the detection of the query still works and that we
            queries = [
                textwrap.dedent(
                    f"""
            DO
            $do$
            BEGIN
                CREATE USER "{TEST_IAM_USERNAME}" WITH LOGIN;
                GRANT rds_iam TO {TEST_IAM_USERNAME};
            END
            $do$;"""
                )
            ]
        else:
            queries = [
                # create user (no password required), grant rds_iam role
                f'CREATE USER "{TEST_IAM_USERNAME}" WITH LOGIN;',
                f"GRANT rds_iam TO {TEST_IAM_USERNAME};",
            ]

        for query in queries:
            TestRDSBase.query_postgres(
                port,
                query=query,
                hostname=hostname,
                password=db_pass,
                results=False,
            )

        return result

    return _create_db


def _add_role_to_db_instance(rds_client, db_identifier: str, feature_name: str, role: str):
    def _add_role():
        # IAM is eventually consistent, and this call may intermittently fail
        return rds_client.add_role_to_db_instance(
            DBInstanceIdentifier=db_identifier,
            FeatureName=feature_name,
            RoleArn=role,
        )

    result = retry(
        _add_role, retries=60 if is_aws_cloud() else 30, sleep=5 if is_aws_cloud() else 1
    )

    def _check_role_ready():
        result = rds_client.describe_db_instances(DBInstanceIdentifier=db_identifier)
        instance = result["DBInstances"][0]
        matching = [
            r
            for r in instance["AssociatedRoles"]
            if r["RoleArn"] == role and r["FeatureName"] == feature_name
        ]
        assert matching[0]["Status"] == "ACTIVE"

    retry(_check_role_ready, retries=60 if is_aws_cloud() else 30, sleep=5 if is_aws_cloud() else 1)

    return result


def _add_role_to_db_cluster(rds_client, cluster_id: str, feature_name: str, role: str):
    def _add_role():
        # IAM is eventually consistent, and this call may intermittently fail
        return rds_client.add_role_to_db_cluster(
            DBClusterIdentifier=cluster_id,
            FeatureName=feature_name,
            RoleArn=role,
        )

    result = retry(_add_role, retries=30, sleep=2)

    def _check_role_ready():
        result = rds_client.describe_db_clusters(DBClusterIdentifier=cluster_id)
        instance = result["DBClusters"][0]
        matching = [
            r
            for r in instance["AssociatedRoles"]
            if r["RoleArn"] == role and r["FeatureName"] == feature_name
        ]
        assert matching[0]["Status"] == "ACTIVE"

    retry(_check_role_ready, retries=30, sleep=2)

    return result


class TestRDSBase:
    """Base class with shared test utilities for the different DB engines (PG/MySQL/MSSQL)"""

    def _create_db_instance_wait_for_ready(
        self, db_type, rds_create_db_instance, user=None, password=None, db_id=None, **kwargs
    ):
        db_id = db_id or f"rds-{short_uid()}"
        kwargs.setdefault("Port", 12345)
        if user and password:
            kwargs.update({"MasterUsername": user, "MasterUserPassword": password})
        if not kwargs.get("MasterUsername"):
            kwargs["MasterUsername"] = DEFAULT_MASTER_USERNAME
        if not kwargs.get("MasterUserPassword"):
            kwargs["MasterUserPassword"] = DEFAULT_TEST_MASTER_PASSWORD
        result = rds_create_db_instance(
            DBInstanceIdentifier=db_id,
            Engine=db_type,
            **kwargs,
        )
        return result

    def _create_table_and_select(self, db_type, port, user=None, password=None):
        table_name = f"test{short_uid()}"
        query = f"""
            CREATE TABLE {table_name} (id integer);
            INSERT INTO {table_name}(id) VALUES (123);
            SELECT * FROM {table_name};
        """
        result = None
        if db_type in ("mariadb", "mysql"):
            result = self.query_mysql(port, query, user=user, password=password)
        elif "sqlserver" in db_type:
            result = self.query_mssql(port, query, user=user, password=password)
        elif "postgres" in db_type:
            self.query_postgres(port, query, username=user, password=password, results=False)
            result = self.query_postgres(port, f"SELECT * FROM {table_name}")
        assert result == [123]

    def _assert_sample_data_exists(self, port, table_name):
        # query new DB instance
        query = f"SELECT * FROM {table_name}"
        result = self.query_postgres(port, query)
        assert result == [{"id": 123, "value": "test"}]

    def _insert_sample_data(self, port):
        # insert test data
        table_name = f"test{short_uid()}"
        query = """
            CREATE TABLE {table} (id integer, value text);
            INSERT INTO {table} (id, value) VALUES (123, 'test')
        """.format(table=table_name)
        self.query_postgres(port, query, results=False)
        return table_name

    # query util functions

    def query_mysql(self, port, query, user=None, password=None):
        user = user or db_user
        password = password or DEFAULT_TEST_MASTER_PASSWORD

        # TODO: potentially unify with engine_mysql.query_mysql(..) util function

        connection = pymysql.connect(
            user=user,
            password=password,
            port=port,
            database=db_name,
            cursorclass=pymysql.cursors.DictCursor,
        )

        with connection:
            with connection.cursor() as cursor:
                queries = [q for q in query.split(";") if q.strip()]
                result = None
                for query in queries:
                    cursor.execute(query)
                    result = cursor.fetchall()
                if len(result) == 1 and len(result[0]) == 1:
                    # convert results like [{'id': 123}] to [123]
                    result[0] = list(result[0].values())[0]
                return result

    @classmethod
    def query_postgres(
        cls,
        port: int,
        query: str,
        database: str = None,
        username: str = None,
        password: str = None,
        hostname: str = None,
        results: bool = True,
    ):
        from postgres import Postgres

        database = database or db_name
        password = password or DEFAULT_TEST_MASTER_PASSWORD
        hostname = hostname or LOCALHOST_IP
        username = username or db_user

        # Note: Using the make_dsn(..) utility here, as `password` (in particular for RDS IAM auth tokens)
        # may contain characters not compatible to be embedded in a postgres://... connection URL.
        db_connection_string = make_dsn(
            host=hostname, port=port, database=database, user=username, password=password
        )
        db = Postgres(db_connection_string)

        try:
            if not results:
                result = db.run(query)
            else:
                result = db.all(query)
            if result:
                for i in range(len(result)):
                    if isinstance(result[i], tuple):
                        result[i] = result[i]._asdict()

            return result
        finally:
            # clear the pool right away and close connections, before the object is garbage collected
            db.pool.clear()

    def query_mssql(self, port, query, user=None, password=None):
        import pymssql

        user = user or db_user
        password = password or DEFAULT_TEST_MASTER_PASSWORD

        wait_for_port_open(port, retries=3, sleep_time=1)
        conn = pymssql.connect(
            server="localhost", port=port, user=user, password=password, database=db_name
        )
        with conn:
            cursor = conn.cursor(as_dict=True)
            cursor.execute(query)
            result = list(cursor)
            if len(result) == 1 and len(result[0]) == 1:
                # convert results like [{'id': 123}] to [123]
                result[0] = list(result[0].values())[0]
            return result


@skip_if_postgres_unavailable
class TestRdsPostgres(TestRDSBase):
    @markers.aws.validated
    def test_describe_db_instance_filters(self, aws_client, rds_create_db_instance):
        cred = "Test123!"
        user = "user1"
        db_id_1 = f"rds-1-{short_uid()}"
        result = rds_create_db_instance(
            DBInstanceIdentifier=db_id_1,
            DBInstanceClass="db.m5.large",
            Engine="postgres",
            MasterUsername=user,
            MasterUserPassword=cred,
            AllocatedStorage=5,
            EngineVersion="13.7",
            PubliclyAccessible=False,
        )

        db_id_2 = f"rds-2-{short_uid()}"
        result_2 = rds_create_db_instance(
            DBInstanceIdentifier=db_id_2,
            DBInstanceClass="db.m5.large",
            Engine="postgres",
            MasterUsername=user,
            MasterUserPassword=cred,
            AllocatedStorage=5,
            EngineVersion="13.7",
            PubliclyAccessible=False,
        )

        dbi_resource_id = result["DbiResourceId"]
        assert dbi_resource_id != result_2["DbiResourceId"]
        dbi_filter = aws_client.rds.describe_db_instances(
            Filters=[{"Name": "dbi-resource-id", "Values": [dbi_resource_id]}]
        )["DBInstances"]

        id_filter = aws_client.rds.describe_db_instances(
            Filters=[{"Name": "db-instance-id", "Values": [db_id_1]}]
        )["DBInstances"]

        assert len(dbi_filter) == 1
        assert len(id_filter) == 1
        assert dbi_filter == id_filter

        engine_filter = aws_client.rds.describe_db_instances(
            Filters=[{"Name": "engine", "Values": ["postgres", "mysql"]}]
        )

        assert (
            len(engine_filter["DBInstances"]) >= 2
        )  # TODO in CI some database seems not be cleaned up
        db_ids = [i["DBInstanceIdentifier"] for i in engine_filter["DBInstances"]]
        assert db_id_1 in db_ids
        assert db_id_2 in db_ids

        engine_filter = aws_client.rds.describe_db_instances(
            Filters=[{"Name": "engine", "Values": ["mysql"]}]
        )
        assert len(engine_filter["DBInstances"]) == 0

        filters_combined = aws_client.rds.describe_db_instances(
            Filters=[
                {"Name": "engine", "Values": ["postgres", "mysql"]},
                {"Name": "db-instance-id", "Values": [db_id_1]},
            ]
        )["DBInstances"]

        assert len(filters_combined) == 1
        assert filters_combined == dbi_filter

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(
        paths=(
            SKIP_VERIFY_DB_INSTANCE_POSTGRES
            + [
                "$..DBName",  # added in LocalStack
            ]
        )
    )
    def test_db_instance_already_exists(self, rds_create_db_instance, snapshot, aws_client):
        snapshot.add_transformer(snapshot.transform.rds_api())
        snapshot.add_transformer(get_availability_zone_transformer(aws_client.sts.meta.region_name))

        cred = "Test123!"
        user = "test"
        db_id = f"rds-{short_uid()}"
        result = rds_create_db_instance(
            DBInstanceIdentifier=db_id,
            DBInstanceClass="db.m6g.large",
            Engine="postgres",
            MasterUsername=user,
            MasterUserPassword=cred,
            AllocatedStorage=5,
            EngineVersion="13.7",
        )
        snapshot.match("create-db-instance", result)
        assert result

        with pytest.raises(Exception) as exc:
            aws_client.rds.create_db_instance(
                DBInstanceIdentifier=db_id,
                DBInstanceClass="db.m6g.large",
                Engine="postgres",
                Port=12345,
                MasterUsername=user,
                MasterUserPassword=cred,
                AllocatedStorage=5,
            )

        exc.match("DBInstanceAlreadyExists")
        snapshot.match("create-db-instance-already-exists", exc.value.response)

    @markers.aws.validated
    def test_db_cluster_already_exists(self, rds_create_db_cluster, snapshot, aws_client):
        cred = "Test123!"
        user = "test"
        db_id = f"rds-{short_uid()}"

        result = rds_create_db_cluster(
            DBClusterIdentifier=db_id,
            Engine="aurora-postgresql",
            MasterUsername=user,
            MasterUserPassword=cred,
        )
        # TODO currently comparison not feasible
        # snapshot.match("create-db-cluster", result)
        assert result

        with pytest.raises(Exception) as exc:
            rds_create_db_cluster(
                DBClusterIdentifier=db_id,
                Engine="aurora-postgresql",
                MasterUsername=user,
                MasterUserPassword=cred,
            )

        exc.match("DBClusterAlreadyExists")
        snapshot.match("create-db-cluster-already-exists", exc.value.response)

    @markers.aws.unknown
    def test_create_postgres(self, rds_create_db_instance, aws_client):
        db_type = "postgres"
        result = self._create_db_instance_wait_for_ready(db_type, rds_create_db_instance)
        port = result["Endpoint"]["Port"]
        address = result["Endpoint"]["Address"]

        describe_res = aws_client.rds.describe_db_instances(
            DBInstanceIdentifier=result["DBInstanceIdentifier"]
        )

        describe_address = describe_res["DBInstances"][0]["Endpoint"]["Address"]
        assert address == describe_address == "localhost.localstack.cloud"

        self._create_table_and_select(db_type, port)

        arn = result["DBInstanceArn"]
        tags = [{"Key": "hello", "Value": "world"}, {"Key": "my-key", "Value": "my-value"}]
        aws_client.rds.add_tags_to_resource(ResourceName=arn, Tags=tags)

        result = aws_client.rds.list_tags_for_resource(ResourceName=arn)
        assert tags == result["TagList"]

        aws_client.rds.remove_tags_from_resource(ResourceName=arn, TagKeys=["my-key"])
        result = aws_client.rds.list_tags_for_resource(ResourceName=arn)
        assert [{"Key": "hello", "Value": "world"}] == result["TagList"]

    @markers.aws.only_localstack
    # tests if port is allocated on the host, and freed after the instance is deleted
    def test_create_db_custom_port(self, rds_create_db_instance, aws_client):
        custom_port = external_service_ports.reserve_port(duration=0.1)
        time.sleep(0.1)
        result = self._create_db_instance_wait_for_ready(
            "postgres", rds_create_db_instance, Port=custom_port
        )

        # assert that the DB is available under the custom port
        port = result["Endpoint"]["Port"]
        assert port == custom_port
        wait_for_port_open(port, sleep_time=0.5, retries=20)

        # delete DB instance, assert that port is available again
        instance_id = result["DBInstanceIdentifier"]
        aws_client.rds.delete_db_instance(DBInstanceIdentifier=instance_id)
        wait_for_port_closed(port, sleep_time=0.5, retries=20)

    @markers.aws.validated
    def test_create_db_cluster_non_existing_parameter_group(self, snapshot, aws_client):
        with pytest.raises(ClientError) as e:
            aws_client.rds.create_db_cluster(
                DBClusterIdentifier=f"rds-cluster-{short_uid()}",
                Engine="aurora-postgresql",
                MasterUsername="myuser",
                MasterUserPassword="Test123!",
                DBClusterParameterGroupName="my-test-group",
            )

        snapshot.match("create_db_cluster", e.value.response)

    @markers.aws.validated
    def test_create_db_instance_non_existing_parameter_group(self, snapshot, aws_client):
        with pytest.raises(ClientError) as e:
            aws_client.rds.create_db_instance(
                DBInstanceIdentifier=f"rds-cluster-{short_uid()}",
                DBInstanceClass="db.m6g.large",
                Engine="postgres",
                MasterUsername="myuser",
                MasterUserPassword="Test123!",
                AllocatedStorage=5,
                EngineVersion="13.7",
                DBParameterGroupName="my-test-group",
            )

        snapshot.match("create_db_instance", e.value.response)

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(
        paths=SKIP_VERIFY_DB_INSTANCE_POSTGRES
        + [  # DBInstance comparison
            # different value
            "$..AllocatedStorage",  # expected 20 for this config
            "$..StorageType",
            "$..AvailabilityZone",  # not yet available on AWS? added in LS
        ]
        + SKIP_VERIFY_DB_CLUSTER_POSTGRES
    )
    def test_create_aurora_v2_cluster(self, rds_create_db_cluster, snapshot, aws_client):
        snapshot.add_transformer(snapshot.transform.rds_api(), priority=2)

        snapshot.add_transformer(
            snapshot.transform.key_value("Endpoint", reference_replacement=False)
        )
        snapshot.add_transformer(
            snapshot.transform.key_value(
                "Port", value_replacement="<port>", reference_replacement=False
            )
        )
        region = aws_client.sts.meta.region_name
        snapshot.add_transformer(
            get_availability_zones_transformer(region),
            priority=-1,
        )
        snapshot.add_transformer(
            get_availability_zone_transformer(region),
            priority=-1,
        )
        db_cluster_id = f"rds-cluster-{short_uid()}"
        db_instance_id = f"rds-inst-{short_uid()}"
        db_type = "aurora-postgresql"
        instance_class = "db.t3.large"
        rds_create_db_cluster(
            DBClusterIdentifier=db_cluster_id,
            Engine=db_type,
            DatabaseName=db_name,
            EngineVersion="13.7",
        )
        result = aws_client.rds.describe_db_clusters(DBClusterIdentifier=db_cluster_id)
        snapshot.match("describe-db-cluster-1", result)

        result = aws_client.rds.describe_db_cluster_endpoints(DBClusterIdentifier=db_cluster_id)
        snapshot.match("describe-db-cluster-endpoints", result)

        # try to set different engine
        with pytest.raises(ClientError) as ctx:
            aws_client.rds.create_db_instance(
                DBClusterIdentifier=db_cluster_id,
                DBInstanceIdentifier=db_instance_id,
                Engine="aurora-mysql",
                EngineVersion="13.7",
                DBInstanceClass=instance_class,
            )
        snapshot.match("error-engine", ctx.value)

        # try to set StorageSize
        with pytest.raises(ClientError) as ctx:
            aws_client.rds.create_db_instance(
                DBClusterIdentifier=db_cluster_id,
                DBInstanceIdentifier=db_instance_id,
                EngineVersion="13.7",
                Engine=db_type,
                AllocatedStorage=20,
                DBInstanceClass=instance_class,
            )
        snapshot.match("error-storage-size", ctx.value)

        # try to set different db name
        with pytest.raises(ClientError) as ctx:
            aws_client.rds.create_db_instance(
                DBClusterIdentifier=db_cluster_id,
                DBInstanceIdentifier=db_instance_id,
                Engine=db_type,
                EngineVersion="13.7",
                DBInstanceClass=instance_class,
                DBName="hello",
            )
        snapshot.match("error-dbname", ctx.value)

        # try to set different master username
        with pytest.raises(ClientError) as ctx:
            aws_client.rds.create_db_instance(
                DBClusterIdentifier=db_cluster_id,
                DBInstanceIdentifier=db_instance_id,
                Engine=db_type,
                EngineVersion="13.7",
                DBInstanceClass=instance_class,
                MasterUsername="hello",
            )
        snapshot.match("error-master-user", ctx.value)

        # try to set different master user password
        with pytest.raises(ClientError) as ctx:
            aws_client.rds.create_db_instance(
                DBClusterIdentifier=db_cluster_id,
                DBInstanceIdentifier=db_instance_id,
                Engine=db_type,
                EngineVersion="13.7",
                DBInstanceClass=instance_class,
                MasterUserPassword="hello",
            )
        snapshot.match("error-master-user-password", ctx.value)

        # create instance with valid values
        try:
            aws_client.rds.create_db_instance(
                DBClusterIdentifier=db_cluster_id,
                DBInstanceIdentifier=db_instance_id,
                Engine="aurora-postgresql",
                EngineVersion="13.7",
                DBInstanceClass=instance_class,
            )
            wait_until_db_available(aws_client.rds, instance_id=db_instance_id)
            result = aws_client.rds.describe_db_clusters(DBClusterIdentifier=db_cluster_id)
            snapshot.match("describe-db-cluster", result)
            result = aws_client.rds.describe_db_instances(DBInstanceIdentifier=db_instance_id)
            snapshot.match("describe-db-instances", result)
            result = aws_client.rds.describe_db_cluster_endpoints(DBClusterIdentifier=db_cluster_id)
            snapshot.match("describe-db-cluster-endpoints-2", result)
        finally:
            aws_client.rds.delete_db_instance(
                DBInstanceIdentifier=db_instance_id, SkipFinalSnapshot=True
            )

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(
        paths=SKIP_VERIFY_DB_INSTANCE_POSTGRES
        + [  # DBInstance comparison
            # different value
            "$..AllocatedStorage",
            "$..DBParameterGroups",
            "$..StorageType",
            "$..EngineVersion",  # defaults to 11.16
            "$..AvailabilityZone",  # different value
            "$..PromotionTier",  # missing
            "$..StorageThroughput",  # missing
            "$..CertificateDetails",  # missing
            "$..delete_db_cluster.DBCluster.DBClusterMembers",  # on AWS it is still available, but in status "deleting"
            "$..delete_db_cluster.DBCluster.Status",  # on AWS it is still available, but LS is faster
        ]
        + SKIP_VERIFY_DB_CLUSTER_POSTGRES
    )
    def test_create_aurora_v2_cluster_delete_instances(
        self, rds_create_db_instance, rds_create_db_cluster, snapshot, aws_client
    ):
        snapshot.add_transformer(snapshot.transform.rds_api())
        snapshot.add_transformer(
            snapshot.transform.key_value("ReaderEndpoint", reference_replacement=False)
        )
        snapshot.add_transformer(
            snapshot.transform.key_value("Endpoint", reference_replacement=False)
        )
        db_cluster_id = f"rds-cluster-{short_uid()}"
        db_instance_id = f"rds-inst-{short_uid()}"
        db_type = "aurora-postgresql"
        instance_class = "db.t3.large"
        rds_create_db_cluster(
            DBClusterIdentifier=db_cluster_id,
            Engine=db_type,
            DatabaseName=db_name,
        )
        rds_create_db_instance(
            DBClusterIdentifier=db_cluster_id,
            DBInstanceIdentifier=db_instance_id,
            Engine="aurora-postgresql",
            DBInstanceClass=instance_class,
        )
        result = aws_client.rds.describe_db_instances(DBInstanceIdentifier=db_instance_id)
        snapshot.match("describe-db-instances", result)

        # try to delete cluster -> expect to fail because we still have instances
        with pytest.raises(ClientError) as ctx:
            aws_client.rds.delete_db_cluster(
                DBClusterIdentifier=db_cluster_id, SkipFinalSnapshot=True
            )

        snapshot.match("error-delete_db_cluster", ctx.value)

        # delete instance
        result = aws_client.rds.delete_db_instance(
            DBInstanceIdentifier=db_instance_id, SkipFinalSnapshot=True
        )
        snapshot.match("delete_db_instance", result)

        # delete cluster
        result = aws_client.rds.delete_db_cluster(
            DBClusterIdentifier=db_cluster_id, SkipFinalSnapshot=True
        )
        snapshot.match("delete_db_cluster", result)

    @markers.aws.validated
    def test_describe_db_cluster_not_existent(self, snapshot, aws_client):
        non_existent_id = "fake-db-cluster-id"

        with pytest.raises(Exception) as exc:
            aws_client.rds.describe_db_clusters(DBClusterIdentifier=non_existent_id)

        snapshot.match("describe-db-clusters-with-cluster-id", exc.value.response)

    @markers.aws.unknown
    def test_create_aurora_postgres(
        self, rds_create_db_instance, rds_create_db_cluster, aws_client
    ):
        db_type = "aurora-postgresql"
        db_id = f"rds-{short_uid()}"

        cluster_result = rds_create_db_cluster(
            DBClusterIdentifier=db_id, Engine=db_type, DatabaseName=db_name
        )

        result = rds_create_db_instance(
            DBClusterIdentifier=db_id, Engine=db_type, DBInstanceClass="db.m3.large"
        )

        port = result["Endpoint"]["Port"]
        assert port == cluster_result["Port"]
        self._create_table_and_select(db_type, port)

        parameter_group = cluster_result["DBClusterParameterGroup"]
        assert parameter_group.startswith("default.aurora-postgresql")

        result = aws_client.rds.describe_db_cluster_parameter_groups()
        groups = result.get("DBClusterParameterGroups", [])
        assert groups
        assert parameter_group in [tmp["DBClusterParameterGroupName"] for tmp in groups]

    @markers.aws.unknown
    def test_create_aurora_postgres_instance(self, rds_create_db_instance, aws_client):
        db_type = "aurora-postgresql"
        result = self._create_db_instance_wait_for_ready(db_type, rds_create_db_instance)
        port = result["Endpoint"]["Port"]
        assert result["EngineVersion"] == POSTGRES_DEFAULT_VERSION
        self._create_table_and_select(db_type, port)

        db_group_name = result["DBParameterGroups"][0]["DBParameterGroupName"]
        assert db_group_name.startswith("default.aurora-postgresql")

        result = aws_client.rds.describe_db_parameter_groups()
        groups = result.get("DBParameterGroups", [])
        assert groups
        assert db_group_name in [tmp["DBParameterGroupName"] for tmp in groups]

    @markers.aws.unknown
    def test_db_cluster_scaling(self, rds_create_db_cluster, aws_client):
        cluster_id = f"c-{short_uid()}"
        result = rds_create_db_cluster(
            DBClusterIdentifier=cluster_id,
            Engine="aurora-postgresql",
            ScalingConfiguration={"MinCapacity": 1, "MaxCapacity": 4},
        )
        assert result["DBClusterIdentifier"] == cluster_id
        result = aws_client.rds.describe_db_clusters(DBClusterIdentifier=cluster_id)["DBClusters"]
        result = [c for c in result if c["DBClusterIdentifier"] == cluster_id]
        assert len(result) == 1

    @markers.aws.unknown
    def test_db_proxies(self, rds_create_db_cluster, rds_create_db_proxy, aws_client):
        cluster_id = f"c-{short_uid()}"
        result = rds_create_db_cluster(DBClusterIdentifier=cluster_id, Engine="aurora-postgresql")
        assert result["DBClusterIdentifier"] == cluster_id
        db_port = result["Port"]

        # create DB proxy
        proxy_name = f"p-{short_uid()}"
        # AWS automatically creates a target group named `default`, no way to create one yourself for now
        default_target_group_name = "default"
        proxy_tags = [{"Key": "tag_key", "Value": "rds-proxy"}]
        response = rds_create_db_proxy(
            DBProxyName=proxy_name,
            EngineFamily="POSTGRESQL",
            Auth=[{"UserName": "test", "SecretArn": "secret123"}],
            RoleArn="r1",
            VpcSubnetIds=["s1"],
            Tags=proxy_tags,
        )["DBProxy"]
        assert response["DBProxyName"] == proxy_name
        assert "DBProxyArn" in response
        assert response["Status"], "available"

        # verify that tags are kept for proxy resources
        tags_for_proxy = aws_client.rds.list_tags_for_resource(ResourceName=response["DBProxyArn"])
        assert tags_for_proxy["TagList"] == proxy_tags

        # describe default proxy target group, check its automatic creation
        target_group = aws_client.rds.describe_db_proxy_target_groups(
            DBProxyName=proxy_name, TargetGroupName=default_target_group_name
        )["TargetGroups"]
        assert len(target_group) == 1
        assert target_group[0]["DBProxyName"] == proxy_name
        assert target_group[0]["Status"] == "available"
        assert target_group[0]["TargetGroupName"] == "default"
        # test if the default values are set
        assert target_group[0]["ConnectionPoolConfig"]["MaxConnectionsPercent"] == 100
        assert target_group[0]["ConnectionPoolConfig"]["MaxIdleConnectionsPercent"] == 50

        # register proxy targets
        response = aws_client.rds.register_db_proxy_targets(
            DBProxyName=proxy_name,
            TargetGroupName=default_target_group_name,
            DBClusterIdentifiers=[cluster_id],
        )
        targets = response["DBProxyTargets"]
        assert len(targets) == 1
        assert targets[0]["RdsResourceId"] == cluster_id
        assert targets[0]["Type"] == "RDS_SERVERLESS_ENDPOINT"

        # describe proxy targets
        targets = aws_client.rds.describe_db_proxy_targets(
            DBProxyName=proxy_name, TargetGroupName=default_target_group_name
        )["Targets"]
        assert len(targets) == 1
        assert targets[0]["RdsResourceId"] == cluster_id
        assert targets[0]["Type"] == "RDS_SERVERLESS_ENDPOINT"
        # for now, we assume that the proxy simply has the same endpoint as the actual DB
        assert targets[0]["Port"] == db_port
        proxies = aws_client.rds.describe_db_proxies(DBProxyName=proxy_name)["DBProxies"]
        assert proxies[0]["Endpoint"] == f"localhost.localstack.cloud:{db_port}"

        # modify proxy target group
        response = aws_client.rds.modify_db_proxy_target_group(
            DBProxyName=proxy_name,
            TargetGroupName=default_target_group_name,
            ConnectionPoolConfig={"MaxConnectionsPercent": 99},
        )
        assert response["ResponseMetadata"]["HTTPStatusCode"] == 200
        assert response["DBProxyTargetGroup"]["ConnectionPoolConfig"]["MaxConnectionsPercent"] == 99
        # check other parameters are still present and the same
        assert (
            response["DBProxyTargetGroup"]["ConnectionPoolConfig"]["MaxIdleConnectionsPercent"]
            == 50
        )

        # check modification of proxy target group
        target_group = aws_client.rds.describe_db_proxy_target_groups(
            DBProxyName=proxy_name, TargetGroupName=default_target_group_name
        )["TargetGroups"]
        assert target_group[0]["ConnectionPoolConfig"]["MaxConnectionsPercent"] == 99
        assert target_group[0]["ConnectionPoolConfig"]["MaxIdleConnectionsPercent"] == 50

        # deregister proxy targets
        response = aws_client.rds.deregister_db_proxy_targets(
            DBProxyName=proxy_name,
            TargetGroupName=default_target_group_name,
            DBClusterIdentifiers=[cluster_id],
        )
        assert response["ResponseMetadata"]["HTTPStatusCode"] == 200

        targets = aws_client.rds.describe_db_proxy_targets(
            DBProxyName=proxy_name, TargetGroupName=default_target_group_name
        )["Targets"]
        assert len(targets) == 0

        # try to deregister again
        with pytest.raises(Exception) as ctx:
            aws_client.rds.deregister_db_proxy_targets(
                DBProxyName=proxy_name,
                TargetGroupName=default_target_group_name,
                DBClusterIdentifiers=[cluster_id],
            )
            assert "DBProxyTargetNotFoundFault" in ctx.value

        # try with wrong parameters
        with pytest.raises(Exception) as ctx:
            aws_client.rds.register_db_proxy_targets(
                DBProxyName=proxy_name,
                TargetGroupName=default_target_group_name,
                DBClusterIdentifiers=[cluster_id],
                DBInstanceIdentifiers=[cluster_id],
            )
            assert "InvalidParameterCombination" in ctx.value
            assert (
                "Must specify either DB instance identifier or DB cluster identifier, not both."
                in ctx.value
            )
        with pytest.raises(Exception) as ctx:
            aws_client.rds.register_db_proxy_targets(
                DBProxyName=proxy_name,
                TargetGroupName=default_target_group_name,
                DBClusterIdentifiers=[cluster_id, cluster_id],
            )
            assert "InvalidParameterValue" in ctx.value
            assert "Only one DB cluster is supported but 2 clusters are provided" in ctx.value

    @markers.aws.validated
    def test_add_role_to_db_instance(
        self,
        rds_create_db_instance,
        create_iam_role_s3_access_lambda_invoke_for_db,
        aws_client,
        snapshot,
    ):
        # create DB instance
        db_id = f"rds-{short_uid()}"
        instance = self._create_db_instance_wait_for_ready(
            "postgres", rds_create_db_instance, db_id=db_id
        )
        snapshot.add_transformer(snapshot.transform.regex(db_id, "<db-id>"))
        # add role to instance
        feature_name = "s3Import"
        role = create_iam_role_s3_access_lambda_invoke_for_db(source_arn=instance["DBInstanceArn"])
        _add_role_to_db_instance(aws_client.rds, db_id, feature_name, role)
        snapshot.add_transformer(snapshot.transform.regex(role.split("role/")[-1], "<role-name>"))

        # assert role is present
        result = aws_client.rds.describe_db_instances(DBInstanceIdentifier=db_id)["DBInstances"]
        snapshot.match("associated-roles", result[0]["AssociatedRoles"])

        # assert role cannot be added twice
        with pytest.raises(ClientError) as exc:
            aws_client.rds.add_role_to_db_instance(
                DBInstanceIdentifier=db_id,
                FeatureName=feature_name,
                RoleArn=role,
            )
        snapshot.match("error-1", exc.value.response)
        # remove role from instance
        aws_client.rds.remove_role_from_db_instance(
            DBInstanceIdentifier=db_id, RoleArn=role, FeatureName=feature_name
        )

        # assert role is no longer present (can take some time)
        def _role_removed():
            result = aws_client.rds.describe_db_instances(DBInstanceIdentifier=db_id)["DBInstances"]
            assert not result[0].get("AssociatedRoles")

        retry(_role_removed, retries=30, sleep=2)

        # assert deleted role cannot be deleted again
        with pytest.raises(ClientError) as exc:
            aws_client.rds.remove_role_from_db_instance(
                DBInstanceIdentifier=db_id, RoleArn=role, FeatureName=feature_name
            )
        snapshot.match("error-2", exc.value.response)

    @markers.aws.validated
    def test_add_role_to_db_cluster(
        self,
        rds_create_db_cluster,
        create_iam_role_s3_access_lambda_invoke_for_db,
        aws_client,
        snapshot,
    ):
        # create DB cluster
        cluster_id = f"rds-{short_uid()}"
        cluster = rds_create_db_cluster(DBClusterIdentifier=cluster_id, Engine="aurora-postgresql")
        snapshot.add_transformer(snapshot.transform.regex(cluster_id, "<db-id>"))
        # add role to cluster
        feature_name = "s3Export"
        role = create_iam_role_s3_access_lambda_invoke_for_db(source_arn=cluster["DBClusterArn"])
        _add_role_to_db_cluster(aws_client.rds, cluster_id, feature_name, role)
        snapshot.add_transformer(snapshot.transform.regex(role.split("role/")[-1], "<role-name>"))

        # assert role is present
        result = aws_client.rds.describe_db_clusters(DBClusterIdentifier=cluster_id)["DBClusters"]
        snapshot.match("associated-roles", result[0]["AssociatedRoles"])

        # assert role cannot be added twice
        with pytest.raises(ClientError) as exc:
            aws_client.rds.add_role_to_db_cluster(
                DBClusterIdentifier=cluster_id, RoleArn=role, FeatureName=feature_name
            )
        snapshot.match("error-1", exc.value.response)

        # remove role from instance
        aws_client.rds.remove_role_from_db_cluster(
            DBClusterIdentifier=cluster_id, RoleArn=role, FeatureName=feature_name
        )

        # assert role is no longer present (can take some time)
        def _role_removed():
            result = aws_client.rds.describe_db_clusters(DBClusterIdentifier=cluster_id)[
                "DBClusters"
            ]
            assert not result[0].get("AssociatedRoles")

        retry(_role_removed, retries=30, sleep=2)

        # assert deleted role cannot be deleted again
        with pytest.raises(ClientError) as exc:
            aws_client.rds.remove_role_from_db_cluster(
                DBClusterIdentifier=cluster_id, RoleArn=role, FeatureName=feature_name
            )
        snapshot.match("error-2", exc.value.response)

    @markers.aws.unknown
    def test_modify_db_cluster(self, rds_create_db_cluster, aws_client):
        cluster_id = f"rds-{short_uid()}"
        engine = "aurora-postgresql"
        log_exports = ["test"]
        initial_tags = [{"Key": "hello", "Value": "world"}]
        rds_create_db_cluster(
            DBClusterIdentifier=cluster_id,
            Engine=engine,
            DatabaseName=db_name,
            EnableCloudwatchLogsExports=log_exports,
            EnableHttpEndpoint=True,
            Tags=initial_tags,
        )
        result = aws_client.rds.describe_db_clusters(DBClusterIdentifier=cluster_id)["DBClusters"]
        assert 1 == len(result)
        assert log_exports == result[0].get("EnabledCloudwatchLogsExports")
        assert result[0].get("HttpEndpointEnabled") is True
        assert result[0].get("TagList") == initial_tags
        arn = result[0].get("DBClusterArn")

        with pytest.raises(Exception) as ctx:
            aws_client.rds.modify_db_cluster(DBClusterIdentifier="id_does_not_exist")
        assert "not found" in str(ctx.value)

        result = aws_client.rds.modify_db_cluster(
            DBClusterIdentifier=cluster_id, EnableHttpEndpoint=False
        )
        assert log_exports == result["DBCluster"].get("EnabledCloudwatchLogsExports")
        assert not result["DBCluster"].get("HttpEndpointEnabled")

        result = aws_client.rds.describe_db_clusters(DBClusterIdentifier=cluster_id)["DBClusters"]
        assert 1 == len(result)
        assert log_exports == result[0].get("EnabledCloudwatchLogsExports")
        assert not result[0].get("HttpEndpointEnabled")

        # add and remove tags
        result = aws_client.rds.list_tags_for_resource(ResourceName=arn)
        assert result["TagList"] == initial_tags

        aws_client.rds.remove_tags_from_resource(ResourceName=arn, TagKeys=["hello"])
        result = aws_client.rds.list_tags_for_resource(ResourceName=arn)
        assert result["TagList"] == []
        result = aws_client.rds.describe_db_clusters(DBClusterIdentifier=cluster_id)["DBClusters"]
        assert result[0].get("TagList") == []

        new_tags = [
            {"Key": "my-first-key", "Value": "hey"},
            {"Key": "my-second-key", "Value": "there"},
        ]
        aws_client.rds.add_tags_to_resource(ResourceName=arn, Tags=new_tags)
        result = aws_client.rds.list_tags_for_resource(ResourceName=arn)
        assert result["TagList"] == new_tags
        result = aws_client.rds.describe_db_clusters(DBClusterIdentifier=cluster_id)["DBClusters"]
        assert result[0].get("TagList") == new_tags

    @markers.aws.validated
    def test_db_cluster_endpoints(
        self, rds_create_db_cluster, rds_create_db_cluster_endpoint, aws_client
    ):
        cluster_id = f"rds-{short_uid()}"
        endpoint_identifier = f"endpoint-{short_uid()}"
        endpoint_type = "READER"
        static_members = []
        version = "10.18"
        rds_create_db_cluster(
            DBClusterIdentifier=cluster_id,
            Engine="aurora-postgresql",
            EngineVersion=version,
            DatabaseName=db_name,
        )

        with pytest.raises(Exception) as exc:
            aws_client.rds.modify_db_cluster_endpoint(
                DBClusterEndpointIdentifier=endpoint_identifier, EndpointType=endpoint_type
            )
        exc.match("DBClusterEndpointNotFoundFault")
        exc.match(f"DBClusterEndpoint {endpoint_identifier} not found")

        initial_tags = [{"Key": "hello", "Value": "world"}]
        rds_create_db_cluster_endpoint(
            DBClusterEndpointIdentifier=endpoint_identifier,
            DBClusterIdentifier=cluster_id,
            EndpointType=endpoint_type,
            StaticMembers=static_members,
            Tags=initial_tags,
        )
        result = aws_client.rds.describe_db_cluster_endpoints(
            DBClusterEndpointIdentifier=endpoint_identifier
        )["DBClusterEndpoints"]
        assert 1 == len(result)
        arn = result[0].get("DBClusterEndpointArn")

        assert result[0].get("DBClusterEndpointIdentifier") == endpoint_identifier
        assert result[0].get("DBClusterIdentifier") == cluster_id
        assert result[0].get("DBClusterEndpointArn")
        assert result[0].get("EndpointType") == "CUSTOM"
        assert result[0].get("CustomEndpointType") == endpoint_type
        assert result[0].get("StaticMembers") == static_members
        assert not result[0].get("ExcludedMembers")

        result = aws_client.rds.list_tags_for_resource(ResourceName=arn)
        assert result["TagList"] == initial_tags

        new_static_members = ["hello"]
        excluded_members = ["unknown"]
        with pytest.raises(Exception) as exc:
            aws_client.rds.modify_db_cluster_endpoint(
                DBClusterEndpointIdentifier=endpoint_identifier,
                StaticMembers=new_static_members,
                ExcludedMembers=excluded_members,
            )
        exc.match("InvalidParameterValue")
        exc.match("You can't specify both static and excluded members")

        aws_client.rds.modify_db_cluster_endpoint(
            DBClusterEndpointIdentifier=endpoint_identifier, ExcludedMembers=[]
        )
        result = aws_client.rds.describe_db_cluster_endpoints(
            DBClusterEndpointIdentifier=endpoint_identifier
        )["DBClusterEndpoints"]
        assert 1 == len(result)
        assert result[0].get("DBClusterEndpointIdentifier") == endpoint_identifier
        assert result[0].get("DBClusterIdentifier") == cluster_id
        assert result[0].get("EndpointType") == "CUSTOM"
        assert result[0].get("CustomEndpointType") == endpoint_type
        assert result[0].get("ExcludedMembers") == []
        assert result[0].get("DBClusterEndpointArn")

        # add and remove tags
        aws_client.rds.remove_tags_from_resource(ResourceName=arn, TagKeys=["hello"])
        result = aws_client.rds.list_tags_for_resource(ResourceName=arn)
        assert result["TagList"] == []

        new_tags = [
            {"Key": "my-first-key", "Value": "hey"},
            {"Key": "my-second-key", "Value": "there"},
        ]
        aws_client.rds.add_tags_to_resource(ResourceName=arn, Tags=new_tags)
        result = aws_client.rds.list_tags_for_resource(ResourceName=arn)
        assert result["TagList"] == new_tags

        # todo assert return is same cluster
        aws_client.rds.delete_db_cluster_endpoint(DBClusterEndpointIdentifier=endpoint_identifier)

        def assert_deleted():
            result = aws_client.rds.describe_db_cluster_endpoints(
                DBClusterEndpointIdentifier=endpoint_identifier
            )
            assert len(result["DBClusterEndpoints"]) == 0

        retry(assert_deleted, sleep=1, retries=90)

    @markers.aws.validated
    def test_invalid_cluster_identifier(self, rds_create_db_cluster):
        cluster_id = "invalid_rds_id_with_underscores"
        with pytest.raises(Exception) as exc:
            rds_create_db_cluster(
                DBClusterIdentifier=cluster_id,
                Engine="postgres",
                EngineVersion="10.18",
                DatabaseName=db_name,
            )
        exc.match("DBClusterIdentifier is not a valid identifier")

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(
        paths=[
            # missing:
            "$..ActivityStreamStatus",
            "$..AssociatedRoles",
            "$..AutoMinorVersionUpgrade",
            "$..AvailabilityZones",
            "$..BackupRetentionPeriod",
            "$..Capacity",
            "$..ClusterCreateTime",
            "$..CopyTagsToSnapshot",
            "$..CrossAccountClone",
            "$..DBSubnetGroup",
            "$..DeletionProtection",
            "$..DomainMemberships",
            "$..EarliestRestorableTime",
            "$..HostedZoneId",
            "$..HttpEndpointEnabled",
            "$..KmsKeyId",
            "$..LatestRestorableTime",
            "$..NetworkType",
            "$..PreferredBackupWindow",
            "$..PreferredMaintenanceWindow",
            "$..ReadReplicaIdentifiers",
            "$..ScalingConfigurationInfo",
            # different value
            "$..DBClusterParameterGroup",  # expected: default.aurora-postgresql13
            "$..StorageEncrypted",  # expected: True
            # added in LS:
            "$..DatabaseName",
        ]
    )
    def test_serverless_no_custom_cluster_endpoint(
        self, rds_create_db_cluster, rds_create_db_cluster_endpoint, aws_client, snapshot
    ):
        snapshot.add_transformer(snapshot.transform.rds_api())
        snapshot.add_transformer(snapshot.transform.key_value("Endpoint"), priority=-1)
        snapshot.add_transformer(
            snapshot.transform.key_value(
                "Port", value_replacement="<port>", reference_replacement=False
            )
        )
        region = aws_client.sts.meta.region_name

        snapshot.add_transformer(
            get_availability_zones_transformer(region),
            priority=-1,
        )
        cluster_id = f"rds-{short_uid()}"
        rds_create_db_cluster(
            DBClusterIdentifier=cluster_id,
            Engine="aurora-postgresql",
            EngineVersion="13.9",
            EngineMode="serverless",
        )
        describe = aws_client.rds.describe_db_clusters(DBClusterIdentifier=cluster_id)
        snapshot.match("describe-serverless-v1-cluster", describe)

        describe_endpoints = aws_client.rds.describe_db_cluster_endpoints(
            DBClusterIdentifier=cluster_id
        )
        snapshot.match("describe-db-cluster-endpoints", describe_endpoints)

        with pytest.raises(Exception) as exc:
            rds_create_db_cluster_endpoint(
                DBClusterEndpointIdentifier=f"endpoint-{short_uid()}",
                DBClusterIdentifier=cluster_id,
                EndpointType="READER",
            )
        exc.match("InvalidParameterValue")
        exc.match("Feature not supported by the cluster mode")
        snapshot.match("invalid_create_db_cluster_endpoint", exc.value.response)

    @markers.aws.unknown
    def test_modify_db_instance_with_db_parameter_group(
        self, rds_create_db_parameter_group, rds_create_db_instance, aws_client
    ):
        db_result = self._create_db_instance_wait_for_ready("postgres", rds_create_db_instance)
        port = db_result["Endpoint"]["Port"]
        db_id = db_result["DBInstanceIdentifier"]
        group_name = "testing-postgres"
        group_family = "postgres-11"
        description = "testing config for postgres"

        rds_create_db_parameter_group(
            DBParameterGroupName=group_name,
            DBParameterGroupFamily=group_family,
            Description=description,
        )

        db_parameter_group = aws_client.rds.describe_db_parameter_groups(
            DBParameterGroupName=group_name
        )
        assert db_parameter_group["DBParameterGroups"][0]["DBParameterGroupName"] == group_name
        assert db_parameter_group["DBParameterGroups"][0]["DBParameterGroupFamily"] == group_family
        assert db_parameter_group["DBParameterGroups"][0]["Description"] == description

        response = self.query_postgres(port, "SHOW max_connections;")
        old_max_conn = int(response[0])
        new_max_conn = old_max_conn + 1
        parameters = [
            {
                "ParameterName": "max_connections",
                "ParameterValue": str(new_max_conn),
                "ApplyMethod": "immediate",
            }
        ]
        aws_client.rds.modify_db_parameter_group(
            DBParameterGroupName=group_name, Parameters=parameters
        )

        aws_client.rds.modify_db_instance(
            DBInstanceIdentifier=db_id, DBParameterGroupName=group_name, ApplyImmediately=True
        )
        response = aws_client.rds.describe_db_instances(DBInstanceIdentifier=db_id)
        instance = response["DBInstances"][0]
        assert instance.get("DBParameterGroups")[0].get("DBParameterGroupName") == group_name
        wait_until_db_available(aws_client.rds, instance_id=db_id)
        response = self.query_postgres(port, "SHOW max_connections;")
        assert new_max_conn == int(response[0])

    @markers.aws.unknown
    def test_query_from_s3(self, rds_create_db_instance, aws_client):
        db_id = f"s3-query-{short_uid()}"
        result = self._create_db_instance_wait_for_ready(
            "postgres", rds_create_db_instance, db_id=db_id
        )
        port = result["Endpoint"]["Port"]

        # upload test file to S3
        bucket_name = f"rds-{short_uid()}"
        key = "my/test/file.csv"
        resources.create_s3_bucket(bucket_name, s3_client=aws_client.s3)
        aws_client.s3.upload_fileobj(io.BytesIO(to_bytes(TEST_CSV.strip())), bucket_name, key)

        table_name = f"test{short_uid()}"
        query = """
            CREATE TABLE {table} (id integer, value text);
            COPY {table} from 's3://{b}/{k}'
        """.format(table=table_name, b=bucket_name, k=key)
        self.query_postgres(port, query, results=False)
        result = self.query_postgres(port, f"SELECT * FROM {table_name}")
        assert result == [
            {"id": 1, "value": "value 1"},
            {"id": 2, "value": "value 2"},
            {"id": 3, "value": "value 3"},
        ]

    @markers.aws.unknown
    def test_create_snapshot_cluster(
        self, rds_create_db_cluster, rds_restore_db_cluster_from_snapshot, aws_client
    ):
        # create DB instance/cluster
        db_id = f"rds-snap0-{short_uid()}"
        engine = "postgres"
        result = rds_create_db_cluster(
            DBClusterIdentifier=db_id, Engine=engine, DatabaseName=db_name
        )
        port = result["Port"]

        # create snapshot with sample data
        table_name = self._insert_sample_data(port)
        snapshot_id = f"rds-snap-{short_uid()}"
        cluster_snapshot = aws_client.rds.create_db_cluster_snapshot(
            DBClusterSnapshotIdentifier=snapshot_id, DBClusterIdentifier=db_id
        )

        cluster_snapshots = aws_client.rds.describe_db_cluster_snapshots(
            DBClusterSnapshotIdentifier=snapshot_id
        )
        assert cluster_snapshot["DBClusterSnapshot"] == cluster_snapshots["DBClusterSnapshots"][0]

        # restore snapshot into new DB cluster
        db_id_new = f"rds-snap1-{short_uid()}"
        result = rds_restore_db_cluster_from_snapshot(
            DBClusterIdentifier=db_id_new,
            SnapshotIdentifier=snapshot_id,
            Engine=engine,
        )
        assert "DBCluster" in result
        assert result["DBCluster"]["Engine"] == engine
        port_new = result["DBCluster"]["Port"]
        self._assert_sample_data_exists(port_new, table_name)

        deleted_cluster_snapshot = aws_client.rds.delete_db_cluster_snapshot(
            DBClusterSnapshotIdentifier=snapshot_id
        )
        assert (
            deleted_cluster_snapshot["DBClusterSnapshot"] == cluster_snapshot["DBClusterSnapshot"]
        )
        cluster_snapshots = aws_client.rds.describe_db_cluster_snapshots(
            DBClusterSnapshotIdentifier=snapshot_id
        )
        assert len(cluster_snapshots["DBClusterSnapshots"]) == 0

    @markers.aws.unknown
    def test_create_snapshot_instance(
        self, rds_create_db_instance, rds_restore_db_instance_from_snapshot, aws_client
    ):
        db_id = f"rds-snap0-{short_uid()}"
        result = self._create_db_instance_wait_for_ready(
            "postgres", rds_create_db_instance, db_id=db_id
        )
        port = result["Endpoint"]["Port"]

        # create snapshot with sample data
        table_name = self._insert_sample_data(port)
        snapshot_id = f"rds-snap-{short_uid()}"
        db_snapshot = aws_client.rds.create_db_snapshot(
            DBSnapshotIdentifier=snapshot_id, DBInstanceIdentifier=db_id
        )
        assert db_snapshot["DBSnapshot"]["DBSnapshotIdentifier"] == snapshot_id
        assert db_snapshot["DBSnapshot"]["DBInstanceIdentifier"] == db_id
        assert db_snapshot["DBSnapshot"]["Status"] == "available"

        # restore snapshot into new DB instance
        db_id_new = f"rds-snap1-{short_uid()}"
        result = rds_restore_db_instance_from_snapshot(
            DBInstanceIdentifier=db_id_new,
            DBSnapshotIdentifier=snapshot_id,
            DBInstanceClass="c2",
        )["DBInstance"]
        assert result["Engine"] == "postgres"
        port_new = result["Endpoint"]["Port"]

        self._assert_sample_data_exists(port_new, table_name)

    @pytest.mark.parametrize("pg_version", ["11.15", "12.9", "13.4"])
    @markers.aws.only_localstack
    def test_postgres_versions(self, rds_create_db_cluster, pg_version, monkeypatch):
        monkeypatch.setattr(ext_config, "RDS_PG_CUSTOM_VERSIONS", True)
        db_id = f"rds-{short_uid()}"
        engine = "postgres"
        result = rds_create_db_cluster(
            DBClusterIdentifier=db_id, Engine=engine, EngineVersion=pg_version, DatabaseName=db_name
        )

        # check version of deployed instance
        port = result["Port"]
        result = self.query_postgres(port, "SELECT version()")
        assert result
        version_str = result[0]
        major_version = pg_version.split(".")[0]
        assert f"postgresql {major_version}" in version_str.lower()

    @markers.aws.unknown
    def test_postgres_db_parametergroup_named_default(self, rds_create_db_instance, aws_client):
        result = rds_create_db_instance(
            DBInstanceClass="db.large",
            Engine="postgres",
            Port=12345,
            DBParameterGroupName="default.postgres.my-custom.11",
        )

        db_group_name = result["DBParameterGroups"][0]["DBParameterGroupName"]
        assert db_group_name == "default.postgres.my-custom.11"

        result = aws_client.rds.describe_db_parameter_groups()
        groups = result.get("DBParameterGroups", [])
        assert groups
        assert db_group_name in [tmp["DBParameterGroupName"] for tmp in groups]

    @markers.aws.validated
    def test_create_db_cluster_with_invalid_engine(self, aws_client):
        with pytest.raises(ClientError) as e:
            aws_client.rds.create_db_cluster(
                DBClusterIdentifier=f"rds-cluster-{short_uid()}", Engine="garbage"
            )

        assert e.match("InvalidParameterValue")
        assert e.match("Invalid DB engine")

    @markers.aws.validated
    # TODO: currently lots of parity issues, especially for the snapshot result of describe_db_instances(). To be fixed!
    @markers.snapshot.skip_snapshot_verify
    def test_generate_db_auth_token(self, create_db_instance_with_iam_auth, snapshot, aws_client):
        snapshot.add_transformer(snapshot.transform.rds_api())
        snapshot.add_transformer(
            snapshot.transform.key_value("Endpoint", reference_replacement=False)
        )
        # create the DB with the `GRANT rds_iam TO iam_user` call wrapped in a transaction in a code block, as we have
        # another test for the default user case
        result = create_db_instance_with_iam_auth(with_block=True)
        snapshot.match("db-instance", result)
        db_id = result["DBInstanceIdentifier"]
        hostname = result["Endpoint"]["Address"]
        port = result["Endpoint"]["Port"]

        # generate valid token, assert that query succeeds
        token = aws_client.rds.generate_db_auth_token(
            DBUsername=TEST_IAM_USERNAME, DBHostname=hostname, Port=port
        )
        assert "Signature=" in token
        assert "Action=connect" in token
        assert "DBUser=test" in token
        result = self.query_postgres(
            port,
            "SELECT version()",
            hostname=hostname,
            username=TEST_IAM_USERNAME,
            password=token,
            database=db_name,
        )
        assert "PostgreSQL" in result[0]

        # generate invalid token (for invalid user), assert that query fails
        invalid_token = aws_client.rds.generate_db_auth_token(
            DBUsername="invalid", DBHostname=hostname, Port=port
        )
        with pytest.raises(Exception) as err:
            self.query_postgres(
                port,
                "SELECT version()",
                hostname=hostname,
                password=invalid_token,
                database=db_name,
            )
        err.match("authentication failed")

        # disable authentication, attempt to run query again
        aws_client.rds.modify_db_instance(
            DBInstanceIdentifier=db_id, EnableIAMDatabaseAuthentication=False
        )
        with pytest.raises(Exception) as err:
            self.query_postgres(
                port, "SELECT version()", hostname=hostname, password=token, database=db_name
            )
        err.match("authentication failed")

    @markers.aws.unknown
    def test_iam_db_token_auth_from_lambda(
        self, create_db_instance_with_iam_auth, create_lambda_function, aws_client
    ):
        result = create_db_instance_with_iam_auth()
        hostname = result["Endpoint"]["Address"]
        port = result["Endpoint"]["Port"]

        lambda_code = textwrap.dedent(
            f"""
        import boto3, os
        # apply small patch required for pg8000 import
        from importlib import metadata
        def meta_version(*args): return "1.2.3"
        metadata.version = meta_version
        import pg8000
        def handler(event, context):
            client = boto3.client("rds", endpoint_url=os.getenv("AWS_ENDPOINT_URL"))
            token = client.generate_db_auth_token(DBUsername="{TEST_IAM_USERNAME}", DBHostname="{hostname}", Port={port})
            ls_hostname = os.getenv("LOCALSTACK_HOSTNAME")
            connection = pg8000.connect(
                user="{TEST_IAM_USERNAME}", password=token, database="{db_name}", host=ls_hostname, port={port}
            )
            cursor = connection.cursor()
            cursor.execute("SELECT version(), 123")
            result = list(cursor.fetchall())
            return {{"result": result}}
        """
        )
        func_name = f"test-{short_uid()}"
        create_lambda_function(
            func_name=func_name,
            handler_file=lambda_code,
            libs=["postgres", "psycopg2", "pg8000", "scramp", "asn1crypto"],
        )

        result = aws_client.lambda_.invoke(FunctionName=func_name)
        payload = json.load(result["Payload"])
        result = payload["result"]
        assert result
        result_row = result[0]
        assert "PostgreSQL" in result_row[0]
        assert result_row[1] == 123

    @markers.aws.validated
    def test_reboot_db_instance(self, rds_create_db_instance, aws_client):
        # create DB instance
        db_id = f"rds-{short_uid()}"
        self._create_db_instance_wait_for_ready("postgres", rds_create_db_instance, db_id=db_id)
        aws_client.rds.reboot_db_instance(DBInstanceIdentifier=db_id)
        wait_until_db_available(aws_client.rds, instance_id=db_id)

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(
        paths=SKIP_VERIFY_DB_INSTANCE_POSTGRES
        + [  # DBInstance comparison
            # different value
            "$..AllocatedStorage",
            "$..DBParameterGroups",
            "$..StorageType",
            "$..EngineVersion",  # defaults to 11.16
            "$..AvailabilityZone",  # different value
            "$..PromotionTier",  # missing
            "$..StorageThroughput",  # missing
            "$..CertificateDetails",  # missing
            "$..DedicatedLogVolume",  # missing
            "$.reboot-db-instance.DBInstance.DBInstanceStatus",
            "$..DBInstance.IAMDatabaseAuthenticationEnabled",  # missing
            "$..DBInstance.MultiAZ",  # different value
            "$..DBInstance.OptionGroupMemberships",  # missing
            "$..DBInstance.StorageEncrypted",  # missing
            "$..DBInstance.TagList",  # missing
            "$..DBInstance.DbiResourceId",  # missing
            # on AWS it is still available, but in status "deleting"
        ]
        + SKIP_VERIFY_DB_CLUSTER_POSTGRES
    )
    def test_create_aurora_v2_cluster_reboot_instances(
        self, rds_create_db_instance, rds_create_db_cluster, snapshot, aws_client
    ):
        snapshot.add_transformer(snapshot.transform.rds_api())
        snapshot.add_transformer(
            snapshot.transform.key_value("ReaderEndpoint", reference_replacement=False)
        )
        snapshot.add_transformer(
            snapshot.transform.key_value("Endpoint", reference_replacement=False)
        )
        db_cluster_id = f"rds-cluster-{short_uid()}"
        db_instance_id = f"rds-inst-{short_uid()}"
        db_type = "aurora-postgresql"
        instance_class = "db.t3.large"
        rds_create_db_cluster(
            DBClusterIdentifier=db_cluster_id,
            Engine=db_type,
            DatabaseName=db_name,
        )
        rds_create_db_instance(
            DBClusterIdentifier=db_cluster_id,
            DBInstanceIdentifier=db_instance_id,
            Engine="aurora-postgresql",
            DBInstanceClass=instance_class,
        )
        result = aws_client.rds.describe_db_instances(DBInstanceIdentifier=db_instance_id)
        snapshot.match("describe-db-instances", result)

        result = aws_client.rds.reboot_db_instance(DBInstanceIdentifier=db_instance_id)
        snapshot.match("reboot-db-instance", result)

        wait_until_db_available(aws_client.rds, instance_id=db_instance_id)


@markers.resource_heavy
class TestRdsMysql(TestRDSBase):
    @pytest.mark.parametrize(
        ["use_docker", "engine_version", "expected_actual_engine"],
        [
            (False, "5.7.39", "MariaDB"),
            (True, "8.0.30", "MySQL Community Server"),
        ],
    )
    @markers.aws.unknown
    def test_create_mysql(
        self,
        use_docker,
        engine_version,
        expected_actual_engine,
        rds_create_db_instance,
        monkeypatch,
        aws_client,
    ):
        monkeypatch.setattr(ext_config, "RDS_MYSQL_DOCKER", use_docker)
        db_type = "mysql"
        credentials = "test1234"
        user = "myuser"
        result = self._create_db_instance_wait_for_ready(
            db_type,
            rds_create_db_instance,
            user=user,
            password=credentials,
            EngineVersion=engine_version,
        )
        address = result["Endpoint"]["Address"]

        describe_res = aws_client.rds.describe_db_instances(
            DBInstanceIdentifier=result["DBInstanceIdentifier"]
        )

        describe_address = describe_res["DBInstances"][0]["Endpoint"]["Address"]
        assert address == describe_address == "localhost.localstack.cloud"
        port = result["Endpoint"]["Port"]
        self._create_table_and_select(db_type, port, user=user, password=credentials)

        # test for actual version
        query = (
            "show variables where variable_name = 'version' or variable_name = 'version_comment';"
        )

        version_info = self.query_mysql(port, query, user=user, password=credentials)
        version = [v.get("Value") for v in version_info if v.get("Variable_name") == "version"]
        version_comment = [
            v.get("Value") for v in version_info if v.get("Variable_name") == "version_comment"
        ]

        if use_docker:
            # for MySQL the server name is in the 'version_comment'
            assert engine_version in version
            assert expected_actual_engine in version_comment[0]
        else:
            # for MariaDB the server name is part of the 'version' variable
            assert expected_actual_engine in version[0]

    @markers.snapshot.skip_snapshot_verify(
        paths=[
            # These values are either different or otherwise can't be matched
            "$..DBParameterGroups..DBParameterGroupName",
            "$..Endpoint",
            "$..Port",
            "$..PreferredMaintenanceWindow",  # LS sets the same value for the instance as for the clust
            "$..ReaderEndpoint",
            "$..StatusInfos",
            "$..StorageType",  # We set gp2, aws sets aurora
            "$..StorageEncrypted",
            # This value is included in the localstack response but not in the AWS response
            "$..DatabaseName",
            "$..DbInstancePort",
            "$..DBName",
            "$..EnabledCloudwatchLogsExports",
            # The following values are not included in the Localstack response
            "$..ActivityStreamStatus",
            "$..AssociatedRoles",
            "$..AutoMinorVersionUpgrade",
            "$..AvailabilityZones",
            "$..BackupRetentionPeriod",
            "$..Capacity",
            "$..CopyTagsToSnapshot",
            "$..ClusterCreateTime",
            "$..CrossAccountClone",
            "$..DBSubnetGroup",
            "$..DeletionProtection",
            "$..DomainMemberships",
            "$..EarliestRestorableTime",
            "$..HostedZoneId",
            "$..HttpEndpointEnabled",
            "$..KmsKeyId",
            "$..LatestRestorableTime",
            "$..NetworkType",
            "$..PreferredBackupWindow",
            "$..PreferredMaintenanceWindow",
            "$..ReadReplicaIdentifiers",
            "$..ScalingConfigurationInfo",
            "$..AllocatedStorage",  # AWS sets this to 1 for aurora
            "$..BackupTarget",
            "$..CACertificateIdentifier",
            "$..CertificateDetails",
            "$..CustomerOwnedIpEnabled",
            "$..DBName",
            "$..DedicatedLogVolume",
            "$..MonitoringInterval",
            "$..NetworkType",
            "$..OptionGroupMemberships..OptionGroupName",
            "$..PendingModifiedValues",
            "$..StorageThroughput",
            "$..PerformanceInsightsKMSKeyId",
            "$..LocalWriteForwardingStatus",
            "$..AvailabilityZone",
            "$..LicenseModel",
        ]
    )
    @pytest.mark.parametrize(
        ["engine_mode", "engine_version"],
        [
            ("provisioned", "8.0.mysql_aurora.3.04.0"),  # Provisioned aurora
            ("serverless", "5.7.mysql_aurora.2.11.4"),  # Severless V1
        ],
    )
    @markers.aws.validated
    def test_create_aurora_db(
        self,
        rds_create_db_instance,
        rds_create_db_cluster,
        snapshot,
        engine_mode,
        engine_version,
        aws_client,
    ):
        snapshot.add_transformer(
            snapshot.transform.key_value(
                "AvailabilityZones",
                reference_replacement=False,
                value_replacement="<availability_zones>",
            )
        )
        snapshot.add_transformer(
            snapshot.transform.key_value(
                "CertificateDetails",
                reference_replacement=False,
                value_replacement="<certificate_details>",
            )
        )
        snapshot.add_transformer(
            snapshot.transform.key_value(
                "DBSubnetGroup", reference_replacement=False, value_replacement="<db_subnet_group>"
            )
        )

        snapshot.add_transformer(
            snapshot.transform.key_value("PreferredBackupWindow", reference_replacement=False)
        )
        snapshot.add_transformer(
            snapshot.transform.key_value("PreferredMaintenanceWindow", reference_replacement=False)
        )
        snapshot.add_transformer(snapshot.transform.rds_api())

        def fix_for_arm64(description: dict):
            # If validating the tests on an arm based cpu, the following differences are expected
            if not is_aws_cloud() and get_arch() == "arm64":
                description["EngineVersion"] = engine_version
                if engine_version == "5.7.mysql_aurora.2.11.4":
                    description["DBClusterParameterGroup"] = "default.aurora-mysql5.7"
            return description

        cluster_id = f"aurora-cluster-{short_uid()}"
        instance_id = f"aurora-instance-{short_uid()}"
        db_type = "aurora-mysql"
        credentials = "test1234"
        user = "myuser"
        rds_create_db_cluster(
            DBClusterIdentifier=cluster_id,
            Engine=db_type,
            MasterUsername=user,
            MasterUserPassword=credentials,
            EngineMode=engine_mode,
            EngineVersion=engine_version,
        )
        response = aws_client.rds.describe_db_clusters(DBClusterIdentifier=cluster_id)
        cluster = fix_for_arm64(response["DBClusters"][0])
        snapshot.match("create-cluster", cluster)

        def create_instance():
            rds_create_db_instance(
                DBClusterIdentifier=cluster_id,
                DBInstanceIdentifier=instance_id,
                Engine=db_type,
                EngineVersion=engine_version,
                DBInstanceClass="db.t4g.medium",
                EnablePerformanceInsights=True,
                PerformanceInsightsRetentionPeriod=7,
            )

        if engine_mode == "serverless":
            # Can't create instances for Serverless v1
            if is_aws_cloud():
                # TODO: We are currently not raising an exception and just start an instance instead
                with pytest.raises(Exception) as e:
                    create_instance()
                snapshot.match("error-create-instance", e.value.response)
        else:
            create_instance()
            response = aws_client.rds.describe_db_instances(DBInstanceIdentifier=instance_id)
            instance = fix_for_arm64(response["DBInstances"][0])
            snapshot.match("create-instance", instance)

    @markers.aws.validated
    def test_create_aurora_db_invalid_version(self, rds_create_db_cluster, snapshot):
        if get_arch() == "arm64":
            return pytest.skip(
                "This won't fail on arm as we specifically allow this behaviour as we can't support mapping"
            )
        cluster_id = f"aurora-cluster-{short_uid()}"
        db_type = "aurora-mysql"
        credentials = "test1234"
        user = "myuser"
        with pytest.raises(ClientError) as e:
            rds_create_db_cluster(
                DBClusterIdentifier=cluster_id,
                Engine=db_type,
                MasterUsername=user,
                MasterUserPassword=credentials,
                EngineVersion="8.0.34",  # This is the Mysql version. Aurora requires the Aurora style syntax
            )
        snapshot.match("create-cluster-error", e.value.response)

        engine_version = rds_create_db_cluster(
            Engine=db_type,
            MasterUsername=user,
            MasterUserPassword=credentials,
            EngineVersion="8.0",
        )["EngineVersion"]
        snapshot.match("create-aurora-mysql-8.0", engine_version)

        if is_aws_cloud():
            # TODO this may fail locally/on CI because it requests mysql image 5.7.12
            #    which may already be disabled by some docker versions:
            #    [DEPRECATION NOTICE] Docker Image Format v1 and Docker Image manifest version 2,
            #    schema 1 support is disabled by default
            engine_version = rds_create_db_cluster(
                Engine=db_type,
                MasterUsername=user,
                MasterUserPassword=credentials,
                EngineVersion="5.7",
            )["EngineVersion"]
            snapshot.match("create-aurora-mysql-5.7", engine_version)

        with pytest.raises(ClientError) as e:
            # version 5.6 is not accepted
            engine_version = rds_create_db_cluster(
                Engine=db_type,
                MasterUsername=user,
                MasterUserPassword=credentials,
                EngineVersion="5.6",
            )
        snapshot.match("create-cluster-error-5.6", e.value.response)

    @markers.aws.validated
    def test_delete_db_parameters_in_use(
        self,
        aws_client,
        rds_create_db_instance,
        snapshot,
        rds_create_db_cluster,
        rds_create_db_parameter_group,
        rds_create_db_cluster_parameter_group,
        cleanups,
    ):
        snapshot.add_transformer(snapshot.transform.rds_api())
        group_name = "testing-mysql"
        group_family = "mysql8.0"
        description = "custom mysql db parameter group"

        res = rds_create_db_parameter_group(
            DBParameterGroupName=group_name,
            DBParameterGroupFamily=group_family,
            Description=description,
        )
        snapshot.match("create-db-parameter-group", res)
        # make sure the cleanup happens in the right order, otherwise db-parameters don't get deleted
        cleanups.append(
            lambda: retry(
                lambda: aws_client.rds.delete_db_parameter_group(DBParameterGroupName=group_name),
                retries=30,
                sleep=40 if is_aws_cloud() else 1,
            )
        )
        db_id = rds_create_db_instance(
            Engine="mysql",
            EngineVersion="8.0",
            DBName=db_name,
            MasterUsername=DEFAULT_MASTER_USERNAME,
            MasterUserPassword=DEFAULT_TEST_MASTER_PASSWORD,
            DBParameterGroupName=group_name,
            PubliclyAccessible=False,
            expose_public_port=False,
        )["DBInstanceIdentifier"]

        cleanups.append(
            lambda: aws_client.rds.delete_db_instance(
                DBInstanceIdentifier=db_id, SkipFinalSnapshot=True
            )
        )
        # try to delete parameter group which is still in use
        with pytest.raises(ClientError) as e:
            aws_client.rds.delete_db_parameter_group(DBParameterGroupName=group_name)
        snapshot.match("delete-db-parameter-group-in-use-error", e.value.response)

        # test the same for db-group-parameters
        cluster_group_name = f"{group_name}-cluster"
        result = rds_create_db_cluster_parameter_group(
            DBClusterParameterGroupName=cluster_group_name,
            DBParameterGroupFamily="aurora-mysql8.0",
            Description="description for custom db cluster parameter group",
        )
        cleanups.append(
            lambda: retry(
                lambda: aws_client.rds.delete_db_cluster_parameter_group(
                    DBClusterParameterGroupName=cluster_group_name
                ),
                retries=30,
                sleep=30 if is_aws_cloud() else 1,
            )
        )

        snapshot.match("create-db-cluster-parameter-group", result)
        db_cluster_id = rds_create_db_cluster(
            Engine="aurora-mysql",
            MasterUsername=DEFAULT_MASTER_USERNAME,
            MasterUserPassword=DEFAULT_TEST_MASTER_PASSWORD,
            EngineVersion="8.0",
            DBClusterParameterGroupName=cluster_group_name,
        )["DBClusterIdentifier"]

        cleanups.append(
            lambda: aws_client.rds.delete_db_cluster(
                DBClusterIdentifier=db_cluster_id, SkipFinalSnapshot=True
            )
        )
        with pytest.raises(ClientError) as e:
            aws_client.rds.delete_db_cluster_parameter_group(
                DBClusterParameterGroupName=cluster_group_name
            )
        snapshot.match("delete-db-cluster-parameter-group-in-use-error", e.value.response)


@markers.only_in_docker
class TestRdsMariaDB(TestRDSBase):
    @markers.aws.unknown
    def test_create_mariadb(self, rds_create_db_instance, aws_client):
        db_type = "mariadb"
        credentials = "test1234"
        user = "myuser"
        result = self._create_db_instance_wait_for_ready(
            db_type, rds_create_db_instance, user=user, password=credentials
        )
        address = result["Endpoint"]["Address"]

        describe_res = aws_client.rds.describe_db_instances(
            DBInstanceIdentifier=result["DBInstanceIdentifier"]
        )

        describe_address = describe_res["DBInstances"][0]["Endpoint"]["Address"]
        assert address == describe_address == "localhost.localstack.cloud"
        port = result["Endpoint"]["Port"]
        self._create_table_and_select(db_type, port, user=user, password=credentials)

        # test for actual version, for MariaDB this is part of the 'version' variable
        query = "show variables where variable_name = 'version';"
        version_info = self.query_mysql(port, query, user=user, password=credentials)
        assert "MariaDB" in version_info[0]["Value"]


# MSSQL does not yet officially support arm, see: https://github.com/microsoft/mssql-docker/issues/802
@markers.only_on_amd64
@markers.resource_heavy
class TestRdsMssql(TestRDSBase):
    @classmethod
    def init_async(cls):
        def _run(*args):
            with INIT_LOCK_MSSQL:
                if DOCKER_IMAGE_MSSQL not in DOCKER_CLIENT.get_docker_image_names():
                    DOCKER_CLIENT.pull_image(DOCKER_IMAGE_MSSQL)

        start_worker_thread(_run)

    @markers.aws.unknown
    def test_create_mssql(self, rds_create_db_instance, monkeypatch, aws_client):
        monkeypatch.setenv("MSSQL_ACCEPT_EULA", "Y")
        user = "myuser"
        password = "Test123!"
        db_type = "sqlserver-se"
        result = self._create_db_instance_wait_for_ready(
            db_type, rds_create_db_instance, user=user, password=password
        )
        address = result["Endpoint"]["Address"]

        describe_res = aws_client.rds.describe_db_instances(
            DBInstanceIdentifier=result["DBInstanceIdentifier"]
        )

        describe_address = describe_res["DBInstances"][0]["Endpoint"]["Address"]
        assert address == describe_address == "localhost.localstack.cloud"
        port = result["Endpoint"]["Port"]
        self._create_table_and_select(db_type, port, user=user, password=password)


class TestRdsCrud:
    @markers.aws.unknown
    def test_create_db_parameter_group_add_tags(self, aws_client):
        tags = [{"Key": "character_set_client", "Value": "utf-8"}]
        result = aws_client.rds.create_db_parameter_group(
            DBParameterGroupName="test-sqlserver-2017",
            DBParameterGroupFamily="mysql5.6",
            Description="MySQL Group",
            Tags=tags,
        )
        resource = result["DBParameterGroup"]["DBParameterGroupArn"]
        result = aws_client.rds.list_tags_for_resource(ResourceName=resource)
        assert result["TagList"] == tags

        server_tags = [{"Key": "character_set_server", "Value": "utf-8"}]
        # this call triggered exception
        aws_client.rds.add_tags_to_resource(ResourceName=resource, Tags=server_tags)

        combined_tags = tags + server_tags
        result = aws_client.rds.list_tags_for_resource(ResourceName=resource)
        assert result["TagList"] == combined_tags

    @markers.aws.validated
    def test_db_cluster_parameter_groups(
        self, rds_create_db_cluster_parameter_group, aws_client, snapshot
    ):
        group_name = "g1"
        tags = [{"Key": "Hello", "Value": "World"}]
        result = rds_create_db_cluster_parameter_group(
            DBClusterParameterGroupName=group_name,
            DBParameterGroupFamily="aurora-postgresql14",
            Description="desc 123",
            Tags=tags,
        )
        group = result.get("DBClusterParameterGroup", {})

        snapshot.match("create_db_cluster_parameter_group", result)

        assert group.get("DBClusterParameterGroupName") == group_name
        assert group.get("DBParameterGroupFamily") == "aurora-postgresql14"

        result = aws_client.rds.describe_db_cluster_parameter_groups(
            DBClusterParameterGroupName=group_name
        )
        snapshot.match("describe_db_cluster_parameter_groups", result)

        arn = result["DBClusterParameterGroups"][0]["DBClusterParameterGroupArn"]
        params = [
            {
                "ParameterName": "ansi_force_foreign_key_checks",
                "ParameterValue": "0",
                "ApplyMethod": "immediate",
            }
        ]
        result = aws_client.rds.modify_db_cluster_parameter_group(
            DBClusterParameterGroupName=group_name, Parameters=params
        )
        assert result["DBClusterParameterGroupName"] == group_name
        snapshot.match("modify_db_cluster_parameter_group", result)

        result = aws_client.rds.describe_db_cluster_parameters(
            DBClusterParameterGroupName=group_name
        )
        sub_list = [
            i for i in result["Parameters"] if i["ParameterName"] == "ansi_force_foreign_key_checks"
        ]

        assert all(p in sub_list[0] for p in params[0])

        result = aws_client.rds.list_tags_for_resource(ResourceName=arn)
        snapshot.match("list_tags_for_resource", result)
        assert tags == result["TagList"]

    @markers.aws.validated
    def test_copy_db_parameter_groups(
        self, rds_create_db_parameter_group, rds_copy_db_parameter_group, aws_client, snapshot
    ):
        source_group_name = "source"
        source_group_desc = "source parameter group"
        source_group_family = "mysql5.7"
        target_group_name = "target"
        target_group_desc = "target parameter group"
        rds_create_db_parameter_group(
            DBParameterGroupName=source_group_name,
            DBParameterGroupFamily=source_group_family,
            Description=source_group_desc,
        )

        response = rds_copy_db_parameter_group(
            SourceDBParameterGroupIdentifier=source_group_name,
            TargetDBParameterGroupIdentifier=target_group_name,
            TargetDBParameterGroupDescription=target_group_desc,
        )
        snapshot.match("copy_db_parameter_groups", response)

        with pytest.raises(ClientError) as e:
            rds_copy_db_parameter_group(
                SourceDBParameterGroupIdentifier=source_group_name,
                TargetDBParameterGroupIdentifier=target_group_name,
                TargetDBParameterGroupDescription=target_group_desc,
            )
        snapshot.match("copy_db_parameter_groups_already_exists_error", e.value)

        with pytest.raises(ClientError) as e:
            rds_copy_db_parameter_group(
                SourceDBParameterGroupIdentifier="non-existing",
                TargetDBParameterGroupIdentifier="non-existing",
                TargetDBParameterGroupDescription=target_group_desc,
            )
        snapshot.match("copy_db_parameter_groups_non_existing_error_1", e.value)

        with pytest.raises(ClientError) as e:
            rds_copy_db_parameter_group(
                SourceDBParameterGroupIdentifier="non-existing",
                TargetDBParameterGroupIdentifier=target_group_name,
                TargetDBParameterGroupDescription=target_group_desc,
            )
        snapshot.match("copy_db_parameter_groups_non_existing_error_2", e.value)

        response = aws_client.rds.describe_db_parameter_groups(
            DBParameterGroupName=target_group_name
        )
        snapshot.match("describe_db_parameter_groups", response)

    @markers.aws.validated
    def test_describe_db_engine_versions(self, aws_client):
        versions = aws_client.rds.describe_db_engine_versions()["DBEngineVersions"]
        assert versions

        versions = aws_client.rds.describe_db_engine_versions(
            Engine="aurora-postgresql", EngineVersion="13.13"
        )
        assert len(versions["DBEngineVersions"]) == 1

    @markers.aws.validated
    def test_describe_db_engine_versions_paginated(self, aws_client):
        versions = aws_client.rds.describe_db_engine_versions()["DBEngineVersions"]
        assert versions

        versions = aws_client.rds.describe_db_engine_versions(
            Engine="aurora-postgresql", MaxRecords=20
        )
        assert len(versions["DBEngineVersions"]) == 20
        assert "Marker" in versions

        versions = aws_client.rds.describe_db_engine_versions()
        assert len(versions["DBEngineVersions"]) == 100
        assert "Marker" in versions

    @markers.aws.unknown
    def test_db_subnet_group(self, cleanups, aws_client):
        vpc_id = aws_client.ec2.create_vpc(CidrBlock="10.0.0.0/16")["Vpc"]["VpcId"]
        cleanups.append(lambda: aws_client.ec2.delete_vpc(VpcId=vpc_id))
        subnet_public_id = aws_client.ec2.create_subnet(VpcId=vpc_id, CidrBlock="10.0.0.0/21")[
            "Subnet"
        ]["SubnetId"]
        cleanups.append(lambda: aws_client.ec2.delete_subnet(SubnetId=subnet_public_id))
        subnet_private_id = aws_client.ec2.create_subnet(VpcId=vpc_id, CidrBlock="10.0.8.0/21")[
            "Subnet"
        ]["SubnetId"]
        cleanups.append(lambda: aws_client.ec2.delete_subnet(SubnetId=subnet_private_id))

        db_subnet_group = aws_client.rds.create_db_subnet_group(
            DBSubnetGroupName="test_db_subnet_group",
            DBSubnetGroupDescription="description",
            SubnetIds=[subnet_public_id, subnet_private_id],
        )
        cleanups.append(
            lambda: aws_client.rds.delete_db_subnet_group(DBSubnetGroupName="test_db_subnet_group")
        )
        # we use moto for db_subnet_groups, but we add an ARN to the response, check the presence
        assert db_subnet_group["DBSubnetGroup"]["DBSubnetGroupName"] == "test_db_subnet_group"
        assert db_subnet_group["DBSubnetGroup"]["DBSubnetGroupArn"].startswith("arn:aws:rds:")
        assert db_subnet_group["DBSubnetGroup"]["DBSubnetGroupArn"].endswith(
            ":subgrp:test_db_subnet_group"
        )

        subnet_describe = aws_client.rds.describe_db_subnet_groups()

        assert subnet_describe["DBSubnetGroups"][0] == db_subnet_group["DBSubnetGroup"]

        with pytest.raises(ClientError) as e:
            aws_client.rds.create_db_subnet_group(
                DBSubnetGroupName="failing_db_subnet_group",
                DBSubnetGroupDescription="desc",
                SubnetIds=["random_id"],
            )
        assert e.match("InvalidSubnetID.NotFound")
        assert e.match("The subnet ID 'random_id' does not exist")

    @markers.snapshot.skip_snapshot_verify(
        paths=(
            [
                # for some options set to true, no further explanation found
                "$..OptionGroup.AllowsVpcAndNonVpcInstanceMemberships",
            ]
        )
    )
    @markers.aws.validated
    def test_negative_cases_modify_option_group(self, cleanups, aws_client, snapshot):
        # copy non-existent option group
        with pytest.raises(Exception) as exc:
            aws_client.rds.copy_option_group(
                SourceOptionGroupIdentifier="doesnotexist",
                TargetOptionGroupIdentifier="mytargetgroup",
                TargetOptionGroupDescription="copy will fail",
            )

        snapshot.match("option-group-does-not-exist", exc.value.response)

        aws_client.rds.create_option_group(
            OptionGroupName="mytest",
            EngineName="mariadb",
            MajorEngineVersion="10.0",
            OptionGroupDescription="my test desc",
        )
        cleanups.append(lambda: aws_client.rds.delete_option_group(OptionGroupName="mytest"))
        # test
        with pytest.raises(Exception) as exc:
            aws_client.rds.modify_option_group(
                OptionGroupName="mytest",
                ApplyImmediately=True,
            )
        snapshot.match("invalid-modify", exc.value.response)

        # create option group with same name
        with pytest.raises(Exception) as exc:
            aws_client.rds.create_option_group(
                OptionGroupName="mytest",
                EngineName="mysql",
                MajorEngineVersion="8.0",
                OptionGroupDescription="this creation will fail",
            )

        snapshot.match("option-group-already-exists", exc.value.response)

        # remove option that is not set, does not throw exception
        response = aws_client.rds.modify_option_group(
            OptionGroupName="mytest",
            OptionsToRemove=["MARIADB_AUDIT_PLUGIN"],
            ApplyImmediately=True,
        )
        snapshot.match("remove-not-existing-option", response)

    @markers.snapshot.skip_snapshot_verify(
        paths=(
            [
                # for some options set to true, no further explanation found
                "$..OptionGroupsList..AllowsVpcAndNonVpcInstanceMemberships",
                "$..OptionGroup.AllowsVpcAndNonVpcInstanceMemberships",
            ]
        )
    )
    @markers.aws.validated
    def test_create_modify_option_group(self, cleanups, aws_client, snapshot):
        # TODO the options on AWS will include a lot of default settings, that we currently ignore in LS
        #   depending on the engine this can be dozens of settings
        #   we check the option-settings manually for now
        snapshot.add_transformer(
            KeyValueBasedTransformer(
                lambda k, v: v if k == "Options" and v != [] else None,
                "<options>",
                replace_reference=False,
            )
        )

        tags = [{"Key": "option-1", "Value": "1"}]
        response = aws_client.rds.create_option_group(
            OptionGroupName="mytest",
            EngineName="mariadb",
            MajorEngineVersion="10.0",
            OptionGroupDescription="my test desc",
            Tags=tags,
        )
        cleanups.append(lambda: aws_client.rds.delete_option_group(OptionGroupName="mytest"))

        snapshot.match("create_option_group", response)
        snapshot.match(
            "describe_option_group", aws_client.rds.describe_option_groups(OptionGroupName="mytest")
        )

        # check tags
        result = aws_client.rds.list_tags_for_resource(
            ResourceName=response["OptionGroup"]["OptionGroupArn"]
        )
        snapshot.match("list_tags", result)
        # add option
        response = aws_client.rds.modify_option_group(
            OptionGroupName="mytest",
            OptionsToInclude=[
                {
                    "OptionName": "MARIADB_AUDIT_PLUGIN",
                    "OptionSettings": [
                        {"Name": "SERVER_AUDIT_EVENTS", "Value": "CONNECT,QUERY,TABLE"},
                    ],
                },
            ],
            ApplyImmediately=True,
        )
        setting = [
            s
            for s in response["OptionGroup"]["Options"][0]["OptionSettings"]
            if s["Name"] == "SERVER_AUDIT_EVENTS"
        ]
        assert setting[0]["Value"] == "CONNECT,QUERY,TABLE"

        snapshot.match("modify_to_include", response)
        snapshot.match(
            "describe_option_group2",
            aws_client.rds.describe_option_groups(OptionGroupName="mytest"),
        )

        # copy option group
        response = aws_client.rds.copy_option_group(
            SourceOptionGroupIdentifier="mytest",
            TargetOptionGroupIdentifier="secondtest",
            TargetOptionGroupDescription="hello this is a second test",
        )
        cleanups.append(lambda: aws_client.rds.delete_option_group(OptionGroupName="secondtest"))

        # check tags copy with no tags set
        result = aws_client.rds.list_tags_for_resource(
            ResourceName=response["OptionGroup"]["OptionGroupArn"]
        )
        snapshot.match("list_tags_copy", result)

        snapshot.match("copy_option_group", response)

        response = aws_client.rds.modify_option_group(
            OptionGroupName="secondtest",
            OptionsToInclude=[
                {
                    "OptionName": "MARIADB_AUDIT_PLUGIN",
                    "OptionSettings": [
                        {"Name": "SERVER_AUDIT_EVENTS", "Value": "QUERY_DDL,QUERY_DML"},
                        {"Name": "SERVER_AUDIT_FILE_ROTATE_SIZE", "Value": "10000"},
                    ],
                },
            ],
            ApplyImmediately=True,
        )
        snapshot.match(
            "modify_option_group",
            response,
        )
        setting = [
            s
            for s in response["OptionGroup"]["Options"][0]["OptionSettings"]
            if s["Name"] == "SERVER_AUDIT_EVENTS" or s["Name"] == "SERVER_AUDIT_FILE_ROTATE_SIZE"
        ]
        assert len(setting) == 2
        assert setting[0]["Value"] == "QUERY_DDL,QUERY_DML"
        assert setting[0]["Name"] == "SERVER_AUDIT_EVENTS"
        assert setting[1]["Name"] == "SERVER_AUDIT_FILE_ROTATE_SIZE"
        assert setting[1]["Value"] == "10000"

        snapshot.match(
            "describe_option_group_copy",
            aws_client.rds.describe_option_groups(OptionGroupName="secondtest"),
        )
        snapshot.match(
            "describe_option_group3",
            aws_client.rds.describe_option_groups(OptionGroupName="mytest"),
        )

        # remove option
        response = aws_client.rds.modify_option_group(
            OptionGroupName="mytest",
            OptionsToRemove=["MARIADB_AUDIT_PLUGIN"],
            ApplyImmediately=True,
        )
        snapshot.match("modify_to_remove", response)
        snapshot.match(
            "describe_option_group4",
            aws_client.rds.describe_option_groups(OptionGroupName="mytest"),
        )
        snapshot.match(
            "describe_option_group_copy2",
            aws_client.rds.describe_option_groups(OptionGroupName="secondtest"),
        )

        # copy option group
        response = aws_client.rds.copy_option_group(
            SourceOptionGroupIdentifier="mytest",
            TargetOptionGroupIdentifier="anothertest",
            TargetOptionGroupDescription="another test with tags",
            Tags=[{"Key": "tag1", "Value": "mytag"}],
        )
        cleanups.append(lambda: aws_client.rds.delete_option_group(OptionGroupName="anothertest"))

        # check tags copy with tags set
        result = aws_client.rds.list_tags_for_resource(
            ResourceName=response["OptionGroup"]["OptionGroupArn"]
        )
        snapshot.match("list_tags_copy_with_tags", result)

        response = aws_client.rds.create_option_group(
            OptionGroupName="mysql-test",
            EngineName="mysql",
            MajorEngineVersion="8.0",
            OptionGroupDescription="mysql test group",
            Tags=tags,
        )
        cleanups.append(lambda: aws_client.rds.delete_option_group(OptionGroupName="mysql-test"))

        # check describe with filters for engine + engine version
        response = aws_client.rds.describe_option_groups(
            EngineName="mariadb", MajorEngineVersion="10.0"
        )["OptionGroupsList"]
        # filter so it can be compared with AWS result
        setting = [
            s
            for s in response
            if s["OptionGroupName"] in ["mytest", "secondtest", "anothertest", "mysql-test"]
        ]
        assert len(setting) == 3

    @markers.aws.only_localstack
    # testing cluster-endpoints depending on ENV RDS_CLUSTER_ENDPOINT_HOST_ONLY
    @pytest.mark.parametrize("cluster_endpoints_host_only", [True, False])
    def test_cluster_endpoint_address(
        self,
        aws_client,
        cluster_endpoints_host_only,
        rds_create_db_cluster_endpoint,
        rds_create_db_cluster,
        monkeypatch,
    ):
        monkeypatch.setattr(
            ext_config, "RDS_CLUSTER_ENDPOINT_HOST_ONLY", cluster_endpoints_host_only
        )
        cluster_id = f"cluster-{short_uid()}"
        user = "HelloUser"
        cred = "Test123!"
        create_result = rds_create_db_cluster(
            DBClusterIdentifier=cluster_id,
            Engine="aurora-postgresql",
            MasterUsername=user,
            MasterUserPassword=cred,
        )

        rds_create_db_cluster_endpoint(
            DBClusterEndpointIdentifier=f"custom-endpoint-{short_uid()}",
            DBClusterIdentifier=cluster_id,
            EndpointType="READER",
            StaticMembers=[],
        )
        endpoints = aws_client.rds.describe_db_cluster_endpoints(DBClusterIdentifier=cluster_id)
        describe_db_cluster = aws_client.rds.describe_db_clusters(DBClusterIdentifier=cluster_id)

        port = create_result["Port"]
        port_extension = f":{port}"
        if cluster_endpoints_host_only:
            assert port_extension not in create_result["Endpoint"]
            assert port_extension not in create_result["ReaderEndpoint"]
            assert port_extension not in describe_db_cluster["DBClusters"][0]["Endpoint"]
            for endpoint in endpoints["DBClusterEndpoints"]:
                assert port_extension not in endpoint["Endpoint"]
        else:
            assert create_result["Endpoint"].endswith(port_extension)
            assert create_result["ReaderEndpoint"].endswith(port_extension)
            assert describe_db_cluster["DBClusters"][0]["Endpoint"].endswith(port_extension)
            for endpoint in endpoints["DBClusterEndpoints"]:
                assert endpoint["Endpoint"].endswith(port_extension)


@markers.only_in_docker
class TestRdsPostgresLambdaExtensions(TestRDSBase):
    @markers.aws.needs_fixing
    @pytest.mark.parametrize(
        "engine_version",
        ["10.23", "11.16", "12.8", "13.4", "14.7", "15.2"],
    )
    def test_lambda_extensions(
        self,
        rds_create_db_cluster,
        rds_create_db_instance,
        create_lambda_function,
        account_id,
        region_name,
        engine_version,
    ):
        db_id = f"rds-{short_uid()}"
        engine = "aurora-postgresql"
        rds_create_db_cluster(
            DBClusterIdentifier=db_id,
            Engine=engine,
            DatabaseName=db_name,
            EngineVersion=engine_version,
        )
        result = rds_create_db_instance(
            DBClusterIdentifier=db_id,
            Engine=engine,
            DBInstanceClass="db.m3.large",
            EngineVersion=engine_version,
        )
        port = result["Endpoint"]["Port"]

        # create test function
        func_name = f"rds-{short_uid()}"
        zip_file = testutil.create_lambda_archive(TEST_LAMBDA_ECHO, get_content=True)
        create_lambda_function(zip_file=zip_file, func_name=func_name)

        # the queries below should work
        query = "CREATE EXTENSION aws_lambda"
        self.query_postgres(port, query, results=False)
        query = "CREATE   EXTENSION IF NOT EXISTS  aws_lambda CASCADE"
        self.query_postgres(port, query, results=False)

        # run queries with special Lambda features
        query = "SELECT aws_commons.create_lambda_function_arn('%s')" % func_name
        result = self.query_postgres(port, query)
        assert result == [arns.lambda_function_arn(func_name, account_id, region_name)]
        # FIXME aws returns different format? Tested with sql-helper lambda, returned: ['(rds-75a8cb48,eu-central-1)']
        region_name = "eu-central-1"
        query = f"SELECT aws_commons.create_lambda_function_arn('{func_name}', '{region_name}')"
        result = self.query_postgres(port, query)
        assert result == [arns.lambda_function_arn(func_name, account_id, region_name=region_name)]

        query = "SELECT aws_lambda.invoke('%s', '{\"body\": \"Hello!\"}'::json)" % func_name
        result = self.query_postgres(port, query)
        # FIXME: potential permission error on AWS (if the database is not set to public accessible)
        #  {'error': '{\'S\': \'ERROR\', \'V\': \'ERROR\', \'C\': \'XX000\', \'M\': \'unable to access credentials stored with the database instanc...RN) is associated with the feature-name: "Lambda".\', \'F\': \'rds_common.c\', \'L\': \'202\', \'R\': \'populateCredentials\'}', 'status': 'ERROR'}
        assert result == ['(200,{},$latest,"")']

        # assert that Lambda has been invoked
        def check_invocations():
            events = testutil.get_lambda_log_events(func_name)
            assert len(events) > 0

        retry(check_invocations, retries=6, sleep=1)


class TestRdsReset(TestRDSBase):
    @markers.aws.only_localstack
    def test_reset_cluster_with_instances(
        self, aws_client, rds_create_db_cluster, rds_create_db_instance
    ):
        # make sure everything is cleaned up before starting the test
        self._reset(aws_client)

        # create one cluster with a related instance
        # verify the data-dirs are gone after reset
        # cluster + instance for postgres
        db_cluster_id_postgres = f"rds-cluster-{short_uid()}"

        db_type = "aurora-postgresql"
        instance_class = "db.t3.large"
        rds_create_db_cluster(
            DBClusterIdentifier=db_cluster_id_postgres,
            Engine=db_type,
        )
        rds_create_db_instance(
            DBClusterIdentifier=db_cluster_id_postgres,
            DBInstanceIdentifier=f"rds-inst-{short_uid()}",
            Engine="aurora-postgresql",
            DBInstanceClass=instance_class,
        )

        # describe-db-clusters
        clusters = aws_client.rds.describe_db_clusters()["DBClusters"]
        assert len(clusters) == 1, f"expected 1 cluster, got: {clusters}"

        # check the path exists
        path = DBBackend.get("postgres").get_default_data_dir(clusters[0])

        assert os.path.exists(path), f"expected path exists {path}"
        # describe-db-instances
        result = aws_client.rds.describe_db_instances()["DBInstances"]
        assert len(result) == 1, "expected 1 running instances"

        # verify db is reachable
        port = result[0]["Endpoint"]["Port"]
        assert port == clusters[0]["Port"]
        self._create_table_and_select(db_type, port)

        # reset + check everything is cleared
        self._reset(aws_client)

        # verify dirs are empty
        state_path = DBBackend.get_rds_base_data_dir()
        assert not os.path.exists(state_path), f"expected dir does not exist: {state_path}"

        # verify db are not reachable anymore
        with pytest.raises(Exception):
            self.query_postgres(port, "SELECT 1")

    @pytest.mark.parametrize("db_engine", ("mysql", "sqlserver-se", "mariadb"))
    @markers.aws.only_localstack
    def test_reset_db_instance(self, aws_client, rds_create_db_instance, monkeypatch, db_engine):
        if get_arch() == "arm64" and "sqlserver" in db_engine:
            return pytest.skip("mssql not supported on arm")

        monkeypatch.setattr(ext_config, "RDS_MYSQL_DOCKER", 1)
        monkeypatch.setenv("MSSQL_ACCEPT_EULA", "Y")

        # make sure everything is cleaned up before starting the test
        self._reset(aws_client)

        instance_class = "db.t3.large"

        # TODO engine version relevant for mysql and currently ignored for mariadb + sqlserver
        #  -> might change in future
        db_version = "8.0.32"
        user = "myuser"
        password = "MyPassw0rd!"
        rds_create_db_instance(
            MasterUsername=user,
            MasterUserPassword=password,
            DBInstanceIdentifier=f"rds-inst-{short_uid()}",
            Engine=db_engine,
            EngineVersion=db_version,
            DBInstanceClass=instance_class,
        )
        # describe-db-instances
        result = aws_client.rds.describe_db_instances()["DBInstances"]
        assert len(result) == 1, "expected 1 running instances"

        # check the path exists
        if "sqlserver" not in db_engine:
            # sqlserver does currently not support persistence -> there is no dir mapped to this instance
            path = DBBackend.get(db_engine).get_default_data_dir(result[0])
            assert os.path.exists(path), f"expected path exists {path}"

        # describe-db-instances
        result = aws_client.rds.describe_db_instances()["DBInstances"]
        assert len(result) == 1, "expected 1 running instances"

        # verify db is reachable
        port = result[0]["Endpoint"]["Port"]
        self._create_table_and_select(db_engine, port, user=user, password=password)

        # reset + check everything is cleared
        self._reset(aws_client)

        # verify dirs are empty
        state_path = DBBackend.get_rds_base_data_dir()
        assert not os.path.exists(state_path), f"expected dir does not exist: {state_path}"

        # verify db is not reachable anymore
        with pytest.raises(Exception):
            if db_engine in ("mariadb", "mysql"):
                self.query_mysql(port, "SELECT 1")
            elif "sqlserver" in db_engine:
                self.query_mssql(port, "SELECT 1")

    def _reset(self, aws_client):
        # reset + check everything is cleared
        requests.post(f"{config.internal_service_url()}/_localstack/state/rds/reset")
        assert aws_client.rds.describe_db_clusters()["DBClusters"] == [], "expected 0 clusters"
        assert aws_client.rds.describe_db_instances()["DBInstances"] == [], "expected 0 instances"


class TestRdsPostgresCrossAccount(TestRDSBase):
    @markers.aws.only_localstack
    def test_create_restore_snapshot_cluster_cross_account(
        self,
        rds_create_db_cluster,
        rds_restore_db_cluster_from_snapshot,
        aws_client,
        secondary_aws_client,
    ):
        # create DB instance/cluster
        db_id = f"rds-snap0-{short_uid()}"
        engine = "postgres"
        result = rds_create_db_cluster(
            DBClusterIdentifier=db_id, Engine=engine, DatabaseName=db_name
        )
        port = result["Port"]

        # create snapshot with sample data
        table_name = self._insert_sample_data(port)
        self._assert_sample_data_exists(port, table_name)
        snapshot_id = f"rds-snap-{short_uid()}"
        cluster_snapshot = aws_client.rds.create_db_cluster_snapshot(
            DBClusterSnapshotIdentifier=snapshot_id, DBClusterIdentifier=db_id
        )
        snapshot_arn = cluster_snapshot["DBClusterSnapshot"]["DBClusterSnapshotArn"]

        cluster_snapshots = aws_client.rds.describe_db_cluster_snapshots(
            DBClusterSnapshotIdentifier=snapshot_id
        )
        assert cluster_snapshots["DBClusterSnapshots"][0] == cluster_snapshot["DBClusterSnapshot"]

        cluster_snapshots_secondary_account = (
            secondary_aws_client.rds.describe_db_cluster_snapshots(
                DBClusterSnapshotIdentifier=snapshot_id
            )
        )
        # assert that the snapshot doesn't exist in the secondary account
        assert cluster_snapshots_secondary_account["DBClusterSnapshots"] == []

        # restore snapshot into new DB cluster
        db_id_new = f"rds-snap1-{short_uid()}"
        result = rds_restore_db_cluster_from_snapshot(
            rds_client=secondary_aws_client.rds,
            DBClusterIdentifier=db_id_new,
            SnapshotIdentifier=snapshot_arn,
            Engine=engine,
        )
        assert "DBCluster" in result
        assert result["DBCluster"]["Engine"] == engine
        port_new = result["DBCluster"]["Port"]

        clusters = secondary_aws_client.rds.describe_db_clusters(DBClusterIdentifier=db_id_new)
        assert clusters["DBClusters"][0]["DBClusterIdentifier"] == db_id_new

        self._assert_sample_data_exists(port_new, table_name)

        deleted_cluster_snapshot = aws_client.rds.delete_db_cluster_snapshot(
            DBClusterSnapshotIdentifier=snapshot_id
        )
        assert (
            deleted_cluster_snapshot["DBClusterSnapshot"] == cluster_snapshot["DBClusterSnapshot"]
        )
        cluster_snapshots = aws_client.rds.describe_db_cluster_snapshots(
            DBClusterSnapshotIdentifier=snapshot_id
        )
        assert len(cluster_snapshots["DBClusterSnapshots"]) == 0

        # assert that we cannot restore from just the snapshot name because it does not exist
        with pytest.raises(ClientError):
            rds_restore_db_cluster_from_snapshot(
                rds_client=secondary_aws_client.rds,
                DBClusterIdentifier=db_id_new,
                SnapshotIdentifier=snapshot_id,
                Engine=engine,
            )

    @markers.aws.only_localstack
    def test_create_restore_snapshot_instance_cross_account(
        self,
        rds_create_db_instance,
        rds_restore_db_instance_from_snapshot,
        aws_client,
        secondary_aws_client,
    ):
        db_id = f"rds-snap0-{short_uid()}"
        result = self._create_db_instance_wait_for_ready(
            "postgres", rds_create_db_instance, db_id=db_id
        )
        port = result["Endpoint"]["Port"]

        # create snapshot with sample data
        table_name = self._insert_sample_data(port)

        snapshot_id = f"rds-snap-{short_uid()}"
        db_snapshot = aws_client.rds.create_db_snapshot(
            DBSnapshotIdentifier=snapshot_id, DBInstanceIdentifier=db_id
        )
        assert db_snapshot["DBSnapshot"]["DBSnapshotIdentifier"] == snapshot_id
        assert db_snapshot["DBSnapshot"]["DBInstanceIdentifier"] == db_id
        assert db_snapshot["DBSnapshot"]["Status"] == "available"
        snapshot_arn = db_snapshot["DBSnapshot"]["DBSnapshotArn"]

        # restore snapshot into new DB instance
        db_id_new = f"rds-snap1-{short_uid()}"
        result = rds_restore_db_instance_from_snapshot(
            rds_client=secondary_aws_client.rds,
            DBInstanceIdentifier=db_id_new,
            DBSnapshotIdentifier=snapshot_arn,
            DBInstanceClass="c2",
        )["DBInstance"]
        assert result["Engine"] == "postgres"
        port_new = result["Endpoint"]["Port"]

        instances = secondary_aws_client.rds.describe_db_instances(DBInstanceIdentifier=db_id_new)
        assert instances["DBInstances"][0]["DBInstanceIdentifier"] == db_id_new

        self._assert_sample_data_exists(port_new, table_name)

        # assert that we cannot restore from just the snapshot name because it does not exist
        with pytest.raises(ClientError):
            rds_restore_db_instance_from_snapshot(
                rds_client=secondary_aws_client.rds,
                DBInstanceIdentifier=db_id_new,
                DBSnapshotIdentifier=snapshot_id,
                DBInstanceClass="c2",
            )
