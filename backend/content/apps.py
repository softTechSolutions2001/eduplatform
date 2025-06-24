from django.apps import AppConfig


class ContentConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'content'
    verbose_name = 'Content & Statistics'

    def ready(self):
        """
        Initialize signals and perform other setup
        """
        try:
            # Import signals module to register signal handlers
            import content.signals
        except ImportError:
            pass
