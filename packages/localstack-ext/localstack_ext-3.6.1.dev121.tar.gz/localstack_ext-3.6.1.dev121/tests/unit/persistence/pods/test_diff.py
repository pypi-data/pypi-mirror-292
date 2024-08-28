from localstack.pro.core.persistence.pods.diff.algo import (
    StoreContext,
    _get_operation_list_from_attributes,
)
from localstack.pro.core.persistence.pods.diff.models import BackendType, Operation, OperationType


class DummySqsQueue:
    pass


def test_get_operations_from_attributes():
    target_attributes = {
        "queues": {
            "queue_one": DummySqsQueue(),
            "queue_two": DummySqsQueue(),
        }
    }
    source_attributes = {"queues": {"queue_two": DummySqsQueue(), "queue_three": DummySqsQueue()}}
    context = StoreContext(
        account_id="0123456789", region="us-east-1", service="sqs", backend_type=BackendType.STORE
    )
    operations = _get_operation_list_from_attributes(
        target_attributes=target_attributes,
        source_attributes=source_attributes,
        store_context=context,
    )
    assert len(operations) == 2
    assert operations[0] == Operation(
        operation_type=OperationType.MODIFICATION,
        account_id="0123456789",
        backend=BackendType.STORE,
        region="us-east-1",
        resources=[{"attribute": "queues", "attribute_key": "queue_two"}],
        service="sqs",
    )

    assert operations[1] == Operation(
        operation_type=OperationType.ADDITION,
        account_id="0123456789",
        backend=BackendType.STORE,
        region="us-east-1",
        resources=[{"attribute": "queues", "attribute_key": "queue_three"}],
        service="sqs",
    )
