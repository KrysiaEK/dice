import factory
from dice.apps.users.models import User


class UserFactory(factory.django.DjangoModelFactory):
    """Factory of ``User`` model instances."""

    username = factory.Sequence(lambda n: f'user{n}')

    class Meta:
        model = User
