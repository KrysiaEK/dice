import factory.fuzzy
from dice.apps.games.models import Room, Game
from dice.apps.users.tests.factories import UserFactory


class RoomFactory(factory.django.DjangoModelFactory):
    host = factory.SubFactory(UserFactory)
    user = factory.SubFactory(UserFactory)

    class Meta:
        model = Room


class GameFactory(factory.django.DjangoModelFactory):
    room = factory.SubFactory(RoomFactory)

    class Meta:
        model = Game
