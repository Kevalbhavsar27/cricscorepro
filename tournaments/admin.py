from django.contrib import admin
from .models import Tournament


@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'user',
        'match_type',
        'custom_overs',
        'location',
        'status',
        'start_date',
        'end_date',
    )
    search_fields = ('name', 'location', 'user__username')
    list_filter = ('match_type', 'status')