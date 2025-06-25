from .serializers import LoginSerializer,RegisterSerializer,ProfileSerializer
from django.contrib.auth.models import User
from .models import Profile
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

""" Student role{
    "username" : "Student",
    "password" : "test123",
    "email" : "student@student.com"


    Mentor role{
    "username" : "mentor",
    "password" : "test123",
    "email": "mentor@mentor.com}

}"""

class ProfilesListAPIView(generics.ListAPIView):

    queryset = Profile.objects.order_by("-points")[:10]
    serializer_class = ProfileSerializer


class LoginAPIView(APIView):

    authentication_classes = []
    permission_classes = []

    def post(self,request):
        serializer = LoginSerializer(data = request.data)
        if(serializer.is_valid()):
            data = serializer.validated_data
            refresh_token = data["tokens"]["refresh"]
            access_token = data["tokens"]["access"]

            res = Response({
                "username" : data["username"],
                "role" : data["role"],
                "access" : access_token
            })

            res.set_cookie(
                key= "refresh_token",
                value = refresh_token,
                httponly= True,
                samesite= "Lax",
                secure= False,
                max_age = 86400 
            )

            return res
        return Response(serializer.errors,status = 400)


class RegisterAPIView(APIView):

    authentication_classes = []
    permission_classes = []

    def post(self,request):
        serializer = RegisterSerializer(data = request.data)

        if(serializer.is_valid()):
            data = serializer.save()

            refresh_token = data["tokens"]["refresh"]
            access_token = data["tokens"]["access"]

            res = Response({
                "username" : data["username"],
                "role" : data["role"],
                "access" : access_token
            })

            res.set_cookie(
                key= "refresh_token",
                value = refresh_token,
                httponly= True,
                samesite= "Lax",
                secure = False,
                max_age = 86400
            )

            return res

        return Response(serializer.errors,status = 400)

class RefreshTokenAPIView(APIView):

    authentication_classes = []
    permission_classes = []

    def post(self,request):
        refresh_token = request.COOKIES.get('refresh_token')

        if refresh_token is None:
            return Response({"detail" : "NO refresh token"},status = 400)
        
        try:
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)
            return Response({"access" : access_token})

        except TokenError:
            return Response({"detail" : "Invalid token"},status = 401)

class LogoutAPIView(APIView):

    authentication_classes = []
    permission_classes = []

    def post(self,request):
        try:
            refresh_token = request.COOKIES.get("refresh_token")
            token = RefreshToken(refresh_token)
            print(refresh_token)
            token.blacklist()
            res = Response({"detail" : "Successfully loggedd out."})
            res.delete_cookie("refresh_token")

            return res    

        except Exception as e:
            return Response({"detail" : f"{str(e)}"},status = 400)
