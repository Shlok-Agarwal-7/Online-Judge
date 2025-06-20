from django.db import models
from django.contrib.auth.models import User 

# Create your models here.

class Profile(models.Model):
    points = models.IntegerField(default = 100)
    role = models.CharField(default = "Student") 
    user = models.OneToOneField(User,on_delete = models.CASCADE,related_name = "profile")

    def __str__(self):
        return self.user.username
    