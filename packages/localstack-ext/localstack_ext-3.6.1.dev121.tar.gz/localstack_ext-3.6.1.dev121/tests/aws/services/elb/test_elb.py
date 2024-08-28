import json
import logging
import re
import socket

import pytest
import requests
from botocore.exceptions import ClientError
from localstack import config
from localstack.config import in_docker
from localstack.pro.core.aws.api.elbv2 import LoadBalancerAttributes
from localstack.testing.aws.util import is_aws_cloud
from localstack.testing.pytest import markers
from localstack.utils.aws.arns import lambda_function_name
from localstack.utils.json import json_safe
from localstack.utils.strings import short_uid, to_str
from localstack.utils.sync import retry
from werkzeug import Request, Response

TEST_LAMBDA_ECHO = """
import json
def handler(event, context):
    print(event)
    return {
        "statusCode": 200,
        "body": json.dumps(event)
    }
"""

ELB_LAMBDA = """
def handler(event, context):
    return {
        "isBase64Encoded": False,
        "statusCode": 200,
        "statusDescription": "200 OK",
        "headers": {
            "Set-cookie": "cookies",
            "Content-Type": "application/json"
        },
        "body": "%s"
    }
"""

LOG = logging.getLogger(__name__)


@pytest.fixture
def elbv2_create_load_balancer(ec2_create_security_group, aws_client):
    elbv2_load_balancers = []

    def factory(**kwargs):
        if "Name" not in kwargs:
            kwargs["Name"] = f"elb-{short_uid()}"
        if "Subnets" not in kwargs:
            kwargs["Subnets"] = [
                s["SubnetId"] for s in aws_client.ec2.describe_subnets()["Subnets"]
            ]

        # default Type is "application"
        if kwargs.get("Type") in ("application", None) and "SecurityGroups" not in kwargs:
            vpcs = aws_client.ec2.describe_vpcs(Filters=[{"Name": "isDefault", "Values": ["true"]}])
            vpc_id = vpcs["Vpcs"][0]["VpcId"]

            sg_name = f"alb-sg-{short_uid()}"
            security_group = ec2_create_security_group(
                VpcId=vpc_id, GroupName=sg_name, Description="Security group for ALB", ports=[80]
            )
            sg_id = security_group["GroupId"]
            kwargs["SecurityGroups"] = [sg_id]

        response = aws_client.elbv2.create_load_balancer(**kwargs)
        elbv2_load_balancers.append(response["LoadBalancers"][0]["LoadBalancerArn"])
        return response

    yield factory

    for load_balancer_arn in elbv2_load_balancers:
        try:
            aws_client.elbv2.delete_load_balancer(LoadBalancerArn=load_balancer_arn)
        except Exception as e:
            LOG.debug(f"Error cleaning up elbv2 load balancer: {load_balancer_arn}, {e}")


@pytest.fixture
def elbv2_create_target_group(aws_client):
    target_group_arns = []

    def factory(**kwargs):
        result = aws_client.elbv2.create_target_group(**kwargs)
        arn = result["TargetGroups"][0]["TargetGroupArn"]
        target_group_arns.append(arn)
        return result

    yield factory

    for arn in target_group_arns:
        try:
            aws_client.elbv2.delete_target_group(TargetGroupArn=arn)
        except Exception as e:
            LOG.debug("Unable to delete target group %s: %s", arn, e)


@pytest.fixture
def ec2_create_security_group(aws_client):
    ec2_sgs = []

    def factory(ports=None, **kwargs):
        if "GroupName" not in kwargs:
            kwargs["GroupName"] = f"sg-{short_uid()}"
        security_group = aws_client.ec2.create_security_group(**kwargs)

        permissions = [
            {
                "FromPort": port,
                "IpProtocol": "tcp",
                "IpRanges": [{"CidrIp": "0.0.0.0/0"}],
                "ToPort": port,
            }
            for port in ports or []
        ]
        if "VpcId" not in kwargs:
            # default vpc group can use the group-name
            aws_client.ec2.authorize_security_group_ingress(
                GroupName=kwargs["GroupName"],
                IpPermissions=permissions,
            )
        else:
            # non default, has to use the group-id
            aws_client.ec2.authorize_security_group_ingress(
                GroupId=security_group["GroupId"],
                IpPermissions=permissions,
            )

        ec2_sgs.append(security_group["GroupId"])
        return security_group

    yield factory

    for sg_group_id in ec2_sgs:
        try:
            aws_client.ec2.delete_security_group(GroupId=sg_group_id)
        except Exception as e:
            LOG.debug(f"Error cleaning up ec2 security group: {sg_group_id}, {e}")


@pytest.fixture()
def elb_transformers(snapshot):
    snapshot.add_transformer(
        [
            snapshot.transform.key_value("CanonicalHostedZoneId"),
            snapshot.transform.key_value("DNSName"),
            snapshot.transform.key_value("LoadBalancerArn"),
            snapshot.transform.key_value("LoadBalancerName"),
            snapshot.transform.key_value("VpcId"),
            snapshot.transform.jsonpath("$..LoadBalancers[0].SecurityGroups[0]", "sg-id"),
        ]
    )


@pytest.fixture
def add_target_group(default_vpc, aws_client):
    target_groups = []

    def _create(
        tg_name: str, tg_type: str, tg_id: str = None, http_port: int = 1, vpc_id: str = None
    ) -> str:
        vpc_id = vpc_id or default_vpc["VpcId"]

        # create target group
        is_ip_target = tg_type in ("instance", "ip")
        kwargs = {"Protocol": "HTTP", "Port": http_port, "VpcId": vpc_id} if is_ip_target else {}
        result = aws_client.elbv2.create_target_group(
            Name=tg_name, TargetType=tg_type, HealthCheckEnabled=True, **kwargs
        )
        tg_arn = result["TargetGroups"][0]["TargetGroupArn"]

        # provide required IAM permissions
        if tg_type == "lambda":
            aws_client.lambda_.add_permission(
                FunctionName=lambda_function_name(tg_id),
                StatementId=f"c{short_uid()}",
                Action="lambda:InvokeFunction",
                Principal="elasticloadbalancing.amazonaws.com",
                SourceArn=tg_arn,
            )

        # register IP targets for group
        tg_id = tg_id or "127.0.0.1"
        target_details = {"Port": http_port} if is_ip_target else {}
        targets = [{"Id": tg_id, "AvailabilityZone": "all", **target_details}]
        aws_client.elbv2.register_targets(TargetGroupArn=tg_arn, Targets=targets)

        target_groups.append(tg_arn)
        return tg_arn

    yield _create

    for tg_arn in target_groups:
        try:
            aws_client.elbv2.delete_target_group(TargetGroupArn=tg_arn)
        except Exception as e:
            LOG.debug("Unable to delete target group %s: %s", tg_arn, e)


@pytest.fixture
def elbv2_create_rule(aws_client):
    rules = []

    def _create(**kwargs):
        result = aws_client.elbv2.create_rule(**kwargs)
        for rule in result["Rules"]:
            rules.append(rule["RuleArn"])
        return result

    yield _create

    for rule in rules:
        try:
            aws_client.elbv2.delete_rule(RuleArn=rule)
        except Exception as e:
            LOG.debug("Unable to delete rule %s: %s", rule, e)


@pytest.fixture
def elbv2_create_listener(aws_client):
    listeners = []

    def _create(**kwargs):
        result = aws_client.elbv2.create_listener(**kwargs)
        for listener in result["Listeners"]:
            listeners.append(listener["ListenerArn"])
        return result

    yield _create

    for listener in listeners:
        try:
            aws_client.elbv2.delete_listener(ListenerArn=listener)
        except Exception as e:
            LOG.debug("Unable to delete listener %s: %s", listener, e)


@pytest.fixture
def http_echo_server(httpserver):
    def _echo(request: Request, **_) -> Response:
        result = {
            "data": request.data or "{}",
            "headers": dict(request.headers),
            "request_url": request.url,
        }
        response_body = json.dumps(json_safe(result))
        return Response(response_body, headers={"x-echo-server": str(id(httpserver))})

    httpserver.expect_request(re.compile("/.*")).respond_with_handler(_echo)
    return httpserver


def create_dict_from_attributes_map(attributes_map: LoadBalancerAttributes):
    return {attr["Key"]: attr["Value"] for attr in attributes_map}


def wait_until_hostname_resolves(hostname: str):
    def _resolve_hostname():
        assert socket.gethostbyname_ex(hostname)

    retry(_resolve_hostname, retries=100, sleep=3)


class TestELB:
    @markers.only_on_amd64
    @markers.snapshot.skip_snapshot_verify(
        paths=[
            # LocalStack might add the port depending on the setup to the host
            "$..headers.host",
            # TODO: AWS adds those 4 headers to the lambda payload
            "$..headers.x-amzn-trace-id",
            "$..headers.x-forwarded-for",
            "$..headers.x-forwarded-port",
            "$..headers.x-forwarded-proto",
        ]
    )
    @markers.aws.validated
    def test_load_balancing(
        self,
        create_lambda_function,
        elbv2_create_load_balancer,
        elbv2_create_rule,
        elbv2_create_listener,
        elb_transformers,
        add_target_group,
        http_echo_server,
        snapshot,
        aws_client,
    ):
        elb_name = f"elb-{short_uid()}"
        tg_ip_name = f"tg-ip-{short_uid()}"
        tg_lambda_name = f"tg-lambda-{short_uid()}"
        fn_name = f"elb-tgt-{short_uid()}"
        snapshot.add_transformers_list(
            [
                snapshot.transform.key_value("x-amzn-trace-id"),
                snapshot.transform.key_value("x-forwarded-for"),
            ]
        )

        # get subnets
        subnets = [s["SubnetId"] for s in aws_client.ec2.describe_subnets()["Subnets"]]

        # create load balancer
        result = elbv2_create_load_balancer(Name=elb_name, Subnets=subnets)
        assert result.get("LoadBalancers")
        elb_arn = result["LoadBalancers"][0]["LoadBalancerArn"]
        elb_host = result["LoadBalancers"][0]["DNSName"]
        # we do not need to snapshot the whole CreateLoadBalancer call, but the DNSName and LoadBalancerName fields
        # are useful for reference replacing
        snapshot.match(
            "load-balancer-dns-name",
            {
                "DNSName": result["LoadBalancers"][0]["DNSName"],
                "LoadBalancerName": result["LoadBalancers"][0]["LoadBalancerName"],
            },
        )

        # deploy test Lambda
        lambda_resp = create_lambda_function(handler_file=TEST_LAMBDA_ECHO, func_name=fn_name)
        lambda_arn = lambda_resp["CreateFunctionResponse"]["FunctionArn"]

        # add target groups
        test_port = http_echo_server.port
        tg_lambda_arn = add_target_group(tg_lambda_name, "lambda", tg_id=lambda_arn)
        snapshot.add_transformer(snapshot.transform.regex(tg_lambda_arn, "<lambda-target-arn>"))
        if not is_aws_cloud():
            # note: we can only add target groups for internal IP ranges (tests need to be extended for snapshotting)
            tg_ip_arn = add_target_group(tg_ip_name, "ip", http_port=test_port)

        def _assert_tg_error(key, **kwargs):
            with pytest.raises(ClientError) as exc:
                aws_client.elbv2.create_target_group(Name=f"tg-{short_uid()}", **kwargs)
            snapshot.match(f"error-tg-{key}", exc.value.response)

        # assert error for missing Port
        _assert_tg_error("port-missing", TargetType="ip", Protocol="HTTP")
        # assert error for missing VpcId
        _assert_tg_error("vpc-missing", TargetType="ip", Protocol="HTTP", Port=1234)
        # assert error for invalid Protocol for `lambda` target type
        _assert_tg_error("proto-invalid", TargetType="lambda", Protocol="HTTP")
        # assert error for invalid Port for `lambda` target type
        _assert_tg_error("port-invalid", TargetType="lambda", Port=1234)
        # assert error for invalid VpcId for `lambda` target type
        _assert_tg_error("vpc-invalid", TargetType="lambda", VpcId="vpc-test123")

        # create listener
        action = {
            "Type": "forward",
            "TargetGroupArn": tg_lambda_arn,
            "ForwardConfig": {"TargetGroups": [{"TargetGroupArn": tg_lambda_arn, "Weight": 1}]},
        }
        listener_proto = "HTTP"
        port = 80 if is_aws_cloud() else config.GATEWAY_LISTEN[0].port
        result = elbv2_create_listener(
            LoadBalancerArn=elb_arn, Protocol=listener_proto, Port=port, DefaultActions=[action]
        )
        assert result.get("Listeners")
        listener_port = result["Listeners"][0]["Port"]
        listener_arn = result["Listeners"][0]["ListenerArn"]

        # create rule for Lambda targets
        conditions = [{"Field": "path-pattern", "PathPatternConfig": {"Values": ["/lambda"]}}]
        actions = [
            {
                "Type": "forward",
                "TargetGroupArn": tg_lambda_arn,
                "ForwardConfig": {"TargetGroups": [{"TargetGroupArn": tg_lambda_arn, "Weight": 1}]},
            }
        ]
        elbv2_create_rule(
            ListenerArn=listener_arn, Conditions=conditions, Actions=actions, Priority=1
        )

        # create rule for IP targets (currently not yet enabled for AWS tests)
        if not is_aws_cloud():
            conditions = [
                {"Field": "path-pattern", "PathPatternConfig": {"Values": ["/ip/foo/bar"]}}
            ]
            actions = [
                {
                    "Type": "forward",
                    "TargetGroupArn": tg_ip_arn,
                    "ForwardConfig": {"TargetGroups": [{"TargetGroupArn": tg_ip_arn, "Weight": 1}]},
                }
            ]
            elbv2_create_rule(
                ListenerArn=listener_arn, Conditions=conditions, Actions=actions, Priority=2
            )

        if is_aws_cloud():
            # wait for ELB creation and DNS records to propagate
            wait_until_hostname_resolves(elb_host)

            def _check_target_health():
                tg_healths = aws_client.elbv2.describe_target_health(TargetGroupArn=tg_lambda_arn)
                tg_healths = tg_healths["TargetHealthDescriptions"]
                assert tg_healths[0]["TargetHealth"]["State"] == "healthy"

            # wait for targets to be in state active
            retry(_check_target_health, retries=60, sleep=5)

        # construct endpoint
        url = f"{listener_proto.lower()}://{elb_host}:{listener_port}"

        # make IP request (currently not yet enabled for real AWS mode)
        if not is_aws_cloud():
            request_url = f"{url}/ip/foo/bar?param1=value1"
            response = requests.get(request_url, verify=False)
            assert response.ok
            result = json.loads(to_str(response.content))
            # assert that the response is coming from the echo server, and that the request URL contains path+params
            assert response.headers.get("x-echo-server")
            assert result.get("request_url") == request_url

        # make Lambda request
        response = requests.post(
            f"{url}/lambda/foo/bar?p1=v1",
            "FOOBAR",
            headers={
                "X-Elb-Name": elb_name,
                "User-Agent": "python-requests/test",
            },
            verify=False,
        )
        assert response.ok
        result = json.loads(to_str(response.content))
        snapshot.match("response-lambda", result)

        # test the base64 encoding of the received lambda events
        # TODO: this should most probably be in its own test, but there is a lot of infrastructure to deploy
        #  and lambda were not tested individually
        # make Lambda request with Content-Type application/json
        response = requests.post(
            f"{url}/lambda/foo/bar?p1=v1",
            json={"test": "value"},
            headers={
                "X-Elb-Name": elb_name,
                "User-Agent": "python-requests/test",
            },
            verify=False,
        )
        assert response.ok
        snapshot.match("response-lambda-json", response.json())

        # make Lambda request with Content-Type text/csv
        response = requests.post(
            f"{url}/lambda/foo/bar?p1=v1",
            data="test1,test2,test3",
            headers={
                "X-Elb-Name": elb_name,
                "Content-Type": "text/csv",
                "User-Agent": "python-requests/test",
            },
            verify=False,
        )
        assert response.ok
        snapshot.match("response-lambda-csv", response.json())
        # make Lambda request with Content-Type text/csv but with Content-Encoding, we don't really encode the data
        response = requests.post(
            f"{url}/lambda/foo/bar?p1=v1",
            data="test1,test2,test3",
            headers={
                "X-Elb-Name": elb_name,
                "Content-Type": "text/csv",
                "Content-Encoding": "br",
                "User-Agent": "python-requests/test",
            },
            verify=False,
        )
        assert response.ok
        snapshot.match("response-lambda-csv-encoded", response.json())

    @markers.aws.only_localstack
    @pytest.mark.skipif(
        condition=not in_docker(),
        reason="Binding port 443 is only possible in docker",
    )
    def test_redirect_listener(
        self,
        default_vpc,
        elbv2_create_load_balancer,
        elbv2_create_rule,
        elbv2_create_listener,
        elb_transformers,
        add_target_group,
        acm_request_certificate,
        aws_client,
    ):
        """
        Check the following setup:
        * fixed-response listener listening on port 443 returning text/plain "ok"
        * redirect listener listening on port 4566 redirecting to fixed-response listener
        """
        elb_name = f"elb-{short_uid()}"

        subnets = [
            s["SubnetId"]
            for s in aws_client.ec2.describe_subnets(
                Filters=[{"Name": "vpc-id", "Values": [default_vpc["VpcId"]]}]
            )["Subnets"]
        ]

        # create load balancer
        result = elbv2_create_load_balancer(Name=elb_name, Subnets=subnets)
        elb_arn = result["LoadBalancers"][0]["LoadBalancerArn"]
        elb_host = result["LoadBalancers"][0]["DNSName"]

        fixed_response_port = 443
        fixed_response_protocol = "HTTPS"

        redirect_port = config.GATEWAY_LISTEN[0].port
        redirect_protocol = "HTTP"

        fixed_response_action = {
            "Type": "fixed-response",
            "FixedResponseConfig": {
                "StatusCode": "200",
                "ContentType": "text/plain",
                "MessageBody": "ok",
            },
        }

        cert = acm_request_certificate()
        elbv2_create_listener(
            LoadBalancerArn=elb_arn,
            Protocol=fixed_response_protocol,
            Port=fixed_response_port,
            DefaultActions=[fixed_response_action],
            Certificates=[
                {
                    "CertificateArn": cert["CertificateArn"],
                }
            ],
        )

        redirect_action = {
            "Type": "redirect",
            "RedirectConfig": {
                "Port": str(fixed_response_port),
                "Protocol": fixed_response_protocol,
                "StatusCode": "HTTP_302",
            },
        }

        elbv2_create_listener(
            LoadBalancerArn=elb_arn,
            Protocol=redirect_protocol,
            Port=redirect_port,
            DefaultActions=[redirect_action],
        )

        # make request against response listener
        url = f"{fixed_response_protocol.lower()}://{elb_host}:{fixed_response_port}/"
        response = requests.get(url)
        assert response.status_code == 200
        assert response.text == "ok"

        # test redirect endpoint
        url = f"{redirect_protocol.lower()}://{elb_host}:{redirect_port}/"
        response = requests.get(url, allow_redirects=False)

        assert response.status_code == 302

        response = requests.get(url)
        assert response.status_code == 200
        assert response.text == "ok"

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(
        paths=[
            "$..LoadBalancers[0].AvailabilityZones",
            "$..LoadBalancers[0].IpAddressType",
            "$..LoadBalancers[0].Scheme",
            "$..Attributes",
            "$.._AttributesDict.'access_logs.s3.enabled'",
            "$.._AttributesDict.'idle_timeout.timeout_seconds'",
            "$.._AttributesDict.'routing.http.x_amzn_tls_version_and_cipher_suite.enabled'",
            "$.._AttributesDict.'routing.http.xff_client_port.enabled'",
            "$.._AttributesDict.'routing.http.xff_header_processing.mode'",
            "$.._AttributesDict.'waf.fail_open.enabled'",
        ]
    )
    def test_alb_modify_attributes(
        self, elbv2_create_load_balancer, elb_transformers, snapshot, aws_client
    ):
        response = elbv2_create_load_balancer(
            Type="application",  # ALB
            IpAddressType="ipv4",
        )
        snapshot.match("create-alb", response)

        alb_arn = response["LoadBalancers"][0]["LoadBalancerArn"]
        response = aws_client.elbv2.modify_load_balancer_attributes(
            LoadBalancerArn=alb_arn,
            Attributes=[
                {"Key": "routing.http2.enabled", "Value": "true"},
                {"Key": "routing.http.drop_invalid_header_fields.enabled", "Value": "false"},
                {"Key": "routing.http.preserve_host_header.enabled", "Value": "false"},
                {"Key": "routing.http.desync_mitigation_mode", "Value": "defensive"},
                {"Key": "deletion_protection.enabled", "Value": "false"},
            ],
        )
        # fixme: dirty hack, even if ordering the list, if an Attribute is missing, the whole order will be thrown off
        # instead, create a dict from the map for easy comparison, and skip the verification of original field
        response["_AttributesDict"] = create_dict_from_attributes_map(response["Attributes"])
        snapshot.match("modify-alb-attributes", response)

        response = aws_client.elbv2.describe_load_balancer_attributes(LoadBalancerArn=alb_arn)
        response["_AttributesDict"] = create_dict_from_attributes_map(response["Attributes"])
        snapshot.match("describe-alb-attributes", response)

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(
        paths=[
            "$..LoadBalancers[0].AvailabilityZones",
            "$..LoadBalancers[0].IpAddressType",
            "$..LoadBalancers[0].Scheme",
            "$..Error.Type",
        ]
    )
    def test_alb_set_ip_address_type(
        self, elbv2_create_load_balancer, elb_transformers, snapshot, aws_client
    ):
        response = elbv2_create_load_balancer(
            Type="application",  # ALB
            IpAddressType="ipv4",
        )
        snapshot.match("create-alb", response)

        alb_arn = response["LoadBalancers"][0]["LoadBalancerArn"]
        response = aws_client.elbv2.set_ip_address_type(
            LoadBalancerArn=alb_arn, IpAddressType="ipv4"
        )
        snapshot.match("set-ip-address-type-ipv4", response)

        with pytest.raises(ClientError) as e:
            aws_client.elbv2.set_ip_address_type(LoadBalancerArn=alb_arn, IpAddressType="internal")
        snapshot.match("set-ip-address-type-internal", e.value.response)


class TestLoadBalancer:
    @pytest.fixture()
    def elbv2_transformers(self, snapshot):
        # add transformers to snapshot
        snapshot.add_transformer(
            [
                snapshot.transform.key_value("SubnetId", "subnet-id", reference_replacement=True),
                snapshot.transform.key_value("ZoneName", "region", reference_replacement=True),
                snapshot.transform.key_value("CanonicalHostedZoneId", reference_replacement=False),
                snapshot.transform.key_value("LoadBalancerArn", reference_replacement=False),
                snapshot.transform.key_value("LoadBalancerName", reference_replacement=False),
                snapshot.transform.key_value("DNSName", reference_replacement=False),
                snapshot.transform.key_value("VpcId"),
                snapshot.transform.jsonpath(
                    "$..LoadBalancers[0].SecurityGroups[0]", "sg-id", reference_replacement=False
                ),
            ]
        )

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(
        paths=[
            "$..LoadBalancers[0].AvailabilityZones",
            "$..LoadBalancers[0].IpAddressType",
            "$..LoadBalancers[0].Scheme",
        ]
    )
    def test_create_load_balancer(
        self, ec2_create_security_group, elbv2_transformers, snapshot, aws_client, region_name
    ):
        # get subnets and vpc id for load balancer for region <region>a and <region>b
        filters = [{"Name": "availability-zone", "Values": [f"{region_name}a", f"{region_name}b"]}]
        subnets_response = aws_client.ec2.describe_subnets(Filters=filters)["Subnets"]
        subnet_ids = [s["SubnetId"] for s in subnets_response]
        vpc_id = subnets_response[0]["VpcId"]

        # create security group for above vpc id
        sg_name = f"alb-sg-{short_uid()}"
        security_group = ec2_create_security_group(
            VpcId=vpc_id, GroupName=sg_name, Description="Security group for ALB", ports=[80]
        )
        sg_id = security_group["GroupId"]

        # create load balancer
        elb_name = f"elb-{short_uid()}"
        response = aws_client.elbv2.create_load_balancer(
            Name=elb_name,
            Subnets=subnet_ids,
            SecurityGroups=[sg_id],
        )
        snapshot.match("create-load-balancer", response)

        # create load balancer with already existing name
        response_multiple = aws_client.elbv2.create_load_balancer(
            Name=elb_name,
            Subnets=subnet_ids,
            SecurityGroups=[sg_id],
        )

        snapshot.match("create-load-balancer-with-already-existing-name", response_multiple)

        aws_client.elbv2.delete_load_balancer(
            LoadBalancerArn=response["LoadBalancers"][0]["LoadBalancerArn"]
        )

        # create internal load balancer
        response_internal_lb = aws_client.elbv2.create_load_balancer(
            Name=f"elb-internal-{short_uid()}",
            Subnets=subnet_ids,
            SecurityGroups=[sg_id],
            Scheme="internal",
        )
        snapshot.match("create-internal-load-balancer", response_internal_lb)

        aws_client.elbv2.delete_load_balancer(
            LoadBalancerArn=response_internal_lb["LoadBalancers"][0]["LoadBalancerArn"]
        )

        # create network load balancer
        response_network_lb = aws_client.elbv2.create_load_balancer(
            Name=f"elb-network-{short_uid()}",
            Subnets=subnet_ids,
            SecurityGroups=[sg_id],
            Type="network",
        )
        snapshot.match("create-network-load-balancer", response_network_lb)

        aws_client.elbv2.delete_load_balancer(
            LoadBalancerArn=response_network_lb["LoadBalancers"][0]["LoadBalancerArn"]
        )

        # create gateway load balancer
        response_gateway_lb = aws_client.elbv2.create_load_balancer(
            Name=f"elb-gateway-{short_uid()}", Subnets=subnet_ids, Type="gateway"
        )
        snapshot.match("create-gateway-load-balancer", response_gateway_lb)

        aws_client.elbv2.delete_load_balancer(
            LoadBalancerArn=response_gateway_lb["LoadBalancers"][0]["LoadBalancerArn"]
        )

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(
        paths=[
            "$..LoadBalancers[0].AvailabilityZones",
            "$..LoadBalancers[0].IpAddressType",
            "$..LoadBalancers[0].Scheme",
        ]
    )
    def test_failing_create_load_balancer(
        self, ec2_create_security_group, elbv2_transformers, snapshot, aws_client, region_name
    ):
        # get subnets and vpc id for load balancer for region <region>a and <region>b
        filters = [{"Name": "availability-zone", "Values": [f"{region_name}a", f"{region_name}b"]}]
        subnets_response = aws_client.ec2.describe_subnets(Filters=filters)["Subnets"]
        subnet_ids = [s["SubnetId"] for s in subnets_response]
        vpc_id = subnets_response[0]["VpcId"]

        # create security group for above vpc id
        sg_name = f"alb-sg-{short_uid()}"
        security_group = ec2_create_security_group(
            VpcId=vpc_id, GroupName=sg_name, Description="Security group for ALB", ports=[80]
        )
        sg_id = security_group["GroupId"]

        # create gateway load balancer with security group
        with pytest.raises(ClientError) as e:
            aws_client.elbv2.create_load_balancer(
                Name=f"elb-gateway-{short_uid()}",
                Subnets=subnet_ids,
                SecurityGroups=[sg_id],
                Type="gateway",
            )
        snapshot.match("create-gateway-load-balancer-with-security-group", e.value.response)

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(
        paths=[
            "$..LoadBalancers[0].AvailabilityZones",
            "$..LoadBalancers[0].IpAddressType",
            "$..LoadBalancers[0].Scheme",
            "$..LoadBalancers..State.Code",
        ]
    )
    def test_describe_load_balancers(
        self, snapshot, elbv2_transformers, elbv2_create_load_balancer, aws_client
    ):
        elb_name = f"elb-{short_uid()}"

        # get subnets
        subnets = [s["SubnetId"] for s in aws_client.ec2.describe_subnets()["Subnets"]]

        # create load balancer
        result = elbv2_create_load_balancer(Name=elb_name, Subnets=subnets)

        # describe load balancers with name
        response_with_name = aws_client.elbv2.describe_load_balancers(Names=[elb_name])
        snapshot.match("describe-load-balancers-with-name", response_with_name)

        # describe load balancers with arn
        response_with_arn = aws_client.elbv2.describe_load_balancers(
            LoadBalancerArns=[result["LoadBalancers"][0]["LoadBalancerArn"]]
        )
        snapshot.match("describe-load-balancers-with-arn", response_with_arn)

    @markers.aws.validated
    def test_failing_describe_load_balancers(
        self, elbv2_transformers, elbv2_create_load_balancer, snapshot, aws_client
    ):
        # describe load balancers with non-existing name
        with pytest.raises(ClientError) as e:
            aws_client.elbv2.describe_load_balancers(Names=["elb-non-existing-name"])

        snapshot.match("describe-load-balancers-with-non-existing-name", e.value.response)

        # describe load balancers with non-existing arn
        sample_arn_1 = "arn:aws:elasticloadbalancing:us-east-1:111111111111:loadbalancer/app/elb-non-existing-arn-1/0000000000000000"
        with pytest.raises(ClientError) as e:
            aws_client.elbv2.describe_load_balancers(LoadBalancerArns=[sample_arn_1])
        snapshot.add_transformer(snapshot.transform.regex(sample_arn_1, "<load_balancer_arn_1>"))

        snapshot.match("describe-load-balancers-with-non-existing-arn", e.value.response)

        # describe load balancers with both non-existing name and arn
        with pytest.raises(ClientError) as e:
            aws_client.elbv2.describe_load_balancers(
                Names=["elb-non-existing-name"], LoadBalancerArns=[sample_arn_1]
            )
        snapshot.match("describe-load-balancers-with-non-existing-name-and-arn", e.value.response)

        # describe load balancers with multiple non-existing names
        with pytest.raises(ClientError) as e:
            aws_client.elbv2.describe_load_balancers(
                Names=["elb-non-existing-name", "elb-non-existing-name-2"]
            )
        snapshot.match("describe-load-balancers-with-multiple-non-existing-names", e.value.response)

        # describe load balancers with multiple non-existing arns
        sample_arn_2 = "arn:aws:elasticloadbalancing:us-east-1:111111111111:loadbalancer/app/elb-non-existing-arn-2/0000000000000000"
        snapshot.add_transformer(snapshot.transform.regex(sample_arn_2, "<load_balancer_arn_2>"))
        with pytest.raises(ClientError) as e:
            aws_client.elbv2.describe_load_balancers(LoadBalancerArns=[sample_arn_1, sample_arn_2])
        snapshot.match("describe-load-balancers-with-multiple-non-existing-arns", e.value.response)

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(
        paths=[
            "$..Rules..Actions..TargetGroupArn",
            "$..Rules..Conditions..Values",
            "$..LoadBalancers..AvailabilityZones..LoadBalancerAddresses",
            "$..LoadBalancers..IpAddressType",
            "$..Listeners..AlpnPolicy",
            "$..Listeners..DefaultActions..FixedResponseConfig.MessageBody",
            "$..Listeners..Port",
            "$..Listeners..SslPolicy",
            "$..TargetGroups..IpAddressType",
            "$..TargetGroups..ProtocolVersion",
        ]
    )
    def test_create_loadbalancer_rule(
        self,
        elbv2_create_load_balancer,
        elbv2_create_target_group,
        elbv2_create_listener,
        elbv2_create_rule,
        ec2_create_security_group,
        aws_client,
        elbv2_transformers,
        snapshot,
        region_name,
    ):
        elb_name = f"elb-{short_uid()}"
        snapshot.add_transformer(snapshot.transform.regex(elb_name, "<elb-name>"))
        snapshot.add_transformer(snapshot.transform.resource_name(), priority=-1)

        # get subnets and vpc id for load balancer for region <region>a and <region>b
        filters = [{"Name": "availability-zone", "Values": [f"{region_name}a", f"{region_name}b"]}]
        subnets_response = aws_client.ec2.describe_subnets(Filters=filters)["Subnets"]
        vpc_id = subnets_response[0]["VpcId"]
        subnets = [s["SubnetId"] for s in subnets_response if s["VpcId"] == vpc_id]
        security_group = ec2_create_security_group(
            VpcId=vpc_id,
            GroupName=f"my-sec-group-{short_uid()}",
            Description="Test Security group for ALB",
            ports=[80],
        )
        sg_id = security_group["GroupId"]

        # create load balancer
        result = elbv2_create_load_balancer(
            Name=elb_name,
            SecurityGroups=[sg_id],
            Subnets=subnets,
            Scheme="internet-facing",
            Type="application",
            IpAddressType="ipv4",
        )
        assert result.get("LoadBalancers")
        snapshot.match("create_load_balancer", result)
        elb_arn = result["LoadBalancers"][0]["LoadBalancerArn"]

        # create listener
        action = {
            "Type": "fixed-response",
            "Order": 1,
            "FixedResponseConfig": {"StatusCode": "404", "ContentType": "text/plain"},
        }
        result = elbv2_create_listener(
            LoadBalancerArn=elb_arn, Protocol="HTTP", Port=80, DefaultActions=[action]
        )
        assert result.get("Listeners")
        listener_arn = result["Listeners"][0]["ListenerArn"]
        snapshot.match("create_listener", result)

        # create target group
        target_group_name = f"k8s-echoserv-echoserv-{short_uid()}"
        snapshot.add_transformer(
            snapshot.transform.regex(target_group_name, "<target_group_name>"), priority=-1
        )

        result = elbv2_create_target_group(
            Name=target_group_name,
            TargetType="ip",
            Protocol="HTTP",
            ProtocolVersion="HTTP1",
            Port=8080,
            VpcId=vpc_id,
            HealthCheckProtocol="HTTP",
            HealthCheckPort="traffic-port",
            HealthCheckEnabled=True,
            HealthCheckPath="/",
            HealthCheckIntervalSeconds=15,
            HealthCheckTimeoutSeconds=5,
            HealthyThresholdCount=2,
            UnhealthyThresholdCount=2,
            Matcher={"HttpCode": "200"},
        )
        target_group_arn = result["TargetGroups"][0]["TargetGroupArn"]
        snapshot.match("create_target_group", result)

        # create rule
        conditions = [{"Field": "path-pattern", "PathPatternConfig": {"Values": ["/"]}}]
        actions = [
            {
                "Type": "forward",
                "Order": 1,
                "ForwardConfig": {"TargetGroups": [{"TargetGroupArn": target_group_arn}]},
            }
        ]
        result = elbv2_create_rule(
            ListenerArn=listener_arn, Conditions=conditions, Actions=actions, Priority=1
        )
        snapshot.match("create-rule", result)


class TestRoute53Integrations:
    @markers.aws.validated
    def test_route53_elb_integration(
        self,
        create_lambda_function,
        elbv2_create_load_balancer,
        elbv2_create_rule,
        elbv2_create_listener,
        default_vpc,
        add_target_group,
        route53_create_hosted_zone,
        snapshot,
        aws_client,
    ):
        elb_name = f"elb-{short_uid()}"
        target_group_name = f"tg-lambda-{short_uid()}"
        function_name = f"elb-tgt-1-{short_uid()}"
        snapshot.add_transformer(snapshot.transform.regex(elb_name, "<elb-name>"))

        # get subnets
        subnets = [
            s["SubnetId"]
            for s in aws_client.ec2.describe_subnets(
                Filters=[{"Name": "vpc-id", "Values": [default_vpc["VpcId"]]}]
            )["Subnets"]
        ]

        # create load balancer
        result = elbv2_create_load_balancer(Name=elb_name, Subnets=subnets)
        elb_arn = result["LoadBalancers"][0]["LoadBalancerArn"]
        elb_host = result["LoadBalancers"][0]["DNSName"]

        # set up route53 alias
        zone_name = "example.invalid"
        zone_id = route53_create_hosted_zone(Name=zone_name)

        # create record sets
        changes = [
            {
                "Action": "UPSERT",
                "ResourceRecordSet": {
                    "Name": zone_name,
                    "Type": "A",
                    "AliasTarget": {
                        # Hosted Zone ID for eu-central-1 ALB
                        # If test fails, check your region here: https://docs.aws.amazon.com/general/latest/gr/elb.html
                        "HostedZoneId": "Z215JYRZR1TBD5",
                        "DNSName": elb_host,
                        "EvaluateTargetHealth": True,
                    },
                },
            },
        ]

        change_resource_record_set_result = aws_client.route53.change_resource_record_sets(
            HostedZoneId=zone_id, ChangeBatch={"Changes": changes}
        )

        # deploy test Lambda
        lambda_resp = create_lambda_function(
            handler_file=ELB_LAMBDA % "lambda1", func_name=function_name
        )
        lambda_arn = lambda_resp["CreateFunctionResponse"]["FunctionArn"]

        # add target groups
        tg_lambda_arn = add_target_group(target_group_name, "lambda", tg_id=lambda_arn)
        snapshot.add_transformer(snapshot.transform.regex(tg_lambda_arn, "<lambda-target-arn>"))

        # create listener
        action = {
            "Type": "forward",
            "TargetGroupArn": tg_lambda_arn,
            "ForwardConfig": {"TargetGroups": [{"TargetGroupArn": tg_lambda_arn, "Weight": 1}]},
        }
        listener_proto = "HTTP"
        port = 80 if is_aws_cloud() else config.GATEWAY_LISTEN[0].port
        result = elbv2_create_listener(
            LoadBalancerArn=elb_arn, Protocol=listener_proto, Port=port, DefaultActions=[action]
        )
        listener_port = result["Listeners"][0]["Port"]

        def _check_target_health():
            tg_healths = aws_client.elbv2.describe_target_health(TargetGroupArn=tg_lambda_arn)
            tg_healths = tg_healths["TargetHealthDescriptions"]
            assert tg_healths[0]["TargetHealth"]["State"] == "healthy"

        # wait for targets to be in state active
        retry(_check_target_health, retries=60, sleep=5)

        # construct endpoint
        url = f"{listener_proto.lower()}://{elb_host}:{listener_port}"

        # make Lambda request
        def _try_request():
            response = requests.get(url, verify=False)
            assert response.ok
            return response

        response = retry(_try_request, sleep=2, retries=15)
        result = to_str(response.content)
        snapshot.match("response-lambda", result)

        aws_client.route53.get_waiter("resource_record_sets_changed").wait(
            Id=change_resource_record_set_result["ChangeInfo"]["Id"]
        )

        response = requests.get(url, headers={"Host": zone_name}, verify=False)
        assert response.ok
        result = to_str(response.content)
        snapshot.match("response-lambda-route53-host", result)


class TestRuleConditions:
    """
    Test LB rule conditions
    See: https://docs.aws.amazon.com/elasticloadbalancing/latest/APIReference/API_RuleCondition.html
    """

    @markers.aws.validated
    def test_rule_conditions_integration(
        self,
        elbv2_create_load_balancer,
        elbv2_create_rule,
        elbv2_create_listener,
        default_vpc,
        snapshot,
        aws_client,
    ):
        """
        Create a Load Balancer with multiple rules and conditions. Test the rules with requests.
        Assert that pathget is not called for non-GET requests.

        | Conditions                                         | Priority | Response Code | Response          |
        | -------------------------------------------------- | -------- | ------------- | ----------------- |
        |                                                    |          | 404           |                   |
        | path-condition: /doget                             | 1        | 200           | doget path called |
        | path-condition: /pathget, http-request-method: GET | 2        | 200           | pathget called    |
        | path-condition: /doget2                            | 3        | 200           | doget2 called     |
        | path-pattern: /ip/*                               | 4        | 200           | ip called         |
        """
        elb_name = f"elb-{short_uid()}"
        snapshot.add_transformer(snapshot.transform.regex(elb_name, "<elb-name>"))

        # get subnets
        subnets = [
            s["SubnetId"]
            for s in aws_client.ec2.describe_subnets(
                Filters=[{"Name": "vpc-id", "Values": [default_vpc["VpcId"]]}]
            )["Subnets"]
        ]

        # create load balancer
        result = elbv2_create_load_balancer(Name=elb_name, Subnets=subnets)
        elb_arn = result["LoadBalancers"][0]["LoadBalancerArn"]
        elb_host = result["LoadBalancers"][0]["DNSName"]

        # create listener
        action = {
            "Type": "fixed-response",
            "Order": 1,
            "FixedResponseConfig": {"StatusCode": "404", "ContentType": "text/plain"},
        }

        listener_proto = "HTTP"
        port = 80 if is_aws_cloud() else config.GATEWAY_LISTEN[0].port
        result = elbv2_create_listener(
            LoadBalancerArn=elb_arn, Protocol=listener_proto, Port=port, DefaultActions=[action]
        )
        listener_port = result["Listeners"][0]["Port"]
        listener_arn = result["Listeners"][0]["ListenerArn"]

        # construct endpoint
        url = f"{listener_proto.lower()}://{elb_host}:{listener_port}"

        if is_aws_cloud():
            # wait for ELB creation and DNS records to propagate
            wait_until_hostname_resolves(elb_host)

        # create rule with just path condition
        conditions = [{"Field": "path-pattern", "PathPatternConfig": {"Values": ["/doget"]}}]
        actions = [
            {
                "Type": "fixed-response",
                "FixedResponseConfig": {
                    "StatusCode": "200",
                    "ContentType": "text/plain",
                    "MessageBody": "doget path called",
                },
            }
        ]
        elbv2_create_rule(
            ListenerArn=listener_arn, Conditions=conditions, Actions=actions, Priority=1
        )
        # create rule with just path and http-request-method GET condition
        conditions = [
            {"Field": "path-pattern", "PathPatternConfig": {"Values": ["/pathget"]}},
            {"Field": "http-request-method", "HttpRequestMethodConfig": {"Values": ["GET"]}},
        ]
        actions = [
            {
                "Type": "fixed-response",
                "FixedResponseConfig": {
                    "StatusCode": "200",
                    "ContentType": "text/plain",
                    "MessageBody": "pathget called",
                },
            }
        ]
        elbv2_create_rule(
            ListenerArn=listener_arn, Conditions=conditions, Actions=actions, Priority=2
        )
        # Create a doget2 rule with priority 3
        # This is testing that /doget will not match this rule
        conditions = [{"Field": "path-pattern", "PathPatternConfig": {"Values": ["/doget2"]}}]
        actions = [
            {
                "Type": "fixed-response",
                "FixedResponseConfig": {
                    "StatusCode": "200",
                    "ContentType": "text/plain",
                    "MessageBody": "doget2 called",
                },
            }
        ]
        elbv2_create_rule(
            ListenerArn=listener_arn, Conditions=conditions, Actions=actions, Priority=3
        )

        # Create a wildcard rule
        conditions = [{"Field": "path-pattern", "PathPatternConfig": {"Values": ["/ip/*"]}}]
        actions = [
            {
                "Type": "fixed-response",
                "FixedResponseConfig": {
                    "StatusCode": "200",
                    "ContentType": "text/plain",
                    "MessageBody": "ip called",
                },
            }
        ]
        elbv2_create_rule(
            ListenerArn=listener_arn, Conditions=conditions, Actions=actions, Priority=4
        )

        # make Lambda request
        def _try_request():
            response = requests.get(url, verify=False)
            assert response.status_code == 404
            return response

        response = retry(_try_request, sleep=2, retries=15)

        snapshot.match("response-default-route-rule", response.status_code)

        def _try_path_request():
            response = requests.get(url + "/doget", verify=False)
            assert response.ok
            return response

        response = retry(_try_path_request, sleep=2, retries=15)
        result = to_str(response.content)
        assert result == "doget path called"

        snapshot.match("response-path", result)

        def _try_path_get_request():
            response = requests.get(url + "/pathget", verify=False)
            assert response.ok
            return response

        response = retry(_try_path_get_request, sleep=2, retries=15)
        result = to_str(response.content)
        assert result == "pathget called"
        snapshot.match("response-path-get-condition", result)

        def _try_path_delete_request():
            response = requests.delete(url + "/pathget", verify=False)
            assert response.status_code == 404
            return response

        # Do a DELETE to /pathget and it should return 404
        response = retry(_try_path_delete_request, sleep=2, retries=15)
        snapshot.match("response-path-delete-condition", response.status_code)

        def _try_path_head_request():
            response = requests.head(url + "/pathget", verify=False)
            assert response.status_code == 404
            return response

        # Do a HEAD to /pathget and it should return 404
        response = retry(_try_path_head_request, sleep=2, retries=15)
        snapshot.match("response-path-head-condition", response.status_code)

        def _try_path_post_request():
            response = requests.post(url + "/pathget", verify=False, data="foo")
            assert response.status_code == 404
            return response

        # Do a POST to /pathget and it should return 404
        response = retry(_try_path_post_request, sleep=2, retries=15)
        snapshot.match("response-path-post-condition", response.status_code)

        def _try_path_put_request():
            response = requests.put(url + "/pathget", verify=False, data="foo")
            assert response.status_code == 404
            return response

        # Do a PUT to /pathget and it should return 404
        response = retry(_try_path_put_request, sleep=2, retries=15)
        snapshot.match("response-path-put-condition", response.status_code)

        # Do a GET to /doget2 and it should return 200
        def _try_doget2_request():
            response = requests.get(url + "/doget2", verify=False)
            assert response.ok
            return response

        response = retry(_try_doget2_request, sleep=2, retries=15)
        result = to_str(response.content)
        assert result == "doget2 called"
        snapshot.match("response-doget2", result)

        # Do a GET to /doget2 and it should return 200
        def _try_ip_wildcard_request():
            response = requests.get(url + "/ip/foo/bar?something=localstack", verify=False)
            assert response.ok
            return response

        response = retry(_try_ip_wildcard_request, sleep=2, retries=15)
        result = to_str(response.content)
        assert result == "ip called"
        snapshot.match("response-ip-wildcard", result)
