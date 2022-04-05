from django.contrib import admin

from dice.apps.games.models import Game, Room


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    pass


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    pass
