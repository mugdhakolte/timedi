"""Used for send notifications"""
from django.conf import settings
from django.core.management.base import BaseCommand

from notifications.models import NotificationType


class Command(BaseCommand):
    """Fetches and processes notifications that are pending."""

    def handle(self, *args, **kwargs):
        for notification_type_code in settings.NOTIFICATION_TYPES:
            NotificationType.objects.get_or_create(code=notification_type_code.lower())
