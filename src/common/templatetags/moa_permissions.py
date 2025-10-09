"""
Template tags for MOA RBAC system.

Provides permission checks in templates.
"""

from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def user_can_edit_organization(context, organization):
    """Check if current user can edit the organization."""
    user = context.get('request').user if 'request' in context else context.get('user')

    if not user or not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    if user.is_oobc_staff:
        return True

    if user.is_moa_staff:
        return user.owns_moa_organization(organization)

    return False


@register.simple_tag(takes_context=True)
def user_can_edit_ppa(context, ppa):
    """Check if current user can edit the PPA."""
    user = context.get('request').user if 'request' in context else context.get('user')

    if not user or not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    if user.is_oobc_staff:
        return True

    if user.is_moa_staff:
        return user.can_edit_ppa(ppa)

    return False


@register.simple_tag(takes_context=True)
def user_can_view_ppa(context, ppa):
    """Check if current user can view the PPA."""
    user = context.get('request').user if 'request' in context else context.get('user')

    if not user or not user.is_authenticated:
        return False

    if user.is_superuser or user.is_oobc_staff:
        return True

    if user.is_moa_staff:
        return user.can_view_ppa(ppa)

    return False


@register.simple_tag(takes_context=True)
def user_can_delete_ppa(context, ppa):
    """Check if current user can delete the PPA."""
    # Same permissions as edit
    return user_can_edit_ppa(context, ppa)


@register.simple_tag(takes_context=True)
def user_can_create_ppa(context):
    """Check if current user can create PPAs."""
    user = context.get('request').user if 'request' in context else context.get('user')

    if not user or not user.is_authenticated:
        return False

    # Superusers, OOBC staff, and MOA staff can all create PPAs
    return user.is_superuser or user.is_oobc_staff or user.is_moa_staff


@register.simple_tag(takes_context=True)
def user_can_access_mana(context):
    """Check if current user can access MANA assessments."""
    user = context.get('request').user if 'request' in context else context.get('user')

    if not user or not user.is_authenticated:
        return False

    # Only OOBC staff can access MANA
    return user.is_superuser or user.is_oobc_staff
