import warnings
from django.apps import AppConfig


class AiAssistantConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "ai_assistant"
    verbose_name = "AI Assistant"

    def ready(self):
        """
        Called when the AI assistant app is ready.
        Suppress PyTorch JIT warnings for cleaner development output.
        """
        # Suppress PyTorch JIT warnings (cosmetic only)
        # These warnings are harmless but clutter the development console
        warnings.filterwarnings('ignore',
            message='Unable to retrieve source for @torch.jit._overload function',
            category=UserWarning,
            module='torch._jit_internal'
        )
