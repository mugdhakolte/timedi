"""Used for send notifications"""
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from notifications.models import NotificationTemplate


class Command(BaseCommand):
    """Fetches and processes notifications that are pending."""

    help = 'Fetches and processes notifications that are pending.'

    def handle(self, *args, **kwargs):
        for notification_template_name in settings.NOTIFICATION_TEMPLATES:

            try:
                notification_template = NotificationTemplate.objects.get(name=notification_template_name)
            except NotificationTemplate.DoesNotExist:
                notification_template = NotificationTemplate()
                notification_template.name = notification_template_name
            finally:
                template_name = "{}_email_template.html".format(notification_template_name)
                template_path = os.path.join(settings.BASE_DIR, 'notifications/templates', template_name)
                with open(template_path, 'r') as f:
                    template_content = f.read()
                notification_template.content = template_content
                notification_template.save()
