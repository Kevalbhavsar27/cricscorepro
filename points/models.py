from django.db import models
from django.contrib.auth.models import User
from tournaments.models import Tournament
from teams.models import Team


class PointsTable(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='points_table')
    team = models.ForeignKey(Team, on_delete=models.CASCADE)

    matches = models.PositiveIntegerField(default=0)
    wins = models.PositiveIntegerField(default=0)
    losses = models.PositiveIntegerField(default=0)
    ties = models.PositiveIntegerField(default=0)
    no_results = models.PositiveIntegerField(default=0)
    points = models.PositiveIntegerField(default=0)

    runs_for = models.PositiveIntegerField(default=0)
    balls_for = models.PositiveIntegerField(default=0)
    runs_against = models.PositiveIntegerField(default=0)
    balls_against = models.PositiveIntegerField(default=0)

    net_run_rate = models.FloatField(default=0.0)

    class Meta:
        unique_together = ('tournament', 'team')

    def calculate_nrr(self):
        if self.balls_for == 0 or self.balls_against == 0:
            self.net_run_rate = 0
        else:
            run_rate_for = (self.runs_for / self.balls_for) * 6
            run_rate_against = (self.runs_against / self.balls_against) * 6
            self.net_run_rate = round(run_rate_for - run_rate_against, 3)

    def __str__(self):
        return f"{self.team.name} - {self.tournament.name}"