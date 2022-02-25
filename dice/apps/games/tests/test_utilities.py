from unittest import TestCase

from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token

from dice.apps.games.utilities import Figures
from dice.apps.users.tests.factories import UserFactory
from dice.apps.games.tests.factories import RoomFactory, RoundFactory, GameFactory
from dice.apps.games.models import Room, Round
from datetime import timedelta

