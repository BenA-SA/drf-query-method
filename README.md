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
* Created by [Ben Atkinson](https://streamlinedanalytics.co.uk) | GitHub [@BenA-SA](https://github.com/BenA-SA) | PyPI [@Ben-SA](https://pypi.org/user/Ben-SA/)
* BSD 3-Clause License

## Usage

Define a `query()` handler, then call `patch()` once at startup:

```python
import drf_query_method

drf_query_method.patch()


class NoteViewSet(ModelViewSet):
    ...

    def query(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
```

Routers then send `QUERY /notes/` to `query()`, and `SearchFilter`, `OrderingFilter`, django-filter's
`DjangoFilterBackend` and django-rest-framework-datatables read their parameters from the request body. If you'd rather not patch DRF, import drop-in
classes with the same names from `drf_query_method` instead. See the [documentation](https://BenA-SA.github.io/drf-query-method/usage/)
for both approaches, and for sending `QUERY` requests from JavaScript and other clients.

The package is in early development. Releases are on [PyPI](https://pypi.org/project/drf-query-method/).

## CSRF

`QUERY` is a safe method, so it never needs a CSRF token, on any supported Django version. Django 6.2 exempts it from
CSRF checks itself. On Django 4.2 to 6.1, where this package adds `QUERY`, it also teaches Django's
`CsrfViewMiddleware` to treat `QUERY` as safe, so the behaviour matches 6.2. DRF's `SessionAuthentication` uses the same
check, so session-authenticated `QUERY` requests work without a token too.

The trade-off is the one `GET` has always had: a `query()` handler must never change data. Cross-site requests are
still guarded by CORS, because browsers can only send `QUERY` from JavaScript, and `QUERY` isn't a CORS-safelisted
method, so a cross-origin request needs your server's permission first.

## Compatibility

* Python 3.10+
* Django 4.2, 5.0, 5.1, 5.2, 6.0 and 6.1. Django 6.2 adds `QUERY` natively; on earlier versions this package adds it,
  including Django 6.2's CSRF behaviour.
* Django REST framework 3.16+
* django-filter and django-rest-framework-datatables, optionally

## Installation

```bash
pip install drf-query-method
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup, testing, and release instructions.
