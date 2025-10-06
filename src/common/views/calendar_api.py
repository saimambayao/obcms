"""API views for calendar drag-and-drop and interactive features."""

import json
import logging
from datetime import datetime, time, timedelta

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from common.models import WorkItem
from coordination.models import StakeholderEngagement

logger = logging.getLogger(__name__)


def _strip_known_prefix(raw_id: str) -> str:
    """Remove calendar composite prefixes to recover underlying primary keys."""

    if not raw_id:
        return raw_id

    known_prefixes = (
        "coordination-event-",
        "coordination-activity-",
        "staff-task-",
        "staff-training-",
        "communities-event-",
        "staff-leave-",
    )

    for prefix in known_prefixes:
        if raw_id.startswith(prefix):
            return raw_id[len(prefix) :]

    return raw_id


@login_required
@require_http_methods(["POST"])
def calendar_event_update(request):
    """
    Update event date/time via drag-and-drop or resize.

    Expected POST data:
    {
        "id": "event-uuid",
        "type": "event",  # or "engagement"
        "start": "2025-10-15T09:00:00",
        "end": "2025-10-15T11:00:00",
        "allDay": false
    }
    """
    try:
        data = json.loads(request.body)
        event_id = data.get("id")
        event_type = data.get("type", "event")
        start_str = data.get("start")
        end_str = data.get("end")
        all_day = data.get("allDay", False)
        metadata = data.get("metadata") or {}

        if not event_id or not start_str:
            return JsonResponse(
                {"success": False, "error": "Missing required fields"}, status=400
            )

        # Parse datetime strings
        try:
            start_dt = datetime.fromisoformat(start_str.replace("Z", "+00:00"))
            if timezone.is_aware(start_dt):
                start_dt = timezone.localtime(start_dt)

            end_dt = None
            if end_str:
                end_dt = datetime.fromisoformat(end_str.replace("Z", "+00:00"))
                if timezone.is_aware(end_dt):
                    end_dt = timezone.localtime(end_dt)
        except (ValueError, AttributeError) as e:
            logger.error(f"Error parsing datetime: {e}")
            return JsonResponse(
                {"success": False, "error": "Invalid datetime format"}, status=400
            )

        # Update event based on type
        normalized_id = _strip_known_prefix(str(event_id))

        if event_type == "event":
            try:
                # Event is now WorkItem with work_type='activity' or 'sub_activity'
                activity = WorkItem.objects.get(
                    pk=normalized_id,
                    work_type__in=[WorkItem.WORK_TYPE_ACTIVITY, WorkItem.WORK_TYPE_SUB_ACTIVITY]
                )

                # Check permissions
                if not (
                    request.user.is_staff
                    or request.user.is_superuser
                    or activity.created_by == request.user
                    or request.user.has_perm("common.change_workitem")
                ):
                    return JsonResponse(
                        {"success": False, "error": "Permission denied"}, status=403
                    )

                # Update activity fields
                activity.start_date = start_dt.date()

                if all_day:
                    activity.start_time = None
                    activity.end_time = None
                    if end_dt:
                        # FullCalendar adds 1 day to end for all-day events
                        activity.due_date = (end_dt - timedelta(days=1)).date()
                    else:
                        activity.due_date = start_dt.date()
                else:
                    activity.start_time = start_dt.time()

                    if end_dt:
                        if end_dt.date() == start_dt.date():
                            activity.end_time = end_dt.time()
                            activity.due_date = None
                        else:
                            activity.due_date = end_dt.date()
                            activity.end_time = end_dt.time()

                        # Calculate duration and store in activity_data
                        duration = end_dt - start_dt
                        if not activity.activity_data:
                            activity.activity_data = {}
                        activity.activity_data['duration_hours'] = duration.total_seconds() / 3600

                activity.save(
                    update_fields=[
                        "start_date",
                        "start_time",
                        "due_date",
                        "end_time",
                        "activity_data",
                    ]
                )

                logger.info(
                    f"Activity {event_id} rescheduled by {request.user.username}: "
                    f"{start_dt} to {end_dt}"
                )

                return JsonResponse(
                    {
                        "success": True,
                        "message": f"Activity '{activity.title}' rescheduled successfully",
                    }
                )

            except WorkItem.DoesNotExist:
                return JsonResponse(
                    {"success": False, "error": "Activity not found"}, status=404
                )

        elif event_type == "engagement" or event_type == "activity":
            try:
                engagement = StakeholderEngagement.objects.get(pk=normalized_id)

                # Check permissions
                if not (
                    request.user.is_staff
                    or request.user.is_superuser
                    or engagement.created_by == request.user
                    or request.user.has_perm(
                        "coordination.change_stakeholderengagement"
                    )
                ):
                    return JsonResponse(
                        {"success": False, "error": "Permission denied"}, status=403
                    )

                # Update engagement schedule
                engagement.planned_date = start_dt
                fields_to_update = ["planned_date"]

                if end_dt:
                    duration = end_dt - start_dt
                    engagement.duration_minutes = int(
                        duration.total_seconds() / 60
                    )
                    fields_to_update.append("duration_minutes")
                elif engagement.duration_minutes is not None:
                    engagement.duration_minutes = None
                    fields_to_update.append("duration_minutes")

                engagement.save(update_fields=fields_to_update)

                logger.info(
                    f"Engagement {event_id} rescheduled by {request.user.username}: "
                    f"{start_dt} to {end_dt}"
                )

                return JsonResponse(
                    {
                        "success": True,
                        "message": f"Activity '{engagement.title}' rescheduled successfully",
                    }
                )

            except StakeholderEngagement.DoesNotExist:
                return JsonResponse(
                    {"success": False, "error": "Engagement not found"}, status=404
                )

        else:
            if event_type in {"staff_task", "task"}:
                try:
                    task = WorkItem.objects.select_related("created_by").get(
                        pk=_strip_known_prefix(str(event_id)),
                        work_type__in=[WorkItem.WORK_TYPE_TASK, WorkItem.WORK_TYPE_SUBTASK]
                    )
                except WorkItem.DoesNotExist:
                    return JsonResponse(
                        {"success": False, "error": "Task not found"}, status=404
                    )

                if not (
                    request.user.is_staff
                    or request.user.is_superuser
                    or task.created_by == request.user
                    or request.user.has_perm("common.change_workitem")
                ):
                    return JsonResponse(
                        {"success": False, "error": "Permission denied"},
                        status=403,
                    )

                updates = []
                original_start_date = task.start_date
                original_due_date = task.due_date

                new_start_date = start_dt.date() if start_dt else None
                new_due_date = None

                if end_dt:
                    new_due_date = end_dt.date()
                elif new_start_date:
                    new_due_date = new_start_date

                reference_date = original_start_date or original_due_date
                delta_days = 0
                if new_start_date and reference_date:
                    delta_days = (new_start_date - reference_date).days

                if new_start_date:
                    if original_start_date and delta_days:
                        task.start_date = original_start_date + timedelta(
                            days=delta_days
                        )
                    elif original_start_date and not delta_days:
                        task.start_date = new_start_date
                    elif metadata.get("hasStartDate") and not original_start_date:
                        task.start_date = new_start_date

                if new_due_date is not None:
                    if original_due_date and delta_days:
                        task.due_date = original_due_date + timedelta(days=delta_days)
                    elif original_due_date and not delta_days:
                        task.due_date = new_due_date
                    elif not original_due_date:
                        task.due_date = new_due_date
                elif metadata.get("hasDueDate") and original_due_date is not None:
                    task.due_date = None

                if task.start_date != original_start_date:
                    updates.append("start_date")
                if task.due_date != original_due_date:
                    updates.append("due_date")

                if not updates:
                    return JsonResponse(
                        {
                            "success": True,
                            "message": "Task already up to date",
                        }
                    )

                updates.append("updated_at")
                task.save(update_fields=updates)

                logger.info(
                    "Staff task %s rescheduled by %s: start=%s end=%s",
                    task.pk,
                    request.user.username,
                    new_start_date,
                    new_due_date,
                )

                return JsonResponse(
                    {
                        "success": True,
                        "message": f"Task '{task.title}' rescheduled successfully",
                    }
                )

            return JsonResponse(
                {"success": False, "error": "Invalid event type"}, status=400
            )

    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Invalid JSON"}, status=400)
    except Exception as e:
        logger.error(f"Error updating calendar event: {e}", exc_info=True)
        return JsonResponse({"success": False, "error": "Server error"}, status=500)
