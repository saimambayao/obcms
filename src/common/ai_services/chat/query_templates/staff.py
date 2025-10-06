"""
Staff & User Management Query Templates for OBCMS Chat System

15+ template variations for querying staff, users, tasks, and activity data including:
- Staff directory queries (by role, department, status)
- Task management (my tasks, team tasks, overdue, completed)
- User preferences (settings, notifications, dashboard)
- Activity tracking (recent activity, work logs, contributions)
"""

from typing import Any, Dict
from common.ai_services.chat.query_templates.base import QueryTemplate


# =============================================================================
# STAFF DIRECTORY TEMPLATES (5 templates)
# =============================================================================

STAFF_DIRECTORY_TEMPLATES = [
    QueryTemplate(
        id='staff_all_users',
        category='staff',
        pattern=r'\b(show|list|display|get)\s+(me\s+)?(all\s+)?(staff|users|team members)\b',
        query_template='User.objects.filter(is_active=True).order_by("last_name", "first_name")[:50]',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Show me all staff',
            'List users',
            'Display team members',
            'Get all staff',
            'Staff directory'
        ],
        priority=7,
        description='List all active staff members',
        tags=['list', 'staff', 'directory']
    ),
    QueryTemplate(
        id='staff_by_role',
        category='staff',
        pattern=r'\b(show|list|display)\s+(me\s+)?(?P<role>coordinator|admin|manager|staff|user)s?\b',
        query_template='User.objects.filter(is_active=True, groups__name__icontains="{role}").order_by("last_name")[:50]',
        required_entities=['role'],
        optional_entities=[],
        examples=[
            'Show me coordinators',
            'List admins',
            'Display managers',
            'Get all coordinators',
            'Show staff users'
        ],
        priority=8,
        description='List staff by role/group',
        tags=['list', 'staff', 'role']
    ),
    QueryTemplate(
        id='staff_count_total',
        category='staff',
        pattern=r'\b(how many|count|total|number of)\s+(staff|users|team members)\b',
        query_template='User.objects.filter(is_active=True).count()',
        required_entities=[],
        optional_entities=[],
        examples=[
            'How many staff do we have?',
            'Count users',
            'Total staff',
            'Number of team members',
            'Staff count'
        ],
        priority=8,
        description='Count total active staff',
        tags=['count', 'staff']
    ),
    QueryTemplate(
        id='staff_count_by_role',
        category='staff',
        pattern=r'\b(how many|count|total)\s+(?P<role>coordinator|admin|manager)s?\b',
        query_template='User.objects.filter(is_active=True, groups__name__icontains="{role}").count()',
        required_entities=['role'],
        optional_entities=[],
        examples=[
            'How many coordinators?',
            'Count admins',
            'Total managers',
            'Number of coordinators'
        ],
        priority=8,
        description='Count staff by role',
        tags=['count', 'staff', 'role']
    ),
    QueryTemplate(
        id='staff_search_by_name',
        category='staff',
        pattern=r'\b(find|search|who is)\s+(?P<name>[\w\s]+?)\s*(staff|user)?\b',
        query_template='User.objects.filter(Q(first_name__icontains="{name}") | Q(last_name__icontains="{name}")).order_by("last_name")[:10]',
        required_entities=['name'],
        optional_entities=[],
        examples=[
            'Find John staff',
            'Search Maria user',
            'Who is Ahmed?',
            'Find staff named Sarah'
        ],
        priority=9,
        description='Search staff by name',
        tags=['search', 'staff', 'name']
    ),
]


# =============================================================================
# TASK MANAGEMENT TEMPLATES (6 templates)
# =============================================================================

TASK_MANAGEMENT_TEMPLATES = [
    QueryTemplate(
        id='tasks_my_tasks',
        category='staff',
        pattern=r'\b(my|show my|get my|list my)\s+tasks?\b',
        query_template='Task.objects.filter(assigned_to=request.user, status__in=["pending", "in_progress"]).order_by("due_date", "-priority")[:30]',
        required_entities=[],
        optional_entities=[],
        examples=[
            'My tasks',
            'Show my tasks',
            'Get my tasks',
            'List my tasks',
            'What are my tasks?'
        ],
        priority=10,
        description='Show current user tasks',
        tags=['list', 'tasks', 'personal']
    ),
    QueryTemplate(
        id='tasks_overdue',
        category='staff',
        pattern=r'\b(overdue|late|past due)\s+tasks?\b',
        query_template='Task.objects.filter(assigned_to=request.user, status__in=["pending", "in_progress"], due_date__lt=timezone.now()).order_by("due_date")[:20]',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Overdue tasks',
            'Late tasks',
            'Past due tasks',
            'Show overdue tasks',
            'My overdue tasks'
        ],
        priority=10,
        description='Show overdue tasks',
        tags=['list', 'tasks', 'overdue', 'urgent']
    ),
    QueryTemplate(
        id='tasks_today',
        category='staff',
        pattern=r'\b(today|today\'s|tasks?\s+for\s+today)\b',
        query_template='Task.objects.filter(assigned_to=request.user, due_date__date=timezone.now().date()).order_by("-priority", "due_date")[:20]',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Today tasks',
            "Today's tasks",
            'Tasks for today',
            'What tasks do I have today?',
            'Show today tasks'
        ],
        priority=10,
        description='Show tasks due today',
        tags=['list', 'tasks', 'today']
    ),
    QueryTemplate(
        id='tasks_completed',
        category='staff',
        pattern=r'\b(completed|done|finished)\s+tasks?\b',
        query_template='Task.objects.filter(assigned_to=request.user, status="completed").order_by("-updated_at")[:30]',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Completed tasks',
            'Done tasks',
            'Finished tasks',
            'My completed tasks',
            'Show completed tasks'
        ],
        priority=7,
        description='Show completed tasks',
        tags=['list', 'tasks', 'completed']
    ),
    QueryTemplate(
        id='tasks_high_priority',
        category='staff',
        pattern=r'\b(high priority|urgent|critical)\s+tasks?\b',
        query_template='Task.objects.filter(assigned_to=request.user, priority__in=["high", "critical"], status__in=["pending", "in_progress"]).order_by("due_date")[:20]',
        required_entities=[],
        optional_entities=[],
        examples=[
            'High priority tasks',
            'Urgent tasks',
            'Critical tasks',
            'Show high priority tasks',
            'My urgent tasks'
        ],
        priority=9,
        description='Show high priority tasks',
        tags=['list', 'tasks', 'priority', 'urgent']
    ),
    QueryTemplate(
        id='tasks_count_my_tasks',
        category='staff',
        pattern=r'\b(how many|count)\s+(of\s+)?(my\s+)?tasks?(\s+(do i have|i have))?\b',
        query_template='Task.objects.filter(assigned_to=request.user, status__in=["pending", "in_progress"]).count()',
        required_entities=[],
        optional_entities=[],
        examples=[
            'How many my tasks?',
            'Count my tasks',
            'How many tasks do I have?',
            'Number of my tasks'
        ],
        priority=8,
        description='Count current user tasks',
        tags=['count', 'tasks', 'personal']
    ),
]


# =============================================================================
# USER PREFERENCES TEMPLATES (2 templates)
# =============================================================================

USER_PREFERENCES_TEMPLATES = [
    QueryTemplate(
        id='preferences_notification_settings',
        category='staff',
        pattern=r'\b(notification|alert|email)\s+(settings|preferences|config)\b',
        query_template='request.user.notification_preferences',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Notification settings',
            'Alert preferences',
            'Email settings',
            'My notification settings',
            'Show notification preferences'
        ],
        priority=7,
        description='Show notification settings',
        tags=['preferences', 'notifications', 'settings']
    ),
    QueryTemplate(
        id='preferences_dashboard_config',
        category='staff',
        pattern=r'\b(dashboard|home)\s+(settings|preferences|config|customization)\b',
        query_template='request.user.dashboard_preferences',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Dashboard settings',
            'Home preferences',
            'Dashboard config',
            'Dashboard customization',
            'My dashboard settings'
        ],
        priority=6,
        description='Show dashboard preferences',
        tags=['preferences', 'dashboard', 'settings']
    ),
]


# =============================================================================
# ACTIVITY TRACKING TEMPLATES (2 templates)
# =============================================================================

ACTIVITY_TRACKING_TEMPLATES = [
    QueryTemplate(
        id='activity_recent',
        category='staff',
        pattern=r'\b(recent|latest|my)\s+(activity|actions)(\s+history)?\b|\bactivity\s+history\b',
        query_template='AuditLog.objects.filter(user=request.user).select_related("content_type").order_by("-timestamp")[:30]',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Recent activity',
            'Latest activity',
            'My activity',
            'My actions',
            'Activity history'
        ],
        priority=7,
        description='Show recent user activity',
        tags=['activity', 'history', 'personal']
    ),
    QueryTemplate(
        id='activity_work_log',
        category='staff',
        pattern=r'\b(work log|time log|contributions|my work|work summary)\b',
        query_template='Task.objects.filter(assigned_to=request.user).values("status").annotate(count=Count("id"), hours=Sum("time_spent")).order_by("-count")',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Work log',
            'Time log',
            'My contributions',
            'Show my work',
            'Work summary'
        ],
        priority=6,
        description='Show work log and contributions',
        tags=['activity', 'work_log', 'summary']
    ),
]


# =============================================================================
# COMBINE ALL STAFF TEMPLATES
# =============================================================================

STAFF_TEMPLATES = (
    STAFF_DIRECTORY_TEMPLATES +
    TASK_MANAGEMENT_TEMPLATES +
    USER_PREFERENCES_TEMPLATES +
    ACTIVITY_TRACKING_TEMPLATES
)

# Total: 5 + 6 + 2 + 2 = 15 staff templates with 50+ example query variations
