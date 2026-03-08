from django.db import models
from django.contrib.auth.models import User

class GameSession(models.Model):

    INCIDENT_TYPES = [
        ('phishing','Phishing'),
        ('ransomware', 'Ransomware'),
        ('malware', 'Malware'),
        ('data_loss','Data Loss'),
        ('denial_of_service','DoS'),
    ]

    STATUSES = (
        ('in_progress', 'In Progress'),
        ('paused', 'Paused'),
        ('completed', 'Completed'), # when all questions are complete
        ('failed', 'Failed'), # fails if health reaches 0
        ('abandoned', 'Abandoned'), # user quits
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )

    incident_type = models.CharField(max_length = 50, choices = INCIDENT_TYPES)
    difficulty = models.IntegerField()

    score = models.IntegerField(default = 0)
    health = models.IntegerField(default = 100)

    status = models.charField(max_length = 50, choices = STATUSES, default = 'in_progress')

    def __str__(self):
        return f'Session {self.id} - {self.user.username}'

