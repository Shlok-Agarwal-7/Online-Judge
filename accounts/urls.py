from .views import LoginAPIView
from django.urls import path

urlpatterns = [
    path("api/login",LoginAPIView.as_view(),name = "login_user_api")
]
