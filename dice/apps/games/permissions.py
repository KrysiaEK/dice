from rest_framework import permissions

from dice.apps.games.models import Room


class InRoomPermission(permissions.BasePermission):
    """Ensure user is a member of a room."""

    message = 'You are not in this room.'

    def has_object_permission(self, request, view, obj):
        return request.user == obj.host or request.user == obj.user


class GameNotExists(permissions.BasePermission):
    """Ensure game doesn't exist."""

    message = 'Game already exists.'

    def has_object_permission(self, request, view, obj):
        try:
            return obj.game is None
        except Room.game.RelatedObjectDoesNotExist:
            return True
