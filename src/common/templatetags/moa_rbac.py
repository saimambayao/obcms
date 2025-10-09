"""
Template tags for MOA RBAC (Role-Based Access Control) system.

This module provides comprehensive template tags for checking MOA permissions
and filtering data by user's MOA organization.

Usage in templates:
    {% load moa_rbac %}

    {% is_moa_focal_user user as is_focal %}
    {% if is_focal %}
        <p>You are an MOA focal user</p>
    {% endif %}

    {% can_manage_moa user organization as can_manage %}
    {% if can_manage %}
        <a href="{% url 'edit_org' %}">Edit Organization</a>
    {% endif %}
"""

from django import template
from django.db.models import QuerySet

register = template.Library()


@register.simple_tag
def is_moa_focal_user(user):
    """
    Check if user is an MOA focal user.

    Args:
        user: User instance

    Returns:
        bool: True if user is MOA focal user with assigned organization

    Example (as tag):
        {% is_moa_focal_user user as is_focal %}
        {% if is_focal %}
            <p>Welcome, MOA focal user!</p>
        {% endif %}

    Example (as filter):
        {% if user|is_moa_focal_user_filter %}
            <p>Welcome, MOA focal user!</p>
        {% endif %}
    """
    if not user or not user.is_authenticated:
        return False

    return (user.is_moa_staff and
            user.moa_organization is not None and
            user.is_approved)


@register.filter
def is_moa_focal_user_filter(user):
    """Filter alias for is_moa_focal_user."""
    return is_moa_focal_user(user)


@register.simple_tag
def can_manage_moa(user, organization):
    """
    Check if user can manage the given MOA organization.

    Args:
        user: User instance
        organization: Organization instance or ID

    Returns:
        bool: True if user can edit this organization

    Example:
        {% can_manage_moa user organization as can_manage %}
        {% if can_manage %}
            <button>Edit Organization</button>
        {% endif %}
    """
    if not user or not user.is_authenticated:
        return False

    # Superuser can manage any organization
    if user.is_superuser:
        return True

    # OOBC staff can manage any organization
    if user.is_oobc_staff:
        return True

    # MOA staff can only manage their own organization
    if user.is_moa_staff:
        # Handle both Organization instances and IDs
        if hasattr(organization, 'id'):
            return user.owns_moa_organization(organization.id)
        else:
            return user.owns_moa_organization(organization)

    return False


@register.simple_tag
def can_manage_ppa(user, ppa):
    """
    Check if user can manage (edit/delete) the given PPA.

    Args:
        user: User instance
        ppa: MonitoringEntry (PPA) instance

    Returns:
        bool: True if user can edit/delete this PPA

    Example:
        {% can_manage_ppa user ppa as can_manage %}
        {% if can_manage %}
            <a href="{% url 'ppa_edit' ppa.id %}">Edit PPA</a>
            <button class="delete-btn">Delete PPA</button>
        {% endif %}
    """
    if not user or not user.is_authenticated:
        return False

    # Superuser can manage any PPA
    if user.is_superuser:
        return True

    # OOBC staff can manage any PPA
    if user.is_oobc_staff:
        return True

    # MOA staff can only manage their own MOA's PPAs
    if user.is_moa_staff:
        return user.can_edit_ppa(ppa)

    return False


@register.simple_tag
def filter_user_ppas(user, ppas_queryset):
    """
    Filter PPAs queryset to only show PPAs accessible to user.

    For MOA users: Returns only PPAs from their MOA
    For OOBC/Superuser: Returns all PPAs

    Args:
        user: User instance
        ppas_queryset: QuerySet of MonitoringEntry objects

    Returns:
        QuerySet: Filtered PPAs

    Example:
        {% filter_user_ppas user all_ppas as user_ppas %}
        {% for ppa in user_ppas %}
            <li>{{ ppa.title }}</li>
        {% endfor %}
    """
    if not user or not user.is_authenticated:
        return ppas_queryset.none()

    # Superuser and OOBC staff see all PPAs
    if user.is_superuser or user.is_oobc_staff:
        return ppas_queryset

    # MOA staff see only their own MOA's PPAs
    if user.is_moa_staff and user.moa_organization:
        return ppas_queryset.filter(implementing_moa=user.moa_organization)

    # Default: return empty queryset
    return ppas_queryset.none()


@register.simple_tag
def get_user_moa(user):
    """
    Get the user's MOA organization.

    Args:
        user: User instance

    Returns:
        Organization instance or None

    Example:
        {% get_user_moa user as moa %}
        {% if moa %}
            <p>Your MOA: {{ moa.name }}</p>
        {% else %}
            <p class="warning">No MOA assigned</p>
        {% endif %}
    """
    if not user or not user.is_authenticated:
        return None

    if user.is_moa_staff:
        return user.moa_organization

    return None


@register.simple_tag
def can_view_ppa_budget(user, ppa):
    """
    Check if user can view budget information for the given PPA.

    Budget information is sensitive and restricted to:
    - Superusers (all budgets)
    - OOBC staff (all budgets)
    - MOA staff (only their own MOA's PPA budgets)

    Args:
        user: User instance
        ppa: MonitoringEntry (PPA) instance

    Returns:
        bool: True if user can view budget information

    Example:
        {% can_view_ppa_budget user ppa as can_view_budget %}
        {% if can_view_budget %}
            <div class="budget-section">
                <h3>Budget Information</h3>
                <p>Allocation: {{ ppa.budget_allocation }}</p>
                <p>Expenditure: {{ ppa.actual_expenditure }}</p>
            </div>
        {% else %}
            <p class="text-muted">Budget information restricted</p>
        {% endif %}
    """
    if not user or not user.is_authenticated:
        return False

    # Superuser can view all budgets
    if user.is_superuser:
        return True

    # OOBC staff can view all budgets
    if user.is_oobc_staff:
        return True

    # MOA staff can view budget only for their own MOA's PPAs
    if user.is_moa_staff:
        return user.can_view_ppa(ppa)

    return False


# Additional helper tags for comprehensive template support


@register.filter
def has_moa_organization(user):
    """
    Filter to check if user has an assigned MOA organization.

    Args:
        user: User instance

    Returns:
        bool: True if user has MOA organization assigned

    Example:
        {% if user|has_moa_organization %}
            <p>MOA: {{ user.moa_organization.name }}</p>
        {% else %}
            <div class="alert alert-warning">
                No MOA organization assigned. Contact administrator.
            </div>
        {% endif %}
    """
    if not user or not user.is_authenticated:
        return False

    return user.is_moa_staff and user.moa_organization is not None


@register.simple_tag
def can_view_communities(user):
    """
    Check if user can view OBC communities.

    All authenticated users can view OBC communities (public data).

    Args:
        user: User instance

    Returns:
        bool: True if user can view communities

    Example:
        {% can_view_communities user as can_view %}
        {% if can_view %}
            <a href="{% url 'communities_list' %}">Browse Communities</a>
        {% endif %}
    """
    if not user or not user.is_authenticated:
        return False

    # All authenticated users can view communities
    return True


@register.simple_tag
def can_edit_communities(user):
    """
    Check if user can edit OBC communities.

    Only OOBC staff can edit communities (MOA users have view-only access).

    Args:
        user: User instance

    Returns:
        bool: True if user can edit communities

    Example:
        {% can_edit_communities user as can_edit %}
        {% if can_edit %}
            <a href="{% url 'community_create' %}">Add Community</a>
        {% else %}
            <p class="text-muted">View-only access</p>
        {% endif %}
    """
    if not user or not user.is_authenticated:
        return False

    # Only superuser and OOBC staff can edit communities
    return user.is_superuser or user.is_oobc_staff


@register.simple_tag
def can_access_mana(user):
    """
    Check if user can access MANA (Mapping and Needs Assessment) module.

    MANA is restricted to OOBC staff only.

    Args:
        user: User instance

    Returns:
        bool: True if user can access MANA

    Example (as tag):
        {% can_access_mana user as can_access %}
        {% if can_access %}
            <li><a href="{% url 'mana_dashboard' %}">MANA Assessments</a></li>
        {% endif %}

    Example (as filter):
        {% if user|can_access_mana_filter %}
            <li><a href="{% url 'mana_dashboard' %}">MANA Assessments</a></li>
        {% endif %}
    """
    if not user or not user.is_authenticated:
        return False

    # Only superuser and OOBC staff can access MANA
    return user.is_superuser or user.is_oobc_staff


@register.filter
def can_access_mana_filter(user):
    """Filter alias for can_access_mana."""
    return can_access_mana(user)


@register.simple_tag
def can_create_ppa(user):
    """
    Check if user can create new PPAs.

    Both OOBC staff and MOA staff can create PPAs.

    Args:
        user: User instance

    Returns:
        bool: True if user can create PPAs

    Example:
        {% can_create_ppa user as can_create %}
        {% if can_create %}
            <a href="{% url 'ppa_create' %}" class="btn btn-primary">
                Create New PPA
            </a>
        {% endif %}
    """
    if not user or not user.is_authenticated:
        return False

    # Superuser, OOBC staff, and MOA staff can create PPAs
    return user.is_superuser or user.is_oobc_staff or user.is_moa_staff


@register.filter
def can_create_ppa_filter(user):
    """Filter alias for can_create_ppa."""
    return can_create_ppa(user)


@register.simple_tag
def can_manage_work_item(user, work_item):
    """
    Check if user can manage (edit/delete) the given work item.

    Args:
        user: User instance
        work_item: WorkItem instance

    Returns:
        bool: True if user can manage this work item

    Example:
        {% can_manage_work_item user work_item as can_manage %}
        {% if can_manage %}
            <button class="edit-btn">Edit Work Item</button>
        {% endif %}
    """
    if not user or not user.is_authenticated:
        return False

    # Superuser can manage any work item
    if user.is_superuser:
        return True

    # OOBC staff can manage any work item
    if user.is_oobc_staff:
        return True

    # MOA staff can manage work items linked to their PPAs
    if user.is_moa_staff:
        return user.can_edit_work_item(work_item)

    return False


@register.simple_tag
def filter_user_work_items(user, work_items_queryset):
    """
    Filter work items queryset to only show items accessible to user.

    For MOA users: Returns only work items linked to their MOA's PPAs
    For OOBC/Superuser: Returns all work items

    Args:
        user: User instance
        work_items_queryset: QuerySet of WorkItem objects

    Returns:
        QuerySet: Filtered work items

    Example:
        {% filter_user_work_items user all_work_items as user_items %}
        {% for item in user_items %}
            <li>{{ item.title }}</li>
        {% endfor %}
    """
    if not user or not user.is_authenticated:
        return work_items_queryset.none()

    # Superuser and OOBC staff see all work items
    if user.is_superuser or user.is_oobc_staff:
        return work_items_queryset

    # MOA staff see only work items linked to their PPAs
    if user.is_moa_staff and user.moa_organization:
        # Filter by ppa_category and implementing_moa via isolation fields
        return work_items_queryset.filter(
            ppa_category='moa_ppa',
            moa_id=user.moa_organization.id
        )

    # Default: return empty queryset
    return work_items_queryset.none()


@register.simple_tag
def user_moa_name(user):
    """
    Get the name of user's MOA organization (convenience tag).

    Args:
        user: User instance

    Returns:
        str: MOA organization name or empty string

    Example (as tag):
        {% user_moa_name user %}

    Example (as filter):
        {{ user|user_moa_name_filter }}
    """
    if not user or not user.is_authenticated:
        return ""

    if user.is_moa_staff and user.moa_organization:
        return user.moa_organization.name

    return ""


@register.filter
def user_moa_name_filter(user):
    """Filter alias for user_moa_name."""
    return user_moa_name(user)


@register.filter
def can_access_oobc_management(user):
    """
    Check if user can access OOBC Management module.

    OOBC Management is restricted to OOBC staff only (includes calendar, staff management, etc.).

    Args:
        user: User instance

    Returns:
        bool: True if user can access OOBC Management

    Example:
        {% if user|can_access_oobc_management %}
            <li><a href="{% url 'oobc_management_home' %}">OOBC Management</a></li>
        {% endif %}
    """
    if not user or not user.is_authenticated:
        return False

    # Only superuser and OOBC staff can access OOBC Management
    return user.is_superuser or user.is_oobc_staff


@register.filter
def get_coordination_label(user):
    """
    Get appropriate label for Coordination menu based on user type.

    MOA users see "My MOA Profile" (direct link to their org).
    OOBC staff see "Coordination" (full coordination module).

    Args:
        user: User instance

    Returns:
        str: Menu label

    Example:
        <a href="...">{{ user|get_coordination_label }}</a>
    """
    if not user or not user.is_authenticated:
        return "Coordination"

    if user.is_moa_staff and user.moa_organization:
        return "My MOA Profile"

    return "Coordination"


@register.simple_tag
def get_coordination_url(user):
    """
    Get appropriate URL for Coordination menu based on user type.

    MOA users go directly to their organization detail page.
    OOBC staff go to the organizations list (full coordination module).

    Args:
        user: User instance

    Returns:
        str: URL path

    Example:
        <a href="{% get_coordination_url user %}">Coordination</a>
    """
    if not user or not user.is_authenticated:
        return "/coordination/organizations/"

    if user.is_moa_staff and user.moa_organization:
        # Direct link to their MOA organization detail page
        return f"/coordination/organizations/{user.moa_organization.id}/"

    # OOBC staff see full coordination module
    return "/coordination/organizations/"


@register.filter
def can_access_geographic_data(user):
    """
    Check if user can access Geographic Data module.

    Geographic data management is restricted to OOBC staff only.

    Args:
        user: User instance

    Returns:
        bool: True if user can access Geographic Data

    Example:
        {% if user|can_access_geographic_data %}
            <li><a href="{% url 'geographic_data' %}">Geographic Data</a></li>
        {% endif %}
    """
    if not user or not user.is_authenticated:
        return False

    # Only superuser and OOBC staff can access Geographic Data
    return user.is_superuser or user.is_oobc_staff


@register.filter
def can_access_oobc_initiatives(user):
    """
    Check if user can access OOBC Initiatives.

    OOBC Initiatives are internal programs managed by OOBC.

    Args:
        user: User instance

    Returns:
        bool: True if user can access OOBC Initiatives

    Example:
        {% if user|can_access_oobc_initiatives %}
            <li><a href="{% url 'oobc_initiatives' %}">OOBC Initiatives</a></li>
        {% endif %}
    """
    if not user or not user.is_authenticated:
        return False

    # Only superuser and OOBC staff can access OOBC Initiatives
    return user.is_superuser or user.is_oobc_staff


@register.filter
def can_access_me_analytics(user):
    """
    Check if user can access M&E Analytics dashboard.

    M&E Analytics is restricted to OOBC staff for strategic analysis.

    Args:
        user: User instance

    Returns:
        bool: True if user can access M&E Analytics

    Example:
        {% if user|can_access_me_analytics %}
            <li><a href="{% url 'me_analytics' %}">M&E Analytics</a></li>
        {% endif %}
    """
    if not user or not user.is_authenticated:
        return False

    # Only superuser and OOBC staff can access M&E Analytics
    return user.is_superuser or user.is_oobc_staff


@register.filter
def can_access_policies(user):
    """
    Check if user can access Policy Recommendations.

    MOA users can access policies/programs/services (filtered to their MOA only).
    OOBC staff can access all policies.

    Args:
        user: User instance

    Returns:
        bool: True if user can access Policies

    Example:
        {% if user|can_access_policies %}
            <li><a href="{% url 'policies' %}">Policies</a></li>
        {% endif %}
    """
    if not user or not user.is_authenticated:
        return False

    # MOA users CAN access policies (filtered to their MOA's policies only)
    # OOBC staff can access all policies
    return user.is_superuser or user.is_oobc_staff or user.is_moa_staff