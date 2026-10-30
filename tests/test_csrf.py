import pytest
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.middleware.csrf import CsrfViewMiddleware
from django.test import RequestFactory

from drf_query_method import add_query_method
from drf_query_method.test import APIClient


@pytest.fixture
def client(db):
    client = APIClient(enforce_csrf_checks=True)
    client.force_login(User.objects.create(username="alice"))
    return client


def test_session_authenticated_query_needs_no_csrf_token(client):
    response = client.query("/session/", {"search": "a"}, format="json")
    assert response.status_code == 200
    assert response.data == {"method": "QUERY"}


def test_session_authenticated_post_still_needs_a_csrf_token(client):
    assert client.post("/session/", {}, format="json").status_code == 403


def test_csrf_middleware_accepts_query_as_a_safe_method():
    middleware = CsrfViewMiddleware(lambda request: HttpResponse())
    request = RequestFactory().generic("QUERY", "/")
    assert middleware.process_view(request, lambda request: HttpResponse(), (), {}) is None
    assert request.csrf_processing_done


def test_add_query_method_wraps_the_middleware_once():
    add_query_method()
    add_query_method()
    process_view = CsrfViewMiddleware.process_view
    assert not hasattr(getattr(process_view, "__wrapped__", None), "__wrapped__")
