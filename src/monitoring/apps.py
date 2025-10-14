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
        - calendar_cache_invalidator (post_save, post_delete for MonitoringEntry)
        """
        import monitoring.signals  # noqa: F401

        # Connect MonitoringEntry signals to common calendar cache invalidator
        # This avoids circular dependency between common and monitoring apps
        from common.signals import connect_monitoring_signals
        connect_monitoring_signals()

        # Register MonitoringEntry with auditlog (avoiding circular dependency)
        from auditlog.registry import auditlog
        auditlog.register(
            self.get_model('MonitoringEntry'),
            include_fields=[
                'title',
                'category',
                'status',
                'approval_status',
                'budget_allocation',
                'budget_obc_allocation',
                'implementing_moa',
                'lead_organization',
                'fiscal_year',
                'plan_year',
                'funding_source',
                'appropriation_class',
            ],
            serialize_data=True,
        )
