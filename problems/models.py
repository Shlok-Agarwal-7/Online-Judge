from django.contrib.auth.models import User
from django.db import models

# Create your models here.


class ProblemTag(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.name}"


class Problem(models.Model):

    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    question = models.TextField()
    difficulty = models.CharField(
        max_length=20,
        choices=[
            ("Easy", "Easy"),
            ("Medium", "Medium"),
            ("Hard", "Hard"),
        ],
    )
    tags = models.ManyToManyField(ProblemTag, related_name="problems",blank = True)
    sample_input = models.CharField(max_length = 100)
    sample_output = models.CharField(max_length = 100)

    def __str__(self):
        return f"{self.title} - {self.id}"


class TestCase(models.Model):

    problem = models.ForeignKey(
        Problem, on_delete=models.CASCADE, related_name="testcases"
    )
    input = models.TextField()
    output = models.TextField()

    def __str__(self):
        return f"{self.problem.title} - {self.id}"


class Submission(models.Model):
    code = models.TextField()
    language = models.CharField(
        max_length=50, choices=[("py", "Python"), ("cpp", "C++"), ("java", "Java")]
    )
    verdict = models.CharField(max_length=50)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="submissions")
    problem = models.ForeignKey(
        Problem, on_delete=models.CASCADE, related_name="submissions"
    )

    def __str__(self):
        return f"{self.problem.title} - {self.user.username}"
