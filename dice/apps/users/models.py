from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Model representing dice's user."""

    score = models.IntegerField(default=1200)
