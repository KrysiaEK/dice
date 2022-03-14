from unittest import TestCase

from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token

from dice.apps.rounds.utilities import Figures
from dice.apps.games.tests.factories import GameFactory
from dice.apps.rounds.tests.factories import RoundFactory


class GameTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
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

    def test_count_final_points(self):
        RoundFactory(game=self.game, user=self.user, figure=Figures.FIVE, points=15)
        RoundFactory(game=self.game, user=self.user, figure=Figures.LARGE_STRAIGHT, points=40)
        RoundFactory(game=self.game, user=self.host, figure=Figures.FULL_HOUSE, points=25)
        RoundFactory(game=self.game, user=self.host, figure=Figures.THREE, points=12)
        response = self.client_host.get(
            f'/api/v1/games/{self.game.id}/count_final_points/',
            format='json',
        )
        self.assertEqual(response.json().get('host_points'), 37)
        self.assertEqual(response.json().get('user_points'), 55)
        self.assertEqual(response.status_code, 200)

    def test_count_final_points_with_extra_points(self):
        RoundFactory(game=self.game, user=self.user, figure=Figures.FIVE, points=25, extra_points=50)
        RoundFactory(game=self.game, user=self.user, figure=Figures.LARGE_STRAIGHT, points=40)
        RoundFactory(game=self.game, user=self.host, figure=Figures.FULL_HOUSE, points=25)
        RoundFactory(game=self.game, user=self.host, figure=Figures.THREE, points=12)
        response = self.client_host.get(
            f'/api/v1/games/{self.game.id}/count_final_points/',
            format='json',
        )
        self.assertEqual(response.json().get('host_points'), 37)
        self.assertEqual(response.json().get('user_points'), 115)
        self.assertEqual(response.status_code, 200)

    def test_count_final_points_round_is_none(self):
        response = self.client_host.get(
            f'/api/v1/games/{self.game.id}/count_final_points/',
            format='json',
        )
        self.assertEqual(response.json().get('host_points'), 0)
        self.assertEqual(response.json().get('user_points'), 0)
        self.assertEqual(response.status_code, 200)

    def test_count_final_points_round_user_is_none(self):
        RoundFactory(game=self.game, user=self.host, figure=Figures.FULL_HOUSE, points=25)
        response = self.client_host.get(
            f'/api/v1/games/{self.game.id}/count_final_points/',
            format='json',
        )
        self.assertEqual(response.json().get('host_points'), 25)
        self.assertEqual(response.json().get('user_points'), 0)
        self.assertEqual(response.status_code, 200)


class NonAPIGameTestCase(TestCase):
    def setUp(self):
        self.game = GameFactory()
        self.host = self.game.room.host
        self.user = self.game.room.user

    def test_count_score(self):
        RoundFactory(game=self.game, user=self.host, figure=Figures.SIX, points=30)
        self.game.update_players_ranking()
        self.user.refresh_from_db()
        self.host.refresh_from_db()
        self.assertEqual(self.host.score, 1210)
        self.assertEqual(self.user.score, 1190)

    def test_count_score_draw(self):
        self.game.update_players_ranking()
        self.user.refresh_from_db()
        self.host.refresh_from_db()
        self.assertEqual(self.host.score, 1200)
        self.assertEqual(self.user.score, 1200)
