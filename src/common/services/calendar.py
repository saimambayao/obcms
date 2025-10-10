"""Shared calendar aggregation utilities for OOBC modules."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, time, timedelta
from typing import Dict, List, Optional, Sequence, Tuple

from django.core.cache import cache
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone
from django.utils.dateparse import parse_date

from common.constants import CALENDAR_MODULE_ORDER
from common.models import (
    CalendarResourceBooking,
    StaffLeave,
    TrainingEnrollment,
    WorkItem,  # Replaced StaffTask
)
from communities.models import CommunityEvent, OBCCommunity
from coordination.models import (
    Communication,
    # Event removed - migrated to WorkItem
    Organization,
    Partnership,
    PartnershipMilestone,
    StakeholderEngagement,
)
from mana.models import BaselineDataCollection
from monitoring.models import MonitoringEntry, MonitoringEntryWorkflowStage
from recommendations.policy_tracking.models import PolicyRecommendation


CALENDAR_CACHE_INDEX_KEY = "calendar:payload:index"
CALENDAR_CACHE_TTL = 300  # seconds


def invalidate_calendar_cache() -> None:
    """Clear cached calendar payloads and per-view responses."""

    cache.clear()


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


def _increment(
    stats: Dict[str, CalendarStats], module: str, *, upcoming: bool, completed: bool
) -> None:
    """Increment module stats counters."""

    record = stats.setdefault(module, CalendarStats())
    record.total += 1
    if upcoming:
        record.upcoming += 1
    if completed:
        record.completed += 1


def _oobc_workitem_scope() -> Q:
    """
    Return a Q clause limiting WorkItem queries to OOBC-owned items.

    Excludes MOA work items implemented by external organizations while
    preserving OOBC-led MOAs so they continue to surface in internal tools.
    """
    oobc_org = (
        Organization.objects.filter(
            name__iexact="Office for Other Bangsamoro Communities (OOBC)"
        ).first()
        or Organization.objects.filter(acronym__iexact="OOBC").first()
    )

    moa_filter = Q(ppa_category="moa_ppa") | Q(related_ppa__category="moa_ppa")
    if oobc_org:
        oobc_owned_moa = Q(implementing_moa=oobc_org) | Q(
            related_ppa__implementing_moa=oobc_org
        )
        return ~(moa_filter & ~oobc_owned_moa)
    return ~moa_filter


def build_calendar_payload(
    *,
    filter_modules: Optional[Sequence[str]] = None,
) -> Dict[str, object]:
    """Gather calendar entries across OOBC modules.

    Args:
        filter_modules: optional iterable restricting modules to include.

    Returns:
        Dict containing entries, module statistics, upcoming highlights, and
        conflict hints suitable for rendering calendar dashboards.
    """

    requested_modules = list(filter_modules) if filter_modules is not None else None
    allowed_modules_set = set(requested_modules or []) or None

    now = timezone.now()
    due_soon_cutoff = now + timedelta(days=2)
    oobc_scope = _oobc_workitem_scope()

    normalized_modules = ("__all__",)
    if allowed_modules_set is not None:
        normalized_modules = tuple(sorted(allowed_modules_set)) or ("__all__",)

    cache_key = f"calendar:payload:{'|'.join(normalized_modules)}"
    cached_payload = cache.get(cache_key)
    if cached_payload is not None:
        return deepcopy(cached_payload)

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

    # Coordination Events (migrated to WorkItem) ---------------------------
    # TODO: Refactor to use WorkItem with work_type='activity'
    # See: docs/refactor/WORKITEM_MIGRATION_COMPLETE.md
    if include_module("coordination"):
        events = (
            WorkItem.objects.filter(
                oobc_scope,
                work_type__in=['activity', 'sub_activity'],
            )
            .select_related("created_by")
        )

        for event in events:
            start_dt = _combine(event.start_date, event.start_time)
            all_day = event.start_time is None

            # WorkItem uses due_date instead of end_date
            if event.due_date:
                end_time = (
                    event.end_time
                    if event.end_time
                    else (time.max if not all_day else time.max)
                )
                end_dt = _combine(event.due_date, end_time)
                if all_day and end_dt:
                    end_dt = end_dt + timedelta(days=1)
            elif event.end_time:
                end_dt = _combine(event.start_date, event.end_time)
            elif all_day and start_dt:
                end_dt = start_dt + timedelta(days=1)
            else:
                end_dt = start_dt

            aware_start = _ensure_aware(start_dt)
            upcoming_flag = bool(aware_start and aware_start >= now)
            completed_flag = event.status == "completed"

            # WorkItem doesn't have community, organizer, venue fields
            # These were part of the old Event model
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
                    "type": "event",
                    "objectId": str(event.pk),
                    "supportsEditing": True,
                    "modalUrl": reverse(
                        "common:work_item_modal", kwargs={"work_item_id": event.pk}
                    ),
                    "status": event.status,
                    "workType": event.get_work_type_display(),
                    "description": event.description or "",
                },
                "editable": True,
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
                upcoming_items.append(
                    (
                        display_start,
                        {
                            "module": module_name,
                            "title": event.title,
                            "start": display_start,
                            "status": event.status,
                        },
                    )
                )
                timed_entries.append(
                    {
                        "module": module_name,
                        "title": event.title,
                        "start": display_start,
                        "end": display_end or display_start,
                        "location": "",  # WorkItem doesn't have venue field
                    }
                )

                if display_start.date() in heatmap_days:
                    idx = heatmap_days.index(display_start.date())
                    heatmap_counts.setdefault(module_name, [0] * len(heatmap_days))
                    heatmap_counts[module_name][idx] += 1

            _increment(
                stats, "coordination", upcoming=upcoming_flag, completed=completed_flag
            )

            if aware_start:
                severity = None
                label = None
                action_type = None

                # WorkItem status values: not_started, in_progress, at_risk, blocked, completed, cancelled
                if event.status == "not_started":
                    label = "Activity not started"
                    action_type = "approval"
                    if aware_start < now:
                        severity = "critical"
                        action_type = "escalation"
                elif event.status == "in_progress":
                    label = "Activity in progress"
                    action_type = "workflow"
                    if aware_start < now and event.due_date and event.due_date < now.date():
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
                        notes=event.description[:280] if event.description else "",
                        severity=severity,
                    )

            # WorkItem doesn't have follow_up_required, follow_up_date, follow_up_notes
            # These were part of the old Event model

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
                    "type": "engagement",
                    "objectId": str(engagement.pk),
                    "supportsEditing": True,
                    "status": engagement.status,
                    "community": getattr(engagement.community, "name", ""),
                    "engagementType": getattr(engagement.engagement_type, "name", ""),
                    "location": engagement.venue,
                },
                "editable": True,
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
                upcoming_items.append(
                    (
                        display_start,
                        {
                            "module": module_name,
                            "title": engagement.title,
                            "start": display_start,
                            "status": engagement.status,
                        },
                    )
                )
                timed_entries.append(
                    {
                        "module": module_name,
                        "title": engagement.title,
                        "start": display_start,
                        "end": display_end or display_start,
                        "location": engagement.venue,
                    }
                )

                if display_start.date() in heatmap_days:
                    idx = heatmap_days.index(display_start.date())
                    heatmap_counts.setdefault(module_name, [0] * len(heatmap_days))
                    heatmap_counts[module_name][idx] += 1

            _increment(
                stats, "coordination", upcoming=upcoming_flag, completed=completed_flag
            )

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
                    "status": (
                        "completed" if communication.follow_up_completed else "pending"
                    ),
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

            upcoming_items.append(
                (
                    aware_start,
                    {
                        "module": module_name,
                        "title": communication.subject,
                        "start": aware_start,
                        "status": status_value,
                    },
                )
            )
            timed_entries.append(
                {
                    "module": module_name,
                    "title": communication.subject,
                    "start": aware_start,
                    "end": aware_start + timedelta(hours=1),
                    "location": None,
                }
            )

            if aware_start.date() in heatmap_days:
                idx = heatmap_days.index(aware_start.date())
                heatmap_counts.setdefault(module_name, [0] * len(heatmap_days))
                heatmap_counts[module_name][idx] += 1

            _increment(
                stats, "coordination", upcoming=upcoming_flag, completed=completed_flag
            )

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
                    "end": (
                        _isoformat(start_dt + timedelta(days=1)) if start_dt else None
                    ),
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
                    display_end = (
                        _ensure_aware(start_dt + timedelta(days=1))
                        if start_dt
                        else None
                    )
                    upcoming_items.append(
                        (
                            display_start,
                            {
                                "module": module_name,
                                "title": payload["title"],
                                "start": display_start,
                                "status": status_value,
                            },
                        )
                    )
                    timed_entries.append(
                        {
                            "module": module_name,
                            "title": payload["title"],
                            "start": display_start,
                            "end": display_end or display_start,
                            "location": None,
                        }
                    )

                    if display_start.date() in heatmap_days:
                        idx = heatmap_days.index(display_start.date())
                        heatmap_counts.setdefault(module_name, [0] * len(heatmap_days))
                        heatmap_counts[module_name][idx] += 1

                _increment(
                    stats,
                    "coordination",
                    upcoming=upcoming_flag,
                    completed=partnership_complete,
                )

                due = aware_start
                if start_dt and start_dt.time() == time.min:
                    due = _ensure_aware(_combine(date_value, time.max))
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
            upcoming_items.append(
                (
                    display_start,
                    {
                        "module": module_name,
                        "title": payload["title"],
                        "start": display_start,
                        "status": milestone.status,
                    },
                )
            )
            timed_entries.append(
                {
                    "module": module_name,
                    "title": payload["title"],
                    "start": display_start,
                    "end": display_start + timedelta(hours=1),
                    "location": None,
                }
            )

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

                if milestone.status in {"delayed", "overdue"} or (due and due < now):
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
                upcoming_items.append(
                    (
                        display_start,
                        {
                            "module": module_name,
                            "title": payload["title"],
                            "start": display_start,
                            "status": baseline.status,
                        },
                    )
                )
                timed_entries.append(
                    {
                        "module": module_name,
                        "title": payload["title"],
                        "start": display_start,
                        "end": display_end or display_start,
                        "location": baseline.location,
                    }
                )

                if display_start.date() in heatmap_days:
                    idx = heatmap_days.index(display_start.date())
                    heatmap_counts.setdefault(module_name, [0] * len(heatmap_days))
                    heatmap_counts[module_name][idx] += 1

            _increment(stats, "mana", upcoming=upcoming_flag, completed=completed_flag)

    # Staff Tasks (migrated to WorkItem) ---------------------------------------
    # TODO: Refactor to use WorkItem instead of StaffTask
    # See: docs/refactor/WORKITEM_MIGRATION_COMPLETE.md
    if include_module("staff"):
        tasks = (
            WorkItem.objects.filter(
                oobc_scope,
                work_type__in=['task', 'subtask'],
            )
            .prefetch_related(
                "assignees",
                "parent",
            )
        )

        for task in tasks:
            # Skip tasks that are linked to activities (to avoid duplication with coordination module)
            # This replaces the old behavior of skipping tasks with linked_event
            if task.parent and task.parent.work_type in ['activity', 'sub_activity']:
                continue

            start_dt = _combine(task.start_date) if task.start_date else None
            due_dt = (
                _combine(task.due_date, default_time=time.max)
                if task.due_date
                else None
            )
            start_for_sorting = start_dt or due_dt

            if not start_for_sorting:
                continue

            aware_due = _ensure_aware(due_dt)
            upcoming_flag = bool(aware_due and aware_due >= now)
            completed_flag = task.status == 'completed'

            assignee_names = [
                member.get_full_name() or member.username
                for member in task.assignees.all()
                if member
            ]
            team_names = []
            team_slugs = []

            # Default task color
            task_color = "#7c3aed"  # Purple

            payload = {
                "id": f"staff-task-{task.pk}",
                "title": task.title,
                "start": _isoformat(start_for_sorting),
                "end": _isoformat(due_dt),
                "allDay": True,
                "backgroundColor": task_color,
                "borderColor": task_color,
                "textColor": "#f9fafb",
                "extendedProps": {
                    "module": "staff",
                    "category": "task",
                    "type": "staff_task",
                    "objectId": str(task.pk),
                    "supportsEditing": True,
                    "hasStartDate": bool(task.start_date),
                    "hasDueDate": bool(task.due_date),
                    "modalUrl": reverse("common:work_item_modal", kwargs={"work_item_id": task.pk}),
                    "status": task.status,
                    "team": ", ".join(team_names) if team_names else "Unassigned",
                    "team_slugs": team_slugs,
                    "assignee": (
                        ", ".join(assignee_names) if assignee_names else "Unassigned"
                    ),
                    "location": None,
                    "description": task.description or "",
                    "workType": task.get_work_type_display(),
                },
                "editable": True,
                "durationEditable": True,
            }

            # WorkItem uses parent/children hierarchy instead of linked_workflow/linked_event
            # Add parent context if exists
            if task.parent:
                payload["extendedProps"]["parent"] = {
                    "id": str(task.parent.id),
                    "title": task.parent.title,
                    "workType": task.parent.get_work_type_display(),
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
            upcoming_items.append(
                (
                    display_start,
                    {
                        "module": module_name,
                        "title": task.title,
                        "start": display_start,
                        "status": task.status,
                    },
                )
            )
            timed_entries.append(
                {
                    "module": module_name,
                    "title": task.title,
                    "start": display_start,
                    "end": display_end,
                    "location": None,
                }
            )

            if display_start.date() in heatmap_days:
                idx = heatmap_days.index(display_start.date())
                heatmap_counts.setdefault(module_name, [0] * len(heatmap_days))
                heatmap_counts[module_name][idx] += 1

            _increment(stats, "staff", upcoming=upcoming_flag, completed=completed_flag)

            if task.status != 'completed' and aware_due:
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
            upcoming_items.append(
                (
                    display_start,
                    {
                        "module": module_name,
                        "title": payload["title"],
                        "start": display_start,
                        "status": enrollment.status,
                    },
                )
            )
            timed_entries.append(
                {
                    "module": module_name,
                    "title": payload["title"],
                    "start": display_start,
                    "end": display_end or display_start,
                    "location": None,
                }
            )

            if display_start.date() in heatmap_days:
                idx = heatmap_days.index(display_start.date())
                heatmap_counts.setdefault(module_name, [0] * len(heatmap_days))
                heatmap_counts[module_name][idx] += 1

            _increment(stats, "staff", upcoming=upcoming_flag, completed=completed_flag)

    # Policy Recommendations -------------------------------------------------
    if include_module("policy"):
        policies = PolicyRecommendation.objects.select_related(
            "proposed_by", "lead_author"
        )

        for policy in policies:
            milestones = [
                ("policy_submission", policy.submission_date, "Submission"),
                ("policy_review", policy.review_deadline, "Review Deadline"),
                (
                    "policy_start",
                    policy.implementation_start_date,
                    "Implementation Start",
                ),
                (
                    "policy_deadline",
                    policy.implementation_deadline,
                    "Implementation Deadline",
                ),
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

                upcoming_items.append(
                    (
                        aware_start,
                        {
                            "module": module_name,
                            "title": f"{policy.title} ({label})",
                            "start": aware_start,
                            "status": policy.status,
                        },
                    )
                )
                timed_entries.append(
                    {
                        "module": module_name,
                        "title": f"{policy.title} ({label})",
                        "start": aware_start,
                        "end": aware_start + timedelta(hours=1),
                        "location": None,
                    }
                )

                if aware_start.date() in heatmap_days:
                    idx = heatmap_days.index(aware_start.date())
                    heatmap_counts.setdefault(module_name, [0] * len(heatmap_days))
                    heatmap_counts[module_name][idx] += 1

                _increment(
                    stats, "policy", upcoming=upcoming_flag, completed=completed_flag
                )

                if category in {"policy_review", "policy_deadline"}:
                    is_escalated = aware_start < now and policy.status not in {
                        "implemented",
                        "approved",
                    }
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

                upcoming_items.append(
                    (
                        aware_start,
                        {
                            "module": module_name,
                            "title": f"{entry.title} ({label})",
                            "start": aware_start,
                            "status": entry.status,
                        },
                    )
                )
                timed_entries.append(
                    {
                        "module": module_name,
                        "title": f"{entry.title} ({label})",
                        "start": aware_start,
                        "end": aware_start + timedelta(hours=1),
                        "location": None,
                    }
                )

                if aware_start.date() in heatmap_days:
                    idx = heatmap_days.index(aware_start.date())
                    heatmap_counts.setdefault(module_name, [0] * len(heatmap_days))
                    heatmap_counts[module_name][idx] += 1

                _increment(
                    stats, "planning", upcoming=upcoming_flag, completed=completed_flag
                )

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
                            notes = (
                                f"{indicator}: {actual or 0}/{target or 0}"
                                if indicator
                                else ""
                            )
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

            # Custom milestone timeline populated via JSON metadata
            raw_milestones = entry.milestone_dates or []
            if isinstance(raw_milestones, dict):
                raw_milestones = [raw_milestones]
            elif not isinstance(raw_milestones, (list, tuple)):
                raw_milestones = []

            status_color_map = {
                "completed": ("#22c55e", "#16a34a"),  # emerald
                "done": ("#22c55e", "#16a34a"),
                "closed": ("#22c55e", "#16a34a"),
                "delayed": ("#f97316", "#ea580c"),  # amber
                "at_risk": ("#f97316", "#ea580c"),
                "blocked": ("#f43f5e", "#e11d48"),  # rose
                "overdue": ("#f43f5e", "#e11d48"),
                "cancelled": ("#94a3b8", "#64748b"),  # slate
            }

            for milestone_index, milestone in enumerate(raw_milestones):
                if not isinstance(milestone, dict):
                    continue

                milestone_date_value = milestone.get("date")
                parsed_date = None

                if isinstance(milestone_date_value, datetime):
                    parsed_date = milestone_date_value.date()
                elif hasattr(milestone_date_value, "isoformat") and not isinstance(
                    milestone_date_value, (str, bytes)
                ):
                    parsed_date = milestone_date_value
                elif isinstance(milestone_date_value, str):
                    parsed_date = parse_date(milestone_date_value)
                    if parsed_date is None:
                        try:
                            parsed_date = datetime.fromisoformat(
                                milestone_date_value
                            ).date()
                        except ValueError:
                            parsed_date = None

                if parsed_date is None:
                    continue

                start_dt = _combine(parsed_date)
                aware_start = _ensure_aware(start_dt)

                milestone_status = (
                    str(milestone.get("status") or "").lower() or entry.status
                )
                milestone_title = (
                    milestone.get("title") or milestone.get("label") or "Milestone"
                )
                milestone_notes = (
                    milestone.get("notes")
                    or milestone.get("description")
                    or milestone.get("summary")
                    or ""
                )

                background_color, border_color = status_color_map.get(
                    milestone_status,
                    ("#14b8a6", "#0f766e"),
                )

                completed_flag = milestone_status in {"completed", "done", "closed"}
                upcoming_flag = bool(
                    aware_start and aware_start >= now and not completed_flag
                )

                payload = {
                    "id": f"planning-entry-{entry.pk}-milestone-{milestone_index}",
                    "title": f"{entry.title} – {milestone_title}",
                    "start": _isoformat(start_dt),
                    "end": _isoformat(start_dt + timedelta(days=1)),
                    "allDay": True,
                    "backgroundColor": background_color,
                    "borderColor": border_color,
                    "textColor": "#0f172a",
                    "extendedProps": {
                        "module": "planning",
                        "category": "planning_milestone_custom",
                        "status": milestone_status,
                        "priority": entry.priority,
                        "location": None,
                        "sector": entry.sector,
                        "milestoneTitle": milestone_title,
                        "milestoneStatus": milestone_status,
                        "milestoneIndex": milestone_index,
                        "relatedEntryId": str(entry.pk),
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

                if aware_start:
                    upcoming_items.append(
                        (
                            aware_start,
                            {
                                "module": module_name,
                                "title": payload["title"],
                                "start": aware_start,
                                "status": milestone_status,
                            },
                        )
                    )
                    timed_entries.append(
                        {
                            "module": module_name,
                            "title": payload["title"],
                            "start": aware_start,
                            "end": aware_start + timedelta(hours=1),
                            "location": None,
                        }
                    )

                    if aware_start.date() in heatmap_days:
                        idx = heatmap_days.index(aware_start.date())
                        heatmap_counts.setdefault(module_name, [0] * len(heatmap_days))
                        heatmap_counts[module_name][idx] += 1

                _increment(
                    stats, "planning", upcoming=upcoming_flag, completed=completed_flag
                )

                risk_statuses = {"delayed", "at_risk", "blocked", "overdue"}
                severity = None
                action_type = "workflow"

                if completed_flag:
                    action_type = "workflow"
                elif milestone_status in risk_statuses or (
                    aware_start and aware_start < now
                ):
                    action_type = "escalation"
                    severity = "critical"
                elif upcoming_flag:
                    action_type = "follow_up"

                append_workflow_action(
                    workflow_actions_entry,
                    module_name,
                    payload["id"],
                    action_type=action_type,
                    label=milestone_title,
                    due=aware_start,
                    status=milestone_status,
                    notes=milestone_notes,
                    severity=severity,
                )

        if include_module("planning"):
            stages = MonitoringEntryWorkflowStage.objects.select_related(
                "entry"
            ).filter(due_date__isnull=False)

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

                upcoming_items.append(
                    (
                        aware_start,
                        {
                            "module": module_name,
                            "title": f"{stage.entry.title} - {stage.get_stage_display()}",
                            "start": aware_start,
                            "status": stage.status,
                        },
                    )
                )
                timed_entries.append(
                    {
                        "module": module_name,
                        "title": f"{stage.entry.title} - {stage.get_stage_display()}",
                        "start": aware_start,
                        "end": aware_start + timedelta(hours=1),
                        "location": None,
                    }
                )

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

    # Community Events ------------------------------------------------------
    if include_module("communities"):
        community_events = CommunityEvent.objects.select_related("community").filter(
            is_public=True
        )

        for ce in community_events:
            start_dt = _combine(
                ce.start_date, ce.start_time if not ce.all_day else None
            )
            end_dt = (
                _combine(ce.end_date, ce.end_time if not ce.all_day else None)
                if ce.end_date
                else start_dt
            )

            if ce.all_day and end_dt:
                end_dt = end_dt + timedelta(days=1)

            aware_start = _ensure_aware(start_dt)
            upcoming_flag = bool(aware_start and aware_start >= now)

            # Color based on event type
            if ce.event_type == "cultural":
                bg_color = "#f59e0b"  # amber
                border_color = "#d97706"
            elif ce.event_type == "religious":
                bg_color = "#8b5cf6"  # purple
                border_color = "#7c3aed"
            elif ce.event_type == "disaster":
                bg_color = "#ef4444"  # red
                border_color = "#dc2626"
            else:
                bg_color = "#10b981"  # green
                border_color = "#059669"

            payload = {
                "id": f"communities-event-{ce.pk}",
                "title": f"[{ce.community.name}] {ce.title}",
                "start": _isoformat(start_dt),
                "end": _isoformat(end_dt),
                "allDay": ce.all_day,
                "backgroundColor": bg_color,
                "borderColor": border_color,
                "extendedProps": {
                    "module": "communities",
                    "category": "community_event",
                    "event_type": ce.event_type,
                    "community": ce.community.name,
                    "is_recurring": ce.is_recurring,
                },
            }

            entries.append(payload)
            module_name = "communities"
            module_set.add(module_name)

            if start_dt and aware_start.date() in heatmap_days:
                idx = heatmap_days.index(aware_start.date())
                heatmap_counts.setdefault(module_name, [0] * len(heatmap_days))
                heatmap_counts[module_name][idx] += 1

            _increment(stats, module_name, upcoming=upcoming_flag, completed=False)

            if upcoming_flag:
                upcoming_items.append(
                    (
                        aware_start,
                        {
                            "module": module_name,
                            "title": f"[{ce.community.name}] {ce.title}",
                            "start": aware_start,
                            "status": "scheduled",
                        },
                    )
                )

    # Staff Leave -----------------------------------------------------------
    if include_module("staff"):
        staff_leaves = StaffLeave.objects.select_related("staff").filter(
            status__in=["pending", "approved"]
        )

        for leave in staff_leaves:
            start_dt = _combine(leave.start_date)
            end_dt = _combine(leave.end_date)
            if end_dt:
                end_dt = end_dt + timedelta(days=1)  # Include end date

            aware_start = _ensure_aware(start_dt)
            upcoming_flag = bool(aware_start and aware_start >= now)

            # Color based on leave status
            if leave.status == "approved":
                bg_color = "#6366f1"  # indigo
                border_color = "#4f46e5"
            else:  # pending
                bg_color = "#f59e0b"  # amber
                border_color = "#d97706"

            staff_name = leave.staff.get_full_name().strip()
            username = (leave.staff.username or "").strip()
            title_prefix = username or staff_name or "OOBC Staff"

            payload = {
                "id": f"staff-leave-{leave.pk}",
                "title": f"{title_prefix} - {leave.get_leave_type_display()}",
                "start": _isoformat(start_dt),
                "end": _isoformat(end_dt),
                "allDay": True,
                "backgroundColor": bg_color,
                "borderColor": border_color,
                "extendedProps": {
                    "module": "staff",
                    "category": "leave",
                    "leave_type": leave.leave_type,
                    "status": leave.status,
                    "staff_member": staff_name or username,
                },
            }

            entries.append(payload)
            workflow_actions_entry: List[Dict] = []
            payload["extendedProps"]["workflowActions"] = workflow_actions_entry

            module_name = "staff"
            module_set.add(module_name)

            if start_dt and aware_start.date() in heatmap_days:
                idx = heatmap_days.index(aware_start.date())
                heatmap_counts.setdefault(module_name, [0] * len(heatmap_days))
                heatmap_counts[module_name][idx] += 1

            _increment(
                stats,
                module_name,
                upcoming=upcoming_flag,
                completed=leave.status == "completed",
            )

            # Add approval workflow if pending
            if leave.status == "pending":
                append_workflow_action(
                    workflow_actions_entry,
                    module_name,
                    payload["id"],
                    action_type="approval",
                    label="Pending Leave Approval",
                    due=aware_start,
                    status=leave.status,
                    notes=f"{leave.get_leave_type_display()} - {leave.reason[:100]}",
                )

    # Resource Bookings -----------------------------------------------------
    if include_module("resources"):
        bookings = CalendarResourceBooking.objects.select_related(
            "resource", "booked_by"
        ).filter(status__in=["pending", "approved"])

        for booking in bookings:
            aware_start = _ensure_aware(booking.start_datetime)
            aware_end = _ensure_aware(booking.end_datetime)
            upcoming_flag = bool(aware_start and aware_start >= now)

            # Get description from notes or linked event
            description = booking.notes[:50] if booking.notes else "Resource Booking"

            # Color based on status
            if booking.status == "approved":
                bg_color = "#059669"  # emerald
                border_color = "#047857"
            else:  # pending
                bg_color = "#f59e0b"  # amber
                border_color = "#d97706"

            payload = {
                "id": f"resources-booking-{booking.pk}",
                "title": booking.resource.name,
                "start": _isoformat(booking.start_datetime),
                "end": _isoformat(booking.end_datetime),
                "allDay": False,
                "backgroundColor": bg_color,
                "borderColor": border_color,
                "extendedProps": {
                    "module": "resources",
                    "category": "booking",
                    "resource": booking.resource.name,
                    "resource_type": booking.resource.resource_type,
                    "status": booking.status,
                    "booked_by": booking.booked_by.get_full_name(),
                    "notes": description,
                },
            }

            entries.append(payload)
            workflow_actions_entry: List[Dict] = []
            payload["extendedProps"]["workflowActions"] = workflow_actions_entry

            module_name = "resources"
            module_set.add(module_name)

            if aware_start.date() in heatmap_days:
                idx = heatmap_days.index(aware_start.date())
                heatmap_counts.setdefault(module_name, [0] * len(heatmap_days))
                heatmap_counts[module_name][idx] += 1

            _increment(
                stats,
                module_name,
                upcoming=upcoming_flag,
                completed=booking.status == "completed",
            )

            if upcoming_flag:
                upcoming_items.append(
                    (
                        aware_start,
                        {
                            "module": module_name,
                            "title": f"[{booking.resource.name}] {description[:30]}",
                            "start": aware_start,
                            "status": booking.status,
                        },
                    )
                )

            timed_entries.append(
                {
                    "module": module_name,
                    "title": f"[{booking.resource.name}] {description[:30]}",
                    "start": aware_start,
                    "end": aware_end,
                    "location": booking.resource.location,
                }
            )

            # Add approval workflow if pending
            if booking.status == "pending":
                append_workflow_action(
                    workflow_actions_entry,
                    module_name,
                    payload["id"],
                    action_type="approval",
                    label="Pending Booking Approval",
                    due=aware_start,
                    status=booking.status,
                    notes=f"{booking.resource.name} - {description[:100]}",
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
            same_location = candidate.get("location") and candidate.get(
                "location"
            ) == other.get("location")

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
            module: status_counts.get(module, {}) for module in heatmap_modules
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

    for entry in entries:
        props = entry.setdefault("extendedProps", {})
        if props.get("supportsEditing") is True:
            entry.setdefault("editable", True)
        else:
            props["supportsEditing"] = False
            if entry.get("editable") is not True:
                entry["editable"] = False
            entry.setdefault("durationEditable", False)

    payload = {
        "entries": entries,
        "module_stats": module_stats,
        "upcoming_highlights": upcoming_highlights,
        "conflicts": conflicts,
        "follow_up_items": follow_up_items,
        "workflow_actions": workflow_actions_global,
        "analytics": analytics,
    }

    cache.set(cache_key, payload, timeout=CALENDAR_CACHE_TTL)
    cache_index = set(cache.get(CALENDAR_CACHE_INDEX_KEY, []))
    cache_index.add(cache_key)
    cache.set(CALENDAR_CACHE_INDEX_KEY, list(cache_index), timeout=CALENDAR_CACHE_TTL)

    return deepcopy(payload)
