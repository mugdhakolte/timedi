from .models import Token
from django.utils.crypto import get_random_string
import datetime


def create_token(user, action):
    """To create random token in database."""

    token = get_random_string(length=64)
    created_at = datetime.datetime.now()
    expires_at = datetime.datetime.now() + datetime.timedelta(days=1)
    token = Token.objects.create(
        user=user, action=action, token=token, created_at=created_at,
        expires_at=expires_at)
    return token
