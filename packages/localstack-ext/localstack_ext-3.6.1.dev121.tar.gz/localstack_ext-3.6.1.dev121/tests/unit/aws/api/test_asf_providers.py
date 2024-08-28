import pytest
from localstack.testing.aws.asf_utils import (
    check_provider_signature,
    collect_implemented_provider_operations,
)


@pytest.mark.parametrize(
    "sub_class,base_class,method_name",
    collect_implemented_provider_operations(
        provider_module="localstack.pro.core.services", asf_api_module="localstack.pro.core.aws.api"
    ),
)
def test_provider_signatures(sub_class: type, base_class: type, method_name: str):
    check_provider_signature(sub_class, base_class, method_name)
