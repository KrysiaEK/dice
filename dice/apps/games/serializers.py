import random

from rest_framework import serializers
from dice.apps.games.models import Room, Game, Dice, Round
from dice.apps.users.serializers import UserSerializer


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
    user = UserSerializer(required=False)
    turn = serializers.IntegerField(read_only=True)
    game = serializers.PrimaryKeyRelatedField(required=True, queryset=Game.objects.all())
    points = serializers.IntegerField(read_only=True)

    class Meta:
        model = Round
        fields = ['dice1', 'dice2', 'dice3', 'dice4', 'dice5', 'turn', 'user', 'game', 'points']

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
            'user': self.context.get('request').user,
            'game_id': validated_data.get('game').id,
        }
        return super().create(validated_data)
