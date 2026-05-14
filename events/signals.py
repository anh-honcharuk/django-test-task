from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import EventRegistration


@receiver(post_save, sender=EventRegistration)
def notify_registration(sender, instance, created, **kwargs):
    if not created:
        return
    user = instance.user
    event = instance.event
    subject = f"You're registered for {event.title}"
    body = (
        f"Hello {user.get_username()},\n\n"
        f"Your registration for the event '{event.title}' has been confirmed.\n\n"
        f"Date: {event.date}\n"
        f"Location: {event.location}\n\n"
        f"We look forward to seeing you there!"
    )
    if user.email:
        send_mail(
            subject,
            body,
            None,
            [user.email],
            fail_silently=True,
        )
