from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics

from .models import Contest, ContestProblem, ContestSubmission
from .serializers import (
    AddExistingProblemSerializer,
    ContestProblemSerializer,
    ContestSerializer,
    ContestSubmissionSerializer,
)

# Create your views here.


class PreviousContestListView(generics.ListAPIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = ContestSerializer

    def get_queryset(self):
        return Contest.objects.filter(end_time__lt=timezone.now())


class UpcomingContestListView(generics.ListAPIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = ContestSerializer

    def get_queryset(self):
        return Contest.objects.filter(start_time__gt=timezone.now()).order_by(
            "start_time"
        )


class RunningContestListView(generics.ListAPIView):

    authentication_classes = []
    permission_classes = []

    serializer_class = ContestSerializer

    def get_queryset(self):
        return Contest.objects.filter(
            end_time__gte=timezone.now(), start_time__lte=timezone.now()
        )


class ContestProblemListView(generics.ListAPIView):
    authentication_classes = []
    permission_classes = []

    def get_queryset(self):
        contest_id = self.kwargs.get("contest_id")
        return (
            ContestProblem.objects.filter(contest_id=contest_id)
            .select_related("problem")
            .order_by("order")
        )

    serializer_class = ContestProblemSerializer


class ContestSubmissionsView(generics.ListAPIView):
    def get_queryset(self):
        contest_id = self.kwargs.get("contest_id")
        user = self.request.user
        return ContestSubmission.objects.filter(
            contest_id=contest_id, submission_user=user
        ).select_related("submission")

    serializer_class = ContestSubmissionSerializer


class ContestDetialView(generics.RetrieveAPIView):
    authentication_classes = []
    permission_classes = []

    queryset = Contest
    serializer_class = ContestSerializer


class ContestCreateView(generics.CreateAPIView):

    serializer_class = ContestSerializer
    queryset = Contest.objects.all()


class AddExistingProblemView(generics.CreateAPIView):
    serializer_class = AddExistingProblemSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        contest = get_object_or_404(Contest, id=self.kwargs["contest_id"])
        context["contest"] = contest
        return context