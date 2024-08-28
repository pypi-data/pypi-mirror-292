import json
import logging
import re
from contextlib import closing
from typing import TYPE_CHECKING, Optional

import botocore.exceptions
import pytest
import requests
import yaml
from kubernetes import client as k8s_client
from kubernetes import config
from kubernetes.stream import stream
from kubernetes.stream.ws_client import WSClient
from localstack import config as localstack_config
from localstack.pro.core.services.eks.k8s_utils import (
    EKS_LOADBALANCER_PORT,
    KubeConfig,
    KubeProviderLocal,
    check_connectivity,
    get_cluster_endpoint,
    get_k8s_client,
)
from localstack.pro.core.services.eks.provider import TAG_LB_PORTS, TAG_VOLUME_MOUNT
from localstack.pro.core.utils.k8s import wait_for_pod_ready
from localstack.testing.aws.util import is_aws_cloud
from localstack.testing.pytest import markers
from localstack.testing.snapshots.transformer_utility import TransformerUtility
from localstack.utils.aws.arns import get_partition
from localstack.utils.docker_utils import DOCKER_CLIENT, get_host_path_for_path_in_docker
from localstack.utils.files import mkdir, save_file
from localstack.utils.functions import run_safe
from localstack.utils.net import is_port_open, wait_for_port_closed
from localstack.utils.strings import short_uid, to_str
from localstack.utils.sync import poll_condition, retry

from tests.aws.fixtures import set_global_service_provider

if TYPE_CHECKING:
    from mypy_boto3_eks.type_defs import ClusterTypeDef

LOG = logging.getLogger(__name__)

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
NGINX_POD_WITH_MOUNT = {
    "apiVersion": "v1",
    "kind": "Pod",
    "metadata": {"name": "pod-with-mount"},
    "spec": {
        "volumes": [{"name": "example-volume", "hostPath": {"path": "/tmp/mount"}}],
        "containers": [
            {
                "image": "nginx",
                "name": "nginx-container",
                "volumeMounts": [{"mountPath": "/tmp", "name": "example-volume"}],
            }
        ],
    },
}

CURL_JOB = {
    "apiVersion": "batch/v1",
    "kind": "Job",
    "metadata": {"name": "curl-job"},
    "spec": {
        "template": {
            "spec": {
                "containers": [
                    {
                        "image": "curlimages/curl:8.3.0",
                        "name": "curl-container",
                        "command": [
                            "curl",
                            "-s",
                            "http://something.localhost.localstack.cloud:4566/_localstack/health",
                        ],
                    }
                ],
                "restartPolicy": "Never",
            },
            "backoffLimit": 4,
        },
    },
}

K8S_DEPL_NGINX = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
  labels:
    app: nginx
spec:
  replicas: 1
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx
        ports:
        - containerPort: 80
"""
K8S_DEPL_ECR_IMAGE = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
  labels:
    app: nginx
spec:
  replicas: 1
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: {repository_uri}
        ports:
        - containerPort: 80
"""

K8S_DEPL_ECR_IMAGE_NODE_AFFINITY = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
  labels:
    app: nginx
spec:
  replicas: 1
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      nodeSelector:
        node_in: group
      containers:
      - name: nginx
        image: {repository_uri}
        ports:
        - containerPort: 80
"""
K8S_SERVICE_NGINX = """
apiVersion: v1
kind: Service
metadata:
  name: nginx
  namespace: default
  labels:
    app: nginx
  annotations:
    service.beta.kubernetes.io/aws-load-balancer-type: "nlb"
spec:
  ports:
  - name: http
    port: 80
    protocol: TCP
    targetPort: 80
  selector:
    app: nginx
  type: ClusterIP
"""
K8S_INGRESS_NGINX = """
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: <name>
  annotations:
    ingress.kubernetes.io/ssl-redirect: "false"
    traefik.ingress.kubernetes.io/router.entrypoints: web,websecure
    # note: currently traefik in k3d doesn't seem to support HTTP/HTTPS multiplexing, hence we
    #  need to create two Ingress in the test (https://github.com/traefik/traefik/issues/8502)
    #tls: traefik.ingress.kubernetes.io/router.tls: "true"
spec:
  tls:
  - secretName: ls-secret-tls
    hosts:
    - eks-8081.localhost.localstack.cloud
    - eks-8082.localhost.localstack.cloud
  rules:
  - host: eks-8081.localhost.localstack.cloud
    http:
      paths:
      - path: /test123
        pathType: Prefix
        backend:
          service:
            name: nginx
            port:
              number: 80
  - host: eks-8082.localhost.localstack.cloud
    http:
      paths:
      - path: /test456
        pathType: Prefix
        backend:
          service:
            name: nginx
            port:
              number: 80
"""


@pytest.fixture(scope="class")
def iam_role(aws_client):
    role_name = f"r-{short_uid()}"
    assume_policy_doc = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Action": "sts:AssumeRole",
                "Principal": {"Service": "eks.amazonaws.com"},
                "Effect": "Allow",
            }
        ],
    }
    assume_policy_doc = json.dumps(assume_policy_doc)
    result = aws_client.iam.create_role(
        RoleName=role_name, AssumeRolePolicyDocument=assume_policy_doc
    )
    role_arn = result["Role"]["Arn"]
    policy_arn = f"arn:{get_partition(aws_client.iam.meta.region_name)}:iam::aws:policy/AmazonEKSClusterPolicy"
    aws_client.iam.attach_role_policy(RoleName=result["Role"]["RoleName"], PolicyArn=policy_arn)

    yield role_arn

    aws_client.iam.detach_role_policy(RoleName=result["Role"]["RoleName"], PolicyArn=policy_arn)
    aws_client.iam.delete_role(RoleName=role_name)


@pytest.fixture(scope="class")
def subnet_ids(aws_client):
    vpc_list = aws_client.ec2.describe_vpcs(Filters=[{"Name": "is-default", "Values": ["true"]}])
    vpc_list = vpc_list["Vpcs"]

    subnet_ids = aws_client.ec2.describe_subnets(
        Filters=[{"Name": "vpc-id", "Values": [vpc_list[0]["VpcId"]]}]
    )["Subnets"]
    return [sub["SubnetId"] for sub in subnet_ids][:2]


@pytest.fixture(scope="class")
def create_eks_cluster(iam_role, set_kube_provider, aws_client, subnet_ids):
    clusters = []

    def _create_cluster(**kwargs):
        if not is_aws_cloud():
            set_kube_provider("k3s")

            cluster_name = f"cluster-{short_uid()}"
            container_dir = f"{localstack_config.dirs.mounted_tmp}/{cluster_name}"
            mkdir(container_dir)
            mount_dir = get_host_path_for_path_in_docker(container_dir)
            kwargs["name"] = cluster_name
            tags = kwargs.setdefault("tags", {})
            tags.update({TAG_VOLUME_MOUNT: f"{mount_dir}:/tmp/mount"})

        cluster_name = kwargs.pop("name", None) or f"c-{short_uid()}"

        aws_client.eks.create_cluster(
            name=cluster_name,
            roleArn=iam_role,
            resourcesVpcConfig={"subnetIds": subnet_ids},
            **kwargs,
        )

        def _created():
            _cluster = aws_client.eks.describe_cluster(name=cluster_name)["cluster"]
            assert _cluster["status"] == "ACTIVE"
            return _cluster

        # Note that it can take a very long time on some systems for the network to stabilize (up to 2+min on MacOS).
        # On real AWS, the EKS cluster creation can take even longer - up to 15+ minutes.
        clusters.append(cluster_name)
        retries = 500 if is_aws_cloud() else 200
        cluster = retry(_created, retries=retries, sleep=2)
        return cluster

    yield _create_cluster

    for cluster_name in clusters:
        aws_client.eks.delete_cluster(name=cluster_name)
        if not is_aws_cloud():
            wait_for_port_closed(EKS_LOADBALANCER_PORT, retries=15, sleep_time=1)


@pytest.fixture(scope="class")
def eks_cluster(create_eks_cluster) -> "ClusterTypeDef":
    return create_eks_cluster(tags={TAG_LB_PORTS: "8081,8082"})


def _local_kube_unavailable():
    port = KubeProviderLocal.DEFAULT_KUBE_PORT
    if not is_port_open(port):
        return True
    try:
        endpoint = get_cluster_endpoint(port, internal=True)
        _test_connectivity(endpoint)
        return False
    except Exception:
        return True


class TestEKSLocal:
    @pytest.fixture(autouse=True)
    def skip_if_kube_unavailable(self):
        # This is not a marker to avoid evaluation on collection time.
        if _local_kube_unavailable():
            pytest.skip("Tests only available for local cluster mode")

    @markers.aws.unknown
    def test_create_cluster(self, aws_client, set_kube_provider):
        set_kube_provider("local")

        client = aws_client.eks
        config.load_kube_config()

        # list clusters
        clusters = client.list_clusters()["clusters"]
        clusters_before = len(clusters)

        # create cluster
        cluster_name = f"c-{short_uid()}"
        cluster = client.create_cluster(name=cluster_name, roleArn="r1", resourcesVpcConfig={})
        cluster = cluster["cluster"]
        assert cluster["name"] == cluster_name

        # list clusters, check size
        clusters = client.list_clusters()["clusters"]
        assert len(clusters) == clusters_before + 1

        # check cluster connectivity
        _test_connectivity(cluster["endpoint"])

        # delete cluster
        client.delete_cluster(name=cluster_name)
        clusters = client.list_clusters()["clusters"]
        assert len(clusters) == clusters_before

    @markers.aws.unknown
    def test_update_cluster_config(self, aws_client, set_kube_provider):
        set_kube_provider("local")

        client = aws_client.eks
        config.load_kube_config()

        # create cluster
        cluster_name = "c-%s" % short_uid()
        cluster = client.create_cluster(name=cluster_name, roleArn="r1", resourcesVpcConfig={})[
            "cluster"
        ]

        # update config
        response = client.update_cluster_config(name=cluster["name"], resourcesVpcConfig={})
        assert response["update"]["status"] == "Successful"

        # clean up
        client.delete_cluster(name=cluster_name)

    @markers.aws.unknown
    def test_manage_node_groups(self, aws_client, set_kube_provider):
        set_kube_provider("local")

        client = aws_client.eks

        # create cluster
        cluster_name = "c-%s" % short_uid()
        client.create_cluster(name=cluster_name, roleArn="r1", resourcesVpcConfig={})

        groups_before = client.list_nodegroups(clusterName=cluster_name)["nodegroups"]

        # create node group
        group_name = "g-%s" % short_uid()
        client.create_nodegroup(
            clusterName=cluster_name, nodegroupName=group_name, subnets=[], nodeRole="role123"
        )

        # describe node group
        result = client.describe_nodegroup(clusterName=cluster_name, nodegroupName=group_name)[
            "nodegroup"
        ]
        assert result["status"] == "ACTIVE"

        # update node group
        client.update_nodegroup_config(clusterName=cluster_name, nodegroupName=group_name)
        client.update_nodegroup_version(
            clusterName=cluster_name, nodegroupName=group_name, version="234"
        )
        result = client.describe_nodegroup(clusterName=cluster_name, nodegroupName=group_name)[
            "nodegroup"
        ]
        assert result["version"] == "234"

        # delete node group
        client.delete_nodegroup(clusterName=cluster_name, nodegroupName=group_name)
        groups_after = client.list_nodegroups(clusterName=cluster_name)["nodegroups"]
        assert len(groups_before) == len(groups_after)

        # clean up
        client.delete_cluster(name=cluster_name)

    @markers.aws.unknown
    def test_create_fargate_profile(self, aws_client, set_kube_provider):
        set_kube_provider("local")

        client = aws_client.eks

        # create cluster
        cluster_name = "c-%s" % short_uid()
        client.create_cluster(name=cluster_name, roleArn="r1", resourcesVpcConfig={})

        profiles_before = client.list_fargate_profiles(clusterName=cluster_name)[
            "fargateProfileNames"
        ]

        # create fargate profile
        prof_name = "prof-%s" % short_uid()
        pod_role = "arn:aws:iam:TODO"
        create_result = client.create_fargate_profile(
            fargateProfileName=prof_name, clusterName=cluster_name, podExecutionRoleArn=pod_role
        )["fargateProfile"]
        profiles_after = client.list_fargate_profiles(clusterName=cluster_name)[
            "fargateProfileNames"
        ]
        assert len(profiles_after) == len(profiles_before) + 1

        # describe fargate profile
        describe_result = client.describe_fargate_profile(
            clusterName=cluster_name, fargateProfileName=prof_name
        )["fargateProfile"]

        for result in [create_result, describe_result]:
            assert result["fargateProfileName"] == prof_name
            assert prof_name in result["fargateProfileArn"]
            assert result["podExecutionRoleArn"] == pod_role

        # delete profile
        client.delete_fargate_profile(clusterName=cluster_name, fargateProfileName=prof_name)

        # try to fetch deleted profile (should raise exception)
        with pytest.raises(botocore.exceptions.ClientError):
            client.describe_fargate_profile(
                clusterName=cluster_name,
                fargateProfileName=prof_name,
            )

        # clean up
        client.delete_cluster(name=cluster_name)


class TestEKS:
    @markers.aws.validated
    @pytest.mark.parametrize("kube_version", ["1.19", "1.20", "1.21", "1.22", "1.23"])
    def test_get_parameters_eks_amis(self, kube_version, aws_client):
        # ensure that EKS has been initialized
        aws_client.eks.list_clusters()
        # fetch AMIs as params from SSM
        param_name = (
            f"/aws/service/eks/optimized-ami/{kube_version}/amazon-linux-2/recommended/image_id"
        )
        param = aws_client.ssm.get_parameter(Name=param_name)["Parameter"]
        assert param["Type"] == "String"
        assert re.match("^ami-.*", param["Value"])

    @markers.aws.unknown
    def test_additional_amis_present(self, aws_client):
        result = aws_client.ec2.describe_images(
            Filters=[{"Name": "name", "Values": ["amazon-eks-node-1.20-v*"]}], Owners=["amazon"]
        )
        images = result["Images"]
        assert len(images) >= 1
        assert "amazon" in [image.get("ImageOwnerAlias") for image in images]
        assert "amazon-eks-node-1.20-v1" in [image.get("Name") for image in images]

    @pytest.mark.skip(reason="switching providers is currently not supported")
    @markers.aws.unknown
    def test_mocked_responses(self, aws_client):
        with set_global_service_provider("eks", "mock"):
            clusters = []
            # assume that creation of 100 clusters can only work in mocked mode
            for i in range(10):
                cluster_name = f"c-{short_uid()}"
                aws_client.eks.create_cluster(
                    name=cluster_name, roleArn="r1", resourcesVpcConfig={}
                )
                clusters.append(cluster_name)

            created_clusters = set(aws_client.eks.list_clusters()["clusters"])
            for cluster in clusters:
                assert cluster in created_clusters
                cluster = aws_client.eks.describe_cluster(name=cluster_name)
                assert "arn" in cluster["cluster"]
                assert cluster["cluster"]["status"] == "ACTIVE"

            for cluster in clusters:
                aws_client.eks.delete_cluster(name=cluster)

    @pytest.mark.parametrize("invalid_k8s_version", ["test", "100.1", "1.60", "0"])
    @markers.aws.validated
    def test_invalid_k8s_versions(
        self, aws_client, iam_role, invalid_k8s_version, snapshot, subnet_ids
    ):
        snapshot.add_transformer(snapshot.transform.key_value("clusterName"))
        cluster_name = f"test-cluster-{short_uid()}"
        with pytest.raises(aws_client.eks.exceptions.ClientError) as e:
            aws_client.eks.create_cluster(
                name=cluster_name,
                roleArn=iam_role,
                resourcesVpcConfig={"subnetIds": subnet_ids},
                version=invalid_k8s_version,
            )
        snapshot.match("invalid-k8s-version-exception", e.value.response)


class TestK3SCluster:
    def get_kube_config(self, cluster: "ClusterTypeDef") -> KubeConfig:
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
            "contexts": [
                {"name": "default", "context": {"cluster": cluster_name, "user": "default"}}
            ],
            "users": [
                {
                    "name": "default",
                    "user": {},
                }
            ],
        }
        return KubeConfig(kube_config)

    @markers.aws.only_localstack
    @markers.skip_offline
    def test_create_app_in_k3s_cluster(self, eks_cluster):
        self._test_eks_integrations(K8S_DEPL_NGINX, eks_cluster, check_lb_ports=True)

    @markers.aws.only_localstack
    @markers.skip_offline
    def test_ecr_eks_integration(self, create_repository, eks_cluster, aws_client):
        repo_name = f"test-repo-{short_uid()}"
        repo_uri = create_repository(repositoryName=repo_name)["repository"]["repositoryUri"]
        DOCKER_CLIENT.pull_image("nginx")
        DOCKER_CLIENT.tag_image("nginx", repo_uri)
        DOCKER_CLIENT.push_image(repo_uri)
        deployment_config = K8S_DEPL_ECR_IMAGE.format(repository_uri=repo_uri)
        self._test_eks_integrations(deployment_config, eks_cluster)

    @markers.aws.only_localstack
    @markers.skip_offline
    def test_ecr_eks_integration_multiple_nodes(
        self, create_repository, eks_cluster, aws_client, iam_role, cleanups
    ):
        repo_name = f"test-repo-{short_uid()}"
        nodegroup_name = f"group-{short_uid()}"
        aws_client.eks.create_nodegroup(
            clusterName=eks_cluster["name"],
            nodeRole=iam_role,
            nodegroupName=nodegroup_name,
            subnets=["0.0.0.0/0"],
            scalingConfig={"desiredSize": 1},
            labels={"node_in": "group"},
        )
        cleanups.append(
            lambda: aws_client.eks.delete_nodegroup(
                clusterName=eks_cluster["name"], nodegroupName=nodegroup_name
            )
        )
        repo_uri = create_repository(repositoryName=repo_name)["repository"]["repositoryUri"]
        DOCKER_CLIENT.pull_image("nginx")
        DOCKER_CLIENT.tag_image("nginx", repo_uri)
        DOCKER_CLIENT.push_image(repo_uri)
        deployment_config = K8S_DEPL_ECR_IMAGE_NODE_AFFINITY.format(repository_uri=repo_uri)
        self._test_eks_integrations(deployment_config, eks_cluster)

    def _test_eks_integrations(self, deployment_config, cluster, check_lb_ports=False):
        # create cluster
        kube_config = self.get_kube_config(cluster)
        _test_connectivity(kube_config)
        lb_port1 = EKS_LOADBALANCER_PORT
        lb_port2 = EKS_LOADBALANCER_PORT + 1

        # test deploying a simple app
        ns = "default"
        api_client = _get_k8s_client(kube_config)
        core_client = k8s_client.CoreV1Api(api_client)
        apps_client = k8s_client.AppsV1Api(api_client)
        net_client = k8s_client.NetworkingV1Api(api_client)

        try:
            # create deployment
            depl = yaml.safe_load(deployment_config)
            resp_depl = apps_client.create_namespaced_deployment(body=depl, namespace=ns)
            assert resp_depl.metadata.name == "nginx-deployment"
            # create service
            service = yaml.safe_load(K8S_SERVICE_NGINX)
            resp_service = core_client.create_namespaced_service(body=service, namespace=ns)
            assert resp_service.metadata.name == "nginx"

            # create ingress (HTTP)
            ingress = K8S_INGRESS_NGINX.replace("<name>", "nginx")
            ingress = yaml.safe_load(ingress)
            resp_ingress = net_client.create_namespaced_ingress(body=ingress, namespace=ns)
            assert resp_ingress.metadata.name == "nginx"
            # create ingress (HTTPS)
            ingress = K8S_INGRESS_NGINX.replace("<name>", "nginx-ssl").replace("#tls: ", "")
            ingress = yaml.safe_load(ingress)
            resp_ingress = net_client.create_namespaced_ingress(body=ingress, namespace=ns)
            assert resp_ingress.metadata.name == "nginx-ssl"

            def _check_invoke(port, path):
                # add header to support host-based ingress routing
                headers = {"Host": f"eks-{port}.localhost.localstack.cloud:{port}"}
                # run load balancer requests for HTTP/HTTPS endpoint
                for protocol in ["http", "https"]:
                    base_url = get_cluster_endpoint(port, internal=True, protocol=protocol)
                    url = f"{base_url}{path}"
                    response = requests.get(url, verify=False, headers=headers)
                    assert "nginx" in to_str(response.content), f"error: {response.content}"

            # Note that it can take some time for the app (nginx server) to be fully up and running
            retry(lambda: _check_invoke(lb_port1, "/test123"), retries=200, sleep=2)

            if check_lb_ports:
                with pytest.raises(Exception) as exc:
                    _check_invoke(lb_port1, "/test456")
                exc.match("404 page not found")
                _check_invoke(lb_port2, "/test456")
                with pytest.raises(Exception) as exc:
                    _check_invoke(lb_port2, "/test123")
                exc.match("404 page not found")

        finally:
            run_safe(lambda: net_client.delete_namespaced_ingress(name="nginx", namespace=ns))
            run_safe(lambda: net_client.delete_namespaced_ingress(name="nginx-ssl", namespace=ns))
            run_safe(lambda: core_client.delete_namespaced_service(name="nginx", namespace=ns))
            run_safe(
                lambda: apps_client.delete_namespaced_deployment(
                    name="nginx-deployment", namespace=ns
                )
            )

    # test shamelessly inspired from https://github.com/kubernetes-client/python/blob/master/examples/pod_exec.py
    @markers.skip_offline
    @markers.aws.unknown
    def test_eks_pod_exec(self, eks_cluster):
        """Running a nginx pod and exec'ing into it to run some commands, to check if proxy behaves correctly"""
        kube_config = self.get_kube_config(eks_cluster)
        _test_connectivity(kube_config)
        ns = "default"
        pod_name = "nginx-pod"
        api_client = _get_k8s_client(kube_config)
        core_client = k8s_client.CoreV1Api(api_client)
        try:
            core_client.create_namespaced_pod(namespace=ns, body=NGINX_POD)

            def check_pod_state():
                resp = core_client.read_namespaced_pod(name=pod_name, namespace=ns)
                return resp.status.phase == "Running"

            # wait until pod is ready
            poll_condition(check_pod_state, timeout=20)

            # running exec
            message = "We are no strangers to"
            exec_command = ["/bin/sh", "-c", f"echo {message}"]
            resp = stream(
                core_client.connect_get_namespaced_pod_exec,
                name=pod_name,
                namespace=ns,
                command=exec_command,
                stderr=True,
                stdin=False,
                stdout=True,
                tty=False,
            )
            assert resp.strip() == message
            # try more interactive commands
            exec_command = ["/bin/sh"]
            resp_client: WSClient = stream(
                core_client.connect_get_namespaced_pod_exec,
                name=pod_name,
                namespace=ns,
                command=exec_command,
                stderr=True,
                stdin=True,
                stdout=True,
                tty=False,
                _preload_content=False,
            )

            command = f"echo {message}\n"
            with closing(resp_client):
                resp_client.write_stdin(command)

                def assert_echo_response():
                    resp_client.update(timeout=1)
                    echo_response = resp_client.read_stdout()
                    assert echo_response.strip() == message

                retry(assert_echo_response)
        finally:
            core_client.delete_namespaced_pod(name=pod_name, namespace=ns)

    @markers.aws.only_localstack
    @markers.skip_offline
    def test_volume_mount(self, eks_cluster):
        """Running a nginx pod and exec-ing into it to check the volume mount"""
        kube_config = self.get_kube_config(eks_cluster)
        mount_dir = _get_mount_dir(eks_cluster)
        save_file(f"{mount_dir}/foo.txt", "foo")
        _test_connectivity(kube_config)
        ns = "default"
        pod_name = NGINX_POD_WITH_MOUNT["metadata"]["name"] = f"pod-{short_uid()}"
        api_client = _get_k8s_client(kube_config)
        core_client = k8s_client.CoreV1Api(api_client)
        try:
            core_client.create_namespaced_pod(namespace=ns, body=NGINX_POD_WITH_MOUNT)

            def check_pod_state():
                resp = core_client.read_namespaced_pod(name=pod_name, namespace=ns)
                return resp.status.phase == "Running"

            # wait until pod is ready
            poll_condition(check_pod_state, timeout=60)

            # running exec
            exec_command = ["/bin/sh", "-c", "ls /tmp"]
            resp = stream(
                core_client.connect_get_namespaced_pod_exec,
                name=pod_name,
                namespace=ns,
                command=exec_command,
                stderr=True,
                stdin=False,
                stdout=True,
                tty=False,
            )
            assert "foo.txt" in resp.strip()
        finally:
            core_client.delete_namespaced_pod(name=pod_name, namespace=ns)

    @markers.aws.only_localstack
    @markers.skip_offline
    def test_localstack_communication_from_pod(self, eks_cluster, cleanups):
        """Test if the localstack container is reachable from a pod"""
        # has to be executed in a container
        kube_config = self.get_kube_config(eks_cluster)
        ns = "default"
        job_name = "curl-job"
        api_client = _get_k8s_client(kube_config)
        core_client = k8s_client.CoreV1Api(api_client)
        batch_client = k8s_client.BatchV1Api(api_client)
        batch_client.create_namespaced_job(namespace=ns, body=CURL_JOB)
        cleanups.append(lambda: batch_client.delete_namespaced_job(namespace=ns, name=job_name))

        def check_job_state():
            resp = batch_client.read_namespaced_job_status(name=job_name, namespace=ns)
            return resp.status.succeeded is not None

        # wait until job succeeded
        assert poll_condition(check_job_state, timeout=20)

        pods = core_client.list_namespaced_pod(namespace=ns, label_selector=f"job-name={job_name}")
        pod_name = pods.items[0].metadata.name
        logs = core_client.read_namespaced_pod_log(name=pod_name, namespace=ns)
        assert "services" in logs

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(
        paths=[
            "$..certificateAuthority",
            "$..endpoint",
            "$..identity",
            "$..kubernetesNetworkConfig",
            "$..logging",
            "$..resourcesVpcConfig",
            "$..roleArn",
            "$..tags",
        ]
    )
    def test_cluster_default_version(self, eks_cluster, snapshot):
        snapshot.add_transformer(TransformerUtility.jsonpath("$..cluster_details.name", "name"))

        snapshot.match("cluster_details", eks_cluster)

    @markers.aws.only_localstack
    @markers.skip_offline
    @markers.only_in_docker
    @pytest.mark.skipif(
        condition=localstack_config.DNS_ADDRESS == 0,
        reason="Requires transparent endpoint injection to be enabled",
    )
    def test_pull_public_s3_image_with_transparent_endpoint_injection(self, eks_cluster, cleanups):
        kube_config = self.get_kube_config(eks_cluster)
        api_client = _get_k8s_client(kube_config)
        core_client = k8s_client.CoreV1Api(api_client)

        pod_name = f"nginx-{short_uid()}"
        spec = {
            "apiVersion": "v1",
            "kind": "Pod",
            "metadata": {
                "name": pod_name,
                "labels": {
                    "app": "nginx",
                },
            },
            "spec": {
                "containers": [
                    {
                        "name": "nginx",
                        "image": "registry.k8s.io/nginx:1.7.9",
                        "ports": [
                            {"containerPort": 80},
                        ],
                    },
                ],
            },
        }

        ns = "default"
        core_client.create_namespaced_pod(namespace=ns, body=spec)
        cleanups.append(lambda: core_client.delete_namespaced_pod(name=pod_name, namespace=ns))

        wait_for_pod_ready(v1_client=core_client, namespace=ns, pod_name=pod_name, timeout=60)


def _get_k8s_client(cluster_info):
    return get_k8s_client(cluster_info, internal=False)


# HELPER FUNCTIONS
def _test_connectivity(cluster_config):
    if isinstance(cluster_config, dict):
        cluster_config = KubeConfig(cluster_config)
    check_connectivity(cluster_config, internal=False)


def _get_mount_dir(cluster: "ClusterTypeDef") -> Optional[str]:
    if TAG_VOLUME_MOUNT in cluster["tags"]:
        return f"{localstack_config.dirs.mounted_tmp}/{cluster['name']}"
    return None
