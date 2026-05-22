from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
    verbose_name = 'Configuration'

    def ready(self):
        from core.signals import register_content_signals
        register_content_signals()
