"""
WorkItem Test Factories

Factory classes for generating test data (Phase 5 - Testing).

Provides:
- WorkItemFactory for easy test data creation
- Predefined fixtures for common scenarios
- Helper functions for complex hierarchies
"""

import factory
from datetime import date, timedelta
from django.contrib.auth import get_user_model

from common.work_item_model import WorkItem
from common.models import StaffTeam

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    """Factory for creating test users."""

    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@oobc.gov.ph")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    is_active = True


class StaffTeamFactory(factory.django.DjangoModelFactory):
    """Factory for creating test teams."""

    class Meta:
        model = StaffTeam

    name = factory.Sequence(lambda n: f"Team {n}")
    description = factory.Faker("sentence")
    is_active = True


class WorkItemFactory(factory.django.DjangoModelFactory):
    """Factory for creating test work items."""

    class Meta:
        model = WorkItem

    work_type = WorkItem.WORK_TYPE_TASK
    title = factory.Faker("sentence", nb_words=4)
    description = factory.Faker("paragraph")
    status = WorkItem.STATUS_NOT_STARTED
    priority = WorkItem.PRIORITY_MEDIUM
    progress = 0
    start_date = factory.LazyFunction(lambda: date.today())
    due_date = factory.LazyFunction(lambda: date.today() + timedelta(days=7))
    calendar_color = "#3B82F6"
    is_calendar_visible = True
    auto_calculate_progress = True


class ProjectFactory(WorkItemFactory):
    """Factory for creating projects."""

    work_type = WorkItem.WORK_TYPE_PROJECT
    title = factory.Sequence(lambda n: f"Project {n}")
    project_data = factory.LazyFunction(
        lambda: {
            "workflow_stage": "planning",
            "budget": 500000,
            "funding_source": "BARMM",
        }
    )


class ActivityFactory(WorkItemFactory):
    """Factory for creating activities."""

    work_type = WorkItem.WORK_TYPE_ACTIVITY
    title = factory.Sequence(lambda n: f"Activity {n}")
    activity_data = factory.LazyFunction(
        lambda: {
            "event_type": "workshop",
            "location": "Cotabato City",
            "max_participants": 30,
        }
    )


class TaskFactory(WorkItemFactory):
    """Factory for creating tasks."""

    work_type = WorkItem.WORK_TYPE_TASK
    title = factory.Sequence(lambda n: f"Task {n}")
    task_data = factory.LazyFunction(
        lambda: {
            "domain": "general",
            "deliverable_type": "report",
        }
    )


class SubtaskFactory(WorkItemFactory):
    """Factory for creating subtasks."""

    work_type = WorkItem.WORK_TYPE_SUBTASK
    title = factory.Sequence(lambda n: f"Subtask {n}")


# Helper functions for creating complex hierarchies

def create_project_hierarchy(
    num_activities=3,
    num_tasks_per_activity=2,
    creator=None,
):
    """
    Create a complete project hierarchy.

    Returns:
        tuple: (project, activities, tasks)
    """
    if creator is None:
        creator = UserFactory()

    project = ProjectFactory(created_by=creator)

    activities = []
    tasks = []

    for i in range(num_activities):
        activity = ActivityFactory(
            parent=project,
            title=f"Activity {i+1}",
            created_by=creator,
        )
        activities.append(activity)

        for j in range(num_tasks_per_activity):
            task = TaskFactory(
                parent=activity,
                title=f"Task {i+1}.{j+1}",
                created_by=creator,
            )
            tasks.append(task)

    return project, activities, tasks


def create_mana_assessment_project(researcher=None):
    """
    Create a MANA assessment project with typical structure.

    Returns:
        WorkItem: Root project
    """
    if researcher is None:
        researcher = UserFactory(username="researcher")

    project = ProjectFactory(
        title="MANA Assessment - Region XII",
        start_date=date(2025, 1, 1),
        due_date=date(2025, 6, 30),
        created_by=researcher,
        project_data={
            "workflow_stage": "data_collection",
            "assessment_type": "mana",
            "target_region": "Region XII",
        },
    )

    # Planning phase
    planning = ActivityFactory(
        title="Assessment Planning",
        parent=project,
        start_date=date(2025, 1, 1),
        due_date=date(2025, 1, 31),
    )

    TaskFactory(
        title="Develop assessment framework",
        parent=planning,
        task_data={
            "domain": "mana",
            "assessment_phase": "planning",
        },
    )

    # Data collection phase
    data_collection = ActivityFactory(
        title="Field Data Collection",
        parent=project,
        start_date=date(2025, 2, 1),
        due_date=date(2025, 4, 30),
        activity_data={
            "event_type": "field_visit",
            "location": "Region XII",
        },
    )

    TaskFactory(
        title="Conduct household surveys",
        parent=data_collection,
        task_data={
            "domain": "mana",
            "assessment_phase": "data_collection",
            "deliverable_type": "survey_data",
        },
    )

    TaskFactory(
        title="Interview community leaders",
        parent=data_collection,
        task_data={
            "domain": "mana",
            "assessment_phase": "data_collection",
            "deliverable_type": "interview_notes",
        },
    )

    # Analysis phase
    analysis = ActivityFactory(
        title="Data Analysis",
        parent=project,
        start_date=date(2025, 5, 1),
        due_date=date(2025, 5, 31),
    )

    TaskFactory(
        title="Analyze survey results",
        parent=analysis,
        task_data={
            "domain": "mana",
            "assessment_phase": "analysis",
        },
    )

    return project


def create_policy_development_project(policy_officer=None):
    """
    Create a policy development project.

    Returns:
        WorkItem: Root project
    """
    if policy_officer is None:
        policy_officer = UserFactory(username="policy_officer")

    project = ProjectFactory(
        title="OBC Education Policy Framework",
        start_date=date(2025, 1, 1),
        due_date=date(2025, 12, 31),
        created_by=policy_officer,
        project_data={
            "policy_area": "education",
            "policy_stage": "drafting",
        },
    )

    # Evidence collection
    evidence = ActivityFactory(
        title="Evidence Collection",
        parent=project,
        start_date=date(2025, 1, 1),
        due_date=date(2025, 3, 31),
    )

    TaskFactory(
        title="Review existing policies",
        parent=evidence,
        task_data={
            "domain": "policy",
            "policy_phase": "evidence_collection",
        },
    )

    # Stakeholder consultation
    consultation = ActivityFactory(
        title="Stakeholder Consultation",
        parent=project,
        start_date=date(2025, 4, 1),
        due_date=date(2025, 6, 30),
        activity_data={
            "event_type": "consultation",
            "stakeholder_groups": ["educators", "community_leaders"],
        },
    )

    TaskFactory(
        title="Conduct consultation workshops",
        parent=consultation,
        task_data={
            "domain": "policy",
            "policy_phase": "consultation",
        },
    )

    # Drafting
    drafting = ActivityFactory(
        title="Policy Drafting",
        parent=project,
        start_date=date(2025, 7, 1),
        due_date=date(2025, 9, 30),
    )

    TaskFactory(
        title="Draft policy document",
        parent=drafting,
        task_data={
            "domain": "policy",
            "policy_phase": "drafting",
        },
    )

    return project


def create_deep_hierarchy(depth=5):
    """
    Create a deep hierarchy for testing tree operations.

    Args:
        depth: Number of levels in the hierarchy

    Returns:
        WorkItem: Deepest child item
    """
    parent = ProjectFactory(title="Root Project")

    current = parent
    for i in range(depth - 1):
        current = TaskFactory(
            title=f"Level {i+1}",
            parent=current,
        )

    return current


def create_wide_tree(num_children=10, num_levels=3):
    """
    Create a wide tree for testing scalability.

    Args:
        num_children: Number of children per node
        num_levels: Number of levels in the tree

    Returns:
        WorkItem: Root project
    """
    project = ProjectFactory(title="Wide Project")

    def add_children(parent, level):
        if level >= num_levels:
            return

        for i in range(num_children):
            if level == 0:
                child = ActivityFactory(
                    title=f"Activity {i}",
                    parent=parent,
                )
            else:
                child = TaskFactory(
                    title=f"Task L{level}-{i}",
                    parent=parent,
                )

            add_children(child, level + 1)

    add_children(project, 0)
    return project


# Predefined test scenarios

def create_calendar_test_data():
    """
    Create test data for calendar integration tests.

    Returns:
        dict: Test data with various work items
    """
    user = UserFactory(username="calendar_user")

    # Current month items
    today = date.today()

    ongoing_task = TaskFactory(
        title="Ongoing Task",
        start_date=today - timedelta(days=5),
        due_date=today + timedelta(days=5),
        status=WorkItem.STATUS_IN_PROGRESS,
        calendar_color="#3B82F6",
    )

    upcoming_workshop = ActivityFactory(
        title="Upcoming Workshop",
        start_date=today + timedelta(days=10),
        due_date=today + timedelta(days=10),
        activity_data={
            "event_type": "workshop",
            "location": "Cotabato City",
        },
        calendar_color="#10B981",
    )

    overdue_task = TaskFactory(
        title="Overdue Task",
        start_date=today - timedelta(days=20),
        due_date=today - timedelta(days=5),
        status=WorkItem.STATUS_AT_RISK,
        calendar_color="#F59E0B",
    )

    return {
        "user": user,
        "ongoing_task": ongoing_task,
        "upcoming_workshop": upcoming_workshop,
        "overdue_task": overdue_task,
    }
