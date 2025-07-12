from django.contrib.auth.models import User
from rest_framework import generics
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Profile
from .serializers import LoginSerializer, ProfileSerializer, RegisterSerializer

""" Student role{
    "username" : "Student",
    "password" : "test123",
    "email" : "student@student.com"


    Mentor role{
    "username" : "mentor",
    "password" : "test123",
    "email": "mentor@mentor.com}

}"""


class ProfileDetailAPIView(generics.RetrieveAPIView):

    authentication_classes = []
    permission_classes = []

    serializer_class = ProfileSerializer

    def get_object(self):
        username = self.kwargs.get("username")
        try:
            user = User.objects.get(username=username)
            return user.profile  # via related_name="profile"
        except User.DoesNotExist:
            raise NotFound("User not found")


class ProfilesListAPIView(generics.ListAPIView):

    serializer_class = ProfileSerializer

    def get_queryset(self):
        end_rank = int(self.request.query_params.get("range", 10))
        start_rank = 1

        return Profile.objects.filter(
            rank__gte=start_rank,
            rank__lte=end_rank,
        ).order_by("rank")


class LocalLeaderboardAPIView(generics.ListAPIView):
    serializer_class = ProfileSerializer

    def get_queryset(self):
        range_value = int(self.request.query_params.get("range", 1))
        user_profile = self.request.user.profile
        user_rank = user_profile.rank

        start_rank = max(1, user_rank - range_value)
        end_rank = user_rank + range_value

        return Profile.objects.filter(
            rank__gte=start_rank,
            rank__lte=end_rank,
        ).order_by("rank")


class LoginAPIView(APIView):

    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            refresh_token = data["tokens"]["refresh"]
            access_token = data["tokens"]["access"]

            res = Response(
                {
                    "username": data["username"],
                    "role": data["role"],
                    "access": access_token,
                }
            )

            res.set_cookie(
                key="refresh_token",
                value=refresh_token,
                httponly=True,
                samesite="Lax",
                secure=False,
                max_age=86400,
            )

            return res
        return Response(serializer.errors, status=400)


class RegisterAPIView(APIView):

    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            data = serializer.save()

            refresh_token = data["tokens"]["refresh"]
            access_token = data["tokens"]["access"]

            res = Response(
                {
                    "username": data["username"],
                    "role": data["role"],
                    "access": access_token,
                }
            )

            res.set_cookie(
                key="refresh_token",
                value=refresh_token,
                httponly=True,
                samesite="Lax",
                secure=False,
                max_age=86400,
            )

            return res

        return Response(serializer.errors, status=400)


class RefreshTokenAPIView(APIView):

    authentication_classes = []
    permission_classes = []

    def post(self, request):
        refresh_token = request.COOKIES.get("refresh_token")

        if refresh_token is None:
            return Response({"detail": "NO refresh token"}, status=400)

        try:
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)
            return Response({"access": access_token})

        except TokenError:
            return Response({"detail": "Invalid token"}, status=401)


class LogoutAPIView(APIView):

    authentication_classes = []
    permission_classes = []

    def post(self, request):
        try:
            refresh_token = request.COOKIES.get("refresh_token")
            token = RefreshToken(refresh_token)
            token.blacklist()
            res = Response({"detail": "Successfully loggedd out."})
            res.delete_cookie("refresh_token")

            return res

        except Exception as e:
            return Response({"detail": f"{str(e)}"}, status=400)
