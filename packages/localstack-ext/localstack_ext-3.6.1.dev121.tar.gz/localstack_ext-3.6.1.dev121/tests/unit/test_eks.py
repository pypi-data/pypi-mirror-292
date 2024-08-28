import pytest
from localstack.pro.core.services.eks.k8s_utils import KubeProviderLocal


def test_select_default_cluster_in_kube_config():
    kube_config = {
        "kind": "Config",
        "clusters": [
            {"name": "c2", "cluster": {}},
            {"name": "c3"},
            {"name": "c1"},
        ],
        "contexts": [
            {"name": "ctx1", "context": {"cluster": "c1", "user": "u1"}},
            {"name": "ctx3", "context": {"cluster": "c3", "user": "u1"}},
            {"name": "ctx2", "context": {"cluster": "c2", "user": "u1"}},
        ],
        "users": [
            {
                "name": "u1",
                "user": {},
            }
        ],
    }

    for ctx in [1, 2, 3]:
        config = {"current-context": f"ctx{ctx}", **kube_config}
        result = KubeProviderLocal.select_current_cluster_in_kube_config(config)
        clusters = result["clusters"]
        assert len(clusters) == 1
        assert clusters[0]["name"] == f"c{ctx}"

    with pytest.raises(Exception):
        KubeProviderLocal.select_current_cluster_in_kube_config(kube_config)
    with pytest.raises(Exception):
        config = {"current-context": "invalid", **kube_config}
        KubeProviderLocal.select_current_cluster_in_kube_config(config)
