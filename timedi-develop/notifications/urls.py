"""Default routers for api urls."""

from rest_framework.routers import DefaultRouter

from notifications.viewsets import (NotificationViewSet,
                                    NotificationTemplateViewSet,)

ROUTER = DefaultRouter()

handler404 = 'api.error_handlers.page_not_found'

handler500 = 'api.error_handlers.server_error'

ROUTER.register('notification-template', NotificationTemplateViewSet,
                base_name='notification_template')

ROUTER.register('notifications', NotificationViewSet, base_name='notification')

urlpatterns = ROUTER.urls
