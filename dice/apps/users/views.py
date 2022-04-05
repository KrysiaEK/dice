from rest_framework import viewsets
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response

from dice.apps.users.models import User
from dice.apps.users.serializers import UserSerializer


class UserViewSet(viewsets.mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class CustomObtainAuthToken(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        """Create authentication token."""

        response = super(CustomObtainAuthToken, self).post(request, *args, **kwargs)
        token = Token.objects.get(key=response.data['token'])
        return Response({'token': token.key, 'user_id': token.user_id})
