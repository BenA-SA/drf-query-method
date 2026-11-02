"""A mixin that lets a list view answer QUERY without writing a ``query()`` handler."""


class QueryMixin:
    """Answer ``QUERY`` by delegating to ``list()``, so filters can travel in the request body.

    Put it before the view's base class, for example
    ``class NoteViewSet(QueryMixin, ModelViewSet)``. It works with any view
    that has a ``list()`` method, including a ``ViewSet`` that defines its own.

    :func:`~drf_query_method.patch` gives DRF's ``ListModelMixin`` the same
    handler, so with DRF patched the mixin is only needed for views that
    define ``list()`` without ``ListModelMixin``.
    """

    def query(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)  # ty: ignore[unresolved-attribute]
