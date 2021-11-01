import random

from django.db import models

from dice.apps.games.utilities import Figures


class Room(models.Model):
    host = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name="room_host")
    user = models.ForeignKey('users.User', on_delete=models.SET_NULL, blank=True, null=True,
                             related_name="second_player")


class Game(models.Model):
    room = models.OneToOneField(Room, on_delete=models.CASCADE)


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

    def count_points(self):
        if self.figure in [Figures.ONE, Figures.TWO, Figures.THREE, Figures.FOUR, Figures.FIVE, Figures.SIX]:
            return self.dices.count(self.figure) * self.figure
        elif self.figure == Figures.TRIO:
            for i in range(1, 7):
                if self.dices.count(i) >= 3:
                    return sum(self.dices)
            return 0
        elif self.figure == Figures.QUATRO:
            for i in range(1, 7):
                if self.dices.count(i) >= 4:
                    return sum(self.dices)
        elif self.figure == Figures.FULL_HOUSE:
            for i in range(1, 7):
                for j in range(1, 7):
                    if self.dices.count(i) == 3 and self.dices.count(j) == 2:
                        return 25
            return 0
        elif self.figure == Figures.SMALL_STRAIGHT:
            for i in range(1, 4):
                for x in range(i, i + 4):
                    if x not in self.dices:
                        break
                else:
                    return 30
            return 0
        elif self.figure == Figures.LARGE_STRAIGHT:
            for i in range(1, 3):
                for x in range(i, i + 5):
                    if x not in self.dices:
                        break
                else:
                    return 40
            return 0
        elif self.figure == Figures.YATZY:
            for i in range(1, 7):
                if self.dices.count(i) == 5:
                    return 50
            return 0
        elif self.figure == Figures.CHANCE:
            return sum(self.dices)
        raise Exception('niepoprawna figura')
