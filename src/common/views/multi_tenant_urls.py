"""
Multi-tenant URL Views for BMMS Architecture

Provides views for organization switching and management in BMMS multi-tenant mode.
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_http_methods
from django.contrib import messages

from obc_management.settings.bmms_config import is_bmms_mode, is_obcms_mode
from common.middleware.multi_tenant_urls import (
    get_organization_by_code,
    validate_organization_access,
    create_organization_switcher
)


@login_required
def switch_organization(request, org_code=None):
    """
    Switch current organization context.

    Args:
        request: HTTP request object
        org_code: Target organization code (optional)

    Returns:
        HttpResponse: Redirect to organization dashboard or error page
    """
    if is_obcms_mode():
        # OBCMS mode: no organization switching needed
        return redirect('common:dashboard')

    if org_code:
        # Validate organization exists and user has access
        organization = get_organization_by_code(org_code)

        if organization and validate_organization_access(request, organization):
            # Set organization context in session
            request.session['current_organization_code'] = organization.code
            request.session['current_organization'] = str(organization.id)

            # Add success message
            messages.success(request, f'Switched to {organization.name} ({organization.code})')

            # Redirect to organization dashboard
            return redirect('common:dashboard')  # Will be handled by URL routing
        else:
            messages.error(request, f'Access denied to organization {org_code}')
            return redirect('common:page_restricted')

    # No org_code provided, redirect to organization selection
    return redirect('organization_selection')


@login_required
def organization_selection(request):
    """
    Organization selection page for BMMS mode.

    Args:
        request: HTTP request object

    Returns:
        HttpResponse: Organization selection page
    """
    if is_obcms_mode():
        # OBCMS mode: redirect to dashboard
        return redirect('common:dashboard')

    # Get organization switcher data
    switcher_data = create_organization_switcher(request)

    if not switcher_data.get('organizations'):
        # No organizations available
        messages.error(request, 'No organizations available for your account.')
        return redirect('common:dashboard')

    if len(switcher_data['organizations']) == 1:
        # Only one organization, auto-select it
        org = switcher_data['organizations'][0]
        request.session['current_organization_code'] = org.code
        request.session['current_organization'] = str(org.id)
        return redirect('common:dashboard')

    return render(request, 'common/organization_selection.html', {
        'organizations': switcher_data['organizations'],
        'current_organization': switcher_data.get('current_organization'),
    })


@login_required
@require_http_methods(["GET"])
def validate_organization(request, org_code):
    """
    Validate organization code and return JSON response.

    Args:
        request: HTTP request object
        org_code: Organization code to validate

    Returns:
        JsonResponse: Validation result
    """
    organization = get_organization_by_code(org_code)

    if organization:
        has_access = validate_organization_access(request, organization)

        return JsonResponse({
            'valid': True,
            'has_access': has_access,
            'organization_name': organization.name,
            'organization_type': getattr(organization, 'organization_type', 'Unknown'),
        })
    else:
        return JsonResponse({
            'valid': False,
            'error': 'Organization not found or inactive',
        })


@login_required
@require_http_methods(["GET"])
def current_organization(request):
    """
    Get current organization context as JSON response.

    Args:
        request: HTTP request object

    Returns:
        JsonResponse: Current organization information
    """
    if is_obcms_mode():
        return JsonResponse({
            'org_code': None,
            'org_name': 'OBCMS Mode',
            'org_type': 'Single-tenant',
            'is_active': True,
            'mode': 'obcms',
        })

    org_code = request.session.get('current_organization_code')
    org = get_organization_by_code(org_code) if org_code else None

    if org:
        return JsonResponse({
            'org_code': org.code,
            'org_name': org.name,
            'org_type': getattr(org, 'organization_type', 'Unknown'),
            'is_active': org.is_active,
            'mode': 'bmms',
        })
    else:
        return JsonResponse({
            'org_code': None,
            'org_name': None,
            'org_type': None,
            'is_active': False,
            'mode': 'bmms',
        })


@login_required
@require_http_methods(["POST"])
def set_organization_preference(request):
    """
    Set preferred organization for future sessions.

    Args:
        request: HTTP request object

    Returns:
        JsonResponse: Operation result
    """
    org_code = request.POST.get('org_code')
    if not org_code:
        return JsonResponse({'success': False, 'error': 'Organization code required'})

    organization = get_organization_by_code(org_code)
    if not organization:
        return JsonResponse({'success': False, 'error': 'Organization not found'})

    if not validate_organization_access(request, organization):
        return JsonResponse({'success': False, 'error': 'Access denied'})

    # Set preference in user profile (if available)
    if hasattr(request.user, 'preferred_organization'):
        request.user.preferred_organization = organization
        request.user.save()
    else:
        # Store in session
        request.session['preferred_organization_code'] = org_code

    return JsonResponse({'success': True, 'organization': organization.name})


@login_required
def organization_dashboard(request, org_code):
    """
    Organization-specific dashboard redirect.

    Args:
        request: HTTP request object
        org_code: Organization code

    Returns:
        HttpResponse: Redirect to appropriate dashboard
    """
    if is_obcms_mode():
        return redirect('common:dashboard')

    organization = get_organization_by_code(org_code)
    if not organization:
        return redirect('organization_selection')

    if not validate_organization_access(request, organization):
        return redirect('common:page_restricted')

    # Set organization context
    request.session['current_organization_code'] = organization.code
    request.session['current_organization'] = str(organization.id)

    # Redirect to main dashboard (will be filtered by organization context)
    return redirect('common:dashboard')


# HTMX endpoints for instant organization switching
@login_required
@require_http_methods(["GET"])
def organization_switcher_partial(request):
    """
    Render organization switcher dropdown for HTMX updates.

    Args:
        request: HTTP request object

    Returns:
        HttpResponse: Partial HTML for organization switcher
    """
    if is_obcms_mode():
        return render(request, 'common/partials/empty.html')

    switcher_data = create_organization_switcher(request)

    return render(request, 'common/partials/organization_switcher.html', {
        'organizations': switcher_data.get('organizations', []),
        'current_organization': switcher_data.get('current_organization'),
        'can_switch': switcher_data.get('can_switch', False),
    })


@login_required
@require_http_methods(["POST"])
def quick_switch_organization(request):
    """
    Quick organization switch for HTMX (no page reload).

    Args:
        request: HTTP request object

    Returns:
        HttpResponse: HTMX response with updated content
    """
    org_code = request.POST.get('org_code')
    if not org_code:
        return HttpResponseBadRequest('Organization code required')

    organization = get_organization_by_code(org_code)
    if not organization or not validate_organization_access(request, organization):
        return HttpResponseBadRequest('Invalid organization or access denied')

    # Set organization context
    request.session['current_organization_code'] = organization.code
    request.session['current_organization'] = str(organization.id)

    # Return success response with organization info
    return render(request, 'common/partials/organization_switch_success.html', {
        'organization': organization,
        'message': f'Switched to {organization.name}',
    })