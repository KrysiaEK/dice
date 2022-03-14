import factory.fuzzy
from dice.apps.rounds.models import Round, Dice


class DiceFactory(factory.django.DjangoModelFactory):
    value = factory.fuzzy.FuzzyInteger(1, 6)

    class Meta:
        model = Dice


class RoundFactory(factory.django.DjangoModelFactory):
    game = factory.SubFactory('dice.apps.games.tests.factories.GameFactory')
    user = factory.SelfAttribute('game.room.host')

    class Meta:
        model = Round
