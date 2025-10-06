"""Template tags for task management views."""

from django import template
from django.urls import NoReverseMatch, reverse

register = template.Library()


@register.filter
def lookup(dictionary, key):
    """
    Template filter to lookup a dictionary value by key.

    Usage in templates:
        {{ tasks_by_phase|lookup:phase_key }}
    """
    if dictionary is None:
        return None
    return dictionary.get(key, [])


@register.filter
def domain_color(domain_code):
    """
    Return Tailwind color class for domain.

    Usage:
        {{ task.domain|domain_color }}
    """
    colors = {
        "mana": "emerald",
        "coordination": "blue",
        "policy": "purple",
        "monitoring": "amber",
        "services": "rose",
        "general": "gray",
    }
    return colors.get(domain_code, "gray")


@register.filter
def status_color(status_code):
    """
    Return Tailwind color class for task status.

    Usage:
        {{ task.status|status_color }}
    """
    colors = {
        "not_started": "gray",
        "in_progress": "blue",
        "on_hold": "amber",
        "at_risk": "rose",
        "completed": "emerald",
        "cancelled": "gray",
    }
    return colors.get(status_code, "gray")


@register.filter
def priority_color(priority_code):
    """
    Return Tailwind color class for task priority.

    Usage:
        {{ task.priority|priority_color }}
    """
    colors = {
        "critical": "rose",
        "high": "amber",
        "medium": "blue",
        "low": "gray",
    }
    return colors.get(priority_code, "gray")


@register.simple_tag
def task_action_url(task, action="detail"):
    """Return the appropriate URL for WorkItem-backed tasks with legacy fallbacks."""

    work_item_id = getattr(task, "work_item_id", None)
    if work_item_id:
        try:
            if action == "detail":
                return reverse("common:work_item_detail", kwargs={"pk": work_item_id})
            if action == "edit":
                return reverse("common:work_item_edit", kwargs={"pk": work_item_id})
            if action == "delete":
                return reverse("common:work_item_delete", kwargs={"pk": work_item_id})
            if action == "modal":
                return reverse(
                    "common:work_item_modal", kwargs={"work_item_id": work_item_id}
                )
        except NoReverseMatch:
            # Fall through to legacy URLs when namespace not available
            pass

    task_id = getattr(task, "pk", None)
    if task_id is None:
        return ""

    try:
        if action in {"detail", "modal", "edit"}:
            return reverse("common:staff_task_modal", args=[task_id])
        if action == "delete":
            return reverse("common:staff_task_delete", args=[task_id])
    except NoReverseMatch:
        return ""

    return ""
