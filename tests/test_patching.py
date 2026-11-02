import django_filters.rest_framework
import pytest
from django.contrib.auth.models import User
from rest_framework import filters, generics, mixins, permissions, routers, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.schemas.generators import EndpointEnumerator
from rest_framework.test import APIClient, APIRequestFactory

from drf_query_method import patch, unpatch
from tests.views import UserSerializer


@pytest.fixture
def users(db):
    for username in ["alice", "bob", "carol"]:
        User.objects.create(username=username)


def build_viewset(with_query_handler=True):
    class DRFUserViewSet(viewsets.ModelViewSet):
        queryset = User.objects.order_by("pk")
        serializer_class = UserSerializer
        permission_classes = [permissions.IsAuthenticatedOrReadOnly]
        filter_backends = [filters.SearchFilter, django_filters.rest_framework.DjangoFilterBackend]
        search_fields = ["username"]
        filterset_fields = ["username"]

    class OwnHandlerViewSet(DRFUserViewSet):
        def query(self, request, *args, **kwargs):
            return self.list(request, *args, **kwargs)

    return OwnHandlerViewSet if with_query_handler else DRFUserViewSet


def test_patch_adds_drf_api(patched):
    assert "QUERY" in permissions.SAFE_METHODS
    assert permissions.DjangoModelPermissions.perms_map["QUERY"] == []
    assert permissions.DjangoObjectPermissions.perms_map["QUERY"] == []
    assert hasattr(Request, "filter_params")
    assert hasattr(APIRequestFactory, "query")
    assert hasattr(APIClient, "query")


def test_patch_is_idempotent(patched):
    patch()
    list_route = routers.SimpleRouter.routes[0]
    assert list_route.mapping["query"] == "query"


@pytest.mark.skipif(hasattr(Request, "filter_params"), reason="DRF supports QUERY natively, so patch() leaves it alone")
def test_unpatch_restores_drf():
    patch()
    unpatch()
    assert "query" not in mixins.ListModelMixin.__dict__
    assert "QUERY" not in permissions.SAFE_METHODS
    assert "QUERY" not in permissions.DjangoModelPermissions.perms_map
    assert not hasattr(Request, "filter_params")
    assert "query" not in routers.SimpleRouter.routes[0].mapping


@pytest.mark.parametrize("with_query_handler", [True, False], ids=["own-handler", "list-mixin-handler"])
def test_drf_router_and_filters_use_query_body(patched, users, with_query_handler):
    router = routers.SimpleRouter()
    router.register("users", build_viewset(with_query_handler), basename="users")
    list_view = router.urls[0].callback
    detail_view = router.urls[1].callback
    factory = APIRequestFactory()

    response = list_view(factory.query("/users/", {"search": "o"}, format="json"))
    assert [user["username"] for user in response.data] == ["bob", "carol"]

    response = list_view(factory.query("/users/", {"username": "alice"}, format="json"))
    assert [user["username"] for user in response.data] == ["alice"]

    response = detail_view(factory.query("/users/1/", {}, format="json"), pk=1)
    assert response.status_code == 405


def test_query_action_keeps_its_route(patched):
    class ActionViewSet(viewsets.GenericViewSet):
        queryset = User.objects.all()

        @action(detail=False, methods=["post"])
        def query(self, request):
            return Response("action")

    router = routers.SimpleRouter()
    router.register("x", ActionViewSet, basename="x")
    assert [url.name for url in router.urls] == ["x-query"]


def test_method_mapper_supports_query(patched):
    class MappedViewSet(viewsets.GenericViewSet):
        @action(detail=False)
        def search(self, request):
            return Response("get")

        @search.mapping.query
        def search_query(self, request):
            return Response("query")

    assert MappedViewSet.search.mapping["query"] == "search_query"


def test_schema_generator_skips_query(patched):
    class View(generics.ListAPIView):
        queryset = User.objects.all()
        serializer_class = UserSerializer

        def query(self, request, *args, **kwargs):
            return self.list(request, *args, **kwargs)

    assert EndpointEnumerator().get_allowed_methods(View.as_view()) == ["GET"]


def test_list_views_answer_query_without_a_handler(patched, users):
    class View(generics.ListAPIView):
        queryset = User.objects.order_by("pk")
        serializer_class = UserSerializer
        filter_backends = [filters.SearchFilter]
        search_fields = ["username"]

    response = View.as_view()(APIRequestFactory().query("/", {"search": "o"}, format="json"))
    assert [user["username"] for user in response.data] == ["bob", "carol"]


def test_views_without_list_do_not_answer_query(patched, users):
    class View(generics.RetrieveAPIView):
        queryset = User.objects.all()
        serializer_class = UserSerializer

    response = View.as_view()(APIRequestFactory().query("/", {}, format="json"), pk=1)
    assert response.status_code == 405
    assert "QUERY" not in response["Allow"]


def test_view_defined_query_wins(patched, users):
    class View(generics.ListAPIView):
        queryset = User.objects.all()
        serializer_class = UserSerializer

        def query(self, request):
            return Response("own")

    assert View.as_view()(APIRequestFactory().query("/", {}, format="json")).data == "own"


def test_list_view_can_opt_out_of_query(patched, users):
    class View(generics.ListAPIView):
        queryset = User.objects.all()
        serializer_class = UserSerializer
        http_method_names = [method for method in generics.ListAPIView.http_method_names if method != "query"]

    response = View.as_view()(APIRequestFactory().query("/", {}, format="json"))
    assert response.status_code == 405


def test_query_action_on_list_viewset_keeps_its_route(patched, users):
    class ActionViewSet(viewsets.ModelViewSet):
        queryset = User.objects.order_by("pk")
        serializer_class = UserSerializer

        @action(detail=False, methods=["post"])
        def query(self, request):
            return Response("action")

    router = routers.SimpleRouter()
    router.register("x", ActionViewSet, basename="x")
    list_view = next(url.callback for url in router.urls if url.name == "x-list")
    assert "query" not in list_view.actions
    assert list_view(APIRequestFactory().query("/x/", {}, format="json")).status_code == 405


def test_drf_spectacular_schema_skips_query(patched):
    from drf_spectacular.generators import SchemaGenerator
    from drf_spectacular.openapi import AutoSchema

    class SchemaViewSet(viewsets.ModelViewSet):
        queryset = User.objects.all()
        serializer_class = UserSerializer
        schema = AutoSchema()

    router = routers.SimpleRouter()
    router.register("users", SchemaViewSet, basename="users")
    schema = SchemaGenerator(patterns=router.urls).get_schema(request=None, public=True)
    assert set(schema["paths"]["/users/"]) == {"get", "post"}
