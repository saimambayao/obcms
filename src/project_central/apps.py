from django.apps import AppConfig


class ProjectCentralConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "project_central"
    verbose_name = "Project Management Portal"

    def ready(self):
        """Import signal handlers when app is ready."""
        try:
            import project_central.signals  # noqa
        except ImportError:
            pass
