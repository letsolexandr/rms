from django.core.management.base import BaseCommand
from django.core.management import CommandError, call_command
from django.contrib.contenttypes.models import ContentType

class Command(BaseCommand):

    def handle(self, *args, **options):
        call_command("loaddata", 'initial_lcore.json', app_label='core')
