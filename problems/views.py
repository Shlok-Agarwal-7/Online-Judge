from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.views import APIView

from .helpers import get_ai_hint, run_code, submit_code, update_rank_on_point_increase
from .models import Problem, ProblemTag, Submission, TestCase
from .permissions import isMentor
from .serializers import (
    HintRequestSerializer,
    ProblemDetailSerializer,
    ProblemListSerializer,
    ProblemSerializer,
    ProblemTagSerializer,
    RunCodeSerializer,
    SubmissionSerializer,
)

# Create your views here.


class ProblemListView(generics.ListAPIView):

    authentication_classes = []
    permission_classes = []

    queryset = Problem.objects.all()
    serializer_class = ProblemListSerializer


class ProblemDetialView(generics.RetrieveAPIView):

    queryset = Problem.objects.all()
    serializer_class = ProblemDetailSerializer


class ProblemTagListAPIView(generics.ListAPIView):
    queryset = ProblemTag.objects.all()
    serializer_class = ProblemTagSerializer


class ProblemHintAPIView(APIView):

    def post(self, request):
        serializer = HintRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        title = serializer.validated_data["title"]
        question = serializer.validated_data["question"]

        hint = get_ai_hint(title, question)
        return Response({"problem": title, "hint": hint})


class ProblemCreateView(APIView):

    permission_classes = [isMentor]

    def post(self, request):
        serializer = ProblemSerializer(data=request.data, context={"request": request})

        if serializer.is_valid():
            data = serializer.save()
            return Response(data, status=201)

        return Response(serializer.errors, status=400)


class ProblemDeleteView(generics.DestroyAPIView):

    permission_classes = [isMentor]

    queryset = Problem.objects.all()
    serializer_class = ProblemSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        try:
            id = instance.id
            self.perform_destroy(instance)
            return Response({"detail": f"Destroyed Problem with id{id}"}, status=200)

        except Exception as e:
            return Response(
                {"detail": f"couldnt destroy due to server issues try later"},
                status=500,
            )


class ProblemUpdateView(generics.UpdateAPIView):

    permission_classes = [isMentor]

    queryset = Problem.objects.all()
    serializer_class = ProblemSerializer

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(
            data=request.data, instance=instance, partial=True
        )

        if serializer.is_valid():
            data = serializer.save()
            return Response(data, status=200)

        return Response(serializer.errors, status=400)


class RunCodeView(APIView):

    def post(self, request):
        serializer = RunCodeSerializer(data=request.data)
        if serializer.is_valid():
            code = serializer.validated_data["code"]
            language = serializer.validated_data["language"]
            input_data = serializer.validated_data["input_data"]

            out = run_code(language, code, input_data)

            # if err: return Response({"error": str(err)}, status=400)

            return Response({"output": str(out)}, status=200)

        else:
            return Response(serializer.errors, status=400)


class SubmitCodeView(APIView):

    def post(self, request):
        serializer = SubmissionSerializer(data=request.data)
        if serializer.is_valid():
            code = serializer.validated_data["code"]
            language = serializer.validated_data["language"]
            problem_id = serializer.validated_data["problem_id"]
            user = request.user

            problem = get_object_or_404(Problem, id=problem_id)

            result = submit_code(language, code, problem.id)
            verdict = result.get("verdict")

            if verdict == "Accepted":
                first_ac = not problem.submissions.filter(
                    verdict="Accepted", user=request.user
                ).exists()

                if first_ac:
                    old_points = user.profile.points
                    if problem.difficulty == "Hard":
                        earned = 100
                    elif problem.difficulty == "Medium":
                        earned = 50
                    elif problem.difficulty == "Easy":
                        earned = 25

                    user.profile.points += earned
                    user.profile.save()
                    update_rank_on_point_increase(
                        user.profile, old_points, user.profile.points
                    )

            submission = Submission.objects.create(
                code=code,
                language=language,
                verdict=verdict,
                problem=problem,
                user=user,
            )

            response_serializer = SubmissionSerializer(submission)

            return Response(response_serializer.data, status=201)

        return Response(serializer.errors, status=400)


class GetUserForProblemSubmissions(generics.ListAPIView):
    serializer_class = SubmissionSerializer

    def get_queryset(self):
        problem_id = self.request.query_params.get("problem")
        if not problem_id:
            return Submission.objects.none()

        return Submission.objects.filter(problem=problem_id, user=self.request.user)


class GetAllSubmissions(generics.ListAPIView):
    serializer_class = SubmissionSerializer

    def get_queryset(self):
        problem_id = self.request.query_params.get("problem")
        if not problem_id:
            return Submission, objects.none()

        return Submission.objects.filter(problem=problem_id)


class MySubmissions(generics.ListAPIView):
    serializer_class = SubmissionSerializer

    def get_queryset(self):
        username = self.kwargs.get("username")
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise NotFound("User not found")

        return Submission.objects.filter(user=user).order_by("-id")
