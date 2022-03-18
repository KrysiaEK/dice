from rest_framework import permissions

from dice.apps.games.models import Room


class InRoomPermission(permissions.BasePermission):
    """Permission checking if user is in room.

    If user isn't in room 403 is raised.
    """

    message = 'You are not in this room.'

    def has_object_permission(self, request, view, obj):
        return request.user == obj.host or request.user == obj.user


class GameNotExists(permissions.BasePermission):
    """Permission checking if game already exists.

    If game already started 403 is raised.
    """

    message = 'Game already exists.'

    def has_object_permission(self, request, view, obj):
        try:
            if obj.game is not None:
                return False
        except Room.game.RelatedObjectDoesNotExist:
            return True
