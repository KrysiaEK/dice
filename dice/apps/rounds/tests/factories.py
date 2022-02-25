import factory.fuzzy
from dice.apps.rounds.models import Round, Dice
from dice.apps.games.tests.factories import GameFactory


class DiceFactory(factory.django.DjangoModelFactory):
    value = factory.fuzzy.FuzzyInteger(1, 6)

    class Meta:
        model = Dice


class RoundFactory(factory.django.DjangoModelFactory):
    game = factory.SubFactory(GameFactory)
    user = factory.SelfAttribute('game.room.host')

    class Meta:
        model = Round
