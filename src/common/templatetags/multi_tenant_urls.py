"""
Multi-tenant URL Template Tags

Provides Django template tags for organization-aware URL generation.
Supports both OBCMS and BMMS modes seamlessly.

Usage:
    {% load multi_tenant_urls %}

    Generate organization-aware URLs:
    {% org_url 'common:dashboard' %}
    {% org_url 'communities:communities_home' org_code='DSWD' %}

    Get current organization context:
    {% current_org as org %}
    {{ org.code }} - {{ org.name }}

    Check if in BMMS mode:
    {% if is_bmms_mode %}
        <a href="{% org_url 'ocm:dashboard' %}">OCM Dashboard</a>
    {% else %}
        <a href="{% org_url 'common:dashboard' %}">Dashboard</a>
    {% endif %}
"""

from django import template
from django.urls import reverse
from django.utils.html import format_html

from obc_management.settings.bmms_config import (
    is_bmms_mode,
    is_obcms_mode,
    get_default_organization_code
)

register = template.Library()


@register.simple_tag(takes_context=True)
def org_url(context, url_name, org_code=None, **kwargs):
    """
    Generate organization-aware URL based on current operational mode.

    Args:
        context: Django template context
        url_name: URL name to reverse
        org_code: Organization code (for BMMS mode, optional)
        **kwargs: Additional URL parameters

    Returns:
        str: Generated URL

    Examples:
        {% org_url 'common:dashboard' %}
        {% org_url 'communities:communities_home' org_code='DSWD' %}
        {% org_url 'mana:mana_home' org_code=current_org.code %}
    """
    request = context.get('request')
    if not request:
        # Fallback to standard URL reversal if no request context
        return reverse(url_name, kwargs=kwargs)

    if is_obcms_mode():
        # OBCMS mode: standard URL reversal
        return reverse(url_name, kwargs=kwargs)
    else:
        # BMMS mode: include organization context
        if not org_code:
            # Try to get organization from context
            org_code = get_current_org_code(request)

        if org_code:
            # Add organization code to URL parameters
            if ':' in url_name:
                # Namespaced URL - check if it's already moa-namespaced
                namespace, name = url_name.split(':', 1)
                if namespace not in ['ocm', 'api', 'admin']:
                    # Convert to moa namespace for organization URLs
                    url_name = f'moa:{name}'

            kwargs['org_code'] = org_code

        return reverse(url_name, kwargs=kwargs)


@register.simple_tag(takes_context=True)
def current_org(context):
    """
    Get current organization from request context.

    Args:
        context: Django template context

    Returns:
        Organization or None: Current organization instance

    Examples:
        {% current_org as org %}
        {% if org %}
            <span class="org-badge">{{ org.code }}: {{ org.name }}</span>
        {% endif %}
    """
    request = context.get('request')
    if not request:
        return None

    return get_current_organization(request)


@register.simple_tag
def is_bmms_mode():
    """
    Check if system is running in BMMS mode.

    Returns:
        bool: True if in BMMS mode

    Examples:
        {% if is_bmms_mode %}
            <div class="bmms-header">
                <span>BMMS Multi-tenant Mode</span>
            </div>
        {% endif %}
    """
    return is_bmms_mode()


@register.simple_tag
def is_obcms_mode():
    """
    Check if system is running in OBCMS mode.

    Returns:
        bool: True if in OBCMS mode

    Examples:
        {% if is_obcms_mode %}
            <div class="obcms-header">
                <span>OBCMS Single-tenant Mode</span>
            </div>
        {% endif %}
    """
    return is_obcms_mode()


@register.simple_tag(takes_context=True)
def organization_switcher(context):
    """
    Generate organization switcher dropdown HTML.

    Args:
        context: Django template context

    Returns:
        safe_html: HTML for organization switcher

    Examples:
        {% organization_switcher %}
    """
    request = context.get('request')
    if not request or is_obcms_mode():
        return format_html('')

    user = request.user
    if not user.is_authenticated:
        return format_html('')

    # Get user's accessible organizations
    organizations = get_user_organizations(user)
    current_org = get_current_organization(request)

    if not organizations or len(organizations) <= 1:
        return format_html('')

    # Generate dropdown HTML
    html = ['<div class="organization-switcher dropdown">']
    html.append('<button class="btn btn-outline-secondary dropdown-toggle" type="button" id="orgSwitcher" data-bs-toggle="dropdown">')

    if current_org:
        html.append(f'<i class="fas fa-building"></i> {current_org.code}: {current_org.name}')
    else:
        html.append('<i class="fas fa-building"></i> Select Organization')

    html.append('</button>')
    html.append('<ul class="dropdown-menu" aria-labelledby="orgSwitcher">')

    for org in organizations:
        active_class = 'active' if current_org and org.code == current_org.code else ''
        html.append(f'''
            <li>
                <a class="dropdown-item {active_class}" href="#"
                   hx-post="/switch-organization/{org.code}/"
                   hx-target="#main-content"
                   hx-push-url="true">
                    <i class="fas fa-building"></i> {org.code}: {org.name}
                </a>
            </li>
        ''')

    html.append('</ul>')
    html.append('</div>')

    return format_html(''.join(html))


@register.simple_tag(takes_context=True)
def breadcrumb_with_org(context, *items):
    """
    Generate breadcrumb navigation with organization context.

    Args:
        context: Django template context
        *items: List of (url_name, title) tuples

    Returns:
        safe_html: Breadcrumb HTML

    Examples:
        {% breadcrumb_with_org
           'common:dashboard' 'Dashboard'
           'communities:communities_home' 'Communities'
        %}
    """
    request = context.get('request')
    if not request:
        return format_html('')

    html = ['<nav aria-label="breadcrumb"><ol class="breadcrumb">']

    # Add organization context if in BMMS mode
    if is_bmms_mode():
        current_org = get_current_organization(request)
        if current_org:
            html.append(f'''
                <li class="breadcrumb-item">
                    <a href="{org_url(context, 'moa:org_dashboard', org_code=current_org.code)}">
                        <i class="fas fa-building"></i> {current_org.code}
                    </a>
                </li>
            ''')
        else:
            html.append('''
                <li class="breadcrumb-item">
                    <a href="/ocm/dashboard/">
                        <i class="fas fa-landmark"></i> OCM
                    </a>
                </li>
            ''')

    # Add breadcrumb items
    for i, item in enumerate(items):
        if isinstance(item, str):
            # Simple string (last item, no link)
            html.append(f'<li class="breadcrumb-item active" aria-current="page">{item}</li>')
        elif len(item) == 2:
            url_name, title = item
            if i == len(items) - 1:
                # Last item, no link
                html.append(f'<li class="breadcrumb-item active" aria-current="page">{title}</li>')
            else:
                # Generate URL with organization context
                url = org_url(context, url_name)
                html.append(f'<li class="breadcrumb-item"><a href="{url}">{title}</a></li>')

    html.append('</ol></nav>')

    return format_html(''.join(html))


@register.simple_tag(takes_context=True)
def sidebar_menu(context):
    """
    Generate sidebar navigation menu with organization context.

    Args:
        context: Django template context

    Returns:
        safe_html: Sidebar menu HTML

    Examples:
        {% sidebar_menu %}
    """
    request = context.get('request')
    if not request:
        return format_html('')

    # Define menu structure
    menu_items = [
        {
            'url': 'common:dashboard',
            'title': 'Dashboard',
            'icon': 'fas fa-tachometer-alt',
            'permission': None,
        },
        {
            'url': 'communities:communities_home',
            'title': 'Communities',
            'icon': 'fas fa-users',
            'permission': None,
        },
        {
            'url': 'mana:mana_home',
            'title': 'MANA',
            'icon': 'fas fa-chart-line',
            'permission': None,
        },
        {
            'url': 'coordination:partnership_list',
            'title': 'Coordination',
            'icon': 'fas fa-handshake',
            'permission': None,
        },
        {
            'url': 'planning:planning_dashboard',
            'title': 'Planning',
            'icon': 'fas fa-clipboard-list',
            'permission': None,
        },
        {
            'url': 'budget_preparation:budget_dashboard',
            'title': 'Budget Preparation',
            'icon': 'fas fa-calculator',
            'permission': None,
        },
        {
            'url': 'budget_execution:execution_dashboard',
            'title': 'Budget Execution',
            'icon': 'fas fa-coins',
            'permission': None,
        },
    ]

    # Add OCM menu items if in BMMS mode
    if is_bmms_mode():
        menu_items.extend([
            {
                'url': 'ocm:dashboard',
                'title': 'OCM Dashboard',
                'icon': 'fas fa-landmark',
                'permission': 'ocm.view_dashboard',
            },
        ])

    html = ['<nav class="sidebar-menu"><ul class="nav flex-column">']

    for item in menu_items:
        # Check permissions if specified
        if item.get('permission') and request.user:
            if not request.user.has_perm(item['permission']):
                continue

        # Generate URL with organization context
        url = org_url(context, item['url'])

        # Check if current page
        current_path = request.path
        active_class = 'active' if current_path.startswith(url.split('?')[0]) else ''

        html.append(f'''
            <li class="nav-item">
                <a class="nav-link {active_class}" href="{url}">
                    <i class="{item['icon']}"></i>
                    <span>{item['title']}</span>
                </a>
            </li>
        ''')

    html.append('</ul></nav>')

    return format_html(''.join(html))


# Helper functions
def get_current_organization(request):
    """Get current organization from request."""
    try:
        from common.middleware.organization_context import get_organization_context
        return get_organization_context(request)
    except ImportError:
        return None


def get_current_org_code(request):
    """Get current organization code from request."""
    org = get_current_organization(request)
    return org.code if org else None


def get_user_organizations(user):
    """Get organizations accessible to user."""
    if not user.is_authenticated:
        return []

    try:
        from organizations.models import UserOrganizationAssignment
        return [
            assignment.organization
            for assignment in UserOrganizationAssignment.objects.filter(
                user=user,
                is_active=True
            ).select_related('organization')
        ]
    except ImportError:
        return []


@register.filter
def org_safe(value):
    """
    Make value safe for organization context in URLs.

    Args:
        value: String to make URL-safe

    Returns:
        str: URL-safe string
    """
    import re
    # Remove any characters that aren't alphanumeric, underscore, or hyphen
    return re.sub(r'[^A-Za-z0-9_-]', '', str(value))


@register.simple_tag(takes_context=True)
def org_api_url(context, endpoint, org_code=None, **kwargs):
    """
    Generate organization-aware API URL.

    Args:
        context: Django template context
        endpoint: API endpoint path
        org_code: Organization code (optional)
        **kwargs: Additional URL parameters

    Returns:
        str: API URL

    Examples:
        {% org_api_url '/api/v1/communities/' %}
        {% org_api_url '/api/v1/assessments/' org_code='DSWD' %}
    """
    request = context.get('request')
    if not request:
        return endpoint

    if is_obcms_mode():
        return endpoint
    else:
        if not org_code:
            org_code = get_current_org_code(request)

        if org_code:
            # Add organization parameter to API URL
            separator = '&' if '?' in endpoint else '?'
            return f"{endpoint}{separator}org_code={org_code}"

        return endpoint