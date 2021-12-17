from rest_framework import viewsets
from rest_framework.status import HTTP_201_CREATED, HTTP_403_FORBIDDEN
from rest_framework.response import Response
from .models import Room, Round, Game, Dice
from .serializers import RoomSerializer, RoundSerializer, GameSerializer
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from .decorators import user_is_authenticated, user_in_room, game_not_exists

from .utilities import Figures


class RoomViewSet(viewsets.mixins.CreateModelMixin, viewsets.mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(Room.objects.filter(
            active=True))  # dodać kolejny filtr patrzący czy dany room nie nie był utworzony więcej niż ponad 1h temu

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        serializer.save()

    def create(self, request, *args, **kwargs):
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

    @user_is_authenticated
    @action(detail=True, methods=['PUT'])
    def join(self, request, **kwargs):
        room = self.get_object()
        if room.user:
            return Response(status=HTTP_403_FORBIDDEN)
        if request.user == room.host:
            return Response(status=HTTP_403_FORBIDDEN)
        room.user = request.user
        room.save()
        return Response({'status': 'joined the room'})

    @game_not_exists
    @user_in_room
    @user_is_authenticated
    @action(detail=True, methods=['POST'])
    def leave(self, request, **kwargs):
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

    # dodać w modelu pole kiedy założono room i po 1h room dostaje status nieaktywny (

    @user_in_room
    @game_not_exists
    @action(detail=True, methods=['POST'])
    def start(self, request, **kwargs):
        room = self.get_object()
        if room.user != request.user and room.host != request.user:
            return Response(status=HTTP_403_FORBIDDEN)
        # ustaw czas kiedy pierwszy kliknął
        # ustaw kto kliknął start
        # spr czy drugi gracz klinknął już start w ciągu ostatnich 10 sek i zacznij grę (porównać z game_start)
        game = Game.objects.create(room=room)
        game.save()
        # a jak nie spełni się warunek to:


class GameViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = GameSerializer
    queryset = Game.objects.all()

    @action(detail=True, methods=['GET'])
    def count_final_points(self, request, **kwargs):
        game = self.get_object()
        host_points, user_points = game.count_final_points()
        return Response(data={'host_points': host_points, 'user_points': user_points})

    @action(detail=True, methods=['GET'])
    def rounds(self, request, **kwargs):
        game = self.get_object()
        rounds_queryset = game.round_set.all().order_by('id')
        rounds = RoundSerializer(rounds_queryset, many=True)
        return Response(data={'all_rounds': rounds.data})


class RoundViewSet(viewsets.mixins.CreateModelMixin, viewsets.mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = RoundSerializer
    queryset = Round.objects.all()

    def extra_validation(self, game):
        if not (game.room.user == self.request.user or game.room.host == self.request.user):
            raise PermissionDenied('spadaj zlodzieju tozsamosci')
        if Round.objects.filter(user=self.request.user, figure__isnull=True, game=game).exists():
            raise PermissionDenied('Istenieje niezakończona runda, nie można stworzyć kolejnej')
        if Round.objects.filter(user=self.request.user, game=game).count() == 13:
            raise PermissionDenied('Wszystkie figury są zajęte, nie można utworzyć nowej rundy')
        last_round = Round.objects.filter(game=game).order_by('id').last()
        if last_round is None:  # zrobić z tego jedną linijkę z or i and
            if game.room.host != self.request.user:
                raise PermissionDenied('Nie Twoja runda')
        elif last_round.user == self.request.user:
            raise PermissionDenied('Nie Twoja runda')

    def perform_create(self, serializer):
        game = serializer.validated_data['game']
        self.extra_validation(game)
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
            return Response(status=403, data={'error': 'Figura już jest zajeta'})
        game_round.figure = chosen_figure
        game_round.points = game_round.count_points()
        game_round.extra_points = game_round.count_extra_points()
        game_round.save()
        if game_round.game.round_set.all().count() == 26:
            game_round.game.update_players_ranking()
        new_round = Round.objects.create(game=game_round.game, user=request.user)
        new_round.save()
        return Response(
            data={'points': game_round.points, 'extra_points': game_round.extra_points, "round_id": new_round.id})

    # napisz test dla update_player_rank robię 26 round i puszczam figur choice, wywyołuję figure_choice --> sprawdzić czy wywołuje się funkcja update_player_rank
    # for choice in choices

    @action(detail=True, methods=['GET'])
    def count_possible_points(self, request, **kwargs):
        game_round = self.get_object()
        possible_points = []
        for choice in Figures.Choices:
            possible_points.append(game_round.count_points(choice[0]))
        return Response(data={'possible_points': possible_points})


# gra się nie zaczyna od razu jak ktoś wchodzi do room

# zrobić sprawdzanie kiedy ktoś zrobił ostatnio ruch jeśli nie robi przez minutę to druga osoba wygrywa
# *odświerzanie room --> spr czy ktoś tam jest, jeśli nie to usuwa: DJANGO PERIODIC TASK
