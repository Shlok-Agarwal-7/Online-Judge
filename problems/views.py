from django.shortcuts import render
from rest_framework import generics
from .models import Problem,TestCase
from .serializers import ProblemDetailSerializer,ProblemListSerializer

# Create your views here.

class ProblemListView(generics.ListCreateAPIView):
    queryset = Problem.objects.all()
    serializer_class = ProblemListSerializer 

class ProblemDetialView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Problem.objects.all()
    serializer_class = ProblemDetailSerializer