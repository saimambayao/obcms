"""Additional template filters for text formatting and utilities."""

from collections.abc import Mapping, Sequence
from typing import Any, Optional

from django import template

register = template.Library()


@register.filter(name="underscore_to_space")
def underscore_to_space(value: Optional[str]) -> str:
    """Convert underscores to spaces for friendlier display labels."""

    if not isinstance(value, str):
        return value
    return value.replace("_", " ")


@register.filter(name="get_item")
def get_item(container: Any, key: Any) -> Any:
    """Safely retrieve ``container[key]`` from mappings or sequences."""

    if container is None:
        return ""

    if isinstance(container, Mapping):
        return container.get(key, "")

    try:
        return container[key]  # type: ignore[index]
    except (IndexError, KeyError, TypeError):
        return ""


@register.filter(name='mul')
def multiply(value, arg):
    """Multiply the value by the argument.

    Usage: {{ value|mul:arg }}
    Example: {{ 5|mul:3 }} returns 15
    """
    try:
        return int(value) * int(arg)
    except (ValueError, TypeError):
        return 0


@register.filter(name='sub')
def subtract(value, arg):
    """Subtract the argument from the value.

    Usage: {{ value|sub:arg }}
    Example: {{ 10|sub:3 }} returns 7
    """
    try:
        return int(value) - int(arg)
    except (ValueError, TypeError):
        return 0


@register.filter(name='div')
def divide(value, arg):
    """Divide the value by the argument.

    Usage: {{ value|div:arg }}
    Example: {{ 10|div:2 }} returns 5
    """
    try:
        if int(arg) == 0:
            return 0
        return int(value) // int(arg)
    except (ValueError, TypeError):
        return 0
