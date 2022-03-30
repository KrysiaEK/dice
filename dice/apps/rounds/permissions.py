from rest_framework import permissions


class InRoomPermission(permissions.BasePermission):
    """Ensure user is a member of a room."""

    message = 'You are not in this room.'

    def has_object_permission(self, request, view, obj):
        return request.user == obj.room.host or request.user == obj.room.user
