from rest_framework import serializers

from dice.apps.games.models import Room, Game


class GameSerializer(serializers.ModelSerializer):
    """Serializer of ``Game`` model instances."""

    class Meta:
        model = Game
        fields = ['id']


class RoomSerializer(serializers.ModelSerializer):
    """Serializer of ``Room`` model instances."""

    host_name = serializers.ReadOnlyField(source='host.username')
    user_name = serializers.ReadOnlyField(source='user.username')
    game_id = serializers.ReadOnlyField(source='game.id')

    class Meta:
        model = Room
        fields = ['id', 'host', 'host_name', 'user', 'user_name', 'game_id', 'time_of_creation']
