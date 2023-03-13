from django.utils import timezone
from django.apps import AppConfig



class CoreConfig(AppConfig):
    name = 'apps.core'
    verbose_name = 'Адміністрування'

    def ready(self):
        from apps.core.signals import init_core_signals
        init_core_signals()

        