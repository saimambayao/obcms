"""
Multi-tenant URL Configuration Module

Provides dynamic URL routing for OBCMS/BMMS dual architecture.
Supports both single-tenant (OBCMS) and multi-tenant (BMMS) modes.

URL Patterns:
- OBCMS Mode: /dashboard/, /communities/, /mana/, /coordination/
- BMMS Mode: /moa/{ORG_CODE}/dashboard/, /moa/{ORG_CODE}/communities/, etc.
- OCM Mode: /ocm/dashboard/, /ocm/analytics/ (always available)
"""

from django.urls import path, include, re_path
from django.conf import settings
from django.shortcuts import redirect
from django.views.generic import RedirectView
from django.utils.module_loading import import_string

from obc_management.settings.bmms_config import (
    is_bmms_mode,
    is_obcms_mode,
    get_default_organization_code
)


def get_multi_tenant_urlpatterns():
    """
    Get URL patterns based on current operational mode.

    Returns:
        list: URL patterns for current mode (OBCMS or BMMS)
    """
    if is_obcms_mode():
        return get_obcms_urlpatterns()
    else:
        return get_bmms_urlpatterns()


def get_obcms_urlpatterns():
    """
    Get URL patterns for OBCMS single-tenant mode.

    URL Structure:
    - /dashboard/ → Dashboard
    - /communities/ → Communities module
    - /mana/ → MANA module
    - /coordination/ → Coordination module
    - (current structure maintained)

    Returns:
        list: URL patterns for OBCMS mode
    """
    return [
        # Core application URLs (current structure)
        path("", include("common.urls")),
        path("communities/", include("communities.urls")),
        path("coordination/", include("coordination.urls")),
        path("policies/", include("recommendations.policies.urls")),
        path("monitoring/", include("monitoring.urls")),

        # Planning and Budgeting Modules
        path("planning/", include("planning.urls")),
        path("budget/preparation/", include("budget_preparation.urls")),
        path("budget/execution/", include("budget_execution.urls")),

        # Project Management and Documents
        path("project-management/", include("project_central.urls")),
        path("documents/", include(("recommendations.documents.urls", "documents"), namespace="documents")),
        path("mana/", include(("mana.urls", "mana"), namespace="mana")),

        # OCM Aggregation (always available)
        path("ocm/", include(("ocm.urls", "ocm"), namespace="ocm")),
    ]


def get_bmms_urlpatterns():
    """
    Get URL patterns for BMMS multi-tenant mode.

    URL Structure:
    - /moa/{ORG_CODE}/dashboard/ → Organization-specific dashboard
    - /moa/{ORG_CODE}/communities/ → Organization communities
    - /moa/{ORG_CODE}/mana/ → Organization MANA
    - /moa/{ORG_CODE}/coordination/ → Organization coordination
    - /ocm/dashboard/ → OCM aggregated oversight
    - /ocm/analytics/ → OCM cross-ministry analytics

    Returns:
        list: URL patterns for BMMS mode
    """
    # Organization code pattern (alphanumeric, underscores, hyphens)
    org_pattern = r'(?P<org_code>[A-Za-z0-9_-]+)'

    return [
        # BMMS Multi-tenant Organization URLs
        # /moa/{ORG_CODE}/... patterns
        re_path(rf'^moa/{org_pattern}/', include([
            # Core application URLs with organization context
            path("", include("common.urls")),
            path("communities/", include("communities.urls")),
            path("coordination/", include("coordination.urls")),
            path("policies/", include("recommendations.policies.urls")),
            path("monitoring/", include("monitoring.urls")),

            # Planning and Budgeting Modules
            path("planning/", include("planning.urls")),
            path("budget/preparation/", include("budget_preparation.urls")),
            path("budget/execution/", include("budget_execution.urls")),

            # Project Management and Documents
            path("project-management/", include("project_central.urls")),
            path("documents/", include(("recommendations.documents.urls", "documents"), namespace="documents")),
            path("mana/", include(("mana.urls", "mana"), namespace="mana")),

            # Organization-specific dashboard (default to common dashboard)
            path("", lambda request: redirect("common:dashboard"), name="org_dashboard"),
        ], namespace='moa')),

        # OCM Aggregation Layer (separate from organization URLs)
        path("ocm/", include(("ocm.urls", "ocm"), namespace="ocm")),

        # Root redirect to OCM dashboard for BMMS mode
        path("", lambda request: redirect("ocm:dashboard"), name="bmms_home"),
    ]


def get_organization_urlpatterns():
    """
    Get organization-specific URL patterns for dynamic routing.

    Returns:
        list: URL patterns for organization context routing
    """
    return [
        # Organization switching endpoints
        path('switch-organization/', switch_organization, name='switch_organization'),
        path('switch-organization/<str:org_code>/', switch_organization, name='switch_organization_code'),

        # Organization validation endpoint
        path('validate-organization/<str:org_code>/', validate_organization, name='validate_organization'),

        # Current organization context endpoint
        path('current-organization/', current_organization, name='current_organization'),
    ]


def switch_organization(request, org_code=None):
    """
    Switch current organization context.

    Args:
        request: HTTP request object
        org_code: Target organization code (optional)

    Returns:
        HttpResponse: Redirect to organization dashboard or error page
    """
    # Import here to avoid circular imports
    from common.middleware.organization_context import set_organization_context

    if org_code:
        # Validate organization exists and user has access
        from organizations.models import Organization

        try:
            organization = Organization.objects.get(code=org_code, is_active=True)

            # Check user access permissions
            if not has_organization_access(request.user, organization):
                return redirect('common:page_restricted')

            # Set organization context
            set_organization_context(request, organization)

            # Redirect to organization dashboard
            return redirect('moa:org_dashboard', org_code=org_code)

        except Organization.DoesNotExist:
            return redirect('common:page_restricted')

    # No org_code provided, redirect to organization selection
    return redirect('organization_selection')


def validate_organization(request, org_code):
    """
    Validate organization code and return JSON response.

    Args:
        request: HTTP request object
        org_code: Organization code to validate

    Returns:
        JsonResponse: Validation result
    """
    from organizations.models import Organization
    from django.http import JsonResponse

    try:
        organization = Organization.objects.get(code=org_code, is_active=True)
        has_access = has_organization_access(request.user, organization)

        return JsonResponse({
            'valid': True,
            'has_access': has_access,
            'organization_name': organization.name,
            'organization_type': organization.organization_type,
        })

    except Organization.DoesNotExist:
        return JsonResponse({
            'valid': False,
            'error': 'Organization not found or inactive',
        })


def current_organization(request):
    """
    Get current organization context as JSON response.

    Args:
        request: HTTP request object

    Returns:
        JsonResponse: Current organization information
    """
    from django.http import JsonResponse
    from common.middleware.organization_context import get_organization_context

    org = get_organization_context(request)

    if org:
        return JsonResponse({
            'org_code': org.code,
            'org_name': org.name,
            'org_type': org.organization_type,
            'is_active': org.is_active,
        })
    else:
        return JsonResponse({
            'org_code': None,
            'org_name': None,
            'org_type': None,
            'is_active': False,
        })


def has_organization_access(user, organization):
    """
    Check if user has access to organization.

    Args:
        user: User instance
        organization: Organization instance

    Returns:
        bool: True if user has access
    """
    # Superusers have access to all organizations
    if user.is_superuser:
        return True

    # Check user's organization assignments
    from organizations.models import UserOrganizationAssignment

    return UserOrganizationAssignment.objects.filter(
        user=user,
        organization=organization,
        is_active=True
    ).exists()


def get_legacy_redirect_urlpatterns():
    """
    Get legacy URL redirect patterns for backward compatibility.

    Returns:
        list: URL patterns for legacy redirects
    """
    return [
        # Redirect old project-central URLs (already implemented in main urls.py)
        # Additional legacy redirects can be added here as needed
    ]


# URL pattern generators for templates
def generate_url(url_name, org_code=None, **kwargs):
    """
    Generate organization-aware URL.

    Args:
        url_name: URL name to reverse
        org_code: Organization code (for BMMS mode)
        **kwargs: Additional URL parameters

    Returns:
        str: Generated URL
    """
    from django.urls import reverse

    if is_obcms_mode():
        # OBCMS mode: standard URL reversal
        return reverse(url_name, kwargs=kwargs)
    else:
        # BMMS mode: include organization context
        if org_code:
            if ':' in url_name:
                # Namespaced URL
                namespace, name = url_name.split(':', 1)
                url_name = f'moa:{name}'
            else:
                # Non-namespaced URL
                pass

            kwargs['org_code'] = org_code

        return reverse(url_name, kwargs=kwargs)


def get_current_organization_code(request):
    """
    Get current organization code from request.

    Args:
        request: HTTP request object

    Returns:
        str or None: Current organization code
    """
    from common.middleware.organization_context import get_organization_context

    org = get_organization_context(request)
    return org.code if org else None


# URL pattern collections for different purposes
def get_api_urlpatterns():
    """Get API URL patterns (same for both modes)."""
    return [
        # API v1 (Current stable version)
        path("api/v1/", include("api.v1.urls")),

        # Legacy API endpoints (deprecated)
        path("api/administrative/", include(("common.api_urls", "common_api"), namespace="common_api")),
        path("api/communities/", include("communities.api_urls")),
        path("api/municipal-profiles/", include("municipal_profiles.api_urls")),
        path("api/mana/", include("mana.api_urls")),
        path("api/coordination/", include("coordination.api_urls")),
        path("api/policies/", include("recommendations.policies.api_urls")),
        path("api/policy-tracking/", include("recommendations.policy_tracking.api_urls")),

        # Browsable API authentication
        path("api-auth/", include("rest_framework.urls")),
    ]


def get_admin_urlpatterns():
    """Get admin URL patterns (same for both modes)."""
    return [
        # Health check endpoints
        path("health/", import_string("common.views.health.health_check"), name="health"),
        path("live/", import_string("obc_management.views.health.liveness_probe"), name="liveness"),
        path("ready/", import_string("obc_management.views.health.readiness_probe"), name="readiness"),

        # Admin interface
        path("admin/", include("admin.site.urls")),

        # Custom admin views
        path("admin/auth/group/", import_string("common.admin_views.group_changelist_view"), name="custom_group_changelist"),
    ]


def get_utility_urlpatterns():
    """Get utility URL patterns (health checks, redirects, etc.)."""
    return [
        # Project Central legacy redirects
        path(
            "project-central/<path:remaining_path>",
            RedirectView.as_view(
                url="/project-management/%(remaining_path)s",
                permanent=False
            ),
            name="project_central_legacy_redirect"
        ),
        path(
            "project-central/",
            RedirectView.as_view(
                url="/project-management/",
                permanent=False
            ),
            name="project_central_root_redirect"
        ),
    ]