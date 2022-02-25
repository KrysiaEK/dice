from django.contrib import admin

from dice.apps.users.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
	pass
