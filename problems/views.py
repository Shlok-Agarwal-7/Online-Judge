from django.shortcuts import render
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Problem,TestCase,Submission
from .serializers import ProblemDetailSerializer,ProblemListSerializer,ProblemSerializer
from .permissions import isMentor

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

    def post(self,request):
        serializer = ProblemSerializer(data = request.data, context={"request": request})

        if(serializer.is_valid()):
            data = serializer.save()
            return Response(data,status = 201)
        
        return Response(serializer.errors,status = 400)


class ProblemDeleteView(generics.DestroyAPIView):

    permission_classes = [isMentor]

    queryset = Problem.objects.all()
    serializer_class = ProblemSerializer
    
    def destroy(self,request,*args,**kwargs):
        instance = self.get_object()

        try:
            id = instance.id
            self.perform_destroy(instance)
            return Response({"detail" : f"Destroyed Problem with id{id}"},status = 200)
        
        except Exception as e:
            return Response({"detail" : f"couldnt destroy due to server issues try later"},status = 500)
        
class ProblemUpdateView(generics.UpdateAPIView):

    permission_classes = [isMentor]

    queryset = Problem.objects.all()
    serializer_class = ProblemSerializer

    def update(self,request,*args,**kwargs): 
        instance = self.get_object()
        serializer = self.get_serializer(data = request.data,instance = instance)

        if(serializer.is_valid()):
            data = serializer.save()
            return Response(data,status = 200) 


        return Response(serializer.errors,status = 400)
