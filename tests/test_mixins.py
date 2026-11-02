"""QueryMixin on the opt-in path, without patch()."""

import pytest
from django.contrib.auth.models import User
from django.urls import include, path
from rest_framework import mixins, viewsets
from rest_framework.response import Response

from drf_query_method import QueryMixin, filters
from drf_query_method import viewsets as query_viewsets
from drf_query_method.routers import SimpleRouter
from drf_query_method.test import APIClient
from tests.views import UserSerializer


class UserViewSet(QueryMixin, query_viewsets.ModelViewSet):
    queryset = User.objects.order_by("pk")
    serializer_class = UserSerializer
    permission_classes = []
    filter_backends = [filters.SearchFilter]
    search_fields = ["username"]


class HandWrittenListViewSet(QueryMixin, query_viewsets.ViewSet):
    permission_classes = []

    def list(self, request):
        return Response("list")


class OwnQueryViewSet(QueryMixin, query_viewsets.ModelViewSet):
    queryset = User.objects.order_by("pk")
    serializer_class = UserSerializer
    permission_classes = []

    def query(self, request, *args, **kwargs):
        return Response("own")


router = SimpleRouter()
router.register("users", UserViewSet, basename="users")
router.register("hand", HandWrittenListViewSet, basename="hand")
router.register("own", OwnQueryViewSet, basename="own")

urlpatterns = [path("", include(router.urls))]

pytestmark = pytest.mark.urls("tests.test_mixins")


@pytest.fixture
def client(db):
    for username in ["alice", "bob", "carol"]:
        User.objects.create(username=username)
    return APIClient()


def test_query_delegates_to_list_with_body_filters(client):
    response = client.query("/users/", {"search": "o"}, format="json")
    assert response.status_code == 200
    assert [user["username"] for user in response.data] == ["bob", "carol"]


def test_detail_route_does_not_answer_query(client):
    response = client.query("/users/1/", {}, format="json")
    assert response.status_code == 405
    assert "QUERY" not in response["Allow"]


def test_works_with_a_hand_written_list(client):
    assert client.query("/hand/", {}, format="json").data == "list"


def test_view_defined_query_wins(client):
    assert client.query("/own/", {}, format="json").data == "own"


def test_drf_classes_are_not_patched():
    assert "query" not in mixins.ListModelMixin.__dict__
    assert not hasattr(viewsets.ModelViewSet, "query")


def test_query_runs_as_the_list_action():
    list_view = next(url.callback for url in router.urls if url.name == "users-list")
    own_view = next(url.callback for url in router.urls if url.name == "own-list")
    assert list_view.actions["query"] == "list"
    assert own_view.actions["query"] == "query"
