from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from datetime import timedelta

from dice.apps.users.tests.factories import UserFactory
from dice.apps.games.tests.factories import RoomFactory
from dice.apps.games.models import Room


class RoomTestCase(APITestCase):
    """Tests for rooms' views."""

    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()
        cls.room = RoomFactory(user=None)

    def setUp(self):
        self.token = Token.objects.create(user=self.user)
        self.token_host = Token.objects.create(user=self.room.host)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        self.client_host = self.client_class()
        self.client_host.credentials(HTTP_AUTHORIZATION='Token ' + self.token_host.key)

    # todo(KrysiaEK): test list view?

    def test_create_room(self):
        """Test create room.

        Checking if person who created room is host.
        """

        rooms_before = Room.objects.count()
        response = self.client.post('/api/v1/rooms/')
        rooms_after = Room.objects.count()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(rooms_after, rooms_before + 1)
        host_id = response.json().get('host')
        self.assertEqual(host_id, self.user.id)

    def test_create_room_user_in_two_rooms(self):
        """Test checking if 403 is raised when person who wants to create new room is in other, active room."""

        room = RoomFactory()
        room.host = self.user
        room.save()
        rooms_before = Room.objects.count()
        response = self.client.post('/api/v1/rooms/')
        rooms_after = Room.objects.count()
        self.assertEqual(response.status_code, 403)
        self.assertEqual(rooms_after, rooms_before)

    def test_create_room_user_in_two_rooms_one_inactive(self):
        """Test checking create room when person who wants to create new room is in other, inactive room."""

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

    def test_join_room(self):
        """Test checking joining room."""

        # todo(KrysiaEK): sprawdzić czy status joined room
        response = self.client.put(
            f'/api/v1/rooms/{self.room.id}/join/',
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        self.room.refresh_from_db()
        user_id = self.room.user.id
        self.assertEqual(user_id, self.user.id)

    def test_join_room_user_exists(self):
        """Test checking if error 403 is raised when room is full and somebody try to join it."""

        user = UserFactory()
        self.room.user = user
        self.room.save()
        response = self.client.put(
            f'/api/v1/rooms/{self.room.id}/join/',
            format='json',
        )
        self.assertEqual(response.status_code, 403)

    # todo(KrysiaEK): host chce dołączyć jeszcze raz, i 403

    def test_leave_room_by_user(self):
        """Test checking leaving room by user."""

        # todo(KrysiaEK): spr czy status 'you left the room'

        self.room.user = self.user
        self.room.save()
        response = self.client.post(
            f'/api/v1/rooms/{self.room.id}/leave/',
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        self.room.refresh_from_db()
        self.assertEqual(None, self.room.user)

    # todo(KrysiaEK): test host wychodzi, user zostaje hostem

    # todo(KrysiaEK): host wychodzi, ale nie było usera, room nieaktywny

    def test_start_game(self):
        """Test checking game start.

        Test simulates creating room, joining user to room, pressing start game by user and later by host. Then game is
        created."""

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
        """Test checking pressing start by second user after 10 seconds.

        Game isn't created. Players can press start again.
        """

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

    # todo(KrysiaEK): test gdy 'start' naciska ta sama osoba
