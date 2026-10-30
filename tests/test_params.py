import pytest
from rest_framework.exceptions import ParseError
from rest_framework.parsers import FormParser, JSONParser
from rest_framework.request import Request

from drf_query_method import filter_params
from drf_query_method.test import APIRequestFactory

factory = APIRequestFactory()


def make_request(django_request):
    return Request(django_request, parsers=[JSONParser(), FormParser()])


def test_get_uses_query_params():
    request = make_request(factory.get("/", {"search": "a"}))
    assert filter_params(request) is request.query_params


def test_query_body_is_merged_over_url():
    request = make_request(factory.query("/?search=url&page=2", {"search": "body", "tags": ["a", "b"]}, format="json"))
    params = filter_params(request)
    assert params["search"] == "body"
    assert params["page"] == "2"
    assert params.getlist("tags") == ["a", "b"]


def test_query_form_body():
    request = make_request(factory.query("/", "search=form", content_type="application/x-www-form-urlencoded"))
    assert filter_params(request)["search"] == "form"


def test_query_body_must_be_an_object():
    request = make_request(factory.query("/", ["a"], format="json"))
    with pytest.raises(ParseError):
        filter_params(request)
