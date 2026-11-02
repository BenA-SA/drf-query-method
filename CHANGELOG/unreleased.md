# Unreleased

Record user-visible changes here before the next release.

## Added

- Add `"drf_query_method"` to `INSTALLED_APPS` to apply `patch()` at startup, so you no longer need to call it from
  one of your own apps' `AppConfig.ready()`. `patch()` stays public and idempotent for projects that prefer to call it
  explicitly, and the opt-in classes are unaffected when the app isn't installed.
- `QueryMixin` gives a list view a `query()` handler that delegates to `list()`, so `QUERY` no longer needs a
  hand-written handler on each view: `class NoteViewSet(QueryMixin, ModelViewSet)`. It works with any view that has a
  `list()` method.

## Changed

- `patch()` gives DRF's `ListModelMixin` the same `query()` handler, so with DRF patched every list view and viewset
  accepts `QUERY` on its list route without any change to the view. Views that define their own `query()` keep it,
  detail routes still return 405, and a view can opt out by leaving `query` out of `http_method_names`.
- When drf-spectacular is installed, `patch()` leaves `QUERY` out of its schema. drf-spectacular previously failed with
  `KeyError: 'query'` on any view with a `query()` handler.

## Documentation

- README and usage docs make `INSTALLED_APPS` the primary setup path, and drop the per-view `query()`
  boilerplate from the examples, showing `QueryMixin` for the opt-in classes.
