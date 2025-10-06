"""
Staff and General Query Templates for OBCMS Chat System

Provides query templates for:
- Staff queries (15 templates): Tasks, calendar events, workload, team management
- General queries (10 templates): Help, navigation, system info, statistics

These templates enable staff to quickly access their personal data and navigate
the system efficiently without needing complex query construction.
"""

from typing import Any, Dict
from common.ai_services.chat.query_templates.base import QueryTemplate


# =============================================================================
# STAFF/TASK QUERY TEMPLATES (15 templates)
# =============================================================================

STAFF_TEMPLATES = [
    # -------------------------------------------------------------------------
    # MY TASKS
    # -------------------------------------------------------------------------
    QueryTemplate(
        id='staff_my_tasks',
        category='staff',
        pattern=r'\b(my|show my|list my|view my)\s+tasks\b',
        query_template='Task.objects.filter(assigned_to__id={user_id})',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Show my tasks',
            'My tasks',
            'List my tasks',
            'View my tasks',
            'What tasks are assigned to me?'
        ],
        priority=10,
        description='Show all tasks assigned to the current user',
        tags=['staff', 'tasks', 'my', 'assigned']
    ),
    QueryTemplate(
        id='staff_tasks_assigned_to_me',
        category='staff',
        pattern=r'\b(tasks?\s+(assigned\s+)?to\s+me|assigned\s+tasks?)\b',
        query_template='Task.objects.filter(assigned_to__id={user_id})',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Tasks assigned to me',
            'Assigned tasks',
            'Tasks to me',
            'What am I assigned to?'
        ],
        priority=10,
        description='Show tasks assigned to current user',
        tags=['staff', 'tasks', 'assigned']
    ),

    # -------------------------------------------------------------------------
    # TASKS BY STATUS
    # -------------------------------------------------------------------------
    QueryTemplate(
        id='staff_pending_tasks',
        category='staff',
        pattern=r'\b(my\s+)?(pending|todo|outstanding|open)\s+tasks?\b',
        query_template='Task.objects.filter(assigned_to__id={user_id}, status="pending")',
        required_entities=[],
        optional_entities=[],
        examples=[
            'My pending tasks',
            'Show pending tasks',
            'Todo tasks',
            'Outstanding tasks',
            'Open tasks'
        ],
        priority=9,
        description='Show pending tasks for current user',
        tags=['staff', 'tasks', 'status', 'pending']
    ),
    QueryTemplate(
        id='staff_completed_tasks',
        category='staff',
        pattern=r'\b(my\s+)?(completed|done|finished)\s+tasks?\b',
        query_template='Task.objects.filter(assigned_to__id={user_id}, status="completed")',
        required_entities=[],
        optional_entities=[],
        examples=[
            'My completed tasks',
            'Show completed tasks',
            'Done tasks',
            'Finished tasks',
            'Tasks I completed'
        ],
        priority=9,
        description='Show completed tasks for current user',
        tags=['staff', 'tasks', 'status', 'completed']
    ),
    QueryTemplate(
        id='staff_overdue_tasks',
        category='staff',
        pattern=r'\b(my\s+)?(overdue|late|past due)\s+tasks?\b',
        query_template='Task.objects.filter(assigned_to__id={user_id}, due_date__lt=timezone.now(), status__in=["pending", "in_progress"])',
        required_entities=[],
        optional_entities=[],
        examples=[
            'My overdue tasks',
            'Show overdue tasks',
            'Late tasks',
            'Past due tasks',
            'Tasks that are overdue'
        ],
        priority=9,
        description='Show overdue tasks for current user',
        tags=['staff', 'tasks', 'status', 'overdue']
    ),
    QueryTemplate(
        id='staff_in_progress_tasks',
        category='staff',
        pattern=r'\b(my\s+)?(in progress|ongoing|current|active)\s+tasks?\b',
        query_template='Task.objects.filter(assigned_to__id={user_id}, status="in_progress")',
        required_entities=[],
        optional_entities=[],
        examples=[
            'My in progress tasks',
            'Show ongoing tasks',
            'Current tasks',
            'Active tasks',
            'Tasks in progress'
        ],
        priority=9,
        description='Show in-progress tasks for current user',
        tags=['staff', 'tasks', 'status', 'in_progress']
    ),

    # -------------------------------------------------------------------------
    # TASKS BY PRIORITY
    # -------------------------------------------------------------------------
    QueryTemplate(
        id='staff_high_priority_tasks',
        category='staff',
        pattern=r'\b(my\s+)?(high priority|urgent|important|critical)\s+tasks?\b',
        query_template='Task.objects.filter(assigned_to__id={user_id}, priority__in=["high", "urgent", "critical"])',
        required_entities=[],
        optional_entities=[],
        examples=[
            'My high priority tasks',
            'Show urgent tasks',
            'Important tasks',
            'Critical tasks'
        ],
        priority=8,
        description='Show high-priority tasks for current user',
        tags=['staff', 'tasks', 'priority', 'high']
    ),
    QueryTemplate(
        id='staff_recent_tasks',
        category='staff',
        pattern=r'\b(my\s+)?(recent|latest|new)\s+tasks?\b',
        query_template='Task.objects.filter(assigned_to__id={user_id}).order_by("-created_at")[:10]',
        required_entities=[],
        optional_entities=[],
        examples=[
            'My recent tasks',
            'Show recent tasks',
            'Latest tasks',
            'New tasks',
            'Recently created tasks'
        ],
        priority=8,
        description='Show recently created tasks for current user',
        tags=['staff', 'tasks', 'recent']
    ),

    # -------------------------------------------------------------------------
    # TASKS ASSIGNED TO OTHERS
    # -------------------------------------------------------------------------
    QueryTemplate(
        id='staff_tasks_assigned_to_user',
        category='staff',
        pattern=r'\btasks?\s+assigned\s+to\s+(?P<staff_name>[\w\s]+?)(\?|$)',
        query_template='Task.objects.filter(assigned_to__username__icontains="{staff_name}")',
        required_entities=['staff_member'],
        optional_entities=[],
        examples=[
            'Tasks assigned to John',
            'Show tasks for Sarah',
            'What tasks is Maria working on?',
            'Tasks for admin'
        ],
        priority=7,
        description='Show tasks assigned to a specific staff member',
        tags=['staff', 'tasks', 'assigned', 'other']
    ),

    # -------------------------------------------------------------------------
    # TASK WORKLOAD
    # -------------------------------------------------------------------------
    QueryTemplate(
        id='staff_task_count',
        category='staff',
        pattern=r'\b(how many|count|total)\s+(tasks?\s+)?(do i have|assigned to me|on my plate)\b',
        query_template='Task.objects.filter(assigned_to__id={user_id}).count()',
        required_entities=[],
        optional_entities=[],
        examples=[
            'How many tasks do I have?',
            'Count my tasks',
            'Total tasks assigned to me',
            'How many tasks on my plate?'
        ],
        priority=8,
        description='Count total tasks assigned to current user',
        tags=['staff', 'tasks', 'count']
    ),

    # -------------------------------------------------------------------------
    # CALENDAR/EVENTS
    # -------------------------------------------------------------------------
    QueryTemplate(
        id='staff_my_events',
        category='staff',
        pattern=r'\b(my|show my|view my)\s+(events?|calendar|schedule|appointments?)\b',
        query_template='CalendarEvent.objects.filter(Q(created_by__id={user_id}) | Q(attendees__id={user_id}))',
        required_entities=[],
        optional_entities=[],
        examples=[
            'My events',
            'Show my calendar',
            'My schedule',
            'View my appointments',
            'What events do I have?'
        ],
        priority=10,
        description='Show calendar events for current user',
        tags=['staff', 'calendar', 'events', 'my']
    ),
    QueryTemplate(
        id='staff_upcoming_events',
        category='staff',
        pattern=r'\b(upcoming|future|next|coming)\s+(events?|appointments?|meetings?)\b',
        query_template='CalendarEvent.objects.filter(Q(created_by__id={user_id}) | Q(attendees__id={user_id}), start_time__gte=timezone.now()).order_by("start_time")[:10]',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Upcoming events',
            'Show upcoming meetings',
            'Future appointments',
            'Next events',
            'Coming events'
        ],
        priority=9,
        description='Show upcoming events for current user',
        tags=['staff', 'calendar', 'events', 'upcoming']
    ),

    # -------------------------------------------------------------------------
    # TEAM TASKS
    # -------------------------------------------------------------------------
    QueryTemplate(
        id='staff_team_tasks',
        category='staff',
        pattern=r'\b(team|our|group|department)\s+tasks?\b',
        query_template='Task.objects.filter(assigned_to__groups__in={user_groups})',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Team tasks',
            'Our tasks',
            'Show team tasks',
            'Department tasks',
            'Group tasks'
        ],
        priority=7,
        description='Show tasks for user\'s team/groups',
        tags=['staff', 'tasks', 'team']
    ),

    # -------------------------------------------------------------------------
    # PROJECT TASKS
    # -------------------------------------------------------------------------
    QueryTemplate(
        id='staff_project_tasks',
        category='staff',
        pattern=r'\btasks?\s+for\s+(project|ppa)\s+(?P<project_name>[\w\s]+?)(\?|$)',
        query_template='Task.objects.filter(related_project__title__icontains="{project_name}")',
        required_entities=['project'],
        optional_entities=[],
        examples=[
            'Tasks for project Alpha',
            'Show tasks for Education PPA',
            'Tasks in Livelihood project'
        ],
        priority=6,
        description='Show tasks for a specific project',
        tags=['staff', 'tasks', 'project']
    ),
    QueryTemplate(
        id='staff_my_project_tasks',
        category='staff',
        pattern=r'\b(my\s+)?tasks?\s+on\s+(this\s+)?project\b',
        query_template='Task.objects.filter(assigned_to__id={user_id}, related_project__isnull=False)',
        required_entities=[],
        optional_entities=[],
        examples=[
            'My tasks on project',
            'Tasks on this project',
            'My project tasks',
            'Project-related tasks'
        ],
        priority=7,
        description='Show user\'s project-related tasks',
        tags=['staff', 'tasks', 'project', 'my']
    ),
]


# =============================================================================
# GENERAL QUERY TEMPLATES (10 templates)
# =============================================================================

GENERAL_TEMPLATES = [
    # -------------------------------------------------------------------------
    # HELP QUERIES
    # -------------------------------------------------------------------------
    QueryTemplate(
        id='general_help',
        category='general',
        pattern=r'\b(help|what can you do|capabilities|how do i|how to)\b',
        query_template='HELP',  # Special marker for help handler
        required_entities=[],
        optional_entities=[],
        examples=[
            'Help',
            'What can you do?',
            'How do I use this?',
            'Show me what you can do',
            'What are your capabilities?'
        ],
        priority=10,
        description='Show help and capabilities',
        tags=['general', 'help']
    ),
    QueryTemplate(
        id='general_example_queries',
        category='general',
        pattern=r'\b(examples?|sample queries|show me examples|what can i ask)\b',
        query_template='EXAMPLES',  # Special marker for examples handler
        required_entities=[],
        optional_entities=[],
        examples=[
            'Show me examples',
            'What can I ask?',
            'Example queries',
            'Sample questions',
            'Give me examples'
        ],
        priority=9,
        description='Show example queries',
        tags=['general', 'help', 'examples']
    ),

    # -------------------------------------------------------------------------
    # SYSTEM INFO
    # -------------------------------------------------------------------------
    QueryTemplate(
        id='general_system_modules',
        category='general',
        pattern=r'\b(what modules|system modules|available modules|what systems?)\b',
        query_template='MODULES',  # Special marker for modules handler
        required_entities=[],
        optional_entities=[],
        examples=[
            'What modules are available?',
            'Show system modules',
            'What systems do you have?',
            'Available modules'
        ],
        priority=8,
        description='Show available OBCMS modules',
        tags=['general', 'system', 'modules']
    ),
    QueryTemplate(
        id='general_system_capabilities',
        category='general',
        pattern=r'\b(what do you know|what data|what information|system capabilities)\b',
        query_template='CAPABILITIES',  # Special marker for capabilities handler
        required_entities=[],
        optional_entities=[],
        examples=[
            'What do you know?',
            'What data do you have?',
            'What information is available?',
            'System capabilities'
        ],
        priority=8,
        description='Show system data and capabilities',
        tags=['general', 'system', 'info']
    ),

    # -------------------------------------------------------------------------
    # NAVIGATION
    # -------------------------------------------------------------------------
    QueryTemplate(
        id='general_navigate_to',
        category='general',
        pattern=r'\b(take me to|go to|open|show me|navigate to)\s+(?P<destination>[\w\s]+?)(\?|$)',
        query_template='NAVIGATE:{destination}',  # Special marker for navigation
        required_entities=[],
        optional_entities=[],
        examples=[
            'Take me to dashboard',
            'Go to communities',
            'Open MANA',
            'Show me coordination',
            'Navigate to policies'
        ],
        priority=9,
        description='Navigate to a specific page',
        tags=['general', 'navigation']
    ),
    QueryTemplate(
        id='general_dashboard',
        category='general',
        pattern=r'\b(dashboard|home|main page|home page)\b',
        query_template='NAVIGATE:dashboard',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Go to dashboard',
            'Take me home',
            'Show dashboard',
            'Main page',
            'Home'
        ],
        priority=8,
        description='Navigate to dashboard',
        tags=['general', 'navigation', 'dashboard']
    ),

    # -------------------------------------------------------------------------
    # STATISTICS
    # -------------------------------------------------------------------------
    QueryTemplate(
        id='general_statistics_overview',
        category='general',
        pattern=r'\b(show\s+)?(stats|statistics|overview|summary|dashboard stats)\b',
        query_template='STATISTICS',  # Special marker for stats handler
        required_entities=[],
        optional_entities=[],
        examples=[
            'Show stats',
            'System statistics',
            'Overview',
            'Summary',
            'Dashboard stats'
        ],
        priority=8,
        description='Show system statistics overview',
        tags=['general', 'statistics', 'overview']
    ),

    # -------------------------------------------------------------------------
    # RECENT ACTIVITY
    # -------------------------------------------------------------------------
    QueryTemplate(
        id='general_recent_activity',
        category='general',
        pattern=r'\b(recent activity|latest activity|what\'?s new|recent changes)\b',
        query_template='RECENT_ACTIVITY',  # Special marker for activity handler
        required_entities=[],
        optional_entities=[],
        examples=[
            'Recent activity',
            'What\'s new?',
            'Latest activity',
            'Show recent changes',
            'Recent updates'
        ],
        priority=7,
        description='Show recent system activity',
        tags=['general', 'activity', 'recent']
    ),

    # -------------------------------------------------------------------------
    # GREETING & THANKS
    # -------------------------------------------------------------------------
    QueryTemplate(
        id='general_greeting',
        category='general',
        pattern=r'\b(hi|hello|hey|greetings|good morning|good afternoon)\b',
        query_template='GREETING',  # Special marker for greeting handler
        required_entities=[],
        optional_entities=[],
        examples=[
            'Hi',
            'Hello',
            'Hey there',
            'Good morning',
            'Greetings'
        ],
        priority=6,
        description='Respond to greetings',
        tags=['general', 'greeting', 'social']
    ),
    QueryTemplate(
        id='general_thanks',
        category='general',
        pattern=r'\b(thanks|thank you|thx|appreciate it)\b',
        query_template='THANKS',  # Special marker for thanks handler
        required_entities=[],
        optional_entities=[],
        examples=[
            'Thanks',
            'Thank you',
            'Thanks a lot',
            'I appreciate it'
        ],
        priority=6,
        description='Respond to thanks',
        tags=['general', 'thanks', 'social']
    ),
]


# =============================================================================
# EXPORTS (Registration handled by query_templates/__init__.py)
# =============================================================================

# Export template lists for registry auto-registration
__all__ = ['STAFF_TEMPLATES', 'GENERAL_TEMPLATES']
