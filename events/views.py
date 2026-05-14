from django.db import transaction
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .filters import EventFilter
from .models import Event, EventRegistration
from .permissions import IsOrganizerOrReadOnly
from .serializers import (
    EventRegistrationSerializer,
    EventSerializer,
    EventWriteSerializer,
)


@extend_schema_view(
    list=extend_schema(
        summary="List events",
        description="Supports search and filters.",
        tags=["events"],
    ),
    retrieve=extend_schema(summary="Get event", tags=["events"]),
    create=extend_schema(summary="Create event (authenticated)", tags=["events"]),
    update=extend_schema(summary="Update event (organizer only)", tags=["events"]),
    partial_update=extend_schema(
        summary="Partial update (organizer only)", tags=["events"]
    ),
    destroy=extend_schema(summary="Delete event (organizer only)", tags=["events"]),
)
class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.select_related("organizer").all()
    permission_classes = [IsOrganizerOrReadOnly]
    filterset_class = EventFilter
    search_fields = ("title", "description", "location")
    ordering_fields = ("date", "title")
    ordering = ["-date"]

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return EventWriteSerializer
        return EventSerializer

    @extend_schema(
        summary="Register for event",
        tags=["events"],
        responses={201: EventRegistrationSerializer, 400: None},
    )
    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def register(self, request, pk=None):
        event = self.get_object()
        if event.organizer_id == request.user.id:
            return Response(
                {"detail": "Organizers do not need to register for their own event."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if EventRegistration.objects.filter(event=event, user=request.user).exists():
            return Response(
                {"detail": "Already registered for this event."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        with transaction.atomic():
            reg = EventRegistration.objects.create(event=event, user=request.user)
        ser = EventRegistrationSerializer(reg, context={"request": request})
        return Response(ser.data, status=status.HTTP_201_CREATED)

    @extend_schema(
        summary="Cancel registration",
        tags=["events"],
        responses={204: None, 404: None},
    )
    @register.mapping.delete
    def unregister(self, request, pk=None):
        event = self.get_object()
        deleted, _ = EventRegistration.objects.filter(
            event=event, user=request.user
        ).delete()
        if not deleted:
            return Response(
                {"detail": "No registration found for this event."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema_view(
    list=extend_schema(summary="My event registrations", tags=["registrations"]),
    retrieve=extend_schema(summary="Registration detail", tags=["registrations"]),
)
class MyRegistrationViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = EventRegistrationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return EventRegistration.objects.filter(user=self.request.user).select_related(
            "event", "user"
        )

