from unittest import TestCase

from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token

from dice.apps.games.utilities import Figures
from dice.apps.users.tests.factories import UserFactory
from dice.apps.games.tests.factories import RoomFactory, RoundFactory, GameFactory
from dice.apps.games.models import Room, Round
from datetime import timedelta


class RoomTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpClass()
        cls.user = UserFactory()
        cls.room = RoomFactory(user=None)

    def setUp(self):
        self.token = Token.objects.create(user=self.user)
        self.token_host = Token.objects.create(user=self.room.host)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        self.client_host = self.client_class()
        self.client_host.credentials(HTTP_AUTHORIZATION='Token ' + self.token_host.key)

    def test_create_room(self):
        rooms_before = Room.objects.count()
        response = self.client.post('/api/v1/rooms/')
        rooms_after = Room.objects.count()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(rooms_after, rooms_before + 1)
        host_id = response.json().get('host')
        self.assertEqual(host_id, self.user.id)

    def test_create_room_user_in_two_rooms(self):
        room = RoomFactory()
        room.host = self.user
        room.save()
        rooms_before = Room.objects.count()
        response = self.client.post('/api/v1/rooms/')
        rooms_after = Room.objects.count()
        self.assertEqual(response.status_code, 403)
        self.assertEqual(rooms_after, rooms_before)

    def test_create_room_user_in_two_rooms_one_inactive(self):
        room = RoomFactory()
        room.host = self.user
        room.active = False
        room.save()
        rooms_before = Room.objects.count()
        response = self.client.post('/api/v1/rooms/')
        rooms_after = Room.objects.count()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(rooms_after, rooms_before + 1)
        host_id = response.json().get('host')
        self.assertEqual(host_id, self.user.id)

    """
    def test_list_rooms(self):
        response = self.client_host.get('/api/v1/rooms/list/')
        self.assertEqual(response.status_code, 200)
        room = RoomFactory()
        room2 = RoomFactory()
        room.time_of_creation = timezone.now() + timedelta(hours=17)
        room.save()
        room2.time_of_creation = timezone.now()
        room2.save()
        response = self.client_host.get('/api/list')
        self.assertEqual(response.status_code, 200)
        print(response.json())
    """

    def test_join_room(self):
        response = self.client.put(
            f'/api/v1/rooms/{self.room.id}/join/',
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        self.room.refresh_from_db()
        user_id = self.room.user.id
        self.assertEqual(user_id, self.user.id)

    def test_join_room_user_exists(self):
        user = UserFactory()
        self.room.user = user
        self.room.save()
        response = self.client.put(
            f'/api/v1/rooms/{self.room.id}/join/',
            format='json',
        )
        self.assertEqual(response.status_code, 403)

    def test_leave_room_by_user(self):
        #self.room.refresh_from_db() # dlaczego tutaj to nie jest potrzebne?
        self.room.user = self.user
        self.room.save()
        response = self.client.post(
            f'/api/v1/rooms/{self.room.id}/leave/',
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        self.room.refresh_from_db()
        self.assertEqual(None, self.room.user)

    """"
    def test_leave_room_by_host(self):
        response = self.client_host.post(
            f'/api/v1/rooms/{self.room.id}/leave/',
            format='json',
        )
        print(response.json())
        self.assertEqual(response.status_code, 200)
        self.room.refresh_from_db()
        self.assertEqual(None, self.room.host)
        self.assertEqual(False, self.room.active)
    """

    def test_start_game(self):
        response = self.client.get(
            f'/api/v1/rooms/{self.room.id}/',
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsNone(data.get('game_id'))
        response = self.client.put(
            f'/api/v1/rooms/{self.room.id}/join/',
            format='json',
        )
        self.assertIsNone(data.get('game_id'))
        response = self.client.post(
            f'/api/v1/rooms/{self.room.id}/start/',
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        response = self.client_host.post(
            f'/api/v1/rooms/{self.room.id}/start/',
            format='json',
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertIsNotNone(data.get('game_id'))
        response = self.client.get(
            f'/api/v1/rooms/{self.room.id}/',
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsNotNone(data.get('game_id'))

    def test_start_game_after_10_sec(self):
        response = self.client.get(
            f'/api/v1/rooms/{self.room.id}/',
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsNone(data.get('game_id'))
        response = self.client.put(
            f'/api/v1/rooms/{self.room.id}/join/',
            format='json',
        )
        self.assertIsNone(data.get('game_id'))
        self.assertIsNone(data.get('game_id'))
        response = self.client.post(
            f'/api/v1/rooms/{self.room.id}/start/',
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        self.room.refresh_from_db()
        self.room.start_game = self.room.start_game - timedelta(seconds=11)
        self.room.save()
        response = self.client_host.post(
            f'/api/v1/rooms/{self.room.id}/start/',
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        response = self.client.get(
            f'/api/v1/rooms/{self.room.id}/',
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsNone(data.get('game_id'))


class GameTestCase(APITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
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

    def test_get_one_round_queryset(self):
        RoundFactory(game=self.game, user=self.host, figure=Figures.FULL_HOUSE, points=25)
        response = self.client_host.get(
            f'/api/v1/games/{self.game.id}/rounds/',
            format='json',
        )
        self.assertEqual(response.status_code, 200)

    def test_get_two_rounds_queryset(self):
        RoundFactory(game=self.game, user=self.host, figure=Figures.FULL_HOUSE, points=25)
        RoundFactory(game=self.game, user=self.user, figure=Figures.SMALL_STRAIGHT, points=30)
        response = self.client_host.get(
            f'/api/v1/games/{self.game.id}/rounds/',
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json().get('all_rounds')), 2)

    def test_get_rounds_from_two_games_queryset(self):
        game2 = GameFactory()
        RoundFactory(game=self.game, user=self.host, figure=Figures.FULL_HOUSE, points=0)
        RoundFactory(game=game2, user=game2.room.host, figure=Figures.SMALL_STRAIGHT, points=30)
        response = self.client_host.get(
            f'/api/v1/games/{self.game.id}/rounds/',
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json().get('all_rounds')), 1)


class RoundTestCase(APITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
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

    def test_roll(self):
        response = self.client_host.patch(
            f'/api/v1/rounds/{self.game_round.id}/reroll/',
            data=[
                self.game_round.dice1.id, self.game_round.dice2.id
            ],
            format='json',
        )
        self.assertEqual(response.status_code, 200)

    def test_too_many_roll(self):
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

    def test_figure_choice_with_extra_points_yatzy_wrong(self):
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
        self.game_round.figure = Figures.LARGE_STRAIGHT
        self.game_round.points = 40
        self.game_round.save()
        response = self.client_user.get(
            f'/api/v1/rounds/{self.game_round.id}/',
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get('points'), 40)

    '''
    def test_update_ranking(self):
        
        for choice in Figures.Choices:

            for figure_value, figure_name in Figures.Choices:
                RoundFactory(game=self.game, user=self.user, figure=figure_value)
                RoundFactory(game=self.game, user=self.host, figure=figure_value)
    '''

    def test_delete_round(self):
        response = self.client_user.delete(
            f'/api/v1/rounds/{self.game_round.id}/',
            format='json',
        )
        self.assertEqual(response.status_code, 405)

    def test_count_possble_points(self):
        self.game_round.set_dices(5, 5, 4, 3, 6)
        response = self.client_host.get(
            f'/api/v1/rounds/{self.game_round.id}/count_possible_points/',
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get('possible_points'), [0, 0, 3, 4, 10, 6, 0, 0, 0, 30, 0, 0, 23])


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


class NonAPIRoundTestCase(TestCase):
    def setUp(self):
        self.round = RoundFactory()

    def test_count_large_straight(self):
        self.round.set_dices(4, 3, 2, 5, 1)
        self.round.figure = Figures.LARGE_STRAIGHT
        self.round.save()
        self.assertEqual(self.round.count_points(), 40)

    def test_count_small_straight(self):
        self.round.set_dices(4, 3, 2, 1, 6)
        self.round.figure = Figures.SMALL_STRAIGHT
        self.assertEqual(self.round.count_points(), 30)

    def test_count_full_house(self):
        self.round.set_dices(2, 2, 3, 3, 3)
        self.round.figure = Figures.FULL_HOUSE
        self.assertEqual(self.round.count_points(), 25)

    def test_count_one(self):
        self.round.set_dices(1, 1, 1, 1, 6)
        self.round.figure = Figures.ONE
        self.assertEqual(self.round.count_points(), 4)

    def test_count_two(self):
        self.round.set_dices(2, 4, 5, 1, 6)
        self.round.figure = Figures.TWO
        self.assertEqual(self.round.count_points(), 2)

    def test_count_three(self):
        self.round.set_dices(3, 4, 3, 1, 3)
        self.round.figure = Figures.THREE
        self.assertEqual(self.round.count_points(), 9)

    def test_count_four(self):
        self.round.set_dices(3, 4, 4, 1, 2)
        self.round.figure = Figures.FOUR
        self.assertEqual(self.round.count_points(), 8)

    def test_count_five(self):
        self.round.set_dices(3, 5, 4, 1, 2)
        self.round.figure = Figures.FIVE
        self.assertEqual(self.round.count_points(), 5)

    def test_count_six(self):
        self.round.set_dices(6, 6, 6, 6, 2)
        self.round.figure = Figures.SIX
        self.assertEqual(self.round.count_points(), 24)

    def test_count_trio(self):
        self.round.set_dices(5, 6, 5, 5, 2)
        self.round.figure = Figures.TRIO
        self.assertEqual(self.round.count_points(), 23)

    def test_count_quatro(self):
        self.round.set_dices(5, 5, 5, 5, 2)
        self.round.figure = Figures.QUATRO
        self.assertEqual(self.round.count_points(), 22)

    def test_count_yatzy(self):
        self.round.set_dices(1, 1, 1, 1, 1)
        self.round.figure = Figures.YATZY
        self.assertEqual(self.round.count_points(), 50)

    def test_count_chance(self):
        self.round.set_dices(5, 5, 4, 3, 6)
        self.round.figure = Figures.CHANCE
        self.assertEqual(self.round.count_points(), 23)
