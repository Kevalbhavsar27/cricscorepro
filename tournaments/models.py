from django.db import models
from django.contrib.auth.models import User


class Tournament(models.Model):
    MATCH_TYPE_CHOICES = [
        ('T1', 'T1 - 1 Over'),
        ('T2', 'T2 - 2 Overs'),
        ('T5', 'T5 - 5 Overs'),
        ('T10', 'T10 - 10 Overs'),
        ('T20', 'T20 - 20 Overs'),
        ('ODI', 'ODI - 50 Overs'),
        ('TEST', 'Test Match'),
        ('CUSTOM', 'Custom Overs'),
    ]

    STATUS_CHOICES = [
        ('Upcoming', 'Upcoming'),
        ('Running', 'Running'),
        ('Completed', 'Completed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=150)
    location = models.CharField(max_length=150)

    match_type = models.CharField(max_length=20, choices=MATCH_TYPE_CHOICES)

    custom_overs = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Only required when match type is Custom"
    )

    start_date = models.DateField()
    end_date = models.DateField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Upcoming'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def get_overs(self):
        overs_map = {
            'T1': 1,
            'T2': 2,
            'T5': 5,
            'T10': 10,
            'T20': 20,
            'ODI': 50,
        }

        if self.match_type == 'CUSTOM':
            return self.custom_overs

        if self.match_type == 'TEST':
            return None

        return overs_map.get(self.match_type)

    def __str__(self):
        return self.name