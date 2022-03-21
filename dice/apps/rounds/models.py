import random
from django.db import models
from django.db.models import Sum

from dice.apps.rounds.utilities import Figures


class Dice(models.Model):
    """Dice model."""

    value = models.PositiveSmallIntegerField()

    @classmethod
    def create(cls):
        """Function to create dice."""

        dice = cls(value=random.randint(1, 6))
        dice.save()
        return dice

    def reroll(self):
        """Function to roll dice again and set new value."""

        self.value = random.randint(1, 6)
        self.save(update_fields=['value'])


class Round(models.Model):
    """Round model."""

    TURN_CHOICES = (
        (1, 1),
        (2, 2),
        (3, 3),
    )
    game = models.ForeignKey('games.Game', on_delete=models.CASCADE)
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
        """Function to save dices' values."""

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
        """Function to count points for individual figure based on dices' values."""

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
        raise Exception('Niepoprawna figura')

    def count_extra_points(self):
        """Function to add up extra points gotten by another yatzy and by getting minimum 63 points in upper figures."""

        return self.count_extra_points_yatzy() + self.count_extra_points_63()

    def count_extra_points_yatzy(self):
        """Function to add up points gotten by throwing more than one yatzy.

        For every yatzy player gets 50 points."""

        super_round = Round.objects.filter(game=self.game, user=self.user, figure=Figures.YATZY, points=50)
        if not super_round.exists():
            return 0
        if not self.figure or self.dices.count(self.dice1.value) != 5:
            return 0
        return 50

    def count_extra_points_63(self):
        """Function to check if player have 63 or more points in upper figures (1, 2, 3, 4, 5, 6).

        Player who got at least 63 points gets another 35 points."""

        upper_figures = Round.objects.filter(game=self.game, user=self.user,
                                             figure__in=Figures.UPPER_FIGURES).aggregate(sum_points=Sum("points"))
        upper_figures_points = upper_figures['sum_points']
        if upper_figures_points is None:
            return 0
        if upper_figures_points >= 63 or upper_figures_points + self.count_points() < 63:
            return 0
        return 35
