import json
import os

import aws_cdk as cdk
import aws_cdk.aws_neptune_alpha as neptune
import pytest
from localstack.testing.pytest import markers
from localstack.testing.scenario.cdk_lambda_helper import (
    load_nodejs_lambda_to_s3,
    load_python_lambda_to_s3,
)
from localstack.utils.strings import to_bytes

from tests.aws.cdk_helper import delete_db_instances_from_cluster
from tests.aws.scenario.rds_neptune_docdb.constructs.aurora_postgres_construct import (
    LAMBDA_RDS_QUERY_HELPER,
    AuroraPostgresConstruct,
)
from tests.aws.scenario.rds_neptune_docdb.constructs.docdb_construct import (
    LAMBDA_DOCDB_QUERY_HELPER,
    DocDBConstruct,
)


@markers.acceptance_test
class TestRdsNeptuneDocDB:
    """
    Tests concurrent creation of RDS, Neptune, and DocDB Clusters
    * testing the rds-api which by default addresses all three services, and related filters
    * testing secrets creation for RDS database, and using secret to connect to the database with a lambda
    * testing secrets for DocDB + Node.js lambda to connect to DocDB and run sample query
    """

    @pytest.fixture(scope="class")
    def patch_docdb_proxy_container(self):
        """patching the DOCDB_PROXY_CONTAINER env, can be removed once this is the default"""
        from _pytest.monkeypatch import MonkeyPatch
        from localstack.pro.core import config as ext_config

        mpatch = MonkeyPatch()
        mpatch.setattr(ext_config, "DOCDB_PROXY_CONTAINER", True)
        yield mpatch
        mpatch.undo()

    @pytest.fixture(scope="class", autouse=True)
    def infrastructure(self, aws_client, infrastructure_setup, patch_docdb_proxy_container):
        infra = infrastructure_setup(namespace="RdsNeptuneDocDB")

        stack = cdk.Stack(infra.cdk_app, "ClusterStack")

        vpc = cdk.aws_ec2.Vpc(
            stack, "vpc", restrict_default_security_group=False
        )  # avoid custom resource
        cdk.aws_ec2.SecurityGroup(stack, "securityGroup", vpc=vpc)

        aurora_cluster = AuroraPostgresConstruct(stack, "AuroraPostgresConstruct", vpc=vpc)

        neptune_cluster = neptune.DatabaseCluster(
            stack,
            "NeptuneCluster",
            vpc=vpc,
            instance_type=neptune.InstanceType.R5_LARGE,
            removal_policy=cdk.RemovalPolicy.DESTROY,
        )

        docdb = DocDBConstruct(stack, "DocDBConstruct", vpc=vpc)
        # setup custom lambdas
        infra.add_custom_setup(
            lambda: load_python_lambda_to_s3(
                aws_client.s3,
                infra.get_asset_bucket(),
                LAMBDA_RDS_QUERY_HELPER,
                os.path.join(os.path.dirname(__file__), "functions/query_helper_rds.py"),
                additional_python_packages=["pg8000"],
            )
        )

        infra.add_custom_setup(
            lambda: load_nodejs_lambda_to_s3(
                aws_client.s3,
                infra.get_asset_bucket(),
                LAMBDA_DOCDB_QUERY_HELPER,
                os.path.join(os.path.dirname(__file__), "functions/query_helper_docdb.js"),
                additional_nodjs_packages=["mongodb"],
            )
        )

        # outputs
        cdk.CfnOutput(stack, "ClusterId", value=aurora_cluster.database_cluster.cluster_identifier)
        cdk.CfnOutput(stack, "SecretArn", value=aurora_cluster.database_cluster.secret.secret_arn)
        cdk.CfnOutput(
            stack, "RDSLambdaQueryHelper", value=aurora_cluster.rds_query_fn.function_name
        )

        cdk.CfnOutput(stack, "NeptuneClusterId", value=neptune_cluster.cluster_identifier)

        cdk.CfnOutput(stack, "DocDBClusterId", value=docdb.docdb_cluster.cluster_identifier)
        cdk.CfnOutput(stack, "DocDBSecretArn", value=docdb.docdb_cluster.secret.secret_arn)
        cdk.CfnOutput(stack, "DocDBLambdaQueryHelper", value=docdb.docdb_query_fn.function_name)

        # workaround for a issue in neptune-alpha lib -> instances are not deleted
        infra.add_custom_teardown(
            lambda: delete_db_instances_from_cluster(
                aws_client.rds,
                infra.get_stack_outputs(stack_name="ClusterStack").get("NeptuneClusterId"),
            )
        )
        with infra.provisioner() as prov:
            yield prov

    @markers.aws.validated
    def test_docdb_connection(self, aws_client, infrastructure, snapshot):
        outputs = infrastructure.get_stack_outputs(stack_name="ClusterStack")
        helper_fn = outputs["DocDBLambdaQueryHelper"]

        result = aws_client.lambda_.invoke(FunctionName=helper_fn)
        result = json.load(result["Payload"])
        snapshot.add_transformer(
            snapshot.transform.key_value("_id", "id", reference_replacement=False)
        )
        snapshot.match("docdb-query", result)

    @markers.aws.validated
    def test_scenario_validate_infra(self, aws_client, infrastructure):
        outputs = infrastructure.get_stack_outputs(stack_name="ClusterStack")
        # validate rds
        cluster_id = outputs["ClusterId"]
        clusters = aws_client.rds.describe_db_clusters(DBClusterIdentifier=cluster_id)["DBClusters"]
        assert clusters
        assert len(clusters[0]["DBClusterMembers"]) == 2

        # validate rds secret
        secret_arn = outputs["SecretArn"]
        secret = aws_client.secretsmanager.describe_secret(SecretId=secret_arn)
        assert secret["ARN"] == secret_arn
        secret_value = aws_client.secretsmanager.get_secret_value(SecretId=secret_arn)
        secret_string = secret_value["SecretString"]
        assert "username" in secret_string

        # validate neptune
        neptune_cluster_id = outputs["NeptuneClusterId"]
        clusters = aws_client.rds.describe_db_clusters(DBClusterIdentifier=neptune_cluster_id)[
            "DBClusters"
        ]
        assert clusters

        clusters = aws_client.neptune.describe_db_clusters(DBClusterIdentifier=neptune_cluster_id)[
            "DBClusters"
        ]
        assert clusters
        assert len(clusters[0]["DBClusterMembers"]) == 1

        # validate docdb
        docdb_cluster_id = outputs["DocDBClusterId"]
        clusters = aws_client.rds.describe_db_clusters(DBClusterIdentifier=docdb_cluster_id)[
            "DBClusters"
        ]
        assert clusters

        clusters = aws_client.docdb.describe_db_clusters(DBClusterIdentifier=docdb_cluster_id)[
            "DBClusters"
        ]
        assert clusters
        assert len(clusters[0]["DBClusterMembers"]) == 1

        # validate docdb secret
        secret_arn = outputs["DocDBSecretArn"]
        secret_value = aws_client.secretsmanager.get_secret_value(SecretId=secret_arn)
        secret_json = json.loads(secret_value["SecretString"])
        assert secret_json.get("username") == "myuser"
        expected_keys = [
            "dbClusterIdentifier",
            "engine",
            "port",
            "host",
            "username",
        ]  # TODO ssl
        keys = list(secret_json.keys())
        assert all(key in keys for key in expected_keys)

    @markers.aws.validated
    def test_describe_db_clusters_with_filter(self, aws_client, infrastructure):
        outputs = infrastructure.get_stack_outputs(stack_name="ClusterStack")
        rds_cluster_id = outputs["ClusterId"]
        docdb_cluster_id = outputs["DocDBClusterId"]
        neptune_cluster_id = outputs["NeptuneClusterId"]

        # describe clusters without filter
        rds_clusters = aws_client.rds.describe_db_clusters()["DBClusters"]
        neptune_clusters = aws_client.neptune.describe_db_clusters()["DBClusters"]
        docdb_clusters = aws_client.docdb.describe_db_clusters()["DBClusters"]
        assert len(rds_clusters) == len(neptune_clusters) == len(docdb_clusters)

        rds_cluster_identifiers = [db["DBClusterIdentifier"] for db in rds_clusters]
        assert rds_cluster_id in rds_cluster_identifiers
        assert docdb_cluster_id in rds_cluster_identifiers
        assert neptune_cluster_id in rds_cluster_identifiers

        neptune_cluster_identifiers = [db["DBClusterIdentifier"] for db in neptune_clusters]
        assert rds_cluster_id in neptune_cluster_identifiers
        assert docdb_cluster_id in neptune_cluster_identifiers
        assert neptune_cluster_id in neptune_cluster_identifiers

        docdb_cluster_identifiers = [db["DBClusterIdentifier"] for db in docdb_clusters]
        assert rds_cluster_id in docdb_cluster_identifiers
        assert docdb_cluster_id in docdb_cluster_identifiers
        assert neptune_cluster_id in docdb_cluster_identifiers

        # describe clusters with filter

        # filter for cluster ids
        rds_clusters = aws_client.rds.describe_db_clusters(
            Filters=[{"Name": "db-cluster-id", "Values": [rds_cluster_id, neptune_cluster_id]}]
        )["DBClusters"]
        assert len(rds_clusters) == 2
        assert docdb_cluster_id not in [db["DBClusterIdentifier"] for db in rds_clusters]

        # filter rds/docdb/neptune for "engine=neptune"
        # all apis should return the same result
        rds_clusters = aws_client.rds.describe_db_clusters(
            Filters=[{"Name": "engine", "Values": ["neptune"]}]
        )["DBClusters"]
        neptune_clusters = aws_client.neptune.describe_db_clusters(
            Filters=[{"Name": "engine", "Values": ["neptune"]}]
        )["DBClusters"]
        docdb_clusters = aws_client.docdb.describe_db_clusters(
            Filters=[{"Name": "engine", "Values": ["neptune"]}]
        )["DBClusters"]

        rds_cluster_identifiers = [db["DBClusterIdentifier"] for db in rds_clusters]
        assert rds_cluster_id not in rds_cluster_identifiers
        assert docdb_cluster_id not in rds_cluster_identifiers
        assert neptune_cluster_id in rds_cluster_identifiers

        neptune_cluster_identifiers = [db["DBClusterIdentifier"] for db in neptune_clusters]
        assert rds_cluster_id not in neptune_cluster_identifiers
        assert docdb_cluster_id not in neptune_cluster_identifiers
        assert neptune_cluster_id in neptune_cluster_identifiers

        docdb_cluster_identifiers = [db["DBClusterIdentifier"] for db in docdb_clusters]
        assert rds_cluster_id not in docdb_cluster_identifiers
        assert docdb_cluster_id not in docdb_cluster_identifiers
        assert neptune_cluster_id in docdb_cluster_identifiers

        # filter for docdb
        rds_clusters = aws_client.rds.describe_db_clusters(
            Filters=[{"Name": "engine", "Values": ["docdb"]}]
        )["DBClusters"]
        rds_cluster_identifiers = [db["DBClusterIdentifier"] for db in rds_clusters]
        assert rds_cluster_id not in rds_cluster_identifiers
        assert docdb_cluster_id in rds_cluster_identifiers
        assert neptune_cluster_id not in rds_cluster_identifiers

        # filter for mysql
        rds_clusters = aws_client.rds.describe_db_clusters(
            Filters=[{"Name": "engine", "Values": ["mysql"]}]
        )["DBClusters"]
        rds_cluster_identifiers = [db["DBClusterIdentifier"] for db in rds_clusters]
        assert rds_cluster_id not in rds_cluster_identifiers
        assert docdb_cluster_id not in rds_cluster_identifiers
        assert neptune_cluster_id not in rds_cluster_identifiers

        # filter for aurora-postgresql
        rds_clusters = aws_client.rds.describe_db_clusters(
            Filters=[{"Name": "engine", "Values": ["aurora-postgresql"]}]
        )["DBClusters"]
        rds_cluster_identifiers = [db["DBClusterIdentifier"] for db in rds_clusters]
        assert rds_cluster_id in rds_cluster_identifiers
        assert docdb_cluster_id not in rds_cluster_identifiers
        assert neptune_cluster_id not in rds_cluster_identifiers

    @markers.aws.validated
    def test_describe_db_instances_with_filter(self, aws_client, infrastructure):
        outputs = infrastructure.get_stack_outputs(stack_name="ClusterStack")
        rds_cluster_id = outputs["ClusterId"]
        docdb_cluster_id = outputs["DocDBClusterId"]
        neptune_cluster_id = outputs["NeptuneClusterId"]

        rds_members = aws_client.rds.describe_db_clusters(DBClusterIdentifier=rds_cluster_id)[
            "DBClusters"
        ][0]["DBClusterMembers"]
        rds_instance_ids = [db["DBInstanceIdentifier"] for db in rds_members]

        neptune_members = aws_client.rds.describe_db_clusters(
            DBClusterIdentifier=neptune_cluster_id
        )["DBClusters"][0]["DBClusterMembers"]
        neptune_instance_ids = [db["DBInstanceIdentifier"] for db in neptune_members]

        docdb_members = aws_client.rds.describe_db_clusters(DBClusterIdentifier=docdb_cluster_id)[
            "DBClusters"
        ][0]["DBClusterMembers"]
        docdb_instance_ids = [db["DBInstanceIdentifier"] for db in docdb_members]

        # describe without filters
        rds_instances = aws_client.rds.describe_db_instances()["DBInstances"]
        neptune_instances = aws_client.neptune.describe_db_instances()["DBInstances"]
        docdb_instances = aws_client.docdb.describe_db_instances()["DBInstances"]

        rds_identifiers = [db["DBInstanceIdentifier"] for db in rds_instances]
        assert all(db_id in rds_identifiers for db_id in rds_instance_ids)
        assert all(db_id in rds_identifiers for db_id in docdb_instance_ids)
        assert all(db_id in rds_identifiers for db_id in neptune_instance_ids)

        neptune_identifiers = [db["DBInstanceIdentifier"] for db in neptune_instances]
        assert all(db_id in neptune_identifiers for db_id in rds_instance_ids)
        assert all(db_id in neptune_identifiers for db_id in docdb_instance_ids)
        assert all(db_id in neptune_identifiers for db_id in neptune_instance_ids)

        docdb_identifiers = [db["DBInstanceIdentifier"] for db in docdb_instances]
        assert all(db_id in docdb_identifiers for db_id in rds_instance_ids)
        assert all(db_id in docdb_identifiers for db_id in docdb_instance_ids)
        assert all(db_id in docdb_identifiers for db_id in neptune_instance_ids)

        # describe with filter neptune
        rds_instances = aws_client.rds.describe_db_instances(
            Filters=[{"Name": "engine", "Values": ["neptune"]}]
        )["DBInstances"]
        rds_identifiers = [db["DBInstanceIdentifier"] for db in rds_instances]
        assert all(db_id not in rds_identifiers for db_id in rds_instance_ids)
        assert all(db_id not in rds_identifiers for db_id in docdb_instance_ids)
        assert all(db_id in rds_identifiers for db_id in neptune_instance_ids)

        # describe with filter docdb
        rds_instances = aws_client.rds.describe_db_instances(
            Filters=[{"Name": "engine", "Values": ["docdb"]}]
        )["DBInstances"]
        rds_identifiers = [db["DBInstanceIdentifier"] for db in rds_instances]
        assert all(db_id not in rds_identifiers for db_id in rds_instance_ids)
        assert all(db_id in rds_identifiers for db_id in docdb_instance_ids)
        assert all(db_id not in rds_identifiers for db_id in neptune_instance_ids)

        # describe with filter mysql
        rds_instances = aws_client.rds.describe_db_instances(
            Filters=[{"Name": "engine", "Values": ["mysql"]}]
        )["DBInstances"]
        rds_identifiers = [db["DBInstanceIdentifier"] for db in rds_instances]
        assert all(db_id not in rds_identifiers for db_id in rds_instance_ids)
        assert all(db_id not in rds_identifiers for db_id in docdb_instance_ids)
        assert all(db_id not in rds_identifiers for db_id in neptune_instance_ids)

        # describe with filter aurora-postgresql + neptune
        rds_instances = aws_client.rds.describe_db_instances(
            Filters=[{"Name": "engine", "Values": ["aurora-postgresql", "neptune"]}]
        )["DBInstances"]
        rds_identifiers = [db["DBInstanceIdentifier"] for db in rds_instances]
        assert all(db_id in rds_identifiers for db_id in rds_instance_ids)
        assert all(db_id not in rds_identifiers for db_id in docdb_instance_ids)
        assert all(db_id in rds_identifiers for db_id in neptune_instance_ids)

        # describe with filter db-cluster-id
        rds_instances = aws_client.rds.describe_db_instances(
            Filters=[{"Name": "db-cluster-id", "Values": [docdb_cluster_id, neptune_cluster_id]}]
        )["DBInstances"]
        rds_identifiers = [db["DBInstanceIdentifier"] for db in rds_instances]
        assert all(db_id not in rds_identifiers for db_id in rds_instance_ids)
        assert all(db_id in rds_identifiers for db_id in docdb_instance_ids)
        assert all(db_id in rds_identifiers for db_id in neptune_instance_ids)

        # describe with filter db-instance-id
        rds_instances = aws_client.rds.describe_db_instances(
            Filters=[{"Name": "db-instance-id", "Values": rds_instance_ids + docdb_instance_ids}]
        )["DBInstances"]
        rds_identifiers = [db["DBInstanceIdentifier"] for db in rds_instances]
        assert all(db_id in rds_identifiers for db_id in rds_instance_ids)
        assert all(db_id in rds_identifiers for db_id in docdb_instance_ids)
        assert all(db_id not in rds_identifiers for db_id in neptune_instance_ids)

    @markers.aws.validated
    def test_rds_lambda(self, aws_client, infrastructure, snapshot):
        outputs = infrastructure.get_stack_outputs(stack_name="ClusterStack")
        rds_helper_fn = outputs["RDSLambdaQueryHelper"]

        create_table = {"sqlQuery": "CREATE TABLE books (id SERIAL, title TEXT, author TEXT);"}

        insert_into = {
            "sqlQuery": "INSERT INTO books VALUES (1, 'How to Anything', 'Jane Doe'), (2, 'Writing effective Tests', 'John Doe')"
        }

        query = {"sqlQuery": "SELECT * FROM books"}

        for q in [create_table, insert_into, query]:
            result = aws_client.lambda_.invoke(
                FunctionName=rds_helper_fn,
                Payload=to_bytes(json.dumps(q)),
            )
            result = json.load(result["Payload"])
            snapshot.match(f"{q['sqlQuery'].split(' ')[0]}", result)
