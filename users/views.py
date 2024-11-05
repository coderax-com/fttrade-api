from unittest.mock import patch

import jwt

from datetime import datetime, timedelta, UTC
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from fttrade import settings
from .serializers import UserSerializer
from .models import User


class RegisterView(CreateAPIView):
    """
    User Registration view
    """
    serializer_class = UserSerializer


class UserView(RetrieveAPIView):
    """
    User details view
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, ]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user
