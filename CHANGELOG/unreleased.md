# Unreleased

## Added

- `patch()` makes [django-rest-framework-datatables](https://github.com/izimobil/django-rest-framework-datatables) read
  `QUERY` request bodies, so server-side DataTables can send their parameters as a `QUERY` body.

## Changed

- `filter_params()` caches its result on the request.
