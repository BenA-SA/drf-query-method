"""Make Django accept the QUERY method on versions before 6.2."""

import functools

from django.middleware.csrf import CsrfViewMiddleware
from django.views.generic import View


def add_query_method() -> None:
    """Make Django before 6.2 handle ``QUERY`` as Django 6.2 does.

    Django 6.2 supports ``QUERY`` natively, so this does nothing there. On
    earlier versions it adds ``query`` to ``View.http_method_names``, so any
    view, including DRF's, can dispatch ``QUERY`` requests to a ``query()``
    handler, and it treats ``QUERY`` as a safe method in
    ``CsrfViewMiddleware``, so ``QUERY`` requests need no CSRF token. See
    :func:`skip_csrf_for_query`.
    """
    if "query" in View.http_method_names:
        return
    View.http_method_names = [*View.http_method_names, "query"]
    CsrfViewMiddleware.process_view = skip_csrf_for_query(CsrfViewMiddleware.process_view)


def skip_csrf_for_query(process_view):
    """Wrap ``CsrfViewMiddleware.process_view`` to accept ``QUERY`` like ``GET``.

    Django 6.2 adds ``QUERY`` to the methods the middleware exempts as safe
    under RFC 9110. Earlier versions hard-code ``GET``, ``HEAD``, ``OPTIONS``
    and ``TRACE``, so the wrapper sends ``QUERY`` down the same path: a request
    already processed, or a ``csrf_exempt`` view, is left alone, and anything
    else is accepted without a token. Every other method falls through to
    Django unchanged.

    DRF's ``SessionAuthentication`` checks CSRF through ``CSRFCheck``, a
    ``CsrfViewMiddleware`` subclass, so it follows the same rule.
    """

    @functools.wraps(process_view)
    def wrapper(self, request, callback, callback_args, callback_kwargs):
        if request.method != "QUERY":
            return process_view(self, request, callback, callback_args, callback_kwargs)
        if getattr(request, "csrf_processing_done", False) or getattr(callback, "csrf_exempt", False):
            return None
        return self._accept(request)

    return wrapper
