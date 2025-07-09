from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

from problems.models import Problem, Submission


# Create your models here.
class Contest(models.Model):
    title = models.CharField(max_length=50)
    description = models.TextField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"Contest {self.id}"

    @property
    def is_completed(self):
        return timezone.now() > self.end_time

    @property
    def is_upcoming(self):
        return timezone.now() < self.start_time

    @property
    def is_running(self):
        now = timezone.now()
        return self.start_time <= now <= self.end_time


class ContestProblem(models.Model):
    contest = models.ForeignKey(
        Contest, on_delete=models.CASCADE, related_name="problems"
    )
    problem = models.OneToOneField(Problem, on_delete=models.CASCADE)
    order = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.contest.title} - {self.order}"


class ContestSubmission(models.Model):
    contest = models.ForeignKey(
        Contest, on_delete=models.CASCADE, related_name="submissions"
    )
    submission = models.OneToOneField(Submission, on_delete=models.CASCADE)
    submission_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.id}"
