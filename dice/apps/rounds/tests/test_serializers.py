from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token

from dice.apps.rounds.utilities import Figures
from dice.apps.games.tests.factories import RoomFactory, GameFactory
from dice.apps.rounds.tests.factories import RoundFactory


class RoundTestCase(APITestCase):
    """Tests for rounds' serializers."""

    @classmethod
    def setUpTestData(cls):
        cls.game_round = RoundFactory()
        cls.game = cls.game_round.game
        cls.host = cls.game.room.host
        cls.user = cls.game.room.user

    def setUp(self):
        self.token_host = Token.objects.create(user=self.host)
        self.token_user = Token.objects.create(user=self.user)
        self.client_host = self.client_class()
        self.client_host.credentials(HTTP_AUTHORIZATION='Token ' + self.token_host.key)
        self.client_user = self.client_class()
        self.client_user.credentials(HTTP_AUTHORIZATION='Token ' + self.token_user.key)

    def test_create_first_round_by_host(self):
        """Test checking creating round properly.

        Round is created by host and 5 dices are rolled.
        """

        room = RoomFactory(user=self.user, host=self.host)
        game = GameFactory(room=room)
        response = self.client_host.post(
            f'/api/v1/rounds/',
            data={
                'game': game.id,
            },
            format='json',
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertTrue(data.get('dice1').get('value') < 7)
        self.assertTrue(data.get('dice2').get('value') < 7)
        self.assertTrue(data.get('dice3').get('value') < 7)
        self.assertTrue(data.get('dice4').get('value') < 7)
        self.assertTrue(data.get('dice5').get('value') < 7)

    def test_create_first_round_by_user(self):
        """Test checking if error 403 is raised when user wants to create first round."""

        room = RoomFactory(user=self.user, host=self.host)
        game = GameFactory(room=room)
        response = self.client_user.post(
            f'/api/v1/rounds/',
            data={
                'game': game.id,
            },
            format='json',
        )
        self.assertEqual(response.status_code, 403)

    def test_create_next_round(self):
        """Test checking if 403 is raised when host try to create new round before first was ended."""

        response = self.client_host.post(
            f'/api/v1/rounds/',
            data={
                'game': self.game.id,
            },
            format='json',
        )
        self.assertEqual(response.status_code, 403)

    def test_create_second_round(self):
        """Test checking creating user round after host round is ended."""

        self.game_round.figure = Figures.LARGE_STRAIGHT
        self.game_round.save()
        response = self.client_user.post(
            f'/api/v1/rounds/',
            data={
                'game': self.game.id,
            },
            format='json',
        )
        self.assertEqual(response.status_code, 201)

    def test_create_third_round(self):
        """Test checking creating host round after user round is ended."""

        self.game_round.figure = Figures.LARGE_STRAIGHT
        self.game_round.save()
        RoundFactory(game=self.game, user=self.user, figure=Figures.FIVE)
        response = self.client_host.post(
            f'/api/v1/rounds/',
            data={
                'game': self.game.id,
            },
            format='json',
        )
        self.assertEqual(response.status_code, 201)
