import random

from django.db import models


class Room(models.Model):
    host = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name="room_host")
    user = models.ForeignKey('users.User', on_delete=models.SET_NULL, blank=True, null=True,
                             related_name="second_player")


class Game(models.Model):
    room = models.OneToOneField(Room, on_delete=models.CASCADE)
    # jak że w rround będzie one to one to można użyć game.round żeby dostać round
    # która runda (tak jak turn w Round)
    # on to many do Pole, a jak się tworzy game to automatycznie stworzyć 2 pola dla jednego gracza
    # czyja kolej, mogę wyznaczyć to po numerze rundy (% to reszta z dzielenia)

# klejny model o nazwie POLE, pole ma swój typ (np. strit, choice field), info czu zotsał wybrany czy nie, a jak został
# wybrany
# to ile ma pkt (mogę usatwić jako null i jęlsi nie jest nullem to że zotał wybrany już, nawet jak ma 0 LUB
# BooleanField)


class Dice(models.Model):
    value = models.PositiveSmallIntegerField()
    chosen = models.BooleanField(default=False)

    @classmethod
    def create(cls):
        dice = cls(value=random.randint(1, 6))
        dice.save()
        return dice

class Round(models.Model):
    TURN_CHOICES = (
        (1, 1),
        (2, 2),
        (3, 3),
    )
    game = models.OneToOneField(Game, on_delete=models.CASCADE)
    # user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    dice1 = models.OneToOneField(Dice, on_delete=models.CASCADE, related_name='round_as_first_dice', default=Dice.create)
    dice2 = models.OneToOneField(Dice, on_delete=models.CASCADE, related_name='round_as_second_dice', default=Dice.create)
    dice3 = models.OneToOneField(Dice, on_delete=models.CASCADE, related_name='round_as_third_dice', default=Dice.create)
    dice4 = models.OneToOneField(Dice, on_delete=models.CASCADE, related_name='round_as_fourth_dice', default=Dice.create)
    dice5 = models.OneToOneField(Dice, on_delete=models.CASCADE, related_name='round_as_fifth_dice', default=Dice.create)
    turn = models.PositiveSmallIntegerField(choices=TURN_CHOICES, default=1)
    # figure = models.CharField(blank=True, null=True, max_length=15)
