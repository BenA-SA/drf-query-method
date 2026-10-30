"""DRF viewsets that only answer QUERY on routes that map it."""

from rest_framework import viewsets


def drop_unmapped_query(view) -> None:
    """Stop a viewset answering QUERY on a route whose actions don't map it.

    A viewset's ``query()`` method has the same name as the QUERY handler, so
    without this every route of a viewset that defines ``query()`` would
    answer QUERY, including detail routes.
    """
    if "query" not in (getattr(view, "action_map", None) or {}):
        view.http_method_names = [method for method in view.http_method_names if method != "query"]


class QueryViewSetMixin:
    def dispatch(self, request, *args, **kwargs):
        drop_unmapped_query(self)
        return super().dispatch(request, *args, **kwargs)  # ty: ignore[unresolved-attribute]


class ViewSet(QueryViewSetMixin, viewsets.ViewSet):
    pass


class GenericViewSet(QueryViewSetMixin, viewsets.GenericViewSet):
    pass


class ReadOnlyModelViewSet(QueryViewSetMixin, viewsets.ReadOnlyModelViewSet):
    pass


class ModelViewSet(QueryViewSetMixin, viewsets.ModelViewSet):
    pass
