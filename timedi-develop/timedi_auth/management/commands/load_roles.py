import os

from django.conf import settings
from django.core.management.base import BaseCommand

from timedi_auth.models import Role


class Command(BaseCommand):
    """
    To create roles in db.

    Management command will create the commands specified in the config and
    will create in database.
    """
    help = 'Creates roles in db.'

    def handle(self, *args, **options):
        for role in settings.DEFAULT_ROLES:
            Role.objects.get_or_create(name=role)
