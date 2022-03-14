from rest_framework import permissions


class InRoomPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        room = self.get_object()
        if self.request.user != room.host and self.request.user != room.user:
            return False
        return True
