# Usage

A view accepts `QUERY` by defining a `query()` handler. The request body is parsed by DRF's usual parsers, so
`request.data` works as it does for `POST`:

```python
from rest_framework.response import Response
from rest_framework.views import APIView


class SearchNotes(APIView):
    def query(self, request):
        notes = Note.objects.filter(title__icontains=request.data.get("title", ""))
        return Response(NoteSerializer(notes, many=True).data)
```

Generic views and viewsets don't provide `query()`, so a list view that should accept `QUERY` delegates to `list()`:

```python
class NoteViewSet(ModelViewSet):
    ...

    def query(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
```

The rest of DRF needs to know about `QUERY` too: routers, viewsets, filters, permissions and the test client. There
are two ways to do that.

## Option 1: patch DRF

Call `patch()` once at startup, for example in one of your apps' `AppConfig.ready()`:

```python
from django.apps import AppConfig


class NotesConfig(AppConfig):
    name = "notes"

    def ready(self):
        import drf_query_method

        drf_query_method.patch()
```

DRF then behaves as if [encode/django-rest-framework#10091](https://github.com/encode/django-rest-framework/pull/10091)
were merged:

* `SimpleRouter` and `DefaultRouter` route `QUERY` to a viewset's `query()` on the list route only. An existing
  `@action` named `query` keeps its own route.
* `QUERY` is in `permissions.SAFE_METHODS`, and needs no permissions in `DjangoModelPermissions` and
  `DjangoObjectPermissions`.
* `request.filter_params` merges a `QUERY` request's body over its URL query parameters, and `SearchFilter` and
  `OrderingFilter` read from it.
* `@action(...).mapping.query`, `APIRequestFactory.query()` and `APIClient.query()` are available.
* DRF's deprecated OpenAPI generator leaves `QUERY` out, as OpenAPI 3.0 has no query operation.
* If [django-filter](https://github.com/carltongibson/django-filter) is installed, `DjangoFilterBackend` reads the
  request body too.

`patch()` is safe to call more than once, and leaves DRF alone once DRF supports `QUERY` itself.

## Option 2: opt-in classes

Every class has the same name as DRF's (or django-filter's), so you change the import rather than the code:

| Instead of | Import |
|---|---|
| `rest_framework.routers.SimpleRouter`, `DefaultRouter` | `drf_query_method.routers` |
| `rest_framework.viewsets.ViewSet`, `GenericViewSet`, `ReadOnlyModelViewSet`, `ModelViewSet` | `drf_query_method.viewsets` |
| `rest_framework.filters.SearchFilter`, `OrderingFilter` | `drf_query_method.filters` |
| `rest_framework.permissions.IsAuthenticatedOrReadOnly`, `DjangoModelPermissions`, `DjangoModelPermissionsOrAnonReadOnly`, `DjangoObjectPermissions`, `SAFE_METHODS` | `drf_query_method.permissions` |
| `rest_framework.test.APIRequestFactory`, `APIClient`, `APITestCase` and friends | `drf_query_method.test` |
| `django_filters.rest_framework.DjangoFilterBackend` | `drf_query_method.django_filters` |

Use the router and viewset classes together: the viewsets stop a `query()` method answering `QUERY` on detail routes.

On Django versions before 6.2, also call `drf_query_method.add_query_method()` at startup (`patch()` does this for you).

## Filters and the request body

`QUERY` parameters take the same form as query-string values. Multiple ordering fields are one comma-separated string,
and a JSON list becomes multiple values, like a repeated query-string parameter:

```http
QUERY /notes/?page=2 HTTP/1.1
Content-Type: application/json

{"search": "django", "ordering": "-created,title"}
```

Pagination parameters stay in the URL, so the `next` and `previous` links carry the page. Clients must send them as
`QUERY` requests with the same body to keep the filters.

Custom filter backends should read their parameters with `drf_query_method.filter_params(request)` rather than
`request.query_params`.

## Django versions before 6.2

Django 6.2 supports `QUERY` natively. On earlier versions this package adds it, with one difference: Django's CSRF
middleware treats `QUERY` as unsafe until 6.2, so session-authenticated `QUERY` requests need a CSRF token.

## Moving to DRF's own support

If DRF adds `QUERY` support, remove the `patch()` call (or switch the imports back to DRF's) and uninstall this
package. Your `query()` handlers, `request.filter_params` and test code keep working.
