import logging
import os

import aws_cdk as cdk
import aws_cdk.aws_ec2 as ec2
import aws_cdk.aws_neptune_alpha as neptune
import pytest
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection
from gremlin_python.process.anonymous_traversal import traversal
from gremlin_python.process.graph_traversal import __
from gremlin_python.process.traversal import Bindings, Cardinality, Merge, T, gt
from localstack.testing.aws.util import is_aws_cloud
from localstack.testing.pytest import markers
from localstack.utils.files import load_file, save_file
from localstack.utils.strings import short_uid
from localstack.utils.sync import retry
from localstack_snapshot.snapshots.transformer import GenericTransformer, KeyValueBasedTransformer

from tests.aws.services.neptune.tunnel_forwarder import start_tunnel_thread

KEY_PAIR_FILE_PATH = "/tmp/neptune-key-pair"
LOG = logging.getLogger(__name__)


class TestNeptuneCfn:
    STACK_NAME = "NeptuneStack"

    @pytest.fixture(scope="class")
    def patch_neptune(self):
        """patching the NEPTUNE_USE_SSL env to test the wss protocol"""
        from _pytest.monkeypatch import MonkeyPatch
        from localstack.pro.core import config as ext_config

        mpatch = MonkeyPatch()
        mpatch.setattr(ext_config, "NEPTUNE_USE_SSL", True)

        yield mpatch

        mpatch.undo()

    @pytest.fixture(scope="class", autouse=True)
    def infrastructure(self, aws_client, infrastructure_setup, patch_neptune):
        # When running snapshots this flag will need to be True as a bastion is created for aws only
        infra = infrastructure_setup(namespace="Neptune", force_synth=True)
        stack = cdk.Stack(infra.cdk_app, self.STACK_NAME)
        bastion = None
        # Neptune DB cluster can only be created in an Amazon Virtual Private Cloud (Amazon VPC),
        # and its endpoints are only accessible within that VPC
        vpc = ec2.Vpc(
            stack,
            "vpc",
            restrict_default_security_group=False,
            enable_dns_hostnames=True,
            enable_dns_support=True,
        )

        # Neptune Database and default parameter groups
        cluster_params = neptune.ClusterParameterGroup(
            stack,
            "ClusterParams",
            description="Cluster parameter group",
            family=neptune.ParameterGroupFamily.NEPTUNE_1_3,
            parameters={"neptune_enable_audit_log": "1"},
        )

        db_params = neptune.ParameterGroup(
            stack,
            "DbInstanceParams",
            description="Db parameter group",
            family=neptune.ParameterGroupFamily.NEPTUNE_1_3,
            parameters={"neptune_query_timeout": "120000"},
        )
        neptune_cluster = neptune.DatabaseCluster(
            stack,
            "NeptuneCluster",
            vpc=vpc,
            instance_type=neptune.InstanceType.T3_MEDIUM,
            removal_policy=cdk.RemovalPolicy.DESTROY,
            instances=2,
            cluster_parameter_group=cluster_params,
            parameter_group=db_params,
            # Creating an older version as well to have more coverage over the label delimiter patch
            engine_version=neptune.EngineVersion.V1_3_0_0,
        )
        if not is_aws_cloud():
            # When running locally, we will also perform our tests against a tx enabled version.
            tx_neptune_cluster = neptune.DatabaseCluster(
                stack,
                "TxNeptuneCluster",
                vpc=vpc,
                instance_type=neptune.InstanceType.T3_MEDIUM,
                removal_policy=cdk.RemovalPolicy.DESTROY,
                instances=2,
                cluster_parameter_group=cluster_params,
                parameter_group=db_params,
                # TODO This is the current default. But not supported yet by aws cdk. Once supported, we should
                #  uncomment to make sure we keep same versions for testing
                # engine_version=neptune.EngineVersion.V1_3_2_1,
            )
        else:
            tx_neptune_cluster = neptune_cluster

        # Security group that will allow access from local => bastion and from bastion => neptune
        security_group = ec2.SecurityGroup(stack, "securityGroup", vpc=vpc)
        neptune_cluster.connections.allow_from(security_group, ec2.Port.tcp(8182))
        tx_neptune_cluster.connections.allow_from(security_group, ec2.Port.tcp(8182))

        if is_aws_cloud():
            bastion = self.create_bastion_host(stack, vpc, security_group)

        cdk.CfnOutput(stack, "NeptuneClusterId", value=neptune_cluster.cluster_identifier)
        cdk.CfnOutput(stack, "DBParameterGroupName", value=db_params.parameter_group_name)
        cdk.CfnOutput(
            stack, "DBClusterParameterGroupName", value=cluster_params.cluster_parameter_group_name
        )
        cdk.CfnOutput(
            stack, "NeptuneEndpoint", value=neptune_cluster.cluster_endpoint.socket_address
        )
        cdk.CfnOutput(stack, "ClusterHostName", value=neptune_cluster.cluster_endpoint.hostname)
        cdk.CfnOutput(
            stack,
            "ClusterPort",
            value=cdk.Token.as_string(neptune_cluster.cluster_endpoint.port),
        )
        cdk.CfnOutput(
            stack, "TxClusterHostName", value=tx_neptune_cluster.cluster_endpoint.hostname
        )
        cdk.CfnOutput(
            stack,
            "TxClusterPort",
            value=cdk.Token.as_string(tx_neptune_cluster.cluster_endpoint.port),
        )
        cdk.CfnOutput(stack, "BastionPublicIp", value=bastion and bastion.instance_public_ip or "")
        cdk.CfnOutput(stack, "BastionInstanceId", value=bastion and bastion.instance_id or "")

        def delete_keys():
            if os.path.exists(KEY_PAIR_FILE_PATH):
                os.remove(KEY_PAIR_FILE_PATH)
            if os.path.exists(f"{KEY_PAIR_FILE_PATH}.public"):
                os.remove(f"{KEY_PAIR_FILE_PATH}.public")

        infra.add_custom_teardown(delete_keys)

        with infra.provisioner(skip_teardown=False) as prov:
            yield prov

    def create_bastion_host(self, stack, vpc, security_group):
        if not os.path.exists(KEY_PAIR_FILE_PATH) or not os.path.exists(
            f"{KEY_PAIR_FILE_PATH}.public"
        ):
            # We are locally saving both public and private key to prevent Cfn from trying to recreate the keys on every
            # run resulting in failures
            private_key = rsa.generate_private_key(
                public_exponent=65537, key_size=2048, backend=default_backend()
            )
            pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption(),
            )
            public_key_material = private_key.public_key().public_bytes(
                encoding=serialization.Encoding.OpenSSH, format=serialization.PublicFormat.OpenSSH
            )
            save_file(KEY_PAIR_FILE_PATH, content=pem, permissions=0o600)
            save_file(f"{KEY_PAIR_FILE_PATH}.public", content=public_key_material)
            public_key = public_key_material.decode()
        else:
            public_key = load_file(f"{KEY_PAIR_FILE_PATH}.public")

        key_pair = ec2.KeyPair(stack, "bastion-neptune-access", public_key_material=public_key)
        bastion = ec2.BastionHostLinux(
            stack,
            "BastionHostLinux",
            vpc=vpc,
            security_group=security_group,
            subnet_selection={"subnet_type": ec2.SubnetType.PUBLIC},
        )
        bastion.instance.instance.add_property_override("KeyName", key_pair.key_pair_name)
        bastion.allow_ssh_access_from(ec2.Peer.any_ipv4())
        return bastion

    @pytest.fixture
    def graph_connection(self, infrastructure):
        outputs = infrastructure.get_stack_outputs(self.STACK_NAME)
        host_name_param = "ClusterHostName"
        bastion_ip_param = "BastionPublicIp"
        cluster_port_param = "ClusterPort"
        threads = []
        conns = []
        graphs = []

        def _graph_connection(tx_enabled: bool = False):
            tx = "Tx" if tx_enabled else ""
            neptune_endpoint = outputs[tx + host_name_param]
            ec2_ip = outputs[bastion_ip_param]
            port = int(outputs[tx + cluster_port_param])
            if is_aws_cloud():
                threads.append(
                    start_tunnel_thread(
                        local_port=port,
                        remote_host=neptune_endpoint,
                        remote_port=port,
                        host=ec2_ip,
                        username="ec2-user",
                        keyfile=KEY_PAIR_FILE_PATH,
                    )
                )
                # localhost:8182 is now tunnelled to <neptune_endpoint:8182 through <bastion>:22
                neptune_endpoint = "localhost"
            conn = DriverRemoteConnection(
                # ssl validation will fail on aws as the certificate won't accept 'localhost` as host
                f"wss://{neptune_endpoint}:{port}/gremlin",
                "g",
                ssl=not is_aws_cloud(),
            )
            conns.append(conn)
            g = traversal().withRemote(conn)
            graphs.append(g)
            g.V().drop().iterate()
            return g

        yield _graph_connection

        # Clean up db and connections
        for g in graphs:
            g.V().drop().iterate()
        for conn in conns:
            conn.commit()
            conn.close()
        for thread in threads:
            thread.stop()

    @pytest.mark.parametrize("tx_enabled", [True, False])
    @markers.aws.validated
    def test_post_infra_setup(
        self, infrastructure, aws_client, graph_connection, snapshot, tx_enabled
    ):
        # This test should always remain the first step after infrastructure creation as it will wait for neptune to become available
        outputs = infrastructure.get_stack_outputs(stack_name=self.STACK_NAME)
        cluster_id = outputs["NeptuneClusterId"]

        def _wait_for_neptune_instances():
            # Cfn sometimes returns CREATED before the instances are ready. We must wait.
            result = aws_client.neptune.describe_db_instances(
                Filters=[{"Name": "db-cluster-id", "Values": [cluster_id]}]
            )
            for instance in result["DBInstances"]:
                assert instance["DBInstanceStatus"] == "available"

        retry(
            _wait_for_neptune_instances,
            retries=100 if is_aws_cloud() else 30,
            sleep=15 if is_aws_cloud() else 1,
        )
        g = graph_connection(tx_enabled)
        result = g.inject(0).next()
        snapshot.match("test-inject", result)

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(
        paths=[
            "$..Parameters",  # TODO: describe_db_*_parameter_group returns nothing on LS
            "$..DBInstances..AllocatedStorage",
            "$..DBInstances..AvailabilityZone",
            "$..DBInstances..DBName",  # TODO should not be added for instance that belongs to cluster
            "$..DBInstances..DBSubnetGroup",
            "$..DBInstances..DbInstancePort",
            "$..DBInstances..DomainMemberships",
            "$..DBInstances..EnabledCloudwatchLogsExports",
            "$..DBInstances..EngineVersion",
            "$..DBInstances..KmsKeyId",
            "$..DBInstances..LicenseModel",
            "$..DBInstances..MasterUsername",  # TODO should be the same as the cluster's master username
            "$..DBInstances..MonitoringInterval",
            "$..DBInstances..OptionGroupMemberships..OptionGroupName",
            "$..DBInstances..PendingModifiedValues",
            "$..DBInstances..PerformanceInsightsEnabled",
            "$..DBInstances..PromotionTier",
            "$..DBInstances..StatusInfos",
            "$..DBInstances..StorageEncrypted",
            "$..DBInstances..StorageType",
            "$..DBInstances..DbiResourceId",  # TODO LS returns the same id for both instances
            "$..DBInstances..VpcSecurityGroups..VpcSecurityGroupId",
            "$..DBClusters..AssociatedRoles",
            "$..DBClusters..AvailabilityZones",
            "$..DBClusters..BackupRetentionPeriod",
            "$..DBClusters..ClusterCreateTime",
            "$..DBClusters..CopyTagsToSnapshot",
            "$..DBClusters..CrossAccountClone",
            "$..DBClusters..DBClusterParameterGroup",
            "$..DBClusters..DBSubnetGroup",
            "$..DBClusters..DatabaseName",
            "$..DBClusters..DeletionProtection",
            "$..DBClusters..EarliestRestorableTime",
            "$..DBClusters..EngineVersion",
            "$..DBClusters..HostedZoneId",
            "$..DBClusters..KmsKeyId",
            "$..DBClusters..LatestRestorableTime",
            "$..DBClusters..MasterUsername",
            "$..DBClusters..PreferredBackupWindow",
            "$..DBClusters..PreferredMaintenanceWindow",
            "$..DBClusters..ReadReplicaIdentifiers",
            "$..DBClusters..ReaderEndpoint",
        ]
    )
    # TODO: describe_db_*_parameter_group returns nothing on LS
    # TODO: describe-db-clusters: missing params, different defaults
    # TODO: describe-db-instances: missing/added params; different defaults
    def test_describe(self, aws_client, infrastructure, snapshot):
        snapshot.add_transformer(snapshot.transform.rds_api())

        snapshot.add_transformer(
            snapshot.transform.key_value("Endpoint", reference_replacement=False)
        )
        snapshot.add_transformer(snapshot.transform.key_value("DBParameterGroupName"))
        snapshot.add_transformer(snapshot.transform.key_value("DBSubnetGroupName"))
        snapshot.add_transformer(snapshot.transform.key_value("DBClusterParameterGroup"))

        region = aws_client.sts.meta.region_name
        snapshot.add_transformer(
            KeyValueBasedTransformer(
                lambda k, v: v
                if k == "AvailabilityZones"
                and isinstance(v, list)
                and all(zone.startswith(region) for zone in v)
                else None,
                replacement="availability-zones",
                replace_reference=False,
            ),
            priority=-1,
        )

        outputs = infrastructure.get_stack_outputs(stack_name=self.STACK_NAME)
        neptune_endpoint = outputs.get("NeptuneEndpoint")
        # just a basic check that we have a valid endpoint-pattern, e.g. before we had 'localhost:4510:4510'
        # the endpoint will be validated by the lambda, which actually connects to neptune
        assert len(neptune_endpoint.split(":")) == 2
        cluster_id = outputs["NeptuneClusterId"]
        result = aws_client.neptune.describe_db_clusters(DBClusterIdentifier=cluster_id)
        result["DBClusters"][0]["DBClusterMembers"].sort(key=lambda x: x["IsClusterWriter"])

        snapshot.match("describe_db_clusters", result)
        db_cluster_members = result["DBClusters"][0]["DBClusterMembers"]
        writer_instance_id = [
            m["DBInstanceIdentifier"] for m in db_cluster_members if m["IsClusterWriter"]
        ][0]
        reader_instance_id = [
            m["DBInstanceIdentifier"] for m in db_cluster_members if not m["IsClusterWriter"]
        ][0]
        assert writer_instance_id
        assert reader_instance_id

        result = aws_client.neptune.describe_db_instances(DBInstanceIdentifier=writer_instance_id)
        snapshot.match("describe_db_instances_writer", result)

        result = aws_client.neptune.describe_db_instances(DBInstanceIdentifier=reader_instance_id)
        snapshot.match("describe_db_instances_reader", result)

        db_param_group_name = outputs["DBParameterGroupName"]

        result = aws_client.neptune.describe_db_parameters(DBParameterGroupName=db_param_group_name)
        snapshot.match("describe_db_parameter_group", result)

        cluster_param_group_name = outputs["DBClusterParameterGroupName"]

        result = aws_client.neptune.describe_db_cluster_parameters(
            DBClusterParameterGroupName=cluster_param_group_name
        )
        snapshot.match("describe_db_cluster_parameter_group", result)

    @pytest.mark.parametrize("tx_enabled", [True, False])
    @markers.aws.validated
    def test_query(self, aws_client, infrastructure, snapshot, graph_connection, tx_enabled):
        g = graph_connection(tx_enabled)
        v1 = (
            g.addV("person")
            .property(T.id, "1")
            .property("name", "marko")
            .property("age", 29)
            .next()
        )
        v2 = (
            g.addV("person")
            .property(T.id, "2")
            .property("name", "stephen")
            .property("age", 33)
            .next()
        )
        v3 = g.addV("person").property(T.id, "3").property("name", "mia").property("age", 30).next()

        g.V(Bindings.of("id", v1)).addE("knows").to(v2).property("weight", 0.75).iterate()
        g.V(Bindings.of("id", v1)).addE("knows").to(v3).property("weight", 0.85).iterate()

        names = g.V().values("name").to_list()

        marco_knows = g.V("1").outE("knows").inV().values("name").order().to_list()

        marco_knows_older_30 = g.V("1").out("knows").has("age", gt(30)).values("name").to_list()

        result = {
            "names": names,
            "marco_knows": marco_knows,
            "marco_knows_older_30": marco_knows_older_30,
        }
        snapshot.match("neptune_query_result", result)

    @pytest.mark.parametrize("tx_enabled", [True, False])
    @markers.aws.validated
    def test_property_cardinality(self, graph_connection, tx_enabled, snapshot):
        g = graph_connection(tx_enabled)

        vertex = g.addV("hand").property("card", "ace").next()
        node = g.V(vertex.id).property("card", "king").value_map().next()
        node["card"].sort()
        snapshot.match("set-property-default", node)

        node = g.V(vertex.id).property(Cardinality.single, "card", "queen").value_map().next()
        node["card"].sort()
        snapshot.match("set-property-single", node)

        node = g.V(vertex.id).property("card", "king").value_map().next()
        node["card"].sort()
        snapshot.match("set-property-add-to-single", node)

        node = g.V(vertex.id).property("card", "king").value_map().next()
        node["card"].sort()
        snapshot.match("set-property-add-repeat", node)

    @pytest.mark.parametrize("cardinality", [Cardinality.single, Cardinality.set_, None])
    @pytest.mark.parametrize("tx_enabled", [True, False])
    @markers.aws.validated
    def test_property_cardinality_merge(self, graph_connection, cardinality, snapshot, tx_enabled):
        g = graph_connection(tx_enabled)

        vertex = g.addV("hand").property("card", "ace").next()
        if cardinality:
            side_effect = __.property(cardinality, "card", "king")
        else:
            side_effect = __.property("card", "king")
        node = (
            g.merge_v({T.id: vertex.id})
            .option(Merge.on_match, __.side_effect(side_effect).constant({}))
            .value_map()
            .next()
        )
        node["card"].sort()
        snapshot.match("set-property-merge", node)

    @pytest.mark.parametrize("tx_enabled", [True, False])
    @markers.aws.validated
    def test_multi_label(self, aws_client, infrastructure, snapshot, graph_connection, tx_enabled):
        snapshot.add_transformer(snapshot.transform.key_value("id", value_replacement="vertex-id"))
        g = graph_connection(tx_enabled)

        vertex = g.addV("Label1::Label2::Label3").next()
        vertex_dict = {"id": str(vertex.id), "label": vertex.label}
        label_1 = g.V().hasLabel("Label1").to_list()
        label_1_list = _parse_vertices(label_1)
        assert len(label_1_list) == 1

        label_2 = g.V().hasLabel("Label2").to_list()
        label_2_list = _parse_vertices(label_2)
        assert len(label_2_list) == 1

        label_3 = g.V().hasLabel("Label3").to_list()
        label_3_list = _parse_vertices(label_3)
        assert len(label_3_list) == 1

        label_123 = g.V().hasLabel("Label1::Label2::Label3").to_list()
        label_123_list = _parse_vertices(label_123)
        assert len(label_123_list) == 0

        # test several labels
        label_list_valid = g.V().hasLabel("Label2", "Label3", "something").to_list()
        label_list_valid = _parse_vertices(label_list_valid)
        assert len(label_list_valid) == 1

        label_list_empty = g.V().hasLabel("Label4", "something").to_list()
        label_list_empty = _parse_vertices(label_list_empty)
        assert len(label_list_empty) == 0

        result = {
            "multi_label_inserted": vertex_dict,
            "Label1": label_1_list[0],
            "Label2": label_2_list[0],
            "Label3": label_3_list[0],
            "Label1::Label2::Label3": label_123_list,
            "Label2, Label3, something": label_list_valid[0],
            "Label4, something": label_list_empty,
        }

        def _sort_labels(snapshot_content: dict, *args) -> dict:
            """
            the returned label order is not guaranteed, e.g. even though we add label "Label1::Label2::Label3"
            it was returned differently by AWS sometimes, e.g. "Label1::Label3::Label2", indicating that there is no real order
            therefore we manually order the labels before snapshotting
            """
            for _, v in snapshot_content["neptune_query_result"].items():
                if isinstance(v, dict) and "label" in v:
                    labels = v["label"].split("::")
                    labels.sort()
                    v["label"] = "::".join(labels)
            return snapshot_content

        snapshot.add_transformer(GenericTransformer(_sort_labels))
        snapshot.match("neptune_query_result", result)

    @markers.aws.validated
    def test_neptune_transaction_success(self, infrastructure, snapshot, graph_connection):
        rollback = False

        g = graph_connection(tx_enabled=True)
        tx = g.tx()
        gtx = tx.begin()

        try:
            # Creating two nodes in the same tx
            v1 = gtx.addV("label1").property("name", "foo").next()
            v2 = gtx.addV("label1").property("name", "bar").next()
            gtx.addE("edge").from_(v1).to(v2).next()
            tx.commit()
        except Exception as e:
            rollback = True
            tx.rollback()
        finally:
            if tx.is_open():
                tx.close()
        nodes = g.V().value_map(True).toList()
        edges = g.E().value_map(True).toList()

        v1_id = v1.id
        nodes.sort(key=lambda x: x[T.id] == v1_id)

        assert not rollback
        snapshot.match("success-tx-nodes", _deserialize(nodes))
        snapshot.match("success-tx-edges", _deserialize(edges))

        gtx = tx.begin()
        try:
            # Updating a node in subsequent tx
            gtx.V(v1_id).property("last_name", "foo2").next()
            tx.commit()
        except Exception as e:
            rollback = True
            tx.rollback()
        finally:
            if tx.is_open():
                tx.close()
        assert not rollback
        nodes = g.V(v1_id).value_map(True).toList()
        snapshot.match("updated-tx-node", _deserialize(nodes))

    @markers.aws.validated
    def test_neptune_transaction_rollback(self, infrastructure, graph_connection):
        rollback = False

        g = graph_connection(tx_enabled=True)
        tx = g.tx()
        gtx = tx.begin()

        try:
            # Creating 2 nodes with the same id results in a rollback
            vid = short_uid()
            gtx.addV("label1").property(T.id, vid).next()
            gtx.addV("label1").property(T.id, vid).next()
            tx.commit()
        except Exception:
            rollback = True
            tx.rollback()
        nodes = g.V().toList()
        assert rollback
        assert nodes == []


def _parse_vertices(vertices):
    # Convert each vertex to a dictionary and collect them in a list
    vertices_data = []
    for vertex in vertices:
        vertex_data = {"id": str(vertex.id), "label": vertex.label}
        vertices_data.append(vertex_data)

    return vertices_data


def _deserialize(vertices_data):
    sers = []
    for vertex in vertices_data:
        ser = {}
        for k, v in vertex.items():
            match k:
                case T():
                    ser[k.name] = v
                case _:
                    ser[k] = v
        sers.append(ser)
    return sers
