# Unreleased

Record user-visible changes here before the next release.

## Added

- Add `"drf_query_method"` to `INSTALLED_APPS` to apply `patch()` at startup, so you no longer need to call it from
  one of your own apps' `AppConfig.ready()`. `patch()` stays public and idempotent for projects that prefer to call it
  explicitly, and the opt-in classes are unaffected when the app isn't installed.

## Documentation

- README and usage docs make `INSTALLED_APPS` the primary setup path.
