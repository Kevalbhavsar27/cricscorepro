from django.db import models
from django.contrib.auth.models import User
from players.models import Player


class PlayerStats(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    player = models.OneToOneField(
        Player,
        on_delete=models.CASCADE,
        related_name='stats'
    )

    matches = models.PositiveIntegerField(default=0)

    innings = models.PositiveIntegerField(default=0)

    runs = models.PositiveIntegerField(default=0)
    balls = models.PositiveIntegerField(default=0)

    fours = models.PositiveIntegerField(default=0)
    sixes = models.PositiveIntegerField(default=0)

    highest_score = models.PositiveIntegerField(default=0)

    wickets = models.PositiveIntegerField(default=0)

    bowling_balls = models.PositiveIntegerField(default=0)
    bowling_runs = models.PositiveIntegerField(default=0)

    best_bowling_wickets = models.PositiveIntegerField(default=0)
    best_bowling_runs = models.PositiveIntegerField(default=0)

    catches = models.PositiveIntegerField(default=0)
    run_outs = models.PositiveIntegerField(default=0)

    def strike_rate(self):
        if self.balls == 0:
            return 0
        return round((self.runs / self.balls) * 100, 2)

    def economy(self):
        if self.bowling_balls == 0:
            return 0
        return round((self.bowling_runs / self.bowling_balls) * 6, 2)

    def batting_average(self):
        if self.innings == 0:
            return 0
        return round(self.runs / self.innings, 2)

    def bowling_average(self):
        if self.wickets == 0:
            return 0
        return round(self.bowling_runs / self.wickets, 2)

    def overs_bowled(self):
        overs = self.bowling_balls // 6
        balls = self.bowling_balls % 6
        return f"{overs}.{balls}"

    def __str__(self):
        return self.player.name