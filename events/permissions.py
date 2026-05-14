from rest_framework import permissions


class IsOrganizerOrReadOnly(permissions.BasePermission):
    """Anyone can read; only the organizer may edit or delete an event."""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and obj.organizer_id == request.user.id
