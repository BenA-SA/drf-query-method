import pytest
from django.contrib.auth.models import User

from drf_query_method.test import APIRequestFactory
from tests.views import UserSearchView

factory = APIRequestFactory()
view = UserSearchView.as_view()


@pytest.fixture
def users(db):
    for username in ["alice", "bob", "carol"]:
        User.objects.create(username=username)


def usernames(response):
    return [user["username"] for user in response.data]


def test_search_reads_query_body(users):
    response = view(factory.query("/", {"search": "o"}, format="json"))
    assert usernames(response) == ["carol", "bob"]


def test_ordering_reads_query_body(users):
    response = view(factory.query("/", {"ordering": "username"}, format="json"))
    assert usernames(response) == ["alice", "bob", "carol"]


def test_non_string_ordering_falls_back_to_default(users):
    response = view(factory.query("/", {"ordering": {"username": "asc"}}, format="json"))
    assert usernames(response) == ["carol", "bob", "alice"]


def test_non_string_search_is_a_bad_request(users):
    response = view(factory.query("/", {"search": {"a": 1}}, format="json"))
    assert response.status_code == 400


def test_get_is_unchanged(users):
    response = view(factory.get("/", {"search": "o", "ordering": "username"}))
    assert usernames(response) == ["bob", "carol"]
