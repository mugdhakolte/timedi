from django.dispatch import receiver
from django.db.models.signals import pre_save
from rest_framework_simplejwt.tokens import AccessToken
from .models import *


@receiver(pre_save, sender=UserTimediPermissionMap)
def blacklist_token_before_delete_user(sender, instance, **kwargs):
    if instance.user.is_superuser:
        return True
    try:
        for access_token_obj in AccessToken.objects.filter(user=instance.user):
            BlacklistedAccessToken.objects.create(token=access_token_obj.token, user=instance.user)
            access_token_obj.delete()
    except AccessToken.DoesNotExist:
        pass
