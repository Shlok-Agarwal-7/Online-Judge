from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username")

    class Meta:
        model = Profile
        fields = ["username", "points", "rank"]


# ! Serializer to Login the user
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        """
        Returns : username,role,tokens{refresh,access}
        """

        username = attrs.get("username")
        password = attrs.get("password")

        user = User.objects.filter(username=username).first()

        if user:
            role = user.profile.role
            if user.check_password(password):
                refresh = RefreshToken.for_user(user)
                access_token = refresh.access_token
                return {
                    "username": user.username,
                    "role": user.profile.role,
                    "tokens": {"refresh": str(refresh), "access": str(access_token)},
                }
            else:
                raise serializers.ValidationError(
                    {"detail": "Invalid Password Please Recheck Password"}
                )
        else:
            raise serializers.ValidationError({"detail": "User not found"})


#! Serializer to Register the user


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
    email = serializers.EmailField()

    def validate(self, attrs):
        """
        Validates user inputs from the user
        """

        username = attrs.get("username")
        email = attrs.get("email")

        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError("Username already in use pick a new one")

        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("Email already in use pick a new one")

        return attrs

    def create(self, validated_data):
        """
        creates a new user in the DB
        Returns : username,role,tokens{refresh,access}
        """

        username = validated_data["username"]
        password = validated_data["password"]
        email = validated_data["email"]

        try:
            new_user = User.objects.create_user(
                username=username, password=password, email=email
            )
            profile = Profile.objects.create(user=new_user)
            role = profile.role
            refresh = RefreshToken.for_user(new_user)

            access_token = refresh.access_token
            username = new_user.username
            role = new_user.profile.role
            return {
                "username": username,
                "role": role,
                "tokens": {"refresh": str(refresh), "access": str(access_token)},
            }

        except Exception as e:
            raise serializers.ValidationError(
                f"Error occured when creating user {str(e)}"
            )
