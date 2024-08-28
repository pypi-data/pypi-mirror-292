import pytest
from botocore.exceptions import ClientError
from localstack.testing.pytest import markers
from localstack.utils.strings import short_uid


@pytest.fixture(autouse=True)
def elbv2_snapshot_transformers(snapshot):
    snapshot.add_transformer(
        [
            snapshot.transform.key_value("TargetGroupArn"),
            snapshot.transform.key_value("TargetGroupName"),
            snapshot.transform.key_value("VpcId"),
        ]
    )


@pytest.fixture
def default_vpc_id(aws_client):
    vpcs = aws_client.ec2.describe_vpcs(Filters=[{"Name": "isDefault", "Values": ["true"]}])
    return vpcs["Vpcs"][0]["VpcId"]


@pytest.fixture
def create_target_group(aws_client):
    tgs = []

    def _create(*args, **kwargs):
        response = aws_client.elbv2.create_target_group(*args, **kwargs)
        tgs.append(response["TargetGroups"][0]["TargetGroupArn"])
        return response

    yield _create

    for tg in tgs:
        aws_client.elbv2.delete_target_group(TargetGroupArn=tg)


class TestElbV2TargetGroups:
    @markers.aws.validated
    def test_target_group_crud(self, aws_client, snapshot, default_vpc_id):
        target_group_name = short_uid()

        with pytest.raises(ClientError) as exc:
            aws_client.elbv2.create_target_group(Name=target_group_name)
        snapshot.match("create_target_group_err_1", exc.value.response)

        with pytest.raises(ClientError) as exc:
            aws_client.elbv2.create_target_group(Name=target_group_name, Protocol="HTTP")
        snapshot.match("create_target_group_err_2", exc.value.response)

        with pytest.raises(ClientError) as exc:
            aws_client.elbv2.create_target_group(
                Name=target_group_name,
                Protocol="HTTP",
                Port=80,
            )
        snapshot.match("create_target_group_err_3", exc.value.response)

        with pytest.raises(ClientError) as exc:
            aws_client.elbv2.create_target_group(
                Name=target_group_name,
                Protocol="HTTP",
                Port=80,
                VpcId="vpc-1234",
            )
        snapshot.match("create_target_group_err_4", exc.value.response)

        # TODO: write validation for invalid protocol

        # tests the default parameters
        response = aws_client.elbv2.create_target_group(
            Name=target_group_name,
            Protocol="HTTP",
            Port=80,
            VpcId=default_vpc_id,
        )
        snapshot.match("create_target_group_1", response)

        response = aws_client.elbv2.delete_target_group(
            TargetGroupArn=response["TargetGroups"][0]["TargetGroupArn"]
        )
        assert response["ResponseMetadata"]["HTTPStatusCode"] == 200

        response = aws_client.elbv2.create_target_group(Name=target_group_name, TargetType="lambda")
        snapshot.match("create_target_group_2", response)
        aws_client.elbv2.delete_target_group(
            TargetGroupArn=response["TargetGroups"][0]["TargetGroupArn"]
        )

        with pytest.raises(ClientError) as exc:
            aws_client.elbv2.create_target_group(Name=target_group_name, TargetType="ip")
        snapshot.match("create_target_group_err_5", exc.value.response)

        with pytest.raises(ClientError) as exc:
            aws_client.elbv2.create_target_group(
                Name=target_group_name,
                TargetType="ip",
                Protocol="HTTP",
            )
        snapshot.match("create_target_group_err_6", exc.value.response)

        with pytest.raises(ClientError) as exc:
            aws_client.elbv2.create_target_group(
                Name=target_group_name,
                TargetType="ip",
                Protocol="HTTP",
                Port=80,
            )
        snapshot.match("create_target_group_err_7", exc.value.response)

        response = aws_client.elbv2.create_target_group(
            Name=target_group_name,
            TargetType="ip",
            Protocol="HTTP",
            Port=80,
            VpcId=default_vpc_id,
        )
        snapshot.match("create_target_group_3", response)
        aws_client.elbv2.delete_target_group(
            TargetGroupArn=response["TargetGroups"][0]["TargetGroupArn"]
        )

        with pytest.raises(ClientError) as exc:
            aws_client.elbv2.create_target_group(
                Name=target_group_name,
                Protocol="HTTP",
                Port=8080,
                VpcId=default_vpc_id,
                HealthCheckProtocol="HTTP",
                HealthCheckPath="/",
                HealthCheckIntervalSeconds=5,
                HealthCheckTimeoutSeconds=5,
                HealthyThresholdCount=5,
                UnhealthyThresholdCount=2,
            )
        snapshot.match("create_target_group_err_8", exc.value.response)

        with pytest.raises(ClientError) as exc:
            aws_client.elbv2.create_target_group(
                Name=target_group_name,
                Protocol="HTTP",
                Port=8080,
                VpcId=default_vpc_id,
                HealthCheckProtocol="HTTP",
                HealthCheckPath="/",
                HealthCheckIntervalSeconds=30,
                HealthCheckTimeoutSeconds=100,
                HealthyThresholdCount=5,
                UnhealthyThresholdCount=2,
            )
        snapshot.match("create_target_group_err_9", exc.value.response)

        response = aws_client.elbv2.create_target_group(
            Name=target_group_name,
            Protocol="HTTP",
            Port=8080,
            VpcId=default_vpc_id,
            HealthCheckProtocol="HTTP",
            HealthCheckPath="/",
            HealthCheckIntervalSeconds=5,
            HealthCheckTimeoutSeconds=3,
            HealthyThresholdCount=5,
            UnhealthyThresholdCount=2,
            Matcher={"HttpCode": "200"},
        )
        snapshot.match("create_target_group_4", response)

        target_group_arn = response["TargetGroups"][0]["TargetGroupArn"]

        response = aws_client.elbv2.describe_target_health(TargetGroupArn=target_group_arn)
        snapshot.match("describe_target_health_1", response)

        aws_client.elbv2.delete_target_group(TargetGroupArn=target_group_arn)

    @markers.aws.validated
    @pytest.mark.parametrize(
        "protocol", ["HTTP", "HTTPS", "TCP", "TLS", "UDP", "TCP_UDP", "GENEVE"]
    )
    def test_target_group_protocol_default_values(
        self, aws_client, default_vpc_id, snapshot, protocol
    ):
        target_group_name = short_uid()
        response = aws_client.elbv2.create_target_group(
            Name=target_group_name,
            Protocol=protocol,
            Port=6081 if protocol == "GENEVE" else 80,
            VpcId=default_vpc_id,
        )
        snapshot.match("create_target_group", response)
        aws_client.elbv2.delete_target_group(
            TargetGroupArn=response["TargetGroups"][0]["TargetGroupArn"]
        )

    @markers.aws.validated
    @pytest.mark.parametrize("target_type", ["instance", "ip", "lambda", "alb"])
    def test_target_group_target_type_default_values(
        self, aws_client, default_vpc_id, snapshot, target_type
    ):
        target_group_name = short_uid()

        param = {
            "Name": target_group_name,
            "TargetType": target_type,
        }

        if target_type != "lambda":
            param["Protocol"] = "HTTP" if target_type != "alb" else "TCP"
            param["Port"] = 80
            param["VpcId"] = default_vpc_id

        response = aws_client.elbv2.create_target_group(**param)
        snapshot.match("create_target_group", response)
        aws_client.elbv2.delete_target_group(
            TargetGroupArn=response["TargetGroups"][0]["TargetGroupArn"]
        )

    @markers.aws.validated
    @pytest.mark.parametrize(
        "protocol_name, should_raise",
        [
            ("HTTP", True),
            ("HTTPS", True),
            ("TCP", False),
            ("TLS", False),
            ("UDP", False),
            ("TCP_UDP", False),
        ],
    )
    def test_target_group_healthcheck_interval(
        self, aws_client, default_vpc_id, snapshot, protocol_name, should_raise
    ):
        target_group_name = short_uid()

        def _create_target_group(
            protocol_name, target_group_name, vpc_id, health_check_timeout_seconds
        ):
            return aws_client.elbv2.create_target_group(
                Name=target_group_name,
                Protocol=protocol_name,
                Port=80,
                VpcId=vpc_id,
                HealthCheckProtocol="HTTP",
                HealthCheckPath="/",
                HealthCheckIntervalSeconds=5,
                HealthCheckTimeoutSeconds=health_check_timeout_seconds,
                HealthyThresholdCount=5,
                UnhealthyThresholdCount=2,
            )

        with pytest.raises(ClientError) as exc:
            _create_target_group(protocol_name, target_group_name, default_vpc_id, 6)
        snapshot.match("create_target_group_err_1", exc.value.response)

        if should_raise:
            with pytest.raises(ClientError) as exc:
                _create_target_group(protocol_name, target_group_name, default_vpc_id, 5)
            snapshot.match("create_target_group_err_2", exc.value.response)
        else:
            response = _create_target_group(protocol_name, target_group_name, default_vpc_id, 5)
            aws_client.elbv2.delete_target_group(
                TargetGroupArn=response["TargetGroups"][0]["TargetGroupArn"]
            )

    @markers.aws.validated
    def test_target_group_attributes_deregistration(
        self, aws_client, default_vpc_id, snapshot, create_target_group
    ):
        response = create_target_group(Name=short_uid(), TargetType="lambda")
        target_group_arn = response["TargetGroups"][0]["TargetGroupArn"]
        with pytest.raises(ClientError) as exc:
            aws_client.elbv2.modify_target_group_attributes(
                TargetGroupArn=target_group_arn,
                Attributes=[{"Key": "deregistration_delay.timeout_seconds", "Value": "300"}],
            )
        snapshot.match("create_target_group_err_1", exc.value.response)

        response = create_target_group(
            Name=short_uid(), Protocol="HTTP", Port=80, VpcId=default_vpc_id
        )
        target_group_arn = response["TargetGroups"][0]["TargetGroupArn"]
        with pytest.raises(ClientError) as exc:
            aws_client.elbv2.modify_target_group_attributes(
                TargetGroupArn=target_group_arn,
                Attributes=[{"Key": "deregistration_delay.timeout_seconds", "Value": "10000"}],
            )
        snapshot.match("create_target_group_err_2", exc.value.response)

    @markers.aws.validated
    @pytest.mark.parametrize(
        "protocol, should_raise, stickiness_type",
        [
            # stickiness.type = "source_ip"
            ("HTTP", True, "source_ip"),
            ("HTTPS", True, "source_ip"),
            ("TCP", False, "source_ip"),
            ("TLS", True, "source_ip"),
            ("UDP", False, "source_ip"),
            ("TCP_UDP", False, "source_ip"),
            ("GENEVE", True, "source_ip"),
            # stickiness.type = "lb_cookie"
            ("HTTP", False, "lb_cookie"),
            ("HTTPS", False, "lb_cookie"),
            ("TCP", True, "lb_cookie"),
            ("TLS", True, "lb_cookie"),
            ("UDP", True, "lb_cookie"),
            ("TCP_UDP", True, "lb_cookie"),
            ("GENEVE", True, "lb_cookie"),
            # stickiness.type = "app_cookie"
            ("HTTP", False, "app_cookie"),
            ("HTTPS", False, "app_cookie"),
            ("TCP", True, "app_cookie"),
            ("TLS", True, "app_cookie"),
            ("UDP", True, "app_cookie"),
            ("TCP_UDP", True, "app_cookie"),
            ("GENEVE", True, "app_cookie"),
            # stickiness.type = "source_ip_dest_ip"
            ("HTTP", True, "source_ip_dest_ip"),
            ("HTTPS", True, "source_ip_dest_ip"),
            ("TCP", True, "source_ip_dest_ip"),
            ("TLS", True, "source_ip_dest_ip"),
            ("UDP", True, "source_ip_dest_ip"),
            ("TCP_UDP", True, "source_ip_dest_ip"),
            ("GENEVE", False, "source_ip_dest_ip"),
            # stickiness.type = "source_ip_dest_ip_proto"
            ("HTTP", True, "source_ip_dest_ip_proto"),
            ("HTTPS", True, "source_ip_dest_ip_proto"),
            ("TCP", True, "source_ip_dest_ip_proto"),
            ("TLS", True, "source_ip_dest_ip_proto"),
            ("UDP", True, "source_ip_dest_ip_proto"),
            ("TCP_UDP", True, "source_ip_dest_ip_proto"),
            ("GENEVE", False, "source_ip_dest_ip_proto"),
        ],
    )
    def test_target_group_attributes_stickiness(
        self,
        aws_client,
        default_vpc_id,
        snapshot,
        create_target_group,
        protocol,
        should_raise,
        stickiness_type,
    ):
        response = create_target_group(
            Name=short_uid(),
            Protocol=protocol,
            Port=6081 if protocol == "GENEVE" else 80,
            VpcId=default_vpc_id,
        )
        target_group_arn = response["TargetGroups"][0]["TargetGroupArn"]
        attributes = [
            {"Key": "stickiness.enabled", "Value": "true"},
            {"Key": "stickiness.type", "Value": stickiness_type},
        ]
        if stickiness_type == "app_cookie":
            attributes.append({"Key": "stickiness.app_cookie.cookie_name", "Value": "localstack"})
        if should_raise:
            with pytest.raises(ClientError) as exc:
                aws_client.elbv2.modify_target_group_attributes(
                    TargetGroupArn=target_group_arn, Attributes=attributes
                )
            snapshot.match("create_target_group_err", exc.value.response)
        else:
            aws_client.elbv2.modify_target_group_attributes(
                TargetGroupArn=target_group_arn, Attributes=attributes
            )
