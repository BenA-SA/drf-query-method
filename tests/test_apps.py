import pytest
from django.apps import apps
from django.conf import settings
from django.test import override_settings
from rest_framework import permissions, routers
from rest_framework.request import Request

from drf_query_method import patch, unpatch
from drf_query_method.apps import DrfQueryMethodConfig
from drf_query_method.patching import _applied

native_query = pytest.mark.skipif(
    hasattr(Request, "filter_params"), reason="DRF supports QUERY natively, so patch() leaves it alone"
)


@pytest.fixture
def installed():
    with override_settings(INSTALLED_APPS=[*settings.INSTALLED_APPS, "drf_query_method"]):
        yield
    unpatch()


@native_query
def test_installing_the_app_patches_drf(installed):
    assert isinstance(apps.get_app_config("drf_query_method"), DrfQueryMethodConfig)
    assert "QUERY" in permissions.SAFE_METHODS
    assert routers.SimpleRouter.routes[0].mapping["query"] == "query"


def test_explicit_patch_alongside_the_app_is_harmless(installed):
    applied = list(_applied)
    patch()
    assert _applied == applied


@native_query
def test_drf_is_left_alone_without_the_app():
    assert not _applied
    assert "QUERY" not in permissions.SAFE_METHODS
