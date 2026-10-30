"""django-filter's DRF backend, reading QUERY request bodies.

Importing this module requires django-filter.
"""

from django.http import QueryDict
from django_filters import rest_framework

from drf_query_method.params import filter_params


def as_filter_data(params):
    """Stringify a QUERY body's scalar values, as a query string would deliver them.

    django-filter's widgets expect strings. JSON numbers and booleans become
    ``"5"`` and ``"True"``, which its fields parse as usual, rather than
    reaching widgets that call ``.split(",")`` on them.
    """
    data = QueryDict(mutable=True)
    for key, values in params.lists():
        data.setlist(key, [value if value is None or isinstance(value, str) else str(value) for value in values])
    return data


def get_filterset_kwargs(self, request, queryset, view, original):
    kwargs = original(self, request, queryset, view)
    if request.method == "QUERY":
        kwargs["data"] = as_filter_data(filter_params(request))
    return kwargs


class DjangoFilterBackend(rest_framework.DjangoFilterBackend):
    def get_filterset_kwargs(self, request, queryset, view):
        return get_filterset_kwargs(
            self, request, queryset, view, rest_framework.DjangoFilterBackend.get_filterset_kwargs
        )
