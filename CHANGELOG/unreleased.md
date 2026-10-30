# Unreleased

These are the changes that will go out in the next release.

## Added

- `patch()`, which adds `QUERY` support to DRF in place, and to django-filter's `DjangoFilterBackend` when installed.
- Opt-in routers, viewsets, filters, permissions, test clients and a django-filter backend, named after DRF's.
- `filter_params()`, the URL query parameters with a `QUERY` request's body merged over them.
- `add_query_method()`, which lets Django versions before 6.2 dispatch `QUERY`.

drf-query-method started out as a project generated from [Cookiecutter PyPackage](https://github.com/audreyfeldroy/cookiecutter-pypackage) containing:

- Initial scaffold for drf-query-method.
- `src/drf_query_method/` package with a py.typed marker
- Tests with pytest and pytest-django
- CI via GitHub Actions: lint (Ruff), type check (ty), a Python/Django/DRF test matrix, coverage reporting
- Security scanning: CodeQL analysis for public repositories, Dependabot, and a Zizmor workflow audit
- Docs site with Zensical + mkdocstrings and a GitHub Pages deployment workflow
- Trusted publishing to PyPI with OIDC and build provenance attestation
- `justfile` with dev commands: qa, test, type-check, docs-serve, release
- Issue templates, PR template, contributing guide, code of conduct, security policy
- BSD 3-Clause license, .editorconfig, .gitignore

### Contributors

[@BenA-SA](https://github.com/BenA-SA) (Ben Atkinson) created drf-query-method.
