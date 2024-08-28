import pytest
from localstack.pro.core.persistence.pickling import reducers


@pytest.fixture(scope="session", autouse=True)
def register_reducers():
    reducers.register()
