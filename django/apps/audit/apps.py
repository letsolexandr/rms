from django.apps import AppConfig

class AuditConfig(AppConfig):
    name = 'apps.audit'
    verbose_name = 'Лог дій користувача'

    def ready(self):
        from apps.audit.signals import auth_signals, model_signals, request_signals