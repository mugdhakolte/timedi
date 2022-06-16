from rest_framework import permissions


class IsSuperUser(permissions.BasePermission):
    """Global permission check for SuperUser."""

    def has_permission(self, request, view):
        user = request.user
        return user.is_authenticated and user.is_superuser

    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and request.user.is_superuser


class CheckPermission(permissions.BasePermission):
    """Global permission check for SuperUser."""

    def has_permission(self, request, view):
        user = request.user
        if hasattr(view, 'required_permission') and not request.user.is_superuser:
            for perm in view.required_permission:
                write = None
                read = None
                if view.action in ['list', 'retrieve']:
                    read = True
                elif view.action in ['create', 'update', 'partial_update']:
                    write = True
                if user.has_permission(perm, write, read):
                    return True
        return True

    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated
