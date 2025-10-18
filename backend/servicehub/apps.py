from django.apps import AppConfig


class ServicehubConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'servicehub'
    verbose_name = 'ServiceHub'
    
    def ready(self):
        """Import signals when app is ready."""
        import servicehub.utils.signals  # noqa

