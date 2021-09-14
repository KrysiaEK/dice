from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token

from dice.apps.users.factories import UserFactory
from dice.apps.games.factories import RoomFactory, RoundFactory, GameFactory
from dice.apps.games.models import Room


class RoomTestCase(APITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = UserFactory()
        cls.room = RoomFactory(user=None)

    def setUp(self):
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

    def test_create_room(self):
        rooms_before = Room.objects.count()
        response = self.client.post('/api/v1/rooms/')
        rooms_after = Room.objects.count()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(rooms_after, rooms_before + 1)
        host_id = response.json().get('host')
        self.assertEqual(host_id, self.user.id)

    def test_join_room(self):
        response = self.client.put(
            f'/api/v1/rooms/{self.room.id}/join/',
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        self.room.refresh_from_db()
        user_id = self.room.user.id
        self.assertEqual(user_id, self.user.id)
        data = response.json()
        self.assertTrue(data.get('game_id'))

    def test_join_room_user_exists(self):
        user = UserFactory()
        self.room.user = user
        self.room.save()
        response = self.client.put(
            f'/api/v1/rooms/{self.room.id}/join/',
            format='json',
        )
        self.assertEqual(response.status_code, 403)

    def test_get_game_status(self):
        response = self.client.get(
            f'/api/v1/rooms/{self.room.id}/',
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsNone(data.get('game'))
        response = self.client.put(
            f'/api/v1/rooms/{self.room.id}/join/',
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        response = self.client.get(
            f'/api/v1/rooms/{self.room.id}/',
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsNotNone(data.get('game'))


class RoundTestCase(APITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.game_round = RoundFactory()

    def setUp(self):
        self.token = Token.objects.create(user=self.game_round.game.room.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

    def test_roll(self):
        response = self.client.patch(
            f'/api/v1/rounds/{self.game_round.id}/reroll/',
            data=[
                self.game_round.dice1.id, self.game_round.dice2.id
            ],
            format='json',
        )
        self.assertEqual(response.status_code, 200)

    def test_too_many_roll(self):
        for status_code in [200, 200, 403]:
            response = self.client.patch(
                f'/api/v1/rounds/{self.game_round.id}/reroll/',
                data=[
                    self.game_round.dice1.id, self.game_round.dice2.id
                ],
                format='json',
            )
            self.game_round.refresh_from_db()
            self.assertEqual(status_code, response.status_code)

#napisać test czy przy przerzucie zmienia się id kości

    """
    def test_create_round(self):
        response = self.client.post(
            f'/api/v1/rounds/',
            format='json',
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        print(data)
        self.assertTrue(data.get('dice1').get('value') < 7)
        self.assertTrue(data.get('dice2').get('value') < 7)
        self.assertTrue(data.get('dice3').get('value') < 7)
        self.assertTrue(data.get('dice4').get('value') < 7)
        self.assertTrue(data.get('dice5').get('value') < 7)
    """

    def test_roll_again(self):
        game_round2 = RoundFactory()

        response = self.client.patch(
            f'/api/v1/rounds/{self.game_round.id}/reroll/',
            data=[
                self.game_round.dice2.id, game_round2.dice4.id
            ],
            format='json',
        )
        self.assertEqual(response.status_code, 403)



   