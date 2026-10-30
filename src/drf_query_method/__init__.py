"""Support for the HTTP QUERY method (RFC 10008) in Django REST framework.

This is a stop-gap until DRF supports ``QUERY`` itself
(encode/django-rest-framework#10091). It mirrors the names used there, so
moving to DRF's own support means removing this package rather than
rewriting views.

There are two ways to use it:

* Opt-in classes with the same names as DRF's, for example
  ``drf_query_method.filters.SearchFilter``, imported in place of DRF's.
* :func:`patch`, which applies the same behaviour to DRF itself, and to
  django-filter when it is installed.
"""

from drf_query_method.methods import add_query_method
from drf_query_method.params import filter_params
from drf_query_method.patching import patch, unpatch

__all__ = ["add_query_method", "filter_params", "patch", "unpatch"]
