"""
RBAC Management Views for User Approvals Integration

Provides comprehensive role-based access control management views
integrated with the User Approvals workflow.

Features:
- User permissions listing with role/permission information
- Role assignment/removal (HTMX-powered)
- Feature toggles for users (HTMX-powered)
- Direct permission grants/denials
- Bulk role assignments
- Permission auditing

See:
- src/common/rbac_models.py - RBAC data models
- src/common/services/rbac_service.py - Permission checking service
- src/common/decorators/rbac.py - Permission decorators
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q, Count, Prefetch
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.views.decorators.http import require_http_methods, require_POST

from common.decorators.rbac import require_permission
from common.forms.rbac_forms import (
    UserRoleAssignmentForm,
    UserPermissionForm,
    BulkRoleAssignmentForm,
    FeatureToggleForm,
)
from common.models import User
from common.rbac_models import (
    Feature,
    Permission,
    Role,
    UserRole,
    UserPermission,
    RolePermission,
)
from common.services.rbac_service import RBACService


# ============================================================================
# HTMX RESPONSE HELPERS
# ============================================================================

def htmx_response(request, template, context=None, **kwargs):
    """
    Helper to return appropriate response for HTMX requests.

    Args:
        request: HTTP request
        template: Template name (or dict with htmx/full keys)
        context: Template context dict
        **kwargs: Additional response parameters

    Returns:
        Rendered template response
    """
    context = context or {}

    # Handle template dict with htmx/full variants
    if isinstance(template, dict):
        if request.htmx:
            template = template.get('htmx', template.get('full'))
        else:
            template = template.get('full', template.get('htmx'))

    return render(request, template, context, **kwargs)


def htmx_success_message(message, target=None):
    """
    Generate HTMX success message response.

    Args:
        message: Success message text
        target: Optional HTMX target selector

    Returns:
        HttpResponse with HX-Trigger header
    """
    response = HttpResponse("")

    # Set HX-Trigger for toast notification
    trigger_data = {
        'showMessage': {
            'type': 'success',
            'message': message
        }
    }

    if target:
        trigger_data['refreshTarget'] = target

    import json
    response['HX-Trigger'] = json.dumps(trigger_data)

    return response


def htmx_error_message(message, status=400):
    """
    Generate HTMX error message response.

    Args:
        message: Error message text
        status: HTTP status code

    Returns:
        HttpResponse with error message
    """
    response = HttpResponse(
        f'<div class="alert alert-error">{message}</div>',
        status=status
    )

    # Set HX-Trigger for toast notification
    import json
    response['HX-Trigger'] = json.dumps({
        'showMessage': {
            'type': 'error',
            'message': message
        }
    })

    return response


# ============================================================================
# USER PERMISSIONS MANAGEMENT
# ============================================================================

@login_required
@require_permission('oobc_management.manage_user_permissions')
def user_permissions_list(request):
    """
    List all users with their role and permission information.

    Features:
    - Paginated user list
    - Role/permission summary per user
    - Search and filter capabilities
    - HTMX-powered for instant updates
    """
    # Get filter parameters
    search_query = request.GET.get('q', '')
    user_type_filter = request.GET.get('user_type', '')
    role_filter = request.GET.get('role', '')
    org_filter = request.GET.get('organization', '')

    # Base queryset with optimized queries
    users = User.objects.select_related('moa_organization').prefetch_related(
        Prefetch('user_roles', queryset=UserRole.objects.filter(is_active=True).select_related('role', 'organization')),
        Prefetch('direct_permissions', queryset=UserPermission.objects.filter(is_active=True).select_related('permission__feature')),
    ).filter(is_active=True)

    # Apply filters
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query)
        )

    if user_type_filter:
        users = users.filter(user_type=user_type_filter)

    if role_filter:
        users = users.filter(user_roles__role__id=role_filter, user_roles__is_active=True).distinct()

    if org_filter:
        users = users.filter(
            Q(moa_organization__id=org_filter) |
            Q(user_roles__organization__id=org_filter)
        ).distinct()

    # Annotate with counts
    users = users.annotate(
        role_count=Count('user_roles', filter=Q(user_roles__is_active=True)),
        direct_permission_count=Count('direct_permissions', filter=Q(direct_permissions__is_active=True))
    ).order_by('last_name', 'first_name')

    # Paginate
    paginator = Paginator(users, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # Get available roles and organizations for filters
    available_roles = Role.objects.filter(is_active=True).order_by('name')

    from coordination.models import Organization
    available_orgs = Organization.objects.filter(
        organization_type='bmoa',
        is_active=True
    ).order_by('name')

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'user_type_filter': user_type_filter,
        'role_filter': role_filter,
        'org_filter': org_filter,
        'available_roles': available_roles,
        'available_orgs': available_orgs,
        'user_types': User.USER_TYPES,
    }

    template = {
        'htmx': 'common/rbac/partials/user_list.html',
        'full': 'common/rbac/user_permissions_list.html',
    }

    return htmx_response(request, template, context)


@login_required
@require_permission('oobc_management.manage_user_permissions')
def user_permissions_detail(request, user_id):
    """
    Show detailed permissions for a specific user.

    Displays:
    - All assigned roles (with organization context)
    - Direct permission grants/denials
    - Effective permissions (computed from roles + direct)
    - Permission history/audit trail
    """
    user = get_object_or_404(User, pk=user_id)

    # Get user's roles with organization context
    user_roles = UserRole.objects.filter(
        user=user,
        is_active=True
    ).select_related('role', 'organization', 'assigned_by').filter(
        Q(expires_at__isnull=True) | Q(expires_at__gt=timezone.now())
    ).order_by('-assigned_at')

    # Get direct permissions
    direct_permissions = UserPermission.objects.filter(
        user=user,
        is_active=True
    ).select_related('permission__feature', 'organization', 'granted_by').filter(
        Q(expires_at__isnull=True) | Q(expires_at__gt=timezone.now())
    ).order_by('-assigned_at')

    # Get organization context for permission checks
    organization = RBACService.get_user_organization_context(request)

    # Get effective permissions
    permission_ids = RBACService.get_user_permissions(user, organization)
    effective_permissions = Permission.objects.filter(
        id__in=permission_ids
    ).select_related('feature').order_by('feature__module', 'feature__name', 'codename')

    # Get accessible features
    accessible_features = RBACService.get_accessible_features(user, organization)

    context = {
        'target_user': user,
        'user_roles': user_roles,
        'direct_permissions': direct_permissions,
        'effective_permissions': effective_permissions,
        'accessible_features': accessible_features,
        'organization': organization,
    }

    return render(request, 'common/rbac/user_permissions_detail.html', context)


# ============================================================================
# ROLE ASSIGNMENT/REMOVAL
# ============================================================================

@login_required
@require_POST
@require_permission('oobc_management.assign_user_roles')
def user_role_assign(request, user_id):
    """
    Assign a role to a user (HTMX endpoint).

    Handles:
    - Role assignment with organization context
    - Expiration dates (optional)
    - Duplicate role prevention
    - Audit trail tracking
    """
    user = get_object_or_404(User, pk=user_id)
    form = UserRoleAssignmentForm(request.POST)

    if form.is_valid():
        role = form.cleaned_data['role']
        organization = form.cleaned_data.get('organization')
        expires_at = form.cleaned_data.get('expires_at')

        # Check for duplicate assignment
        existing = UserRole.objects.filter(
            user=user,
            role=role,
            organization=organization,
            is_active=True
        ).exists()

        if existing:
            return htmx_error_message(
                f"User already has the {role.name} role in this context.",
                status=400
            )

        # Create role assignment
        try:
            with transaction.atomic():
                UserRole.objects.create(
                    user=user,
                    role=role,
                    organization=organization,
                    expires_at=expires_at,
                    assigned_by=request.user,
                    is_active=True
                )

                # Invalidate user's permission cache
                RBACService.clear_cache(user_id=user.id)

                # Log the assignment (using audit log if available)
                from common.auditlog_config import log_model_change
                log_model_change(
                    request,
                    user,
                    'update',
                    changes={'role_assigned': role.name}
                )

            return htmx_success_message(
                f"Successfully assigned {role.name} role to {user.get_full_name()}",
                target='#user-roles-list'
            )

        except Exception as e:
            return htmx_error_message(
                f"Failed to assign role: {str(e)}",
                status=500
            )

    # Form validation errors
    errors = '<br>'.join([f"{field}: {', '.join(errs)}" for field, errs in form.errors.items()])
    return htmx_error_message(f"Validation errors:<br>{errors}", status=400)


@login_required
@require_POST
@require_permission('oobc_management.assign_user_roles')
def user_role_remove(request, user_id, role_id):
    """
    Remove a role from a user (HTMX endpoint).

    Handles:
    - Deactivation (not deletion) for audit trail
    - Permission cache invalidation
    - System role protection
    """
    user = get_object_or_404(User, pk=user_id)

    # Find the specific UserRole assignment
    user_role = get_object_or_404(
        UserRole,
        user=user,
        role__id=role_id,
        is_active=True
    )

    # Prevent removal of system-critical roles
    if user_role.role.is_system_role and user.is_superuser:
        return htmx_error_message(
            "Cannot remove system role from superuser.",
            status=403
        )

    try:
        with transaction.atomic():
            # Deactivate (don't delete for audit trail)
            user_role.is_active = False
            user_role.save(update_fields=['is_active', 'updated_at'])

            # Invalidate user's permission cache
            RBACService.clear_cache(user_id=user.id)

            # Log the removal
            from common.auditlog_config import log_model_change
            log_model_change(
                request,
                user,
                'update',
                changes={'role_removed': user_role.role.name}
            )

        return htmx_success_message(
            f"Successfully removed {user_role.role.name} role from {user.get_full_name()}",
            target='#user-roles-list'
        )

    except Exception as e:
        return htmx_error_message(
            f"Failed to remove role: {str(e)}",
            status=500
        )


# ============================================================================
# FEATURE TOGGLES
# ============================================================================

@login_required
@require_POST
@require_permission('oobc_management.manage_feature_access')
def user_feature_toggle(request, user_id, feature_id):
    """
    Enable/disable a feature for a user (HTMX endpoint).

    Creates direct permission grant/denial for feature access.
    """
    user = get_object_or_404(User, pk=user_id)
    feature = get_object_or_404(Feature, pk=feature_id)

    form = FeatureToggleForm(request.POST)

    if form.is_valid():
        is_granted = form.cleaned_data['is_granted']
        organization = form.cleaned_data.get('organization')
        expires_at = form.cleaned_data.get('expires_at')
        reason = form.cleaned_data.get('reason', '')

        # Get the view permission for this feature
        view_permission = feature.permissions.filter(
            permission_type='view',
            is_active=True
        ).first()

        if not view_permission:
            return htmx_error_message(
                f"No view permission found for feature {feature.name}",
                status=400
            )

        try:
            with transaction.atomic():
                # Create or update direct permission
                user_perm, created = UserPermission.objects.update_or_create(
                    user=user,
                    permission=view_permission,
                    organization=organization,
                    defaults={
                        'is_granted': is_granted,
                        'expires_at': expires_at,
                        'reason': reason,
                        'granted_by': request.user,
                        'is_active': True
                    }
                )

                # Invalidate cache
                RBACService.clear_cache(user_id=user.id)

                # Log the change
                from common.auditlog_config import log_model_change
                log_model_change(
                    request,
                    user,
                    'update',
                    changes={
                        'feature_access': {
                            'feature': feature.name,
                            'granted': is_granted,
                            'reason': reason
                        }
                    }
                )

            action = "enabled" if is_granted else "disabled"
            return htmx_success_message(
                f"Successfully {action} {feature.name} for {user.get_full_name()}",
                target='#user-features-list'
            )

        except Exception as e:
            return htmx_error_message(
                f"Failed to toggle feature: {str(e)}",
                status=500
            )

    # Form validation errors
    errors = '<br>'.join([f"{field}: {', '.join(errs)}" for field, errs in form.errors.items()])
    return htmx_error_message(f"Validation errors:<br>{errors}", status=400)


# ============================================================================
# BULK OPERATIONS
# ============================================================================

@login_required
@require_POST
@require_permission('oobc_management.assign_user_roles')
def bulk_assign_roles(request):
    """
    Assign role to multiple users at once.

    Features:
    - Bulk role assignment
    - Organization context support
    - Duplicate prevention
    - Progress tracking
    """
    form = BulkRoleAssignmentForm(request.POST)

    if form.is_valid():
        users = form.cleaned_data['users']
        role = form.cleaned_data['role']
        organization = form.cleaned_data.get('organization')
        expires_at = form.cleaned_data.get('expires_at')

        success_count = 0
        skip_count = 0
        errors = []

        try:
            with transaction.atomic():
                for user in users:
                    # Check for existing assignment
                    existing = UserRole.objects.filter(
                        user=user,
                        role=role,
                        organization=organization,
                        is_active=True
                    ).exists()

                    if existing:
                        skip_count += 1
                        continue

                    # Create assignment
                    UserRole.objects.create(
                        user=user,
                        role=role,
                        organization=organization,
                        expires_at=expires_at,
                        assigned_by=request.user,
                        is_active=True
                    )

                    # Invalidate cache
                    RBACService.clear_cache(user_id=user.id)
                    success_count += 1

                # Log bulk operation
                from common.auditlog_config import log_model_change
                log_model_change(
                    request,
                    role,
                    'update',
                    changes={
                        'bulk_assignment': {
                            'users_count': success_count,
                            'role': role.name
                        }
                    }
                )

            message = f"Successfully assigned {role.name} to {success_count} user(s)."
            if skip_count > 0:
                message += f" Skipped {skip_count} user(s) with existing assignment."

            return htmx_success_message(message, target='#user-list')

        except Exception as e:
            return htmx_error_message(
                f"Bulk assignment failed: {str(e)}",
                status=500
            )

    # Form validation errors
    errors = '<br>'.join([f"{field}: {', '.join(errs)}" for field, errs in form.errors.items()])
    return htmx_error_message(f"Validation errors:<br>{errors}", status=400)


# ============================================================================
# ROLE & FEATURE LISTING
# ============================================================================

@login_required
@require_permission('oobc_management.view_rbac_config')
def role_list(request):
    """
    List all available roles with permission details.

    Shows:
    - Role hierarchy
    - Permission counts
    - User assignment counts
    - Organization scoping
    """
    # Get organization context
    organization = RBACService.get_user_organization_context(request)

    # Base queryset
    roles = Role.objects.filter(is_active=True).annotate(
        user_count=Count('user_assignments', filter=Q(user_assignments__is_active=True)),
        permission_count=Count('role_permissions', filter=Q(role_permissions__is_active=True))
    )

    # Filter by organization if in MOA context
    if organization:
        roles = roles.filter(
            Q(organization=organization) | Q(scope='system')
        )

    roles = roles.order_by('-level', 'name')

    context = {
        'roles': roles,
        'organization': organization,
    }

    return render(request, 'common/rbac/role_list.html', context)


@login_required
@require_permission('oobc_management.view_rbac_config')
def feature_list(request):
    """
    List all features with access controls.

    Shows:
    - Feature hierarchy
    - Module grouping
    - Active/inactive status
    - Organization-specific features
    """
    # Get organization context
    organization = RBACService.get_user_organization_context(request)

    # Base queryset
    features = Feature.objects.filter(is_active=True).select_related('parent').prefetch_related(
        'permissions'
    ).annotate(
        permission_count=Count('permissions', filter=Q(permissions__is_active=True))
    )

    # Filter by organization if in MOA context
    if organization:
        features = features.filter(
            Q(organization=organization) | Q(organization__isnull=True)
        )

    # Group by module
    features_by_module = {}
    for feature in features.order_by('module', 'sort_order', 'name'):
        if feature.module not in features_by_module:
            features_by_module[feature.module] = []
        features_by_module[feature.module].append(feature)

    context = {
        'features_by_module': features_by_module,
        'organization': organization,
    }

    return render(request, 'common/rbac/feature_list.html', context)
