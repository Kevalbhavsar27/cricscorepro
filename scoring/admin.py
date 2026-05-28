from django.contrib import admin
from .models import Innings, BallByBall


@admin.register(Innings)
class InningsAdmin(admin.ModelAdmin):
    list_display = (
        'match',
        'innings_number',
        'batting_team',
        'bowling_team',
        'runs',
        'wickets',
        'legal_balls',
        'is_completed',
        'user',
    )


@admin.register(BallByBall)
class BallByBallAdmin(admin.ModelAdmin):
    list_display = (
        'innings',
        'over_number',
        'ball_number',
        'batsman',
        'bowler',
        'runs',
        'extra_type',
        'extra_runs',
        'is_wicket',
        'is_legal_ball',
    )