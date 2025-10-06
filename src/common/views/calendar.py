"""
Unified Calendar Feed Views for WorkItem Hierarchy

This module provides calendar integration for the unified WorkItem model,
supporting hierarchical Projects → Activities → Tasks visualization.

See: docs/refactor/CALENDAR_INTEGRATION_PLAN.md
"""

import json
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.views.decorators.cache import never_cache
from django.core.cache import cache
from django.db import models
from common.models import WorkItem


@login_required
@never_cache
def work_items_calendar_feed(request):
    """
    Unified calendar feed for all work items (Projects, Activities, Tasks).

    Returns hierarchical work items with MPTT metadata for tree visualization.

    Query Parameters:
        - type: Filter by work_type (project, activity, task)
        - status: Filter by status
        - start: Start date (ISO format)
        - end: End date (ISO format)

    Response Format:
        {
            "workItems": [
                {
                    "id": "work-item-{uuid}",
                    "title": "Work item title",
                    "type": "Project|Activity|Task",
                    "start": "2025-10-01",
                    "end": "2025-12-31",
                    "color": "#1e40af",
                    "level": 0,
                    "parentId": "work-item-{parent-uuid}" or null,
                    "breadcrumb": "Project > Activity > Task",
                    "url": "/work-items/{uuid}/modal/",
                    "hasChildren": true,
                    "childCount": 5,
                    "status": "in_progress",
                    "priority": "high",
                    "extendedProps": {
                        "assignees": ["John Doe"],
                        "progress": 65
                    }
                }
            ],
            "hierarchy": {
                "maxLevel": 3,
                "totalProjects": 15,
                "totalActivities": 48,
                "totalTasks": 234
            }
        }
    """
    # Optional filters
    work_type = request.GET.get('type')  # project, activity, task
    status = request.GET.get('status')
    start_date_str = request.GET.get('start')
    end_date_str = request.GET.get('end')

    # Parse ISO 8601 datetime strings to dates (FullCalendar sends timezone-aware strings)
    from datetime import datetime
    start_date = None
    end_date = None

    if start_date_str:
        try:
            # Parse ISO 8601 format (e.g., "2025-09-28T00:00:00+08:00")
            start_date = datetime.fromisoformat(start_date_str).date()
        except (ValueError, AttributeError):
            # Fallback: try YYYY-MM-DD format
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            except ValueError:
                pass

    if end_date_str:
        try:
            # Parse ISO 8601 format
            end_date = datetime.fromisoformat(end_date_str).date()
        except (ValueError, AttributeError):
            # Fallback: try YYYY-MM-DD format
            try:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            except ValueError:
                pass

    # Cache key based on filters with versioning
    # Version invalidates ALL caches when any work item changes
    user_id = request.user.id
    cache_version = cache.get(f'calendar_version:{user_id}') or 0
    cache_key = f"calendar_feed:{user_id}:v{cache_version}:{work_type}:{status}:{start_date}:{end_date}"
    cached = cache.get(cache_key)
    if cached:
        return JsonResponse(cached, safe=False)

    # Base query with MPTT optimization
    queryset = WorkItem.objects.select_related('parent').prefetch_related('assignees')

    # Only show calendar-visible items
    queryset = queryset.filter(is_calendar_visible=True)

    # Date range filter
    if start_date and end_date:
        queryset = queryset.filter(
            models.Q(start_date__range=[start_date, end_date]) |
            models.Q(due_date__range=[start_date, end_date])
        )

    # Type filter
    if work_type:
        # Map simplified types to actual work_type values
        type_mapping = {
            'project': [WorkItem.WORK_TYPE_PROJECT, WorkItem.WORK_TYPE_SUB_PROJECT],
            'activity': [WorkItem.WORK_TYPE_ACTIVITY, WorkItem.WORK_TYPE_SUB_ACTIVITY],
            'task': [WorkItem.WORK_TYPE_TASK, WorkItem.WORK_TYPE_SUBTASK],
        }
        if work_type.lower() in type_mapping:
            queryset = queryset.filter(work_type__in=type_mapping[work_type.lower()])

    # Status filter
    if status:
        queryset = queryset.filter(status=status)

    # Serialize to calendar format
    work_items = []
    for item in queryset:
        # Build breadcrumb path
        breadcrumb = _build_breadcrumb(item)

        # Check if has children
        has_children = item.get_children().exists()
        child_count = item.get_children().count()

        work_items.append({
            'id': f'work-item-{item.pk}',
            'title': item.title,
            'type': item.get_work_type_display(),  # "Project", "Activity", "Task"
            'workType': item.work_type,  # Raw value for filtering
            'start': item.start_date.isoformat() if item.start_date else None,
            'end': item.due_date.isoformat() if item.due_date else None,
            'color': item.calendar_color,
            'level': item.level,  # MPTT tree level
            'parentId': f'work-item-{item.parent.pk}' if item.parent else None,
            'breadcrumb': breadcrumb,
            'url': f'/oobc-management/work-items/{item.pk}/modal/',
            'hasChildren': has_children,
            'childCount': child_count,
            'status': item.status,
            'statusDisplay': item.get_status_display(),
            'priority': item.priority,
            'priorityDisplay': item.get_priority_display(),
            'progress': item.progress,
            'extendedProps': {
                'assignees': [u.get_full_name() for u in item.assignees.all()],
                'teams': [t.name for t in item.teams.all()],
            }
        })

    # Build hierarchy metadata
    hierarchy = {
        'maxLevel': queryset.aggregate(models.Max('level'))['level__max'] or 0,
        'totalProjects': queryset.filter(
            work_type__in=[WorkItem.WORK_TYPE_PROJECT, WorkItem.WORK_TYPE_SUB_PROJECT]
        ).count(),
        'totalActivities': queryset.filter(
            work_type__in=[WorkItem.WORK_TYPE_ACTIVITY, WorkItem.WORK_TYPE_SUB_ACTIVITY]
        ).count(),
        'totalTasks': queryset.filter(
            work_type__in=[WorkItem.WORK_TYPE_TASK, WorkItem.WORK_TYPE_SUBTASK]
        ).count(),
    }

    # Cache for 5 minutes - cache the array directly
    cached_data = cache.get(cache_key)
    if cached_data is None:
        cache.set(cache_key, work_items, 300)

    # FullCalendar expects an array of events
    return JsonResponse(work_items, safe=False)


def _build_breadcrumb(work_item):
    """Build breadcrumb path for work item (Project > Activity > Task)."""
    ancestors = work_item.get_ancestors(include_self=True)
    breadcrumb_parts = [ancestor.title for ancestor in ancestors]
    return ' > '.join(breadcrumb_parts)


@login_required
def work_item_modal(request, work_item_id):
    """
    Render unified modal for WorkItem (Project, Activity, or Task).

    This replaces separate task_modal and event_modal views.

    Args:
        work_item_id: UUID of the WorkItem

    Returns:
        HTML modal content
    """
    work_item = get_object_or_404(WorkItem, pk=work_item_id)

    # Get children for hierarchy display
    children = work_item.get_children()

    # Get ancestors for breadcrumb
    ancestors = work_item.get_ancestors()

    # Generate URLs for actions
    from django.urls import reverse
    delete_url = reverse('common:work_item_delete', kwargs={'pk': work_item.pk})
    edit_url = reverse('common:work_item_edit', kwargs={'pk': work_item.pk})

    context = {
        'work_item': work_item,
        'children': children,
        'ancestors': ancestors,
        'breadcrumb': _build_breadcrumb(work_item),
        'delete_url': delete_url,
        'edit_url': edit_url,
    }

    return render(request, 'common/partials/work_item_modal.html', context)
