from rest_framework import serializers
from .models import Problem,TestCase 



# used for sending and receving data of testcase 
class TestCaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestCase
        fields = ("id","input","output")


# used for individual problem page
class ProblemDetailSerializer(serializers.ModelSerializer):
    testcases = TestCaseSerializer(many = True,read_only = True)

    class Meta:
        model = Problem
        fields = ("id","title","created_by","created_at","question","testcases")

# used for list of problems page 
class ProblemListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Problem
        fields = ("id","title","created_by","created_at")
