"""Make Django accept the QUERY method on versions before 6.2."""

from django.views.generic import View


def add_query_method() -> None:
    """Add ``query`` to Django's ``View.http_method_names`` if it is missing.

    Django 6.2 lists ``query`` itself, so this does nothing there. On earlier
    versions it lets any view, including DRF's, dispatch ``QUERY`` requests to
    a ``query()`` handler. Earlier versions of Django's CSRF middleware treat
    ``QUERY`` as unsafe, so session-authenticated ``QUERY`` requests need a
    CSRF token until Django 6.2.
    """
    if "query" not in View.http_method_names:
        View.http_method_names = [*View.http_method_names, "query"]
