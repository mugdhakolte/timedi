from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.contrib.auth.models import AbstractUser
from timedi_auth.choices import *


class User(AbstractUser):

    email = models.EmailField()
    name = models.CharField(max_length=30)

    class Meta:
        permissions = [
            {'name': 'read', 'code': 'Read'},
            {'name': 'write', 'code': 'Write'},
        ]


user_group, created = Group.objects.get_or_create(
    choice=DEFAULT_GROUPS_CHOICES)

ct = ContentType.objects.get_for_model(User)

permission = Permission.objects.create(code='Read', name='read',
                                       content_type=ct)
user_group.permissions.add(permission)
