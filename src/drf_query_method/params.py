"""The parameters filter backends should read for a request."""

from collections.abc import Mapping

from django.http import QueryDict
from django.utils.datastructures import MultiValueDict
from rest_framework.exceptions import ParseError

_CACHE_ATTRIBUTE = "_drf_query_method_filter_params"


def merge_filter_params(request) -> QueryDict:
    """Return ``request.query_params`` with a QUERY request's body merged over it.

    For any method other than ``QUERY`` this is ``request.query_params``
    itself. A ``QUERY`` request carries its query in the request body, so the
    parsed body is merged over the URL query parameters, and the body wins
    for any key present in both. List values in a JSON body become multiple
    values, as repeated query-string parameters do.

    Raises ``ParseError`` (400) when the body is not an object of parameters,
    such as a JSON array. The result is cached on the request, as packages
    such as django-rest-framework-datatables read many parameters each.
    """
    if request.method != "QUERY":
        return request.query_params

    cached = request.__dict__.get(_CACHE_ATTRIBUTE)
    if cached is not None:
        return cached

    body = request.data
    if not isinstance(body, Mapping):
        raise ParseError(f"QUERY request body must be an object of parameters, not {type(body).__name__}.")

    if not isinstance(body, MultiValueDict):
        body = MultiValueDict({key: value if isinstance(value, list) else [value] for key, value in body.items()})

    params = request.query_params.copy()
    for key, values in body.lists():
        params.setlist(key, values)
    request.__dict__[_CACHE_ATTRIBUTE] = params
    return params


def filter_params(request) -> QueryDict:
    """The parameters filter backends should read for ``request``.

    Uses ``request.filter_params`` when DRF provides it, natively or through
    :func:`drf_query_method.patch`, and computes it otherwise. Custom filter
    backends should read their parameters through this rather than
    ``request.query_params``, so that they support ``QUERY`` requests.
    """
    if hasattr(type(request), "filter_params"):
        return request.filter_params
    return merge_filter_params(request)
