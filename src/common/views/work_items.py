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
from django.db.models import Q, Count
from django.views.decorators.http import require_POST, require_http_methods
from django.core.exceptions import PermissionDenied

from common.work_item_model import WorkItem
from common.forms.work_items import WorkItemForm


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
    """
    # Get filter parameters
    work_type_filter = request.GET.get('work_type', '')
    status_filter = request.GET.get('status', '')
    priority_filter = request.GET.get('priority', '')
    search_query = request.GET.get('q', '')

    # Base queryset - root level items first
    queryset = WorkItem.objects.all()

    # Apply filters
    if work_type_filter:
        queryset = queryset.filter(work_type=work_type_filter)
    if status_filter:
        queryset = queryset.filter(status=status_filter)
    if priority_filter:
        queryset = queryset.filter(priority=priority_filter)
    if search_query:
        queryset = queryset.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    # Annotate with children count
    queryset = queryset.annotate(
        children_count=Count('children')
    )

    # Order by tree structure
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
    """
    work_item = get_object_or_404(WorkItem, pk=pk)

    # Get breadcrumb (ancestors)
    breadcrumb = work_item.get_ancestors(include_self=True)

    # Get direct children
    children = work_item.get_children().annotate(
        children_count=Count('children')
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

    context = {
        'work_item': work_item,
        'breadcrumb': breadcrumb,
        'children': children,
        'type_specific_data': type_specific_data,
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

    if request.method == 'POST':
        form = WorkItemForm(request.POST)
        form.user = request.user  # For created_by field

        if form.is_valid():
            work_item = form.save(commit=False)
            work_item.created_by = request.user
            work_item.save()
            form.save_m2m()  # Save many-to-many fields

            # Invalidate calendar cache
            invalidate_calendar_cache(request.user.id)

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
    }

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
    work_item = get_object_or_404(WorkItem, pk=pk)

    # Check edit permissions
    permissions = get_work_item_permissions(request.user, work_item)
    if not permissions['can_edit']:
        messages.error(request, 'You do not have permission to edit this work item.')
        raise PermissionDenied('You do not have permission to edit this work item.')

    if request.method == 'POST':
        form = WorkItemForm(request.POST, instance=work_item)

        if form.is_valid():
            work_item = form.save()

            # Update progress of parent if auto_calculate is enabled
            if work_item.parent and work_item.parent.auto_calculate_progress:
                work_item.parent.update_progress()

            # Invalidate calendar cache
            invalidate_calendar_cache(request.user.id)

            messages.success(
                request,
                f'{work_item.get_work_type_display()} "{work_item.title}" updated successfully.'
            )
            return redirect('common:work_item_detail', pk=work_item.pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = WorkItemForm(instance=work_item)

    # Build breadcrumb from work item ancestors
    breadcrumb = list(work_item.get_ancestors(include_self=True))

    context = {
        'form': form,
        'action': 'Edit',
        'work_item': work_item,
        'breadcrumb': breadcrumb,
    }

    return render(request, 'work_items/work_item_form.html', context)


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

    # Handle HTMX DELETE request (from calendar modal)
    if request.method == 'DELETE':
        import json

        work_title = work_item.title
        work_type_display = work_item.get_work_type_display()
        work_item_id = str(work_item.id)

        # Cascade delete (MPTT handles this automatically)
        work_item.delete()

        # CRITICAL: Invalidate calendar cache to prevent stale data
        invalidate_calendar_cache(request.user.id)

        # Return empty response with HX-Trigger to update calendar
        return HttpResponse(
            status=200,
            headers={
                'HX-Trigger': json.dumps({
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
                })
            }
        )

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

            # Delete the work item
            work_item.delete()

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
    """
    work_item = get_object_or_404(WorkItem, pk=pk)
    children = work_item.get_children().annotate(
        children_count=Count('children')
    )

    context = {
        'work_items': children,
        'parent_level': work_item.level + 1,
    }

    return render(request, 'work_items/_work_item_tree_nodes.html', context)


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
    """
    # Get date range from query params
    start = request.GET.get('start')
    end = request.GET.get('end')

    # Filter work items
    queryset = WorkItem.objects.filter(is_calendar_visible=True)

    if start:
        queryset = queryset.filter(due_date__gte=start)
    if end:
        queryset = queryset.filter(start_date__lte=end)

    # Convert to FullCalendar events
    events = [work_item.get_calendar_event() for work_item in queryset]

    return JsonResponse(events, safe=False)
