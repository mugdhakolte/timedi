import os

from django.conf import settings
from django.contrib.auth.models import Permission
from django.core.management.base import BaseCommand

from timedi_auth.models import TimediPermission


class Command(BaseCommand):
    """
    To create permissions in db.

    Management command will create the commands specified in the config and
    will create in database.
    """
    help = 'Creates permissions in db.'

    def handle(self, *args, **options):
        for module in settings.MODULES:
            TimediPermission.objects.get_or_create(**module)
