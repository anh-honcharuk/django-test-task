from drf_spectacular.utils import extend_schema
from rest_framework import generics, permissions

from .models import EventRegistration
from .serializers import EventRegistrationSerializer


@extend_schema(summary="Cancel registration by owner id", tags=["registrations"])
class RegistrationCancelView(generics.DestroyAPIView):
    serializer_class = EventRegistrationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return EventRegistration.objects.filter(user=self.request.user)
