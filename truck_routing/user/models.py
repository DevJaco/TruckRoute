from django.contrib.auth.models import AbstractUser
from django.db import models

# Just creating a custom user in case we need down the line.
class User(AbstractUser):
    pass