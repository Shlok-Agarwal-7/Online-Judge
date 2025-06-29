from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

from .helpers import run_code, submit_code
from .models import Problem, Submission, TestCase
from .permissions import isMentor
from .serializers import (
    ProblemDetailSerializer,
    ProblemListSerializer,
    ProblemSerializer,
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
        serializer = self.get_serializer(data=request.data, instance=instance)

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
            problem = serializer.validated_data["problem"]
            user = request.user

            result = submit_code(language, code, problem.id)
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


class GetUserSubmissions(generics.ListAPIView):
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
