# -*- coding: utf-8 -*-
"""Implement API views here.
Implements the API views for notification service.
"""

from rest_framework.viewsets import ModelViewSet

# from notifications.models import *
from notifications.serializers import *


class NotificationViewSet(ModelViewSet):
    """This class is for REST apis related to Notification service."""

    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    http_method_names = ['post']


class NotificationTemplateViewSet(ModelViewSet):
    """This class is for REST apis related to Notification
    Template service.
    """

    queryset = NotificationTemplate.objects.all()
    serializer_class = NotificationTemplateSerializer
