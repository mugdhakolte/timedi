"""
Serializers for timedi_auth.
"""

from django.utils.translation import gettext_lazy as _

from rest_framework import serializers
from rest_framework_simplejwt.state import token_backend
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

from timedi_auth.models import *


class LoginSerializer(serializers.Serializer):
    """To validate the login credentials."""

    password = serializers.CharField(trim_whitespace=False)
    username = serializers.CharField(trim_whitespace=False)


class LogoutSerializer(serializers.Serializer):
    """To validate the login credentials."""
    refresh = serializers.CharField(required=True)
    access = serializers.CharField(required=True)

    default_error_messages = {
        'bad_token': _('Token is invalid or expired')
    }

    def validate(self, attrs):
        self.refresh_token = attrs['refresh']
        self.access_token = attrs['access']
        return attrs

    def save(self, **kwargs):
        try:
            RefreshToken(self.refresh_token).blacklist()
            token_obj = token_backend.decode(self.access_token, True)
            BlacklistedAccessToken.objects.create(token=self.access_token, user_id=token_obj['user_id'])
            AccessToken.objects.get(token=self.access_token, user_id=token_obj['user_id']).delete()
        except AccessToken.DoesNotExist:
            self.fail('bad_token')


class ForgotPasswordSerializer(serializers.Serializer):
    """A serializer for forgot password."""
    username = serializers.CharField()


class ResetPasswordSerializer(serializers.Serializer):
    """A serializer for change password."""

    token = serializers.SlugRelatedField(queryset=Token.objects, slug_field='token')
    new_password = serializers.CharField()


class ChangePasswordSerializer(serializers.Serializer):
    """A serializer for change password."""

    old_password = serializers.CharField(trim_whitespace=False)
    new_password = serializers.CharField(trim_whitespace=False)
    confirm_password = serializers.CharField(trim_whitespace=False)

    def validate_old_password(self, old_password):
        """
        """
        request = self.context['request']
        if not request.user.check_password(old_password):
            msg = _('Old password is not correct')
            raise serializers.ValidationError(msg, code='authorization')

    def validate(self, validated_data):
        """To validate on new and old password."""

        old_password = validated_data.get('old_password')
        new_password = validated_data.get('new_password')
        confirm_password = validated_data.get('confirm_password')
        if old_password == new_password:
            msg = _('Old Password and New Password should not be same')
            raise serializers.ValidationError(msg, code='authorization')
        if new_password != confirm_password:
            msg = _('New Password and Confirm Password does not match')
            raise serializers.ValidationError(msg, code='authorization')
        return validated_data


class ValidateTokenSerializer(serializers.Serializer):
    access = serializers.CharField(required=True)
