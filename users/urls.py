from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenBlacklistView,
)

from . import views


urlpatterns = [
    path('register', views.RegisterView.as_view(), name='register'),
    path('user', views.UserView.as_view(), name='user'),
    path('login', TokenObtainPairView.as_view(), name='login'),
    path('refresh-token/', TokenRefreshView.as_view(), name='refresh_token'),
    path('logout', TokenBlacklistView.as_view(), name='logout'),
]
