from django.urls import path

from .views import (
    ContestProblemListView,
    ContestSubmissionsView,
    PreviousContestListView,
    RunningContestListView,
    UpcomingContestListView,
    ContestDetialView,
    ContestCreateView,
    AddExistingProblemView
)

urlpatterns = [
    path("contests/upcoming", UpcomingContestListView.as_view(), name="upcoming_contest"),
    path("contests/previous", PreviousContestListView.as_view(), name="previous_contest"),
    path("contests/running", RunningContestListView.as_view(), name="running_contest"),
    path("contests/<int:contest_id>/problems",ContestProblemListView.as_view(),name="contest_problems"),
    path("contests/<int:pk>",ContestDetialView.as_view(),name = "contest-details"),
    path("contests/create",ContestCreateView.as_view(),name = "create-contest"),
    path("contests/<int:contest_id>/addproblem",AddExistingProblemView.as_view(),name = "add-problem-contest")
]
