from urllib.parse import urlencode

import django_filters
import pytest
from django.contrib.auth.models import User
from rest_framework import generics
from rest_framework.renderers import JSONRenderer
from rest_framework.test import APIRequestFactory
from rest_framework_datatables import filters, pagination, renderers
from rest_framework_datatables.django_filters.backends import DatatablesFilterBackend
from rest_framework_datatables.django_filters.filters import GlobalFilter
from rest_framework_datatables.django_filters.filterset import DatatablesFilterSet

from tests.views import UserSerializer

DATATABLES_PARAMS = {
    "draw": "3",
    "start": "1",
    "length": "1",
    "columns[0][data]": "username",
    "columns[0][name]": "username",
    "columns[0][searchable]": "true",
    "columns[0][orderable]": "true",
    "columns[0][search][value]": "",
    "columns[0][search][regex]": "false",
    "order[0][column]": "0",
    "order[0][dir]": "desc",
    "search[value]": "o",
    "search[regex]": "false",
}


class GlobalCharFilter(GlobalFilter, django_filters.CharFilter):
    pass


class UserGlobalFilterSet(DatatablesFilterSet):
    username = GlobalCharFilter(lookup_expr="icontains")

    class Meta:
        model = User
        fields = ["username"]


def build_view(filter_backend):
    class View(generics.ListAPIView):
        queryset = User.objects.order_by("pk")
        serializer_class = UserSerializer
        permission_classes = []
        filterset_class = UserGlobalFilterSet
        renderer_classes = [JSONRenderer, renderers.DatatablesRenderer]
        filter_backends = [filter_backend]
        pagination_class = pagination.DatatablesPageNumberPagination

        def query(self, request, *args, **kwargs):
            return self.list(request, *args, **kwargs)

    return View.as_view()


@pytest.fixture
def users(db):
    for username in ["alice", "bob", "carol"]:
        User.objects.create(username=username)


@pytest.mark.parametrize("filter_backend", [filters.DatatablesFilterBackend, DatatablesFilterBackend])
def test_datatables_reads_query_body(patched, users, filter_backend):
    request = APIRequestFactory().query(
        "/?format=datatables", urlencode(DATATABLES_PARAMS), content_type="application/x-www-form-urlencoded"
    )
    response = build_view(filter_backend)(request)
    response.render()
    assert response.data["draw"] == 3
    assert response.data["recordsTotal"] == 3
    assert response.data["recordsFiltered"] == 2
    assert [user["username"] for user in response.data["data"]] == ["bob"]


def test_datatables_get_is_unchanged(patched, users):
    request = APIRequestFactory().get("/", {**DATATABLES_PARAMS, "format": "datatables"})
    response = build_view(filters.DatatablesFilterBackend)(request)
    assert [user["username"] for user in response.data["data"]] == ["bob"]


def test_merged_filter_params_are_cached_per_request():
    from rest_framework.parsers import JSONParser
    from rest_framework.request import Request

    from drf_query_method.params import merge_filter_params
    from drf_query_method.test import APIRequestFactory as QueryRequestFactory

    request = Request(QueryRequestFactory().query("/", {"a": "1"}, format="json"), parsers=[JSONParser()])
    assert merge_filter_params(request) is merge_filter_params(request)
