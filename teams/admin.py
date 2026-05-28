from django.contrib import admin
from .models import Team


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'short_name', 'tournament', 'user', 'city', 'captain_name')
    search_fields = ('name', 'short_name', 'city', 'captain_name', 'user__username')
    list_filter = ('tournament',)