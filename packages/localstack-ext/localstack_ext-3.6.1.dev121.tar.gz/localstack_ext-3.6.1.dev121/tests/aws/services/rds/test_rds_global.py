import logging
from operator import itemgetter

import aws_cdk as cdk
import aws_cdk.aws_rds as rds
import pytest
from botocore.exceptions import ClientError
from localstack.pro.core.services.rds.db_utils import DEFAULT_MASTER_USERNAME
from localstack.testing.aws.util import is_aws_cloud
from localstack.testing.pytest import markers
from localstack.utils.strings import short_uid
from localstack.utils.sync import poll_condition, retry
from localstack_snapshot.snapshots.transformer import JsonpathTransformer

from tests.aws.services.rds.test_rds import (
    DEFAULT_TEST_MASTER_PASSWORD,
    TestRDSBase,
    get_availability_zones_transformer,
    wait_until_db_available,
)

LOG = logging.getLogger(__name__)

DB_NAME = "test"


@pytest.fixture
def create_global_cluster(aws_client):
    global_cluster_ids = list()

    def _create_global_cluster(**kwargs):
        response = aws_client.rds.create_global_cluster(**kwargs)
        cluster_id = response["GlobalCluster"]["GlobalClusterIdentifier"]
        global_cluster_ids.append(cluster_id)
        wait_until_db_available(aws_client.rds, global_cluster_id=cluster_id)
        return response

    yield _create_global_cluster

    for cluster_id in global_cluster_ids:
        try:
            aws_client.delete_global_cluster(GlobalClusterIdentifier=cluster_id)
        except Exception as e:
            LOG.debug("error cleaning up global cluster %s: %s", cluster_id, e)


class TestGlobalCluster(TestRDSBase):
    @markers.aws.only_localstack
    def test_global_cluster_read_write(
        self, aws_client_factory, rds_create_db_cluster, aws_client, cleanups, create_global_cluster
    ):
        """tests if the endpoints of all cluster and instances for a global cluster are the same"""
        db_type = "aurora-postgresql"
        engine_version = "13.7"
        global_cluster_id = f"global-id-{short_uid()}"
        create_global_cluster(
            GlobalClusterIdentifier=global_cluster_id, Engine=db_type, EngineVersion=engine_version
        )

        # create primary
        primary_cluster = f"rds-cluster-1-{short_uid()}"
        db_instance_id_1 = f"rds-inst-{short_uid()}"
        db_instance_id_2 = f"rds-inst-{short_uid()}"
        instance_class = "db.r5.large"

        result = rds_create_db_cluster(
            DBClusterIdentifier=primary_cluster,
            Engine=db_type,
            DatabaseName=DB_NAME,
            EngineVersion=engine_version,
            GlobalClusterIdentifier=global_cluster_id,
            MasterUsername=DEFAULT_MASTER_USERNAME,
            MasterUserPassword=DEFAULT_TEST_MASTER_PASSWORD,
        )
        cluster_arn_primary = result["DBClusterArn"]

        wait_until_db_available(aws_client.rds, cluster_id=primary_cluster)
        cleanups.append(
            lambda: aws_client.rds.remove_from_global_cluster(
                GlobalClusterIdentifier=global_cluster_id, DbClusterIdentifier=cluster_arn_primary
            )
        )
        dbi_resource_ids = []
        for instance in [db_instance_id_1, db_instance_id_2]:
            # add instance to the primary cluster
            response = aws_client.rds.create_db_instance(
                DBClusterIdentifier=primary_cluster,
                DBInstanceIdentifier=instance,
                Engine=db_type,
                EngineVersion=engine_version,
                DBInstanceClass=instance_class,
            )
            dbi_resource_ids.append(response["DBInstance"]["DbiResourceId"])
            wait_until_db_available(aws_client.rds, instance_id=instance)

        assert dbi_resource_ids[0] != dbi_resource_ids[1]
        # assert error "Cannot specify database name for cross region replication cluster"
        second_client = aws_client_factory(region_name="eu-west-1").rds
        secondary_cluster = f"rds-cluster-2-{short_uid()}"

        # add a secondary cluster
        result = rds_create_db_cluster(
            region_name="eu-west-1",
            DBClusterIdentifier=secondary_cluster,
            Engine=db_type,
            EngineVersion=engine_version,
            GlobalClusterIdentifier=global_cluster_id,
        )
        cluster_arn_secondary = result["DBClusterArn"]
        wait_until_db_available(second_client, cluster_id=secondary_cluster)

        cleanups.append(
            lambda: aws_client.rds.remove_from_global_cluster(
                GlobalClusterIdentifier=global_cluster_id, DbClusterIdentifier=cluster_arn_secondary
            )
        )

        # add instance to the secondary cluster
        response = second_client.create_db_instance(
            DBClusterIdentifier=secondary_cluster,
            DBInstanceIdentifier=db_instance_id_1,
            Engine=db_type,
            EngineVersion=engine_version,
            DBInstanceClass=instance_class,
        )
        assert response["DBInstance"]["DbiResourceId"] not in dbi_resource_ids
        dbi_resource_ids.append(response["DBInstance"]["DbiResourceId"])
        wait_until_db_available(second_client, instance_id=db_instance_id_1)

        # verify that all instances + cluster point to the same endpoint
        primary_describe = aws_client.rds.describe_db_clusters(DBClusterIdentifier=primary_cluster)
        secondary_describe = second_client.describe_db_clusters(
            DBClusterIdentifier=secondary_cluster
        )

        # cluster
        assert (
            primary_describe["DBClusters"][0]["Endpoint"]
            == secondary_describe["DBClusters"][0]["Endpoint"]
        )
        assert (
            primary_describe["DBClusters"][0]["Port"] == secondary_describe["DBClusters"][0]["Port"]
        )

        # instances
        primary_instance_1 = aws_client.rds.describe_db_instances(
            DBInstanceIdentifier=db_instance_id_1
        )
        primary_instance_2 = aws_client.rds.describe_db_instances(
            DBInstanceIdentifier=db_instance_id_2
        )
        secondary_instance_1 = second_client.describe_db_instances(
            DBInstanceIdentifier=db_instance_id_1
        )
        endpoint = primary_instance_1["DBInstances"][0]["Endpoint"]
        p_instance_1_endpoint = f"{endpoint['Address']}:{endpoint['Port']}"
        endpoint = primary_instance_2["DBInstances"][0]["Endpoint"]
        p_instance_2_endpoint = f"{endpoint['Address']}:{endpoint['Port']}"
        endpoint = secondary_instance_1["DBInstances"][0]["Endpoint"]
        s_instance_1_endpoint = f"{endpoint['Address']}:{endpoint['Port']}"

        assert p_instance_1_endpoint == p_instance_2_endpoint == s_instance_1_endpoint
        assert primary_describe["DBClusters"][0]["Port"] == endpoint["Port"]

        # verify DbiResourceIds
        assert primary_instance_1["DBInstances"][0]["DbiResourceId"] == dbi_resource_ids[0]
        assert primary_instance_2["DBInstances"][0]["DbiResourceId"] == dbi_resource_ids[1]
        assert secondary_instance_1["DBInstances"][0]["DbiResourceId"] == dbi_resource_ids[2]

        # test db is available
        self._create_table_and_select(db_type, endpoint["Port"])

    @markers.aws.needs_fixing
    def test_global_cluster_remove_instances_from_cluster(
        self, aws_client_factory, rds_create_db_cluster, aws_client, cleanups, create_global_cluster
    ):
        """tests db-instance 'isWriter' attribute changes correctly when removing db-instances from the cluster"""
        db_type = "aurora-postgresql"
        engine_version = "13.7"
        global_cluster_id = f"global-id-{short_uid()}"
        create_global_cluster(
            GlobalClusterIdentifier=global_cluster_id, Engine=db_type, EngineVersion=engine_version
        )

        # create primary
        primary_cluster = f"rds-cluster-1-{short_uid()}"
        instance_class = "db.r5.large"
        result = rds_create_db_cluster(
            DBClusterIdentifier=primary_cluster,
            Engine=db_type,
            DatabaseName=DB_NAME,
            EngineVersion=engine_version,
            GlobalClusterIdentifier=global_cluster_id,
            MasterUsername="tester",
            MasterUserPassword="Test123!",
        )
        cluster_arn_primary = result["DBClusterArn"]

        wait_until_db_available(aws_client.rds, cluster_id=primary_cluster)
        cleanups.append(
            lambda: _remove_from_global_cluster_wait(
                aws_client, global_cluster_id=global_cluster_id, cluster_arn=cluster_arn_primary
            )
        )

        for instance in ["instance1", "instance2", "instance3"]:
            # add instance to the primary cluster
            aws_client.rds.create_db_instance(
                DBClusterIdentifier=primary_cluster,
                DBInstanceIdentifier=instance,
                Engine=db_type,
                EngineVersion=engine_version,
                DBInstanceClass=instance_class,
            )

            wait_until_db_available(aws_client.rds, instance_id=instance)

        db_cluster_members = aws_client.rds.describe_db_clusters(
            DBClusterIdentifier=cluster_arn_primary
        )["DBClusters"][0].get("DBClusterMembers", [])
        assert 3 == len(db_cluster_members)
        writer = [db for db in db_cluster_members if db.get("IsClusterWriter")]
        assert 1 == len(writer)
        assert writer[0]["DBInstanceIdentifier"] == "instance1"

        # delete a instance that is not writer

        aws_client.rds.delete_db_instance(DBInstanceIdentifier="instance2")

        db_cluster_members = aws_client.rds.describe_db_clusters(
            DBClusterIdentifier=cluster_arn_primary
        )["DBClusters"][0].get("DBClusterMembers", [])
        assert 2 == len(db_cluster_members)
        writer = [db for db in db_cluster_members if db.get("IsClusterWriter")]
        assert 1 == len(writer)
        assert writer[0]["DBInstanceIdentifier"] == "instance1"

        # delete writer
        aws_client.rds.delete_db_instance(DBInstanceIdentifier="instance1")

        db_cluster_members = aws_client.rds.describe_db_clusters(
            DBClusterIdentifier=cluster_arn_primary
        )["DBClusters"][0].get("DBClusterMembers", [])
        assert 1 == len(db_cluster_members)
        writer = [db for db in db_cluster_members if db.get("IsClusterWriter")]
        assert 1 == len(writer)
        current_writer = writer[0]["DBInstanceIdentifier"]

        # add another instance
        aws_client.rds.create_db_instance(
            DBClusterIdentifier=primary_cluster,
            DBInstanceIdentifier="new-instance",
            Engine=db_type,
            EngineVersion=engine_version,
            DBInstanceClass=instance_class,
        )

        # we should have more members now, but still the same writer
        db_cluster_members = aws_client.rds.describe_db_clusters(
            DBClusterIdentifier=cluster_arn_primary
        )["DBClusters"][0].get("DBClusterMembers", [])
        assert 2 == len(db_cluster_members)
        writer = [db for db in db_cluster_members if db.get("IsClusterWriter")]
        assert 1 == len(writer)
        assert current_writer == writer[0]["DBInstanceIdentifier"]


class TestGlobalClusterCDK:
    DB_TYPE = "aurora-postgresql"
    ENGINE_VERSION = "15.2"
    DEFAULT_MASTER_USERNAME = "test"

    @pytest.fixture(scope="class", autouse=True)
    def infrastructure(self, aws_client, aws_client_factory, infrastructure_setup):
        infra = infrastructure_setup(namespace="GlobalCluster")
        stack_region_1 = cdk.Stack(infra.cdk_app, "GlobalCluster")

        vpc = cdk.aws_ec2.Vpc(
            stack_region_1, "vpc", restrict_default_security_group=False
        )  # avoid custom resource
        cdk.aws_ec2.SecurityGroup(stack_region_1, "securityGroup", vpc=vpc)
        engine = rds.DatabaseClusterEngine.aurora_postgres(
            version=rds.AuroraPostgresEngineVersion.VER_15_2
        )  # noqa

        database_cluster = rds.DatabaseCluster(
            stack_region_1,
            "primaryCluster",
            engine=engine,
            vpc=vpc,
            writer=rds.ClusterInstance.serverless_v2("writer"),
            readers=[
                rds.ClusterInstance.serverless_v2("reader", scale_with_writer=True),
                rds.ClusterInstance.serverless_v2("reader2"),
            ],
            serverless_v2_min_capacity=0.5,
            serverless_v2_max_capacity=1,
            default_database_name="myfirstdb",
            credentials=rds.Credentials.from_username(username=self.DEFAULT_MASTER_USERNAME),
        )
        global_cluster = rds.CfnGlobalCluster(
            stack_region_1,
            "globalCluster",
            source_db_cluster_identifier=database_cluster.cluster_identifier,
            global_cluster_identifier="myglobalcluster",
        )

        database_cluster.apply_removal_policy(cdk.RemovalPolicy.DESTROY)
        global_cluster.apply_removal_policy(cdk.RemovalPolicy.DESTROY)

        cdk.CfnOutput(stack_region_1, "ClusterIdPrimary", value=database_cluster.cluster_identifier)
        cdk.CfnOutput(stack_region_1, "GlobalClusterId", value=global_cluster.ref)

        with infra.provisioner() as prov:
            yield prov

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(
        paths=[
            "$..DBClusters..ActivityStreamStatus",
            "$..DBClusters..AssociatedRoles",
            "$..DBClusters..AutoMinorVersionUpgrade",
            "$..DBClusters..AvailabilityZones",
            "$..DBClusters..BackupRetentionPeriod",
            "$..DBClusters..ClusterCreateTime",
            "$..DBClusters..CrossAccountClone",
            "$..DBClusters..DBClusterMembers..PromotionTier",  # TODO not clear how the promotion-tier and isClusterWriter is chosen initially
            "$..DBClusters..DeletionProtection",
            "$..DBClusters..DomainMemberships",
            "$..DBClusters..EarliestRestorableTime",
            "$..DBClusters..EngineMode",
            "$..DBClusters..GlobalWriteForwardingRequested",
            "$..DBClusters..HostedZoneId",
            "$..DBClusters..HttpEndpointEnabled",
            "$..DBClusters..LatestRestorableTime",
            "$..DBClusters..NetworkType",
            "$..DBClusters..PreferredBackupWindow",
            "$..DBClusters..PreferredMaintenanceWindow",
            "$..DBClusters..ReadReplicaIdentifiers",
            "$..DBClusters..TagList",  # TODO not sure where the tags are set, it's not on the cluster directly
        ]
    )
    def test_validate_initial_setup(self, aws_client, infrastructure, snapshot):
        self._add_specific_transformers(snapshot, regions=[aws_client.sts.meta.region_name])

        outputs = infrastructure.get_stack_outputs("GlobalCluster")
        global_cluster_name = outputs.get("GlobalClusterId")
        primary_cluster_name = outputs.get("ClusterIdPrimary")

        # describe cluster
        describe_cluster = aws_client.rds.describe_db_clusters(
            DBClusterIdentifier=primary_cluster_name
        )
        describe_cluster["DBClusters"][0]["DBClusterMembers"].sort(
            key=itemgetter("IsClusterWriter"), reverse=True
        )
        snapshot.match("primary_describe_ready", describe_cluster)

        # describe global cluster
        result = aws_client.rds.describe_global_clusters(
            GlobalClusterIdentifier=global_cluster_name
        )
        snapshot.match("describe_global_cluster_primary", result)

        describe_endpoints = aws_client.rds.describe_db_cluster_endpoints(
            DBClusterIdentifier=primary_cluster_name
        )
        snapshot.match("describe_db_cluster_endpoints", describe_endpoints)

        # assert reader-endpoint + writer-endpoint
        reader_endpoint = describe_cluster["DBClusters"][0]["ReaderEndpoint"]
        endpoint = describe_cluster["DBClusters"][0]["Endpoint"]
        reader_endpoint_describe_endpoints = [
            endpoint["Endpoint"]
            for endpoint in describe_endpoints["DBClusterEndpoints"]
            if endpoint["EndpointType"] == "READER"
        ][0]
        writer_endpoint_describe_endpoints = [
            endpoint["Endpoint"]
            for endpoint in describe_endpoints["DBClusterEndpoints"]
            if endpoint["EndpointType"] == "WRITER"
        ][0]

        assert reader_endpoint == reader_endpoint_describe_endpoints
        assert endpoint == writer_endpoint_describe_endpoints

    @markers.aws.validated
    def test_invalid_secondary_cluster(
        self, aws_client, aws_client_factory, infrastructure, snapshot
    ):
        # assert error "Cannot specify database name for cross region replication cluster"
        outputs = infrastructure.get_stack_outputs("GlobalCluster")
        global_cluster_id = outputs.get("GlobalClusterId")
        second_client = aws_client_factory(region_name="eu-west-1").rds
        secondary_cluster = f"rds-cluster-2-{short_uid()}"
        with pytest.raises(ClientError) as exc:
            second_client.create_db_cluster(
                DBClusterIdentifier=secondary_cluster,
                Engine=self.DB_TYPE,
                DatabaseName=DB_NAME,
                EngineVersion=self.ENGINE_VERSION,
                GlobalClusterIdentifier=global_cluster_id,
                EnableGlobalWriteForwarding=True,
            )
        snapshot.match("error-specify-replica-db-name", exc.value.response)

        # assert error "Global write forwarding is not supported for engine aurora-postgresql"
        with pytest.raises(ClientError) as exc:
            second_client.create_db_cluster(
                DBClusterIdentifier=secondary_cluster,
                Engine=self.DB_TYPE,
                EngineVersion=self.ENGINE_VERSION,
                GlobalClusterIdentifier=global_cluster_id,
                EnableGlobalWriteForwarding=True,
            )
        snapshot.match("error-global-write-forwarding", exc.value.response)

        # TODO Cannot specify user name for cross region replication cluster
        with pytest.raises(ClientError) as exc:
            second_client.create_db_cluster(
                DBClusterIdentifier=secondary_cluster,
                Engine=self.DB_TYPE,
                EngineVersion=self.ENGINE_VERSION,
                GlobalClusterIdentifier=global_cluster_id,
                MasterUsername="newuser",
            )
        snapshot.match("error-invalid-masterusername", exc.value.response)

        with pytest.raises(ClientError) as exc:
            second_client.create_db_cluster(
                DBClusterIdentifier=secondary_cluster,
                Engine=self.DB_TYPE,
                EngineVersion=self.ENGINE_VERSION,
                GlobalClusterIdentifier=global_cluster_id,
                MasterUserPassword="N3W!PWD#newuser",
            )
        snapshot.match("error-invalid-masterpassword", exc.value.response)

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(
        paths=[
            "$..DBClusters..ActivityStreamStatus",
            "$..DBClusters..AssociatedRoles",
            "$..DBClusters..AutoMinorVersionUpgrade",
            "$..DBClusters..AvailabilityZones",
            "$..DBClusters..BackupRetentionPeriod",
            "$..DBClusters..ClusterCreateTime",
            "$..DBClusters..CopyTagsToSnapshot",
            "$..DBClusters..CrossAccountClone",
            "$..DBClusters..DBSubnetGroup",  # TODO "default" if not set
            "$..DBClusters..DeletionProtection",
            "$..DBClusters..DomainMemberships",
            "$..DBClusters..EarliestRestorableTime",
            "$..DBClusters..EngineMode",
            "$..DBClusters..GlobalWriteForwardingRequested",
            "$..DBClusters..HostedZoneId",
            "$..DBClusters..HttpEndpointEnabled",
            "$..DBClusters..LatestRestorableTime",
            "$..DBClusters..NetworkType",
            "$..DBClusters..PreferredBackupWindow",
            "$..DBClusters..PreferredMaintenanceWindow",
            "$..DBClusters..ReadReplicaIdentifiers",
        ]
    )
    def test_promote_secondary_headless(
        self,
        aws_client,
        aws_client_factory,
        infrastructure,
        snapshot,
        cleanups,
    ):
        outputs = infrastructure.get_stack_outputs("GlobalCluster")
        global_cluster_id = outputs.get("GlobalClusterId")

        self._add_specific_transformers(
            snapshot, regions=[aws_client.sts.meta.region_name, "eu-west-1"]
        )

        # setup secondary headless
        second_client = aws_client_factory(region_name="eu-west-1").rds
        secondary_cluster = f"second-cluster-{short_uid()}"

        result = second_client.create_db_cluster(
            DBClusterIdentifier=secondary_cluster,
            Engine=self.DB_TYPE,
            EngineVersion=self.ENGINE_VERSION,
            GlobalClusterIdentifier=global_cluster_id,
        )
        cluster_arn_secondary = result["DBCluster"]["DBClusterArn"]
        cleanups.append(
            lambda: second_client.delete_db_cluster(
                DBClusterIdentifier=secondary_cluster, SkipFinalSnapshot=True
            )
        )
        cleanups.append(
            lambda: _remove_from_global_cluster_wait(
                aws_client, global_cluster_id, cluster_arn_secondary
            )
        )
        wait_until_db_available(second_client, cluster_id=secondary_cluster)

        result1 = aws_client.rds.describe_db_cluster_endpoints()
        result2 = second_client.describe_db_cluster_endpoints()
        snapshot.match("describe_db_cluster_endpoint_default_region", result1)
        snapshot.match("describe_db_cluster_endpoint_region_secondary", result2)

        global_cluster_describe = aws_client.rds.describe_global_clusters(
            GlobalClusterIdentifier=global_cluster_id
        )
        snapshot.match("describe_global_clusters", global_cluster_describe)

        secondary_describe = second_client.describe_db_clusters(
            DBClusterIdentifier=secondary_cluster
        )
        snapshot.match("describe_db_clusters_secondary_headless", secondary_describe)

        # invalid failover
        with pytest.raises(ClientError) as exc:
            aws_client.rds.failover_global_cluster(
                GlobalClusterIdentifier=global_cluster_id,
                TargetDbClusterIdentifier=cluster_arn_secondary,
            )
        snapshot.match("invalid_state", exc.value.response)

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(
        paths=[
            "$..DBClusters..ActivityStreamStatus",
            "$..DBClusters..AssociatedRoles",
            "$..DBClusters..AutoMinorVersionUpgrade",
            "$..DBClusters..AvailabilityZones",
            "$..DBClusters..BackupRetentionPeriod",
            "$..DBClusters..ClusterCreateTime",
            "$..DBClusters..CopyTagsToSnapshot",
            "$..DBClusters..CrossAccountClone",
            "$..DBClusters..DBSubnetGroup",
            "$..DBClusters..DeletionProtection",
            "$..DBClusters..DomainMemberships",
            "$..DBClusters..EarliestRestorableTime",
            "$..DBClusters..EngineMode",
            "$..DBClusters..GlobalWriteForwardingRequested",
            "$..DBClusters..HostedZoneId",
            "$..DBClusters..HttpEndpointEnabled",
            "$..DBClusters..LatestRestorableTime",
            "$..DBClusters..NetworkType",
            "$..DBClusters..PreferredBackupWindow",
            "$..DBClusters..PreferredMaintenanceWindow",
            "$..DBClusters..ReadReplicaIdentifiers",
        ]
    )
    @markers.resource_heavy
    def test_failover(self, aws_client, aws_client_factory, infrastructure, snapshot, cleanups):
        self._add_specific_transformers(
            snapshot, regions=[aws_client.sts.meta.region_name, "eu-west-1"]
        )
        # add a secondary cluster
        second_client = aws_client_factory(region_name="eu-west-1").rds
        outputs = infrastructure.get_stack_outputs("GlobalCluster")
        global_cluster_id = outputs.get("GlobalClusterId")
        primary_cluster_id = outputs.get("ClusterIdPrimary")
        secondary_cluster = f"second-cluster-{short_uid()}"

        result = second_client.create_db_cluster(
            DBClusterIdentifier=secondary_cluster,
            Engine=self.DB_TYPE,
            EngineVersion=self.ENGINE_VERSION,
            GlobalClusterIdentifier=global_cluster_id,
        )
        cluster_arn_secondary = result["DBCluster"]["DBClusterArn"]
        cleanups.append(
            lambda: second_client.delete_db_cluster(
                DBClusterIdentifier=secondary_cluster, SkipFinalSnapshot=True
            )
        )
        cleanups.append(
            lambda: _remove_from_global_cluster_wait(
                aws_client, global_cluster_id, cluster_arn_secondary
            )
        )
        wait_until_db_available(second_client, cluster_id=secondary_cluster)

        # add instance to the secondary cluster
        db_instance_id_1 = f"inst-{short_uid()}"
        second_client.create_db_instance(
            DBClusterIdentifier=secondary_cluster,
            DBInstanceIdentifier=db_instance_id_1,
            Engine=self.DB_TYPE,
            EngineVersion=self.ENGINE_VERSION,
            DBInstanceClass="db.r5.large",
        )
        cleanups.append(
            lambda: second_client.delete_db_instance(
                DBInstanceIdentifier=db_instance_id_1, SkipFinalSnapshot=True
            )
        )
        wait_until_db_available(second_client, instance_id=db_instance_id_1)

        # describe cluster
        result = second_client.describe_db_clusters(DBClusterIdentifier=secondary_cluster)
        snapshot.match("describe_secondary_cluster_ready", result)

        cluster_arn_primary = aws_client.rds.describe_db_clusters(
            DBClusterIdentifier=primary_cluster_id
        )["DBClusters"][0]["DBClusterArn"]

        # describe cluster
        result1 = aws_client.rds.describe_global_clusters(GlobalClusterIdentifier=global_cluster_id)
        result2 = second_client.describe_global_clusters(GlobalClusterIdentifier=global_cluster_id)
        assert result1["GlobalClusters"] == result2["GlobalClusters"]
        snapshot.match("global_cluster_with_members", result1)

        members = result1["GlobalClusters"][0]["GlobalClusterMembers"]
        assert len(members) == 2
        members_map = {m["DBClusterArn"]: m for m in members}
        assert members_map.get(cluster_arn_primary)["IsWriter"]
        assert not members_map.get(cluster_arn_secondary)["IsWriter"]

        assert cluster_arn_secondary in members_map.get(cluster_arn_primary)["Readers"]

        assert not result1["GlobalClusters"][0].get("FailoverState")
        # check members + properties of primary + secondary before failover
        #   primary:
        describe = aws_client.rds.describe_db_clusters(DBClusterIdentifier=primary_cluster_id)

        assert len(describe["DBClusters"][0]["DBClusterMembers"]) == 3

        #   secondary #1:
        describe = second_client.describe_db_clusters(DBClusterIdentifier=secondary_cluster)
        members_map = {
            p["DBInstanceIdentifier"]: p for p in describe["DBClusters"][0]["DBClusterMembers"]
        }

        assert len(members_map) == 1
        assert not members_map.get(db_instance_id_1)["IsClusterWriter"]

        # describe cluster-endpoints
        result1 = aws_client.rds.describe_db_cluster_endpoints()
        result2 = second_client.describe_db_cluster_endpoints()
        snapshot.match("describe_db_cluster_endpoint_region_2", result1)
        snapshot.match("describe_db_cluster_endpoint_region_secondary_2", result2)

        # failover
        result = self._run_failover(
            aws_client,
            global_cluster_identifier=global_cluster_id,
            target_cluster_arn=cluster_arn_secondary,
        )
        snapshot.match("failover-global-cluster", result)

        # verify that the primary instance switched
        result = aws_client.rds.describe_global_clusters(GlobalClusterIdentifier=global_cluster_id)
        snapshot.match("describe_global_cluster_after_failover", result)

        writer_cluster = [
            m for m in result["GlobalClusters"][0]["GlobalClusterMembers"] if m["IsWriter"]
        ]
        assert len(writer_cluster) == 1
        assert writer_cluster[0]["DBClusterArn"] == cluster_arn_secondary

        # check members + properties of primary + secondary after failover
        #   primary:
        wait_until_db_available(aws_client.rds, cluster_id=primary_cluster_id)
        describe = aws_client.rds.describe_db_clusters(DBClusterIdentifier=primary_cluster_id)
        assert all(not m["IsClusterWriter"] for m in describe["DBClusters"][0]["DBClusterMembers"])

        #   secondary #1:
        wait_until_db_available(second_client, cluster_id=secondary_cluster)
        describe = second_client.describe_db_clusters(DBClusterIdentifier=secondary_cluster)
        assert describe["DBClusters"][0]["DBClusterMembers"][0]["IsClusterWriter"]

        # endpoints after
        result1 = aws_client.rds.describe_db_cluster_endpoints()
        result2 = second_client.describe_db_cluster_endpoints()
        snapshot.match("describe_db_cluster_endpoint_region_2_after", result1)
        snapshot.match("describe_db_cluster_endpoint_region_secondary_2_after", result2)

        # switch back
        self._run_failover(
            aws_client,
            global_cluster_identifier=global_cluster_id,
            target_cluster_arn=cluster_arn_primary,
        )
        result = aws_client.rds.describe_global_clusters(GlobalClusterIdentifier=global_cluster_id)
        snapshot.match("describe_global_cluster_after_second_failover", result)

        writer_cluster = [
            m for m in result["GlobalClusters"][0]["GlobalClusterMembers"] if m["IsWriter"]
        ]
        assert len(writer_cluster) == 1
        assert writer_cluster[0]["DBClusterArn"] == cluster_arn_primary

        # remove secondary
        aws_client.rds.remove_from_global_cluster(
            GlobalClusterIdentifier=global_cluster_id, DbClusterIdentifier=cluster_arn_secondary
        )

        def check_removed_global_cluster():
            res = aws_client.rds.describe_global_clusters(GlobalClusterIdentifier=global_cluster_id)
            return len(res["GlobalClusters"][0].get("GlobalClusterMembers")) == 1

        assert poll_condition(
            check_removed_global_cluster,
            timeout=900 if is_aws_cloud() else 30,
            interval=3 if is_aws_cloud() else 0.5,
        )

        result = aws_client.rds.describe_global_clusters(GlobalClusterIdentifier=global_cluster_id)
        snapshot.match("describe_global_after_removing", result)

        # endpoints after removal
        result1 = aws_client.rds.describe_db_cluster_endpoints()
        result2 = second_client.describe_db_cluster_endpoints()
        snapshot.match("describe_db_cluster_endpoint_removal_secondary", result1)
        snapshot.match("describe_db_cluster_endpoint_region_secondary_removal_secondary", result2)

    def _add_specific_transformers(self, snapshot, regions: list[str]):
        snapshot.add_transformer(snapshot.transform.rds_api())
        snapshot.add_transformer(
            snapshot.transform.key_value("ReaderEndpoint", reference_replacement=False)
        )
        snapshot.add_transformer(
            snapshot.transform.key_value("Endpoint", reference_replacement=False)
        )
        snapshot.add_transformer(
            snapshot.transform.key_value(
                "Port", value_replacement="<port>", reference_replacement=False
            )
        )
        for region in regions:
            snapshot.add_transformer(
                get_availability_zones_transformer(region),
                priority=-1,
            )
        snapshot.add_transformer(
            JsonpathTransformer(
                "$..TagList..Value", replacement="<tag-value-replaced>", replace_reference=False
            )
        )
        snapshot.add_transformer(
            snapshot.transform.key_value("DBSubnetGroup", reference_replacement=False)
        )

    def _check_failover_running(self, aws_client, global_cluster_id):
        res = aws_client.rds.describe_global_clusters(GlobalClusterIdentifier=global_cluster_id)
        return res["GlobalClusters"][0].get("FailoverState", {}).get("Status") == "switching-over"

    def _check_failover_finished(self, aws_client, global_cluster_id):
        res = aws_client.rds.describe_global_clusters(GlobalClusterIdentifier=global_cluster_id)
        return True if not res["GlobalClusters"][0].get("FailoverState") else False

    def _run_failover(self, aws_client, global_cluster_identifier, target_cluster_arn):
        result = aws_client.rds.failover_global_cluster(
            GlobalClusterIdentifier=global_cluster_identifier,
            TargetDbClusterIdentifier=target_cluster_arn,
        )
        assert poll_condition(
            lambda: self._check_failover_running(aws_client, global_cluster_identifier),
            timeout=300 if is_aws_cloud() else 30,
            interval=3 if is_aws_cloud() else 0.5,
        )

        assert poll_condition(
            lambda: self._check_failover_finished(aws_client, global_cluster_identifier),
            timeout=900 if is_aws_cloud() else 40,
            interval=3 if is_aws_cloud() else 1,
        )
        return result


def _remove_from_global_cluster_wait(aws_client, global_cluster_id, cluster_arn):
    def _check_global_cluster_members():
        describe = aws_client.rds.describe_global_clusters(
            GlobalClusterIdentifier=global_cluster_id
        )
        members = [m["DBClusterArn"] for m in describe["GlobalClusters"][0]["GlobalClusterMembers"]]
        return cluster_arn not in members

    if _check_global_cluster_members():
        return

    aws_client.rds.remove_from_global_cluster(
        GlobalClusterIdentifier=global_cluster_id, DbClusterIdentifier=cluster_arn
    )

    assert retry(
        lambda: _check_global_cluster_members(),
        retries=900 if is_aws_cloud() else 40,
        sleep=3 if is_aws_cloud() else 1,
    )
