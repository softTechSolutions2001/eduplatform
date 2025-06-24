from django.apps import AppConfig


class AICourseBuilderConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ai_course_builder'
    verbose_name = 'AI Course Builder'

    def ready(self):
        # Import any signals here
        pass
