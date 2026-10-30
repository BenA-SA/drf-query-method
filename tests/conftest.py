import pytest

from drf_query_method import add_query_method, patch, unpatch


def pytest_configure(config):
    add_query_method()


@pytest.fixture
def patched():
    patch()
    yield
    unpatch()
