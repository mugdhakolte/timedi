from rest_framework import permissions


class IsSuperUser(permissions.BasePermission):
    """Global permission check for SuperUser."""
    def has_permission(self, request, view):
        user = request.user
        return user.is_authenticated and user.is_superuser

    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and request.user.is_superuser
