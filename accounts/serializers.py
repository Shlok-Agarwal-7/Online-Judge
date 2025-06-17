from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self,attrs):
        username = attrs.get("username")
        password = attrs.get("password")


        user = User.objects.filter(username = username).first()

        if user :
            if user.check_password(password):
                refresh = RefreshToken.for_user(user)
                return{
                    "username" : username,
                    "tokens" : {
                        "refresh" : str(refresh),
                        "access" : str(refresh.access_token)
                    }
                }
            else:
                raise serializers.ValidationError("Invalid Password Please Recheck Password")
        else:
            raise serializers.ValidationError("User not found")
    