from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Event, EventRegistration


class OrganizerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email")


class EventSerializer(serializers.ModelSerializer):
    organizer = OrganizerSerializer(read_only=True)

    class Meta:
        model = Event
        fields = (
            "id",
            "title",
            "description",
            "date",
            "location",
            "organizer"
        )
        read_only_fields = ("organizer",)


class EventWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ("id", "title", "description", "date", "location")

    def create(self, validated_data):
        validated_data["organizer"] = self.context["request"].user
        return super().create(validated_data)


class EventRegistrationSerializer(serializers.ModelSerializer):
    event_title = serializers.CharField(source="event.title", read_only=True)
    event_date = serializers.DateTimeField(source="event.date", read_only=True)

    class Meta:
        model = EventRegistration
        fields = (
            "id",
            "event",
            "event_title",
            "event_date",
            "registered_at",
        )
        read_only_fields = ("registered_at", "event_title", "event_date")
