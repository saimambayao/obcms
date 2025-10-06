import json

import pytest
from datetime import timedelta
from django.urls import reverse
from django.utils import timezone
from django.core.cache import cache

from common.models import StaffTeam, User
from common.work_item_model import WorkItem
from common.services.calendar import build_calendar_payload
from coordination.models import (
    Communication,
    Organization,
    Partnership,
    PartnershipMilestone,
)
from monitoring.models import MonitoringEntry
from recommendations.policy_tracking.models import PolicyRecommendation


@pytest.mark.django_db
def test_oobc_calendar_view_renders_for_staff(client):
    user = User.objects.create_user(
        username="calendar_user",
        password="password123",
        user_type="oobc_staff",
        is_staff=True,
        is_approved=True,
    )
    client.force_login(user)

    response = client.get(reverse("common:oobc_calendar"))

    assert response.status_code == 200
    assert "module_cards" in response.context
    assert "calendar_events_json" in response.context
    assert "follow_up_items" in response.context
    data = (
        json.loads(response.context["calendar_events_json"])
        if response.context["calendar_events_json"]
        else []
    )
    assert isinstance(data, list)


@pytest.mark.django_db
def test_build_calendar_payload_handles_staff_tasks():
    staff_user = User.objects.create_user(
        username="tasker",
        password="secret",
        user_type="oobc_staff",
        is_approved=True,
    )
    team = StaffTeam.objects.create(
        name="Coordination Team", description="", is_active=True
    )
    task = WorkItem.objects.create(
        title="Prepare briefing",
        description="",
        work_type=WorkItem.WORK_TYPE_TASK,
        created_by=staff_user,
        status=WorkItem.STATUS_IN_PROGRESS,
        priority=WorkItem.PRIORITY_HIGH,
        start_date=timezone.now().date(),
        due_date=timezone.now().date(),
    )
    task.assignees.set([staff_user])
    task.teams.set([team])

    payload = build_calendar_payload(filter_modules=["staff"])

    assert payload["module_stats"].get("staff", {}).get("total") == 1
    assert any(
        entry["extendedProps"].get("module") == "staff" for entry in payload["entries"]
    )


@pytest.mark.django_db
def test_build_calendar_payload_includes_policy_and_planning():
    user = User.objects.create_user(
        username="planner",
        password="secret",
        user_type="oobc_staff",
        is_approved=True,
    )

    org = Organization.objects.create(
        name="Test Organization",
        organization_type="nga",
    )

    communication = Communication.objects.create(
        organization=org,
        communication_type="email",
        direction="outgoing",
        status="sent",
        priority="medium",
        subject="Follow-up needed",
        content="Coordinate with partner",
        communication_date=timezone.now().date(),
        requires_follow_up=True,
        follow_up_date=timezone.now().date() + timedelta(days=1),
        recorded_by=user,
    )

    policy = PolicyRecommendation.objects.create(
        title="Scholarship Support",
        category="social_development",
        description="Expand scholarship coverage",
        rationale="Address educational gaps",
        scope="regional",
        proposed_by=user,
        problem_statement="Limited scholarship slots for OBCs",
        policy_objectives="Ensure equitable access",
        proposed_solution="Create dedicated scholarship fund",
        expected_outcomes="Increased scholarship recipients",
        submission_date=timezone.now().date(),
        review_deadline=timezone.now().date() + timedelta(days=2),
        implementation_start_date=timezone.now().date() + timedelta(days=10),
    )

    MonitoringEntry.objects.create(
        title="Livelihood Program",
        category="moa_ppa",
        summary="Skills training for fisherfolk",
        start_date=timezone.now().date() + timedelta(days=3),
        next_milestone_date=timezone.now().date() + timedelta(days=5),
        milestone_dates=[
            {
                "date": (timezone.now().date() + timedelta(days=7)).isoformat(),
                "title": "Procurement window",
                "status": "upcoming",
            }
        ],
        lead_organization=org,
        created_by=user,
    )

    payload = build_calendar_payload(
        filter_modules=["coordination", "policy", "planning"]
    )

    assert payload["module_stats"].get("policy", {}).get("total") >= 1
    assert payload["module_stats"].get("planning", {}).get("total") >= 1
    follow_up_modules = {item["module"] for item in payload.get("follow_up_items", [])}
    assert "coordination" in follow_up_modules
    assert "planning" in follow_up_modules
    workflow_types = {action["type"] for action in payload.get("workflow_actions", [])}
    assert "approval" in workflow_types
    assert "follow_up" in workflow_types

    planning_milestones = [
        entry
        for entry in payload["entries"]
        if entry["extendedProps"].get("module") == "planning"
        and entry["extendedProps"].get("category") == "planning_milestone_custom"
    ]
    assert (
        planning_milestones
    ), "Custom planning milestones should appear in calendar payload"
    assert any(
        milestone["extendedProps"].get("milestoneTitle") == "Procurement window"
        for milestone in planning_milestones
    )


@pytest.mark.django_db
def test_build_calendar_payload_skips_tasks_linked_to_events():
    cache.clear()

    user = User.objects.create_user(
        username="eventer",
        password="secret",
        user_type="oobc_staff",
        is_approved=True,
    )

    # Create an activity (replaces old Event model)
    event = WorkItem.objects.create(
        title="Coordination Meeting",
        work_type=WorkItem.WORK_TYPE_ACTIVITY,
        start_date=timezone.now().date() + timedelta(days=1),
        status=WorkItem.STATUS_IN_PROGRESS,
        created_by=user,
    )

    # Create a task with the activity as parent (replaces linked_event)
    WorkItem.objects.create(
        title="Prepare agenda",
        work_type=WorkItem.WORK_TYPE_TASK,
        parent=event,
        due_date=timezone.now().date() + timedelta(days=1),
        created_by=user,
    )

    payload = build_calendar_payload(filter_modules=["coordination", "staff"])

    staff_entries = [
        entry
        for entry in payload["entries"]
        if entry["extendedProps"].get("module") == "staff"
    ]
    coordination_entries = [
        entry
        for entry in payload["entries"]
        if entry["extendedProps"].get("module") == "coordination"
    ]

    assert coordination_entries, "Event should appear in coordination module"
    assert not any(
        entry["title"].startswith("Prepare agenda") for entry in staff_entries
    ), "Linked task should not duplicate calendar entries"


@pytest.mark.django_db
def test_calendar_payload_cache_invalidation_on_task_save():
    cache.clear()

    user = User.objects.create_user(
        username="cache_test",
        password="secret",
        user_type="oobc_staff",
        is_approved=True,
    )

    WorkItem.objects.create(
        title="Initial task",
        work_type=WorkItem.WORK_TYPE_TASK,
        due_date=timezone.now().date() + timedelta(days=2),
        status=WorkItem.STATUS_IN_PROGRESS,
        created_by=user,
    )

    first_payload = build_calendar_payload(filter_modules=["staff"])
    first_staff_entries = [
        entry
        for entry in first_payload["entries"]
        if entry["extendedProps"].get("module") == "staff"
    ]
    assert len(first_staff_entries) == 1

    WorkItem.objects.create(
        title="Newly added task",
        work_type=WorkItem.WORK_TYPE_TASK,
        due_date=timezone.now().date() + timedelta(days=3),
        status=WorkItem.STATUS_NOT_STARTED,
        created_by=user,
    )

    second_payload = build_calendar_payload(filter_modules=["staff"])
    second_staff_entries = [
        entry
        for entry in second_payload["entries"]
        if entry["extendedProps"].get("module") == "staff"
    ]
    assert (
        len(second_staff_entries) == 2
    ), "Calendar cache should refresh after task changes"


@pytest.mark.django_db
def test_build_calendar_payload_tracks_partnership_workflows():
    user = User.objects.create_user(
        username="partnership_user",
        password="secret",
        user_type="oobc_staff",
        is_approved=True,
    )

    org = Organization.objects.create(
        name="BARMM MOF",
        organization_type="nga",
    )

    partnership = Partnership.objects.create(
        title="Fiscal Coordination MOU",
        partnership_type="mou",
        description="Coordinate budget support for OOBC communities",
        objectives="Align fiscal support",
        scope="BARMM",
        lead_organization=org,
        concept_date=timezone.now().date() - timedelta(days=5),
        negotiation_start_date=timezone.now().date() - timedelta(days=2),
        signing_date=timezone.now().date() + timedelta(days=1),
        start_date=timezone.now().date() + timedelta(days=15),
        renewal_date=timezone.now().date() + timedelta(days=365),
        created_by=user,
        status="pending_approval",
    )
    partnership.organizations.add(org)

    PartnershipMilestone.objects.create(
        partnership=partnership,
        title="Secure BARMM approval",
        description="Awaiting BARMM MOF signature",
        milestone_type="approval",
        due_date=timezone.now().date() + timedelta(days=1),
        created_by=user,
    )

    payload = build_calendar_payload(filter_modules=["coordination"])

    categories = {
        entry["extendedProps"].get("category")
        for entry in payload["entries"]
        if entry["extendedProps"].get("module") == "coordination"
    }
    assert "partnership_signing" in categories

    approval_actions = [
        action
        for action in payload.get("workflow_actions", [])
        if action.get("module") == "coordination" and action.get("type") == "approval"
    ]
    assert any("Partnership" in action.get("label", "") for action in approval_actions)

    compliance_metrics = (
        payload.get("analytics", {}).get("compliance", {}).get("modules", {})
    )
    assert compliance_metrics.get("coordination", {}).get("pending_approvals", 0) >= 1


@pytest.mark.django_db
def test_oobc_calendar_feed_json_requires_login(client):
    user = User.objects.create_user(
        username="api_user",
        password="secret",
        user_type="oobc_staff",
        is_approved=True,
    )
    client.force_login(user)

    response = client.get(reverse("common:oobc_calendar_feed_json"))
    assert response.status_code == 200
    payload = response.json()
    assert "events" in payload
    assert "module_stats" in payload
    assert "workflow_actions" in payload
    assert "workflow_summary" in payload


@pytest.mark.django_db
def test_oobc_calendar_feed_ics_download(client):
    user = User.objects.create_user(
        username="ics_user",
        password="secret",
        user_type="oobc_staff",
        is_approved=True,
    )
    client.force_login(user)

    response = client.get(reverse("common:oobc_calendar_feed_ics"))
    assert response.status_code == 200
    assert response["Content-Type"] == "text/calendar"
    assert "BEGIN:VCALENDAR" in response.content.decode()


@pytest.mark.django_db
def test_oobc_calendar_brief_renders(client):
    user = User.objects.create_user(
        username="brief_user",
        password="secret",
        user_type="oobc_staff",
        is_approved=True,
    )
    client.force_login(user)

    response = client.get(reverse("common:oobc_calendar_brief"))
    assert response.status_code == 200
    assert "OOBC Calendar Brief" in response.content.decode()
