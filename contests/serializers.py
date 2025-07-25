from rest_framework import serializers

from problems.models import Problem
from problems.serializers import ProblemListSerializer, SubmissionSerializer

from .models import Contest, ContestProblem, ContestSubmission


class ContestSerializer(serializers.ModelSerializer):
    created_by = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Contest
        fields = ["id", "title", "description", "start_time", "end_time", "created_by"]

    def get_created_by(self, obj):
        return obj.created_by.username

    def validate(self, attrs):
        title = attrs.get("title")

        if Contest.objects.filter(title=title).exists():
            raise serializers.ValidationError(
                {"detail": "Contest with the same name already exists"}
            )

        if attrs["start_time"] >= attrs["end_time"]:
            raise serializers.ValidationError(
                {"detail": "End time must be after start time."}
            )


        return attrs

    def create(self, validated_data):
        validated_data["created_by"] = self.context["request"].user
        return super().create(validated_data)


class ContestProblemSerializer(serializers.ModelSerializer):
    problem = ProblemListSerializer()

    class Meta:
        model = ContestProblem
        fields = ("order", "problem")


class ContestSubmissionSerializer(serializers.ModelSerializer):
    submission = SubmissionSerializer(read_only=True)

    class Meta:
        model = ContestSubmission
        fields = ("submission", "submission_time")


class AddExistingProblemSerializer(serializers.ModelSerializer):
    problem_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = ContestProblem
        fields = ("order", "problem_id")

    def validate_problem_id(self, value):
        if ContestProblem.objects.filter(problem_id=value).exists():
            raise serializers.ValidationError(
                {"detail": "This problem is already added to another contest"}
            )
        return value

    def create(self, validated_data):
        contest = self.context["contest"]
              
        try:
            problem = Problem.objects.get(id=validated_data["problem_id"])
        except Problem.DoesNotExist:
            raise serializers.ValidationError({"problem_id": "Invalid problem ID"})

        return ContestProblem.objects.create(
            contest=contest, problem=problem, order=validated_data["order"]
        )
