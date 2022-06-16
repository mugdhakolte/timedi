import json

from django.conf import settings

from notifications.models import Notification, NotificationType, NotificationTemplate


def send_forgot_password_email(user, username, token):
    """
    """
    try:
        context = {
            'url': "{0}/reset-password/{1}/".format(settings.APP_URL, token.token),
            'name': user.full_name,
            'username': username,
            'subject': "Reset Password"
        }
        notification_template = NotificationTemplate.objects.get(name="forgot_password")
        notification_type = NotificationType.objects.get(code="email")
        Notification.objects.create(type=notification_type,
                                    template=notification_template,
                                    context=json.dumps(context),
                                    receiver=user.email)
        return True
    except:
        return False


def send_new_user_email(user, username, password):
    """
    """
    context = {
        'name': user.full_name,
        'username': username,
        "password": password,
        'subject': "New User"
    }
    notification_template = NotificationTemplate.objects.get(name="new_user")
    notification_type = NotificationType.objects.get(code="email")
    Notification.objects.create(type=notification_type,
                                template=notification_template,
                                context=json.dumps(context),
                                receiver=user.email)
