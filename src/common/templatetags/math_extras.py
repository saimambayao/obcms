"""Custom math template filters for Django templates."""

from django import template

register = template.Library()


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


@register.filter(name='abs')
def absolute(value):
    """Return the absolute value.

    Usage: {{ value|abs }}
    Example: {{ -5|abs }} returns 5
    """
    try:
        return abs(value)
    except (ValueError, TypeError):
        return 0


@register.filter(name='currency_php')
def currency_php(value):
    """Format a number as Philippine Peso currency with comma separators.

    Usage: {{ value|currency_php }}
    Example: {{ 2003400|currency_php }} returns "₱ 2,003,400.00"
    """
    try:
        # Convert to float first
        num = float(value) if value is not None else 0
        # Format with thousand separators and 2 decimal places
        formatted = "{:,.2f}".format(num)
        return f"₱ {formatted}"
    except (ValueError, TypeError):
        return "₱ 0.00"


@register.filter(name='percentage_of')
def percentage_of(value, total):
    """Calculate percentage of value relative to total.

    Usage: {{ value|percentage_of:total }}
    Example: {{ 50|percentage_of:200 }} returns 25.0
    """
    try:
        val = float(value) if value is not None else 0
        tot = float(total) if total is not None else 0
        if tot == 0:
            return 0
        return (val / tot) * 100
    except (ValueError, TypeError, ZeroDivisionError):
        return 0
