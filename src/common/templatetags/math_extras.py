"""Custom math template filters for Django templates."""

from decimal import Decimal, InvalidOperation

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
        num = float(value) if value is not None else 0
        formatted = "{:,.2f}".format(num)
        return f"₱ {formatted}"
    except (ValueError, TypeError):
        return "₱ 0.00"


@register.filter(name='percentage_of')
def percentage_of(value, total):
    """Return the percentage (value / total * 100) safely for Decimal values."""
    try:
        total_decimal = Decimal(str(total))
        if total_decimal == 0:
            return Decimal('0')
        value_decimal = Decimal(str(value)) if value is not None else Decimal('0')
        return (value_decimal / total_decimal) * Decimal('100')
    except (InvalidOperation, TypeError, ValueError):
        return Decimal('0')
