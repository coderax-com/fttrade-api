from unittest.mock import patch

import jwt

from datetime import datetime, timedelta, UTC
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response

from fttrade import settings
from .serializers import UserSerializer
from .models import User


class RegisterView(CreateAPIView):
    """
    User Registration view
    """
    serializer_class = UserSerializer


class LoginView(APIView):
    """
    User Authentication view
    """

    def post(self, request):
        email = request.data['email']
        password = request.data['password']
        user = User.objects.filter(email=email).first()
        err_msg = 'Invalid email or password'

        if not user:
            raise AuthenticationFailed(err_msg)

        if not user.check_password(password):
            raise AuthenticationFailed(err_msg)

        token = self.generate_token(user)

        data = {
            'jwt': token,
        }

        response = Response(data)
        response.set_cookie(key='jwt', value=token, httponly=True)
        return response

    @staticmethod
    def generate_token(user):

        payload = {
            'id': user.id,
            'exp': datetime.now(UTC) + timedelta(hours=settings.TOKEN_EXPIRY_HOURS),
            'iat': datetime.now(UTC),
        }

        token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
        return token
