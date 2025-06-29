from rest_framework import serializers

from .models import Problem, Submission, TestCase


# used for sending and receving data of testcase
class TestCaseSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = TestCase
        fields = ("id", "input", "output")


# used for individual problem page
class ProblemDetailSerializer(serializers.ModelSerializer):
    testcases = TestCaseSerializer(many=True, read_only=True)

    class Meta:
        model = Problem
        fields = (
            "id",
            "title",
            "created_by",
            "created_at",
            "question",
            "testcases",
            "difficulty",
        )


# used for list of problems page
class ProblemListSerializer(serializers.ModelSerializer):
    created_by = serializers.SerializerMethodField()

    class Meta:
        model = Problem
        fields = ("id", "title", "created_by", "created_at", "difficulty")

    def get_created_by(self, obj):
        return obj.created_by.username


class ProblemSerializer(serializers.ModelSerializer):
    testcases = TestCaseSerializer(many=True)

    class Meta:
        model = Problem
        fields = ("title", "question", "testcases", "difficulty")

    def create(self, validated_data):

        testcases_data = validated_data.pop("testcases", [])

        user = None

        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user

        try:
            problem = Problem.objects.create(created_by=user, **validated_data)

            for testcase in testcases_data:
                TestCase.objects.create(problem=problem, **testcase)

            return {"detail": f"Problem Created Succesfully {problem.id}"}
        except Exception as e:
            raise serializers.ValidationError(f"An Error occured {e}")

    def update(self, instance, validated_data):

        testcases_data = validated_data.pop("testcases", [])

        print(f"testcases_data {testcases_data}")

        try:
            if validated_data.get("title") != " ":
                instance.title = validated_data.get("title")

            if validated_data.get("question") != " ":
                instance.question = validated_data.get("question")

            if validated_data.get("difficulty") != " ":
                instance.difficulty = validated_data.get("difficulty")

            instance.save()

            TestCase.objects.filter(problem=instance).delete()

            for testcase_data in testcases_data:
                testcase = TestCase.objects.create(problem=instance, **testcase_data)

            return {"detail": f"updated the fields and testcases for {instance.id}"}

        except Exception as e:
            raise serializers.ValidationError(f"An error occured {e}")


class SubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = ["id", "code", "language", "verdict", "problem"]
        read_only_fields = ["verdict"]

class RunCodeSerializer(serializers.Serializer):
    code = serializers.CharField()
    language = serializers.ChoiceField(
        choices=[("py", "Python"), ("cpp", "C++"), ("java", "Java")]
    )
    input_data = serializers.CharField(allow_blank=True)
