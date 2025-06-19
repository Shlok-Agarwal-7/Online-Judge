from .serializers import LoginSerializer,RegisterSerializer
from django.contrib.auth.models import User
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken


class LoginAPIView(APIView):

    authentication_classes = []
    permission_classes = []

    def post(self,request):
        serializer = LoginSerializer(data = request.data)
        if(serializer.is_valid()):
            return Response(serializer.validated_data,status = 200)
        return Response(serializer.errors,status = 400)



class RegisterAPIView(APIView):

    authentication_classes = []
    permission_classes = []

    def post(self,request):
        serializer = RegisterSerializer(data = request.data)

        if(serializer.is_valid()):
            data = serializer.save()
            return Response(data,status = 201)

        return Response(serializer.errors,status = 400)



class LogoutAPIView(APIView):

    authentication_classes = []
    permission_classes = []

    def post(self,request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            # print(refresh_token)
            token.blacklist()
            return Response({"detail" : "Successfully logged out."})
            
        except Exception as e:
            return Response({"detail" : f"{str(e)}"},status = 400)
