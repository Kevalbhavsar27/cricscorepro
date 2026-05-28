from django.db import models
from django.contrib.auth.models import User
from teams.models import Team


class Player(models.Model):

    ROLE_CHOICES = [
        ('Batsman', 'Batsman'),
        ('Bowler', 'Bowler'),
        ('All Rounder', 'All Rounder'),
        ('Wicket Keeper', 'Wicket Keeper'),
    ]

    BATTING_STYLE_CHOICES = [
        ('Right Hand Bat', 'Right Hand Bat'),
        ('Left Hand Bat', 'Left Hand Bat'),
    ]

    BOWLING_STYLE_CHOICES = [
        ('Right Arm Fast', 'Right Arm Fast'),
        ('Left Arm Fast', 'Left Arm Fast'),
        ('Right Arm Spin', 'Right Arm Spin'),
        ('Left Arm Spin', 'Left Arm Spin'),
        ('None', 'None'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name='players'
    )

    name = models.CharField(max_length=150)

    role = models.CharField(
        max_length=30,
        choices=ROLE_CHOICES
    )

    batting_style = models.CharField(
        max_length=50,
        choices=BATTING_STYLE_CHOICES
    )

    bowling_style = models.CharField(
        max_length=50,
        choices=BOWLING_STYLE_CHOICES
    )

    jersey_number = models.PositiveIntegerField(
        blank=True,
        null=True
    )

    age = models.PositiveIntegerField(
        blank=True,
        null=True
    )

    image = models.ImageField(
        upload_to='player_images/',
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name