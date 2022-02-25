from django.contrib import admin

from dice.apps.games.models import Room, Game


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    pass


@admin.register(Game)
class RoomAdmin(admin.ModelAdmin):
    pass
