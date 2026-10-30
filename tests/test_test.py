import json

import pytest

from drf_query_method.test import APIClient, APIRequestFactory


def test_factory_encodes_json():
    request = APIRequestFactory().query("/", {"a": 1}, format="json")
    assert request.method == "QUERY"
    assert request.content_type == "application/json"
    assert json.loads(request.body) == {"a": 1}


def test_factory_accepts_content_type():
    request = APIRequestFactory().query("/", "a=1", content_type="application/x-www-form-urlencoded")
    assert request.body == b"a=1"


def test_client_sends_query():
    response = APIClient().query("/query/", {"a": 1}, format="json")
    assert response.data == {"method": "QUERY", "data": {"a": 1}}


@pytest.mark.parametrize("follow", [False, True])
def test_client_follows_redirects(follow):
    response = APIClient().query("/redirect/", {"a": 1}, format="json", follow=follow)
    if follow:
        assert response.data == {"method": "QUERY", "data": {"a": 1}}
    else:
        assert response.status_code == 307
