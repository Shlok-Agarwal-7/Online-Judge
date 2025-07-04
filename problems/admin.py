from django.contrib import admin

from .models import Problem, ProblemTag, Submission, TestCase

# Register your models here.
admin.site.register(Problem)
admin.site.register(TestCase)
admin.site.register(Submission)
admin.site.register(ProblemTag)
