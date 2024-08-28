import json

import pytest as pytest
from localstack.pro.core.aws.api.servicediscovery import (
    DnsConfig,
    DnsRecord,
    RecordType,
    RoutingPolicy,
)
from localstack.testing.pytest import markers
from localstack.utils.functions import empty_context_manager
from localstack.utils.strings import short_uid
from localstack.utils.sync import retry, wait_until
from localstack_snapshot.snapshots.transformer import GenericTransformer

from tests.aws.services.servicediscovery.helper_functions import (
    cleanup_namespace,
    delete_service,
    deregister_instance,
    operation_succeeded,
)


class TestServicediscovery:
    @pytest.fixture(autouse=True)
    def servicediscovery_api_snapshot_transformer(self, snapshot):
        snapshot.add_transformer(snapshot.transform.key_value("Id"))
        snapshot.add_transformer(snapshot.transform.key_value("Name"))
        snapshot.add_transformer(
            snapshot.transform.key_value("CreateDate", reference_replacement=False)
        )
        snapshot.add_transformer(
            snapshot.transform.key_value("HostedZoneId", reference_replacement=False)
        )

    # TODO: test updates
    # TODO: parameterize for different namespaces (public/private DNS, http)
    # TODO: parameterize tagging for service/namespace
    # TODO: test tag collision/duplicates + error cases
    @markers.aws.unknown
    def test_create_service(self, aws_client):
        service_name = f"service-{short_uid()}"
        service_description = "service-description"
        namespace_name = f"namespace-{short_uid()}"
        tag1 = {"Key": "Tag1Key", "Value": "Tag1Value"}
        tag2 = {"Key": "Tag2Key", "Value": "Tag2Value"}

        # create namespace
        create_namespace_result = aws_client.servicediscovery.create_http_namespace(
            Name=namespace_name, Tags=[tag1]
        )
        assert wait_until(operation_succeeded(create_namespace_result["OperationId"], aws_client))
        operation = aws_client.servicediscovery.get_operation(
            OperationId=create_namespace_result["OperationId"]
        )
        namespace_id = operation["Operation"]["Targets"]["NAMESPACE"]

        # list namespaces
        list_namespaces_result = aws_client.servicediscovery.list_namespaces()
        assert namespace_id in [
            namespace["Id"] for namespace in list_namespaces_result["Namespaces"]
        ]

        # get namespace
        get_namespace_result = aws_client.servicediscovery.get_namespace(Id=namespace_id)
        namespace_arn = get_namespace_result["Namespace"]["Arn"]
        assert namespace_id in namespace_arn
        assert get_namespace_result["Namespace"]["Id"] == namespace_id
        assert get_namespace_result["Namespace"]["Name"] == namespace_name

        # namespace tag support
        namespace_tags_before = aws_client.servicediscovery.list_tags_for_resource(
            ResourceARN=namespace_arn
        )["Tags"]
        assert tag1 in namespace_tags_before
        aws_client.servicediscovery.tag_resource(
            ResourceARN=get_namespace_result["Namespace"]["Arn"], Tags=[tag2]
        )
        namespace_tags_after = aws_client.servicediscovery.list_tags_for_resource(
            ResourceARN=namespace_arn
        )["Tags"]
        assert tag1 in namespace_tags_after
        assert tag2 in namespace_tags_after
        aws_client.servicediscovery.untag_resource(ResourceARN=namespace_arn, TagKeys=[tag1["Key"]])
        namespace_tags_after_delete = aws_client.servicediscovery.list_tags_for_resource(
            ResourceARN=namespace_arn
        )["Tags"]
        assert tag1 not in namespace_tags_after_delete
        assert tag2 in namespace_tags_after_delete

        # create service
        create_service_result = aws_client.servicediscovery.create_service(
            Name=service_name,
            NamespaceId=namespace_id,
            Description=service_description,
            Tags=[tag1],
        )
        service_id = create_service_result["Service"]["Id"]
        assert create_service_result["Service"]["Name"] == service_name
        assert create_service_result["Service"]["NamespaceId"] == namespace_id

        # list services
        list_services_result = aws_client.servicediscovery.list_services()
        service_names = [s["Name"] for s in list_services_result["Services"]]
        assert service_name in service_names

        # get service
        get_service_result = aws_client.servicediscovery.get_service(Id=service_id)
        assert get_service_result["Service"]["Name"] == service_name
        assert get_service_result["Service"]["Id"] == service_id
        service_arn = get_service_result["Service"]["Arn"]
        assert service_id in service_arn

        # service tag support
        service_tags_before = aws_client.servicediscovery.list_tags_for_resource(
            ResourceARN=service_arn
        )["Tags"]
        assert tag1 in service_tags_before
        aws_client.servicediscovery.tag_resource(
            ResourceARN=get_service_result["Service"]["Arn"], Tags=[tag2]
        )
        service_tags_after = aws_client.servicediscovery.list_tags_for_resource(
            ResourceARN=service_arn
        )["Tags"]
        assert tag1 in service_tags_after
        assert tag2 in service_tags_after
        aws_client.servicediscovery.untag_resource(ResourceARN=service_arn, TagKeys=[tag1["Key"]])
        service_tags_after_delete = aws_client.servicediscovery.list_tags_for_resource(
            ResourceARN=service_arn
        )["Tags"]
        assert tag1 not in service_tags_after_delete
        assert tag2 in service_tags_after_delete

        # delete service
        aws_client.servicediscovery.delete_service(Id=service_id)
        # delete namespace
        delete_namespace_result = aws_client.servicediscovery.delete_namespace(Id=namespace_id)
        assert wait_until(operation_succeeded(delete_namespace_result["OperationId"], aws_client))

    @markers.snapshot.skip_snapshot_verify(
        paths=[
            "$..Service.CreateDate",  # missing
            "$..Service.DnsConfig",  # missing
            "$..Service.Type",  # missing
            "$..CreatorRequestId",  # not the same as in create_service
        ]
    )
    @markers.aws.validated
    def test_create_service_exceptions(self, aws_client, snapshot):
        service_name = f"service-{short_uid()}"
        namespace_name = f"namespace-{short_uid()}.com"

        snapshot.add_transformer(snapshot.transform.regex(service_name, "<service-name>"))
        snapshot.add_transformer(snapshot.transform.key_value("ServiceId"))
        snapshot.add_transformer(snapshot.transform.key_value("NamespaceId"))

        # create namespace
        create_namespace_result = aws_client.servicediscovery.create_public_dns_namespace(
            Name=namespace_name
        )
        assert wait_until(operation_succeeded(create_namespace_result["OperationId"], aws_client))
        operation = aws_client.servicediscovery.get_operation(
            OperationId=create_namespace_result["OperationId"]
        )
        namespace_id = operation["Operation"]["Targets"]["NAMESPACE"]

        # create service
        create_service_result = aws_client.servicediscovery.create_service(
            Name=service_name,
            DnsConfig=DnsConfig(
                NamespaceId=namespace_id,
                RoutingPolicy=RoutingPolicy.WEIGHTED,
                DnsRecords=[DnsRecord(TTL=300, Type=RecordType.CNAME)],
            ),
        )
        snapshot.match("create-service", create_service_result)
        # TODO: assert service id prefix "srv-"
        service_id = create_service_result["Service"]["Id"]

        # create service with duplicated name and the same namespace on top level
        with pytest.raises(aws_client.servicediscovery.exceptions.ServiceAlreadyExists) as e:
            aws_client.servicediscovery.create_service(
                Name=service_name,
                NamespaceId=namespace_id,
                DnsConfig=DnsConfig(
                    NamespaceId=namespace_id,
                    RoutingPolicy=RoutingPolicy.WEIGHTED,
                    DnsRecords=[DnsRecord(TTL=300, Type=RecordType.CNAME)],
                ),
            )
        snapshot.match("create-service-with-same-name", e.value.response)

        # create service with duplicated name and the same namespace in the DNS config
        with pytest.raises(aws_client.servicediscovery.exceptions.ServiceAlreadyExists) as e:
            aws_client.servicediscovery.create_service(
                Name=service_name,
                DnsConfig=DnsConfig(
                    NamespaceId=namespace_id,
                    RoutingPolicy=RoutingPolicy.WEIGHTED,
                    DnsRecords=[DnsRecord(TTL=300, Type=RecordType.CNAME)],
                ),
            )
        snapshot.match("create-service-with-same-name-dns-namespace", e.value.response)

        # TODO: ensure cleanup upon test failure
        # delete service
        aws_client.servicediscovery.delete_service(Id=service_id)
        with pytest.raises(aws_client.servicediscovery.exceptions.ServiceNotFound) as e:
            aws_client.servicediscovery.get_service(Id=service_id)
        snapshot.match("get-service-doesnotexist", e.value.response)

        # delete namespace
        delete_namespace_result = aws_client.servicediscovery.delete_namespace(Id=namespace_id)
        assert wait_until(operation_succeeded(delete_namespace_result["OperationId"], aws_client))
        with pytest.raises(aws_client.servicediscovery.exceptions.NamespaceNotFound) as e:
            aws_client.servicediscovery.get_namespace(Id=namespace_id)
        snapshot.match("get-namespace-doesnotexist", e.value.response)

    @markers.snapshot.skip_snapshot_verify(
        paths=[
            "$..Service.CreateDate",  # missing
            "$..Service.Type",  # missing
            "$..Instances..HealthStatus",
            "$..Instances..NamespaceName",
            "$..Instances..ServiceName",
            "$..InstancesRevision",
        ]
    )
    @markers.aws.validated
    def test_register_instance(self, aws_client, snapshot, cleanups):
        # create namespace
        namespace = f"test.ns-{short_uid()}"
        create_namespace_result = aws_client.servicediscovery.create_public_dns_namespace(
            Name=namespace
        )
        assert wait_until(operation_succeeded(create_namespace_result["OperationId"], aws_client))
        operation = aws_client.servicediscovery.get_operation(
            OperationId=create_namespace_result["OperationId"]
        )
        namespace_id = operation["Operation"]["Targets"]["NAMESPACE"]

        cleanups.append(lambda: cleanup_namespace(namespace_id, aws_client))

        # create service
        service_name = f"s-{short_uid()}"
        discover_instances_result = aws_client.servicediscovery.create_service(
            Name=service_name,
            NamespaceId=namespace_id,
            DnsConfig={
                "NamespaceId": namespace_id,
                "RoutingPolicy": "WEIGHTED",
                "DnsRecords": [{"Type": "A", "TTL": 100}],
            },
        )
        snapshot.match("create-service-with-dns-config", discover_instances_result)
        service_id = discover_instances_result["Service"]["Id"]
        # add delete service cleanup
        cleanups.append(lambda: aws_client.servicediscovery.delete_service(Id=service_id))

        instance_id = f"instance-{short_uid()}"
        creator_request_id = f"request-{short_uid()}"

        snapshot.add_transformer(
            snapshot.transform.key_value("CreateDate", reference_replacement=False)
        )
        snapshot.add_transformer(
            snapshot.transform.key_value("UpdateDate", reference_replacement=False)
        )
        snapshot.add_transformer(snapshot.transform.key_value("OperationId"))
        snapshot.add_transformer(
            snapshot.transform.key_value("InstancesRevision", reference_replacement=False)
        )
        snapshot.add_transformer(snapshot.transform.regex(namespace, "<namespace>"))
        snapshot.add_transformer(snapshot.transform.regex(namespace_id, "<namespace-id>"))
        snapshot.add_transformer(snapshot.transform.regex(service_name, "<service-name>"))
        snapshot.add_transformer(snapshot.transform.regex(service_id, "<service-id>"))
        snapshot.add_transformer(snapshot.transform.regex(instance_id, "<instance-id>"))
        snapshot.add_transformer(snapshot.transform.regex(creator_request_id, "<request-id>"))

        # update service
        update_service_result = aws_client.servicediscovery.update_service(
            Id=service_id,
            Service={
                "Description": "description 2.0",
                "DnsConfig": {
                    "DnsRecords": [{"Type": "A", "TTL": 150}],
                },
            },
        )
        snapshot.match("update-service-result", update_service_result)
        assert update_service_result["OperationId"]

        # register instance
        register_instance_result = aws_client.servicediscovery.register_instance(
            ServiceId=service_id,
            InstanceId=instance_id,
            CreatorRequestId=creator_request_id,
            Attributes={"AWS_INSTANCE_IPV4": "172.0.0.1", "AWS_INSTANCE_PORT": "8080"},
        )
        # register instance requests targeting the same service ID and instance ID cannot happen in parallel:
        # https://docs.aws.amazon.com/cloud-map/latest/api/API_RegisterInstance.html
        assert wait_until(operation_succeeded(register_instance_result["OperationId"], aws_client))
        snapshot.match("register-instance-result", register_instance_result)

        # get instance
        get_instance_result = aws_client.servicediscovery.get_instance(
            ServiceId=service_id, InstanceId=instance_id
        )
        snapshot.match("get-instance", get_instance_result)

        # register existing same instance leads to update
        register_instance_result_v2 = aws_client.servicediscovery.register_instance(
            ServiceId=service_id,
            InstanceId=instance_id,
            CreatorRequestId=creator_request_id,
            Attributes={"AWS_INSTANCE_IPV4": "172.1.1.1", "AWS_INSTANCE_PORT": "8080"},
        )
        assert wait_until(
            operation_succeeded(register_instance_result_v2["OperationId"], aws_client)
        )
        snapshot.match("register-instance-result-v2", register_instance_result_v2)

        # get instance
        get_instance_result_v2 = aws_client.servicediscovery.get_instance(
            ServiceId=service_id, InstanceId=instance_id
        )
        snapshot.match("get-instance-v2", get_instance_result_v2)

        # list instances
        list_instances_result = aws_client.servicediscovery.list_instances(ServiceId=service_id)
        instance_matches = [i for i in list_instances_result["Instances"] if i["Id"] == instance_id]
        snapshot.match("list-instances-matching-id", instance_matches)

        # discover instance
        discover_instances_result = aws_client.servicediscovery.discover_instances(
            ServiceName=service_name, NamespaceName=namespace
        )
        snapshot.match("discover-instances-result", discover_instances_result)

        # deregister instance
        deregister_instance_result = aws_client.servicediscovery.deregister_instance(
            ServiceId=service_id, InstanceId=instance_id
        )
        assert wait_until(
            operation_succeeded(deregister_instance_result["OperationId"], aws_client)
        )
        snapshot.match("deregister-instance-result", deregister_instance_result)

    @markers.snapshot.skip_snapshot_verify(
        paths=[
            "$..InstancesRevision",
        ]
    )
    @markers.aws.validated
    def test_register_instance_exceptions(self, aws_client, snapshot, cleanups):
        # create namespace
        namespace = f"test.ns-{short_uid()}"
        create_namespace_result = aws_client.servicediscovery.create_public_dns_namespace(
            Name=namespace
        )
        assert wait_until(operation_succeeded(create_namespace_result["OperationId"], aws_client))
        operation = aws_client.servicediscovery.get_operation(
            OperationId=create_namespace_result["OperationId"]
        )
        namespace_id = operation["Operation"]["Targets"]["NAMESPACE"]

        cleanups.append(lambda: cleanup_namespace(namespace_id, aws_client))

        # create service
        service_name = f"s-{short_uid()}"
        create_service_result = aws_client.servicediscovery.create_service(
            Name=service_name,
            NamespaceId=namespace_id,
            DnsConfig={
                "NamespaceId": namespace_id,
                "RoutingPolicy": "WEIGHTED",
                "DnsRecords": [{"Type": "A", "TTL": 100}],
            },
        )
        service_id = create_service_result["Service"]["Id"]
        # add delete service cleanup
        cleanups.append(lambda: aws_client.servicediscovery.delete_service(Id=service_id))

        snapshot.add_transformer(snapshot.transform.regex(service_id, "<service-id>"))

        # register instance
        with pytest.raises(aws_client.servicediscovery.exceptions.ServiceNotFound) as e:
            aws_client.servicediscovery.register_instance(
                ServiceId="doesnotexist-service-id",
                InstanceId="doesnotexist-instance-id",
                Attributes={"AWS_INSTANCE_IPV4": "172.0.0.1", "AWS_INSTANCE_PORT": "8080"},
            )
        snapshot.match("register-instance-doesnotexist", e.value.response)

        # get instance
        with pytest.raises(aws_client.servicediscovery.exceptions.InstanceNotFound) as e:
            aws_client.servicediscovery.get_instance(
                ServiceId=service_id, InstanceId="doesnotexist"
            )
        snapshot.match("get-instance-doesnotexist", e.value.response)

        # discover instance
        with pytest.raises(aws_client.servicediscovery.exceptions.NamespaceNotFound) as e:
            aws_client.servicediscovery.discover_instances(
                ServiceName=service_name, NamespaceName="doesnotexist"
            )
        snapshot.match("discover-instance-namespace-doesnotexist", e.value.response)

        discover_instances_result_doesnotexist = aws_client.servicediscovery.discover_instances(
            ServiceName="doesnotexist", NamespaceName=namespace
        )
        snapshot.match(
            "discover-instances-result-doesnotexist", discover_instances_result_doesnotexist
        )

        # deregister instance
        with pytest.raises(aws_client.servicediscovery.exceptions.ServiceNotFound) as e:
            aws_client.servicediscovery.deregister_instance(
                ServiceId="doesnotexist-service-id", InstanceId="doesnotexist-instance-id"
            )
        snapshot.match("deregister-instance-service-doesnotexist", e.value.response)

        with pytest.raises(aws_client.servicediscovery.exceptions.InstanceNotFound) as e:
            aws_client.servicediscovery.deregister_instance(
                ServiceId=service_id, InstanceId="doesnotexist"
            )
        snapshot.match("deregister-instance-instance-doesnotexist", e.value.response)

    @markers.snapshot.skip_snapshot_verify(
        paths=[
            "$..InstancesRevision",
        ]
    )
    @markers.aws.validated
    def test_filtering_http_namespace(self, aws_client, snapshot, cleanups):
        # create namespace
        namespace = f"test-ns-{short_uid()}"
        create_namespace_result = aws_client.servicediscovery.create_http_namespace(Name=namespace)
        assert wait_until(operation_succeeded(create_namespace_result["OperationId"], aws_client))
        operation = aws_client.servicediscovery.get_operation(
            OperationId=create_namespace_result["OperationId"]
        )
        namespace_id = operation["Operation"]["Targets"]["NAMESPACE"]
        cleanups.append(lambda: cleanup_namespace(namespace_id, aws_client))

        # list namespaces with filter matching
        list_namespaces_result = aws_client.servicediscovery.list_namespaces(
            Filters=[{"Name": "HTTP_NAME", "Values": [namespace]}]
        )
        snapshot.match("list-namespaces-filter-exist", list_namespaces_result)
        # list namespace with filter matching multiple complex filters
        # NAME, HTTP_NAME and TYPE all only support EQ and BEGINS_WITH conditions
        # EQ and BEGINS_WITH only support a single value
        list_namespaces_result = aws_client.servicediscovery.list_namespaces(
            Filters=[
                {"Name": "HTTP_NAME", "Values": [namespace], "Condition": "BEGINS_WITH"},
                {
                    "Name": "TYPE",
                    "Values": ["HTTP"],
                    "Condition": "EQ",
                },
            ]
        )
        snapshot.match("list-namespaces-filter-exist-complex", list_namespaces_result)
        # list namespaces with filter not matching
        list_namespaces_result = aws_client.servicediscovery.list_namespaces(
            Filters=[{"Name": "HTTP_NAME", "Values": ["doesnotexist"]}]
        )
        snapshot.match("list-namespaces-filter-doesnotexist", list_namespaces_result)
        # list namespaces with filter not matching multiple complex filters
        list_namespaces_result = aws_client.servicediscovery.list_namespaces(
            Filters=[
                {"Name": "NAME", "Values": ["doesnotexist"], "Condition": "EQ"},  # no match
                {"Name": "TYPE", "Values": ["HTTP"], "Condition": "BEGINS_WITH"},  # match
            ]
        )
        snapshot.match("list-namespaces-filter-doesnotexist-complex", list_namespaces_result)

        # create service
        service_name = f"test-service-{short_uid()}"
        key_service = "testkey_service"
        value_service = "testvalue_service"
        tag1 = {"Key": key_service, "Value": value_service}
        create_service_result = aws_client.servicediscovery.create_service(
            Name=service_name,
            NamespaceId=namespace_id,
            Description="service description",
            Tags=[tag1],
        )
        service_id = create_service_result["Service"]["Id"]
        cleanups.append(lambda: delete_service(service_id, aws_client))

        # list services with filter matching
        list_services_result = aws_client.servicediscovery.list_services(
            Filters=[{"Name": "NAMESPACE_ID", "Values": [namespace_id]}]
        )
        snapshot.match("list-services-filter-exist", list_services_result)
        # list services with filter matching multiple complex filters
        # only NAMESPACE_ID with EQ condition supported by AWS
        list_services_result = aws_client.servicediscovery.list_services(
            Filters=[
                {"Name": "NAMESPACE_ID", "Values": [namespace_id], "Condition": "EQ"},
            ]
        )
        snapshot.match("list-service-filter-exist-complex", list_services_result)
        # list services with filter not matching
        list_services_result = aws_client.servicediscovery.list_services(
            Filters=[{"Name": "NAMESPACE_ID", "Values": ["doesnotexist"]}]
        )
        snapshot.match("list-services-filter-doesnotexist", list_services_result)
        # list services with filter matching multiple complex filters
        list_services_result = aws_client.servicediscovery.list_services(
            Filters=[
                {"Name": "NAMESPACE_ID", "Values": ["doesnotexists"], "Condition": "EQ"},
            ]
        )
        snapshot.match("list-services-filter-doesnotexist-complex", list_services_result)

        # register instance
        instance_id = f"test-instance-{short_uid()}"
        creator_request_id = f"request-{short_uid()}"
        key_instance = "testkey_instance"
        value_instance = "testvalue_instance"
        register_instance_result = aws_client.servicediscovery.register_instance(
            ServiceId=service_id,
            InstanceId=instance_id,
            CreatorRequestId=creator_request_id,
            Attributes={
                "AWS_INSTANCE_IPV4": "172.0.0.1",
                "AWS_INSTANCE_PORT": "8080",
                key_instance: value_instance,
            },
        )
        # register instance requests targeting the same service ID and instance ID cannot happen in parallel:
        # https://docs.aws.amazon.com/cloud-map/latest/api/API_RegisterInstance.html
        assert wait_until(operation_succeeded(register_instance_result["OperationId"], aws_client))
        cleanups.append(lambda: deregister_instance(instance_id, service_id, aws_client))

        # register instance with optional parameter
        optional_instance_id = f"test-optional-instance-{short_uid()}"
        creator_request_id = f"request-optional-{short_uid()}"
        optional_key_instance = "optionalkey_instance"
        optional_value_instance = "optionalvalue_instance"
        register_instance_result = aws_client.servicediscovery.register_instance(
            ServiceId=service_id,
            InstanceId=optional_instance_id,
            CreatorRequestId=creator_request_id,
            Attributes={
                "AWS_INSTANCE_IPV4": "172.0.0.1",
                "AWS_INSTANCE_PORT": "8080",
                key_instance: value_instance,
                optional_key_instance: optional_value_instance,
            },
        )
        # register instance requests targeting the same service ID and instance ID cannot happen in parallel:
        # https://docs.aws.amazon.com/cloud-map/latest/api/API_RegisterInstance.html
        assert wait_until(operation_succeeded(register_instance_result["OperationId"], aws_client))
        cleanups.append(lambda: deregister_instance(instance_id, service_id, aws_client))

        # discover instance with filter parameter matching
        discover_instance_results = aws_client.servicediscovery.discover_instances(
            ServiceName=service_name,
            NamespaceName=namespace,
            QueryParameters={key_instance: value_instance},
        )
        snapshot.match("discover-instances-result-parameter-exist", discover_instance_results)
        # discover instance with filter parameter not matching
        discover_instance_results = aws_client.servicediscovery.discover_instances(
            ServiceName=service_name,
            NamespaceName=namespace,
            QueryParameters={"env": "doesnotexist"},
        )
        snapshot.match(
            "discover-instances-result-parameter-doesnotexist", discover_instance_results
        )
        # discover instance with filter parameter not matching key non existant
        discover_instance_results = aws_client.servicediscovery.discover_instances(
            ServiceName=service_name,
            NamespaceName=namespace,
            QueryParameters={"env": value_instance},
        )
        snapshot.match(
            "discover-instances-result-parameter-doesnotexist-wrong-key", discover_instance_results
        )
        # discover instance with filter parameter not matching value non existant
        discover_instance_results = aws_client.servicediscovery.discover_instances(
            ServiceName=service_name,
            NamespaceName=namespace,
            QueryParameters={key_instance: "doesnotexist"},
        )
        snapshot.match(
            "discover-instances-result-parameter-doesnotexist-wrong-value",
            discover_instance_results,
        )

        # discover instance with filter parameter matching and optional parameter matching
        discover_instance_results = aws_client.servicediscovery.discover_instances(
            ServiceName=service_name,
            NamespaceName=namespace,
            QueryParameters={key_instance: value_instance},
            OptionalParameters={optional_key_instance: optional_value_instance},
        )
        snapshot.match(
            "discover-instances-result-parameter-exist-optionalparameter-exists",
            discover_instance_results,
        )

        # discover instance with filter parameter matching and optional parameter not matching
        discover_instance_results = aws_client.servicediscovery.discover_instances(
            ServiceName=service_name,
            NamespaceName=namespace,
            QueryParameters={key_instance: value_instance},
            OptionalParameters={"env": "doesnotexist"},
        )
        snapshot.match(
            "discover-instances-result-parameter-exist-optionalparameter-doesnotexist",
            discover_instance_results,
        )

        # add transformers
        snapshot.add_transformer(
            snapshot.transform.key_value("CreateDate", reference_replacement=False)
        )
        snapshot.add_transformer(
            snapshot.transform.key_value("UpdateDate", reference_replacement=False)
        )
        snapshot.add_transformer(snapshot.transform.key_value("OperationId"))
        snapshot.add_transformer(
            snapshot.transform.key_value("InstancesRevision", reference_replacement=False)
        )
        snapshot.add_transformer(snapshot.transform.regex(namespace, "<namespace>"))
        snapshot.add_transformer(snapshot.transform.regex(namespace_id, "<namespace-id>"))
        snapshot.add_transformer(snapshot.transform.regex(service_name, "<service-name>"))
        snapshot.add_transformer(snapshot.transform.regex(service_id, "<service-id>"))
        snapshot.add_transformer(snapshot.transform.regex(instance_id, "<instance-id>"))
        snapshot.add_transformer(snapshot.transform.regex(optional_instance_id, "<instance-id>"))
        snapshot.add_transformer(snapshot.transform.regex(creator_request_id, "<request-id>"))
        snapshot.add_transformer(
            snapshot.transform.jsonpath("$..Instances..HealthStatus", "health-status")
        )

    @markers.aws.unknown
    def test_dns_namespace_public(self, aws_client):
        ns_public = f"ns-public.{short_uid()}"

        # assert creation with invalid name fails (AWS parity)
        with pytest.raises(Exception) as e:
            aws_client.servicediscovery.create_public_dns_namespace(Name="invalid_name")
        e.match("InvalidInput")

        # create public namespace

        def _assert_created():
            list_result = aws_client.servicediscovery.list_namespaces()["Namespaces"]
            matching = [ns for ns in list_result if ns["Name"] == ns_public]
            assert len(matching) == 1
            return matching[0]["Id"]

        create_public = aws_client.servicediscovery.create_public_dns_namespace(Name=ns_public)
        op_id = create_public["OperationId"]
        assert op_id
        namespace_id = retry(_assert_created, sleep=1, retries=45, sleep_before=0)

        # delete public namespace

        def _assert_deleted():
            list_result = aws_client.servicediscovery.list_namespaces()
            matching = [ns for ns in list_result["Namespaces"] if ns["Name"] == ns_public]
            assert len(matching) == 0

        delete_ns = aws_client.servicediscovery.delete_namespace(Id=namespace_id)
        assert delete_ns["OperationId"]
        retry(_assert_deleted, sleep=1, retries=45, sleep_before=0)

    @markers.aws.only_localstack  # TODO - VPC integration not fully compatible yet
    def test_dns_namespace_private(self, aws_client, cleanups):
        # create private namespace

        ns_private = f"ns-private.{short_uid()}"

        # we must create the VPC or else Route53 will raise an error that the VPC does not exist
        vpc_create_result = aws_client.ec2.create_vpc(CidrBlock="10.0.1.0/16")
        vpc_id = vpc_create_result["Vpc"]["VpcId"]
        cleanups.append(lambda: aws_client.ec2.delete_vpc(VpcId=vpc_id))

        def _assert_created():
            list_result = aws_client.servicediscovery.list_namespaces()
            matching = [ns for ns in list_result["Namespaces"] if ns["Name"] == ns_private]
            assert len(matching) == 1
            return matching[0]["Id"]

        create_private = aws_client.servicediscovery.create_private_dns_namespace(
            Name=ns_private, Vpc=vpc_id
        )
        op_id = create_private["OperationId"]
        assert op_id
        namespace_id = retry(_assert_created, sleep=1, retries=45, sleep_before=0)

        def _assert_deleted():
            list_result = aws_client.servicediscovery.list_namespaces()
            matching = [ns for ns in list_result["Namespaces"] if ns["Name"] == ns_private]
            assert len(matching) == 0

        delete_ns = aws_client.servicediscovery.delete_namespace(Id=namespace_id)
        assert delete_ns["OperationId"]
        retry(_assert_deleted, sleep=1, retries=45, sleep_before=0)

    @markers.aws.validated
    @markers.snapshot.skip_snapshot_verify(paths=["$..OperationId"])
    def test_dns_namespace_private_hosted_zone(self, aws_client, snapshot, default_vpc, cleanups):
        domain_name = f"domain-{short_uid()}.com"
        snapshot.add_transformer(
            GenericTransformer(
                lambda obj, *args: json.loads(
                    json.dumps(obj).replace(f"'{domain_name}'", "'namespace'")
                )
            )
        )

        response = aws_client.servicediscovery.create_private_dns_namespace(
            Name=domain_name, Vpc=default_vpc["VpcId"]
        )
        snapshot.match("private_dns", response)

        def _cleanup():
            if namespace:
                aws_client.servicediscovery.delete_namespace(Id=namespace["Id"])

        namespace = None
        cleanups.append(_cleanup)

        def _get_namespace():
            result = aws_client.servicediscovery.list_namespaces(MaxResults=100)
            matching = [ns for ns in result["Namespaces"] if ns["Name"] == domain_name]
            assert matching
            return matching[0]

        # wait until namespace has been created
        namespace = retry(_get_namespace, retries=60, sleep=1)
        snapshot.match("namespace", namespace)

        response = aws_client.route53.list_hosted_zones_by_name(DNSName=domain_name)
        assert response["HostedZones"], "the hosted zone has not been created"

    @markers.aws.unknown
    def test_create_untagged_resource(self, aws_client):
        namespace_name = f"namespace-{short_uid()}"
        tag1 = {"Key": "Tag1Key", "Value": "Tag1Value"}

        # create namespace
        create_namespace_result = aws_client.servicediscovery.create_http_namespace(
            Name=namespace_name
        )

        assert wait_until(operation_succeeded(create_namespace_result["OperationId"], aws_client))
        operation = aws_client.servicediscovery.get_operation(
            OperationId=create_namespace_result["OperationId"]
        )
        namespace_id = operation["Operation"]["Targets"]["NAMESPACE"]

        get_namespace_result = aws_client.servicediscovery.get_namespace(Id=namespace_id)
        namespace_arn = get_namespace_result["Namespace"]["Arn"]

        # namespace tag support
        namespace_tags_before = aws_client.servicediscovery.list_tags_for_resource(
            ResourceARN=namespace_arn
        )["Tags"]
        assert len(namespace_tags_before) == 0
        aws_client.servicediscovery.tag_resource(
            ResourceARN=get_namespace_result["Namespace"]["Arn"], Tags=[tag1]
        )
        namespace_tags_after = aws_client.servicediscovery.list_tags_for_resource(
            ResourceARN=namespace_arn
        )["Tags"]
        assert tag1 in namespace_tags_after

    # the test test_create_untagged_resource had a side effect, which is only present in CI,
    # on the test test_create_instances (making it red). When setting test_create_untagged_resource
    # to the end of the suite, the tests are green.
    # TODO: fix this side effect

    @markers.aws.validated
    @pytest.mark.parametrize("ns_name", ["test-domain-<rnd>", "test-<rnd>.com", "invalid name"])
    @pytest.mark.parametrize("ns_visibility", ["private", "public"])
    def test_dns_namespace_with_and_without_dot(
        self, default_vpc, ns_name, ns_visibility, snapshot, cleanups, aws_client
    ):
        """Test creation of DNS namespaces with or without dots in the DNS name"""

        snapshot.add_transformer(
            GenericTransformer(
                lambda obj, *args: json.loads(
                    json.dumps(obj).replace(f"'{ns_name}'", "'namespace'")
                )
            )
        )

        def _cleanup():
            if namespace:
                aws_client.servicediscovery.delete_namespace(Id=namespace["Id"])

        namespace = None
        cleanups.append(_cleanup)

        ns_name = ns_name.replace("<rnd>", short_uid())

        if ns_visibility == "private":
            kwargs = {"Vpc": default_vpc["VpcId"]}
            create_func = aws_client.servicediscovery.create_private_dns_namespace
        else:
            kwargs = {}
            create_func = aws_client.servicediscovery.create_public_dns_namespace

        context = None
        if "invalid" in ns_name or (ns_visibility == "public" and "." not in ns_name):
            # expect an exception if a public DNS namespace does not contain a dot
            context = pytest.raises(Exception)

        with context or empty_context_manager() as ctx:
            create_func(Name=ns_name, Description="test 123", **kwargs)
        if context:
            snapshot.match("error", ctx.value.response)
            return

        def _get_namespace():
            result = aws_client.servicediscovery.list_namespaces(MaxResults=100)
            matching = [ns for ns in result["Namespaces"] if ns["Name"] == ns_name]
            assert matching
            return matching[0]

        # wait until namespace has been created
        namespace = retry(_get_namespace, retries=60, sleep=1)
        snapshot.match("namespace", namespace)
