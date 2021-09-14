from rest_framework import viewsets, serializers
from rest_framework.status import HTTP_201_CREATED, HTTP_403_FORBIDDEN, HTTP_400_BAD_REQUEST
from rest_framework.response import Response
from .models import Room, Round, Game, Dice
from .serializers import RoomSerializer, RoundSerializer, DiceSerializer, GameSerializer
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied

#from utilities import roll_dices


class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer

    def perform_create(self, serializer):
        serializer.save()

    def create(self, request, *args, **kwargs):
        data = {
            'host': self.request.user.id,
            **request.data
        }
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=HTTP_201_CREATED, headers=headers)

    @action(detail=True, methods=['PUT'])
    def join(self, request, **kwargs):
        room = self.get_object()
        if room.user:
            return Response(status=HTTP_403_FORBIDDEN)
        if request.user and not request.user.is_authenticated:
            raise PermissionDenied('spadaj zlodzieju tozsamosci')
        room.user = request.user
        room.save()
        print(room.id, 'room id')
        print(room.user.id, 'room user id')
        game = Game.objects.create(room=room)
        game.save()
        round = Round.objects.create(game=game)
        round.save()
        print(game.round)
        return Response({'status': 'joined the room', 'game_id': game.id})


class GameViewSet(viewsets.ModelViewSet):
    pass


class RoundViewSet(viewsets.ModelViewSet):
    serializer_class = RoundSerializer
    queryset = Round.objects.all()

    @action(detail=True, methods=['PATCH'])
    def reroll(self, request, **kwargs):
        game_round = self.get_object()
        if game_round.turn >= 3:
            return Response(status=HTTP_403_FORBIDDEN)
        if not (game_round.game.room.user.id == request.user.id or game_round.game.room.host.id == request.user.id):
            raise PermissionDenied('spadaj zlodzieju tozsamosci')
        game_dices = [game_round.dice1.id, game_round.dice2.id, game_round.dice3.id, game_round.dice4.id,
                      game_round.dice5.id]
        dices_to_reroll = request.data
        for dice in dices_to_reroll:
            if dice not in game_dices:
                return Response(status=HTTP_403_FORBIDDEN)
        for dice in dices_to_reroll:
            if dice == game_round.dice1.id:
                game_round.dice1 = Dice.create()
            elif dice == game_round.dice2.id:
                game_round.dice2 = Dice.create()
            elif dice == game_round.dice3.id:
                game_round.dice3 = Dice.create()
            elif dice == game_round.dice4.id:
                game_round.dice4 = Dice.create()
            elif dice == game_round.dice5.id:
                game_round.dice5 = Dice.create()
        game_round.turn += 1
        game_round.save()
        return Response(RoundSerializer(game_round).data)

   # @action
    #def wybór figury():
        #delete old round
        #create new round

        """
        round.delete()
        round = Round.objects.create(game=game)
        round.save()
        """