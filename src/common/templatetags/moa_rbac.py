"""
Template tags and filters for the MOA RBAC experience.

Keeps backwards compatibility for legacy `{% load moa_rbac %}` directives
while delegating to the newer `moa_permissions` utilities and exposing the
filters used across templates.
"""

from django import template

from . import moa_permissions as base_tags

register = template.Library()


def _get_authenticated_user(user):
    """Return the authenticated user object or ``None``."""
    if not user:
        return None
    is_authenticated = getattr(user, "is_authenticated", False)
    if callable(is_authenticated):
        is_authenticated = is_authenticated()
    if not is_authenticated:
        return None
    return user


def _has_staff_or_superpowers(user):
    """Helper that checks for superuser or OOBC staff privileges."""
    return bool(
        getattr(user, "is_superuser", False)
        or getattr(user, "is_oobc_staff", False)
    )


# ---------------------------------------------------------------------------
# Filters
# ---------------------------------------------------------------------------

@register.simple_tag
def is_moa_focal_user(user):
    """Simple-tag variant to mirror the legacy implementation."""
    user = _get_authenticated_user(user)
    if not user:
        return False
    return bool(
        getattr(user, "is_moa_staff", False)
        and getattr(user, "is_approved", False)
        and getattr(user, "moa_organization", None)
    )


@register.filter(name="is_moa_focal_user_filter")
def is_moa_focal_user_filter(user):
    """Filter alias for the `is_moa_focal_user` simple tag."""
    return is_moa_focal_user(user)


@register.filter(name="user_moa_name_filter")
def user_moa_name_filter(user):
    """Return the preferred MOA organization name for the user."""
    user = _get_authenticated_user(user)
    if not user:
        return ""
    moa_org = getattr(user, "moa_organization", None)
    if moa_org and getattr(moa_org, "name", ""):
        return moa_org.name
    return ""


@register.filter(name="can_create_ppa_filter")
def can_create_ppa_filter(user):
    """Determine whether the user can create or manage PPAs."""
    user = _get_authenticated_user(user)
    if not user:
        return False
    if getattr(user, "is_superuser", False):
        return True
    if getattr(user, "is_oobc_staff", False):
        return True
    return getattr(user, "is_moa_staff", False)


# ---------------------------------------------------------------------------
# Simple tags
# ---------------------------------------------------------------------------

@register.simple_tag
def can_manage_moa(user, organization):
    """Return True if user can manage the supplied organization."""
    user = _get_authenticated_user(user)
    if not user or organization is None:
        return False
    if _has_staff_or_superpowers(user):
        return True
    if getattr(user, "is_moa_staff", False):
        if hasattr(organization, "id"):
            return user.owns_moa_organization(organization.id)
        return user.owns_moa_organization(str(organization))
    return False


@register.simple_tag
def can_manage_ppa(user, ppa):
    """Return True if user can manage (edit/delete) the supplied PPA."""
    user = _get_authenticated_user(user)
    if not user or ppa is None:
        return False
    if _has_staff_or_superpowers(user):
        return True
    if getattr(user, "is_moa_staff", False):
        return user.can_edit_ppa(ppa)
    return False


@register.simple_tag
def filter_user_ppas(user, ppas_queryset):
    """Filter a PPA queryset so MOA users only see their own entries."""
    user = _get_authenticated_user(user)
    if not user:
        return ppas_queryset.none()
    if _has_staff_or_superpowers(user):
        return ppas_queryset
    if getattr(user, "is_moa_staff", False) and getattr(user, "moa_organization", None):
        return ppas_queryset.filter(implementing_moa=user.moa_organization)
    return ppas_queryset.none()


@register.simple_tag
def get_user_moa(user):
    """Return the MOA organization associated with the user, if any."""
    user = _get_authenticated_user(user)
    if not user:
        return None
    if getattr(user, "is_moa_staff", False):
        return getattr(user, "moa_organization", None)
    return None


@register.simple_tag
def can_view_ppa_budget(user, ppa):
    """Return True if the user can view budget information for the PPA."""
    user = _get_authenticated_user(user)
    if not user or ppa is None:
        return False
    if _has_staff_or_superpowers(user):
        return True
    if getattr(user, "is_moa_staff", False):
        return user.can_view_ppa(ppa)
    return False


@register.simple_tag
def can_manage_work_item(user, work_item):
    """Return True if user can manage the supplied work item."""
    user = _get_authenticated_user(user)
    if not user or work_item is None:
        return False
    if hasattr(user, "can_edit_work_item"):
        return user.can_edit_work_item(work_item)
    return False


@register.simple_tag
def can_access_mana(user):
    """Check if the user can access the MANA module."""
    user = _get_authenticated_user(user)
    if not user:
        return False
    return _has_staff_or_superpowers(user)


@register.filter(name="can_access_mana_filter")
def can_access_mana_filter(user):
    """Filter alias for `can_access_mana`."""
    return can_access_mana(user)


@register.filter(name="has_moa_organization")
def has_moa_organization(user):
    """Return True if the user has a linked MOA organization."""
    user = _get_authenticated_user(user)
    if not user:
        return False
    return bool(
        getattr(user, "is_moa_staff", False)
        and getattr(user, "moa_organization", None)
    )


@register.simple_tag
def can_view_communities(user):
    """All authenticated users can view communities."""
    user = _get_authenticated_user(user)
    return bool(user)


@register.simple_tag
def can_edit_communities(user):
    """Return True if the user can edit community records."""
    user = _get_authenticated_user(user)
    if not user:
        return False
    return _has_staff_or_superpowers(user)


@register.filter(name="can_access_geographic_data")
def can_access_geographic_data(user):
    """
    Return True if the user can reach the geographic data module.

    Geographic data is part of the MANA module and requires mana_access feature.
    """
    user = _get_authenticated_user(user)
    if not user:
        return False

    # Check for mana_access feature using RBAC system
    from common.services.rbac_service import RBACService
    return RBACService.has_feature_access(user, 'mana_access', organization=None)


@register.filter(name="can_access_oobc_initiatives")
def can_access_oobc_initiatives(user):
    """Return True if the user can view OOBC initiatives."""
    user = _get_authenticated_user(user)
    if not user:
        return False
    return _has_staff_or_superpowers(user)


@register.filter(name="can_access_me_analytics")
def can_access_me_analytics(user):
    """
    Return True if the user can view M&E analytics dashboards.

    M&E Analytics is part of the Project Management module and requires
    project_management_access feature.
    """
    user = _get_authenticated_user(user)
    if not user:
        return False

    # Check for project_management_access feature using RBAC system
    from common.services.rbac_service import RBACService
    return RBACService.has_feature_access(user, 'project_management_access', organization=None)


@register.filter(name="can_access_oobc_management")
def can_access_oobc_management(user):
    """Return True if the user can access OOBC management tools."""
    user = _get_authenticated_user(user)
    if not user:
        return False
    return _has_staff_or_superpowers(user)


@register.filter(name="can_access_policies")
def can_access_policies(user):
    """Return True if the user can browse policy recommendations."""
    user = _get_authenticated_user(user)
    if not user:
        return False
    if _has_staff_or_superpowers(user):
        return True
    return getattr(user, "is_moa_staff", False)


@register.simple_tag
def can_create_ppa(user):
    """Return True if the user can create PPAs."""
    return can_create_ppa_filter(user)


@register.simple_tag
def filter_user_work_items(user, work_items_queryset):
    """Filter work items so MOA users only see those linked to their MOA."""
    user = _get_authenticated_user(user)
    if not user:
        return work_items_queryset.none()
    if _has_staff_or_superpowers(user):
        return work_items_queryset
    if getattr(user, "is_moa_staff", False) and getattr(user, "moa_organization", None):
        return work_items_queryset.filter(
            ppa_category="moa_ppa",
            moa_id=user.moa_organization.id,
        )
    return work_items_queryset.none()


@register.simple_tag
def user_moa_name(user):
    """Simple-tag variant mirroring the legacy helper."""
    return user_moa_name_filter(user)


@register.filter(name="get_coordination_label")
def get_coordination_label(user):
    """Return the navigation label for the Coordination menu."""
    user = _get_authenticated_user(user)
    if not user:
        return "Coordination"
    if getattr(user, "is_moa_staff", False) and getattr(user, "moa_organization", None):
        return "MOA Profile"
    return "Coordination"


@register.simple_tag
def get_coordination_url(user):
    """Return the navigation URL for the Coordination menu."""
    user = _get_authenticated_user(user)
    if not user:
        return "/coordination/organizations/"
    if getattr(user, "is_moa_staff", False) and getattr(user, "moa_organization", None):
        return f"/coordination/organizations/{user.moa_organization.id}/"
    return "/coordination/organizations/"


# ---------------------------------------------------------------------------
# Delegated helpers to keep `{% load moa_rbac %}` working with the original
# template tags defined in `moa_permissions`.
# ---------------------------------------------------------------------------


@register.simple_tag(takes_context=True)
def user_can_edit_organization(context, organization):
    """Proxy to the base `user_can_edit_organization` tag."""
    return base_tags.user_can_edit_organization(context, organization)


@register.simple_tag(takes_context=True)
def user_can_edit_ppa(context, ppa):
    """Proxy to the base `user_can_edit_ppa` tag."""
    return base_tags.user_can_edit_ppa(context, ppa)


@register.simple_tag(takes_context=True)
def user_can_view_ppa(context, ppa):
    """Proxy to the base `user_can_view_ppa` tag."""
    return base_tags.user_can_view_ppa(context, ppa)


@register.simple_tag(takes_context=True)
def user_can_delete_ppa(context, ppa):
    """Proxy to the base `user_can_delete_ppa` tag."""
    return base_tags.user_can_delete_ppa(context, ppa)


@register.simple_tag(takes_context=True)
def user_can_create_ppa(context):
    """Proxy to the base `user_can_create_ppa` tag."""
    return base_tags.user_can_create_ppa(context)


@register.simple_tag(takes_context=True)
def user_can_access_mana(context):
    """Proxy to the base `user_can_access_mana` tag."""
    return base_tags.user_can_access_mana(context)
