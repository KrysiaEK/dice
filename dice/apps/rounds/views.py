from rest_framework import viewsets
from rest_framework.status import HTTP_403_FORBIDDEN
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied

from dice.apps.rounds.models import Round, Dice
from dice.apps.rounds.serializers import RoundSerializer
from dice.apps.rounds.utilities import Figures


class RoundViewSet(viewsets.mixins.CreateModelMixin, viewsets.mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """View set to manage rounds."""

    serializer_class = RoundSerializer
    queryset = Round.objects.all()

    def extra_validation(self, game):
        """Validation if next round can be created.

        1. Validation if user is in room.
        2. Validation if previous round ended.
        3. Validation if there are more figures and game didn't ended.
        4. Validation if first round is created for host (host is starting).
        5. Validation if round is created for the right user.

        If not PermissionDenied is raised.
        """

        if not (game.room.user == self.request.user or game.room.host == self.request.user):
            raise PermissionDenied('Spadaj złodzieju tożsamości')
        if Round.objects.filter(user=self.request.user, figure__isnull=True, game=game).exists():
            raise PermissionDenied('Istenieje niezakończona runda, nie można stworzyć kolejnej')
        if Round.objects.filter(user=self.request.user, game=game).count() == 13:
            raise PermissionDenied('Wszystkie figury są zajęte, nie można utworzyć nowej rundy')
        last_round = Round.objects.filter(game=game).order_by('id').last()
        if last_round is None:
            if game.room.host != self.request.user:
                raise PermissionDenied('Nie Twoja runda')
        elif last_round.user == self.request.user:
            raise PermissionDenied('Nie Twoja runda')

    def perform_create(self, serializer):
        """Function to create round with validation."""

        game = serializer.validated_data['game']
        self.extra_validation(game)
        super().perform_create(serializer)

    @action(detail=True, methods=['PATCH'])
    def reroll(self, request, **kwargs):
        """Function to set dices' new values.

        Player decide which dices he/she wants to roll again and roll them at the most twice.
        Validation if player rolled dices at most three times (first roll + 2 rerolls).
        Validation if dices rolls player whose turn is it.
        Validation if dice is from right round.
        """

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
        """Function to choose figure and save points.

        New round is created. After last round game ends and players' rankings are updated.
        Validation if right player (whose turn it is) is making choice.
        Validation if player don't want to choose figure again.
        """

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

    @action(detail=True, methods=['GET'])
    def count_possible_points(self, request, **kwargs):
        """Function to count points for each figure to show player how many points she/he can get with dice
        configuration he/she has."""

        game_round = self.get_object()
        possible_points = []
        for choice in Figures.Choices:
            possible_points.append(game_round.count_points(choice[0]))
        return Response(data={'possible_points': possible_points})
