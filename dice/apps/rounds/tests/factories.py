import factory.fuzzy
from dice.apps.rounds.models import Round, Dice


class DiceFactory(factory.django.DjangoModelFactory):
    """Factory of ``Dice`` model instances."""

    value = factory.fuzzy.FuzzyInteger(1, 6)

    class Meta:
        model = Dice


class RoundFactory(factory.django.DjangoModelFactory):
    """Factory of ``Round`` model instances."""

    game = factory.SubFactory('dice.apps.games.tests.factories.GameFactory')
    user = factory.SelfAttribute('game.room.host')

    class Meta:
        model = Round
