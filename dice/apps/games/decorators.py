from rest_framework.exceptions import PermissionDenied
from rest_framework.status import HTTP_403_FORBIDDEN, HTTP_400_BAD_REQUEST
from rest_framework.response import Response
from functools import wraps
from .models import Room


def user_is_authenticated(view_function):
    @wraps(view_function)  # bo django robi z nazwy funkcji url, a dekorator zmienia nazwę funckji, więc wrap jest potrzebny by zachować nazwę
    def decorator(self, request, **kwargs):
        if request.user and not request.user.is_authenticated:
            raise PermissionDenied('spadaj zlodzieju tozsamosci')
        return view_function(self, request, **kwargs)
    return decorator


def user_in_room(view_function):
    @wraps(view_function)
    def decorator(self, request, **kwargs):
        room = self.get_object()
        if self.request.user != room.host and self.request.user != room.user:
            print(self.request.user, room.host, room.user)
            return Response('You are not in this room!', status=HTTP_400_BAD_REQUEST)
        return view_function(self, request, **kwargs)
    return decorator


def game_not_exists(view_function):
    @wraps(view_function)
    def decorator(self, request, **kwargs):
        room = self.get_object()
        try:
            if room.game is not None:
                return Response(status=HTTP_403_FORBIDDEN)
        except Room.game.RelatedObjectDoesNotExist:
            pass
        return view_function(self, request, **kwargs)
    return decorator
