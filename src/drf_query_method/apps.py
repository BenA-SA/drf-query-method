"""Django app configuration, which applies :func:`~drf_query_method.patch` at startup."""

from django.apps import AppConfig


class DrfQueryMethodConfig(AppConfig):
    """Calls :func:`~drf_query_method.patch` once Django's app registry is ready.

    Adding ``"drf_query_method"`` to ``INSTALLED_APPS`` is all the setup
    :func:`~drf_query_method.patch` needs. Projects that use the opt-in
    classes instead, or call :func:`~drf_query_method.patch` themselves,
    leave the app out.
    """

    name = "drf_query_method"
    verbose_name = "DRF QUERY method"

    def ready(self) -> None:
        from drf_query_method.patching import patch

        patch()
