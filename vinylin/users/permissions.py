from rest_framework.permissions import BasePermission


class IsOwner(BasePermission):
    """Allows access only to owners"""

    def has_permission(self, request, view):
        return bool(request.user.pk == int(view.kwargs.get('pk', 0)))
