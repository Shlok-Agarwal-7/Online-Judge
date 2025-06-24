from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Problem(models.Model):
    
    created_by = models.ForeignKey(User,on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    question = models.TextField() 
    difficulty = models.CharField(max_length = 20,choices = [
        ('Easy', 'Easy'),
        ('Medium', 'Medium'),
        ('Hard', 'Hard'),
    ])

    def __str__(self):
        return f"{self.title} - {self.id}"



class TestCase(models.Model):
    
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE,related_name = 'testcases')
    input = models.TextField()
    output = models.TextField()

    def __str__(self):
        return f"{self.problem.title} - {self.id}" 
