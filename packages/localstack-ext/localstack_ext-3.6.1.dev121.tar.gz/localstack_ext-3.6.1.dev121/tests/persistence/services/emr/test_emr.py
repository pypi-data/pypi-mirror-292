import pytest
from localstack.utils.strings import short_uid


@pytest.mark.skip(reason="The cluster is not created hence we cannot technically persist it")
def test_emr_create_and_list_clusters(persistence_validations, snapshot, aws_client):
    # Create EMR Cluster
    cluster_name = f"my-emr-cluster-{short_uid()}"
    response = aws_client.emr.run_job_flow(
        Name=cluster_name,
        ReleaseLabel="emr-5.9.0",
        Instances={
            "InstanceGroups": [
                {
                    "InstanceRole": "MASTER",
                    "InstanceType": "m4.large",
                    "InstanceCount": 1,
                },
                {
                    "InstanceRole": "CORE",
                    "InstanceType": "m4.large",
                    "InstanceCount": 1,
                },
            ]
        },
    )

    # List EMR Clusters
    def validate_list_clusters():
        snapshot.match(
            "list_clusters",
            aws_client.emr.list_clusters(
                ClusterStates=["STARTING", "BOOTSTRAPPING", "RUNNING", "WAITING"]
            ),
        )

    persistence_validations.register(validate_list_clusters)
