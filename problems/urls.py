from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from problems import views

urlpatterns = [
    path("problems/", views.ProblemListView.as_view()),
    path("problems/<int:pk>/", views.ProblemDetialView.as_view()),
    path("problems/create", views.ProblemCreateView.as_view()),
    path("problems/<int:pk>/delete", views.ProblemDeleteView.as_view()),
    path("problems/<int:pk>/update", views.ProblemUpdateView.as_view()),
    path("execute", views.RunCodeView.as_view()),
    path("submit", views.SubmitCodeView.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
