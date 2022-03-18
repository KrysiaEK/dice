from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token

from dice.apps.rounds.utilities import Figures
from dice.apps.rounds.tests.factories import RoundFactory
from dice.apps.rounds.models import Round


class RoundTestCase(APITestCase):
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

    # todo(KrysiaEK): 6 testów testujących walidację create round

    def test_roll(self):
        """Test checking rolling again chosen dices."""

        response = self.client_host.patch(
            f'/api/v1/rounds/{self.game_round.id}/reroll/',
            data=[
                self.game_round.dice1.id, self.game_round.dice2.id
            ],
            format='json',
        )
        self.assertEqual(response.status_code, 200)

    def test_too_many_roll(self):
        """Test checking if error 403 is raised when player rolled dices 3 times."""

        for status_code in [200, 200, 403]:
            response = self.client_host.patch(
                f'/api/v1/rounds/{self.game_round.id}/reroll/',
                data=[
                    self.game_round.dice1.id, self.game_round.dice2.id
                ],
                format='json',
            )
            self.game_round.refresh_from_db()
            self.assertEqual(status_code, response.status_code)

    def test_invalid_roll_again(self):
        """Test checking if error 403 is raised when player wants to roll dice from different round."""

        # todo(KrysiaEK): sprawdzic czy właśwciwy status
        game_round2 = RoundFactory()
        response = self.client_host.patch(
            f'/api/v1/rounds/{self.game_round.id}/reroll/',
            data=[
                self.game_round.dice2.id, game_round2.dice4.id
            ],
            format='json',
        )
        self.assertEqual(response.status_code, 403)

    def test_figure_choice(self):
        """Test checking figure choice."""

        self.game_round.set_dices(4, 4, 4, 3, 3)
        rounds_before = Round.objects.count()
        response = self.client_host.patch(
            f'/api/v1/rounds/{self.game_round.id}/figure_choice/',
            data={
                'figure': Figures.FULL_HOUSE,
            },
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        rounds_after = Round.objects.count()
        self.assertEqual(rounds_after, rounds_before + 1)
        self.assertEqual(response.json().get('points'), 25)

    def test_figure_choice_already_chosen(self):
        """Test checking if error 403 is raised when player wants to choose already chosen figure."""

        self.game_round.figure = Figures.FULL_HOUSE
        self.game_round.save()
        response = self.client_host.patch(
            f'/api/v1/rounds/{self.game_round.id}/figure_choice/',
            data={
                'figure': Figures.FULL_HOUSE,
            },
            format='json',
        )
        self.assertEqual(response.status_code, 403)

    def test_choose_figure_for_zero_points(self):
        """Test checking if user got 0 points if she/he chose figure but had wrong configuration of numbers."""

        self.game_round.set_dices(4, 4, 5, 3, 2)
        response = self.client_host.patch(
            f'/api/v1/rounds/{self.game_round.id}/figure_choice/',
            data={
                'figure': Figures.FULL_HOUSE,
            },
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get('points'), 0)

    def test_all_figures_taken(self):
        """Test checking if error 403 is raised when user try to create round after end of the game (when all figures
        were chosen)."""

        self.game_round.figure = Figures.ONE
        self.game_round.save()
        for figure_value, figure_name in Figures.Choices:
            RoundFactory(game=self.game, user=self.user, figure=figure_value)
            RoundFactory(game=self.game, user=self.host, figure=figure_value)
        response = self.client_user.post(
            f'/api/v1/rounds/',
            data={
                'game': self.game.id,
            },
            format='json',
        )
        self.assertEqual(response.status_code, 403)

    def test_figure_choice_with_extra_points_yatzy(self):
        """Test checking if user got extra points for second yatzy."""

        self.game_round.set_dices(4, 4, 4, 4, 4)
        RoundFactory(game=self.game, user=self.host, figure=Figures.YATZY, points=50)
        response = self.client_host.patch(
            f'/api/v1/rounds/{self.game_round.id}/figure_choice/',
            data={
                'figure': Figures.FOUR,
            },
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get('extra_points'), 50)

    #todo (KrysiaEK):
    # 1. test gdy ktoś chce wybrać figurę gdy nie jego kolej
    # 2. test gdy figura którą ktoś chce wybrać jest już zajęta

    def test_figure_choice_with_extra_points_yatzy_wrong(self):
        """Test checking if user got 0 extra points for yatzy after he/she already chose yatzy figure with 0 points."""

        self.game_round.set_dices(4, 4, 4, 4, 4)
        RoundFactory(game=self.game, user=self.host, figure=Figures.YATZY, points=0)
        response = self.client_host.patch(
            f'/api/v1/rounds/{self.game_round.id}/figure_choice/',
            data={
                'figure': Figures.FOUR,
            },
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get('extra_points'), 0)

    def test_figure_choice_with_extra_points_63(self):
        """Test checking if user got 35 extra points for getting 63 or more points for upper figures."""

        self.game_round.set_dices(4, 4, 4, 3, 3)
        RoundFactory(game=self.game, user=self.host, figure=Figures.SIX, points=24)
        RoundFactory(game=self.game, user=self.host, figure=Figures.FIVE, points=20)
        RoundFactory(game=self.game, user=self.host, figure=Figures.FOUR, points=16)
        response = self.client_host.patch(
            f'/api/v1/rounds/{self.game_round.id}/figure_choice/',
            data={
                'figure': Figures.THREE,
            },
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get('extra_points'), 35)

    def test_figure_choice_with_extra_points_63_wrong(self):
        """Test checking if user got 0 extra points for after completing upper figures but has less than 63 points."""

        self.game_round.set_dices(4, 4, 4, 3, 3)
        RoundFactory(game=self.game, user=self.host, figure=Figures.SIX, points=30)
        RoundFactory(game=self.game, user=self.host, figure=Figures.FIVE, points=20)
        RoundFactory(game=self.game, user=self.host, figure=Figures.FOUR, points=16)
        response = self.client_host.patch(
            f'/api/v1/rounds/{self.game_round.id}/figure_choice/',
            data={
                'figure': Figures.THREE,
            },
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get('extra_points'), 0)

    def test_show_figure_and_points(self):
        """Test checking getting information about taken figure and points obtained for this figure."""

        self.game_round.figure = Figures.LARGE_STRAIGHT
        self.game_round.points = 40
        self.game_round.save()
        response = self.client_user.get(
            f'/api/v1/rounds/{self.game_round.id}/',
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get('points'), 40)

    def test_delete_round(self):
        """Test checking if error 405 is raised when somebody try to delete round."""

        response = self.client_user.delete(
            f'/api/v1/rounds/{self.game_round.id}/',
            format='json',
        )
        self.assertEqual(response.status_code, 405)

    def test_count_possble_points(self):
        """Test checking counting possible points."""

        self.game_round.set_dices(5, 5, 4, 3, 6)
        response = self.client_host.get(
            f'/api/v1/rounds/{self.game_round.id}/count_possible_points/',
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get('possible_points'), [0, 0, 3, 4, 10, 6, 0, 0, 0, 30, 0, 0, 23])
