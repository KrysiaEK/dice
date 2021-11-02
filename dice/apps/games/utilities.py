import random


def roll_dices():
    dices = []
    for i in range(5):
        dices.append(random.randint(1, 6))
    return dices


class Figures:
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    TRIO = 7
    QUATRO = 8
    FULL_HOUSE = 25
    SMALL_STRAIGHT = 30
    LARGE_STRAIGHT = 40
    YATZY = 50
    CHANCE = 100

    Choices = (
        (ONE, '1'),
        (TWO, '2'),
        (THREE, '3'),
        (FOUR, '4'),
        (FIVE, '5'),
        (SIX, '6'),
        (TRIO, '3x'),
        (QUATRO, '4x'),
        (FULL_HOUSE, "3+2x"),
        (SMALL_STRAIGHT, 'Small straight'),
        (LARGE_STRAIGHT, 'Large straight'),
        (YATZY, 'Yatzy'),
        (CHANCE, 'Chance')
    )

    UPPER_FIGURES = (ONE, TWO, THREE, FOUR, FIVE, SIX)
