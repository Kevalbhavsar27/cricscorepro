from django.db import models
from django.contrib.auth.models import User
from tournaments.models import Tournament


class Team(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='teams')

    name = models.CharField(max_length=150)
    short_name = models.CharField(max_length=20)
    city = models.CharField(max_length=100, blank=True, null=True)
    captain_name = models.CharField(max_length=150, blank=True, null=True)
    coach_name = models.CharField(max_length=150, blank=True, null=True)
    logo = models.ImageField(upload_to='team_logos/', blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name