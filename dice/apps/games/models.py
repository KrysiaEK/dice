from django.db import models
from django.db.models import Sum, F
from django.utils import timezone

from dice.apps.rounds.models import Round, Dice


class Room(models.Model):
    host = models.ForeignKey('users.User', on_delete=models.CASCADE, blank=True, null=True, related_name="room_host")
    user = models.ForeignKey('users.User', on_delete=models.SET_NULL, blank=True, null=True,
                             related_name="second_player")
    active = models.BooleanField(default=True)
    time_of_creation = models.DateTimeField(default=timezone.now())
    start_game = models.DateTimeField(null=True, blank=True)
    who_started_game = models.ForeignKey('users.User', on_delete=models.SET_NULL, blank=True, null=True)


class Game(models.Model):
    room = models.OneToOneField(Room, on_delete=models.CASCADE)

    def count_final_points(self):
        final_points = self.round_set.values('user').annotate(points_sum=Sum(F('points') + F('extra_points')))
        try:
            host_points = final_points.get(user=self.room.host)['points_sum']
        except Round.DoesNotExist:
            host_points = 0
        try:
            user_points = final_points.get(user=self.room.user)['points_sum']
        except Round.DoesNotExist:
            user_points = 0
        return host_points, user_points

    def update_players_ranking(self):
        host_points, user_points = self.count_final_points()
        start_host_score = self.room.host.score
        start_user_score = self.room.user.score
        expected_host_score = (10 ** (start_host_score / 400)) / (
                    (10 ** (start_host_score / 400)) + (10 ** (start_user_score / 400)))
        expected_user_score = (10 ** (start_user_score / 400)) / (
                    (10 ** (start_user_score / 400)) + (10 ** (start_host_score / 400)))
        if host_points > user_points:
            host_score = 1
            user_score = 0
        elif user_points > host_points:
            host_score = 0
            user_score = 1
        else:
            host_score, user_score = 0.5, 0.5
        self.room.host.score = int(start_host_score + 20 * (host_score - expected_host_score))
        self.room.user.score = int(start_user_score + 20 * (user_score - expected_user_score))
        self.room.host.save()
        self.room.user.save()
        return self.room.host.score, self.room.user.score
