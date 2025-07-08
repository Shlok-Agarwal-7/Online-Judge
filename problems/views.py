import time

from celery.result import AsyncResult
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
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
from .tasks import run_code_task, submit_code_task

# Create your views here.


class ProblemListView(generics.ListAPIView):

    authentication_classes = []
    permission_classes = []

    queryset = Problem.objects.all()
    serializer_class = ProblemListSerializer

    # @method_decorator(cache_page(60 * 60 * 2, key_prefix="ProblemsList"))
    # # def list(self, request, *args, **kwargs):
    # #     return super().list(request, *args, **kwargs)

    # # def get_queryset(self):
    # #     # Simulate delay (e.g., 2 seconds)
    # #     time.sleep(2)
    # #     return super().get_queryset()


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
            return Response({"output": str(out)}, status=200)
            # task = run_code_task.delay(language, code, input_data)
            # return Response({"task_id": task.id})
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

            problem = Problem.objects.get(id=problem_id)

            result = submit_code(language, code, problem_id)

            verdict = result.get("verdict")

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


# class CheckRunStatus(APIView):

#     def get(self,request,task_id):
#         result = AsyncResult(task_id)
#         if result.ready():
#                 return Response({"status": result.status, "output": result.result})
#         return Response({"status": result.status})


# class CheckSubmitStatus(APIView):

#     def get(self,request,submission_id):
#         submission = Submission.objects.get(id=submission_id, user = self.request.user)
#         return Response({"verdict": submission.verdict})


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
            return Submission.objects.none()

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
