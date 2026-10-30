"""Tests for `drf_query_method` package."""

import django

import drf_query_method


def test_import():
    """Verify the package imports alongside a supported Django version."""
    assert drf_query_method.__name__ == "drf_query_method"
    assert django.VERSION >= (4, 2)
