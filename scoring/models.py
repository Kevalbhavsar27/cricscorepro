from django.db import models
from django.contrib.auth.models import User
from matches.models import Match
from teams.models import Team
from players.models import Player


class Innings(models.Model):
    INNINGS_CHOICES = [
        (1, '1st Innings'),
        (2, '2nd Innings'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='innings')
    innings_number = models.PositiveIntegerField(choices=INNINGS_CHOICES)

    batting_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='batting_innings')
    bowling_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='bowling_innings')

    runs = models.PositiveIntegerField(default=0)
    wickets = models.PositiveIntegerField(default=0)
    legal_balls = models.PositiveIntegerField(default=0)

    striker = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, blank=True, related_name='striker_innings')
    non_striker = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, blank=True, related_name='non_striker_innings')
    current_bowler = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, blank=True, related_name='bowler_innings')

    target = models.PositiveIntegerField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def overs_display(self):
        overs = self.legal_balls // 6
        balls = self.legal_balls % 6
        return f"{overs}.{balls}"

    def run_rate(self):
        if self.legal_balls == 0:
            return 0
        return round((self.runs / self.legal_balls) * 6, 2)

    def __str__(self):
        return f"{self.match} - Innings {self.innings_number}"


class BallByBall(models.Model):
    EXTRA_CHOICES = [
        ('None', 'None'),
        ('Wide', 'Wide'),
        ('No Ball', 'No Ball'),
        ('Bye', 'Bye'),
        ('Leg Bye', 'Leg Bye'),
    ]

    WICKET_CHOICES = [
        ('None', 'None'),
        ('Bowled', 'Bowled'),
        ('Caught', 'Caught'),
        ('LBW', 'LBW'),
        ('Run Out', 'Run Out'),
        ('Stumped', 'Stumped'),
        ('Hit Wicket', 'Hit Wicket'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    innings = models.ForeignKey(Innings, on_delete=models.CASCADE, related_name='balls')

    over_number = models.PositiveIntegerField()
    ball_number = models.PositiveIntegerField()

    batsman = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, related_name='balls_faced')
    bowler = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, related_name='balls_bowled')

    runs = models.PositiveIntegerField(default=0)
    extra_type = models.CharField(max_length=20, choices=EXTRA_CHOICES, default='None')
    extra_runs = models.PositiveIntegerField(default=0)

    is_wicket = models.BooleanField(default=False)
    wicket_type = models.CharField(max_length=20, choices=WICKET_CHOICES, default='None')
    out_player = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, blank=True, related_name='wickets_lost')

    is_legal_ball = models.BooleanField(default=True)
    commentary = models.CharField(max_length=255, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def total_runs(self):
        return self.runs + self.extra_runs

    def __str__(self):
        return f"{self.over_number}.{self.ball_number} - {self.total_runs()} runs"