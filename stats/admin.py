from django.contrib import admin
from .models import PlayerStats


@admin.register(PlayerStats)
class PlayerStatsAdmin(admin.ModelAdmin):
    list_display = (
        'player',
        'matches',
        'runs',
        'wickets',
        'highest_score',
    )

    search_fields = ('player__name',)