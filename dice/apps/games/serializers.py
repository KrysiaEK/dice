import random

from rest_framework import serializers
from dice.apps.games.models import Room, Game, Dice, Round


class GameSerializer(serializers.ModelSerializer):

    class Meta:
        model = Game
        fields = ['id']


class RoomSerializer(serializers.ModelSerializer):
    game = GameSerializer(read_only=True)

    class Meta:
        model = Room
        fields = ['id', 'host', 'user', 'game']


class DiceSerializer(serializers.ModelSerializer):
    value = serializers.IntegerField(required=False)

    class Meta:
        model = Dice
        fields = ['id', 'value', 'chosen']


class RoundSerializer(serializers.ModelSerializer):
    dice1 = DiceSerializer(required=False)
    dice2 = DiceSerializer(required=False)
    dice3 = DiceSerializer(required=False)
    dice4 = DiceSerializer(required=False)
    dice5 = DiceSerializer(required=False)
    turn = serializers.IntegerField(read_only=True)

    class Meta:
        model = Round
        fields = ['dice1', 'dice2', 'dice3', 'dice4', 'dice5', 'turn']

    def create(self, validated_data):
        dices = []
        for i in range(5):
            dice = Dice.objects.create(value=random.randint(1, 6))
            dices.append(dice)
        validated_data = {
            'dice1_id': dices[0].id,
            'dice2_id': dices[1].id,
            'dice3_id': dices[2].id,
            'dice4_id': dices[3].id,
            'dice5_id': dices[4].id,
        }
        return super().create(validated_data)
