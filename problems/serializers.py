from rest_framework import serializers

from .models import Problem, ProblemTag, Submission, TestCase


# used for sending and receving data of testcase
class TestCaseSerializer(serializers.ModelSerializer):

    class Meta:
        model = TestCase
        fields = ("input", "output")


class ProblemTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProblemTag
        fields = ["id", "name"]

class HintRequestSerializer(serializers.Serializer):
    title = serializers.CharField()
    question = serializers.CharField()

# used for individual problem page
class ProblemDetailSerializer(serializers.ModelSerializer):
    tags = serializers.SlugRelatedField(many=True, read_only=True, slug_field="name")

    class Meta:
        model = Problem
        fields = (
            "id",
            "title",
            "created_by",
            "created_at",
            "question",
            "sample_input",
            "sample_output",
            "difficulty",
            "time_limit",
            "memory_limit",
            "tags",
            "blacklist"
        )


# used for list of problems page
class ProblemListSerializer(serializers.ModelSerializer):
    created_by = serializers.SerializerMethodField()

    tags = serializers.SlugRelatedField(many=True, read_only=True, slug_field="name")

    class Meta:
        model = Problem
        fields = ("id", "title", "created_by", "created_at", "difficulty", "tags")

    def get_created_by(self, obj):
        return obj.created_by.username

class ProblemSerializer(serializers.ModelSerializer):
    testcases = TestCaseSerializer(many=True, required=False)
    tags = serializers.SlugRelatedField(
        many=True, slug_field="name", queryset=ProblemTag.objects.all()
    )

    class Meta:
        model = Problem
        fields = (
            "title",
            "question",
            "testcases",
            "difficulty",
            "tags",
            "sample_input",
            "sample_output",
            "time_limit",
            "memory_limit",
            "blacklist"
        )
    
    def validate(self, attrs):
        title = attrs.get("title")

        if self.instance == None and Problem.objects.filter(title = title).exists():
            raise serializers.ValidationError({"detail" : "Similar problem with same title already exists"})

        return attrs

    def create(self, validated_data):

        testcases_data = validated_data.pop("testcases", [])
        tags_data = validated_data.pop("tags", None)

        user = None

        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user

        try:
            problem = Problem.objects.create(created_by=user, **validated_data)

            problem.tags.set(tags_data)
            for testcase in testcases_data:
                TestCase.objects.create(problem=problem, **testcase)

            return {"detail": f"Problem Created Succesfully {problem.id}"}
        except Exception as e:
            raise serializers.ValidationError(f"An Error occured {e}")

    def update(self, instance, validated_data):
        testcases_data = validated_data.pop("testcases", [])
        tags_data = validated_data.pop("tags", None)

        try:
            for attr in [
                "title",
                "question",
                "difficulty",
                "sample_input",
                "sample_output",
                "blacklist",
                "memory_limit",
                "time_limit",
            ]:
                if attr in validated_data:
                    setattr(instance, attr, validated_data[attr])

            instance.save()

            if tags_data is not None:
                instance.tags.set(tags_data)

            if testcases_data:
                TestCase.objects.filter(problem=instance).delete()

                for testcase_data in testcases_data:
                    testcase = TestCase.objects.create(
                        problem=instance, **testcase_data
                    )

            return {"detail": f"updated the fields and testcases for {instance.id}"}

        except Exception as e:
            raise serializers.ValidationError(f"An error occured {e}")


class SubmissionSerializer(serializers.ModelSerializer):
    problem_id = serializers.IntegerField(write_only=True, required=True)
    problem = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()

    class Meta:
        model = Submission
        fields = ["id", "code", "language", "verdict", "problem_id", "user", "problem"]
        read_only_fields = ["verdict", "problem", "user"]

    def get_problem(self, obj):
        return obj.problem.title

    def get_user(self, obj):
        return obj.user.username


class RunCodeSerializer(serializers.Serializer):
    code = serializers.CharField()
    language = serializers.ChoiceField(
        choices=[("py", "Python"), ("cpp", "C++"), ("java", "Java")]
    )
    input_data = serializers.CharField(allow_blank=True)
