"""DRF's test request factory and client, with a ``.query()`` method."""

from rest_framework import test


def factory_query(self, path, data=None, format=None, content_type=None, **extra):
    """Build a QUERY request, encoding ``data`` as ``.post()`` does."""
    data, content_type = self._encode_data(data, format, content_type)
    return self.generic("QUERY", path, data, content_type, **extra)


def client_query(self, path, data=None, format=None, content_type=None, follow=False, **extra):
    """Send a QUERY request, encoding ``data`` as ``.post()`` does."""
    response = factory_query(self, path, data=data, format=format, content_type=content_type, **extra)
    if follow:
        response = self._handle_redirects(response, data=data, format=format, content_type=content_type, **extra)
    return response


class APIRequestFactory(test.APIRequestFactory):
    query = factory_query


class APIClient(test.APIClient):
    query = client_query


class APISimpleTestCase(test.APISimpleTestCase):
    client_class = APIClient


class APITransactionTestCase(test.APITransactionTestCase):
    client_class = APIClient


class APITestCase(test.APITestCase):
    client_class = APIClient


class APILiveServerTestCase(test.APILiveServerTestCase):
    client_class = APIClient
