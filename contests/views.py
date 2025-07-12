from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

from problems.helpers import submit_code, update_user_score_if_first_ac
from problems.models import Problem, Submission
from problems.permissions import isMentor
from problems.serializers import SubmissionSerializer

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

    permission_classes = [isMentor]

    serializer_class = ContestSerializer
    queryset = Contest.objects.all()


class AddExistingProblemView(generics.CreateAPIView):
    serializer_class = AddExistingProblemSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        contest = get_object_or_404(Contest, id=self.kwargs["contest_id"])
        context["contest"] = contest
        return context


class ContestMakeSubmissionView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = SubmissionSerializer(data=request.data)
        if serializer.is_valid():
            code = serializer.validated_data["code"]
            language = serializer.validated_data["language"]
            problem_id = serializer.validated_data["problem_id"]
            user = request.user

            contest = get_object_or_404(Contest, id=self.kwargs.get("contest_id"))

            if not contest.is_running:
                return Response(
                    {
                        "detail": "Contest has ended",
                    },
                    status=403,
                )

            problem = get_object_or_404(Problem, id=problem_id)

            result = submit_code(language, code, problem_id)
            verdict = result.get("verdict")

            print("The verdcit was", verdict)

            if verdict == "Accepted":
                update_user_score_if_first_ac(user.id, problem.id)

            submission = Submission.objects.create(
                code=code,
                language=language,
                verdict=verdict,
                problem=problem,
                user=user,
            )

            contest_submission = ContestSubmission.objects.create(
                submission=submission, submission_time=timezone.now(), contest=contest
            )

            response_serializer = SubmissionSerializer(submission)
            return Response(response_serializer.data, status=201)

        return Response(serializer.errors, status=400)


class getContestLeaderboardView(APIView):
    def get(self, request, *args, **kwargs):
        contest_id = self.kwargs.get("contest_id")
        contest = get_object_or_404(Contest, id=contest_id)
