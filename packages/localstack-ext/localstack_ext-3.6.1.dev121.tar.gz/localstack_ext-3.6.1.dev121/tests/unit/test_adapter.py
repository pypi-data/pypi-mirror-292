from localstack.pro.core.persistence.pods.service_state.service_state import ServiceState
from localstack.pro.core.persistence.pods.service_state.service_state_types import (
    BackendState,
    ServiceKey,
)
from localstack.pro.core.persistence.utils.adapters import ServiceStateMarshaller
from localstack.state import pickle


class TestAdapter:
    def test_from_state_to_zip(self):
        service_state = ServiceState()
        service_key = ServiceKey("0000", "us-east-1", "cognito-idp")
        dummy_content = {"UserPool": {"id": "hello"}}
        dummy_backend = BackendState(service_key, {"region_state": pickle.dumps(dummy_content)})
        service_state.put_backend(dummy_backend)

        zip_content = ServiceStateMarshaller.marshall(state=service_state)
        assert zip_content

        deserialized_service: ServiceState = ServiceStateMarshaller.unmarshall(
            zip_content=zip_content, unmarshall_function=pickle.loads
        )
        assert list(deserialized_service.state.keys())[0] == service_key
        retrieved_backend = list(deserialized_service.state.values())[0].backends["region_state"]
        assert retrieved_backend == dummy_content
