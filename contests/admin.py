from django.contrib import admin

from .models import Contest, ContestProblem, ContestSubmission

# Register your models here.

admin.site.register(Contest)
admin.site.register(ContestProblem)
admin.site.register(ContestSubmission)
