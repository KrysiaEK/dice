from rest_framework import viewsets
from rest_framework.status import HTTP_201_CREATED, HTTP_403_FORBIDDEN
from rest_framework.response import Response
from rest_framework.decorators import action
from datetime import timedelta
from django.utils import timezone

from dice.apps.games.models import Room, Game
from dice.apps.games.serializers import RoomSerializer, GameSerializer
from dice.apps.rounds.serializers import RoundSerializer
from dice.apps.games.permissions import InRoomPermission, GameNotExists


class RoomViewSet(viewsets.mixins.CreateModelMixin, viewsets.mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """Views set of ``Room`` model."""

    queryset = Room.objects.all()
    serializer_class = RoomSerializer

    def list(self, request, *args, **kwargs):
        """List all active ``Room`` instances."""

        room = self.get_object()
        time_of_expire = room.time_of_creation + timedelta(hours=10)
        queryset = self.filter_queryset(Room.objects.filter(
            active=True, time_of_creation__lt=time_of_expire))
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        serializer.save()

    def create(self, request, *args, **kwargs):
        """Create ``Room`` instance hosted by authenticated user.

        Following validation is performed to ensure ``Room`` instance
        will have proper state:

        + player is not a host of other active room
        + user(host) is not a member of other active room

        """

        data = {
            'host': self.request.user.id,
            **request.data
        }
        if Room.objects.filter(host=self.request.user, active=True).exists() or Room.objects.filter(
                user=self.request.user, active=True).exists():
            return Response(status=HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=HTTP_201_CREATED, headers=headers)

    @action(detail=True, methods=['PUT'])
    def join(self, request, **kwargs):
        """Join ``Room`` instance by authenticated user.

        Following validation is performed to ensure ``Room`` instance
        will have proper state:

        + room is not full
        + host don't join again

        """

        room = self.get_object()
        if room.user:
            return Response(status=HTTP_403_FORBIDDEN)
        if request.user == room.host:
            return Response(status=HTTP_403_FORBIDDEN)
        room.user = request.user
        room.save()
        return Response({'status': 'joined the room'})

    @action(detail=True, methods=['POST'], permission_classes=[InRoomPermission, GameNotExists])
    def leave(self, request, **kwargs):
        """Leave ``Room`` instance by authenticated user.

        If host left room then second player become a host,
        if there is no second player then room become inactive.

        Following validation is performed to ensure ``Room`` instance
        will have proper state:

        + user is member of a room
        + game is not created

        """

        room = self.get_object()
        if self.request.user == room.host:
            if room.user:
                room.host = room.user
                room.user = None
            else:
                room.host = None
                room.active = False
        else:
            room.user = None
        room.save()
        return Response({'status': 'you left the room'})

    @action(detail=True, methods=['POST'], permission_classes=[InRoomPermission, GameNotExists])
    def start(self, request, **kwargs):
        """Create ``Game`` instance by two authenticated users.

        Following validation is performed to ensure ``Game`` instance
        will have proper state:

        + user is member of room
        + game is not created
        + one player press start once

        """

        room = self.get_object()
        if room.host is None or room.user is None:
            return Response({'status': 'waiting for second user'})
        if room.start_game is None or room.start_game + timedelta(seconds=10) < timezone.now():
            room.start_game = timezone.now()
            room.who_started_game = request.user
            room.save()
            return Response({'status': 'waiting for second user'})
        if room.who_started_game == request.user:
            return Response({'status': 'waiting for second user'})
        game = Game.objects.create(room=room)
        game.save()
        return Response(data={'game_id': game.id}, status=HTTP_201_CREATED)


class GameViewSet(viewsets.ReadOnlyModelViewSet):
    """Views set of ``Game`` model."""

    serializer_class = GameSerializer
    queryset = Game.objects.all()

    @action(detail=True, methods=['GET'])
    def count_final_points(self, request, **kwargs):
        """Get and count players' final points."""

        game = self.get_object()
        host_points, user_points = game.count_final_points()
        return Response(data={'host_points': host_points, 'user_points': user_points})

    @action(detail=True, methods=['GET'])
    def rounds(self, request, **kwargs):
        """Get all game's ``Round`` instances."""

        game = self.get_object()
        rounds_queryset = game.round_set.all().order_by('id')
        rounds = RoundSerializer(rounds_queryset, many=True)
        return Response(data={'all_rounds': rounds.data})
