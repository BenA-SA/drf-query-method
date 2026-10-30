from types import SimpleNamespace

import pytest
from django.contrib.auth.models import AnonymousUser, Permission, User
from django.http import Http404
from rest_framework import generics

from drf_query_method import permissions
from drf_query_method.test import APIRequestFactory
from tests.views import UserSerializer

factory = APIRequestFactory()


def user_list_view(permission_class):
    class View(generics.ListCreateAPIView):
        queryset = User.objects.all()
        serializer_class = UserSerializer
        permission_classes = [permission_class]
        authentication_classes = []

        def query(self, request, *args, **kwargs):
            return self.list(request, *args, **kwargs)

    return View.as_view()


@pytest.fixture
def user_without_permissions(db):
    return User.objects.create(username="nobody")


def call(view, request, user):
    from rest_framework.test import force_authenticate

    force_authenticate(request, user=user)
    return view(request)


def test_query_is_a_safe_method():
    assert "QUERY" in permissions.SAFE_METHODS


def test_is_authenticated_or_read_only_allows_anonymous_query(db):
    view = user_list_view(permissions.IsAuthenticatedOrReadOnly)
    assert view(factory.query("/", {}, format="json")).status_code == 200
    assert view(factory.post("/", {}, format="json")).status_code in (401, 403)


def test_model_permissions_need_no_permission_for_query(user_without_permissions):
    view = user_list_view(permissions.DjangoModelPermissions)
    assert call(view, factory.query("/", {}, format="json"), user_without_permissions).status_code == 200
    assert call(view, factory.post("/", {"username": "x"}, format="json"), user_without_permissions).status_code == 403


def test_model_permissions_post_still_needs_add_permission(user_without_permissions):
    user_without_permissions.user_permissions.add(Permission.objects.get(codename="add_user"))
    user = User.objects.get(pk=user_without_permissions.pk)
    view = user_list_view(permissions.DjangoModelPermissions)
    assert call(view, factory.post("/", {"username": "x"}, format="json"), user).status_code == 201


def test_anon_read_only_allows_anonymous_query(db):
    view = user_list_view(permissions.DjangoModelPermissionsOrAnonReadOnly)
    assert view(factory.query("/", {}, format="json")).status_code == 200


class ObjectPermissionsUser(AnonymousUser):
    def __init__(self, *granted):
        self.granted = set(granted)

    def has_perms(self, perm_list, obj=None):
        return set(perm_list) <= self.granted


class ViewObjectPermissions(permissions.DjangoObjectPermissions):
    perms_map = {
        **permissions.DjangoObjectPermissions.perms_map,
        "GET": ["%(app_label)s.view_%(model_name)s"],
        "QUERY": ["%(app_label)s.view_%(model_name)s"],
    }


def check_object_permission(method, user):
    permission = ViewObjectPermissions()
    view = SimpleNamespace(get_queryset=lambda: User.objects.none())
    return permission.has_object_permission(SimpleNamespace(method=method, user=user), view, object())


def test_object_permissions_allow_query_with_view_permission():
    assert check_object_permission("QUERY", ObjectPermissionsUser("auth.view_user")) is True


def test_object_permissions_hide_objects_from_query():
    with pytest.raises(Http404):
        check_object_permission("QUERY", ObjectPermissionsUser())


def test_object_permissions_forbid_writes_to_readable_objects():
    assert check_object_permission("DELETE", ObjectPermissionsUser("auth.view_user")) is False


def test_object_permissions_hide_unreadable_objects_from_writes():
    with pytest.raises(Http404):
        check_object_permission("DELETE", ObjectPermissionsUser())


def test_object_permissions_require_no_permission_for_query():
    assert permissions.DjangoObjectPermissions.perms_map["QUERY"] == []
