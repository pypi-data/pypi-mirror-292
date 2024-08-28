import pytest
from localstack.utils.strings import short_uid


@pytest.mark.skip(reason="The cluster is not created hence we cannot technically persist it")
def test_describe_redshift_cluster(persistence_validations, snapshot, aws_client):
    redshift_cluster_identifier = f"redshiftcluster-{short_uid()}"
    redshift_database_name = "db1"
    redshift_username = "crawlertestredshiftusername"
    redshift_password = "crawlertestredshiftpassword"

    # Create Redshift Cluster
    aws_client.redshift.create_cluster(
        ClusterIdentifier=redshift_cluster_identifier,
        DBName=redshift_database_name,
        MasterUsername=redshift_username,
        MasterUserPassword=redshift_password,
        NodeType="n1",
    )

    # Describe Redshift Cluster
    def validate_describe_cluster():
        snapshot.match(
            "describe_cluster",
            aws_client.redshift.describe_clusters(ClusterIdentifier=redshift_cluster_identifier),
        )

    persistence_validations.register(validate_describe_cluster)
