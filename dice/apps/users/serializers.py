from rest_framework import serializers
from django.contrib.auth.hashers import make_password

from dice.apps.users.models import User


class UserSerializer(serializers.ModelSerializer):
    score = serializers.IntegerField(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'score']

    password = serializers.CharField(
        write_only=True,
        required=True,
        help_text='Leave empty if no change needed'
    )

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data.get('password'))
        return super().create(validated_data)
