"""
Deprecation Warnings for Legacy Models

This module provides deprecation warning decorators and utilities for legacy model usage.

IMPORTANT: The following models are marked as ABSTRACT and cannot be used:
- StaffTask (use WorkItem with work_type='task')
- Event (use WorkItem with work_type='activity')
- ProjectWorkflow (use WorkItem with work_type='project')

All database records have been migrated to WorkItem.
See: docs/refactor/WORKITEM_MIGRATION_COMPLETE.md
"""

import warnings
import functools
from typing import Callable


class LegacyModelWarning(DeprecationWarning):
    """Custom warning for deprecated legacy models that are now abstract."""
    pass


def warn_legacy_model_usage(model_name: str, replacement: str = "WorkItem") -> None:
    """
    Issue a deprecation warning for legacy model usage.

    Args:
        model_name: Name of the deprecated model (e.g., "StaffTask", "Event")
        replacement: Name of the replacement model (default: "WorkItem")
    """
    warnings.warn(
        f"{model_name} is deprecated and marked as ABSTRACT. "
        f"All save/delete operations will raise NotImplementedError. "
        f"Use {replacement} instead. "
        f"See docs/refactor/WORKITEM_MIGRATION_COMPLETE.md for migration details.",
        LegacyModelWarning,
        stacklevel=3,
    )


def warn_abstract_model_access(model_name: str, replacement: str) -> None:
    """
    Issue a warning when an abstract legacy model is accessed.

    Args:
        model_name: Name of the deprecated abstract model
        replacement: Full replacement guidance (e.g., "WorkItem with work_type='task'")
    """
    warnings.warn(
        f"{model_name} is deprecated and will be removed in version 3.0. "
        f"Use {replacement} instead. "
        f"See: docs/refactor/WORKITEM_MIGRATION_COMPLETE.md",
        LegacyModelWarning,
        stacklevel=3,
    )


# Enable warnings in development
warnings.simplefilter('always', LegacyModelWarning)


def deprecated_view(model_name: str, replacement_url: str = None) -> Callable:
    """
    Decorator to mark a view function as deprecated.

    Args:
        model_name: Name of the deprecated model this view uses
        replacement_url: URL pattern for the replacement view (optional)

    Example:
        @deprecated_view("StaffTask", replacement_url="work-items:list")
        def staff_task_list(request):
            # Legacy view code...
            pass
    """

    def decorator(view_func: Callable) -> Callable:
        @functools.wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Issue deprecation warning
            message = (
                f"View '{view_func.__name__}' uses deprecated {model_name} model. "
                f"This view is maintained for backward compatibility only. "
            )

            if replacement_url:
                message += f"Use '{replacement_url}' instead. "

            message += (
                "See docs/refactor/LEGACY_CODE_DEPRECATION_PLAN.md for details."
            )

            warnings.warn(
                message,
                DeprecationWarning,
                stacklevel=2,
            )

            # Execute the original view
            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator


# Legacy model names
LEGACY_STAFF_TASK = "StaffTask"
LEGACY_EVENT = "Event"
LEGACY_PROJECT_WORKFLOW = "ProjectWorkflow"
LEGACY_TASK_TEMPLATE = "TaskTemplate"
LEGACY_TASK_TEMPLATE_ITEM = "TaskTemplateItem"
