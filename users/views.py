from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from .serializers import UserSerializer


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
