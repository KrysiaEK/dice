import factory.fuzzy
from dice.apps.games.models import Room, Game


class RoomFactory(factory.django.DjangoModelFactory):
    host = factory.SubFactory('dice.apps.users.tests.factories.UserFactory')
    user = factory.SubFactory('dice.apps.users.tests.factories.UserFactory')

    class Meta:
        model = Room


class GameFactory(factory.django.DjangoModelFactory):
    room = factory.SubFactory(RoomFactory)

    class Meta:
        model = Game
