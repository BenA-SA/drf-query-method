import django_filters
import pytest
from django.contrib.auth.models import User
from rest_framework import generics

from drf_query_method.django_filters import DjangoFilterBackend
from drf_query_method.test import APIRequestFactory
from tests.views import UserSerializer

factory = APIRequestFactory()


class NumberInFilter(django_filters.BaseInFilter, django_filters.NumberFilter):
    pass


class UserFilter(django_filters.FilterSet):
    username = django_filters.CharFilter(lookup_expr="icontains")
    id__in = NumberInFilter(field_name="id")
    is_staff = django_filters.BooleanFilter()

    class Meta:
        model = User
        fields = []


class UserFilterView(generics.ListAPIView):
    queryset = User.objects.order_by("username")
    serializer_class = UserSerializer
    permission_classes = []
    filter_backends = [DjangoFilterBackend]
    filterset_class = UserFilter

    def query(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


view = UserFilterView.as_view()


@pytest.fixture
def users(db):
    return [
        User.objects.create(username="alice", is_staff=True),
        User.objects.create(username="bob"),
        User.objects.create(username="carol"),
    ]


def usernames(response):
    return [user["username"] for user in response.data]


def test_reads_query_body(users):
    assert usernames(view(factory.query("/", {"username": "o"}, format="json"))) == ["bob", "carol"]


def test_reads_json_booleans(users):
    assert usernames(view(factory.query("/", {"is_staff": True}, format="json"))) == ["alice"]


def test_csv_filter_accepts_a_json_number(users):
    response = view(factory.query("/", {"id__in": users[1].pk}, format="json"))
    assert usernames(response) == ["bob"]


def test_csv_filter_accepts_a_string(users):
    response = view(factory.query("/", {"id__in": f"{users[0].pk},{users[1].pk}"}, format="json"))
    assert usernames(response) == ["alice", "bob"]


def test_invalid_value_is_a_bad_request(users):
    assert view(factory.query("/", {"id__in": "x"}, format="json")).status_code == 400


def test_get_is_unchanged(users):
    assert usernames(view(factory.get("/", {"username": "o"}))) == ["bob", "carol"]
