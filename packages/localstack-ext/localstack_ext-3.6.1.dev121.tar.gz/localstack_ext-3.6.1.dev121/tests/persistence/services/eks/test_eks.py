from typing import TYPE_CHECKING

import pytest
from localstack.pro.core import config as config_ext
from localstack.pro.core.services.eks.k8s_utils import (
    KubeConfig,
    get_k8s_client,
)
from localstack.testing.pytest import markers
from localstack.utils.sync import poll_condition

if TYPE_CHECKING:
    from mypy_boto3_eks.type_defs import ClusterTypeDef

from kubernetes import client as k8s_client
from localstack.utils.strings import short_uid

NGINX_POD = {
    "apiVersion": "v1",
    "kind": "Pod",
    "metadata": {"name": "nginx-pod"},
    "spec": {
        "containers": [
            {
                "image": "nginx",
                "name": "nginx-container",
            }
        ]
    },
}


# XXX duplicated from from integration tests
def get_kube_config(cluster: "ClusterTypeDef") -> KubeConfig:
    cluster_name = cluster["name"]
    cert_data = cluster.get("certificateAuthority", {}).get("data") or ""
    kube_config = {
        "kind": "Config",
        "current-context": "default",
        "clusters": [
            {
                "name": cluster_name,
                "cluster": {
                    "certificate-authority-data": cert_data,
                    "server": cluster["endpoint"],
                },
            }
        ],
        "contexts": [{"name": "default", "context": {"cluster": cluster_name, "user": "default"}}],
        "users": [
            {
                "name": "default",
                "user": {},
            }
        ],
    }
    return KubeConfig(kube_config)


@pytest.mark.skipif(
    condition=config_ext.EKS_K8S_PROVIDER != "k3s",
    reason="TODO",
)
@markers.snapshot.skip_snapshot_verify(
    paths=["$..cluster.endpoint"]
)  # the port of the endpoint can differ
@pytest.mark.skip(reason="Creating a namespace returns a 409.")
def test_eks_create_and_describe_cluster(persistence_validations, snapshot, aws_client):
    cluster_name = f"cluster-{short_uid()}"
    role_arn = "arn:aws:iam::000000000000:role/eks-role"

    # Create EKS Cluster
    aws_client.eks.create_cluster(name=cluster_name, roleArn=role_arn, resourcesVpcConfig={})

    # Describe EKS Cluster
    def validate_describe_cluster():
        aws_client.eks.get_waiter("cluster_active").wait(name=cluster_name)
        snapshot.match("describe_cluster", aws_client.eks.describe_cluster(name=cluster_name))

    def validate_connectivity():
        aws_client.eks.get_waiter("cluster_active").wait(name=cluster_name)
        cluster_details = aws_client.eks.describe_cluster(name=cluster_name)["cluster"]
        kube_config = get_kube_config(cluster_details)

        ns = "default"
        pod_name = "nginx-pod"
        api_client = get_k8s_client(kube_config)
        core_client = k8s_client.CoreV1Api(api_client)
        # fixme: this returns a 409. Works fine when the test runs in isolation. It only happens when the entire suite
        #   runs.
        core_client.create_namespaced_pod(namespace=ns, body=NGINX_POD)

        def check_pod_state():
            resp = core_client.read_namespaced_pod(name=pod_name, namespace=ns)
            return resp.status.phase == "Running"

        # wait until pod is ready
        poll_condition(check_pod_state, timeout=20)

    persistence_validations.register(validate_describe_cluster)
    persistence_validations.register(validate_connectivity)
