from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .registration_views import RegistrationCancelView
from .views import EventViewSet, MyRegistrationViewSet

router = DefaultRouter()
router.register(r"events", EventViewSet, basename="event")
router.register(r"my-registrations", MyRegistrationViewSet, basename="my-registration")

urlpatterns = [
    path("", include(router.urls)),
    path(
        "registrations/<int:pk>/",
        RegistrationCancelView.as_view(),
        name="registration-cancel",
    ),
]
