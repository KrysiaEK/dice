import random
from dice.apps.rounds.models import Dice


def default_dice_value():
    """Factory default value for `value` field in ``Dice`` model."""
    return random.randint(1, 6)


def default_dice_factory():
    """Factory default value for `dice*` fields in ``Round`` model."""
    return Dice.objects.create()
