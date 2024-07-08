# accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    points = models.IntegerField(default=0)
    # add additional fields in here

    def __str__(self):
        return self.username