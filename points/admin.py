from django.contrib import admin
from .models import PointsTable


@admin.register(PointsTable)
class PointsTableAdmin(admin.ModelAdmin):
    list_display = (
        'team',
        'tournament',
        'matches',
        'wins',
        'losses',
        'ties',
        'points',
        'net_run_rate',
        'user',
    )
    list_filter = ('tournament',)
    search_fields = ('team__name', 'tournament__name', 'user__username')