"""Support functions for staff management workflows."""

from __future__ import annotations

from datetime import timedelta
from typing import Iterable, Sequence

from django.db import OperationalError, transaction
from django.db.models import Max
from django.utils import timezone

from common.constants import STAFF_TEAM_DEFINITIONS
from common.models import (
    StaffProfile,
    WorkItem,
    StaffTeam,
    StaffTeamMembership,
    User,
)


def ensure_default_staff_teams() -> Sequence[StaffTeam]:
    """Back-fill default teams so the dashboard always has core units."""

    updated_teams: list[StaffTeam] = []
    for definition in STAFF_TEAM_DEFINITIONS:
        team, created = StaffTeam.objects.get_or_create(
            name=definition["name"],
            defaults={
                "description": definition.get("description", ""),
                "mission": definition.get("mission", ""),
                "focus_areas": definition.get("focus", []),
            },
        )
        fields_to_update: list[str] = []
        if not created:
            if (
                definition.get("description")
                and team.description != definition["description"]
            ):
                team.description = definition["description"]
                fields_to_update.append("description")
            if definition.get("mission") and team.mission != definition["mission"]:
                team.mission = definition["mission"]
                fields_to_update.append("mission")
            if definition.get("focus") and team.focus_areas != definition["focus"]:
                team.focus_areas = definition["focus"]
                fields_to_update.append("focus_areas")
            if fields_to_update:
                fields_to_update.append("updated_at")
                team.save(update_fields=fields_to_update)
        updated_teams.append(team)
    return updated_teams


def assign_board_position(task: WorkItem) -> WorkItem:
    """Ensure the task has a trailing board position within its status column."""

    if task.board_position:
        return task
    try:
        max_position = (
            WorkItem.objects.filter(status=task.status)
            .exclude(pk=task.pk)
            .aggregate(Max("board_position"))
            .get("board_position__max")
            or 0
        )
        task.board_position = max_position + 1
        task.save(update_fields=["board_position", "updated_at"])
    except OperationalError:
        # Database may not yet have the board_position column (pre-migration).
        return task
    return task


def ensure_membership(
    team: StaffTeam, user: User, assigned_by: User | None = None
) -> StaffTeamMembership:
    """Ensure a staff user is linked to a team."""

    membership, created = StaffTeamMembership.objects.get_or_create(
        team=team,
        user=user,
        defaults={
            "role": StaffTeamMembership.ROLE_MEMBER,
            "assigned_by": assigned_by,
        },
    )
    if not membership.is_active:
        membership.is_active = True
        membership.assigned_by = membership.assigned_by or assigned_by
        membership.save(update_fields=["is_active", "assigned_by", "updated_at"])
    return membership


def ensure_staff_profiles_for_users(users: Iterable[User]) -> list[StaffProfile]:
    """Back-fill StaffProfile records for the given staff users."""

    profiles: list[StaffProfile] = []
    for user in users:
        profile, _ = StaffProfile.objects.get_or_create(user=user)
        profiles.append(profile)
    return profiles


def seed_tasks(
    created_by: User | None,
    staff_users: Sequence[User],
    blueprints: Iterable[dict],
    today: timezone.datetime | None = None,
) -> list[WorkItem]:
    """Create staff tasks based on blueprints and distribute to staff."""

    if today is None:
        today = timezone.now().date()
    tasks: list[WorkItem] = []
    staff_cycle = list(staff_users)
    if not staff_cycle and created_by:
        staff_cycle = [created_by]
    if not staff_cycle:
        return tasks
    staff_count = len(staff_cycle)

    for index, blueprint in enumerate(blueprints):
        team, _ = StaffTeam.objects.get_or_create(name=blueprint["team"])
        assignee = staff_cycle[index % staff_count]
        defaults = {
            "priority": blueprint.get("priority", WorkItem.PRIORITY_MEDIUM),
            "status": blueprint.get("status", WorkItem.STATUS_NOT_STARTED),
            "impact": blueprint.get("impact", ""),
            "description": blueprint.get("description", ""),
            "progress": blueprint.get("progress", 0),
            "created_by": created_by,
        }
        due_in_days = blueprint.get("due_in_days", 7)
        duration = blueprint.get("duration_days", 3)
        due_date = today + timedelta(days=due_in_days)
        start_date = due_date - timedelta(days=duration)
        if start_date < today:
            start_date = today
        defaults.update({"start_date": start_date, "due_date": due_date})
        task, _ = WorkItem.objects.get_or_create(
            title=blueprint["title"],
            defaults=defaults,
        )
        task.teams.add(team)
        task.assignees.set([assignee])
        if (
            blueprint.get("status") == WorkItem.STATUS_COMPLETED
            and task.completed_at is None
        ):
            task.completed_at = timezone.now()
            task.progress = 100
            task.save(update_fields=["completed_at", "progress", "updated_at"])
        assign_board_position(task)
        ensure_membership(team, assignee, created_by)
        tasks.append(task)
    return tasks


@transaction.atomic
def seed_staff_demo_data(created_by: User | None = None) -> list[WorkItem]:
    """Seed staff teams and demo tasks useful for staging environments."""

    ensure_default_staff_teams()
    staff_users = list(
        User.objects.filter(user_type__in=("oobc_staff", "admin"), is_active=True)
    )
    if created_by and created_by not in staff_users:
        staff_users.insert(0, created_by)
    if not staff_users:
        demo_user, _ = User.objects.get_or_create(
            username="staff.demo",
            defaults={
                "first_name": "Team",
                "last_name": "Demo",
                "email": "staff.demo@example.com",
                "user_type": "oobc_staff",
                "is_active": True,
                "is_approved": True,
            },
        )
        staff_users.append(demo_user)

    default_blueprints = [
        {
            "title": "Refresh barangay mapping layers",
            "team": "MANA Team",
            "priority": WorkItem.PRIORITY_HIGH,
            "status": WorkItem.STATUS_IN_PROGRESS,
            "impact": "Update field datasets ahead of deployment windows.",
            "due_in_days": 5,
        },
        {
            "title": "Compile monthly monitoring brief",
            "team": "M&E Unit",
            "priority": WorkItem.PRIORITY_MEDIUM,
            "status": WorkItem.STATUS_NOT_STARTED,
            "impact": "Surface programme progress indicators for leadership.",
            "due_in_days": 7,
        },
        {
            "title": "Finalize Q3 resource alignment",
            "team": "Planning and Budgeting Unit",
            "priority": WorkItem.PRIORITY_HIGH,
            "status": "at_risk",  # WorkItem may not have STATUS_AT_RISK constant
            "impact": "Close gaps in funding envelopes with finance leads.",
            "due_in_days": 3,
        },
        {
            "title": "Inter-agency coordination briefing",
            "team": "Coordination Unit",
            "priority": WorkItem.PRIORITY_MEDIUM,
            "status": WorkItem.STATUS_IN_PROGRESS,
            "impact": "Align commitments for upcoming community engagement.",
            "due_in_days": 6,
        },
        {
            "title": "Design livelihood support package",
            "team": "Community Development Unit",
            "priority": WorkItem.PRIORITY_MEDIUM,
            "status": WorkItem.STATUS_NOT_STARTED,
            "impact": "Bundle social protection and livelihood components.",
            "due_in_days": 9,
        },
        {
            "title": "Synthesize field interviews",
            "team": "Research Unit",
            "priority": WorkItem.PRIORITY_LOW,
            "status": WorkItem.STATUS_COMPLETED,
            "impact": "Feed insights into policy evidence dashboards.",
            "due_in_days": 2,
        },
    ]

    return seed_tasks(created_by, staff_users, default_blueprints)
