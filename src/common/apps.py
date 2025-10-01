from django.apps import AppConfig


class CommonConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "common"

    def ready(self):
        import common.signals
        import common.services.task_automation  # Load task automation signal handlers
