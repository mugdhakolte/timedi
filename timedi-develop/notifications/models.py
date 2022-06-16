"""Models for Notification Service."""
import uuid

from django.db import models
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.core.management import call_command
from django.utils.translation import gettext as _
from django.utils.module_loading import import_string

from notifications.validators import JSONValidator


class NotificationType(models.Model):
    """Model for notification type like code : sms,email,push etc."""
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)

    code = models.CharField(max_length=16, unique=True, null=False,
                            blank=False)


class NotificationTemplate(models.Model):
    """Model for template format for the notification."""
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    content = models.TextField(blank=False)
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Notification(models.Model):
    """model for notification to send with scheduled time,
    predefined template,receiver email or phone number etc.
    """
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    template = models.ForeignKey(NotificationTemplate,
                                 on_delete=models.CASCADE,
                                 related_name='notifications')
    type = models.ForeignKey(NotificationType, on_delete=models.CASCADE,
                             related_name='notifications')
    is_sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)
    receiver = models.CharField(max_length=50, blank=False, null=False)
    context = models.TextField(default='{}', validators=[JSONValidator()])
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)

    def clean(self):
        """relevant validations depending type and receiver
        :return: None or raises ValidationError
        """
        notification_type_sender_path = settings.NOTIFICATION_TYPES[self.type.code]
        notification_type_sender = import_string(notification_type_sender_path)()
        notification_type_sender.validate(self.receiver)
        super().clean()


@receiver(post_save, sender=Notification)
def call_send_notification_post_notification_save(sender, instance, created, **kwargs):
    if created:
        call_command('send_notifications')
