# drf-query-method

[![PyPI version](https://img.shields.io/pypi/v/drf-query-method.svg)](https://pypi.org/project/drf-query-method/)

Support for the HTTP `QUERY` method ([RFC 10008](https://www.rfc-editor.org/rfc/rfc10008.html)) in Django REST framework.

> [!NOTE]
> **This is a stop-gap.** Support for `QUERY` has been proposed for Django REST framework itself in
> [encode/django-rest-framework#10091](https://github.com/encode/django-rest-framework/pull/10091).
> If it is merged, use DRF's built-in support instead. This package exists so you can use `QUERY` in the
> meantime, and on Django versions before 6.2. It mirrors the names in that PR (`query()` handlers and
> `request.filter_params`), so switching over should mean removing this package rather than rewriting your views.

`QUERY` is safe and idempotent like `GET`, but carries a request body like `POST`. It suits searches whose
parameters are too long or too structured for a URL.

* [GitHub](https://github.com/BenA-SA/drf-query-method/) | [PyPI](https://pypi.org/project/drf-query-method/) | [Documentation](https://BenA-SA.github.io/drf-query-method/)
* Created by [Ben Atkinson](https://streamlinedanalytics.co.uk) | GitHub [@BenA-SA](https://github.com/BenA-SA)
* BSD 3-Clause License

## Status

Early development; nothing is released yet. The plan:

* Opt-in classes: a router that maps `QUERY` to a viewset's `query()`, `SearchFilter` and `OrderingFilter` that read
  the request body, permission classes that treat `QUERY` as safe, and test clients with `.query()`.
* `request.filter_params`: the URL query parameters with a `QUERY` request's body merged over them.
* An optional `drf_query_method.patch()` that applies all of the above to DRF itself, as if the upstream PR were merged.
  If [django-filter](https://github.com/carltongibson/django-filter) is installed, it is patched too, so
  `DjangoFilterBackend` reads the request body as well.
* On Django versions before 6.2, `QUERY` is added to Django's allowed methods.

## Compatibility

* Python 3.10+
* Django 4.2, 5.0, 5.1, 5.2, 6.0 and 6.1. Django 6.2 adds `QUERY` natively; on earlier versions this package adds it.
* Django REST framework 3.16+

## Installation

```bash
pip install drf-query-method
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup, testing, and release instructions.
