from django.contrib import admin
from .models import Player


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'team',
        'role',
        'batting_style',
        'bowling_style',
        'user'
    )

    search_fields = ('name', 'team__name')
    list_filter = ('role', 'team')