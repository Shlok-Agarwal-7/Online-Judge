from django.contrib.auth.models import User
from django.db import models

# Create your models here.


class Profile(models.Model):
    points = models.IntegerField(default=100, db_index=True)
    role = models.CharField(default="Student")
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    rank = models.IntegerField(default=0, db_index=True)

    def __str__(self):
        return self.user.username
