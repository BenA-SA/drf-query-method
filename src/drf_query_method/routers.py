"""DRF routers that route QUERY to a viewset's ``query()`` on the list route."""

import copy

from rest_framework import routers


def _is_list_route(route) -> bool:
    return isinstance(route, routers.Route) and route.mapping.get("get") == "list"


def with_query_route(routes):
    """Map QUERY to ``query`` on the list route of ``routes``."""
    return [
        route._replace(mapping={**route.mapping, "query": "query"}) if _is_list_route(route) else route
        for route in routes
    ]


def without_query_route(routes):
    """Remove the QUERY mapping from every route in ``routes``."""
    return [
        route._replace(mapping={method: action for method, action in route.mapping.items() if action != "query"})
        if isinstance(route, routers.Route)
        else route
        for route in routes
    ]


def has_query_action(viewset) -> bool:
    """Whether the viewset already has an ``@action`` named ``query``."""
    return any(action.__name__ == "query" for action in viewset.get_extra_actions())


def get_routes_keeping_query_actions(router, viewset, get_routes):
    """Call ``get_routes``, leaving QUERY unrouted when the viewset has an ``@action`` named ``query``.

    That action keeps its own route, and DRF would otherwise reject it for
    clashing with the built-in ``query`` route.
    """
    if not has_query_action(viewset):
        return get_routes(router, viewset)

    router_without_query = copy.copy(router)
    router_without_query.routes = without_query_route(router.routes)
    return get_routes(router_without_query, viewset)


class QueryRouterMixin:
    routes = with_query_route(routers.SimpleRouter.routes)

    def get_routes(self, viewset):
        return get_routes_keeping_query_actions(self, viewset, super(QueryRouterMixin, type(self)).get_routes)  # ty: ignore[unresolved-attribute]


class SimpleRouter(QueryRouterMixin, routers.SimpleRouter):
    pass


class DefaultRouter(QueryRouterMixin, routers.DefaultRouter):
    pass
