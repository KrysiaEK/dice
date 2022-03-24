from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Model representing dice's user."""

    score = models.IntegerField(default=1200)
