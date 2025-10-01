"""Shared calendar aggregation utilities for OOBC modules."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, time, timedelta
from typing import Dict, List, Optional, Sequence, Tuple

from django.utils import timezone

from common.constants import CALENDAR_MODULE_ORDER
from common.models import StaffTask, TrainingEnrollment
from coordination.models import (
    Communication,
    Event,
    Partnership,
    PartnershipMilestone,
    StakeholderEngagement,
)
from mana.models import BaselineDataCollection
from monitoring.models import MonitoringEntry, MonitoringEntryWorkflowStage
from recommendations.policy_tracking.models import PolicyRecommendation


@dataclass
class CalendarStats:
    """Stores totals per module for dashboard presentation."""

    total: int = 0
    upcoming: int = 0
    completed: int = 0


def _combine(date_part, time_part=None, default_time=time.min):
    """Return combined naive datetime or None if date missing."""

    if not date_part:
        return None
    selected_time = time_part if time_part is not None else default_time
    return datetime.combine(date_part, selected_time)


def _ensure_aware(dt_value: Optional[datetime]) -> Optional[datetime]:
    """Convert naive datetimes to timezone-aware counterparts."""

    if not dt_value:
        return None
    if timezone.is_naive(dt_value):
        return timezone.make_aware(dt_value, timezone.get_current_timezone())
    return timezone.localtime(dt_value)


def _isoformat(dt_value: Optional[datetime]) -> Optional[str]:
    """Return ISO formatted datetime string handling TZ awareness."""

    if not dt_value:
        return None
    if timezone.is_naive(dt_value):
        aware_value = timezone.make_aware(dt_value, timezone.get_current_timezone())
    else:
        aware_value = timezone.localtime(dt_value)
    return aware_value.isoformat()


def _increment(stats: Dict[str, CalendarStats], module: str, *, upcoming: bool,
               completed: bool) -> None:
    """Increment module stats counters."""

    record = stats.setdefault(module, CalendarStats())
    record.total += 1
    if upcoming:
        record.upcoming += 1
    if completed:
        record.completed += 1


def build_calendar_payload(
    *, filter_modules: Optional[Sequence[str]] = None,
) -> Dict[str, object]:
    """Gather calendar entries across OOBC modules.

    Args:
        filter_modules: optional iterable restricting modules to include.

    Returns:
        Dict containing entries, module statistics, upcoming highlights, and
        conflict hints suitable for rendering calendar dashboards.
    """

    requested_modules = (
        list(filter_modules)
        if filter_modules is not None
        else None
    )
    allowed_modules_set = set(requested_modules or []) or None

    now = timezone.now()
    due_soon_cutoff = now + timedelta(days=2)

    entries: List[Dict] = []
    stats: Dict[str, CalendarStats] = {}
    upcoming_items: List[Tuple[datetime, Dict]] = []
    timed_entries: List[Dict] = []
    follow_up_items: List[Dict] = []
    workflow_actions_global: List[Dict] = []

    status_counts: Dict[str, Dict[str, int]] = {}
    module_set: set[str] = set()
    heatmap_days = [now.date() + timedelta(days=index) for index in range(7)]
    heatmap_counts: Dict[str, List[int]] = {}
    workflow_summary = {
        "follow_up": 0,
        "approval": 0,
        "escalation": 0,
        "workflow": 0,
    }

    if requested_modules:
        module_seed = [
            module for module in requested_modules if module in CALENDAR_MODULE_ORDER
        ]
        module_seed += [
            module for module in requested_modules if module not in module_seed
        ]
    else:
        module_seed = list(CALENDAR_MODULE_ORDER)

    def include_module(module_name: str) -> bool:
        return allowed_modules_set is None or module_name in allowed_modules_set

    def severity_for_due(due_datetime: Optional[datetime]) -> str:
        if not due_datetime:
            return "info"
        if due_datetime < now:
            return "critical"
        if due_datetime <= due_soon_cutoff:
            return "warning"
        return "info"

    def append_workflow_action(
        entry_actions: List[Dict],
        module: str,
        entry_id: str,
        action_type: str,
        label: str,
        *,
        due: Optional[datetime] = None,
        status: Optional[str] = None,
        notes: str = "",
        severity: Optional[str] = None,
    ) -> Dict[str, object]:
        action = {
            "module": module,
            "entry_id": entry_id,
            "type": action_type,
            "label": label,
            "due": due,
            "status": status,
            "notes": notes,
            "severity": severity or severity_for_due(due),
            "overdue": bool(due and due < now),
        }
        entry_actions.append(action)
        workflow_actions_global.append(action)
        workflow_summary[action_type] = workflow_summary.get(action_type, 0) + 1
        if action_type == "follow_up":
            follow_up_items.append(action)
        return action

    # Coordination Events ---------------------------------------------------
    if include_module("coordination"):
        events = Event.objects.select_related("community", "organizer")

        for event in events:
            start_dt = _combine(event.start_date, event.start_time)
            all_day = event.start_time is None

            if event.end_date:
                end_time = (
                    event.end_time
                    if event.end_time
                    else (time.max if not all_day else time.max)
                )
                end_dt = _combine(event.end_date, end_time)
                if all_day and end_dt:
                    end_dt = end_dt + timedelta(days=1)
            elif event.end_time:
                end_dt = _combine(event.start_date, event.end_time)
            elif event.duration_hours and start_dt:
                end_dt = start_dt + timedelta(hours=float(event.duration_hours))
            elif all_day and start_dt:
                end_dt = start_dt + timedelta(days=1)
            else:
                end_dt = start_dt

            aware_start = _ensure_aware(start_dt)
            upcoming_flag = bool(aware_start and aware_start >= now)
            completed_flag = event.status == "completed"

            payload = {
                "id": f"coordination-event-{event.pk}",
                "title": event.title,
                "start": _isoformat(start_dt),
                "end": _isoformat(end_dt),
                "allDay": all_day,
                "backgroundColor": "#2563eb",
                "borderColor": "#1d4ed8",
                "textColor": "#ffffff" if all_day else None,
                "extendedProps": {
                    "module": "coordination",
                    "category": "event",
                    "status": event.status,
                    "community": getattr(event.community, "name", ""),
                    "organizer": getattr(event.organizer, "get_full_name", None)
                    and event.organizer.get_full_name()
                    or getattr(event.organizer, "username", ""),
                    "location": event.venue,
                },
            }

            entries.append(payload)
            workflow_actions_entry: List[Dict] = []
            payload["extendedProps"]["workflowActions"] = workflow_actions_entry

            module_name = payload["extendedProps"].get("module", "coordination")
            module_set.add(module_name)

            status_value = payload["extendedProps"].get("status") or "unspecified"
            status_counts.setdefault(module_name, {})
            status_counts[module_name][status_value] = (
                status_counts[module_name].get(status_value, 0) + 1
            )

            if start_dt:
                display_start = _ensure_aware(start_dt)
                display_end = _ensure_aware(end_dt) if end_dt else None
                upcoming_items.append((display_start, {
                    "module": module_name,
                    "title": event.title,
                    "start": display_start,
                    "status": event.status,
                }))
                timed_entries.append({
                    "module": module_name,
                    "title": event.title,
                    "start": display_start,
                    "end": display_end or display_start,
                    "location": event.venue,
                })

                if display_start.date() in heatmap_days:
                    idx = heatmap_days.index(display_start.date())
                    heatmap_counts.setdefault(module_name, [0] * len(heatmap_days))
                    heatmap_counts[module_name][idx] += 1

            _increment(stats, "coordination", upcoming=upcoming_flag, completed=completed_flag)

            if aware_start:
                severity = None
                label = None
                action_type = None

                if event.status in {"draft", "planned"}:
                    label = "Event approval"
                    action_type = "approval"
                    if aware_start < now:
                        severity = "critical"
                        action_type = "escalation"
                elif event.status == "scheduled":
                    label = "Event readiness"
                    action_type = "workflow"
                    if aware_start < now:
                        severity = "critical"
                        action_type = "escalation"

                if action_type:
                    append_workflow_action(
                        workflow_actions_entry,
                        module_name,
                        payload["id"],
                        action_type=action_type,
                        label=label,
                        due=aware_start,
                        status=event.status,
                        notes=event.agenda[:280] if event.agenda else event.objectives[:280],
                        severity=severity,
                    )

            if event.follow_up_required and event.follow_up_date:
                follow_dt = _ensure_aware(_combine(event.follow_up_date))
                if follow_dt:
                    append_workflow_action(
                        workflow_actions_entry,
                        module_name,
                        payload["id"],
                        action_type="follow_up",
                        label="Event follow-up",
                        due=follow_dt,
                        status=event.status,
                        notes=event.follow_up_notes or "",
                    )

    # Coordination Stakeholder Engagements ---------------------------------
    if include_module("coordination"):
        engagements = StakeholderEngagement.objects.select_related(
            "community", "engagement_type"
        )

        for engagement in engagements:
            start_dt = engagement.planned_date
            end_dt = None
            if engagement.duration_minutes and start_dt:
                end_dt = start_dt + timedelta(minutes=engagement.duration_minutes)

            aware_start = _ensure_aware(start_dt)
            upcoming_flag = bool(aware_start and aware_start >= now)
            completed_flag = engagement.status == "completed"

            payload = {
                "id": f"coordination-activity-{engagement.pk}",
                "title": engagement.title,
                "start": _isoformat(start_dt),
                "end": _isoformat(end_dt),
                "allDay": False,
                "backgroundColor": "#059669",
                "borderColor": "#047857",
                "extendedProps": {
                    "module": "coordination",
                    "category": "stakeholder_engagement",
                    "status": engagement.status,
                    "community": getattr(engagement.community, "name", ""),
                    "engagementType": getattr(
                        engagement.engagement_type, "name", ""
                    ),
                    "location": engagement.venue,
                },
            }

            entries.append(payload)
            workflow_actions_entry: List[Dict] = []
            payload["extendedProps"]["workflowActions"] = workflow_actions_entry

            module_name = payload["extendedProps"].get("module", "coordination")
            module_set.add(module_name)

            status_value = payload["extendedProps"].get("status") or "unspecified"
            status_counts.setdefault(module_name, {})
            status_counts[module_name][status_value] = (
                status_counts[module_name].get(status_value, 0) + 1
            )

            if start_dt:
                display_start = _ensure_aware(start_dt)
                display_end = _ensure_aware(end_dt) if end_dt else None
                upcoming_items.append((display_start, {
                    "module": module_name,
                    "title": engagement.title,
                    "start": display_start,
                    "status": engagement.status,
                }))
                timed_entries.append({
                    "module": module_name,
                    "title": engagement.title,
                    "start": display_start,
                    "end": display_end or display_start,
                    "location": engagement.venue,
                })

                if display_start.date() in heatmap_days:
                    idx = heatmap_days.index(display_start.date())
                    heatmap_counts.setdefault(module_name, [0] * len(heatmap_days))
                    heatmap_counts[module_name][idx] += 1

            _increment(stats, "coordination", upcoming=upcoming_flag, completed=completed_flag)

    # Coordination Communications Follow-ups --------------------------------
    if include_module("coordination"):
        communications = Communication.objects.select_related("organization").filter(
            requires_follow_up=True
        )

        for communication in communications:
            due_source = communication.follow_up_date or communication.due_date
            if not due_source:
                continue

            start_dt = _combine(due_source)
            aware_start = _ensure_aware(start_dt)
            upcoming_flag = bool(aware_start and aware_start >= now)
            completed_flag = bool(communication.follow_up_completed)

            payload = {
                "id": f"coordination-communication-{communication.pk}",
                "title": communication.subject,
                "start": _isoformat(start_dt),
                "end": _isoformat(start_dt + timedelta(days=1)) if start_dt else None,
                "allDay": True,
                "backgroundColor": "#f97316",
                "borderColor": "#ea580c",
                "textColor": "#1f2937",
                "extendedProps": {
                    "module": "coordination",
                    "category": "communication_follow_up",
                    "status": "completed" if communication.follow_up_completed else "pending",
                    "organization": getattr(communication.organization, "name", ""),
                    "location": None,
                },
            }

            entries.append(payload)
            workflow_actions_entry: List[Dict] = []
            payload["extendedProps"]["workflowActions"] = workflow_actions_entry

            module_name = payload["extendedProps"].get("module", "coordination")
            module_set.add(module_name)

            status_value = payload["extendedProps"].get("status") or "unspecified"
            status_counts.setdefault(module_name, {})
            status_counts[module_name][status_value] = (
                status_counts[module_name].get(status_value, 0) + 1
            )

            upcoming_items.append((aware_start, {
                "module": module_name,
                "title": communication.subject,
                "start": aware_start,
                "status": status_value,
            }))
            timed_entries.append({
                "module": module_name,
                "title": communication.subject,
                "start": aware_start,
                "end": aware_start + timedelta(hours=1),
                "location": None,
            })

            if aware_start.date() in heatmap_days:
                idx = heatmap_days.index(aware_start.date())
                heatmap_counts.setdefault(module_name, [0] * len(heatmap_days))
                heatmap_counts[module_name][idx] += 1

            _increment(stats, "coordination", upcoming=upcoming_flag, completed=completed_flag)

            append_workflow_action(
                workflow_actions_entry,
                module_name,
                payload["id"],
                action_type="follow_up",
                label="Communication follow-up",
                due=aware_start,
                status="Completed" if communication.follow_up_completed else "Pending",
                notes=communication.follow_up_notes or communication.content[:280],
            )

    # Coordination Partnerships -------------------------------------------
    if include_module("coordination"):
        partnerships = Partnership.objects.select_related(
            "lead_organization", "focal_person"
        )

        for partnership in partnerships:
            timeline = [
                (
                    "partnership_concept",
                    partnership.concept_date,
                    "Concept Finalised",
                    "#a855f7",
                    "#9333ea",
                ),
                (
                    "partnership_negotiation",
                    partnership.negotiation_start_date,
                    "Negotiations Start",
                    "#a855f7",
                    "#7c3aed",
                ),
                (
                    "partnership_signing",
                    partnership.signing_date,
                    "Signing Deadline",
                    "#7c3aed",
                    "#6d28d9",
                ),
                (
                    "partnership_start",
                    partnership.start_date,
                    "Implementation Start",
                    "#4c1d95",
                    "#4338ca",
                ),
                (
                    "partnership_end",
                    partnership.end_date,
                    "End of Term",
                    "#581c87",
                    "#4c1d95",
                ),
                (
                    "partnership_renewal",
                    partnership.renewal_date,
                    "Renewal Review",
                    "#5b21b6",
                    "#4c1d95",
                ),
            ]

            partnership_complete = partnership.status in {
                "completed",
                "terminated",
                "expired",
            }

            for category, date_value, label, bg_color, border_color in timeline:
                if not date_value:
                    continue

                start_dt = _combine(date_value)
                aware_start = _ensure_aware(start_dt)
                upcoming_flag = bool(aware_start and aware_start >= now)

                payload = {
                    "id": f"coordination-partnership-{partnership.pk}-{category}",
                    "title": f"{partnership.title} – {label}",
                    "start": _isoformat(start_dt),
                    "end": _isoformat(start_dt + timedelta(days=1)) if start_dt else None,
                    "allDay": True,
                    "backgroundColor": bg_color,
                    "borderColor": border_color,
                    "textColor": "#f8fafc",
                    "extendedProps": {
                        "module": "coordination",
                        "category": category,
                        "status": partnership.status,
                        "priority": partnership.priority,
                        "leadOrganization": getattr(
                            partnership.lead_organization, "name", ""
                        ),
                        "focalPerson": getattr(
                            partnership.focal_person, "get_full_name", None
                        )
                        and partnership.focal_person.get_full_name()
                        or getattr(partnership.focal_person, "username", ""),
                        "location": None,
                    },
                }

                entries.append(payload)
                workflow_actions_entry: List[Dict] = []
                payload["extendedProps"]["workflowActions"] = workflow_actions_entry

                module_name = payload["extendedProps"].get("module", "coordination")
                module_set.add(module_name)

                status_value = payload["extendedProps"].get("status") or "unspecified"
                status_counts.setdefault(module_name, {})
                status_counts[module_name][status_value] = (
                    status_counts[module_name].get(status_value, 0) + 1
                )

                if start_dt:
                    display_start = aware_start
                    display_end = _ensure_aware(
                        start_dt + timedelta(days=1)
                    ) if start_dt else None
                    upcoming_items.append((display_start, {
                        "module": module_name,
                        "title": payload["title"],
                        "start": display_start,
                        "status": status_value,
                    }))
                    timed_entries.append({
                        "module": module_name,
                        "title": payload["title"],
                        "start": display_start,
                        "end": display_end or display_start,
                        "location": None,
                    })

                    if display_start.date() in heatmap_days:
                        idx = heatmap_days.index(display_start.date())
                        heatmap_counts.setdefault(
                            module_name, [0] * len(heatmap_days)
                        )
                        heatmap_counts[module_name][idx] += 1

                _increment(
                    stats,
                    "coordination",
                    upcoming=upcoming_flag,
                    completed=partnership_complete,
                )

                due = aware_start
                if category == "partnership_signing" and partnership.status in {
                    "pending_approval",
                    "pending_signature",
                }:
                    severity = "critical" if due and due < now else None
                    action_type = "approval"
                    if severity == "critical":
                        action_type = "escalation"
                    append_workflow_action(
                        workflow_actions_entry,
                        module_name,
                        payload["id"],
                        action_type=action_type,
                        label="Partnership approval",
                        due=due,
                        status=partnership.status,
                        notes=partnership.description[:280],
                        severity=severity,
                    )
                elif category == "partnership_start" and partnership.status in {
                    "pending_signature",
                    "negotiation",
                    "active",
                }:
                    severity = "critical" if due and due < now else None
                    action_type = "workflow"
                    if severity == "critical" and partnership.status != "active":
                        action_type = "escalation"
                    append_workflow_action(
                        workflow_actions_entry,
                        module_name,
                        payload["id"],
                        action_type=action_type,
                        label="Implementation readiness",
                        due=due,
                        status=partnership.status,
                        notes=partnership.objectives[:280],
                        severity=severity,
                    )
                elif category == "partnership_end" and not partnership_complete:
                    append_workflow_action(
                        workflow_actions_entry,
                        module_name,
                        payload["id"],
                        action_type="follow_up",
                        label="Close-out planning",
                        due=due,
                        status=partnership.status,
                        notes=partnership.expected_outcomes[:280],
                    )
                elif (
                    category == "partnership_renewal"
                    and partnership.is_renewable
                    and not partnership_complete
                ):
                    append_workflow_action(
                        workflow_actions_entry,
                        module_name,
                        payload["id"],
                        action_type="follow_up",
                        label="Renewal preparation",
                        due=due,
                        status=partnership.status,
                        notes=partnership.renewal_criteria[:280],
                    )

    # Partnership Milestones -----------------------------------------------
    if include_module("coordination"):
        milestones = PartnershipMilestone.objects.select_related("partnership")

        for milestone in milestones:
            if not milestone.due_date:
                continue

            start_dt = _combine(milestone.due_date)
            aware_start = _ensure_aware(start_dt)
            upcoming_flag = bool(aware_start and aware_start >= now)
            completed_flag = milestone.status == "completed"

            payload = {
                "id": f"coordination-milestone-{milestone.pk}",
                "title": f"{milestone.partnership.title} – {milestone.title}",
                "start": _isoformat(start_dt),
                "end": _isoformat(start_dt + timedelta(days=1)),
                "allDay": True,
                "backgroundColor": "#f472b6",
                "borderColor": "#db2777",
                "textColor": "#1f2937",
                "extendedProps": {
                    "module": "coordination",
                    "category": "partnership_milestone",
                    "status": milestone.status,
                    "milestoneType": milestone.milestone_type,
                    "location": None,
                },
            }

            entries.append(payload)
            workflow_actions_entry: List[Dict] = []
            payload["extendedProps"]["workflowActions"] = workflow_actions_entry

            module_name = payload["extendedProps"].get("module", "coordination")
            module_set.add(module_name)

            status_value = payload["extendedProps"].get("status") or "unspecified"
            status_counts.setdefault(module_name, {})
            status_counts[module_name][status_value] = (
                status_counts[module_name].get(status_value, 0) + 1
            )

            display_start = aware_start
            upcoming_items.append((display_start, {
                "module": module_name,
                "title": payload["title"],
                "start": display_start,
                "status": milestone.status,
            }))
            timed_entries.append({
                "module": module_name,
                "title": payload["title"],
                "start": display_start,
                "end": display_start + timedelta(hours=1),
                "location": None,
            })

            if display_start.date() in heatmap_days:
                idx = heatmap_days.index(display_start.date())
                heatmap_counts.setdefault(module_name, [0] * len(heatmap_days))
                heatmap_counts[module_name][idx] += 1

            _increment(
                stats,
                "coordination",
                upcoming=upcoming_flag,
                completed=completed_flag,
            )

            if milestone.status not in {"completed", "cancelled"}:
                due = aware_start
                severity = None
                action_type = "workflow"

                if milestone.milestone_type == "approval":
                    action_type = "approval"
                elif milestone.milestone_type in {"report", "deliverable"}:
                    action_type = "follow_up"

                if (
                    milestone.status in {"delayed", "overdue"}
                    or (due and due < now)
                ):
                    severity = "critical"
                    if action_type == "workflow":
                        action_type = "escalation"

                append_workflow_action(
                    workflow_actions_entry,
                    module_name,
                    payload["id"],
                    action_type=action_type,
                    label=f"{milestone.get_milestone_type_display()} milestone",
                    due=due,
                    status=milestone.status,
                    notes=milestone.description[:280],
                    severity=severity,
                )

    # MANA Baseline Data Collection ----------------------------------------
    if include_module("mana"):
        baseline_qs = BaselineDataCollection.objects.select_related(
            "study", "supervisor"
        )

        for baseline in baseline_qs:
            start_dt = _combine(baseline.planned_date)
            end_dt = (
                start_dt + timedelta(hours=baseline.duration_hours)
                if start_dt and baseline.duration_hours
                else start_dt
            )

            aware_start = _ensure_aware(start_dt)
            upcoming_flag = bool(aware_start and aware_start >= now)
            completed_flag = baseline.status in {"completed", "validated"}

            payload = {
                "id": f"mana-baseline-{baseline.pk}",
                "title": f"{baseline.get_collection_method_display()} - {baseline.study.title}",
                "start": _isoformat(start_dt),
                "end": _isoformat(end_dt),
                "allDay": True,
                "backgroundColor": "#d97706",
                "borderColor": "#b45309",
                "textColor": "#1f2937",
                "extendedProps": {
                    "module": "mana",
                    "category": "baseline_collection",
                    "status": baseline.status,
                    "study": baseline.study.title,
                    "location": baseline.location,
                    "supervisor": getattr(baseline.supervisor, "get_full_name", None)
                    and baseline.supervisor.get_full_name()
                    or getattr(baseline.supervisor, "username", ""),
                },
            }

            entries.append(payload)
            workflow_actions_entry: List[Dict] = []
            payload["extendedProps"]["workflowActions"] = workflow_actions_entry

            module_name = payload["extendedProps"].get("module", "mana")
            module_set.add(module_name)

            status_value = payload["extendedProps"].get("status") or "unspecified"
            status_counts.setdefault(module_name, {})
            status_counts[module_name][status_value] = (
                status_counts[module_name].get(status_value, 0) + 1
            )

            if start_dt:
                display_start = _ensure_aware(start_dt)
                display_end = _ensure_aware(end_dt) if end_dt else None
                upcoming_items.append((display_start, {
                    "module": module_name,
                    "title": payload["title"],
                    "start": display_start,
                    "status": baseline.status,
                }))
                timed_entries.append({
                    "module": module_name,
                    "title": payload["title"],
                    "start": display_start,
                    "end": display_end or display_start,
                    "location": baseline.location,
                })

                if display_start.date() in heatmap_days:
                    idx = heatmap_days.index(display_start.date())
                    heatmap_counts.setdefault(module_name, [0] * len(heatmap_days))
                    heatmap_counts[module_name][idx] += 1

            _increment(stats, "mana", upcoming=upcoming_flag, completed=completed_flag)

    # Staff Tasks -----------------------------------------------------------
    if include_module("staff"):
        tasks = StaffTask.objects.prefetch_related("teams", "assignees")

        for task in tasks:
            start_dt = _combine(task.start_date) if task.start_date else None
            due_dt = _combine(task.due_date, default_time=time.max) if task.due_date else None
            start_for_sorting = start_dt or due_dt

            if not start_for_sorting:
                continue

            aware_due = _ensure_aware(due_dt)
            upcoming_flag = bool(aware_due and aware_due >= now)
            completed_flag = task.status == StaffTask.STATUS_COMPLETED

            assignee_names = [
                member.get_full_name() or member.username
                for member in task.assignees.all()
                if member
            ]
            task_teams = list(task.teams.all())
            team_names = [team.name for team in task_teams]
            team_slugs = [team.slug for team in task_teams]
            payload = {
                "id": f"staff-task-{task.pk}",
                "title": task.title,
                "start": _isoformat(start_for_sorting),
                "end": _isoformat(due_dt),
                "allDay": True,
                "backgroundColor": "#7c3aed",
                "borderColor": "#6d28d9",
                "textColor": "#f9fafb",
                "extendedProps": {
                    "module": "staff",
                    "category": "task",
                    "status": task.status,
                    "team": ", ".join(team_names) if team_names else "Unassigned",
                    "team_slugs": team_slugs,
                    "assignee": ", ".join(assignee_names) if assignee_names else "Unassigned",
                    "location": None,
                },
            }

            entries.append(payload)
            workflow_actions_entry: List[Dict] = []
            payload["extendedProps"]["workflowActions"] = workflow_actions_entry

            module_name = payload["extendedProps"].get("module", "staff")
            module_set.add(module_name)

            status_value = payload["extendedProps"].get("status") or "unspecified"
            status_counts.setdefault(module_name, {})
            status_counts[module_name][status_value] = (
                status_counts[module_name].get(status_value, 0) + 1
            )

            display_start = _ensure_aware(start_for_sorting)
            display_end = aware_due or display_start
            upcoming_items.append((display_start, {
                "module": module_name,
                "title": task.title,
                "start": display_start,
                "status": task.status,
            }))
            timed_entries.append({
                "module": module_name,
                "title": task.title,
                "start": display_start,
                "end": display_end,
                "location": None,
            })

            if display_start.date() in heatmap_days:
                idx = heatmap_days.index(display_start.date())
                heatmap_counts.setdefault(module_name, [0] * len(heatmap_days))
                heatmap_counts[module_name][idx] += 1

            _increment(stats, "staff", upcoming=upcoming_flag, completed=completed_flag)

            if task.status != StaffTask.STATUS_COMPLETED and aware_due:
                append_workflow_action(
                    workflow_actions_entry,
                    module_name,
                    payload["id"],
                    action_type="follow_up",
                    label="Staff task due",
                    due=aware_due,
                    status=task.status,
                    notes=task.description or "",
                )

    # Staff Trainings -------------------------------------------------------
    if include_module("staff"):
        enrollments = TrainingEnrollment.objects.select_related(
            "staff_profile__user", "program"
        )

        for enrollment in enrollments:
            scheduled_date = enrollment.scheduled_date
            start_dt = _combine(scheduled_date) if scheduled_date else None
            end_dt = start_dt

            if not start_dt:
                continue

            aware_start = _ensure_aware(start_dt)
            upcoming_flag = bool(aware_start and aware_start >= now)
            completed_flag = enrollment.status == TrainingEnrollment.STATUS_COMPLETED

            payload = {
                "id": f"staff-training-{enrollment.pk}",
                "title": f"Training: {enrollment.program.title}",
                "start": _isoformat(start_dt),
                "end": _isoformat(end_dt),
                "allDay": True,
                "backgroundColor": "#0ea5e9",
                "borderColor": "#0284c7",
                "textColor": "#0f172a",
                "extendedProps": {
                    "module": "staff",
                    "category": "training",
                    "status": enrollment.status,
                    "team": None,
                    "assignee": enrollment.staff_profile.user.get_full_name(),
                    "location": None,
                },
            }

            entries.append(payload)
            workflow_actions_entry: List[Dict] = []
            payload["extendedProps"]["workflowActions"] = workflow_actions_entry

            module_name = payload["extendedProps"].get("module", "staff")
            module_set.add(module_name)

            status_value = payload["extendedProps"].get("status") or "unspecified"
            status_counts.setdefault(module_name, {})
            status_counts[module_name][status_value] = (
                status_counts[module_name].get(status_value, 0) + 1
            )

            display_start = aware_start
            display_end = _ensure_aware(end_dt) if end_dt else None
            upcoming_items.append((display_start, {
                "module": module_name,
                "title": payload["title"],
                "start": display_start,
                "status": enrollment.status,
            }))
            timed_entries.append({
                "module": module_name,
                "title": payload["title"],
                "start": display_start,
                "end": display_end or display_start,
                "location": None,
            })

            if display_start.date() in heatmap_days:
                idx = heatmap_days.index(display_start.date())
                heatmap_counts.setdefault(module_name, [0] * len(heatmap_days))
                heatmap_counts[module_name][idx] += 1

            _increment(stats, "staff", upcoming=upcoming_flag, completed=completed_flag)

    # Policy Recommendations -------------------------------------------------
    if include_module("policy"):
        policies = PolicyRecommendation.objects.select_related("proposed_by", "lead_author")

        for policy in policies:
            milestones = [
                ("policy_submission", policy.submission_date, "Submission"),
                ("policy_review", policy.review_deadline, "Review Deadline"),
                ("policy_start", policy.implementation_start_date, "Implementation Start"),
                ("policy_deadline", policy.implementation_deadline, "Implementation Deadline"),
            ]

            for category, date_value, label in milestones:
                if not date_value:
                    continue

                start_dt = _combine(date_value)
                aware_start = _ensure_aware(start_dt)
                upcoming_flag = bool(aware_start and aware_start >= now)
                completed_flag = policy.status in {"implemented"}

                payload = {
                    "id": f"policy-{policy.pk}-{category}",
                    "title": f"{policy.title} ({label})",
                    "start": _isoformat(start_dt),
                    "end": _isoformat(start_dt + timedelta(days=1)),
                    "allDay": True,
                    "backgroundColor": "#ec4899",
                    "borderColor": "#db2777",
                    "textColor": "#fff7ed",
                    "extendedProps": {
                        "module": "policy",
                        "category": category,
                        "status": policy.status,
                        "priority": policy.priority,
                        "scope": policy.scope,
                        "location": None,
                    },
                }

                entries.append(payload)
                workflow_actions_entry: List[Dict] = []
                payload["extendedProps"]["workflowActions"] = workflow_actions_entry

                module_name = payload["extendedProps"].get("module", "policy")
                module_set.add(module_name)

                status_value = payload["extendedProps"].get("status") or "unspecified"
                status_counts.setdefault(module_name, {})
                status_counts[module_name][status_value] = (
                    status_counts[module_name].get(status_value, 0) + 1
                )

                upcoming_items.append((aware_start, {
                    "module": module_name,
                    "title": f"{policy.title} ({label})",
                    "start": aware_start,
                    "status": policy.status,
                }))
                timed_entries.append({
                    "module": module_name,
                    "title": f"{policy.title} ({label})",
                    "start": aware_start,
                    "end": aware_start + timedelta(hours=1),
                    "location": None,
                })

                if aware_start.date() in heatmap_days:
                    idx = heatmap_days.index(aware_start.date())
                    heatmap_counts.setdefault(module_name, [0] * len(heatmap_days))
                    heatmap_counts[module_name][idx] += 1

                _increment(stats, "policy", upcoming=upcoming_flag, completed=completed_flag)

                if category in {"policy_review", "policy_deadline"}:
                    is_escalated = aware_start < now and policy.status not in {"implemented", "approved"}
                    action_type = (
                        "approval"
                        if category == "policy_review"
                        else ("escalation" if is_escalated else "workflow")
                    )
                    append_workflow_action(
                        workflow_actions_entry,
                        module_name,
                        payload["id"],
                        action_type=action_type,
                        label=f"{label}",
                        due=aware_start,
                        status=policy.status,
                        notes=policy.rationale[:280],
                        severity="critical" if is_escalated else None,
                    )
                elif category == "policy_start":
                    append_workflow_action(
                        workflow_actions_entry,
                        module_name,
                        payload["id"],
                        action_type="workflow",
                        label="Implementation start",
                        due=aware_start,
                        status=policy.status,
                        notes=policy.proposed_solution[:280],
                    )

    # Planning & Monitoring Entries ----------------------------------------
    if include_module("planning"):
        planning_entries = MonitoringEntry.objects.select_related(
            "lead_organization", "submitted_by_community", "related_policy"
        )

        for entry in planning_entries:
            date_milestones = [
                ("planning_start", entry.start_date, "Start"),
                ("planning_milestone", entry.next_milestone_date, "Next Milestone"),
                ("planning_target_end", entry.target_end_date, "Target Completion"),
            ]

            for category, date_value, label in date_milestones:
                if not date_value:
                    continue

                start_dt = _combine(date_value)
                aware_start = _ensure_aware(start_dt)
                upcoming_flag = bool(aware_start and aware_start >= now)
                completed_flag = entry.status == "completed"

                payload = {
                    "id": f"planning-entry-{entry.pk}-{category}",
                    "title": f"{entry.title} ({label})",
                    "start": _isoformat(start_dt),
                    "end": _isoformat(start_dt + timedelta(days=1)),
                    "allDay": True,
                    "backgroundColor": "#14b8a6",
                    "borderColor": "#0f766e",
                    "textColor": "#0f172a",
                    "extendedProps": {
                        "module": "planning",
                        "category": category,
                        "status": entry.status,
                        "priority": entry.priority,
                        "location": None,
                        "sector": entry.sector,
                    },
                }

                entries.append(payload)
                workflow_actions_entry: List[Dict] = []
                payload["extendedProps"]["workflowActions"] = workflow_actions_entry

                module_name = payload["extendedProps"].get("module", "planning")
                module_set.add(module_name)

                status_value = payload["extendedProps"].get("status") or "unspecified"
                status_counts.setdefault(module_name, {})
                status_counts[module_name][status_value] = (
                    status_counts[module_name].get(status_value, 0) + 1
                )

                upcoming_items.append((aware_start, {
                    "module": module_name,
                    "title": f"{entry.title} ({label})",
                    "start": aware_start,
                    "status": entry.status,
                }))
                timed_entries.append({
                    "module": module_name,
                    "title": f"{entry.title} ({label})",
                    "start": aware_start,
                    "end": aware_start + timedelta(hours=1),
                    "location": None,
                })

                if aware_start.date() in heatmap_days:
                    idx = heatmap_days.index(aware_start.date())
                    heatmap_counts.setdefault(module_name, [0] * len(heatmap_days))
                    heatmap_counts[module_name][idx] += 1

                _increment(stats, "planning", upcoming=upcoming_flag, completed=completed_flag)

                if category == "planning_milestone":
                    append_workflow_action(
                        workflow_actions_entry,
                        module_name,
                        payload["id"],
                        action_type="follow_up",
                        label=f"{label}",
                        due=aware_start,
                        status=entry.status,
                        notes=entry.follow_up_actions or entry.support_required or "",
                    )
                elif category == "planning_target_end":
                    # Prefer structured outcome framework when available for calendar notes
                    notes = ""
                    if isinstance(entry.outcome_framework, dict):
                        outputs = entry.outcome_framework.get("outputs") or []
                        if outputs:
                            first_output = outputs[0]
                            indicator = first_output.get("indicator") or ""
                            target = first_output.get("target")
                            actual = first_output.get("actual")
                            notes = f"{indicator}: {actual or 0}/{target or 0}" if indicator else ""
                    if not notes and entry.outcome_indicators:
                        notes = entry.outcome_indicators[:280]

                    append_workflow_action(
                        workflow_actions_entry,
                        module_name,
                        payload["id"],
                        action_type="workflow",
                        label=f"{label}",
                        due=aware_start,
                        status=entry.status,
                        notes=notes,
                    )

        if include_module("planning"):
            stages = (
                MonitoringEntryWorkflowStage.objects.select_related("entry")
                .filter(due_date__isnull=False)
            )

            for stage in stages:
                if stage.status == MonitoringEntryWorkflowStage.STATUS_COMPLETED:
                    continue

                start_dt = _combine(stage.due_date)
                aware_start = _ensure_aware(start_dt)
                upcoming_flag = bool(aware_start and aware_start >= now)

                payload = {
                    "id": f"planning-stage-{stage.pk}",
                    "title": f"{stage.entry.title} - {stage.get_stage_display()}",
                    "start": _isoformat(start_dt),
                    "end": _isoformat(start_dt + timedelta(hours=1)),
                    "allDay": True,
                    "backgroundColor": "#0ea5e9",
                    "borderColor": "#0284c7",
                    "textColor": "#0f172a",
                    "extendedProps": {
                        "module": "planning",
                        "category": "workflow_stage",
                        "status": stage.status,
                        "location": None,
                    },
                }

                entries.append(payload)
                workflow_actions_entry: List[Dict] = []
                payload["extendedProps"]["workflowActions"] = workflow_actions_entry

                module_name = payload["extendedProps"].get("module", "planning")
                module_set.add(module_name)

                status_value = payload["extendedProps"].get("status") or "unspecified"
                status_counts.setdefault(module_name, {})
                status_counts[module_name][status_value] = (
                    status_counts[module_name].get(status_value, 0) + 1
                )

                upcoming_items.append((aware_start, {
                    "module": module_name,
                    "title": f"{stage.entry.title} - {stage.get_stage_display()}",
                    "start": aware_start,
                    "status": stage.status,
                }))
                timed_entries.append({
                    "module": module_name,
                    "title": f"{stage.entry.title} - {stage.get_stage_display()}",
                    "start": aware_start,
                    "end": aware_start + timedelta(hours=1),
                    "location": None,
                })

                if aware_start.date() in heatmap_days:
                    idx = heatmap_days.index(aware_start.date())
                    heatmap_counts.setdefault(module_name, [0] * len(heatmap_days))
                    heatmap_counts[module_name][idx] += 1

                _increment(stats, "planning", upcoming=upcoming_flag, completed=False)

                is_escalated = (
                    aware_start < now
                    or stage.status == MonitoringEntryWorkflowStage.STATUS_BLOCKED
                )
                append_workflow_action(
                    workflow_actions_entry,
                    module_name,
                    payload["id"],
                    action_type="escalation" if is_escalated else "workflow",
                    label=f"{stage.get_stage_display()}",
                    due=aware_start,
                    status=stage.status,
                    notes=stage.notes or stage.entry.support_required or "",
                    severity="critical" if is_escalated else None,
                )

    # Sort upcoming highlights ---------------------------------------------
    upcoming_items.sort(key=lambda item: item[0])
    upcoming_highlights = [
        {
            "module": data["module"],
            "title": data["title"],
            "start": data["start"],
            "status": data["status"],
        }
        for _, data in upcoming_items[:10]
    ]

    # Conflict detection ----------------------------------------------------
    conflicts: List[Dict[str, object]] = []
    timed_entries.sort(key=lambda item: item["start"] or now)

    for idx, candidate in enumerate(timed_entries):
        candidate_start = candidate["start"]
        candidate_end = candidate.get("end") or candidate_start
        if not candidate_start or not candidate_end:
            continue

        for other in timed_entries[idx + 1 :]:
            other_start = other["start"]
            if not other_start:
                continue
            if other_start >= candidate_end:
                break
            other_end = other.get("end") or other_start
            if other_end <= candidate_start:
                continue

            same_module = candidate["module"] == other["module"]
            same_location = (
                candidate.get("location")
                and candidate.get("location") == other.get("location")
            )

            if not (same_module or same_location):
                continue

            conflicts.append(
                {
                    "module": candidate["module"],
                    "title_a": candidate["title"],
                    "title_b": other["title"],
                    "start": candidate_start,
                    "end": candidate_end,
                    "location": candidate.get("location") or other.get("location"),
                }
            )

    follow_up_items.sort(key=lambda item: item["due"])

    for module in module_seed:
        module_set.add(module)

    module_stats = {}
    for module, data in stats.items():
        module_stats[module] = {
            "total": data.total,
            "upcoming": data.upcoming,
            "completed": data.completed,
        }
    for module in module_set:
        module_stats.setdefault(
            module,
            {"total": 0, "upcoming": 0, "completed": 0},
        )

    for module in module_set:
        status_counts.setdefault(module, {})
        heatmap_counts.setdefault(module, [0] * len(heatmap_days))

    heatmap_modules = []
    for module in module_seed:
        if module not in heatmap_modules and module in module_set:
            heatmap_modules.append(module)
    for module in sorted(module_set):
        if module not in heatmap_modules:
            heatmap_modules.append(module)

    analytics = {
        "heatmap": {
            "dates": heatmap_days,
            "modules": heatmap_modules,
            "matrix": {
                module: heatmap_counts.get(module, [0] * len(heatmap_days))
                for module in heatmap_modules
            },
        },
        "status_counts": {
            module: status_counts.get(module, {})
            for module in heatmap_modules
        },
        "workflow_summary": workflow_summary,
    }

    compliance_modules: Dict[str, Dict[str, int]] = {}
    compliance_totals = {
        "overdue": 0,
        "pending_approvals": 0,
        "escalations": 0,
        "follow_up": 0,
    }

    for action in workflow_actions_global:
        module = action.get("module")
        if not module:
            continue

        module_stats_record = compliance_modules.setdefault(
            module,
            {
                "overdue": 0,
                "pending_approvals": 0,
                "escalations": 0,
                "follow_up": 0,
            },
        )

        if action.get("overdue"):
            module_stats_record["overdue"] += 1
            compliance_totals["overdue"] += 1

        action_type = action.get("type")
        if action_type == "approval":
            module_stats_record["pending_approvals"] += 1
            compliance_totals["pending_approvals"] += 1
        elif action_type == "escalation":
            module_stats_record["escalations"] += 1
            compliance_totals["escalations"] += 1
        elif action_type == "follow_up":
            module_stats_record["follow_up"] += 1
            compliance_totals["follow_up"] += 1

    analytics["compliance"] = {
        "modules": compliance_modules,
        "totals": compliance_totals,
    }

    return {
        "entries": entries,
        "module_stats": module_stats,
        "upcoming_highlights": upcoming_highlights,
        "conflicts": conflicts,
        "follow_up_items": follow_up_items,
        "workflow_actions": workflow_actions_global,
        "analytics": analytics,
    }
