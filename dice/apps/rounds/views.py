from rest_framework import viewsets
from rest_framework.status import HTTP_403_FORBIDDEN
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied

from dice.apps.rounds.models import Round, Dice
from dice.apps.rounds.serializers import RoundSerializer
from dice.apps.rounds.utilities import Figures
from dice.apps.rounds.permissions import InRoomPermission


class RoundViewSet(viewsets.mixins.CreateModelMixin, viewsets.mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = RoundSerializer
    queryset = Round.objects.all()

    def extra_validation(self, game):
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
        self.permission_classes = [InRoomPermission]
        self.check_object_permissions(self.request, game)
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

# zrobić sprawdzanie kiedy ktoś zrobił ostatnio ruch jeśli nie robi przez minutę to druga osoba wygrywa
# *odświerzanie room --> spr czy ktoś tam jest, jeśli nie to usuwa: DJANGO PERIODIC TASK
