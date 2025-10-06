"""
Template tags for Communities AI features.

Provides filters for displaying AI predictions in templates.
"""

from django import template

register = template.Library()


@register.filter(name='get_item')
def get_item(dictionary, key):
    """
    Get item from dictionary by key.

    Usage in template:
        {{ my_dict|get_item:'key_name' }}
    """
    if not dictionary or not isinstance(dictionary, dict):
        return None
    return dictionary.get(key)


@register.filter(name='percentage')
def percentage(value, decimals=0):
    """
    Convert float to percentage string.

    Usage:
        {{ 0.85|percentage }}  -> "85%"
        {{ 0.8567|percentage:1 }}  -> "85.7%"
    """
    if value is None:
        return "N/A"

    try:
        value = float(value)
        if decimals == 0:
            return f"{int(value * 100)}%"
        else:
            return f"{value * 100:.{decimals}f}%"
    except (ValueError, TypeError):
        return "N/A"


@register.filter(name='priority_color')
def priority_color(score):
    """
    Get Tailwind color class based on priority score.

    Usage:
        <div class="text-{{ score|priority_color }}-600">
    """
    try:
        score = float(score)
        if score >= 0.8:
            return 'red'  # Critical priority
        elif score >= 0.6:
            return 'orange'  # High priority
        elif score >= 0.4:
            return 'yellow'  # Medium priority
        else:
            return 'gray'  # Low priority
    except (ValueError, TypeError):
        return 'gray'


@register.filter(name='priority_label')
def priority_label(score):
    """
    Get priority label based on score.

    Usage:
        {{ score|priority_label }}  -> "Critical", "High", "Medium", "Low"
    """
    try:
        score = float(score)
        if score >= 0.8:
            return 'Critical'
        elif score >= 0.6:
            return 'High'
        elif score >= 0.4:
            return 'Medium'
        else:
            return 'Low'
    except (ValueError, TypeError):
        return 'Unknown'


@register.filter(name='need_icon')
def need_icon(need_category):
    """
    Get Font Awesome icon class for need category.

    Usage:
        <i class="{{ 'Health Infrastructure'|need_icon }}"></i>
    """
    icon_map = {
        'health_infrastructure': 'fa-hospital',
        'education_facilities': 'fa-school',
        'livelihood_programs': 'fa-seedling',
        'water_and_sanitation': 'fa-tint',
        'road_and_transport': 'fa-road',
        'electricity': 'fa-bolt',
        'governance_capacity': 'fa-landmark',
        'cultural_preservation': 'fa-mosque',
        'islamic_education_madrasah': 'fa-quran',
        'peace_and_security': 'fa-shield-alt',
        'land_tenure_security': 'fa-map-marked-alt',
        'financial_inclusion': 'fa-coins',
    }

    key = need_category.lower().replace(' ', '_').replace('(', '').replace(')', '')
    return icon_map.get(key, 'fa-circle')
