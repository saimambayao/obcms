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

            # Invalidate caches
            invalidate_calendar_cache(request.user.id)
            invalidate_work_item_tree_cache(work_item)  # Invalidate tree cache

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


@login_required
def work_item_sidebar_detail(request, pk):
    """
    HTMX endpoint: Return work item detail view for sidebar (calendar or work items tree).

    Used for displaying work item information in the sidebar detail panel.
    """
    work_item = get_object_or_404(WorkItem, pk=pk)

    # Get permissions for current user
    permissions = get_work_item_permissions(request.user, work_item)

    context = {
        'work_item': work_item,
        'can_edit': permissions['can_edit'],
        'can_delete': permissions['can_delete'],
    }

    # Use different template based on referrer (work items tree vs calendar)
    referer = request.META.get('HTTP_REFERER', '')
    if 'work-items' in referer:
        return render(request, 'work_items/partials/sidebar_detail.html', context)
    else:
        return render(request, 'common/partials/calendar_event_detail.html', context)


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

    # Determine which template to use based on referrer
    referer = request.META.get('HTTP_REFERER', '')
    is_work_items_tree = 'work-items' in referer
    detail_template = 'work_items/partials/sidebar_detail.html' if is_work_items_tree else 'common/partials/calendar_event_detail.html'
    edit_template = 'work_items/partials/sidebar_edit_form.html' if is_work_items_tree else 'common/partials/calendar_event_edit_form.html'

    # For GET requests: If user can't edit, gracefully show detail view instead
    if request.method == 'GET' and not permissions['can_edit']:
        # Fallback to read-only detail view
        context = {
            'work_item': work_item,
            'can_edit': permissions['can_edit'],
            'can_delete': permissions['can_delete'],
        }
        return render(request, detail_template, context)

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

            if is_work_items_tree:
                # Return updated edit form for sidebar + updated tree row for instant update
                from django.template.loader import render_to_string
                from common.forms.work_items import WorkItemQuickEditForm

                # Re-render the edit form with updated data (keep sidebar open)
                form = WorkItemQuickEditForm(instance=work_item, user=request.user)
                context = {'form': form, 'work_item': work_item}
                edit_form_html = render_to_string(edit_template, context, request=request)

                # Render the updated tree row for out-of-band swap
                # Template now has id="work-item-row-{{ work_item.id }}" for HTMX targeting
                row_html = render_to_string('work_items/_work_item_tree_row.html', {
                    'work_item': work_item
                }, request=request)

                # Extract ONLY the main <tr> (exclude placeholder and skeleton rows)
                import re
                # Match the main row: from opening <tr id="work-item-row-X"> to its closing </tr>
                # Use non-greedy match to get just the first <tr>...</tr>
                pattern = rf'(<tr\s+id="work-item-row-{work_item.id}"[^>]*>.*?</tr>)'
                match = re.search(pattern, row_html, re.DOTALL)

                if match:
                    # Successfully extracted just the main row
                    main_row_only = match.group(1)
                    row_html_with_oob = main_row_only.replace(
                        f'id="work-item-row-{work_item.id}"',
                        f'id="work-item-row-{work_item.id}" hx-swap-oob="true"',
                        1
                    )
                else:
                    # Fallback: add hx-swap-oob to entire template output
                    # This includes placeholder/skeleton rows, but HTMX will only swap the matching ID
                    row_html_with_oob = row_html.replace(
                        f'id="work-item-row-{work_item.id}"',
                        f'id="work-item-row-{work_item.id}" hx-swap-oob="true"',
                        1
                    )

                # Combine both: edit form stays in sidebar + row updates instantly
                from django.http import HttpResponse
                combined_html = edit_form_html + '\n' + row_html_with_oob

                response = HttpResponse(combined_html)
                response['HX-Trigger'] = json.dumps({
                    'showToast': {
                        'message': f'{work_item.get_work_type_display()} updated successfully',
                        'level': 'success'
                    }
                })
                return response
            else:
                # Calendar: Return updated detail view HTML
                context = {
                    'work_item': work_item,
                    'can_edit': permissions['can_edit'],
                    'can_delete': permissions['can_delete'],
                }
                response = render(request, detail_template, context)
                response['HX-Trigger'] = json.dumps({
                    'calendarRefresh': {'eventId': str(work_item.pk)},
                    'showToast': {
                        'message': f'{work_item.get_work_type_display()} updated successfully',
                        'level': 'success'
                    }
                })
                return response
        else:
            # Return form with errors
            context = {'form': form, 'work_item': work_item}
            return render(request, edit_template, context)

    else:  # GET
        from common.forms.work_items import WorkItemQuickEditForm

        form = WorkItemQuickEditForm(instance=work_item, user=request.user)
        context = {'form': form, 'work_item': work_item}
        return render(request, edit_template, context)


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
    context = {'form': form, 'work_item': duplicate}

    response = render(request, 'common/partials/calendar_event_edit_form.html', context)

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
    HTMX endpoint: Create work item from sidebar (calendar or work items tree).

    GET: Return create form HTML with pre-populated date from query params
    POST: Process form submission and return success response with refresh trigger

    This enables quick creation: double-click date → create form opens
    """
    # Determine which template to use based on referrer
    referer = request.META.get('HTTP_REFERER', '')
    is_work_items_tree = 'work-items' in referer
    create_template = 'work_items/partials/sidebar_create_form.html' if is_work_items_tree else 'common/partials/calendar_event_create_form.html'
    if request.method == 'POST':
        from common.forms.work_items import WorkItemQuickEditForm

        form = WorkItemQuickEditForm(request.POST, user=request.user)
        if form.is_valid():
            # Form handles created_by and assignee conversion
            work_item = form.save()

            # Invalidate caches
            invalidate_calendar_cache(request.user.id)
            invalidate_work_item_tree_cache(work_item)

            # Return success response with appropriate triggers
            import json
            response = HttpResponse(status=204)  # No Content

            if is_work_items_tree:
                # Work items tree: trigger reload and close sidebar
                response['HX-Trigger'] = json.dumps({
                    'workItemCreated': {'workItemId': str(work_item.pk)},
                    'showToast': {
                        'message': f'{work_item.get_work_type_display()} created successfully',
                        'level': 'success'
                    }
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
            logger.error(f"POST data: {request.POST}")

            # Return form with errors
            context = {'form': form, 'is_create': True}
            return render(request, create_template, context)

    else:  # GET
        from common.forms.work_items import WorkItemQuickEditForm

        # Get pre-populated date from query params
        start_date = request.GET.get('start_date')
        due_date = request.GET.get('due_date', start_date)  # Default due_date = start_date
        parent_id = request.GET.get('parent')  # For "Add Child" action

        initial = {}
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
        context = {'form': form, 'is_create': True}
        return render(request, create_template, context)
