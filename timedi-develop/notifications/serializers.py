"""Serializer for notification and notification template"""

from rest_framework import serializers

from notifications.models import NotificationTemplate, Notification, NotificationType


class NotificationSerializer(serializers.ModelSerializer):
    """Notification model serializer class for notifications."""

    template = serializers.SlugRelatedField(queryset=NotificationTemplate.objects,
                                            slug_field='name', required=True)
    type = serializers.SlugRelatedField(queryset=NotificationType.objects,
                                        slug_field='code', required=True)

    class Meta:
        """Meta class for notification model serializer."""
        model = Notification
        fields = "__all__"


class NotificationTemplateSerializer(serializers.ModelSerializer):
    """Model Serializer class for listing all notification templates."""

    class Meta:
        """Meta class for notification template serializer."""
        model = NotificationTemplate
        fields = "__all__"
