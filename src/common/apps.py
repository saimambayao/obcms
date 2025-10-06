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
