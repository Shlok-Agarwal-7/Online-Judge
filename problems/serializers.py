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


class ProblemSerializer(serializers.ModelSerializer):
    testcases = TestCaseSerializer(many = True)

    class Meta:
        model = Problem
        fields = ("title","question","testcases")

    def create(self,validated_data):

        testcases_data = validated_data.pop('testcases',[])

        user = None

        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user
        

        try:
            problem = Problem.objects.create(created_by = user ,**validated_data)

            for testcase in testcases_data:
                TestCase.objects.create(problem = problem,**testcase)
        
            return {
                "detail" : f"Problem Created Succesfully {problem.id}"
            }
        except Exception as e :
            raise serializers.ValidationError(f"An Error occured {e}")

    
    def update(self,instance,validated_data):

        testcases_data = validated_data.pop('testcases',[])


        try:
            if(validated_data.get("title") != " "):
                instance.title = validated_data.get("title")


            if(validated_data.get("question") != " "):
                instance.question = validated_data.get("question")
            
            instance.save()

            for testcase_data in testcases_data:

                testcase_id = testcase_data.get("id")

                try:

                    if(testcase_id != None):
                            testcase = TestCase.objects.get(id = testcase_id,problem = instance)
                            
                            for attr,value in testcase_data:
                                if(attr != id):
                                    setattr(testcase,attr,value)
                            
                            testcase.save()
                    else:
                    
                            testcase = TestCase.objects.create(problem = instance,**testcase_data)
                            

                except Exception as e:
                        raise serializers.ValidationError(f"An Error occured {e}")
 

            return {
                "detial" : f"updated the fields and testcases for {instance.id}"
            }

        except Exception as e:
            raise serializers.ValidationError(f"An error occured {e}")

