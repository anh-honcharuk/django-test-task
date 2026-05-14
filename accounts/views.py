from django.contrib.auth.models import User
from drf_spectacular.utils import extend_schema
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import UserRegistrationSerializer


@extend_schema(summary="Register a new user", tags=["auth"])
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
        }
        return Response(data, status=status.HTTP_201_CREATED)


@extend_schema(summary="Obtain JWT pair", tags=["auth"])
class LoginView(TokenObtainPairView):
    """Obtain JWT access and refresh tokens using username and password."""
