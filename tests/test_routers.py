import pytest
from django.urls import include, path

from drf_query_method.routers import DefaultRouter, SimpleRouter
from drf_query_method.test import APIClient
from tests.views import PlainUserViewSet, QueryActionViewSet, UserViewSet

router = SimpleRouter()
router.register("users", UserViewSet)
router.register("plain", PlainUserViewSet, basename="plain")
router.register("actions", QueryActionViewSet, basename="actions")

default_router = DefaultRouter()
default_router.register("users", UserViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("default/", include(default_router.urls)),
]

pytestmark = pytest.mark.urls("tests.test_routers")


@pytest.fixture
def client(db):
    from django.contrib.auth.models import User

    User.objects.create(username="alice")
    return APIClient()


def test_list_route_maps_query():
    list_route = next(route for route in router.routes if getattr(route, "mapping", {}).get("get") == "list")
    assert list_route.mapping["query"] == "query"


def test_query_reaches_the_viewset(client):
    response = client.query("/users/", {}, format="json")
    assert response.status_code == 200
    assert response.data[0]["username"] == "alice"


def test_default_router_routes_query(client):
    assert client.query("/default/users/", {}, format="json").status_code == 200


def test_viewset_without_query_handler_is_not_allowed(client):
    assert client.query("/plain/", {}, format="json").status_code == 405


def test_detail_route_does_not_answer_query(client):
    response = client.query("/users/1/", {}, format="json")
    assert response.status_code == 405
    assert "QUERY" not in response["Allow"]


def test_query_action_keeps_its_route(client):
    assert client.post("/actions/query/").data == "action"


def test_query_action_is_not_bound_to_query_method(client):
    response = client.query("/actions/", {}, format="json")
    assert response.status_code == 405
