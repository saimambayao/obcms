import sys
from django.apps import AppConfig


class CommonConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "common"

    def ready(self):
        import common.signals
        # NOTE: task_automation signals disabled - TaskTemplate model removed
        # import common.services.task_automation  # Load task automation signal handlers

        # Register models with auditlog for security audit trail
        try:
            from common.auditlog_config import register_auditlog_models
            register_auditlog_models()
        except Exception as e:
            # Don't fail app startup if auditlog registration fails
            print(f"⚠️  Warning: Auditlog registration failed: {e}")

        # Mark Django startup as complete to enable background geocoding
        # This prevents HTTP requests during startup which can cause 30-60s delays
        # NOTE: Geocoding is automatically disabled during management commands
        try:
            from common.services.deferred_geocoding import mark_django_startup_complete
            mark_django_startup_complete()
        except Exception as e:
            # Log error but don't fail startup
            print(f"⚠️  Warning: Failed to mark Django startup complete: {e}")
