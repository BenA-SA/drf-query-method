"""DRF's ``SearchFilter`` and ``OrderingFilter``, reading QUERY request bodies.

``get_ordering`` is adapted from Django REST framework
(Copyright Encode OSS Ltd, BSD 3-Clause; see LICENSE).
"""

from rest_framework import filters
from rest_framework.fields import CharField

from drf_query_method.params import filter_params


def get_search_terms(self, request):
    """Search terms come from ``?search=...``, or a QUERY request's body, and may be whitespace delimited."""
    value = filter_params(request).get(self.search_param, "")
    field = CharField(trim_whitespace=False, allow_blank=True)
    cleaned_value = field.run_validation(value)
    return filters.search_smart_split(cleaned_value)


def get_ordering(self, request, queryset, view):
    """Ordering comes from a comma delimited ``?ordering=...``, or a QUERY request's body."""
    params = filter_params(request).get(self.ordering_param)
    if params and isinstance(params, str):
        fields = [param.strip() for param in params.split(",")]
        ordering = self.remove_invalid_fields(queryset, fields, view, request)
        if ordering:
            return ordering

    return self.get_default_ordering(view)


class SearchFilter(filters.SearchFilter):
    get_search_terms = get_search_terms


class OrderingFilter(filters.OrderingFilter):
    get_ordering = get_ordering
