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

A list view answers `QUERY` by delegating to `list()`, so its filters can travel in the request body. With
[`patch()`](#option-1-patch-drf), every view built on DRF's `ListModelMixin` gets that handler, including
`ListAPIView`, `ModelViewSet` and `ReadOnlyModelViewSet`. Without it, add `QueryMixin`, which works with any view that
has a `list()` method:

```python
from drf_query_method import QueryMixin


class NoteViewSet(QueryMixin, ModelViewSet):
    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    filter_backends = [SearchFilter]
    search_fields = ["title"]
```

Either way, a view that defines its own `query()` keeps it. That handler is a plain method:

```python
class NoteViewSet(ModelViewSet):
    ...

    def query(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
```

The rest of DRF needs to know about `QUERY` too: routers, viewsets, filters, permissions and the test client. There
are two ways to do that.

## Option 1: patch DRF

Add the package to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    ...
    "rest_framework",
    "drf_query_method",
]
```

Its `AppConfig.ready()` calls `drf_query_method.patch()` when Django starts. The app has no models, migrations,
templates or URLs, so that is all it does.

If you'd rather patch DRF explicitly, leave the app out and call `patch()` once at startup yourself, for example in one
of your apps' `AppConfig.ready()`:

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

* Every view built on `ListModelMixin` has a `query()` handler that delegates to `list()`, unless it defines its own.
  This includes generic list views such as `ListAPIView` and `ListCreateAPIView`, not just viewsets.
* `SimpleRouter` and `DefaultRouter` route `QUERY` to a viewset's `query()` on the list route only, so detail routes
  return 405. An existing `@action` named `query` keeps its own route.
* `QUERY` is in `permissions.SAFE_METHODS`, and needs no permissions in `DjangoModelPermissions` and
  `DjangoObjectPermissions`.
* `request.filter_params` merges a `QUERY` request's body over its URL query parameters, and `SearchFilter` and
  `OrderingFilter` read from it.
* `@action(...).mapping.query`, `APIRequestFactory.query()` and `APIClient.query()` are available.
* DRF's deprecated OpenAPI generator leaves `QUERY` out, as OpenAPI 3.0 has no query operation. If
  [drf-spectacular](https://github.com/tfranzel/drf-spectacular) is installed, it leaves `QUERY` out too, rather than
  failing on views with a `query()` handler.
* If [django-filter](https://github.com/carltongibson/django-filter) is installed, `DjangoFilterBackend` reads the
  request body too.
* If [django-rest-framework-datatables](https://github.com/izimobil/django-rest-framework-datatables) is installed, its
  filter backends, pagination and renderer read the request body too. See [DataTables](#datatables) below.

To keep a list view from answering `QUERY`, leave `query` out of its `http_method_names`:

```python
class NoteList(ListAPIView):
    http_method_names = [method for method in ListAPIView.http_method_names if method != "query"]
```

`patch()` is safe to call more than once, including alongside the installed app. Once DRF supports `QUERY` itself, `patch()` leaves DRF's routers, filters and
permissions alone, but still gives list views their `query()` handler, as DRF only routes `QUERY` to views that define
one.

## Option 2: opt-in classes

Every class has the same name as DRF's (or django-filter's), so you change the import rather than the code. Don't add
`drf_query_method` to `INSTALLED_APPS` on this path, as that patches DRF:

| Instead of | Import |
|---|---|
| `rest_framework.routers.SimpleRouter`, `DefaultRouter` | `drf_query_method.routers` |
| `rest_framework.viewsets.ViewSet`, `GenericViewSet`, `ReadOnlyModelViewSet`, `ModelViewSet` | `drf_query_method.viewsets` |
| `rest_framework.filters.SearchFilter`, `OrderingFilter` | `drf_query_method.filters` |
| `rest_framework.permissions.IsAuthenticatedOrReadOnly`, `DjangoModelPermissions`, `DjangoModelPermissionsOrAnonReadOnly`, `DjangoObjectPermissions`, `SAFE_METHODS` | `drf_query_method.permissions` |
| `rest_framework.test.APIRequestFactory`, `APIClient`, `APITestCase` and friends | `drf_query_method.test` |
| `django_filters.rest_framework.DjangoFilterBackend` | `drf_query_method.django_filters` |

DRF's views have no `query()` handler on this path, so add `QueryMixin` to the list views that should accept `QUERY`
(or define `query()` yourself). It works with these viewsets and with DRF's generic views:

```python
from drf_query_method import QueryMixin
from drf_query_method.filters import SearchFilter
from drf_query_method.viewsets import ModelViewSet


class NoteViewSet(QueryMixin, ModelViewSet):
    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    filter_backends = [SearchFilter]
    search_fields = ["title"]
```

django-rest-framework-datatables is supported through `patch()` only.

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

## Sending QUERY requests

Most HTTP clients accept any method name. With `fetch()`:

```javascript
const response = await fetch("/api/notes/", {
  method: "QUERY",
  headers: {"Content-Type": "application/json"},
  body: JSON.stringify({search: "django", ordering: "-created"}),
});
```

With jQuery, which sends `data` as a form-encoded body for any method other than `GET` and `HEAD`:

```javascript
$.ajax({url: "/api/notes/", type: "QUERY", data: {search: "django"}});
```

With curl:

```sh
curl -X QUERY -H "Content-Type: application/json" -d '{"search": "django"}' https://example.com/api/notes/
```

A few things to check before relying on `QUERY` in production:

* **CORS.** `QUERY` is not a CORS-safelisted method, so cross-origin requests trigger a preflight request, and
  the server must list `QUERY` in `Access-Control-Allow-Methods`. With
  [django-cors-headers](https://github.com/adamchainz/django-cors-headers), add it to `CORS_ALLOW_METHODS`:

    ```python
    from corsheaders.defaults import default_methods

    CORS_ALLOW_METHODS = (*default_methods, "QUERY")
    ```

* **CSRF.** None needed: `QUERY` is a safe method, so it never needs a CSRF token on any supported Django version. See
  [Django versions before 6.2](#django-versions-before-62) for how older versions get the same behaviour.
* **Proxies, CDNs and firewalls.** Some reject request methods they don't recognise. Check that `QUERY` reaches your
  application through everything in front of it.
* **Caching.** `QUERY` responses are cacheable in principle, but caches generally don't key on request bodies, and
  Django's `cache_page` ignores `QUERY` from 6.2. Don't expect responses to be cached.
## DataTables

With `patch()` and [django-rest-framework-datatables](https://github.com/izimobil/django-rest-framework-datatables),
a server-side DataTable can send its parameters as a `QUERY` body instead of a long query string. Keep `format=datatables`
in the URL, and set the Ajax type:

```javascript
new DataTable("#notes", {
  serverSide: true,
  ajax: {url: "/api/notes/?format=datatables", type: "QUERY"},
  columns: [{data: "title"}, {data: "created"}],
});
```

jQuery sends DataTables' parameters as a form-encoded body for any method other than `GET` and `HEAD`, which is the
form django-rest-framework-datatables expects. With `patch()`, the list view already has a `query()` handler. Its `?keep=` parameter is
still read from the URL.

## Django versions before 6.2

Django 6.2 supports `QUERY` natively. On Django 4.2 to 6.1, `add_query_method()` (which `patch()` calls) brings the same
behaviour to older versions in two ways:

* It adds `query` to Django's allowed view methods, so views can define a `query()` handler.
* It treats `QUERY` as a safe method in `CsrfViewMiddleware`, as Django 6.2 does. Before 6.2 the middleware only
  exempts `GET`, `HEAD`, `OPTIONS` and `TRACE`, so without this, session-authenticated `QUERY` requests would need a
  CSRF token. DRF's `SessionAuthentication` checks CSRF through the same middleware, so it follows suit.

The result is that `QUERY` never needs a CSRF token, whichever supported Django version you're on. If you call
`add_query_method()` yourself rather than `patch()`, call it once at startup, before requests are served.

This is safe for the same reason it is in Django 6.2. CSRF protects against another site making a logged-in user's
browser send a request. HTML forms can only send `GET` and `POST`, so `QUERY` can only come from JavaScript, and
because `QUERY` is not a CORS-safelisted method, the browser asks your server's permission with a preflight request
before sending a cross-origin one. As with `GET`, a `query()` handler must never change data.

## Moving to DRF's own support

If DRF adds `QUERY` support, remove `drf_query_method` from `INSTALLED_APPS` (or remove the `patch()` call, or switch
the imports back to DRF's) and uninstall this package. Your `query()` handlers, `request.filter_params` and test code keep working.

DRF's own support only routes `QUERY` to views that define `query()`. Before uninstalling, give each list view that
relies on `patch()`'s automatic handler, or on `QueryMixin`, a `query()` handler of its own.
