import random
from django.db import models
from dice.apps.games.utilities import Figures
from django.db.models import Sum, F
from django.utils import timezone


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


class Dice(models.Model):
    value = models.PositiveSmallIntegerField()

    @classmethod
    def create(cls):
        dice = cls(value=random.randint(1, 6))
        dice.save()
        return dice

    def reroll(self):
        self.value = random.randint(1, 6)
        self.save(update_fields=['value'])


class Round(models.Model):
    TURN_CHOICES = (
        (1, 1),
        (2, 2),
        (3, 3),
    )
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    dice1 = models.OneToOneField(Dice, on_delete=models.CASCADE, related_name='round_as_first_dice',
                                 default=Dice.create)
    dice2 = models.OneToOneField(Dice, on_delete=models.CASCADE, related_name='round_as_second_dice',
                                 default=Dice.create)
    dice3 = models.OneToOneField(Dice, on_delete=models.CASCADE, related_name='round_as_third_dice',
                                 default=Dice.create)
    dice4 = models.OneToOneField(Dice, on_delete=models.CASCADE, related_name='round_as_fourth_dice',
                                 default=Dice.create)
    dice5 = models.OneToOneField(Dice, on_delete=models.CASCADE, related_name='round_as_fifth_dice',
                                 default=Dice.create)
    turn = models.PositiveSmallIntegerField(choices=TURN_CHOICES, default=1)
    figure = models.PositiveIntegerField(blank=True, null=True, choices=Figures.Choices)
    points = models.PositiveIntegerField(blank=True, null=True)
    extra_points = models.PositiveIntegerField(default=0)

    @property
    def dices(self):
        return [self.dice1.value, self.dice2.value, self.dice3.value, self.dice4.value, self.dice5.value]

    def set_dices(self, dice1, dice2, dice3, dice4, dice5):
        self.dice1.value = dice1
        self.dice2.value = dice2
        self.dice3.value = dice3
        self.dice4.value = dice4
        self.dice5.value = dice5
        self.dice1.save()
        self.dice2.save()
        self.dice3.save()
        self.dice4.save()
        self.dice5.save()

    def count_points(self, figure=None):
        if figure is None:
            figure = self.figure
        if figure in Figures.UPPER_FIGURES:
            return self.dices.count(figure) * figure
        elif figure == Figures.TRIO:
            for i in range(1, 7):
                if self.dices.count(i) >= 3:
                    return sum(self.dices)
            return 0
        elif figure == Figures.QUATRO:
            for i in range(1, 7):
                if self.dices.count(i) >= 4:
                    return sum(self.dices)
            return 0
        elif figure == Figures.FULL_HOUSE:
            for i in range(1, 7):
                for j in range(1, 7):
                    if self.dices.count(i) == 3 and self.dices.count(j) == 2:
                        return 25
            return 0
        elif figure == Figures.SMALL_STRAIGHT:
            for i in range(1, 4):
                for x in range(i, i + 4):
                    if x not in self.dices:
                        break
                else:
                    return 30
            return 0
        elif figure == Figures.LARGE_STRAIGHT:
            for i in range(1, 3):
                for x in range(i, i + 5):
                    if x not in self.dices:
                        break
                else:
                    return 40
            return 0
        elif figure == Figures.YATZY:
            if self.dices.count(self.dice1.value) == 5:
                return 50
            return 0
        elif figure == Figures.CHANCE:
            return sum(self.dices)
        raise Exception('niepoprawna figura')

    def count_extra_points(self):
        return self.count_extra_points_yatzy() + self.count_extra_points_63()

    def count_extra_points_yatzy(self):
        super_round = Round.objects.filter(game=self.game, user=self.user, figure=Figures.YATZY, points=50)
        if not super_round.exists():
            return 0
        if not self.figure or self.dices.count(self.dice1.value) != 5:
            return 0
        return 50

    def count_extra_points_63(self):
        upper_figures = Round.objects.filter(game=self.game, user=self.user,
                                             figure__in=Figures.UPPER_FIGURES).aggregate(sum_points=Sum("points"))
        upper_figures_points = upper_figures['sum_points']
        if upper_figures_points is None:
            return 0
        if upper_figures_points >= 63 or upper_figures_points + self.count_points() < 63:
            return 0
        return 35
