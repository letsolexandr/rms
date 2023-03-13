from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType
from django.utils.functional import Promise


class Command(BaseCommand):
    help = 'Оновлює опис моделей'

    def handle(self, *args, **options):
        self.generate()

    def generate(self):
        self.stdout.write(self.style.SUCCESS(f'Початок   ...'))
        for c in ContentType.objects.all():
                cl = c.model_class()

                # Promises classes are from translated, mostly django-internal models. ignore them.
                if cl and not isinstance(cl._meta.verbose_name, Promise):
                    self.stdout.write(self.style.SUCCESS(str(cl)))
                    new_name = cl._meta.verbose_name
                    self.stdout.write(self.style.SUCCESS('....'+new_name))
                    if c.name != new_name:
                        c.name = new_name
                        c.save()

        self.stdout.write(self.style.SUCCESS(f'закінчено ...'))
