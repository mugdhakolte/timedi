"""This file for validation of phone number and json"""
import re
import json

from django.core.validators import BaseValidator
from django.core.exceptions import ValidationError


class PhoneNumberValidator(BaseValidator):
    """Validator for phone numbers."""

    message = "Ensure phonenumber is valid"
    _pattern = r'(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})'

    def __init__(self):
        pass

    def __call__(self, value):
        """
            :param phonenumber type -string:
            :return: raises ValidationError or returns value if input is valid
            US phone number.
        """
        match = re.search(self._pattern, value)
        if not match:
            raise ValidationError("Not a valid phone number")


class JSONValidator(BaseValidator):
    """Validator for JSON fields."""
    message = 'Ensure valid json.'

    def __init__(self):
        pass

    def __call__(self, value):
        """
            :param string:
            :return: raises validationError or return cleaned value
            as dict (valid json object)
        """
        try:
            json.loads(value)
        except ValueError:
            raise ValidationError("Not a valid json")
