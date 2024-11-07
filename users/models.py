from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    Class that represents a user account.
    """
    name = models.CharField(max_length=150)
    email = models.CharField(max_length=64, unique=True)
    username = None
    first_name = None
    last_name = None

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []