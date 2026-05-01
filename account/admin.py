from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Profile

@admin.register(User)
class UserAdmin(UserAdmin):
	list_display = ["id", *UserAdmin.list_display]
	ordering = ("-date_joined", )

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
	pass