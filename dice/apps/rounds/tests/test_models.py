from unittest import TestCase

from dice.apps.rounds.utilities import Figures
from dice.apps.rounds.tests.factories import RoundFactory


# todo(KrysiaEK): Dice Tests:
#  1. create
#  2. reroll

# todo(KrysiaEK): Round Test:
#  1. count_extra_points_yatzy
#  2. count_extra_points_63
#  3. count_extra_points


class NonAPIRoundTestCase(TestCase):
    """Ensure points are properly calculated for each figure."""

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
