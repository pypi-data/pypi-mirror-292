import contextlib
import logging
import socket
from typing import Any, Dict, List
from urllib.parse import urlparse

import dns
import dnslib
import pytest
from dns import resolver
from dns.rdatatype import RdataType
from localstack import config, constants
from localstack.constants import LOCALHOST_HOSTNAME
from localstack.testing.aws.util import is_aws_cloud
from localstack.testing.pytest import markers
from localstack.utils.collections import is_sub_dict
from localstack.utils.net import is_ip_address
from localstack.utils.strings import short_uid
from localstack.utils.sync import poll_condition, retry

LOG = logging.getLogger(__name__)


@pytest.fixture
def route53_create_health_check(aws_client):
    health_checks = []

    def _create(**kwargs):
        result = aws_client.route53.create_health_check(**kwargs)
        health_checks.append(result["HealthCheck"])
        return result["HealthCheck"]

    yield _create

    for health_check in health_checks:
        with contextlib.suppress(Exception):
            aws_client.route53.delete_health_check(HealthCheckId=health_check["Id"])


def resolve_dns(
    domain: str, name_server: str = None, datatype: RdataType = None
) -> List[Dict[str, Any]]:
    domain = dns.name.from_text(domain)
    if not domain.is_absolute():
        domain = domain.concatenate(dns.name.root)

    datatype = datatype or dns.rdatatype.ANY
    request = dns.message.make_query(domain, datatype)

    # Note: using LOCALHOST_IP, as constants.LOCALHOST has been raising "Text input malformed" errors recently
    name_server = name_server or constants.LOCALHOST_IP
    if not is_ip_address(name_server):
        name_server = socket.gethostbyname(name_server)
    if is_aws_cloud():
        port = 53
    else:
        port = config.DNS_PORT

    # run the DNS resolution request
    try:
        response = dns.query.udp(request, name_server, timeout=5, port=port)
        if response.flags & dns.flags.TC:
            response = dns.query.tcp(request, name_server, timeout=5, port=port)
    except Exception:
        response = dns.query.tcp(request, name_server, timeout=5, port=port)

    records = []
    for answer in response.answer:
        for rec in answer:
            entry = {
                "type": str(dnslib.QTYPE.get(rec.rdtype)),
                "name": str(answer.name),
                "ttl": answer.ttl,
            }
            for attr in ["address", "target"]:
                value = getattr(rec, attr, None)
                if value:
                    entry[attr] = str(value)
            records.append(entry)
    return records


class TestRoute53:
    @pytest.mark.parametrize("local_zone", [True, False])
    @markers.aws.unknown
    @pytest.mark.skipif(
        not config.use_custom_dns(),
        reason="DNS resolution testing will hang if dns server is not available",
    )
    def test_dns_resolution(self, local_zone, route53_create_hosted_zone, aws_client):
        # create hosted zone
        zone_name = f"z-{short_uid()}.test" if local_zone else LOCALHOST_HOSTNAME
        zone_id = route53_create_hosted_zone(Name=zone_name, CallerReference="test123")

        # create record sets
        cname = f"{short_uid()}.{zone_name}"
        target1 = "target1.com."
        target2 = "target2.com."
        changes = [
            {
                "Action": "CREATE",
                "ResourceRecordSet": {
                    # create regular CNAME
                    "Name": cname,
                    "Type": "CNAME",
                    "ResourceRecords": [{"Value": target1}],
                },
            },
            {
                "Action": "CREATE",
                "ResourceRecordSet": {
                    # create wildcard subdomain
                    "Name": f"*.{cname}",
                    "Type": "CNAME",
                    "ResourceRecords": [{"Value": target2}],
                },
            },
        ]
        result = aws_client.route53.change_resource_record_sets(
            HostedZoneId=zone_id, ChangeBatch={"Comment": "test 123", "Changes": changes}
        )
        assert result["ResponseMetadata"]["HTTPStatusCode"] == 200

        # run DNS request (exact match, subdomain match)
        queries = [
            (cname, target1),
            (f"subdomain.{cname}", target2),
        ]
        for query, target in queries:
            query = query.rstrip(".")
            result = resolve_dns(query)
            cname_result = [res for res in result if res["type"] == "CNAME"][0]
            expected = {"type": "CNAME", "name": f"{query}.", "target": target}
            assert is_sub_dict(expected, cname_result)

    @markers.aws.validated
    @pytest.mark.skipif(
        not config.use_custom_dns() and not is_aws_cloud(),
        reason="DNS resolution testing will hang if dns server is not available",
    )
    def test_resource_record_lifecycle_with_dns_resolution(
        self, route53_create_hosted_zone, aws_client
    ):
        # create hosted zone
        zone_name = f"z-{short_uid()}.test"
        zone_id = route53_create_hosted_zone(Name=zone_name, CallerReference=f"test-{short_uid()}")
        dns_server_for_zone = aws_client.route53.get_hosted_zone(Id=zone_id)["DelegationSet"][
            "NameServers"
        ][0]

        # create record sets
        cname = f"{short_uid()}.{zone_name}"
        target1 = "target1.com."
        target2 = "target2.com."
        target3 = "target3.com."
        changes = [
            {
                "Action": "CREATE",
                "ResourceRecordSet": {
                    # create regular CNAME
                    "Name": cname,
                    "Type": "CNAME",
                    "TTL": 30,
                    "ResourceRecords": [{"Value": target1}],
                },
            },
            {
                "Action": "CREATE",
                "ResourceRecordSet": {
                    # create wildcard subdomain
                    "Name": f"*.{cname}",
                    "Type": "CNAME",
                    "TTL": 30,
                    "ResourceRecords": [{"Value": target2}],
                },
            },
        ]
        result = aws_client.route53.change_resource_record_sets(
            HostedZoneId=zone_id, ChangeBatch={"Comment": "test 123", "Changes": changes}
        )
        assert result["ResponseMetadata"]["HTTPStatusCode"] == 200
        # wait for change resource set finished
        aws_client.route53.get_waiter("resource_record_sets_changed").wait(
            Id=result["ChangeInfo"]["Id"]
        )

        def test_queries(queries: list[tuple[str, str]]):
            for query, target in queries:
                query = query.rstrip(".")
                result = resolve_dns(
                    query, name_server=dns_server_for_zone, datatype=RdataType.CNAME
                )
                if not target:
                    # TODO AWS does not return a single entry here, not even a SOA.
                    return not [res for res in result if res["type"] == "CNAME"]
                if not result:
                    return False
                cname_result = [res for res in result if res["type"] == "CNAME"][0]
                expected = {"type": "CNAME", "name": f"{query}.", "target": target}
                return is_sub_dict(expected, cname_result)

        queries = [
            (cname, target1),
            (f"subdomain.{cname}", target2),
        ]
        assert poll_condition(lambda: test_queries(queries=queries))

        changes = [
            {
                "Action": "UPSERT",
                "ResourceRecordSet": {
                    # create wildcard subdomain
                    "Name": f"*.{cname}",
                    "Type": "CNAME",
                    "TTL": 30,
                    "ResourceRecords": [{"Value": target3}],
                },
            },
        ]
        result = aws_client.route53.change_resource_record_sets(
            HostedZoneId=zone_id, ChangeBatch={"Comment": "test 123", "Changes": changes}
        )
        # wait for change resource set finished
        aws_client.route53.get_waiter("resource_record_sets_changed").wait(
            Id=result["ChangeInfo"]["Id"]
        )

        queries = [
            (f"subdomain.{cname}", target3),
        ]
        assert poll_condition(lambda: test_queries(queries=queries))

        changes = [
            {
                "Action": "DELETE",
                "ResourceRecordSet": {
                    # create wildcard subdomain
                    "Name": f"*.{cname}",
                    "Type": "CNAME",
                    "TTL": 30,
                    "ResourceRecords": [{"Value": target3}],
                },
            },
        ]
        result = aws_client.route53.change_resource_record_sets(
            HostedZoneId=zone_id, ChangeBatch={"Comment": "test 123", "Changes": changes}
        )
        # wait for change resource set finished
        aws_client.route53.get_waiter("resource_record_sets_changed").wait(
            Id=result["ChangeInfo"]["Id"]
        )

        queries = [
            (f"subdomain.{cname}", None),
        ]
        assert poll_condition(lambda: test_queries(queries=queries))

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(
        paths=[
            "$..MaxItems",
            "$..ResourceRecordSets..Name",
            "$..ResourceRecordSets..ResourceRecords..Value",
            "$..ChangeInfo.Comment",
            "$..ChangeInfo.Status",
            "$..DelegationSet.Id",
            "$..DelegationSet.NameServers",
            "$..HostedZone.CallerReference",
        ]
    )
    def test_resource_record_lifecycle(self, route53_create_hosted_zone, aws_client, snapshot):
        snapshot.add_transformer(
            snapshot.transform.jsonpath("$..HostedZone.Id", value_replacement="hosted-zone-id")
        )
        snapshot.add_transformer(
            snapshot.transform.jsonpath("$..ChangeInfo.Id", value_replacement="change-id")
        )
        snapshot.add_transformer(
            snapshot.transform.jsonpath(
                "$..DelegationSet.NameServers.[*]", value_replacement="nameserver"
            )
        )
        snapshot.add_transformer(
            snapshot.transform.jsonpath("$..HostedZone.Name", value_replacement="zone-name")
        )
        snapshot.add_transformer(snapshot.transform.key_value("CallerReference"))
        # create hosted zone
        zone_name = f"z-{short_uid()}.test"
        zone_id = route53_create_hosted_zone(Name=zone_name, CallerReference=f"test-{short_uid()}")

        get_hosted_zone_response = aws_client.route53.get_hosted_zone(Id=zone_id)
        snapshot.match("get-hosted-zone-response", get_hosted_zone_response)

        # create record sets
        cname = f"cname.{zone_name}"
        target1 = "target1.test."
        target2 = "subdomain.target1.test."
        changes = [
            {
                "Action": "CREATE",
                "ResourceRecordSet": {
                    # create regular CNAME
                    "Name": cname,
                    "Type": "CNAME",
                    "TTL": 30,
                    "ResourceRecords": [{"Value": target1}],
                },
            },
            {
                "Action": "UPSERT",
                "ResourceRecordSet": {
                    # create wildcard subdomain
                    "Name": f"*.{cname}",
                    "Type": "CNAME",
                    "TTL": 30,
                    "ResourceRecords": [{"Value": target1}],
                },
            },
        ]
        result = aws_client.route53.change_resource_record_sets(
            HostedZoneId=zone_id, ChangeBatch={"Comment": "test 123", "Changes": changes}
        )
        assert result["ResponseMetadata"]["HTTPStatusCode"] == 200
        snapshot.match("change-resource-record-sets-response", result)
        # wait for change resource set finished
        aws_client.route53.get_waiter("resource_record_sets_changed").wait(
            Id=result["ChangeInfo"]["Id"]
        )

        list_resource_record_sets_response = aws_client.route53.list_resource_record_sets(
            HostedZoneId=zone_id
        )
        snapshot.match("list-resource-record-sets-response", list_resource_record_sets_response)

        changes = [
            {
                "Action": "UPSERT",
                "ResourceRecordSet": {
                    # create wildcard subdomain
                    "Name": f"*.{cname}",
                    "Type": "CNAME",
                    "TTL": 30,
                    "ResourceRecords": [{"Value": target2}],
                },
            },
        ]
        result = aws_client.route53.change_resource_record_sets(
            HostedZoneId=zone_id, ChangeBatch={"Comment": "test 123", "Changes": changes}
        )
        # wait for change resource set finished
        aws_client.route53.get_waiter("resource_record_sets_changed").wait(
            Id=result["ChangeInfo"]["Id"]
        )

        list_resource_record_sets_response = aws_client.route53.list_resource_record_sets(
            HostedZoneId=zone_id
        )
        snapshot.match(
            "list-resource-record-sets-response-after-update", list_resource_record_sets_response
        )

        changes = [
            {
                "Action": "DELETE",
                "ResourceRecordSet": {
                    # create wildcard subdomain
                    "Name": cname,
                    "Type": "CNAME",
                    "TTL": 30,
                    "ResourceRecords": [{"Value": target1}],
                },
            },
        ]
        result = aws_client.route53.change_resource_record_sets(
            HostedZoneId=zone_id, ChangeBatch={"Comment": "test 123", "Changes": changes}
        )
        # wait for change resource set finished
        aws_client.route53.get_waiter("resource_record_sets_changed").wait(
            Id=result["ChangeInfo"]["Id"]
        )

        list_resource_record_sets_response = aws_client.route53.list_resource_record_sets(
            HostedZoneId=zone_id
        )
        snapshot.match(
            "list-resource-record-sets-response-after-delete", list_resource_record_sets_response
        )

    @markers.aws.unknown
    @pytest.mark.skipif(
        not config.use_custom_dns(),
        reason="DNS resolution testing will hang if dns server is not available",
    )
    def test_alias_target_resolution(self, route53_create_hosted_zone, aws_client):
        zone_name = "usecanopy.test"
        zone_id = route53_create_hosted_zone(Name=zone_name)

        # create record sets
        changes = [
            {
                "Action": "CREATE",
                "ResourceRecordSet": {
                    "Name": "anything.usecanopy.test",
                    "Type": "CNAME",
                    "ResourceRecords": [{"Value": "my.target.com"}],
                },
            },
            {
                "Action": "CREATE",
                "ResourceRecordSet": {
                    "Name": "hello.usecanopy.test",
                    "Type": "A",
                    "ResourceRecords": [{"Value": "1.2.3.4"}],
                },
            },
            {
                "Action": "CREATE",
                "ResourceRecordSet": {
                    "Name": "usecanopy.test",
                    "Type": "A",
                    "AliasTarget": {
                        "HostedZoneId": "Z2FDTNDATAQYW2",
                        "DNSName": "388453ae.cloudfront.localhost.localstack.cloud",
                        "EvaluateTargetHealth": True,
                    },
                },
            },
        ]

        # TODO: add snapshot for response of this call
        aws_client.route53.change_resource_record_sets(
            HostedZoneId=zone_id, ChangeBatch={"Changes": changes}
        )

        res = resolver.Resolver()
        res.nameservers = ["127.0.0.1"]
        res.nameserver_ports["127.0.0.1"] = config.DNS_PORT

        # resolving might take a few seconds
        def check_available():
            try:
                result = res.resolve("usecanopy.test").response.answer
                return len(result)
            except dns.exception.DNSException:
                return 0

        assert poll_condition(lambda: check_available() == 1, timeout=10)

        # check AliasTarget
        result = res.resolve("usecanopy.test").response.answer
        assert len(result) == 1
        assert result[0].to_text() == "usecanopy.test. 300 IN A 127.0.0.1"

        # check CNAME
        result = res.resolve("anything.usecanopy.test", rdtype=dns.rdatatype.CNAME).response.answer
        assert len(result) == 1
        assert result[0].to_text() == "anything.usecanopy.test. 300 IN CNAME my.target.com."

        # check A record
        result = res.resolve("hello.usecanopy.test").response.answer
        assert len(result) == 1
        assert result[0].to_text() == "hello.usecanopy.test. 300 IN A 1.2.3.4"

        # should be resolved implicitly
        result = res.resolve("388453ae.cloudfront.localhost.localstack.cloud").response.answer
        assert len(result) == 1
        assert (
            result[0].to_text()
            == "388453ae.cloudfront.localhost.localstack.cloud. 300 IN A 127.0.0.1"
        )

    @markers.aws.validated
    @pytest.mark.skipif(
        not config.use_custom_dns() and not is_aws_cloud(),
        reason="DNS resolution testing will hang if dns server is not available",
    )
    def test_alias_lifecycle_with_dns_resolution(self, route53_create_hosted_zone, aws_client):
        zone_name = "usecanopy.test"
        zone_id = route53_create_hosted_zone(Name=zone_name)
        dns_server_for_zone = aws_client.route53.get_hosted_zone(Id=zone_id)["DelegationSet"][
            "NameServers"
        ][0]

        # create record sets
        changes = [
            {
                "Action": "CREATE",
                "ResourceRecordSet": {
                    "Name": "hello.usecanopy.test",
                    "Type": "A",
                    "TTL": 300,
                    "ResourceRecords": [{"Value": "1.2.3.4"}],
                },
            },
            {
                "Action": "CREATE",
                "ResourceRecordSet": {
                    "Name": "goodbye.usecanopy.test",
                    "Type": "A",
                    "TTL": 300,
                    "ResourceRecords": [{"Value": "4.3.2.1"}],
                },
            },
            {
                "Action": "CREATE",
                "ResourceRecordSet": {
                    "Name": "usecanopy.test",
                    "Type": "A",
                    "AliasTarget": {
                        "HostedZoneId": zone_id.rpartition("/")[2],
                        "DNSName": "hello.usecanopy.test",
                        "EvaluateTargetHealth": True,
                    },
                },
            },
        ]

        result = aws_client.route53.change_resource_record_sets(
            HostedZoneId=zone_id, ChangeBatch={"Changes": changes}
        )
        aws_client.route53.get_waiter("resource_record_sets_changed").wait(
            Id=result["ChangeInfo"]["Id"]
        )

        res = resolver.Resolver()
        nameserver = dns_server_for_zone if is_aws_cloud() else "127.0.0.1"
        if not is_ip_address(nameserver):
            nameserver = socket.gethostbyname(nameserver)
        port = 53 if is_aws_cloud() else config.DNS_PORT
        res.nameservers = [nameserver]
        res.nameserver_ports[nameserver] = port

        # resolving might take a few seconds
        def check_available():
            try:
                result = res.resolve("usecanopy.test").response.answer
                return len(result)
            except dns.exception.DNSException:
                return 0

        assert poll_condition(lambda: check_available() == 1, timeout=10)

        # check AliasTarget
        result = res.resolve("usecanopy.test").response.answer
        assert len(result) == 1
        assert result[0].to_text() == "usecanopy.test. 300 IN A 1.2.3.4"

        # check A record
        result = res.resolve("hello.usecanopy.test").response.answer
        assert len(result) == 1
        assert result[0].to_text() == "hello.usecanopy.test. 300 IN A 1.2.3.4"

        # upsert alias
        changes = [
            {
                "Action": "UPSERT",
                "ResourceRecordSet": {
                    "Name": "usecanopy.test",
                    "Type": "A",
                    "AliasTarget": {
                        "HostedZoneId": zone_id.rpartition("/")[2],
                        "DNSName": "goodbye.usecanopy.test",
                        "EvaluateTargetHealth": True,
                    },
                },
            },
        ]

        result = aws_client.route53.change_resource_record_sets(
            HostedZoneId=zone_id, ChangeBatch={"Changes": changes}
        )
        aws_client.route53.get_waiter("resource_record_sets_changed").wait(
            Id=result["ChangeInfo"]["Id"]
        )

        result = res.resolve("usecanopy.test").response.answer
        assert len(result) == 1
        assert result[0].to_text() == "usecanopy.test. 300 IN A 4.3.2.1"

        # delete alias
        changes = [
            {
                "Action": "DELETE",
                "ResourceRecordSet": {
                    "Name": "usecanopy.test",
                    "Type": "A",
                    "AliasTarget": {
                        "HostedZoneId": zone_id.rpartition("/")[2],
                        "DNSName": "goodbye.usecanopy.test",
                        "EvaluateTargetHealth": True,
                    },
                },
            },
        ]

        result = aws_client.route53.change_resource_record_sets(
            HostedZoneId=zone_id, ChangeBatch={"Changes": changes}
        )
        aws_client.route53.get_waiter("resource_record_sets_changed").wait(
            Id=result["ChangeInfo"]["Id"]
        )

        # TODO as route53 response as authoritative dns server for the zone, it will not answer with NXDOMAIN
        # in contrast to our DNS server, which will answer with NXDOMAIN as returned from upstream DNS
        # with pytest.raises(resolver.NoAnswer):
        #     res.resolve("usecanopy.test")

    @markers.aws.unknown
    def test_health_checks(self, aws_client, echo_http_server_url, route53_create_health_check):
        parsed_url = urlparse(echo_http_server_url)
        protocol = parsed_url.scheme.upper()
        host, _, port = parsed_url.netloc.partition(":")
        port = port or (443 if protocol == "HTTPS" else 80)
        path = (
            f"{parsed_url.path}health"
            if parsed_url.path.endswith("/")
            else f"{parsed_url.path}/health"
        )

        good_health_check = route53_create_health_check(
            CallerReference=short_uid(),
            HealthCheckConfig={
                "FullyQualifiedDomainName": host,
                "Port": int(port),
                "ResourcePath": path,
                "Type": protocol,
                "RequestInterval": 10,
            },
        )["Id"]

        response = aws_client.route53.get_health_check_status(HealthCheckId=good_health_check)
        assert len(response["HealthCheckObservations"]) == 1
        observation = response["HealthCheckObservations"][0]
        assert observation["Region"] == "us-east-1"
        assert observation["IPAddress"] == "127.0.0.1"
        assert observation["StatusReport"]["Status"].startswith("Success")

        bad_health_check = route53_create_health_check(
            CallerReference=short_uid(),
            HealthCheckConfig={
                "FullyQualifiedDomainName": host,
                "Port": int(port),
                "ResourcePath": path,
                "Type": protocol,
                "RequestInterval": 10,
            },
        )["Id"]

        aws_client.route53.update_health_check(
            HealthCheckId=bad_health_check,
            FullyQualifiedDomainName=f"bad-host-{short_uid()}.com",
        )

        response = aws_client.route53.get_health_check_status(HealthCheckId=bad_health_check)
        assert len(response["HealthCheckObservations"]) == 1
        observation = response["HealthCheckObservations"][0]
        assert observation["Region"] == "us-east-1"
        assert observation["IPAddress"] == "127.0.0.1"
        assert observation["StatusReport"]["Status"].startswith("Failure")

    # currently not working in host mode, as DNS server is running in a separate process
    @pytest.mark.skipif(
        not config.use_custom_dns() and not is_aws_cloud(),
        reason="DNS resolution testing will hang if dns server is not available",
    )
    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(
        paths=[
            "$..CallerReference",
            "$..HealthCheckConfig.EnableSNI",
            "$..HealthCheckConfig.FullyQualifiedDomainName",
            "$..HealthCheckConfig.IPAddress",
            "$..HealthCheckConfig.Port",
            "$..HealthCheckConfig.Type",
            "$..ttl",
        ]
    )
    def test_dns_failover_based_on_health_check(
        self,
        route53_create_hosted_zone,
        route53_create_health_check,
        echo_http_server_url,
        aws_client,
        snapshot,
    ):
        snapshot.add_transformer(snapshot.transform.key_value("CallerReference"))
        client = aws_client.route53

        # create hosted zone
        zone_name = f"ls-test-{short_uid()}.com"
        zone_id = route53_create_hosted_zone(Name=zone_name)
        zone_id = zone_id.split("/")[-1]
        snapshot.add_transformer(snapshot.transform.regex(zone_id, "<zone-id>"))
        snapshot.add_transformer(snapshot.transform.regex(zone_name, "<zone-name>"))
        result = client.get_hosted_zone(Id=zone_id)
        snapshot.match("hosted-zone", result["HostedZone"])
        nameserver = result["DelegationSet"]["NameServers"][0]

        # create health check
        parsed_url = urlparse(echo_http_server_url)
        protocol = parsed_url.scheme.upper()
        host, _, port = parsed_url.netloc.partition(":")
        port = port or (443 if protocol == "HTTPS" else 80)
        path = (
            f"{parsed_url.path}health"
            if parsed_url.path.endswith("/")
            else f"{parsed_url.path}/health"
        )
        health_check = route53_create_health_check(
            CallerReference=short_uid(),
            HealthCheckConfig={
                "FullyQualifiedDomainName": host,
                "Port": int(port),
                "ResourcePath": path,
                "Type": protocol,
                "RequestInterval": 10,
            },
        )
        snapshot.match("health-check", health_check)

        # create record sets for target1 & target2
        changes = [
            {
                "Action": "CREATE",
                "ResourceRecordSet": {
                    "Name": f"{target}.{zone_name}",
                    "Type": "CNAME",
                    "TTL": 60,
                    "ResourceRecords": [{"Value": f"{target}.example.com"}],
                },
            }
            for target in ("target1", "target2")
        ]
        client.change_resource_record_sets(HostedZoneId=zone_id, ChangeBatch={"Changes": changes})

        # create record sets for alias targets
        changes = [
            {
                "Action": "CREATE",
                "ResourceRecordSet": {
                    "Name": f"test.{zone_name}",
                    "Type": "CNAME",
                    "SetIdentifier": "target1",
                    "HealthCheckId": health_check["Id"],
                    "Failover": "PRIMARY",
                    "AliasTarget": {
                        "HostedZoneId": zone_id,
                        "DNSName": f"target1.{zone_name}",
                        "EvaluateTargetHealth": True,
                    },
                },
            },
            {
                "Action": "CREATE",
                "ResourceRecordSet": {
                    "Name": f"test.{zone_name}",
                    "Type": "CNAME",
                    "SetIdentifier": "target2",
                    "Failover": "SECONDARY",
                    "AliasTarget": {
                        "HostedZoneId": zone_id,
                        "DNSName": f"target2.{zone_name}",
                        "EvaluateTargetHealth": True,
                    },
                },
            },
        ]
        client.change_resource_record_sets(HostedZoneId=zone_id, ChangeBatch={"Changes": changes})

        # Note for snapshot testing: you may need to flush your local DNS cache for this test to succeed
        sleep_before = 5 if is_aws_cloud() else 0

        def _check_resolve(name: str, expected_target: str = None):
            result = resolve_dns(name, name_server=nameserver, datatype=RdataType.CNAME)
            assert result
            if expected_target:
                returned_target = result[0].get("target") or result[0].get("address")
                assert returned_target == expected_target
            return result

        def _resolve(name: str, expected_target: str = None):
            return retry(
                _check_resolve,
                name=name,
                expected_target=expected_target,
                retries=30,
                sleep=3,
                sleep_before=sleep_before,
            )

        # assert that the correct result (target1) is being returned
        result = _resolve(f"target1.{zone_name}")
        snapshot.match("dns-resolved-1", result)
        result = _resolve(f"test.{zone_name}", expected_target="target1.example.com.")
        snapshot.match("dns-resolved-2", result)

        # update health check with invalid target host
        client.update_health_check(
            HealthCheckId=health_check["Id"],
            FullyQualifiedDomainName=f"invalid-host-{short_uid()}.com",
        )
        # assert that the correct result (now fallback target, target2) is being returned
        result = _resolve(f"test.{zone_name}", expected_target="target2.example.com.")
        snapshot.match("dns-resolved-3", result)
