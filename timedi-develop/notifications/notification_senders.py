# -*- coding: utf-8 -*-
"""
Implementation for Notifications.

Used to abstract the different type of Notification and enforce the
implementation of required methods.

"""
import json
from abc import ABC, abstractmethod

from django.core.mail import EmailMessage
from django.core.validators import validate_email

from notifications.validators import PhoneNumberValidator


class BaseNotificationSender(ABC):
    """To enforce the implementation of necessary methods for notifications."""

    @abstractmethod
    def send(self, *args, **kwargs):
        """
        To enforce implementation of methods.

        :raises exception or passes implicitly
        """
        pass  # pylint: disable=unnecessary-pass

    @abstractmethod
    def validate(self, value):
        """
        Must override the validation for the notification receiver.

        e.g. phonenumber for SMS, email address for Email
        either return valid value or raise ValidationError
        """
        pass  # pylint: disable=unnecessary-pass


class EmailNotificationSender(BaseNotificationSender):
    """Email Utilities."""

    def __init__(self, *args, **kwargs): # pylint: disable=unused-argument
        """
        To initilize the default subject for email.

        :param args: nil
        :param kwargs: nil
        """
        self._subject = "Subject"

    def send(self, *args, **kwargs):
        """
        For sending email to user.

        :returns should return boolean status for success or failure
        """
        notification = kwargs.get("notification")
        context = json.loads(notification.context)
        email = EmailMessage(
            context.get("subject", self._subject),
            notification.template.content.format(**context),
            to=[notification.receiver],
        )
        email.content_subtype = "html"
        email.send()

    def validate(self, value):
        """
        To validate provided email.

        :param email type string :
        :return: raises ValidationError or returns valid value
        """
        return validate_email(value)


class SMSNotificationSender(BaseNotificationSender):
    """SMS utilities."""

    def send(self, *args, **kwargs):
        """
        To send sms to user.

        :returns should return boolean status for success or failure
        """
        pass  # pylint: disable=unnecessary-pass

    def validate(self, value):
        """
        To validate the provided phonenumber.

        :param phonenumber type string :
        :return: raises ValidationError or returns valid value
        """
        return PhoneNumberValidator().__call__(value)
