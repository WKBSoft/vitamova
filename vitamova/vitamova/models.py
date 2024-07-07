# vitamova/models.py

from django.contrib.auth.models import User
from django.db import models

class Status(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='status')
    points = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.user.username} - {self.points} points'
