import django_filters
from django.db import models

from .models import Event


class EventFilter(django_filters.FilterSet):
    """Filter events by date range, location, and organizer."""

    date_from = django_filters.IsoDateTimeFilter(field_name="date", lookup_expr="gte")
    date_to = django_filters.IsoDateTimeFilter(field_name="date", lookup_expr="lte")
    location = django_filters.CharFilter(lookup_expr="icontains")
    organizer = django_filters.NumberFilter(field_name="organizer__id")

    class Meta:
        model = Event
        fields = ["location", "organizer"]
