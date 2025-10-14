"""
OCM App Configuration
"""
from django.apps import AppConfig


class OcmConfig(AppConfig):
    """Configuration for OCM (Office of the Chief Minister) app"""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ocm'
    verbose_name = 'OCM Aggregation'

    def ready(self):
        """Import signal handlers when app is ready"""
        # Future: Import signals for cache invalidation
        pass
