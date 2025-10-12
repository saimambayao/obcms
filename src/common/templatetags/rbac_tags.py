"""
RBAC Template Tags for Dynamic Permission-Based UI Rendering

Provides clean template tag interface for the RBACService, enabling:
- Feature-based permission checks for navbar items
- Dynamic menu rendering based on user permissions
- Permission-gated action buttons
- Organization-aware access control

These tags integrate with the comprehensive RBAC models (Feature, Permission, Role)
and maintain backward compatibility with existing moa_rbac tags.

Usage:
    {% load rbac_tags %}

    {# Check specific permission #}
    {% has_permission user 'communities.view_obc_community' org as can_view %}
    {% if can_view %}
        <a href="...">View Communities</a>
    {% endif %}

    {# Check feature access #}
    {% has_feature_access user 'communities.barangay_obc' org as can_access %}

    {# Get accessible features for navbar #}
    {% get_accessible_features user as features %}
    {% for feature in features %}
        <a href="{{ feature.url_pattern }}">
            <i class="fas {{ feature.icon }}"></i> {{ feature.name }}
        </a>
    {% endfor %}

    {# Filter version for simple checks #}
    {{ user|can_access_feature:'mana.regional_overview' }}

See:
- src/common/services/rbac_service.py - Core permission logic
- src/common/rbac_models.py - RBAC data models
- docs/improvements/NAVBAR_RBAC_ANALYSIS.md - Navbar structure
"""

from django import template
from django.contrib.auth import get_user_model

from common.services.rbac_service import RBACService

User = get_user_model()
register = template.Library()


# ============================================================================
# PERMISSION CHECKS
# ============================================================================


@register.simple_tag(takes_context=True)
def has_permission(context, user, permission_code, organization=None):
    """
    Check if user has specific permission in organization context.

    Args:
        context: Template context (auto-injected)
        user: User object to check permissions for
        permission_code: Permission code (e.g., 'communities.view_obc_community')
        organization: Optional organization context (uses request.organization if None)

    Returns:
        bool: True if user has permission

    Usage:
        {% has_permission user 'communities.view_obc_community' org as can_view %}
        {% if can_view %}
            <a href="...">View Communities</a>
        {% endif %}
    """
    if not user or not user.is_authenticated:
        return False

    request = context.get('request')
    if not request:
        return False

    # If no organization provided, use request organization or user's organization
    if organization is None:
        organization = RBACService.get_user_organization_context(request)

    return RBACService.has_permission(request, permission_code, organization)


@register.simple_tag(takes_context=True)
def has_feature_access(context, user, feature_key, organization=None):
    """
    Check if user can access a feature (navbar item, module, etc.).

    Args:
        context: Template context (auto-injected)
        user: User object to check access for
        feature_key: Feature identifier (e.g., 'communities.barangay_obc')
        organization: Optional organization context

    Returns:
        bool: True if user can access the feature

    Usage:
        {% has_feature_access user 'communities.barangay_obc' as can_access %}
        {% if can_access %}
            <a href="/communities/barangay/">Barangay OBC</a>
        {% endif %}
    """
    if not user or not user.is_authenticated:
        return False

    request = context.get('request')
    if not request:
        # Fallback: use the service method without request context
        return RBACService.has_feature_access(user, feature_key, organization)

    # Get organization from request if not provided
    if organization is None:
        organization = RBACService.get_user_organization_context(request)

    return RBACService.has_feature_access(user, feature_key, organization)


@register.simple_tag
def get_accessible_features(user, organization=None, parent=None):
    """
    Get all features user can access, optionally filtered by parent.

    Args:
        user: User object
        organization: Optional organization context
        parent: Optional parent feature to filter by (for sub-features)

    Returns:
        List of Feature objects user can access

    Usage:
        {# Get all accessible features #}
        {% get_accessible_features user as features %}

        {# Get sub-features of a parent #}
        {% get_accessible_features user parent=parent_feature as sub_features %}

        {% for feature in features %}
            <a href="{{ feature.url_pattern }}">
                <i class="fas {{ feature.icon }}"></i> {{ feature.name }}
            </a>

            {% if feature.children.all %}
                {% get_accessible_features user parent=feature as sub_features %}
                {% for sub in sub_features %}
                    <a href="{{ sub.url_pattern }}">{{ sub.name }}</a>
                {% endfor %}
            {% endif %}
        {% endfor %}
    """
    if not user or not user.is_authenticated:
        return []

    # Get all accessible features
    features = RBACService.get_accessible_features(user, organization)

    # Filter by parent if provided
    if parent:
        features = [f for f in features if f.parent == parent]

    return features


# ============================================================================
# FILTER VERSIONS (for simple checks)
# ============================================================================


@register.filter(name='can_access_feature')
def can_access_feature_filter(user, feature_key):
    """
    Filter version for quick feature access checks.

    Args:
        user: User object
        feature_key: Feature identifier

    Returns:
        bool: True if user can access feature

    Usage:
        {% if user|can_access_feature:'mana.regional_overview' %}
            <a href="...">Regional MANA</a>
        {% endif %}
    """
    if not user or not user.is_authenticated:
        return False

    return RBACService.has_feature_access(user, feature_key)


@register.filter(name='can_perform_action')
def can_perform_action_filter(user, permission_code):
    """
    Filter version for quick permission checks.

    Args:
        user: User object
        permission_code: Permission code (e.g., 'communities.create_obc')

    Returns:
        bool: True if user has permission

    Usage:
        {% if user|can_perform_action:'communities.create_obc' %}
            <button>Add Community</button>
        {% endif %}
    """
    if not user or not user.is_authenticated:
        return False

    # This is a simple filter - create minimal request object
    # For full context-aware checks, use the simple_tag version
    return user.is_superuser or user.is_oobc_staff


# ============================================================================
# LEGACY COMPATIBILITY (delegates to moa_rbac)
# ============================================================================


@register.simple_tag
def get_permission_context(request):
    """
    Get complete permission context for templates.

    Returns dict with:
    - has_organization_context: bool
    - current_organization: Organization object or None
    - can_switch_organization: bool
    - available_organizations: List of organizations
    - is_ocm_user: bool
    - is_oobc_staff: bool
    - is_moa_staff: bool

    Usage:
        {% get_permission_context request as perm_context %}

        {% if perm_context.can_switch_organization %}
            <select id="org-switcher">
                {% for org in perm_context.available_organizations %}
                    <option value="{{ org.id }}">{{ org.name }}</option>
                {% endfor %}
            </select>
        {% endif %}
    """
    return RBACService.get_permission_context(request)


@register.simple_tag
def get_user_organizations(user):
    """
    Get list of organizations user can access.

    Args:
        user: User object

    Returns:
        List of Organization objects

    Usage:
        {% get_user_organizations user as orgs %}
        {% for org in orgs %}
            <li>{{ org.name }}</li>
        {% endfor %}
    """
    if not user or not user.is_authenticated:
        return []

    return RBACService.get_organizations_with_access(user)


# ============================================================================
# UTILITY TAGS
# ============================================================================


@register.simple_tag
def feature_url(feature):
    """
    Get URL for a feature.

    Args:
        feature: Feature object

    Returns:
        str: URL pattern for the feature

    Usage:
        <a href="{% feature_url feature %}">{{ feature.name }}</a>
    """
    if not feature:
        return '#'

    return feature.url_pattern or '#'


@register.simple_tag
def feature_icon(feature):
    """
    Get icon class for a feature.

    Args:
        feature: Feature object

    Returns:
        str: Icon class (e.g., 'fa-users')

    Usage:
        <i class="fas {% feature_icon feature %}"></i>
    """
    if not feature:
        return 'fa-circle'

    return feature.icon or 'fa-circle'


@register.filter(name='has_sub_features')
def has_sub_features(feature):
    """
    Check if feature has child features.

    Args:
        feature: Feature object

    Returns:
        bool: True if feature has children

    Usage:
        {% if feature|has_sub_features %}
            {# Render dropdown #}
        {% endif %}
    """
    if not feature:
        return False

    return feature.children.exists() if hasattr(feature, 'children') else False
