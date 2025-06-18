from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken,TokenError

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




class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
    email = serializers.EmailField()

    def validate(self,attrs):
        username = attrs.get("username")
        email = attrs.get("email")

        if(User.objects.filter(username = username).exists()):
            raise serializers.ValidationError("Username already in use pick a new one")

                
        if(User.objects.filter(email = email).exists()):
            raise serializers.ValidationError("Email already in use pick a new one")

        return attrs
    
    def create(self,validated_data):
        username = validated_data['username']
        password = validated_data['password']
        email = validated_data['email']

        try:
            new_user = User.objects.create_user(username = username,password = password,email = email)
            refresh = RefreshToken.for_user(new_user)
            return{
                "username" : username,
                "tokens" : {
                    "refresh" : str(refresh),
                    "access" : str(refresh.access_token)
                }
            }

        except Exception as e:
            raise serializers.ValidationError(f"Error occured when creating user {str(e)}")


class LogoutSerializer(serializer.Serializer):
    refresh = serializers.CharField();

    def validate(self,attrs):
        self.token = attrs['refresh']
        return attrs

    def save(self):
        try:
            token = RefreshToken(self.token)
            token.blacklist()
        except TokenError:
            raise serializers.ValidateError("invalid or expired token")