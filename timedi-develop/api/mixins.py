# from .models import User
# from rest_framework import serializers
# from django.utils.translation import gettext_lazy as _
#
#
# class EmailValidatorMixin:
#     """To validate email if user with given email exists and user is active"""
#
#     def validate_email(self, email_id):
#         """To validate if email exists."""
#         try:
#             user = User.objects.get(email=email_id)
#             if not user.is_active:
#                 raise serializers.ValidationError(_('User is not active.'))
#         except User.DoesNotExist:
#             raise serializers.ValidationError(_('Invalid email_id'))
#         return email_id
