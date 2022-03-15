from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from datetime import timedelta

from dice.apps.users.tests.factories import UserFactory
from dice.apps.games.tests.factories import RoomFactory, GameFactory
from dice.apps.games.models import Room


class RoomTestCase(APITestCase):
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

    # todo (KrysiaEK): TEST LIST VIEW?
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

    def test_join_room(self):
        # todo (KrysiaEK): sprawdzić czy status joined room
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

    # todo(KrysiaEK): host chce dołączyć jeszcze raz, i 403

    def test_leave_room_by_user(self):
        # todo(KrysiaEK): spr czy status 'you left the room'
        # self.room.refresh_from_db() # dlaczego tutaj to nie jest potrzebne?
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

    def test_leave_room_by_user_not_in_room(self):
        response = self.client.post(
            f'/api/v1/rooms/{self.room.id}/leave/',
            format='json',
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json().get('detail'), 'You are not in this room.')

    def test_leave_room_after_game_start(self):
        GameFactory(room=self.room)
        response = self.client_host.post(
            f'/api/v1/rooms/{self.room.id}/leave/',
            format='json',
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json().get('detail'), 'Game already exists.')


    # todo(KrysiaEK): ktoś chce wyjść gdy gra już wystartowała

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

    # todo(KrysiaEK): test gdy 'start' naciska ta sama osoba

    def test_start_game_by_user_not_in_room(self):
        response = self.client.post(
            f'/api/v1/rooms/{self.room.id}/start/',
            format='json',
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json().get('detail'), 'You are not in this room.')

    def test_start_room_after_game_start(self):

        GameFactory(room=self.room)
        response = self.client_host.post(
            f'/api/v1/rooms/{self.room.id}/start/',
            format='json',
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json().get('detail'), 'Game already exists.')

    # todo(KrysiaEK): ktoś chce startować gdy nie ma jeszcze drugiego usera
