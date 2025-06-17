from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from problems import views


urlpatterns = [
    path("problems/",views.ProblemListView.as_view()),
    path("problems/<int:pk>/",views.ProblemDetialView.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)