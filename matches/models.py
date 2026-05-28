from django.db import models
from django.contrib.auth.models import User
from tournaments.models import Tournament
from teams.models import Team


class Match(models.Model):

    STATUS_CHOICES = [
        ('Upcoming', 'Upcoming'),
        ('Live', 'Live'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]

    TOSS_DECISION_CHOICES = [
        ('Bat', 'Bat'),
        ('Bowl', 'Bowl'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    tournament = models.ForeignKey(
        Tournament,
        on_delete=models.CASCADE,
        related_name='matches'
    )

    team_a = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name='team_a_matches'
    )

    team_b = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name='team_b_matches'
    )

    venue = models.CharField(max_length=150)
    match_date = models.DateTimeField()

    toss_winner = models.ForeignKey(
        Team,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='toss_wins'
    )

    toss_decision = models.CharField(
        max_length=10,
        choices=TOSS_DECISION_CHOICES,
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Upcoming'
    )

    winner = models.ForeignKey(
        Team,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='match_wins'
    )

    result_text = models.CharField(max_length=255, blank=True, null=True)
    qr_code = models.ImageField(upload_to='match_qr_codes/', blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def match_title(self):
        return f"{self.team_a.short_name} vs {self.team_b.short_name}"

    def __str__(self):
        return self.match_title()