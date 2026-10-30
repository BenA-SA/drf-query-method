from django.views.generic import View
from rest_framework.test import APIRequestFactory

from drf_query_method import add_query_method
from tests.views import QueryEchoView


def test_django_views_accept_query():
    assert "query" in View.http_method_names


def test_add_query_method_is_idempotent():
    add_query_method()
    assert View.http_method_names.count("query") == 1


def test_api_view_dispatches_query():
    request = APIRequestFactory().generic("QUERY", "/", '{"a": 1}', "application/json")
    response = QueryEchoView.as_view()(request)
    assert response.status_code == 200
    assert response.data == {"method": "QUERY", "data": {"a": 1}}
