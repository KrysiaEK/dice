from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from dice.apps.games.tests.factories import GameFactory
from dice.apps.rounds.tests.factories import RoundFactory
from dice.apps.rounds.utilities import Figures


class GameTestCase(APITestCase):
    """Tests of ``Game`` views methods."""

    @classmethod
    def setUpTestData(cls):
        """Setup related models required to run tests."""

        cls.game = GameFactory()
        cls.host = cls.game.room.host
        cls.user = cls.game.room.user

    def setUp(self):
        self.token_host = Token.objects.create(user=self.host)
        self.token_user = Token.objects.create(user=self.user)
        self.client_host = self.client_class()
        self.client_host.credentials(HTTP_AUTHORIZATION='Token ' + self.token_host.key)
        self.client_user = self.client_class()
        self.client_user.credentials(HTTP_AUTHORIZATION='Token ' + self.token_user.key)

    def test_get_one_round_queryset(self):
        """Ensure one round queryset is displayed."""

        RoundFactory(game=self.game, user=self.host, figure=Figures.FULL_HOUSE, points=25)
        response = self.client_host.get(
            f'/api/v1/games/{self.game.id}/rounds/',
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json().get('all_rounds')), 1)

    def test_get_two_rounds_queryset(self):
        """Ensure two rounds queryset is displayed."""

        RoundFactory(game=self.game, user=self.host, figure=Figures.FULL_HOUSE, points=25)
        RoundFactory(game=self.game, user=self.user, figure=Figures.SMALL_STRAIGHT, points=30)
        response = self.client_host.get(
            f'/api/v1/games/{self.game.id}/rounds/',
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json().get('all_rounds')), 2)

    def test_get_rounds_from_two_games_queryset(self):
        """Ensure two rounds queryset from two different games is displayed."""

        game2 = GameFactory()
        RoundFactory(game=self.game, user=self.host, figure=Figures.FULL_HOUSE, points=0)
        RoundFactory(game=game2, user=game2.room.host, figure=Figures.SMALL_STRAIGHT, points=30)
        response = self.client_host.get(
            f'/api/v1/games/{self.game.id}/rounds/',
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json().get('all_rounds')), 1)
