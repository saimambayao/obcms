from django.apps import AppConfig


class CoordinationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "coordination"

    def ready(self):
        """Import signal handlers when app is ready."""
        import coordination.signals  # noqa: F401
