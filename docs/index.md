# drf-query-method

Support for the HTTP `QUERY` method ([RFC 10008](https://www.rfc-editor.org/rfc/rfc10008.html)) in Django REST framework.

!!! note
    **This is a stop-gap.** Support for `QUERY` has been proposed for Django REST framework itself in
    [encode/django-rest-framework#10091](https://github.com/encode/django-rest-framework/pull/10091).
    If it is merged, use DRF's built-in support instead. This package exists so you can use `QUERY` in the
    meantime, and on Django versions before 6.2. It mirrors the names in that PR (`query()` handlers and
    `request.filter_params`), so switching over should mean removing this package rather than rewriting your views.

## Getting started

- [Installation](installation.md) - how to install drf-query-method
- [Usage](usage.md) - how to use drf-query-method
- [API Reference](api.md) - auto-generated API documentation
