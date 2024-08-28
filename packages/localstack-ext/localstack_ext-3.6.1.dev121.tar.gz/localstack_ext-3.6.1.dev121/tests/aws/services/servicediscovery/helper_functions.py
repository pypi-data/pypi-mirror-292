import logging

from localstack.aws.connect import ServiceLevelClientFactory
from localstack.utils.sync import ShortCircuitWaitException, retry, wait_until

LOG = logging.getLogger(__name__)


def operation_succeeded(operation_id: str, aws_client: ServiceLevelClientFactory):
    def _operation_succeeded():
        status = aws_client.servicediscovery.get_operation(OperationId=operation_id)["Operation"][
            "Status"
        ]
        if status == "SUCCESS":
            return True
        elif status == "FAIL":
            raise ShortCircuitWaitException()
        else:
            return False

    return _operation_succeeded


def cleanup_namespace(namespace_id: str, aws_client: ServiceLevelClientFactory):
    delete_namespace_result = aws_client.servicediscovery.delete_namespace(Id=namespace_id)
    assert wait_until(operation_succeeded(delete_namespace_result["OperationId"], aws_client))
    LOG.debug("Delete namespace: %s succeeded", namespace_id)


def delete_service(service_id: str, aws_client: ServiceLevelClientFactory):
    aws_client.servicediscovery.delete_service(Id=service_id)

    def _delete_service_succeeded():
        try:
            aws_client.servicediscovery.get_service(Id=service_id)
        except aws_client.servicediscovery.exceptions.ServiceNotFoundException:
            pass

    retry(_delete_service_succeeded, retries=3, sleep=2)
    LOG.debug("Delete service: %s succeeded", service_id)


def deregister_instance(instance_id: str, service_id: str, aws_client: ServiceLevelClientFactory):
    deregister_instance_result = aws_client.servicediscovery.deregister_instance(
        ServiceId=service_id, InstanceId=instance_id
    )
    assert wait_until(operation_succeeded(deregister_instance_result["OperationId"], aws_client))
    LOG.debug("Deregister instance: %s succeeded", instance_id)
