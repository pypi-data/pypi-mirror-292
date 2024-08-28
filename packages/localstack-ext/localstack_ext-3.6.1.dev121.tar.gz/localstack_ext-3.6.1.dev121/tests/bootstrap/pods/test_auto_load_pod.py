import logging

from localstack.aws.connect import connect_to
from localstack.pro.core.bootstrap.pods_client import StateService
from localstack.utils.container_utils.container_client import VolumeBind
from localstack.utils.sync import poll_condition

LOG = logging.getLogger(__name__)


def test_pod_auto_load(pro_container, wait_for_localstack_ready, tmp_path, aws_client, monkeypatch):
    pod_dir = tmp_path / "init-pods.d"
    pod_dir.mkdir()

    pro_container.config.volumes.add(
        VolumeBind(str(pod_dir), "/etc/localstack/init-pods.d"),
    )
    pro_container.config.env_vars["PERSISTENCE"] = "0"

    def _get_client(_running_container):
        from localstack import config as localstack_config

        port = _running_container.config.env_vars["GATEWAY_LISTEN"]
        endpoint = f"http://localhost{port}"
        monkeypatch.setattr(localstack_config, "external_service_url", lambda: endpoint)
        aws_client = connect_to(endpoint_url=endpoint)
        return aws_client.sqs

    pod_path = f"file://{pod_dir}/auto-load-pod"
    with pro_container.start() as running_container:
        wait_for_localstack_ready(running_container, timeout=120)
        queue_url = _get_client(running_container).create_queue(QueueName="test-auto-load")[
            "QueueUrl"
        ]
        pod_client = StateService()
        pod_client.export_pod(pod_path)

    def _check_queue() -> bool:
        try:
            return (
                _get_client(running_container).get_queue_url(QueueName="test-auto-load")["QueueUrl"]
                == queue_url
            )
        except Exception:
            return False

    with pro_container.start() as running_container:
        wait_for_localstack_ready(running_container, timeout=120)

        assert poll_condition(_check_queue, interval=1, timeout=20)


def test_startup_activate_pro_0(pro_container, wait_for_localstack_ready):
    pro_container.config.env_vars["ACTIVATE_PRO"] = "0"

    with pro_container.start() as running_container:
        wait_for_localstack_ready(running_container, timeout=120)
        logs = running_container.get_logs()
        assert "Ready" in logs
