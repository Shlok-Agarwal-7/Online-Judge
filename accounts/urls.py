from .views import LoginAPIView,RegisterAPIView,LogoutAPIView,ProfilesListAPIView,RefreshTokenAPIView
from django.urls import path

urlpatterns = [
    path("api/login",LoginAPIView.as_view(),name = "login_user_api"),
    path("api/register",RegisterAPIView.as_view(),name = "register_user_api"),
    path("api/logout",LogoutAPIView.as_view(),name = "logout_user_api"),
    path("api/top-users",ProfilesListAPIView.as_view(),name = "top_user_api"),
    path("api/refresh-access",RefreshTokenAPIView.as_view(),name = "refresh_token_api")
]