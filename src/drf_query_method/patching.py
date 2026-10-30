"""Apply QUERY support to DRF itself, and to django-filter when installed.

:func:`patch` makes DRF behave as if encode/django-rest-framework#10091 were
merged, so existing views, routers and settings pick up ``QUERY`` without
changing imports. Call it once at startup, for example from an
``AppConfig.ready()``. It does nothing to DRF once DRF supports ``QUERY``
itself.
"""

import importlib.util

from drf_query_method.methods import add_query_method

_MISSING = object()
_applied: list[tuple[object, str, object]] = []


def _set(owner, name: str, value) -> None:
    _applied.append((owner, name, owner.__dict__.get(name, _MISSING)))
    setattr(owner, name, value)


def _patch_drf() -> None:
    from rest_framework import decorators, filters, permissions, routers, test, viewsets
    from rest_framework.request import Request
    from rest_framework.schemas.generators import EndpointEnumerator

    from drf_query_method import filters as query_filters
    from drf_query_method import permissions as query_permissions
    from drf_query_method import test as query_test
    from drf_query_method.params import merge_filter_params
    from drf_query_method.routers import get_routes_keeping_query_actions, with_query_route
    from drf_query_method.viewsets import drop_unmapped_query

    _set(Request, "filter_params", property(merge_filter_params))
    _set(filters.SearchFilter, "get_search_terms", query_filters.get_search_terms)
    _set(filters.OrderingFilter, "get_ordering", query_filters.get_ordering)

    _set(permissions, "SAFE_METHODS", query_permissions.SAFE_METHODS)
    for permission_class in (permissions.DjangoModelPermissions, permissions.DjangoObjectPermissions):
        _set(permission_class, "perms_map", {**permission_class.perms_map, "QUERY": []})

    _set(routers.SimpleRouter, "routes", with_query_route(routers.SimpleRouter.routes))
    simple_get_routes = routers.SimpleRouter.get_routes
    _set(
        routers.SimpleRouter,
        "get_routes",
        lambda router, viewset: get_routes_keeping_query_actions(router, viewset, simple_get_routes),
    )

    def dispatch(self, request, *args, **kwargs):
        drop_unmapped_query(self)
        return super(viewsets.ViewSetMixin, self).dispatch(request, *args, **kwargs)

    _set(viewsets.ViewSetMixin, "dispatch", dispatch)
    _set(decorators.MethodMapper, "query", lambda self, func: self._map("query", func))
    _set(test.APIRequestFactory, "query", query_test.factory_query)
    _set(test.APIClient, "query", query_test.client_query)

    get_allowed_methods = EndpointEnumerator.get_allowed_methods
    _set(
        EndpointEnumerator,
        "get_allowed_methods",
        lambda self, callback: [method for method in get_allowed_methods(self, callback) if method != "QUERY"],
    )


def _patch_django_filter() -> None:
    from django_filters.rest_framework import DjangoFilterBackend

    from drf_query_method.django_filters import get_filterset_kwargs

    original = DjangoFilterBackend.get_filterset_kwargs
    _set(
        DjangoFilterBackend,
        "get_filterset_kwargs",
        lambda self, request, queryset, view: get_filterset_kwargs(self, request, queryset, view, original),
    )


def patch() -> None:
    """Add QUERY support to Django, DRF and django-filter in place.

    Safe to call more than once. On Django versions before 6.2 this also
    calls :func:`~drf_query_method.add_query_method`, which :func:`unpatch`
    does not undo.
    """
    if _applied:
        return

    from rest_framework.request import Request

    add_query_method()
    if not hasattr(Request, "filter_params"):
        _patch_drf()
    if importlib.util.find_spec("django_filters") is not None:
        _patch_django_filter()


def unpatch() -> None:
    """Undo :func:`patch`, mainly for tests."""
    while _applied:
        owner, name, original = _applied.pop()
        if original is _MISSING:
            delattr(owner, name)
        else:
            setattr(owner, name, original)
