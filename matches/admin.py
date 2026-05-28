from django.contrib import admin
from .models import Match


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = (
        'match_title',
        'tournament',
        'team_a',
        'team_b',
        'venue',
        'match_date',
        'status',
        'winner',
        'user',
    )

    search_fields = (
        'team_a__name',
        'team_b__name',
        'venue',
        'tournament__name',
        'user__username',
    )

    list_filter = ('status', 'tournament')