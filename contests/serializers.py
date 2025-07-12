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

        name = attrs.get("title")
        start_time = attrs.get("start_time")
        end_time = attrs.get("end_time")

        if Contest.objects.filter(title=name).exists():
            raise serializers.ValidationError(
                "Contest name already in use pick a new one"
            )

        if Contest.objects.filter(start_time=start_time).exists():
            raise serializers.ValidationError(
                "Another Contest at the same time pick another time"
            )

        if Contest.objects.filter(end_time=end_time).exists():
            raise serializers.ValidationError(
                "Another Contest at the same time pick another time"
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
                "This problem is already added to another contest."
            )
        return value

    def create(self, validated_data):
        contest = self.context["contest"]
        problem = Problem.objects.get(id=validated_data["problem_id"])
        return ContestProblem.objects.create(
            contest=contest, problem=problem, order=validated_data["order"]
        )
