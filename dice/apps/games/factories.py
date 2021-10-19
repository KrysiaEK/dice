import factory
import factory.fuzzy
from dice.apps.games.models import Room, Round, Game, Dice
from dice.apps.users.factories import UserFactory


class RoomFactory(factory.django.DjangoModelFactory):
    host = factory.SubFactory(UserFactory)
    user = factory.SubFactory(UserFactory)

    class Meta:
        model = Room


class DiceFactory(factory.django.DjangoModelFactory):
    value = factory.fuzzy.FuzzyInteger(1, 6)

    class Meta:
        model = Dice


class GameFactory(factory.django.DjangoModelFactory):
    room = factory.SubFactory(RoomFactory)

    class Meta:
        model = Game


class RoundFactory(factory.django.DjangoModelFactory):
    game = factory.SubFactory(GameFactory)
    user = factory.SelfAttribute('game.room.host')

    class Meta:
        model = Round
