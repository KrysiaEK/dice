from rest_framework import permissions

import dice.apps.games.tests.test_views.test_game_views

from dice.apps.games.models import Room


class InRoomPermission(permissions.BasePermission):
    message = 'You are not in this room.'

    def has_object_permission(self, request, view, obj):
        return request.user == obj.host or request.user == obj.user


class GameNotExists(permissions.BasePermission):
    message = 'Game already exists.'

    def has_object_permission(self, request, view, obj):
        try:
            if obj.game is not None:
                return False
        except Room.game.RelatedObjectDoesNotExist:
            return True

