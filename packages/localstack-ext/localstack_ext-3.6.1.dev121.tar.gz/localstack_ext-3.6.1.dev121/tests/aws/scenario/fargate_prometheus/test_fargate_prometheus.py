import gzip
import json

import aws_cdk as cdk
import pytest
import requests
from localstack.testing.aws.util import is_aws_cloud
from localstack.testing.pytest import markers
from localstack.utils.sync import retry


class TestFargatePrometheus:
    @pytest.fixture(scope="class", autouse=True)
    def infrastructure(self, aws_client, infrastructure_setup):
        infra = infrastructure_setup(namespace="TestFargatePrometheus", force_synth=False)
        stack = cdk.Stack(infra.cdk_app, "FargatePrometheusStack")

        task_definition = cdk.aws_ecs.FargateTaskDefinition(
            stack,
            "FargateTaskDefinition",
            memory_limit_mib=1024,
            cpu=512,
        )

        container = task_definition.add_container(
            "PrometheusContainer",
            container_name="PrometheusAppContainer",
            image=cdk.aws_ecs.ContainerImage.from_registry(name="prom/prometheus"),
            logging=cdk.aws_ecs.LogDriver.aws_logs(stream_prefix="PrometheusApp"),
        )
        container.add_port_mappings(cdk.aws_ecs.PortMapping(container_port=9090))

        lb_service = cdk.aws_ecs_patterns.ApplicationLoadBalancedFargateService(
            stack,
            "FargatePrometheusService",
            service_name="PrometheusService",
            desired_count=1,
            task_definition=task_definition,
            protocol=cdk.aws_elasticloadbalancingv2.ApplicationProtocol.HTTP,
            target_protocol=cdk.aws_elasticloadbalancingv2.ApplicationProtocol.HTTP,
            load_balancer_name="prometheus",
        )
        # doesn't matter on localstack right now, but prevents this working on AWS since "/" will return a 302 status code which it interprets as unhealthy
        lb_service.target_group.configure_health_check(path="/-/healthy")

        cdk.CfnOutput(stack, "LbDnsName", value=lb_service.load_balancer.load_balancer_dns_name)

        with infra.provisioner(skip_teardown=False) as prov:
            yield prov

    @markers.aws.validated
    def test_infra(self, infrastructure):
        outputs = infrastructure.get_stack_outputs("FargatePrometheusStack")
        dns_name = outputs["LbDnsName"]
        if is_aws_cloud():
            endpoint = f"http://{dns_name}/api/v1/query?query=time()"
        else:
            endpoint = f"http://{dns_name}:4566/api/v1/query?query=time()"

        def _check_gzip_compression():
            # borrowed from opensearch test
            # ensure that requests with the "Accept-Encoding": "gzip" header receive gzip compressed responses
            gzip_accept_headers = {"Accept-Encoding": "gzip"}
            gzip_response = requests.get(endpoint, headers=gzip_accept_headers, stream=True)
            # get the raw data, don't let requests decode the response
            raw_gzip_data = b"".join(
                chunk for chunk in gzip_response.raw.stream(1024, decode_content=False)
            )
            # force the gzip decoding here (which would raise an exception if it's not actually gzip)
            decompressed = gzip.decompress(raw_gzip_data)
            assert decompressed
            data = json.loads(decompressed)
            assert data["status"] == "success"

        # might need to retry since localstack doesn't actually perform any health checks
        retry(_check_gzip_compression)
