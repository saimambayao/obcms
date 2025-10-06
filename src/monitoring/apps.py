from django.apps import AppConfig


class MonitoringConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "monitoring"

    def ready(self):
        """
        Import signal handlers when Django starts.

        Signal handlers registered:
        - track_approval_status_change (pre_save)
        - handle_ppa_approval_workflow (post_save)
        - sync_workitem_to_ppa (post_save)
        """
        import monitoring.signals  # noqa: F401
