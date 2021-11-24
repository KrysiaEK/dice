from rest_framework.exceptions import PermissionDenied
from functools import wraps


def user_is_authenticated(view_function):
    @wraps(view_function)  # bo django robi z nazwy funkcji url, a dekorator zmienia nazwę funckji, więc wrap jest potrzebny by zachować nazwę
    def decorator(self, request, *args, **kwargs):
        if request.user and not request.user.is_authenticated:
            raise PermissionDenied('spadaj zlodzieju tozsamosci')
        return view_function(self, request, *args, **kwargs)
    return decorator
