"""A mixin that lets a list view answer QUERY without writing a ``query()`` handler."""


class QueryMixin:
    """Answer ``QUERY`` by delegating to ``list()``, so filters can travel in the request body.

    Put it before the view's base class, for example
    ``class NoteViewSet(QueryMixin, ModelViewSet)``. It works with any view
    that has a ``list()`` method, including a ``ViewSet`` that defines its own.

    :func:`~drf_query_method.patch` gives DRF's ``ListModelMixin`` the same
    handler, so with DRF patched the mixin is only needed for views that
    define ``list()`` without ``ListModelMixin``.


    The routers in this package, and DRF's once patched, route ``QUERY`` on
    such a viewset straight to the ``list`` action, so ``self.action`` is
    ``"list"`` and code that branches on it, such as ``get_serializer_class()``
    or ``get_permissions()``, treats ``QUERY`` like ``GET``.
    """

    def query(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)  # ty: ignore[unresolved-attribute]

    query.delegates_to_list = True  # ty: ignore[unresolved-attribute]


def delegates_query_to_list(viewset) -> bool:
    """Whether the viewset's ``query()`` is :class:`QueryMixin`'s, rather than one it defines itself."""
    return getattr(getattr(viewset, "query", None), "delegates_to_list", False)
