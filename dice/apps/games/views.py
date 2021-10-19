from rest_framework import viewsets, serializers
from rest_framework.status import HTTP_201_CREATED, HTTP_403_FORBIDDEN, HTTP_400_BAD_REQUEST
from rest_framework.response import Response
from .models import Room, Round, Game, Dice
from .serializers import RoomSerializer, RoundSerializer, DiceSerializer, GameSerializer
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from .utilities import Figures


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
        game = Game.objects.create(room=room)
        game.save()
        return Response({'status': 'joined the room', 'game_id': game.id})


class GameViewSet(viewsets.ModelViewSet):
    # policz pkt dnaego użytkownika i porównaj z pkt drugiego użytkownika
    # popbrać info o wszystkich roundach (informacja o aktualnej rundzie (szukam ostatniej rundy), że by drugi gracz widział co się dzieje u pierwszego lub jeśli go wywali to żeby wiedział na czym stoi)
    pass


class RoundViewSet(viewsets.ModelViewSet):
    serializer_class = RoundSerializer
    queryset = Round.objects.all()

    def perform_create(self, serializer):
        game = serializer.validated_data['game']
        if not (game.room.user == self.request.user or game.room.host == self.request.user):
            raise PermissionDenied('spadaj zlodzieju tozsamosci')
        if Round.objects.filter(user=self.request.user, figure__isnull=True, game=game).exists():
            raise PermissionDenied('Istenieje niezakończona runda, nie można stworzyć kolejnej')
        if Round.objects.filter(user=self.request.user, game=game).count() == 13:
            raise PermissionDenied('Wszystkie figury są zajęte, nie można utworzyć nowej rundy')
        last_round = Round.objects.filter(game=game).order_by('id').last()
        if last_round is None: # zrobić z tego jedną linijkę z or i and
            if game.room.host != self.request.user:
                raise PermissionDenied('Nie Twoja runda')
        elif last_round.user == self.request.user:
            raise PermissionDenied('Nie Twoja runda')
        super().perform_create(serializer)

    @action(detail=True, methods=['PATCH'])
    def reroll(self, request, **kwargs):
        game_round = self.get_object()
        if game_round.turn >= 3:
            return Response(status=HTTP_403_FORBIDDEN)
        if game_round.user != request.user:
            raise PermissionDenied('nie Twoja runda')
        game_dices = [game_round.dice1.id, game_round.dice2.id, game_round.dice3.id, game_round.dice4.id,
                      game_round.dice5.id]
        dices_to_reroll = request.data
        for dice in dices_to_reroll:
            if dice not in game_dices:
                return Response(status=HTTP_403_FORBIDDEN)
        for dice in dices_to_reroll:
            dice = Dice.objects.get(id=dice)
            dice.reroll()
        game_round.turn += 1
        game_round.save()
        return Response(RoundSerializer(game_round).data)

    @action(detail=True, methods=['PATCH'])
    def figure_choice(self, request, **kwargs):
        game_round = self.get_object()
        if game_round.user != request.user:
            raise PermissionDenied('nie Twoja runda')
        chosen_figure = request.data.get('figure')
        if game_round.game.round_set.all().filter(user=request.user, figure=chosen_figure).exists():
            return Response(status=401, data={'error': 'Figura już jest zajeta'})
        game_round.figure = chosen_figure
        game_round.points = game_round.count_points()
        game_round.save()
        return Response(data={'points': game_round.count_points()})


# premia za ułożenie 63 pkt na górze
# premia za 2 generały

