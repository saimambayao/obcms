"""
WorkItem CRUD views with hierarchical tree display.

Implements:
- Tree list view with expand/collapse
- Detail view with breadcrumb and children
- Create/Edit views with dynamic forms
- Delete view with cascade options
- HTMX integration for interactive tree
"""

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.db import models
from django.db.models import Q, Count
from django.views.decorators.http import require_POST, require_http_methods
from django.core.exceptions import PermissionDenied, ValidationError
from django.utils import timezone

from common.work_item_model import WorkItem
from common.forms.work_items import WorkItemForm
from coordination.models import Organization
from coordination.utils.organizations import get_oobc_organization


def invalidate_calendar_cache(user_id):
    """
    Invalidate calendar cache for a specific user using cache versioning.

    This increments a version number, making all cached calendar feeds
    with the old version invalid. This is more reliable than trying to
    delete specific cache keys because FullCalendar's date ranges vary
    based on the view (month/week/day) and may span multiple months.

    Args:
        user_id: ID of the user whose calendar cache should be invalidated
    """
    from django.core.cache import cache

    version_key = f'calendar_version:{user_id}'
    try:
        cache.incr(version_key)
    except ValueError:
        # Key doesn't exist yet, initialize it
        cache.set(version_key, 1, None)  # Never expire


def invalidate_work_item_tree_cache(work_item):
    """
    Invalidate tree expansion cache for a work item and its ancestors.

    When a work item is created, updated, or deleted, we need to invalidate:
    1. Cache for the work item's parent (if it exists)
    2. Cache for all ancestors up the tree
    3. Cache for the work item itself (if it has children)
    4. Cache for all users who might have viewed it

    This ensures that the tree view shows up-to-date data after modifications.

    Args:
        work_item: WorkItem instance that was modified
    """
    from django.core.cache import cache
    from django.contrib.auth import get_user_model

    User = get_user_model()

    # Get all users (for cache key invalidation)
    # In production, consider storing active viewers in cache instead
    user_ids = User.objects.values_list('id', flat=True)

    # Invalidate cache for the work item itself (if it has children)
    for user_id in user_ids:
        cache_key = f"work_item_children:{work_item.id}:{user_id}"
        cache.delete(cache_key)

    # Invalidate cache for parent and all ancestors
    if work_item.parent:
        for user_id in user_ids:
            cache_key = f"work_item_children:{work_item.parent.id}:{user_id}"
            cache.delete(cache_key)

        # Recursively invalidate ancestors
        for ancestor in work_item.get_ancestors():
            for user_id in user_ids:
                cache_key = f"work_item_children:{ancestor.id}:{user_id}"
                cache.delete(cache_key)


def get_work_item_permissions(user, work_item):
    """
    Check user permissions for work item operations.

    Permission logic:
    1. Owner (created_by) can always edit/delete their own work items
    2. Superusers can edit/delete any work item
    3. Staff users with specific permissions can edit/delete
    4. Assigned users can edit (but not delete) work items

    Args:
        user: Django User instance
        work_item: WorkItem instance

    Returns:
        dict: {'can_edit': bool, 'can_delete': bool}
    """
    # Owner can always edit and delete
    if work_item.created_by == user:
        return {'can_edit': True, 'can_delete': True}

    # Superusers can do anything
    if user.is_superuser:
        return {'can_edit': True, 'can_delete': True}

    # Check Django permissions
    has_change_perm = user.has_perm('common.change_workitem')
    has_delete_perm = user.has_perm('common.delete_workitem')

    # Staff with appropriate permissions
    can_edit = user.is_staff and has_change_perm
    can_delete = user.is_staff and has_delete_perm

    # Assigned users can edit (but not delete unless they have permission)
    if user in work_item.assignees.all():
        can_edit = True

    return {'can_edit': can_edit, 'can_delete': can_delete}


@login_required
def work_item_list(request):
    """
    Display hierarchical tree view of all work items.

    Features:
    - MPTT tree structure with indentation
    - Expand/collapse functionality
    - Filter by type, status, priority
    - Search by title
    - Quick actions: view, edit, delete, add child

    Performance optimizations:
    - select_related() for ForeignKey fields
    - prefetch_related() for ManyToMany fields
    - only() to load minimal fields for list view
    - Database indexes on filter fields (work_type, status, priority)
    """
    # Get filter parameters
    work_type_filter = request.GET.get('work_type', '')
    status_filter = request.GET.get('status', '')
    priority_filter = request.GET.get('priority', '')
    search_query = request.GET.get('q', '')

    # Base queryset with optimized loading
    queryset = (
        WorkItem.objects
        .select_related('parent', 'created_by')  # Avoid N+1 on FK
        .prefetch_related('assignees', 'teams')  # Preload M2M
        .only(
            # Core fields for list display
            'id', 'work_type', 'title', 'status', 'priority', 'progress',
            'start_date', 'due_date',
            # MPTT fields (required for tree ordering)
            'level', 'tree_id', 'lft', 'rght',
            # FK fields (for select_related)
            'parent_id', 'created_by_id',
        )
    )

    # Apply filters (indexes on work_type, status, priority)
    if work_type_filter:
        queryset = queryset.filter(work_type=work_type_filter)
    if status_filter:
        queryset = queryset.filter(status=status_filter)
    if priority_filter:
        queryset = queryset.filter(priority=priority_filter)
    if search_query:
        # Note: icontains queries on title benefit from pg_trgm index in PostgreSQL
        queryset = queryset.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    # CRITICAL: Filter to show ONLY root items initially
    # Children are loaded on-demand via HTMX when user expands
    queryset = queryset.filter(level=0)

    # CRITICAL: Exclude MOA PPAs owned by external implementers, but keep OOBC-owned items visible.
    oobc_org = get_oobc_organization()

    moa_filter = Q(ppa_category='moa_ppa') | Q(related_ppa__category='moa_ppa')
    if oobc_org:
        oobc_owned_moa = Q(implementing_moa=oobc_org) | Q(
            related_ppa__implementing_moa=oobc_org
        )
        queryset = queryset.exclude(moa_filter & ~oobc_owned_moa)
    else:
        queryset = queryset.exclude(moa_filter)

    # Annotate with children count
    queryset = queryset.annotate(
        children_count=Count('children')
    )

    # Order by tree structure (uses tree_id and lft indexes)
    queryset = queryset.order_by('tree_id', 'lft')

    context = {
        'work_items': queryset,
        'work_type_choices': WorkItem.WORK_TYPE_CHOICES,
        'status_choices': WorkItem.STATUS_CHOICES,
        'priority_choices': WorkItem.PRIORITY_CHOICES,
        'work_type_filter': work_type_filter,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
        'search_query': search_query,
    }

    if request.headers.get('HX-Request') and request.GET.get('partial') == 'tree':
        return render(request, 'work_items/partials/tree_wrapper.html', context)

    return render(request, 'work_items/work_item_list.html', context)


@login_required
def work_item_detail(request, pk):
    """
    Display detailed view of a work item.

    Shows:
    - All work item fields
    - Parent breadcrumb navigation
    - List of direct children (expandable tree)
    - Timeline/dates
    - Assigned users and teams
    - Type-specific data (conditionally rendered)
    - Edit/Delete buttons

    Performance optimizations:
    - select_related() for parent chain (breadcrumb)
    - prefetch_related() for M2M relationships
    - Optimized children queryset with minimal fields
    """
    # Load work item with related data
    work_item = get_object_or_404(
        WorkItem.objects
        .select_related('parent', 'created_by')
        .prefetch_related('assignees', 'teams', 'related_items'),
        pk=pk
    )

    # Get breadcrumb (ancestors) - already optimized by select_related on parent
    breadcrumb = work_item.get_ancestors(include_self=True)

    # Get direct children with optimized query
    children = (
        work_item.get_children()
        .select_related('parent', 'created_by')
        .prefetch_related('assignees', 'teams')
        .only(
            'id', 'work_type', 'title', 'status', 'priority', 'progress',
            'start_date', 'due_date',
            'level', 'tree_id', 'lft', 'rght',
            'parent_id', 'created_by_id',
        )
        .annotate(children_count=Count('children'))
        .order_by('lft')  # Ensure tree order (left-to-right traversal)
    )

    # Get type-specific data
    type_specific_data = {}
    if work_item.is_project:
        type_specific_data = work_item.project_data
    elif work_item.is_activity:
        type_specific_data = work_item.activity_data
    elif work_item.is_task:
        type_specific_data = work_item.task_data

    # Get permissions for current user
    permissions = get_work_item_permissions(request.user, work_item)

    # Get related items (manual links only; siblings are linked bidirectionally)
    related_items = work_item.related_items.order_by('title')

    context = {
        'work_item': work_item,
        'breadcrumb': breadcrumb,
        'children': children,
        'type_specific_data': type_specific_data,
        'related_items': related_items,
        'can_edit': permissions['can_edit'],
        'can_delete': permissions['can_delete'],
    }

    return render(request, 'work_items/work_item_detail.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def work_item_create(request):
    """
    Create new work item.

    Features:
    - Unified form with type selector
    - Parent selector (autocomplete, hierarchical)
    - Dynamic form fields based on type
    - Validation rules (enforce hierarchy constraints)
    - Success redirect to detail view
    """
    # Get parent_id from query params (for "Add Child" quick action)
    parent_id = request.GET.get('parent')
    parent = None
    if parent_id:
        parent = get_object_or_404(WorkItem, pk=parent_id)

    # Get ppa_id from query params (for "Add Work Item" from PPA page)
    ppa_id = request.GET.get('ppa_id')
    related_ppa = None
    if ppa_id:
        from monitoring.models import MonitoringEntry
        related_ppa = get_object_or_404(MonitoringEntry, pk=ppa_id)

        # Auto-set parent to execution project if it exists
        # This ensures the work item appears in the PPA's work item tree
        if related_ppa.execution_project and not parent:
            parent = related_ppa.execution_project

    requested_work_type = request.GET.get('work_type')
    valid_work_types = {code for code, _ in WorkItem.WORK_TYPE_CHOICES}

    if request.method == 'POST':
        form = WorkItemForm(request.POST)
        form.user = request.user  # For created_by field

        if form.is_valid():
            work_item = form.save(commit=False)
            work_item.created_by = request.user

            work_item.save()
            form.save_m2m()  # Save many-to-many fields

            # Auto-populate isolation fields (ppa_category, implementing_moa) from PPA source
            if work_item.populate_isolation_fields():
                work_item.save(update_fields=['ppa_category', 'implementing_moa'])

            # Link to existing siblings (if any)
            work_item.sync_sibling_related_links()

            # Invalidate caches
            invalidate_calendar_cache(request.user.id)
            invalidate_work_item_tree_cache(work_item)  # Invalidate tree cache

            messages.success(
                request,
                f'{work_item.get_work_type_display()} "{work_item.title}" created successfully.'
            )
            return redirect('common:work_item_detail', pk=work_item.pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        # Pre-populate form if parent specified
        initial = {}
        if parent:
            initial['parent'] = parent
            # Suggest default work_type based on parent
            if parent.work_type == WorkItem.WORK_TYPE_PROJECT:
                initial['work_type'] = WorkItem.WORK_TYPE_ACTIVITY
            elif parent.work_type == WorkItem.WORK_TYPE_ACTIVITY:
                initial['work_type'] = WorkItem.WORK_TYPE_TASK
            elif parent.work_type == WorkItem.WORK_TYPE_TASK:
                initial['work_type'] = WorkItem.WORK_TYPE_SUBTASK

        if related_ppa:
            initial['related_ppa'] = related_ppa

        if requested_work_type in valid_work_types and 'work_type' not in initial:
            initial['work_type'] = requested_work_type

        form = WorkItemForm(initial=initial)

    # Build breadcrumb if parent exists
    breadcrumb = []
    if parent:
        breadcrumb = list(parent.get_ancestors(include_self=True))

    context = {
        'form': form,
        'action': 'Create',
        'parent': parent,
        'breadcrumb': breadcrumb,
        'allowed_child_type_choices': [],
        'ppa': related_ppa,  # Pass PPA context to template
        'ppa_info': related_ppa,  # Alias for template clarity
        'ppa_id': ppa_id,  # Pass ppa_id for form submission
    }

    # If HTMX request, return modal partial
    if request.headers.get('HX-Request'):
        return render(request, 'work_items/partials/work_item_modal_form.html', context)

    return render(request, 'work_items/work_item_form.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def work_item_edit(request, pk):
    """
    Edit existing work item.

    Features:
    - Pre-populated form
    - Allow changing parent (with validation)
    - Allow changing type (with data preservation)
    - Update children progress if parent completed
    """
    work_item = get_object_or_404(
        WorkItem.objects.prefetch_related('related_items'),
        pk=pk
    )

    # Check edit permissions
    permissions = get_work_item_permissions(request.user, work_item)
    if not permissions['can_edit']:
        messages.error(request, 'You do not have permission to edit this work item.')
        raise PermissionDenied('You do not have permission to edit this work item.')

    if request.method == 'POST':
        is_autosave = request.headers.get('X-Autosave') == 'true'
        form = WorkItemForm(request.POST, instance=work_item)

        if form.is_valid():
            work_item = form.save()

            # Auto-populate isolation fields (ppa_category, implementing_moa) from PPA source
            # This handles cases where parent or related_ppa was changed
            if work_item.populate_isolation_fields():
                work_item.save(update_fields=['ppa_category', 'implementing_moa'])

            # Update progress of parent if auto_calculate is enabled
            if work_item.parent and work_item.parent.auto_calculate_progress:
                work_item.parent.update_progress()

            # Invalidate caches
            invalidate_calendar_cache(request.user.id)
            invalidate_work_item_tree_cache(work_item)  # Invalidate tree cache

            if is_autosave:
                saved_at = timezone.localtime()
                return JsonResponse({
                    'success': True,
                    'saved_at': saved_at.isoformat(),
                })

            messages.success(
                request,
                f'{work_item.get_work_type_display()} "{work_item.title}" updated successfully.'
            )
            return redirect('common:work_item_detail', pk=work_item.pk)
        else:
            if is_autosave:
                return JsonResponse({
                    'success': False,
                    'errors': form.errors,
                }, status=400)
            messages.error(request, 'Please correct the errors below.')
    else:
        form = WorkItemForm(instance=work_item)

    # Build breadcrumb from work item ancestors
    breadcrumb = list(work_item.get_ancestors(include_self=True))

    # Allowed child type options for quick add widget
    work_type_labels = dict(WorkItem.WORK_TYPE_CHOICES)
    allowed_child_type_codes = WorkItem.get_allowed_child_types(work_item.work_type)
    allowed_child_type_choices = [
        (code, work_type_labels.get(code, code.replace('_', ' ').title()))
        for code in allowed_child_type_codes
    ]

    # Get related items limited to same level within same parent
    # IMPORTANT: Filter by ppa_category to enforce MOA/OOBC isolation
    related_parent_id = work_item.parent_id
    related_queryset = WorkItem.objects.filter(
        work_type=work_item.work_type,
        parent_id=related_parent_id,
        ppa_category=work_item.ppa_category  # Same category (moa_ppa/oobc_ppa/obc_request)
    ).exclude(pk=work_item.pk).exclude(pk__in=work_item.related_items.values_list('pk', flat=True))

    # For MOA PPAs, also filter by implementing_moa to ensure MOA-specific isolation
    if work_item.ppa_category == 'moa_ppa' and work_item.implementing_moa:
        related_queryset = related_queryset.filter(implementing_moa=work_item.implementing_moa)

    related_queryset = related_queryset.only('id', 'work_type', 'title').order_by('title')[:100]

    context = {
        'form': form,
        'action': 'Edit',
        'work_item': work_item,
        'breadcrumb': breadcrumb,
        'all_work_items': related_queryset,
        'allowed_child_type_choices': allowed_child_type_choices,
        'related_items': work_item.related_items.order_by('title'),
    }

    return render(request, 'work_items/work_item_form.html', context)


@login_required
def work_item_delete_modal(request, pk):
    """
    HTMX endpoint: Return delete confirmation modal content.

    Used for displaying delete confirmation in a modal dialog.
    Returns modal HTML with work item details and descendant count.
    """
    work_item = get_object_or_404(WorkItem, pk=pk)

    # Check delete permissions
    permissions = get_work_item_permissions(request.user, work_item)
    if not permissions['can_delete']:
        # Return error modal content
        context = {
            'error_message': 'You do not have permission to delete this work item.',
        }
        return render(request, 'work_items/_work_item_delete_error_modal.html', context)

    # Get descendants count
    descendants = work_item.get_descendants()
    descendants_count = descendants.count()

    context = {
        'work_item': work_item,
        'descendants': descendants,
        'descendants_count': descendants_count,
    }

    # Wrap in modal component
    return render(request, 'components/modal.html', {
        'modal_id': 'work-item-delete-modal',
        'title': 'Delete Work Item',
        'content_template': 'work_items/_work_item_delete_modal.html',
        'size': 'md',
        'closeable': True,
        'backdrop_dismiss': True,
        **context
    })


@login_required
@require_http_methods(["GET", "POST", "DELETE"])
def work_item_delete(request, pk):
    """
    Delete work item with cascade options.

    Features:
    - Two-step confirmation (GET/POST for full page)
    - HTMX DELETE support (from calendar modal)
    - Show impact (number of children to be deleted)
    - Cascade delete children OR re-parent to grandparent (user choice)
    - Success message, redirect to list OR HTMX trigger
    """
    work_item = get_object_or_404(WorkItem, pk=pk)

    # Check delete permissions
    permissions = get_work_item_permissions(request.user, work_item)
    if not permissions['can_delete']:
        # Handle HTMX DELETE request
        if request.method == 'DELETE':
            import json
            return HttpResponse(
                status=403,
                headers={
                    'HX-Trigger': json.dumps({
                        'showToast': {
                            'message': 'You do not have permission to delete this work item.',
                            'level': 'error'
                        }
                    })
                }
            )
        # Handle regular request
        messages.error(request, 'You do not have permission to delete this work item.')
        raise PermissionDenied('You do not have permission to delete this work item.')

    # Get descendants count
    descendants = work_item.get_descendants()
    descendants_count = descendants.count()

    current_url = request.headers.get('HX-Current-URL', '') or ''
    referer = request.META.get('HTTP_REFERER', '') or ''
    is_moa_page = '/coordination/organizations/' in current_url or '/coordination/organizations/' in referer

    # Handle HTMX DELETE request (from calendar modal)
    if request.method == 'DELETE':
        import json

        work_title = work_item.title
        work_type_display = work_item.get_work_type_display()
        work_item_id = str(work_item.id)

        # Invalidate tree cache BEFORE deletion (while parent still exists)
        invalidate_work_item_tree_cache(work_item)

        # Cascade delete (MPTT handles this automatically)
        work_item.delete()

        # CRITICAL: Invalidate calendar cache to prevent stale data
        invalidate_calendar_cache(request.user.id)

        # Return empty response with HX-Trigger to update calendar
        organization_id = (
            work_item.implementing_moa_id
            or (work_item.related_ppa.implementing_moa_id if work_item.related_ppa else None)
        )

        trigger_payload = {
            'workItemDeleted': {
                'id': work_item_id,
                'title': work_title,
                'type': work_type_display
            },
            'showToast': {
                'message': f'{work_type_display} "{work_title}" deleted successfully',
                'level': 'success'
            },
            'refreshCalendar': True
        }

        if is_moa_page:
            trigger_payload['refreshMoaWorkItems'] = {
                'organizationId': str(organization_id) if organization_id else None,
                'workItemId': work_item_id,
            }

        return HttpResponse(status=200, headers={'HX-Trigger': json.dumps(trigger_payload)})

    if request.method == 'POST':
        action = request.POST.get('action', 'cancel')

        if action == 'delete':
            # Get re-parent option
            reparent = request.POST.get('reparent', 'no') == 'yes'

            work_title = work_item.title
            work_type_display = work_item.get_work_type_display()
            parent = work_item.parent

            if reparent and parent:
                # Re-parent children to grandparent
                for child in work_item.get_children():
                    child.move_to(parent, 'last-child')
                    child.save()

                messages.success(
                    request,
                    f'{work_type_display} "{work_title}" deleted. {descendants_count} child(ren) re-parented.'
                )
            else:
                # Cascade delete (MPTT handles this automatically)
                messages.success(
                    request,
                    f'{work_type_display} "{work_title}" and {descendants_count} descendant(s) deleted.'
                )

            # Invalidate tree cache BEFORE deletion
            invalidate_work_item_tree_cache(work_item)

            # Delete the work item
            work_item.delete()

            # Invalidate calendar cache
            invalidate_calendar_cache(request.user.id)

            return redirect('common:work_item_list')
        else:
            # Cancel - redirect back to detail
            return redirect('common:work_item_detail', pk=work_item.pk)

    context = {
        'work_item': work_item,
        'descendants': descendants,
        'descendants_count': descendants_count,
        'can_reparent': bool(work_item.parent),
    }

    return render(request, 'work_items/work_item_delete_confirm.html', context)


@login_required
def work_item_tree_partial(request, pk):
    """
    HTMX endpoint: Return children tree for expand/collapse.

    Used for interactive tree expansion without full page reload.

    Performance optimizations:
    - select_related() for ForeignKey fields (parent, created_by)
    - prefetch_related() for ManyToMany fields (assignees, teams)
    - only() to load only required fields for template rendering
    - Caching with 5-minute TTL for frequently accessed children
    """
    from django.core.cache import cache
    import hashlib

    # Generate cache key based on work item ID and user (for permission-aware caching)
    cache_key = f"work_item_children:{pk}:{request.user.id}"

    # Try to get from cache
    cached_html = cache.get(cache_key)
    if cached_html:
        return HttpResponse(cached_html)

    # Get parent work item (only need level field)
    work_item = get_object_or_404(WorkItem.objects.only('id', 'level'), pk=pk)

    # Optimized query: Load only fields needed by template
    children = (
        work_item.get_children()
        .select_related('parent', 'created_by')  # Avoid N+1 on FK fields
        .prefetch_related('assignees', 'teams')  # Preload M2M relationships
        .only(
            # Core fields
            'id', 'work_type', 'title', 'status', 'priority', 'progress',
            # Dates
            'start_date', 'due_date',
            # MPTT fields
            'level', 'tree_id', 'lft', 'rght',
            # Foreign keys (for select_related)
            'parent_id', 'created_by_id',
        )
        .annotate(children_count=Count('children'))
        .order_by('lft')  # CRITICAL: Ensure tree order (left-to-right traversal)
    )

    context = {
        'work_items': children,
        'parent_level': work_item.level + 1,
    }

    # Render and cache the response
    response = render(request, 'work_items/_work_item_tree_nodes.html', context)

    # Cache for 5 minutes (300 seconds)
    # Invalidated on work item updates via signal or explicit cache clear
    cache.set(cache_key, response.content.decode('utf-8'), 300)

    return response


@login_required
@require_POST
def work_item_update_progress(request, pk):
    """
    HTMX endpoint: Update work item progress.

    Used for inline progress updates without full page reload.
    """
    work_item = get_object_or_404(WorkItem, pk=pk)

    new_progress = request.POST.get('progress', 0)
    try:
        new_progress = int(new_progress)
        if 0 <= new_progress <= 100:
            work_item.progress = new_progress
            work_item.save(update_fields=['progress', 'updated_at'])

            # Update parent if auto-calculate enabled
            if work_item.parent and work_item.parent.auto_calculate_progress:
                work_item.parent.update_progress()

            return JsonResponse({
                'success': True,
                'progress': work_item.progress,
                'message': 'Progress updated'
            })
    except (ValueError, TypeError):
        pass

    return JsonResponse({
        'success': False,
        'message': 'Invalid progress value'
    }, status=400)


@login_required
def work_item_calendar_feed(request):
    """
    JSON feed for FullCalendar integration.

    Returns all calendar-visible work items as FullCalendar events.

    CRITICAL: This endpoint is for the general OOBC calendar at /oobc-management/calendar/
    It should ONLY show general OOBC work items, NOT PPA-specific work items.
    PPA calendars have their own separate endpoints.

    Query Parameters:
        - start: Start date filter
        - end: End date filter
        - assignee: Filter by assignee user ID (for staff-specific calendars)
    """
    # Get date range and assignee from query params
    start = request.GET.get('start')
    end = request.GET.get('end')
    assignee_id = request.GET.get('assignee')

    # Filter work items - ONLY general OOBC work items (no PPA-specific items)
    queryset = WorkItem.objects.filter(
        is_calendar_visible=True,
        # Exclude PPA-specific work items from general OOBC calendar
        related_ppa__isnull=True,
        ppa_category__isnull=True,
        implementing_moa__isnull=True
    )

    if start:
        queryset = queryset.filter(due_date__gte=start)
    if end:
        queryset = queryset.filter(start_date__lte=end)

    # Filter by assignee (for staff-specific calendars)
    if assignee_id:
        queryset = queryset.filter(assignees__id=assignee_id)
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Staff calendar: Filtering by assignee ID {assignee_id}, found {queryset.count()} work items")

    # Convert to FullCalendar events
    events = [work_item.get_calendar_event() for work_item in queryset]

    return JsonResponse(events, safe=False)


@login_required
def work_item_sidebar_detail(request, pk):
    """
    HTMX endpoint: Return work item detail view for sidebar (calendar or work items tree).

    Used for displaying work item information in the sidebar detail panel.
    """
    work_item = get_object_or_404(WorkItem, pk=pk)

    # Get permissions for current user
    permissions = get_work_item_permissions(request.user, work_item)

    referer = request.META.get('HTTP_REFERER', '')
    hx_target_raw = request.headers.get('HX-Target', '') or ''
    hx_target = hx_target_raw.lstrip('#')

    is_sidebar_target = hx_target in {'sidebar-content', 'ppa-sidebar-content'}
    is_work_items_tree = 'work-items' in referer or is_sidebar_target
    is_staff_profile = '/staff/profiles/' in referer or '/profile/' in referer
    is_ppa_sidebar = hx_target == 'ppa-sidebar-content'
    use_sidebar_templates = is_work_items_tree or is_staff_profile or is_ppa_sidebar
    is_calendar_context = not use_sidebar_templates

    if hx_target:
        sidebar_target_id = hx_target
    elif use_sidebar_templates:
        sidebar_target_id = 'sidebar-content'
    else:
        sidebar_target_id = 'detailPanelBody'

    close_action = 'closeSidebar'
    if sidebar_target_id.endswith('detailPanelBody'):
        prefix = sidebar_target_id[: -len('detailPanelBody')].rstrip('-')
        close_action = f'{prefix}_closeDetailPanel' if prefix else 'closeDetailPanel'

    if is_ppa_sidebar:
        close_action = 'closePPASidebar'

    context = {
        'work_item': work_item,
        'can_edit': permissions['can_edit'],
        'can_delete': permissions['can_delete'],
        'sidebar_target_id': sidebar_target_id,
        'close_action': close_action,
    }

    return render(request, 'work_items/partials/sidebar_detail.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def work_item_sidebar_edit(request, pk):
    """
    HTMX endpoint: Handle inline editing in sidebar (calendar or work items tree).

    GET: Return edit form HTML (or detail view if no edit permission)
    POST: Process form submission and return updated detail view
    """
    work_item = get_object_or_404(WorkItem, pk=pk)

    # Check edit permissions
    permissions = get_work_item_permissions(request.user, work_item)

    referer = request.META.get('HTTP_REFERER', '')
    hx_target_raw = request.headers.get('HX-Target', '') or ''
    hx_target = hx_target_raw.lstrip('#')

    is_tree_page = 'work-items' in referer
    is_moa_page = '/coordination/organizations/' in referer
    is_ppa_sidebar = hx_target == 'ppa-sidebar-content' or ('/monitoring/entry/' in referer and not is_moa_page)
    is_staff_sidebar = '/staff/profiles/' in referer or '/profile/' in referer

    use_sidebar_templates = is_tree_page or is_ppa_sidebar or is_staff_sidebar or is_moa_page
    should_update_oob_row = is_tree_page or is_ppa_sidebar

    if hx_target:
        sidebar_target_id = hx_target
    elif use_sidebar_templates:
        sidebar_target_id = 'sidebar-content'
    else:
        sidebar_target_id = 'detailPanelBody'

    close_action = 'closeSidebar'
    if sidebar_target_id.endswith('detailPanelBody'):
        prefix = sidebar_target_id[: -len('detailPanelBody')].rstrip('-')
        close_action = f'{prefix}_closeDetailPanel' if prefix else 'closeDetailPanel'

    if is_ppa_sidebar:
        close_action = 'closePPASidebar'

    # For GET requests: If user can't edit, gracefully show detail view instead
    if request.method == 'GET' and not permissions['can_edit']:
        # Fallback to read-only detail view
        context = {
            'work_item': work_item,
            'can_edit': permissions['can_edit'],
            'can_delete': permissions['can_delete'],
            'sidebar_target_id': sidebar_target_id,
            'close_action': close_action,
        }
        return render(request, 'work_items/partials/sidebar_detail.html', context)

    # For POST requests: If user can't edit, return 403 error
    if request.method == 'POST' and not permissions['can_edit']:
        import json
        return HttpResponse(
            status=403,
            headers={
                'HX-Trigger': json.dumps({
                    'showToast': {
                        'message': 'You do not have permission to edit this work item.',
                        'level': 'error'
                    }
                })
            }
        )

    if request.method == 'POST':
        from common.forms.work_items import WorkItemQuickEditForm

        form = WorkItemQuickEditForm(request.POST, instance=work_item, user=request.user)
        if form.is_valid():
            work_item = form.save()

            # Update progress of parent if auto_calculate is enabled
            if work_item.parent and work_item.parent.auto_calculate_progress:
                work_item.parent.update_progress()

            # Invalidate calendar cache
            invalidate_calendar_cache(request.user.id)

            # Refresh work_item from database to get all updated fields
            work_item.refresh_from_db()

            # For work items tree: return detail view + updated row via out-of-band swap
            # For calendar: return detail view and trigger calendar refresh
            import json

            if should_update_oob_row:
                # Return updated edit form for sidebar + updated tree row for instant update
                from django.template.loader import render_to_string
                from common.forms.work_items import WorkItemQuickEditForm

                # Re-render the edit form with updated data (keep sidebar open)
                form = WorkItemQuickEditForm(instance=work_item, user=request.user)
                context = {
                    'form': form,
                    'work_item': work_item,
                    'sidebar_target_id': sidebar_target_id,
                    'close_action': close_action,
                }
                edit_form_html = render_to_string('work_items/partials/sidebar_edit_form.html', context, request=request)

                # Render the updated row for out-of-band swap
                if is_tree_page:
                    row_template = 'work_items/_work_item_tree_row.html'
                else:
                    row_template = 'monitoring/partials/_ppa_work_item_row.html'

                row_html = render_to_string(row_template, {'work_item': work_item}, request=request)

                # Extract ONLY the main <tr> (exclude placeholder and skeleton rows)
                import re
                # Match the main row: from opening <tr id="..."> to its closing </tr>
                # Use non-greedy match to get just the first <tr>...</tr>
                row_id = f'work-item-row-{work_item.id}' if is_tree_page else f'ppa-work-item-row-{work_item.id}'
                pattern = rf'(<tr\s+id="{row_id}"[^>]*>.*?</tr>)'
                match = re.search(pattern, row_html, re.DOTALL)

                if match:
                    # Successfully extracted just the main row
                    main_row_only = match.group(1)
                    # Add hx-swap-oob attribute right after the opening <tr tag
                    row_html_with_oob = main_row_only.replace(
                        '<tr ',
                        '<tr hx-swap-oob="true" ',
                        1
                    )
                else:
                    # Fallback: add hx-swap-oob to entire template output
                    row_html_with_oob = row_html.replace(
                        '<tr ',
                        '<tr hx-swap-oob="true" ',
                        1
                    )

                # Wrap form in div container for proper HTML structure
                # Wrap row in table structure to prevent browser from stripping it
                # HTMX will process OOB swaps before the main innerHTML swap
                from django.http import HttpResponse
                combined_html = f'''
                <div>{edit_form_html}</div>
                <table style="display:none;">
                    <tbody>
                        {row_html_with_oob}
                    </tbody>
                </table>
                '''

                response = HttpResponse(combined_html)
                response['HX-Trigger'] = json.dumps({
                    'showToast': {
                        'message': f'{work_item.get_work_type_display()} updated successfully',
                        'level': 'success'
                    }
                })
                return response
            else:
                # Return updated detail view HTML (calendar, PPA sidebar, or staff sidebar)
                context = {
                    'work_item': work_item,
                    'can_edit': permissions['can_edit'],
                    'can_delete': permissions['can_delete'],
                    'sidebar_target_id': sidebar_target_id,
                    'close_action': close_action,
                }
                response = render(request, 'work_items/partials/sidebar_detail.html', context)

                triggers = {
                    'showToast': {
                        'message': f'{work_item.get_work_type_display()} updated successfully',
                        'level': 'success'
                    }
                }
                if not use_sidebar_templates:
                    triggers['calendarRefresh'] = {'eventId': str(work_item.pk)}
                if is_ppa_sidebar:
                    triggers['refreshPPAWorkItems'] = {
                        'reload': False,
                        'workItemId': str(work_item.pk)
                    }
                if is_moa_page:
                    organization_id = (
                        work_item.implementing_moa_id
                        or (work_item.related_ppa.implementing_moa_id if work_item.related_ppa else None)
                    )
                    triggers['refreshMoaWorkItems'] = {
                        'organizationId': str(organization_id) if organization_id else None,
                        'workItemId': str(work_item.pk),
                    }
                    triggers['closeSidebar'] = True

                response['HX-Trigger'] = json.dumps(triggers)
                return response
        else:
            # Return form with errors
            context = {
                'form': form,
                'work_item': work_item,
                'sidebar_target_id': sidebar_target_id,
                'close_action': close_action,
            }
            return render(request, 'work_items/partials/sidebar_edit_form.html', context)

    else:  # GET
        from common.forms.work_items import WorkItemQuickEditForm

        form = WorkItemQuickEditForm(instance=work_item, user=request.user)
        context = {
            'form': form,
            'work_item': work_item,
            'sidebar_target_id': sidebar_target_id,
            'close_action': close_action,
        }
        return render(request, 'work_items/partials/sidebar_edit_form.html', context)


@login_required
@require_http_methods(["POST"])
def work_item_duplicate(request, pk):
    """
    HTMX endpoint: Duplicate work item.

    Creates a copy of the work item with " (Copy)" suffix and opens it for editing.
    Returns the edit form for the duplicated item with calendar refresh trigger.
    """
    original = get_object_or_404(WorkItem, pk=pk)

    # Check if user has permission to create work items
    if not request.user.is_staff and not request.user.has_perm('common.add_workitem'):
        import json
        return HttpResponse(
            status=403,
            headers={
                'HX-Trigger': json.dumps({
                    'showToast': {
                        'message': 'You do not have permission to duplicate work items.',
                        'level': 'error'
                    }
                })
            }
        )

    # Create duplicate
    duplicate = WorkItem.objects.get(pk=original.pk)
    duplicate.pk = None  # Create new instance
    duplicate.id = None
    duplicate.title = f"{original.title} (Copy)"
    duplicate.created_by = request.user
    duplicate.save()

    # Copy many-to-many relationships
    duplicate.assignees.set(original.assignees.all())
    duplicate.teams.set(original.teams.all())

    # Invalidate calendar cache
    invalidate_calendar_cache(request.user.id)

    # Load edit form for the duplicate
    from common.forms.work_items import WorkItemQuickEditForm
    form = WorkItemQuickEditForm(instance=duplicate, user=request.user)
    target_id = request.headers.get('HX-Target', '').lstrip('#') or 'detailPanelBody'
    close_action = 'closeSidebar'
    if target_id.endswith('detailPanelBody'):
        prefix = target_id[: -len('detailPanelBody')].rstrip('-')
        close_action = f'{prefix}_closeDetailPanel' if prefix else 'closeDetailPanel'
    context = {
        'form': form,
        'work_item': duplicate,
        'sidebar_target_id': target_id,
        'close_action': close_action,
    }

    response = render(request, 'work_items/partials/sidebar_edit_form.html', context)

    # Trigger calendar refresh and success toast
    import json
    response['HX-Trigger'] = json.dumps({
        'calendarRefresh': {'eventId': str(duplicate.pk)},
        'showToast': {
            'message': f'Duplicated as "{duplicate.title}"',
            'level': 'success'
        }
    })

    return response


@login_required
@require_http_methods(["GET", "POST"])
def work_item_sidebar_create(request):
    """
    HTMX endpoint: Create work item from sidebar (calendar, work items tree, or PPA page).

    GET: Return create form HTML with pre-populated date from query params
    POST: Process form submission and return success response with refresh trigger

    This enables quick creation: double-click date → create form opens
    """
    from coordination.models import Organization
    from monitoring.models import MonitoringEntry

    # Get PPA ID from query params (if creating from PPA page)
    ppa_id = request.GET.get('ppa_id') or request.POST.get('ppa_id')
    if not ppa_id:
        ppa_id = None
    related_ppa = None
    if ppa_id:
        try:
            related_ppa = MonitoringEntry.objects.get(pk=ppa_id)
        except MonitoringEntry.DoesNotExist:
            related_ppa = None

    implementing_moa_param = request.GET.get('implementing_moa') or request.POST.get('implementing_moa')
    if not implementing_moa_param:
        implementing_moa_param = None
    ppa_options = []
    has_disabled_ppa_options = False
    if not related_ppa and implementing_moa_param:
        ppa_queryset = MonitoringEntry.objects.filter(
            category='moa_ppa',
            implementing_moa_id=implementing_moa_param,
        ).order_by('title')
        ppa_options = [
            {
                'id': str(ppa.pk),
                'title': ppa.title,
                'tracking_enabled': ppa.enable_workitem_tracking,
            }
            for ppa in ppa_queryset
        ]
        tracking_enabled = [option for option in ppa_options if option['tracking_enabled']]
        has_disabled_ppa_options = any(not option['tracking_enabled'] for option in ppa_options)
        if len(tracking_enabled) == 1:
            try:
                related_ppa = MonitoringEntry.objects.get(pk=tracking_enabled[0]['id'])
                ppa_id = tracking_enabled[0]['id']
            except MonitoringEntry.DoesNotExist:
                related_ppa = None

    # Determine which template to use based on referrer
    referer = request.META.get('HTTP_REFERER', '')
    hx_current_url = request.META.get('HTTP_HX_CURRENT_URL', '')
    path_context = f'{referer} {hx_current_url}'

    is_moa_page = (
        '/coordination/organizations/' in path_context
        or bool(implementing_moa_param)
    )
    is_work_items_tree = 'work-items' in path_context
    is_oobc_dashboard = (
        '/monitoring/oobc-initiatives/' in path_context
        or request.GET.get('oobc_dashboard') == '1'
    )
    is_oobc_advanced_calendar = '/oobc-management/calendar/advanced-modern/' in path_context
    is_staff_profile = '/staff/profiles/' in path_context or '/profile/' in path_context
    is_ppa_page = (
        '/monitoring/entry/' in path_context
        or (ppa_id is not None and not is_moa_page)
    )
    use_ppa_sidebar = bool(is_ppa_page and not is_moa_page)

    hx_target_raw = request.headers.get('HX-Target', '') or ''
    hx_target = hx_target_raw.lstrip('#')

    is_calendar_context = not (is_ppa_page or is_moa_page or is_work_items_tree or is_staff_profile)

    if hx_target:
        sidebar_target_id = hx_target
    elif use_ppa_sidebar:
        sidebar_target_id = 'ppa-sidebar-content'
    elif is_calendar_context:
        sidebar_target_id = 'detailPanelBody'
    else:
        sidebar_target_id = 'sidebar-content'

    close_action = 'closeSidebar'
    if sidebar_target_id.endswith('detailPanelBody'):
        prefix = sidebar_target_id[: -len('detailPanelBody')].rstrip('-')
        close_action = f'{prefix}_closeDetailPanel' if prefix else 'closeDetailPanel'

    if use_ppa_sidebar:
        close_action = 'closePPASidebar'

    oobc_org = (
        Organization.objects.filter(name__iexact="Office for Other Bangsamoro Communities (OOBC)").first()
        or Organization.objects.filter(acronym__iexact="OOBC").first()
    )
    auto_assign_oobc = bool(
        (is_work_items_tree or is_oobc_dashboard or is_oobc_advanced_calendar)
        and not is_moa_page
        and not is_ppa_page
        and oobc_org
    )

    implementing_moa_obj = None
    if related_ppa and related_ppa.implementing_moa:
        implementing_moa_obj = related_ppa.implementing_moa
    elif implementing_moa_param:
        try:
            implementing_moa_obj = Organization.objects.get(pk=implementing_moa_param)
        except Organization.DoesNotExist:
            implementing_moa_obj = None
    elif auto_assign_oobc:
        implementing_moa_obj = oobc_org

    resolved_implementing_moa_id = str(implementing_moa_obj.pk) if implementing_moa_obj else None
    lock_implementing_moa = bool(implementing_moa_obj and (auto_assign_oobc or is_moa_page or related_ppa))
    requires_related_ppa_flag = bool(
        is_ppa_page or is_moa_page or (implementing_moa_param and not auto_assign_oobc)
    )
    if is_work_items_tree:
        requires_related_ppa_flag = False
    if auto_assign_oobc:
        requires_related_ppa_flag = False

    oobc_ppa_queryset = MonitoringEntry.objects.none()
    if auto_assign_oobc:
        oobc_ppa_queryset = MonitoringEntry.objects.filter(
            Q(category="oobc_ppa") | Q(category="moa_ppa", implementing_moa=oobc_org),
        ).order_by("title")

    # Surface PPA options for auto-assigned OOBC context or when MOA was resolved indirectly
    if not related_ppa and not ppa_options and implementing_moa_obj:
        if auto_assign_oobc:
            ppa_queryset = oobc_ppa_queryset
        else:
            ppa_queryset = (
                MonitoringEntry.objects.filter(
                    category__in=["moa_ppa", "oobc_ppa"],
                    implementing_moa=implementing_moa_obj,
                )
                .order_by("title")
            )

        ppa_options = [
            {
                "id": str(ppa.pk),
                "title": ppa.title,
                "tracking_enabled": ppa.enable_workitem_tracking,
            }
            for ppa in ppa_queryset
        ]
        tracking_enabled = [option for option in ppa_options if option["tracking_enabled"]]
        has_disabled_ppa_options = any(not option["tracking_enabled"] for option in ppa_options)
        if len(tracking_enabled) == 1 and not ppa_id:
            try:
                related_ppa = MonitoringEntry.objects.get(pk=tracking_enabled[0]["id"])
                ppa_id = tracking_enabled[0]["id"]
            except MonitoringEntry.DoesNotExist:
                related_ppa = None

    # Use PPA-specific template if on PPA page, otherwise use sidebar template
    create_template = 'work_items/partials/sidebar_create_form.html'

    if request.method == 'POST':
        from common.forms.work_items import WorkItemQuickEditForm
        from django.contrib.auth import get_user_model
        User = get_user_model()

        post_data = request.POST.copy()
        if auto_assign_oobc and oobc_org and not post_data.get('implementing_moa'):
            post_data['implementing_moa'] = str(oobc_org.pk)

        form = WorkItemQuickEditForm(post_data, user=request.user)
        if auto_assign_oobc:
            form.fields['related_ppa'].queryset = oobc_ppa_queryset
            if oobc_org:
                form.fields['implementing_moa'].queryset = Organization.objects.filter(pk=oobc_org.pk)
        assignee_id = post_data.get('assignee_id')
        assignee_user = None
        if assignee_id:
            try:
                assignee_user = User.objects.get(pk=assignee_id)
            except User.DoesNotExist:
                assignee_user = None

        if form.is_valid():
            cleaned_related_ppa = form.cleaned_data.get('related_ppa')
            target_related_ppa = cleaned_related_ppa or related_ppa

            # Only enforce PPA selection when working within PPA-anchored flows
            if not target_related_ppa and requires_related_ppa_flag:
                if ppa_options:
                    form.add_error(None, "Please select a MOA PPA before creating a work item.")
                else:
                    form.add_error(None, "Unable to determine the related PPA. Open this form from a specific PPA detail page and try again.")
                context = {
                    'form': form,
                    'is_create': True,
                    'ppa_id': ppa_id,
                    'ppa_info': related_ppa,
                    'ppa_options': ppa_options,
                    'selected_ppa_id': post_data.get('ppa_id') or ppa_id,
                    'implementing_moa_id': resolved_implementing_moa_id,
                    'has_disabled_ppa_options': has_disabled_ppa_options,
                    'use_ppa_sidebar': use_ppa_sidebar,
                    'sidebar_target_id': sidebar_target_id,
                    'lock_implementing_moa': lock_implementing_moa,
                    'implementing_moa_obj': implementing_moa_obj,
                    'auto_assign_oobc': auto_assign_oobc,
                    'assignee_user': assignee_user,
                    'assignee_id': assignee_id,
                    'requires_related_ppa': requires_related_ppa_flag and not auto_assign_oobc,
                    'close_action': close_action,
                }
                return render(request, create_template, context)

            # Form handles created_by and assignee conversion
            work_item = form.save(commit=False)

            # Adopt the PPA selected in the form (if any) as the active related PPA
            if target_related_ppa:
                related_ppa = target_related_ppa

            if related_ppa:
                import json
                import logging

                logger = logging.getLogger(__name__)

                try:
                    project = related_ppa.ensure_execution_project(
                        created_by=request.user,
                        updated_by=request.user,
                    )
                except ValidationError as exc:
                    message = "; ".join(exc.messages) if hasattr(exc, "messages") else str(exc)
                    logger.warning(
                        "Unable to ensure execution project for PPA %s: %s",
                        related_ppa.pk,
                        message,
                    )
                    return HttpResponse(
                        status=400,
                        headers={
                            'HX-Trigger': json.dumps({
                                'showToast': {
                                    'message': message,
                                    'level': 'error'
                                }
                            })
                        }
                    )
                except Exception:
                    logger = logging.getLogger(__name__)
                    logger.exception(
                        "Unexpected error ensuring execution project for PPA %s",
                        related_ppa.pk,
                    )
                    return HttpResponse(
                        status=500,
                        headers={
                            'HX-Trigger': json.dumps({
                                'showToast': {
                                    'message': 'Unable to create the work item right now. Please try again.',
                                    'level': 'error'
                                }
                            })
                        }
                    )

                work_item.related_ppa = related_ppa

                # Auto-parent to the ensured execution project when none supplied
                if project and not work_item.parent:
                    work_item.parent = project

                # Align implementing MOA with related PPA when available
                if related_ppa.implementing_moa:
                    work_item.implementing_moa = related_ppa.implementing_moa

                # Auto-populate isolation fields (ppa_category, implementing_moa)
                work_item.populate_isolation_fields()

            work_item.save()

            # Handle assignee from hidden field (if creating from staff profile)
            if assignee_user:
                work_item.assigned_users.add(assignee_user)

            # Link to PPA if ppa_id was provided
            # Invalidate caches
            invalidate_calendar_cache(request.user.id)
            invalidate_work_item_tree_cache(work_item)

            # Return success response with appropriate triggers
            import json
            response = HttpResponse(status=204)  # No Content

            if is_ppa_page:
                # PPA page: refresh tab content via HTMX helpers (no full reload)
                trigger_payload = {
                    'reload': False,
                    'entryId': str(related_ppa.pk) if related_ppa else ppa_id,
                    'workItemId': str(work_item.pk),
                }
                response['HX-Trigger'] = json.dumps({
                    'workItemCreated': {'workItemId': str(work_item.pk), 'ppaId': ppa_id},
                    'refreshPPAWorkItems': trigger_payload,
                    'showToast': {
                        'message': f'{work_item.get_work_type_display()} created successfully',
                        'level': 'success'
                    },
                    'closePPASidebar': True
                })
            elif is_work_items_tree:
                # Work items tree: trigger reload and close sidebar
                response['HX-Trigger'] = json.dumps({
                    'workItemCreated': {'workItemId': str(work_item.pk)},
                    'showToast': {
                        'message': f'{work_item.get_work_type_display()} created successfully',
                        'level': 'success'
                    }
                })
            elif is_moa_page:
                org_id = (
                    resolved_implementing_moa_id
                    or (str(related_ppa.implementing_moa_id) if related_ppa and related_ppa.implementing_moa_id else None)
                )
                response['HX-Trigger'] = json.dumps({
                    'workItemCreated': {
                        'workItemId': str(work_item.pk),
                        'context': 'moa',
                        'organizationId': org_id,
                    },
                    'refreshMoaWorkItems': {
                        'organizationId': org_id,
                        'workItemId': str(work_item.pk),
                        'reason': 'created',
                    },
                    'showToast': {
                        'message': f'{work_item.get_work_type_display()} created successfully',
                        'level': 'success'
                    },
                    'closeSidebar': True,
                })
            else:
                # Calendar: trigger calendar refresh and close panel
                response['HX-Trigger'] = json.dumps({
                    'calendarRefresh': {'eventId': str(work_item.pk)},
                    'showToast': {
                        'message': f'{work_item.get_work_type_display()} created successfully',
                        'level': 'success'
                    },
                    'closeDetailPanel': True
                })
            return response
        else:
            # Log form errors for debugging
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Work item creation failed. Errors: {form.errors.as_json()}")
            logger.error(f"POST data: {post_data}")

            # Return form with errors
            context = {
                'form': form,
                'is_create': True,
                'ppa_id': ppa_id,
                'ppa_info': related_ppa,
                'ppa_options': ppa_options,
                'selected_ppa_id': post_data.get('ppa_id') or ppa_id,
                'implementing_moa_id': resolved_implementing_moa_id,
                'has_disabled_ppa_options': has_disabled_ppa_options,
                'use_ppa_sidebar': use_ppa_sidebar,
                'sidebar_target_id': sidebar_target_id,
                'assignee_user': assignee_user,
                'assignee_id': assignee_id,
                'lock_implementing_moa': lock_implementing_moa,
                'implementing_moa_obj': implementing_moa_obj,
                'auto_assign_oobc': auto_assign_oobc,
                    'requires_related_ppa': requires_related_ppa_flag and not auto_assign_oobc,
                'close_action': close_action,
            }
            return render(request, create_template, context)

    else:  # GET
        from common.forms.work_items import WorkItemQuickEditForm
        from django.contrib.auth import get_user_model
        User = get_user_model()

        # Get pre-populated date from query params
        start_date = request.GET.get('start_date')
        due_date = request.GET.get('due_date', start_date)  # Default due_date = start_date
        parent_id = request.GET.get('parent')  # For "Add Child" action
        assignee_id = request.GET.get('assignee')  # For pre-filling assignee (from staff profile)

        initial = {}
        assignee_user = None

        # Handle assignee pre-fill (from staff profile)
        if assignee_id:
            try:
                assignee_user = User.objects.get(pk=assignee_id)
            except User.DoesNotExist:
                pass

        if start_date:
            initial['start_date'] = start_date
        if due_date:
            initial['due_date'] = due_date
        if parent_id:
            try:
                parent = WorkItem.objects.get(pk=parent_id)
                initial['parent'] = parent
                # Suggest default work_type based on parent
                if parent.work_type == WorkItem.WORK_TYPE_PROJECT:
                    initial['work_type'] = WorkItem.WORK_TYPE_ACTIVITY
                elif parent.work_type == WorkItem.WORK_TYPE_ACTIVITY:
                    initial['work_type'] = WorkItem.WORK_TYPE_TASK
                elif parent.work_type == WorkItem.WORK_TYPE_TASK:
                    initial['work_type'] = WorkItem.WORK_TYPE_SUBTASK
            except WorkItem.DoesNotExist:
                pass
        elif related_ppa and related_ppa.execution_project:
            # If creating from PPA and execution project exists, default to activity
            initial['parent'] = related_ppa.execution_project
            initial['work_type'] = WorkItem.WORK_TYPE_ACTIVITY

        if implementing_moa_obj:
            initial['implementing_moa'] = implementing_moa_obj

        if related_ppa:
            initial['related_ppa'] = related_ppa

        # Default values for new work items
        if 'status' not in initial:
            initial['status'] = 'not_started'
        if 'priority' not in initial:
            initial['priority'] = 'medium'
        if 'progress' not in initial:
            initial['progress'] = 0
        if 'work_type' not in initial:
            initial['work_type'] = 'task'  # Default to task

        form = WorkItemQuickEditForm(initial=initial, user=request.user)
        if auto_assign_oobc:
            form.fields['related_ppa'].queryset = oobc_ppa_queryset
            if oobc_org:
                form.fields['implementing_moa'].queryset = Organization.objects.filter(pk=oobc_org.pk)
        context = {
            'form': form,
            'is_create': True,
            'ppa_id': ppa_id,
            'ppa_info': related_ppa,
            'ppa_options': ppa_options,
            'selected_ppa_id': ppa_id,
            'implementing_moa_id': resolved_implementing_moa_id,
            'has_disabled_ppa_options': has_disabled_ppa_options,
            'assignee_user': assignee_user,  # Pass assignee info to template
            'assignee_id': assignee_id,  # Pass assignee ID for hidden field
            'use_ppa_sidebar': use_ppa_sidebar,
            'sidebar_target_id': sidebar_target_id,
            'lock_implementing_moa': lock_implementing_moa,
            'implementing_moa_obj': implementing_moa_obj,
            'auto_assign_oobc': auto_assign_oobc,
            'requires_related_ppa': requires_related_ppa_flag and not auto_assign_oobc,
            'close_action': close_action,
        }
        return render(request, create_template, context)


@login_required
@require_http_methods(["GET"])
def work_item_search_related(request, pk):
    """
    HTMX endpoint: Search for work items to add as related items.

    Returns filtered dropdown options based on search query.
    """
    work_item = get_object_or_404(WorkItem, pk=pk)
    search_query = request.GET.get('q', '').strip()

    # Get work items at same level and parent, excluding current or already related
    # IMPORTANT: Filter by ppa_category to enforce MOA/OOBC isolation
    work_items = WorkItem.objects.filter(
        work_type=work_item.work_type,
        parent_id=work_item.parent_id,
        ppa_category=work_item.ppa_category  # Same category (moa_ppa/oobc_ppa/obc_request)
    ).exclude(pk=work_item.pk).exclude(pk__in=work_item.related_items.values_list('pk', flat=True))

    # For MOA PPAs, also filter by implementing_moa to ensure MOA-specific isolation
    if work_item.ppa_category == 'moa_ppa' and work_item.implementing_moa:
        work_items = work_items.filter(implementing_moa=work_item.implementing_moa)

    # Apply search filter if query provided
    if search_query:
        work_items = work_items.filter(
            models.Q(title__icontains=search_query) |
            models.Q(work_type__icontains=search_query)
        )

    # Limit results and order by recent
    work_items = work_items.select_related('created_by').order_by('-created_at')[:50]

    # Return HTML options
    context = {
        'work_items': work_items,
        'search_query': search_query
    }
    return render(request, 'work_items/partials/_related_items_options.html', context)


@login_required
@require_POST
def work_item_add_related(request, pk):
    """
    HTMX endpoint: Add a related item to the work item.

    Returns updated related items list HTML for instant update.
    """
    import json

    work_item = get_object_or_404(WorkItem, pk=pk)

    # Check edit permissions
    permissions = get_work_item_permissions(request.user, work_item)
    if not permissions['can_edit']:
        return HttpResponse(
            status=403,
            headers={
                'HX-Trigger': json.dumps({
                    'showToast': {
                        'message': 'You do not have permission to modify this work item.',
                        'level': 'error'
                    }
                })
            }
        )

    related_item_id = request.POST.get('related_item_id')
    if not related_item_id:
        return HttpResponse(
            status=400,
            headers={
                'HX-Trigger': json.dumps({
                    'showToast': {
                        'message': 'Please select a work item to link.',
                        'level': 'error'
                    }
                })
            }
        )

    try:
        related_item = WorkItem.objects.get(pk=related_item_id)

        # Prevent linking to self
        if related_item == work_item:
            return HttpResponse(
                status=400,
                headers={
                    'HX-Trigger': json.dumps({
                        'showToast': {
                            'message': 'Cannot link a work item to itself.',
                            'level': 'error'
                        }
                })
            }
        )

        # Enforce same level (work type) and parent linkage rules
        if (
            related_item.work_type != work_item.work_type
            or related_item.parent_id != work_item.parent_id
        ):
            return HttpResponse(
                status=400,
                headers={
                    'HX-Trigger': json.dumps({
                        'showToast': {
                            'message': 'Related items must share the same level and parent.',
                            'level': 'error'
                        }
                    })
                }
            )

        # Add to related items (bidirectional)
        work_item.add_related_link(related_item)

        # Return updated related items list
        updated_work_item = (
            WorkItem.objects
            .prefetch_related('related_items')
            .get(pk=pk)
        )
        context = {
            'work_item': updated_work_item,
            'related_items': updated_work_item.related_items.order_by('title'),
        }
        response = render(request, 'work_items/partials/_related_items_list.html', context)
        response['HX-Trigger'] = json.dumps({
            'showToast': {
                'message': f'Linked to "{related_item.title}"',
                'level': 'success'
            }
        })
        return response

    except WorkItem.DoesNotExist:
        return HttpResponse(
            status=404,
            headers={
                'HX-Trigger': json.dumps({
                    'showToast': {
                        'message': 'Work item not found.',
                        'level': 'error'
                    }
                })
            }
        )


@login_required
@require_POST
def work_item_remove_related(request, pk, related_id):
    """
    HTMX endpoint: Remove a related item from the work item.

    Returns updated related items list HTML for instant update.
    """
    import json

    work_item = get_object_or_404(WorkItem, pk=pk)

    # Check edit permissions
    permissions = get_work_item_permissions(request.user, work_item)
    if not permissions['can_edit']:
        return HttpResponse(
            status=403,
            headers={
                'HX-Trigger': json.dumps({
                    'showToast': {
                        'message': 'You do not have permission to modify this work item.',
                        'level': 'error'
                    }
                })
            }
        )

    try:
        related_item = WorkItem.objects.get(pk=related_id)

        # Ensure the link exists before attempting to remove it
        if not work_item.related_items.filter(pk=related_id).exists():
            return HttpResponse(
                status=400,
                headers={
                    'HX-Trigger': json.dumps({
                        'showToast': {
                            'message': f'"{related_item.title}" is not linked to this work item.',
                            'level': 'error'
                        }
                    })
                }
            )

        # Remove from manually linked items only; do not impact hierarchy
        work_item.remove_related_link(related_item)

        # Refresh work_item from database to get updated related_items
        work_item = (
            WorkItem.objects
            .prefetch_related('related_items')
            .get(pk=pk)
        )

        # Return updated related items list
        context = {
            'work_item': work_item,
            'related_items': work_item.related_items.order_by('title'),
        }
        response = render(request, 'work_items/partials/_related_items_list.html', context)
        response['HX-Trigger'] = json.dumps({
            'showToast': {
                'message': f'Unlinked from "{related_item.title}"',
                'level': 'success'
            }
        })
        return response

    except WorkItem.DoesNotExist:
        return HttpResponse(
            status=404,
            headers={
                'HX-Trigger': json.dumps({
                    'showToast': {
                        'message': 'Related item not found.',
                        'level': 'error'
                    }
                })
            }
        )


@login_required
@require_POST
def work_item_quick_create_child(request, pk):
    """
    HTMX endpoint: Quickly create a child work item.

    Used by the "Add Child Item" quick creation form on the edit page.
    Returns updated children list HTML for instant update.
    """
    import json

    parent = get_object_or_404(WorkItem, pk=pk)

    # Check if user has permission to create work items
    if not request.user.is_staff and not request.user.has_perm('common.add_workitem'):
        return HttpResponse(
            status=403,
            headers={
                'HX-Trigger': json.dumps({
                    'showToast': {
                        'message': 'You do not have permission to create work items.',
                        'level': 'error'
                    }
                })
            }
        )

    # Get form data
    child_work_type = request.POST.get('child_work_type')
    child_title = request.POST.get('child_title', '').strip()
    child_status = request.POST.get('child_status', WorkItem.STATUS_NOT_STARTED)
    child_priority = request.POST.get('child_priority', WorkItem.PRIORITY_MEDIUM)
    child_start_date = request.POST.get('child_start_date')
    child_end_date = request.POST.get('child_end_date')

    # Validation
    if not child_work_type or child_work_type == 'Select type...':
        return HttpResponse(
            status=400,
            headers={
                'HX-Trigger': json.dumps({
                    'showToast': {
                        'message': 'Please select a work type for the child item.',
                        'level': 'error'
                    }
                })
            }
        )

    if not child_title:
        return HttpResponse(
            status=400,
            headers={
                'HX-Trigger': json.dumps({
                    'showToast': {
                        'message': 'Please enter a title for the child item.',
                        'level': 'error'
                    }
                })
            }
        )

    # Validate parent-child relationship
    if not parent.can_have_child_type(child_work_type):
        return HttpResponse(
            status=400,
            headers={
                'HX-Trigger': json.dumps({
                    'showToast': {
                        'message': f'{parent.get_work_type_display()} cannot have {dict(WorkItem.WORK_TYPE_CHOICES)[child_work_type]} as child.',
                        'level': 'error'
                    }
                })
            }
        )

    # Create the child work item with enhanced fields
    child = WorkItem(
        parent=parent,
        work_type=child_work_type,
        title=child_title,
        created_by=request.user,
        status=child_status,
        priority=child_priority,
        progress=0
    )

    # Add dates if provided
    if child_start_date:
        from datetime import datetime
        child.start_date = datetime.strptime(child_start_date, '%Y-%m-%d').date()
    if child_end_date:
        from datetime import datetime
        child.end_date = datetime.strptime(child_end_date, '%Y-%m-%d').date()

    try:
        child.full_clean()  # Validate model
        child.save()

        # Ensure new child is linked to its siblings for related items list
        child.sync_sibling_related_links()

        # Invalidate caches
        invalidate_calendar_cache(request.user.id)
        invalidate_work_item_tree_cache(child)

        # Return updated children list
        context = {'work_item': parent}
        response = render(request, 'work_items/partials/_children_items_list.html', context)
        response['HX-Trigger'] = json.dumps({
            'showToast': {
                'message': f'{child.get_work_type_display()} "{child.title}" created successfully',
                'level': 'success'
            },
            'childCreated': {'childId': str(child.id)}
        })
        return response

    except Exception as e:
        return HttpResponse(
            status=400,
            headers={
                'HX-Trigger': json.dumps({
                    'showToast': {
                        'message': f'Error creating child item: {str(e)}',
                        'level': 'error'
                    }
                })
            }
        )


@login_required
def work_item_search_users(request, pk):
    """
    HTMX endpoint: Search for users to assign to work item.

    Returns filtered dropdown options based on search query.
    """
    from common.models import User
    from django.db.models import Case, IntegerField, Value, When
    from common.constants import STAFF_DIRECTORY_PRIORITY

    work_item = get_object_or_404(WorkItem, pk=pk)
    search_query = request.GET.get('q', '').strip()

    # Get active users, excluding already assigned
    users = (
        User.objects.filter(is_active=True)
        .exclude(pk__in=work_item.assignees.values_list('pk', flat=True))
        .annotate(
            preferred_order=Case(
                *[
                    When(username=username, then=Value(idx))
                    for idx, username in enumerate(STAFF_DIRECTORY_PRIORITY)
                ],
                default=Value(len(STAFF_DIRECTORY_PRIORITY)),
                output_field=IntegerField(),
            ),
            user_type_order=Case(
                When(user_type="oobc_executive", then=Value(0)),
                When(user_type="oobc_staff", then=Value(1)),
                When(user_type="admin", then=Value(2)),
                default=Value(3),
                output_field=IntegerField(),
            ),
        )
    )

    # Apply search filter if query provided
    if search_query:
        users = users.filter(
            models.Q(first_name__icontains=search_query) |
            models.Q(last_name__icontains=search_query) |
            models.Q(username__icontains=search_query) |
            models.Q(position__icontains=search_query)
        )

    # Order and limit results
    users = users.order_by('preferred_order', 'user_type_order', 'last_name', 'first_name')[:50]

    # Return HTML options
    context = {
        'users': users,
        'search_query': search_query
    }
    return render(request, 'work_items/partials/_assignee_options.html', context)


@login_required
@require_POST
def work_item_add_assignee(request, pk):
    """
    HTMX endpoint: Add a user to work item assignees.

    Returns updated assignees list HTML for instant update.
    """
    import json
    from common.models import User

    work_item = get_object_or_404(WorkItem, pk=pk)

    # Check edit permissions
    permissions = get_work_item_permissions(request.user, work_item)
    if not permissions['can_edit']:
        return HttpResponse(
            status=403,
            headers={
                'HX-Trigger': json.dumps({
                    'showToast': {
                        'message': 'You do not have permission to modify this work item.',
                        'level': 'error'
                    }
                })
            }
        )

    user_id = request.POST.get('user_id')
    if not user_id:
        return HttpResponse(
            status=400,
            headers={
                'HX-Trigger': json.dumps({
                    'showToast': {
                        'message': 'Please select a user to assign.',
                        'level': 'error'
                    }
                })
            }
        )

    try:
        user = User.objects.get(pk=user_id)

        # Add to assignees
        work_item.assignees.add(user)

        # Return updated assignees list
        context = {'work_item': work_item}
        response = render(request, 'work_items/partials/_assigned_users_list.html', context)
        response['HX-Trigger'] = json.dumps({
            'showToast': {
                'message': f'Assigned to {user.get_full_name()}',
                'level': 'success'
            }
        })
        return response

    except User.DoesNotExist:
        return HttpResponse(
            status=404,
            headers={
                'HX-Trigger': json.dumps({
                    'showToast': {
                        'message': 'User not found.',
                        'level': 'error'
                    }
                })
            }
        )


@login_required
@require_POST
def work_item_remove_assignee(request, pk, user_id):
    """
    HTMX endpoint: Remove a user from work item assignees.

    Returns updated assignees list HTML for instant update.
    """
    import json
    from common.models import User

    work_item = get_object_or_404(WorkItem, pk=pk)

    # Check edit permissions
    permissions = get_work_item_permissions(request.user, work_item)
    if not permissions['can_edit']:
        return HttpResponse(
            status=403,
            headers={
                'HX-Trigger': json.dumps({
                    'showToast': {
                        'message': 'You do not have permission to modify this work item.',
                        'level': 'error'
                    }
                })
            }
        )

    try:
        user = User.objects.get(pk=user_id)
        work_item.assignees.remove(user)

        # Return updated assignees list
        context = {'work_item': work_item}
        response = render(request, 'work_items/partials/_assigned_users_list.html', context)
        response['HX-Trigger'] = json.dumps({
            'showToast': {
                'message': f'Removed {user.get_full_name()} from assignees',
                'level': 'success'
            }
        })
        return response

    except User.DoesNotExist:
        return HttpResponse(
            status=404,
            headers={
                'HX-Trigger': json.dumps({
                    'showToast': {
                        'message': 'User not found.',
                        'level': 'error'
                    }
                })
            }
        )


@login_required
def work_item_search_teams(request, pk):
    """
    HTMX endpoint: Search for teams to assign to work item.

    Returns filtered dropdown options based on search query.
    """
    from common.models import StaffTeam

    work_item = get_object_or_404(WorkItem, pk=pk)
    search_query = request.GET.get('q', '').strip()

    # Get active teams, excluding already assigned
    teams = (
        StaffTeam.objects.filter(is_active=True)
        .exclude(pk__in=work_item.teams.values_list('pk', flat=True))
        .order_by('name')
    )

    # Apply search filter if query provided
    if search_query:
        teams = teams.filter(
            models.Q(name__icontains=search_query) |
            models.Q(description__icontains=search_query)
        )

    # Limit results
    teams = teams[:50]

    # Return HTML options
    context = {
        'teams': teams,
        'search_query': search_query
    }
    return render(request, 'work_items/partials/_team_options.html', context)


@login_required
@require_POST
def work_item_add_team(request, pk):
    """
    HTMX endpoint: Add a team to work item teams.

    Returns updated teams list HTML for instant update.
    """
    import json
    from common.models import StaffTeam

    work_item = get_object_or_404(WorkItem, pk=pk)

    # Check edit permissions
    permissions = get_work_item_permissions(request.user, work_item)
    if not permissions['can_edit']:
        return HttpResponse(
            status=403,
            headers={
                'HX-Trigger': json.dumps({
                    'showToast': {
                        'message': 'You do not have permission to modify this work item.',
                        'level': 'error'
                    }
                })
            }
        )

    team_id = request.POST.get('team_id')
    if not team_id:
        return HttpResponse(
            status=400,
            headers={
                'HX-Trigger': json.dumps({
                    'showToast': {
                        'message': 'Please select a team to assign.',
                        'level': 'error'
                    }
                })
            }
        )

    try:
        team = StaffTeam.objects.get(pk=team_id)

        # Add to teams
        work_item.teams.add(team)

        # Return updated teams list
        context = {'work_item': work_item}
        response = render(request, 'work_items/partials/_assigned_teams_list.html', context)
        response['HX-Trigger'] = json.dumps({
            'showToast': {
                'message': f'Assigned to team "{team.name}"',
                'level': 'success'
            }
        })
        return response

    except StaffTeam.DoesNotExist:
        return HttpResponse(
            status=404,
            headers={
                'HX-Trigger': json.dumps({
                    'showToast': {
                        'message': 'Team not found.',
                        'level': 'error'
                    }
                })
            }
        )


@login_required
@require_POST
def work_item_remove_team(request, pk, team_id):
    """
    HTMX endpoint: Remove a team from work item teams.

    Returns updated teams list HTML for instant update.
    """
    import json
    from common.models import StaffTeam

    work_item = get_object_or_404(WorkItem, pk=pk)

    # Check edit permissions
    permissions = get_work_item_permissions(request.user, work_item)
    if not permissions['can_edit']:
        return HttpResponse(
            status=403,
            headers={
                'HX-Trigger': json.dumps({
                    'showToast': {
                        'message': 'You do not have permission to modify this work item.',
                        'level': 'error'
                    }
                })
            }
        )

    try:
        team = StaffTeam.objects.get(pk=team_id)
        work_item.teams.remove(team)

        # Return updated teams list
        context = {'work_item': work_item}
        response = render(request, 'work_items/partials/_assigned_teams_list.html', context)
        response['HX-Trigger'] = json.dumps({
            'showToast': {
                'message': f'Removed team "{team.name}" from assignment',
                'level': 'success'
            }
        })
        return response

    except StaffTeam.DoesNotExist:
        return HttpResponse(
            status=404,
            headers={
                'HX-Trigger': json.dumps({
                    'showToast': {
                        'message': 'Team not found.',
                        'level': 'error'
                    }
                })
            }
        )
