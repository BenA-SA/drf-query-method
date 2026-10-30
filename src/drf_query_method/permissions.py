"""DRF permission classes that treat QUERY as a safe method.

``has_object_permission`` is adapted from Django REST framework
(Copyright Encode OSS Ltd, BSD 3-Clause; see LICENSE).
"""

from django.http import Http404
from rest_framework import permissions

SAFE_METHODS = ("GET", "HEAD", "OPTIONS", "QUERY")


class IsAuthenticatedOrReadOnly(permissions.IsAuthenticatedOrReadOnly):
    def has_permission(self, request, view):
        return bool(request.method in SAFE_METHODS or (request.user and request.user.is_authenticated))


class DjangoModelPermissions(permissions.DjangoModelPermissions):
    perms_map = {**permissions.DjangoModelPermissions.perms_map, "QUERY": []}


class DjangoModelPermissionsOrAnonReadOnly(DjangoModelPermissions):
    authenticated_users_only = False


class DjangoObjectPermissions(permissions.DjangoObjectPermissions):
    perms_map = {**permissions.DjangoObjectPermissions.perms_map, "QUERY": []}

    def has_object_permission(self, request, view, obj):
        queryset = self._queryset(view)
        model_cls = queryset.model
        user = request.user

        perms = self.get_required_object_permissions(request.method, model_cls)
        if user.has_perms(perms, obj):
            return True

        # A user without read permission sees a 404 rather than a 403.
        if request.method in SAFE_METHODS:
            raise Http404

        read_perms = self.get_required_object_permissions("GET", model_cls)
        if not user.has_perms(read_perms, obj):
            raise Http404
        return False
