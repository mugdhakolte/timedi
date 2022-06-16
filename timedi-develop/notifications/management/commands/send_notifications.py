"""Used for send notifications"""
import datetime, logging

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.module_loading import import_string

from notifications.models import Notification


class Command(BaseCommand):
    """Fetches and processes notifications that are pending."""

    help = 'Fetches and processes notifications that are pending.'

    def handle(self, *args, **kwargs):
        pending_notifications = Notification.objects.filter(is_sent=False)
        for pending_notification in pending_notifications:
            notification_type_code = pending_notification.type.code
            notification_type_sender_path = settings.NOTIFICATION_TYPES[notification_type_code]
            notification_type_sender = import_string(notification_type_sender_path)()
            params = dict()
            params["notification"] = pending_notification
            try:
                notification_type_sender.send(**params)
                pending_notification.is_sent = True
                pending_notification.sent_at = datetime.datetime.now()
                pending_notification.save()
            except Exception as e:
                logging.getLogger(__name__).error(repr(e))
                #TODO: Add error log message

        #TODO: testing required
