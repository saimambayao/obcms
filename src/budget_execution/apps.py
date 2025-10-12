from django.apps import AppConfig


class BudgetExecutionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'budget_execution'
    verbose_name = 'Budget Execution'
    
    def ready(self):
        import budget_execution.signals  # noqa
